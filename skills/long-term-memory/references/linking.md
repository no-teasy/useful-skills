# 记忆关联指南

本指南说明如何在记忆之间建立双向链接，形成知识网络。

## 链接格式

### 基本语法

```markdown
[[记忆标题]](文件名.md#记忆标题)
```

### 组件说明

| 部分 | 说明 | 示例 |
|------|------|------|
| `[[记忆标题]]` | 显示的记忆标题 | `[[代码风格偏好]]` |
| `(文件名.md#记忆标题)` | 链接目标 | `(user-preferences.md#代码风格偏好)` |

## 使用场景

### 1. 相关记忆引用

当记忆内容与另一记忆相关时，添加引用：

```markdown
## Express 错误处理中间件

<!-- @meta category: snippets | tags: Express, 中间件，错误处理 | created: 2026-03-08 | updated: 2026-03-08 -->

```javascript
const errorHandler = (err, req, res, next) => {
  logger.error(err.message);
  res.status(err.status || 500).json({
    success: false,
    message: err.message
  });
};
```

### 相关记忆
- 参考 [[技术栈决策]](project-context.md#技术栈决策)
- 参见 [[JWT 认证流程]](domain-knowledge.md#JWT 认证流程)

<!-- @end -->
```

### 2. 被引用记录

在记忆条目底部记录哪些其他记忆引用了它：

```markdown
## 技术栈决策

<!-- @meta category: context | tags: 技术选型，架构 | created: 2026-03-10 | updated: 2026-03-10 -->

### 前端技术选型
- **框架**：Vue 3（使用 Composition API）
- **构建工具**：Vite

### 被引用
- [[Express 错误处理中间件]](code-snippets.md#Express 错误处理中间件) 引用了本条目
- [[API 调用封装模板]](code-snippets.md#API 调用封装模板) 引用了本条目

<!-- @end -->
```

## 链接类型

### 内部链接（同一文件内）

```markdown
[[其他记忆标题]](#其他记忆标题)
```

### 外部链接（不同文件）

```markdown
[[记忆标题]](其他文件.md#记忆标题)
```

## 最佳实践

### 1. 保持一致性

链接标题必须与目标记忆的标题**完全一致**：

```markdown
## 代码风格偏好    <!-- 目标标题 -->

[[代码风格偏好]](user-preferences.md#代码风格偏好)  <!-- 正确 -->
[[代码风格]](user-preferences.md#代码风格)          <!-- 错误：标题不匹配 -->
```

### 2. 适度链接

- 每条记忆建议有 2-5 个相关链接
- 避免过度链接造成混乱
- 只链接真正相关的内容

### 3. 双向链接

当 A 引用 B 时，建议在 B 中记录被 A 引用：

```markdown
# 记忆 A 中
### 相关记忆
- 参考 [[记忆 B]](file.md#记忆 B)

# 记忆 B 中
### 被引用
- [[记忆 A]](file.md#记忆 A) 引用了本条目
```

### 4. 链接分组

当有多个相关链接时，可以分组展示：

```markdown
### 相关记忆

**前置知识**
- [[JWT 基础]](domain-knowledge.md#JWT 基础)

**相关实现**
- [[Express 错误处理中间件]](code-snippets.md#Express 错误处理中间件)
- [[API 调用封装模板]](code-snippets.md#API 调用封装模板)

**后续扩展**
- [[认证系统优化计划]](goals-progress.md#认证系统优化计划)
```

## 自动化工具

### 检查断裂链接

```bash
python scripts/check_links.py
```

### 自动生成反向链接

```bash
python scripts/generate_backlinks.py
```

## 示例

### 完整示例：项目认证系统

**文件 1: domain-knowledge.md**
```markdown
## JWT 认证流程

<!-- @meta category: knowledge | tags: 认证，JWT, 安全 | created: 2026-03-05 | updated: 2026-03-05 -->

1. 用户登录成功后生成 JWT token
2. Token 包含用户 ID、角色、过期时间
3. 前端将 token 存储在 localStorage
4. 每次请求在 Authorization header 中携带 token
5. 后端验证 token 有效性并提取用户信息

### 相关记忆
- 实现参考 [[Express 错误处理中间件]](code-snippets.md#Express 错误处理中间件)
- 配置参考 [[技术栈决策]](project-context.md#技术栈决策)

<!-- @end -->
```

**文件 2: code-snippets.md**
```markdown
## Express 错误处理中间件

<!-- @meta category: snippets | tags: Express, 中间件，错误处理 | created: 2026-03-08 | updated: 2026-03-08 -->

```javascript
const errorHandler = (err, req, res, next) => {
  logger.error(err.message);
  res.status(err.status || 500).json({
    success: false,
    message: err.message
  });
};
```

### 相关记忆
- 用于 [[JWT 认证流程]](domain-knowledge.md#JWT 认证流程)

<!-- @end -->
```

**文件 3: project-context.md**
```markdown
## 技术栈决策

<!-- @meta category: context | tags: 技术选型，架构 | created: 2026-03-10 | updated: 2026-03-10 -->

### 认证方案
选择 JWT 作为认证方案

### 被引用
- [[JWT 认证流程]](domain-knowledge.md#JWT 认证流程) 引用了本条目

<!-- @end -->
```

## 常见问题

### Q: 链接标题包含特殊字符怎么办？

A: 保持与目标标题完全一致即可：

```markdown
## Q1 2026 目标：完成编辑器 AI 功能

[[Q1 2026 目标：完成编辑器 AI 功能]](goals-progress.md#Q1 2026 目标：完成编辑器 AI 功能)
```

### Q: 如何链接同一文件内的多个记忆？

A: 使用锚点链接：

```markdown
### 相关记忆
- [[记忆 A]](#记忆 A)
- [[记忆 B]](#记忆 B)
```

### Q: 记忆标题修改后链接会断裂吗？

A: 是的，修改标题后需要更新所有引用该标题的链接。建议使用脚本检查：

```bash
python scripts/check_links.py
```
