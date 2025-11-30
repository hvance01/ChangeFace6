#!/bin/bash

echo "🔄 ChangeFace3 快速启动脚本"
echo "================================"

# 配置变量
PORT="${PORT:-8501}"

# 切换到脚本所在目录
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
cd "$SCRIPT_DIR" || exit 1

echo "📂 应用目录: $SCRIPT_DIR"

# ==================== 停止旧进程 ====================
echo "🔍 检查端口 $PORT..."
if command -v lsof >/dev/null 2>&1; then
    OLD_PID=$(lsof -ti:$PORT 2>/dev/null || true)
    if [ -n "$OLD_PID" ]; then
        echo "⚠️  停止旧进程 (PID: $OLD_PID)..."
        kill -15 $OLD_PID 2>/dev/null || kill -9 $OLD_PID 2>/dev/null || true
        sleep 2
        echo "✅ 旧进程已停止"
    fi
fi

# ==================== 检查虚拟环境 ====================
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在"
    echo "请先运行完整部署脚本: bash deploy.sh"
    exit 1
fi

# ==================== 激活虚拟环境 ====================
echo "🔧 激活虚拟环境..."
. venv/bin/activate

if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ 虚拟环境激活失败"
    exit 1
fi

# ==================== 检查必要文件 ====================
if [ ! -f "app.py" ]; then
    echo "❌ app.py 文件不存在"
    exit 1
fi

# ==================== 启动应用 ====================
echo ""
echo "================================"
echo "🎭 启动 Streamlit 应用"
echo "================================"
echo "监听端口: $PORT"
echo "访问地址: http://$(hostname -I | awk '{print $1}'):$PORT"
echo "================================"
echo ""

exec venv/bin/streamlit run app.py --server.address=0.0.0.0 --server.port=$PORT
