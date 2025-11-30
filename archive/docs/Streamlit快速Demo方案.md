# Streamlit 快速 Demo 方案

## 一、技术架构（极简版）

### 方案：Streamlit 单体应用 ⭐⭐⭐⭐⭐

```
┌─────────────────────────────────────────┐
│          用户浏览器                      │
└──────────────────┬──────────────────────┘
                   │ http://localhost:8501
                   ↓
┌─────────────────────────────────────────┐
│         Streamlit 应用 (Python)          │
│                                         │
│  ├─ 文件上传组件                         │
│  ├─ 进度显示                            │
│  ├─ 结果展示                            │
│  └─ 下载按钮                            │
│                                         │
│  内置功能:                              │
│  ├─ 临时文件存储                         │
│  ├─ 调用 Replicate API                 │
│  └─ 视频播放器                          │
└──────────────────┬──────────────────────┘
                   │
                   ↓
          Replicate API (换脸)
```

**优势:**
- ✅ 100% Python，无需学 JavaScript
- ✅ 10分钟搭建完成 UI
- ✅ 自带文件上传、视频播放等组件
- ✅ 一个文件搞定所有功能
- ✅ 适合快速验证需求

**劣势:**
- ❌ 不适合大规模生产环境
- ❌ 样式定制能力有限
- ❌ 多用户并发性能一般

**适用:** Demo、MVP、内部工具

---

## 二、完整代码实现

### 2.1 项目结构

```
ChangeFace3/
├── app.py                 # Streamlit 主应用
├── requirements.txt       # Python 依赖
├── config.py             # 配置文件
├── utils/
│   ├── __init__.py
│   ├── face_swap.py      # 换脸 API 调用
│   └── file_handler.py   # 文件处理
└── temp/                 # 临时文件目录
```

### 2.2 核心代码

#### `requirements.txt`
```txt
streamlit==1.40.0
replicate==0.25.0
python-dotenv==1.0.0
pillow==10.3.0
requests==2.32.0
```

#### `config.py`
```python
import os
from dotenv import load_dotenv

load_dotenv()

# Replicate API 配置
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

# 文件配置
UPLOAD_DIR = "temp/uploads"
RESULT_DIR = "temp/results"
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

# 确保目录存在
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)

# 换脸 API 选择
FACE_SWAP_MODEL = "replicate_roop"  # 或 "vmodel"

# API 配置
API_CONFIGS = {
    "replicate_roop": {
        "model": "arabyai-replicate/roop_face_swap",
        "cost": 0.11  # USD
    },
    "vmodel": {
        "api_url": "https://api.vmodel.ai/v1/video-face-swap",
        "cost_per_second": 0.03  # USD
    }
}
```

#### `utils/face_swap.py`
```python
import replicate
import requests
import time
from config import REPLICATE_API_TOKEN, API_CONFIGS

def swap_face_replicate_roop(face_image_path: str, video_path: str) -> str:
    """
    使用 Replicate Roop API 进行换脸

    Args:
        face_image_path: 要替换的脸部照片路径
        video_path: 源视频路径

    Returns:
        result_video_url: 处理后的视频 URL
    """
    client = replicate.Client(api_token=REPLICATE_API_TOKEN)

    # 上传文件到 Replicate（或使用公网可访问的URL）
    with open(face_image_path, 'rb') as f:
        face_image = f
        with open(video_path, 'rb') as v:
            video = v

            # 调用 API
            output = client.run(
                API_CONFIGS["replicate_roop"]["model"],
                input={
                    "swap_image": face_image,
                    "target_video": video
                }
            )

    return output


def swap_face_vmodel(face_image_url: str, video_url: str, api_key: str) -> dict:
    """
    使用 VModel API 进行换脸

    Args:
        face_image_url: 脸部照片的公网 URL
        video_url: 源视频的公网 URL
        api_key: VModel API Key

    Returns:
        result: 包含任务状态和结果 URL 的字典
    """
    url = API_CONFIGS["vmodel"]["api_url"]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "target_face": face_image_url,
        "source_video": video_url
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        result = response.json()
        return result
    else:
        raise Exception(f"API Error: {response.status_code} - {response.text}")


def estimate_cost(video_duration_seconds: int, model: str = "replicate_roop") -> float:
    """
    估算换脸成本

    Args:
        video_duration_seconds: 视频时长（秒）
        model: 使用的模型

    Returns:
        cost_usd: 预估成本（美元）
    """
    if model == "replicate_roop":
        return API_CONFIGS["replicate_roop"]["cost"]
    elif model == "vmodel":
        return video_duration_seconds * API_CONFIGS["vmodel"]["cost_per_second"]
    else:
        return 0
```

