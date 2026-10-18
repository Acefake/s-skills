---
name: Figma插件基础
description: "**必须先做的前置步骤**——每次调用 `use_figma` 工具之前，你都必须先调用这个 skill。绝不要不加载这个 skill 就直接调用 `use_figma`。跳过它会导致常见、又很难排查的失败。只要用户想执行一个写操作，或者一个需要在 Figma 文件上下文里执行 JavaScript 的特殊读操作，就触发——例如创建/编辑/删除节点、设置变量或设计令牌、搭建组件和变体、修改自动布局或填充、把变量绑定到属性上，或者用程序检查文件结构。"
disable-model-invocation: false
---

> 翻译自 Figma 官方仓库 https://github.com/figma/mcp-server-guide （skills/figma-use，commit f278942）的 `figma-use` skill，原作者 Figma，许可证：未注明许可证（仓库里没有找到 LICENSE 文件），仅供自用。
> 说明：参考文件 `references/`（包括很大的 `plugin-api-standalone.d.ts` 类型文件和 `working-with-design-systems/` 文件夹）保留英文原文 ⚠️。下面要求在 `skillNames` 里写的是原名 `figma-use`（给 Figma 做使用统计用），保持原样。链接里的 `../figma-generate-design/...`、`../figma-generate-library/...`、`../figma-use-slides/...` 已经改成指向 `Figma搭建页面`、`Figma设计系统`、`Figma幻灯片` 这几个中文名文件夹，正文里提到的其他 skill 也换成了中文名。代码保持原样，代码注释的意思在后面用中文说明。
> 英文名备份：s-figma-use

# use_figma —— Figma 插件 API skill

用 `use_figma` 工具通过 Plugin API 在 Figma 文件里执行 JavaScript。所有详细的参考文档都在 `references/` 里。

**调用 `use_figma` 时，一定要在用逗号分隔的 `skillNames` 参数里加上 `figma-use`。如果这个 skill 是通过 MCP 资源加载的，必须在名字前面加上 `resource:`（例如 `resource:figma-use`）。** 这是一个用来统计 skill 使用情况的日志参数——它不影响执行。

**如果 Figma MCP 工具显示为延迟加载的工具，用一次 `ToolSearch` 调用批量加载它们所有的结构定义**，用 `select:` 语法——例如 `ToolSearch query="select:use_figma,get_screenshot,get_metadata,create_new_file"`。一次来回胜过六次。

**做看得见的设计修改时必须这样：** 在第一次做修改的 `use_figma` 调用之前，和这个 skill 一起加载 [figma-generate-design](../Figma搭建页面/SKILL.md)，并在每次修改调用的 `skillNames` 里写上两个名字。从改一个看得见的属性或元素，到一整个页面、屏幕或由多个部分组成的视图，都适用——即使用户把那个视图叫作组件。`figma-use` 提供 Plugin API 的规则；`figma-generate-design` 提供通过 `search_design_system` 查找设计系统、导入素材，以及逐步拼装的方法。

**可复用组件库的例外：** 如果主要交付物是一个可复用的组件、组件集、变体体系、变量/令牌集合、样式基础，或者其他打算复用或发布的组件库资产，改为加载 [Figma设计系统](../Figma设计系统/SKILL.md)。它提供了 `Figma插件基础` 单独不覆盖的组件创建工作流程——变量基础、变体集和设计令牌绑定。如果任务既包括组件库资产、又包括用到它们的拼装设计，两个配套 skill 都加载。只读的 `use_figma` 调用两个都不需要。

做任何事之前，先加载 [plugin-api-standalone.index.md](references/plugin-api-standalone.index.md)，了解能做什么。当你被要求写 plugin API 代码时，利用这个上下文去 [plugin-api-standalone.d.ts](references/plugin-api-standalone.d.ts) 里搜索相关的类型、方法和属性。它是 API 范围的最终可信来源。它是一个很大的类型文件，所以不要一次全部加载，按需搜索相关的部分。

重要：只要你在处理设计系统，就从 [working-with-design-systems/wwds.md](references/working-with-design-systems/wwds.md) 开始，了解在 Figma 里处理设计系统的关键概念、流程和指南。然后按需加载关于组件、变量、文字样式和效果样式的更具体的参考文件。

