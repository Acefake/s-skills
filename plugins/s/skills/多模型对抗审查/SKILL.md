---
name: 多模型对抗审查
description: "用于“interrogate”（审问）、“adversarial review”（对抗式审查）、“multi-model review”（多模型审查）、“challenge this”（挑战一下）、“stress test this code”（给这段代码做压力测试）、“find blind spots”（找盲点）或“tear this apart”（把它批个体无完肤）。多个大模型审查者从各自独立的角度挑战改动。"
disable-model-invocation: true
---

# 审问

每个配置好的模型派一个审查者，对代码改动做对抗式审查。对抗的信号来自模型的多样性，而不是分配给它们的角色。交付物是一份综合后的结论。**不要**自动应用任何改动。

## 第 1 步：范围

从上下文判断要审查什么：

- 如果用户指了具体的文件或一个 diff，就用那个。
- 如果在一个功能分支上，运行 `git diff main...HEAD`（或者合适的基础分支）得到完整的改动集。
- 如果用户的消息提到了最近的工作，就收集相关的文件。

把 diff 或文件内容，连同审查者理解代码所需要的周边上下文文件，一起打包。

## 第 2 步：意图

在派出审查者之前，根据用户的消息、提交信息、PR 说明（如果有的话）和代码，用一段清楚的话说明意图。如果你对意图拿不准，先问用户再继续。

## 第 3 步：派出审查者

在一条消息里启动所有审查者。读当前软件的 s 模型配置（路径见文末）里 `interrogate reviewers` 那一行，有几个条目就派几个，标记为 Reviewer A、B 等等。没有这份配置或没有这一行，就派两个：一个用你判断力最强的模型，一个用你写代码较快的模型。软件不能给子智能体单独指定模型时，两个都省略模型，让它们跟父对话走，并说一句这次没有换模型。

| 子智能体 | 没有配置、而且软件能指定模型时 |
|----------|---------------|
| Reviewer A | 判断力最强的模型。Cursor 上、并且 `claude-opus-5-5-xhigh` 确实可用时，可以用这个名字 |
| Reviewer B | 较快的写代码模型。Cursor 上、并且 `grok-4.7-xhigh-fast` 确实可用时，可以用这个名字 |

每个审查者用能看代码的类型。只读可以，但不要用会丢掉你需要的工具的只读模式。`model` 设为配置里的条目。`auto` 或 `inherit-parent` 省略模型。工具名见文末。

软件拒绝了某个配置的条目，就让那个审查者用它所在系列里、这次实际可用的最接近的名字，并说明一下。系列按名字前缀分。找不到同一系列，就用 Reviewer A 那一档。别名条目不是模型名，不要对它做回退。不要因为模型名卡住审查。

读 `references/reviewer-prompt.md`，为每个审查者填写同一个模板：写明的意图、diff 或文件内容、`references/rubric.md` 里的评审标准，以及 `references/code-quality-review.md` 里的代码质量视角。按 **poteto工作模式** skill 里 “Subagents” 一节的规定，为每个子智能体的任务选择推理等级，以及快速还是标准速度。

## 第 4 步：综合

结果陆续返回时，拼出一幅统一的图景。解析每个审查者的发现。把用不同说法描述同一个问题的发现合并起来，并记下每个问题是哪些模型提出的。两个或更多模型独立提出的发现，信号最强。只有一个模型提出的发现也要读，但相应地降低权重。记下分歧。如果一个模型指出了某个问题，而另一个明确说了相反的话，这就是给结论用的背景。

## 第 5 步：主审判断

你是主审，一位务实的资深工程师，而不是一个中立的汇总者。完整的框架见 `references/lead-judgment.md`。把每一条发现放进四个类别之一，写上提出它的模型，以及一行理由。

- **Act on**（要处理）。考虑到实际目标，会影响正确性、安全性或可维护性的真实问题。它们在一个真实的 PR 里会挡住合并。
- **Consider**（值得考虑）。有道理，但你不确定它们是否值得现在就花成本去处理。值得用户关注。
- **Noted**（记录在案）。技术上成立，但不需要行动。取决于具体情况、属于过早优化，或者在这个阶段影响很小。
- **Dismissed**（驳回）。错了、吹毛求疵或者缺少背景，附上简短的理由。

## 输出格式

### 意图（Intent）
> [第 2 步写明的那段意图]

