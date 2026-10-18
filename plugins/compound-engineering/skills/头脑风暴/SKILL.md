---
name: 头脑风暴
description: "把模糊或很大的想法，通过探讨整理成一份大小合适、只写需求的统一计划。当用户想头脑风暴（brainstorm），或想确定到底要做什么、做到多大范围时使用。不用于执行已经说清楚的工作。如果是要判断“该不该采用某个具体的外部技术”，请用 ce-pov。"
argument-hint: "[要探索的功能想法或问题] [output:html]"
---

> 翻译自 Compound Engineering 插件（编号 680）的 `ce-brainstorm` skill，原作者 Kieran Klaassen 和 Trevin Chow（版权 © 2025 Every），许可证 MIT（全文见上一级文件夹的 `LICENSE-compound-engineering`），仅供自用。原项目：https://github.com/EveryInc/compound-engineering-plugin（插件版本 3.29.0）。
> 说明：`references/` 和 `scripts/` 文件夹里的文件保持英文原样，没有翻译。文中的命令、文件路径、配置项名字都保持原样；引用其他 skill 的地方已经换成中文名（没翻译的 skill 保持原名）。
> 英文名备份：s-ce-brainstorm

# 为一个功能或改进做头脑风暴

头脑风暴通过对话回答**做什么（WHAT）**；之后 `做计划` 在同一份统一计划文件里补充**怎么做（HOW）**。这个 skill 不写代码。**今年是 2026 年**，用来给产物标日期。

**结果：** 一个和工作大小相称的结果，让 `做计划` 可以直接在它上面继续，不需要自己编造产品行为、范围边界或成功标准：轻量（Lightweight）的工作就是聊天里的一段话；值得写文件时，就是 `<root>/plans/` 下面一份只写需求的统一计划。

**在头脑风暴路线上，完成标准是：** 那个产物已经写好，并且通过了“可以开始规划”检查（Ready for Planning Check）——或者没写文件，因为对话没有产生任何需要用固定编号记录下来、给之后的读者（做计划的人、审查者或将来的读者）看的决定，用户也没要求写——并且已经展示了 Phase 4 的交接。

**轻量的工作在聊天里结束。** Phase 0.3 会在派发任何东西之前，根据需求和有限的直接阅读来判断等级；拿不准时，选更重的那一级。轻量的工作——小、边界清楚、不太有歧义——以聊天里的一段话结束：不写文件，不派“摸底侦察”（grounding scout），不生成多个方案，也不做“说法核验”（claim verifier）。只有出现了一个需要用固定编号记录、给之后读者看的决定，或者用户要求写文件时，才值得写文件。

**在三种情况下，停下来改走别的路线**，由 `references/phase-0.md` 判断，不要凭记忆。每种情况都有自己的结束方式，所以上面的完成标准不适用：非软件工作，这时由 `references/universal-brainstorming.md` 代替 Phase 0.2–4；关于某个具体外部候选技术“该不该用”的结论性问题，这时提议交给 `ce-pov`；以及两者都不是的——简单帮忙、事实性问题、一步就能完成的任务——直接回答。

功能描述就是调用时带进来的内容，不管是用户写的，还是调用它的 skill 传进来的。如果什么都没给，就问用户想探索什么，拿到之前不要往下做。

**`mode:return-to-caller`**（由 `全自动开发` 这类调用方 skill 放在最前面的标记）：去掉这个标记，对话照常进行，但用 `references/handoff.md` 规定的结构化返回结果代替 Phase 4：不展示菜单，也不调用 `全自动开发` 或 `做计划`。


## 产物根目录

在第一次要拼出或读取 `<root>/` 开头的路径时才确定 `<root>`，不要更早；如果一次运行只用临时空间、或者没有代码仓库，一个这样的路径都没碰到，就整个跳过这一步。

<!-- ce-docs-root:start -->
**在拼出任何产物路径之前，先确定 CE 产物根目录 `<root>`。**

- **读取：** 只从 `<repo-root>/.compound-engineering/config.yaml` 读取 `docs_root`（`<repo-root>` = `git rev-parse --show-toplevel`）。不要从 `config.local.yaml` 读取。没有设置时，`<root>` 就是 `docs`，和以前完全一样。
- **校验：** 如果设置了值，它必须是一个相对于仓库的目录，它的真实路径（把符号链接 symlink 解析之后）要在仓库里面，而且既不能是仓库根目录，也不能在 `.git/` 下面。否则就报错停下，报错里写明 `docs_root` 和它的值——绝不要退回用 `docs`。
- **使用：** 把 `<root>` 作为唯一的产物存放位置：不存在就创建；每个路径都拼成 `<root>/<subdir>`，用这个 skill 自己的子目录；绝不要同时再去读 `docs`。
<!-- ce-docs-root:end -->

