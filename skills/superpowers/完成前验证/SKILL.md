---
name: 完成前验证
description: 在准备宣布工作已完成、已修好或已通过之前，在提交（commit）或开 PR 之前使用——要求先运行验证命令、确认输出结果，然后才能说成功；永远先有证据，再下结论
---

> 翻译自 Superpowers 插件（编号 684）的 `verification-before-completion` skill，原作者 Jesse Vincent（版权 © 2025 Jesse Vincent），许可证 MIT（全文见上一级文件夹的 `LICENSE-superpowers`），仅供自用。插件版本 6.1.1。
> 说明：代码块里的内容保持英文原样，每个代码块后面附了中文意思。
> 英文名备份：s-verification-before-completion

# 完成之前先验证

## 概述

没有验证就说工作完成了，这是不诚实，不是效率高。

**核心原则：** 永远先有证据，再下结论。

**违反这条规则的字面意思，就是违反它的精神。**

## 铁律

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

（意思：没有刚刚得到的验证证据，就不能宣布完成。）

如果你在这条消息里没有运行验证命令，就不能说它通过了。

## 关卡流程

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

（意思：在宣布任何状态或表示满意之前：1. 找出：哪条命令能证明这个说法？2. 运行：执行完整的命令（重新跑、跑完整）。3. 阅读：看完整输出，检查退出码，数一数失败的数量。4. 核实：输出是否证实了这个说法？——如果没有：带着证据说明实际状态；如果是：带着证据说出结论。5. 只有到这时：才下结论。跳过任何一步 = 说谎，不是验证。）

## 常见的失败

| 说法 | 需要 | 不够的 |
|-------|----------|----------------|
| 测试通过 | 测试命令的输出：0 个失败 | 之前跑过的结果、“应该能过” |
| 代码风格检查（linter）干净 | linter 输出：0 个错误 | 只查了一部分、凭推测 |
| 构建成功 | 构建命令：退出码 0 | linter 通过了、日志看起来不错 |
| bug 修好了 | 测试原来的症状：通过 | 代码改了、以为修好了 |
| 回归测试有效 | 验证过“红-绿”循环 | 测试通过了一次 |
| 子智能体完成了 | 版本控制（VCS）的改动记录显示有改动 | 子智能体报告“成功” |
| 需求满足了 | 逐行核对的清单 | 测试通过 |

## 危险信号——停下

- 用了“应该”、“大概”、“好像”
- 验证之前就表示满意（“太好了！”、“完美！”、“搞定！”等）
- 没验证就准备提交/推送/开 PR
- 相信子智能体的成功报告
- 依赖只做了一部分的验证
- 想着“就这一次”
- 累了，想赶紧结束
- **任何在没运行验证的情况下暗示成功的措辞**

## 防止找借口

| 借口 | 事实 |
|--------|---------|
| “现在应该能用了” | 去运行验证 |
| “我很有把握” | 有把握 ≠ 有证据 |
| “就这一次” | 没有例外 |
| “linter 通过了” | linter ≠ 编译器 |
| “子智能体说成功了” | 自己独立核实 |
| “我累了” | 累 ≠ 借口 |
| “查一部分就够了” | 一部分什么都证明不了 |
| “换个说法，规则就不适用了” | 精神重于字面 |

## 关键模式

**测试：**
```
✅ [Run test command] [See: 34/34 pass] "All tests pass"
❌ "Should pass now" / "Looks correct"
```
（✅ 运行测试命令，看到 34/34 通过，再说“所有测试通过”；❌ “现在应该能过了” / “看起来是对的”）

**回归测试（TDD 红-绿）：**
```
✅ Write → Run (pass) → Revert fix → Run (MUST FAIL) → Restore → Run (pass)
❌ "I've written a regression test" (without red-green verification)
```
（✅ 写测试 → 运行（通过）→ 撤回修复 → 运行（必须失败）→ 恢复修复 → 运行（通过）；❌ “我写了一个回归测试”（但没做红-绿验证））

**构建：**
```
✅ [Run build] [See: exit 0] "Build passes"
❌ "Linter passed" (linter doesn't check compilation)
```
（✅ 运行构建，看到退出码 0，再说“构建通过”；❌ “linter 通过了”（linter 不检查能不能编译））

**需求：**
```
✅ Re-read plan → Create checklist → Verify each → Report gaps or completion
❌ "Tests pass, phase complete"
```
（✅ 重读计划 → 列出清单 → 逐项核实 → 报告缺口或完成；❌ “测试通过了，这个阶段完成”）

**交给子智能体做：**
```
✅ Agent reports success → Check VCS diff → Verify changes → Report actual state
❌ Trust agent report
```
（✅ 子智能体报告成功 → 查看版本控制的改动 → 核实改动 → 报告实际状态；❌ 直接相信子智能体的报告）

## 为什么这很重要

来自 24 次失败的记忆：
- 你的人类搭档说“我不相信你”——信任破裂了
- 未定义的函数被发布出去——会崩溃
- 漏掉的需求被发布出去——功能不完整
- 在虚假的“完成”上浪费时间 → 改方向 → 返工
- 违反了：“诚实是核心价值。如果你说谎，你会被替换掉。”

## 什么时候用

**以下情况之前，一律要用：**
- 任何形式的“成功/完成”说法
- 任何表示满意的话
- 任何关于工作状态的正面陈述
- 提交、开 PR、标记任务完成
- 进入下一个任务
- 交给子智能体去做

**规则适用于：**
- 原话
- 换个说法和同义词
- 暗示成功的话
- 任何暗示“已完成/正确”的沟通

## 底线

**验证没有捷径。**

运行命令。看输出。然后才说结果。

这一点没有商量余地。
