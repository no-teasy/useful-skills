#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动归档脚本 - 将超过 24 小时的短期记忆自动归档

使用方法:
    python scripts/auto_archive.py           # 归档所有过期文件
    python scripts/auto_archive.py --check   # 仅检查，不执行归档
    python scripts/auto_archive.py --clean   # 清理 30 天前的归档文件
"""

import argparse
from datetime import datetime, timedelta
from pathlib import Path

# 获取脚本所在目录
SCRIPT_DIR = Path(__file__).parent
SHORT_TERM_DIR = SCRIPT_DIR.parent / "short-term"
ARCHIVED_DIR = SHORT_TERM_DIR / "archived"

# 归档保留天数
ARCHIVE_RETENTION_DAYS = 30


def get_yesterday_date():
    """获取昨天的日期"""
    return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")


def auto_archive(dry_run=False):
    """自动归档超过 24 小时的短期记忆"""
    now = datetime.now()
    archived_count = 0

    # 确保归档目录存在
    ARCHIVED_DIR.mkdir(parents=True, exist_ok=True)

    # 遍历所有短期记忆文件
    for file_path in SHORT_TERM_DIR.glob("*.md"):
        if file_path.name == "README.md":
            continue

        # 从文件名解析日期
        try:
            file_date_str = file_path.stem  # 如 "2026-03-11"
            file_date = datetime.strptime(file_date_str, "%Y-%m-%d")

            # 计算文件年龄（小时）
            age_hours = (now - file_date).total_seconds() / 3600

            # 如果超过 24 小时，归档
            if age_hours > 24:
                if dry_run:
                    print(f"📦 [将归档] {file_path.name} (已 {age_hours:.1f} 小时)")
                else:
                    dest_path = ARCHIVED_DIR / file_path.name
                    # 使用 try-except 处理文件冲突（避免 TOCTOU 问题）
                    try:
                        file_path.rename(dest_path)
                        archived_count += 1
                    except FileExistsError:
                        # 目标已存在，生成带时间戳的唯一文件名
                        timestamp = datetime.now().strftime("%H%M%S")
                        dest_path = ARCHIVED_DIR / f"{file_path.stem}_{timestamp}.md"
                        file_path.rename(dest_path)
                        archived_count += 1
                    except PermissionError:
                        print(f"⚠️  权限错误：无法归档 {file_path.name}")
                    except OSError as e:
                        print(f"⚠️  归档失败 {file_path.name}: {e}")
        except ValueError:
            pass  # 跳过无法解析的文件

    if archived_count > 0:
        print(f"📦 已归档 {archived_count} 个过期短期记忆文件")

    return archived_count


def clean_old_archives():
    """清理 30 天前的归档文件"""
    now = datetime.now()
    cleaned_count = 0
    
    print(f"🧹 清理过期归档文件...")
    print(f"   保留期限：{ARCHIVE_RETENTION_DAYS} 天")
    print()
    
    for file_path in ARCHIVED_DIR.glob("*.md"):
        try:
            file_date_str = file_path.stem
            file_date = datetime.strptime(file_date_str, "%Y-%m-%d")
            
            age_days = (now - file_date).days
            
            if age_days > ARCHIVE_RETENTION_DAYS:
                file_path.unlink()
                print(f"🗑️  [已删除] {file_path.name} (已 {age_days} 天)")
                cleaned_count += 1
            else:
                print(f"📦 [保留] {file_path.name} (已 {age_days} 天)")
        
        except ValueError:
            print(f"⚠️  [跳过] {file_path.name} - 无法解析日期")
    
    print()
    print(f"✅ 清理完成，共删除 {cleaned_count} 个文件")
    
    return cleaned_count


def show_status():
    """显示短期记忆状态"""
    now = datetime.now()
    
    print("📊 短期记忆状态")
    print("=" * 50)
    print()
    
    # 当前短期记忆
    current_files = [f for f in SHORT_TERM_DIR.glob("*.md") if f.name != "README.md"]
    print(f"📂 当前短期记忆：{len(current_files)} 个")
    for file_path in sorted(current_files):
        try:
            file_date = datetime.strptime(file_path.stem, "%Y-%m-%d")
            age_hours = (now - file_date).total_seconds() / 3600
            status = "⚠️  待归档" if age_hours > 24 else "✅ 正常"
            print(f"   {status} {file_path.name} ({age_hours:.1f} 小时)")
        except ValueError:
            print(f"   ❓ {file_path.name} (日期格式错误)")
    
    print()
    
    # 归档文件
    archived_files = list(ARCHIVED_DIR.glob("*.md"))
    print(f"🗄️  已归档：{len(archived_files)} 个")
    if archived_files:
        # 显示最近 5 个
        for file_path in sorted(archived_files)[-5:]:
            try:
                file_date = datetime.strptime(file_path.stem, "%Y-%m-%d")
                age_days = (now - file_date).days
                print(f"   📦 {file_path.name} ({age_days} 天)")
            except ValueError:
                print(f"   ❓ {file_path.name} (日期格式错误)")
    
    print()
    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(description='短期记忆自动归档工具', add_help=True)
    parser.add_argument('--check', action='store_true', help='仅检查，不执行归档')
    parser.add_argument('--clean', action='store_true', help='清理 30 天前的归档文件')
    parser.add_argument('--status', action='store_true', help='显示状态')
    
    args = parser.parse_args()
    
    if args.status:
        show_status()
    elif args.clean:
        clean_old_archives()
    else:
        auto_archive(dry_run=args.check)


if __name__ == '__main__':
    main()
