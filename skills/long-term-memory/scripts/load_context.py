#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
统一记忆加载脚本 - 加载长期记忆、短期记忆、向量记忆到上下文

**重要：AI 第一次调用时必须使用 --mode all**

使用方法:
    python scripts/load_context.py --mode all               # 加载长期记忆 + 当天短期记忆（默认）
    python scripts/load_context.py --mode vector --query "关键词"  # 仅向量搜索（语义检索）
    python scripts/load_context.py --mode all --query "关键词"  # 长期 + 短期 + 向量搜索
    python scripts/load_context.py --mode all --full        # 加载完整内容
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

# 获取脚本所在目录
SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
LIB_DIR = SCRIPT_DIR / "lib"

# 添加 lib 目录到路径
sys.path.insert(0, str(LIB_DIR))

# 导入内部库
from auto_archive import auto_archive

# 记忆目录
MEMORIES_DIR = SKILL_DIR / "memories"
SHORT_TERM_DIR = SKILL_DIR / "short-term"
VECTOR_DB_DIR = SKILL_DIR / "vector_db"

# 长期记忆文件类别
MEMORY_FILES = [
    "user-preferences.md",
    "user-profile.md",
    "decisions-context.md",
    "tasks-reminder.md",
    "knowledge-base.md"
]


def print_separator(char='=', length=60):
    """打印分隔线"""
    print(char * length)


def print_header(mode_name: str):
    """打印头部信息"""
    print_separator()
    print("🧠 记忆加载系统")
    print_separator()
    print(f"📂 加载模式：{mode_name}")
    print(f"⏰ 加载时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_separator()
    print()


# ==================== 长期记忆加载 ====================

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


def extract_memories(content, file_name=''):
    """从文件内容中提取所有记忆条目"""
    memories = []
    pattern = r'## (.+?)\s*\n\s*(<!--\s*@meta.+?-->)\s*\n(.*?)<!--\s*@end\s*-->'
    matches = re.finditer(pattern, content, re.DOTALL)
    
    for match in matches:
        title = match.group(1).strip()
        meta_line = match.group(2)
        entry_content = match.group(3).strip()
        meta = parse_meta(meta_line)
        
        memories.append({
            'title': title,
            'meta': meta,
            'content': entry_content,
            'file': file_name
        })
    
    return memories


def load_long_term_memories(full: bool = False):
    """加载长期记忆"""
    print("📚 加载长期记忆...\n")
    
    all_memories = {}
    
    for file_name in MEMORY_FILES:
        file_path = MEMORIES_DIR / file_name
        if not file_path.exists():
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        memories = extract_memories(content, file_name)
        if memories:
            all_memories[file_name] = memories
    
    if not all_memories:
        print("⚠️  未找到长期记忆文件")
        return
    
    # 打印摘要
    total = sum(len(memories) for memories in all_memories.values())
    print(f"📊 共 {total} 条长期记忆\n")
    
    for file_name, memories in all_memories.items():
        print(f"📄 {file_name} ({len(memories)} 条)")
        for memory in memories:
            tags = memory['meta'].get('tags', '无')
            print(f"   • {memory['title']}")
            print(f"     标签：{tags}")
        print()
    
    # 打印完整内容（如果请求）
    if full:
        print_separator('-', 40)
        print("📖 完整记忆内容")
        print_separator('-', 40)
        
        for file_name, memories in all_memories.items():
            for memory in memories:
                print(f"\n## {memory['title']}")
                print(f"标签：{memory['meta'].get('tags', '无')}")
                print()
                print(memory['content'])
                print()
                print_separator('-', 40)


# ==================== 短期记忆加载 ====================

def load_short_term_memories(date: str = None):
    """加载短期记忆"""
    print("⏱️  加载短期记忆...\n")
    
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    file_path = SHORT_TERM_DIR / f"{date}.md"
    
    if not file_path.exists():
        print(f"⚠️  今日 ({date}) 暂无短期记忆")
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取 session 内容
    pattern = r'<!--\s*@session.+?-->\s*\n(.*?)<!--\s*@end\s*-->'
    matches = re.finditer(pattern, content, re.DOTALL)
    
    count = 0
    for match in matches:
        entry_content = match.group(1).strip()
        print(f"📝 {entry_content[:150]}...")
        count += 1
    
    if count == 0:
        print("⚠️  今日暂无短期记忆")
    else:
        print(f"\n📊 共 {count} 条短期记忆")


# ==================== 向量记忆加载 ====================

def load_vector_memories(query: str = None, top_k: int = 5):
    """加载向量记忆（语义搜索）"""
    print("🧠 加载向量记忆...\n")

    try:
        import chromadb
        from openai import OpenAI
        import os
    except ImportError:
        print("⚠️  需要安装依赖：pip install chromadb openai")
        return

    if not VECTOR_DB_DIR.exists():
        print("⚠️  向量库不存在，请先运行：python scripts/vector_store.py sync")
        return

    # 验证环境变量
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        print("⚠️  OPENAI_API_KEY 未配置")
        print("   请创建 .env 文件并配置 OPENAI_API_KEY")
        print("   参考：SETUP_GUIDE.md")
        return

    try:
        base_url = os.getenv("OPENAI_BASE_URL", "")
        model_name = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        
        # 初始化客户端
        if base_url:
            client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            client = OpenAI(api_key=api_key)
        
        chroma_client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))
        collection = chroma_client.get_collection(name="memories")

        if query:
            # 语义搜索
            response = client.embeddings.create(input=query, model=model_name)
            query_embedding = response.data[0].embedding

            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )

            print(f"🔍 语义搜索：\"{query}\"\n")

            if results and results['ids'] and results['ids'][0]:
                for i, doc_id in enumerate(results['ids'][0]):
                    content = results['documents'][0][i]
                    metadata = results['metadatas'][0][i]
                    distance = results['distances'][0][i] if results['distances'] else 0

                    print(f"{i+1}. [{metadata.get('source', 'unknown')}]")
                    print(f"   内容：{content[:150]}...")
                    print(f"   相似度：{1 - distance:.4f}")
                    print()
            else:
                # 检查库是否为空
                count = collection.count()
                if count == 0:
                    print("⚠️  向量库为空，请先运行：python scripts/vector_store.py sync")
                else:
                    print(f"⚠️  未找到与 \"{query}\" 相关的记忆")
                    print(f"   向量库中共有 {count} 条记忆")
                    print("   建议：尝试其他关键词")
        else:
            # 列出所有
            results = collection.get(limit=top_k, include=["documents", "metadatas"])

            print(f"📋 向量记忆（最近 {top_k} 条）\n")

            if results and results['ids']:
                for i, doc_id in enumerate(results['ids']):
                    content = results['documents'][i]
                    metadata = results['metadatas'][i]

                    print(f"{i+1}. [{metadata.get('source', 'unknown')}]")
                    print(f"   内容：{content[:150]}...")
                    print()
            else:
                print("⚠️  向量库为空")

    except Exception as e:
        print(f"⚠️  向量搜索失败：{e}")
        print("   请检查：")
        print("   1. .env 文件是否存在")
        print("   2. OPENAI_API_KEY 是否正确")
        print("   3. 网络连接是否正常")


