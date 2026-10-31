---
name: why
description: "「为什么是这样」「我们为什么选了这个」「这个阈值哪来的」。查设计理由和取舍，带引用。运行时怎么走用 how。Use when you need the reason a design, choice, regression, or threshold is the way it is."
disable-model-invocation: true
---

本会话首次使用本库技能时，按[全局提示词自检](../setup-s-instructions/references/daily-check.md)只读检查一次。
## 运行环境适配

涉及宿主工具、模型配置或子代理时，按需阅读[宿主适配](../../HOSTS.md)。


# 为什么（Why）

调查代码背后的动机和意图。与它配套的 `how` skill 回答代码做了什么、是怎么工作的。`why` 回答是哪些力量让它变成了现在这个形状。

下面每一次派出，都对应 s 模型配置里的一个角色行。路径见文末。把模型设成那一行的值。没有这一行，调查用较快的写代码模型，综合用判断力最强的模型。值是 `auto` 或 `inherit-parent`，或者软件不能指定模型，就不设。软件拒绝了某个名字，就换同一系列里它接受的最接近的名字，并说一句。按 **s-mode** skill 里 “子智能体” 一节的规定，为每个子智能体的任务选择推理等级，以及快速还是标准速度。行值带括号时（如 `sonnet（medium）`），按[行值格式](../setup-s-models/references/role-keys.md)拆开：括号前是模型，括号里的档位当起始推理等级传给宿主，不要把括号连模型名一起传。

每次派出的都是能写文件的通用类型，不要用会去掉 MCP 的只读模式。调查者和综合者要靠 MCP 核对引用。调查者仍然不应该写任何东西。Cursor 的 `grok-4.7-xhigh-fast` 和 `claude-opus-5-5-xhigh` 只在 Cursor 上、并且这次确实可用时才当作默认。

## 工作姿态

以一个**细心、谨慎、精确的调查者**的姿态工作。对你知道的和你推断的，要诚实地区分。完整的可信度框架和措辞指南见 `references/epistemics.md`。综合者必须遵守它。

## 第 1 步：弄懂目标和问题

**目标**通常是一段代码、一种写法、一个功能，或者一个有名字的设计决定。**问题**通常是一个设计理由、一个取舍、一个促成它的边界情况、一个外部约束、死代码，或者一次大范围的历史梳理。

如果目标很模糊（“我们为什么这么做？”却没有明确的所指），就根据对话的上下文（打开的文件、最近的修改、光标位置、刚刚讨论的内容）做出你最好的猜测。简短地说出你的理解，让用户在你理解错时可以纠正，然后继续。

## 第 2 步：确立代码锚点

在派出调查者之前，先直接建立种子上下文：文件路径和行范围、关键符号（函数、类、常量）、最近几次涉及目标的提交、合并提交里的 PR 编号（标题行里 `(#1234)` 这样的格式），以及任何链接的工单 ID。运行 `git blame -L <start>,<end> <file>` 查最后一次修改的提交，`git log --follow -p -- <file>` 查包含补丁、跨越重命名的完整历史，`git log --oneline -20 -- <file>` 查能看到 PR 编号的最近提交，`git log -1 --format=%B <commit>` 提取 PR 编号。然后，对任何有实质内容的提交，拉取 PR 的正文和讨论：`gh pr view <number> --json title,body,author,createdAt,mergedAt,labels,closingIssuesReferences,comments,reviews`。这个锚点要发给每个调查者和综合者。

## 第 3 步：派出并行的调查者

**默认做完整的并行调查。** 目标是一份完整的覆盖地图，而不是最小的那一份。没找到也要记录下来，不要跳过搜索。

### 发现可用来源

在派出调查者之前，从 Cursor 环境里列出可用的 MCP。如果有可用工具的映射表，就用它。否则就查看 Cursor 提供的 `mcps/` 目录，看看启用了哪些 MCP 服务器。

把每个可用的 MCP 对应到一类证据：

1. 版本控制历史
2. 问题 / 工单跟踪系统
3. 长篇文档
4. 实时团队聊天
5. 基础设施可观测性
6. 错误 / 异常跟踪
7. 产品分析数据仓库

版本控制总是可以通过 git 和 `gh` 使用。对其他六类，根据 MCP 的名字、服务器说明、工具名和资源描述来分类。如果一个 MCP 可能属于不止一类，就选和它的主要证据相符的那一类。把有歧义的情况记录在覆盖地图里。

每个有对应 MCP 的类别派一个调查者，全部放在一条消息里，让它们并发运行，每个调查者只负责一个工具或 MCP。不要让一个智能体负责多个 MCP。模型用「为什么的调查者」那一行，没有再读旧键 `why investigators`。没有这一行，或软件不能指定模型，就按开头的规则省略或换一个更快的写代码模型。

每个调查者的提示词，是填好的 `references/investigator-prompt.md`，再加上：
- 所选 MCP 对应类别的操作手册 `references/sources/<source>.md`，根据 `references/source-playbook.md` 里的例子改写
- **如果目标代码看起来是防御性的**（空值检查、重试逻辑、超时处理、限流、功能开关、出站流量防护、内存溢出处理），加上 `references/sources/incident-postmortem.md`
- 代码锚点和用户原来的问题

### 调查者名单，每个可用的证据类别一个

