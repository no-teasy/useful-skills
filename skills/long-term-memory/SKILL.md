---
name: long-term-memory
description: 长期记忆管理系统，将 AI 助手的记忆、用户偏好、重要对话、业务知识等信息写入不同的 markdown 文件，并在每次对话开始时自动读取。适用于日常办公、客服咨询、生活助手等多种场景，实现跨会话的个性化服务。
---

# 长期记忆管理系统

> **技能定位**：让 AI 助手拥有跨会话的持久化记忆能力，记住用户信息、偏好、历史交互和重要事项，提供个性化、连续性的智能服务。

> **核心要求**：**AI 第一次调用时必须使用 `--mode all` 加载所有记忆！**

---

## ⚠️ 强制性指令（最高优先级）

### 指令 1：第一次对话必须加载全部记忆

**AI 第一次调用记忆系统时，必须首先使用 --mode all 加载所有记忆！**

```bash
python scripts/load_context.py --mode all
```

**这是强制性的，没有例外！**

**原因**：
- 长期记忆包含用户偏好、个人信息、重要决定
- 当天短期记忆包含临时对话上下文
- 两者结合才能完整了解用户背景

**加载内容**：
- 长期记忆（5 个文件，全量加载）
- 当天短期记忆（自动加载未归档的）
- 过期短期记忆（>24 小时）自动归档，不加载

**向量搜索**：
- 使用 `--mode vector --query "关键词"` 进行语义搜索
- 或在 `--mode all` 基础上添加 `--query "关键词"`
- **永远不会加载所有向量记忆**，必须指定查询关键词

### 指令 2：积极识别可记录信息

**在对话过程中，时刻保持警惕，识别任何值得记录的信息：**

| 信息类型 | 用户表达示例 | 应记录到 |
|----------|--------------|----------|
| **个人信息** | "我是产品经理"、"我在北京"、"我家孩子 5 岁" | user-profile.md |
| **偏好声明** | "我喜欢简洁的回复"、"用表格展示" | user-preferences.md |
| **重要决定** | "我决定选 A"、"下周开始执行" | decisions-context.md |
| **待办事项** | "记得提醒我"、"下周三前要完成" | tasks-reminder.md |
| **知识经验** | "这个流程是..."、"需要注意的是..." | knowledge-base.md |

**识别后，立即向用户确认并记录，不要等到对话结束！**

### 指令 3：主动管理记忆

**不仅仅是记录，还要主动管理：**

- **更新**：发现信息变化时，主动更新旧记忆
- **删除**：发现过期信息时，主动建议删除
- **关联**：发现记忆间关系时，主动建立链接
- **搜索**：用户提及相关话题时，主动搜索已有记忆

---

## 快速开始

### 1. 检查配置状态（首次使用）

首次使用时，运行配置检查：

```bash
cd skills/long-term-memory
python scripts/check_config.py --status
```

### 2. 配置环境变量（首次使用）

**AI 引导配置**：

第一次使用时，AI 会自动引导你完成配置。或者手动运行：

```bash
python scripts/check_config.py --guide
```

配置过程中需要填写：
- **OPENAI_API_KEY**（必填）- OpenAI API 密钥
- **OPENAI_BASE_URL**（可选）- 自定义 API 地址
- **OPENAI_EMBEDDING_MODEL**（可选）- 嵌入模型名称

配置完成后会自动创建 `configured.txt` 标记文件。

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 初始化向量库

```bash
python scripts/vector_store.py init
python scripts/vector_store.py sync
```

### 5. 测试配置

```bash
python scripts/load_context.py --mode all
```

**🆕 新用户？** 参考 [SETUP_GUIDE.md](SETUP_GUIDE.md) 获取完整配置帮助。

---

## 配置说明

### 环境变量配置

创建 `.env` 文件（在技能目录下），配置以下环境变量：

```bash
# OpenAI API 配置
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1          # 可选，自定义 API 地址
OPENAI_EMBEDDING_MODEL=text-embedding-3-small      # 可选，自定义嵌入模型

# 或者使用兼容 OpenAI API 的其他服务
# 例如使用 Azure OpenAI、本地部署的模型等
OPENAI_BASE_URL=https://your-custom-endpoint.com/v1
```

