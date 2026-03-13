# 记忆系统配置向导

> 本指南帮助 AI 助手帮助用户完成长期记忆系统的完整配置

---

## AI 配置流程

当用户首次使用记忆系统时，AI 应按照以下流程帮助用户配置：

```
┌─────────────────┐
│  1. 检查环境    │ → Python 版本、pip 是否安装
└────────┬────────┘
         ↓
┌─────────────────┐
│  2. 安装依赖    │ │ pip install -r requirements.txt
└────────┬────────┘
         ↓
┌─────────────────┐
│  3. 配置 .env   │ → API Key、Base URL、模型名
└────────┬────────┘
         ↓
┌─────────────────┐
│  4. 初始化向量库│ → python scripts/vector_store.py init
└────────┬────────┘
         ↓
┌─────────────────┐
│  5. 测试配置    │ → 运行测试命令验证配置
└─────────────────┘
```

---

## 步骤 1：检查环境

### AI 应该执行的检查

```bash
# 检查 Python 版本（需要 3.8+）
python --version

# 检查 pip 是否安装
pip --version

# 检查是否在正确的目录
pwd  # 应该在 skills/long-term-memory 目录下
```

### 预期输出

```
Python 3.8.0 或更高版本
pip 20.0 或更高版本
路径包含 skills/long-term-memory
```

### 如果检查失败

**Python 版本过低**：
```
⚠️  检测到 Python 版本低于 3.8
请安装 Python 3.8 或更高版本
下载地址：https://www.python.org/downloads/
```

**pip 未安装**：
```
⚠️  未检测到 pip
请安装 pip：
Windows: python -m ensurepip --upgrade
Mac/Linux: python -m ensurepip --upgrade
```

**目录不正确**：
```
⚠️  当前目录不是记忆系统目录
请切换到 skills/long-term-memory 目录
cd skills/long-term-memory
```

---

## 步骤 2：安装依赖

### AI 应该执行的命令

```bash
# 进入技能目录
cd skills/long-term-memory

# 安装依赖
pip install -r requirements.txt
```

### requirements.txt 内容

```
chromadb>=0.4.0
openai>=1.0.0
python-dotenv>=1.0.0
```

### 预期输出

```
Successfully installed chromadb-0.x.x openai-1.x.x python-dotenv-1.x.x
```

### 如果安装失败

**网络问题（国内用户）**：
```bash
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**权限问题**：
```bash
# 使用 --user 参数
pip install -r requirements.txt --user
```

---

## 步骤 3：配置 .env 文件

### AI 应该帮助用户创建 .env 文件

**文件位置**：`skills/long-term-memory/.env`

### 基础配置（推荐）

```bash
# OpenAI API 配置
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 完整配置（可选）

```bash
# OpenAI API 配置
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 自定义 API 基础 URL（可选）
# 如果使用 OpenAI 官方，可以注释掉或删除此行
OPENAI_BASE_URL=https://api.openai.com/v1

# 自定义嵌入模型（可选）
# 默认使用 text-embedding-3-small
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

### AI 应该询问用户的问题

1. **使用哪个 API 服务？**
   - OpenAI 官方
   - Azure OpenAI
   - 本地部署模型（如 Ollama、vLLM）
   - 其他兼容服务

2. **API Key 是什么？**
   - 引导用户获取 API Key
   - 提醒用户不要分享 API Key

3. **是否需要自定义模型？**
   - 默认：`text-embedding-3-small`
   - 替代：`text-embedding-3-large`、`bge-large-zh-v1.5` 等

### 不同服务的配置示例

**OpenAI 官方**：
```bash
OPENAI_API_KEY=sk-xxxxxxxx
# OPENAI_BASE_URL=https://api.openai.com/v1  # 默认，可不写
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

**Azure OpenAI**：
```bash
OPENAI_API_KEY=xxxxxxxxxxxxxxxx
OPENAI_BASE_URL=https://your-resource.openai.azure.com/openai/deployments/your-deployment
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002
```

**本地 Ollama**：
```bash
OPENAI_API_KEY=ollama  # Ollama 不需要 API Key
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_EMBEDDING_MODEL=nomic-embed-text
```

**其他兼容服务**：
```bash
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://your-custom-endpoint.com/v1
OPENAI_EMBEDDING_MODEL=your-embedding-model
```

---

## 步骤 4：初始化向量库

### AI 应该执行的命令

```bash
# 初始化 ChromaDB 向量库
python scripts/vector_store.py init

# 同步现有短期记忆到向量库（如果有）
python scripts/vector_store.py sync
```

### 预期输出

```
✅ 向量库初始化完成

🔄 同步短期记忆到向量库...
✅ 同步完成，共 x 条短期记忆
```

### 如果初始化失败

**ChromaDB 错误**：
```
⚠️  ChromaDB 初始化失败
尝试删除向量库目录后重试：
rm -rf vector_db
python scripts/vector_store.py init
```

**API 错误**：
```
⚠️  OpenAI API 调用失败
请检查：
1. .env 文件是否存在
2. OPENAI_API_KEY 是否正确
3. 网络连接是否正常
```

---

## 步骤 5：测试配置

### AI 应该执行的测试命令

```bash
# 测试记忆加载
python scripts/load_context.py --mode all

# 测试向量搜索（如果有短期记忆）
python scripts/load_context.py --mode vector --query "测试"
```

