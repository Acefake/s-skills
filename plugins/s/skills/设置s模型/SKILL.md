---
name: 设置s模型
description: "配置 s 在每个角色上用哪个模型、用多大的推理预算。检测你可用的模型，并把结果写到当前软件会读的位置。用于 /设置s模型、“配置 s 模型”、“s 预算”，或者修改 s 的模型选择。"
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。


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

`~` 在 Windows 上是 `%USERPROFILE%`。工具名以 [poteto工作模式](../poteto工作模式/SKILL.md) 文末的表为准。角色行的正文仍是第 5 步那一份。Cursor、OpenCode、Codex 还要按下面的做法，把「这个角色用哪个模型」落到该软件真正会派出去的配置上。WorkBuddy 和 Claude Code 只写角色行。

| | 写到哪里 | 会不会自动读 | 依据 |
|---|---|---|---|
| Cursor | `~/.cursor/rules/s-models.mdc`。frontmatter 写 `description: s per-role model choices (overrides skill defaults)` 和 `alwaysApply: true`，下面接第 5 步的正文 | 会。新对话生效 | Cursor 的用户规则目录。这是原版的写法 |
| WorkBuddy | `~/.codebuddy/rules/s-models.md`。frontmatter 写 `alwaysApply: true`，下面接正文。Windows 路径是 `%USERPROFILE%\.codebuddy\rules\s-models.md` | 公开文档说会。新对话生效。当前这个 WorkBuddy 如果读不到 `.md`，再写同名的 `s-models.mdc`，或在设置里的「用户规则」粘贴正文 | CodeBuddy / WorkBuddy 的公开文档：用户规则在 `~/.codebuddy/rules/`，CLI 文档写的是 `.md`，IDE 文档的例子是 `.mdc`。不要写到 `~/.cursor/rules/`。这次没有在 Windows 上重新测过写入 |
| Claude Code | `~/.claude/rules/s-models.md`。只要第 5 步的正文，不要套 Cursor 的 frontmatter。Windows 是 `%USERPROFILE%\.claude\rules\` | 会。官方文档说这个目录里的个人规则对所有项目生效 | [Claude Code 的记忆文档](https://code.claude.com/docs/en/memory)。不要写到 `~/.cursor/rules/` |
| Codex | 在 `~/.codex/AGENTS.md` 里维护 `# s model configuration` 到 `# end s model configuration` 这一段。设过 `CODEX_HOME` 就用那个目录。同目录已有 `AGENTS.override.md` 时，Codex 读的是 override 而不是 `AGENTS.md`，就改 override 里的同一段。需要单独模型的角色，再写 `~/.codex/agents/s-<角色>.toml`，见下面 Codex 一节 | 会读 `AGENTS.md` 这一段，也会读 `agents/` 里的自定义智能体。只替换标记之间的内容，只覆盖 `s-` 开头的智能体文件 | [AGENTS.md](https://developers.openai.com/codex/guides/agents-md)，[Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) |
| OpenCode | 同样只改 `~/.config/opencode/AGENTS.md` 里的那一段。需要单独模型的角色，再写 `~/.config/opencode/agents/s-<角色>.md`，见下面 OpenCode 一节 | V2 会读这个全局 `AGENTS.md`，也会发现 `agents/` 里的 Markdown。Windows 上如果 `~/.config/opencode/` 没被读到，改用 OpenCode 自己的配置目录，并告诉用户。这次没有在 Windows 上测过 | [Instructions](https://opencode.ai/v2/docs/instructions)，[Agents](https://opencode.ai/v2/docs/agents/) |
| 对不上 | `~/s-models.md`，内容就是第 5 步的正文 | 不会。告诉用户把正文贴进该软件「每次对话都带上」的说明里。不要假装软件会自动读这个文件 | 没有公开文档支撑时的兜底 |

派不出子智能体、或不能给子智能体单独指定模型的软件，仍然可以运行这个 skill：把角色行写成 `inherit-parent`，并说明多样性这步做不到。

### Cursor（原版设计）

这次对话在 Cursor 里时，按下面做。模型名通过 `Task` 的 `model` 参数传给子智能体。`inherit-parent` 和 `auto` 省略 `model`。

预算和确认用 `AskQuestion`，四个标签一字不改。检测不到模型时，请用户把有权限的名字贴过来。

写入 `~/.cursor/rules/s-models.mdc`，覆盖整个文件。frontmatter 用这两行：

```
description: s per-role model choices (overrides skill defaults)
alwaysApply: true
```

`grok-4.7-xhigh-fast` 和 `claude-opus-5-5-xhigh` 只有这次真的能传给 `Task` 才写进文件。两个都在、预算是 `large` 时，角色行就是下面这份。预算不是 `large` 时，仍用这两个系列，只按第 3 步改后缀，改完的名字必须仍在检测结果里。

```
feature, refactoring: grok-4.7-xhigh-fast
bug-fix: grok-4.7-xhigh-fast
perf-issue: grok-4.7-xhigh-fast
hillclimb: grok-4.7-xhigh-fast
judgment and prose: claude-opus-5-5-xhigh
hardest tasks: claude-opus-5-5-xhigh
how explorer: grok-4.7-xhigh-fast
how explainer: claude-opus-5-5-xhigh
why investigators: grok-4.7-xhigh-fast
why synthesizer: claude-opus-5-5-xhigh
reflect tooling: grok-4.7-xhigh-fast
reflect judgment, divergent, synthesizer: claude-opus-5-5-xhigh
arena runners: claude-opus-5-5-xhigh, grok-4.7-xhigh-fast
arena cross-judge pool: claude-opus-5-5-xhigh, grok-4.7-xhigh-fast
swarm workers: grok-4.7-xhigh-fast
architect runners: claude-opus-5-5-xhigh, grok-4.7-xhigh-fast
interrogate reviewers: claude-opus-5-5-xhigh, grok-4.7-xhigh-fast
```

检测不到这两个名字时，用检测到的写代码模型和判断模型填同一张表，并说明默认名这次不可用。写完告诉用户：新开一个对话后，这条规则才会生效。

各 skill 在 Cursor 里的 `Task` 参数（`subagent_type`、`readonly`、`environment`、`cloud_base_branch`、`run_in_background`）写在那个 skill 文末的 Cursor 一节，这里不另做一套。

### OpenCode

官方做法以 V2 为准：[Agents](https://opencode.ai/v2/docs/agents/)、[Tools](https://opencode.ai/v2/docs/tools)、[Commands](https://opencode.ai/v2/docs/commands)、[从 V1 迁移](https://opencode.ai/v2/docs/migrate-v1/)。

角色行仍写在 `~/.config/opencode/AGENTS.md` 的标记段里，给父对话看。真正钉住模型的是智能体文件：`subagent` 工具官方参数是 agent ID、短 `description`、完整 `prompt`，工具页没有 `model` 参数。所以每个需要单独模型的角色，再写一个 Markdown 智能体。

- 路径：`~/.config/opencode/agents/s-<角色>.md`。项目里可以用 `.opencode/agents/s-<角色>.md`。只覆盖 `s-` 开头的这些文件，别动用户的其他智能体。`<角色>` 是角色行名字：空格和逗号换成连字符，连续的连字符合并。例如 `how explorer` 写成 `s-how-explorer.md`，`reflect judgment, divergent, synthesizer` 写成 `s-reflect-judgment-divergent-synthesizer.md`。
- 列表角色（`arena runners`、`architect runners`、`interrogate reviewers`、`arena cross-judge pool`）每个条目一个文件，在这个名字后面加 `-1`、`-2`。别的角色一个文件。`swarm workers` 是一个模型、多个工作者，只写 `s-swarm-workers.md`。
- `inherit-parent` 和 `auto` 不写智能体文件。
- frontmatter 必须有 `mode: subagent`。漏掉时，新的自定义智能体默认是 `primary`，`subagent` 工具派不了它。`description` 写这个角色是干什么的。`model` 写这次确认过的 `provider/model`，档位接在 `#` 后面，例如 `anthropic/claude-sonnet-4-5#high`。正文是这个角色的系统提示，一两句即可。
- 只读角色（对抗审查、代码怎么工作、竞技场交叉评审）在 `permissions` 里对 `edit` 和 `shell` 设 `effect: deny`。需要 MCP 的角色（代码为什么这样、反思）不要禁 `execute`，MCP 默认从那里走。
- 等价写法是配置文件里的 `agents` 对象（JSONC）。Markdown 和 JSON 二选一，不要两处各写一套会打架的字段。
- 内置 `general` 工具面宽，但不能再派子智能体。内置 `explore` 只搜索和读，不改文件。V2 没有内置 `scout`。隐藏的 `compaction`、`title`、`summary` 不能选。
- 没配 `model` 的子智能体继承父会话的模型。按 ID 选一个 primary 智能体，不会改掉会话里已经存的模型。
- 新文件不要用 V1 的单数 `agent`、分开的 `variant`、`prompt`、`permission`、`tools`、`disable`、`maxSteps`。V2 会翻译一部分旧 frontmatter，新写的用上面的字段。

未核实：在 `subagent` 调用上再传 `model`。工具页没写这个参数。维护者在 [issue 6651](https://github.com/anomalyco/opencode/issues/6651)（2026-10-01，关单，称 [#49194](https://github.com/anomalyco/opencode/pull/49194) 已加上）和仍开放的 [issue 51071](https://github.com/anomalyco/opencode/issues/51071) 里写了可选 `model`，优先级是调用参数、然后智能体的 `model`、然后父会话。按工具页来：不要传这个参数。

### Codex

这里说的是本地 Codex（CLI、IDE、桌面应用）。ChatGPT Work 是另一套托管环境，不要把它的界面套过来。

官方文档：[Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)、[配置进阶](https://learn.chatgpt.com/docs/config-file/config-advanced)、[AGENTS.md](https://developers.openai.com/codex/guides/agents-md)。当前版本默认能派子智能体。没有 Cursor 那种带 `model` 参数的 `Task` 工具。

角色行仍写在 `~/.codex/AGENTS.md`（或 `AGENTS.override.md`）的标记段里。需要单独模型的角色，再写自定义智能体：

- 路径：`~/.codex/agents/s-<角色>.toml`。设过 `CODEX_HOME` 就用那个目录下的 `agents/`。项目里可以用 `.codex/agents/`。只覆盖 `s-` 开头的文件。`<角色>` 的拼法和 OpenCode 一节相同：`how explorer` 是 `s-how-explorer.toml`，列表角色再加 `-1`、`-2`。`name` 字段等于不带扩展名的文件名。
- `inherit-parent` 和 `auto` 不写文件。
- 必填 `name`、`description`、`developer_instructions`。`name` 是派出时用的名字，和文件名保持一致最省事，以 `name` 为准。
- 同时写 `model` 和 `model_reasoning_effort`。模型名必须是这次账号里真有的。文档举例是 `gpt-6.1-sol`（重活）和 `gpt-6-luna`（快、窄），账号没有这两个名字就不要写。推理档位用第 3 步的预算目标：`unlimited` 对 `max`，`large` 对 `xhigh`，`medium` 对 `high`，`small` 对 `medium`。文档列出的档位还有 `ultra` 和 `low`。只有该模型支持这个档位才写入；不支持就写它支持的、不超过目标的最高档，并告诉用户。文档建议 GPT-6 Luna 从 `high` 起，GPT-6 Astra 从 `low` 起。
- 只读角色把「不要改文件」写进 `developer_instructions`。文档写明：这句话不会变成单独的只读沙箱。子智能体继承父级这一轮的沙箱和审批。自定义智能体继承父级的权限、provider 和 MCP，文件里不能改这些。
- 内置 `worker` 做实现，`explorer` 做读得多的探索，`default` 是通用兜底。同名自定义智能体会盖过内置。

多样性不要只靠 `[agents].default_subagent_model`。那是全体一个默认值。文档里的解析顺序是：自定义文件里写了 `model` 或 `model_reasoning_effort` 时，文件优先；文件应用前，每个字段先按「这次派出时点名的值 → `[agents]` 的对应默认 → 父级」解析。文件只写了 `model`、没写推理档位时，会保留刚才解析到的档位。`default_subagent_model` 和 `default_subagent_reasoning_effort` 可以不写。并发上限是 `max_concurrent_threads_per_session`（旧名 `max_threads`），不写时由 Codex 自己选默认。这些键在 `~/.codex/config.toml` 的 `[agents]` 里。示例配置里还有一段注释掉的 `[agents.<role>]`，用 `description` 和 `config_file` 指向 toml。Subagents 页说放进 `agents/` 目录、用 `name` 识别即可。

profile 是整次进程的覆盖：`codex --profile <name>` 先读 `~/.codex/config.toml`，再盖上 `~/.codex/<name>.config.toml` 的顶层键。Codex 0.134.0 起不再读 `config.toml` 里的 `[profiles.<name>]`，也不再支持顶层 `profile = "..."`。不要把 profile 当成某个子智能体的模型开关。未核实：能不能给一个被派的子智能体单独选 profile。文档没有这么写。

### WorkBuddy 和 Claude Code

这两个只写上面表格里的角色行，不另做智能体文件。

WorkBuddy 拉差异时，写代码类角色用 `"lite"`，判断类角色用 `"reasoning"`。这是以前在 WorkBuddy 里适配过的写法，这次没有在 Windows 上重新测过。没有这种开关就写 `inherit-parent`。

Claude Code 拉差异时，判断类用 `opus`，写代码类用 `sonnet`（或这次账号里的完整模型 ID）。派的时候不写模型或写 `inherit`，就跟父对话走。
