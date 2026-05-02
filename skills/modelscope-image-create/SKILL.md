---
name: modelscope-image-create
description: 使用 ModelScope API 生成和编辑 AI 图像。支持文生图（Qwen-Image、FLUX、Z-Image 等）和图像编辑（Qwen-Image-Edit），通过文本提示词生成或编辑高质量图像。当用户需要生成图片、编辑图片、文生图、AI 绘画时使用此技能。
---

# ModelScope 图像生成与编辑

## 概述

使用 ModelScope 平台的 AI 图像 API，通过自然语言描述生成或编辑高质量图像。支持多种主流模型，包括通义万相、FLUX、Z-Image 等。

**核心功能**：
- 文本生成图像（文生图）✅ 已实现
- 图像编辑（Qwen-Image-Edit）✅ 已实现（需要本地部署或云端服务）
- 支持多种主流模型
- 可配置图像尺寸、负向提示词等参数

## 使用场景

**使用此技能当**：
- 用户要求"生成一张图片"、"画一张图" → 使用 `generate_image.py`
- 用户要求"编辑图片"、"修改图片"、"P图" → 使用 `edit_image.py`（云端服务）
- 用户描述场景想要可视化
- 用户需要 AI 艺术创作
- 用户提到"文生图"、"AI 绘画"、"text-to-image"、"image-editing"

## 快速参考

### 图像生成 ✅ 完全可用

| 任务 | 命令 | 说明 |
|------|------|------|
| **基础生成** | `python scripts/generate_image.py --prompt "描述文字"` | 使用默认模型 |
| **指定模型** | `python scripts/generate_image.py --prompt "描述" --model Qwen/Qwen-Image` | 仅在需要时指定 |
| **指定尺寸** | `python scripts/generate_image.py --prompt "描述" --size 1024x1024` |  |
| **负向提示词** | `python scripts/generate_image.py --prompt "描述" --negative-prompt "模糊,低质量"` |  |
| **保存路径** | `python scripts/generate_image.py --prompt "描述" --output ./result.png` |  |

### 图像编辑 ✅ 需要配置

| 任务 | 命令 | 说明 |
|------|------|------|
| **云端编辑** | `python scripts/edit_image.py --image input.png --prompt "编辑描述"` | 需要 ModelScope 云端服务 |
| **本地部署** | 使用 Python SDK 脚本 | 推荐用于生产环境 |

## 核心工作流

### 1. 图像生成（完全可用）

```bash
python scripts/generate_image.py --prompt "一只金色的猫坐在云朵上，梦幻风格"
```

**输出示例**：
```
🎨 提交图像生成任务...
📝 提示词: 一只金色的猫坐在云朵上，梦幻风格
🤖 模型: MAILAND/majicflus_v1
📐 尺寸: 1024x1024
📋 任务 ID: 6552325
✅ 任务成功!
💾 保存路径: ./outputs/result_image_20260501_123456.png
```

### 2. 图像编辑

#### 方式 A：使用 Python SDK 本地部署（推荐）

```python
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
from PIL import Image

# 初始化图像编辑管道
image_edit_pipeline = pipeline(
    task=Tasks.image_editing,
    model='damo/Qwen-Image-Edit-2509'
)

# 输入原图 + 自然语言指令
input_data = {
    'image': 'input.png',
    'text': '将背景改成日落'
}

# 执行编辑
result = image_edit_pipeline(input_data)
output_image = result['output_img']
output_image.save("edited_output.png")
```

#### 方式 B：使用云端 API（需要服务订阅）

```bash
# 使用 scripts/edit_image.py（需要 ModelScope 云端服务支持）
python scripts/edit_image.py --image photo.png --prompt "把背景改成日落"
```

## 可用模型

### 文生图模型 ✅ 完全可用

| 模型 ID | 说明 | 特点 |
|---------|------|------|
| `MAILAND/majicflus_v1` | 麦橘超然 | 艺术风格，创意效果好 |
| `Qwen/Qwen-Image` | 通义万相 | 阿里出品，综合能力强 |
| `Tongyi-MAI/Z-Image-Turbo` | 造相 Turbo | 快速生成，高质量 |
| `MusePublic/489_ckpt_FLUX_1` | FLUX.1-dev | 艺术风格出色 |

### 图像编辑模型

