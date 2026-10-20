---
name: principle-attack-the-premise
description: "Use when two or more fixes that share a premise fail the same check. 中文触发：当两个或更多基于同一个前提的修复都没能通过同一道检查时使用。先把这个前提写下来并直接验证它，再去写下一个默认它成立的修复。"
disable-model-invocation: false
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。


# 质疑前提

当两个或更多基于同一个前提的修复，都没能通过同一道检查（gate）时，要怀疑的是前提，而不是这些修复。

**为什么：** 每一个失败的修复，都是反对它所假设的那个看法的证据。在同一个前提上再做第三次修复，就是把力气花在证据已经表明不是原因的地方。

**做法：**
- **把前提写下来。** 前提就是每个失败的修复都默认成立的那一句话。
- **在下一个修复之前先验证前提。** 找一个“如果前提是错的，结果就会不一样”的观察，然后去做这个观察。不光看失败有多严重，也要看失败是怎么分布的。按照 [Build the Lever](../principle-build-the-lever/SKILL.md)（打造杠杆），让这个检查可以重复运行。
- **跟着证据走。** 如果证据和前提矛盾，原因就在别处。去找这些失败有哪些共同点是前提没有预料到的。如果证据证实了前提，就按 [Fix Root Causes](../principle-fix-root-causes/SKILL.md)（修根本原因）再问下一个“为什么”。之前的修复可能处理的是一个后果，而不是原因。
- **消除条件，而不是补偿它**，按照 [Laziness Protocol](../principle-laziness-protocol/SKILL.md)（偷懒守则）。如果证据表明某一部分总是落在吃亏的一边，就改掉把它放到那里的东西。一个事后收拾残局的机制，会把原因留在原地，还让每次运行都多做一份工作。

**停：** 在前提被写下来并验证之前，不要开始下一个修复。

这条原则和 [Redesign from First Principles](../principle-redesign-from-first-principles/SKILL.md)（从第一性原理重新设计）不同：那一条是围绕一个新需求重建设计；这一条是质疑当前设计所默认的某个事实。
