---
name: refactor-architecture
description: "「/refactor-architecture」「重构架构」「找重构点」「模块耦合太紧」「代码难测」。扫浅模块，出 HTML 报告，再逐个追问定案。Use when the user wants to improve architecture, find refactoring opportunities, consolidate tightly-coupled modules, or make a codebase more testable and AI-navigable."
disable-model-invocation: true
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。


# 架构重构

找出架构上的摩擦，提出**加深（deepening）机会**：把浅模块变成深模块的重构。目的是好测、好让 AI 读懂。

这件事建立在项目自己的领域模型和一套共用的设计词汇上：

- 架构词汇和原则在 [VOCABULARY.md](VOCABULARY.md)：**模块**、**接口**、**实现**、**深度**、**接缝**、**适配器**、**杠杆**、**局部性**，以及删除测试、「接口就是测试面」、「一个适配器是假想的接缝，两个才是真的」。每条建议都严格用这些词，不要漂移成「组件」「服务」「API」「边界」。
- `GLOSSARY.md` 里的领域词给好的接缝起名；`docs/adr/` 里的 ADR 记录了已经定下的决定，不要重新争论。

## 流程

### 1. 摸查

**先划范围再扫描：YAGNI。** 加深一个模块的回报是以后改它更容易，所以要偏重最近在改的地方。动手看之前先定看哪：

- 用户指了方向（某个模块、子系统、痛点），就按它来，跳过下面的推断。
- 否则往回翻一大段提交历史（`git log --oneline`、`git log --stat`），找出反复出现的文件和区域，也就是热点，先看那些路径。改动分散、没有明显热点，就把网撒大。

先读领域词表（`GLOSSARY.md`）和所涉区域的 ADR。

然后派一个子智能体走一遍代码库。不要套死规则，自然地探索，记下哪里让你觉得别扭：

- 理解一个概念要在很多小模块之间来回跳？
- 哪些模块是**浅**的，接口几乎和实现一样复杂？
- 哪里为了好测把纯函数抽了出去，但真正的 bug 藏在调用方式里（没有**局部性**）？
- 哪些紧耦合的模块跨着接缝互相泄漏？
- 哪些部分没有测试，或者通过现有接口很难测？

对怀疑是浅的东西做**删除测试**：删掉它，复杂度是集中了，还是只是挪了个地方？「会集中」就是你要找的信号。

依赖图可以拿工具补一手（只当线索，不替代阅读）：

| 栈 | 看依赖和循环 |
|---|---|
| TS / React / Vue | `npx madge --circular --extensions ts,tsx,vue src`；或 `dependency-cruiser` |
| Go | `go list -deps ./...`、`go mod graph`；包循环编译器直接报 |
| Java | `jdeps -summary`；规则要长期守住用 ArchUnit |

### 2. 把候选写成 HTML 报告

在系统临时目录写一个自包含的 HTML 文件，不往仓库里落任何东西。临时目录取 `$TMPDIR`，没有就用 `/tmp`（Windows 用 `%TEMP%`），写到 `<tmpdir>/architecture-review-<时间戳>.html`，每次运行都是新文件。替用户打开（Linux `xdg-open <路径>`，macOS `open <路径>`，Windows `start <路径>`），并告诉他绝对路径。

报告用 **Tailwind（CDN）** 排版，用 **Mermaid（CDN）** 画关系图、流程图、时序图这类能可靠表达结构的图。Mermaid 和手写 CSS/SVG 混着用：关系是图状的（调用图、依赖、时序）用 Mermaid；想要更有编辑感的（体量图、剖面图、折叠示意）用手写 div/SVG。每个候选都要有**前后对比图**。要可视化。

每个候选渲染成一张卡片：

- **文件**：涉及哪些文件或模块
- **问题**：现在的架构为什么别扭
- **方案**：用大白话说要改什么
- **收益**：用局部性和杠杆来讲，以及测试会怎样变好
- **前 / 后对比图**：左右并排，手绘风，表现出浅在哪、加深后什么样
- **推荐强度**：`强烈推荐`、`值得一看`、`推测` 三选一，做成徽章

报告最后一节是**首选建议**：先做哪个、为什么。

**领域用 GLOSSARY.md 的词，架构用 VOCABULARY.md 的词。** 如果 `GLOSSARY.md` 定义了「订单」，就说「订单受理模块」，不说「FooBarHandler」，也不说「订单服务」。

**和 ADR 冲突**：候选违反现有 ADR 时，只有摩擦真的大到值得重开 ADR 才列出来，并在卡片里明确标出（例如一个警示框：_「违反 ADR-0007，但值得重开，因为……」_）。不要把 ADR 禁止的理论重构全列一遍。

完整的 HTML 骨架、图的画法和样式要求见 [HTML-REPORT.md](HTML-REPORT.md)。

这一步**不要**提接口设计。文件写好后问用户：「想先深挖哪一个？」

### 3. 追问到定案

用户选定一个候选后，一次只问一个问题，沿着决策树和他走一遍：约束、依赖、加深后模块的形状、接缝后面放什么、哪些测试能留下来。能从代码里查到的自己查，不要问。

决定一成形就顺手落地，保持领域模型是新的：

- **给加深后的模块起的名字不在 `GLOSSARY.md` 里？** 把词加进去。文件不存在就这时候建。
- **对话里把一个模糊的词说清楚了？** 当场更新 `GLOSSARY.md`。
- **用户以站得住的理由否掉了候选？** 主动提一句：_「要不要记成一条 ADR，以后架构审查就不会再提它？」_ 只在以后的探索者确实需要这个理由才能避免重复提议时才问；临时理由（「现在不值得」）和不言自明的理由就跳过。
- **想比较加深后模块的几种接口？** 按 [DESIGN-IT-TWICE.md](DESIGN-IT-TWICE.md) 的并行子智能体做法来；具体怎么拆依赖、怎么换测试见 [DEEPENING.md](DEEPENING.md)。

### 4. 落地

定案以后要动手：
- 只动一个模块簇：按 s-mode 的 `playbooks/refactoring.md` 做，先锁住行为（特征测试或对拍脚本），再小步迁移，每步保持绿，最后证明行为没变。
- 跨多个模块或要分几个 PR：先 `writing-plans` 写分步计划，再按上面的步骤逐段做。
- 新接口上测什么用 `test-strategy` 定；旧调用方按 `principle-migrate-callers-then-delete-legacy-apis` 迁完再删。

### 5. 守住

迁完把新的模块依赖方向写成检查，放进 CI，否则几周后又会长回去：

| 栈 | 怎么守 |
|---|---|
| TS / React / Vue | `dependency-cruiser` 的 `forbidden` 规则（禁止循环、禁止越层引用），CI 跑 `depcruise src` |
| Go | 用 `internal/` 目录让编译器拦住越界引用；再细的规则用 `go-arch-lint` 或一个 `go list` 脚本 |
| Java | ArchUnit 测试（`layeredArchitecture()`、`noClasses().should().dependOnClassesThat()`），随单测一起跑 |

规则只写这次定下来的接缝，不要一次写满整张理想架构图。被规则拦住时，要么改代码，要么在 ADR 里写明为什么放行。
