#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
向量记忆存储脚本 - 使用 ChromaDB + OpenAI Embeddings

功能:
- 仅将短期记忆转换为向量存储（长期记忆默认全量加载）
- 提供语义搜索功能

使用方法:
    python scripts/vector_store.py init                    # 初始化向量库
    python scripts/vector_store.py add --content "内容" --source short-2026-03-11
    python scripts/vector_store.py sync                    # 同步短期记忆到向量库
    python scripts/vector_store.py query --query "关键词" --top-k 5
"""

import argparse
import hashlib
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

import chromadb
from chromadb.config import Settings
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取脚本所在目录
SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
VECTOR_DB_DIR = SKILL_DIR / "vector_db"

# 确保向量数据库目录存在
VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)

# 从环境变量读取配置
api_key = os.getenv("OPENAI_API_KEY", "")
base_url = os.getenv("OPENAI_BASE_URL", "")
model_name = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

# 初始化 OpenAI 客户端
if base_url:
    client = OpenAI(api_key=api_key, base_url=base_url)
else:
    client = OpenAI(api_key=api_key)

# 初始化 ChromaDB 客户端
chroma_client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))


def validate_config():
    """验证必要的环境变量"""
    if not api_key:
        print("❌ OPENAI_API_KEY 未配置")
        print("   请创建 .env 文件并配置 OPENAI_API_KEY")
        print("   参考：SETUP_GUIDE.md")
        sys.exit(1)


def get_embedding(text: str, model: str = None) -> List[float]:
    """获取文本的向量嵌入"""
    if model is None:
        model = model_name
    response = client.embeddings.create(
        input=text,
        model=model
    )
    return response.data[0].embedding


def test_api_connection():
    """测试 API 连接"""
    try:
        test_embedding = get_embedding("test connection")
        return True
    except Exception as e:
        print(f"❌ API 连接测试失败：{e}")
        return False


def generate_id(content: str, source: str) -> str:
    """生成唯一的记忆 ID"""
    text = f"{source}:{content}"
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def get_collection(name: str = "memories"):
    """获取或创建集合"""
    return chroma_client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"}  # 使用余弦相似度
    )


def add_memory(
    content: str,
    source: str,
    metadata: Optional[Dict[str, Any]] = None
):
    """添加短期记忆到向量库"""
    collection = get_collection()
    
    # 生成唯一 ID
    doc_id = generate_id(content, source)
    
    # 准备元数据
    doc_metadata = {
        "source": source,
        "type": "short",  # 只存储短期记忆
        "created_at": datetime.now().isoformat(),
        **(metadata or {})
    }
    
    # 获取向量
    embedding = get_embedding(content)
    
    # 添加到集合
    collection.add(
        ids=[doc_id],
        embeddings=[embedding],
        documents=[content],
        metadatas=[doc_metadata]
    )
    
    print(f"✅ 已添加向量记忆")
    print(f"   来源：{source}")
    print(f"   类型：short")
    print(f"   ID: {doc_id[:8]}...")


def query_memories(
    query: str,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """查询向量记忆（仅短期记忆）"""
    collection = get_collection()
    
    # 获取查询向量
    query_embedding = get_embedding(query)
    
    # 查询（只查询短期记忆，无需过滤）
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )
    
    # 格式化结果
    memories = []
    if results and results['ids'] and results['ids'][0]:
        for i, doc_id in enumerate(results['ids'][0]):
            memories.append({
                'id': doc_id,
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i] if results['distances'] else None
            })
    
    return memories


def sync_short_term_memories():
    """同步短期记忆到向量库"""
    short_term_dir = SKILL_DIR / "short-term"
    
    if not short_term_dir.exists():
        print("❌ 短期记忆目录不存在")
        return
    
    print("🔄 同步短期记忆到向量库...")
    
    # 先清空集合（避免重复）
    try:
        chroma_client.delete_collection("memories")
    except:
        pass
    collection = get_collection()
    
    count = 0
    for file_path in short_term_dir.glob("*.md"):
        if file_path.name == "README.md":
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取 session 内容
        pattern = r'<!--\s*@session.+?-->\s*\n(.*?)<!--\s*@end\s*-->'
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for match in matches:
            entry_content = match.group(1).strip()
            source = f"short-{file_path.stem}"
            
            try:
                add_memory(entry_content, source)
                count += 1
            except Exception as e:
                pass
    
    print(f"✅ 同步完成，共 {count} 条短期记忆")


def delete_memory(doc_id: str):
    """删除记忆"""
    collection = get_collection()
    collection.delete(ids=[doc_id])
    print(f"✅ 已删除记忆：{doc_id[:8]}...")


def list_memories(limit: int = 20):
    """列出向量库中的记忆"""
    collection = get_collection()
    
    # 获取所有记忆（通过空查询）
    results = collection.get(
        limit=limit,
        include=["documents", "metadatas"]
    )
    
    print(f"📊 向量库中的记忆（最近 {limit} 条）\n")
    
    if results and results['ids']:
        for i, doc_id in enumerate(results['ids']):
            metadata = results['metadatas'][i] if results['metadatas'] else {}
            document = results['documents'][i] if results['documents'] else ''
            
            print(f"{i+1}. [{metadata.get('type', '?')}] {metadata.get('source', 'unknown')}")
            print(f"   内容：{document[:100]}...")
            print(f"   创建：{metadata.get('created_at', 'unknown')}")
            print()
    else:
        print("   (无记忆)")


def get_stats():
    """获取向量库统计信息"""
    collection = get_collection()
    count = collection.count()
    
    print("📊 向量库统计")
    print("=" * 40)
    print(f"总记忆数：{count}")
    print(f"数据库位置：{VECTOR_DB_DIR}")
    print("=" * 40)


def main():
    parser = argparse.ArgumentParser(description='向量记忆存储工具', add_help=True)
    subparsers = parser.add_subparsers(dest='command', help='命令类型')
    
    # init 命令
    init_parser = subparsers.add_parser('init', help='初始化向量库')
    
    # add 命令
    add_parser = subparsers.add_parser('add', help='添加记忆到向量库')
    add_parser.add_argument('--content', required=True, help='记忆内容')
    add_parser.add_argument('--source', required=True, help='来源（如文件名）')
    add_parser.add_argument('--type', choices=['long', 'short'], default='long', help='记忆类型')
    
    # sync 命令
    sync_parser = subparsers.add_parser('sync', help='同步短期记忆到向量库')
    
    # query 命令
    query_parser = subparsers.add_parser('query', help='查询记忆')
    query_parser.add_argument('--query', required=True, help='搜索关键词')
    query_parser.add_argument('--top-k', type=int, default=5, help='返回结果数量')
    
    # list 命令
    list_parser = subparsers.add_parser('list', help='列出记忆')
    list_parser.add_argument('--limit', type=int, default=20, help='显示数量')
    
    # delete 命令
    delete_parser = subparsers.add_parser('delete', help='删除记忆')
    delete_parser.add_argument('--id', required=True, help='记忆 ID')
    
    # stats 命令
    stats_parser = subparsers.add_parser('stats', help='显示统计信息')
    
    args = parser.parse_args()
    
    if args.command == 'init':
        # 验证配置
        validate_config()
        
        # 测试 API 连接
        print("🔍 测试 API 连接...")
        if test_api_connection():
            print("✅ API 连接测试成功")
        else:
            print("⚠️  API 连接测试失败，请检查网络和 API 配置")
            print("   继续初始化向量库（仅创建本地数据库）")
        
        # 创建集合
        get_collection()
        print("✅ 向量库初始化完成")
        print()
        print("下一步：同步短期记忆到向量库")
        print("  python scripts/vector_store.py sync")
    elif args.command == 'add':
        add_memory(args.content, args.source)
    elif args.command == 'sync':
        sync_short_term_memories()
    elif args.command == 'query':
        results = query_memories(args.query, args.top_k)
        if results:
            print(f"🔍 查询结果：\"{args.query}\"\n")
            for i, mem in enumerate(results, 1):
                print(f"{i}. [{mem['metadata'].get('type', 'short')}] {mem['metadata'].get('source', 'unknown')}")
                print(f"   内容：{mem['content']}")
                print(f"   相似度：{1 - mem['distance']:.4f}" if mem['distance'] else "N/A")
                print()
        else:
            print(f"❌ 未找到匹配 \"{args.query}\" 的记忆")
    elif args.command == 'list':
        list_memories(args.limit)
    elif args.command == 'delete':
        delete_memory(args.id)
    elif args.command == 'stats':
        get_stats()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
