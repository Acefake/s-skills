---
name: arena
description: "就同一个任务同时派出 N 个并行的候选者，选出一个作为基础，再把落选者最强的部分嫁接进去。用于 /arena、“arena this”、“扔进竞技场”，或者只尝试一次做一个不简单的产物、很可能会定下错误形状的时候。Use when one attempt would lock in the wrong shape and you want several candidates, then graft the best parts together."
disable-model-invocation: true
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。


# 竞技场

在启动任何东西之前，先开一个待办清单，每个阶段一条（定框架、分派、交叉评审、选基础、嫁接、验证）。

## 阶段 A：定框架

每个候选者拿到的提示词都一样，所以提示词就是约定。

1. 说明每个候选者要产出的是什么产物。
2. 推导出评分标准：3-6 条具体的、可以打分的标准，说明在*这个*任务上成功是什么样子。它是阶段 D 里挑选者用的工具。候选者只看到任务本身。
3. 选择参赛者。用当前软件的 s 模型配置里 `arena runners` 那一行（路径见文末）。没有这份配置或没有这一行，就派两个：一个用判断力最强的模型，一个用较快的写代码模型。软件不能给子智能体单独指定模型时，省略模型，让它们跟父对话走，并说一句这次没有换模型。`auto` 或 `inherit-parent` 也省略。软件拒绝了某个名字，就换同一系列里它接受的最接近的名字，并说一句。不要把 Cursor 的 `grok-*`、`claude-*`、`composer-*` 名字填进别的软件。Cursor 上、并且 `claude-opus-5-5-xhigh` 与 `grok-4.7-xhigh-fast` 确实可用时，没有配置可以用这两个。当竞技场要覆盖多个设计方向时，多派一些参赛者。如果这份工作主要受生成量限制、而不是对判断力敏感，就把同一个模型用 N 次。按 **poteto-mode** skill 里 “子智能体” 一节的规定，为每个子智能体的任务选择推理等级，以及快速还是标准速度。
4. 按照 **principle-separate-before-serializing-shared-state** 原则 skill，给每个候选者一个它自己的输出位置（尽量用一个 git worktree，否则用 `/tmp/arena-<slug>/candidate-<n>/`）。

## 阶段 B：分派

在一条消息里用 `run_in_background: true` 派出全部 N 个子智能体。每个都给：任务、共享背景资料的路径、它自己的输出路径，以及这样的指示：产出这个产物，并写一段简短的理由，说明它考虑过哪些备选方案、否定了哪些。

如果某个候选者没有产出，就用剩下的 N-1 个继续，并注明这个掉线。

## 阶段 C：交叉评审

阶段 B 的所有候选者都完成后，从 s 模型配置里的 `arena cross-judge pool` 那一行选一个模型。没有这一行，就选一个和父级不同系列的模型；软件不能指定，就省略。优先选和父级不同系列的。派出一个只读的评审子智能体。它看到评分标准和按路径标签区分的各个候选者，逐条打分，并推荐一个基础，附上理由。它和你在阶段 D 的阅读并行进行。候选者还在写的时候，不要派出它。

## 阶段 D：选基础

在挑选之前，把每个候选者从头到尾读完。对照评分标准一条一条给每个候选者打分，而不是凭整体感觉，然后和交叉评审的结果比较。在基础的选择上意见一致，就确认了这个选择。意见不一致，说明你们当中有一方有偏差，或者评分标准有歧义。做决定之前，把双方的理由都读一遍。

选那个未来的维护者最容易在不破坏不变量的前提下扩展的基础。如果两个感觉不相上下，按照偷懒守则（Laziness Protocol），选边界更干净或 API 更小的那个。

## 阶段 E：嫁接

把每个落选的候选者再过一遍，找出值得移植到基础里的东西，通常每个候选者一两样，而不是大部分内容。按照 **principle-redesign-from-first-principles** 原则 skill，亲手把每一处嫁接融进去，让结果在同一个心智模型下保持连贯。不要机械地粘贴。

如果候选者都收敛到同一个形状，那就是很强的一致意见。记下这一点，直接交付这个共识形状。不需要嫁接。如果它们差得天南地北，说明阶段 A 的要求写得不够清楚。重新定框架再跑一遍，而不是把分歧取个平均。

