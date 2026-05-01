#!/usr/bin/env python3
"""
ModelScope 文生图模型列表查询脚本
获取 ModelScope 平台上可用的文生图模型
"""

import argparse
import json
import sys
from urllib.parse import urlencode

try:
    import requests
except ImportError:
    print("错误: 需要安装 requests 库")
    print("请运行: pip install requests")
    sys.exit(1)

MODELSCOPE_OPENAPI_BASE = "https://modelscope.cn/openapi/v1"
DEFAULT_TASK = "text-to-image-synthesis"
DEFAULT_PAGE_SIZE = 20


def list_models(search=None, task=None, owner=None, sort="downloads", 
                page_number=1, page_size=DEFAULT_PAGE_SIZE, json_output=False):
    url = f"{MODELSCOPE_OPENAPI_BASE}/models"
    
    params = {
        "page_number": page_number,
        "page_size": page_size,
        "sort": sort
    }
    
    if task:
        params["filter.task"] = task
    else:
        params["filter.task"] = DEFAULT_TASK
    
    if search:
        params["search"] = search
    if owner:
        params["owner"] = owner
    
    headers = {
        "Accept": "application/json"
    }
    
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code != 200:
        print(f"错误: 获取模型列表失败 ({response.status_code})")
        print(f"响应: {response.text}")
        sys.exit(1)
    
    data = response.json()
    
    if json_output:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return
    
    if not data.get("success"):
        print("错误: API 返回失败")
        print(data)
        sys.exit(1)
    
    models = data.get("data", {}).get("models", [])
    total_count = data.get("data", {}).get("total_count", 0)
    
    print(f"📋 文生图模型列表 (共 {total_count} 个)")
    print("=" * 80)
    
    if search:
        print(f"🔍 搜索关键词: {search}")
    if owner:
        print(f"👤 作者筛选: {owner}")
    print()
    
    for i, model in enumerate(models, 1):
        model_id = model.get("id", "N/A")
        display_name = model.get("display_name", "")
        downloads = model.get("downloads", 0)
        likes = model.get("likes", 0)
        description = model.get("description", "")
        license_info = model.get("license", "")
        
        print(f"{i}. {model_id}")
        if display_name:
            print(f"   名称: {display_name}")
        print(f"   📥 下载: {downloads:,} | ❤️  喜欢: {likes:,}")
        if license_info:
            print(f"   📜 许可: {license_info}")
        if description:
            desc = description[:100] + "..." if len(description) > 100 else description
            print(f"   📝 {desc}")
        print()
    
    if total_count > page_size * page_number:
        print(f"... 还有 {total_count - page_size * page_number} 个模型未显示")
        print(f"使用 --page {page_number + 1} 查看更多")


def main():
    parser = argparse.ArgumentParser(
        description="ModelScope 文生图模型列表查询工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 列出热门文生图模型
  python list_models.py
  
  # 搜索特定模型
  python list_models.py --search "flux"
  python list_models.py --search "qwen"
  
  # 按作者筛选
  python list_models.py --owner "Qwen"
  
  # 按喜欢数排序
  python list_models.py --sort likes
  
  # 输出 JSON 格式
  python list_models.py --json
  
  # 查看更多结果
  python list_models.py --page 2 --page-size 50
        """
    )
    
    parser.add_argument(
        "--search", "-s",
        help="搜索关键词"
    )
    
    parser.add_argument(
        "--task", "-t",
        default=DEFAULT_TASK,
        help=f"任务类型 (默认: {DEFAULT_TASK})"
    )
    
    parser.add_argument(
        "--owner", "-o",
        help="按作者筛选"
    )
    
    parser.add_argument(
        "--sort",
        choices=["default", "downloads", "likes", "last_modified"],
        default="downloads",
        help="排序方式 (默认: downloads)"
    )
    
    parser.add_argument(
        "--page",
        type=int,
        default=1,
        help="页码 (默认: 1)"
    )
    
    parser.add_argument(
        "--page-size",
        type=int,
        default=DEFAULT_PAGE_SIZE,
        help=f"每页数量 (默认: {DEFAULT_PAGE_SIZE}, 最大: 50)"
    )
    
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="输出 JSON 格式"
    )
    
    args = parser.parse_args()
    
    list_models(
        search=args.search,
        task=args.task,
        owner=args.owner,
        sort=args.sort,
        page_number=args.page,
        page_size=min(args.page_size, 50),
        json_output=args.json
    )


if __name__ == "__main__":
    main()
