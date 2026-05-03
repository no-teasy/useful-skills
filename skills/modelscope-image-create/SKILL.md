---
name: modelscope-image-create
description: 使用 ModelScope API 生成和编辑 AI 图像。支持文生图和图像编辑，通过文本提示词生成或编辑高质量图像。当用户需要生成图片、编辑图片、文生图、AI 绘画时使用此技能。
---

# ModelScope 图像生成与编辑

## 快速开始

### 1. 配置 Token

```bash
export MODELSCOPE_SDK_TOKEN="your_token_here"
```

获取 Token：[https://www.modelscope.cn/my/myaccesstoken](https://www.modelscope.cn/my/myaccesstoken)

### 2. 生成图片

```bash
cd /workspace/skills/modelscope-image-create
python scripts/generate_image.py --prompt "A cute golden cat sitting on a cloud"
```

### 3. 编辑图片

```bash
python scripts/edit_image.py --image outputs/result_image_xxx.png --prompt "Change background to sunset"
```

---

## 图像生成

### 快速命令

| 功能 | 命令 |
|------|------|
| 基础生成 | `python scripts/generate_image.py --prompt "描述"` |
| 指定模型 | `python scripts/generate_image.py --prompt "描述" --model Qwen/Qwen-Image` |
| 指定尺寸 | `python scripts/generate_image.py --prompt "描述" --size 1024x1024` |
| 负向提示 | `python scripts/generate_image.py --prompt "描述" --negative-prompt "模糊,低质量"` |
| 指定输出 | `python scripts/generate_image.py --prompt "描述" --output ./result.png` |

### 完整示例

```bash
python scripts/generate_image.py \
  --prompt "A magical forest with glowing mushrooms" \
  --model "Tongyi-MAI/Z-Image-Turbo" \
  --size "1024x1024" \
  --negative-prompt "low quality, blurry" \
  --seed 12345 \
  --steps 40 \
  --guidance 4.5 \
  --output "./result.png"
```

### 文生图模型

| 模型 | 说明 |
|------|------|
| `Tongyi-MAI/Z-Image-Turbo` | 造相 Turbo - 快速生成（**默认**） |
| `MAILAND/majicflus_v1` | 麦橘超然 - 艺术风格 |
| `Qwen/Qwen-Image` | 通义万相 - 综合能力强 |
| `MusePublic/489_ckpt_FLUX_1` | FLUX.1-dev - 高质量 |

---

## 图像编辑

### 支持输入

- 本地文件：`--image input.png`（自动 Base64 编码）
- 在线 URL：`--image "https://example.com/photo.jpg"`

### 快速命令

| 功能 | 命令 |
|------|------|
| 编辑本地图片 | `python scripts/edit_image.py --image photo.png --prompt "编辑描述"` |
| 使用在线图片 | `python scripts/edit_image.py --image "https://example.com/photo.jpg" --prompt "描述"` |

### 完整示例

```bash
python scripts/edit_image.py \
  --image "my_photo.png" \
  --prompt "Change to Studio Ghibli anime style" \
  --model "FireRedTeam/FireRed-Image-Edit-1.1" \
  --negative-prompt "low quality" \
  --output "./edited_photo.png"
```

### 编辑模型

| 模型 | 说明 |
|------|------|
| `FireRedTeam/FireRed-Image-Edit-1.1` | FireRed 编辑版（**默认**） |
| `Qwen/Qwen-Image-Edit-2511` | Qwen 最新版 |
| `Qwen/Qwen-Image-Edit-2509` | Qwen 稳定版 |

---

## 模型列表查询

```bash
# 列出热门模型
python scripts/list_models.py

# 搜索特定模型
python scripts/list_models.py --search "flux"
```

⚠️ **注意**：`list_models.py` 中显示的模型**不一定都支持 API 调用**。建议使用本 skill 推荐的默认模型，它们已验证支持 API 调用。

---

## 参数说明

### 通用参数

| 参数 | 必填 | 说明 | 示例 |
|------|------|------|------|
| `--prompt` | ✅ | 正向提示词（建议英文） | `"A girl walking down the corridor"` |
| `--model` | ❌ | 模型 ID（使用环境变量默认值） | `"Tongyi-MAI/Z-Image-Turbo"` |
| `--negative-prompt` | ❌ | 负向提示词 | `"lowres, blurry"` |
| `--seed` | ❌ | 随机种子 [0, 2^31-1] | `12345` |
| `--steps` | ❌ | 采样步数 [1, 100] | `40` |
| `--guidance` | ❌ | 提示词引导系数 [1.5, 20] | `4.5` |
| `--output` | ❌ | 输出文件路径 | `./result.png` |

### 生成参数

| 参数 | 必填 | 说明 | 示例 |
|------|------|------|------|
| `--size` | ❌ | 图像尺寸 | `"1024x1024"` |

### 编辑参数

| 参数 | 必填 | 说明 | 示例 |
|------|------|------|------|
| `--image` | ✅ | 输入图片（本地路径或 URL） | `"photo.png"` |

### 分辨率范围

| 模型系列 | 支持范围 |
|---------|---------|
| SD 系列 | 64x64 ~ 2048x2048 |
| FLUX | 64x64 ~ 1024x1024 |
| Qwen-Image | 64x64 ~ 1664x1664 |
| Z-Image-Turbo | 512x512 ~ 2048x2048 |

---

## 最佳实践

### 提示词结构

```
[主体描述] + [风格/光线] + [质量要求]
```

**示例**：
```
A cute golden cat sitting on a soft cloud,
watercolor painting style,
warm afternoon sunlight,
high detail, 8K, professional artwork
```

### 负向提示词

```
low quality, blurry, watermark, signature,
bad anatomy, extra fingers, text, error
```

### 环境变量配置

```bash
# ~/.bashrc 或 ~/.zshrc
export MODELSCOPE_SDK_TOKEN="your_token_here"
export MODELSCOPE_DEFAULT_MODEL="Tongyi-MAI/Z-Image-Turbo"
export MODELSCOPE_EDIT_MODEL="FireRedTeam/FireRed-Image-Edit-1.1"
```

### 免费额度

| 项目 | 限制 |
|------|------|
| 每日调用次数 | 2000 次 |
| 单模型每日调用 | 500 次 |
| 重置时间 | 每日 00:00 |

---

## 相关文件

| 文件 | 说明 |
|------|------|
| [scripts/generate_image.py](file:///workspace/skills/modelscope-image-create/scripts/generate_image.py) | 图像生成脚本 |
| [scripts/edit_image.py](file:///workspace/skills/modelscope-image-create/scripts/edit_image.py) | 图像编辑脚本 |
| [scripts/list_models.py](file:///workspace/skills/modelscope-image-create/scripts/list_models.py) | 模型列表查询脚本 |
| [references/api_reference.md](file:///workspace/skills/modelscope-image-create/references/api_reference.md) | API 详细文档 |