| 模型 ID | 说明 | 特点 | 使用方式 |
|---------|------|------|----------|
| `Qwen/Qwen-Image-Edit-2511` | 最新版 | 角色一致性好，支持 LoRA | 本地部署 |
| `Qwen/Qwen-Image-Edit-2509` | 稳定版 | 单人一致性好 | 本地部署 |
| `damo/Qwen-Image-Edit-2509` | 云端版 | 云端服务 | 需要订阅 |

## 参数说明

### generate_image.py 参数

| 参数 | 必需 | 默认值 | 说明 |
|------|------|--------|------|
| `--prompt` | ✅ | - | 正向提示词，描述想要生成的图像 |
| `--model` | ❌ | 环境变量或 `MAILAND/majicflus_v1` | 模型 ID |
| `--size` | ❌ | `1024x1024` | 图像尺寸 |
| `--negative-prompt` | ❌ | - | 负向提示词 |
| `--output` | ❌ | 自动生成 | 输出文件路径 |
| `--seed` | ❌ | 随机 | 随机种子 |
| `--steps` | ❌ | 模型默认 | 采样步数 |
| `--guidance` | ❌ | 模型默认 | 引导系数 |

### edit_image.py 参数

| 参数 | 必需 | 默认值 | 说明 |
|------|------|--------|------|
| `--image` | ✅ | - | 输入图像路径（可多次指定） |
| `--prompt` | ✅ | - | 编辑提示词 |
| `--model` | ❌ | 环境变量或 `Qwen/Qwen-Image-Edit-2511` | 模型 ID |
| `--negative-prompt` | ❌ | - | 负向提示词 |
| `--output` | ❌ | 自动生成 | 输出文件路径 |
| `--seed` | ❌ | 随机 | 随机种子 |
| `--steps` | ❌ | 模型默认 | 采样步数 |
| `--guidance` | ❌ | 模型默认 | 引导系数 |

## 环境配置

### 获取 API Token

1. 访问 [ModelScope](https://www.modelscope.cn/)
2. 注册/登录账号
3. 进入 [API Token 管理](https://www.modelscope.cn/my/myaccesstoken)
4. 创建新的访问令牌

### 配置环境变量

**必需配置 - API Token**：
- Linux/macOS：
  ```bash
  export MODELSCOPE_SDK_TOKEN="your_token_here"
  ```
- Windows (PowerShell)：
  ```powershell
  $env:MODELSCOPE_SDK_TOKEN="your_token_here"
  ```

**可选配置 - 默认模型**：
- 文生图默认模型：
  ```bash
  export MODELSCOPE_DEFAULT_MODEL="MAILAND/majicflus_v1"
  ```
- 图像编辑默认模型：
  ```bash
  export MODELSCOPE_EDIT_MODEL="Qwen/Qwen-Image-Edit-2511"
  ```

### 图像编辑环境配置（本地部署）

```bash
# 安装 ModelScope SDK
pip install modelscope

# （可选）安装最新版本
pip install git+https://github.com/modelscope/modelscope.git

# 硬件要求
# - GPU VRAM: 至少 12GB（FP16）或 10GB（BF16）
# - 不支持纯 CPU 模式
```

## 常见问题

### Q: 图像编辑 API 返回 404 错误怎么办？

**A**: 图像编辑可能需要以下方式之一：
1. 使用 ModelScope Python SDK 本地部署（推荐）
2. 使用 ModelScope 云端订阅服务
3. 使用 Hugging Face Spaces 在线体验

### Q: 图像生成/编辑失败

**检查项**：
1. API Token 是否正确配置
2. 网络连接是否正常
3. 模型 ID 是否正确
4. 提示词是否包含敏感内容

### Q: 生成速度慢

**优化建议**：
1. 使用 Turbo 模型（如 `Z-Image-Turbo`）
2. 减少采样步数
3. 使用较小的图像尺寸

## 相关文件

- `scripts/generate_image.py` - 图像生成脚本（完全可用）
- `scripts/edit_image.py` - 图像编辑脚本（需要云端服务或本地部署）
- `scripts/list_models.py` - 模型列表查询脚本
- `references/api_reference.md` - API 详细文档

## 错误处理

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `MODELSCOPE_SDK_TOKEN not set` | 未配置 Token | 设置环境变量 |
| `404 Not Found` | 编辑 API 不可用 | 使用本地 SDK 部署或订阅云端服务 |
| `Task timeout` | 任务超时 | 重试或使用更快的模型 |
| `Network error` | 网络问题 | 检查网络连接 |
| `Rate limit exceeded` | 超过调用限制 | 等待额度重置 |

---

*详细 API 文档：[references/api_reference.md](references/api_reference.md)*
