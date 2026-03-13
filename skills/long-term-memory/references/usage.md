# 记忆系统详细使用指南

> 本文档提供记忆系统的详细使用说明，包括高级功能、最佳实践和故障排除。

---

## 目录

1. [记忆加载详解](#记忆加载详解)
2. [记忆管理详解](#记忆管理详解)
3. [短期记忆详解](#短期记忆详解)
4. [向量记忆详解](#向量记忆详解)
5. [记忆关联系统](#记忆关联系统)
6. [最佳实践](#最佳实践)
7. [故障排除](#故障排除)

---

## 记忆加载详解

### load_context.py 参数说明

| 参数 | 必填 | 说明 | 示例 |
|------|------|------|------|
| `--mode` | ✅ | 加载模式 | `all`, `vector` |
| `--query` | ❌ | 搜索关键词 | `"体检"` |
| `--full` | ❌ | 加载完整内容 | `--full` |
| `--top-k` | ❌ | 向量搜索结果数 | `--top-k 10` |

### 模式说明

**`--mode all`**（默认模式）
- 加载长期记忆（5 个文件）
- 加载当天短期记忆
- 自动归档过期短期记忆（>24 小时）
- 可选：添加 `--query` 进行向量搜索

**`--mode vector --query "关键词"`**
- 仅进行向量语义搜索
- 不加载长期/短期记忆
- 必须指定 `--query` 参数

### 使用场景

**场景 1：对话开始**
```bash
python scripts/load_context.py --mode all
```

**场景 2：语义搜索**
```bash
# 用户问："我之前说过要去哪里旅行？"
python scripts/load_context.py --mode vector --query "旅行"
```

**场景 3：完整加载 + 搜索**
```bash
# 既需要背景信息，又需要搜索特定内容
python scripts/load_context.py --mode all --query "体检"
```

---

## 记忆管理详解

### 添加记忆

```bash
python scripts/manage_memories.py add \
  --file user-preferences.md \
  --title "沟通风格偏好" \
  --content "- 回复风格：简洁直接\n- 输出格式：优先使用表格" \
  --tags "沟通风格，输出格式"
```

### 搜索记忆

```bash
# 关键词搜索
python scripts/manage_memories.py search --query "旅行"

# 搜索特定文件
python scripts/manage_memories.py search --query "旅行" --file decisions-context.md
```

### 更新记忆

```bash
python scripts/manage_memories.py update \
  --file user-preferences.md \
  --title "沟通风格偏好" \
  --content "- 回复风格：非常简洁"
```

### 删除记忆

```bash
python scripts/manage_memories.py delete \
  --file user-preferences.md \
  --title "沟通风格偏好"
```

---

## 短期记忆详解

### 添加短期记忆

```bash
# 记录对话内容
python scripts/manage_short_term.py add \
  --content "用户说下周要搬家，正在找搬家公司" \
  --agent chat

# 指定时间段
python scripts/manage_short_term.py add \
  --content "用户预约了上午体检" \
  --agent health \
  --section morning
```

### 查看短期记忆

```bash
# 查看今天
python scripts/manage_short_term.py show

# 查看指定日期
python scripts/manage_short_term.py show --date 2026-03-11
```

### 待跟进事项

```bash
python scripts/manage_short_term.py followup \
  --item "体检结果出来后记录到健康档案"
```

### Agent 间消息

```bash
python scripts/manage_short_term.py message \
  --from chat \
  --to health \
  --content "用户今天上午有体检，需要空腹"
```

---

## 向量记忆详解

### 初始化向量库

```bash
# 首次使用
python scripts/vector_store.py init

# 同步短期记忆
python scripts/vector_store.py sync
```

### 添加向量记忆

```bash
python scripts/vector_store.py add \
  --content "用户说今天上午要体检" \
  --source short-2026-03-11
```

### 向量搜索

```bash
# 语义搜索
python scripts/vector_store.py query --query "医院检查" --top-k 5
```

### 统计信息

```bash
python scripts/vector_store.py stats
```

---

## 记忆关联系统

### 链接格式

```markdown
[[记忆标题]](文件名.md#记忆标题)
```

### 示例

```markdown
### 相关记忆
- 参考 [[代码风格偏好]](user-preferences.md#代码风格偏好)
- 参见 [[Express 错误处理中间件]](code-snippets.md#Express 错误处理中间件)
- 相关 [[JWT 认证流程]](domain-knowledge.md#JWT 认证流程)
```

### 双向链接

当在记忆 A 中引用记忆 B 时，在记忆 B 中添加反向链接：

```markdown
### 被引用
- [[记忆 A]](文件 A.md#标题) 引用了本条目
```

**详细指南**：参考 [references/linking.md](references/linking.md)

---

## 最佳实践

### 1. 记忆命名

**好的命名**：
- `## 沟通风格偏好` - 清晰具体
- `## 日本旅行方案决策` - 包含关键信息
- `## 孩子疫苗接种提醒` - 明确主题

**避免的命名**：
- `## 一些配置` - 太模糊
- `## 旅行` - 不够具体
- `## 事情` - 无意义

### 2. 标签使用

**好的标签**：
- 2-4 个标签
- 使用逗号分隔
- 涵盖主要主题

```markdown
<!-- @meta category: preferences | tags: 沟通风格，输出格式 | ... -->
```

**避免的标签**：
- 太多标签（>10 个）
- 太宽泛（如"其他"）
- 重复内容

### 3. 记忆关联

**适度关联**：
- 每条记忆 2-5 个相关链接
- 只链接真正相关的内容
- 建立双向链接

**避免**：
- 过度链接造成混乱
- 链接到不存在的记忆
- 单向链接（只引用不反向）

### 4. 记忆更新

**及时更新**：
- 发现信息变化立即更新
- 更新 `updated` 日期
- 保留重要历史信息

**示例**：
```markdown
## 职业背景

<!-- @meta ... | updated: 2026-03-11 -->

- 职业：产品经理
- 公司：XX 科技（2024 年至今）
- 之前：YY 公司（2020-2024）
```

---

## 故障排除

### 问题 1：忘记加载记忆

**症状**：回复时忽略了用户偏好

**解决**：
```bash
# 立即加载
python scripts/load_context.py --mode all

# 向用户致歉
"抱歉，我刚才没有加载您的记忆。
 现在已读取所有记忆，我会根据您的偏好继续工作。"
```

### 问题 2：重复记录

**症状**：同一信息被记录多次

**预防**：
```bash
# 添加前先搜索
python scripts/manage_memories.py search --query "关键词"
```

**解决**：
```bash
# 删除重复条目
python scripts/manage_memories.py delete --file user-preferences.md --title "重复标题"
```

### 问题 3：记忆格式错误

**症状**：脚本无法解析记忆条目

**检查清单**：
- [ ] 标题使用 `## ` 二级标题
- [ ] meta 注释格式正确
- [ ] 结束标记正确
- [ ] 日期格式为 ISO

**修复示例**：
```markdown
## 正确的标题

<!-- @meta category: 类别 | tags: 标签 | created: 2026-03-11 | updated: 2026-03-11 -->

内容...

<!-- @end -->
```

### 问题 4：向量搜索失败

**症状**：向量搜索报错

**检查**：
```bash
# 运行配置检查
python scripts/setup_check.py

# 检查 .env 文件
cat .env

# 检查向量库
python scripts/vector_store.py stats
```

**解决**：
```bash
# 重新配置
# 编辑 .env 文件，确保 OPENAI_API_KEY 正确

# 重新初始化向量库
rm -rf vector_db
python scripts/vector_store.py init
python scripts/vector_store.py sync
```

### 问题 5：短期记忆未归档

**症状**：过期短期记忆仍在 short-term/ 目录

**解决**：
```bash
# 手动归档
python scripts/manage_short_term.py archive --date 2026-03-10

# 或运行自动归档（在 load_context.py 中自动执行）
python scripts/load_context.py --mode all
```

---

## 高级功能

### 批量操作

```bash
# 批量导出记忆
python scripts/manage_memories.py export --output backup.json

# 批量导入记忆
python scripts/manage_memories.py import --file backup.json
```

### 记忆统计

```bash
# 查看记忆数量
python scripts/manage_memories.py stats

# 查看存储使用
python scripts/manage_memories.py disk-usage
```

### 自定义脚本

可以创建自定义脚本来扩展功能：

```python
# scripts/custom_script.py
from pathlib import Path

memories_dir = Path('memories')
for file_path in memories_dir.glob('*.md'):
    # 自定义处理逻辑
    pass
```

---

## 相关文档

- [SETUP_GUIDE.md](../SETUP_GUIDE.md) - 配置向导
- [linking.md](linking.md) - 记忆关联指南
- [example_memories.md](example_memories.md) - 记忆示例
