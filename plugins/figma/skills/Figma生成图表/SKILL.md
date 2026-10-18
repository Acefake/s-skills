---
name: Figma生成图表
description: "必须先做的前置步骤——每次调用 `generate_diagram` 工具之前，都要先加载这个 skill。绝不要不加载这个 skill 就直接调用 `generate_diagram`。只要用户要求创建、生成、画、渲染、草绘或搭建一张图——流程图、架构图、时序图、ERD 或实体关系图、状态图或状态机、甘特图或时间线——就触发。用户提到 Mermaid 语法，或者想在 FigJam 里把系统架构、决策树、依赖图、API 调用流程、认证握手、数据库结构或流水线画出来时，也触发。它会把你引到对应图类型的指南，设定通用的 Mermaid 限制，并告诉你什么时候该换一种图，或者干脆不用这个工具（思维导图、饼图、类图等）。"
---

> 翻译自 Figma 官方仓库 https://github.com/figma/mcp-server-guide （skills/figma-generate-diagram，commit f278942）的 `figma-generate-diagram` skill，原作者 Figma，许可证：未注明许可证（仓库里没有找到 LICENSE 文件），仅供自用。
> 说明：参考文件 `references/` 一共约 100 KB，太大，保留英文原文 ⚠️。工具名、参数名、Mermaid 关键字保持原样。链接里的 `../figma-use-figjam/...` 已经改成 `../FigJam白板操作/...`，正文里提到的其他 skill 也换成了中文名。
> 英文名备份：s-figma-generate-diagram

# generate-diagram

**每次调用 `generate_diagram` 工具之前，你都必须先加载这个 skill。** 跳过它会导致本来可以避免的渲染失败和低质量的结果。

`generate_diagram` 接收 Mermaid.js 语法，生成一张可以编辑的 FigJam 图。这个 skill 把你引到对应类型的指南，并设定通用的限制。

## 第 1 步：`generate_diagram` 是对的工具吗？

### 支持的图类型

`flowchart`、`sequenceDiagram`、`stateDiagram` / `stateDiagram-v2`、`gantt`、`erDiagram`。

### 不支持的——不要调用这个工具

如果用户想要下面任何一种，直接告诉他们 `generate_diagram` 不支持，而不是调用工具然后失败：
- **饼图、思维导图、维恩图、类图、用户旅程图（journey）、时间线（timeline）、象限图、C4、git 图、需求图**

### 什么时候建议用户去 Figma 里编辑

这个工具做不到：
- 修改已有图的字体
- 移动单个形状
- 生成之后逐个节点地编辑图

如果用户要对已有的图做这些事，建议他们在 Figma 里打开这张图，在那里编辑。如果是内容层面的修改，通常重新生成更快。

## 第 2 步：选图的类型

简单的分流——用第一个匹配上的。

| 用户想要…… | 类型 | 下一步 |
|---|---|---|
| 服务 + 数据存储 + 队列 + 第三方集成 | **架构流程图** | 阅读 [references/architecture.md](./references/architecture.md) |
| 决策树、流程、流水线、依赖图、用户旅程 | **流程图** | 阅读 [references/flowchart.md](./references/flowchart.md) |
| 各方之间随时间的交互（API 调用、认证、消息） | **时序图** | 阅读 [references/sequence.md](./references/sequence.md) |
| 数据模型、表、键、对应关系数量 | **ER 图** | 阅读 [references/erd.md](./references/erd.md) |
| 有名字的状态以及它们之间的转换 | **状态图** | 阅读 [references/state.md](./references/state.md) |
| 带日期、里程碑的项目计划 | **甘特图** | 阅读 [references/gantt.md](./references/gantt.md) |

如果用户要的是流程图，而它描述的是软件基础设施（服务、数据存储、队列、外部集成），就引到 `architecture.md`——而不是 `flowchart.md`。拿不准时，问用户。

## 第 3 步：通用限制（适用于所有图类型）

1. Mermaid 源码的任何地方都**不要用 emoji**。工具会拒绝。
2. 标签里**不要用 `\n`**。只在绝对需要时才换行，而且只能用真正的换行（不是转义序列）。
3. 标签里**不要用 HTML 标签**。
4. **保留字**——不要把 `end`、`subgraph`、`graph` 用作节点 ID。
5. **节点 ID**：用驼峰命名（`userService`），不要有空格。下划线在某些处理器里会弄坏连线的走向。
6. **标签里的特殊字符**必须用引号包起来：`A["Process (main)"]`、`-->|"O(1) lookup"|`。
7. **时序图**——Mermaid 的 `Note over X` / `Note left of X` / `Note right of X` 会被渲染器悄悄去掉；不要把它们写进源码。如果用户想在时序图上加批注，先生成基础图，再通过混合工作流加便利贴/文字（[references/workflow.md](references/workflow.md)）。
8. **甘特图**——`classDef`、`class` 和任何其他样式都会在预处理时被去掉；渲染出来的图不会有颜色。如果用户想要按颜色区分阶段、里程碑或任务，先生成基础图，再通过混合工作流加颜色/批注（[references/workflow.md](references/workflow.md)）——或者，对于根本上就需要样式的图，改为直接用 `use_figma` 搭建时间线（见 [references/gantt.md](references/gantt.md) 第 11 节）。
9. **任何 `use_figma` 扩展里都只用 FigJam 支持的 API。** `generate_diagram` 的结果会落在一个 FigJam 文件里（`figma.com/board/...`），所以混合扩展必须只用 FigJam 支持的 API。**不要**调用 `figma.createPage()`——它只在 Design 文件里能用（`figma.com/design/...`），在 FigJam 里会抛出 `TypeError: figma.createPage no such property 'createPage' on the figma global object`。改用 FigJam 的分区（section）来组织内容（见 [FigJam白板操作](../FigJam白板操作/SKILL.md)）。

