---
name: Figma搭建页面
description: "当任务是把一个应用的页面、视图或多区块布局翻译到 Figma 里时，和 Figma插件基础 一起使用这个 skill。触发语：'write to Figma'（写到 Figma）、'create in Figma from code'（根据代码在 Figma 里创建）、'push page to Figma'（把页面推到 Figma）、'take this app/page and build it in Figma'（把这个应用/页面在 Figma 里搭出来）、'create a screen'（做一个屏幕）、'build a landing page in Figma'（在 Figma 里做一个落地页）、'update the Figma screen to match code'（更新 Figma 屏幕让它和代码一致）、'convert this modal/dialog/drawer/panel to Figma'（把这个弹窗/对话框/抽屉/面板转到 Figma）。只要用户想根据代码或描述，在 Figma 里搭建或更新一个完整页面、弹窗、对话框、抽屉、侧边栏、面板、表单、仪表盘、列表、表格、卡片、页头、消息预览或其他拼装出来的产品界面，这就是首选的工作流程 skill——即使用户把这个拼装界面叫作组件。它会从 Code Connect 文件、已有屏幕和组件库搜索中找出设计系统的组件、变量和样式，然后导入它们，用设计系统令牌而不是写死的值，一个区块一个区块地逐步拼装视图。"
disable-model-invocation: false
---

> 翻译自 Figma 官方仓库 https://github.com/figma/mcp-server-guide （skills/figma-generate-design，commit f278942）的 `figma-generate-design` skill，原作者 Figma，许可证：未注明许可证（仓库里没有找到 LICENSE 文件），仅供自用。
> 说明：SKILL.md 本身约 39 KB，参考文件 `references/`（`componentization.md`、`discover-product-font.md`）保留英文原文 ⚠️。下面要求在 `skillNames` 里写的是原名 `figma-generate-design`（给 Figma 做使用统计用），保持原样。链接里的 `../figma-use/...`、`../figma-generate-library/...`、`../figma-code-connect/...` 已经改成指向 `Figma插件基础`、`Figma设计系统`、`Figma组件对应代码` 这几个中文名文件夹，正文里提到的其他 skill 也换成了中文名。代码保持原样，代码注释的意思在后面用中文说明。
> 英文名备份：s-figma-generate-design

# 根据设计系统搭建 / 更新屏幕和视图

**交付物的硬性关卡：** 代码转设计的输出，必须用可编辑的文字、组件、图标和层级把界面重新做出来。
完整界面的任何截图或压平的渲染图，都只能当作视觉参考：绝不要把它上传或导入到交付物里，包括作为包装框的填充或子节点，即使它就在代码仓库里、或者看起来像素更精确。完成之前，检查结果；如果界面主要不是由可编辑的图层表示的，就按语义重新搭建，或者报告失败。

用这个 skill 在 Figma 里创建或更新**屏幕、视图和多区块的界面容器**，方式是**复用已发布的设计系统**——组件、变量和样式——而不是用写死的值画基础图形。这包括完整页面、弹窗、对话框、抽屉、侧边栏、面板，以及任何由多个区块组成的视图。关键的一点：Figma 文件很可能有一个已发布的设计系统，里面的组件、颜色/间距变量和文字/效果样式，和代码库的界面组件和令牌是对应的。找到并使用它们，而不是用十六进制颜色画方块。

**必须这样**：在任何 `use_figma` 调用之前，你**必须**同时加载 [Figma插件基础](../Figma插件基础/SKILL.md)。那个 skill 包含适用于你写的每个脚本的关键规则（颜色范围、加载字体等）。

**作为这个 skill 的一部分调用 `use_figma` 时，一定要在用逗号分隔的 `skillNames` 参数里加上 `figma-generate-design`。如果这个 skill 是通过 MCP 资源加载的，必须在名字前面加上 `resource:`（例如 `resource:figma-generate-design`）。** 这是一个日志参数——它不影响执行。

## HTML 转 Figma 的例外情况

下面这些情况，初次创建用 `html_to_figma`：

- 输入是一个已有的原始或静态 HTML 文档。直接把它交给 `html_to_figma`。
- 提示要求创建一个新设计，而且没有可以照着还原的、已经渲染出来的界面实现。创建一个自包含的 HTML 文档，交给 `html_to_figma`。

如果 `html_to_figma` 不可用，按下面已有的工作流程来。

## Skill 的边界

- 当交付物是一个由设计系统组件实例搭成的**拼装好的 Figma 视图**（新的或更新的）时用这个 skill——包括表单、仪表盘、列表、表格、卡片、页头、面板、对话框、消息预览或其他多区块容器。即使用户把这个拼装视图叫作组件，也适用。
- 如果主要交付物是一个打算做变体、令牌或发布用的**可复用组件库基础件或基础规范**，改用 [Figma设计系统](../Figma设计系统/SKILL.md) 加 [Figma插件基础](../Figma插件基础/SKILL.md)。
- 如果用户想写 **Code Connect 对应**，切换到 [Figma组件对应代码](../Figma组件对应代码/SKILL.md)。

## 前提条件

