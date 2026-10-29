---
name: principle-laziness-protocol
description: "「能删就删」「最小改动」「别加这一层」。重构或评估改动时，留能解决问题的最小改动。Use when refactoring, judging a diff, or about to add an abstraction, a layer, or pass-through signals."
disable-model-invocation: false
---

本会话首次使用本库技能时，按[全局提示词自检](../setup-s-instructions/references/daily-check.md)只读检查一次。
# 偷懒守则

- **把决定合并到一处。** 不要在好几个地方重复同一个选择。把它放在唯一的事实来源后面，再把结果当作一个简单的开关传下去。
- **让 diff 尽量小。** 做能解决问题的最小改动。行数少，胜过“优雅”的样板代码。