**配置说明**：
- `OPENAI_API_KEY` - **必填**，OpenAI API 密钥
- `OPENAI_BASE_URL` - 可选，自定义 API 基础 URL（默认使用 OpenAI 官方）
- `OPENAI_EMBEDDING_MODEL` - 可选，嵌入模型名称（默认 `text-embedding-3-small`）

### 配置管理命令

```bash
# 检查配置状态
python scripts/check_config.py --status

# 引导配置（交互式）
python scripts/check_config.py --guide

# 重置配置（删除标记文件）
python scripts/check_config.py --reset

# 仅检查配置（用于脚本）
python scripts/check_config.py
```

### 配置完成标记

配置完成后会自动创建 `configured.txt` 文件，用于标识配置已完成。

- **存在** `configured.txt` - 配置已完成，不会再次引导
- **不存在** `configured.txt` - 配置未完成，AI 会引导配置

如需重新配置，运行：
```bash
python scripts/check_config.py --reset
python scripts/check_config.py --guide
```

---

## 记忆文件结构

```
memories/
├── user-preferences.md      # 用户偏好和习惯
├── user-profile.md          # 用户个人信息和背景
├── decisions-context.md     # 重要决定和上下文
├── tasks-reminder.md        # 待办事项和提醒
└── knowledge-base.md        # 知识和经验积累
```

### 记忆条目格式

```markdown
## [记忆标题]

<!-- @meta category: 类别 | tags: 标签 1, 标签 2 | created: YYYY-MM-DD | updated: YYYY-MM-DD -->

记忆内容...

### 相关记忆（可选）
- 参见 [[其他记忆标题]](其他文件.md#其他记忆标题)

<!-- @end -->
```

---

## 行为指令（强制执行）

### 步骤 1：第一次对话 - 必须加载全部记忆

**这是强制性的第一步，没有例外！**

```
┌─────────────────────────────────────────────────┐
│  1. 检测用户第一条消息                           │
│  2. 运行 python scripts/load_context.py --mode all   │
│  3. 自动归档过期短期记忆（>24 小时）               │
│  4. 加载长期记忆 + 当天短期记忆                   │
│  5. 在内心总结记忆要点                           │
│  6. 根据记忆调整交互方式                         │
│  7. 开始回复用户                                 │
└─────────────────────────────────────────────────┘
```

**执行示例：**
```bash
# 第一步：加载全部记忆（必须！）
python scripts/load_context.py --mode all
```

**内心独白示例（读取后）：**
> "加载完成，共 13 条长期记忆，2 条当天短期记忆。
> 用户是产品经理，在北京工作，喜欢简洁回复。
> 五一计划去日本旅行，酒店已订。
> 今天用户说要去体检。
> 好的，我了解了，现在可以开始回复用户了。"

**不加载记忆就回复是严重错误！**

### 步骤 2：后续对话 - 根据需要加载

**根据对话内容，选择合适的加载模式：**

```bash
# 默认模式（长期 + 当天短期）
python scripts/load_context.py --mode all

# 仅向量搜索（语义检索）
python scripts/load_context.py --mode vector --query "旅行"

# 长期 + 短期 + 向量搜索
python scripts/load_context.py --mode all --query "旅行"

# 加载完整内容
python scripts/load_context.py --mode all --full
```

### 步骤 3：对话中 - 时刻保持警惕

**在对话的每一句话中，都要思考：这个信息值得记录吗？**

**识别→确认→记录 流程：**

```
用户输入
    ↓
是否包含可记录信息？
    ├─ 是 → 属于哪一类？ → 向用户确认 → 立即记录
    └─ 否 → 继续正常对话
```

**实时识别示例：**

```
用户：我是做产品经理的，平时工作比较忙
      ↑
      └─ "我是做产品经理的" → 个人信息 → 记录到 user-profile.md

AI：我记一下，您是产品经理，工作比较忙对吗？
     （运行 manage_memories.py add --file user-profile.md ...）
     好的，已记录。那您平时喜欢怎么放松呢？
```