- 必须连接 Figma MCP 服务器
- 目标 Figma 文件必须有一个带组件的已发布设计系统（或者能访问一个团队库）
- 用户必须提供一个目标 Figma 文件（网址或 `fileKey`）。如果他们还没有，先调用 `/Figma新建文件`（或调用 `create_new_file`），并复用返回的 file_key。`use_figma` 和 `generate_figma_design` 都需要一个已经存在的 `fileKey`。
- 要搭建/更新的屏幕/视图的源代码或描述

## 和 generate_figma_design 并行的工作流程（只限网页应用）

当要根据一个能在浏览器里渲染的**网页应用**搭建屏幕时，两种方法并行跑效果最好：

1. **并行做：**
   - 针对目标 Figma 文件（`fileKey`），用这个 skill 的工作流程（use_figma + 设计系统组件）开始搭建屏幕。
   - 针对**同一个 `fileKey`** 运行 `generate_figma_design`，把正在运行的网页应用的像素级截图捕获到那个文件里。`generate_figma_design` 总是需要 `fileKey`——如果用户还没有 Figma 文件，先调用 `/Figma新建文件`（或调用 `create_new_file` MCP 工具）拿到一个，并在这个 skill 和捕获两边都复用那个 file_key。
2. **两边都完成后：** 更新 use_figma 的输出，让它和 `generate_figma_design` 捕获的像素级布局一致。捕获提供了要对准的确切间距、尺寸和视觉处理，而你的 use_figma 输出里有和设计系统关联的正确组件实例。如果捕获里有图片，就从捕获的图片填充里复制 `imageHash` 值，把它们转到你的 use_figma 输出里（详见第 5 步）。
3. **确认看起来不错之后：** 删掉 `generate_figma_design` 的输出——它只是用作视觉参考。

这结合了两者的长处：`generate_figma_design` 给出像素级精确的布局，而 use_figma 给出保持关联、可以更新的正确设计系统组件实例。

**当源头包含应用用到的独立内容图片时（比如照片、头像、logo 或图标），这个并行工作流程是必须的。完整界面的截图或压平的渲染图是视觉参考，不是内容图片。** `use_figma` Plugin API 不能获取外部图片网址——它只能通过复制文件里已有节点的 `imageHash` 值来设置图片填充。`generate_figma_design` 会把所有看得见的图片栅格化到 Figma 里，提供你需要的哈希值。如果有这些内容图片时你跳过了捕获，它们的图片框会是空白的。

对于非网页应用（iOS、Android 等），或者在更新已有屏幕时，用下面的标准工作流程。

## 必须遵守的工作流程

**按顺序做这些步骤。不要跳步。**

> **必须保持的不变条件：**
>
> - 在修改交付物之前，完成 Code Connect 调研并选定目标组件库。只为调研做的导入和临时实例是允许的；临时实例要马上删掉。
> - 每个选定的资产在哪里导入就在哪里使用。如果导入失败，先试下一个适用的精确结果，再去手动搭一个替代品。

### 第 1 步：弄懂交付物

动 Figma 之前，先弄懂你要搭什么：

1. 如果是根据代码搭建，阅读相关的源文件，了解结构、区块，以及用了哪些组件。
2. 找出视图的主要区块（例如页面：页头、主视觉、内容面板、页脚；弹窗：标题栏、表单区块、操作栏；侧边栏：导航、内容区域、底部操作）。
3. 对每个区块，列出涉及的界面组件（按钮、输入框、卡片、导航胶囊、折叠面板等）。
4. **从源头找出产品用的字体家族。不要默认用 Inter。** 写任何脚本之前，先找出产品用的是*哪种*字体。去哪里找（CSS 变量、组件文件）以及怎样处理混乱的 Figma 字体名，见 [references/discover-product-font.md](references/discover-product-font.md)。
5. **检查视图里有没有图片**（例如 `<img>`、`<Image>`、背景图、产品照片、头像、从网址加载的图标）。如果有，而且这是一个网页应用，你**必须**运行并行的 `generate_figma_design` 捕获工作流程——和第 2 步同时马上开始，让捕获在你调研组件时进行。见上面的“和 generate_figma_design 并行的工作流程”。

### 第 2 步：收集组件 key、变量和样式

你需要从设计系统拿到三样东西：**组件**（按钮、卡片等）、**变量**（颜色、间距、圆角）和**样式**（文字样式、像阴影这样的效果样式）。有设计系统令牌时，不要写死十六进制颜色或像素值。

#### 2a：找出组件

**2a-i——必须做：查看需要的组件有没有 Code Connect。** 从第 1 步列出的组件清单开始，检查每个组件在代码库里有没有 Code Connect 文件。Code Connect 文件放在组件源码旁边，按平台命名：

- **TypeScript/JS**：`*.figma.ts`、`*.figma.js`
- **React（基于解析器）**：`*.figma.tsx`
- **Kotlin/Compose**：包含 `@FigmaConnect` 的 `.kt` 文件
- **Swift**：包含 `FigmaConnect` 的 `.swift` 文件

对你需要的每个组件（例如 Button、Card、Input），搜索它的 Code Connect 文件——按组件名用 glob 或 grep（例如 `**/Button.figma.tsx`、`**/Card.figma.ts`）。只读取和你真正需要的组件匹配的文件。

