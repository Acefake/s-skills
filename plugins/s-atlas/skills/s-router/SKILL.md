---
name: s-router
description: "「开始任何对话」「先查技能」「该用哪个」「拿不准」。在作答、提问、探索代码库或读文件之前，先查找并调用相关技能。Use when starting any conversation - establishes how to find and use skills, requiring skill invocation before ANY response including clarifying questions."
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。

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

**进入计划模式之前：** 如果你还没有做过头脑风暴，先调用 brainstorming 技能。小改动不进计划模式。

然后宣布「正在使用 [skill] 来 [purpose]」，并严格按该技能执行。如果它有清单，为每一项建立一个待办。

## 小改动走快路

同时满足下面三条就是小改动：意图明确，只动一两个文件，不改对外接口、数据结构或依赖。拿不准就不算。

小改动：
- 不走 brainstorming 和 writing-plans，不等设计审批，直接做。
- 只加载对口的能力技能：bug 用 systematic-debugging（有便宜的测试点就 tdd），写代码用 code-style，界面用 impeccable。
- 提交前过一遍 deslop，交付前按 principle-prove-it-works 实际跑一遍（测试、命令或页面），把结果说出来。

做着做着发现不止一两个文件，或要改接口，就停下来改走下面的流程。

## 技能优先级

多项技能同时适用时，流程技能优先——它们确定做法，然后由实现技能（frontend-design 等）去执行。Brainstorming 和 systematic-debugging 是最常用的流程技能，但这条规则对任何流程技能都成立。

- 「我们来做 X」→ 先 brainstorming，然后是实现技能（小改动见上一节）。
- 「修这个 bug」→ 先 systematic-debugging，然后是领域技能。修 bug、报错、bug-fix、fix bug 都走它。
- 写或改 Word、幻灯片、表格、PDF → `docx`、`pptx`、`xlsx`、`pdf`。README、写文档、RFC 用 `technical-writing`。中英翻译用 `translate`。
- 写提交说明或开 PR → `commit-pr`。还没决定分支怎么集成时用 `finishing-a-development-branch`。
- 审 PR、分支、diff 或本地改动 → `s-review`。默认只出报告。每条发现带文件:行和 P0/P1/P2。
- 画架构图、流程图、时序图、数据流图、ER 图、类图，或把回答做成一页 → `archify`。架构重构评审仍用 `refactor-architecture`。
- 教我、讲讲这块代码怎么工作 → `how`。已删除的 teach 不要加载。

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
