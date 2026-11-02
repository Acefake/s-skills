---
name: s-init
description: "「/s-init」「初始化 s」「新机器配置 s」「一键配置 s」。按顺序完成当前宿主的全局技能提示词和模型配置，每步写入前都要用户确认。Use when the user explicitly asks to set up s-atlas on a host in one go: global skill instructions first, then model configuration."
disable-model-invocation: true
---
本会话首次使用本库技能时，按[全局提示词自检](../setup-s-instructions/references/daily-check.md)只读检查一次。
## 运行环境适配

涉及宿主工具、模型配置或子代理时，按需阅读[宿主适配](../../HOSTS.md)。

# 一键初始化 s

只在用户明确调用本技能或要求一次配好 s 时运行。它只负责顺序和汇总，具体做法都在两个现有技能里，不在这里重复。

## 1. 识别宿主

按 [setup-s-instructions](../setup-s-instructions/SKILL.md) 第 1 节识别 Codex、Claude Code、Cursor 或 WorkBuddy；无法确定才询问。只处理当前宿主。

## 2. 检查全局提示词

用 [global_instructions.py](../setup-s-instructions/scripts/global_instructions.py) 对当前宿主做只读检查，不带 `--apply`，以返回的 `status` 为准。退出码 2 是检查结果，不是失败。

## 3. 按状态处理提示词

- `configured`：说明已是最新，不写入，进入第 4 步。
- `missing` 或 `outdated`：说明将改的位置和备份方式，用户明确同意后，按 setup-s-instructions 第 2 节加 `--apply` 写入，再检查一次，预期 `configured`。
- Cursor 返回 `user_rules_verification_required`（退出码 3）：按 setup-s-instructions 的 Cursor 分支处理，以回读真实 User Rules 为准；没有编辑能力就交付 block 并标记“尚未配置”，不算完成。
- 用户拒绝或跳过：记下“提示词未配置”，询问是否仍继续配置模型；用户同意才进入第 4 步，否则停下并汇总。

## 4. 配置模型

加载 [setup-s-models](../setup-s-models/SKILL.md)，沿用第 1 节识别的宿主，从它的“一次一问”开始（它的宿主确认步骤照走），原样执行，包括第 3 步展示完整 18 行、第 4 步确认后才写入。不在这里替它预选预算或模型。

## 5. 汇总

分别跑 setup-s-instructions 的只读检查和 setup-s-models 的 `check`，报告：

- 宿主与当前插件版本。
- 提示词：状态、位置、是否修改、备份位置。
- 模型：配置文件路径、预算、是否通过 `check`。
- 未完成项，以及提示“新会话才会加载全局规则和模型配置”。

## 失败与中断

任一步失败、被拒绝或被跳过，就停下报告哪一项已完成、哪一项未完成；只有用户明确同意才继续后面的步骤，不静默继续，也不回滚已完成的步骤。不提交或公开用户的全局配置内容。
