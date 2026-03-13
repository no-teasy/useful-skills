#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
记忆管理脚本 - 用于添加、搜索、列出和删除记忆条目

使用方法:
    python manage_memories.py add --file user-preferences.md --title "标题" --content "内容"
    python manage_memories.py search --query "关键词"
    python manage_memories.py list
    python manage_memories.py delete --file user-preferences.md --title "标题"
    python manage_memories.py update --file user-preferences.md --title "标题" --content "新内容"
"""

import argparse
import os
import re
from datetime import datetime
from pathlib import Path

# 获取脚本所在目录
SCRIPT_DIR = Path(__file__).parent
MEMORIES_DIR = SCRIPT_DIR.parent / "memories"

# 记忆文件类别
MEMORY_FILES = [
    "user-preferences.md",
    "user-profile.md",
    "decisions-context.md",
    "tasks-reminder.md",
    "knowledge-base.md"
]


def get_today():
    """获取今天的日期（ISO 格式）"""
    return datetime.now().strftime("%Y-%m-%d")


def parse_meta(meta_line):
    """解析 meta 注释行"""
    match = re.search(r'@meta\s+(.+?)\s*-->', meta_line)
    if not match:
        return {}
    
    meta_str = match.group(1)
    meta = {}
    
    # 解析键值对
    pairs = re.findall(r'(\w+):\s*([^|]+)', meta_str)
    for key, value in pairs:
        meta[key.strip()] = value.strip()
    
    return meta


def find_memory_entry(content, title):
    """查找记忆条目的位置"""
    pattern = rf'## {re.escape(title)}\s*\n\s*<!--\s*@meta.+?-->\s*\n(.*?)<!--\s*@end\s*-->'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.start(), match.end(), match.group(0)
    return None


def add_memory(file_name, title, content, tags=""):
    """添加新的记忆条目"""
    file_path = MEMORIES_DIR / file_name
    
    if not file_path.exists():
        print(f"❌ 文件不存在：{file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        existing_content = f.read()
    
    # 检查是否已存在相同标题
    if find_memory_entry(existing_content, title):
        print(f"⚠️  已存在标题为 '{title}' 的记忆条目")
        return False
    
    # 生成 meta 信息
    today = get_today()
    category = file_name.replace('.md', '')
    meta = f"<!-- @meta category: {category} | tags: {tags} | created: {today} | updated: {today} -->"
    
    # 创建新的记忆条目
    new_entry = f"""
## {title}

{meta}

{content}

