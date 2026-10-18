---
name: 多模型对抗审查
description: "用于“interrogate”（审问）、“adversarial review”（对抗式审查）、“multi-model review”（多模型审查）、“challenge this”（挑战一下）、“stress test this code”（给这段代码做压力测试）、“find blind spots”（找盲点）或“tear this apart”（把它批个体无完肤）。多个大模型审查者从各自独立的角度挑战改动。"
disable-model-invocation: true
---

> 翻译自 pstack 插件（编号 9717366）的 `interrogate` skill，原作者 Lauren Tan（版权 © 2026 Lauren Tan），许可证 MIT（全文见上一级文件夹的 `LICENSE-pstack`），仅供自用。插件版本 0.15.25，原项目：https://github.com/cursor/plugins/tree/main/pstack 。
> 说明：`disable-model-invocation: true` 表示这个 skill 只能由用户主动调用，AI 不会自己调用它。文中引用其他 skill 的地方（链接、加粗或反引号里的名字、`/命令`）已经换成这个中文名版里的中文名，链接也指向对应的中文名文件夹；没翻译的 skill 保持原名。中英文名对照见 README 的“中文名对照表”。参考文件 `references/` 已翻成中文。模型名和严重程度标签（`critical`、`warning`、`nit`）保持原样。
> 英文名备份：s-interrogate

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

用 Task 工具在一条消息里启动所有审查者，`~/.cursor/rules/pstack-models.mdc` 里 `interrogate reviewers` 那一行有几个条目就派几个，标记为 Reviewer A、B 等等，和条目数对应。如果这条规则或那一行不存在，就用表里的默认值。

| 子智能体 | 默认模型 |
|----------|---------------|
| Reviewer A | `claude-opus-5-5-xhigh` |
| Reviewer B | `grok-4.7-xhigh-fast` |

每个审查者的参数是 `subagent_type: generalPurpose`、`readonly: true`，`model` 设为它配置的条目；如果没有配置那一行，就设为表里的默认值。对于 `auto` 或 `inherit-parent` 条目，省略 `model`，让那个审查者用父级的模型。

如果 Task 工具拒绝了某个配置的条目，就让那个审查者用它所在系列在表里的默认值，并说明一下。系列按前缀划分：`claude-*` 是一个系列；`grok-*` 和 `cursor-grok-*`、`composer-*` 是一个系列。被拒绝的 `composer-*` 条目改用 Reviewer B 的默认值。如果找不到匹配的系列，就用 Reviewer A 的默认值。如果它连表里的默认值也拒绝，就从它报错信息里的有效模型名中选最接近的等价模型来派出（优先选同一系列、同一推理档位的），并另开一个 PR 去更新默认值表。不要因为模型名的问题卡住审查。永远不要把别名条目当成被拒绝的模型名，也不要对它用上面任何一种回退规则。

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