下面每一类，都特别擅长找出某一种形状的“为什么”，写在“最擅长”后面。用它来知道该期待什么样的返回结果；当某一类返回空时，说出缺口；只有在极少数可以证明无关的情况下，才用它来说明为什么跳过。

1. **版本控制**（git 历史、用 `gh` 查 PR、代码注释、测试）。总是要派，这是唯一有保证的来源。最擅长*在审查时记录下来的、实现时的理由*。
2. **问题 / 工单跟踪系统**（例如 Linear、Jira、GitHub Issues、Plane、Shortcut 的 MCP）。最擅长*产品或业务上的推动力*。当“为什么”来自工程之外时最有用。
3. **长篇文档**（例如 Notion、Confluence、Google Docs、Coda 的 MCP）。最擅长*长篇的设计理由*，也就是在变成代码之前就写出来的那些。
4. **实时团队聊天**（例如 Slack、Discord、Microsoft Teams、Mattermost 的 MCP）。最擅长*从来没写进文档的实时讨论*。当版本控制、工单和文档留下的记录很少时尤其重要。
5. **基础设施可观测性**（例如 Datadog、New Relic、Honeycomb、Grafana、Splunk 的 MCP）。最擅长*促成这段代码的基础设施和运行时的实际情况*。当目标是在响应某个基础设施信号时最有用（超时、重试、限流、熔断）。
6. **错误 / 异常跟踪**（例如 Sentry、Rollbar、Bugsnag、Airbrake 的 MCP）。最擅长*促成防御性或纠正性代码的那些具体异常和错误的来龙去脉*。对 catch 块、空值防护、类型检查、重试和其他防御最有用。
7. **产品分析数据仓库**（例如 Databricks、Snowflake、BigQuery、ClickHouse、dbt、Redshift 的 MCP）。最擅长*塑造了这段代码的产品和数据的实际情况*。对受功能开关控制的代码、由实验驱动的上线、数据迁移，以及“这个数字是从哪来的”这类问题最有用。

### 什么时候可以跳过一个调查者

只有在有**明确的、写下来的理由**时才可以，而且这个理由要写进最后的 Sources Consulted（查阅过的来源）。有两种有效的理由：

- **在这个环境里，这个类别没有可用的 MCP。** 把它标为一个缺口，而不是一个选择：“Real-time team chat skipped. No matching MCP available, so the conversational record was not searchable.”（跳过了实时团队聊天。没有对应的 MCP，所以聊天记录无法搜索。）
- **这个来源可以被证明是无关的**，而不只是“可能无关”。门槛很高：“Error / exception tracking skipped. Target is a build-time script with no runtime code path.”（跳过了错误 / 异常跟踪。目标是一个构建时的脚本，没有运行时的代码路径。）

如果你对范围的评估表明，目标是只涉及一个提交的简单情况，PR 说明里已经有完整的答案，那么**只有在**确认了全部七类可用来源的搜索都是多余的之后，你才可以直接回答。要明确地这么说。这种情况应该很少见。

## 第 4 步：综合

派出一个综合者。模型用「为什么的综合者」那一行，没有再读旧键 `why synthesizer`。没有这一行，或软件不能指定模型，就按开头的规则省略或换一个更强的模型。它会拿到：
1. 调查者的发现，包括所有没找到结果的情况，以及所有附了理由而跳过的类别
2. 代码锚点
3. 用户原来的问题
4. `references/epistemics.md` 里的认知可信度框架
5. `references/synthesizer-prompt.md` 里的综合者提示词模板

## 第 5 步：呈现

把综合者的输出呈现给用户。为了清楚，你可以做些轻微的修改，或者从对话里补充一点上下文，但**不要改写表示可信度的措辞**。

## 输出格式

结构就是 `references/synthesizer-prompt.md` 里的那个：The Question（问题）、The Code in Question（相关代码）、What We Found（我们发现了什么）、What We Can Reasonably Infer（我们可以合理推断什么）、Competing Hypotheses（相互竞争的假设）、What We Don't Know（我们不知道什么）、Sources Consulted（查阅过的来源）、Confidence Summary（可信度总结）。可以按需要调整，但要保持“可信度分开表述”这一点不变，并且 Sources Consulted 要每个调查者一行，包括那些什么都没找到或被跳过的，并写明原因。

在 Sources Consulted 之后，如果用户问 `why` 是为了接下来要修改这段代码，就把这些来龙去脉的发现，转换成一组 Preserve（要保留）/ Change（要改）/ Avoid（要避免）/ Risk（风险）约束，用于规划这次修改。

## 要避免的常见失败模式

- **近因偏差**。以为最近的那次提交就是权威。现在的形状，常常是许多更早的决定一层层累积起来的。要往前追溯。

## 宿主适配

调查读「为什么的调查者」（旧键 `why investigators`），综合读「为什么的综合者」（旧键 `why synthesizer`）。中文键优先。配置路径以 [setup-s-models](../setup-s-models/SKILL.md) 为准。调查者要能用 MCP，提示词里仍然禁止它写文件。

Codex、Claude Code、Cursor、WorkBuddy 的工具和配置见[宿主适配](../../HOSTS.md)；按当前宿主读取对应参考。

### 派不出子智能体

在主对话里按来源一类一类查，并说一句没有换模型。
