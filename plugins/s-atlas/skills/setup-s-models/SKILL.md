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

1. **确认宿主。** 说出检测到的软件。选项是它，加上 Codex、Claude Code、Cursor、WorkBuddy。

2. **选预算，可跳过。** 已有预算先说出来。选项一字不改：
   - `unlimited — max reasoning`（不限，最大推理）
   - `large — xhigh reasoning`（大，很高推理）
   - `medium — high reasoning`（中，高推理）
   - `small — medium reasoning`（小，中等推理）
   跳过则 `# budget` 写 `inherit-parent`，后面不改模型名后缀。选定后，第 3、4 步只列该档在检测结果里的名字。后缀目标依次是 max、xhigh、high、medium；名字以 `fast` 结尾时看前一段。对不上任何一个已检测名字，就用同一系列里不超过目标档的最高已检测名字。没有这种后缀时，unlimited 和 large 用该系列最强的已检测名字，medium 用中间的，small 用更便宜或更快的。系列只有一个名字就不动，并说明没有可调档位。系列按名字前缀分；宿主参考里有系列表就以那张表为准。

3. **选写代码的模型。** 选项只有上一步得到的已检测名字，加上 `inherit-parent`。这个名字写入 `feature, refactoring`、`bug-fix`、`perf-issue`、`hillclimb`、`how explorer`、`why investigators`、`reflect tooling`、`swarm workers`。跳过则这些行都是 `inherit-parent`。

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
