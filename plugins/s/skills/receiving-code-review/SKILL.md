---
name: receiving-code-review
description: "收到代码评审反馈、落实建议之前，尤其当反馈含糊或在技术上可疑时；需要技术严谨与核验，而不是表演式认同或盲目落实。Use when you received code review feedback, before applying it, especially when the feedback is vague or technically suspicious."
---
本技能译自 Jesse Vincent 的 Superpowers（MIT）。许可证见 [LICENSE-superpowers](../../LICENSE-superpowers)。

# 接收代码评审

## 概述

代码评审需要的是技术评估，不是情绪表演。

**核心原则：** 落实之前先核验。假设之前先询问。技术正确优先于社交舒适。

## 回应模式

```
WHEN receiving code review feedback:

1. READ: Complete feedback without reacting
2. UNDERSTAND: Restate requirement in own words (or ask)
3. VERIFY: Check against codebase reality
4. EVALUATE: Technically sound for THIS codebase?
5. RESPOND: Technical acknowledgment or reasoned pushback
6. IMPLEMENT: One item at a time, test each
```

## 禁止的回应

**绝不：**
- 「你完全正确！」（明确违反指令文件）
- 「说得好！」/「反馈太棒了！」（表演式）
- 「我现在就去实现」（核验之前）

**改为：**
- 重述技术要求
- 提出澄清问题
- 如果错了，用技术理由提出异议
- 直接开始做（行动大于言辞）

## 处理含糊反馈

```
IF any item is unclear:
  STOP - do not implement anything yet
  ASK for clarification on unclear items

WHY: Items may be related. Partial understanding = wrong implementation.
```

**示例：**
```
your human partner: "Fix 1-6"
You understand 1,2,3,6. Unclear on 4,5.

❌ WRONG: Implement 1,2,3,6 now, ask about 4,5 later
✅ RIGHT: "I understand items 1,2,3,6. Need clarification on 4 and 5 before proceeding."
```

## 按来源分别处理

### 来自你的人类伙伴
- **可信** - 理解之后再落实
- **范围不清时仍然要问**
- **不要表演式认同**
- **直接行动**，或做技术上的确认

### 来自外部评审者
```
BEFORE implementing:
  1. Check: Technically correct for THIS codebase?
  2. Check: Breaks existing functionality?
  3. Check: Reason for current implementation?
  4. Check: Works on all platforms/versions?
  5. Check: Does reviewer understand full context?

IF suggestion seems wrong:
  Push back with technical reasoning

IF can't easily verify:
  Say so: "I can't verify this without [X]. Should I [investigate/ask/proceed]?"

IF conflicts with your human partner's prior decisions:
  Stop and discuss with your human partner first
```

**你的人类伙伴的规则：**「外部反馈——保持怀疑，但仔细核对」

## 对「专业」功能做 YAGNI 检查

```
IF reviewer suggests "implementing properly":
  grep codebase for actual usage

  IF unused: "This endpoint isn't called. Remove it (YAGNI)?"
  IF used: Then implement properly
```

**你的人类伙伴的规则：**「你和评审者都向我汇报。如果不需要这个功能，就不要加。」

## 落实顺序

```
FOR multi-item feedback:
  1. Clarify anything unclear FIRST
  2. Then implement in this order:
     - Blocking issues (breaks, security)
     - Simple fixes (typos, imports)
     - Complex fixes (refactoring, logic)
  3. Test each fix individually
  4. Verify no regressions
```

## 何时提出异议

在以下情况提出异议：
- 建议会破坏现有功能
- 评审者缺少完整上下文
- 违反 YAGNI（未使用的功能）
- 对这个技术栈在技术上不正确
- 存在遗留或兼容性原因
- 与你的人类伙伴先前的架构决策冲突

**如何提出异议：**
- 用技术理由，不用防御姿态
- 提出具体问题
- 引用能工作的测试或代码
- 若涉及架构，让你的人类伙伴参与

**如果你不舒服当众提出异议：** 点明这种不安，然后把你看到的问题告诉伙伴。对方会欣赏你的坦诚。

## 确认正确的反馈

当反馈确实正确时：
```
✅ "Fixed. [Brief description of what changed]"
✅ "Good catch - [specific issue]. Fixed in [location]."
✅ [Just fix it and show in the code]

❌ "You're absolutely right!"
❌ "Great point!"
❌ "Thanks for catching that!"
❌ "Thanks for [anything]"
❌ ANY gratitude expression
```

**为什么不道谢：** 行动会说话。直接修。代码本身表明你听到了反馈。

**如果你发现自己正要写「Thanks」：** 删掉它。改为陈述修复。

## 得体地纠正自己的异议

如果你提出了异议，但你是错的：
```
✅ "You were right - I checked [X] and it does [Y]. Implementing now."
✅ "Verified this and you're correct. My initial understanding was wrong because [reason]. Fixing."

❌ Long apology
❌ Defending why you pushed back
❌ Over-explaining
```

事实性地陈述纠正，然后继续。

## 常见错误

| 错误 | 修正 |
|---------|-----|
| 表演式认同 | 陈述要求，或直接行动 |
| 盲目落实 | 先对照代码库核验 |
| 未测试就成批修改 | 一次一项，逐项测试 |
| 假定评审者是对的 | 检查是否会弄坏现有行为 |
| 回避异议 | 技术正确 > 舒适 |
| 部分落实 | 先澄清全部条目 |
| 无法核验仍继续 | 说明限制，询问方向 |

## 真实示例

**表演式认同（差）：**
```
Reviewer: "Remove legacy code"
❌ "You're absolutely right! Let me remove that..."
```

**技术核验（好）：**
```
Reviewer: "Remove legacy code"
✅ "Checking... build target is 10.15+, this API needs 13+. Need legacy for backward compat. Current impl has wrong bundle ID - fix it or drop pre-13 support?"
```

**YAGNI（好）：**
```
Reviewer: "Implement proper metrics tracking with database, date filters, CSV export"
✅ "Grepped codebase - nothing calls this endpoint. Remove it (YAGNI)? Or is there usage I'm missing?"
```

**含糊条目（好）：**
```
your human partner: "Fix items 1-6"
You understand 1,2,3,6. Unclear on 4,5.
✅ "Understand 1,2,3,6. Need clarification on 4 and 5 before implementing."
```

## GitHub 线程回复

在 GitHub 上回复行内评审评论时，在评论线程中回复（`gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies`），不要作为顶层 PR 评论。

## 底线

**外部反馈 = 待评估的建议，不是必须服从的命令。**

核验。提问。然后落实。

不要表演式认同。始终保持技术严谨。
