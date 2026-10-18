---
name: 设置s模型
description: "配置 s 在每个角色上用哪个模型、用多大的推理预算。检测你可用的模型，并把结果写到当前软件会读的位置。用于 /设置s模型、“配置 s 模型”、“s 预算”，或者修改 s 的模型选择。"
---

# 设置 s

给 s 的每个角色选定模型，并写到**当前这个软件**会读的位置。不要写死 Cursor 的规则目录。你现在不在 Cursor 里，就不要碰 `~/.cursor/rules/`。

角色行的正文在各软件里是同一份。差别只在文件放哪、要不要套该软件的 frontmatter。路径见文末「在不同软件里怎么用」。

## 步骤

### 1. 确认软件，再检测可用的模型

先判断这次对话跑在哪个软件里。看你实际有的工具、用户怎么称呼这个软件，以及家目录里已经存在的配置。不要猜。像两个软件时，问一句。五个都对不上，走文末的兜底。

然后列出这个软件里、你这次真的可以传给子智能体的模型名。这是唯一可靠的来源。软件如果提供了列出账号可用模型的命令或接口，用它来核对。一个都检测不到，就请用户把有权限的模型名贴过来。

永远不要写一个你没确认可用的真实模型名。别名 `inherit-parent` 和 `auto` 总是有效，它们的意思是：这个角色跟父对话走，派子智能体时不指定模型。

Cursor 文档和旧默认值里的 `grok-4.7-xhigh-fast`、`claude-opus-5-5-xhigh` 只在 Cursor 上、并且这次检测得到它们时才能写入。WorkBuddy、Claude Code、Codex、OpenCode 不要照抄这两个名字。

### 2. 加载当前状态

按文末的路径读当前软件里已经写过的配置。Codex 和 OpenCode 只读 `# s model configuration` 到 `# end s model configuration` 这一段，不要把用户文件里的其他说明当成角色行。

没有这份配置，就从下面的角色表开始，每个角色先填「需要选择」。如果某一行的角色不在第 5 步的表里，比如 `how critics`，那是已经停用的角色，删掉它。

### 3. 预算、对应和确认

**(a) 询问预算。** 用这个软件里向用户提问的工具（名字见 [poteto工作模式](../poteto工作模式/SKILL.md) 文末的表）。没有这种工具，就在对话里列出选项。标签一字不改。配置里如果已有预算，先说出来。没有配置时，说明 `large` 和下面的默认档一致。

- `unlimited — max reasoning`（不限，最大推理）
- `large — xhigh reasoning`（大，很高推理）
- `medium — high reasoning`（中，高推理）
- `small — medium reasoning`（小，中等推理）

**(b) 应用预算。** 用这次检测到的模型填表。重新运行时，保留用户已经改成别的系列、列表或别名（`inherit-parent`、`auto`）的角色。

模型名带推理档位后缀时（最后一段是 `max`、`xhigh`、`high`、`medium`、`low`；如果最后是 `fast`，看它前面那一段），四档预算分别把后缀改成 `max`、`xhigh`、`high`、`medium`。改完必须仍是检测到的名字，否则用同一系列里、不超过目标档位的最高已检测名字。系列按名字的前缀分。`inherit-parent` 和 `auto` 不变。

模型名没有这种后缀时，不要编出一个不存在的名字。`unlimited` 和 `large` 用该系列最强的已检测名字，`medium` 用中间的，`small` 用更便宜或更快的。这个系列只有一个名字，就保持不动，并说明预算没有可调的档位。

软件只能在「快」和「强」之间选（WorkBuddy 里对应 `"lite"` 和 `"reasoning"`，这是以前在 WorkBuddy 里适配过的写法）：写代码类角色用快的，判断类角色用强的。没有这种开关，就写 `inherit-parent`。

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
| `how explorer` | 代码怎么工作，探索 | 较快的写代码模型 |
| `how explainer` | 代码怎么工作，讲解 | 更强的模型 |
| `why investigators` | 代码为什么这样，调查 | 较快的写代码模型 |
| `why synthesizer` | 代码为什么这样，综合 | 更强的模型 |
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

