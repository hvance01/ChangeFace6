#!/usr/bin/env python3
"""
Akool API 端到端测试脚本
测试视频换脸完整流程
"""

import os
import sys

# 添加项目根目录到路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

from utils.akool_client import AkoolClient, swap_face_akool, upload_to_temp_hosting

# 测试文件路径
TEST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "input")
FACE_IMAGE = os.path.join(TEST_DIR, "target.jpg")
VIDEO_FILE = os.path.join(TEST_DIR, "target.mp4")


def test_api_connection():
    """测试API连接"""
    print("=" * 50)
    print("测试1: API连接测试")
    print("=" * 50)

    api_key = os.getenv("AKOOL_API_KEY")
    if not api_key:
        print("❌ 未找到 AKOOL_API_KEY")
        return False

    print(f"✅ API Key 已配置: {api_key[:10]}...")

    try:
        client = AkoolClient(api_key)
        credit_info = client.get_credit_info()
        print(f"✅ API连接成功!")
        print(f"   账户信息: {credit_info.get('data', {})}")
        return True
    except Exception as e:
        print(f"❌ API连接失败: {e}")
        return False


def test_file_upload():
    """测试文件上传"""
    print("\n" + "=" * 50)
    print("测试2: 文件上传测试")
    print("=" * 50)

    try:
        print(f"上传图片: {FACE_IMAGE}")
        image_url = upload_to_temp_hosting(FACE_IMAGE)
        print(f"✅ 图片上传成功: {image_url[:50]}...")

        print(f"上传视频: {VIDEO_FILE}")
        video_url = upload_to_temp_hosting(VIDEO_FILE)
        print(f"✅ 视频上传成功: {video_url[:50]}...")

        return image_url, video_url
    except Exception as e:
        print(f"❌ 文件上传失败: {e}")
        return None, None


def test_face_swap(face_url, video_url):
    """测试换脸API"""
    print("\n" + "=" * 50)
    print("测试3: 视频换脸测试")
    print("=" * 50)

    api_key = os.getenv("AKOOL_API_KEY")
    client = AkoolClient(api_key)

    try:
        # 检测人脸
        print("正在检测人脸...")
        detect_result = client.detect_faces(face_url, "image")
        faces = detect_result.get("data", {}).get("faces", [])
        if faces:
            landmarks = faces[0].get("landmarks_str")
            print(f"✅ 检测到人脸，landmarks: {landmarks[:30] if landmarks else 'N/A'}...")
        else:
            print("⚠️ 未检测到人脸，将使用自动检测")
            landmarks = None

        # 提交换脸任务
        print("正在提交换脸任务...")
        result = client.swap_face_video(
            source_face_url=face_url,
            target_video_url=video_url,
            source_landmarks=landmarks,
            face_enhance=True
        )

        job_id = result.get("data", {}).get("_id")
        print(f"✅ 任务已提交，Job ID: {job_id}")

        # 等待结果
        print("正在等待处理完成（可能需要2-5分钟）...")

        def progress_callback(status, message):
            print(f"   状态: {message}")

        result_url = client.wait_for_result(
            job_id=job_id,
            timeout=600,
            poll_interval=10,
            progress_callback=progress_callback
        )

        print(f"\n🎉 换脸成功!")
        print(f"📥 结果视频URL: {result_url}")
        return result_url

    except Exception as e:
        print(f"❌ 换脸失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_full_flow():
    """测试完整流程（使用高级函数）"""
    print("\n" + "=" * 50)
    print("测试4: 完整流程测试 (swap_face_akool)")
    print("=" * 50)

    def progress_callback(status, message):
        print(f"   [{status}] {message}")

    try:
        result_url = swap_face_akool(
            face_image_path=FACE_IMAGE,
            video_path=VIDEO_FILE,
            face_enhance=True,
            progress_callback=progress_callback
        )

        print(f"\n🎉 完整流程测试成功!")
        print(f"📥 结果视频URL: {result_url}")
        return result_url

    except Exception as e:
        print(f"❌ 完整流程测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    print("🚀 Akool API 端到端测试")
    print("=" * 50)
    print(f"人脸图片: {FACE_IMAGE}")
    print(f"测试视频: {VIDEO_FILE}")
    print("=" * 50)

    # 检查文件是否存在
    if not os.path.exists(FACE_IMAGE):
        print(f"❌ 人脸图片不存在: {FACE_IMAGE}")
        return
    if not os.path.exists(VIDEO_FILE):
        print(f"❌ 视频文件不存在: {VIDEO_FILE}")
        return

    print(f"✅ 测试文件已确认存在")

    # 测试1: API连接
    if not test_api_connection():
        print("\n❌ API连接失败，请检查API Key配置")
        return

    # 测试4: 完整流程（最简单的方式）
    result = test_full_flow()

    if result:
        print("\n" + "=" * 50)
        print("✅ 所有测试通过!")
        print("=" * 50)
        print(f"\n下载换脸后的视频: {result}")
    else:
        print("\n" + "=" * 50)
        print("❌ 测试失败")
        print("=" * 50)


if __name__ == "__main__":
    main()
