---
name: modelscope-image-create
description: 使用 ModelScope API 生成和编辑 AI 图像。支持文生图（Qwen-Image、FLUX、Z-Image 等）和图像编辑（Qwen-Image-Edit），通过文本提示词生成或编辑高质量图像。当用户需要生成图片、编辑图片、文生图、AI 绘画时使用此技能。
---

# ModelScope 图像生成与编辑

## 概述

使用 ModelScope 平台的 AI 图像 API，通过自然语言描述生成或编辑高质量图像。支持多种主流模型，包括通义万相、FLUX、Z-Image 等。

**核心功能**：
- 文本生成图像（文生图）
- 图像编辑（风格转换、局部修改、多人合成等）
- 支持多种主流模型
- 可配置图像尺寸、负向提示词等参数

## 使用场景

**使用此技能当**：
- 用户要求"生成一张图片"、"画一张图" → 使用 `generate_image.py`
- 用户要求"编辑图片"、"修改图片"、"P图" → 使用 `edit_image.py`
- 用户描述场景想要可视化
- 用户需要 AI 艺术创作
- 用户提到"文生图"、"AI 绘画"、"text-to-image"、"image-editing"

## 快速参考

### 图像生成

| 任务 | 命令 | 说明 |
|------|------|------|
| **基础生成** | `python scripts/generate_image.py --prompt "描述文字"` | 使用默认模型 |
| **指定模型** | `python scripts/generate_image.py --prompt "描述" --model Qwen/Qwen-Image` | 仅在需要时指定 |
| **指定尺寸** | `python scripts/generate_image.py --prompt "描述" --size 1024x1024` |  |
| **负向提示词** | `python scripts/generate_image.py --prompt "描述" --negative-prompt "模糊,低质量"` |  |
| **保存路径** | `python scripts/generate_image.py --prompt "描述" --output ./result.png` |  |

### 图像编辑

| 任务 | 命令 | 说明 |
|------|------|------|
| **编辑图片** | `python scripts/edit_image.py --image input.png --prompt "编辑描述"` | 使用默认模型 |
| **多人合成** | `python scripts/edit_image.py -i person1.png -i person2.png -p "两人站在一起"` | 合成合照 |
| **风格转换** | `python scripts/edit_image.py --image photo.png --prompt "转换成吉卜力风格"` |  |
| **局部修改** | `python scripts/edit_image.py --image photo.png --prompt "给猫戴上墨镜"` |  |

### 模型查询

| 任务 | 命令 |
|------|------|
| **列出模型** | `python scripts/list_models.py` |
| **搜索模型** | `python scripts/list_models.py --search "flux"` |

## 核心工作流

### 1. 图像生成

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

```bash
# 编辑单张图片
python scripts/edit_image.py --image photo.png --prompt "把背景改成日落"

# 多人合照合成
python scripts/edit_image.py -i person1.png -i person2.png -p "两人站在一起合影"

# 风格转换
python scripts/edit_image.py --image portrait.png --prompt "转换成吉卜力动画风格"
```

## 可用模型

### 文生图模型

| 模型 ID | 说明 | 特点 |
|---------|------|------|
| `MAILAND/majicflus_v1` | 麦橘超然 | 艺术风格，创意效果好 |
| `Qwen/Qwen-Image` | 通义万相 | 阿里出品，综合能力强，中文理解好 |
| `Tongyi-MAI/Z-Image-Turbo` | 造相 Turbo | 快速生成，高质量 |
| `MusePublic/489_ckpt_FLUX_1` | FLUX.1-dev | 艺术风格出色 |

### 图像编辑模型

| 模型 ID | 说明 | 特点 |
|---------|------|------|
| `Qwen/Qwen-Image-Edit-2511` | 最新版 | 角色一致性好，支持 LoRA |
| `Qwen/Qwen-Image-Edit-2509` | 稳定版 | 单人一致性好 |
| `Qwen/Qwen-Image-Edit` | 基础版 | 通用编辑能力 |

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
  export MODELSCOPE_DEFAULT_MODEL="Qwen/Qwen-Image"
  ```
- 图像编辑默认模型：
  ```bash
  export MODELSCOPE_EDIT_MODEL="Qwen/Qwen-Image-Edit-2511"
  ```

### 免费额度

| 项目 | 额度 |
|------|------|
| 每日调用次数 | 2000 次 |
| 单模型限制 | 500 次/天 |
| 重置时间 | 每日 00:00 |

## 常见问题

### 图像生成/编辑失败

**检查项**：
1. API Token 是否正确配置
2. 网络连接是否正常
3. 模型 ID 是否正确
4. 提示词是否包含敏感内容

### 生成速度慢

**优化建议**：
1. 使用 Turbo 模型（如 `Z-Image-Turbo`）
2. 减少采样步数
3. 使用较小的图像尺寸

### 图像质量不满意

**改进方法**：
1. 优化提示词，增加细节描述
2. 使用负向提示词排除不想要的元素
3. 尝试不同的模型
4. 调整 guidance 参数

## 相关文件

- `scripts/generate_image.py` - 图像生成脚本
- `scripts/edit_image.py` - 图像编辑脚本
- `scripts/list_models.py` - 模型列表查询脚本
- `references/api_reference.md` - API 详细文档

## 错误处理

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `MODELSCOPE_SDK_TOKEN not set` | 未配置 Token | 设置环境变量 |
| `Task timeout` | 任务超时 | 重试或使用更快的模型 |
| `Network error` | 网络问题 | 检查网络连接 |
| `Invalid model` | 模型不存在 | 使用 `list_models.py` 查看可用模型 |
| `Rate limit exceeded` | 超过调用限制 | 等待额度重置 |

---

*详细 API 文档：[references/api_reference.md](references/api_reference.md)*
