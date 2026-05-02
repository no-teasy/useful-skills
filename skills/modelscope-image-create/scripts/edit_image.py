#!/usr/bin/env python3
"""
ModelScope 图像编辑脚本（根据官方文档更新）
支持 URL 和 Base64 编码图片输入
"""

import argparse
import base64
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

try:
    import requests
except ImportError:
    print("错误: 需要安装 requests 库")
    print("请运行: pip install requests")
    sys.exit(1)

try:
    from PIL import Image
    from io import BytesIO
except ImportError:
    print("警告: Pillow 库未安装，将使用 requests 下载图片")

MODELSCOPE_API_BASE = "https://api-inference.modelscope.cn/v1/images/generations"
DEFAULT_MODEL = os.environ.get("MODELSCOPE_EDIT_MODEL", "Qwen/Qwen-Image-Edit-2511")
DEFAULT_SIZE = "1024x1024"
DEFAULT_OUTPUT = "./outputs"
MAX_POLL_COUNT = 120
POLL_INTERVAL = 5


def image_to_data_url(image_path):
    """将本地图片转换为 Base64 编码的 data URL"""
    with open(image_path, "rb") as f:
        img_data = f.read()
    
    base64_data = base64.b64encode(img_data).decode("utf-8")
    mime_type = "image/png" if image_path.lower().endswith(".png") else "image/jpeg"
    return f"data:{mime_type};base64,{base64_data}"


def get_token():
    token = os.environ.get("MODELSCOPE_SDK_TOKEN")
    if not token:
        print("错误: 未设置 MODELSCOPE_SDK_TOKEN 环境变量")
        print("请先获取 API Token: https://www.modelscope.cn/my/myaccesstoken")
        print("然后设置环境变量:")
        print("  Linux/macOS: export MODELSCOPE_SDK_TOKEN='your_token'")
        print("  Windows: set MODELSCOPE_SDK_TOKEN='your_token'")
        sys.exit(1)
    return token


def submit_task(token, image_input, prompt, model, negative_prompt=None, 
               seed=None, steps=None, guidance=None, loras=None):
    url = MODELSCOPE_API_BASE
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-ModelScope-Async-Mode": "true"
    }
    
    payload = {
        "model": model,
        "prompt": prompt,
        "size": DEFAULT_SIZE
    }
    
    # 处理图像输入（URL 或 Base64）
    if image_input.startswith("http://") or image_input.startswith("https://"):
        payload["image_url"] = image_input
    elif image_input.startswith("data:"):
        payload["image_url"] = image_input
    elif os.path.exists(image_input):
        print(f"编码本地图片: {image_input}")
        payload["image_url"] = image_to_data_url(image_input)
    else:
        print(f"错误: 找不到输入文件: {image_input}")
        sys.exit(1)
    
    if negative_prompt:
        payload["negative_prompt"] = negative_prompt
    if seed is not None:
        payload["seed"] = seed
    if steps is not None:
        payload["steps"] = steps
    if guidance is not None:
        payload["guidance"] = guidance
    if loras is not None:
        payload["loras"] = loras
    
    print(f"提交图像编辑任务...")
    print(f"模型: {model}")
    print(f"提示词: {prompt}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 401:
            print("错误: API Token 无效或已过期")
            sys.exit(1)
        elif response.status_code == 404:
            print(f"错误: API 端点不可用 (404)")
            print(f"提示: 有些模型可能不支持图像编辑，请确认模型是否为编辑模型")
            print(f"      推荐编辑模型: Qwen/Qwen-Image-Edit-2511, Qwen/Qwen-Image-Edit-2509")
            sys.exit(1)
        elif response.status_code == 429:
            print("错误: 请求过于频繁，请稍后重试")
            sys.exit(1)
        elif response.status_code != 200:
            print(f"错误: 提交任务失败 ({response.status_code})")
            print(f"响应: {response.text}")
            sys.exit(1)
        
        return response.json()
        
    except Exception as e:
        print(f"请求失败: {e}")
        sys.exit(1)


def poll_task_status(token, task_id):
    url = f"https://api-inference.modelscope.cn/v1/tasks/{task_id}"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-ModelScope-Task-Type": "image_generation"
    }
    
    for i in range(MAX_POLL_COUNT):
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code != 200:
                print(f"警告: 轮询任务状态失败 ({response.status_code})")
                time.sleep(POLL_INTERVAL)
                continue
            
            data = response.json()
            status = data.get("task_status", "UNKNOWN")
            
            if i % 6 == 0:
                print(f"任务处理中 (尝试 {i+1}/{MAX_POLL_COUNT}): 状态 = {status}")
            
            if status == "SUCCEED":
                print("任务成功!")
                return data
            elif status == "FAILED":
                error_msg = data.get("message", "未知错误")
                print(f"任务失败: {error_msg}")
                print(f"完整响应: {data}")
                sys.exit(1)
            else:
                time.sleep(POLL_INTERVAL)
        except Exception as e:
            print(f"警告: 轮询请求异常: {e}")
            time.sleep(POLL_INTERVAL)
    
    print("任务超时（超过最大等待时间）")
    sys.exit(1)