从每个匹配的 Code Connect 文件里，取出 Figma 组件的网址。从网址里解析出 `fileKey` 和 `nodeId`（把连字符换成冒号：`123-456` → `123:456`）。然后通过 `use_figma` 解析出组件 key：

**例子：** Code Connect 文件里有 `// url=https://figma.com/design/ABC123/File?node-id=609-35535`。解析出 `fileKey` = `ABC123`，`nodeId` = `609:35535`。针对**组件库文件**（fileKey `ABC123`，不是目标文件）运行 `use_figma` 来解析 key：

```js
const node = await figma.getNodeByIdAsync("609:35535");
const set = node?.parent?.type === "COMPONENT_SET" ? node.parent : node;
if (set?.type === "COMPONENT_SET") {
  return { assetType: "component_set", componentSetKey: set.key };
}
if (set?.type === "COMPONENT") {
  return { assetType: "component", componentKey: set.key };
}
throw new Error("Expected a component or component set");
```

把多个查找批量放在一次调用里。在第 4 步，根据每一项的 `assetType`，把返回的 key 用在 `importComponentByKeyAsync()` 或 `importComponentSetByKeyAsync()` 上。

标记已解析的组件，接着处理还没解析的。

**2a-ii——必须做：选定组件库范围，然后搜索并检查整个视图。** 调用 `get_libraries`。如果用户点名了一个或多个组件库，就用它们确切的 key，不管它们出现在 `libraries_added_to_file` 还是 `libraries_available_to_add` 里。否则就在 `libraries_added_to_file` 里的所有组件库中一起搜索。每次搜索都在 `includeLibraryKeys` 里传入选定的 key。只有当还没解决的缺口找不到合适的匹配时，才从 `libraries_available_to_add` 里加入特别相关的组件库，并重试那些还没解决的查询；不要扩大到不相关的可用组件库。在第一次批量的 `search_design_system` 调用里，为要求的视图或流程放一条组件查询，和从源码或 Code Connect 检查中已知的、还没解决的项目的查询放在一起。整个视图的查询按用途和容器命名（例如 `billing settings drawer`）。检查最强的候选。如果它覆盖了两个或更多要求的区块，就选它作为基础；否则不用整体组合件，继续往下做。

**2a-iii——检查已有的屏幕。** 检查目标文件里是否已经有用同一个设计系统做的屏幕。一次只读的 `use_figma` 调用就能把一个已有的框盘点清楚——它的组件 key、绑定的变量和文字/效果样式——一次权威的遍历。在这里运行一次，在 2b 和 2c 里复用结果，而不是重新遍历这个框：

```js
const frame = figma.currentPage.findOne(n => n.name === "Existing Screen");
const components = new Map();
const styles = { text: new Map(), effect: new Map() };
const variableIds = new Set();

// boundVariables and style ids can sit on any scene node, so walk them all.
for (const node of frame?.findAll(() => true) ?? []) {
  if (node.type === "INSTANCE") {
    const mc = node.mainComponent;
    const cs = mc?.parent?.type === "COMPONENT_SET" ? mc.parent : null;
    const key = cs ? cs.key : mc?.key;
    if (key && !components.has(key)) {
      components.set(key, { name: cs ? cs.name : mc.name, key, isSet: !!cs, sampleVariant: mc.name });
    }
  }
  for (const b of Object.values(node.boundVariables ?? {}).flat()) {
    if (b?.id) variableIds.add(b.id);
  }
  for (const [prop, bucket] of [["textStyleId", "text"], ["effectStyleId", "effect"]]) {
    if (prop in node && typeof node[prop] === "string" && node[prop]) {
      const s = await figma.getStyleByIdAsync(node[prop]);
      if (s) styles[bucket].set(s.id, { name: s.name, id: s.id, key: s.key });
    }
  }
}
const vars = await Promise.all([...variableIds].map(id => figma.variables.getVariableByIdAsync(id)));

return {
  components: [...components.values()],
  variables: vars.filter(Boolean).map(v => ({ name: v.name, id: v.id, key: v.key, type: v.resolvedType, remote: v.remote })),
  textStyles: [...styles.text.values()],
  effectStyles: [...styles.effect.values()],
};
```

（代码注释意思：boundVariables 和样式 id 可能出现在任何场景节点上，所以要遍历所有节点。）

把 `components` 和你还没解析的组件对比；2a-i 拿到的 Code Connect key 仍然是权威的。把新解析出来的标记上。

**2a-iv——只搜索搭建需要的缺口。** 在 Code Connect、整个视图的调研和已有屏幕的检查之后，搜索设计还需要的、还没解决的组件和令牌。把互相独立、每条一个意图的查询批量放在一起，让 `includeLibraryKeys` 限定在选定的组件库范围内，并把选定的 key 带到搭建里。不要为了把每个还没解决的角色都搜遍而推迟搭建。

```
// Step 1: Discover available libraries
get_libraries({ fileKey })
// Returns: {
//   libraries_added_to_file: [...],
//   libraries_available_to_add: [...],
//   libraries_available_to_add_next_offset: number | null
// }

// Step 2: Search within a specific library using its libraryKey
search_design_system({ queries: [{ entity: "component", query: "button" }], fileKey, includeLibraryKeys: ["lk-abc123..."] })
```

