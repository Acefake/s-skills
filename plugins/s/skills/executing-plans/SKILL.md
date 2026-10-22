---
name: executing-plans
description: "已经有书面实现计划，要在单独的会话里按审查检查点执行。要在当前会话里派子智能体逐个任务做，用 subagent-driven-development。Use when you have a written implementation plan to execute in a separate session with review checkpoints."
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。

本技能译自 Jesse Vincent 的 Superpowers（MIT）。许可证见上一级文件夹的 `LICENSE-superpowers`。

# 执行计划

## 概述

加载计划，批判性地审阅，执行全部任务，完成时汇报。

**开始时宣布：**「我正在使用 executing-plans 技能来实现这份计划。」

**注意：** 告诉你的人类协作者，Superpowers 在能够使用子代理时效果好得多。如果运行在支持子代理的平台上，工作质量会高很多（Claude Code、Codex CLI、Codex App 和 Copilot CLI 都算；各平台工具参考见 `../using-superpowers/references/`）。如果子代理可用，使用 subagent-driven-development，而不是本技能。

## 流程

### 第 1 步：加载并审阅计划
1. 阅读计划文件
2. 批判性审阅——找出你对计划的疑问或担心
3. 如果有担心：开始之前先向你的人类协作者提出
4. 如果没有担心：为计划条目创建待办，然后继续

### 第 2 步：执行任务

对每个任务：
1. 标为 in_progress
2. 严格按每一步执行（计划里的步骤都很小）
3. 按计划写明的方式运行验证
4. 标为 completed

### 第 3 步：完成开发

全部任务完成并验证之后：
- 宣布：「我正在使用 finishing-a-development-branch 技能来完成这项工作。」
- **必需子技能：** 使用 finishing-a-development-branch
- 遵循该技能来验证测试、给出选项、执行所选项

## 何时停下并求助

**出现下面情况时立刻停止执行：**
- 碰到阻碍（缺少依赖、测试失败、说明不清楚）
- 计划有关键缺口，没法开始
- 你不理解某条说明
- 验证反复失败

**请求澄清，而不是猜测。**

## 何时回到前面的步骤

**遇到下面情况时回到审阅（第 1 步）：**
- 协作者根据你的反馈更新了计划
- 根本做法需要重新考虑

**不要硬闯阻碍**——停下来问。

## 记住
- 先批判性地审阅计划
- 严格按计划步骤执行
- 不要跳过验证
- 计划说到技能时，就去引用该技能
- 受阻时停下，不要猜
- 没有用户的明确同意，不要在 main/master 分支上开始实现

## 集成

**必需的工作流技能：**
- **using-git-worktrees** - 保证工作区是隔离的（创建一个，或确认已有的那个）
- **writing-plans** - 创建本技能要执行的计划
- **finishing-a-development-branch** - 全部任务之后完成开发