## 1. 关键规则
1.  **用 `return` 把数据传回去。** 返回值会自动做 JSON 序列化（对象、数组、字符串、数字）。**不要**调用 `figma.closePlugin()`，也不要把代码包在 async 立即执行函数里——这些会替你处理。
2.  **写普通的 JavaScript，可以在顶层用 `await` 和 `return`。** 代码会自动被包进一个 async 上下文。**不要**包在 `(async () => { ... })()` 里。
3.  `figma.notify()` **会抛出 "not implemented"（未实现）**——绝不要用
3a. **返回节点 ID，把工作流程状态放在 Figma 文件之外。** 给人看的组件用途和使用说明，只写在 `COMPONENT` 或 `COMPONENT_SET` 的 `node.description` 里——绝不要写在框或实例上。
3b. **访问特定类型的属性之前，先收窄类型。** 检查 `node.type`，用 `"characters" in node` 这样的能力判断，或者用 `findAllWithCriteria` 预先筛选。`characters` 需要一个能放文字的节点；可选链（?.）不能防止访问不支持的属性。
4.  `console.log()` 的内容**不会**返回——用 `return` 输出
5.  **按“可以安全重试”来决定每次搭建调用的大小，并根据证据验证。** 不要只为了制造验证检查点就拆开一个能正常工作的操作。当合并后的脚本仍然可以安全重试时，把相关的工作批量处理；一个完整的部分或页面可以在一次调用里搭完。在跨越页面上下文、部分执行后很难恢复，或者真正失败后需要有针对性地重试时，再拆分。每次写操作都返回受影响的 ID 和相关的数量、名字或边界——这就算结构验证。只在缺少必要证据、或者在一次相关修改之后，才单独做结构检查。通常拼装完截一次图，修完视觉问题后再截一次。最近一张通过的截图就是最终检查；如果没有相关的变化，不要重复截图。满足要求就停下。
6.  颜色是 **0–1 的范围**（不是 0–255）：`{r: 1, g: 0, b: 0}` = 红色。填充的 `color` 对象**只用** `{r, g, b}`——**没有 `a` 字段**；不透明度放在填充这一层（`{ type: 'SOLID', color: {...}, opacity: 0.5 }`）。
7.  填充/描边是**只读数组**——复制、修改、再重新赋值
8.  **每次编辑文字都按标准做法来：加载字体 → `await` → 修改 → 返回受影响的节点 ID。** 跳过加载会抛出 `Cannot write to node with unloaded font "<family> <style>"`。这条规则不只针对 `characters`——它适用于对字体没加载的节点做的任何操作（`appendChild`、`insertChild`、`setBoundVariable`、`setExplicitVariableModeForCollection`、`setValueForMode`、碰到文字的 `findAll` 回调）。修改已有的文字时，通过 `getStyledTextSegments(['fontName'])` 加载节点*当前*的字体，而不是一个写死的默认字体。大多数环境里 Inter 是预先加载好的，所以用其他字体家族时更容易暴露这个 bug——每种字体的做法都一样。如果样式字符串没核实过，先用 `await figma.listAvailableFontsAsync()`——**绝不要猜**（`"SemiBold"` 和 `"Semi Bold"` 是常见的坑）。对于作用范围是 `FONT_FAMILY` 的变量，在 `setBoundVariable("fontFamily", …)`、`setValueForMode` 或 `setExplicitVariableModeForCollection` 之前，加载每个相关模式里的每个值。`lineHeight`/`letterSpacing` 接收 `{unit, value}`，不是光秃秃的数字。见 [标准的文字编辑做法](references/gotchas.md#canonical-text-edit-recipe-font-load--await--mutate--return-ids)。
9.  **页面是逐步加载的**——用 `await figma.setCurrentPageAsync(page)` 切换页面并加载它的内容。同步的写法 `figma.currentPage = page` **不能用**，会抛出 `"Setting figma.currentPage is not supported"`。每次 `use_figma` 调用开始时，页面上下文都会重置到**第一个页面**，所以每次调用都要重新切换；**每次调用最多切换一次**，多页面的工作要并行分发——见 [页面规则](#2-页面规则关键) 和 [gotchas.md](references/gotchas.md#set-current-page-once-per-use_figma-call--split-multi-page-work-into-parallel-calls)。
10. `setBoundVariableForPaint` 返回一个**新的**填充——必须接住它并重新赋值
11. `createVariable` 接受集合的**对象或 ID 字符串**（优先用对象）
12. **`layoutSizingHorizontal/Vertical` 能取什么值受结构上下文限制——`FIXED` 总是可以，`HUG` 和 `FILL` 不一定。** `'HUG'` 只在自动布局框本身、或者它的 **TEXT** 子节点上有效。`'FILL'` 只在自动布局框的子节点上有效，而且这个子节点不能是绝对定位的、不能在不可变的框里、也不能是画布网格的子节点。实际的结论：**先**添加到一个自动布局的父节点里，再设置 `HUG`/`FILL`——新建的或者还没有父节点的节点还满足不了这条规则。这个属性本身在每个 `SceneNode` 上都存在；报错是值被拒绝，而不是“没有这个属性”。见 [常见坑](references/gotchas.md#layoutsizinghorizontallayoutsizingvertical-value-rules-fixed-hug-fill)。
12a. **装着相关子元素的容器要用自动布局。** 当子元素之间有结构关系时——上下堆叠、左右并排、对齐、有间距、贴合内容——用 `figma.createAutoLayout()` 把它们包起来，而不是用带绝对 `x`/`y` 的 `figma.createFrame()`。绝对坐标决定容器放在画布的什么位置；自动布局决定容器里的子元素之间是什么关系。不用容器的话，文字重新排版、内容变化或重叠时就没有任何保护。
12b. **`layoutSizing*` 和 `*AxisSizingMode` 是两套不同的枚举——不要混用。** `layoutSizingHorizontal`/`layoutSizingVertical`（设在**子节点**上）接收 `'FIXED'|'HUG'|'FILL'`；`primaryAxisSizingMode`/`counterAxisSizingMode`（设在**框**本身上）接收 `'FIXED'|'AUTO'`。所以 `layoutSizingVertical = 'AUTO'` 是无效的（用 `'HUG'`），`counterAxisSizingMode = 'FILL'` 会抛出 `Expected 'FIXED' | 'AUTO', received 'FILL'`（用 `'FIXED'`/`'AUTO'`）。同一个设置方法还有两个错误——`Error: in set_layoutSizingHorizontal: node must be an auto-layout frame or a child of an auto-layout frame` 和 `Error: in set_layoutSizingHorizontal: FILL can only be set on children of auto-layout frames`——意思是节点还不在自动布局的上下文里；**建议：把父节点做成自动布局（`figma.createAutoLayout()`），并在设置之前先 `appendChild` 这个节点**（见第 12 条规则）。见 [常见坑](references/gotchas.md#layoutsizing-vs-axissizingmode-two-different-sizing-enums)。
12c. **`resize()` 会把尺寸模式重置成 `FIXED`，所以要在设置 `layoutSizing*` 之前调用它。** 一个会自动换行的 **TEXT** 块需要 `textAutoResize = 'HEIGHT'` 加上一个明确的 FIXED 宽度（`resize()`），而**不是**只设 `FILL`——默认的 `WIDTH_AND_HEIGHT` 模式会忽略 `FILL`，把节点压成一条几乎零宽度的细线。之后确认 `node.width > 0`。
13. **新的顶层节点不要放在 (0,0)。** 直接添加到页面上的节点默认在 (0,0)。扫描 `figma.currentPage.children` 找一个空的位置（例如最右边那个节点的右边）。这只适用于页面级的节点——嵌套在其他框或自动布局容器里的节点由父节点定位。见 [常见坑](references/gotchas.md)。
14. **`use_figma` 出错时，遵守 `safeToRetryWithoutCanvasRead`。** 如果是 `true`，修好错误再重试。如果是 `false`，先读画布，弄清楚变了什么，再做修改。见 [错误恢复](#7-错误恢复和自我修正)。
15. **必须 `return` 所有创建/修改过的节点 ID。** 只要脚本在画布上创建了新节点或修改了已有节点，就收集每个受影响的节点 ID，放在一个结构化的对象里返回（例如 `return { createdNodeIds: [...], mutatedNodeIds: [...] }`）。后续调用要引用、验证或清理这些节点，这一点必不可少。`use_figma` 调用之间不保留任何状态，所以要把之前调用拿到的 ID 作为**字符串字面量**传进去，而不是变量。多步骤的完整例子见 [common-patterns.md](references/common-patterns.md)。
16. **创建变量时一定要明确设置 `variable.scopes`。** 默认的 `ALL_SCOPES` 会出现在每个属性选择器里——几乎从来不是你想要的。用具体的作用范围，比如背景用 `["FRAME_FILL", "SHAPE_FILL"]`，文字颜色用 `["TEXT_FILL"]`，间距用 `["GAP"]` 等。完整列表见 [variable-patterns.md](references/variable-patterns.md)。
17. **每个 Promise 都要 `await`。** 绝不要留下没 await 的 Promise——没 await 的异步调用（例如没加 `await` 的 `figma.loadFontAsync(...)`，或者没加 `await` 的 `figma.setCurrentPageAsync(page)`）会“发出去就不管了”，造成悄无声息的失败或竞争条件。脚本可能在异步操作完成之前就返回了，导致数据缺失或改动只做了一半。
18. **绝不要从一个变体组件上读取 `componentPropertyDefinitions`。** 先找准真正的拥有者：如果节点本身是 `COMPONENT_SET`，就用它；只有当一个 `COMPONENT` 的父节点不是 `COMPONENT_SET` 时才用这个 `COMPONENT`；否则把变体 `COMPONENT` 提升到它的父组件集。可选链不能让这个 getter 变安全。见 [组件属性拥有者的收窄](references/component-patterns.md#component-property-owner-narrowing)。
> 每条规则详细的 WRONG/CORRECT（错误/正确）例子，见 [常见坑和常见错误](references/gotchas.md)。

## 2. 页面规则（关键）

只能异步设置页面，以及每次调用都会重置上下文，这两点在第 9 条规则里讲了。这一节展开讲那条需要完整例子的规则：**每个脚本最多切换一次页面，多页面的工作要并行分发。**

绝不要遍历 `figma.root.children` 并在循环里切换页面——每次切换都会重新加载文件。如果工作跨越多个页面，**把它拆成 N 次 `use_figma` 调用（每个目标页面一次），并行发出**——在一条助手消息里放 N 个 `use_figma` 工具调用块。运行环境会同时执行它们；每个脚本只设置一次 `currentPage`。

> **明确的指示：** 并行分发时，你**必须**在**一条消息**里发出这 N 个工具调用。不要分成好几轮发。不要等一个完成再发下一个。按页面一个接一个地调用，会让拆分的好处全部白费。

```js
// AVOID — switches pages N times in one script, reloads the file each time
for (const page of figma.root.children) {
  await figma.setCurrentPageAsync(page);
  // ... touch this page ...
}

// PREFER — read-only discovery call to get page IDs, then in the NEXT message
// emit N parallel use_figma tool calls (one per page), each setting currentPage once.
```

（代码注释意思：AVOID（避免）——在一个脚本里切换 N 次页面，每次都重新加载文件；PREFER（推荐）——先用一次只读的调用拿到页面 ID，然后在下一条消息里并行发出 N 个 use_figma 工具调用（每页一个），每个只设置一次 currentPage。）

任何多页面的工作都默认并行分发——读和写都一样。你也可以多次调用 `use_figma` 来逐步搭建（例如先 `return` 已有节点的元数据，然后在后续脚本里修改它们）。完整的理由见 [gotchas.md → Set current page once per `use_figma` call](references/gotchas.md#set-current-page-once-per-use_figma-call--split-multi-page-work-into-parallel-calls)。

## 3. `return` 是你的输出通道

AI 助手**只**能看到你 `return` 的值——`console.log()` 是看不见的（第 4 条规则），抛出的错误会被自动捕获（让它们往上传，或者明确地 `throw`）。硬性要求是第 15 条规则：每个创建或修改画布节点的脚本，都**必须**在一个结构化对象里返回所有受影响的节点 ID，加上任何可以据此行动的状态——例如 `return { createdNodeIds: [...], mutatedNodeIds: [...], count: 5, errors: [] }`——这样后续调用才能引用、验证或清理它们。

## 4. 编辑器模式

`use_figma` 在**设计模式**下工作（editorType 为 `"figma"`，默认）。FigJam（`"figjam"`）和 Slides（`"slides"`）能用的节点类型不一样——大多数设计节点在 FigJam 里被禁用，FigJam 专用的节点在 Slides 里被禁用。

**从网址判断编辑器：** Design = `figma.com/design/...`，FigJam = `figma.com/board/...`，Slides = `figma.com/slides/...`。在假设某个 API 可用之前先确认。

设计模式下可用：Rectangle、Frame、Component、Text、Ellipse、Star、Line、Vector、Polygon、BooleanOperation、Slice、Page、Section、TextPath。

设计模式下**禁用**：Sticky、Connector、ShapeWithText、CodeBlock、Slide、SlideRow、SlideGrid、InteractiveSlideElement、Webpage。

Slides 模式下可用：Rectangle、Frame、Component、Text、Ellipse、Star、Line、Vector、Polygon、BooleanOperation、Slice、Section、TextPath、Slide、SlideRow、SlideGrid、InteractiveSlideElement。

Slides 模式下**禁用**：Sticky、Connector、ShapeWithText、CodeBlock、Webpage、Page。

**只能在 Design 文件里用的 API（不只是节点类型）：** `figma.createPage()` 只在 Design 文件（`figma.com/design/...`）里可用。在 FigJam（`figma.com/board/...`）和 Slides（`figma.com/slides/...`）里，它都会抛出 `TypeError: figma.createPage no such property 'createPage' on the figma global object`。不要在 FigJam 或 Slides 的工作流程里写 `figma.createPage()`。

> **Slides 说明：** 目前还没有专门读取 Slides 文件的工具。用带只读脚本的 `use_figma` 来检查（见第 6 节的“先检查”做法），用 `get_screenshot` / `await node.screenshot()` 获取视觉上下文。Slides 专用的 API 指导，加载 [Figma幻灯片](../Figma幻灯片/SKILL.md) skill。

## 5. 高效的 API——优先用这些，而不是啰嗦的写法

这些 API 能减少样板代码、消除顺序错误、压缩输出的 token。**永远优先用它们，而不是啰嗦的写法。**

### `node.query(selector)`——类似 CSS 的节点搜索

用类似 CSS 的选择器在一棵子树里查找节点。取代啰嗦的 `findAll` + 筛选循环。

```js
// BEFORE — verbose traversal
const texts = frame.findAll(n => n.type === 'TEXT' && n.name === 'Title')

// AFTER — one-liner with query
const texts = frame.query('TEXT[name=Title]')
```

（代码注释意思：BEFORE（之前）——啰嗦的遍历；AFTER（之后）——用 query 一行搞定。）

**选择器语法：**
- 类型：`FRAME`、`TEXT`、`RECTANGLE`、`ELLIPSE`、`COMPONENT`、`INSTANCE`、`SECTION`（不区分大小写）
- 属性完全匹配：`[name=Card]`、`[visible=true]`、`[opacity=0.5]`
- 属性部分匹配：`[name*=art]`（包含）、`[name^=Header]`（开头是）、`[name$=Nav]`（结尾是）
- 点路径遍历：`[fills.0.type=SOLID]`、`[fills.*.type=SOLID]`（通配下标）
- 实例匹配：`[mainComponent=nodeId]`、`[mainComponent.name=Button]`
- 组合符：`FRAME > TEXT`（直接子节点）、`FRAME TEXT`（任意后代）、`A + B`（紧邻的兄弟）、`A ~ B`（后面的任意兄弟）
- 伪类：`:first-child`、`:last-child`、`:nth-child(2)`、`:not(TYPE)`、`:is(FRAME, RECTANGLE)`、`:where(TEXT, ELLIPSE)`
- 节点 ID：`#nodeId` 或者直接写 GUID
- 逗号：`TEXT, RECTANGLE`（并集）
- 通配符：`*`（任意类型）

**QueryResult 的方法：**
| 方法 | 说明 |
|---|---|
| `.length` | 匹配到的节点数量 |
| `.first()` | 第一个匹配的节点（或 `null`） |
| `.last()` | 最后一个匹配的节点（或 `null`） |
| `.toArray()` | 转成普通数组 |
| `.each(fn)` | 用回调遍历，返回 `this` 方便链式调用 |
| `.map(fn)` | 映射成新数组 |
| `.filter(fn)` | 筛选成新的 QueryResult |
| `.values(keys)` | 取出属性值：`.values(['name', 'x', 'y'])` → `[{name, x, y}, ...]` |
| `.set(props)` | 给所有匹配的节点设置属性（见下面的 `node.set()`） |
| `.query(selector)` | 在匹配的节点里再查询 |
| `for...of` | 可迭代——能用在 `for` 循环里 |

**范围：** `node.query()` 在那个节点的子树里搜索。要搜索整个页面：`figma.currentPage.query('...')`。没有全局的 `figma.query()`。

**例子：**
```js
// Recolor all text inside cards
figma.currentPage.query('FRAME[name^=Card] TEXT').set({
  fills: [{type: 'SOLID', color: {r: 0.2, g: 0.2, b: 0.8}}]
})

// Get names and positions of all frames
return figma.currentPage.query('FRAME').values(['name', 'x', 'y'])

// Find the first component named "Button"
const btn = figma.currentPage.query('COMPONENT[name=Button]').first()

// Find all instances of a specific component
figma.currentPage.query(`INSTANCE[mainComponent=${compId}]`)

// Find nodes with solid fills using dot-path traversal
figma.currentPage.query('[fills.0.type=SOLID]')
```

（代码注释意思：给卡片里的所有文字换颜色；获取所有框的名字和位置；找到第一个名叫 "Button" 的组件；找到某个组件的所有实例；用点路径遍历找到有纯色填充的节点。）

### `node.set(props)`——批量更新属性

一次调用设置多个属性。返回 `this` 方便链式调用。

```js
// BEFORE — one line per property
frame.opacity = 0.5
frame.cornerRadius = 8
frame.name = "Card"

// AFTER — single call
frame.set({ opacity: 0.5, cornerRadius: 8, name: "Card" })
```

（代码注释意思：BEFORE（之前）——每个属性一行；AFTER（之后）——一次调用。）

**优先的键顺序：** 不管对象里键的顺序如何，`layoutMode` 总是先于其他属性（比如 `width`/`height`）被应用。这能避免一个常见的 bug：`resize()` 的表现取决于 `layoutMode` 有没有设置。

**宽高的处理：** `width` 和 `height` 会自动通过 `node.resize()` 设置——设置 `{ width: 200 }` 会调用 `resize(200, currentHeight)`。

**和 query 链式调用：**
```js
// Find all rectangles named "Divider" and update them
figma.currentPage.query('RECTANGLE[name=Divider]').set({
  fills: [{type: 'SOLID', color: {r: 0.9, g: 0.9, b: 0.9}}],
  cornerRadius: 2
})
```

（代码注释意思：找到所有名叫 "Divider" 的矩形并更新它们。）

### `figma.createAutoLayout(direction?, props?)`——自动布局框

创建一个已经开启自动布局、两个方向都贴合内容的框。**只要子元素之间有结构关系，这就是默认的容器（见第 12a 条规则）。**

```js
// BEFORE — manual setup, easy to get ordering wrong
const frame = figma.createFrame()
frame.layoutMode = 'VERTICAL'
frame.primaryAxisSizingMode = 'AUTO'
frame.counterAxisSizingMode = 'AUTO'
frame.layoutSizingHorizontal = 'HUG'
frame.layoutSizingVertical = 'HUG'

// AFTER — one call, layout ready
const frame = figma.createAutoLayout('VERTICAL')
```

（代码注释意思：BEFORE（之前）——手动设置，很容易把顺序弄错；AFTER（之后）——一次调用，布局就绪。）

子节点添加进去后，马上就能用 `layoutSizingHorizontal/Vertical = 'FILL'`——不需要手动设置尺寸模式。

第一个或第二个参数可以是一个可选的属性对象：
```js
figma.createAutoLayout({ name: 'Card', itemSpacing: 12 })               // HORIZONTAL + props
figma.createAutoLayout('VERTICAL', { name: 'Column', itemSpacing: 8 })  // VERTICAL + props
```

（代码注释意思：第一行是水平方向 + 属性；第二行是垂直方向 + 属性。）

### `node.placeholder`——表示 AI 正在工作的闪光遮罩

在节点上加一个闪光的视觉遮罩，表示工作正在进行中。**做完一定要去掉闪光**——残留的闪光会让用户困惑，也说明工作没做完。

```js
// Mark as in-progress
frame.placeholder = true

// ... build out the content ...

// MUST remove when done — never leave shimmers on finished nodes
frame.placeholder = false
```

（代码注释意思：标记为进行中；……搭建内容……；做完必须去掉——绝不要在完成的节点上留下闪光。）

搭建复杂布局时，在填充各个部分之前先给它们设 `placeholder = true`，然后每完成一个部分就给它设 `placeholder = false`。

### `await node.screenshot(opts?)`——内联截图

把一个节点截成 PNG，直接内联在返回结果里。不再需要单独调用 `get_screenshot`。

```js
// Take a screenshot of a frame (returned inline in the tool response)
await frame.screenshot()

// Custom scale (default auto-scales: 0.5x or capped so max dimension ≤ 1024px)
await frame.screenshot({ scale: 2 })

// Include overlapping content from sibling nodes
await frame.screenshot({ contentsOnly: false })
```

（代码注释意思：给一个框截图（内联在工具返回结果里）；自定义缩放（默认自动缩放：0.5 倍，或者限制到最大边 ≤ 1024px）；包括兄弟节点里重叠的内容。）

**什么时候用：** 遵守第 5 条规则。需要视觉证据时，截一张拼装后的图。如果之后修了视觉问题，再截一张修复后的图；那张通过的截图就是最终的。不要再额外截一张没有变化的“最终”截图。

**自动命名：** 图片的说明文字包含节点的元数据——`"Card (300x150 at 0,60).png"`——不用分析图片就能知道空间信息。

**默认缩放：** 用 0.5 倍缩放，但会自动限制，让输出的最大边永远不超过 1024px。明确写 `{ scale: N }` 会绕过这个限制。

## 6. 逐步推进的工作流程（怎样避免 bug）

最常见的浪费来自不必要的拆分、多余的验证，以及不能安全重试的脚本。**按第 5 条规则的“安全重试、根据证据验证”约定来做。**

### 关键规则

- **按可恢复性来划分调用边界，而不是按验证节奏。** 安全的时候，把相关的创建、属性更新、挂父节点和有针对性的诊断批量处理。一整个页面可以是一次调用；不要只为了验证每一部分，就把它拆成页头/内容/页脚几次调用。**Slides 的例外：** 在 Slides 文件里，每页幻灯片是独立的子树——要考虑的限制是每页的复杂度，而不是所有幻灯片加起来的节点总数。一次调用搭建 3–5 页新幻灯片是安全的，一次调用对整套幻灯片的每一页做同样的修改（例如加页脚、给标题换颜色）也是安全的。搭建幻灯片的工作流程见 [Figma幻灯片](../Figma幻灯片/SKILL.md)。
- **从上往下搭，先用占位。** 先创建外层结构，每个部分都设 `placeholder = true`，然后在后续调用里逐步用真实内容替换占位。

### 做法

1. **先检查。** 创建任何东西之前，运行一个只读的 `use_figma`，弄清文件里已经有什么——页面、组件、变量、命名约定。和已有的保持一致。
2. **搭骨架。** 用占位的部分创建顶层结构。每个部分都设 `placeholder = true`，让用户看到进展。
3. **按可以安全重试的批次填内容。** 当操作仍然可以安全重试时，多个相关的部分可以一起填。每完成一个部分就把它的 `placeholder` 设成 `false`。
4. **每次调用都返回 ID**（第 15 条规则）——后续调用需要用创建的节点/变量/集合 ID 作为输入。
5. **写操作要返回验证证据。** 返回 ID 和相关的数量、名字、层级或边界。只在缺证据、或者某次修改让之前的证据失效时，才单独加一次审查。视觉检查按第 5 条规则来。
6. **修好再往下走。** 如果验证发现了问题，先修好再进入下一步。不要在坏掉的基础上搭建。

### 复杂任务建议的步骤顺序

```
Step 1: Inspect file — discover existing pages, components, variables, conventions
Step 2: Create tokens/variables (if needed)
       → return collection, variable, and mode counts
Step 3: Create individual components
       → return component IDs and relevant child/variant counts
Step 4: Compose layouts from component instances
       → return layout IDs/bounds + take a composition screenshot
Step 5: Apply a targeted visual fix only if needed
       → take one post-fix screenshot; this is final
Step 6: Stop if nothing relevant changed
```

（意思：第 1 步：检查文件——找出已有的页面、组件、变量、约定；第 2 步：创建令牌/变量（如果需要）→ 返回集合、变量和模式的数量；第 3 步：创建单个组件 → 返回组件 ID 和相关的子节点/变体数量；第 4 步：用组件实例拼装布局 → 返回布局 ID/边界 + 截一张拼装图；第 5 步：只在需要时做有针对性的视觉修复 → 截一张修复后的图，这就是最终的；第 6 步：如果没有相关的变化就停下。）

### 每一步验证什么

| 在……之后 | 用 `get_metadata` 检查 | 用 `get_screenshot` 检查 |
|---|---|---|
| 创建变量 | 集合数量、变量数量、模式名 | — |
| 创建组件 | 子节点数量、变体名、属性定义 | 变体可见、没有塌缩、网格清楚 |
| 绑定变量 | 节点属性反映了绑定 | 颜色/令牌解析正确 |
| 拼装布局 | 实例节点有 mainComponent，层级正确 | 没有被裁掉/截断的文字，没有重叠的元素，间距正确 |

## 7. 错误恢复和自我修正

遇到任何 `use_figma` 错误，都遵守 `safeToRetryWithoutCanvasRead`（第 14 条规则）：`true` → 改正指出的错误并重试，不用额外读画布做诊断；`false` → 先读画布，弄清楚变了什么，再做修改。如果同一个 API 或属性错误出现了两次，查看一次它的定义，修好根本原因再重试；不要围绕同一个无效的修改继续拆分操作。修法已经写在关键规则里的错误，在那里诊断——`"not implemented"`（`figma.notify`，第 3 条规则）、`layoutSizing*` 的 HUG/FILL 被拒绝（第 12、12b 条规则）、`"Setting figma.currentPage is not supported"`（第 9 条规则）、在变体上读 `componentPropertyDefinitions`（第 18 条规则），以及在错误的节点类型上用 `characters`/`description`（第 3a、3b 条规则）。下面几行讲的是约定里没提到的失败：

| 错误信息 | 可能的原因 | 怎样修 |
|---|---|---|
| 属性值超出范围 | 颜色通道 > 1（用了 0–255 而不是 0–1） | 除以 255 |
| `"Cannot read properties of null"` | 节点不存在（ID 错了、页面错了） | 检查页面上下文，核实 ID |
| 脚本卡住 / 没有响应 | 死循环或者没有完成的 promise | 检查有没有 `while(true)` 或漏掉的 `await`；确保代码会结束 |
| `"The node with id X does not exist"` | 父实例因为子节点的 `detachInstance()` 被隐式分离，导致 ID 变了 | 从一个稳定的（非实例的）父框开始遍历，重新找到节点 |

### 脚本成功了，但结果看起来不对时

调用 `get_metadata` 检查结构是否正确（层级、数量、位置），调用 `get_screenshot` 检查视觉是否正确——仔细找被裁掉/截断的文字（行高把内容切掉了）和重叠的元素，这些很常见又容易漏看。判断问题是结构上的还是视觉上的，然后写一个**有针对性的**修复脚本，只改坏掉的部分——不要全部重建。

> 完整的验证工作流程见 [验证和错误恢复](references/validation-and-recovery.md)。

## 8. 提交前的检查清单
提交**任何** `use_figma` 调用之前，对照 [第 1 节](#1-关键规则) 的操作约定重新读一遍脚本。以前在这里一条条列出的检查项现在都在那里——违反其中任何一条的脚本都还不能提交：

- [ ] **输出**——用 `return`（不是 `figma.closePlugin()`），没有包在 async 立即执行函数里，没有用 `console.log()` 当输出；`return` 的是结构化数据，包含所有创建/修改过的节点 ID（第 1、2、4、15 条规则）
- [ ] **颜色和填充**——0–1 的范围；填充的 `color` 只有 `{r, g, b}`（没有 `a`）；填充/描边作为新数组重新赋值（第 6、7 条规则）
- [ ] **类型收窄**——访问 `characters`、`description` 和 `componentPropertyDefinitions` 之前先做了判断/收窄（第 3a、3b、18 条规则）
- [ ] **页面**——切换用 `await figma.setCurrentPageAsync(page)`，每次调用最多一次（第 9 条规则）
- [ ] **布局和尺寸**——相关的子元素放在 `figma.createAutoLayout()` 里；顶层节点不放在 (0,0)；`HUG`/`FILL` 在 `appendChild` 之后设置；`resize()` 在尺寸模式之前；自动换行的 TEXT 用 `textAutoResize='HEIGHT'` + FIXED 宽度（第 12、12a、12b、12c、13 条规则）
- [ ] **文字**——按标准的字体做法，样式名通过 `listAvailableFontsAsync()` 核实过；`lineHeight`/`letterSpacing` 用 `{unit, value}`；`FONT_FAMILY` 变量先加载每个模式的值（第 8 条规则）
- [ ] **异步和状态**——每个 Promise 都 `await` 了；多步骤之间的 ID 作为字符串字面量传递（第 15、17 条规则）

## 9. 创建之前先找出约定

**创建任何东西之前，一定要先检查 Figma 文件。** 不同的文件用不同的命名约定、变量结构和组件模式。你的代码应该和已有的保持一致，而不是强加新的约定。

对任何约定（命名、作用范围、结构）拿不准时，先查 Figma 文件，再查用户的代码库。只有两边都没有时，才退回到常见的模式。

### 快速检查脚本

**列出所有页面和顶层节点：**
```js
const pages = figma.root.children.map(p => `${p.name} id=${p.id} children=${p.children.length}`);
return pages.join('\n');
```

**列出所有页面上已有的组件：**

对于已发布的组件，`search_design_system` 是一个选择。对于画布上的组件，用两步并行分发的做法——**不要在一个脚本里遍历页面。**

第 1 步：一次只读的 `use_figma` 拿到页面 ID：
```js
return figma.root.children.map(p => ({ id: p.id, name: p.name }));
```

第 2 步：在**下一轮助手回复里，每个页面并行发出一个 `use_figma`**（一条消息里放 N 个工具调用块）。每个运行：
```js
const page = await figma.getNodeByIdAsync(PAGE_ID);
await figma.setCurrentPageAsync(page);
// findAllWithCriteria uses an indexed type lookup — hundreds of times faster
// than the findAll(n => n.type === '…') side-effect-in-predicate antipattern.
const matches = page.findAllWithCriteria({ types: ['COMPONENT', 'COMPONENT_SET'] });
return matches.map(n => ({ page: page.name, name: n.name, type: n.type, id: n.id }));
```

（代码注释意思：findAllWithCriteria 用的是按类型建了索引的查找——比 findAll(n => n.type === '…') 这种在判断函数里带副作用的反面写法快几百倍。）

**列出已有的变量集合和它们的约定：**
```js
const collections = await figma.variables.getLocalVariableCollectionsAsync();
const results = collections.map(c => ({
  name: c.name, id: c.id,
  varCount: c.variableIds.length,
  modes: c.modes.map(m => m.name)
}));
return results;
```

## 10. 参考文档

根据你的任务涉及什么，按需加载这些：

| 文档 | 什么时候加载 | 讲了什么 |
|-----|-------------|----------------|
| [gotchas.md](references/gotchas.md) | 任何 `use_figma` 之前 | 每个已知的坑，带 WRONG/CORRECT（错误/正确）代码例子——从 [标准的文字编辑做法](references/gotchas.md#canonical-text-edit-recipe-font-load--await--mutate--return-ids) 开始 |
| [common-patterns.md](references/common-patterns.md) | 需要能运行的代码例子 | 脚本骨架：形状、文字、自动布局、变量、组件、多步骤工作流程 |
| [plugin-api-patterns.md](references/plugin-api-patterns.md) | 创建/编辑节点 | 填充、描边、自动布局、效果、编组、复制、样式 |
| [api-reference.md](references/api-reference.md) | 需要确切的 API 范围 | 节点创建、变量 API、核心属性、哪些能用哪些不能用 |
| [validation-and-recovery.md](references/validation-and-recovery.md) | 多步骤写操作或错误恢复 | `get_metadata` 和 `get_screenshot` 的工作流程、必须做的错误恢复步骤 |
| [component-patterns.md](references/component-patterns.md) | 创建组件/变体 | combineAsVariants、组件属性、INSTANCE_SWAP、变体布局、找出已有组件、元数据遍历 |
| [variable-patterns.md](references/variable-patterns.md) | 创建/绑定变量 | 集合、模式、作用范围、别名、绑定方式、找出已有变量 |
| [text-style-patterns.md](references/text-style-patterns.md) | 创建/应用文字样式 | 字号阶梯、通过 `listAvailableFontsAsync` 查找字体、列出样式、给节点应用样式 |
| [effect-style-patterns.md](references/effect-style-patterns.md) | 创建/应用效果样式 | 投影、列出样式、给节点应用样式 |
| [plugin-api-standalone.index.md](references/plugin-api-standalone.index.md) | 需要了解完整的 API 范围 | Plugin API 里所有类型、方法和属性的索引 |
| [plugin-api-standalone.d.ts](references/plugin-api-standalone.d.ts) | 需要确切的类型签名 | 完整的类型文件——搜索具体的符号，不要一次全部加载 |

## 11. 代码片段例子

你会在这里的文档各处看到代码片段。这些片段包含有用、可以改作他用的 plugin API 代码。可以原样用，也可以边做边当作起步代码。如果有关键概念最适合写成通用的代码片段，把它们指出来并写到磁盘上，方便以后复用。
