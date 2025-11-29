import os
import uuid
from pathlib import Path
import time
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
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            file_age = current_time - os.path.getmtime(file_path)
            if file_age > max_age_seconds:
                try:
                    os.remove(file_path)
                    print(f"Deleted old file: {filename}")
                except Exception as e:
                    print(f"Error deleting {filename}: {e}")
