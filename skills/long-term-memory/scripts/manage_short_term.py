#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
短期记忆管理脚本 - 管理 24 小时内的临时记忆

使用方法:
    python scripts/manage_short_term.py add --content "内容" --agent chat --section morning
    python scripts/manage_short_term.py show --date 2026-03-11
    python scripts/manage_short_term.py list
    python scripts/manage_short_term.py archive --date 2026-03-10
"""

import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path

# 获取脚本所在目录
SCRIPT_DIR = Path(__file__).parent
SHORT_TERM_DIR = SCRIPT_DIR.parent / "short-term"
ARCHIVED_DIR = SHORT_TERM_DIR / "archived"


def get_today_date():
    """获取今天的日期"""
    return datetime.now().strftime("%Y-%m-%d")


def get_today_datetime():
    """获取今天的日期时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_time_section():
    """获取当前时间段"""
    hour = datetime.now().hour
    if 0 <= hour < 12:
        return "上午"
    elif 12 <= hour < 18:
        return "下午"
    else:
        return "晚上"


def get_or_create_today_file():
    """获取或创建今天的短期记忆文件（使用原子操作避免竞争条件）"""
    today = get_today_date()
    file_path = SHORT_TERM_DIR / f"{today}.md"

    if file_path.exists():
        return file_path

    # 创建新文件内容
    content = f"""---
date: {today}
created: {get_today_datetime()}
updated: {get_today_datetime()}
agents: []
---

# 短期记忆 {today}

> 本文件记录 {today} 的短期记忆，24 小时后自动归档到 archived/ 目录。

---

## 时间线

### 上午 (00:00-12:00)

<!-- 暂无记录 -->

### 下午 (12:00-18:00)

<!-- 暂无记录 -->

### 晚上 (18:00-24:00)

<!-- 暂无记录 -->

---

## 今日摘要

### 待跟进事项
- [ ]

### 临时信息
-

### 情绪状态
- 无特殊记录

---

## Agent 间消息

<!-- 用于多个 Agent 之间传递信息 -->

| 时间 | 发送 Agent | 接收 Agent | 消息内容 |
|------|-----------|-----------|----------|

---
"""

    # 使用 exclusive create 避免竞争条件
    try:
        # 尝试创建文件（如果已存在则抛出 FileExistsError）
        file_path.touch(exist_ok=False)
        # 写入初始内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
    except FileExistsError:
        # 另一个进程已创建文件，直接返回
        return file_path
    except PermissionError:
        print(f"❌ 权限错误：无法创建 {file_path}")
        raise
    except OSError as e:
        print(f"❌ 创建文件失败：{e}")
        raise


def add_memory(content, agent="chat", section=None):
    """添加短期记忆"""
    file_path = get_or_create_today_file()
    
    with open(file_path, 'r', encoding='utf-8') as f:
        file_content = f.read()
    
    # 确定时间段
    if section is None:
        section = get_time_section()
    
    section_map = {
        "上午": "上午 (00:00-12:00)",
        "下午": "下午 (12:00-18:00)",
        "晚上": "晚上 (18:00-24:00)",
        "morning": "上午 (00:00-12:00)",
        "afternoon": "下午 (12:00-18:00)",
        "evening": "晚上 (18:00-24:00)"
    }
    
    section_title = section_map.get(section, f"{section} (00:00-12:00)")
    
    # 生成 session ID
    session_id = f"session-{datetime.now().strftime('%H%M%S')}"
    timestamp = datetime.now().strftime("%H:%M")
    
    # 创建记忆条目
    memory_entry = f"""
<!-- @session id: {session_id} | agent: {agent} | time: {timestamp} -->

**用户**：{content}

**关键信息**：
- 记录时间：{timestamp}

<!-- @end -->
"""
    
    # 找到对应时间段并插入 - 使用更灵活的正则表达式
    pattern = rf'(### {re.escape(section_title)}\n\n)(.*?)(?=\n### |\n---\n|\Z)'
    match = re.search(pattern, file_content, re.DOTALL)
    
    if match:
        # 替换"暂无记录"
        section_content = match.group(2)
        if "暂无记录" in section_content:
            section_content = section_content.replace("<!-- 暂无记录 -->", memory_entry.strip())
        else:
            section_content += memory_entry
        
        file_content = file_content[:match.start()] + match.group(1) + section_content + file_content[match.end():]
    else:
        print(f"⚠️  未找到时间段：{section_title}")
        print(f"   请检查文件格式是否正确")
        return False
    
    # 更新时间
    file_content = re.sub(
        r'updated: \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',
        f'updated: {get_today_datetime()}',
        file_content
    )
    
    # 更新 agents 列表
    if f'{agent}' not in file_content:
        file_content = re.sub(
            r'agents: \[\]',
            f'agents: [{agent}]',
            file_content
        )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(file_content)
    
    print(f"✅ 已添加短期记忆")
    print(f"   时间：{timestamp}")
    print(f"   Agent: {agent}")
    print(f"   文件：{file_path.name}")
    
    return True


