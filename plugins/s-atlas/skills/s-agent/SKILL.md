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

没有路径时，在做任何别的事之前，先找一份路径以 `skills/s-mode/SKILL.md` 结尾的文件。找到不止一份时，用旁边插件清单里 `version` 最高的那份。技能目录里看不到它，并不等于这份插件不在。一份都没有，就停下来告诉父对话。

用到哪条原则，就去读那条 `principle-*` skill。写代码时按 `code-style`，写测试时按 `test-strategy`，碰交互界面时守 `impeccable` 的 optimize 预算；父对话只会点名，不会转述内容。

每次新任务派一个新的 s-agent。只有 s-mode “子智能体” 一节写明的那几种情况，才恢复一个已经在跑的。用通用类型代替本文件，会跳过这次全文阅读，然后慢慢跑偏。

## 宿主适配


Codex、Claude Code、Cursor、WorkBuddy 的工具和配置见[宿主适配](../../HOSTS.md)；按当前宿主读取对应参考。
