#!/bin/bash

echo "📦 打包 ChangeFace3 应用"
echo "================================"

# 检查必需文件
REQUIRED_FILES=(
    "app.py"
    "config.py"
    "requirements.txt"
    "start.sh"
    ".env.example"
)

echo "检查必需文件..."
MISSING_FILES=0
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ 缺少文件: $file"
        MISSING_FILES=$((MISSING_FILES + 1))
    else
        echo "✅ $file"
    fi
done

if [ $MISSING_FILES -gt 0 ]; then
    echo ""
    echo "❌ 有 $MISSING_FILES 个必需文件缺失，无法打包"
    exit 1
fi

echo ""
echo "开始打包..."

# 删除旧的打包文件
rm -f package.tgz

# 打包（排除不需要的文件）
tar zcvf package.tgz \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='.env' \
    --exclude='*.pyc' \
    --exclude='*.log' \
    --exclude='package.tgz' \
    --exclude='temp' \
    --exclude='.idea' \
    --exclude='.vscode' \
    .

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 打包成功！"
    echo "📦 文件: package.tgz"
    echo "📏 大小: $(du -h package.tgz | cut -f1)"
    echo ""
    echo "部署命令："
    echo "  tar zxvf /home/admin/app/package.tgz -C /home/admin/app/"
    echo "  sh /home/admin/app/start.sh"
else
    echo "❌ 打包失败"
    exit 1
fi
