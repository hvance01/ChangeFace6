#!/bin/bash

echo "📦 安装 ChangeFace3 系统依赖"
echo "================================"
echo ""

# 检查是否有 sudo 权限
if ! command -v sudo >/dev/null 2>&1; then
    echo "⚠️  sudo 命令不可用，请手动安装以下依赖："
    echo "   - python3.11-venv"
    echo "   - python3.11-dev"
    echo "   - curl"
    exit 1
fi

echo "正在检测系统..."

# 检测操作系统
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VER=$VERSION_ID
else
    echo "❌ 无法检测操作系统"
    exit 1
fi

echo "系统: $OS $VER"
echo ""

# 根据操作系统安装依赖
case $OS in
    ubuntu|debian)
        echo "📥 更新软件包列表..."
        sudo apt update

        echo "📥 安装 Python 虚拟环境支持..."
        sudo apt install -y python3.11-venv python3.11-dev curl

        if [ $? -eq 0 ]; then
            echo "✅ 依赖安装成功！"
            echo ""
            echo "现在可以运行:"
            echo "  sh start-aliyun.sh"
        else
            echo "❌ 依赖安装失败"
            exit 1
        fi
        ;;

    centos|rhel|fedora)
        echo "📥 安装 Python 虚拟环境支持..."
        sudo yum install -y python3-devel python3-pip curl

        if [ $? -eq 0 ]; then
            echo "✅ 依赖安装成功！"
            echo ""
            echo "现在可以运行:"
            echo "  sh start-aliyun.sh"
        else
            echo "❌ 依赖安装失败"
            exit 1
        fi
        ;;

    *)
        echo "❌ 不支持的操作系统: $OS"
        echo ""
        echo "请手动安装以下依赖："
        echo "  - python3.11-venv"
        echo "  - python3.11-dev"
        echo "  - curl"
        exit 1
        ;;
esac
