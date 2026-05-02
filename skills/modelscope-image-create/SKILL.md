---
name: modelscope-image-create
description: 使用 ModelScope API 生成和编辑 AI 图像。支持文生图（Qwen-Image、FLUX、Z-Image 等）和图像编辑（Qwen-Image-Edit），通过文本提示词生成或编辑高质量图像。当用户需要生成图片、编辑图片、文生图、AI 绘画时使用此技能。
---

# ModelScope 图像生成与编辑

## 概述

使用 ModelScope 平台的 AI 图像 API，通过自然语言描述生成或编辑高质量图像。支持多种主流模型。

**核心功能**：
- 文本生成图像（文生图）✅ 完全可用
- 图像编辑（Qwen-Image-Edit）✅ API 正常响应
- 支持多种主流模型
- 支持 URL、Base64 编码等图片输入方式

## 快速参考

### 图像生成 ✅ 完全可用

| 任务 | 命令 | 说明 |
|------|------|------|
| **基础生成** | `python scripts/generate_image.py --prompt "描述文字"` | 使用默认模型 |
| **指定模型** | `python scripts/generate_image.py --prompt "描述" --model Qwen/Qwen-Image` | 仅在需要时指定 |
| **指定尺寸** | `python scripts/generate_image.py --prompt "描述" --size 1024x1024` |  |
| **负向提示词** | `python scripts/generate_image.py --prompt "描述" --negative-prompt "模糊,低质量"` |  |
| **保存路径** | `python scripts/generate_image.py --prompt "描述" --output ./result.png` |  |

### 图像编辑 ✅ API 正常响应

| 任务 | 命令 | 说明 |
|------|------|------|
| **编辑本地图片** | `python scripts/edit_image.py --image input.png --prompt "编辑描述"` | 本地文件自动 Base64 编码 |
| **使用在线 URL** | `python scripts/edit_image.py --image "https://example.com/photo.jpg" --prompt "编辑描述"` | 公网可访问地址 |
| **使用 LoRA** | `python scripts/edit_image.py --image input.png --prompt "风格转换" --loras "<lora-id>"` | 可选 LoRA 模型 |

### 模型查询

| 任务 | 命令 |
|------|------|
| **列出模型** | `python scripts/list_models.py` |
| **搜索模型** | `python scripts/list_models.py --search "flux"` |

## 核心工作流

### 1. 图像生成

```bash
python scripts/generate_image.py --prompt "A cute golden cat sitting on a cloud"
```

### 2. 图像编辑

```bash
# 编辑本地图片
python scripts/edit_image.py --image photo.png --prompt "Change background to sunset"

# 使用在线图片
python scripts/edit_image.py --image "https://example.com/photo.jpg" --prompt "Style transfer"
```

## 可用模型

### 文生图模型

| 模型 ID | 说明 | 特点 |
|---------|------|------|
| `MAILAND/majicflus_v1` | 麦橘超然 | 艺术风格，创意效果好 |
| `Qwen/Qwen-Image` | 通义万相 | 阿里出品，综合能力强 |
| `Tongyi-MAI/Z-Image-Turbo` | 造相 Turbo | 快速生成，高质量 |
| `MusePublic/489_ckpt_FLUX_1` | FLUX.1-dev | 艺术风格出色 |

### 图像编辑模型

| 模型 ID | 说明 | 特点 |
|---------|------|------|
| `Qwen/Qwen-Image-Edit-2511` | 最新版 | 角色一致性好，支持 LoRA |
| `Qwen/Qwen-Image-Edit-2509` | 稳定版 | 单人一致性好 |
| `Qwen/Qwen-Image-Edit` | 基础版 | 通用编辑能力 |

## 参数说明

### 通用参数

| 参数名 | 说明 | 是否必须 | 类型 | 示例 |
|-------|------|--------|------|------|
| `model` | 模型 ID | 是 | string | `MAILAND/majicflus_v1` |
| `prompt` | 正向提示词（建议使用英文） | 是 | string | `"A girl walking down the corridor."` |
| `negative_prompt` | 负向提示词 | 否 | string | `"lowres, bad quality"` |
| `seed` | 随机种子 | 否 | int | `12345` |
| `steps` | 采样步数 | 否 | int | `30` |
| `guidance` | 提示词引导系数 | 否 | float | `3.5` |

### 分辨率范围

| 模型系列 | 范围 |
|---------|------|
| SD 系列 | [64x64, 2048x2048] |
| FLUX | [64x64, 1024x1024] |
| Qwen-Image | [64x64, 1664x1664] |
| Z-Image-Turbo | [512x512, 2048x2048] |

### 图像编辑特定参数

| 参数名 | 说明 | 是否必须 | 类型 | 示例 |
|-------|------|--------|------|------|
| `image_url` | 待编辑图片（URL 或 Base64） | 是 | string | 公网 URL 或 `data:image/jpeg;base64,...` |
| `loras` | LoRA 模型 | 否 | string/dict | `"<lora-repo-id>"` 或 `{"<id>": 0.6}` |

## 环境配置

### 获取 API Token

1. 访问 [ModelScope](https://www.modelscope.cn/)
2. 注册/登录账号
3. 进入 [API Token 管理](https://www.modelscope.cn/my/myaccesstoken)
4. 创建新的访问令牌

### 配置环境变量

**必需配置**：
```bash
export MODELSCOPE_SDK_TOKEN="your_token_here"
```

**可选配置 - 默认模型**：
```bash
export MODELSCOPE_DEFAULT_MODEL="MAILAND/majicflus_v1"
export MODELSCOPE_EDIT_MODEL="Qwen/Qwen-Image-Edit-2511"
```

### 免费额度

| 项目 | 限制 |
|------|------|
| 每日调用次数 | 2000 次 |
| 单模型限制 | 500 次/天 |
| 重置时间 | 每日 00:00 |

## 相关文件

- `scripts/generate_image.py` - 图像生成脚本（完全可用）
- `scripts/edit_image.py` - 图像编辑脚本（支持 URL/Base64）
- `scripts/list_models.py` - 模型列表查询脚本
- `references/api_reference.md` - API 详细文档

## 错误处理

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `MODELSCOPE_SDK_TOKEN not set` | 未配置 Token | 设置环境变量 |
| `404 Not Found` | API 端点不可用 | 确认模型是否为支持图像编辑的模型 |
| `Task timeout` | 任务超时 | 重试或使用更快的模型 |
| `Rate limit exceeded` | 超过调用限制 | 等待额度重置 |

---

*详细 API 文档：[references/api_reference.md](references/api_reference.md)*