def show_memory(date=None):
    """显示指定日期的短期记忆"""
    if date is None:
        date = get_today_date()
    
    file_path = SHORT_TERM_DIR / f"{date}.md"
    
    if not file_path.exists():
        # 检查归档文件
        file_path = ARCHIVED_DIR / f"{date}.md"
        if not file_path.exists():
            print(f"❌ 未找到日期 {date} 的短期记忆")
            return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📖 短期记忆 {date}")
    print("=" * 50)
    print(content)


def list_memories():
    """列出所有短期记忆文件"""
    print("📋 短期记忆列表\n")
    
    # 当前短期记忆
    print("📂 当前短期记忆:")
    for file_path in sorted(SHORT_TERM_DIR.glob("*.md")):
        if file_path.name == "README.md":
            continue
        stats = file_path.stat()
        size = stats.st_size
        print(f"   📄 {file_path.name} ({size} bytes)")
    
    print()
    
    # 归档文件
    print("🗄️  已归档:")
    archived_files = list(ARCHIVED_DIR.glob("*.md"))
    if archived_files:
        for file_path in sorted(archived_files)[-10:]:  # 只显示最近 10 个
            stats = file_path.stat()
            size = stats.st_size
            print(f"   📦 {file_path.name} ({size} bytes)")
    else:
        print("   (无)")


def archive_memory(date=None):
    """归档指定日期的短期记忆"""
    if date is None:
        # 归档昨天的文件
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        date = yesterday
    else:
        yesterday = date
    
    file_path = SHORT_TERM_DIR / f"{yesterday}.md"
    
    if not file_path.exists():
        print(f"❌ 未找到日期 {yesterday} 的短期记忆")
        return False
    
    # 移动到归档目录
    dest_path = ARCHIVED_DIR / f"{yesterday}.md"
    file_path.rename(dest_path)
    
    print(f"✅ 已归档 {yesterday} 的短期记忆")
    print(f"   位置：{dest_path}")
    
    return True


def add_followup(item):
    """添加待跟进事项"""
    file_path = get_or_create_today_file()
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到待跟进事项部分
    pattern = r'(### 待跟进事项\n)(.*?)(?=\n### |\n---\n)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        new_item = f"- [ ] {item}\n"
        section_content = match.group(2)
        if "- [ ] " not in section_content or "暂无" in section_content:
            section_content = new_item
        else:
            section_content += new_item
        
        content = content[:match.start()] + match.group(1) + section_content + content[match.end():]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已添加待跟进事项：{item}")


def add_agent_message(from_agent, to_agent, message):
    """添加 Agent 间消息"""
    file_path = get_or_create_today_file()
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    timestamp = datetime.now().strftime("%H:%M")
    
    # 找到 Agent 间消息表格
    pattern = r'(\| 时间 \| 发送 Agent \| 接收 Agent \| 消息内容 \|\n\|------\|-----------\|-----------\|----------\|\n)(.*?)(?=\n---\n|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        new_row = f"| {timestamp} | {from_agent} | {to_agent} | {message} |\n"
        table_content = match.group(2)
        if table_content.strip() == "":
            table_content = new_row
        else:
            table_content += new_row
        
        content = content[:match.start()] + match.group(1) + table_content + content[match.end():]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已添加 Agent 消息：{from_agent} → {to_agent}")


def main():
    parser = argparse.ArgumentParser(description='短期记忆管理工具', add_help=True)
    subparsers = parser.add_subparsers(dest='command', help='命令类型')
    
    # add 命令
    add_parser = subparsers.add_parser('add', help='添加短期记忆')
    add_parser.add_argument('--content', required=True, help='记忆内容')
    add_parser.add_argument('--agent', default='chat', help='Agent 名称')
    add_parser.add_argument('--section', choices=['上午', '下午', '晚上', 'morning', 'afternoon', 'evening'], help='时间段')
    
    # show 命令
    show_parser = subparsers.add_parser('show', help='显示短期记忆')
    show_parser.add_argument('--date', help='日期 (YYYY-MM-DD)')
    
    # list 命令
    list_parser = subparsers.add_parser('list', help='列出所有短期记忆')
    
    # archive 命令
    archive_parser = subparsers.add_parser('archive', help='归档短期记忆')
    archive_parser.add_argument('--date', help='日期 (YYYY-MM-DD)')
    
    # followup 命令
    followup_parser = subparsers.add_parser('followup', help='添加待跟进事项')
    followup_parser.add_argument('--item', required=True, help='待跟进事项')
    
    # message 命令
    message_parser = subparsers.add_parser('message', help='添加 Agent 间消息')
    message_parser.add_argument('--from', dest='from_agent', required=True, help='发送 Agent')
    message_parser.add_argument('--to', dest='to_agent', required=True, help='接收 Agent')
    message_parser.add_argument('--content', required=True, help='消息内容')
    
    args = parser.parse_args()
    
    if args.command == 'add':
        add_memory(args.content, args.agent, args.section)
    elif args.command == 'show':
        show_memory(args.date)
    elif args.command == 'list':
        list_memories()
    elif args.command == 'archive':
        archive_memory(args.date)
    elif args.command == 'followup':
        add_followup(args.item)
    elif args.command == 'message':
        add_agent_message(args.from_agent, args.to_agent, args.content)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