#### `utils/file_handler.py`
```python
import os
import uuid
from pathlib import Path
from config import UPLOAD_DIR, RESULT_DIR

def save_uploaded_file(uploaded_file, file_type="image") -> str:
    """
    保存上传的文件到临时目录

    Args:
        uploaded_file: Streamlit UploadedFile 对象
        file_type: 文件类型 ("image" 或 "video")

    Returns:
        file_path: 保存的文件路径
    """
    # 生成唯一文件名
    file_extension = Path(uploaded_file.name).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"

    # 确定保存路径
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # 保存文件
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return file_path


def cleanup_old_files(directory: str, max_age_hours: int = 24):
    """
    清理超过指定时间的旧文件

    Args:
        directory: 要清理的目录
        max_age_hours: 文件最大保留时间（小时）
    """
    import time

    current_time = time.time()
    max_age_seconds = max_age_hours * 3600

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            file_age = current_time - os.path.getmtime(file_path)
            if file_age > max_age_seconds:
                os.remove(file_path)
                print(f"Deleted old file: {filename}")
```

#### `app.py` - Streamlit 主应用
```python
import streamlit as st
import os
from pathlib import Path
from utils.face_swap import swap_face_replicate_roop, estimate_cost
from utils.file_handler import save_uploaded_file, cleanup_old_files
from config import UPLOAD_DIR, RESULT_DIR

# 页面配置
st.set_page_config(
    page_title="视频换脸工具 - ChangeFace3",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 标题
st.title("🎭 营销视频换脸工具")
st.markdown("---")

# 侧边栏 - 使用说明
with st.sidebar:
    st.header("📖 使用说明")
    st.markdown("""
    ### 操作步骤：
    1. 上传**头像照片**（要替换成的脸）
    2. 上传**营销视频**（原始视频）
    3. 点击**开始换脸**按钮
    4. 等待处理完成（约1-2分钟）
    5. 下载处理后的视频

    ### 文件要求：
    - **照片格式**：JPG, PNG
    - **照片大小**：< 10MB
    - **视频格式**：MP4, MOV
    - **视频大小**：< 500MB
    - **视频时长**：建议 < 60秒

    ### 💰 成本：
    - 每次处理：¥0.8 ($0.11)
    - 不限视频长度
    """)

    st.markdown("---")
    st.info("💡 提示：使用清晰的正面照片效果最佳")

# 主界面 - 分两列
col1, col2 = st.columns(2)

# 左列 - 上传文件
with col1:
    st.subheader("📤 步骤1: 上传文件")

    # 上传头像照片
    face_image = st.file_uploader(
        "上传头像照片 (要替换成的脸)",
        type=["jpg", "jpeg", "png"],
        help="请上传清晰的正面照片"
    )

    if face_image:
        st.image(face_image, caption="上传的头像", use_container_width=True)
        st.success(f"✅ 照片已上传: {face_image.name}")

    st.markdown("---")

    # 上传视频
    video_file = st.file_uploader(
        "上传营销视频 (原始视频)",
        type=["mp4", "mov"],
        help="请上传需要换脸的营销视频"
    )

    if video_file:
        st.video(video_file)
        st.success(f"✅ 视频已上传: {video_file.name}")

        # 显示文件信息
        file_size_mb = video_file.size / (1024 * 1024)
        st.info(f"📊 文件大小: {file_size_mb:.2f} MB")

# 右列 - 处理和结果
with col2:
    st.subheader("🎬 步骤2: 开始处理")

    # 开始换脸按钮
    if st.button("🚀 开始换脸", type="primary", use_container_width=True):
        if not face_image or not video_file:
            st.error("❌ 请先上传头像照片和视频！")
        else:
            try:
                # 显示处理状态
                with st.spinner("正在处理中，请稍候..."):
                    # 保存上传的文件
                    st.info("📁 正在保存文件...")
                    face_path = save_uploaded_file(face_image, "image")
                    video_path = save_uploaded_file(video_file, "video")

                    # 调用换脸 API
                    st.info("🎨 正在调用换脸 API...")
                    result_url = swap_face_replicate_roop(face_path, video_path)

                    # 保存结果到 session state
                    st.session_state.result_url = result_url
                    st.session_state.processing_complete = True

                st.success("✅ 处理完成！")
                st.balloons()

            except Exception as e:
                st.error(f"❌ 处理失败: {str(e)}")
                st.exception(e)

    # 显示结果
    if st.session_state.get("processing_complete", False):
        st.markdown("---")
        st.subheader("📥 步骤3: 下载结果")

        result_url = st.session_state.get("result_url")

        # 显示结果视频
        st.video(result_url)

        # 下载按钮
        st.markdown(f"[⬇️ 点击下载视频]({result_url})")

        st.success("🎉 视频换脸完成！您可以下载使用了。")

        # 重新开始按钮
        if st.button("🔄 处理新视频", use_container_width=True):
            st.session_state.processing_complete = False
            st.rerun()

# 页面底部
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray;">
    <p>Powered by Replicate Roop API | ChangeFace3 © 2025</p>
</div>
""", unsafe_allow_html=True)

# 后台任务：清理旧文件
cleanup_old_files(UPLOAD_DIR, max_age_hours=24)
cleanup_old_files(RESULT_DIR, max_age_hours=24)
```

---

## 三、本地运行步骤

### 3.1 环境准备

