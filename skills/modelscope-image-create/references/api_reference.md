# ModelScope API 参考文档

## 概述

本文档提供 ModelScope 图像生成 API 的详细参考信息。

## API 端点

### 基础 URL

| API 类型 | URL |
|----------|-----|
| 推理 API | `https://modelscope.cn/api/v1` |
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
  "model": "Qwen/Qwen-Image",
  "prompt": "一只金色的猫坐在云朵上",
  "size": "1024x1024",
  "negative_prompt": "模糊,低质量",
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
  "status": "PENDING"
}
```

### 查询任务状态

**端点**: `GET /tasks/{task_id}`

**Headers**:
```
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json
```

**响应 (处理中)**:
```json
{
  "task_id": "abc123def456",
  "status": "RUNNING",
  "progress": 50
}
```

**响应 (成功)**:
```json
{
  "task_id": "abc123def456",
  "status": "SUCCEEDED",
  "output": {
    "images": [
      "https://modelscope.cn/.../image1.png"
    ]
  }
}
```

**响应 (失败)**:
```json
{
  "task_id": "abc123def456",
  "status": "FAILED",
  "message": "错误原因"
}
```

**任务状态**:

| 状态 | 说明 |
|------|------|
| `PENDING` | 等待处理 |
| `RUNNING` | 正在处理 |
| `SUCCEEDED` | 成功完成 |
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
| `filter.library` | string | ❌ | 框架筛选 |
| `filter.license` | string | ❌ | 许可证筛选 |

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

### 获取模型详情

**端点**: `GET /models/{owner}/{repo_name}`

**示例**: `GET /models/Qwen/Qwen-Image`

**响应**:
```json
{
  "success": true,
  "data": {
    "id": "Qwen/Qwen-Image",
    "display_name": "Qwen-Image",
    "description": "...",
    "downloads": 2568039,
    "likes": 431,
    "license": "apache-2.0",
    "tasks": ["text-to-image-synthesis"],
    "created_at": "2025-08-02T04:25:45Z",
    "last_modified": "2025-08-18T02:42:52Z"
  }
}
```

## 推荐模型

### 高质量模型

| 模型 ID | 说明 | 参数量 | 下载量 |
|---------|------|--------|--------|
| `Qwen/Qwen-Image` | 通义万相 | 28B | 2.5M+ |
| `Tongyi-MAI/Z-Image-Turbo` | 造相 Turbo | 10B | 527K+ |
| `Tongyi-MAI/Z-Image` | 造相 | 10B | 123K+ |
| `MusePublic/489_ckpt_FLUX_1` | FLUX.1-dev | 28B | 1.3M+ |
| `MAILAND/majicflus_v1` | 麦橘超然 | 11B | 547K+ |

### 风格化模型

| 模型 ID | 风格 |
|---------|------|
| `yiwanji/FLUX_xiao_hong_shu_ji_zhi_zhen_shi_V2` | 小红书风格 |
| `laonansheng/ruanqing-Z-Image-Turbo-Tongyi-MAI-v1.0` | 软情风格 |
| `laonansheng/naixi-girl-Z-Image-Turbo-Tongyi-MAI-v1.0` | 奶昔女孩 |

## 错误码

| HTTP 状态码 | 说明 |
|-------------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 认证失败或 Token 无效 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 429 | 请求过于频繁 |
| 500 | 服务器内部错误 |
| 503 | 服务不可用 |

## 使用限制

### 免费额度

| 项目 | 限制 |
|------|------|
| 每日总调用次数 | 2000 次 |
| 单模型每日调用 | 500 次 |
| 重置时间 | 每日 00:00 (北京时间) |

### 速率限制

- 建议: 每秒不超过 5 次请求
- 异步任务: 最多等待 2 分钟

## 代码示例

### Python (requests)

```python
import requests
import time

API_BASE = "https://modelscope.cn/api/v1"
TOKEN = "your_token_here"

def generate_image(prompt, model="Qwen/Qwen-Image"):
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "X-ModelScope-Async-Mode": "true"
    }
    
    payload = {
        "model": model,
        "prompt": prompt,
        "size": "1024x1024"
    }
    
    response = requests.post(
        f"{API_BASE}/images/generations",
        headers=headers,
        json=payload
    )
    
    task_id = response.json()["task_id"]
    
    while True:
        status_response = requests.get(
            f"{API_BASE}/tasks/{task_id}",
            headers=headers
        )
        data = status_response.json()
        
        if data["status"] == "SUCCEEDED":
            return data["output"]["images"][0]
        elif data["status"] == "FAILED":
            raise Exception(data.get("message", "Task failed"))
        
        time.sleep(5)

image_url = generate_image("一只金色的猫坐在云朵上")
print(f"Generated image: {image_url}")
```

### cURL

```bash
TOKEN="your_token_here"

TASK_ID=$(curl -s -X POST "https://modelscope.cn/api/v1/images/generations" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-ModelScope-Async-Mode: true" \
  -d '{"model":"Qwen/Qwen-Image","prompt":"一只金色的猫","size":"1024x1024"}' \
  | jq -r '.task_id')

echo "Task ID: $TASK_ID"

while true; do
  STATUS=$(curl -s "https://modelscope.cn/api/v1/tasks/$TASK_ID" \
    -H "Authorization: Bearer $TOKEN" \
    | jq -r '.status')
  
  echo "Status: $STATUS"
  
  if [ "$STATUS" = "SUCCEEDED" ]; then
    curl -s "https://modelscope.cn/api/v1/tasks/$TASK_ID" \
      -H "Authorization: Bearer $TOKEN" \
      | jq -r '.output.images[0]'
    break
  elif [ "$STATUS" = "FAILED" ]; then
    echo "Task failed"
    break
  fi
  
  sleep 5
done
```

## 相关链接

- [ModelScope 官网](https://www.modelscope.cn/)
- [API Token 管理](https://www.modelscope.cn/my/myaccesstoken)
- [模型文档](https://www.modelscope.cn/docs)
- [OpenAPI 规范](https://www.modelscope.cn/.well-known/openapi.json)
