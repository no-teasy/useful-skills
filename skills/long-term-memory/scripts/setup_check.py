#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速配置检查脚本

使用方法:
    python scripts/setup_check.py
"""

import os
import sys
from pathlib import Path

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def check_python_version():
    """检查 Python 版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error(f"Python 版本过低：{version.major}.{version.minor}.{version.micro}")
        print_info("需要 Python 3.8 或更高版本")
        print_info("下载地址：https://www.python.org/downloads/")
        return False
    print_success(f"Python 版本：{version.major}.{version.minor}.{version.micro}")
    return True

def check_pip():
    """检查 pip"""
    try:
        import pip
        print_success(f"pip 版本：{pip.__version__}")
        return True
    except ImportError:
        print_error("未安装 pip")
        print_info("安装方法：python -m ensurepip --upgrade")
        return False

def check_directory():
    """检查目录"""
    cwd = Path.cwd()
    if 'long-term-memory' in str(cwd):
        print_success(f"目录正确")
        print_info(f"当前路径：{cwd}")
        return True
    else:
        print_warning(f"目录可能不正确")
        print_info(f"当前路径：{cwd}")
        print_info("应该在 skills/long-term-memory 目录下")
        return False

def check_env():
    """检查 .env 文件"""
    env_file = Path('.env')
    if env_file.exists():
        print_success(f".env 文件存在")
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'OPENAI_API_KEY' in content:
                # 隐藏敏感信息
                api_key_line = [line for line in content.split('\n') if 'OPENAI_API_KEY' in line]
                if api_key_line:
                    key = api_key_line[0].split('=')[1].strip()
                    masked_key = key[:5] + '***' + key[-3:] if len(key) > 8 else '***'
                    print_success(f"OPENAI_API_KEY 已配置：{masked_key}")
                else:
                    print_success("OPENAI_API_KEY 已配置")
            else:
                print_warning("OPENAI_API_KEY 未配置")
            
            if 'OPENAI_BASE_URL' in content:
                print_success("OPENAI_BASE_URL 已配置（自定义 API 地址）")
            
            if 'OPENAI_EMBEDDING_MODEL' in content:
                model = [line for line in content.split('\n') if 'OPENAI_EMBEDDING_MODEL' in line][0].split('=')[1].strip()
                print_success(f"嵌入模型：{model}")
        return True
    else:
        print_error(".env 文件不存在")
        print_info("请创建 .env 文件并配置 OPENAI_API_KEY")
        print_info("参考：SETUP_GUIDE.md")
        return False

def check_dependencies():
    """检查依赖"""
    required = [
        ('chromadb', 'ChromaDB'),
        ('openai', 'OpenAI'),
        ('dotenv', 'python-dotenv'),
    ]
    
    missing = []
    for module, name in required:
        try:
            __import__(module)
            print_success(f"{name} 已安装")
        except ImportError:
            print_error(f"{name} 未安装")
            missing.append(name)
    
    if missing:
        print_info(f"\n请运行：pip install -r requirements.txt")
        return False
    return True

def check_vector_db():
    """检查向量库"""
    vector_db_dir = Path('vector_db')
    if vector_db_dir.exists():
        print_success("向量库目录存在")
        return True
    else:
        print_warning("向量库目录不存在")
        print_info("运行以下命令初始化：python scripts/vector_store.py init")
        return False

def check_memory_files():
    """检查记忆文件"""
    memories_dir = Path('memories')
    if memories_dir.exists():
        print_success("长期记忆目录存在")
        files = list(memories_dir.glob('*.md'))
        print_info(f"  找到 {len(files)} 个记忆文件")
    else:
        print_warning("长期记忆目录不存在")
        print_info("首次使用时会自动创建")
    
    short_term_dir = Path('short-term')
    if short_term_dir.exists():
        print_success("短期记忆目录存在")
    else:
        print_info("短期记忆目录将在首次使用时创建")
    
    return True

def main():
    print_header("🔧 记忆系统配置检查")
    
    checks = [
        ("Python 版本", check_python_version),
        ("pip", check_pip),
        ("目录", check_directory),
        (".env 文件", check_env),
        ("依赖", check_dependencies),
        ("向量库", check_vector_db),
        ("记忆文件", check_memory_files),
    ]
    
    passed = 0
    total = len(checks)
    failed_checks = []
    
    for name, check_func in checks:
        if check_func():
            passed += 1
        else:
            failed_checks.append(name)
        print()
    
    print_header("检查结果")
    print(f"通过：{passed}/{total}")
    
    if passed == total:
        print_success("配置完成，可以开始使用！")
        print("\n使用示例:")
        print("  python scripts/load_context.py --mode all")
        print("  python scripts/manage_short_term.py add --content \"内容\"")
        print("  python scripts/load_context.py --mode vector --query \"关键词\"")
    else:
        print_warning("还有未完成的配置项：")
        for check in failed_checks:
            print(f"  - {check}")
        print("\n请参考 SETUP_GUIDE.md 完成配置")
    
    print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n已取消")
        sys.exit(0)
    except Exception as e:
        print_error(f"发生错误：{e}")
        print_info("请检查是否有足够的权限")
        sys.exit(1)
