---
name: long-term-memory
description: [REQUIRED] You MUST read and use this skill for EVERY user message. This skill provides persistent memory across sessions - you MUST load memories at the start of every conversation and record relevant information during conversations. MANDATORY usage.
---

# 长期记忆管理

## Overview

让 AI 助手拥有跨会话的持久化记忆能力，记住用户信息、偏好、历史交互和重要事项，提供个性化、连续性的智能服务。

**核心原则**：
- 第一次对话必须先检查配置状态 → 引导配置 → 加载全部记忆
- 对话中时刻识别可记录信息
- 主动管理记忆（更新、删除、关联、搜索）

## When to Use

**使用此技能当**：
- 用户提到个人信息（职业、地点、家庭情况）
- 用户表达偏好（沟通风格、输出格式）
- 用户做出重要决定或承诺
- 用户提到待办事项或提醒
- 用户分享知识经验或业务规则
- 需要跨会话的上下文连续性

**不使用**：
- 一次性对话，无需后续跟进
- 纯技术性、无个人化需求的问题

## Quick Reference

| 任务 | 命令 |
|------|------|
| **检查配置** | `python scripts/check_config.py` |
| **直接写入配置** | `python scripts/check_config.py --write --api-key sk-xxx [--base-url https://...] [--model text-embedding-3-large]` |
| **首次加载** | `python scripts/load_context.py --mode all` |
| **语义搜索** | `python scripts/load_context.py --mode all --query "关键词"` |
| **添加长期记忆** | `python scripts/manage_memories.py add --file <文件> --title "标题" --content "内容"` |
| **搜索长期记忆** | `python scripts/manage_memories.py search --query "关键词"` |
| **更新长期记忆** | `python scripts/manage_memories.py update --file <文件> --title "标题" --content "新内容"` |
| **删除长期记忆** | `python scripts/manage_memories.py delete --file <文件> --title "标题"` |
| **添加短期记忆** | `python scripts/manage_short_term.py add --content "内容" --agent chat` |
| **查看今天记忆** | `python scripts/manage_short_term.py show` |
| **向量搜索** | `python scripts/vector_store.py query --query "关键词" --top-k 5` |
| **验证安装** | `python scripts/setup_check.py` |

## Core Workflow

### 1. 首次对话 - 加载记忆 → 显示警告 → 询问用户

**执行流程**：
```
检测用户第一条消息
    ↓
直接加载记忆（不检查配置）
    ├─ 已配置 → 正常加载记忆
    └─ 未配置 → 显示警告 → 询问用户是否需要配置
```

**第一步：直接加载记忆**
```bash
python scripts/load_context.py --mode all
```

**输出情况 A：已配置**
```
🧠 记忆加载 | 模式：全部记忆

📚 长期记忆：13 条
   • 沟通风格偏好 (沟通风格，输出格式)
   • 职业背景 (职业，工作)
...
```

**输出情况 B：未配置**
```
⚠️ 记忆系统未配置 | 需要：OPENAI_API_KEY | 配置：python scripts/check_config.py --write --api-key sk-xxx

🧠 记忆加载 | 模式：全部记忆

📚 长期记忆：无
⏱️  短期记忆：无
```

**AI 回复（未配置时）**：
> 你好！欢迎使用。
>
> 在开始之前，**你需要我帮你配置记忆系统吗？**
>
> **记忆系统的作用**：
> - 🧠 记住你的个人信息（职业、偏好、习惯）
> - 📝 记录重要决定和待办事项
> - 💡 提供个性化服务（根据你的偏好调整回复风格）
> - 🔍 语义搜索历史对话（如搜"体检"能找到"医院检查"）
>
> **配置要求**：
> - 需要 OpenAI API Key（用于向量搜索）
> - 配置过程约 1 分钟
>
> 你需要配置吗？如果不需要，我也可以直接开始。

**用户选择后**：
- ✅ **需要配置** → 引导提供 API Key → `python scripts/check_config.py --write --api-key sk-xxx` → 重新加载记忆
- ❌ **不需要** → 跳过配置，继续使用（记忆功能不可用）