**不要等到对话结束才记录！当下识别，当下记录！**

---

## 常用命令

### 记忆加载

```bash
# 加载长期记忆 + 当天短期记忆
python scripts/load_context.py --mode all

# 仅向量搜索（语义检索）
python scripts/load_context.py --mode vector --query "关键词"

# 长期 + 短期 + 向量搜索
python scripts/load_context.py --mode all --query "关键词"

# 加载完整内容
python scripts/load_context.py --mode all --full
```

### 记忆管理

```bash
# 添加长期记忆
python scripts/manage_memories.py add --file user-preferences.md --title "标题" --content "内容" --tags "标签"

# 搜索记忆
python scripts/manage_memories.py search --query "关键词"

# 列出所有记忆
python scripts/manage_memories.py list

# 更新记忆
python scripts/manage_memories.py update --file user-preferences.md --title "标题" --content "新内容"

# 删除记忆
python scripts/manage_memories.py delete --file user-preferences.md --title "标题"
```

### 短期记忆

```bash
# 添加短期记忆
python scripts/manage_short_term.py add --content "内容" --agent chat

# 查看今天记忆
python scripts/manage_short_term.py show

# 添加待跟进
python scripts/manage_short_term.py followup --item "事项"

# Agent 间消息
python scripts/manage_short_term.py message --from chat --to health --content "消息"
```

### 向量记忆

```bash
# 初始化向量库
python scripts/vector_store.py init

# 同步短期记忆
python scripts/vector_store.py sync

# 添加记忆
python scripts/vector_store.py add --content "内容" --source "来源"

# 查询记忆（语义搜索）
python scripts/vector_store.py query --query "关键词" --top-k 5

# 统计信息
python scripts/vector_store.py stats
```

---

## 记忆类别说明

### user-preferences.md

**用途**：存储用户的工作方式、编码风格、工具偏好等

**示例**：
```markdown
## 沟通风格偏好

<!-- @meta category: preferences | tags: 沟通风格，输出格式 | created: 2026-03-11 | updated: 2026-03-11 -->

- 回复风格：简洁直接，避免冗长解释
- 输出格式：优先使用表格和列表展示信息
- 语言风格：专业但友好，避免过于正式

<!-- @end -->
```

### user-profile.md

**用途**：记录用户的基本信息、职业背景、家庭情况等

**示例**：
```markdown
## 职业背景

<!-- @meta category: profile | tags: 职业，工作，背景 | created: 2026-03-11 | updated: 2026-03-11 -->

- 职业：产品经理
- 行业：互联网/科技
- 工作地点：北京

<!-- @end -->
```

### decisions-context.md

**用途**：记录用户做出的重要决定、选择方案及决策原因

**示例**：
```markdown
## 旅行方案决策

<!-- @meta category: decisions | tags: 旅行，决策，计划 | created: 2026-03-05 | updated: 2026-03-05 -->

**决定内容**：五一假期选择日本关西旅行

**决策原因**：
1. 飞行时间短（3 小时），适合带孩子出行
2. 文化相近，饮食适应
3. 预算适中，人均约 15000 元

<!-- @end -->
```

### tasks-reminder.md

**用途**：记录待办事项、提醒事项、承诺跟进等

**示例**：
```markdown
## 孩子疫苗接种提醒

<!-- @meta category: tasks | tags: 提醒，家庭，健康 | created: 2026-03-10 | updated: 2026-03-10 -->

**提醒事项**：带孩子接种百白破疫苗第三针

**截止日期**：2026-03-25

**优先级**：高

<!-- @end -->
```

### knowledge-base.md

**用途**：存储领域特定知识、业务规则、专业概念等

