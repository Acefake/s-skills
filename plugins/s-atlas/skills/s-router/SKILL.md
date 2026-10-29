---
name: s-router
description: "「开始任何对话」「先查技能」「该用哪个」「拿不准」。在作答、提问、探索代码库或读文件之前，先查找并调用相关技能。Use when starting any conversation - establishes how to find and use skills, requiring skill invocation before ANY response including clarifying questions."
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
| 1 | 上述小改动 | 类型检查或lint一次，改动文件已有测试一次；不新写测试 |
| 2 | 修bug、加功能、改行为 | 有便宜测试点走tdd，修前修后各一次，再跑所在模块 |
| 3 | 跨模块、改接口或依赖、迁移；提交或合并前 | 全量测试一次 |

- 同一份代码已验证就引用结果，后续审查、提交或分支收尾不重跑；失败后修正才重跑。
- e2e、完整构建或预计超过一分钟的命令，只有第3档或用户要求才跑。
- 收尾说明跑了什么和结果；没跑说明档位。

## 任务路由

| 任务 | 技能 |
|---|---|
| 新功能、改行为 | brainstorming，再领域实现技能；小改动按快路 |
| bug、报错、结果不对、bug-fix、fix bug | systematic-debugging，再领域技能 |
| Word、幻灯片、表格、PDF | docx、pptx、xlsx、pdf |
| README、技术文档、RFC | technical-writing |
| 中英翻译 | translate |
| 专利挖掘、交底书、查新 | patent-disclosure |
| 专利申请、权利要求、说明书、附图 | patent-application |
| 提交说明、提交、PR | commit-pr；集成方式未定用finishing-a-development-branch |
| 审PR、分支、本地改动 | s-review，只读报告，含位置与P0/P1/P2 |
| 架构图、流程图、时序图、数据流图、ER图、类图、讲解页 | archify；架构重构评审用refactor-architecture |
| 教我、解释代码怎么工作 | 点名how时加载；未点名时直接讲解，不自动加载显式技能 |

## 共用执行规则

- 项目任务按需回读已确认经验；收到纠正、重复错误或验证过的重要结论时，按 [learn](../learn/SKILL.md) 先提出建议，逐条确认后才保存。没有经验或没有新教训时安静继续，子代理不重复执行。

- 所有代码修改交付前按 [code-style](../code-style/SKILL.md)「交付前自审」检查完整任务差异和关键调用方，简述发现及未解决风险。测试和清理不替代自审；按 code-style「交付前独立评审」派只读 subagent，按风险确定范围，不因改动小而省略。

- 任务路由不覆盖调用政策。标有 `disable-model-invocation: true` 的技能仅在用户点名或已授权工作流明确派发时使用。
- 代码独立评审委派已由全局规则授权；这不改变实现者执行方式，不自动启用子代理开发。
- 提交、推送、rebase、发布与清理按已有任务授权执行；写设计、计划或完成验证本身不授权这些操作。提交步骤统一按[commit-pr](../commit-pr/SKILL.md)。
- 测试强度按验证分档；TDD 是否适用按[tdd](../tdd/SKILL.md)。只读方案不执行测试，不新增测试文件。
- 主任务可在当前或接续会话用[executing-plans](../executing-plans/SKILL.md)执行。用户要求或已授权工作流明确采用子代理时，才用[subagent-driven-development](../subagent-driven-development/SKILL.md)，不因工具可用而自动切换。

## 平台参考与用户指示

派子代理、建工作树或收尾分支时，只读当前平台参考：[Codex](references/codex-tools.md)、[Claude Code](references/claude-code-tools.md)、[Cursor](references/cursor-tools.md)。

用户的指令文件和直接要求优先于技能，技能优先于默认行为。只有用户明确要求时才跳过技能工作流或说明。
