---
name: show-me-your-work
description: "「/show-me-your-work」「留下决定记录」「通宵跑完我回来看」。长时间或无人值守的工作，每个决定记一行。Use when a long or unattended run needs a decision log."
disable-model-invocation: true
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。


# 把你的过程摆出来

只保留一份权威的日志。

## 格式

一个 TSV 文件，每个决定一行。每个单元格都只有一行。证据是一个指针，而不是一段文字。

复制 `references/decision-log-template.tsv`（表头那一行），开始一份干净的日志。各列：

- **ts。** ISO8601 格式的时间戳。
- **phase。** 阶段或工作线。
- **decision。** 选了什么或做了什么，一行。
- **why。** 用平常的话写的理由。如果是某条原则促成的，就直白地说出来，而不是写一个行话标签。
- **evidence。** 能证明它的一个链接或路径：提交的 SHA、PR 编号、`file:line`，或者一个产物、追踪记录或截图的路径。永远不要写一段话。
- **result。** 结果或判断条件的状态：`tests green`（测试通过）、`reverted`（已撤回）、`pixel-diff 0`（像素差异为 0）、`INCONCLUSIVE`（无法确定）、`open`（未解决）。

下面是一个例子，写得很直白，审查者一眼就能看懂。

```
ts	phase	decision	why	evidence	result
2026-05-24T09:02:00Z	frame	counted the work first, about 100 components and roughly 75 hours	wanted to know the size before starting a long run	commit 3a9f1c2	found 5 things to sort out before starting
2026-05-24T09:40:00Z	harness	took screenshots of the old version before changing anything	so we can compare old against new and catch any visual change	scripts/snapshot.sh, baseline/	saved 120 reference screenshots
2026-05-24T11:15:00Z	widget	moved the widget styles over without changing how it looks	keep the change small and the result identical	commit 7c21e0a, pixel-diff 0	looks identical, tests pass
2026-05-24T12:30:00Z	widget	threw out a helper's work because its screenshots were blank	checked the real files instead of trusting its summary	worktree reset	reverted, tightened the instructions for next time
```

（例子的意思，逐行：先统计了工作量，大约 100 个组件、75 小时左右，因为想在开始长时间运行前知道规模，结果发现开始前有 5 件事要理清；改动任何东西之前先给旧版本截图，以便对比新旧、抓出任何视觉变化，存了 120 张参考截图；把 widget 的样式迁移过去、外观不变，让改动小、结果一致，看起来完全一样、测试通过；因为一个助手的截图是空白的，丢掉了它的工作，检查的是真实文件而不是相信它的总结，已撤回，并为下次收紧了指示。）

## 记一行

每一条都写成你告诉队友自己做了什么的样子。平常的话，具体的动作，不要 AI 腔或抽象的行话（**unslop** skill 也适用于日志文字）。

用辅助脚本 `scripts/log.sh <logfile> <phase> <decision> <why> <evidence> <result>`。它是 bash，Windows 上用 Git Bash 或 WSL 跑，PowerShell 跑不了。它会盖上 `ts` 时间戳，第一次使用时写入表头，去掉多余的制表符/换行，并在任何以 `=`、`+`、`-` 或 `@` 开头的单元格前面加一个单引号（防止表格软件把它当公式）。直接用 `printf` 追加一行也可以，但如果单元格内容来自生成的或用户提供的文字，要注意同样这些字符。没有 bash 时，就按同样的列和清洗规则自己追加一行。

记录的是决定点和检查点，而不是每一个动作：选了哪条岔路、完成了一个单元及其验证结果、一次转向或撤回及其起因、发现的一个阻碍、修好的一个关卡。如果是循环运行，每次迭代一行。跳过那些琐碎和不言自明的。

一次运行（run）就是一次智能体对话，包括它后面的轮次和对它的任何总结。一次接手、一个替换上来的智能体或一个新的对话，都开始一次新的运行。当一次运行往一份已经有内容的日志里添加时，它的第一行的 phase 是 `start`；在另一次运行的 `start` 行之后，它的第一行也是 `start`。所以，一次运行在之后的某一轮回到一份日志时，要先读日志的最后几行，看看是不是有别的运行在这期间写过。`start` 行要写明它前面那些不是本次运行写的行的 `ts` 范围，它的 evidence 写明本次运行，比如它的智能体 id。phase `start` 不要用于别的用途。

