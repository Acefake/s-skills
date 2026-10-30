---
name: timed-loop
description: "「/timed-loop」「/loop」「每隔一阵看 CI」「通宵盯到过」。按通过或失败条件反复醒来。一段时长不算完成。Use when work should wake repeatedly until a pass/fail condition is met or it is truly stuck."
disable-model-invocation: true
---

本会话首次使用本库技能时，按[全局提示词自检](../setup-s-instructions/references/daily-check.md)只读检查一次。
## 运行环境适配

涉及宿主工具、模型配置或子代理时，按需阅读[宿主适配](../../HOSTS.md)。


# 定时循环

把同一件检查反复做，直到完成条件成立，或者真的卡住并写明原因。完成条件必须是每次都能跑的检查（测试通过、CI 绿、diff 为零、旧调用方为零）。“再做四小时”不是完成条件。

调用时带上三样：要重复的提示词或 skill、完成条件、间隔。间隔可以是固定的，例如 `1h`；也可以不写，让执行者自己判断何时再看。不写间隔时，仍然要有完成条件。

卡住的出口：试过几轮、证据说明再试同一种做法不会变，就停下来写明为什么，不要改写目标。

## 宿主适配


Codex、Claude Code、Cursor、WorkBuddy 的工具和配置见[宿主适配](../../HOSTS.md)；按当前宿主读取对应参考。
