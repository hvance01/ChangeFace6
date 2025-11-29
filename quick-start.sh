#!/bin/bash

# 快速测试脚本 - 最小化版本
# 适合快速启动，跳过所有检查

echo "🚀 快速启动 ChangeFace3"

# 切换到脚本目录
cd "$(dirname "$0")" || exit 1

# 激活虚拟环境
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "❌ 虚拟环境不存在"
    echo "   运行: bash test-local.sh"
    exit 1
fi

# 启动应用
echo "启动中..."
exec streamlit run app.py --server.address=localhost --server.port=8501
