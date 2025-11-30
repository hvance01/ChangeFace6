#!/usr/bin/env python3
"""
独立测试脚本 - 测试 Replicate API 调用
使用 input2 目录下的测试文件
"""

import os
import sys
from dotenv import load_dotenv
import replicate

# 加载环境变量
load_dotenv()

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

if not REPLICATE_API_TOKEN:
    print("❌ 错误: 未找到 REPLICATE_API_TOKEN")
    print("请在 .env 文件中设置 API Token")
    sys.exit(1)

print(f"✅ API Token 已加载: {REPLICATE_API_TOKEN[:10]}...")

# 测试文件路径
FACE_IMAGE = "input2/target.jpg"
VIDEO_FILE = "input2/target.mp4"

# 检查文件是否存在
if not os.path.exists(FACE_IMAGE):
    print(f"❌ 错误: 找不到文件 {FACE_IMAGE}")
    sys.exit(1)

if not os.path.exists(VIDEO_FILE):
    print(f"❌ 错误: 找不到文件 {VIDEO_FILE}")
    sys.exit(1)

print(f"✅ 找到测试文件:")
print(f"   - 照片: {FACE_IMAGE} ({os.path.getsize(FACE_IMAGE)/1024:.1f} KB)")
print(f"   - 视频: {VIDEO_FILE} ({os.path.getsize(VIDEO_FILE)/1024/1024:.1f} MB)")

print("\n" + "="*60)
print("开始测试 Replicate API 调用...")
print("="*60 + "\n")

try:
    # 打开文件
    print("📂 正在打开文件...")
    with open(FACE_IMAGE, 'rb') as face_file:
        with open(VIDEO_FILE, 'rb') as video_file:
            print("✅ 文件已打开")

            print("\n🚀 调用 Replicate API...")
            print("   模型: okaris/roop:8c1e100e (最新版本)")
            print("   参数:")
            print("   - source: 照片文件")
            print("   - target: 视频文件")
            print("   - keep_fps: True")
            print("   - keep_frames: True")
            print("   - enhance_face: False")

            # 调用 API - 使用完整版本哈希
            output = replicate.run(
                "okaris/roop:8c1e100ecabb3151cf1e6c62879b6de7a4b84602de464ed249b6cff0b86211d8",
                input={
                    "source": face_file,
                    "target": video_file,
                    "keep_fps": True,
                    "keep_frames": True,
                    "enhance_face": False
                }
            )

            print("\n✅ API 调用成功!")
            print(f"\n📤 返回结果类型: {type(output)}")

            # 处理 generator 返回结果
            if hasattr(output, '__iter__') and not isinstance(output, (str, bytes)):
                print("📥 正在获取结果...")
                result_list = list(output)
                print(f"📦 结果数量: {len(result_list)}")

                if len(result_list) > 0:
                    result_url = result_list[0]
                    print(f"🎬 结果视频 URL: {result_url}")
                else:
                    print("❌ 没有返回结果")
                    sys.exit(1)
            else:
                result_url = output
                print(f"🎬 结果视频 URL: {result_url}")

            print("\n" + "="*60)
            print("✅ 测试成功!")
            print("="*60)
            print(f"\n您可以访问以下 URL 下载结果视频:")
            print(result_url)

except Exception as e:
    print("\n" + "="*60)
    print("❌ 测试失败!")
    print("="*60)
    print(f"\n错误类型: {type(e).__name__}")
    print(f"错误信息: {str(e)}")

    # 打印详细的堆栈信息
    import traceback
    print("\n详细错误信息:")
    print(traceback.format_exc())

    sys.exit(1)
