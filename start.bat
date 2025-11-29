@echo off
echo 🚀 ChangeFace3 快速启动脚本
echo ================================

REM 检查 Python 版本
echo 📌 检查 Python 版本...
python --version

REM 检查虚拟环境
if not exist "venv\" (
    echo 📦 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo 🔧 激活虚拟环境...
call venv\Scripts\activate

REM 安装依赖
echo 📥 安装依赖包...
pip install -r requirements.txt

REM 检查 .env 文件
if not exist ".env" (
    echo ⚠️  .env 文件不存在，复制模板...
    copy .env.example .env
    echo ❗ 请编辑 .env 文件，填入你的 Replicate API Token
    echo    获取地址: https://replicate.com/account/api-tokens
    echo.
    pause
)

REM 启动应用
echo 🎭 启动 Streamlit 应用...
streamlit run app.py
