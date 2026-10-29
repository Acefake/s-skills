---
name: setup-s-models
description: "「/setup-s-models」「配置 s 模型」「s 的预算」。检测可用模型，写到当前软件会读的位置。Use when configuring which model and reasoning budget s uses for each role."
---

本会话首次使用本库技能时，按[全局提示词自检](../setup-s-instructions/references/daily-check.md)只读检查一次。
## 运行环境适配

涉及宿主工具、模型配置或子代理时，按需阅读[宿主适配](../../HOSTS.md)。


# 设置 s

给 s 的每个角色选定模型，并写到**当前这个软件**会读的位置。不要写死 Cursor 的规则目录。你现在不在 Cursor 里，就不要碰 `~/.cursor/rules/`。

角色行的正文在各软件里是同一份。差别只在文件放哪、要不要套该软件的 frontmatter。路径见文末「宿主适配」。

## 步骤

### 1. 确认软件，再检测可用的模型

先判断这次对话使用 Codex、Claude Code 还是 Cursor。看实际工具、用户称呼和已有配置，不要猜；无法确定时问一句。不在支持范围时说明限制，不创建未经核实的配置文件。

然后列出这个软件里、你这次真的可以传给子智能体的模型名。这是唯一可靠的来源。软件如果提供了列出账号可用模型的命令或接口，用它来核对。一个都检测不到，就请用户把有权限的模型名贴过来。

永远不要写一个你没确认可用的真实模型名。别名 `inherit-parent` 和 `auto` 总是有效，它们的意思是：这个角色跟父对话走，派子智能体时不指定模型。

Cursor 文档和旧默认值里的 `grok-4.7-xhigh-fast`、`claude-opus-5-5-xhigh` 只在 Cursor 上、并且这次检测得到它们时才能写入。Claude Code、Codex 不要照抄这两个名字。

### 2. 加载当前状态

按宿主参考中的路径读当前软件里已经写过的配置。Codex 只读 `# s model configuration` 到 `# end s model configuration` 这一段，不要把用户文件里的其他说明当成角色行。

没有这份配置，就从下面的角色表开始，每个角色先填「需要选择」。如果某一行的角色不在第 5 步的表里，比如 `how critics`，那是已经停用的角色，删掉它。

### 3. 预算、对应和确认

**(a) 询问预算。** 使用当前宿主的提问工具，名称见[宿主适配](../../HOSTS.md)中对应平台的工具对照。没有这种工具，就在对话里列出选项。标签一字不改。配置里如果已有预算，先说出来。没有配置时，说明 `large` 和下面的默认档一致。

- `unlimited — max reasoning`（不限，最大推理）
- `large — xhigh reasoning`（大，很高推理）
- `medium — high reasoning`（中，高推理）
- `small — medium reasoning`（小，中等推理）

**(b) 应用预算。** 用这次检测到的模型填表。重新运行时，保留用户已经改成别的系列、列表或别名（`inherit-parent`、`auto`）的角色。

模型名带推理档位后缀时（最后一段是 `max`、`xhigh`、`high`、`medium`、`low`；如果最后是 `fast`，看它前面那一段），四档预算分别把后缀改成 `max`、`xhigh`、`high`、`medium`。改完必须仍是检测到的名字，否则用同一系列里、不超过目标档位的最高已检测名字。系列按名字的前缀分。`inherit-parent` 和 `auto` 不变。

模型名没有这种后缀时，不要编出一个不存在的名字。`unlimited` 和 `large` 用该系列最强的已检测名字，`medium` 用中间的，`small` 用更便宜或更快的。这个系列只有一个名字，就保持不动，并说明预算没有可调的档位。

软件只能在「快」和「强」之间选时：写代码类角色用快的，判断类角色用强的。没有这种开关，就写 `inherit-parent`。

**(c) 展示各个角色并确认。** 展示每个角色和它的模型。不在检测结果里的真实模型名标为「需要选择」。列出第 2 步删掉的每一行。问用户是原样接受，还是要改某些角色。选项是检测到的模型，加上 `inherit-parent` 和 `auto`。

评审组类的角色（`arena runners`、`architect runners`、`interrogate reviewers`）的值是一个列表。每个条目（包括别名）各跑一个子智能体，所以列表的长度就是数量。`arena cross-judge pool` 也是列表，但竞技场从中选一个，尽量选和父级不同系列的。`swarm workers` 是每个工作者的默认模型，除非比赛事先给每一组指定了别的模型。

