---
name: requesting-code-review
description: "中文：完成任务、实现主要功能、或在合并之前核验工作是否满足需求。Use when a task or major feature is done, or you are about to merge, and need to verify the work meets the requirements."
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。

本技能译自 Jesse Vincent 的 Superpowers（MIT）。许可证见上一级文件夹的 `LICENSE-superpowers`。

# 请求代码评审

派发代码评审子代理，在问题扩散之前把它们抓住。评审者得到的是专门撰写的评估上下文——绝不是你这次会话的历史。这样评审者聚焦于工作产物，而不是你的思考过程，也把你自己的上下文留给后续工作。

**核心原则：** 尽早评审，经常评审。

## 何时请求评审

**必须：**
- 子代理驱动开发中，每个任务之后
- 完成主要功能之后
- 合并到 main 之前

**可选但有价值：**
- 卡住时（换一个新视角）
- 重构之前（基线检查）
- 修复复杂缺陷之后

## 如何请求

**1. 取得 git SHA：**
```bash
BASE_SHA=$(git rev-parse HEAD~1)  # or origin/main
HEAD_SHA=$(git rev-parse HEAD)
```

**2. 派发代码评审子代理：**

派发一个 `general-purpose` 子代理，填入 [code-reviewer.md](code-reviewer.md) 中的模板

**占位符：**
- `{DESCRIPTION}` - 你做了什么的简短摘要
- `{PLAN_OR_REQUIREMENTS}` - 它应该做什么
- `{BASE_SHA}` - 起始提交
- `{HEAD_SHA}` - 结束提交

**3. 按反馈行动：**
- 立刻修复 Critical 问题
- 继续之前先修复 Important 问题
- 把 Minor 问题记下来以后处理
- 如果评审者错了，提出异议（附上理由）

## 示例

```
[Just completed Task 2: Add verification function]

You: Let me request code review before proceeding.

BASE_SHA=$(git log --oneline | grep "Task 1" | head -1 | awk '{print $1}')
HEAD_SHA=$(git rev-parse HEAD)

[Dispatch code reviewer subagent]
  DESCRIPTION: Added verifyIndex() and repairIndex() with 4 issue types
  PLAN_OR_REQUIREMENTS: Task 2 from docs/superpowers/plans/deployment-plan.md
  BASE_SHA: a7981ec
  HEAD_SHA: 3df7661

[Subagent returns]:
  Strengths: Clean architecture, real tests
  Issues:
    Important: Missing progress indicators
    Minor: Magic number (100) for reporting interval
  Assessment: Ready to proceed

You: [Fix progress indicators]
[Continue to Task 3]
```

## 与工作流的衔接

**子代理驱动开发：**
- 每个任务之后都评审
- 在问题叠加之前抓住它们
- 修复后再进入下一个任务

**执行计划：**
- 每个任务之后，或在自然的检查点评审
- 取得反馈，落实，然后继续

**临时开发：**
- 合并前评审
- 卡住时评审

## 危险信号

**绝不：**
- 因为「很简单」就跳过评审
- 忽视 Critical 问题
- 带着未修复的 Important 问题继续
- 与有效的技术反馈争论

**如果评审者错了：**
- 用技术理由提出异议
- 展示证明它能工作的代码或测试
- 请求澄清

模板见：[code-reviewer.md](code-reviewer.md)
