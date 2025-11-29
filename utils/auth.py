"""
用户认证模块
支持基于账号密码的登录验证
"""
import os
import hashlib
import streamlit as st
from pathlib import Path


class AuthManager:
    """用户认证管理器"""

    def __init__(self, users_file="users.txt"):
        """
        初始化认证管理器

        Args:
            users_file: 用户信息文件路径
        """
        self.users_file = users_file
        self.users = self._load_users()

    def _load_users(self):
        """
        从文件加载用户信息

        文件格式：每行一个用户，格式为 username:password_hash
        支持两种格式：
        1. username:password (明文密码，自动转换为哈希)
        2. username:hash:sha256 (已哈希的密码)
        """
        users = {}

        if not os.path.exists(self.users_file):
            return users

        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()

                    # 跳过空行和注释
                    if not line or line.startswith('#'):
                        continue

                    parts = line.split(':')

                    if len(parts) == 2:
                        # 格式: username:password (明文)
                        username, password = parts
                        password_hash = self._hash_password(password)
                        users[username.strip()] = password_hash

                    elif len(parts) == 3 and parts[2] == 'sha256':
                        # 格式: username:hash:sha256 (已哈希)
                        username, password_hash, _ = parts
                        users[username.strip()] = password_hash

                    else:
                        print(f"警告: 第 {line_num} 行格式错误，已跳过")

        except Exception as e:
            print(f"加载用户文件时出错: {e}")

        return users

    def _hash_password(self, password):
        """
        使用 SHA256 哈希密码

        Args:
            password: 明文密码

        Returns:
            哈希后的密码
        """
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def verify_credentials(self, username, password):
        """
        验证用户凭据

        Args:
            username: 用户名
            password: 密码

        Returns:
            bool: 验证是否成功
        """
        if not username or not password:
            return False

        if username not in self.users:
            return False

        password_hash = self._hash_password(password)
        return self.users[username] == password_hash

    def is_logged_in(self):
        """
        检查用户是否已登录

        Returns:
            bool: 是否已登录
        """
        return st.session_state.get('authenticated', False)

    def login(self, username):
        """
        标记用户为已登录状态

        Args:
            username: 用户名
        """
        st.session_state['authenticated'] = True
        st.session_state['username'] = username

    def logout(self):
        """登出用户"""
        st.session_state['authenticated'] = False
        if 'username' in st.session_state:
            del st.session_state['username']

    def get_current_user(self):
        """
        获取当前登录用户名

        Returns:
            str: 用户名，如果未登录则返回 None
        """
        return st.session_state.get('username')


def show_login_page():
    """
    显示登录页面

    Returns:
        bool: 是否登录成功
    """
    auth = AuthManager()

    # 如果已经登录，直接返回 True
    if auth.is_logged_in():
        return True

    # 页面样式
    st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 40px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .login-title {
            text-align: center;
            color: #1f77b4;
            margin-bottom: 30px;
        }
        </style>
    """, unsafe_allow_html=True)

    # 居中显示登录表单
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)

        st.markdown("<h1 class='login-title'>🎭 ChangeFace3</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: gray;'>视频换脸工具</h3>", unsafe_allow_html=True)

        st.markdown("---")

        # 登录表单
        with st.form("login_form"):
            username = st.text_input("用户名", placeholder="请输入用户名")
            password = st.text_input("密码", type="password", placeholder="请输入密码")

            submitted = st.form_submit_button("🔐 登录", use_container_width=True, type="primary")

            if submitted:
                if auth.verify_credentials(username, password):
                    auth.login(username)
                    st.success(f"✅ 欢迎回来，{username}！")
                    st.rerun()
                else:
                    st.error("❌ 用户名或密码错误")

        st.markdown("</div>", unsafe_allow_html=True)

        # 页面底部提示
        st.markdown("---")
        st.info("💡 首次使用？请联系管理员获取账号")

    return False


def require_login(func):
    """
    装饰器：要求用户登录才能访问

    使用方法：
    @require_login
    def main_app():
        st.write("这是主应用")
    """
    def wrapper(*args, **kwargs):
        auth = AuthManager()
        if not auth.is_logged_in():
            show_login_page()
            return None
        return func(*args, **kwargs)
    return wrapper
