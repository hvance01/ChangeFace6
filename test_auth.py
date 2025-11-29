"""
登录功能测试脚本

用于测试用户认证功能是否正常工作
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.auth import AuthManager


def test_auth():
    """测试认证功能"""
    print("=" * 60)
    print("ChangeFace3 - 登录功能测试")
    print("=" * 60)
    print()

    # 初始化认证管理器
    auth = AuthManager("users.txt")

    print("✓ 认证管理器初始化成功")
    print(f"✓ 用户文件: users.txt")
    print(f"✓ 已加载用户数: {len(auth.users)}")
    print()

    if not auth.users:
        print("⚠️  警告: 未找到任何用户")
        print("   请确保 users.txt 文件存在并包含用户配置")
        print()
        print("示例配置:")
        print("   admin:admin123")
        return

    print("已加载的用户:")
    for username in auth.users.keys():
        print(f"  - {username}")
    print()

    # 测试登录
    print("=" * 60)
    print("测试登录功能")
    print("=" * 60)
    print()

    test_cases = [
        ("admin", "admin123", True),  # 默认账号
        ("admin", "wrongpass", False),  # 错误密码
        ("nonexist", "anypass", False),  # 不存在的用户
    ]

    for username, password, expected in test_cases:
        result = auth.verify_credentials(username, password)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        expected_str = "应成功" if expected else "应失败"

        print(f"{status} | 用户: {username:10} | 密码: {password:15} | {expected_str} | 实际: {'成功' if result else '失败'}")

    print()
    print("=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_auth()
    except FileNotFoundError:
        print("❌ 错误: users.txt 文件不存在")
        print("   请先创建 users.txt 文件")
        print()
        print("快速创建:")
        print("   cp users.txt.example users.txt")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
