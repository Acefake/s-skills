---
name: principle-explain-the-number
description: "「这个数字靠谱吗」「加速比哪来的」「别直接信这个延迟」。相信、报告或按测量数字行动前，先找出限制因素。Use when you are about to trust, report, or act on a measured number."
disable-model-invocation: false
---

本会话首次使用本库技能时，按[全局提示词自检](../setup-s-instructions/references/daily-check.md)只读检查一次。
## 运行环境适配

涉及宿主工具、模型配置或子代理时，按需阅读[宿主适配](../../HOSTS.md)。


# 解释这个数字

- **问一句“为什么不是两倍？”** 说出限制这个结果的资源或代码路径，比如一个 CPU 核、一把锁、磁盘、网络，或者负载生成器本身。要从运行期间采集的性能剖析（profile）或系统计数器里得到它，再对应到源代码。读代码猜出来的不算限制因素。如果你说不出为什么这个数字没有好一倍，你就不知道自己测的是什么。
- **列出这个数字还可能在测别的什么，并用证据逐一排除。** 常见的嫌疑有：出错、被跳过或被缓存的工作、根本没运行的代码、没调优的一方（用的是默认设置）、噪声，以及一个小到对端到端结果没影响的部分。
- **让证据和数字放在一起。** 把运行次数、波动范围和限制因素写进笔记或一个链接到的产物里。

如果是性能数字，用 [benchmark-checklist](../benchmark-checklist/SKILL.md)（benchmark-checklist）这个 skill 走完整套流程。如果是评估结果，对每次试验问同样的问题：每次运行都完成任务了吗？差距在多次试验和不同模型之间都成立吗？这个场景重要吗？

出现下面这些情况，就说明你跳过了这一步：数字背后的证据没有运行次数、没有波动范围、没有指出限制因素；或者省下的时间比被改动的那部分原本花的时间还多。

和 [Prove It Works](../principle-prove-it-works/SKILL.md)（证明它真的能用）不同：那一条检查的是输出是不是真的。
