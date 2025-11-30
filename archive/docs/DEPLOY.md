# 阿里云部署指南

## 快速解决方案

根据你遇到的错误选择对应的解决方案：

### 方案 1：安装系统依赖（推荐，需要 sudo 权限）

```bash
# 解压应用包
tar zxvf /home/admin/app/package.tgz -C /home/admin/app/
cd /home/admin/app/

# 安装系统依赖
bash install-deps.sh

# 启动应用
sh start-aliyun.sh
```

**优点：** 使用标准的 Python venv，稳定可靠
**缺点：** 需要 sudo 权限

---

### 方案 2：使用改进的 start-aliyun.sh（自动回退）

```bash
# 解压应用包
tar zxvf /home/admin/app/package.tgz -C /home/admin/app/
cd /home/admin/app/

# 直接启动（脚本会自动处理 venv 不可用的情况）
sh start-aliyun.sh
```

**优点：** 脚本会自动尝试备用方案（--without-pip + 手动安装 pip）
**缺点：** 需要能访问 bootstrap.pypa.io

---

### 方案 3：使用 virtualenv（不需要 python3-venv）

```bash
# 解压应用包
tar zxvf /home/admin/app/package.tgz -C /home/admin/app/
cd /home/admin/app/

# 使用 virtualenv 版本
sh start-aliyun-virtualenv.sh
```

**优点：** 不需要系统的 python3-venv 包
**缺点：** 需要先安装 virtualenv（脚本会自动尝试安装）

---

## 常见错误及解决方案

### 错误 1: `ensurepip is not available`

```
The virtual environment was not created successfully because ensurepip is not available.
```

**原因：** 系统缺少 `python3-venv` 包

**解决方案：**
1. 有 sudo 权限：运行 `bash install-deps.sh`
2. 没有 sudo 权限：使用 `start-aliyun-virtualenv.sh`

---

### 错误 2: `source: not found`

```
/home/admin/app/start.sh: 18: source: not found
```

**原因：** 使用 `sh` 而非 `bash` 执行脚本，`source` 命令不兼容

**解决方案：** 使用新的 `start-aliyun.sh` 脚本，已修复兼容性

---

### 错误 3: `externally-managed-environment`

```
error: externally-managed-environment
```

**原因：** Python 3.11+ 的 PEP 668 保护机制

**解决方案：** 所有新脚本都使用虚拟环境，已解决此问题

---

## 部署流程对比

| 步骤 | 方案 1 (推荐) | 方案 2 (自动) | 方案 3 (virtualenv) |
|------|--------------|--------------|---------------------|
| 需要 sudo | ✅ 是 | ❌ 否 | ❌ 否 |
| 安装依赖 | `bash install-deps.sh` | - | - |
| 启动命令 | `sh start-aliyun.sh` | `sh start-aliyun.sh` | `sh start-aliyun-virtualenv.sh` |
| 稳定性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## 文件清单

部署所需文件：
- `start-aliyun.sh` - 主启动脚本（自动回退支持）
- `start-aliyun-virtualenv.sh` - virtualenv 版本启动脚本
- `install-deps.sh` - 系统依赖安装脚本
- `.env.example` - 环境变量模板
- `requirements.txt` - Python 依赖列表
- `app.py` - 主应用文件

---

## 环境变量配置

启动前需要配置 `.env` 文件：

```bash
# 方法 1: 部署前在本地创建
cp .env.example .env
vim .env  # 填入你的 REPLICATE_API_TOKEN

# 方法 2: 让脚本自动创建，然后手动编辑
# 脚本会自动从 .env.example 复制
```

获取 Replicate API Token：https://replicate.com/account/api-tokens

---

## 端口说明

应用启动后监听：
- **地址：** 0.0.0.0
- **端口：** 8501

请确保阿里云安全组已开放 8501 端口。

---

## 故障排查

### 查看详细日志

如果启动失败，检查以下日志：
```bash
cat /tmp/venv_error.log
cat /tmp/venv_error2.log
```

### 手动测试虚拟环境

```bash
# 测试 venv
python3 -m venv test_venv

# 测试 virtualenv
python3 -m virtualenv test_venv

# 清理
rm -rf test_venv
```

### 检查 Python 环境

```bash
python3 --version
python3 -m pip --version
```

---

## 需要帮助？

如果以上方案都无法解决问题，请提供以下信息：
1. 完整的错误日志
2. `python3 --version` 的输出
3. `cat /etc/os-release` 的输出
4. 是否有 sudo 权限
