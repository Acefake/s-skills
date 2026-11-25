---
name: orca-bot-bug-hunt
description: "「建个 Orca bot 帮我查 bug」「Orca 里加个排查 bug 的 bot」。调用 Orca 提议一个开发 bot：拿到 bug 报告先复现，再找根因，同意后才修。Use when the user wants an Orca bot that reproduces bugs and finds their root cause."
---

本会话首次使用本库技能时，按[全局提示词自检](../setup-s-instructions/references/daily-check.md)只读检查一次。

# 创建 Bug 排查 bot

用 Orca 自带的 `bug-investigation` 模板，换上中文设定。给它一个 bug 报告或 issue 链接，它在新工作区里派 worker 复现，报告复现步骤和根因。用户同意后才开始修。

## 设定

| 项 | 值 |
| --- | --- |
| 模板 | `bug-investigation`（界面里叫 Bug investigation） |
| name | `bug-hunter` |
| purpose | 复现我交给它的 bug，找到第一次出错的地方，我同意后再修。 |
| watches | 我交给它的 bug 报告，以及指派给我的 Linear issue |
| does | 在新工作区里写出复现步骤，用证据定位根因，提出修法；修之前先等我同意 |
| reports | 在这个聊天里，有复现和根因时 |
| 连接 | GitHub；用 Linear 时再连 Linear |
| 模板自带 | Linear issue 指派给你时触发的自动化，Orca 的 `bug-reproduction` 技能 |
| bot 技能 | [assets/bot-skill.md](assets/bot-skill.md) 放到 `skills/wukong-bug-hunt/SKILL.md` |

## 步骤

1. 按 [Orca bot 创建流程](../../ORCA-BOTS.md) 用上面的设定提议并创建。
2. 用户不用 Linear 时，告诉用户：bot 弹出 Linear 的 Connect 卡片可以不点，模板自带的指派自动化不会触发，不影响手动交 bug。

## 不做

- 不替 bot 复现或修 bug。
- 不改 Orca 模板、`bug-reproduction` 或 Orca 写的文件。
