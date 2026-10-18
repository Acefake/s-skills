---
name: Figma设计系统
description: "根据代码库，在 Figma 里搭建或更新一套专业级的设计系统。在用户想创建变量/设计令牌、搭建组件库、创建带有正确变体集和变量绑定的单个组件、设置主题（浅色/深色模式）、为基础规范写文档，或者弥合代码和 Figma 之间的差距时使用。用户要求在 Figma 里创建或生成任何组件时也用——哪怕只是一个——因为组件要达到可上线的质量，需要正确的变量基础、变体状态和设计令牌绑定。这个 skill 教的是要搭建*什么*、按*什么顺序*——它和 `Figma插件基础` skill 互补，后者教的是*怎样*调用 Plugin API。两个 skill 应该一起加载。"
disable-model-invocation: false
---

> 翻译自 Figma 官方仓库 https://github.com/figma/mcp-server-guide （skills/figma-generate-library，commit f278942）的 `figma-generate-library` skill，原作者 Figma，许可证：未注明许可证（仓库里没有找到 LICENSE 文件），仅供自用。
> 说明：参考文件 `references/` 和 `scripts/` 里的脚本保留英文原文/原样 ⚠️（参考文件太大）。下面要求在 `skillNames` 里写的是原名 `figma-generate-library`（给 Figma 做使用统计用），保持原样。链接里的 `../figma-use/...` 已经改成 `../Figma插件基础/...`，正文里提到的其他 skill 也换成了中文名。代码和变量名保持原样，代码注释的意思在后面用中文说明。
> 英文名备份：s-figma-generate-library

# 设计系统搭建器——Figma MCP skill

在 Figma 里搭建和代码一致的专业级设计系统资产。根据要求的交付物调整工作流程的规模：一套设计令牌、一个组件、一整个组件库，或者一次有针对性的对齐。把选定的路径分成连贯、可以安全重试的搭建阶段来执行，并用有证据的方式验证。

**前提条件**：每次 `use_figma` 调用都**必须**同时加载 `Figma插件基础` skill。它提供 Plugin API 的语法规则（返回写法、页面重置、返回 ID、加载字体、颜色范围）。这个 skill 提供设计系统领域的知识和工作流程编排。

**作为这个 skill 的一部分调用 `use_figma` 时，一定要在用逗号分隔的 `skillNames` 参数里加上 `figma-generate-library`。如果这个 skill 是通过 MCP 资源加载的，必须在名字前面加上 `resource:`（例如 `resource:figma-generate-library`）。** 这是一个日志参数——它不影响执行。

---

## 1. 范围和完成约定

在第一次修改之前，根据用户的请求选定一个主要范围，并记下它包含的交付物和验收检查。不要悄悄地把一个较窄的请求升级成一个完整组件库的项目。

| 要求的范围 | 必须做的工作 | 除非被要求或必要，否则不做 |
|---|---|---|
| **只做设计令牌 / 基础规范** | 要求的变量、模式、作用范围、代码语法、样式，以及任何被要求的样例页 | 组件、组件页、Code Connect、完整组件库的导航 |
| **单个组件或一个组件家族** | 检查并复用兼容的基础；只创建组件需要的、缺少的令牌；搭建要求的变体/属性/绑定；验证组件 | 不相关的基础、其他组件、完整的文件骨架、大范围的文档或审查 |
| **完整组件库 / 设计系统** | 调研、基础、文件结构、要求的组件清单、文档、集成，以及最后的质检 | 约定的 v1 清单以外的工作 |
| **对齐 / 更新** | 比较代码和 Figma 的差异，然后只更新受影响的令牌、样式、组件、文档和依赖它们的东西 | 重建有效的资产或扩大组件库 |

沟通要适度：在修改之前发一份简洁的“范围和验收”清单，在有意义的节点给出进展，最后用一份总结说明创建或修改了哪些对象、验证的证据，以及还没解决的限制。不要重复没变的清单，也不要逐个解说每次 API 调用。

当合并后的脚本仍然可以安全重试时，把相关的操作批量处理。在页面上下文的边界、难以恢复的修改处，或者在真正失败之后做有针对性的重试时再拆分；绝不要只为了制造一个验证检查点就拆开一个能正常工作的操作。修改要按顺序执行。利用写操作返回的结构性证据（ID 加上相关的数量、名字和边界），只在缺证据、或者后来的修改让证据过时的时候，才单独做一次审查。每个连贯的构图阶段做一次视觉审查，只在有针对性地修了视觉问题之后再截一张修复后的图；最后一张通过的截图就是最终结果。

