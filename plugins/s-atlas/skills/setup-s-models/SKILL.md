---
name: setup-s-models
description: "「/setup-s-models」「配置 s 模型」「s 的预算」。一步步选定预算和各角色模型，写到当前软件会读的位置。Use when configuring which model and reasoning budget s uses for each role."
---

本会话首次使用本库技能时，按[全局提示词自检](../setup-s-instructions/references/daily-check.md)只读检查一次。
## 运行环境适配

涉及宿主工具、模型配置或子代理时，按需阅读[宿主适配](../../HOSTS.md)。

# 设置 s 的模型

给下面 17 个角色选定模型，写进当前宿主会读的标记段。路径、起止标记 `# s model configuration` 到 `# end s model configuration`，以及标记外的内容能不能动，以[宿主适配](../../HOSTS.md)为准。再跑一次只替换这一段，不追加第二份。宿主要求 frontmatter 时，只用该宿主参考里写明的那几行，不要套到别的软件。

只写这次已经确认可用的模型名。`inherit-parent` 和 `auto` 始终合法，派子智能体时不传模型。一个都检测不到，就请用户把有权限的名字贴过来。不要编造，也不要把别的软件里的名字抄过来。不在这 17 行里的旧角色不要写回去。

先列出这个软件里、这次真能传给子智能体的模型。软件若能列出账号可用模型，用它核对。

## 一次一问

用当前宿主的提问工具，一次只问一步。没有这种工具，就给编号选项，等回复再问下一步。每步都能跳过。第 2 到第 5 步跳过，对应项写 `inherit-parent`。第 6 步跳过表示接受当前 17 行。第 7 步未确认就不写。第 1 步跳过时：检测已经明确就用它；不明确就不写文件。

1. **确认宿主。** 说出检测到的软件。选项是它，加上 Codex、Claude Code、Cursor、WorkBuddy、DeepSeek Harness（命令 `dsh`）、Nous Research 的 Hermes agent（命令 `hermes`）。路径、技能目录、可用模型和多个 profile 的问法以[宿主适配](../../HOSTS.md)里该宿主的参考为准。Codex、Claude Code、Cursor、WorkBuddy 的写法和派法保持原样。

   认出 DeepSeek Harness 或 Hermes 时，先做完下面的识别，再回到第 2 步。两个都像，或和前面四个冲突，就停在这一步问用户。跳过这一步时，检测已经明确就用它；不明确就不写文件。

   **DeepSeek Harness。** 家目录是 `$DSH_HOME`，没设置就是 `~/.dsh`。技能在 `$DSH_HOME/skills/<name>/SKILL.md`，也扫描项目 `.dsh/skills/`、项目 `.agents/skills/` 和 `$DSH_AGENTS_HOME`（没设置就是 `~/.agents`）下的 `skills/`。标记段写在 `$DSH_HOME/AGENTS.md`：两头标记都在就只替换中间，都没有就追加到末尾，只看到一头就停。`cordis.patch.yml` 是顶层 YAML 数组，运行时按条目替换整段 `config`，注释不会变成注入对话的指令，所以标记段不写进 `$DSH_HOME/cordis.patch.yml`，也不写进 `$DSH_HOME/profiles/<profile>/cordis.patch.yml`。profile 是 `profiles/` 下已经存在的目录。多于一个就列出目录名，问用户用哪一个；只有一个就用它并说出来。只对选中的、已经存在的 profile 运行 `dsh --profile <name> --dump-config` 和 `dsh --profile <name> --dump-config-schema`。这个命令会补齐缺失的 profile 文件，不要对目录里没有的名字运行。按参考判断这次的 `subagent` 工具能不能按次换 `provider` 和 `model`。能，角色行就写成允许列表里的 `<provider>/<model>`，派出时拆回两个字段。不能，或 dump 与 schema 对不上，17 行都写 `inherit-parent`，派出时不传这两个字段，并说明限制。工具暴露了 `reasoning_effort` 时，即使角色行是 `inherit-parent`，也只传映射后的档位，让它落在父级当前路线上；没有这个字段时不传档位。列出模型用会话里的 `list_subagent_models`（有这个工具时）和 dump 里的允许路线；没有非交互的全量目录命令。文档没有 profile 级的 `AGENTS.md`，标记段在这个家目录下的 profile 都能读到。用户要求按 profile 分开写时，说明未确认有这种文件，不把标记段写进 patch。

   **Hermes。** 家目录是 `$HERMES_HOME`，没设置就是 `~/.hermes`。每个 profile 是另一套家目录，默认之外的在 `~/.hermes/profiles/<name>/`。用 `hermes profile list` 列出。多于一个（含默认 profile）就问用户写哪一个；只有默认就用它并说出来。随后的只读命令和 `SOUL.md` 都落在选中的那一家。技能在该家的 `skills/`（`<name>/SKILL.md`，类别子目录可选），项目里还有 `.hermes/skills/` 和 `.agents/skills/`。`config.yaml` 是结构化设置，注释不会进入系统提示，标记段不写进 `config.yaml`，也不改其中任何键，包括 `model`、`providers`、`custom_providers`、`delegation`。标记段写在该家的 `SOUL.md`，替换规则与上面相同。`SOUL.md` 是父对话会读的全局身份文件；子代理的项目上下文不含它。默认的 `delegate_task` 没有按次的模型参数，`delegation.model` 是全体子代理共用的一个模型。因此 17 行都写 `inherit-parent`，派出时不传模型，并说明这个限制。可选的 advanced-delegation 路线只让模型看见路线名；这次没有在工具参数里确认到可按角色传入的模型名之前，不把路线名写进 17 行，也不替用户改 `delegation`。列出模型：只读 `hermes config get model --json`，以及 `providers` 或旧键 `custom_providers` 里的 `models`（`hermes config get providers --json`、`hermes config get custom_providers --json`，键不存在就换另一个）。具名 profile 在这些命令前加 `-p <name>`。不要加 `--raw`。交互式 `hermes model` 会列出策展目录，本步骤不启动它。未确认有非交互的全量模型列表命令；配置里列不出名字时，请用户把有权限的名字贴过来，这些名字仍然不能写进 17 行，因为这次传不出去。