覆盖当前软件的那一份 s 配置，让重新运行保持幂等。Codex 和 OpenCode 只替换标记之间的那一段，不要覆盖用户文件里的其他内容。文件不存在就新建，只放这一段。

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

Cursor 和 WorkBuddy 的规则文件还要带该软件的 frontmatter，见文末。Claude Code 的规则文件用上面这段纯文本，不要套 Cursor 的 `.mdc` frontmatter。

### 6. 确认

告诉用户写到了哪个路径、这个软件会不会自动读它、是不是要新开一个对话。兜底文件不会自动生效，把这句话说清楚。

### 7. 提供一个验证 skill（可选）

检查这个项目有没有办法操作真实的应用来做证明（一个 `verify-*` skill，或者一个已有的测试工具）。如果没有，就提一次：要不要一个放在项目里的验证 skill，让智能体能像用户一样操作应用、证明改动是好的。用户同意，就调用 `/创建验证skill`。用户拒绝，就继续，不要强推。

## 在不同软件里怎么用

`~` 在 Windows 上是 `%USERPROFILE%`。工具名以 [poteto工作模式](../poteto工作模式/SKILL.md) 文末的表为准。

| | 写到哪里 | 会不会自动读 | 依据 |
|---|---|---|---|
| Cursor | `~/.cursor/rules/s-models.mdc`。frontmatter 写 `description: s per-role model choices` 和 `alwaysApply: true`，下面接第 5 步的正文 | 会。新对话生效 | Cursor 的用户规则目录。这是原版的写法 |
| WorkBuddy | `~/.codebuddy/rules/s-models.md`。frontmatter 写 `alwaysApply: true`，下面接正文。Windows 路径是 `%USERPROFILE%\.codebuddy\rules\s-models.md` | 公开文档说会。新对话生效。当前这个 WorkBuddy 如果读不到 `.md`，再写同名的 `s-models.mdc`，或在设置里的「用户规则」粘贴正文 | CodeBuddy / WorkBuddy 的公开文档：用户规则在 `~/.codebuddy/rules/`，CLI 文档写的是 `.md`，IDE 文档的例子是 `.mdc`。不要写到 `~/.cursor/rules/`。这次没有在 Windows 上重新测过写入 |
| Claude Code | `~/.claude/rules/s-models.md`。只要第 5 步的正文，不要套 Cursor 的 frontmatter。Windows 是 `%USERPROFILE%\.claude\rules\` | 会。官方文档说这个目录里的个人规则对所有项目生效 | [Claude Code 的记忆文档](https://code.claude.com/docs/en/memory)。不要写到 `~/.cursor/rules/` |
| Codex | 在 `~/.codex/AGENTS.md` 里维护 `# s model configuration` 到 `# end s model configuration` 这一段。设过 `CODEX_HOME` 就用那个目录。同目录已有 `AGENTS.override.md` 时，Codex 读的是 override 而不是 `AGENTS.md`，就改 override 里的同一段 | 会读这个文件。只替换标记之间的内容，不要覆盖用户的其他说明 | [Codex 的 AGENTS.md 文档](https://developers.openai.com/codex/guides/agents-md) |
| OpenCode | 同样只改 `~/.config/opencode/AGENTS.md` 里的那一段 | 按 OpenCode V2 的文档，会读这个全局 `AGENTS.md`，不认 `CLAUDE.md`。Windows 上如果这个路径没被读到，改用 OpenCode 自己的配置目录，并告诉用户 | [OpenCode 的 Instructions 文档](https://opencode.ai/v2/docs/instructions) |
| 对不上 | `~/s-models.md`，内容就是第 5 步的正文 | 不会。告诉用户把正文贴进该软件「每次对话都带上」的说明里。不要假装软件会自动读这个文件 | 没有公开文档支撑时的兜底 |

派不出子智能体、或不能给子智能体单独指定模型的软件，仍然可以运行这个 skill：把角色行写成 `inherit-parent`，并说明多样性这步做不到。
