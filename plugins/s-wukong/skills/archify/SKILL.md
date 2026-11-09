---
name: archify
description: "「画架构图」「流程图」「时序图」「数据流图」「ER 图」「类图」「做成一页」。把系统、流程、调用链、表结构、历史或答案做成校验过的 HTML 图或结论先行的单页讲解。Use when producing a checked HTML diagram or a conclusion-first one-page explainer. Not for dashboards."
license: Apache-2.0
metadata:
  version: "3.2"
---

本会话首次使用本库技能时，按[全局提示词自检](../setup-s-instructions/references/daily-check.md)只读检查一次。
## 运行环境适配

涉及宿主工具、模型配置或子代理时，按需阅读[宿主适配](../../HOSTS.md)。

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

普通生成按下面五步走。字段、示例批次、ERD、Architecture、finalize 命令和修复上限的全文在 [native-diagram-authoring.md](references/native-diagram-authoring.md)。写第一个候选稿之前先读完该文件。只有该文件写明的分支触发条件成立时，才去读对应的参考资料。

1. 按类型路由表选择一种类型。
2. 按该文件读取默认值、示例和 schema，然后直接写候选稿。
3. 所请求的范围和源码证据都覆盖之后，写出完整候选稿。
4. 写完完整的首个候选稿后，运行该文件里的 `finalize` 命令。
5. 非零退出按该文件第 5 步修复，并读 [delivery-contract.md](references/delivery-contract.md)。

## 更新提示 <a id="update-awareness"></a>

`finalize` 和独立的 `deliver` 会在回执里带上 `update`。提示时机、措辞、暂缓和安装边界的全文在 [update-awareness.md](references/update-awareness.md)，包括该文件末尾「技能流程中的更新提示」。同一次交付不另跑检查。多张图的任务在最终回复里只提一次。

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

首个候选稿和每次修复之后，使用 [native-diagram-authoring.md](references/native-diagram-authoring.md) 里的 `finalize` 命令。非零退出不是成功。视觉复查、序列宽度、截图、失败修复、来源证明、重复交付、导出和打开的全文在 [delivery-contract.md](references/delivery-contract.md)，先读其中「技能流程中的交付步骤」。

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

用用户的语言回复。图或页面本身承载内容，回复按 [user-output.md](references/user-output.md) 写，先读完再回复。
