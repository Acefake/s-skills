# s 技能：动手前先查技能

本文件放进全局指令文件后生效：Claude Code 是 `~/.claude/CLAUDE.md`，Codex 是 `~/.codex/AGENTS.md`，OpenCode 是 `~/.config/opencode/AGENTS.md`，Cursor 放进一条 Always 规则，Hermes 追加到 `~/.hermes/SOUL.md`。也可以放进项目根目录的 `AGENTS.md`。

收到任务后，在读文件、跑命令、提问或作答之前：

1. 对照可用技能列表，找出和这件事沾边的技能。只要有一点可能相关，就先加载它。
2. 读完代码自己就能答，不是跳过技能的理由。技能管的是做法和质量底线，不只是答案。
3. 一件事常常对应几个技能，按下表都加载：

| 任务 | 先加载 |
| --- | --- |
| 新功能、加接口、改行为 | `brainstorming`，定下设计后 `writing-plans` |
| bug、报错、按钮没反应、结果不对 | `systematic-debugging` |
| 界面卡顿、掉帧、滚动慢、INP 高 | `impeccable`（optimize） |
| 界面设计、样式、交互 | `impeccable` |
| 补测试、测什么 | `test-strategy`；写实现时 `tdd` |
| 端到端测试、Playwright、偶发失败 | `e2e-testing` |
| 写或改代码、整理目录 | `code-style` |

加载技能后按它的步骤做；用户的直接要求优先于技能。