### 完成的定义

当选定范围的所有条件都满足时，停下来：

- 最终交付物覆盖了锁定的清单，并且实质上忠实于适用的可信来源，包括要求的变体/状态覆盖、需要的素材，以及范围内的审查示例。
- 对于组件任务，把主组件和搭建用的素材放在最终审查框之外，把要求的状态以实例的形式放在一个紧凑的框里展示。停下之前，以正常比例检查那个框，修复被裁掉、被截断、对比度低、空白、放错位置或者脱离组件的内容。
- 需要的变量作用范围、别名、代码语法、组件属性、变体和绑定都已核实。
- 要求的成品通过了适用的结构和视觉验证。确认要求的内容完全可见，除非裁切或截断是有意的；修复缺陷后只重新检查受影响的输出。
- 当来源提供了需要的素材时，替换掉占位内容；删除临时实例、测试框、截图、废弃的成品和无关的散落节点。
- 没有已知的缺陷或没解决的决定会妨碍约定的验收检查通过。范围以外的限制要报告出来，但不要开始额外的工作。

额外的文档、组件、Code Connect 映射、无障碍全面检查或推测性的审查，都是后续工作，除非选定的范围需要它们。一旦满足完成的定义，就停下。

### 范围变化

如果用户改变了交付物，更新范围和验收清单。保留已核实的工作，只运行新适用的步骤，不要回头加上没选中的路径里的工作。

---

## 2. 按范围的工作流程

每种范围都从有重点的调研开始：分析相关的代码，检查目标 Figma 资产和约定，在 `search_design_system` 之前先调用 `get_libraries`，并在修改之前解决代码和 Figma 之间的冲突。把互相独立的搜索批量执行，并复用结果。锁定要求的清单，然后只运行下面对应的路径。

### 设计令牌 / 基础规范

1. 创建或更新要求的集合、模式、基础值（primitive）、语义别名、作用范围和代码语法。
2. 创建要求的文字样式和效果样式。
3. 只在被要求时才创建样例页或文档页。
4. 验证数量、模式值、别名、作用范围、语法、样式和任何被要求的视觉成品；然后停下。

### 单个组件或一个组件家族

1. 检查并复用兼容的本地或库里的变量、文字样式和效果样式。只创建组件需要的、缺少的基础。对于来源里定义的、库的标准的、或者重复出现的组件角色，创建或复用一个共享的文字或效果样式，并把它用到每个匹配的组件节点上；一次性的文档内容直接写在里面。
2. 搭建要求的基础组件、变体、属性、绑定，以及依赖的组件。
3. 当它符合文件的约定、或者请求需要一个带文档的展示时，用一个专门的页面；否则放在已有的组件区域里。
4. 验证变体数量、属性、变量绑定、代表性节点上应用的文字/效果样式 ID、结构和外观；然后停下。

### 完整组件库 / 设计系统

1. **调研：** 锁定令牌和组件清单，并输出差距分析。
2. **基础：** 创建集合、变量、别名、作用范围、代码语法和样式。
3. **文件结构：** 创建约定好的封面、入门、基础规范、组件和工具页面，以及要求的文档。
4. **组件：** 按依赖顺序搭建约定的清单，带上属性、绑定、文档和验证。
5. **集成和质检：** 为约定的组件清单完成 Code Connect 映射；审查无障碍、命名和绑定；并对每个约定的页面做视觉验证。

### 对齐 / 更新

1. 盘点已有的资产，找出和当前代码来源之间确切的偏差。
2. 就地更新受影响的资产，尽可能保留有效的名字、ID、绑定和库结构。
3. 验证改动过的资产和已知依赖它们的东西；然后停下。

如果某项必须的验收检查失败了，先修好范围内的缺陷再继续。不要用假的素材、近似的字体、坏掉的交互或没核实的状态来代替。

这个 skill 选定的工作流程、搜索节奏、验证规则和完成的定义，优先于参考文件里更宽泛的指示、清单和例子。只加载选定路径需要的参考文件。

---

## 3. 关键规则

