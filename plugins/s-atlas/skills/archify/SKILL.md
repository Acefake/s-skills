---
name: archify
description: "「画架构图」「架构图」「流程图」「时序图」「数据流图」「ER 图」「类图」「做成一页」「用页面讲」。把系统、流程、调用链、表结构、历史或耗时画成经过校验、可交互的独立 HTML 图，或把一个答案做成结论先行的单页讲解页。Use when visualizing systems, API calls, pipelines, schemas, histories, timings, or everyday steps, parts, relationships and states. Also turn an answer into a one-page explainer, with the conclusion first, structured panels, native diagrams and charts, when the user asks for a page, an explainer or an answer to share (做成一页, 用页面讲), or proactively when the user's rules opt in with an [archify explainer: ...] line. Not for dashboards."
license: Apache-2.0
metadata:
  version: "3.2"
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。

# Archify

生成经过检查的独立 HTML：要么是原生图，要么是回答某个问题的单页讲解页。

在你的工作目录中运行命令。除非用户指定了其他位置，否则在该目录下为每个新的产物请求单独建一个文件夹 `.archify/<type>-<slug>-<YYYYMMDD-HHMMSS>/`（本地时间，只确定一次）：把候选稿和 `<slug>.html` 放在里面，修复时复用该文件夹。原生图使用 `candidate.json`，其 `meta.output` 相对于工作目录；讲解页可以使用 `candidate.archify.md` 和可移植的输出文件名。之后的新请求使用新文件夹。在每条命令中把 `bin/archify.mjs` 替换为已安装包的绝对路径，或它相对于你工作目录的路径；CLI 的输入和输出路径都从该目录解析。

为真实代码库画原生图时，在追踪所请求的行为期间阅读 [Repository authoring](references/repository-authoring.md)。系统描述走下面的原生步骤；冻结的候选稿走交接路径。

## 选择产物 <a id="choose-the-artifact"></a>

- 当用户要求画出或可视化一个系统、流程、表结构或历史时，使用原生图和类型路由表。
- 当用户要求以页面形式给出答案时使用 `explainer`：一个页面、一页、一个讲解页、可以分享的东西（“做成一页”、“用页面讲”、“answer with a page”）。没有这类请求时，用文字回答或画出所请求的图。应请求制作的页面，其回复以「输出」一节中那行单行模式提议结尾。
- 上下文中的规则行会改变这一点。`[archify explainer: proactive]`：对于需要表格、步骤或多个小节的解释、对比、权衡、决策、诊断、审查或计划，也要在未被要求时主动做一个页面。`[archify explainer: always-on]`：每条得出结论的回复都还要附一个最多四个面板的紧凑页面，交付时不打开它，回复以其链接收尾。`[archify explainer: on-demand]`：只在被要求时制作，且绝不提议模式。
- 在任何模式下，页面都需要一个背后有一定结构支撑的结论：闲聊、一行答案、原始命令输出和只要文字的请求都不做页面。
- 对于 `explainer`，阅读 [Explainer authoring](references/explainer-authoring.md)，了解其结论、理由、范围、看板布局和可选的原生图。先写出完整草稿，再运行 `finalize explainer` 完成校验、原子交付和产物检查。局部内容修订使用面板补丁。

## 已有候选稿的交接 <a id="existing-candidate-handoff"></a>

当用户提供一个冻结的候选稿时，先以一次 CLI 调用运行 `finalize`。它的通过回执即完成了自动化关卡；在声称视觉质量之前，遵循「交付」一节中的任何视觉审查建议。修复时遵循第 5 步。

`finalize` 在其交付回执中包含一次有界的更新检查；见「更新提示」一节。

## 原生图编写 <a id="native-diagram-authoring"></a>

普通生成使用此路径。只有当分支参考资料所述的触发条件成立时才去读它们。

