---
name: setup-s-models
description: "「/setup-s-models」「配置 s 模型」「s 的预算」。一步步选定预算和各角色模型，写到当前软件会读的位置。Use when configuring which model and reasoning budget s uses for each role."
---

本会话首次使用本库技能时，按[全局提示词自检](../setup-s-instructions/references/daily-check.md)只读检查一次。
## 运行环境适配

涉及宿主工具、模型配置或子代理时，按需阅读[宿主适配](../../HOSTS.md)。

# 设置 s 的模型

给 17 个角色选定模型和预算，写入当前宿主会读的标记段。路径、以及标记外的内容能不能动，以[宿主适配](../../HOSTS.md)为准。写出的起止标记是 `# s 模型配置` 和 `# s 模型配置结束`。再跑一次时，这对标记，或旧标记 `# s model configuration` 到 `# end s model configuration`，都算同一段：整段换成下面的中文块。注释、`# 预算` 和角色键用中文；已有模型值按[角色键对照](references/role-keys.md)抄到中文键。同一角色两行都有时，留中文键上的值，英文键不写回去。旧起始行只要以 `# s model configuration` 开头就算。只看到一头就停，留下原文。宿主要求 frontmatter 时，只用该宿主参考里写明的那几行。Codex 的 `s-*.toml` 文件名仍按旧英文键生成，见该参考。

只写这次确认可用的模型名。`inherit-parent` 和 `auto` 始终合法，派子代理时不传模型。一个都检测不到，请用户把有权限的名字贴过来。不编造，不抄别的软件的名字。这 17 行以外的旧角色不写回去。

先列出这次真能传给子代理的模型。中英角色键见[角色键对照](references/role-keys.md)。写出用中文键，读取时中文键优先。

## 一次一问

用宿主的提问工具，一次一步。没有就给编号，等回复。每步都能跳过。

1. **确认宿主。** 说出检测到的软件。选项是它，加上 Codex、Claude Code、Cursor、WorkBuddy、DeepSeek Harness（`dsh`）、Hermes agent（`hermes`）。两个都像，或和前四个冲突，就停在这里问。跳过时：检测明确就用它，否则不写文件。Codex、Claude Code、Cursor、WorkBuddy 的路径和派法不变，见各自参考。

   **dsh。** 家目录是 `$DSH_HOME`，否则 `~/.dsh`。技能在 `$DSH_HOME/skills/<name>/SKILL.md`。标记段只写 `$DSH_HOME/AGENTS.md`，不写任何 `cordis.patch.yml`。`profiles/` 下多于一个已有目录就问用哪一个；只对那个目录运行 `dsh --profile <name> --dump-config` 和 `--dump-config-schema`。能按次换模型时，角色行写 `<provider>/<model>`。不能换时写 `inherit-parent`，不传 provider 和 model；工具有 `reasoning_effort` 就只传映射后的档位。名单用 `list_subagent_models` 或 dump 里的允许路线。字段和未确认项见 [dsh 参考](../s-router/references/dsh-tools.md)。

   **Hermes。** 家目录是 `$HERMES_HOME`，否则 `~/.hermes`。`hermes profile list` 多于一个就问。技能在该家的 `skills/`。标记段只写该家的 `SOUL.md`，不改 `config.yaml`。默认不能按次传模型，17 行都写 `inherit-parent`，不传模型和档位。名单用 `hermes -p <name> config get`，不要加 `--raw`。见 [Hermes 参考](../s-router/references/hermes-tools.md)。

