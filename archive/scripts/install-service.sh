#!/bin/bash

echo "📦 安装 ChangeFace3 为系统服务"
echo "================================"

# 检查是否有 root 权限
if [ "$(id -u)" -ne 0 ]; then
    echo "❌ 此脚本需要 root 权限"
    echo "   请使用: sudo bash $0"
    exit 1
fi

# 切换到脚本所在目录
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
APP_DIR="$SCRIPT_DIR"

echo "应用目录: $APP_DIR"
echo ""

# 检查服务文件是否存在
if [ ! -f "$APP_DIR/changeface.service" ]; then
    echo "❌ changeface.service 文件不存在"
    exit 1
fi

# 更新服务文件中的路径
echo "🔧 配置服务文件..."
SERVICE_FILE="/tmp/changeface.service"
cp "$APP_DIR/changeface.service" "$SERVICE_FILE"

# 替换路径
sed -i "s|/home/admin/app|$APP_DIR|g" "$SERVICE_FILE"

echo "服务配置："
cat "$SERVICE_FILE"
echo ""

read -p "确认安装服务? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 已取消"
    rm "$SERVICE_FILE"
    exit 0
fi

# 复制服务文件
echo "📋 安装服务文件..."
cp "$SERVICE_FILE" /etc/systemd/system/changeface.service
rm "$SERVICE_FILE"

# 重新加载 systemd
echo "🔄 重新加载 systemd..."
systemctl daemon-reload

# 启用服务
echo "✅ 启用服务..."
systemctl enable changeface

# 启动服务
echo "🚀 启动服务..."
systemctl start changeface

# 等待启动
sleep 3

# 检查状态
echo ""
echo "================================"
echo "📊 服务状态"
echo "================================"
systemctl status changeface --no-pager

echo ""
echo "================================"
echo "🎉 服务安装完成！"
echo "================================"
echo ""
echo "常用命令："
echo "  启动服务: sudo systemctl start changeface"
echo "  停止服务: sudo systemctl stop changeface"
echo "  重启服务: sudo systemctl restart changeface"
echo "  查看状态: sudo systemctl status changeface"
echo "  查看日志: sudo journalctl -u changeface -f"
echo "  禁用服务: sudo systemctl disable changeface"
echo ""
