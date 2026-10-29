---
name: requesting-code-review
description: "「做完了帮我审查」「合并前核验一下」。完成任务或主要功能后，核对是否满足需求。Use when a task or major feature is done, or you are about to merge, and need to verify the work meets the requirements."
---

本会话首次使用本库技能时，按[全局提示词自检](../setup-s-instructions/references/daily-check.md)只读检查一次。
## 运行环境适配

涉及宿主工具、模型配置或子代理时，按需阅读[宿主适配](../../HOSTS.md)。

# 请求代码评审

派发代码评审子代理，在问题扩散之前把它们抓住。评审者得到的是专门撰写的评估上下文——绝不是你这次会话的历史。这样评审者聚焦于工作产物，而不是你的思考过程，也把你自己的上下文留给后续工作。

**核心原则：** 尽早评审，经常评审。

## 何时请求评审

**必须：**
- 子代理驱动开发中，每个任务之后
- 所有代码修改之后，包括简单小改动；范围按 code-style「交付前独立评审」确定
- 合并到 main 之前

**可选但有价值：**
- 卡住时（换一个新视角）
- 重构之前（基线检查）
- 仅咨询设计或调查，尚未修改代码但需要第二视角时

## 如何请求

**1. 确定完整审查范围：**

- 任务验收使用开始实现前记录的基线 SHA；未记录时从计划、提交历史核实真实起点，不默认使用 `HEAD~1`。
- 分支终审使用相对目标分支的 merge-base，覆盖全部任务提交。
- 同时读取暂存、未暂存修改和相关未跟踪文件的实际内容，纳入评审材料。基线时已有的无关修改单独标明并保留。
- 交接时列明基线、HEAD、工作区修改与新文件；提交范围的 diff 不能替代完整任务差异。

```bash
# 分支终审示例，目标分支以实际任务为准
BASE_SHA=$(git merge-base main HEAD)
HEAD_SHA=$(git rev-parse HEAD)
git diff "$BASE_SHA" "$HEAD_SHA"
git status --short
git diff
git diff --cached
```

**2. 派发代码评审子代理：**

使用当前宿主实际可用的只读评审角色，填入 [code-reviewer.md](code-reviewer.md) 中的模板。代码修改交付前的只读评审委派已获授权。用户明确禁止委派或没有委派能力时按 HOSTS 的回退规则自查，明确缺少独立审查；不能标为独立评审通过。已有同一最终代码的评审可复用，不重复派发。

**占位符：**
- `{REVIEW_RISK_AND_SCOPE}` - 风险触发原因、评审范围及复审时需核对的修复；首次评审明确写首次
- `{DESCRIPTION}` - 你做了什么的简短摘要
- `{PLAN_OR_REQUIREMENTS}` - 它应该做什么
- `{BASE_SHA}` - 起始提交
- `{HEAD_SHA}` - 结束提交
- `{WORKING_TREE_FILES_AND_CONTENTS}` - 暂存、未暂存及相关新文件的实际内容，注明与任务的关系；无补充时明确写无

**3. 按反馈行动：**
- 立刻修复 Critical 问题
- 继续之前先修复 Important 问题
- 把 Minor 问题记下来以后处理
- 如果评审者错了，提出异议（附上理由）

## 示例

```
[Just completed Task 2: Add verification function]

You: Let me request code review before proceeding.

BASE_SHA=<派发 Task 2 实现前记录的提交>
HEAD_SHA=$(git rev-parse HEAD)

[Dispatch code reviewer subagent]
  DESCRIPTION: Added verifyIndex() and repairIndex() with 4 issue types
  PLAN_OR_REQUIREMENTS: Task 2 from docs/s-atlas/plans/deployment-plan.md
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
