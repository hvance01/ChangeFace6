#!/usr/bin/env python3
"""
用户密码哈希生成工具

使用方法:
    python generate_hash.py

输入密码后，会生成对应的 SHA256 哈希值，
可以直接在 users.txt 中使用哈希格式。
"""

import hashlib
import getpass


def hash_password(password):
    """生成密码的 SHA256 哈希"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def main():
    print("=" * 60)
    print("ChangeFace3 - 密码哈希生成工具")
    print("=" * 60)
    print()

    while True:
        # 获取用户名
        username = input("请输入用户名 (直接回车退出): ").strip()
        if not username:
            print("\n再见！")
            break

        # 获取密码（隐藏输入）
        password = getpass.getpass("请输入密码: ")

        if not password:
            print("❌ 密码不能为空\n")
            continue

        # 生成哈希
        password_hash = hash_password(password)

        print("\n" + "=" * 60)
        print("生成结果:")
        print("=" * 60)

        print("\n1. 明文格式（推荐，系统会自动哈希）:")
        print(f"   {username}:{password}")

        print("\n2. 哈希格式（预先哈希，更安全）:")
        print(f"   {username}:{password_hash}:sha256")

        print("\n3. 仅哈希值:")
        print(f"   {password_hash}")

        print("\n" + "=" * 60)
        print("请复制上述内容到 users.txt 文件中")
        print("=" * 60)
        print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户取消，退出程序")
    except Exception as e:
        print(f"\n错误: {e}")
