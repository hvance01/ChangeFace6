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
FACE_SWAP_MODEL = "okaris_roop"  # 使用 okaris/roop 模型

# API 配置
API_CONFIGS = {
    "okaris_roop": {
        "model": "okaris/roop:8c1e100ecabb3151cf1e6c62879b6de7a4b84602de464ed249b6cff0b86211d8",
        "cost": 0.089  # USD (~$0.089 per run)
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