## 放在哪里

默认情况下，日志是一份工作用的产物，不提交。把它放在工作目录里的 `decisions.tsv`，或者在同时进行好几项工作时放在 `.audit/<task-slug>.tsv`，并且不放进 git。

只有当工作足够有野心、审查者需要这条记录才能信任结果时，才提交它。

## 规则

- 只追加。一个错误的决定，用新的一行来取代它。永远不要编辑或删除历史。
- 优先用提交进代码库的脚本产生的证据，而不是手工做的一次性证据（见 **principle-encode-lessons-in-structure** 原则 skill）。

## 对照对话记录审查日志

在运行结束、交回之前，检查日志说的是不是实话。读当前工作区 `agent-transcripts/` 目录下本次运行的对话记录（系统提示词里写着路径）。不要对 `~/.cursor/projects/*/` 用通配符。那样会读到无关的私密对话。把本次运行写的各行和实际发生的事逐一对照。这些行分成若干段，每段从本次运行的一个 `start` 行开始（如果日志是本次运行创建的，就从第一行开始），到另一次运行的下一个 `start` 行结束：

- 检查每一行都对应一个真实的决定或动作。
- 检查每一行的证据都能找到，并且显示了这一行所声称的内容。
- 一个影响了工作、却没有记下来的岔路、转向或被放弃的做法，就是一个缺口。把它补上。

改正的是日志，而不是故事。审查永远不编辑或删除任何一行，哪怕是编造的一行。如果某一行记录的既不是真实的决定也不是真实的动作，或者它的说法或证据是错的，就加一行来取代它，写明实际发生了什么，并附上一个能找到的指针。这次审查不检查本次运行那几段之外的行。如果本次运行自己的工作表明其中某一行是错的，就像对待任何错误决定一样，加一行取代它。

## 用另一个模型审查这条记录

交回之前，派出一个子智能体，用和做这份工作的模型不同系列的模型。自我审查不能代替这一步。这个子智能体读审计记录和本次运行的对话记录，然后指出用户应该注意的地方。不是把工作重做一遍，而是扫一遍哪些地方不够好或有风险。按 **s-mode** skill 里 “Subagents” 一节的规定，为每个子智能体的任务选择推理等级，以及快速还是标准速度。

- 证据薄弱或缺失的已记录决定。
- 被跳过的验证步骤，或者在对话记录里找不到证明、却声称做过的验证步骤。
- 事后看来有风险的选择（过早的、范围蔓延的、掩盖症状的）。
- 用户随便扫一眼时会漏掉的缺口。

对于产生了记录的运行，每条回复都以一个“Attention”（注意）部分结尾。第一行单独写审查者的模型（`reviewed by <model>`），然后列出每一个标记，指向具体的行或时刻。“No flags”（没有标记）是一个有效的值。模型名不是。

## 在不同软件里怎么用

这个审查者要和做这份工作的模型不同系列。具体派法以 [s-mode](../s-mode/SKILL.md) 文末为准。

Cursor：一个 `Task`，`subagent_type: generalPurpose`，`readonly: true`，`model` 选和父级不同系列的名字。这次能用时，父级是 `grok-*` 就用 `claude-opus-5-5-xhigh`，父级是 `claude-*` 就用 `grok-4.7-xhigh-fast`。

OpenCode：`subagent` 派一个 `mode: subagent` 的智能体，`model` 用另一个系列。没有现成文件时用内置 `explore`，并说明继承了父级模型、这次没有换系列。不要在调用上传 `model`（工具页没有这个参数）。

Codex：提示词里点名另一个这次账号里真有的模型，或点名一个已经写好、模型不同的自定义智能体。`default_subagent_model` 拉不开系列。

WorkBuddy：能拉开差异时，父级是 `"lite"` 就用 `"reasoning"`，反过来也一样。Claude Code：父级是 `sonnet` 就用 `opus`，或换一个完整 ID。派不出子智能体时，在主对话里换一种角度再看一遍日志，并说一句没有换模型。

## 审阅这条记录

从上往下读，顺着证据指针去看，抽查。GitHub 会把提交进去的 TSV 显示成表格。在终端里用 `column -s$'\t' -t decisions.tsv` 也能显示成表格。

## 和别的 skill 组合

其他 skill 把它们的审计记录交给这里，而不是自己再发明一套。按名字引用它，让它来负责格式。不要重复写这些列。
