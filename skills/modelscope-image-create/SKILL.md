---
name: modelscope-image-create
description: 使用 ModelScope API 生成 AI 图像。支持多种文生图模型（Qwen-Image、FLUX、Z-Image 等），通过文本提示词生成高质量图像。当用户需要生成图片、创建图像、文生图、AI 绘画时使用此技能。
---

# ModelScope 图像生成

## 概述

使用 ModelScope 平台的文生图 API，通过自然语言描述生成高质量 AI 图像。支持多种主流模型，包括通义万相、FLUX、Z-Image 等。

**核心功能**：
- 通过文本提示词生成图像
- 支持多种主流文生图模型
- 可配置图像尺寸、负向提示词等参数
- 自动处理异步任务和结果下载

## 使用场景

**使用此技能当**：
- 用户要求"生成一张图片"、"画一张图"
- 用户描述场景想要可视化
- 用户需要 AI 艺术创作
- 用户提到"文生图"、"AI 绘画"、"text-to-image"

**不使用**：
- 用户要求编辑现有图片
- 用户要求图像处理或滤镜
- 纯文字任务，无图像需求

## 快速参考

| 任务 | 命令 |
|------|------|
| **生成图像** | `python scripts/generate_image.py --prompt "描述文字"` |
| **指定模型** | `python scripts/generate_image.py --prompt "描述" --model Qwen/Qwen-Image` |
| **指定尺寸** | `python scripts/generate_image.py --prompt "描述" --size 1024x1024` |
| **负向提示词** | `python scripts/generate_image.py --prompt "描述" --negative-prompt "模糊,低质量"` |
| **保存路径** | `python scripts/generate_image.py --prompt "描述" --output ./my_images/result.png` |
| **列出模型** | `python scripts/list_models.py` |
| **搜索模型** | `python scripts/list_models.py --search "flux"` |

## 核心工作流

### 1. 基础图像生成

```bash
python scripts/generate_image.py --prompt "一只金色的猫坐在云朵上，梦幻风格"
```

**输出示例**：
```
🎨 图像生成成功！
📝 提示词: 一只金色的猫坐在云朵上，梦幻风格
🤖 模型: Qwen/Qwen-Image
📐 尺寸: 1024x1024
💾 保存路径: ./outputs/result_image_20260501_123456.png
🌐 图片URL: https://modelscope.cn/...
```

### 2. 高级配置

```bash
python scripts/generate_image.py \
  --prompt "赛博朋克城市夜景，霓虹灯闪烁，未来感十足" \
  --model "Tongyi-MAI/Z-Image-Turbo" \
  --size "1920x1080" \
  --negative-prompt "模糊,低质量,变形" \
  --output "./generated/cyberpunk.png"
```

### 3. 批量生成

```bash
# 生成多张不同风格的图像
python scripts/generate_image.py --prompt "山水画风格的中国风景" --model "Qwen/Qwen-Image"
python scripts/generate_image.py --prompt "油画风格的日落海景" --model "MAILAND/majicflus_v1"
python scripts/generate_image.py --prompt "动漫风格的少女肖像" --model "MusePublic/489_ckpt_FLUX_1"
```

## 可用模型

### 推荐模型

| 模型 ID | 说明 | 特点 |
|---------|------|------|
| `Qwen/Qwen-Image` | 通义万相 | 阿里出品，综合能力强，中文理解好 |
| `Tongyi-MAI/Z-Image-Turbo` | 造相 Turbo | 快速生成，高质量 |
| `Tongyi-MAI/Z-Image` | 造相 | 高质量图像生成 |
| `MusePublic/489_ckpt_FLUX_1` | FLUX.1-dev | 艺术风格出色 |
| `MAILAND/majicflus_v1` | 麦橘超然 | 艺术风格，创意效果好 |

### 获取更多模型

```bash
# 列出所有文生图模型
python scripts/list_models.py

# 搜索特定模型
python scripts/list_models.py --search "flux"
python scripts/list_models.py --search "写实"
```

## 参数说明

### generate_image.py 参数

| 参数 | 必需 | 默认值 | 说明 |
|------|------|--------|------|
| `--prompt` | ✅ | - | 正向提示词，描述想要生成的图像 |
| `--model` | ❌ | `Qwen/Qwen-Image` | 模型 ID |
| `--size` | ❌ | `1024x1024` | 图像尺寸，如 `1024x1024`、`1920x1080` |
| `--negative-prompt` | ❌ | - | 负向提示词，描述不想要的元素 |
| `--output` | ❌ | `./outputs/result_image.jpg` | 输出文件路径 |
| `--seed` | ❌ | 随机 | 随机种子，用于复现结果 |
| `--steps` | ❌ | 模型默认 | 采样步数 |
| `--guidance` | ❌ | 模型默认 | 引导系数 |

### 提示词技巧

**好的提示词包含**：
- 主体描述：明确画什么
- 风格描述：艺术风格、画风
- 细节描述：光线、色彩、构图
- 质量词：高清、精细、专业

**示例**：
```
# 基础
一只猫

# 更好
一只金色的猫坐在窗台上

# 最佳
一只金色的猫坐在阳光洒落的窗台上，柔软的毛发，温暖的午后光线，
写实风格，高清细节，8K分辨率，专业摄影
```

## 环境配置

### 获取 API Token

1. 访问 [ModelScope](https://www.modelscope.cn/)
2. 注册/登录账号
3. 进入 [API Token 管理](https://www.modelscope.cn/my/myaccesstoken)
4. 创建新的访问令牌

### 配置环境变量

**Linux/macOS**：
```bash
export MODELSCOPE_SDK_TOKEN="your_token_here"
```

**Windows (PowerShell)**：
```powershell
$env:MODELSCOPE_SDK_TOKEN="your_token_here"
```

**Windows (CMD)**：
```cmd
set MODELSCOPE_SDK_TOKEN=your_token_here
```

### 免费额度

| 项目 | 额度 |
|------|------|
| 每日调用次数 | 2000 次 |
| 单模型限制 | 500 次/天 |
| 重置时间 | 每日 00:00 |

## 常见问题

### 图像生成失败

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

## 内部流程

```
用户提示词 → 参数验证 → 提交异步任务 → 轮询任务状态 → 下载图像 → 保存本地
```

1. 使用 `X-ModelScope-Async-Mode: true` 提交异步任务
2. 每 5 秒轮询任务状态（最多约 2 分钟）
3. 成功后下载图像并保存
4. 返回结果信息

## 相关文件

- `scripts/generate_image.py` - 图像生成脚本
- `scripts/list_models.py` - 模型列表查询脚本
- `references/api_reference.md` - API 详细文档

## 错误处理

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `MODELSCOPE_SDK_TOKEN not set` | 未配置 Token | 设置环境变量 |
| `Task timeout` | 任务超时 | 重试或使用更快的模型 |
| `Network error` | 网络问题 | 检查网络连接 |
| `Invalid model` | 模型不存在 | 使用 `list_models.py` 查看可用模型 |
| `Rate limit exceeded` | 超过调用限制 | 等待额度重置或更换 Token |

---

*详细 API 文档：[references/api_reference.md](references/api_reference.md)*