```bash
# 1. 创建项目目录
mkdir ChangeFace3
cd ChangeFace3

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 创建 .env 文件
echo "REPLICATE_API_TOKEN=your_api_token_here" > .env
```

### 3.2 获取 Replicate API Token

1. 访问 https://replicate.com
2. 注册/登录账号
3. 进入 Account Settings → API Tokens
4. 复制 API Token
5. 粘贴到 `.env` 文件

### 3.3 启动应用

```bash
streamlit run app.py
```

应用会自动在浏览器打开: `http://localhost:8501`

---

## 四、阿里云部署方案（简化版）

### 方案：单服务器部署

```bash
# 1. 购买阿里云轻量应用服务器
# 配置: 2核4G, 3M带宽, Ubuntu 22.04
# 成本: 298元/年

# 2. SSH 连接服务器
ssh root@your_server_ip

# 3. 安装 Python 和依赖
apt update
apt install -y python3 python3-pip python3-venv

# 4. 克隆代码或上传文件
mkdir /opt/changeface
cd /opt/changeface
# 上传所有代码文件

# 5. 安装依赖
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. 配置环境变量
nano .env
# 添加: REPLICATE_API_TOKEN=your_token

# 7. 安装 Nginx 反向代理
apt install -y nginx

# 8. 配置 Nginx
nano /etc/nginx/sites-available/changeface
```

### Nginx 配置文件
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 创建系统服务
```bash
# 创建 systemd 服务文件
nano /etc/systemd/system/changeface.service
```

```ini
[Unit]
Description=ChangeFace3 Streamlit App
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/changeface
Environment="PATH=/opt/changeface/venv/bin"
ExecStart=/opt/changeface/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

### 启动服务
```bash
# 启用 Nginx 配置
ln -s /etc/nginx/sites-available/changeface /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# 启动 Streamlit 服务
systemctl daemon-reload
systemctl start changeface
systemctl enable changeface

# 查看状态
systemctl status changeface
```

---

## 五、Docker 部署（推荐）

### `Dockerfile`
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8501

# 启动命令
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### `docker-compose.yml`
```yaml
version: '3.8'

services:
  streamlit:
    build: .
    ports:
      - "8501:8501"
    environment:
      - REPLICATE_API_TOKEN=${REPLICATE_API_TOKEN}
    volumes:
      - ./temp:/app/temp
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - streamlit
    restart: unless-stopped
```

### 部署命令
```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f streamlit

# 停止服务
docker-compose down
```

---

## 六、成本估算（Streamlit 方案）

### 阿里云单服务器部署

| 项目 | 配置 | 月成本 | 年成本 |
|------|------|--------|--------|
| **轻量服务器** | 2核4G 3M | 25元 | 298元 |
| **API 调用** | 1500次/月 | 1155元 | 13860元 |
| **总计** | - | **1180元** | **14158元** |

**说明:**
- ✅ 无需 OSS/CDN (临时文件存在服务器)
- ✅ 无需数据库 (session state 存内存)
- ✅ 无需 Redis
- ✅ 极简部署,成本最低

**适用场景:**
- Demo 演示
- 内部使用工具
- 日处理量 < 100次

---

## 七、优缺点对比

### Streamlit vs Next.js

| 对比项 | Streamlit | Next.js + FastAPI |
|--------|-----------|-------------------|
| **开发速度** | ⭐⭐⭐⭐⭐ 极快 | ⭐⭐⭐ 中等 |
| **代码量** | 1个文件 | 10+ 文件 |
| **学习成本** | 只需 Python | Python + JS/TS |
| **UI 定制** | ⭐⭐ 有限 | ⭐⭐⭐⭐⭐ 完全自由 |
| **并发性能** | ⭐⭐⭐ 中等 | ⭐⭐⭐⭐⭐ 很强 |
| **适用规模** | < 100 用户/天 | 大规模生产 |
| **部署复杂度** | ⭐ 极简 | ⭐⭐⭐⭐ 复杂 |
| **推荐场景** | MVP/Demo/内部工具 | 正式产品 |

---

## 八、升级路线图

### 阶段1: Streamlit Demo (现在)
```python
单文件应用
↓
快速验证需求
↓
收集用户反馈
```

### 阶段2: 加强版 Streamlit (1-2个月后)
```python
Streamlit + 数据库
↓
用户认证
↓
任务历史记录
```

### 阶段3: 生产级应用 (3个月后)
```python
FastAPI + Next.js
↓
前后端分离
↓
大规模部署
```

---

## 九、总结

### ✅ 为什么选 Streamlit?

1. **开发速度快**: 1天完成 vs 1周
2. **全Python**: 无需学 JS/TS
3. **成本最低**: 单服务器 298元/年
4. **部署简单**: 一条命令启动
5. **快速验证**: 适合 MVP 和 Demo

### 🎯 下一步

1. **立即开始**: 我帮您创建完整项目代码
2. **本地测试**: 10分钟跑通第一个 Demo
3. **阿里云部署**: 1小时上线

**需要我立即创建项目代码吗？** 我可以把所有文件都创建好,您直接运行即可!
