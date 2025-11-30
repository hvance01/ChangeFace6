# CLAUDE.md

Claude Code 开发指南

## 项目概述

ChangeFace 是一个基于 Streamlit 的视频换脸工具，使用 Akool API 实现高质量视频换脸，主要用于营销视频个性化。

## 目录结构

```
ChangeFace/
├── app.py                  # Streamlit 主应用入口
├── config.py               # 配置（API密钥、文件限制、模型选择）
├── requirements.txt        # Python 依赖
├── utils/
│   ├── akool_client.py     # Akool API 客户端（核心）
│   ├── auth.py             # 用户认证（文件存储，SHA256哈希）
│   ├── face_swap.py        # 换脸接口封装（支持多模型）
│   └── file_handler.py     # 文件上传/清理工具
├── tests/
│   ├── test_akool.py       # API 端到端测试
│   └── input/              # 测试数据
└── archive/                # 归档文件（旧文档和脚本）
```

## 核心流程

1. 用户登录 → `AuthManager` 验证（凭据来自 `users.txt`）
2. 上传人脸图片 + 目标视频
3. 调用 `swap_face()` → 自动选择配置的模型（默认 Akool）
4. Akool 流程：
   - 上传文件到临时托管（tmpfiles.org）
   - 调用人脸检测 API 获取 landmarks
   - 提交换脸任务
   - 轮询等待结果
5. 返回结果视频 URL 供下载

## 常用命令

```bash
# 运行应用
streamlit run app.py

# 测试 API
python tests/test_akool.py

# 生成密码哈希（如需要）
python archive/generate_hash.py
```

## 配置说明

### 环境变量 (.env)

```
AKOOL_API_KEY=xxx           # Akool API 密钥（必需）
FACE_SWAP_MODEL=akool       # 使用的模型
```

### 用户账号 (users.txt)

```
username:password           # 明文（首次加载自动哈希）
username:hash:sha256        # 预哈希格式
```

## API 说明

### Akool API

- **文档**: https://docs.akool.com/ai-tools-suite/faceswap
- **认证**: x-api-key header
- **基础URL**: https://openapi.akool.com

关键端点：
- 人脸检测: `/interface/detect-api/detect_faces`
- 视频换脸: `/api/open/v3/faceswap/highquality/specifyvideo`
- 获取结果: `/api/open/v3/faceswap/result/listbyids`

### 响应格式

```python
# 成功响应
{"code": 1000, "msg": "OK", "data": {...}}

# 人脸检测响应
{"error_code": 0, "faces_obj": {"0": {"landmarks": [[[x,y],...]]}}}

# 结果响应
{"code": 1000, "data": {"result": [{"faceswap_status": 2, "url": "..."}]}}
```

状态码：
- `faceswap_status: 1` = 处理中
- `faceswap_status: 2` = 成功
- `faceswap_status: 3` = 失败

## 开发注意事项

1. **文件上传**: Akool 需要公网 URL，使用 tmpfiles.org 临时托管
2. **Landmarks**: 必须先调用人脸检测获取 landmarks 才能换脸
3. **轮询间隔**: 建议 5 秒，超时 10 分钟
4. **错误处理**: 区分网络错误（可重试）和 API 错误（不重试）

## 扩展方向

- [ ] 支持批量视频处理
- [ ] 添加视频预览功能
- [ ] 集成更多换脸模型（Replicate/腾讯云）
- [ ] 添加处理历史记录
- [ ] 优化大文件上传（分片上传）
