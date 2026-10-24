---
name: principle-redesign-from-first-principles
description: "「新需求按第一性原理重做」「别补在旧形状上」。把新需求整合进已有设计时，重做这一层。Use when a new requirement should be redesigned from first principles instead of patched onto the old shape."
disable-model-invocation: false
---
# 从第一性原理重新设计

整合一个改动时，不要把它硬接到现有设计上。要重新设计，就好像这个需求从一开始就是一个基础假设一样。

- 读完所有受影响的文件，弄懂当前的设计
- 问自己：“如果带着这个新需求从零开始写，我们会做出什么？”
- 把这个改动贯彻到每一处引用：类型、文档、示例、设计理由部分
- 先想清楚整个重新设计，再一步一步交付

这是在把改动整合进已有设计时，保住选择余地的方法。
