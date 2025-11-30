# 部署脚本说明

本项目提供多个部署脚本，适用于不同场景。

## 🚀 快速开始（推荐）

### 在阿里云 ECS 上一键部署

```bash
# 克隆代码
git clone https://你的仓库地址.git /home/admin/app
cd /home/admin/app

# 设置 API Token（可选）
export REPLICATE_API_TOKEN="r8_your_token_here"

# 运行一键部署脚本
bash deploy.sh
```

就这么简单！脚本会自动：
- ✅ 检查 Python 和 Git 环境
- ✅ 创建虚拟环境
- ✅ 安装所有依赖
- ✅ 配置环境变量
- ✅ 启动应用

---

## 📜 脚本列表

### 1. 核心部署脚本

| 脚本 | 用途 | 使用场景 |
|------|------|----------|
| `deploy.sh` | 一键完整部署 | 首次部署或完整重置 |
| `restart.sh` | 快速重启 | 日常重启，不重建环境 |

### 2. 打包部署脚本

| 脚本 | 用途 | 使用场景 |
|------|------|----------|
| `package.sh` | 打包应用为 .tgz | 本地打包后上传部署 |
| `start.sh` | 解压后启动 | 从打包文件部署 |
| `start-aliyun.sh` | 阿里云优化版启动 | 解决 venv 和端口问题 |
| `start-aliyun-virtualenv.sh` | 使用 virtualenv 启动 | python3-venv 不可用时 |

### 3. 系统服务脚本

| 脚本 | 用途 | 使用场景 |
|------|------|----------|
| `install-service.sh` | 安装为 systemd 服务 | 生产环境后台运行 |
| `changeface.service` | systemd 服务配置 | 配合 install-service.sh |

### 4. 端口配置脚本

| 脚本 | 用途 | 使用场景 |
|------|------|----------|
| `start-port.sh` | 自定义端口启动 | 需要特定端口 |
| `setup-port-forward.sh` | 配置端口转发 | 80/443 → 8501 |

### 5. 依赖安装脚本

| 脚本 | 用途 | 使用场景 |
|------|------|----------|
| `install-deps.sh` | 安装系统依赖 | 缺少 python3-venv 等 |

---

## 🎯 使用场景

### 场景 1: 在阿里云 ECS 上从零开始

```bash
# 最简单的方式
git clone <仓库地址> /home/admin/app
cd /home/admin/app
bash deploy.sh
```

### 场景 2: 本地打包后上传部署

```bash
# 本地打包
bash package.sh

# 上传到服务器
scp package.tgz root@服务器IP:/home/admin/app/

# 服务器上解压并启动
tar zxvf /home/admin/app/package.tgz -C /home/admin/app/
sh /home/admin/app/start-aliyun.sh
```

### 场景 3: 后台持久运行（推荐生产环境）

```bash
# 首次部署
bash deploy.sh

# 安装为系统服务
sudo bash install-service.sh

# 以后使用 systemd 管理
sudo systemctl start changeface
sudo systemctl status changeface
```

### 场景 4: 使用标准 HTTP 端口

```bash
# 方案 A: 端口转发（推荐）
sudo bash setup-port-forward.sh
bash deploy.sh

# 方案 B: 直接使用 80 端口
export PORT=80
sudo bash deploy.sh
```

### 场景 5: 日常更新代码

```bash
# 拉取最新代码
git pull

# 快速重启
bash restart.sh
```

---

## 📚 详细文档

- **[DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)** - 完整部署指南
- **[PORT_CONFIG.md](PORT_CONFIG.md)** - 端口配置详解
- **[DEPLOY.md](DEPLOY.md)** - 部署方案对比

---

## 🔧 环境变量

所有脚本支持以下环境变量：

```bash
# 应用目录
export APP_DIR="/home/admin/app"

# Git 仓库（用于 deploy.sh）
export GIT_REPO="https://github.com/你的用户名/ChangeFace.git"
export GIT_BRANCH="main"

# 监听端口
export PORT=8501

# API Token
export REPLICATE_API_TOKEN="r8_xxxxx"
```

---

## 💡 最佳实践

### 生产环境推荐配置

```bash
# 1. 首次部署
git clone <仓库> /opt/changeface
cd /opt/changeface
export REPLICATE_API_TOKEN="你的token"
bash deploy.sh

# 2. 安装为系统服务
sudo bash install-service.sh

# 3. 配置端口转发
sudo bash setup-port-forward.sh

# 4. 配置自动更新（可选）
crontab -e
# 添加: 0 2 * * * cd /opt/changeface && git pull && sudo systemctl restart changeface
```

### 开发环境快速测试

```bash
# 克隆代码
git clone <仓库> ~/changeface
cd ~/changeface

# 快速启动
bash deploy.sh
```

---

## 🆘 故障排查

### 常见问题

1. **虚拟环境创建失败**
   ```bash
   sudo apt install -y python3-venv python3-dev
   ```

2. **端口被占用**
   ```bash
   # 查看占用进程
   lsof -i:8501

   # 停止进程
   kill -9 $(lsof -ti:8501)
   ```

3. **依赖安装失败**
   ```bash
   # 手动安装
   source venv/bin/activate
   pip install -r requirements.txt -v
   ```

4. **systemd 服务无法启动**
   ```bash
   # 查看详细日志
   sudo journalctl -u changeface -xe

   # 检查服务配置
   sudo systemctl status changeface
   ```

---

## 📞 获取帮助

遇到问题？
1. 查看详细文档：`DEPLOY_GUIDE.md`
2. 检查日志：`sudo journalctl -u changeface -f`
3. 提交 Issue 到 GitHub 仓库
