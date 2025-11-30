import requests
from config import REPLICATE_API_TOKEN, AKOOL_API_KEY, API_CONFIGS, FACE_SWAP_MODEL

# Replicate is optional - only needed if using okaris_roop model
try:
    import replicate
except ImportError:
    replicate = None


def swap_face_akool(face_image_path: str, video_path: str, progress_callback=None) -> str:
    """
    使用 Akool API 进行视频换脸 (效果最好)

    Args:
        face_image_path: 要替换的脸部照片路径
        video_path: 源视频路径
        progress_callback: 可选的进度回调函数

    Returns:
        result_video_url: 处理后的视频 URL
    """
    from utils.akool_client import swap_face_akool as akool_swap

    if not AKOOL_API_KEY:
        raise ValueError("请在 .env 文件中设置 AKOOL_API_KEY")

    return akool_swap(
        face_image_path=face_image_path,
        video_path=video_path,
        api_key=AKOOL_API_KEY,
        face_enhance=True,
        progress_callback=progress_callback
    )


def swap_face_replicate_roop(face_image_path: str, video_path: str) -> str:
    """
    使用 Replicate okaris/roop API 进行换脸

    Args:
        face_image_path: 要替换的脸部照片路径
        video_path: 源视频路径

    Returns:
        result_video_url: 处理后的视频 URL
    """
    if replicate is None:
        raise ImportError("replicate 模块未安装。请运行: pip install replicate")
    if not REPLICATE_API_TOKEN:
        raise ValueError("请在 .env 文件中设置 REPLICATE_API_TOKEN")

    # 打开文件并调用 API
    with open(face_image_path, 'rb') as face_file:
        with open(video_path, 'rb') as video_file:
            output = replicate.run(
                API_CONFIGS["okaris_roop"]["model"],
                input={
                    "source": face_file,      # okaris/roop 使用 "source"
                    "target": video_file,      # okaris/roop 使用 "target"
                    "keep_fps": True,          # 保持原始帧率
                    "keep_frames": True,       # 保持帧一致性
                    "enhance_face": False      # 不增强面部（更快）
                }
            )

    # 处理 generator 返回结果
    if hasattr(output, '__iter__') and not isinstance(output, (str, bytes)):
        result_list = list(output)
        if len(result_list) > 0:
            return result_list[0]
        else:
            raise Exception("API 没有返回结果")

    # 如果直接是字符串，直接返回
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


def estimate_cost(video_duration_seconds: int, model: str = None) -> float:
    """
    估算换脸成本

    Args:
        video_duration_seconds: 视频时长（秒）
        model: 使用的模型 (默认使用配置的FACE_SWAP_MODEL)

    Returns:
        cost_usd: 预估成本（美元）
    """
    model = model or FACE_SWAP_MODEL

    if model == "akool":
        # Akool: 10 credits per 10 seconds, roughly $0.10 per 10 seconds
        return (video_duration_seconds / 10) * API_CONFIGS["akool"]["cost_per_10s"]
    elif model == "okaris_roop":
        return API_CONFIGS["okaris_roop"]["cost"]
    elif model == "replicate_roop":
        return API_CONFIGS["replicate_roop"]["cost"]
    elif model == "vmodel":
        return video_duration_seconds * API_CONFIGS["vmodel"]["cost_per_second"]
    else:
        return 0


def swap_face(face_image_path: str, video_path: str, model: str = None, progress_callback=None) -> str:
    """
    通用换脸函数，根据配置自动选择 API

    Args:
        face_image_path: 要替换的脸部照片路径
        video_path: 源视频路径
        model: 使用的模型 (默认使用配置的FACE_SWAP_MODEL)
        progress_callback: 可选的进度回调函数

    Returns:
        result_video_url: 处理后的视频 URL
    """
    model = model or FACE_SWAP_MODEL

    if model == "akool":
        return swap_face_akool(face_image_path, video_path, progress_callback)
    elif model == "okaris_roop":
        return swap_face_replicate_roop(face_image_path, video_path)
    else:
        raise ValueError(f"不支持的模型: {model}")


def get_available_models() -> list:
    """
    获取当前可用的模型列表（已配置API Key的模型）

    Returns:
        list: 可用模型名称列表
    """
    available = []

    if AKOOL_API_KEY:
        available.append("akool")
    if REPLICATE_API_TOKEN:
        available.append("okaris_roop")

    return available


def get_model_info(model: str = None) -> dict:
    """
    获取模型配置信息

    Args:
        model: 模型名称 (默认使用配置的FACE_SWAP_MODEL)

    Returns:
        dict: 模型配置信息
    """
    model = model or FACE_SWAP_MODEL
    return API_CONFIGS.get(model, {})