1. 根据问题从 `architecture`、`workflow`、`sequence`、`dataflow`、`lifecycle`、`erd`、`class`、`tree`、`timeline` 或 `waterfall` 中选择一种。
2. 直接使用类型路由表中的确切 schema 和示例路径，不要列出它们的目录。把 [Authoring defaults](references/authoring-defaults.md) 和该模式的示例放在一个有界批次中读取，与项目文档和完整 schema 分开，以免任何一方被截断；在写之前补回任何缺失的小节。对于 Architecture，使用匹配的 showcase 示例。对于 Architecture 以外的每种模式，还要读该模式的 schema 和通用 schema。在选用任何新字段、枚举或受约束文本之前，先读相关的 schema 定义，尤其是边界种类。示例教的是形状，不是事实。使用全新的 ID、措辞和布局。直接写候选稿，不做前置的 help、doctor、起始校验、临时图或输出路径列举。只为明确要求的标志查询品牌；对于用户提供了 URL 的未知标志，阅读 [Brand marks](references/brand-marks.md)。
3. 一旦所请求的范围以及（对真实代码库而言）[源码证据](references/repository-authoring.md) 都已覆盖，就直接写出完整候选稿，不要在散文中规划坐标。在定坐标之前，先按 Authoring defaults 选择 Architecture 的抽象层级和相连布局：展示主要用户旅程和必要的分支，保留控制角色和改变行为的条件，并为实际的关系标签留出足够空间。节点、关系、来源、视图、卡片或边界的数量都不是目标，也不是上限。先用自动路由；只有对必要的分支、回程、用户提供的几何或经测量的修复，才加显式路由。把 `meta.quality_profile` 设为 `"showcase"`，除非用户要求密集的 `standard`。对于 ERD，使用表优先布局：在 `entities[].attributes` 中展示每一个物理列，保留其 SQL 类型和源码注释，标明每个列承担的每一种键角色（`key` 接受一个角色或一个列表，因此连接表的列是 `["pk", "fk"]`，且每个 `fk` 列还需要像 `"orders.id"` 这样的 `references`），绝不把列挪进卡片来代替表。在放置之前先把表归入功能域，给每个域一个简洁的 `tag`，并把其成员放在由网格单元构成的一个实心矩形中——单行、单列或填满的矩形块，不能是 L 形或对角线。带 tag 的表总是需要 `row`/`col`，因为绝对坐标没有网格单元，而一个其表未填满一个矩形的域无法画成色带：渲染器会报告 `erd/domain-not-drawn`，而不是发布一张无法标出该域的图。多域 schema 最好读成每列一个域——每个 `tag` 一条竖向连续区——因为阅读器会把宽画布放大到阅读器宽度，把高画布缩小直到页面放得下，所以宽排布才是在笔记本视口内保持完整且清晰的那一种。大约超过 8 张表或 50 个字段的 schema 优先 ERD 本身就是一张密集图：以 `standard` 编写其首个全字段版本，只有在布局仍然可读时才升级。
4. 写完完整的首个候选稿后，直接运行 `finalize`。它的第一道关卡是 showcase 校验；成功的初稿不需要单独的预校验。命令运行期间保持候选稿不变：

   ```bash
   node bin/archify.mjs finalize <type> <candidate.json> <output.html> --quality showcase --json
   ```

   对于有仓库支撑的候选稿，在初稿中就包含证据，并使用完整的首条命令：`node bin/archify.mjs finalize <type> <candidate.json> <output.html> --repo-root <repo-root> --quality showcase --json`。传入与 `meta.quality_profile` 匹配的 `--quality`，例如密集的首版 ERD 用 `standard`。

   通过回执证明其中包含的 `validate`、`deliver`、严格 `check` 和真实浏览器 `browser-check` 关卡都已通过。使用它的紧凑摘要；只有针对单独请求或聚焦的失败诊断才运行独立命令。

