# 本地测试指南

## 快速开始

### Linux/macOS

```bash
# 一键启动测试
bash test-local.sh
```

### Windows

```cmd
# 双击运行或命令行执行
test-local.bat
```

## 测试脚本功能

本地测试脚本会自动完成以下检查和配置：

### 1. 环境检查
- ✅ 检查 Python 是否安装
- ✅ 显示 Python 版本

### 2. 虚拟环境管理
- ✅ 检查虚拟环境是否存在
- ✅ 自动创建虚拟环境（如果不存在）
- ✅ 激活虚拟环境

### 3. 依赖管理
- ✅ 检查依赖包是否安装
- ✅ 自动安装缺失的依赖

### 4. 配置文件检查
- ✅ 检查 `.env` 文件
- ✅ 自动从 `.env.example` 创建（如果不存在）
- ✅ 检查 API Token 配置
- ✅ 检查 `users.txt` 文件
- ✅ 自动创建默认管理员账号

### 5. 文件完整性检查
- ✅ 检查所有必要文件是否存在
- ✅ 检查 utils 模块

### 6. 功能测试
- ✅ 运行登录功能测试
- ✅ 验证用户认证模块

### 7. 端口检查
- ✅ 检查 8501 端口是否被占用
- ✅ 显示占用进程 PID

### 8. 启动应用
提供多种启动方式：
- 正常启动
- 启动并自动打开浏览器
- 调试模式启动（自动重载）
- 自定义端口启动
- 仅检查不启动

## 使用示例

### 示例 1: 首次运行

```bash
$ bash test-local.sh

🧪 ChangeFace3 本地测试脚本
================================
📂 项目目录: /Users/xxx/ChangeFace

🔍 检查环境...
✅ Python 3.11.2

📦 检查虚拟环境...
⚠️  虚拟环境不存在，正在创建...
✅ 虚拟环境创建成功

🔧 激活虚拟环境...
✅ 虚拟环境已激活

📥 检查依赖包...
⚠️  缺少依赖包，正在安装...
✅ 依赖包安装完成

⚙️  检查配置文件...
⚠️  .env 文件不存在
   正在从 .env.example 创建 .env...
✅ .env 文件已创建
   ⚠️  请配置 REPLICATE_API_TOKEN

⚠️  users.txt 文件不存在
   正在从 users.txt.example 创建 users.txt...
✅ users.txt 文件已创建
   ⚠️  默认账号: admin / admin123 (请修改密码)

📄 检查必要文件...
✅ app.py
✅ config.py
✅ requirements.txt

✅ utils 目录存在
   ✅ utils/auth.py
   ✅ utils/face_swap.py
   ✅ utils/file_handler.py

🧪 运行功能测试...
测试登录功能...
============================================================
ChangeFace3 - 登录功能测试
============================================================

✓ 认证管理器初始化成功
✓ 用户文件: users.txt
✓ 已加载用户数: 1

已加载的用户:
  - admin

============================================================
测试登录功能
============================================================

✅ PASS | 用户: admin      | 密码: admin123        | 应成功 | 实际: 成功
✅ PASS | 用户: admin      | 密码: wrongpass       | 应失败 | 实际: 失败
✅ PASS | 用户: nonexist   | 密码: anypass         | 应失败 | 实际: 失败

============================================================
测试完成
============================================================

🔍 检查端口占用...
✅ 端口 8501 可用

================================
📊 项目信息
================================
项目目录: /Users/xxx/ChangeFace
Python版本: Python 3.11.2
虚拟环境: /Users/xxx/ChangeFace/venv
监听端口: 8501

================================
🚀 准备启动应用
================================

选择启动方式：
  1) 正常启动 (默认)
  2) 启动并自动打开浏览器
  3) 调试模式启动
  4) 指定端口启动
  5) 仅检查，不启动
  q) 退出

请选择 (1-5 or q): 1

🎭 启动 Streamlit 应用...
================================

访问地址: http://localhost:8501
停止应用: Ctrl+C

  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.100:8501
```

### 示例 2: 日常开发（已配置）

