import os
from dotenv import load_dotenv

load_dotenv()

# Replicate API 配置
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

# Akool API 配置
# 获取方式: https://akool.com -> 登录 -> 点击API图标 -> API Credentials
AKOOL_API_KEY = os.getenv("AKOOL_API_KEY")

# 文件配置
UPLOAD_DIR = "temp/uploads"
RESULT_DIR = "temp/results"
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

# 确保目录存在
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)

# 换脸 API 选择
# 可选值: "akool" (推荐，效果最好), "okaris_roop" (备选)
FACE_SWAP_MODEL = os.getenv("FACE_SWAP_MODEL", "akool")

# API 配置
API_CONFIGS = {
    "akool": {
        "name": "Akool Face Swap",
        "description": "效果最好，支持4K，企业级服务",
        "base_url": "https://openapi.akool.com",
        "cost_per_10s": 0.10,  # USD per 10 seconds of video
        "max_resolution": "4K",
        "face_enhance": True,
        "requires": "AKOOL_API_KEY"
    },
    "okaris_roop": {
        "name": "Replicate Roop",
        "description": "开源模型，成本较低",
        "model": "okaris/roop:8c1e100ecabb3151cf1e6c62879b6de7a4b84602de464ed249b6cff0b86211d8",
        "cost": 0.089,  # USD (~$0.089 per run)
        "requires": "REPLICATE_API_TOKEN"
    },
    "replicate_roop": {
        "model": "arabyai-replicate/roop_face_swap",
        "cost": 0.11  # USD
    },
    "vmodel": {
        "api_url": "https://api.vmodel.ai/v1/video-face-swap",
        "cost_per_second": 0.03  # USD
    }
}
