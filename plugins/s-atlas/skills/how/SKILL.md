---
name: how
description: "「这是怎么工作的」「教我这块代码」「走读一下」「这个该放哪」。讲子系统的架构和运行流程。问动机用 why。Use when you need to explain how code works, walk a subsystem before changing it, or decide where something belongs."
disable-model-invocation: true
---

本会话首次使用本库技能时，按[全局提示词自检](../setup-s-instructions/references/daily-check.md)只读检查一次。
## 运行环境适配

涉及宿主工具、模型配置或子代理时，按需阅读[宿主适配](../../HOSTS.md)。


# 怎么工作（How）

探索代码库，回答“X 是怎么工作的？”这类问题。给出的架构讲解，要达到一位资深工程师刚接手一个子系统时所需要的程度：足够建立一个能用的心智模型，但又不能多到读起来像带注释的源代码。

每次派出的都是一个子智能体。探索用只读类型；只读会丢掉你需要的工具时，改用能看代码、但提示词里禁止它写文件的类型。探索者读 s 模型配置里的「怎么工作的探索者」，没有再读旧键 `how explorer`；讲解者读「怎么工作的讲解者」，没有再读旧键 `how explainer`。路径见文末。没有这一行，探索用较快的写代码模型，讲解用判断力最强的模型。软件不能指定模型，或值是 `auto` / `inherit-parent`，就省略模型。软件拒绝了某个名字，就换同一系列里它接受的最接近的名字，并说一句。按 **s-mode** skill 里 “子智能体” 一节的规定，为每个子智能体的任务选择推理等级，以及快速还是标准速度。Cursor 的 `grok-4.7-xhigh-fast` 和 `claude-opus-5-5-xhigh` 只在 Cursor 上、并且这次确实可用时才当作这两个角色的默认。

## 1. 评估复杂度

如果范围不明确，就说出你的理解，然后去探索。用户可以再纠正方向。

- **简单**（单个模块、一个小工具函数、一个很窄的问题，比如“函数 X 是怎么工作的”）：不派探索者。派出一个讲解者，一次完成探索和讲解，提示词用 `references/explainer-prompt.md` 组装，去掉“探索者发现”那一节。跳到第 4 步。
- **复杂**（跨多个文件或服务的子系统、一个横跨多处的功能、完整的架构概览）：进入第 2 步。

拿不准的时候，走简单路线。

## 2. 探索（只用于复杂情况）

把问题拆成 2 到 4 个角度，每个角度是子系统中不同的一块。在一条消息里派出所有探索者，每个都用 `references/explorer-prompt.md`，并填好它负责的角度。

## 3. 综合（只用于复杂情况）

所有探索者都返回之后，派出一个讲解者，用 `references/explainer-prompt.md`，并填入每个探索者的发现。

## 4. 呈现

把讲解者的输出呈现出来。为了清楚，或者根据对话补充一点上下文，做些轻微的修改没问题。不要大幅重写。

## 输出格式

讲解使用 `references/explainer-prompt.md` 里规定的几个部分，不适用的就去掉：Overview（概览）、Key Concepts（关键概念）、How It Works（怎么工作）、Where Things Live（东西在哪里）、Gotchas（容易踩的坑）。

## 宿主适配

探索读「怎么工作的探索者」（旧键 `how explorer`），讲解读「怎么工作的讲解者」（旧键 `how explainer`）。中文键优先。配置路径以 [setup-s-models](../setup-s-models/SKILL.md) 为准。复杂情况先并行派探索者，等齐再派一个讲解者。

Codex、Claude Code、Cursor、WorkBuddy 的工具和配置见[宿主适配](../../HOSTS.md)；按当前宿主读取对应参考。

### 派不出子智能体

在主对话里自己探索再讲解，并说一句没有换模型。
