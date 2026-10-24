---
name: principle-guard-the-context-window
description: "「上下文要满了」「输出太长」「交给子智能体」。大段输出、长文件和计划只在主线程留摘要。Use when a large output, file, or plan would fill the context window."
disable-model-invocation: false
---
# 守住上下文窗口

**为什么：** 上下文溢出会降低推理质量，产生压缩带来的失真，还会让进度停下来。

**做法：**
- **控制每个阶段的大小，限制范围。** 限制每个阶段涉及的文件数，设定轮次预算，把机制本身的开销也算进去。
