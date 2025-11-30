# ChangeFace - 视频换脸工具

基于 Streamlit 的视频换脸工具，使用 Akool API 实现高质量视频换脸。

## 目录结构

```
ChangeFace/
├── app.py                  # Streamlit 主应用
├── config.py               # 配置文件
├── requirements.txt        # Python 依赖
├── .env.example            # 环境变量模板
├── users.txt.example       # 用户账号模板
├── start.sh                # Linux/Mac 启动脚本
├── start.bat               # Windows 启动脚本
├── utils/
│   ├── __init__.py
│   ├── akool_client.py     # Akool API 客户端
│   ├── auth.py             # 用户认证
│   ├── face_swap.py        # 换脸接口封装
│   └── file_handler.py     # 文件处理
├── tests/
│   ├── test_akool.py       # API 测试脚本
│   └── input/              # 测试数据
└── archive/                # 归档文件（旧文档和脚本）
```

---

## 快速开始

### 第一步：安装依赖

```bash
# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 第二步：获取 Akool API Key

1. 访问 [Akool 官网](https://akool.com) 并注册账号
2. 登录后，点击右上角 **API** 图标
3. 点击 **API Credentials**
4. 复制 **API Key**

### 第三步：配置环境变量

```bash
# 复制模板
cp .env.example .env

# 编辑 .env 文件
```

`.env` 文件内容：
```
AKOOL_API_KEY=你的API密钥
FACE_SWAP_MODEL=akool
```

### 第四步：配置用户账号

```bash
# 复制模板
cp users.txt.example users.txt

# 编辑 users.txt，格式：用户名:密码
echo "admin:admin123" > users.txt
```

### 第五步：运行应用

```bash
# 方式一：直接运行
streamlit run app.py

# 方式二：使用启动脚本
./start.sh        # Linux/Mac
start.bat         # Windows
```

浏览器访问：`http://localhost:8501`

---

## 测试 API 连接

在启动应用前，可以先测试 API 是否正常：

```bash
python tests/test_akool.py
```

成功输出示例：
```
✅ API连接成功!
   账户信息: {'credit': 505}
✅ 所有测试通过!
```

---

## 使用说明

### 操作步骤

1. 使用配置的用户名密码登录
2. 上传**头像照片**（要替换成的脸）
3. 上传**营销视频**（原始视频）
4. 点击**开始换脸**按钮
5. 等待处理完成（约2-5分钟）
6. 下载处理后的视频

### 文件要求

| 类型 | 格式 | 大小限制 |
|------|------|----------|
| 照片 | JPG, PNG | < 10MB |
| 视频 | MP4, MOV | < 500MB |

### 成本说明

- Akool API: 约 ¥0.7/10秒视频
- 账户余额可在 Akool 控制台查看

---

## 常见问题

### API Key 错误

```
❌ Akool API Error: Invalid API Key
```

**解决方案**：
1. 检查 `.env` 文件中 `AKOOL_API_KEY` 是否正确
2. 确认 API Key 没有过期

### 未检测到人脸

```
❌ No face detected in the source image
```

**解决方案**：
- 使用清晰的正面照片
- 确保照片中人脸清晰可见
- 避免使用侧脸或遮挡的照片

### 处理超时

```
❌ Video processing timed out
```

**解决方案**：
- 检查网络连接
- 尝试使用较短的视频
- 稍后重试

---

## 技术说明

- **前端框架**: Streamlit
- **换脸 API**: Akool High-Quality Face Swap
- **Python 版本**: 3.8+
- **认证方式**: 本地文件 + SHA256 哈希

---

## 许可证

MIT License