**示例**：
```markdown
## 签证申请流程（日本）

<!-- @meta category: knowledge | tags: 签证，日本，流程 | created: 2026-03-05 | updated: 2026-03-05 -->

**所需材料**：
1. 护照原件（有效期 6 个月以上）
2. 签证申请表（照片 4.5cm×4.5cm）
3. 在职证明
4. 银行流水（近 6 个月）
5. 行程单

**办理流程**：
1. 准备材料 → 2. 提交旅行社 → 3. 等待审核（5-7 工作日）→ 4. 领取签证

<!-- @end -->
```

---

## 短期记忆系统

> 短期记忆用于记录 24 小时内的临时信息，支持多个 Agent 之间共享上下文。超过 24 小时自动归档，30 天后自动删除。

### 短期记忆 vs 长期记忆

| 特性 | 长期记忆 | 短期记忆 |
|------|----------|----------|
| **用途** | 持久化信息 | 临时信息、Agent 间消息 |
| **保留时间** | 永久保存，手动删除 | 24 小时后归档，30 天后删除 |
| **组织方式** | 按类别分文件 | 按日期分文件（如 `2026-03-11.md`） |
| **典型内容** | 偏好设置、个人信息、知识库 | 对话记录、临时待办、Agent 消息 |

### 短期记忆结构

```
short-term/
├── 2026-03-11.md              # 今天的短期记忆
├── 2026-03-10.md              # 昨天的（待归档）
└── archived/                  # 归档目录（30 天后清理）
    ├── 2026-03-09.md
    └── ...
```

**自动归档**：每次运行 `load_context.py --mode all` 时自动检查并归档过期文件。

---

## 向量记忆系统

> 向量记忆仅存储短期记忆的向量，用于语义搜索。**长期记忆默认全量加载到上下文，不需要向量化。**

### 为什么只向量化短期记忆？

| 记忆类型 | 加载方式 | 是否需要向量 |
|----------|----------|--------------|
| **长期记忆** | 每次对话全量加载 | ❌ 不需要，已在上下文中 |
| **短期记忆** | 按需检索 | ✅ 需要，支持语义搜索 |

### 向量记忆 vs 传统搜索

| 特性 | 传统关键词搜索 | 向量语义搜索 |
|------|----------------|--------------|
| **原理** | 文本匹配 | 向量相似度 |
| **优势** | 精确匹配关键词 | 理解语义，同义词也能搜到 |
| **示例** | 搜"体检"只能找到"体检" | 搜"体检"也能找到"医院检查" |

### 环境变量配置

```bash
# .env 文件
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1          # 可选
OPENAI_EMBEDDING_MODEL=text-embedding-3-small      # 可选
```

**详细配置说明**：参考 [SETUP_GUIDE.md](SETUP_GUIDE.md)

---

## 相关文件

### 核心文档
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - 完整配置向导（环境检查、依赖安装、.env 配置）
- [assets/memory_template.md](assets/memory_template.md) - 记忆条目的完整模板

### 脚本文件
- `scripts/load_context.py` - 统一记忆加载（AI 主要使用）
- `scripts/manage_memories.py` - 长期记忆管理
- `scripts/manage_short_term.py` - 短期记忆管理
- `scripts/vector_store.py` - 向量存储管理
- `scripts/search_memories.py` - 统一搜索
- `scripts/setup_check.py` - 配置检查工具

### 参考文档
- `references/linking.md` - 记忆间双向链接的详细指南
- `references/example_memories.md` - 各类记忆的完整示例

---

## 配置检查

运行配置检查脚本验证安装：

```bash
python scripts/setup_check.py
```

**预期输出**：
```
============================================================
                    🔧 记忆系统配置检查
============================================================

✅ Python 版本：3.13.12
✅ pip 版本：26.0.1
✅ 目录正确
✅ .env 文件存在
  OPENAI_API_KEY 已配置：sk-***
✅ ChromaDB 已安装
✅ OpenAI 已安装
✅ python-dotenv 已安装
✅ 向量库目录存在
✅ 长期记忆目录存在
  找到 5 个记忆文件
✅ 短期记忆目录存在

============================================================
                       检查结果
============================================================

通过：7/7
✅ 配置完成，可以开始使用！
```

---

*详细使用说明请参考：[references/usage.md](references/usage.md)*