（代码注释意思：第 1 步：找出可用的组件库；返回已添加到文件的库、可以添加的库、下一页偏移量。第 2 步：用 libraryKey 在某个特定的组件库里搜索。）

`libraries_available_to_add` 里的组织组件库是分页的（每页 20 个）。当 `libraries_available_to_add_next_offset` 不是 null 时，说明还有更多组织组件库——把 `offset` 设成那个值，再调用一次 `get_libraries` 获取下一页。社区 UI 套件只出现在第一页。如果用户点名的某个组件库在当前页里没看到，放弃之前继续往后翻页。

当文件有很多组件库、你想要有针对性的结果时，这特别有用（例如只在 "iOS 26" 或 "Material 3" 里搜索，而不是从每个组件库都得到匹配）。

**每条查询只放一个意图。** `search_design_system` 不支持“或”的语义，所以绝不要把多个选项或同义词塞进一个字符串（"Button IconButton icon" 什么有用的也匹配不到）。知道确切的设计系统名称或组件类型时就用它；否则按资产在界面里的角色搜索，比如 "archive action icon"（归档操作图标）或 "primary submit button"（主要提交按钮）。
把每个选定的 key 对应到一个区块或属性。复用适用的组合件里的后代，而不是另外搭一套替代品；保持嵌套实例完整，除非只有一个示例/模板包装层必须分离。

在你的对应表里**包含组件属性**——你需要知道每个组件暴露了哪些 TEXT 属性，才能覆盖文字。创建一个临时实例，读取它的 `componentProperties`（以及嵌套实例的），然后删掉临时实例。

带属性信息的组件对应表例子：

```
Component Map:
- Button → key: "abc123", type: COMPONENT_SET
  Properties: { "Label#2:0": TEXT, "Has Icon#4:64": BOOLEAN }
- PricingCard → key: "ghi789", type: COMPONENT_SET
  Properties: { "Device": VARIANT, "Variant": VARIANT }
  Nested "Text Heading" has: { "Text#2104:5": TEXT }
  Nested "Button" has: { "Label#2:0": TEXT }
```

#### 2b：找出变量（颜色、间距、圆角）

**先检查已有的屏幕。** 复用 2a-iii 盘点出来的 `variables`；如果跳过了那一步，在有已有屏幕时在这里运行盘点。对于还没解决的变量，用 `search_design_system`，`queries` 条目的 `entity` 设为 `"variable"`。

> **警告：有两种不同的找变量的方法——不要搞混。**
>
> - 用 `use_figma` 调 `figma.variables.getLocalVariableCollectionsAsync()`——**只返回当前文件里定义的本地变量**。如果它返回空，**不**代表没有变量。远程/已发布的组件库变量对这个 API 是看不见的。
> - 用 `search_design_system` 加 `entity: "variable"` 的查询条目——搜索远程和已发布的组件库变量。每条查询都要用 `includeLibraryKeys` 限定在 2a-ii 选定的组件库 key 内。
>
> **绝不要只因为 `getLocalVariableCollectionsAsync()` 返回空，就得出“没有变量”的结论。** 在决定自己创建之前，一定还要用变量查询条目运行 `search_design_system`，检查组件库变量。

**查询策略：** `search_design_system` 匹配的是**变量名**（例如 "Gray/gray-9"、"core/gray/100"、"space/400"），而不是类别。在一次 `queries` 调用里放多条简短、简单的搜索，而不是一条复合查询。数组里的每一项都必须是一个 `{ "entity": "variable", "query": "..." }` 对象，绝不能是光秃秃的字符串：

- **基础颜色：** `{ "entity": "variable", "query": "gray" }`、`{ "entity": "variable", "query": "red" }` 等。
- **语义颜色：** `{ "entity": "variable", "query": "background" }`、`{ "entity": "variable", "query": "surface" }` 等。
- **间距/尺寸：** `{ "entity": "variable", "query": "space" }`、`{ "entity": "variable", "query": "radius" }` 等。

如果最初的搜索返回空，试试更短的片段或不同的命名习惯——不同组件库差别很大（"grey" 和 "gray"、"spacing" 和 "space"、"color/bg" 和 "background"）。

对于组件库变量（remote = true），用 `figma.variables.importVariableByKeyAsync(key)` 按 key 导入。对于本地变量，直接用 `figma.variables.getVariableByIdAsync(id)`。

绑定方式见 [variable-patterns.md](../Figma插件基础/references/variable-patterns.md)。

#### 2c：找出样式（文字样式、效果样式）

复用 2a-iii 或 2b 盘点出来的 `textStyles` 和 `effectStyles`。如果没有盘点结果，用同一个脚本检查一个可用的屏幕。在写死一个还没解决的、可复用的填充/描边、字体排版或效果角色之前，发一条有重点的 `search_design_system` 条目，`entity: "style"`，比如 "surface"、"border"、"heading"、"body"、"shadow" 或 "elevation"。把互相独立的条目批量放在一起，但不要把已经被某个选定组件或已有屏幕样式覆盖的角色都搜一遍。搜索任何仍然缺少的样式。

用 `figma.importStyleByKeyAsync(key)` 导入组件库样式，然后用 `node.textStyleId = style.id` 或 `node.effectStyleId = style.id` 应用。

