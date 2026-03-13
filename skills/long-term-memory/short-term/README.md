# 短期记忆系统

> 记录 24 小时内的临时信息，支持多 Agent 共享上下文

## 快速开始

### 1. 添加短期记忆

```bash
# 记录用户说的话
python scripts/manage_short_term.py add \
  --content "用户说下周要搬家，正在找搬家公司" \
  --agent chat
```

### 2. 查看今天的记忆

```bash
# 查看今天的所有短期记忆
python scripts/manage_short_term.py show

# 查看指定日期的记忆
python scripts/manage_short_term.py show --date 2026-03-11
```

### 3. 添加待跟进事项

```bash
python scripts/manage_short_term.py followup \
  --item "体检结果出来后记录到健康档案"
```

### 4. Agent 间传递消息

```bash
python scripts/manage_short_term.py message \
  --from chat \
  --to health \
  --content "用户今天上午有体检，需要空腹"
```

### 5. 自动归档

```bash
# 每天运行一次，归档 24 小时前的记忆
python scripts/auto_archive.py

# 查看状态
python scripts/auto_archive.py --status
```

## 文件结构

```
short-term/
├── 2026-03-11.md              # 今天的短期记忆
├── 2026-03-10.md              # 昨天的（待归档）
└── archived/                  # 归档目录
    ├── 2026-03-09.md
    ├── 2026-03-08.md
    └── ...
```

## 记忆格式

```markdown
---
date: 2026-03-11
created: 2026-03-11 00:00:00
updated: 2026-03-11 09:30:00
agents: [chat, health, task]
---

# 短期记忆 2026-03-11

## 时间线

### 上午 (00:00-12:00)

<!-- @session id: session-09301234 | agent: chat | time: 09:30 -->

**用户**：我今天要去医院体检

**关键信息**：
- 体检需要空腹
- 时间：今天上午

<!-- @end -->

### 下午 (12:00-18:00)

<!-- 暂无记录 -->

### 晚上 (18:00-24:00)

<!-- 暂无记录 -->

---

## 今日摘要

### 待跟进事项
- [ ] 体检结果出来后记录

### 临时信息
- 用户今天上午体检

### 情绪状态
- 无特殊记录

---

## Agent 间消息

| 时间 | 发送 Agent | 接收 Agent | 消息内容 |
|------|-----------|-----------|----------|
| 09:30 | chat | health | 用户今天上午有体检 |
```

## 使用场景

### 场景 1：多 Agent 协作

**问题**：用户在不同 Agent 之间切换，上下文丢失

**解决**：使用短期记忆共享上下文

```
用户 → Chat Agent: 我今天要体检
Chat Agent → 短期记忆：记录"用户今天体检"
用户 → Health Agent: 体检要注意什么？
Health Agent ← 读取短期记忆：看到"今天体检"
Health Agent → 用户：需要空腹 8-12 小时
```

### 场景 2：临时待办追踪

**问题**：用户说了一些需要跟进的事情，但不需要长期保存

**解决**：使用短期记忆的待跟进事项

```bash
# 添加待跟进
python scripts/manage_short_term.py followup \
  --item "询问用户体检结果"

# 24 小时后自动归档，30 天后删除
```

### 场景 3：对话上下文保持

**问题**：长对话中，需要记住前面说过的话

**解决**：使用短期记忆记录对话历史

```bash
# 记录对话
python scripts/manage_short_term.py add \
  --content "用户说对海鲜过敏" \
  --agent chat

# 后续对话可以读取
```

## 命令参考

### manage_short_term.py

```bash
# 添加短期记忆
python scripts/manage_short_term.py add --content "内容" --agent chat [--section 上午]

# 显示记忆
python scripts/manage_short_term.py show [--date 2026-03-11]

# 列出所有记忆文件
python scripts/manage_short_term.py list

# 添加待跟进事项
python scripts/manage_short_term.py followup --item "事项"

# Agent 间消息
python scripts/manage_short_term.py message --from chat --to health --content "消息"

# 手动归档
python scripts/manage_short_term.py archive --date 2026-03-10
```

### auto_archive.py

```bash
# 自动归档 24 小时前的记忆
python scripts/auto_archive.py

# 仅检查，不执行
python scripts/auto_archive.py --check

# 清理 30 天前的归档
python scripts/auto_archive.py --clean

# 查看状态
python scripts/auto_archive.py --status
```

## 最佳实践

### 1. 什么应该记录到短期记忆？

✅ **适合短期记忆**：
- 临时对话内容
- 当天待办事项
- Agent 间临时消息
- 用户临时提到的信息（还未确认是否长期保存）

❌ **不适合短期记忆**：
- 用户偏好（应记录到长期记忆）
- 重要决定（应记录到长期记忆）
- 个人信息（应记录到长期记忆）

### 2. 多 Agent 协作

**命名规范**：
- `chat` - 通用对话 Agent
- `health` - 健康顾问 Agent
- `task` - 任务管理 Agent
- `travel` - 旅行规划 Agent
- `work` - 工作助手 Agent

**消息格式**：
```
时间 + 发送方 + 接收方 + 内容清晰
```

### 3. 自动归档

建议设置定时任务，每天运行一次：

```bash
# Linux/Mac cron (每天凌晨 2 点)
0 2 * * * cd /path/to/skill && python scripts/auto_archive.py

# Windows Task Scheduler
# 创建任务，每天运行 auto_archive.py
```

## 常见问题

### Q: 短期记忆和长期记忆有什么区别？

A: 
- **短期记忆**：24 小时临时信息，自动归档，用于多 Agent 共享上下文
- **长期记忆**：永久保存的重要信息，需要手动管理

### Q: 如何把短期记忆转为长期记忆？

A: 发现短期记忆中有价值的信息，手动添加到长期记忆：

```bash
# 从短期记忆发现用户偏好
# 手动添加到长期记忆
python scripts/manage_memories.py add \
  --file user-preferences.md \
  --title "饮食偏好" \
  --content "用户对海鲜过敏"
```

### Q: 归档的文件还能查看吗？

A: 可以，归档文件在 `short-term/archived/` 目录：

```bash
python scripts/manage_short_term.py show --date 2026-03-01
```

### Q: 如何恢复误归档的文件？

A: 手动从 archived/ 目录移回 short-term/ 目录：

```bash
# Linux/Mac
mv short-term/archived/2026-03-11.md short-term/

# Windows
move short-term\archived\2026-03-11.md short-term\
```
