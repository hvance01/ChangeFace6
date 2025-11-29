# 阿里云 ECS 一键部署指南

本指南适用于直接在阿里云 ECS 上克隆代码并部署。

## 快速开始

### 首次部署

```bash
# 1. 登录到阿里云 ECS
ssh root@你的服务器IP

# 2. 安装必要依赖（如果还没安装）
sudo apt update
sudo apt install -y python3 python3-venv python3-dev git curl

# 3. 下载部署脚本
cd /home/admin
curl -O https://你的仓库/deploy.sh
# 或者直接克隆整个仓库
git clone https://你的仓库地址.git app
cd app

# 4. 配置环境变量（可选）
export REPLICATE_API_TOKEN="你的API密钥"

# 5. 运行一键部署脚本
bash deploy.sh
```

### 配置说明

`deploy.sh` 支持以下环境变量：

```bash
# 应用安装目录（默认: /home/admin/app）
export APP_DIR="/home/admin/app"

# Git 仓库地址（如果需要自动克隆）
export GIT_REPO="https://github.com/你的用户名/ChangeFace.git"

# Git 分支（默认: master）
export GIT_BRANCH="main"

# 监听端口（默认: 8501）
export PORT=8501

# Replicate API Token
export REPLICATE_API_TOKEN="r8_xxxxx"
```

### 完整示例

```bash
# 自定义配置并部署
export APP_DIR="/opt/changeface"
export GIT_REPO="https://github.com/你的用户名/ChangeFace.git"
export GIT_BRANCH="main"
export PORT=8501
export REPLICATE_API_TOKEN="r8_your_token_here"

bash deploy.sh
```

---

## 日常操作

### 重启应用

```bash
cd /home/admin/app
bash restart.sh
```

### 更新代码并重启

```bash
cd /home/admin/app
bash deploy.sh  # 会自动拉取最新代码并重启
```

### 停止应用

```bash
# 查找进程
lsof -ti:8501

# 停止进程
kill -9 $(lsof -ti:8501)
```

### 查看日志

```bash
# Streamlit 会输出到标准输出
# 建议使用 screen 或 nohup 运行

# 使用 screen（推荐）
screen -S changeface
bash restart.sh
# Ctrl+A+D 退出 screen

# 重新连接
screen -r changeface

# 使用 nohup
nohup bash restart.sh > /var/log/changeface.log 2>&1 &

# 查看日志
tail -f /var/log/changeface.log
```

---

## 端口配置

### 方案 1: 使用端口转发（推荐）

将 80/443 端口转发到 8501：

```bash
cd /home/admin/app
sudo bash setup-port-forward.sh
```

然后通过 http://你的IP 访问（自动转发到 8501）

### 方案 2: 直接使用 80 端口

```bash
export PORT=80
sudo bash deploy.sh
```

### 方案 3: 使用 Nginx 反向代理

参考 `PORT_CONFIG.md` 中的详细配置。

---

## 后台运行

### 使用 systemd（生产环境推荐）

创建服务文件 `/etc/systemd/system/changeface.service`：

```ini
[Unit]
Description=ChangeFace3 Streamlit Application
After=network.target

[Service]
Type=simple
User=admin
WorkingDirectory=/home/admin/app
Environment="PATH=/home/admin/app/venv/bin"
ExecStart=/home/admin/app/venv/bin/streamlit run app.py --server.address=0.0.0.0 --server.port=8501
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启用并启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable changeface
sudo systemctl start changeface

# 查看状态
sudo systemctl status changeface

# 查看日志
sudo journalctl -u changeface -f
```

### 使用 screen

```bash
# 创建 screen 会话
screen -S changeface

# 在 screen 中启动应用
cd /home/admin/app
bash restart.sh

# 退出 screen（不停止应用）
Ctrl+A, 然后按 D

# 重新连接到 screen
screen -r changeface

# 列出所有 screen 会话
screen -ls
```

### 使用 nohup

```bash
cd /home/admin/app
nohup bash restart.sh > /var/log/changeface.log 2>&1 &

# 查看日志
tail -f /var/log/changeface.log

# 停止
kill $(lsof -ti:8501)
```

---

## 自动更新脚本

创建自动更新脚本 `auto-update.sh`：

```bash
#!/bin/bash

cd /home/admin/app

# 拉取最新代码
git pull origin main

# 如果有更新，则重启
if [ $? -eq 0 ]; then
    echo "代码已更新，重启应用..."
    bash restart.sh
else
    echo "没有更新"
fi
```

配置定时任务（每天凌晨2点自动更新）：

```bash
crontab -e

# 添加以下行
0 2 * * * cd /home/admin/app && bash auto-update.sh
```

---

## 故障排查

### 1. 虚拟环境创建失败

```bash
# 安装 python3-venv
sudo apt install -y python3.11-venv python3.11-dev
```

### 2. 端口被占用

```bash
# 查看占用端口的进程
lsof -i:8501

# 停止进程
kill -9 <PID>
```

### 3. 依赖安装失败

```bash
# 手动安装
cd /home/admin/app
source venv/bin/activate
pip install -r requirements.txt -v
```

### 4. 无法访问应用

检查：
1. 应用是否正常运行：`lsof -i:8501`
2. 防火墙规则：`sudo iptables -L -n`
3. 阿里云安全组是否开放端口
4. 使用 `curl localhost:8501` 测试本地访问

---

## 安全建议

1. **不要以 root 用户运行应用**
   ```bash
   # 创建专用用户
   sudo useradd -m -s /bin/bash changeface
   sudo su - changeface
   ```

2. **配置防火墙**
   ```bash
   # 只开放必要端口
   sudo ufw allow 22/tcp    # SSH
   sudo ufw allow 80/tcp    # HTTP
   sudo ufw allow 443/tcp   # HTTPS
   sudo ufw enable
   ```

3. **保护敏感信息**
   - 不要将 `.env` 文件提交到 git
   - 定期更新 API Token
   - 使用环境变量而非硬编码

4. **定期备份**
   ```bash
   # 备份应用数据
   tar czf /backup/changeface-$(date +%Y%m%d).tar.gz /home/admin/app
   ```

---

## 性能优化

### 1. 使用 Gunicorn（如果需要更高并发）

安装：
```bash
pip install gunicorn
```

启动：
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:8501
```

### 2. 配置 Nginx 缓存

在 Nginx 配置中添加：
```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m;

location / {
    proxy_cache my_cache;
    proxy_pass http://localhost:8501;
}
```

### 3. 监控资源使用

```bash
# 安装 htop
sudo apt install htop

# 查看资源使用
htop

# 查看应用内存使用
ps aux | grep streamlit
```

---

## 快速命令速查表

```bash
# 首次部署
bash deploy.sh

# 快速重启
bash restart.sh

# 停止应用
kill -9 $(lsof -ti:8501)

# 查看日志（如果使用 systemd）
sudo journalctl -u changeface -f

# 更新代码
git pull && bash restart.sh

# 检查端口
lsof -i:8501

# 配置端口转发
sudo bash setup-port-forward.sh
```