详见 [text-style-patterns.md](../Figma插件基础/references/text-style-patterns.md) 和 [effect-style-patterns.md](../Figma插件基础/references/effect-style-patterns.md)。

### 第 3 步：创建包装框

**不要把区块搭成页面的顶层子节点、之后再移到别的父节点下**——跨 `use_figma` 调用用 `appendChild()` 移动节点会悄悄失败，留下孤立的框。先创建一个可修改的包装框，然后直接在它里面搭每个区块。

在包装框里导入并实例化任何选定的整体视图组合件。定制它覆盖到的后代，把缺少的区块添加到包装框里、放在它旁边；绝不要直接往一个实例里添加子节点。把包装框放在远离已有内容的地方，并返回它的 ID：

```js
// Find clear space
let maxX = 0;
for (const child of figma.currentPage.children) {
  maxX = Math.max(maxX, child.x + child.width);
}

const wrapper = figma.createAutoLayout("VERTICAL");

// --- Size the wrapper based on container type ---
// Full page:       wrapper.resize(1440, 100); wrapper.name = "Homepage";
// Modal/dialog:    wrapper.resize(640, 100);  wrapper.name = "Settings Modal";
// Drawer/sidebar:  wrapper.resize(360, 100);  wrapper.name = "Navigation Drawer";
// Panel:           wrapper.resize(400, 100);  wrapper.name = "Details Panel";
// Adapt width to match the source code's actual dimensions.

wrapper.name = "VIEW_NAME";
wrapper.primaryAxisAlignItems = "CENTER";
wrapper.counterAxisAlignItems = "CENTER";
wrapper.resize(WIDTH, 100);
wrapper.layoutSizingHorizontal = "FIXED";
wrapper.x = maxX + 200;
wrapper.y = 0;

return { success: true, wrapperId: wrapper.id };
```

（代码注释意思：找一块空的地方；根据容器类型确定包装框的大小——完整页面 1440 宽、弹窗/对话框 640 宽、抽屉/侧边栏 360 宽、面板 400 宽；宽度要按源代码里的实际尺寸调整。）

### 第 4 步：定制已覆盖的区块，搭建缺少的区块

**这是最重要的一步。** 从选定的组合件开始：定制它已经覆盖的后代，只搭建缺少的区块。按可以安全重试的搭建阶段来做，安全时把相关的区块批量处理。只在页面上下文的边界、部分执行后难以恢复，或者失败后需要有针对性的重试时才拆分——不要只为了制造验证检查点而拆分。每个脚本开头，按 ID 取得可修改的包装框。新内容添加到这个框里，绝不要添加到组件实例里。

```js
const createdNodeIds = [];

// Resolve the wrapper and import every design system dependency in parallel.
// Sequential awaits here serialize N independent IPC round-trips at the top
// of every section build; one Promise.all is dramatically faster.
const [wrapper, buttonSet, bgColorVar, spacingVar, shadowStyle] = await Promise.all([
  figma.getNodeByIdAsync("WRAPPER_ID_FROM_STEP_3"),
  figma.importComponentSetByKeyAsync("BUTTON_SET_KEY"),
  figma.variables.importVariableByKeyAsync("BG_COLOR_VAR_KEY"),
  figma.variables.importVariableByKeyAsync("SPACING_VAR_KEY"),
  figma.importStyleByKeyAsync("SHADOW_STYLE_KEY"),
]);
const primaryButton = buttonSet.children.find(c =>
  c.type === "COMPONENT" && c.name.includes("variant=primary")
) || buttonSet.defaultVariant;

// Build section frame with variable bindings (not hardcoded values)
const section = figma.createAutoLayout();
section.name = "Header";
section.setBoundVariable("paddingLeft", spacingVar);
section.setBoundVariable("paddingRight", spacingVar);
const bgPaint = figma.variables.setBoundVariableForPaint(
  { type: 'SOLID', color: { r: 0, g: 0, b: 0 } }, 'color', bgColorVar
);
section.fills = [bgPaint];

// Apply the effect style imported above
section.effectStyleId = shadowStyle.id;

// Create component instances inside the section
const btnInstance = primaryButton.createInstance();
section.appendChild(btnInstance);
createdNodeIds.push(btnInstance.id);

// Append section to wrapper
wrapper.appendChild(section);
section.layoutSizingHorizontal = "FILL"; // AFTER appending

createdNodeIds.push(section.id);
return { success: true, createdNodeIds };
```

（代码注释意思：取得包装框，并行导入所有设计系统依赖——这里如果一个接一个地 await，会让每个区块搭建开头的 N 次独立通信来回变成串行；一个 Promise.all 快得多。用变量绑定（不是写死的值）搭建区块框；应用上面导入的效果样式；在区块里创建组件实例；把区块添加到包装框里；FILL 要在添加之后设置。）

每次调用都返回创建的节点 ID，加上相关的数量、名字和边界——这就是你默认的结构验证。只在缺这些证据、或者某次相关修改让它失效时，才单独做一次结构读取。视觉检查留到第 5 步。

#### 用 setProperties() 覆盖实例的文字

