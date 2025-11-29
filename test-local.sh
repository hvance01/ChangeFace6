#!/bin/bash

echo "🧪 ChangeFace3 本地测试脚本"
echo "================================"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 切换到脚本所在目录
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
cd "$SCRIPT_DIR" || exit 1

echo -e "${BLUE}📂 项目目录: $SCRIPT_DIR${NC}"
echo ""

# ==================== 检查环境 ====================
echo "🔍 检查环境..."
echo ""

# 检查 Python
if ! command -v python3 >/dev/null 2>&1; then
    echo -e "${RED}❌ Python3 未安装${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✅ $PYTHON_VERSION${NC}"

# ==================== 检查/创建虚拟环境 ====================
echo ""
echo "📦 检查虚拟环境..."

if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  虚拟环境不存在，正在创建...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✅ 虚拟环境创建成功${NC}"
else
    echo -e "${GREEN}✅ 虚拟环境已存在${NC}"
fi

# ==================== 激活虚拟环境 ====================
echo ""
echo "🔧 激活虚拟环境..."
source venv/bin/activate

if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${RED}❌ 虚拟环境激活失败${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 虚拟环境已激活: $VIRTUAL_ENV${NC}"

# ==================== 检查/安装依赖 ====================
echo ""
echo "📥 检查依赖包..."

if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ requirements.txt 不存在${NC}"
    exit 1
fi

# 检查是否需要安装依赖
NEEDS_INSTALL=false

# 检查几个关键包
for package in streamlit replicate python-dotenv pillow; do
    if ! pip show "$package" >/dev/null 2>&1; then
        NEEDS_INSTALL=true
        break
    fi
done

if [ "$NEEDS_INSTALL" = true ]; then
    echo -e "${YELLOW}⚠️  缺少依赖包，正在安装...${NC}"
    pip install -r requirements.txt -q
    echo -e "${GREEN}✅ 依赖包安装完成${NC}"
else
    echo -e "${GREEN}✅ 所有依赖已安装${NC}"
fi

# ==================== 检查配置文件 ====================
echo ""
echo "⚙️  检查配置文件..."

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env 文件不存在${NC}"
    if [ -f ".env.example" ]; then
        echo "   正在从 .env.example 创建 .env..."
        cp .env.example .env
        echo -e "${GREEN}✅ .env 文件已创建${NC}"
        echo -e "${YELLOW}   ⚠️  请编辑 .env 文件，配置 REPLICATE_API_TOKEN${NC}"
    else
        echo -e "${RED}   ❌ .env.example 也不存在，请手动创建 .env 文件${NC}"
    fi
else
    echo -e "${GREEN}✅ .env 文件存在${NC}"

    # 检查 API Token 是否配置
    if grep -q "your_replicate_api_token_here" .env 2>/dev/null; then
        echo -e "${YELLOW}   ⚠️  请配置 REPLICATE_API_TOKEN${NC}"
    else
        echo -e "${GREEN}   ✅ REPLICATE_API_TOKEN 已配置${NC}"
    fi
fi

# 检查 users.txt 文件
echo ""
if [ ! -f "users.txt" ]; then
    echo -e "${YELLOW}⚠️  users.txt 文件不存在${NC}"
    if [ -f "users.txt.example" ]; then
        echo "   正在从 users.txt.example 创建 users.txt..."
        cp users.txt.example users.txt
        # 添加默认管理员账号
        echo "" >> users.txt
        echo "# 默认管理员账号（请修改密码）" >> users.txt
        echo "admin:admin123" >> users.txt
        echo -e "${GREEN}✅ users.txt 文件已创建${NC}"
        echo -e "${YELLOW}   ⚠️  默认账号: admin / admin123 (请修改密码)${NC}"
    else
        echo -e "${RED}   ❌ users.txt.example 也不存在，请手动创建 users.txt 文件${NC}"
    fi
else
    echo -e "${GREEN}✅ users.txt 文件存在${NC}"

    # 显示用户数量
    USER_COUNT=$(grep -v "^#" users.txt | grep -v "^$" | wc -l)
    echo -e "${BLUE}   ℹ️  已配置用户数: $USER_COUNT${NC}"
fi

# 检查必要文件
echo ""
echo "📄 检查必要文件..."

REQUIRED_FILES=(
    "app.py"
    "config.py"
    "requirements.txt"
)

ALL_FILES_EXIST=true
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file${NC}"
    else
        echo -e "${RED}❌ $file (缺失)${NC}"
        ALL_FILES_EXIST=false
    fi
done

if [ "$ALL_FILES_EXIST" = false ]; then
    echo ""
    echo -e "${RED}❌ 缺少必要文件，无法启动${NC}"
    exit 1
fi

# 检查 utils 目录
echo ""
if [ -d "utils" ]; then
    echo -e "${GREEN}✅ utils 目录存在${NC}"

    # 检查关键模块
    for module in auth.py face_swap.py file_handler.py; do
        if [ -f "utils/$module" ]; then
            echo -e "${GREEN}   ✅ utils/$module${NC}"
        else
            echo -e "${YELLOW}   ⚠️  utils/$module (缺失)${NC}"
        fi
    done
else
    echo -e "${RED}❌ utils 目录不存在${NC}"
    exit 1
fi

# ==================== 运行测试 ====================
echo ""
echo "🧪 运行功能测试..."
echo ""

# 测试认证模块
if [ -f "test_auth.py" ]; then
    echo "测试登录功能..."
    python3 test_auth.py
    echo ""
else
    echo -e "${YELLOW}⚠️  test_auth.py 不存在，跳过认证测试${NC}"
    echo ""
fi

# ==================== 检查端口占用 ====================
echo "🔍 检查端口占用..."

PORT=8501
if command -v lsof >/dev/null 2>&1; then
    if lsof -ti:$PORT >/dev/null 2>&1; then
        PID=$(lsof -ti:$PORT)
        echo -e "${YELLOW}⚠️  端口 $PORT 已被占用 (PID: $PID)${NC}"
        echo -e "${YELLOW}   运行以下命令停止: kill -9 $PID${NC}"
    else
        echo -e "${GREEN}✅ 端口 $PORT 可用${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  lsof 命令不可用，无法检查端口${NC}"
fi

# ==================== 显示项目信息 ====================
echo ""
echo "================================"
echo "📊 项目信息"
echo "================================"
echo -e "${BLUE}项目目录:${NC} $SCRIPT_DIR"
echo -e "${BLUE}Python版本:${NC} $PYTHON_VERSION"
echo -e "${BLUE}虚拟环境:${NC} $VIRTUAL_ENV"
echo -e "${BLUE}监听端口:${NC} $PORT"
echo ""

# ==================== 启动选项 ====================
echo "================================"
echo "🚀 准备启动应用"
echo "================================"
echo ""
echo "选择启动方式："
echo "  1) 正常启动 (默认)"
echo "  2) 启动并自动打开浏览器"
echo "  3) 调试模式启动"
echo "  4) 指定端口启动"
echo "  5) 仅检查，不启动"
echo "  q) 退出"
echo ""

read -p "请选择 (1-5 or q): " choice

case $choice in
    1|"")
        echo ""
        echo -e "${GREEN}🎭 启动 Streamlit 应用...${NC}"
        echo "================================"
        echo ""
        echo -e "${BLUE}访问地址: http://localhost:$PORT${NC}"
        echo -e "${BLUE}停止应用: Ctrl+C${NC}"
        echo ""
        exec streamlit run app.py --server.address=localhost --server.port=$PORT
        ;;
    2)
        echo ""
        echo -e "${GREEN}🎭 启动应用并打开浏览器...${NC}"
        echo ""
        exec streamlit run app.py --server.address=localhost --server.port=$PORT --server.headless=false
        ;;
    3)
        echo ""
        echo -e "${GREEN}🎭 调试模式启动...${NC}"
        echo ""
        echo -e "${YELLOW}提示: 文件修改会自动重载${NC}"
        echo ""
        exec streamlit run app.py --server.address=localhost --server.port=$PORT --logger.level=debug
        ;;
    4)
        echo ""
        read -p "请输入端口号: " CUSTOM_PORT
        echo ""
        echo -e "${GREEN}🎭 在端口 $CUSTOM_PORT 启动应用...${NC}"
        echo ""
        exec streamlit run app.py --server.address=localhost --server.port=$CUSTOM_PORT
        ;;
    5)
        echo ""
        echo -e "${GREEN}✅ 检查完成，未启动应用${NC}"
        echo ""
        echo "手动启动命令:"
        echo "  source venv/bin/activate"
        echo "  streamlit run app.py"
        exit 0
        ;;
    q|Q)
        echo ""
        echo -e "${BLUE}👋 退出${NC}"
        exit 0
        ;;
    *)
        echo ""
        echo -e "${RED}❌ 无效选择${NC}"
        exit 1
        ;;
esac
