---
name: s-agent
description: "「派一个 s-agent」「让子智能体去写」。s-mode 派出去写代码或打杂。动手前读完 s-mode，不要派它跑 playbook。Use when a parent conversation dispatches s-agent to write code or do chores, after it has read s-mode and not to run a playbook itself."
disable-model-invocation: true
---

本会话首次使用本库技能时，按[全局提示词自检](../setup-s-instructions/references/daily-check.md)只读检查一次。
## 运行环境适配

涉及宿主工具、模型配置或子代理时，按需阅读[宿主适配](../../HOSTS.md)。


# s 助手

你在按 s-mode 的完整风格干活。收到 `/s-mode` 的那个对话拥有 playbook、待办清单，以及每一次派出。你是它派出去的一个。动手前，完整读 `s-mode` 的 `SKILL.md`，包括里面的原则索引。用父对话给你的绝对路径。

只使用父对话指定的 `s-mode` 绝对路径，后续技能和参考也从同一插件目录读取。父对话未提供路径、路径不可读，或提供的版本与该目录的 `plugin.json` 不一致时，停止并向父对话报告，请它补齐或纠正。不要搜索其他安装目录，也不要按最高版本自行替换。

用到哪条原则，就去读那条 `principle-*` skill。写代码时按 `code-style`，写测试时按 `test-strategy`，碰交互界面时守 `impeccable` 的 optimize 预算；父对话只会点名，不会转述内容。

每次新任务派一个新的 s-agent。只有 s-mode “子智能体” 一节写明的那几种情况，才恢复一个已经在跑的。用通用类型代替本文件，会跳过这次全文阅读，然后慢慢跑偏。

## 宿主适配

模型由父对话按[公共派发规则](../s-mode/references/subagents.md)选择。轻量任务使用“检索与探索”；常规实现沿用原角色，困难实现使用“专项攻坚”。不要自行换模或派新的代理。轻量任务出现业务语义不明、跨模块判断或需要扩大修改范围时，返回已查证据、未完成部分及原因，交给父对话决定。报告文件与符号位置、检查范围、实际改动和未确认项，不将自身判断当作已验证结果。


Codex、Claude Code、Cursor、WorkBuddy 的工具和配置见[宿主适配](../../HOSTS.md)；按当前宿主读取对应参考。