2. **选预算，可跳过。** 已有预算先说出来。选项一字不改：
   - `unlimited — max reasoning`（不限，最大推理）
   - `large — xhigh reasoning`（大，很高推理）
   - `medium — high reasoning`（中，高推理）
   - `small — medium reasoning`（小，中等推理）
   跳过则 `# budget` 写 `inherit-parent`，后面不改模型名后缀。DeepSeek Harness 和 Hermes 无论是否跳过，都不改模型名后缀；选定预算时映射到推理档位：`unlimited` 对 `max`，`large` 对 `xhigh`，`medium` 对 `high`，`small` 对 `medium`。该宿主或该模型没有目标档位时，按参考改成它允许的、不超过目标的最高档，并在 `# budget` 的括号里写实际档位。Codex、Claude Code、Cursor、WorkBuddy 选定预算后，第 3、4 步只列该档在检测结果里的名字。后缀目标依次是 max、xhigh、high、medium；名字以 `fast` 结尾时看前一段。对不上任何一个已检测名字，就用同一系列里不超过目标档的最高已检测名字。没有这种后缀时，unlimited 和 large 用该系列最强的已检测名字，medium 用中间的，small 用更便宜或更快的。系列只有一个名字就不动，并说明没有可调档位。系列按名字前缀分；宿主参考里有系列表就以那张表为准。

3. **选写代码的模型。** 第 1 步已经确定这个宿主不能按次把模型传给子代理时，第 3 到第 5 步不再提问，这些行都写 `inherit-parent`。其余情况，选项只有上一步得到的已检测名字，加上 `inherit-parent`。这个名字写入 `feature, refactoring`、`bug-fix`、`perf-issue`、`hillclimb`、`how explorer`、`why investigators`、`reflect tooling`、`swarm workers`。跳过则这些行都是 `inherit-parent`。

4. **选判断的模型。** 选项同样只有已检测名字和 `inherit-parent`。和第 3 步不同系列的排在前面。这个名字写入 `judgment and prose`、`hardest tasks`、`how explainer`、`why synthesizer`、`reflect judgment, divergent, synthesizer`。跳过则这些行都是 `inherit-parent`。

5. **选评审组。** 四行用同一份列表：`arena runners`、`architect runners`、`interrogate reviewers`、`arena cross-judge pool`。每个条目一个子智能体；`arena cross-judge pool` 从中选一个，优先和父级不同系列。默认是第 3 步和第 4 步的名字，顺序为写代码模型、判断模型。选项：接受这个默认、改为 `inherit-parent`，或从已检测名字里另选。另选时再问一次，只接受检测到的名字和 `inherit-parent`。跳过则四行都是 `inherit-parent`。

6. **展示 17 行。** 问是接受全部，还是改某一行。改的话再问哪一行、改成哪个已检测名字、`inherit-parent` 或 `auto`，然后重新展示，直到接受全部。检测结果里没有的真实模型名不能写。

7. **确认后写入。** 展示完整标记段。用户同意才写。写完说明路径、会不会自动读到、要不要新开对话。没有写进可发现的配置，就把限制说清楚。

正文形状如下。`# budget` 写成用户选的标签和目标档位，或 `inherit-parent`。模型名换成确认过的值。

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
