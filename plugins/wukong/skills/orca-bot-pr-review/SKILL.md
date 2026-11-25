---
name: orca-bot-pr-review
description: "「建个 Orca bot 帮我审 PR」「Orca 里加个 PR 审查 bot」。调用 Orca 提议一个开发 bot：盯等你审的 PR，按风险列问题，附文件和行号。Use when the user wants an Orca bot that reviews pull requests."
---

本会话首次使用本库技能时，按[全局提示词自检](../setup-s-instructions/references/daily-check.md)只读检查一次。

# 创建 PR 审查 bot

用 Orca 自带的 `pr-review` 模板，换上中文设定。有人请你审 PR 时，它在 Orca 里给出审查结论。用户同意之前，它不在 GitHub 上留言。

## 设定

| 项 | 值 |
| --- | --- |
| 模板 | `pr-review`（界面里叫 Pull request review） |
| name | `pr-reviewer` |
| purpose | 审查等我 review 的 PR，按风险列出问题和缺的测试，每条附文件和行号。 |
| watches | 我选的仓库里等我 review 的 PR |
| does | 先写一句改动意图，再按严重、一般、建议列问题，附证据和文件行号，最后给能不能合并 |
| reports | 在这个聊天里，有人请我 review 时 |
| 连接 | GitHub |
| 模板自带 | 被请求 review 时触发的自动化，Orca 的 `pr-review-checklist` 技能 |
| bot 技能 | [assets/bot-skill.md](assets/bot-skill.md) 放到 `skills/wukong-pr-review/SKILL.md` |

## 步骤

1. 按 [Orca bot 创建流程](../../ORCA-BOTS.md) 用上面的设定提议并创建。
2. bot 第一次问要盯哪些仓库时，让用户自己回答。
3. 提醒用户：bot 要在 GitHub 上发评论，得在它的聊天里明确同意。

## 不做

- 不替 bot 审 PR，也不替它连 GitHub。
- 不改 Orca 模板、`pr-review-checklist` 或 Orca 写的文件。
