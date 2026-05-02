#!/usr/bin/env python3
"""
ModelScope 图像编辑脚本 - 本地部署版
使用 ModelScope Python SDK 进行图像编辑
需要本地 GPU 环境
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    from modelscope.pipelines import pipeline
    from modelscope.utils.constant import Tasks
    from PIL import Image
except ImportError:
    print("错误: 需要安装 ModelScope SDK")
    print("请运行: pip install modelscope")
    print("推荐安装最新版本: pip install git+https://github.com/modelscope/modelscope.git")
    sys.exit(1)

try:
    import torch
    if not torch.cuda.is_available():
        print("警告: 未检测到 CUDA GPU，推理速度可能较慢")
except ImportError:
    print("错误: 需要安装 PyTorch")
    print("请运行: pip install torch torchvision")

DEFAULT_MODEL = os.environ.get("MODELSCOPE_EDIT_MODEL", "damo/Qwen-Image-Edit-2509")
DEFAULT_OUTPUT = "./outputs"


def edit_image_local(image_path, prompt, model=None, negative_prompt=None, output=None):
    model = model or DEFAULT_MODEL
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if output:
        output_path = Path(output)
    else:
        output_path = Path(DEFAULT_OUTPUT) / f"edited_image_{timestamp}.png"
    
    print(f"🎨 初始化图像编辑管道...")
    print(f"🤖 模型: {model}")
    
    try:
        image_edit_pipeline = pipeline(
            task=Tasks.image_editing,
            model=model
        )
        
        print(f"📝 提示词: {prompt}")
        print(f"🖼️ 输入图像: {image_path}")
        print("⏳ 正在处理...")
        
        input_data = {
            'image': image_path,
            'text': prompt
        }
        
        if negative_prompt:
            input_data['negative_prompt'] = negative_prompt
        
        result = image_edit_pipeline(input_data)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if isinstance(result, dict) and 'output_img' in result:
            result['output_img'].save(output_path)
        else:
            result.save(output_path)
        
        print(f"\n✅ 图像编辑成功！")
        print(f"💾 保存路径: {output_path.absolute()}")
        return str(output_path.absolute())
        
    except Exception as e:
        print(f"❌ 图像编辑失败: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="ModelScope 图像编辑工具（本地部署版）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
要求:
  - GPU: 至少 12GB VRAM（FP16）或 10GB（BF16）
  - 不支持纯 CPU 模式

安装依赖:
  pip install modelscope torch torchvision
  # 或安装最新版本
  pip install git+https://github.com/modelscope/modelscope.git

示例:
  # 基础编辑
  python edit_image_local.py --image input.png --prompt "把背景改成日落"
  
  # 多人合成
  python edit_image_local.py --image person1.png --prompt "两人站在一起"
  
  # 风格转换
  python edit_image_local.py --image portrait.png --prompt "转换成吉卜力风格"
        """
    )
    
    parser.add_argument(
        "--image", "-i",
        required=True,
        help="输入图像路径"
    )
    
    parser.add_argument(
        "--prompt", "-p",
        required=True,
        help="编辑提示词"
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
    
    args = parser.parse_args()
    
    if not os.path.exists(args.image):
        print(f"错误: 图像文件不存在: {args.image}")
        sys.exit(1)
    
    edit_image_local(
        image_path=args.image,
        prompt=args.prompt,
        model=args.model,
        negative_prompt=args.negative_prompt,
        output=args.output
    )


if __name__ == "__main__":
    main()
