---
name: 原则-守住上下文
description: "当上下文快要满了时使用：大量输出、很长的文件、反复读取、规划分派任务。把大块内容交给子智能体处理；主线程里只保留摘要，不要原始数据。"
disable-model-invocation: true
---

> 翻译自 pstack 插件（编号 9717366）的 `principle-guard-the-context-window` skill，原作者 Lauren Tan（版权 © 2026 Lauren Tan），许可证 MIT（全文见上一级文件夹的 `LICENSE-pstack`），仅供自用。插件版本 0.15.25，原项目：https://github.com/cursor/plugins/tree/main/pstack 。
> 说明：`disable-model-invocation: true` 表示这个 skill 只能由用户主动调用，AI 不会自己调用它。上下文窗口（context window）就是 AI 一次能“记住”的内容容量。原文正文就只有下面这些，照原样翻译。
> 英文名备份：s-principle-guard-the-context-window

# 守住上下文窗口

**为什么：** 上下文溢出会降低推理质量，产生压缩带来的失真，还会让进度停下来。

**做法：**
- **控制每个阶段的大小，限制范围。** 限制每个阶段涉及的文件数，设定轮次预算，把机制本身的开销也算进去。
