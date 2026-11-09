SKILL.md「输出」指向本文。给用户的回复按下面的全文写。

## 输出 <a id="output"></a>

用用户的语言回复，在结果允许的范围内尽量简短；图承载内容，所以一张图通常只需要一行。

- 以指向 HTML 的可点击 Markdown 链接开头：用描述性标题而不是文件名，并使用其绝对路径，路径含空格时用 `<...>` 包起来。
- 当用户想要理解一个系统或代码库，而不是画出所描述的主题时，加一两句话说明关键结论。省略只是复述图中显而易见内容的句子。
- 说明任何会改变图的读法的事项：读者可能预期却被刻意省略的部分或所选的抽象层级、示意而非实测的数值、缺失的源码证据，或在修复过程中被删掉或合并的所请求内容。
- 对于多张图，只报告一次完成，附上已有概览的链接或紧凑的逐图链接，而不是目录路径。

不要复述命令、修复轮次、哈希、质量档位或检查清单；它们留在回执中。如果被问到图是否经过验证，用一行回答，例如“Automated checks passed; not visually reviewed.”。只有为了可复现或排障才给出回执链接和细节。如果所要求的视觉审查无法运行，要说明；只有真正做了视觉检查才声称做过。保留「更新提示」一节中要求的更新提示。

示例：`Created [Checkout request timing](/abs/path/checkout-timing.html). Durations are illustrative, not measured.`

对于讲解页，用两到三行回复：结论和页面链接。只有在某个关卡失败或仍有写作警告时才提及关卡；不要粘贴草稿。

在应请求制作讲解页之后，如果上下文中没有 `[archify explainer: ...]` 行，就在回复末尾加一行可选的提议，提供主动模式，每个对话只提一次，例如：“需要的话，以后遇到解释、对比、排查这类问题，我可以主动做成这样的页面，要开启吗？” 如果用户接受，就把 `[archify explainer: proactive] Make an Archify explainer page, unasked, for explanations, comparisons, decisions, diagnoses, reviews and plans that need a table, steps or several sections.` 添加到当前代理的全局规则文件（例如 `~/.claude/CLAUDE.md`、`~/.codex/AGENTS.md` 或 `~/.config/devin/AGENTS.md`）中，并说出该文件名；删除这一行即可关闭。如果用户拒绝，就提议添加 `[archify explainer: on-demand]`，这样这个问题就不会再出现。
