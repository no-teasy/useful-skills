#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
统一记忆查询脚本 - 搜索长期记忆、短期记忆和向量记忆

使用方法:
    python scripts/search_memories.py --query "关键词"
    python scripts/search_memories.py --query "关键词" --mode vector
    python scripts/search_memories.py --query "关键词" --mode all
    python scripts/search_memories.py --query "关键词" --top-k 10 --type long
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# 获取脚本所在目录
SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent

# 记忆目录
MEMORIES_DIR = SKILL_DIR / "memories"
SHORT_TERM_DIR = SKILL_DIR / "short-term"
VECTOR_DB_DIR = SKILL_DIR / "vector_db"


def search_long_term_memories(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """搜索长期记忆"""
    results = []
    query_lower = query.lower()
    
    if not MEMORIES_DIR.exists():
        return results
    
    for file_path in MEMORIES_DIR.glob("*.md"):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取记忆条目
        pattern = r'## (.+?)\s*\n\s*(<!--\s*@meta.+?-->)\s*\n(.*?)<!--\s*@end\s*-->'
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for match in matches:
            title = match.group(1).strip()
            meta_line = match.group(2)
            entry_content = match.group(3).strip()
            
            # 搜索关键词
            search_text = f"{title} {entry_content}".lower()
            if query_lower in search_text:
                # 解析 meta
                meta_match = re.search(r'@meta\s+(.+?)\s*-->', meta_line)
                meta = {}
                if meta_match:
                    pairs = re.findall(r'(\w+):\s*([^|]+)', meta_match.group(1))
                    for key, value in pairs:
                        meta[key.strip()] = value.strip()
                
                results.append({
                    'type': 'long',
                    'source': file_path.stem,
                    'title': title,
                    'content': entry_content,
                    'metadata': meta,
                    'score': 1.0  # 关键词匹配得分
                })
    
    return results[:top_k]


def search_short_term_memories(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """搜索短期记忆"""
    results = []
    query_lower = query.lower()
    
    if not SHORT_TERM_DIR.exists():
        return results
    
    for file_path in SHORT_TERM_DIR.glob("*.md"):
        if file_path.name == "README.md":
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取 session 内容
        pattern = r'<!--\s*@session.+?-->\s*\n(.*?)<!--\s*@end\s*-->'
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for match in matches:
            entry_content = match.group(1).strip()
            
            if query_lower in entry_content.lower():
                results.append({
                    'type': 'short',
                    'source': f"short-{file_path.stem}",
                    'title': '短期记忆',
                    'content': entry_content,
                    'metadata': {'date': file_path.stem},
                    'score': 1.0
                })
    
    return results[:top_k]


def search_vector_memories(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """搜索向量记忆（仅短期记忆）"""
    try:
        import chromadb
        from openai import OpenAI
        import os
    except ImportError:
        print("⚠️  需要安装依赖：pip install chromadb openai")
        return []
    
    if not VECTOR_DB_DIR.exists():
        print("⚠️  向量库不存在，请先运行：python scripts/vector_store.py sync")
        return []
    
    try:
        # 初始化客户端
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        chroma_client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))
        collection = chroma_client.get_collection(name="memories")
        
        # 获取查询向量
        response = client.embeddings.create(input=query, model="text-embedding-3-small")
        query_embedding = response.data[0].embedding
        
        # 查询（只查询短期记忆，无需过滤）
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        memories = []
        if results and results['ids'] and results['ids'][0]:
            for i, doc_id in enumerate(results['ids'][0]):
                metadata = results['metadatas'][0][i]
                content = results['documents'][0][i]
                distance = results['distances'][0][i] if results['distances'] else 0
                
                memories.append({
                    'type': 'short',  # 向量库只存短期记忆
                    'source': metadata.get('source', 'unknown'),
                    'title': content.split('\n')[0] if '\n' in content else content[:50],
                    'content': content,
                    'metadata': metadata,
                    'score': 1 - distance  # 余弦相似度
                })
        
        return memories
    
    except Exception as e:
        print(f"⚠️  向量搜索失败：{e}")
        return []


def print_results(results: List[Dict[str, Any]], title: str):
    """打印搜索结果"""
    if not results:
        return
    
    print(f"\n{'='*60}")
    print(f"📋 {title}")
    print(f"{'='*60}\n")
    
    for i, mem in enumerate(results, 1):
        type_icon = "📝" if mem['type'] == 'long' else "⏱️" if mem['type'] == 'short' else "🧠"
        print(f"{i}. {type_icon} [{mem['type']}] {mem['source']}")
        print(f"   标题：{mem['title'][:50]}...")
        print(f"   内容：{mem['content'][:150]}...")
        if mem.get('score'):
            print(f"   相关性：{mem['score']:.4f}")
        print()


def search_all(query: str, top_k: int = 5) -> Dict[str, List[Dict[str, Any]]]:
    """搜索所有记忆类型"""
    print(f"🔍 搜索记忆：\"{query}\"")
    print(f"   模式：全部（长期 + 短期 + 向量）")
    
    all_results = {
        'long': search_long_term_memories(query, top_k),
        'short': search_short_term_memories(query, top_k),
        'vector': search_vector_memories(query, top_k)
    }
    
    return all_results


def main():
    parser = argparse.ArgumentParser(description='统一记忆搜索工具', add_help=True)
    parser.add_argument('--query', '-q', required=True, help='搜索关键词')
    parser.add_argument('--mode', choices=['all', 'long', 'short', 'vector'], default='all', help='搜索模式')
    parser.add_argument('--top-k', '-k', type=int, default=5, help='返回结果数量')
    parser.add_argument('--output', choices=['text', 'json'], default='text', help='输出格式')
    
    args = parser.parse_args()
    
    if args.mode == 'all':
        results = search_all(args.query, args.top_k)
        
        # 打印结果
        print_results(results.get('long', []), "长期记忆")
        print_results(results.get('short', []), "短期记忆")
        print_results(results.get('vector', []), "向量记忆")
        
    elif args.mode == 'long':
        results = search_long_term_memories(args.query, args.top_k)
        print_results(results, "长期记忆")
        
    elif args.mode == 'short':
        results = search_short_term_memories(args.query, args.top_k)
        print_results(results, "短期记忆")
        
    elif args.mode == 'vector':
        results = search_vector_memories(args.query, args.top_k, args.type)
        print_results(results, "向量记忆")
    
    # 总结
    if args.mode == 'all':
        total = sum(len(r) for r in results.values())
        print(f"\n{'='*60}")
        print(f"📊 共找到 {total} 条记忆")
        print(f"   长期记忆：{len(results.get('long', []))} 条")
        print(f"   短期记忆：{len(results.get('short', []))} 条")
        print(f"   向量记忆：{len(results.get('vector', []))} 条")
        print(f"{'='*60}")
    elif results:
        print(f"\n{'='*60}")
        print(f"📊 共找到 {len(results)} 条记忆")
        print(f"{'='*60}")
    else:
        print(f"\n❌ 未找到匹配 \"{args.query}\" 的记忆")


if __name__ == '__main__':
    main()
