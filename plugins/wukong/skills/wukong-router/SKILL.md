---
name: wukong-router
description: "「先查技能」「该用哪个」「拿不准」。没有加载全局技能规则，或拿不准该用哪个技能、任务跨模块时，在作答、提问或读文件之前先用它查找并调用相关技能。Use when no global skill rules are loaded, or when it is unclear which skill fits or the task spans modules, before answering or exploring."
---

本会话首次使用本库技能时，按[全局提示词自检](../setup-s-instructions/references/daily-check.md)只读检查一次。
## 运行环境适配

涉及宿主工具、模型配置或子代理时，按需阅读[宿主适配](../../HOSTS.md)。

<SUBAGENT-STOP>
被派来执行具体任务的子代理忽略本技能。
</SUBAGENT-STOP>

## 先选技能，再定验证强度

在回应、提问、探索或读文件前，先检查可用技能。用户点名或任务直接落在描述范围内，就读取并使用；只是沾边的不加载。通常 1–3 个技能足够，不因任务简单、记得内容或已经能回答而跳过。

使用时说明技能和目的，有清单就建立待办。读后确认不适合当前情境时可以不用。

流程技能先确定做法，再加载领域能力。进入计划模式前先用 brainstorming；小改动不进计划模式。第0档仍加载对口技能，只跳过测试。

## 小改动快路

同时满足：意图明确、只动一两个文件、不改对外接口、数据结构或依赖。拿不准就不算。

- 跳过 brainstorming、writing-plans和设计审批。
- 只加载对口技能：bug用systematic-debugging，有便宜测试点时用tdd；代码用code-style，界面用impeccable。
- 代码交付前按 code-style 自审；不提交和不跑测试也不跳过。提交前过deslop，验证按下表。
- 做着发现范围超过上述条件，转回完整流程。

## 验证分档

先按改动定档；明确符合第0档时优先按第0档，即使涉及多份文档、提交或收尾也不自动升级。其他改动拿不准取高一档。各技能要求验证时，强度统一按这里：

| 档 | 适用 | 验证 |
|---|---|---|
| 0 | 文案、注释、文档措辞、样式数值、配置值；只读讲解、审查、方案；用户说不用测 | 不跑测试。改了内容就看diff |
| 1 | 小改动：只动一两个文件、不改对外接口、数据结构或依赖，含这种范围的修bug | 类型检查或lint一次，改动文件已有测试一次；不强制先写失败测试 |
| 2 | 其他修bug、加功能、改行为 | 有便宜测试点走tdd，修前修后各一次，再跑所在模块 |
| 3 | 跨模块、改接口或依赖、迁移；提交或合并前 | 全量测试一次 |

- 同一份代码已验证就引用结果，后续审查、提交或分支收尾不重跑；失败后修正才重跑。
- e2e、完整构建或预计超过一分钟的命令，只有第3档或用户要求才跑。
- 收尾说明跑了什么和结果；没跑说明档位。

## 任务路由

| 任务 | 技能 |
|---|---|
| 新功能、改行为 | brainstorming，再领域实现技能；小改动按快路 |
| bug、报错、结果不对、bug-fix、fix bug | systematic-debugging，再领域技能 |
| Word、幻灯片、表格、PDF、README、技术文档、RFC | 显式技能：用户点名 docx、pptx、xlsx、pdf、technical-writing 时加载；未点名直接做 |
| 提交说明、提交、PR | commit-pr；集成方式未定用finishing-a-development-branch |
| 审PR、分支、本地改动 | wukong-review，只读报告，含位置与P0/P1/P2 |
| 架构图、流程图、时序图、数据流图、ER图、类图、讲解页 | 点名archify时加载（显式技能）；架构重构评审建议用户点名refactor-architecture（显式技能） |
| 教我、解释代码怎么工作 | 点名how时加载；未点名时直接讲解，不自动加载显式技能 |
| 优化提示词，或对话无法补足且会影响结果的需求关键缺口 | prompt-sharpen，加载后先研究，必要时才提问；不以已读代码为加载前提。bug 由 systematic-debugging、新功能设计由 brainstorming 主导，不重复澄清 |
| 建项目档案、同步项目记录、更新架构或规范文档 | project-memory |

## 只读检索派发

- 主代理直接查：单文件、一次 `rg`、约十个文件以内，或查完马上要改这些文件、问题还模糊、要判断业务语义和架构动机的情况。
- 已授权派发：预计要读大量文件或日志（约十个文件以上）、只要结论不要原文、且问题明确、范围清楚。拆成互不重叠的独立问题，默认并发 2 个「检索与探索」子代理，只有 3 条真正独立的边界才派 3 个；有依赖时分轮派，只派一轮，不够由主代理补查。模型按 s 模型配置该行选，没有该行沿用原工作流角色。
- 每个任务写明问题、文件范围、只读限制，要求返回约 30 行内的结论、文件行号和未确认项；不传父会话历史。结论是线索不是证据，「没找到」要由主代理补查关键路径后再采信。
- 只授权只读检索，不授权子代理改文件、测试、提交或其他外部操作；实现类子代理仍需用户要求或已授权的工作流。同一名额的首选与次选不同时启动。用户禁止委派或宿主不可用时，主代理顺序自查并说明。

## 共用执行规则

- 所有代码修改交付前按 [code-style](../code-style/SKILL.md)「交付前自审」自审（第0、1档只看 diff），简述发现及未解决风险。只有第3档或高风险改动才按 code-style「交付前独立评审」派只读 subagent。

- 任务路由不覆盖调用政策。标有 `disable-model-invocation: true` 的技能仅在用户点名或已授权工作流明确派发时使用。
- 代码独立评审委派已由全局规则授权；这不改变实现者执行方式，不自动启用子代理开发。
- 提交、推送、rebase、发布与清理按已有任务授权执行；写设计、计划或完成验证本身不授权这些操作。提交步骤统一按[commit-pr](../commit-pr/SKILL.md)。
- 测试强度按验证分档；TDD 是否适用按[tdd](../tdd/SKILL.md)。只读方案不执行测试，不新增测试文件。
- 主任务可在当前或接续会话用[executing-plans](../executing-plans/SKILL.md)执行。用户要求或已授权工作流明确采用子代理时，才用[subagent-driven-development](../subagent-driven-development/SKILL.md)，不因工具可用而自动切换。

## 平台参考与用户指示

在 T3 Code 编排环境中，涉及模型、委派或工作区时加读 [T3 Code 编排参考](references/t3-code-tools.md)，再读取底层宿主参考。显式 T3 目标失败不自动降级。

派子代理、建工作树或收尾分支时，只读当前平台参考：[Codex](references/codex-tools.md)、[Claude Code](references/claude-code-tools.md)、[Cursor](references/cursor-tools.md)、[WorkBuddy](references/workbuddy-tools.md)、[DeepSeek Harness](references/dsh-tools.md)、[Hermes](references/hermes-tools.md)。

用户的指令文件和直接要求优先于技能，技能优先于默认行为。只有用户明确要求时才跳过技能工作流或说明。