`brainstorm_output` 和 `brainstorm_model` 改用下面这条规则来确定：

<!-- ce-config-layers:start -->
**普通的 CE yaml 配置项，从仓库里的两个文件读取。**

- **读取：** 先读 `<repo-root>/.compound-engineering/config.local.yaml`，再读 `config.yaml`（`<repo-root>` = `git rev-parse --show-toplevel`）。文件不存在就跳过。文件有没有被 gitignore（git 忽略）不影响读取结果。
- **谁先算数：** 第一个有效的（没被注释掉的）值胜出。对单个值来说，空值等于没设置；无效的值会继续看下一层，最后用 skill 的默认值。对列表和映射（map）来说，只要这个键出现了——哪怕是空列表或空映射——就整个替换这个键。
- **不要**把这条规则用在 `docs_root` 上——那个键只从 `config.yaml` 读。
<!-- ce-config-layers:end -->

## 执行流程

各阶段按下面的顺序进行。每个阶段都写明了离开哪些文件就没法正确进行：到了那个阶段就去读，绝不要只凭这张表来做。

| 阶段 | 先读 | 只有这些文件里才有的内容 |
|---|---|---|
| 第一个问题之前，并且整个运行期间都适用——包括非软件路线 | 读 `references/interaction-rules.md` | 核心原则和互动规则：每轮只问一个问题；只问环境本身解决不了的决定；默认使用会等待回答的提问工具，以及可以覆盖这个默认的“视觉探查”关卡；什么时候一个问题才真正是开放式的；以及这个 skill 在那里完整写出的、唯一一条转到 `ce-prototype` 的判断 |
| 把对话中已有的某个决定当作“已定”之前 | 读 `references/settled-decisions.md` | “是否已定”的检验；跳过它会重复问已经定了的问题，或者把没检验过的说法当成定论 |
| 0.0 输出模式 | `references/output-mode.md` | `OUTPUT_FORMAT` 的优先顺序；参数标记的解析规则 |
| 0.1–0.4 续做、分类、转路线、定范围 | `references/phase-0.md` | 续做扫描；“停下改走别的路线”的分类；范围等级；“是不是一件完整的工作”关卡；两个警报条件（视觉或空间相关的功能；不熟悉的领域）；任务清单 |
| 1 理解这个想法 | `references/dialogue.md` | 背景扫描和摸底侦察；可选的 Slack 调研员；压力测试；盲点和视觉探查关卡；和已有 `CONCEPTS.md` 及已核实代码之间的冲突关卡；Phase 1.3 的结束条件 |
| 2–2.6 方案、综合、核验 | `references/approaches.md`，另外在写综合总结之前读 `references/synthesis-summary.md` | 生成方案；提升模型推理等级；范围综合总结；说法核验 |
| 3 写计划 | `references/plan-write.md`，然后读 `references/brainstorm-sections.md` 和对应格式的渲染参考文件 | 是否值得写文档；各章节的约定；“可以开始规划”检查 |
| 4 交接 | `references/handoff.md` | 有哪些选项以及它们什么时候显示；渲染模式规则；每种选择对应的派发方式，包括传给 `做计划` 什么；收尾总结 |

下面这些规则不用读任何文件也成立：

**`OUTPUT_FORMAT` 只能二选一**——markdown 或 HTML，绝不同时用两种。格式按下面的顺序取第一个适用的：这次提示里的要求、用户之前说过的偏好、配置，最后是 markdown；所有运行都这样，包括无界面（headless）运行。

**在头脑风暴路线上写文件时，产物约定不变**：写到 `<root>/plans/YYYY-MM-DD-HHMM-<type>-<topic>-plan.<md|html>`，其中 `HHMM` 用写入时的本地时间；frontmatter（文件开头的元数据）里要有 `artifact_contract: ce-unified-plan/v1` 和 `product_contract_source: ce-brainstorm`；正文是一个 Goal Capsule（目标概要）加上 Product Contract（产品约定）。**不要**输出 Goal Launch Block 或 Reader Index。非软件路线这些都不写。

**写了文件时，只要“可以开始规划”检查里有任何一项不通过，就不要宣布文件已写好，也不要进入 Phase 4**；聊天结果直接进入 Phase 4（交接），不用做检查。即兴编出来的交接菜单是另一种不声不响的失败：它会显示本应隐藏的选项，并把错误的输入传给下一个 skill。

Phase 1.1 的摸底侦察、Phase 2.6 的说法核验，以及可选的 Slack 调研员，按任务的类型分等级选模型，绝不写死某个模型名字；派发其中任何一个之前，先读 `references/model-tiers.md`。提升模型推理等级是另一套单独的机制（`references/reasoning-elevation.md`）。