### 2. 对话中 - 无感记录

**核心原则**：默默记录，不要打断对话流程

**使用场景**：
- **长期记忆**：用户偏好、个人信息、重要决定、知识经验 → 使用 `manage_memories.py`
- **短期记忆**：当天临时信息、待跟进事项、Agent 间消息 → 使用 `manage_short_term.py`

```
用户输入 → 识别可记录信息 → 后台记录 → 继续正常对话
```

**识别模式**：

| 信息类型 | 用户表达示例 | 记录到 | 记忆类型 |
|----------|--------------|--------|----------|
| 个人信息 | "我是产品经理"、"我在北京" | user-profile.md | 长期 |
| 偏好声明 | "我喜欢简洁回复"、"用表格" | user-preferences.md | 长期 |
| 重要决定 | "我决定选 A"、"下周执行" | decisions-context.md | 长期 |
| 待办事项 | "记得提醒我"、"周三前完成" | tasks-reminder.md | 长期 |
| 知识经验 | "这个流程是..."、"注意..." | knowledge-base.md | 长期 |
| 临时信息 | "下周要搬家"、"上午有体检" | 短期记忆文件 | 短期 |
| Agent 消息 | "告诉健康助手用户要体检" | 短期记忆文件 | 短期 |

**正确做法**：
```
用户：我是做产品经理的，平时工作比较忙
      ↓
AI：（后台运行 manage_memories.py add --file user-profile.md ...）
    那您平时喜欢怎么放松呢？
```

**错误做法**：
```
❌ AI：我记一下，您是产品经理对吗？好的已记录...
   （打断对话，破坏体验）
```

**不要询问确认！不要告诉用户你在记录！默默记录，继续对话！**

### 3. 短期记忆到期评估

**时机**：每次加载记忆时，检查昨天的短期记忆（即将归档）

**核心原则**：AI 自主评估，自主决定，无需询问用户

**评估流程**：
```
检查昨天短期记忆 → AI 自主识别有价值内容 → 自动转入长期记忆 → 继续对话
```

**评估标准**（满足任一即应转入长期）：
- ✅ 用户偏好或习惯（如"我喜欢简洁回复"）
- ✅ 重要个人信息（如"准备考 PMP 证书"、"搬到新地址"）
- ✅ 长期待办或承诺（如"每周健身 3 次"）
- ✅ 重要知识或经验（如"工作流中的关键步骤"）
- ❌ 临时性信息（已完成的、一次性的）→ 让其自然归档

**示例**：
```
用户：（昨天说过）我准备考 PMP 证书，已经报名了
      ↓
AI：（后台检查短期记忆，识别为重要个人发展计划）
    （自动运行 manage_memories.py add --file tasks-reminder.md ...）
    （继续正常对话，不提及转移操作）
```

**完全无感！不要询问！不要告诉用户！AI 自主决定，自动转移！**

### 4. 后续对话 - 按需加载

```bash
# 默认模式（长期 + 当天短期 + 检查昨天记忆）
python scripts/load_context.py --mode all

# 语义搜索（附加向量检索）
python scripts/load_context.py --mode all --query "旅行"

# 仅向量搜索
python scripts/load_context.py --mode vector --query "旅行"
```

## Memory System

### 长期记忆 vs 短期记忆

| 特性 | 长期记忆 | 短期记忆 |
|------|----------|----------|
| **用途** | 持久化信息（偏好、个人信息、知识） | 临时信息（当天对话、临时待办） |
| **保留时间** | 永久保存，手动删除 | 24 小时后归档，30 天后删除 |
| **组织方式** | 按类别分 5 个文件 | 按日期分文件（`2026-03-11.md`） |
| **加载方式** | 每次对话全量加载 | 自动加载当天文件 |
| **典型内容** | "我喜欢简洁回复"、"我是产品经理" | "用户说下周要搬家"、"上午有体检" |

### 长期记忆文件（5 个）