角色和用途：

| 角色行 | 用途 | 检测得到多种模型时怎么填 |
|---|---|---|
| `feature, refactoring` | 做功能和重构 | 较快的写代码模型 |
| `bug-fix` | 修 bug | 同上 |
| `perf-issue` | 性能 | 同上 |
| `hillclimb` | 反复改进 | 同上 |
| `judgment and prose` | 文字和判断 | 更强的模型，尽量和写代码的不是同一系列 |
| `hardest tasks` | 最难的改动 | 同上 |
| `how explorer` | how，探索 | 较快的写代码模型 |
| `how explainer` | how，讲解 | 更强的模型 |
| `why investigators` | why，调查 | 较快的写代码模型 |
| `why synthesizer` | why，综合 | 更强的模型 |
| `reflect tooling` | 反思，工具视角 | 较快的写代码模型 |
| `reflect judgment, divergent, synthesizer` | 反思，判断、发散和综合 | 更强的模型 |
| `arena runners` | 竞技场参赛者 | 上面两种各一个 |
| `arena cross-judge pool` | 竞技场交叉评审 | 上面两种都列入 |
| `swarm workers` | 群体作战 | 较快的写代码模型 |
| `architect runners` | 架构草图的参赛者 | 上面两种各一个 |
| `interrogate reviewers` | 对抗审查 | 上面两种各一个 |

只有一种模型，或软件不能给子智能体单独指定模型时，这些行都写 `inherit-parent`，并告诉用户这一步做不到模型多样性。

### 4. 校验

写进去的每个真实模型名都必须在检测结果里。`inherit-parent` 和 `auto` 总是能通过。某个选中的真实模型名不可用，就停下来再问一次。

### 5. 写入

覆盖当前软件的那一份 s 配置，让重新运行保持幂等。Codex 只替换标记之间的那一段，不要覆盖用户文件里的其他内容。文件不存在就新建，只放这一段。

正文形状如下。`# budget` 写成用户选的标签和目标档位。模型名换成第 3 步确认过的值。

```
# s model configuration. One line per role. Delete a line to fall back to the skill default.
# `inherit-parent` or `auto`: the role uses the parent chat model. Do not pass a model when starting a sub-agent.
# A comma-separated list starts one sub-agent per entry, except `arena cross-judge pool`, which picks one entry.
# budget: large (xhigh)
feature, refactoring: <confirmed model or inherit-parent>
bug-fix: <confirmed model or inherit-parent>
perf-issue: <confirmed model or inherit-parent>
hillclimb: <confirmed model or inherit-parent>
judgment and prose: <confirmed model or inherit-parent>
hardest tasks: <confirmed model or inherit-parent>
how explorer: <confirmed model or inherit-parent>
how explainer: <confirmed model or inherit-parent>
why investigators: <confirmed model or inherit-parent>
why synthesizer: <confirmed model or inherit-parent>
reflect tooling: <confirmed model or inherit-parent>
reflect judgment, divergent, synthesizer: <confirmed model or inherit-parent>
arena runners: <one or more confirmed entries>
arena cross-judge pool: <one or more confirmed entries>
swarm workers: <confirmed model or inherit-parent>
architect runners: <one or more confirmed entries>
interrogate reviewers: <one or more confirmed entries>
# end s model configuration
```

Cursor 的规则文件还要带该软件的 frontmatter，见宿主参考。Claude Code 的规则文件用上面这段纯文本，不要套 Cursor 的 `.mdc` frontmatter。

### 6. 确认

告诉用户写到了哪个路径、这个软件会不会自动读它、是不是要新开一个对话。没有实际写入可发现的配置时，把这项限制说清楚。

### 7. 提供一个验证 skill（可选）

检查这个项目有没有办法操作真实的应用来做证明（一个 `verify-*` skill，或者一个已有的测试工具）。如果没有，就提一次：要不要一个放在项目里的验证 skill，让智能体能像用户一样操作应用、证明改动是好的。用户同意，就调用 `/create-verification-skill`。用户拒绝，就继续，不要强推。

## 宿主适配

角色行正文仍使用第 5 步的格式。配置文件位置、角色文件和写入方式见[宿主适配](../../HOSTS.md)。无法单独指定子代理模型时，角色行使用 `inherit-parent`，并说明能力限制。