## 第 4 步：垃圾进，垃圾出

生成的图有多好，上限是你写的 Mermaid 有多好；而 Mermaid 有多好，上限是你掌握的上下文有多少。写 Mermaid 之前，确保你有足够的真实信息来准确描述对象——并利用当前环境给你的一切去收集这些信息。

根据能用的东西，有用的上下文来源包括：

- **源代码**——搜索/阅读相关文件，让图反映真实的服务名、真实的连线标签、真实的数据存储、真实的入口。顺着实际的路由/处理函数/消费者走一遍，比凭记忆重画要好。
- **用户提供的文档**——PRD、规格说明、会议记录、文字稿、研究总结、入职文档、流程说明。如果对象不是代码，请用户粘贴或附上。
- **已有的 Figma 或 FigJam 文件**——如果新图应该和用户已有的某个文件保持一致，用 `get_figjam` 或 `get_design_context` 读取它（见 `Figma插件基础` 和 `FigJam白板操作` 这两个 skill）。
- **你能用的其他 MCP 服务器或工具**——问题跟踪系统、文档网站、CRM、数据分析、内部 wiki、设计系统、数据库结构等。如果某个已连接的工具掌握着你要画的东西的真实情况，就从它那里取，而不是去猜。
- **用户本人**——当描述很单薄或含糊（流向不清楚、范围不清楚、不清楚哪些实体重要）时，生成之前问一两个有针对性的问题。例如：“主要的 3–5 个步骤是什么？”、“每一步由谁负责？”、“什么触发下一步？”。问一个好问题，胜过浪费一张图。

不要为了让图“更完整”而编造连线、标签或实体。缺信息好过编出来的信息——留个空白，并告诉用户。

## 第 5 步：这张图需要的东西会超出 Mermaid 能表达的范围吗？

Mermaid 不是什么都能做。贴在特定节点上的便利贴批注、ERD 上按业务领域给每个节点上色、带附加数据的标注——这些都需要把 `generate_diagram` 和 `use_figma` 组合起来用（通过 [FigJam白板操作](../FigJam白板操作/SKILL.md) skill）。这就是**混合工作流**。

这要靠判断，不是默认做法。当用户的要求明显能从中受益时才用——基础图明显够用时就跳过。说“要用”的信号：用户明确要了备注、颜色、标注，或者“每个节点上附上 X”；他们分享了能对应到具体节点的数据；这张图是要分享出去的成品，而不是用来思考的草图。说“不用”的信号：简短/一看就懂的请求、小图、用户在探索或测试。

**如果确实需要混合工作流，在调用 `generate_diagram` 之前先阅读 [references/workflow.md](./references/workflow.md)**——它讲了这个模式、两个核心做法（批注 + 颜色区分）、沟通方式和失败处理。如果不需要，直接进入第 6 步。

## 第 6 步：调用工具

必填：
- `name`：一个有描述性的标题（会显示给用户）
- `mermaidSyntax`：Mermaid 源码

可选：
- `userIntent`：一句简短的话，描述用户想完成什么——有助于使用统计和后续调优
- `useArchitectureLayoutCode`：**只用于架构图**；值写在 `references/architecture.md` 里
- `fileKey`：如果用户想把图加到一个已有的 FigJam 文件里，而不是新建一个

调用 `generate_diagram` 之前**不要**调用 `create_new_file`——这个工具会自己创建文件。

## 第 7 步：生成之后

- 工具会返回一个链接（或小组件），用户点开就能在 FigJam 里打开这张图。除非客户端会渲染内嵌的小组件，否则用 markdown 链接展示它。
- 如果需要扩展（见第 5 步），现在就用 `use_figma` 组合——模式和做法在 [references/workflow.md](./references/workflow.md) 里。
- 如果同一张图试了 2 次用户还是不满意，就停止重新生成。问清楚具体哪里不对，或者建议他们在 Figma 里打开手动编辑，而不是浪费更多次工具调用。

### 迭代或添加相关的图时，重复使用同一个文件

每次不带 `fileKey` 调用 `generate_diagram`，都会在用户的草稿里新建一个 FigJam 文件。重新生成 4 次 = 4 个要清理的草稿文件。下面这些情况，优先重复使用已有的文件：

- 用户在对同一张图做迭代（“再试一次……”、“改一下标签……”）。
- 用户想要一张跟在第一张旁边的后续图（例如同一个系统的流程图旁边放一张时序图）。

怎样重复使用：

1. 在后续的 `generate_diagram` 调用里**传入 `fileKey`**。从 `figma.com/board/{fileKey}/...` 这样的网址里取出来。图会被添加到已有的文件里，而不是新建一个。
2. 如果你想替换之前的图，而不是加在它旁边，先用 `use_figma` 工具（见 `FigJam白板操作` skill）删掉旧图的节点，然后用同一个 `fileKey` 调用 `generate_diagram`。或者保留旧图，把新图放在旁边——看的人常常能从尝试的历史里受益。

第一次迭代时问用户更喜欢哪种——“在旧图上重新生成，还是两张并排保留？”——并在这次会话后面的迭代里记住他们的回答。
