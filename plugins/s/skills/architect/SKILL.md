---
name: architect
description: "在写代码之前先勾勒类型、函数签名和模块结构，然后在实现逐步填充的过程中一直参与。用于 /architect、“architect this”（给这个做架构）、“design this”（设计一下），或者直接开写代码会定下错误形状的不简单工作。Use when you should sketch types, signatures, and module boundaries before writing a non-trivial change."
disable-model-invocation: true
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。


# 架构设计

用 `not implemented` 的函数体和伪代码，勾勒出类型、函数签名、类的形状和模块边界。综合多个模型的视角，然后照着选定的草图把代码填进去。

## 开始

开始之前，先开一个待办清单，每个阶段一条。

1. 摸底
2. 画草图
3. 达成一致
4. 实现
5. 推倒重来

## 阶段 A：摸清问题

对新代码会接触到的每个系统，建立一个真实的心智模型。对相关的子系统运行 **how** skill。说出一个文件名不算摸底。要产出 `how` 规定的那种架构讲解。如果这个设计重新定义了归属或分层，也要对现有的形状运行 **why** skill，让它背后的理由成为一个约束，而不是一个猜测。

只有当这份工作确实是全新的、周围没有任何要整合的系统时，才跳过阶段 A。

## 阶段 B：画草图

用设计草图这个任务和阶段 A 的摸底产物，运行 **arena** skill。把 `references/runner-prompt.md` 作为每个参赛者的提示词传进去。

参赛者从当前软件的 s 模型配置里 `architect runners` 那一行取，代替 `arena runners`。路径见文末。没有这一行，就按 **arena** 的默认：一个更强的模型，一个较快的写代码模型。软件不能指定模型就省略。别名条目和被拒绝的条目，按 **arena** 阶段 A 的参赛者规则处理。Cursor 的 `claude-opus-5-5-xhigh` 和 `grok-4.7-xhigh-fast` 只在 Cursor 上、并且这次确实可用时才用。

设计两遍。在综合之前，要求至少有两个结构上截然不同的候选，哪怕第一个看起来已经够好了。这就是把 **exhaust-the-design-space** 原则 skill 落到实处。要的是整体形状上的不同方案，而不是在同一个形状里做局部修补。

在综合之前，用 [`references/design-red-flags.md`](references/design-red-flags.md) 筛查每一个候选。假设下一个贡献者是一个智能体：它只看到自己打开的文件，照抄离它最近的例子，走能编译通过的最短路径。优先选那种“一个从单个文件看起来正确的改动，对整个仓库也是正确的”的设计。

按接口深度比较可行的候选。优先选那个在更小、更简单的公开接口后面藏住更多复杂度的设计。一个功能丰富的接口，可以通过把能力集中起来、而不是把它分散到各层，来让调用链保持很短。

Arena 会返回一份综合好的设计包。它的综合决定，用来填写设计理由里的“Synthesis decision”（综合决定）一节。

## 阶段 C：达成一致（可选）

默认：带着综合好的设计直接进入实现。没有人工检查点。

当调用者明确要求时，才加一个检查点：“/architect with checkpoint”（带检查点）、“stop and show me before implementing”（实现之前先停下来给我看），或者类似的话。那时就把综合好的设计展示出来，暂停等待批准。

不管哪种情况，综合结果都可以作为单独的一个提交，这就是 **foundational-thinking** 原则 skill 里“先搭脚手架”的方式。按照 **outcome-oriented-execution** 原则 skill，在填充过程中出现计划好的、范围明确的破坏是可以的。如果想在实现之前对设计施加对抗性的压力，就对综合好的草图运行 **interrogate** skill。

如果人对形状提出异议（在检查点上或者事后），就把它当作阶段 A 的证据。在写更多代码之前，重新摸底，重跑阶段 B。

## 阶段 D：照着草图实现

把 `not implemented` 的函数体换成代码，把伪代码换成逻辑。综合好的草图就是约定。偏离它的地方是要指出来的信号，而不是要默默吸收的摩擦。如果一个函数需要一个草图没预料到的参数，就问一问：是草图错了，是漏了需求，还是实现越界了。

## 阶段 E：架构错了就推倒重来

如果实现一直产生草图吸收不了的摩擦，就把草图扔掉。按照 **redesign-from-first-principles** 和 **fix-root-causes** 这两个原则 skill，不要在一个错误的设计上硬接修补。

信号是一种*模式*，而不是单个的情况。迹象有：

- 同样形状的绕过办法，在不相关的代码里反复出现。
- 多个不相关的边界情况，都需要特殊情况的分支。
- 类型需要逃生口（`any`、类型断言、实际上总是有值的可选字段）才能编译。
- 草图说状态不共享，却出现了“我们需要一把锁”的条件反射。
- 调用方必须知道这个抽象的内部规则才能使用它。
- 在整个实现里，出现了两次或更多次同样形状的、彼此独立的阶段 D 偏离。

自己判断。几个边界情况并不能判一个架构死刑。有些问题本来就复杂。数据里的复杂不等于设计里的复杂。

推倒重来时：

1. 对已经建好的部分重新运行 **how** skill。
2. 按照 redesign-from-first-principles，重新设计，就好像这些新约束从第一天起就是假设一样。
3. 按照 **subtract-before-you-add** 原则 skill，先做减法再做加法。新的草图在变大之前，应该比旧的更小。
4. 回到阶段 B，重新运行 arena。

## 产出

先写调用方的用法，再从中推导出类型草图。小改动就是一个包含新类型和签名的文件。较大的工作是一份模块地图加上类型定义。设计理由随之一起交付，按照 `references/rationale-template.md` 的形状来写，包括用法草图和综合决定。

## 在不同软件里怎么用

这个 skill 把 [arena](../arena/SKILL.md) 的派法拿来画草图。角色行换成 `architect runners`，代替 `arena runners`。拒绝规则、后台、只读评审，都按竞技场文末同一软件的那一节。配置路径以 [setup-s-models](../setup-s-models/SKILL.md) 为准。

### Cursor（原版参数）

没有 `architect runners` 时，一个 `claude-opus-5-5-xhigh`，一个 `grok-4.7-xhigh-fast`，而且这两个名字这次必须真能传给 `Task`。别名条目和被拒绝的条目，按竞技场 Cursor 一节的系列规则处理：`claude-*` 一个系列；`grok-*`、`cursor-grok-*`、`composer-*` 一个系列；被拒绝的 `composer-*` 改用 `grok-4.7-xhigh-fast`；找不到系列就用 `claude-opus-5-5-xhigh`。

参赛者是 `Task`，`run_in_background: true`，`subagent_type: generalPurpose`，`model` 为该条目。

### OpenCode

agent ID 用 `s-architect-runners-1`、`s-architect-runners-2`，`subagent` 加 `background: true`。没有这些文件时用内置 `general`，并说明继承了父级模型。文档：[Agents](https://opencode.ai/v2/docs/agents/)、[Tools](https://opencode.ai/v2/docs/tools)。

### Codex

提示词里点名 `s-architect-runners-1` 和 `s-architect-runners-2`，或点名两个这次账号里真有的模型，写明等齐再汇总。文档：[Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)。

### WorkBuddy 和 Claude Code

WorkBuddy 能拉开差异时用 `"lite"` 和 `"reasoning"`。Claude Code 用 `opus` 和 `sonnet`，或完整 ID。两边都用能写文件的通用类型，后台运行。不要填 Cursor 的模型名。

### 派不出子智能体

在主对话里自己写两份结构不同的草图，再按阶段 B 的标准选一份。
