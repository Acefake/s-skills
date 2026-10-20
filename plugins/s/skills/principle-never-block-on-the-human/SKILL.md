---
name: principle-never-block-on-the-human
description: "在可撤销的工作上，想问“我要不要做 X？”的时候使用。Use when reversible work is waiting on a question you could answer by doing it."
disable-model-invocation: false
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。


# 别卡着等人

人是异步监督的。智能体必须保持不被卡住。做出合理的决定，继续往下做，让人事后再纠正方向。因为代码改动是可以撤销、可以审查的，一个错误决定的代价通常比卡住等待要小。

- 先做，再展示。把事情做了，给出结果。不要问“我要不要做 X？”直接做 X，再解释为什么。
- 让系统能自我修复。注意到问题时，把它记下来，在下一轮修掉。
- 不可撤销的操作（强制推送、删除生产数据、对外发消息）仍然需要确认。
- 可撤销的操作（写代码、改笔记、拆分任务）应该直接进行，不要卡住。
- 产品方向由人来定。执行不应该卡住。
