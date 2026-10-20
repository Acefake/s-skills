---
name: using-superpowers
description: "开始任何对话时，在作答、提出澄清问题、探索代码库或检查文件之前，先查找并调用相关技能。Use when starting any conversation - establishes how to find and use skills, requiring skill invocation before ANY response including clarifying questions."
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。

本技能译自 Jesse Vincent 的 Superpowers（MIT）。许可证见上一级文件夹的 `LICENSE-superpowers`。

<SUBAGENT-STOP>
如果你是被派来执行一项具体任务的子代理，忽略本技能。
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
只要你认为某项技能有哪怕 1% 的可能适用于你正在做的事，你就绝对必须调用该技能。

如果某项技能适用于你的任务，你没有选择余地。你必须使用它。

这一点没有商量余地。你不能靠给自己找理由来绕开。
</EXTREMELY-IMPORTANT>

## 规则

**在任何回应或行动之前，先调用相关或被要求使用的技能**——包括澄清问题、探索代码库或检查文件。如果事后发现它不适合当前情境，你可以不用它。

**进入计划模式之前：** 如果你还没有做过头脑风暴，先调用 brainstorming 技能。

然后宣布「正在使用 [skill] 来 [purpose]」，并严格按该技能执行。如果它有清单，为每一项建立一个待办。

## 技能优先级

多项技能同时适用时，流程技能优先——它们确定做法，然后由实现技能（frontend-design 等）去执行。Brainstorming 和 systematic-debugging 是 Superpowers 最常用的流程技能，但这条规则对任何流程技能都成立。

- 「我们来做 X」→ 先 superpowers:brainstorming，然后是实现技能。
- 「修这个 bug」→ 先 superpowers:systematic-debugging，然后是领域技能。

## 危险信号

这些念头意味着停下来——你正在给自己找理由：

| 念头 | 实际情况 |
|---------|---------|
| "这只是个简单问题" | 问题也是任务。检查技能。 |
| "我需要先了解更多上下文" | 技能检查在澄清问题之前。 |
| "让我先探索代码库" | 技能会告诉你如何探索。先检查。 |
| "我可以快速看一下 git/文件" | 文件缺少对话上下文。检查技能。 |
| "让我先收集信息" | 技能会告诉你如何收集信息。 |
| "这不需要正式技能" | 如果技能存在，就使用它。 |
| "我记得这个技能" | 技能会演进。阅读当前版本。 |
| "这不算一项任务" | 行动即任务。检查技能。 |
| "这个技能小题大做" | 简单的事会变复杂。使用它。 |
| "我先做这一件小事" | 做任何事之前先检查。 |
| "这样感觉很有进展" | 没有纪律的行动会浪费时间。技能防止这一点。 |
| "我知道那是什么意思" | 知道概念不等于使用技能。去调用它。 |

## 平台适配

如果你的运行环境出现在这里，阅读它的参考文件以获取特别说明：

- Codex: `references/codex-tools.md`
- Pi: `references/pi-tools.md`
- Antigravity: `references/antigravity-tools.md`

## 用户指示

用户指示（CLAUDE.md、AGENTS.md、GEMINI.md 等，以及直接提出的要求）优先于技能，技能再覆盖默认行为。只有当你的人类协作者明确告诉你时，才跳过技能的工作流或说明。
