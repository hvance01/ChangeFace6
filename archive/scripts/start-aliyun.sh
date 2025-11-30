#!/bin/sh

echo "🚀 ChangeFace3 阿里云部署启动脚本"
echo "================================"

# 切换到脚本所在目录
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
echo "📂 切换到应用目录: $SCRIPT_DIR"
cd "$SCRIPT_DIR" || exit 1

# 检查 Python 版本
echo "📌 检查 Python 版本..."
python3 --version

# 强制重新创建虚拟环境（不依赖仓库中的venv）
echo "📦 创建虚拟环境..."
if [ -d "venv" ]; then
    echo "   删除旧的虚拟环境..."
    rm -rf venv
fi

echo "   创建新的虚拟环境..."
# 尝试创建虚拟环境，如果失败则尝试其他方法
python3 -m venv venv 2>/tmp/venv_error.log

# 检查虚拟环境是否创建成功
if [ ! -f "venv/bin/activate" ]; then
    echo "⚠️  标准方法创建虚拟环境失败，尝试使用 --without-pip 选项..."

    # 尝试不带 pip 创建虚拟环境
    python3 -m venv --without-pip venv 2>/tmp/venv_error2.log

    if [ ! -f "venv/bin/activate" ]; then
        echo "❌ 虚拟环境创建失败"
        echo "错误信息："
        cat /tmp/venv_error.log 2>/dev/null
        echo ""
        echo "💡 解决方案："
        echo "   需要安装 python3-venv 包："
        echo "   sudo apt update && sudo apt install -y python3.11-venv"
        echo ""
        echo "   或者联系管理员安装以下包："
        echo "   - python3.11-venv"
        echo "   - python3.11-dev"
        exit 1
    fi

    # 手动安装 pip
    echo "   下载并安装 pip..."
    . venv/bin/activate

    # 下载 get-pip.py
    if ! curl -sS https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py; then
        echo "❌ 下载 get-pip.py 失败"
        echo "   尝试备用下载地址..."
        if ! wget -q -O /tmp/get-pip.py https://bootstrap.pypa.io/get-pip.py; then
            echo "❌ 备用下载也失败"
            exit 1
        fi
    fi

    # 检查文件是否下载成功
    if [ ! -f /tmp/get-pip.py ]; then
        echo "❌ get-pip.py 文件不存在"
        exit 1
    fi

    # 安装 pip
    if ! python /tmp/get-pip.py; then
        echo "❌ pip 安装失败"
        rm -f /tmp/get-pip.py
        exit 1
    fi
    rm -f /tmp/get-pip.py

    # 验证 pip 是否可用
    if ! command -v pip >/dev/null 2>&1; then
        echo "❌ pip 安装后仍不可用"
        exit 1
    fi
    echo "✅ pip 安装成功"
else
    echo "✅ 虚拟环境创建成功"
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
. venv/bin/activate

# 检查是否成功激活
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ 虚拟环境激活失败"
    exit 1
fi
echo "✅ 虚拟环境已激活: $VIRTUAL_ENV"

# 安装依赖
echo "📥 安装依赖包..."
echo "   升级 pip..."
pip install --upgrade pip
if [ $? -ne 0 ]; then
    echo "❌ pip 升级失败"
    exit 1
fi

echo "   安装项目依赖..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ 依赖包安装失败"
    exit 1
fi
echo "✅ 所有依赖安装成功"

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "⚠️  .env 文件不存在，复制模板..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "❗ 请编辑 .env 文件，填入你的 Replicate API Token"
        echo "   获取地址: https://replicate.com/account/api-tokens"
        echo "⚠️  继续启动但可能会因为缺少 API Token 而失败"
    else
        echo "❌ .env.example 文件不存在"
        exit 1
    fi
fi

# 检查必要文件
if [ ! -f "app.py" ]; then
    echo "❌ app.py 文件不存在"
    exit 1
fi

# 检查并清理端口占用
echo "🔍 检查端口 8501..."
PORT=8501
if command -v lsof >/dev/null 2>&1; then
    # 使用 lsof 检查端口
    PID=$(lsof -ti:$PORT 2>/dev/null)
    if [ -n "$PID" ]; then
        echo "⚠️  端口 $PORT 已被占用 (PID: $PID)"
        echo "   正在停止旧进程..."
        kill -15 $PID 2>/dev/null || kill -9 $PID 2>/dev/null
        sleep 2
        # 再次检查
        if lsof -ti:$PORT >/dev/null 2>&1; then
            echo "❌ 无法停止占用端口的进程"
            exit 1
        fi
        echo "✅ 旧进程已停止"
    fi
elif command -v netstat >/dev/null 2>&1; then
    # 使用 netstat 检查端口
    if netstat -tuln | grep -q ":$PORT "; then
        echo "⚠️  端口 $PORT 已被占用"
        echo "   尝试查找并停止进程..."
        PID=$(netstat -tulnp 2>/dev/null | grep ":$PORT " | awk '{print $7}' | cut -d'/' -f1)
        if [ -n "$PID" ] && [ "$PID" != "-" ]; then
            kill -15 $PID 2>/dev/null || kill -9 $PID 2>/dev/null
            sleep 2
            echo "✅ 旧进程已停止"
        else
            echo "⚠️  无法自动停止进程，请手动检查"
        fi
    fi
else
    echo "⚠️  无法检查端口状态（lsof 和 netstat 都不可用）"
fi

# 启动应用
echo "🎭 启动 Streamlit 应用..."
echo "📍 访问地址将在下方显示"

# 使用 venv 中的 streamlit
exec venv/bin/streamlit run app.py --server.address=0.0.0.0 --server.port=8501
