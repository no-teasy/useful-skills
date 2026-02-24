# 任务格式规范

## 任务配置文件结构

任务配置文件使用JSON格式，定义需要并行执行的子代理任务：

```json
{
  "tasks": [
    {
      "id": "任务唯一标识符",
      "description": "任务描述",
      "work_dir": "工作目录路径",
      "permissions": ["权限路径列表"],
      "type": "任务类型",
      "priority": "优先级"
    }
  ]
}
```

### 字段说明

- **id**: 任务的唯一标识符，用于跟踪和报告
- **description**: 详细的任务描述，包含具体要求
- **work_dir**: 子代理的工作目录
- **permissions**: 子代理的文件访问权限列表
- **type**: 任务类型 (bug_fix, feature, optimization, refactoring)
- **priority**: 任务优先级 (high, medium, low)

## 权限控制

### 权限格式

权限使用路径模式定义：

```json
{
  "permissions": [
    "/src/module1/*",      // 模块1下所有文件的读写权限
    "/tests/module1/*",    // 模块1测试文件的读写权限
    "/docs/module1/*"      // 模块1文档的只读权限
  ]
}
```

### 权限级别

1. **读写权限** (`rw`): 可以读取和修改文件
2. **只读权限** (`r`): 只能读取文件
3. **无权限** (`none`): 无法访问该路径

## 子代理任务总结报告格式

每个完成的子代理必须返回以下格式的JSON报告：

```json
{
  "task_id": "任务ID",
  "agent": "子代理名称",
  "execution_time": {
    "start": "2023-01-01T10:00:00Z",
    "end": "2023-01-01T10:30:00Z"
  },
  "work_dir": "工作目录",
  "permissions": ["权限范围"],
  "findings": [
    {
      "type": "bug|optimization|security_issue",
      "description": "发现的问题描述",
      "severity": "high|medium|low"
    }
  ],
  "solutions": [
    {
      "description": "解决方案描述",
      "files_modified": ["文件路径列表"]
    }
  ],
  "modified_files": [
    {
      "path": "文件路径",
      "reason": "修改原因",
      "changes": "变更摘要"
    }
  ],
  "test_results": {
    "before": "修复前状态",
    "after": "修复后状态"
  },
  "problems_encountered": [
    {
      "type": "权限不足|依赖缺失|冲突",
      "description": "遇到的问题",
      "requires_attention": true
    }
  ],
  "summary": {
    "completion_rate": "完成度百分比",
    "follow_up_needed": true|false,
    "follow_up_reason": "需要后续工作的原因"
  }
}
```

## 任务调度决策树

```
收到任务请求
    ↓
分析任务依赖关系
    ↓
┌─────────────────┐
│ 任务是否独立？   │ ←───── 否
│                 │
└─────┬───────────┘
      │ 是
      ↓
┌─────────────────┐
│ 有共享资源？    │ ←───── 是 ────→ 顺序执行
│                 │                  ↓
└─────┬───────────┘              冲突解决
      │ 否                        ↓
      ↓                      通知主代理
┌─────────────────┐
│ 资源是否充足？  │ ←───── 否
│ (CPU/内存)      │
└─────┬───────────┘
      │ 是
      ↓
┌─────────────────┐
│ 启动并行子代理  │
│ (每个任务一个)  │
└─────────────────┘
      ↓
┌─────────────────┐
│ 等待所有子代理  │
│ 完成并返回报告  │
└─────────────────┘
      ↓
┌─────────────────┐
│ 合并结果，验证  │
│ 冲突，整合修改  │
└─────────────────┘
```

## 错误处理

### 子代理错误类型

1. **权限错误**: 尝试访问无权限资源
   - 解决: 报告主代理，请求权限调整或重新分配

2. **依赖错误**: 依赖的模块或文件缺失
   - 解决: 检查工作目录和依赖项

3. **冲突错误**: 与其他代理的修改冲突
   - 解决: 报告主代理，协调解决

### 错误报告格式

```json
{
  "error": {
    "type": "权限错误|依赖错误|冲突错误",
    "message": "错误消息",
    "timestamp": "时间戳",
    "task_id": "关联任务ID",
    "requires_intervention": true|false
  }
}
```