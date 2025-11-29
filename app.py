import streamlit as st
import os
from utils.face_swap import swap_face_replicate_roop, estimate_cost
from utils.file_handler import save_uploaded_file, cleanup_old_files
from utils.auth import AuthManager, show_login_page
from config import UPLOAD_DIR, RESULT_DIR

# 页面配置
st.set_page_config(
    page_title="视频换脸工具 - ChangeFace3",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化认证管理器
auth = AuthManager()

# 检查登录状态
if not auth.is_logged_in():
    show_login_page()
    st.stop()  # 停止执行后续代码

# 初始化 session state
if "processing_complete" not in st.session_state:
    st.session_state.processing_complete = False
if "result_url" not in st.session_state:
    st.session_state.result_url = None

# 标题
st.title("🎭 营销视频换脸工具")
st.markdown("### 一键替换视频中的人脸,快速生成个性化营销内容")
st.markdown("---")

# 侧边栏 - 使用说明
with st.sidebar:
    # 显示当前登录用户
    st.markdown(f"""
    <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
        <p style="margin: 0; color: #333;">👤 当前用户: <strong>{auth.get_current_user()}</strong></p>
    </div>
    """, unsafe_allow_html=True)

    # 登出按钮
    if st.button("🚪 退出登录", use_container_width=True):
        auth.logout()
        st.rerun()

    st.markdown("---")

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
    - 每次处理：约 ¥0.6 ($0.089)
    - 不限视频长度
    - 使用 okaris/roop 模型
    """)

    st.markdown("---")
    st.info("💡 提示：使用清晰的正面照片效果最佳")

    st.markdown("---")
    st.markdown("""
    ### 🔑 配置 API Token
    使用前请先配置 Replicate API Token:
    1. 访问 [Replicate](https://replicate.com)
    2. 注册并获取 API Token
    3. 在项目根目录创建 `.env` 文件
    4. 添加: `REPLICATE_API_TOKEN=your_token`
    """)

# 主界面 - 分两列
col1, col2 = st.columns(2)

# 左列 - 上传文件
with col1:
    st.subheader("📤 步骤1: 上传文件")

    # 上传头像照片
    face_image = st.file_uploader(
        "上传头像照片 (要替换成的脸)",
        type=["jpg", "jpeg", "png"],
        help="请上传清晰的正面照片",
        key="face_image_uploader"
    )

    if face_image:
        st.image(face_image, caption="上传的头像", use_container_width=True)
        st.success(f"✅ 照片已上传: {face_image.name}")

    st.markdown("---")

    # 上传视频
    video_file = st.file_uploader(
        "上传营销视频 (原始视频)",
        type=["mp4", "mov"],
        help="请上传需要换脸的营销视频",
        key="video_uploader"
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

    # 检查是否配置了 API Token
    from config import REPLICATE_API_TOKEN
    if not REPLICATE_API_TOKEN or REPLICATE_API_TOKEN == "your_replicate_api_token_here":
        st.error("❌ 未配置 Replicate API Token！")
        st.info("请查看左侧说明配置 API Token")
    else:
        st.success("✅ API Token 已配置")

    # 开始换脸按钮
    if st.button("🚀 开始换脸", type="primary", use_container_width=True, disabled=not REPLICATE_API_TOKEN or REPLICATE_API_TOKEN == "your_replicate_api_token_here"):
        if not face_image or not video_file:
            st.error("❌ 请先上传头像照片和视频！")
        else:
            try:
                # 创建进度容器
                progress_container = st.container()

                with progress_container:
                    # 进度条
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    # 步骤1: 保存文件
                    status_text.text("📁 正在保存文件...")
                    progress_bar.progress(20)
                    face_path = save_uploaded_file(face_image, "image")
                    video_path = save_uploaded_file(video_file, "video")

                    # 步骤2: 调用API
                    status_text.text("🎨 正在调用换脸 API，请稍候（约1-2分钟）...")
                    progress_bar.progress(40)

                    result_url = swap_face_replicate_roop(face_path, video_path)

                    # 步骤3: 完成
                    progress_bar.progress(100)
                    status_text.text("✅ 处理完成！")

                    # 保存结果到 session state
                    st.session_state.result_url = result_url
                    st.session_state.processing_complete = True

                st.success("✅ 视频换脸完成！")
                st.balloons()

            except Exception as e:
                st.error(f"❌ 处理失败: {str(e)}")
                st.exception(e)

                # 常见错误提示
                if "authentication" in str(e).lower() or "api" in str(e).lower():
                    st.info("💡 可能是 API Token 配置错误，请检查 .env 文件")

    # 显示结果
    if st.session_state.get("processing_complete", False):
        st.markdown("---")
        st.subheader("📥 步骤3: 下载结果")

        result_url = st.session_state.get("result_url")

        if result_url:
            # 将 FileOutput 对象转换为字符串
            result_url_str = str(result_url)

            # 只显示下载链接
            st.markdown(f"""
            ### ⬇️ 下载视频
            处理完成！点击下面的链接下载换脸后的视频：

            [🔗 点击下载视频]({result_url_str})

            **视频 URL:**
            ```
            {result_url_str}
            ```
            """)

            st.success("🎉 视频换脸完成！您可以下载使用了。")

            # 重新开始按钮
            if st.button("🔄 处理新视频", use_container_width=True):
                st.session_state.processing_complete = False
                st.session_state.result_url = None
                st.rerun()

# 页面底部
st.markdown("---")

# 显示一些统计信息
col_stat1, col_stat2, col_stat3 = st.columns(3)
with col_stat1:
    st.metric("处理成本", "¥0.6/次", help="使用 okaris/roop API")
with col_stat2:
    st.metric("处理时长", "约1分钟", help="根据视频大小而定")
with col_stat3:
    st.metric("支持格式", "MP4, MOV", help="照片支持 JPG, PNG")

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray;">
    <p>Powered by okaris/roop API on Replicate | ChangeFace3 © 2025</p>
    <p>适合大码男装等行业的营销视频快速换脸</p>
</div>
""", unsafe_allow_html=True)

# 后台任务：清理旧文件（24小时）
try:
    cleanup_old_files(UPLOAD_DIR, max_age_hours=24)
    cleanup_old_files(RESULT_DIR, max_age_hours=24)
except Exception as e:
    pass  # 静默失败，不影响主流程