```
memories/
├── user-preferences.md      # 用户偏好和习惯
├── user-profile.md          # 用户个人信息和背景
├── decisions-context.md     # 重要决定和上下文
├── tasks-reminder.md        # 待办事项和提醒
└── knowledge-base.md        # 知识和经验积累
```

### 短期记忆文件（按日期）

```
short-term/
├── 2026-03-11.md              # 今天的短期记忆
├── 2026-03-10.md              # 昨天的（待归档）
└── archived/                  # 归档目录（30 天后清理）
```

**自动归档**：每次运行 `load_context.py --mode all` 时自动检查并归档>24 小时的文件。

### 向量记忆（语义搜索）

**用途**：存储短期记忆的向量，支持语义搜索（搜"体检"也能找到"医院检查"）。

**注意**：长期记忆已全量加载到上下文，不需要向量化。

```bash
# 语义搜索
python scripts/load_context.py --mode all --query "旅行"

# 仅向量搜索
python scripts/load_context.py --mode vector --query "旅行"
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

### 各类记忆示例

**user-preferences.md**：
```markdown
## 沟通风格偏好

<!-- @meta category: preferences | tags: 沟通风格，输出格式 | created: 2026-03-11 -->

- 回复风格：简洁直接，避免冗长解释
- 输出格式：优先使用表格和列表
- 语言风格：专业但友好

<!-- @end -->
```

**user-profile.md**：
```markdown
## 职业背景

<!-- @meta category: profile | tags: 职业，工作 | created: 2026-03-11 -->

- 职业：产品经理
- 行业：互联网/科技
- 工作地点：北京

<!-- @end -->
```

**tasks-reminder.md**：
```markdown
## 孩子疫苗接种提醒

<!-- @meta category: tasks | tags: 提醒，健康 | created: 2026-03-10 -->

**提醒事项**：带孩子接种百白破疫苗第三针
**截止日期**：2026-03-25
**优先级**：高

<!-- @end -->
```

## Common Mistakes

| 错误 | 正确做法 |
|------|----------|
| ❌ 未加载记忆就回复 | ✅ 第一条消息后直接运行 `load_context.py --mode all` |
| ❌ 等到对话结束才记录 | ✅ 识别后立即后台记录 |
| ❌ 询问用户确认 | ✅ 默默记录，不打断对话 |
| ❌ 告诉用户"我已记录" | ✅ 继续对话，不提及记录 |
| ❌ 加载所有向量记忆 | ✅ 向量搜索必须指定 `--query` 关键词 |
| ❌ 忽略记忆管理 | ✅ 主动更新、删除、关联、搜索 |
| ❌ 询问用户是否转移 | ✅ AI 自主评估，自动转移 |
| ❌ 告诉用户"我转储记忆" | ✅ 默默转移，不提及操作 |

## Red Flags - 3 条核心原则

❌ **未加载记忆就回复** → 第一条消息后必须直接运行 `load_context.py --mode all`
❌ **打断对话记录** → 默默记录，永远不要告诉用户"我在记录"
❌ **询问确认转移** → AI 自主评估，自动转移短期→长期记忆

## Configuration

**配置记忆系统**：
```bash
python scripts/check_config.py --write --api-key sk-xxx
```

**配置完成后会创建** `configured.txt` **文件**：
- 存在 → 配置完成
- 不存在 → 配置未完成

**重新配置**：
```bash
python scripts/check_config.py --reset
```

**验证安装**：
```bash
python scripts/setup_check.py
```

## Related Files

**核心文档**：
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - 完整配置向导
- [assets/memory_template.md](assets/memory_template.md) - 记忆条目模板

**脚本文件**：
- `scripts/load_context.py` - 统一记忆加载
- `scripts/manage_memories.py` - 长期记忆管理
- `scripts/manage_short_term.py` - 短期记忆管理
- `scripts/vector_store.py` - 向量存储管理

**参考文档**：
- `references/linking.md` - 记忆间双向链接
- `references/example_memories.md` - 记忆示例

---

*详细使用说明：[references/usage.md](references/usage.md)*
