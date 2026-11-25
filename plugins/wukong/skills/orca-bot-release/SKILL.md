---
name: orca-bot-release
description: "「建个 Orca bot 盯发版」「Orca 里加个发版检查的 bot」。调用 Orca 提议一个开发 bot：每个工作日早上列出挡住下次发版的检查、PR 和阻塞项。Use when the user wants an Orca bot that tracks release readiness."
---

本会话首次使用本库技能时，按[全局提示词自检](../setup-s-instructions/references/daily-check.md)只读检查一次。

# 创建发版检查 bot

用 Orca 自带的 `release` 模板，换上中文设定。每个工作日早上，它列一份很短的发版清单：失败的检查、还在等审查的 PR、没解决的阻塞项。它只看和报告，不打 tag，也不发版。

## 设定

| 项 | 值 |
| --- | --- |
| 模板 | `release`（界面里叫 Release readiness） |
| name | `release-guard` |
| purpose | 每个工作日早上告诉我下次发版还被什么挡着。 |
| watches | 我选的仓库里的 PR、检查和工作区 |
| does | 列出失败的检查、等审查的 PR、未解决的阻塞项，每项附链接和负责人；全部清空时说一句能发 |
| reports | 在这个聊天里，工作日上午 9 点 |
| 连接 | GitHub |
| 模板自带 | 工作日上午 9 点的清单，Orca 的 `release-readiness` 技能 |
| bot 技能 | [assets/bot-skill.md](assets/bot-skill.md) 放到 `skills/wukong-release/SKILL.md` |

## 步骤

1. 按 [Orca bot 创建流程](../../ORCA-BOTS.md) 用上面的设定提议并创建。
2. bot 第一次运行时，让用户说明发版分支和用来标记阻塞的标签或里程碑，bot 会记进自己的记忆。

## 不做

- 不替 bot 打 tag、写发版说明或发版。
- 不改 Orca 模板、`release-readiness` 或 Orca 写的文件。
