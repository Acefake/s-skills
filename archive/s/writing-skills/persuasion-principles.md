本技能译自 Jesse Vincent 的 Superpowers（MIT）。许可证见上一级文件夹的 `LICENSE-superpowers`。

# 技能设计的说服原则

## 概述

LLM 会对人类所用的同一套说服原则作出反应。理解这套心理，有助于你设计更有效的技能——不是为了操纵，而是为了确保关键实践即便在压力下也会被遵守。

**研究基础：** Meincke 等人（2025）用 N=28,000 段 AI 对话检验了 7 条说服原则。说服技巧把遵从率提高了一倍多（33% → 72%，p < .001）。

## 七条原则

### 1. 权威
**它是什么：** 对专业知识、资历或官方来源的遵从。

**它在技能里如何起作用：**
- 命令式语言："YOU MUST"、"Never"、"Always"
- 不可协商的框架：「没有例外」
- 消除决策疲劳和合理化借口

**何时使用：**
- 强制纪律的技能（TDD、验证要求）
- 安全关键实践
- 已经确立的最佳实践

**示例：**
```markdown
✅ Write code before test? Delete it. Start over. No exceptions.
❌ Consider writing tests first when feasible.
```

### 2. 承诺
**它是什么：** 与先前的行动、陈述或公开声明保持一致。

**它在技能里如何起作用：**
- 要求宣布：「宣布正在使用某技能」
- 迫使做出明确选择：「选 A、B 或 C」
- 使用跟踪：用待办清单做检查清单

**何时使用：**
- 确保技能真的被遵守
- 多步骤流程
- 问责机制

**示例：**
```markdown
✅ When you find a skill, you MUST announce: "I'm using [Skill Name]"
❌ Consider letting your partner know which skill you're using.
```

### 3. 稀缺
**它是什么：** 由时间限制或有限可得性带来的紧迫感。

**它在技能里如何起作用：**
- 有时限的要求：「在继续之前」
- 顺序依赖：「在 X 之后立刻」
- 防止拖延

**何时使用：**
- 立即验证的要求
- 对时间敏感的工作流
- 防止「我以后再做」

**示例：**
```markdown
✅ After completing a task, IMMEDIATELY request code review before proceeding.
❌ You can review code when convenient.
```

### 4. 社会证明
**它是什么：** 顺从别人在做的事，或顺从被视为正常的事。

**它在技能里如何起作用：**
- 普遍模式：「每一次」、「总是」
- 失败模式：「有 X 没有 Y = 失败」
- 建立规范

**何时使用：**
- 记录普遍实践
- 警告常见失败
- 强化标准

**示例：**
```markdown
✅ Checklists without todo tracking = steps get skipped. Every time.
❌ Some people find a todo list helpful for checklists.
```

### 5. 团结
**它是什么：** 共享身份、「我们感」、内群体归属。

**它在技能里如何起作用：**
- 协作语言：「我们的代码库」、「我们是同事」
- 共享目标：「我们都想要质量」

**何时使用：**
- 协作工作流
- 建立团队文化
- 非等级式的实践

**示例：**
```markdown
✅ We're colleagues working together. I need your honest technical judgment.
❌ You should probably tell me if I'm wrong.
```

### 6. 互惠
**它是什么：** 回报已接受好处的义务。

**它如何起作用：**
- 少用——可能让人觉得被操纵
- 技能里很少需要

**何时避免：**
- 几乎总是避免（其他原则更有效）

### 7. 喜好
**它是什么：** 更愿意与自己喜欢的人合作。

**它如何起作用：**
- **不要把它用于换取遵从**
- 与诚实反馈的文化冲突
- 会造成迎合

**何时避免：**
- 在强制纪律时始终避免

## 按技能类型组合原则

| 技能类型 | 使用 | 避免 |
|------------|-----|-------|
| 强制纪律 | 权威 + 承诺 + 社会证明 | 喜好、互惠 |
| 指导/技巧 | 适度权威 + 团结 | 过重的权威 |
| 协作 | 团结 + 承诺 | 权威、喜好 |
| 参考 | 只求清楚 | 全部说服手段 |

## 为什么这有效：心理机制

**清晰界线减少合理化：**
- "YOU MUST" 消除决策疲劳
- 绝对化语言消除「这算例外吗？」的问题
- 明确的反合理化针对性地堵上具体漏洞

**实施意图制造自动行为：**
- 清楚的触发 + 必须的行动 = 自动执行
- 「当 X 时，做 Y」比「一般来说做 Y」更有效
- 降低遵从时的认知负荷

**LLM 是类人的：**
- 训练文本是含有这些模式的人类文本
- 训练数据里，权威语言出现在遵从之前
- 承诺序列（陈述 → 行动）被频繁建模
- 社会证明模式（大家都做 X）建立规范

## 合乎伦理的使用

**正当：**
- 确保关键实践被遵守
- 写出有效的文档
- 防止可预见的失败

**不正当：**
- 为个人利益而操纵
- 制造虚假紧迫感
- 用内疚来换取遵从

**检验标准：** 如果用户完全理解这套技巧，它是否仍服务于用户的真实利益？

## 研究引用

**Cialdini, R. B. (2021).** *Influence: The Psychology of Persuasion (New and Expanded).* Harper Business.
- 说服的七条原则
- 影响力研究的实证基础

**Meincke, L., Shapiro, D., Duckworth, A. L., Mollick, E., Mollick, L., & Cialdini, R. (2025).** Call Me A Jerk: Persuading AI to Comply with Objectionable Requests. University of Pennsylvania.
- 用 N=28,000 段 LLM 对话检验了 7 条原则
- 使用说服技巧后，遵从率从 33% 升到 72%
- 权威、承诺、稀缺最有效
- 验证了 LLM 行为的类人模型

## 速查

设计技能时，问自己：

1. **它是什么类型？**（纪律、指导，还是参考）
2. **我想改变什么行为？**
3. **哪些原则适用？**（纪律类通常是权威 + 承诺）
4. **我是不是组合得太多？**（不要七条全用）
5. **这合乎伦理吗？**（服务于用户的真实利益吗？）
