---
name: setup-s-models
description: "「/setup-s-models」「配置 s 模型」「s 的预算」。一步步选定预算和各角色模型，写到当前软件会读的位置。Use when configuring which model and reasoning budget s uses for each role."
---

本会话首次使用本库技能时，按[全局提示词自检](../setup-s-instructions/references/daily-check.md)只读检查一次。
## 运行环境适配

涉及宿主工具、模型配置或子代理时，按需阅读[宿主适配](../../HOSTS.md)。

# 设置 s 的模型

给 17 个角色选定模型和预算，写入当前宿主会读的标记段。路径、以及标记外的内容能不能动，以[宿主适配](../../HOSTS.md)为准。起止标记仍是 `# s model configuration` 和 `# end s model configuration`。再跑一次只替换这一段。段内旧英文注释一并换掉。宿主要求 frontmatter 时，只用该宿主参考里写明的那几行。

只写这次确认可用的模型名。`inherit-parent` 和 `auto` 始终合法，派子代理时不传模型。一个都检测不到，请用户把有权限的名字贴过来。不编造，不抄别的软件的名字。这 17 行以外的旧角色不写回去。

先列出这次真能传给子代理的模型。

## 一次一问

用宿主的提问工具，一次一步。没有就给编号，等回复。每步都能跳过。

1. **确认宿主。** 说出检测到的软件。选项是它，加上 Codex、Claude Code、Cursor、WorkBuddy、DeepSeek Harness（`dsh`）、Hermes agent（`hermes`）。两个都像，或和前四个冲突，就停在这里问。跳过时：检测明确就用它，否则不写文件。Codex、Claude Code、Cursor、WorkBuddy 的路径和派法不变，见各自参考。

   **dsh。** 家目录是 `$DSH_HOME`，否则 `~/.dsh`。技能在 `$DSH_HOME/skills/<name>/SKILL.md`。标记段只写 `$DSH_HOME/AGENTS.md`，不写任何 `cordis.patch.yml`。`profiles/` 下多于一个已有目录就问用哪一个；只对那个目录运行 `dsh --profile <name> --dump-config` 和 `--dump-config-schema`。能按次换模型时，角色行写 `<provider>/<model>`。不能换时写 `inherit-parent`，不传 provider 和 model；工具有 `reasoning_effort` 就只传映射后的档位。名单用 `list_subagent_models` 或 dump 里的允许路线。字段和未确认项见 [dsh 参考](../s-router/references/dsh-tools.md)。

   **Hermes。** 家目录是 `$HERMES_HOME`，否则 `~/.hermes`。`hermes profile list` 多于一个就问。技能在该家的 `skills/`。标记段只写该家的 `SOUL.md`，不改 `config.yaml`。默认不能按次传模型，17 行都写 `inherit-parent`，不传模型和档位。名单用 `hermes -p <name> config get`，不要加 `--raw`。见 [Hermes 参考](../s-router/references/hermes-tools.md)。

2. **选预算。** 只问这一题，不问套餐或订阅。已有预算先说出来。额度有限的套餐建议选「省」，或在下一步把 17 行都改成 `inherit-parent`。默认是「大」。跳过则 `# budget` 写 `inherit-parent`，不改模型名后缀；下一步先按「大」的角色分工和 2 项评审组来填，后缀用检测结果里原有的名字。

   选项用下面的原文：

   - 省：评审组只留 1 项，用快模型；只有 hardest tasks 用强模型，其余角色都用快模型；推理 medium
   - 中：评审组 1 到 2 项；判断类用强模型，写代码类用快模型；推理 high
   - 大：评审组 2 项，先快模型再强模型；判断类用强模型，写代码类用快模型；推理 xhigh
   - 不限：评审组至少 2 项，有第三个系列再加 1 项；判断类用强模型，写代码类用快模型；推理 max

   快模型是写代码系列，强模型是判断系列，按名字前缀分。写代码类：`feature, refactoring`、`bug-fix`、`perf-issue`、`hillclimb`、`how explorer`、`why investigators`、`reflect tooling`、`swarm workers`。判断类：`judgment and prose`、`hardest tasks`、`how explainer`、`why synthesizer`、`reflect judgment, divergent, synthesizer`。评审组这四行用同一份列表：`arena runners`、`architect runners`、`interrogate reviewers`、`arena cross-judge pool`。逗号分隔的每一项派一个子代理；`arena cross-judge pool` 从中选一项。

   Codex、Claude Code、Cursor、WorkBuddy 把推理目标写进模型名后缀：省 medium，中 high，大 xhigh，不限 max。以 `fast` 结尾时看前一段。没有刚好的后缀，就用同一系列里不超过目标的最高已检测名字。系列没有这种后缀时，不限和大用最强的，中用中间的，省用更便宜或更快的。只有一个名字就不动，并说明没有档位。DeepSeek Harness 和 Hermes 不改名字后缀；括号里写映射后的档位，宿主没有该档就按参考下调。

   中档：两个系列都有就写 2 项，只有一个就写 1 项。不限凑不满 2 项时说明，不把同一个名字重复一遍来凑数。宿主不能按次传模型时，评审组仍按上面的项数写 `inherit-parent`，这样子代理数量会跟着档位减少。

3. **展示 17 行。** 问是接受全部，还是改某一行。改的话问哪一行，以及改成哪个已检测名字、`inherit-parent` 或 `auto`，然后重新展示。检测结果里没有的真实模型名不能写。评审组项数不超过该档：省 1 项，中和大 2 项，不限不设上限。跳过表示接受当前 17 行。

4. **确认后写入。** 展示完整标记段。用户同意才写。写完说明路径、会不会自动读到、要不要新开对话。

`# budget` 写成 `省（medium）`、`中（high）`、`大（xhigh）`、`不限（max）`，宿主下调档位时括号里写实际档位，跳过则写 `inherit-parent`。旧行 `small (medium)`、`medium (high)`、`large (xhigh)`、`unlimited (max)` 与这四档相同。

arena、architect、interrogate 按列表有几项就派几个。swarm、reflect、why、how 不读这一行来决定人数。

```
# s model configuration
# 一行一个角色。删掉一行就用技能默认。
# inherit-parent 或 auto：跟父对话的模型，派子代理时不传模型。
# 逗号分隔的列表，每一项派一个子代理。arena cross-judge pool 从中选一项。
# budget: 大（xhigh）
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
