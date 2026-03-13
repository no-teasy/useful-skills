#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置检查和引导脚本

使用方法:
    python scripts/check_config.py              # 检查配置状态
    python scripts/check_config.py --guide      # 引导用户配置
    python scripts/check_config.py --reset      # 重置配置
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# 获取脚本所在目录
SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent

# 配置文件路径
ENV_FILE = SKILL_DIR / ".env"
CONFIG_MARKER = SKILL_DIR / "configured.txt"


def check_env_file():
    """检查 .env 文件是否存在并有效"""
    if not ENV_FILE.exists():
        return False, ".env 文件不存在"
    
    # 读取并检查必要配置
    with open(ENV_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'OPENAI_API_KEY' not in content or 'sk-' not in content:
        return False, "OPENAI_API_KEY 未配置或格式不正确"
    
    return True, "配置有效"


def check_marker_file():
    """检查配置标记文件"""
    return CONFIG_MARKER.exists()


def create_marker_file():
    """创建配置标记文件"""
    with open(CONFIG_MARKER, 'w', encoding='utf-8') as f:
        f.write(f"# 配置完成标记\n")
        f.write(f"# Configuration completed at: {datetime.now().isoformat()}\n")
        f.write(f"# \n")
        f.write(f"# 如果删除此文件，下次运行时会重新引导配置\n")
        f.write(f"# Delete this file to re-run the configuration guide\n")


def delete_marker_file():
    """删除配置标记文件"""
    if CONFIG_MARKER.exists():
        CONFIG_MARKER.unlink()


def guide_configuration():
    """引导用户配置"""
    print("=" * 60)
    print("🔧 记忆系统配置向导")
    print("=" * 60)
    print()
    
    # 检查是否已配置
    is_valid, message = check_env_file()
    if is_valid:
        print("✅ 检测到已有配置")
        print(f"   {message}")
        print()
        
        response = input("是否要重新配置？(y/N): ").strip().lower()
        if response != 'y':
            print("✅ 使用现有配置")
            create_marker_file()
            return True
    
    print("📋 开始配置")
    print()
    
    # 收集配置信息
    config = {}
    
    # API Key
    print("1️⃣  OpenAI API Key")
    print("   请输入你的 API Key（格式：sk-xxx）")
    api_key = input("   OPENAI_API_KEY: ").strip()
    
    while not api_key.startswith('sk-'):
        print("   ❌ API Key 格式不正确，应以 sk- 开头")
        api_key = input("   请重新输入 OPENAI_API_KEY: ").strip()
    
    config['api_key'] = api_key
    print()
    
    # Base URL（可选）
    print("2️⃣  API Base URL（可选）")
    print("   如果使用 OpenAI 官方 API，直接回车跳过")
    print("   如果使用 Azure OpenAI 或其他兼容服务，请输入完整 URL")
    base_url = input("   OPENAI_BASE_URL: ").strip()
    
    if base_url:
        config['base_url'] = base_url
    print()
    
    # 嵌入模型（可选）
    print("3️⃣  嵌入模型名称（可选）")
    print("   默认：text-embedding-3-small")
    print("   可选：text-embedding-3-large, bge-large-zh-v1.5 等")
    model_name = input("   OPENAI_EMBEDDING_MODEL [text-embedding-3-small]: ").strip()
    
    if not model_name:
        model_name = "text-embedding-3-small"
    config['model_name'] = model_name
    print()
    
    # 确认配置
    print("📋 配置确认")
    print("-" * 60)
    print(f"OPENAI_API_KEY = {api_key[:8]}...{api_key[-3:]}")
    if base_url:
        print(f"OPENAI_BASE_URL = {base_url}")
    print(f"OPENAI_EMBEDDING_MODEL = {model_name}")
    print("-" * 60)
    print()
    
    confirm = input("确认保存配置？(y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ 配置已取消")
        return False
    
    # 写入 .env 文件
    env_content = f"""# OpenAI API 配置
# 由配置向导自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OPENAI_API_KEY={api_key}
"""
    
    if base_url:
        env_content += f"OPENAI_BASE_URL={base_url}\n"
    
    if model_name and model_name != "text-embedding-3-small":
        env_content += f"OPENAI_EMBEDDING_MODEL={model_name}\n"
    
    try:
        with open(ENV_FILE, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("✅ 配置已保存到 .env 文件")
        
        # 创建标记文件
        create_marker_file()
        print("✅ 配置完成标记已创建")
        
        print()
        print("=" * 60)
        print("🎉 配置完成！")
        print("=" * 60)
        print()
        print("下一步：")
        print("  1. 初始化向量库：python scripts/vector_store.py init")
        print("  2. 同步记忆：python scripts/vector_store.py sync")
        print("  3. 测试配置：python scripts/load_context.py --mode all")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ 保存配置失败：{e}")
        return False


def show_config_status():
    """显示配置状态"""
    print("=" * 60)
    print("📊 配置状态检查")
    print("=" * 60)
    print()
    
    # 检查 .env 文件
    env_exists = ENV_FILE.exists()
    print(f"1. .env 文件：{'✅ 存在' if env_exists else '❌ 不存在'}")
    
    if env_exists:
        with open(ENV_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        has_api_key = 'OPENAI_API_KEY' in content
        has_base_url = 'OPENAI_BASE_URL' in content
        has_model = 'OPENAI_EMBEDDING_MODEL' in content
        
        print(f"   - OPENAI_API_KEY: {'✅ 已配置' if has_api_key else '❌ 未配置'}")
        print(f"   - OPENAI_BASE_URL: {'✅ 已配置' if has_base_url else '⚪ 未配置（使用默认）'}")
        print(f"   - OPENAI_EMBEDDING_MODEL: {'✅ 已配置' if has_model else '⚪ 未配置（使用默认）'}")
    
    print()
    
    # 检查标记文件
    marker_exists = check_marker_file()
    print(f"2. 配置标记：{'✅ 已配置' if marker_exists else '❌ 未配置'}")
    print()
    
    # 检查向量库
    vector_db_dir = SKILL_DIR / "vector_db"
    vector_db_exists = vector_db_dir.exists()
    print(f"3. 向量数据库：{'✅ 已初始化' if vector_db_exists else '❌ 未初始化'}")
    print()
    
    # 总体状态
    print("=" * 60)
    if env_exists and marker_exists:
        print("✅ 配置完成，可以开始使用")
    else:
        print("⚠️  配置未完成，需要引导配置")
        print()
        print("运行以下命令开始配置：")
        print("  python scripts/check_config.py --guide")
    print("=" * 60)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='配置检查和引导工具')
    parser.add_argument('--guide', action='store_true', help='引导用户配置')
    parser.add_argument('--reset', action='store_true', help='重置配置（删除标记文件）')
    parser.add_argument('--status', action='store_true', help='显示配置状态')
    
    args = parser.parse_args()
    
    if args.guide:
        success = guide_configuration()
        sys.exit(0 if success else 1)
    
    elif args.reset:
        delete_marker_file()
        print("✅ 配置标记已删除，下次运行时会重新引导配置")
        sys.exit(0)
    
    elif args.status:
        show_config_status()
        sys.exit(0)
    
    else:
        # 默认行为：检查配置
        is_valid, message = check_env_file()
        marker_exists = check_marker_file()
        
        if is_valid and marker_exists:
            print("✅ 配置已完成")
            sys.exit(0)
        else:
            print("⚠️  配置未完成")
            print(f"   {message}")
            print()
            print("运行以下命令开始配置：")
            print("  python scripts/check_config.py --guide")
            sys.exit(1)


if __name__ == '__main__':
    main()
