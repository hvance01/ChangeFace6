# 登录功能使用指南

## 功能说明

ChangeFace3 现已支持基于账号密码的登录验证功能，确保只有授权用户才能访问应用。

## 快速开始

### 1. 配置用户账号

编辑 `users.txt` 文件，添加用户账号：

```txt
# 格式: username:password
admin:admin123
user1:mypassword
user2:strongpass456
```

**重要提示：**
- 每行一个用户
- 用户名和密码用冒号 `:` 分隔
- 密码会自动转换为 SHA256 哈希存储（安全）
- 以 `#` 开头的行为注释
- 空行会被忽略

### 2. 文件位置

- **用户配置文件**: `users.txt` （实际使用的文件）
- **示例文件**: `users.txt.example` （模板文件）

### 3. 首次使用

```bash
# 1. 复制示例文件（如果 users.txt 不存在）
cp users.txt.example users.txt

# 2. 编辑用户文件
vim users.txt
# 或
nano users.txt

# 3. 添加你的账号密码
admin:your_secure_password

# 4. 启动应用
streamlit run app.py
```

## 使用流程

### 登录

1. 访问应用地址：`http://服务器IP:8501`
2. 看到登录页面
3. 输入用户名和密码
4. 点击 **🔐 登录** 按钮
5. 登录成功后自动跳转到主应用

### 查看当前用户

登录后，侧边栏顶部会显示当前登录的用户名：
```
👤 当前用户: admin
```

### 登出

点击侧边栏的 **🚪 退出登录** 按钮即可退出

## 用户管理

### 添加新用户

编辑 `users.txt` 文件，添加新行：

```txt
newuser:newpassword123
```

保存文件后，新用户立即生效（无需重启应用）。

### 修改密码

直接在 `users.txt` 文件中修改密码：

```txt
# 修改前
admin:oldpassword

# 修改后
admin:newpassword
```

保存后新密码立即生效。

### 删除用户

在 `users.txt` 文件中删除对应的行，或在行首添加 `#` 注释掉：

```txt
# 禁用此用户
# user1:password123
```

### 批量导入用户

可以使用脚本批量生成用户：

```python
# generate_users.py
users = [
    ("admin", "admin123"),
    ("user1", "pass1"),
    ("user2", "pass2"),
]

with open("users.txt", "w") as f:
    f.write("# 用户配置文件\n")
    for username, password in users:
        f.write(f"{username}:{password}\n")
```

## 安全建议

### 1. 使用强密码

❌ 弱密码示例：
- `123456`
- `password`
- `admin`

✅ 强密码示例：
- `Adm!n@2025`
- `MyS3cur3P@ss`
- `Ch@ng3Face!2025`

### 2. 密码规范

建议密码包含：
- 至少 8 位字符
- 大小写字母
- 数字
- 特殊符号

### 3. 保护用户文件

```bash
# 设置文件权限，仅所有者可读写
chmod 600 users.txt

# 确保 users.txt 在 .gitignore 中（已自动添加）
cat .gitignore | grep users.txt
```

### 4. 定期更换密码

建议每 3-6 个月更换一次密码。

### 5. 不要共享账号

为每个用户创建独立账号，方便管理和审计。

## 高级功能

### 使用哈希密码

如果不想在文件中存储明文密码，可以预先生成哈希：

```python
import hashlib

password = "your_password"
password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
print(f"Hash: {password_hash}")
```

然后在 `users.txt` 中使用哈希格式：

```txt
# 格式: username:hash:sha256
admin:5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8:sha256
```

### 自定义用户文件路径

修改 `utils/auth.py` 中的默认路径：

```python
auth = AuthManager(users_file="/path/to/your/users.txt")
```

## 故障排查

### 问题 1: 登录失败

**原因：**
- 用户名或密码错误
- `users.txt` 文件不存在
- 文件格式错误

**解决：**
1. 检查用户名和密码是否正确
2. 确认 `users.txt` 文件存在
3. 检查文件格式是否为 `username:password`

### 问题 2: 用户文件不生效

**原因：**
- 文件编码问题
- 行尾符问题（Windows vs Unix）

**解决：**
```bash
# 转换为 UTF-8 编码
iconv -f GBK -t UTF-8 users.txt -o users.txt

# 转换行尾符
dos2unix users.txt
```

### 问题 3: 登录后显示空白

**原因：**
- Session state 未正确初始化

**解决：**
清除浏览器缓存或使用无痕模式重新访问。

## 示例配置

### 单用户（个人使用）

```txt
# users.txt
admin:MySecurePassword123!
```

### 多用户（团队使用）

```txt
# users.txt

# 管理员
admin:AdminPass@2025

# 开发团队
developer1:DevPass123!
developer2:DevPass456!

# 运营团队
operator1:OpPass789!
operator2:OpPass012!

# 测试账号（可随时删除）
# testuser:testpass
```

### 分组管理

```txt
# users.txt

### 管理员组 ###
admin:AdminPass@2025
superadmin:SuperPass@2025

### 开发组 ###
dev1:DevPass1
dev2:DevPass2

### 运营组 ###
op1:OpPass1
op2:OpPass2

### 测试组（临时）###
# test1:test123
```

## API 参考

### AuthManager 类

```python
from utils.auth import AuthManager

# 初始化
auth = AuthManager(users_file="users.txt")

# 验证凭据
is_valid = auth.verify_credentials("username", "password")

# 检查登录状态
if auth.is_logged_in():
    print("已登录")

# 登录
auth.login("username")

# 登出
auth.logout()

# 获取当前用户
current_user = auth.get_current_user()
```

### 在其他页面使用

如果有多个页面，可以在每个页面顶部添加：

```python
from utils.auth import AuthManager, show_login_page

auth = AuthManager()
if not auth.is_logged_in():
    show_login_page()
    st.stop()
```

## 技术细节

### 密码哈希

使用 SHA256 算法对密码进行哈希：

```python
import hashlib
hash_value = hashlib.sha256(password.encode('utf-8')).hexdigest()
```

### Session 管理

使用 Streamlit 的 session_state 管理登录状态：

```python
st.session_state['authenticated'] = True
st.session_state['username'] = username
```

### 文件格式支持

支持两种格式：

1. **明文格式**（自动哈希）:
   ```
   username:password
   ```

2. **哈希格式**:
   ```
   username:hash_value:sha256
   ```

## 后续增强

可以考虑添加的功能：

- [ ] 用户角色权限（管理员、普通用户）
- [ ] 登录日志记录
- [ ] 密码复杂度验证
- [ ] 账号锁定机制（多次失败后锁定）
- [ ] 会话超时
- [ ] 双因素认证（2FA）
- [ ] LDAP/AD 集成
- [ ] OAuth 登录

---

## 联系支持

如有问题，请查看：
- 项目文档：`README.md`
- 部署指南：`DEPLOY_GUIDE.md`
