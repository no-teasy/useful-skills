# AI 配置引导提示词

> 当用户首次使用记忆系统时，AI 应使用此提示词引导用户完成配置。

---

## 触发条件

当检测到以下情况时，AI 应主动引导用户配置：

1. **配置标记文件不存在** - `configured.txt` 不存在
2. **用户首次运行命令** - 运行 `load_context.py` 或其他命令失败
3. **用户明确询问配置** - "如何配置"、"第一次使用"等

---

## AI 引导流程

### 步骤 1：检测配置状态

AI 应先运行配置检查：

```bash
python scripts/check_config.py
```

**预期输出**：
- 如果返回 `✅ 配置已完成` - 直接继续
- 如果返回 `⚠️ 配置未完成` - 开始引导

### 步骤 2：向用户说明

**AI 话术示例**：

```
👋 欢迎使用记忆管理系统！

检测到您是第一次使用，需要完成简单配置才能开始。
配置过程只需要 1 分钟，我会引导您完成。

配置需要填写：
1. OpenAI API Key（必填）- 用于向量搜索
2. API Base URL（可选）- 如使用 Azure OpenAI 或其他服务
3. 嵌入模型名称（可选）- 默认 text-embedding-3-small

是否现在开始配置？（是/否）
```

### 步骤 3：运行配置向导

用户确认后，运行：

```bash
python scripts/check_config.py --guide
```

**脚本会提示用户输入**：
1. OPENAI_API_KEY
2. OPENAI_BASE_URL（可选）
3. OPENAI_EMBEDDING_MODEL（可选）

### 步骤 4：确认配置完成

配置完成后，脚本会显示：

```
🎉 配置完成！

下一步：
  1. 初始化向量库：python scripts/vector_store.py init
  2. 同步记忆：python scripts/vector_store.py sync
  3. 测试配置：python scripts/load_context.py --mode all
```

### 步骤 5：引导初始化向量库

**AI 话术示例**：

```
✅ 配置已完成！现在需要初始化向量数据库。

向量数据库用于语义搜索，可以让您通过关键词找到相关记忆。

是否现在初始化？（是/否）
```

用户确认后运行：

```bash
python scripts/vector_store.py init
python scripts/vector_store.py sync
```

### 步骤 6：测试配置

**AI 话术示例**：

```
🎉 所有配置完成！让我们测试一下是否正常工作。

运行测试命令会加载您的所有记忆到上下文中。
```

```bash
python scripts/load_context.py --mode all
```

---

## 常见问题解答

### Q1: 我没有 OpenAI API Key 怎么办？

**A**: 可以引导用户使用替代方案：

```
如果您没有 OpenAI API Key，可以选择：

1. 申请 OpenAI API Key
   访问：https://platform.openai.com/api-keys

2. 使用兼容服务
   - Azure OpenAI
   - 本地部署模型（如 Ollama）
   - 其他 OpenAI API 兼容服务

配置时填写相应的 Base URL 即可。
```

### Q2: 我可以稍后再配置吗？

**A**: 可以，但功能会受限：

```
可以稍后配置，但未配置前无法使用以下功能：
- 向量语义搜索
- 智能记忆检索

基础功能（如记忆存储、加载）仍可正常使用。

需要配置时运行：
python scripts/check_config.py --guide
```

### Q3: 配置错了可以修改吗？

**A**: 可以重置配置：

```
可以随时修改配置：

方法 1：编辑 .env 文件
  直接修改 skills/long-term-memory/.env

方法 2：重置后重新配置
  python scripts/check_config.py --reset
  python scripts/check_config.py --guide
```

---

## 配置检查清单

AI 应确保用户完成以下配置：

- [ ] `.env` 文件已创建
- [ ] `OPENAI_API_KEY` 已配置
- [ ] `configured.txt` 标记文件已创建
- [ ] 依赖已安装（chromadb, openai, python-dotenv）
- [ ] 向量库已初始化
- [ ] 测试命令运行成功

---

## 错误处理

### 配置失败

如果配置过程中出现错误：

```
⚠️  配置过程中遇到问题。

请检查：
1. .env 文件是否有写入权限
2. API Key 格式是否正确（应以 sk- 开头）
3. 网络连接是否正常

需要帮助吗？我可以帮您排查问题。
```

### 向量库初始化失败

```
⚠️  向量库初始化失败。

可能原因：
1. OPENAI_API_KEY 未配置或无效
2. 网络连接问题
3. API 额度不足

请检查 .env 文件中的配置，或运行：
python scripts/check_config.py --status
```

---

## 配置完成后的提示

配置完成后，AI 应告知用户：

```
🎉 配置完成！您现在可以开始使用记忆系统了。

常用命令：
- 加载记忆：python scripts/load_context.py --mode all
- 添加记忆：python scripts/manage_memories.py add --file <文件> --title "<标题>" --content "<内容>"
- 搜索记忆：python scripts/manage_memories.py search --query "<关键词>"
- 向量搜索：python scripts/load_context.py --mode vector --query "<关键词>"

记忆文件位置：
- 长期记忆：skills/long-term-memory/memories/
- 短期记忆：skills/long-term-memory/short-term/

有任何问题随时问我！
```
