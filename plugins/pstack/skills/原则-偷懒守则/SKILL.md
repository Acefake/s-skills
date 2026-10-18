---
name: 原则-偷懒守则
description: "在重构、评估改动大小，或者想加抽象、加层、层层传递信号时使用。倾向于删除，倾向于能解决问题的最小改动。"
disable-model-invocation: true
---

> 翻译自 pstack 插件（编号 9717366）的 `principle-laziness-protocol` skill，原作者 Lauren Tan（版权 © 2026 Lauren Tan），许可证 MIT（全文见上一级文件夹的 `LICENSE-pstack`），仅供自用。插件版本 0.15.25，原项目：https://github.com/cursor/plugins/tree/main/pstack 。
> 说明：`disable-model-invocation: true` 表示这个 skill 只能由用户主动调用，AI 不会自己调用它。原文正文就只有下面这些，照原样翻译。
> 英文名备份：s-principle-laziness-protocol

# 偷懒守则

- **把决定合并到一处。** 不要在好几个地方重复同一个选择。把它放在唯一的事实来源后面，再把结果当作一个简单的开关传下去。
- **让 diff 尽量小。** 做能解决问题的最小改动。行数少，胜过“优雅”的样板代码。
