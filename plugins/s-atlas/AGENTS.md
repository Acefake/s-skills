# s-atlas 技能：动手前先查技能

本文件放进全局指令文件后生效：Claude Code 是 `~/.claude/CLAUDE.md`，Codex 是 `~/.codex/AGENTS.md`，OpenCode 是 `~/.config/opencode/AGENTS.md`，Cursor 放进一条 Always 规则，Hermes 追加到 `~/.hermes/SOUL.md`。也可以放进项目根目录的 `AGENTS.md`。

收到任务后，在读文件、跑命令、提问或作答之前：

0. 只改文案、注释、文档措辞、样式数值、配置值，或用户说不用测：不跑测试，看一眼 diff 就交付。对口的技能照常加载（比如翻译用 `translate`），没有对口的就直接改。

1. 下表或技能描述能直接对上，就直接加载那个技能；对不上、拿不准或要跨模块，才加载 `s-router`。
2. 对照可用技能列表，加载对口的技能：任务落在它描述写的场景里。只是沾边的不加载。
3. 读完代码自己就能答，不是跳过技能的理由。技能管的是做法和质量底线，不只是答案。
4. 一件事可能对应几个技能，按下表加载：

| 任务 | 先加载 |
| --- | --- |
| 新功能、加接口、改行为 | `brainstorming`，定下设计后 `writing-plans` |
| bug、报错、按钮没反应、结果不对、修 bug、bug-fix、fix bug | `systematic-debugging` |
| 写 README、写文档、RFC、PR 说明的句子 | `technical-writing`（Word 用 `docx`） |
| Word、docx、修订、批注 | `docx` |
| 幻灯片、pptx | `pptx` |
| 表格、xlsx、公式 | `xlsx` |
| PDF | `pdf` |
| 专利交底书、专利挖掘、查新 | `patent-disclosure` |
| 发明专利申请文件、权利要求书、说明书、专利附图 | `patent-application` |
| 提交、开 PR | `commit-pr`（还没决定怎么集成用 `finishing-a-development-branch`） |
| 审 PR、审分支、审本地改动、代码审查 | `s-review` |
| 中英翻译 | `translate` |
| 画架构图、流程图、时序图、ER 图 | `archify` |
| 教我、这块代码怎么工作 | `how` |
| 界面卡顿、掉帧、滚动慢、INP 高 | `impeccable`（optimize） |
| 界面设计、样式、交互 | `impeccable` |
| 补测试、测什么 | `test-strategy`；写实现时 `tdd` |
| 端到端测试、Playwright、偶发失败 | `e2e-testing` |
| 写或改代码、整理目录 | `code-style` |
| 跨模块、大迁移、要并行 | 建议用户点名 `s-mode` |

小改动（意图明确、只动一两个文件、不改对外接口、数据结构或依赖；拿不准就不算）不走 brainstorming 和计划，直接做；提交前过一遍 `deslop`。测试按改动分档（细则见 `s-router`「验证分档」）：小改动跑一次 lint 或类型检查加已有测试，修 bug 和加功能跑所在模块，跨模块或提交前才跑全量；跑过且没改的不重跑。

加载技能后按它的步骤做；用户的直接要求优先于技能。
