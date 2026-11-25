---
name: orca-bot-deps
description: "「建个 Orca bot 管依赖升级」「Orca 里加个查漏洞依赖的 bot」。调用 Orca 提议一个开发 bot：每周列出过期和有漏洞的依赖，同意后分组升级。Use when the user wants an Orca bot that tracks outdated or vulnerable dependencies."
---

本会话首次使用本库技能时，按[全局提示词自检](../setup-s-instructions/references/daily-check.md)只读检查一次。

# 创建依赖升级 bot

用 Orca 自带的 `dependency-updates` 模板，换上中文设定。每周一它列出新的安全公告和大版本更新，最急的排在前面。用户同意后，每组升级开一个 PR。

## 设定

| 项 | 值 |
| --- | --- |
| 模板 | `dependency-updates`（界面里叫 Dependency updates） |
| name | `dep-updater` |
| purpose | 每周列出过期和有漏洞的依赖，最急的在前，我同意后每组开一个 PR 升级。 |
| watches | 我选的仓库里的依赖 |
| does | 列出安全公告和过期依赖并分组，写明破坏性变更；我同意后每组派 worker 升级、跑测试、开 PR |
| reports | 在这个聊天里，每周一上午 9 点 |
| 连接 | GitHub |
| 模板自带 | 每周一上午 9 点的检查，Orca 的 `dependency-upgrade` 技能 |
| bot 技能 | [assets/bot-skill.md](assets/bot-skill.md) 放到 `skills/wukong-deps/SKILL.md` |

## 步骤

1. 按 [Orca bot 创建流程](../../ORCA-BOTS.md) 用上面的设定提议并创建。
2. 仓库用 pnpm、Go modules 或 Maven 这类非 npm 工具时，让用户在 bot 第一次运行时说明，bot 会记进自己的记忆。

## 不做

- 不替 bot 升级依赖或开 PR。
- 不改 Orca 模板、`dependency-upgrade` 或 Orca 写的文件。
