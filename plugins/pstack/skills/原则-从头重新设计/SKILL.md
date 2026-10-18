---
name: 原则-从头重新设计
description: "在把一个新需求整合进已有设计时使用。"
disable-model-invocation: true
---

> 翻译自 pstack 插件（编号 9717366）的 `principle-redesign-from-first-principles` skill，原作者 Lauren Tan（版权 © 2026 Lauren Tan），许可证 MIT（全文见上一级文件夹的 `LICENSE-pstack`），仅供自用。插件版本 0.15.25，原项目：https://github.com/cursor/plugins/tree/main/pstack 。
> 说明：`disable-model-invocation: true` 表示这个 skill 只能由用户主动调用，AI 不会自己调用它。
> 英文名备份：s-principle-redesign-from-first-principles

# 从第一性原理重新设计

整合一个改动时，不要把它硬接到现有设计上。要重新设计，就好像这个需求从一开始就是一个基础假设一样。

- 读完所有受影响的文件，弄懂当前的设计
- 问自己：“如果带着这个新需求从零开始写，我们会做出什么？”
- 把这个改动贯彻到每一处引用：类型、文档、示例、设计理由部分
- 先想清楚整个重新设计，再一步一步交付

这是在把改动整合进已有设计时，保住选择余地的方法。
