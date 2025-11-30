#!/bin/bash

echo "🚀 ChangeFace3 一键部署脚本"
echo "================================"
echo "此脚本将自动完成从代码克隆到应用启动的全部流程"
echo ""

# 配置变量（可根据需要修改）
APP_DIR="${APP_DIR:-/home/admin/app}"
GIT_REPO="${GIT_REPO:-}"  # 在这里填入你的 git 仓库地址
GIT_BRANCH="${GIT_BRANCH:-master}"
PORT="${PORT:-80}"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 打印函数
print_step() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[警告]${NC} $1"
}

print_error() {
    echo -e "${RED}[错误]${NC} $1"
}

# 错误处理
set -e
trap 'print_error "部署失败，请检查错误信息"; exit 1' ERR

# ==================== 步骤 0: 检查环境 ====================
print_step "检查系统环境..."

# 检查 Python
if ! command -v python3 >/dev/null 2>&1; then
    print_error "Python3 未安装"
    echo "安装命令: sudo apt update && sudo apt install -y python3"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_step "Python 版本: $PYTHON_VERSION"

# 检查 Git
if ! command -v git >/dev/null 2>&1; then
    print_error "Git 未安装"
    echo "安装命令: sudo apt update && sudo apt install -y git"
    exit 1
fi

print_step "Git 版本: $(git --version)"

# ==================== 步骤 1: 克隆或更新代码 ====================
print_step "准备代码..."

if [ -z "$GIT_REPO" ]; then
    print_warning "未配置 GIT_REPO，假设代码已存在于当前目录"
    APP_DIR="$(pwd)"
elif [ -d "$APP_DIR/.git" ]; then
    print_step "代码目录已存在，拉取最新代码..."
    cd "$APP_DIR"
    git fetch origin
    git reset --hard origin/$GIT_BRANCH
    git clean -fd
    print_step "代码已更新到最新版本"
else
    print_step "克隆代码仓库..."

    # 如果目录存在但不是 git 仓库，先备份
    if [ -d "$APP_DIR" ]; then
        BACKUP_DIR="${APP_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
        print_warning "目录已存在，备份到 $BACKUP_DIR"
        mv "$APP_DIR" "$BACKUP_DIR"
    fi

    # 创建父目录
    mkdir -p "$(dirname "$APP_DIR")"

    # 克隆代码
    git clone -b "$GIT_BRANCH" "$GIT_REPO" "$APP_DIR"
    cd "$APP_DIR"
    print_step "代码克隆完成"
fi

cd "$APP_DIR"
print_step "当前目录: $(pwd)"

# ==================== 步骤 2: 清理旧环境 ====================
print_step "清理旧环境..."

# 停止旧进程
if command -v lsof >/dev/null 2>&1; then
    OLD_PID=$(lsof -ti:$PORT 2>/dev/null || true)
    if [ -n "$OLD_PID" ]; then
        print_warning "停止占用端口 $PORT 的旧进程 (PID: $OLD_PID)..."
        kill -15 $OLD_PID 2>/dev/null || kill -9 $OLD_PID 2>/dev/null || true
        sleep 2
    fi
fi

# 删除旧虚拟环境
if [ -d "venv" ]; then
    print_step "删除旧虚拟环境..."
    rm -rf venv
fi

# ==================== 步骤 3: 创建虚拟环境 ====================
print_step "创建虚拟环境..."

# 尝试创建虚拟环境
if python3 -m venv venv 2>/tmp/venv_error.log; then
    print_step "虚拟环境创建成功"
else
    print_warning "标准方法创建虚拟环境失败，尝试备用方案..."

    # 尝试不带 pip 创建
    if python3 -m venv --without-pip venv 2>/tmp/venv_error2.log; then
        print_step "使用 --without-pip 创建虚拟环境成功"

        # 手动安装 pip
        print_step "下载并安装 pip..."
        . venv/bin/activate

        if curl -sS https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py; then
            python /tmp/get-pip.py
            rm -f /tmp/get-pip.py
            print_step "pip 安装成功"
        elif wget -q -O /tmp/get-pip.py https://bootstrap.pypa.io/get-pip.py; then
            python /tmp/get-pip.py
            rm -f /tmp/get-pip.py
            print_step "pip 安装成功"
        else
            print_error "无法下载 get-pip.py"
            print_error "请安装 python3-venv: sudo apt install -y python3-venv"
            exit 1
        fi
    else
        print_error "虚拟环境创建失败"
        cat /tmp/venv_error.log 2>/dev/null
        echo ""
        print_error "请安装 python3-venv: sudo apt install -y python3.11-venv"
        exit 1
    fi
fi

# ==================== 步骤 4: 激活虚拟环境 ====================
print_step "激活虚拟环境..."
. venv/bin/activate

if [ -z "$VIRTUAL_ENV" ]; then
    print_error "虚拟环境激活失败"
    exit 1
fi

print_step "虚拟环境已激活: $VIRTUAL_ENV"

# ==================== 步骤 5: 安装依赖 ====================
print_step "安装 Python 依赖包..."

# 升级 pip
print_step "升级 pip..."
pip install --upgrade pip -q

# 安装依赖
print_step "安装项目依赖..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_step "依赖安装完成"
else
    print_error "requirements.txt 不存在"
    exit 1
fi

# ==================== 步骤 6: 配置环境变量 ====================
print_step "配置环境变量..."

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_warning ".env 文件已创建，请编辑并填入你的 API Token"
        print_warning "获取地址: https://replicate.com/account/api-tokens"

        # 如果有环境变量，自动填入
        if [ -n "$REPLICATE_API_TOKEN" ]; then
            sed -i "s/your_replicate_api_token_here/$REPLICATE_API_TOKEN/" .env
            print_step "已自动配置 REPLICATE_API_TOKEN"
        fi
    else
        print_warning ".env.example 不存在，跳过环境变量配置"
    fi
else
    print_step ".env 文件已存在"
fi

# ==================== 步骤 7: 检查必要文件 ====================
print_step "检查必要文件..."

REQUIRED_FILES=("app.py" "requirements.txt")
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "缺少必要文件: $file"
        exit 1
    fi
done

print_step "所有必要文件检查通过"

# ==================== 步骤 8: 启动应用 ====================
print_step "启动应用..."

echo ""
echo "================================"
echo "🎉 部署完成！"
echo "================================"
echo "应用目录: $APP_DIR"
echo "Python版本: $PYTHON_VERSION"
echo "监听端口: $PORT"
echo "访问地址: http://$(hostname -I | awk '{print $1}'):$PORT"
echo ""
echo "正在启动 Streamlit 应用..."
echo "================================"
echo ""

# 启动应用
exec venv/bin/streamlit run app.py --server.address=0.0.0.0 --server.port=$PORT