### 审查者（Reviewers）
- Reviewer [标记]：[模型名]，[N 条发现]（每个审查者一条）

### 要处理（Act On）
[每一条：描述、哪些模型提出的、为什么重要。]

### 值得考虑（Consider）
[每一条：描述、哪些模型提出的、其中的取舍。]

### 记录在案（Noted）
[简短的列表。]

### 驳回（Dismissed）
[每一条附上简短的理由。]

### 一致性地图（Agreement Map）
[模型在哪里一致、在哪里分歧，以及这种模式说明了什么。]

## 在不同软件里怎么用

角色行是 `interrogate reviewers`。配置路径以 [设置s模型](../设置s模型/SKILL.md) 为准。工具名以 [poteto工作模式](../poteto工作模式/SKILL.md) 文末的表为准。一条消息里把审查者都派出去。

### Cursor（原版参数）

用 `Task`。每个审查者：`subagent_type: generalPurpose`，`readonly: true`，`model` 设为那一行的对应条目。`auto` 或 `inherit-parent` 省略 `model`。

没有这行配置时，Reviewer A 用 `claude-opus-5-5-xhigh`，Reviewer B 用 `grok-4.7-xhigh-fast`。这两个名字必须是这次真能传给 `Task` 的。

`Task` 拒绝了某个条目，就改用它所在系列的默认，并说一句。系列按前缀：`claude-*` 是一个系列；`grok-*`、`cursor-grok-*`、`composer-*` 是一个系列。被拒绝的 `composer-*` 改用 Reviewer B 的默认 `grok-4.7-xhigh-fast`。找不到匹配的系列，就用 Reviewer A 的默认 `claude-opus-5-5-xhigh`。连默认也被拒绝时，从报错里的有效名字里选最接近的，优先同一系列、同一推理档位，并另开一个 PR 更新默认表。别名条目不是模型名，不要对它做回退。

### OpenCode

每个审查者调一次 `subagent`。agent ID 用 [设置s模型](../设置s模型/SKILL.md) 写的 `s-interrogate-reviewers-1`、`s-interrogate-reviewers-2`（文件在 `~/.config/opencode/agents/`，`mode: subagent`，`model` 是该条目）。prompt 用填好的审查模板。这两个智能体的 `permissions` 应对 `edit` 和 `shell` 设 `deny`。

没有这些文件时，用内置 `explore`（不改文件），并说明子会话会继承父级模型，这次没有拉开差异。不要把 Cursor 的模型名写进 `model`。不要在调用上传 `model`：工具页没有这个参数，issue 里的写法标为未核实，见 poteto 文末。

文档：[Agents](https://opencode.ai/v2/docs/agents/)、[Tools](https://opencode.ai/v2/docs/tools)。

### Codex

用话派，不要找 `Task` 的 `model` 参数。提示词写成：Spawn one subagent per reviewer. Reviewer A is `<name-a>`（或 “uses model \<A\> with model_reasoning_effort \<档位\>”）. Reviewer B is `<name-b>`. Wait for both. Do not edit files. Return each reviewer's findings.

`<name-a>` 是 `~/.codex/agents/s-interrogate-reviewers-1.toml` 的 `name`。文件里的 `model` 和 `model_reasoning_effort` 优先于口头点名。没有这些文件时，在提示词里点名两个这次账号里真有的模型。文档举例 `gpt-6.1-sol` 和 `gpt-6-luna` 只在账号有它们时才用。`[agents].default_subagent_model` 是全体一个默认，拉不开两个审查者。profile 是整次进程的覆盖，不是每个审查者一个。未核实：给单个子智能体选 profile。

提示词里的「不要改文件」不会变成单独的只读沙箱。文档：[Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)。

### WorkBuddy

`Agent`，`subagent_type: "general-purpose"`。能拉开差异时一个 `"reasoning"`、一个 `"lite"`。没有 `readonly`，在提示词里禁止写文件。不要填 Cursor 的模型名。

### Claude Code

`Agent`，`subagent_type: "general-purpose"`。`model` 用 `opus` 和 `sonnet`，或两个完整 ID。不写或写 `inherit` 就跟父级。需要 MCP 时不要改用会丢掉 MCP 的 `Explore`。

### 派不出子智能体

在主对话里自己审两遍，第二遍换一种角度。软件支持的话，第二遍换一个更强的模型，并说一句。
