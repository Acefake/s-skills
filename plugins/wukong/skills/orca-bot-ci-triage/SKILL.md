---
name: orca-bot-ci-triage
description: "「建个 Orca bot 盯 CI」「Orca 里加个看失败检查的 bot」。调用 Orca 提议一个开发 bot：分清偶发失败和真失败，解释每个挂掉的检查。Use when the user wants an Orca bot that triages failing CI checks."
---

本会话首次使用本库技能时，按[全局提示词自检](../setup-s-instructions/references/daily-check.md)只读检查一次。

# 创建 CI 失败分诊 bot

用 Orca 自带的 `ci-failures` 模板，换上中文设定。检查失败时，它解释失败原因，判断是偶发失败还是真失败，并维护一份偶发失败清单。用户同意后才去修。

## 设定

| 项 | 值 |
| --- | --- |
| 模板 | `ci-failures`（界面里叫 CI failures） |
| name | `ci-triage` |
| purpose | 检查挂了就说清原因，分开偶发失败和真失败，并维护偶发失败清单。 |
| watches | 我选的仓库里的检查运行 |
| does | 读失败日志，找出第一条真正的错误，判断偶发还是真失败并给出依据；我同意后再派 worker 修 |
| reports | 在这个聊天里，检查失败时，以及每周一上午 9 点的偶发失败清单 |
| 连接 | GitHub |
| 模板自带 | 检查失败时触发、每周一汇总的自动化，Orca 的 `ci-failure-triage` 技能 |
| bot 技能 | [assets/bot-skill.md](assets/bot-skill.md) 放到 `skills/wukong-ci-triage/SKILL.md` |

## 步骤

1. 按 [Orca bot 创建流程](../../ORCA-BOTS.md) 用上面的设定提议并创建。
2. 检查失败的事件要 Orca 连上 GitHub 才能收到。bot 说收不到事件时，让用户在 bot 聊天里运行 `orca bot connectors` 看缺哪一项。

## 不做

- 不替 bot 重跑检查或修 CI。
- 不改 Orca 模板、`ci-failure-triage` 或 Orca 写的文件。
