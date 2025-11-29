#!/bin/bash

echo "🔧 配置端口转发规则"
echo "================================"
echo ""
echo "此脚本将配置 iptables 规则，将 80 和 443 端口转发到 8501"
echo "这样 Streamlit 可以以非 root 用户在 8501 端口运行，"
echo "而用户可以通过标准的 HTTP(80) 和 HTTPS(443) 端口访问"
echo ""

# 检查是否有 root 权限
if [ "$(id -u)" -ne 0 ]; then
    echo "❌ 此脚本需要 root 权限"
    echo "   请使用: sudo bash $0"
    exit 1
fi

# 检查 iptables 是否可用
if ! command -v iptables >/dev/null 2>&1; then
    echo "❌ iptables 未安装"
    echo "   安装命令: sudo apt install iptables"
    exit 1
fi

echo "📋 当前转发规则："
iptables -t nat -L PREROUTING -n --line-numbers | grep -E "tcp dpt:(80|443)"

echo ""
read -p "是否要添加/更新端口转发规则? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 已取消"
    exit 0
fi

echo ""
echo "🔧 添加端口转发规则..."

# 删除已存在的规则（如果有）
echo "   清理旧规则..."
iptables -t nat -D PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8501 2>/dev/null
iptables -t nat -D PREROUTING -p tcp --dport 443 -j REDIRECT --to-port 8501 2>/dev/null

# 添加新规则
echo "   添加 80 -> 8501 转发规则..."
iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8501

echo "   添加 443 -> 8501 转发规则..."
iptables -t nat -A PREROUTING -p tcp --dport 443 -j REDIRECT --to-port 8501

echo ""
echo "✅ 端口转发规则已配置！"
echo ""
echo "📋 当前转发规则："
iptables -t nat -L PREROUTING -n --line-numbers | grep -E "tcp dpt:(80|443)"

echo ""
echo "💾 保存规则（使其在重启后保持）..."
if command -v iptables-save >/dev/null 2>&1; then
    if [ -f /etc/iptables/rules.v4 ]; then
        echo "   备份旧规则..."
        cp /etc/iptables/rules.v4 /etc/iptables/rules.v4.bak.$(date +%Y%m%d_%H%M%S)
    fi

    mkdir -p /etc/iptables
    iptables-save > /etc/iptables/rules.v4
    echo "✅ 规则已保存到 /etc/iptables/rules.v4"

    # 安装 iptables-persistent 以自动加载规则
    if ! dpkg -l | grep -q iptables-persistent; then
        echo ""
        echo "💡 建议安装 iptables-persistent 以自动加载规则："
        echo "   sudo apt install iptables-persistent"
    fi
else
    echo "⚠️  iptables-save 不可用，规则在重启后会丢失"
fi

echo ""
echo "🎉 配置完成！"
echo ""
echo "现在可以："
echo "  1. 启动应用: sh start-aliyun.sh  (监听 8501 端口)"
echo "  2. 通过以下地址访问:"
echo "     - http://你的服务器IP (自动转发到 8501)"
echo "     - http://你的服务器IP:8501 (直接访问)"
echo ""
echo "如需删除转发规则:"
echo "  sudo iptables -t nat -D PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8501"
echo "  sudo iptables -t nat -D PREROUTING -p tcp --dport 443 -j REDIRECT --to-port 8501"
