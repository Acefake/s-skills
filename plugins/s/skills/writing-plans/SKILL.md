---
name: writing-plans
description: "中文：已有规格或需求、要做多步骤任务、动手改代码之前。Use when you have a spec or requirements for a multi-step task, before changing code."
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。

本技能译自 Jesse Vincent 的 Superpowers（MIT）。许可证见上一级文件夹的 `LICENSE-superpowers`。

# 编写计划

## 概述

撰写全面的实现计划。假定工程师对我们的代码库毫无背景，对好坏的判断也未必可靠。把他们需要知道的一切写清楚：每个任务要动哪些文件、代码、测试、可能要核对的文档、如何测试。把整份计划拆成一口大小的任务交给他们。DRY。YAGNI。TDD。频繁提交。

假定他们是熟练的开发者，但对我们的工具集或问题领域几乎一无所知。假定他们对良好的测试设计也并不熟悉。

**开始时宣布：**「我正在使用 writing-plans 技能来创建实现计划。」

**上下文：** 若在隔离的 worktree 中工作，它应在执行时已通过 `superpowers:using-git-worktrees` 技能创建。

**计划保存到：** `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`
- （用户对计划存放位置的偏好覆盖此默认值）

## 范围检查

如果规格覆盖多个相互独立的子系统，它本应在头脑风暴阶段被拆成子项目规格。如果当时没有拆，建议把这件事拆成多份计划——每个子系统一份。每份计划都应能独立产出可工作、可测试的软件。

## 文件结构

定义任务之前，先勾勒哪些文件会被创建或修改，以及每个文件负责什么。分解决策在这里定下来。

- 设计边界清晰、接口明确的单元。每个文件只承担一项清晰职责。
- 你对能一次放进上下文的代码推理得最好，文件聚焦时修改也更可靠。优先选择更小、更聚焦的文件，而不是承担过多职责的大文件。
- 一起变更的文件应当放在一起。按职责拆分，不按技术分层拆分。
- 在已有代码库中遵循既有模式。如果代码库使用大文件，不要单方面重组；但如果正在修改的文件已经变得难以驾驭，在计划中加入一次拆分是合理的。

这一结构决定任务如何分解。每个任务应产出独立成立的变更。

## 合适的任务规模

任务是自带一轮测试周期、并且值得一道全新评审关卡的最小单位。划定任务边界时：把初始化、配置、脚手架和文档步骤并入其交付物所需要的那个任务；只在评审者可以有意义地否决其中一个任务、同时批准相邻任务的地方拆分。每个任务结束时都有可独立测试的交付物。

## 一口大小的任务粒度

**每一步只做一个动作（2-5 分钟）：**
- 「编写失败的测试」——一步
- 「运行它，确认它失败」——一步
- 「实现让测试通过的最少代码」——一步
- 「运行测试，确认它们通过」——一步
- 「提交」——一步

## 计划文档头部

**每份计划都必须以这个头部开始：**

```markdown
# [Feature Name] Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

## Global Constraints

[The spec's project-wide requirements — version floors, dependency limits,
naming and copy rules, platform requirements — one line each, with exact
values copied verbatim from the spec. Every task's requirements implicitly
include this section.]

---
```

## 任务结构

````markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

**Interfaces:**
- Consumes: [what this task uses from earlier tasks — exact signatures]
- Produces: [what later tasks rely on — exact function names, parameter
  and return types. A task's implementer sees only their own task; this
  block is how they learn the names and types neighboring tasks use.]

- [ ] **Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

- [ ] **Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

## 禁止占位

每一步都必须包含工程师需要的实际内容。下面这些属于**计划失败**——绝不要写出来：
- 「TBD」「TODO」「以后再实现」「补上细节」
- 「加上适当的错误处理」/「加上校验」/「处理边界情况」
- 「为上面的内容写测试」（没有实际测试代码）
- 「与任务 N 类似」（把代码再写一遍——工程师可能不按顺序读任务）
- 只描述做什么、不展示怎么做的步骤（涉及代码的步骤必须有代码块）
- 引用任何任务都没有定义的类型、函数或方法

## 记住
- 始终给出精确文件路径
- 每一步都给出完整代码——如果某一步修改代码，就把代码展示出来
- 给出精确命令以及预期输出
- DRY、YAGNI、TDD、频繁提交

## 自检

写完整份计划之后，用新的眼光看规格，并对照它检查计划。这是你自己执行的检查清单——不是派发子代理。

**1. 规格覆盖：** 浏览规格中的每一节、每一条需求。你能指出实现它的任务吗？列出所有缺口。

**2. 占位扫描：** 在计划中搜索危险信号——上面「禁止占位」一节中的任何模式。把它们修掉。

**3. 类型一致性：** 后面任务里使用的类型、方法签名和属性名，是否与前面任务中定义的一致？任务 3 里的函数叫 `clearLayers()`，任务 7 里却叫 `clearFullLayers()`，这就是缺陷。

如果发现问题，就地修掉。不必重新审查——修完继续即可。如果发现某条规格需求没有对应任务，把任务补上。

## 执行交接

保存计划后，给出执行方式供选择：

**「计划已完成并保存到 `docs/superpowers/plans/<filename>.md`。两种执行方式：**

**1. 子代理驱动（推荐）** - 我为每个任务派发一个全新子代理，任务之间做评审，迭代快

**2. 会话内执行** - 在本次会话中使用 executing-plans 执行任务，分批执行并设检查点

**用哪种方式？」**

**若选择子代理驱动：**
- **必需子技能：** 使用 superpowers:subagent-driven-development
- 每个任务一个全新子代理 + 两阶段评审

**若选择会话内执行：**
- **必需子技能：** 使用 superpowers:executing-plans
- 分批执行，并为评审设置检查点
