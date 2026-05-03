# ModelScope API 参考文档

## 概述

本文档提供 ModelScope 图像生成 API 的详细参考信息。

## API 端点

### 基础 URL

| API 类型 | URL |
|----------|-----|
| 推理 API | `https://api-inference.modelscope.cn/v1` |
| OpenAPI | `https://modelscope.cn/openapi/v1` |

### 认证

所有 API 请求需要在 Header 中携带 Bearer Token：

```
Authorization: Bearer YOUR_API_TOKEN
```

获取 Token: [https://www.modelscope.cn/my/myaccesstoken](https://www.modelscope.cn/my/myaccesstoken)

## 图像生成 API

### 提交生成任务

**端点**: `POST /images/generations`

**Headers**:
```
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json
X-ModelScope-Async-Mode: true
```

**请求体**:
```json
{
  "model": "MAILAND/majicflus_v1",
  "prompt": "a cute golden cat sitting on a cloud",
  "size": "1024x1024",
  "negative_prompt": "blurry, low quality",
  "seed": 12345,
  "steps": 30,
  "guidance": 3.5
}
```

**参数说明**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `model` | string | ✅ | 模型 ID |
| `prompt` | string | ✅ | 正向提示词 |
| `size` | string | ❌ | 图像尺寸，如 `1024x1024` |
| `negative_prompt` | string | ❌ | 负向提示词 |
| `seed` | integer | ❌ | 随机种子 |
| `steps` | integer | ❌ | 采样步数 |
| `guidance` | float | ❌ | 引导系数 |

**响应**:
```json
{
  "task_id": "abc123def456",
  "task_status": "PROCESSING"
}
```

### 查询任务状态

**端点**: `GET /tasks/{task_id}`

**Headers**:
```
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json
X-ModelScope-Task-Type: image_generation
```

**响应 (处理中)**:
```json
{
  "task_id": "abc123def456",
  "task_status": "PROCESSING"
}
```

**响应 (成功)**:
```json
{
  "task_id": "abc123def456",
  "task_status": "SUCCEED",
  "output_images": [
    "https://example.com/image1.png"
  ]
}
```

**响应 (失败)**:
```json
{
  "task_id": "abc123def456",
  "task_status": "FAILED",
  "message": "错误原因"
}
```

**任务状态**:

| 状态 | 说明 |
|------|------|
| `PENDING` | 等待处理 |
| `PROCESSING` | 正在处理 |
| `SUCCEED` | 成功完成 |
| `FAILED` | 执行失败 |

## 模型列表 API

### 获取模型列表

**端点**: `GET /models`

**参数**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `search` | string | ❌ | 搜索关键词 |
| `owner` | string | ❌ | 作者筛选 |
| `sort` | string | ❌ | 排序: `default`, `downloads`, `likes`, `last_modified` |
| `page_number` | integer | ❌ | 页码 (默认: 1) |
| `page_size` | integer | ❌ | 每页数量 (默认: 10, 最大: 50) |
| `filter.task` | string | ❌ | 任务类型筛选 |

**示例请求**:
```
GET /models?filter.task=text-to-image-synthesis&sort=downloads&page_size=20
```

**响应**:
```json
{
  "success": true,
  "data": {
    "models": [
      {
        "id": "Qwen/Qwen-Image",
        "display_name": "Qwen-Image",
        "description": "通义万相图像生成模型",
        "downloads": 2568039,
        "likes": 431,
        "license": "apache-2.0",
        "tasks": ["text-to-image-synthesis"],
        "tags": ["license:apache-2.0", "library:diffusers"]
      }
    ],
    "total_count": 65993,
    "page_number": 1,
    "page_size": 20
  }
}
```

## 推荐模型

### 高质量模型

| 模型 ID | 说明 | 下载量 |
|---------|------|--------|
| `MAILAND/majicflus_v1` | 麦橘超然 | 547K+ |
| `Qwen/Qwen-Image` | 通义万相 | 2.5M+ |
| `Tongyi-MAI/Z-Image-Turbo` | 造相 Turbo | 527K+ |
| `MusePublic/489_ckpt_FLUX_1` | FLUX.1-dev | 1.3M+ |

### 使用限制

#### 免费额度

| 项目 | 限制 |
|------|------|
| 每日总调用次数 | 2000 次 |
| 单模型每日调用 | 500 次 |
| 重置时间 | 每日 00:00 (北京时间) |

## 代码示例

### Python (requests)

```python
import requests
import time

API_BASE = "https://api-inference.modelscope.cn/v1"
TOKEN = "your_token_here"

def generate_image(prompt, model="MAILAND/majicflus_v1", size="1024x1024"):
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "X-ModelScope-Async-Mode": "true"
    }
    
    payload = {
        "model": model,
        "prompt": prompt,
        "size": size
    }
    
    response = requests.post(
        f"{API_BASE}/images/generations",
        headers=headers,
        json=payload,
        timeout=60
    )
    
    task_id = response.json()["task_id"]
    print(f"Task ID: {task_id}")
    
    poll_headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "X-ModelScope-Task-Type": "image_generation"
    }
    
    while True:
        status_response = requests.get(
            f"{API_BASE}/tasks/{task_id}",
            headers=poll_headers,
            timeout=30
        )
        data = status_response.json()
        
        task_status = data.get("task_status", "UNKNOWN")
        print(f"Status: {task_status}")
        
        if task_status == "SUCCEED":
            return data["output_images"][0]
        elif task_status == "FAILED":
            raise Exception(data.get("message", "Task failed"))
        
        time.sleep(5)

image_url = generate_image("a cute golden cat sitting on a cloud")
print(f"Generated image: {image_url}")
```

## 相关链接

- [ModelScope 官网](https://www.modelscope.cn/)
- [API Token 管理](https://www.modelscope.cn/my/myaccesstoken)
- [模型文档](https://www.modelscope.cn/docs)
- [OpenAPI 规范](https://www.modelscope.cn/.well-known/openapi.json)