<!-- @end -->
"""
    
    # 追加到文件末尾
    try:
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(new_entry)
        print(f"✅ 已添加记忆：{title}")
        print(f"   文件：{file_name}")
        print(f"   标签：{tags}")
        return True
    except PermissionError:
        print(f"❌ 权限错误：无法写入 {file_name}")
        print("   请检查文件权限或使用管理员权限运行")
        return False
    except OSError as e:
        print(f"❌ 写入失败：{e}")
        print("   请检查磁盘空间或文件是否被占用")
        return False


def search_memory(query):
    """搜索记忆条目"""
    results = []
    query = query.strip()  # 去除首尾空格
    
    for file_name in MEMORY_FILES:
        file_path = MEMORIES_DIR / file_name
        if not file_path.exists():
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找所有记忆条目
        pattern = r'## (.+?)\s*\n\s*(<!--\s*@meta.+?-->)\s*\n(.*?)<!--\s*@end\s*-->'
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for match in matches:
            title = match.group(1).strip()
            meta_line = match.group(2)
            entry_content = match.group(3).strip()
            
            # 检查是否匹配查询（不区分大小写）
            query_lower = query.lower()
            if query_lower in title.lower() or query_lower in entry_content.lower() or query_lower in meta_line.lower():
                meta = parse_meta(meta_line)
                results.append({
                    'file': file_name,
                    'title': title,
                    'meta': meta,
                    'content': entry_content[:200] + '...' if len(entry_content) > 200 else entry_content
                })
    
    if not results:
        print(f"❌ 未找到匹配 '{query}' 的记忆")
        return
    
    print(f"📋 找到 {len(results)} 条匹配的记忆：\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. [{result['file']}] {result['title']}")
        print(f"   标签：{result['meta'].get('tags', '无')}")
        print(f"   内容：{result['content']}")
        print()


def list_memories():
    """列出所有记忆条目"""
    print("📚 记忆文件列表：\n")
    
    for file_name in MEMORY_FILES:
        file_path = MEMORIES_DIR / file_name
        if not file_path.exists():
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找所有记忆条目
        pattern = r'## (.+?)\s*\n\s*(<!--\s*@meta.+?-->)'
        matches = re.finditer(pattern, content)
        
        entries = []
        for match in matches:
            title = match.group(1).strip()
            meta_line = match.group(2)
            meta = parse_meta(meta_line)
            entries.append({
                'title': title,
                'tags': meta.get('tags', '无'),
                'created': meta.get('created', '未知'),
                'updated': meta.get('updated', '未知')
            })
        
        if entries:
            print(f"📄 {file_name} ({len(entries)} 条)")
            for entry in entries:
                print(f"   • {entry['title']}")
                print(f"     标签：{entry['tags']} | 创建：{entry['created']} | 更新：{entry['updated']}")
            print()


def delete_memory(file_name, title):
    """删除记忆条目"""
    file_path = MEMORIES_DIR / file_name

    if not file_path.exists():
        print(f"❌ 文件不存在：{file_path}")
        return False

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except PermissionError:
        print(f"❌ 权限错误：无法读取 {file_name}")
        return False
    except OSError as e:
        print(f"❌ 读取失败：{e}")
        return False

    # 查找要删除的条目
    result = find_memory_entry(content, title)
    if not result:
        print(f"❌ 未找到标题为 '{title}' 的记忆条目")
        return False

    start, end, _ = result

    # 删除条目（包括前后的空行）
    new_content = content[:start].rstrip() + '\n\n' + content[end:].lstrip()

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ 已删除记忆：{title}")
        return True
    except PermissionError:
        print(f"❌ 权限错误：无法写入 {file_name}")
        return False
    except OSError as e:
        print(f"❌ 写入失败：{e}")
        return False


def update_memory(file_name, title, new_content):
    """更新记忆条目内容"""
    file_path = MEMORIES_DIR / file_name

    if not file_path.exists():
        print(f"❌ 文件不存在：{file_path}")
        return False

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except PermissionError:
        print(f"❌ 权限错误：无法读取 {file_name}")
        return False
    except OSError as e:
        print(f"❌ 读取失败：{e}")
        return False

    # 查找要更新的条目
    result = find_memory_entry(content, title)
    if not result:
        print(f"❌ 未找到标题为 '{title}' 的记忆条目")
        return False

    start, end, old_entry = result

    # 提取旧的 meta 信息
    meta_match = re.search(r'(<!--\s*@meta.+?-->)', old_entry, re.DOTALL)
    if not meta_match:
        print("❌ 无法找到 meta 信息")
        return False

    old_meta = meta_match.group(1)

    # 更新 meta 中的 updated 日期
    today = get_today()
    new_meta = re.sub(r'updated:\s*\d{4}-\d{2}-\d{2}', f'updated: {today}', old_meta)

    # 创建新的记忆条目
    new_entry = f"""## {title}

{new_meta}

{new_content}

<!-- @end -->
"""

    # 替换旧条目
    new_file_content = content[:start] + new_entry + content[end:]

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_file_content)
        print(f"✅ 已更新记忆：{title}")
        print(f"   文件：{file_name}")
        return True
    except PermissionError:
        print(f"❌ 权限错误：无法写入 {file_name}")
        return False
    except OSError as e:
        print(f"❌ 写入失败：{e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='记忆管理工具', add_help=True)
    subparsers = parser.add_subparsers(dest='command', help='命令类型')
    
    # add 命令
    add_parser = subparsers.add_parser('add', help='添加新的记忆条目')
    add_parser.add_argument('--file', required=True, choices=MEMORY_FILES, help='记忆文件名')
    add_parser.add_argument('--title', required=True, help='记忆标题')
    add_parser.add_argument('--content', required=True, help='记忆内容')
    add_parser.add_argument('--tags', default='', help='标签（逗号分隔）')
    
    # search 命令
    search_parser = subparsers.add_parser('search', help='搜索记忆条目')
    search_parser.add_argument('--query', required=True, help='搜索关键词')
    
    # list 命令
    list_parser = subparsers.add_parser('list', help='列出所有记忆条目')
    
    # delete 命令
    delete_parser = subparsers.add_parser('delete', help='删除记忆条目')
    delete_parser.add_argument('--file', required=True, choices=MEMORY_FILES, help='记忆文件名')
    delete_parser.add_argument('--title', required=True, help='记忆标题')
    
    # update 命令
    update_parser = subparsers.add_parser('update', help='更新记忆条目')
    update_parser.add_argument('--file', required=True, choices=MEMORY_FILES, help='记忆文件名')
    update_parser.add_argument('--title', required=True, help='记忆标题')
    update_parser.add_argument('--content', required=True, help='新的记忆内容')
    
    args = parser.parse_args()
    
    if args.command == 'add':
        add_memory(args.file, args.title, args.content, args.tags)
    elif args.command == 'search':
        search_memory(args.query)
    elif args.command == 'list':
        list_memories()
    elif args.command == 'delete':
        delete_memory(args.file, args.title)
    elif args.command == 'update':
        update_memory(args.file, args.title, args.content)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
