# nt-dispatching-parallel-agents

使用子代理并行执行任务的技能。主代理负责调度，子代理视为员工，分工明确。

## 功能特点

- **并行调度**：多个独立任务同时执行，提高效率
- **专业代理**：内置 5 种专业代理类型
  - 代码修复代理 (Code Fix Agent)
  - 代码编写代理 (Code Generation Agent)
  - 测试生成代理 (Test Generation Agent)
  - 代码审查代理 (Code Review Agent)
  - 文档编写代理 (Documentation Agent)
- **权限管理**：详细的权限控制系统，子代理只能访问指定目录
- **冲突解决**：权限冲突时子代理报告主代理处理
- **标准化报告**：每个代理完成后生成详细的任务总结报告

## 使用方法

### 调用子代理

```markdown
Task(
  description="任务描述",
  prompt="你是代码修复专家...",
  config={
    "permissions": {
      "read": ["/src/**/*"],
      "write": ["/src/**/*"],
      "execute": ["npm test"],
      "forbidden": ["/config/**/*"]
    },
    "timeout": 1800,
    "output_format": "detailed_report"
  }
)
```

### 权限配置说明

- **read**: 可读取的目录列表
- **write**: 可修改的目录列表
- **execute**: 可执行的命令列表
- **forbidden**: 禁止访问的目录列表

### 任务总结报告

每个子代理完成任务后必须生成包含以下内容的报告：

- 任务ID和执行时间
- 发现的问题及详细描述
- 解决方案
- 修改的文件列表
- 测试结果
- 遇到的问题（如权限不足）
- 任务完成度

## 文件结构

```
nt-dispatching-parallel-agents-zh/
├── SKILL.md                    # 主技能文件
├── references/
│   └── agent_prompts.md        # 完整的代理提示词模板
├── assets/
│   └── task_template.json       # 任务配置模板
└── scripts/
    └── task_dispatcher.py       # 任务调度脚本
```

## 权限冲突处理

当子代理需要修改无权限的代码时：

1. 子代理在任务总结报告中详细说明需要修改的内容
2. 主代理分析报告，权衡利弊
3. 主代理决定：
   - 调度其他有权限的代理
   - 主代理自己处理
   - 重新评估修改必要性

## 贡献

欢迎提交 Issue 和 Pull Request！