组件实例自带占位文字（"Title"、"Heading"、"Button"）。用第 2 步找到的组件属性 key，通过 `setProperties()` 覆盖它们——这比直接改 `node.characters` 可靠。完整做法见 [component-patterns.md](../Figma插件基础/references/component-patterns.md#overriding-text-in-a-component-instance)。

对于暴露了自己 TEXT 属性的嵌套实例，在嵌套实例上调用 `setProperties()`：

```js
// Use the type-indexed criteria for the type filter, then narrow by name.
const nestedHeading = cardInstance
  .findAllWithCriteria({ types: ["INSTANCE"] })
  .find(n => n.name === "Text Heading");
if (nestedHeading) {
  nestedHeading.setProperties({ "Text#2104:5": "Actual heading from source code" });
}
```

（代码注释意思：用按类型建了索引的条件做类型筛选，然后再按名字收窄。）

只有对**不**受任何组件属性管理的文字，才退回到直接改 `node.characters`。

#### 仔细读源代码里的默认值

把代码组件翻译成 Figma 实例时，查看源代码里组件 prop 的默认值，而不只是明确传进去的值。例如 `<Button size="small">Register</Button>` 没有传 variant prop——要查看组件定义，找到默认值 `variant = "primary"`。选错变体（例如 Neutral 而不是 Primary）会产生视觉上不对、又很容易漏看的结果。

#### 什么手动搭建，什么从设计系统导入

| 手动搭建 | 从设计系统导入 |
|----------------|--------------------------|
| 包装框 | **组件**：按钮、卡片、输入框、导航等 |
| 区块容器框 | **变量**：颜色（填充、描边）、间距（内边距、间隙）、圆角 |
| 布局网格（行、列） | **文字样式**：标题、正文、说明文字等 |
| | **效果样式**：阴影、模糊等 |

有设计系统变量时，**绝不要写死十六进制颜色或像素间距**。间距/圆角用 `setBoundVariable`，颜色用 `setBoundVariableForPaint`。用 `node.textStyleId` 应用文字样式，用 `node.effectStyleId` 应用效果样式。

#### 把重复和可复用的元素做成组件（必须）

做成组件是**默认**工作流程的一部分，不是可选的后续步骤。第一遍就产出组件化的结构；不要输出一棵扁平的、全是一次性框的树，再等第二条“现在把它组件化”的提示。

- **设计系统实例本来就是组件化的**（第 2 步）。优先用它们。
- **对于设计系统没覆盖、但会重复出现或对应到一个可复用源组件的任何东西，用 `figma.createComponent()` 创建一次本地组件，然后放实例**，而不是手搭 N 个几乎一样的框。一个源组件对应一个 Figma 主组件。

“搭一次、放实例”的做法和代码见 [references/componentization.md](references/componentization.md)。

#### 图标：导入 SVG，绝不要用旋转的基础图形重画

图标是上面“手动搭建还是导入”这条划分的**主要例外。** 如果设计系统把某个图标作为组件提供，就实例化它（一个 INSTANCE_SWAP 属性，而不是每个图标一个变体）。否则——最常见的情况是**从代码库里拿一个图标，放到 Figma 里或替换 Figma 里的某个图标**——把图标的 **SVG 源码直接**作为矢量节点导入。这是图标首要的、默认的做法；不要重画它们。

1. **从代码库拿到 SVG。** 读取图标的源码——内联的 `<svg>`、导入的 `.svg` 素材，或者图标库里的条目——把那个确切的 SVG 字符串传进去。优先用代码库自己的 SVG，而不是手写一个。
2. **用 `figma.createNodeFromSvg(svgString)` 导入**，它返回一个由可编辑矢量路径组成的 `FrameNode`。SVG 字符串**必须**包含 `viewBox`，以及明确的 `width`/`height`（例如 `<svg width="24" height="24" viewBox="0 0 24 24" ...>`）。没有 `width`/`height` 的话，会退回到 `viewBox` 的大小，这通常比插槽小——这是“图标尺寸不对”的常见原因。
3. **按插槽调整大小。** `createNodeFromSvg` 生成的框在调整大小时会缩放里面的内容，所以 `icon.resize(size, size)` 会把整个图标（包括描边粗细）缩放到目标框里。也可以直接把 `width`/`height` 写成目标尺寸。和源头的图标尺寸一致——常见的是 16/20/24px。
4. **绝不要用旋转的线/矩形/椭圆基础图形重画图标。** 在 `use_figma` 环境里，Figma 的线条旋转不可靠，会产生坏掉的、转错角度的图标（一个箭头折线塌成一团、箭头和箭杆分开）。导入 SVG 既更可靠，也更容易编辑。

```js
// Place / replace an icon from a codebase SVG into a 24px slot
const icon = figma.createNodeFromSvg(
  '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">' +
  '<path d="m9 18 6-6-6-6" stroke="#1A1A1A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
);
icon.name = "icon/chevron-right";
icon.resize(24, 24);          // scales the whole icon to the slot
slotFrame.appendChild(icon);
```

（代码注释意思：把代码库里的 SVG 图标放到/替换进一个 24px 的插槽；resize 会把整个图标缩放到插槽大小。）

**代码库里的 SVG 通常用 `currentColor`**（例如 `stroke="currentColor"` / `fill="currentColor"`），`createNodeFromSvg` 会把它导入成**黑色**——它不会继承父元素的颜色。导入后设置想要的颜色：导入前把字面颜色替换进 SVG 字符串，或者用 `setBoundVariableForPaint` 把导入的矢量填充/描边绑定到一个设计系统颜色变量上（和任何填充一样）。要把导入的 SVG 变成可复用的图标组件（用于 INSTANCE_SWAP），见 [Figma设计系统 → Creating Icon Components](../Figma设计系统/references/component-creation.md) 和 [INSTANCE_SWAP 做法](../Figma插件基础/references/component-patterns.md#instance_swap-avoiding-variant-explosion)。

### 第 5 步：验证整个视图并转移图片

做视觉验证之前，用 `use_figma` 读回包装框，返回它的后代总数、里面出现的每种后代节点类型的数量，以及每个带图片填充的节点的 ID、名字、节点类型和尺寸。这些数量是证据，不是一个通过的数字门槛；不要根据截图推断是否可编辑，也不要接受在一张完整界面栅格图上叠几个装样子的可编辑节点。如果包装框里任何地方出现了完整界面的截图或压平的渲染图，删掉它，按语义重新搭建界面，或者报告失败；不要声称已经完成。

拼装完所有区块后，给包装框截**一张整个视图的拼装截图**，和源头比较。如果发现了明显的视觉缺陷，做有针对性的 `use_figma` 修复——不要重建整个视图——然后截**一张**修复后的图。最近一张通过的截图就是最终检查：不要再额外截一张没有变化的“最终”图，也不要给每个区块单独截图。

做视觉修复之前，把包装框里的实例、样式和绑定变量的 key 和第 2 步的对应表比较。每个适用的选定资产都应该出现在输出里；完成之前，把手动做的等价物和原始值替换掉。

在拼装截图里检查：
- **被裁掉/截断的文字**——行高或框的尺寸切掉了字母下伸部分、上伸部分，或者整行
- **重叠的内容**——因为尺寸不对或缺少自动布局，元素叠在一起
- 还显示着占位文字（"Title"、"Heading"、"Button"）
- 因为布局尺寸 bug 而被截断的内容
- 错误的组件变体（例如 Neutral 和 Primary 按钮）
- **错误的字体家族**——文字用的字体和产品用的不一样（例如产品用 SF Pro，却显示成 Inter）。脚本运行没有报错，所以一眼看不出来；要明确地断言它（见下面的“断言字体家族正确”）
- **空白的图片占位**——如果缺图片，在考虑用 `generate_image` 生成占位图之前，先从 `generate_figma_design` 的捕获里转移过来（见下面的“从 generate_figma_design 的捕获里转移图片”）

#### 断言字体家族正确

**你必须明确断言渲染出来的文字用的是第 1 步找出的产品字体**，任何不一致都算验证失败。不要以为成功加载的字体就是正确的字体：产品用 SF Pro 时加载了 Inter，即使没有任何错误也是失败。**如果你有源头参考（正在运行的网页应用、设计稿，或者 `generate_figma_design` 的捕获），你还必须比较渲染出来的截图**——同一家族里差一点的样式能通过家族检查，但看起来仍然不对。

读回脚本（它会把你要修的独立文字，和你要标出来的、受设计系统管理的文字分开）和截图比较的步骤，见 [references/discover-product-font.md](references/discover-product-font.md#verify-the-font-after-building)。

#### 从 generate_figma_design 的捕获里转移图片

如果你并行运行了 `generate_figma_design`，只把应用用到的独立内容素材转移到你的设计系统输出里。绝不要上传或转移捕获的根节点，也不要转移完整界面的任何截图或压平的渲染图。

1. 通过搜索 `type === "IMAGE"` 的填充，找出捕获输出里所有的图片节点：
   ```js
   const capture = await figma.getNodeByIdAsync("CAPTURE_NODE_ID");
   const imageNodes = capture.findAll(() => true).flatMap(n => {
     if (!Array.isArray(n.fills)) return [];
     const imageFill = n.fills.find(f => f.type === "IMAGE");
     return imageFill ? [{ name: n.name, id: n.id, imageHash: imageFill.imageHash }] : [];
   });
   return imageNodes;
   ```
2. 把每张捕获的图片对应到你的 use_figma 输出里相应的框（按位置、名字或顺序）。
3. 把图片哈希应用到目标框上：
   ```js
   targetFrame.fills = [{ type: "IMAGE", imageHash: "hash_from_capture", scaleMode: "FILL" }];
   ```
4. 所有图片都转移完之后，删掉 `generate_figma_design` 的捕获输出。

#### 生成占位图片

先复用可用的源头图片、捕获的图片或组件库图片。如果还剩下占位，告诉用户有多少张图片需要用 Figma 的 `generate_image` 工具生成。征求许可，并说明这个工具会消耗 Figma AI 点数。得到同意后，用需要的参数调用 `generate_image`。

如果 Figma AI 不可用，或者 AI 点数用完了，和用户确认能不能用其他的图片生成工具。只有这些来自其他提供方的图片，才用 `upload_assets` 上传。

### 第 6 步：更新已有的视图

不是从零创建、而是更新时：

1. 用 `get_metadata` 检查已有屏幕的结构。
2. 找出哪些区块需要更新、哪些可以保留。
3. 对每个需要修改的区块：
   - 按 ID 或名字找到已有的节点
   - 如果设计系统组件变了，替换组件实例
   - 按需更新文字内容、变体属性或布局
   - 删除废弃的区块
   - 添加新的区块
4. 按第 4–5 步同样的证据和截图节奏来：结构验证依靠返回的 ID 加上相关的数量、名字和边界，更新完截一张整个视图的截图（只有需要有针对性的视觉修复时，再截一张修复后的图）。

```js
// Example: Swap a button variant in an existing screen.
// Batch the node lookup and component-set import in parallel — they are
// independent and awaiting them sequentially serializes two IPC round-trips.
const [existingButton, buttonSet] = await Promise.all([
  figma.getNodeByIdAsync("EXISTING_BUTTON_INSTANCE_ID"),
  figma.importComponentSetByKeyAsync("BUTTON_SET_KEY"),
]);
if (existingButton && existingButton.type === "INSTANCE") {
  const newVariant = buttonSet.children.find(c =>
    c.name.includes("variant=primary") && c.name.includes("size=lg")
  ) || buttonSet.defaultVariant;
  existingButton.swapComponent(newVariant);
}
return { success: true, mutatedNodeIds: [existingButton.id] };
```

（代码注释意思：例子——在已有屏幕里替换一个按钮变体。把查找节点和导入组件集并行批量处理——它们互相独立，一个接一个地 await 会让两次通信来回变成串行。）

## 参考文档

需要详细的 API 做法和常见坑时，按需从 [Figma插件基础](../Figma插件基础/SKILL.md) 的参考文件里加载这些：

- [component-patterns.md](../Figma插件基础/references/component-patterns.md)——按 key 导入、查找变体、setProperties、覆盖文字、处理实例
- [variable-patterns.md](../Figma插件基础/references/variable-patterns.md)——创建/绑定变量、导入组件库变量、作用范围、别名、找出已有变量
- [text-style-patterns.md](../Figma插件基础/references/text-style-patterns.md)——创建/应用文字样式、导入组件库文字样式、字号阶梯
- [effect-style-patterns.md](../Figma插件基础/references/effect-style-patterns.md)——创建/应用效果样式（阴影）、导入组件库效果样式
- [gotchas.md](../Figma插件基础/references/gotchas.md)——布局的坑（HUG/FILL 的相互作用、counterAxisAlignItems、设置尺寸的顺序）、填充/颜色问题、页面上下文重置

## 错误恢复

按 [Figma插件基础 的错误恢复](../Figma插件基础/SKILL.md#7-error-recovery--self-correction) 来做：

- 如果 `safeToRetryWithoutCanvasRead` 是 `true`，修好错误再重试。
- 如果是 `false`，先读画布，弄清楚变了什么，再做修改。

因为这个 skill 按可以安全重试的搭建阶段来工作，错误自然只局限在当前阶段。之前成功的调用产生的内容保持不变。

## 最佳做法

- **搭建之前一定先搜索。** 设计系统很可能已经有你需要的组件、变量或样式。手动搭建和写死的值应该是例外，而不是常规。
- **搜索还没解决的缺口，每条查询一个意图。** 把同义词和部分词作为单独的 `{ entity, query }` 条目放在一次 `queries` 调用里试，绝不要合并成一个字符串——一个 "NavigationPill" 可能在 "pill"、"nav"、"tab" 或 "chip" 下面找到，所以把它们作为四条组件条目传进去。对变量，用 `entity: "variable"`，查询像 "color"、"spacing" 和 "radius" 这样的词。只对还没解决的搭建缺口这样做，找到合适的资产就停下。
- **优先用设计系统令牌，而不是写死的值。** 颜色、间距和圆角用变量绑定。字体排版用文字样式。阴影用效果样式。这样屏幕能和设计系统保持关联。
- **优先用组件实例，而不是手动搭建。** 实例和源组件保持关联，设计系统演进时会自动更新。
- **默认做成组件。** 重复或可复用的元素搭一次组件，然后放实例。不要交出一棵扁平的、全是一次性框的树，还需要第二遍“把它组件化”。
- **按可以安全重试的搭建阶段来工作。** 当脚本仍然可以安全重试时，把相关的区块批量放进一次 `use_figma` 调用；只在页面上下文的边界、难以恢复的修改处，或者真正失败后需要有针对性的重试时才拆分。
- **每次调用都返回节点 ID 和验证证据。** 返回创建的 ID 加上相关的数量、名字和边界——这是你默认的结构验证，拼装区块和错误恢复时也需要这些 ID。
- **用一张拼装截图做视觉验证。** 拼装完截一张整个视图的截图，只有在有针对性的视觉修复之后再截一张；最近一张通过的截图就是最终的。
- **断言字体家族，而不只是加载成功。** 脚本可能加载了错误的字体却不报错。搭建完之后，确认渲染出来的文字用的是第 1 步找出的产品字体（见第 5 步）。
- **和已有的约定保持一致。** 如果文件里已经有屏幕，和它们的命名、尺寸和布局方式保持一致。
