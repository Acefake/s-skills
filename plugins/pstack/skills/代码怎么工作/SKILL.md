---
name: 代码怎么工作
description: "用于“X 是怎么工作的”、在改东西之前先走读代码，以及关于放在哪里 / 归谁管 / 分层的问题（“这个应该放在哪”、“哪个包负责这个”、“这一层对不对”）。讲解子系统的架构、运行时的流程，帮新人建立心智模型。问动机请用 why。"
disable-model-invocation: true
---

> 翻译自 pstack 插件（编号 9717366）的 `how` skill，原作者 Lauren Tan（版权 © 2026 Lauren Tan），许可证 MIT（全文见上一级文件夹的 `LICENSE-pstack`），仅供自用。插件版本 0.15.25，原项目：https://github.com/cursor/plugins/tree/main/pstack 。
> 说明：`disable-model-invocation: true` 表示这个 skill 只能由用户主动调用，AI 不会自己调用它。文中引用其他 skill 的地方（链接、加粗或反引号里的名字、`/命令`）已经换成这个中文名版里的中文名，链接也指向对应的中文名文件夹；没翻译的 skill 保持原名。中英文名对照见 README 的“中文名对照表”。参考文件 `references/` 已翻成中文。模型名和参数名保持原样。
> 英文名备份：s-how

# 怎么工作（How）

探索代码库，回答“X 是怎么工作的？”这类问题。给出的架构讲解，要达到一位资深工程师刚接手一个子系统时所需要的程度：足够建立一个能用的心智模型，但又不能多到读起来像带注释的源代码。

每次派出的都是一个 Task 子智能体，参数为 `subagent_type: generalPurpose` 和 `readonly: true`。探索者（explorer）用 `pstack-models.mdc` 规则里的 `how explorer` 那一行（默认 `grok-4.7-xhigh-fast`），每个讲解者（explainer）用 `how explainer` 那一行（默认 `claude-opus-5-5-xhigh`）。把 `model` 设成那一行的值；如果这条规则或那一行不存在，就设成默认值。如果值是 `auto` 或 `inherit-parent`，就不设 `model`。如果 Task 工具拒绝某个模型名，就用默认的并说明一下。如果它连默认的也拒绝，就从它的报错信息里选同一系列中最接近的有效模型名。按 **poteto工作模式** skill 里 “Subagents” 一节的规定，为每个子智能体的任务选择推理等级，以及快速还是标准速度。

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
