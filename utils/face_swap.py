import replicate
import requests
from config import REPLICATE_API_TOKEN, API_CONFIGS, FACE_SWAP_MODEL


def swap_face_replicate_roop(face_image_path: str, video_path: str) -> str:
    """
    使用 Replicate okaris/roop API 进行换脸

    Args:
        face_image_path: 要替换的脸部照片路径
        video_path: 源视频路径

    Returns:
        result_video_url: 处理后的视频 URL
    """
    if not REPLICATE_API_TOKEN:
        raise ValueError("请在 .env 文件中设置 REPLICATE_API_TOKEN")

    # 打开文件并调用 API
    with open(face_image_path, 'rb') as face_file:
        with open(video_path, 'rb') as video_file:
            output = replicate.run(
                API_CONFIGS[FACE_SWAP_MODEL]["model"],
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
