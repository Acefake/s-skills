---
name: timed-loop
description: "中文：按一个能判定通过或失败的条件，反复醒来检查，直到完成或真的卡住。用于 /timed-loop、/loop、通宵运行、每隔一段时间看 CI 或 PR。一段时长不算完成条件。Use when work should wake repeatedly until a pass/fail condition is met or it is truly stuck."
disable-model-invocation: true
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。


# 定时循环

把同一件检查反复做，直到完成条件成立，或者真的卡住并写明原因。完成条件必须是每次都能跑的检查（测试通过、CI 绿、diff 为零、旧调用方为零）。“再做四小时”不是完成条件。

调用时带上三样：要重复的提示词或 skill、完成条件、间隔。间隔可以是固定的，例如 `1h`；也可以不写，让执行者自己判断何时再看。不写间隔时，仍然要有完成条件。

卡住的出口：试过几轮、证据说明再试同一种做法不会变，就停下来写明为什么，不要改写目标。

## 在不同软件里怎么用

### Cursor

用 Cursor 内置的 `/loop`。它的原文没有公开。公开文档写的是：`/loop` 按给定间隔反复运行一条提示词或一个 skill；不写固定间隔时，由智能体决定何时醒来；想停就停。可以和 `/goal` 一起用。来源：[Agent Skills](https://cursor.com/docs/skills)、[Agent 概览](https://cursor.com/docs/agent/overview)。

斜杠菜单里有 `/loop` 时，把这次的提示词和间隔交给它，例如 `/loop 1h` 配上检查提示，或 `/loop until <完成条件>`。动态模式是不写死间隔、让它自己决定何时醒来。内置命令负责叫醒主对话。本技能不另做一套计时器。

菜单里没有 `/loop` 时，按下面 OpenCode 一节做，并说明这次没有用到内置命令。

### OpenCode

OpenCode 没有文档化的、能按时叫醒主对话的 `/loop`。派一个后台子智能体盯着完成条件（`subagent`，`background: true`），或者你自己过一会儿再跑同一条检查。回复里写明用的是哪一种。不要假装主对话会被按时叫醒。

### Codex

Codex 的子智能体文档没有按时叫醒主对话的命令。在提示词里写明完成条件和“做完这一轮就停，由父对话再决定要不要再派”。需要守着时，用一个子智能体反复跑检查，父对话等它返回再决定。CLI 的 `/subagents` 用来看线程，不是计时器。

### WorkBuddy 和 Claude Code

两处都没有核对到和 Cursor `/loop` 等价的内置命令。用一个后台盯梢的子智能体，或自己过一会儿再跑同一条检查，并写明用了哪一种。
