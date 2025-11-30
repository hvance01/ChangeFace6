#!/bin/sh

echo "🚀 ChangeFace3 阿里云部署启动脚本 (virtualenv 版本)"
echo "================================"
echo "💡 此脚本使用 virtualenv 而非 venv，适用于没有 python3-venv 的环境"
echo ""

# 切换到脚本所在目录
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
echo "📂 切换到应用目录: $SCRIPT_DIR"
cd "$SCRIPT_DIR" || exit 1

# 检查 Python 版本
echo "📌 检查 Python 版本..."
python3 --version

# 检查 pip 是否可用
if ! command -v pip3 >/dev/null 2>&1 && ! command -v pip >/dev/null 2>&1; then
    echo "❌ pip 不可用，请先安装 pip"
    echo "   安装命令: curl -sS https://bootstrap.pypa.io/get-pip.py | python3"
    exit 1
fi

# 安装 virtualenv（如果尚未安装）
echo "📦 检查 virtualenv..."
if ! python3 -m virtualenv --version >/dev/null 2>&1; then
    echo "   virtualenv 未安装，正在安装..."
    pip3 install --user virtualenv || pip install --user virtualenv

    if [ $? -ne 0 ]; then
        echo "❌ virtualenv 安装失败"
        echo "   请手动运行: pip3 install --user virtualenv"
        exit 1
    fi
fi

# 强制重新创建虚拟环境
echo "📦 创建虚拟环境..."
if [ -d "venv" ]; then
    echo "   删除旧的虚拟环境..."
    rm -rf venv
fi

echo "   使用 virtualenv 创建虚拟环境..."
python3 -m virtualenv venv

# 检查虚拟环境是否创建成功
if [ ! -f "venv/bin/activate" ]; then
    echo "❌ 虚拟环境创建失败"
    exit 1
fi
echo "✅ 虚拟环境创建成功"

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

# 启动应用
echo "🎭 启动 Streamlit 应用..."
echo "📍 访问地址将在下方显示"

# 使用 venv 中的 streamlit
exec venv/bin/streamlit run app.py --server.address=0.0.0.0 --server.port=8501