# ==================== 主函数 ====================

def main():
    parser = argparse.ArgumentParser(description='统一记忆加载工具', add_help=True)
    
    parser.add_argument(
        '--mode',
        choices=['all', 'vector'],
        required=True,
        help='加载模式：all=长期记忆 + 当天短期记忆，vector=仅向量搜索'
    )
    parser.add_argument('--full', action='store_true', help='加载完整内容')
    parser.add_argument('--query', type=str, help='搜索关键词（向量搜索）')
    parser.add_argument('--top-k', type=int, default=5, help='返回结果数量（仅向量搜索）')
    
    args = parser.parse_args()
    
    # vector 模式必须有 query
    if args.mode == 'vector' and not args.query:
        print("❌ --mode vector 必须指定 --query 参数")
        sys.exit(1)
    
    # 只有 --mode all 时才自动归档
    if args.mode == 'all':
        auto_archive(dry_run=False)
        print()
    
    # 打印头部
    mode_names = {
        'all': '全部记忆',
        'vector': '向量搜索'
    }
    print_header(mode_names[args.mode])
    
    if args.mode == 'all':
        # 加载长期记忆 + 当天短期记忆
        load_long_term_memories(full=args.full)
        print()
        load_short_term_memories()  # 加载今天
        
        # 如果有 query 参数，额外加载向量搜索结果
        if args.query:
            print()
            load_vector_memories(args.query, args.top_k)
    
    elif args.mode == 'vector':
        # 仅向量搜索（不加载长期/短期记忆）
        load_vector_memories(args.query, args.top_k)
    
    print()
    print_separator('=')
    print("✅ 记忆加载完成")
    print_separator('=')


if __name__ == '__main__':
    main()
