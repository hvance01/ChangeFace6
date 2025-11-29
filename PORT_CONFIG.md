# 端口配置指南

## 问题描述

Streamlit 默认在 8501 端口启动，但标准 HTTP/HTTPS 服务使用 80/443 端口。
阿里云安全组已开放 80 和 443 端口。

## 解决方案

有三种方式配置端口：

---

## 方案 1：使用端口转发（推荐）⭐⭐⭐⭐⭐

**优点：** 不需要 root 权限运行应用，最安全
**原理：** 使用 iptables 将 80/443 转发到 8501

### 步骤：

1. **配置端口转发（需要 sudo，仅执行一次）**
```bash
sudo bash /home/admin/app/setup-port-forward.sh
```

2. **启动应用（不需要 sudo）**
```bash
sh /home/admin/app/start-aliyun.sh
```

3. **访问应用**
- http://你的服务器IP （通过80端口，自动转发到8501）
- http://你的服务器IP:8501 （直接访问8501）

### 规则说明

```bash
# 查看转发规则
sudo iptables -t nat -L PREROUTING -n | grep 8501

# 手动删除规则（如需要）
sudo iptables -t nat -D PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8501
sudo iptables -t nat -D PREROUTING -p tcp --dport 443 -j REDIRECT --to-port 8501
```

---

## 方案 2：直接使用 80 端口（需要 root）⭐⭐⭐

**优点：** 配置简单
**缺点：** 应用必须以 root 权限运行（安全风险）

```bash
# 使用 80 端口启动
sudo PORT=80 sh /home/admin/app/start-port.sh

# 使用 443 端口启动
sudo PORT=443 sh /home/admin/app/start-port.sh
```

访问地址：
- http://你的服务器IP （80端口）
- https://你的服务器IP （443端口，需要配置SSL证书）

---

## 方案 3：使用 Nginx 反向代理⭐⭐⭐⭐

**优点：** 最灵活，支持 SSL、负载均衡等高级功能
**适用：** 生产环境

### 安装 Nginx

```bash
sudo apt update
sudo apt install nginx
```

### 配置 Nginx

创建配置文件 `/etc/nginx/sites-available/changeface`：

```nginx
server {
    listen 80;
    server_name 你的域名或IP;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/changeface /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

启动应用：

```bash
sh /home/admin/app/start-aliyun.sh
```

---

## 端口占用问题

所有启动脚本都已包含端口检查和清理功能：

```bash
🔍 检查端口 8501...
⚠️  端口 8501 已被占用 (PID: 12345)
   正在停止旧进程...
✅ 旧进程已停止
```

如需手动检查：

```bash
# 查看占用端口的进程
lsof -i:8501
# 或
netstat -tulnp | grep 8501

# 手动停止进程
kill -9 <PID>
```

---

## 安全建议

1. **生产环境推荐：** 方案 1（端口转发）或 方案 3（Nginx）
2. **避免以 root 运行应用**（方案 2）
3. **配置防火墙：** 仅开放必要端口
4. **使用 HTTPS：** 配置 SSL 证书（Let's Encrypt）

---

## 快速启动命令

### 首次部署（推荐方案 1）

```bash
# 1. 解压应用
tar zxvf /home/admin/app/package.tgz -C /home/admin/app/

# 2. 配置端口转发（需要 sudo，仅一次）
sudo bash /home/admin/app/setup-port-forward.sh

# 3. 启动应用
sh /home/admin/app/start-aliyun.sh

# 4. 访问 http://你的IP
```

### 日常重启

```bash
# 只需要执行
sh /home/admin/app/start-aliyun.sh
```

---

## 故障排查

### 1. 端口转发不生效

```bash
# 检查规则是否存在
sudo iptables -t nat -L PREROUTING -n | grep 8501

# 检查应用是否在 8501 监听
netstat -tuln | grep 8501
```

### 2. 无法访问

检查阿里云安全组：
- 80 端口已开放（入方向）
- 443 端口已开放（入方向）

### 3. Permission denied

端口 < 1024 需要 root 权限，使用方案 1 的端口转发。