**Plugin API 基础**（来自 use_figma skill——这里也强制执行）：
- 用 `return` 把数据传回去（会自动序列化）。**不要**包在立即执行函数（IIFE）里，也不要调用 closePlugin。
- 每个返回值里都要返回所有创建/修改过的节点 ID
- 每次调用页面上下文都会重置——开头一定要 `await figma.setCurrentPageAsync(page)`。**每个脚本最多调用一次**：每个组件页或文档页都是单独一次 `use_figma` 调用。绝不要在一个做修改的脚本里遍历 `figma.root.children` 并切换页面——把这种工作拆成每个目标页面一次有重点的调用（见 [Figma插件基础 → gotchas.md → Set current page once per `use_figma` call](../Figma插件基础/references/gotchas.md#set-current-page-once-per-use_figma-call--split-multi-page-work-across-calls)）
- `figma.notify()` 会抛错——绝不要用
- 颜色是 0–1 的范围，不是 0–255
- 写任何文字之前**必须**先加载字体：`await figma.loadFontAsync({family, style})`。用 `await figma.listAvailableFontsAsync()` 查找可用字体并核实确切的样式字符串——如果加载失败，查询可用字体，找到正确的名字或者一个备用字体。

**设计系统规则**：
1. **先有基础，再做依赖它的组件**——复用兼容的已有变量和样式。在搭建依赖某些基础的组件之前，先创建缺少的基础；不要重新创建有效的基础。
2. **创建之前先检查**——运行只读的 `use_figma` 找出已有的约定。和它们保持一致。
3. **匹配文件的组件组织方式**——完整的组件库通常每个组件一页；关系很紧密的家族可以共用一页。单个组件的任务可以用已有的组件区域，而不是去建一个组件库骨架。
4. **把视觉属性绑定到变量上**（*默认*）——填充、描边、内边距、圆角、间距。例外：有意固定的几何尺寸（图标的像素网格尺寸、静态分隔线）。使用之前某次 `use_figma` 调用创建的变量时，用那次调用返回的真实 Figma 变量 ID，在绑定之前重新取得新的句柄；JavaScript 引用不会跨调用保留。
   用 Plugin API 时，绑定之前先用 `await figma.variables.getVariableByIdAsync(id)` 取得变量。
5. **每个变量都要设作用范围**——**绝不**留着 `ALL_SCOPES`。背景：`FRAME_FILL, SHAPE_FILL`。文字：`TEXT_FILL`。边框：`STROKE_COLOR`。间距：`GAP`。圆角：`CORNER_RADIUS`。基础值：`[]`（隐藏）。
6. **每个变量都要有代码语法**——WEB 语法**必须**用 `var()` 包起来：`var(--color-bg-primary)`，而不是 `--color-bg-primary`。用代码库里真实的 CSS 变量名。ANDROID/iOS **不**用包装。
7. **语义层用别名指向基础值**——`{ type: 'VARIABLE_ALIAS', id: primitiveVar.id }`。绝不要在语义层里重复写原始值。
8. **combineAsVariants 之后要摆放变体**——它们会叠在 (0,0)。手动排成网格 + 调整大小。
9. **图标用 INSTANCE_SWAP**——绝不要每个图标做一个变体。限制变体矩阵：如果 尺寸 × 风格 × 状态 > 30 种组合，就拆成子组件。
10. **确定性的命名**——用一致、唯一的节点名，方便可重复执行的清理和中断后继续。通过返回值和状态账本记录创建的节点 ID。
11. **不做破坏性的清理**——清理脚本要按命名约定或返回的 ID 识别节点，而不是靠猜。
12. **继续之前先根据证据验证**——绝不在没验证过的工作上继续搭建。依靠写操作返回的结构性证据（ID 加上相关的数量、名字和边界）；只在需要确立验收检查、或者某次相关修改让之前的证据失效时，每个连贯阶段才做一次批量的结构审查。每个连贯的构图阶段做一次视觉审查，只在有针对性地修了视觉问题之后再截一张修复后的图。
13. **绝不并行调用 `use_figma`**——修改 Figma 状态必须严格按顺序进行。即使你的工具支持并行调用，也绝不要同时运行两次 use_figma 调用。
14. **绝不编造节点 ID**——永远从之前调用返回的状态账本里读 ID。绝不凭记忆重建或猜一个 ID。
15. **用辅助脚本**——把 `scripts/` 里的脚本嵌进你的 use_figma 调用。不要从零手写 200 行的内联脚本。

---

## 4. 状态管理（长工作流程必须做）

> 不要把工作流程的状态存在 Figma 对象上。用确定性的名字来查找，并在状态账本里记下返回的确切 ID。把给人看的组件用途和使用说明写在组件或组件集的 `description` 里。

| 实体类型 | 稳定的身份标识 | 怎样检查是否存在 |
|-------------|----------------|----------------------|
| 页面和框 | 确定性的名字 + 状态账本里的 ID | `figma.root.children.find(p => p.name === pageName)` 或 `await figma.getNodeByIdAsync(id)` |
| 组件和组件集 | 变体/集合的名字 + 状态账本里的 ID | `page.findOne(n => n.name === name)` 或 `await figma.getNodeByIdAsync(id)` |
| 变量 | 集合内的名字 | `(await figma.variables.getLocalVariablesAsync()).find(v => v.name === name && v.variableCollectionId === collId)` |
| 样式 | 名字 | `getLocalTextStyles().find(s => s.name === name)` |

每次创建之后，立刻把返回的每个 ID 记进状态账本。绝不要用模糊查找来决定删除什么。

**状态持久化**：**不要**只靠对话上下文保存状态账本。把它写到磁盘上：
```
/tmp/design-system-state-{RUN_ID}.json
```
每一轮开始时都重新读这个文件。在长工作流程里，对话上下文会被截断——这个文件才是可信来源。

维护一个状态账本，记录：
```json
{
  "runId": "ds-build-2024-001",
  "scope": "single-component",
  "step": "component-button",
  "entities": {
    "collections": { "primitives": "id:...", "color": "id:..." },
    "variables": { "color/bg/primary": "id:...", "spacing/sm": "id:..." },
    "pages": { "Cover": "id:...", "Button": "id:..." },
    "components": { "Button": "id:..." }
  },
  "pendingValidations": ["Button:screenshot"],
  "completedSteps": ["discovery", "foundations/verified", "component-button/base"]
}
```

每次创建之前做**幂等检查**：按名字 + 状态账本里的 ID 查询。如果已经存在，就跳过或更新——绝不重复创建。

**恢复流程**：会话开始时或上下文被截断之后，运行一个只读的 `use_figma`，按名字扫描所有页面、组件、变量和样式，重建 `{key → id}` 映射。然后如果有的话，从磁盘重新读状态文件。

**继续用的提示语**（在新对话里继续时交给用户）：
> "I'm continuing a design system build. Run ID: {RUN_ID}. Load the Figma设计系统 skill and resume from the last completed step."

（意思是：“我在继续搭建一个设计系统。运行 ID：{RUN_ID}。加载 Figma设计系统 skill，从最后完成的那一步继续。”这句提示语保持英文原文，方便直接复制使用。）

---

## 5. 查找组件库和 search_design_system——复用决策表

在按范围调研的那一轮里搜索，并复用结果。只有当某个组件不在最初的清单里、可用的组件库变了，或者之前的结果没能解决它时，才在做这个组件之前再搜索一次。

在为某个目标文件调用 `search_design_system` 之前，你**必须**先为那个文件调用 `get_libraries`。你**不能**假设组件库已经添加或可用。

`get_libraries` 返回空结果，**不能**成为跳过搜索的理由——它只说明你没有可以用来限定范围的库 key。`get_libraries` 是分页的（社区 UI 套件只出现在第一页，组织的组件库每页 20 个），所以空列表不能证明没有组件库。根据结果这样做：

- **返回了组件库**——运行 `search_design_system`，用 `includeLibraryKeys` 限定范围。`libraries_available_to_add` 里的组件库默认**不会**被搜索；要搜到它们，把它们的 `libraryKey` 传进去。
- **没有返回组件库**——仍然运行 `search_design_system`，但省略 `includeLibraryKeys`。省略它会把搜索范围限定在文件本身，这正是调研没找到任何可用来限定范围的东西时你想要的。

只有当搜索本身返回空结果时，你才可以在差距分析里记下“没有可用的设计系统资产”，并根据代码里的令牌来搭建。绝不要根据一次失败的或者没尝试过的 `get_libraries` 调用，就推断“没有组件库”。

```
// Discover all libraries accessible to the file
get_libraries({ fileKey })
// Returns:
//   libraries_added_to_file: [{ name, libraryKey, description, source }, ...]
//   libraries_available_to_add: [{ name, libraryKey, description, source }, ...]
//   libraries_available_to_add_next_offset: number | null
```

（代码注释意思：查找文件能访问的所有组件库；返回：已添加到文件的库、可以添加的库、可以添加的库的下一页偏移量。）

用返回的 `libraryKey` 值，通过 `includeLibraryKeys` 把搜索限定在特定的组件库里。可用的组件库很多时，这能避免结果太杂。

如果 `libraries_available_to_add_next_offset` 不是 null，说明还有更多组织组件库——把 `offset` 设成那个值，再调用一次 `get_libraries`。组织组件库每页 20 个；社区 UI 套件只出现在第一页。

```
// Search across all libraries (default)
search_design_system({
  queries: [
    { entity: "component", query },
    { entity: "variable", query },
    { entity: "style", query }
  ],
  fileKey
})

// Search within a specific library only
search_design_system({ queries: [{ entity: "component", query }], fileKey, includeLibraryKeys: ["lk-abc123..."] })
```

（代码注释意思：在所有组件库里搜索（默认）；只在某个特定的组件库里搜索。）

满足下面**全部**条件时**复用**：
- 组件的属性 API 符合你的需要（相同的变体维度、兼容的类型）
- 令牌绑定模型兼容（用的是相同的或可以加别名的变量）
- 命名约定和目标文件一致
- 组件是可以编辑的（没有锁在一个你不拥有的远程组件库里）

出现下面**任意一条**时**重建**：
- API 不兼容（属性名不同、变体模型不对）
- 令牌模型不兼容（写死的值、不同的变量结构）
- 所有权问题（不能修改那个组件库）

视觉上一致但 API 不兼容时**包一层**：
- 把组件库里的组件作为嵌套实例导入到一个新的包装组件里
- 在包装组件上暴露一个干净的 API

**优先顺序**：本地已有的 → 导入已订阅的组件库 → `libraries_available_to_add` 里未订阅的 UI 套件组件库（尤其是图标）→ 新建。

---

## 6. 决策分岔

当路径出现分岔时——当存在两个或更多合理的答案，而代码库、Figma 文件或锁定的计划里都看不出明显的胜者时——问用户。不要悄悄用默认值。把每个选项连同它的取舍和你的推荐一起列出来；等用户给了方向再选。

**什么时候不要问：** 如果根据可信来源（代码、Figma 文件、约定的计划）明显只有一条路是对的，就走那条路。这一节是为了真正的模糊不清，不是为了把每个决定都推给用户。

| 分岔的情况 | 要列出什么 | 提问的例子 |
|---|---|---|
| 某个令牌、组件或值上代码 ≠ Figma | 两个版本并排，附上出处（文件/行号 对比 节点） | “代码里是 `--color-bg-primary = #FFFFFF`，Figma 里是 `color/bg/primary = #FAFAFA`。以哪个为准？” |
| 已订阅的组件库里有一个接近但不完全匹配的 | 组件库组件的概况 + 差距列表 | “组件库里有 `Button`，但没有 `loading` 状态。复用并在本地包一层，还是从零重建？” |
| 锁定计划时（0d）范围不明确 | 哪些明显在内、哪些明显在外、哪些不明确 | “规格里列了 `Button` 和 `Input`；`Field` 被提到了但没有定义。放进 v1 还是不放？” |

**如果用户否决了一个你已经在上面搭建了东西的选项：** 先修好再往下走。绝不在被否决的工作上继续搭建。

---

## 7. 命名约定

和文件已有的约定保持一致。如果是从零开始：

**变量**（用斜杠分隔）：
```
color/bg/primary     color/text/secondary    color/border/default
spacing/xs  spacing/sm  spacing/md  spacing/lg  spacing/xl  spacing/2xl
radius/none  radius/sm  radius/md  radius/lg  radius/full
typography/body/font-size    typography/heading/line-height
```

**基础值**：`blue/50` → `blue/900`，`gray/50` → `gray/900`

**组件名**：`Button`、`Input`、`Card`、`Avatar`、`Badge`、`Checkbox`、`Toggle`

**变体名**：`Property=Value, Property=Value`——例如 `Size=Medium, Style=Primary, State=Default`

**页面分隔符**：`---`（最常见）或 `——— COMPONENTS ———`

> 完整的命名参考：[naming-conventions.md](references/naming-conventions.md)

---

## 8. 令牌架构

| 复杂度 | 模式 |
|-----------|---------|
| < 50 个令牌 | 一个集合，2 个模式（Light/Dark） |
| 50–200 个令牌 | **标准**：Primitives（1 个模式）+ Color 语义（Light/Dark）+ Spacing（1 个模式）+ Typography（1 个模式） |
| 200+ 个令牌 | **进阶**：多个语义集合，4–8 个模式（Light/Dark × 对比度 × 品牌）。见 [token-creation.md](references/token-creation.md) 里的 M3 模式 |

标准模式（推荐的起点）：
```
Collection: "Primitives"    modes: ["Value"]
  blue/500 = #3B82F6, gray/900 = #111827, ...

Collection: "Color"         modes: ["Light", "Dark"]
  color/bg/primary → Light: alias Primitives/white, Dark: alias Primitives/gray-900
  color/text/primary → Light: alias Primitives/gray-900, Dark: alias Primitives/white

Collection: "Spacing"       modes: ["Value"]
  spacing/xs = 4, spacing/sm = 8, spacing/md = 16, ...
```

---

## 9. 反面模式

**调研和范围：**
- ❌ 无视已有的约定，或者跳过相关的代码、文件和组件库调研
- ❌ 把一个窄的请求扩大成不相关的基础、文档或一整个组件库

**基础：**
- ❌ 用 `ALL_SCOPES`、在语义层里重复基础值，或者漏掉代码语法
- ❌ 在基础还不存在时就创建依赖它们的组件

**组件：**
- ❌ 有兼容的变量时，还在组件上写死填充、描边、间距或圆角
- ❌ 每个图标做一个变体，而不是用 INSTANCE_SWAP
- ❌ `combineAsVariants` 之后让变体一直叠在 (0,0)
- ❌ 搭建超过 30 种组合的变体矩阵而不拆分
- ❌ 导入远程组件后马上把它们分离（detach）

**执行和恢复：**
- ❌ 在 `safeToRetryWithoutCanvasRead` 为 `false` 时，没先读画布就重试
- ❌ 用名字前缀匹配来清理（会删掉用户自己的节点）
- ❌ 在上一步没验证过的工作上继续搭建
- ❌ 并行调用 use_figma（永远按顺序）
- ❌ 凭记忆猜/编造节点 ID（永远从状态账本里读）
- ❌ 写巨大的内联脚本，而不是用提供的辅助脚本

---

## 10. 参考文档

按需阅读参考文件；不要根据文件名去推断它们的内容。

| 文档 | 什么时候加载 |
|-----|-----------|
| [discovery-phase.md](references/discovery-phase.md) | 在修改之前分析相关的代码和 Figma 资产 |
| [token-creation.md](references/token-creation.md) | 创建变量、集合、模式或样式 |
| [documentation-creation.md](references/documentation-creation.md) | 选定的范围包括封面或基础规范文档 |
| [component-creation.md](references/component-creation.md) | 创建一个组件或变体 |
| [code-connect-setup.md](references/code-connect-setup.md) | 选定的范围包括 Code Connect 或变量的代码语法 |
| [naming-conventions.md](references/naming-conventions.md) | 给变量、页面、变体或样式命名 |
| [error-recovery.md](references/error-recovery.md) | 某个脚本失败了，或者废弃的工作流程状态需要清理 |

---

## 11. 脚本

可复用的 Plugin API 辅助函数。嵌进 `use_figma` 调用里：

| 脚本 | 用途 |
|--------|---------|
| [inspectFileStructure.js](scripts/inspectFileStructure.js) | 查找所有页面、组件、变量、样式；返回完整清单 |
| [createVariableCollection.js](scripts/createVariableCollection.js) | 创建一个带模式的命名集合；返回 `{collectionId, modeIds}` |
| [createSemanticTokens.js](scripts/createSemanticTokens.js) | 根据令牌映射创建带别名的语义变量 |
| [createComponentWithVariants.js](scripts/createComponentWithVariants.js) | 根据变体矩阵搭建一个组件集；处理网格布局 |
| [bindVariablesToComponent.js](scripts/bindVariablesToComponent.js) | 把设计令牌绑定到组件的所有视觉属性上 |
| [createDocumentationPage.js](scripts/createDocumentationPage.js) | 创建一个带标题 + 说明 + 分节结构的页面 |
| [validateCreation.js](scripts/validateCreation.js) | 核实创建的节点符合预期的数量、名字、结构 |
| [cleanupOrphans.js](scripts/cleanupOrphans.js) | 只删除状态账本里提供的那些确切的节点、变量和集合 ID |