2. **选预算。** 只问这一题，不问套餐或订阅。已有预算先说出来。额度有限的套餐建议选「省」，或在下一步把 17 行都改成 `inherit-parent`。默认是「大」。跳过则 `# 预算` 写 `inherit-parent`，不改模型名后缀；下一步先按「大」的角色分工和 2 项评审组来填，后缀用检测结果里原有的名字。

   选择卡片里，每一档都带上下面这一行说明，原文照抄：

   - 省：评审只派 1 个快模型，最难的活用强模型，最省额度
   - 中：评审派 1-2 个，判断类用强模型
   - 大：评审派 2 个（一快一强），默认
   - 不限：评审 2 个以上，思考最深，最费额度

   快模型是写代码系列，强模型是判断系列，按名字前缀分。写代码类：`写功能和重构`、`修 bug`、`性能问题`、`爬坡优化`、`怎么工作的探索者`、`为什么的调查者`、`反思的工具视角`、`群体作战的工作者`。判断类：`判断和写作`、`最难的任务`、`怎么工作的讲解者`、`为什么的综合者`、`反思的判断、发散和综合`。评审组这四行用同一份列表：`竞技场参赛者`、`架构设计参赛者`、`审问审查者`、`竞技场交叉评审`。逗号分隔的每一项派一个子代理；竞技场交叉评审从中选一项。

   Codex、Claude Code、Cursor、WorkBuddy 把推理目标写进模型名后缀：省 medium，中 high，大 xhigh，不限 max。以 `fast` 结尾时看前一段。没有刚好的后缀，就用同一系列里不超过目标的最高已检测名字。系列没有这种后缀时，不限和大用最强的，中用中间的，省用更便宜或更快的。只有一个名字就不动，并说明没有档位。DeepSeek Harness 和 Hermes 不改名字后缀；括号里写映射后的档位，宿主没有该档就按参考下调。

   省的四条评审行都写上，恰好 1 项快模型，不留空、不删行。只有 `最难的任务` 用强模型，推理 medium。中仍是 1 到 2 项：两个系列都有就写 2 项，只有一个就写 1 项，推理 high。大是恰好 2 项，先快模型再强模型，推理 xhigh。不限至少 2 项，有第三个系列再加 1 项，不把同一个名字重复一遍来凑数，推理 max。宿主不能按次传模型时，评审组仍按这个项数写 `inherit-parent`，不改成空行。

3. **展示 17 行。** 问是接受全部，还是改某一行。改的话问哪一行，以及改成哪个已检测名字、`inherit-parent` 或 `auto`，然后重新展示。检测结果里没有的真实模型名不能写。评审行数：省恰好 1 项且四行都在，中是 1 到 2 项，大恰好 2 项，不限至少 2 项。省不能把评审行改成空或删掉。跳过表示接受当前 17 行。

4. **确认后写入。** 展示完整标记段。用户同意才写。写完说明路径、会不会自动读到、要不要新开对话。

`# 预算` 写成 `省（medium）`、`中（high）`、`大（xhigh）`、`不限（max）`，宿主下调档位时括号里写实际档位，跳过则写 `inherit-parent`。旧行 `# budget` 以及 `small (medium)`、`medium (high)`、`large (xhigh)`、`unlimited (max)` 与这四档相同。重写时英文档名换成省、中、大、不限，括号里的档位照抄。

arena、architect、interrogate 按列表有几项就派几个。swarm、reflect、why、how 不读预算行来决定人数。这些技能认中文键，也认[角色键对照](references/role-keys.md)里的旧英文键。

```
# s 模型配置
# 一行一个角色。删掉一行就用技能默认。
# inherit-parent 或 auto：跟父对话的模型，派子代理时不传模型。
# 逗号分隔的列表，每一项派一个子代理。竞技场交叉评审从中选一项。
# 预算: 大（xhigh）
写功能和重构: <已确认的模型或 inherit-parent>
修 bug: <已确认的模型或 inherit-parent>
性能问题: <已确认的模型或 inherit-parent>
爬坡优化: <已确认的模型或 inherit-parent>
判断和写作: <已确认的模型或 inherit-parent>
最难的任务: <已确认的模型或 inherit-parent>
怎么工作的探索者: <已确认的模型或 inherit-parent>
怎么工作的讲解者: <已确认的模型或 inherit-parent>
为什么的调查者: <已确认的模型或 inherit-parent>
为什么的综合者: <已确认的模型或 inherit-parent>
反思的工具视角: <已确认的模型或 inherit-parent>
反思的判断、发散和综合: <已确认的模型或 inherit-parent>
竞技场参赛者: <一项或多项已确认的条目>
竞技场交叉评审: <一项或多项已确认的条目>
群体作战的工作者: <已确认的模型或 inherit-parent>
架构设计参赛者: <一项或多项已确认的条目>
审问审查者: <一项或多项已确认的条目>
# s 模型配置结束
```
