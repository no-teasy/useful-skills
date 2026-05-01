#!/usr/bin/env python3
"""
ModelScope 图像编辑脚本
使用 ModelScope API 通过文本提示词编辑图像
"""
import argparse
import base64
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

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
    Image = None

MODELSCOPE_API_BASE = "https://api-inference.modelscope.cn/v1"
DEFAULT_MODEL = os.environ.get("MODELSCOPE_EDIT_MODEL", "Qwen/Qwen-Image-Edit-2511")
DEFAULT_OUTPUT = "./outputs"
MAX_POLL_COUNT = 120
POLL_INTERVAL = 5


def get_token():
    token = os.environ.get("MODELSCOPE_SDK_TOKEN")
    if not token:
        print("错误: 未设置 MODELSCOPE_SDK_TOKEN 环境变量")
        print("请先获取 API Token: https://www.modelscope.cn/my/myaccesstoken")
        print("然后设置环境变量:")
        print("  Linux/macOS: export MODELSCOPE_SDK_TOKEN='your_token'")
        print("  Windows: set MODELSCOPE_SDK_TOKEN=your_token")
        sys.exit(1)
    return token


def image_to_base64(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def submit_task(token, image_paths, prompt, model, negative_prompt=None, seed=None, steps=None, guidance=None):
    url = f"{MODELSCOPE_API_BASE}/images/edits"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-ModelScope-Async-Mode": "true"
    }
    
    images_base64 = []
    for img_path in image_paths:
        images_base64.append(image_to_base64(img_path))
    
    payload = {
        "model": model,
        "prompt": prompt,
        "image": images_base64[0] if len(images_base64) == 1 else images_base64
    }
    
    if negative_prompt:
        payload["negative_prompt"] = negative_prompt
    if seed is not None:
        payload["seed"] = seed
    if steps is not None:
        payload["num_inference_steps"] = steps
    if guidance is not None:
        payload["guidance_scale"] = guidance
    
    response = requests.post(url, headers=headers, json=payload, timeout=120)
    
    if response.status_code == 401:
        print("错误: API Token 无效或已过期")
        sys.exit(1)
    elif response.status_code == 429:
        print("错误: 请求过于频繁，请稍后重试")
        sys.exit(1)
    elif response.status_code != 200:
        print(f"错误: 提交任务失败 ({response.status_code})")
        print(f"响应: {response.text}")
        sys.exit(1)
    
    return response.json()


def poll_task_status(token, task_id):
    url = f"{MODELSCOPE_API_BASE}/tasks/{task_id}"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-ModelScope-Task-Type": "image_editing"
    }
    
    for i in range(MAX_POLL_COUNT):
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"警告: 轮询任务状态失败 ({response.status_code})")
            time.sleep(POLL_INTERVAL)
            continue
        
        data = response.json()
        status = data.get("task_status", "UNKNOWN")
        
        if i % 6 == 0:
            print(f"⏳ 任务处理中 (尝试 {i+1}/{MAX_POLL_COUNT}): 状态 = {status}")
        
        if status == "SUCCEED":
            print("✅ 任务成功!")
            return data
        elif status == "FAILED":
            error_msg = data.get("message", "未知错误")
            print(f"❌ 任务失败: {error_msg}")
            print(f"完整响应: {data}")
            sys.exit(1)
        else:
            time.sleep(POLL_INTERVAL)
    
    print("❌ 任务超时（超过最大等待时间）")
    sys.exit(1)


def download_image(url, output_path):
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


def edit_image(image_paths, prompt, model=None, negative_prompt=None, 
               output=None, seed=None, steps=None, guidance=None):
    token = get_token()
    
    model = model or DEFAULT_MODEL
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if output:
        output_path = Path(output)
    else:
        output_path = Path(DEFAULT_OUTPUT) / f"edited_image_{timestamp}.png"
    
    print(f"🎨 提交图像编辑任务...")
    print(f"📝 提示词: {prompt}")
    print(f"🤖 模型: {model}")
    print(f"🖼️ 输入图像: {', '.join([str(p) for p in image_paths])}")
    if negative_prompt:
        print(f"🚫 负向提示词: {negative_prompt}")
    
    result = submit_task(token, image_paths, prompt, model, negative_prompt, seed, steps, guidance)
    
    task_id = result.get("task_id")
    if not task_id:
        print("错误: 未获取到任务 ID")
        print(f"响应: {result}")
        sys.exit(1)
    
    print(f"📋 任务 ID: {task_id}")
    print("⏳ 等待任务完成...")
    
    task_result = poll_task_status(token, task_id)
    
    images = task_result.get("output_images", [])
    if not images:
        print("错误: 未获取到编辑后的图像")
        print(f"完整响应: {task_result}")
        sys.exit(1)
    
    image_url = images[0]
    print(f"⬇️  下载图像: {image_url}")
    
    if download_image(image_url, output_path):
        print(f"\n✅ 图像编辑成功！")
        print(f"💾 保存路径: {output_path.absolute()}")
        return str(output_path.absolute())
    else:
        print("❌ 图像保存失败")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="ModelScope 图像编辑工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基础用法 - 编辑单张图片
  python edit_image.py --image input.png --prompt "把背景改成日落"
  
  # 多人合照合成
  python edit_image.py --image person1.png --image person2.png --prompt "两人站在一起"
  
  # 风格转换
  python edit_image.py --image photo.png --prompt "转换成吉卜力风格"
  
  # 局部编辑
  python edit_image.py --image photo.png --prompt "给猫戴上墨镜"

推荐模型:
  Qwen/Qwen-Image-Edit-2511 - 最新版，角色一致性好
  Qwen/Qwen-Image-Edit-2509 - 稳定版本
  Qwen/Qwen-Image-Edit     - 基础版本
        """
    )
    
    parser.add_argument(
        "--image", "-i",
        required=True,
        action="append",
        dest="images",
        help="输入图像路径（可多次指定以输入多张图片）"
    )
    
    parser.add_argument(
        "--prompt", "-p",
        required=True,
        help="编辑提示词，描述想要的修改"
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
        help="随机种子"
    )
    
    parser.add_argument(
        "--steps",
        type=int,
        help="采样步数"
    )
    
    parser.add_argument(
        "--guidance",
        type=float,
        help="引导系数"
    )
    
    args = parser.parse_args()
    
    for img_path in args.images:
        if not os.path.exists(img_path):
            print(f"错误: 图像文件不存在: {img_path}")
            sys.exit(1)
    
    edit_image(
        image_paths=args.images,
        prompt=args.prompt,
        model=args.model,
        negative_prompt=args.negative_prompt,
        output=args.output,
        seed=args.seed,
        steps=args.steps,
        guidance=args.guidance
    )


if __name__ == "__main__":
    main()