```bash
$ bash test-local.sh

🧪 ChangeFace3 本地测试脚本
================================

🔍 检查环境...
✅ Python 3.11.2

📦 检查虚拟环境...
✅ 虚拟环境已存在

🔧 激活虚拟环境...
✅ 虚拟环境已激活

📥 检查依赖包...
✅ 所有依赖已安装

⚙️  检查配置文件...
✅ .env 文件存在
   ✅ REPLICATE_API_TOKEN 已配置

✅ users.txt 文件存在
   ℹ️  已配置用户数: 3

📄 检查必要文件...
✅ app.py
✅ config.py
✅ requirements.txt

✅ utils 目录存在
   ✅ utils/auth.py
   ✅ utils/face_swap.py
   ✅ utils/file_handler.py

🧪 运行功能测试...
[测试输出...]

🔍 检查端口占用...
✅ 端口 8501 可用

[启动选项...]
```

## 启动方式详解

### 1. 正常启动

```bash
选择: 1

# 特点
- 在 localhost:8501 启动
- 不自动打开浏览器
- 适合日常开发
```

### 2. 启动并打开浏览器

```bash
选择: 2

# 特点
- 在 localhost:8501 启动
- 自动打开默认浏览器
- 适合首次测试
```

### 3. 调试模式

```bash
选择: 3

# 特点
- 启用详细日志输出
- 文件修改自动重载
- 显示调试信息
- 适合开发调试
```

### 4. 自定义端口

```bash
选择: 4
请输入端口号: 3000

# 特点
- 使用指定端口启动
- 避免端口冲突
- 多实例运行
```

### 5. 仅检查

```bash
选择: 5

# 特点
- 完成所有检查
- 不启动应用
- 查看配置状态
- 运行测试
```

## 手动测试命令

如果需要手动测试，可以使用以下命令：

### 激活虚拟环境

```bash
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate.bat
```

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行测试

```bash
# 测试登录功能
python3 test_auth.py

# 测试哈希生成
python3 generate_hash.py
```

### 启动应用

```bash
# 默认启动
streamlit run app.py

# 指定地址和端口
streamlit run app.py --server.address=localhost --server.port=8501

# 调试模式
streamlit run app.py --logger.level=debug

# 自动打开浏览器
streamlit run app.py --server.headless=false
```

## 常见问题

### 1. 端口被占用

**错误信息：**
```
⚠️  端口 8501 已被占用 (PID: 12345)
```

**解决方法：**
```bash
# 停止占用进程
kill -9 12345

# 或选择其他端口
选择: 4
请输入端口号: 8502
```

### 2. 虚拟环境激活失败

**错误信息：**
```
❌ 虚拟环境激活失败
```

**解决方法：**
```bash
# 删除旧虚拟环境
rm -rf venv

# 重新运行测试脚本
bash test-local.sh
```

### 3. 依赖安装失败

**错误信息：**
```
ERROR: Could not install packages...
```

**解决方法：**
```bash
# 升级 pip
python3 -m pip install --upgrade pip

# 手动安装
pip install -r requirements.txt -v
```

### 4. 配置文件缺失

**错误信息：**
```
⚠️  .env 文件不存在
```

**解决方法：**
脚本会自动创建，或手动复制：
```bash
cp .env.example .env
cp users.txt.example users.txt
```

## 开发流程建议

### 日常开发

```bash
# 1. 运行测试脚本
bash test-local.sh

# 2. 选择调试模式（选项 3）
选择: 3

# 3. 开发时修改代码，应用自动重载

# 4. 停止应用
Ctrl+C
```

### 提交代码前

```bash
# 1. 运行测试
bash test-local.sh
选择: 5  # 仅检查

# 2. 确认所有测试通过

# 3. 提交代码
git add .
git commit -m "your message"
git push
```

### 调试问题

```bash
# 1. 启用调试模式
bash test-local.sh
选择: 3

# 2. 查看详细日志
# 3. 修复问题
# 4. 验证修复
```

## 脚本参数

测试脚本暂不支持命令行参数，但可以通过环境变量控制：

```bash
# 指定端口
PORT=3000 bash test-local.sh

# 跳过测试
SKIP_TESTS=1 bash test-local.sh
```

## 下一步

测试通过后：

1. **配置 API Token**
   ```bash
   vim .env
   # 填入 REPLICATE_API_TOKEN
   ```

2. **配置用户账号**
   ```bash
   vim users.txt
   # 添加/修改用户
   ```

3. **开始开发**
   ```bash
   bash test-local.sh
   ```

4. **部署到服务器**
   ```bash
   # 查看部署文档
   cat DEPLOY_GUIDE.md
   ```

## 相关文档

- **部署指南**: `DEPLOY_GUIDE.md`
- **登录功能**: `LOGIN_GUIDE.md`
- **端口配置**: `PORT_CONFIG.md`
- **脚本说明**: `SCRIPTS.md`
