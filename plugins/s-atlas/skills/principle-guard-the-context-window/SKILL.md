---
name: principle-guard-the-context-window
description: "当上下文快要满了时使用：大量输出、很长的文件、反复读取、规划分派任务。把大块内容交给子智能体处理；主线程里只保留摘要，不要原始数据。Use when a large output, file, or plan would fill the context window."
disable-model-invocation: false
---
# 守住上下文窗口

**为什么：** 上下文溢出会降低推理质量，产生压缩带来的失真，还会让进度停下来。

**做法：**
- **控制每个阶段的大小，限制范围。** 限制每个阶段涉及的文件数，设定轮次预算，把机制本身的开销也算进去。