5. 非零退出绝不是成功。阅读紧凑的 stdout 或 `evidence.summaryReceipt`，然后[修复失败的关卡](references/delivery-contract.md#failed-finalize-and-candidate-repair)，包括其修复次数上限。保留所请求的含义和源码证据。对于多条缠绕的 Architecture 路由，阅读 [Architecture layout repair](references/architecture-layout-repair.md)；对于经测量的字段或几何失败，阅读 [Authoring contract](references/authoring-contract.md)。编辑相连的邻域，然后重新运行第 4 步中的完整 `finalize` 命令。一旦某次运行到达了 `browser-check`，输出路径就拥有了那份证据：之后的每次运行都要给它自己的 `--out-dir <folder>/review-<n>`。

## 更新提示 <a id="update-awareness"></a>

`finalize` 和独立的 `deliver` 会在其回执中包含 `update`。不要为同一次交付另外运行检查。如果 `update.noticeRequired` 为 true，阅读 `references/update-awareness.md`，并在你给用户的最终回复中保留一条紧凑的更新提示，即使某个质量关卡失败也一样。对于包含多张图的任务，在最终回复中只提一次更新。只有在用户明确要求时才暂缓或忽略提醒；绝不主动安装或更新。

在首个候选稿之前，使用编写参考资料和相关的仓库源码，而不是 Archify 的实现或测试。如果经过聚焦修复后诊断信息仍然无法据以行动，再去查看 Archify 的实现。


## 类型路由 <a id="type-router"></a>

| 类型 | 用于 | Schema | 示例 |
|---|---|---|---|
| `architecture` | 组件、服务、云/安全边界、基础设施；日常事物由什么组成 | `schemas/architecture.schema.json` | 系统描述、服务、库和 CLI 仓库：`examples/web-app.architecture.json`；部署仓库：`examples/production-deployment.architecture.json` |
| `workflow` | 流程、审批关卡、工具调用、运维手册、CI/CD；计划和分步骤的生活流程 | `schemas/workflow.schema.json` | `examples/agent-tool-call.workflow.json` |
| `sequence` | API 调用链、请求生命周期、异步追踪、返回；人与人之间的往来 | `schemas/sequence.schema.json` | `examples/cache-miss-request.sequence.json` |
| `dataflow` | 管道、ETL/ELT、血缘、治理、消费方；钱或文件流向哪里 | `schemas/dataflow.schema.json` | `examples/product-analytics.dataflow.json` |
| `lifecycle` | 状态/阶段转换、重试、等待和终止状态；一份申请或订单处于哪一步 | `schemas/lifecycle.schema.json` | `examples/deployment-release.lifecycle.json` |
| `erd` | 表/实体、属性、主键/外键/唯一键，以及它们之间的基数 | `schemas/erd.schema.json` | `examples/orders.erd.json` |
| `tree` | 单父级包含关系：仓库/模块树、能力或功能拆解、组织式分解 | `schemas/tree.schema.json` | `examples/payment-platform.tree.json` |
| `class` | 类、接口、选定的成员，以及类型之间的依赖/关联/继承/实现/组合 | `schemas/class.schema.json` | `examples/payments.class.json` |
| `timeline` | 事情何时发生：事故复盘、发布历史、带来源泳道的按比例时钟上的带时间戳事件 | `schemas/timeline.schema.json` | `examples/payment-incident.timeline.json` |
| `waterfall` | 时间花在了哪里：一次请求或代理运行在共同时间轴上的 span 时长、重叠和嵌套 | `schemas/waterfall.schema.json` | `examples/checkout-request.waterfall.json` |

当在原生图类型之间难以选择时，运行 `node bin/archify.mjs guide "<scenario>" --json`。场景证明示例是结构参考，不是可照抄的事实。

对于日常主题，保持相同的图模式和语义类型，然后用读者能懂的名字命名：如 [Node icons](references/authoring-contract.md#node-icons) 所示，使用日常的 `icon` 值和 `meta.legend` 标签。缺少个人事实时询问用户，而不是编造日期、金额或规则。

## Mermaid 输入 <a id="mermaid-input"></a>

读取 Mermaid 以获取拓扑和含义，然后重新编写 Archify JSON；不要机械地渲染 Mermaid 的样式。

- `flowchart` / `graph` → `workflow`，或者组件图用 `architecture`。
- `sequenceDiagram` → `sequence`；参与者成为语义参与者，箭头成为消息。
- `stateDiagram` → `lifecycle`；状态和转换保留含义，不保留 Mermaid 样式。
- `erDiagram` → `erd`；实体和关系名称、键和基数保留含义，不保留 Mermaid 样式。
- `classDiagram` → `class`；类型种类、选定成员和关系种类保留含义，不保留 Mermaid 样式。

## 交付 <a id="delivery"></a>

首个候选稿和每次修复之后，都使用上面的 `finalize` 命令。

`finalize` 在第一个未通过的关卡处停止。它的紧凑 stdout 和 `<output-stem>.finalize-summary.json` 是普通证据。通过的运行不产生截图，并报告 `visualReview: "not-requested"`。

当一个通过的 Architecture 回执报告 `visualReviewRecommendation.signals.resolvedCrossovers` 时，把候选稿另存一份副本，然后在一次编辑中应用这些提示，且只改变节点的位置和尺寸：每个节点、关系（包括其 `from` 和 `to`）、标签和来源都保持原样。用 `--out-dir <folder>/review-2` 重新运行一次完整的 `finalize`，因为之前的 HTML 已经拥有它的浏览器证据。`--out-dir` 只会重新安置新的 browser-check 回执和默认的 finalize 回执，不会重新安置 HTML 或其交付回执。成功交付会在所请求的输出路径上重写这一对文件；更早的审查证据仍绑定到其原始产物字节。见 [review evidence paths](references/delivery-contract.md#a-new-candidate-at-an-existing-output-path)。如果那次运行失败、报告了更多交叉，或报告了相同的交叉但 `signals.routesOverSuggestedBends` 更多，则恢复副本，并用 `--out-dir <folder>/review-3` 对其定稿。不要开始第二轮布局调整。仅关于多余弯折的提示是可选的。

当 `layoutReviewRecommendation.action` 为 `inspect-sequence-width` 时，在交出新编写的 Sequence 之前遵循 [Sequence width review](references/delivery-contract.md#sequence-width-review)。

对于普通生成（包括新定位的 Architecture），感知审查是可选的。当用户要求视觉审查、在开发审计期间，或存在具体的路由/浏览器问题时，使用 [Optional capture evidence](references/delivery-contract.md#optional-capture-evidence)，并配合 `--out-dir <folder>/visual-check`。`visualReviewRecommendation` 只是建议。在声称视觉质量之前先检查截图；在没有进行感知审查时，任何检查方面的声明都要限定为自动化检查。

对于失败的关卡、独立命令、来源证明/恢复、重复交付、导出或打开，阅读 [Delivery contract](references/delivery-contract.md)。原生图的恢复遵循 `deliver` → 严格来源证明 `check` → `browser-check`；截图需要严格的来源证明。讲解页的交付按其编写指南所述使用 validate、deliver 和 check。

对于 workflow 视口溢出，在下一次布局编辑之前阅读 [Workflow viewport repair](references/authoring-contract.md#workflow-viewport-repair)。

报告验证细节时，区分产物检查、浏览器证据、截图和实际的感知审查。对于明确要求的即时预览或活跃的桌面循环，见 [Optional opening](references/delivery-contract.md#optional-opening)。

## 可选的查看器能力 <a id="optional-viewer-capabilities"></a>

每张渲染出的图默认启用实时动效；省略 `meta.animation`。查看器的 Live/Still 按钮控制播放。

只有当用户明确要求 Share Cards、Route/Reach 卡片、动效、深链接、演示、搜索/聚焦或其他 Viewer Runtime 功能时，才阅读 `references/viewer-runtime.md`。

## 安装与降级 <a id="setup-and-fallback"></a>

技能包内不需要安装任何东西。诊断安装时，用以下命令验证：

```bash
node bin/archify.mjs doctor
node bin/archify.mjs demo <output-directory>
```

对于原生图，当没有 shell 访问权限时，把 architecture SVG 手工放入 `assets/template.html`，使用 CSS 语义类而不是内联颜色，并遵循 `references/delivery-contract.md` 中的视觉审查约定。讲解页需要其渲染器和真实的交付关卡；如果这些不可用，就报告这一限制，并在有用时给出文字答案，不要声称已交付 HTML。

## 输出 <a id="output"></a>

用用户的语言回复，在结果允许的范围内尽量简短；图承载内容，所以一张图通常只需要一行。

- 以指向 HTML 的可点击 Markdown 链接开头：用描述性标题而不是文件名，并使用其绝对路径，路径含空格时用 `<...>` 包起来。
- 当用户想要理解一个系统或代码库，而不是画出所描述的主题时，加一两句话说明关键结论。省略只是复述图中显而易见内容的句子。
- 说明任何会改变图的读法的事项：读者可能预期却被刻意省略的部分或所选的抽象层级、示意而非实测的数值、缺失的源码证据，或在修复过程中被删掉或合并的所请求内容。
- 对于多张图，只报告一次完成，附上已有概览的链接或紧凑的逐图链接，而不是目录路径。

不要复述命令、修复轮次、哈希、质量档位或检查清单；它们留在回执中。如果被问到图是否经过验证，用一行回答，例如“Automated checks passed; not visually reviewed.”。只有为了可复现或排障才给出回执链接和细节。如果所要求的视觉审查无法运行，要说明；只有真正做了视觉检查才声称做过。保留「更新提示」一节中要求的更新提示。

示例：`Created [Checkout request timing](/abs/path/checkout-timing.html). Durations are illustrative, not measured.`

对于讲解页，用两到三行回复：结论和页面链接。只有在某个关卡失败或仍有写作警告时才提及关卡；不要粘贴草稿。

在应请求制作讲解页之后，如果上下文中没有 `[archify explainer: ...]` 行，就在回复末尾加一行可选的提议，提供主动模式，每个对话只提一次，例如：“需要的话，以后遇到解释、对比、排查这类问题，我可以主动做成这样的页面，要开启吗？” 如果用户接受，就把 `[archify explainer: proactive] Make an Archify explainer page, unasked, for explanations, comparisons, decisions, diagnoses, reviews and plans that need a table, steps or several sections.` 添加到当前代理的全局规则文件（例如 `~/.claude/CLAUDE.md`、`~/.codex/AGENTS.md` 或 `~/.config/devin/AGENTS.md`）中，并说出该文件名；删除这一行即可关闭。如果用户拒绝，就提议添加 `[archify explainer: on-demand]`，这样这个问题就不会再出现。