## 阶段 F：验证

按照 **principle-prove-it-works** 原则 skill，像验证任何其他产出一样验证这个综合出来的产物。如果验证发现了竞技场漏掉的问题，要么是阶段 A 错了（重新定框架再跑），要么是某个候选者其实抓到了它、而你漏了这次嫁接（回到阶段 E）。不要糊弄过去。

## 产出

一个综合出来的产物，旁边附一段简短的综合说明，写明：选了哪个作为基础以及原因、交叉评审的结论、每一处嫁接以及它来自哪个候选者、否定了什么以及原因、任何收敛或掉线的情况，以及验证结果。

## 在不同软件里怎么用

参赛者读 `arena runners`，交叉评审读 `arena cross-judge pool` 并从中选一个，优先和父级不同系列。配置路径以 [setup-s-models](../setup-s-models/SKILL.md) 为准。

### Cursor（原版参数）

阶段 B：一条消息里 N 个 `Task`，`run_in_background: true`，`subagent_type: generalPurpose`（参赛者要写到自己的输出目录），`model` 为该条目。`auto` 或 `inherit-parent` 省略 `model`。

没有 `arena runners` 时，一个 `claude-opus-5-5-xhigh`，一个 `grok-4.7-xhigh-fast`，而且这两个名字这次必须真能传给 `Task`。

`Task` 拒绝了某个条目，就改用它所在系列的默认，并说一句。系列按前缀：`claude-*` 是一个系列；`grok-*`、`cursor-grok-*`、`composer-*` 是一个系列。被拒绝的 `composer-*` 改用 `grok-4.7-xhigh-fast`。找不到匹配的系列，就用 `claude-opus-5-5-xhigh`。连默认也被拒绝，就从报错里选同一系列里最接近的有效名字。别名条目不要拿去回退。

阶段 C：参赛者都完成之后，再派一个 `Task`，`subagent_type: generalPurpose`，`readonly: true`，`model` 从 `arena cross-judge pool` 里选一个，优先和父级不同系列。没有这行时，从上面两个默认里选一个不同系列的。

### OpenCode

阶段 B：每个参赛者一次 `subagent`，`background: true`。agent ID 用 `s-arena-runners-1`、`s-arena-runners-2`（`mode: subagent`，各自的 `model`）。没有这些文件时用内置 `general`，并说明继承了父级模型。

阶段 C：等后台子会话都通知完成之后，再派一个只读评审。agent ID 用池里选中的那一个 `s-arena-cross-judge-pool-<n>`。没有文件时用内置 `explore`。不要在调用上传 `model`（工具页没有这个参数；未核实的 issue 写法见 poteto 文末）。

### Codex

阶段 B 的提示词：Spawn one subagent per runner. Runner 1 is `s-arena-runners-1`. Runner 2 is `s-arena-runners-2`. Wait for all of them, then stop. 没有 toml 时，改成点名两个这次账号里真有的模型，并写上 `model_reasoning_effort`。文档举例 `gpt-6.1-sol` 和 `gpt-6-luna` 只在账号有它们时才用。

阶段 C：等齐之后再派一个。Spawn one subagent, `s-arena-cross-judge-pool-<n>`（或点名池里选中的模型）. It only scores. Do not edit files. Wait for it. 提示词禁止改文件，不会变成单独的只读沙箱。

`default_subagent_model` 拉不开多个参赛者。profile 不是每个参赛者一个。未核实：给单个子智能体选 profile。

### WorkBuddy

参赛者用 `Agent`，`subagent_type: "general-purpose"`，`run_in_background: true`。能拉开差异时一个 `"lite"`、一个 `"reasoning"`。交叉评审改派 `Explore` 或 `Plan`。不要填 Cursor 的模型名。

### Claude Code

参赛者用 `Agent`，`subagent_type: "general-purpose"`，`run_in_background: true`。模型用 `opus` 和 `sonnet`，或完整 ID。交叉评审用 `Explore`。不写模型或写 `inherit` 就跟父级。

### 派不出子智能体

在主对话里自己做两稿，再自己按评分标准选。软件支持的话，第二稿换一个更强的模型。
