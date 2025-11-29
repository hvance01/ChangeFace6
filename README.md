# ChangeFace3 - 视频换脸工具

一个基于 Streamlit 的视频换脸工具，专为大码男装等营销视频快速换脸而设计。

## ✨ 功能特点

- 🎭 一键视频换脸
- 🚀 快速处理（1-2分钟）
- 💰 成本低廉（¥0.8/次）
- 📱 界面简洁易用
- 🐍 100% Python 开发

## 🛠️ 技术栈

- **前端**: Streamlit
- **换脸API**: Replicate Roop
- **语言**: Python 3.8+

## 📦 快速开始

### 1. 环境准备

```bash
# 确保已安装 Python 3.8+
python --version

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置 API Token

```bash
# 复制配置文件模板
cp .env.example .env

# 编辑 .env 文件，填入你的 Replicate API Token
# 获取地址: https://replicate.com/account/api-tokens
```

`.env` 文件内容：
```
REPLICATE_API_TOKEN=r8_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. 运行应用

```bash
streamlit run app.py
```

应用会自动在浏览器打开: `http://localhost:8501`

## 📖 使用说明

### 操作步骤

1. 上传**头像照片**（要替换成的脸）
2. 上传**营销视频**（原始视频）
3. 点击**开始换脸**按钮
4. 等待处理完成（约1-2分钟）
5. 下载处理后的视频

### 文件要求

- **照片格式**: JPG, PNG
- **照片大小**: < 10MB
- **视频格式**: MP4, MOV
- **视频大小**: < 500MB
- **视频时长**: 建议 < 60秒

## 💰 成本说明

- **API 调用**: $0.11/次（约 ¥0.8）
- **不限视频长度**: 固定价格
- **使用的 API**: Replicate Roop Face Swap

## 📁 项目结构

```
ChangeFace3/
├── app.py                 # Streamlit 主应用
├── config.py             # 配置文件
├── requirements.txt      # Python 依赖
├── .env.example         # 环境变量模板
├── utils/
│   ├── __init__.py
│   ├── face_swap.py     # 换脸 API 调用
│   └── file_handler.py  # 文件处理
└── temp/                # 临时文件目录
    ├── uploads/         # 上传文件
    └── results/         # 处理结果
```

## 🚀 部署到生产环境

### Docker 部署

```bash
# 构建镜像
docker build -t changeface3 .

# 运行容器
docker run -d -p 8501:8501 \
  -e REPLICATE_API_TOKEN=your_token \
  --name changeface3 \
  changeface3
```

### 阿里云部署

详见 `云部署方案对比.md` 文档。

推荐配置:
- 轻量应用服务器 2核4G (298元/年)
- Ubuntu 22.04
- Nginx 反向代理

## ⚙️ 配置说明

### config.py

可以在 `config.py` 中修改：

- `MAX_FILE_SIZE`: 最大文件大小限制
- `FACE_SWAP_MODEL`: 选择不同的换脸模型
- `API_CONFIGS`: API 配置参数

## 🔧 故障排查

### 1. API Token 错误

```
❌ Error: authentication failed
```

**解决**: 检查 `.env` 文件中的 `REPLICATE_API_TOKEN` 是否正确配置。

### 2. 文件上传失败

```
❌ File size too large
```

**解决**: 压缩视频或调整 `config.py` 中的 `MAX_FILE_SIZE` 设置。

### 3. 处理超时

```
❌ Request timeout
```

**解决**: 视频文件过大或网络问题，尝试：
- 压缩视频
- 检查网络连接
- 等待更长时间

## 📊 性能说明

- **处理速度**: 约 1-2 分钟/视频
- **并发支持**: 单实例建议 < 10 并发
- **文件大小**: 建议 < 200MB
- **推荐场景**: Demo、MVP、内部工具

## 🔄 升级路线

### 当前阶段: Streamlit Demo
- ✅ 快速验证需求
- ✅ 单用户使用
- ✅ 最低成本

### 未来升级: 生产级应用
- [ ] 用户认证系统
- [ ] 数据库存储任务历史
- [ ] FastAPI + Next.js 前后端分离
- [ ] CDN 加速
- [ ] 多用户并发支持

## 📝 注意事项

1. **临时文件清理**: 系统会自动清理 24 小时前的临时文件
2. **隐私保护**: 不要上传包含敏感信息的视频
3. **版权问题**: 确保有权使用上传的照片和视频
4. **使用限制**: 仅用于合法用途，遵守相关法律法规

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 📮 联系方式

- 项目地址: https://github.com/your-repo/changeface3
- 问题反馈: 提交 GitHub Issue

---

Made with ❤️ for 大码男装营销视频换脸