### 预期输出

```
============================================================
🧠 记忆加载系统
============================================================
📂 加载模式：全部记忆
...
📊 共 x 条长期记忆
...
✅ 记忆加载完成
```

### 测试检查清单

- [ ] 长期记忆加载成功
- [ ] 短期记忆加载成功（如果有）
- [ ] 向量搜索正常工作（如果配置了 API）
- [ ] 没有错误信息

---

## 快速配置脚本

AI 可以建议用户运行快速配置脚本：

```bash
# 创建配置脚本
cat > setup_config.py << 'EOF'
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速配置脚本
"""
import os
import sys

def check_python_version():
    """检查 Python 版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 版本过低：{version.major}.{version.minor}")
        print("   需要 Python 3.8 或更高版本")
        return False
    print(f"✅ Python 版本：{version.major}.{version.minor}.{version.micro}")
    return True

def check_pip():
    """检查 pip"""
    try:
        import pip
        print(f"✅ pip 版本：{pip.__version__}")
        return True
    except ImportError:
        print("❌ 未安装 pip")
        return False

def check_directory():
    """检查目录"""
    cwd = os.getcwd()
    if 'long-term-memory' in cwd:
        print(f"✅ 目录正确：{cwd}")
        return True
    else:
        print(f"⚠️  目录可能不正确：{cwd}")
        print("   应该在 skills/long-term-memory 目录下")
        return False

def check_env():
    """检查 .env 文件"""
    env_file = '.env'
    if os.path.exists(env_file):
        print(f"✅ .env 文件存在")
        with open(env_file, 'r') as f:
            content = f.read()
            if 'OPENAI_API_KEY' in content:
                print("   ✅ OPENAI_API_KEY 已配置")
            else:
                print("   ⚠️  OPENAI_API_KEY 未配置")
        return True
    else:
        print(f"❌ .env 文件不存在")
        print("   请创建 .env 文件并配置 OPENAI_API_KEY")
        return False

def check_dependencies():
    """检查依赖"""
    required = ['chromadb', 'openai', 'dotenv']
    missing = []
    for dep in required:
        try:
            __import__(dep.replace('-', '_'))
            print(f"✅ {dep} 已安装")
        except ImportError:
            print(f"❌ {dep} 未安装")
            missing.append(dep)
    
    if missing:
        print(f"\n请运行：pip install -r requirements.txt")
        return False
    return True

def main():
    print("=" * 50)
    print("🔧 记忆系统配置检查")
    print("=" * 50)
    print()
    
    checks = [
        ("Python 版本", check_python_version),
        ("pip", check_pip),
        ("目录", check_directory),
        (".env 文件", check_env),
        ("依赖", check_dependencies),
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        if check_func():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"检查结果：{passed}/{total} 通过")
    
    if passed == total:
        print("✅ 配置完成，可以开始使用！")
    else:
        print("⚠️  还有未完成的配置项，请根据提示完成")
    print("=" * 50)

if __name__ == '__main__':
    main()
EOF

# 运行配置检查
python setup_config.py
```

---

## 常见问题解答

### Q1: 没有 OpenAI API Key 怎么办？

**A**: 可以使用以下替代方案：
1. 申请 OpenAI API Key：https://platform.openai.com/api-keys
2. 使用本地部署的嵌入模型（如 Ollama）
3. 使用其他兼容 OpenAI API 格式的服务

### Q2: 向量库必须配置吗？

**A**: 不是必须的。向量库仅用于语义搜索：
- 如果只需要关键词搜索，可以不配置向量库
- 如果需要语义理解（如搜"健康"能找到"体检"），建议配置

### Q3: 短期记忆必须向量化吗？

**A**: 是的，向量库只存储短期记忆的向量：
- 长期记忆默认全量加载，不需要向量化
- 短期记忆通过向量搜索实现语义检索

### Q4: 配置完成后如何验证？

**A**: 运行测试命令：
```bash
python scripts/load_context.py --mode all
```
如果正常输出记忆内容，说明配置成功。

---

## AI 配置助手提示词

当用户需要配置时，AI 应该：

1. **主动询问**：
   - "您是否已经安装了 Python 3.8+？"
   - "您有 OpenAI API Key 吗？"
   - "您想使用哪个 API 服务？"

2. **逐步引导**：
   - 一次只让用户执行一个步骤
   - 等待用户确认后再继续下一步

3. **错误处理**：
   - 如果某步失败，提供具体的解决方案
   - 不要一次性给出所有可能的解决方案

4. **验证配置**：
   - 配置完成后，运行测试命令验证
   - 确认所有功能正常工作

---

## 配置完成标志

当以下所有条件满足时，配置完成：

- [x] Python 3.8+ 已安装
- [x] 依赖已安装（chromadb, openai, python-dotenv）
- [x] .env 文件已创建并配置
- [x] 向量库已初始化
- [x] 测试命令正常运行

此时 AI 可以告诉用户：
```
✅ 配置完成！

您现在可以开始使用记忆系统了：
- 加载记忆：python scripts/load_context.py --mode all
- 向量搜索：python scripts/load_context.py --mode vector --query "关键词"
- 添加短期记忆：python scripts/manage_short_term.py add --content "内容"
```
