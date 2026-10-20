---
name: verification-before-completion
description: "准备声称工作已完成、已修复或已通过时，以及提交或创建 PR 之前；必须先运行验证命令并核对输出，再做任何成功声称。Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before making any success claims; evidence before assertions always."
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。

本技能译自 Jesse Vincent 的 Superpowers（MIT）。许可证见上一级文件夹的 `LICENSE-superpowers`。

# 完成之前先验证

## 概述

没有验证就声称工作完成，是不诚实，不是效率。

**核心原则：** 先有证据，再下结论，始终如此。

**违反这条规则的字面要求，就是违反它的精神。**

## 铁律

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

如果这条消息里你没有运行验证命令，你就不能声称它通过了。

## 门禁函数

```
BEFORE claiming any status or expressing satisfaction:

1. IDENTIFY: What command proves this claim?
2. RUN: Execute the FULL command (fresh, complete)
3. READ: Full output, check exit code, count failures
4. VERIFY: Does output confirm the claim?
   - If NO: State actual status with evidence
   - If YES: State claim WITH evidence
5. ONLY THEN: Make the claim

Skip any step = lying, not verifying
```

## 常见失败

| 声称 | 需要 | 并不充分 |
|-------|----------|----------------|
| 测试通过 | 测试命令输出：0 个失败 | 上一次运行、"应该能过" |
| linter 干净 | linter 输出：0 个错误 | 部分检查、外推 |
| 构建成功 | 构建命令：退出码 0 | linter 通过、日志看起来不错 |
| 缺陷已修复 | 针对原始症状的测试：通过 | 代码改过了、假定已经修好 |
| 回归测试有效 | 红-绿循环已经核实 | 测试通过了一次 |
| 代理已完成 | VCS diff 显示了变更 | 代理报告 "success" |
| 需求已满足 | 逐行清单 | 测试通过 |

## 危险信号——停下

- 使用「应该」「大概」「看起来」
- 在验证之前表达满意（「太好了！」「完美！」「做完了！」等）
- 准备在没有验证的情况下提交、推送或创建 PR
- 相信代理的成功报告
- 依赖部分验证
- 想着「就这一次」
- 累了，想把活对付完
- **任何在没有运行验证的情况下暗示成功的措辞**

## 防止合理化

| 借口 | 实际情况 |
|--------|---------|
| "现在应该能工作了" | 去运行验证 |
| "我有信心" | 信心不等于证据 |
| "就这一次" | 没有例外 |
| "linter 通过了" | linter 不等于编译器 |
| "代理说成功了" | 独立核实 |
| "我累了" | 疲惫不是借口 |
| "部分检查就够了" | 部分检查什么也证明不了 |
| "换了个说法，所以规则不适用" | 精神重于字面 |

## 关键模式

**测试：**
```
✅ [Run test command] [See: 34/34 pass] "All tests pass"
❌ "Should pass now" / "Looks correct"
```

**回归测试（TDD 红-绿）：**
```
✅ Write → Run (pass) → Revert fix → Run (MUST FAIL) → Restore → Run (pass)
❌ "I've written a regression test" (without red-green verification)
```

**构建：**
```
✅ [Run build] [See: exit 0] "Build passes"
❌ "Linter passed" (linter doesn't check compilation)
```

**需求：**
```
✅ Re-read plan → Create checklist → Verify each → Report gaps or completion
❌ "Tests pass, phase complete"
```

**把工作委派给代理：**
```
✅ Agent reports success → Check VCS diff → Verify changes → Report actual state
❌ Trust agent report
```

## 为什么这很重要

来自 24 条失败记忆：
- 你的人类协作者说「我不相信你」——信任破了
- 未定义的函数被交付出去——运行时会崩溃
- 漏掉的需求被交付出去——功能不完整
- 时间耗在虚假的完成上 → 被打回去 → 返工
- 违反了这条：「诚实是核心价值。如果你说谎，你会被换掉。」

## 何时应用

**在下面每件事之前都要应用：**
- 任何变体的成功/完成声称
- 任何满意的表达
- 任何关于工作状态的正面说法
- 提交、创建 PR、任务完成
- 进入下一项任务
- 委派给代理

**规则适用于：**
- 原句
- 转述和同义词
- 对成功的暗示
- 任何暗示完成或正确的沟通

## 底线

**验证没有捷径。**

运行命令。读输出。然后再声称结果。

这一点没有商量余地。
