#!/usr/bin/env python3
"""
测试更新后的 face_swap.py 函数
"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.face_swap import swap_face_replicate_roop

print("="*60)
print("测试更新后的 swap_face_replicate_roop 函数")
print("="*60 + "\n")

FACE_IMAGE = "input2/target.jpg"
VIDEO_FILE = "input2/target.mp4"

try:
    print(f"📷 照片: {FACE_IMAGE}")
    print(f"🎬 视频: {VIDEO_FILE}\n")

    print("🚀 调用 swap_face_replicate_roop()...")
    result_url = swap_face_replicate_roop(FACE_IMAGE, VIDEO_FILE)

    print("\n✅ 函数调用成功!")
    print(f"🎬 结果视频 URL: {result_url}")

    print("\n" + "="*60)
    print("✅ 后端逻辑测试通过!")
    print("="*60)

except Exception as e:
    print("\n❌ 测试失败!")
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