def download_image(url, output_path):
    try:
        response = requests.get(url, timeout=60)
        if response.status_code != 200:
            print(f"错误: 下载图片失败 ({response.status_code})")
            return False
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if Image:
            img = Image.open(BytesIO(response.content))
            img.save(output_path)
        else:
            with open(output_path, "wb") as f:
                f.write(response.content)
        
        return True
    except Exception as e:
        print(f"下载图片失败: {e}")
        return False


def edit_image(image_input, prompt, model=None, negative_prompt=None, 
               output=None, seed=None, steps=None, guidance=None, loras=None):
    token = get_token()
    
    model = model or DEFAULT_MODEL
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if output:
        output_path = Path(output)
    else:
        output_path = Path(DEFAULT_OUTPUT) / f"edited_image_{timestamp}.png"
    
    result = submit_task(token, image_input, prompt, model, 
                       negative_prompt, seed, steps, guidance, loras)
    
    task_id = result.get("task_id")
    if not task_id:
        print("错误: 未获取到任务 ID")
        print(f"响应: {result}")
        sys.exit(1)
    
    print(f"任务 ID: {task_id}")
    print("等待任务完成...")
    
    task_result = poll_task_status(token, task_id)
    
    images = task_result.get("output_images", [])
    if not images:
        print("错误: 未获取到编辑后的图像")
        print(f"完整响应: {task_result}")
        sys.exit(1)
    
    image_url = images[0]
    print(f"下载图像: {image_url}")
    
    if download_image(image_url, output_path):
        print(f"\n✅ 图像编辑成功！")
        print(f"💾 保存路径: {output_path.absolute()}")
        return str(output_path.absolute())
    else:
        print("❌ 图像保存失败")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="ModelScope 图像编辑工具（支持 URL 和 Base64）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
推荐编辑模型:
  Qwen/Qwen-Image-Edit-2511 - 最新版，角色一致性好
  Qwen/Qwen-Image-Edit-2509 - 稳定版，单人一致性好

分辨率范围:
  SD系列: [64x64, 2048x2048]
  FLUX: [64x64, 1024x1024]
  Qwen-Image: [64x64, 1664x1664]
  Z-Image-Turbo: [512x512, 2048x2048]

示例:
  # 编辑本地图片
  python edit_image.py --image input.png --prompt "把背景改成日落"
  
  # 使用在线图片 URL
  python edit_image.py --image "https://example.com/photo.jpg" --prompt "风格转换"
  
  # 使用 LoRA 模型
  python edit_image.py --image input.png --prompt "动漫风格" --loras "<lora-repo-id>"
  
  # 配置高级参数
  python edit_image.py --image input.png --prompt "编辑描述" --seed 12345 --steps 50
        """
    )
    
    parser.add_argument(
        "--image", "-i",
        required=True,
        help="输入图像（本地路径、URL 或 Base64 编码）"
    )
    
    parser.add_argument(
        "--prompt", "-p",
        required=True,
        help="编辑提示词（建议使用英文效果更好）"
    )
    
    parser.add_argument(
        "--model", "-m",
        default=DEFAULT_MODEL,
        help=f"模型 ID (默认: {DEFAULT_MODEL})"
    )
    
    parser.add_argument(
        "--negative-prompt", "-n",
        help="负向提示词"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="输出文件路径"
    )
    
    parser.add_argument(
        "--seed",
        type=int,
        help="随机种子 [0, 2^31-1]"
    )
    
    parser.add_argument(
        "--steps",
        type=int,
        help="采样步数 [1, 100]"
    )
    
    parser.add_argument(
        "--guidance",
        type=float,
        help="提示词引导系数 [1.5, 20]"
    )
    
    parser.add_argument(
        "--loras",
        help="LoRA 模型（单个: '<lora-repo-id>'，多个: JSON dict）"
    )
    
    args = parser.parse_args()
    
    # 处理 LoRA 参数
    loras = None
    if args.loras:
        try:
            loras = json.loads(args.loras)
        except:
            loras = args.loras
    
    edit_image(
        image_input=args.image,
        prompt=args.prompt,
        model=args.model,
        negative_prompt=args.negative_prompt,
        output=args.output,
        seed=args.seed,
        steps=args.steps,
        guidance=args.guidance,
        loras=loras
    )


if __name__ == "__main__":
    main()
