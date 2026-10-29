---
name: principle-outcome-oriented-execution
description: "「直接改到目标结构」「别搞过渡兼容」。有阶段边界的重写和迁移，直接走向目标架构。Use when a planned rewrite or migration should move directly to the target structure."
disable-model-invocation: false
---

本会话首次使用本库技能时，按[全局提示词自检](../setup-s-instructions/references/daily-check.md)只读检查一次。
# 以结果为导向地执行

优化的目标是预期中、可验证的最终状态，而不是维持平稳的中间状态。

**为什么：** 让每个中间步骤都完全稳定，常常会产生临时的兼容代码，而这些代码最后会变成长期的技术债。直接向目标架构收敛，并在明确的验证边界上证明正确性。

**核心规则：**
- 最终状态的完整性优先于过渡期的稳定
- 只要是计划好的、范围明确的、可以撤销的，中间出现破坏是可以接受的

**护栏：**
- 这条只用于有明确阶段边界的计划内重写和迁移
- 事先说明在哪里可以接受临时破坏
- 迁移过程中，对正在改动的区域保留高信号的检查
- 计划完成时，要求完整的静态检查和运行时验证
