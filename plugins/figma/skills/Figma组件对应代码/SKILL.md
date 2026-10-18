---
name: Figma组件对应代码
description: 创建和维护 Figma Code Connect 模板文件，把 Figma 组件对应到代码片段。在用户提到 Code Connect、Figma 组件对应、设计转代码，或者要求创建/更新 .figma.ts 或 .figma.js 文件时使用。
disable-model-invocation: false
---

> 翻译自 Figma 官方仓库 https://github.com/figma/mcp-server-guide （skills/figma-code-connect，commit f278942）的 `figma-code-connect` skill，原作者 Figma，许可证：未注明许可证（仓库里没有找到 LICENSE 文件），仅供自用。
> 说明：参考文件 `references/`（`api.md`、`advanced-patterns.md`）加上 SKILL.md 超过 30 KB，保留英文原文 ⚠️。代码、方法名、属性类型名保持原样，代码注释的意思在后面用中文说明。
> 英文名备份：s-figma-code-connect

# Code Connect

## 概述

创建 Code Connect 模板文件（`.figma.ts`），把 Figma 组件对应到代码片段。拿到一个 Figma 网址后，按下面的步骤创建模板。

> **你只写 `.figma.ts` 模板文件——绝不写 `.figma.tsx`。** 这个 skill 产出的是*无解析器模板*：一个 `.figma.ts` 文件，它的默认导出用的是 `` figma.code`...` `` 标签模板。**不要**写 `.figma.tsx` 文件，也**不要**用 `figma.connect()`——那是另一种**基于解析器**的 Code Connect 格式（用另一种方式发布），对这个 skill 来说是**错误的产物**；写成 `.figma.tsx` 的输出会被直接拒绝。如果某个组件已经有 `.figma.tsx` 文件，不要动它，把你的 `.figma.ts` 模板加在它旁边。能力强的模型可能会忍不住凭记忆去用更熟悉的 `.figma.tsx` / `figma.connect()` 写法——忍住；在这里正确的输出**永远**是 `.figma.ts` + `figma.code`。

## 前提条件

- **必须连接 Figma MCP 服务器**——继续之前，确认 Figma MCP 工具（例如 `get_code_connect_suggestions`）可以用。如果不能用，引导用户启用 Figma MCP 服务器并重启他们的 MCP 客户端。
- **组件必须已发布**——Code Connect 只对发布到 Figma 团队库的组件有效。如果组件没有发布，告诉用户，然后停下。
- **需要 Organization 或 Enterprise 套餐**——Free 或 Professional 套餐不能用 Code Connect。
- **网址必须包含 `node-id`**——Figma 网址里必须有 `node-id` 查询参数。
- **TypeScript 类型**——要在 `.figma.ts` 文件里获得编辑器自动补全和类型检查，必须把 `@figma/code-connect/figma-types` 加到 `tsconfig.json` 的 `types` 里：
  ```json
  {
    "compilerOptions": {
      "types": ["@figma/code-connect/figma-types"]
    }
  }
  ```

## 第 1 步：解析 Figma 网址

从网址里取出 `fileKey` 和 `nodeId`：

| 网址格式 | fileKey | nodeId |
|---|---|---|
| `figma.com/design/:fileKey/:name?node-id=X-Y` | `:fileKey` | `X-Y` → `X:Y` |
| `figma.com/file/:fileKey/:name?node-id=X-Y` | `:fileKey` | `X-Y` → `X:Y` |
| `figma.com/design/:fileKey/branch/:branchKey/:name` | 用 `:branchKey` | 从 `node-id` 参数取 |

一定要把 `nodeId` 里的连字符换成冒号：`1234-5678` → `1234:5678`。

**完整例子：**

给定：`https://www.figma.com/design/QiEF6w564ggoW8ftcLvdcu/MyDesignSystem?node-id=4185-3778`
- `fileKey` = `QiEF6w564ggoW8ftcLvdcu`
- `nodeId` = `4185-3778` → `4185:3778`

## 第 2 步：找出还没对应的组件

用户给的网址可能指向一个框、一个实例或一个变体——不一定是组件集或独立组件。调用 MCP 工具 `get_code_connect_suggestions`，参数：
- `fileKey`——来自第 1 步
- `nodeId`——来自第 1 步（冒号格式）
- `excludeMappingPrompt`——`true`（返回一个轻量的、还没对应的组件列表）

这个工具会找出选区里已发布、但还没有 Code Connect 对应的组件。

**处理返回结果：**

- **“No published components found in this selection”**（选区里没有已发布的组件）——这个节点里没有已发布的组件。告诉用户需要先在 Figma 里把组件发布到团队库，然后停下。
- **“All component instances in this selection are already connected to code via Code Connect”**（选区里所有组件实例都已经通过 Code Connect 连接到代码）——全部已经对应好了。告诉用户，然后停下。
- **带组件列表的正常返回**——取出每个返回组件的 `mainComponentNodeId`。后面所有步骤都用这些解析出来的节点 ID（而不是网址里原来的那个）。如果返回了多个组件（例如用户选了一个包含几个不同组件实例的框），对每一个都重复第 3–6 步。

## 第 3 步：获取组件属性

调用 MCP 工具 `get_context_for_code_connect`，参数：
- `fileKey`——来自第 1 步
- `nodeId`——第 2 步解析出来的 `mainComponentNodeId`
- `clientFrameworks`——根据 `figma.config.json` 的 `parser` 字段决定（例如 `"react"` → `["react"]`）
- `clientLanguages`——根据项目文件扩展名推断（例如 TypeScript 项目 → `["typescript"]`，JavaScript → `["javascript"]`）

有多个组件时，每个节点 ID 调用一次。

返回结果里有 Figma 组件的**属性定义**——记下每个属性的名字和类型：
- **TEXT**——文字内容（标签、标题、占位文字）
- **BOOLEAN**——开关（显示/隐藏图标、禁用状态）
- **VARIANT**——枚举选项（尺寸、变体、状态）
- **INSTANCE_SWAP**——绑定到特定组件、可替换的嵌套实例（图标、头像）
- **SLOT**——灵活的内容区域（自由布局、混合的子元素）；在模板里用 `getSlot()`（和 INSTANCE_SWAP 不是一回事）

保存这份属性列表——第 5 步写模板时要用。

## 第 4 步：找到对应的代码组件

如果用户没有指定要连接哪个代码组件：

1. 查看 `figma.config.json` 里的 `paths` 和 `importPaths`，找到组件放在哪里
2. 在代码库里搜索和 Figma 组件名匹配的组件。如果 `figma.config.json` 没有指定路径，就查看常见目录（`src/components/`、`components/`、`lib/ui/`、`app/components/`）
3. 阅读候选文件，把它们的 props 接口和第 3 步的 Figma 属性做比较——找匹配的变体类型、尺寸选项、布尔开关和插槽 props
4. 如果有多个候选都匹配，选 props 接口最接近的那个，并向用户解释你的理由
5. 如果找不到匹配的，列出最接近的 2 个候选，请用户确认或提供正确的路径

进入第 5 步之前**先和用户确认**。说明匹配结果：你找到了哪个代码组件、它在哪里、为什么匹配（props 对应关系、命名、用途）。

读取 `figma.config.json` 里的导入路径别名——`importPaths` 部分把 glob 模式对应到导入说明符，`paths` 部分把这些说明符对应到目录。

阅读代码组件的源码，了解它的 props 接口——这决定了第 5 步怎样把 Figma 属性对应到代码 props。

## 第 5 步：创建模板文件（.figma.ts）

### 文件位置

把文件放在已有的 Code Connect 文件旁边。查看 `figma.config.json` 的 `include` 模式找到正确的目录。**文件名用 `ComponentName.figma.ts`——绝不用 `ComponentName.figma.tsx`。** `.figma.tsx` 扩展名是基于解析器的格式；不要新建这种文件，也不要修改已有的。

### 模板结构

每个模板文件都按这个结构：

```ts
// url=https://www.figma.com/file/{fileKey}/{fileName}?node-id={nodeId}
// source={path to code component from Step 4}
// component={code component name from Step 4}
import figma from 'figma'
const instance = figma.selectedInstance

// Extract properties from the Figma component (see property mapping below)
// ...

export default {
  example: figma.code`<Component ... />`,       // Required: code snippet
  imports: ['import { Component } from "..."'], // Optional: import statements
  id: 'component-name',                         // Required: unique identifier
  metadata: {                                    // Optional
    nestable: true,                              // true = inline in parent, false = show as pill
    props: {}                                    // data accessible to parent templates
  }
}
```

（代码注释意思：开头三行分别是 Figma 网址、第 4 步找到的代码组件路径、第 4 步找到的代码组件名；“从 Figma 组件取出属性（见下面的属性对应）”；example 必填，是代码片段；imports 可选，是导入语句；id 必填，是唯一标识；metadata 可选；nestable 为 true 表示在父组件里内联显示，false 表示显示成一个小标签；props 是父模板能访问到的数据。）

### 属性对应

用第 3 步的属性列表来取值。每种 Figma 属性类型，用对应的方法：

| Figma 属性类型 | 模板方法 | 什么时候用 |
|---|---|---|
| TEXT | `instance.getString('Name')` | 标签、标题、占位文字 |
| BOOLEAN | `instance.getBoolean('Name', { true: ..., false: ... })` | 切换显示、条件 props |
| VARIANT | `instance.getEnum('Name', { 'FigmaVal': 'codeVal' })` | 尺寸、变体、状态枚举 |
| INSTANCE_SWAP | `instance.getInstanceSwap('Name')` | 固定组件插槽里被替换的实例（然后用 `hasCodeConnect()` / `executeTemplate()`）——不要和下面的 SLOT 属性搞混 |
| SLOT | `instance.getSlot('Name')` | 只在 Figma 属性类型是 **SLOT** 时用于自由的插槽内容 
| （子图层） | `instance.findInstance('LayerName')` | 没有对应属性的、有名字的子实例 |
| （文字图层） | `instance.findText('LayerName')` → `.textContent` | 有名字的图层里的文字内容 |

**TEXT**——直接取字符串值：
```ts
const label = instance.getString('Label')
```

**VARIANT**——把 Figma 的枚举值对应到代码的值：
```ts
const variant = instance.getEnum('Variant', {
  'Primary': 'primary',
  'Secondary': 'secondary',
})

const size = instance.getEnum('Size', {
  'Small': 'sm',
  'Medium': 'md',
  'Large': 'lg',
})
```

**BOOLEAN**——简单的布尔值，或者对应到某些值：
```ts
// Simple boolean
const disabled = instance.getBoolean('Disabled')

// Mapped to code values (e.g. when the code prop is an enum, not a boolean)
const size = instance.getBoolean('Show Label', { true: 'large', false: 'small' })
```

（代码注释意思：简单的布尔值；对应到代码的值（例如代码里的 prop 是枚举而不是布尔值时）。）

**在有合理对应关系的地方，把 Figma 属性对应到代码 props。** Figma 属性和代码 props 不总是一一对应的——有些 Figma 属性能直接对应（按名字，或者通过上面的 API 方法），有些在代码里没有等价物。有对应的地方就用；没有合适的，就省略这个 Figma 属性，而不是编造一个代码 prop。绝不要输出一个在代码组件 `Props` 接口里不存在的属性名。

### 穷尽地处理变体

当一个 VARIANT 属性有多个可能的值时，`getEnum` 的对应表**必须列出** `get_context_for_code_connect` 返回的**每一个值**。不要漏掉值——没对应的值会悄悄返回 `undefined`，产生坏掉的输出。

```ts
// WRONG — omits 'Warning', which will render as undefined
const status = instance.getEnum('Status', {
  'Success': 'success',
  'Error': 'error',
})

// CORRECT — every value is mapped
const status = instance.getEnum('Status', {
  'Success': 'success',
  'Error': 'error',
  'Warning': 'warning',
  'Info': 'info',
})
```

（代码注释意思：WRONG（错误）——漏了 'Warning'，它会渲染成 undefined；CORRECT（正确）——每个值都对应了。）

当**两个或更多 VARIANT 属性组合起来**产生不同的代码输出时，生成穷尽的条件分支。例如 2 个变体 × 2 个值 = 4 个分支：

```ts
const type = instance.getEnum('Type', { 'Filled': 'filled', 'Outlined': 'outlined' })
const status = instance.getEnum('Status', { 'Success': 'success', 'Error': 'error' })

let colorClass
if (type === 'filled' && status === 'success') {
  colorClass = 'bg-green-500 text-white'
} else if (type === 'filled' && status === 'error') {
  colorClass = 'bg-red-500 text-white'
} else if (type === 'outlined' && status === 'success') {
  colorClass = 'bg-transparent border-green-500'
} else if (type === 'outlined' && status === 'error') {
  colorClass = 'bg-transparent border-red-500'
}
```

如果这些组合产生的输出是**重复的**（例如 `Size` 不会改变片段的结构——只是作为一个 prop 传下去），每个变体一个 `getEnum` 对应就够了——不需要交叉组合的分支。

**INSTANCE_SWAP**——访问可替换的组件实例：
```ts
const icon = instance.getInstanceSwap('Icon')
let iconCode
if (icon && icon.type === 'INSTANCE') {
  iconCode = icon.executeTemplate().example
}
```

**SLOT**——只有当第 3 步报告的 Figma 组件属性类型是 **`SLOT`** 时，`getSlot(propName)` 才有效。不要对 **INSTANCE_SWAP** 属性用 `getSlot()`（那些用 `getInstanceSwap()`）。插槽是组件定义里明确的“内容区域”，不是一般的嵌套实例。

- **签名：** `getSlot(propName: string): ResultSection[] | undefined`
```ts
// Figma property "Content" must be type SLOT in component properties
const content = instance.getSlot('Content')

export default {
  example: figma.code`<Card>${content}</Card>`,
  // ...
}
```

（代码注释意思：Figma 属性 "Content" 在组件属性里必须是 SLOT 类型。）

### 标签模板里的插值

在标签模板里插入值时，用正确的包裹方式：
- **字符串值**（`getString`、`getEnum`、`textContent`）：用引号包起来 → `variant="${variant}"`
- **实例/片段值**（`executeTemplate().example`）：用花括号包起来 → `icon={${iconCode}}`
- **插槽片段**（`getSlot()` 的结果——`ResultSection[] | undefined`）：直接插在 `` figma.code`...` `` 里（和嵌套的代码片段形式一样），例如 `` figma.code`<Select>${content}</Select>` ``——不要当成普通字符串
- **布尔的裸 props**：用条件 → `${disabled ? 'disabled' : ''}`

### 查找后代图层

当你需要访问没有作为组件属性暴露出来的子元素时：

| 方法 | 什么时候用 |
|---|---|
| `instance.getInstanceSwap('PropName')` | Figma 属性类型是 **INSTANCE_SWAP**（固定的被替换实例） |
| `instance.getSlot('PropName')` | Figma 属性类型是 **SLOT**（自由的内容区域） |
| `instance.findInstance('LayerName')` | 你知道子图层的名字（没有组件属性） |
| `instance.findText('LayerName')` → `.textContent` | 你需要某个有名字的文字图层里的文字内容 |
| `instance.findConnectedInstance('id')` | 你知道子元素的 Code Connect `id` |
| `instance.findConnectedInstances(fn)` | 你需要多个符合筛选条件的、已连接的子元素 |
| `instance.findLayers(fn)` | 你需要任何符合筛选条件的图层（文字 + 实例） |

### 嵌套的可配置实例

一个组件可能包含**没有作为组件属性暴露**（没有 INSTANCE_SWAP）、但仍然**可以独立配置**的子实例——它们有自己的变体、属性或替换插槽。这些必须动态解析，不能写死。

1. **检查子元素是否已经有 Code Connect 模板**——用 `get_code_connect_suggestions`，或者查看项目里已有的 `.figma.ts` 文件。
2. **如果没有模板，就为子元素创建一个**，让它单独使用和嵌套时都能正确渲染。
3. **在父模板里引用子元素**，用 `findInstance()` 或 `findConnectedInstance()`，然后调用 `executeTemplate()`。

```ts
// Parent template — the Badge child isn't a prop, but it's configurable
const badge = instance.findInstance('Status Badge')
let badgeCode
if (badge && badge.type === 'INSTANCE') {
  badgeCode = badge.executeTemplate().example
}

export default {
  example: figma.code`<Card>${badgeCode}</Card>`,
  // ...
}
```

（代码注释意思：父模板——Badge 子元素不是一个 prop，但它是可配置的。）

这适用于图标、徽章、标签，以及任何其他本身可配置的嵌套实例——永远要连接它们并动态渲染，绝不要写死它们的内容。

### 嵌套组件的例子

多层嵌套的组件，或者在模板之间传递 metadata prop，见 [advanced-patterns.md](references/advanced-patterns.md)。

```ts
const icon = instance.getInstanceSwap('Icon')
let iconSnippet
if (icon && icon.type === 'INSTANCE') {
  iconSnippet = icon.executeTemplate().example
}

export default {
  example: figma.code`<Button ${iconSnippet ? figma.code`icon={${iconSnippet}}` : ''}>${label}</Button>`,
  // ...
}
```

### 条件 props

```ts
const variant = instance.getEnum('Variant', { 'Primary': 'primary', 'Secondary': 'secondary' })
const disabled = instance.getBoolean('Disabled')

export default {
  example: figma.code`
    <Button
      variant="${variant}"
      ${disabled ? 'disabled' : ''}
    >
      ${label}
    </Button>
  `,
  // ...
}
```

## 第 6 步：验证

把 `.figma.ts` 文件读回来，对照下面这些检查：

- **文件类型和格式正确（第一个检查这个）**——文件是 `ComponentName.figma.ts`（**不是** `.figma.tsx`），它的默认导出是用 `` figma.code`...` `` 标签模板写的无解析器模板。它**不能**用 `figma.connect()`（基于解析器的格式）。如果你写了 `.figma.tsx` 或 `figma.connect()`，丢掉它，重写成 `.figma.ts` 的 `figma.code` 模板。
- **属性覆盖**——第 3 步的每个 Figma 属性都应该在模板里有交代。标出任何漏掉的，问用户是不是有意省略的。
- **代码有效、类型正确**——输出的所有代码都必须有效，并且符合代码组件的 `Props` 接口的类型。绝不要编造组件属性——如果某个 Figma 属性没有对应的代码 prop，就省略它，而不是编一个。
- **没有写死的子元素**——确认每个 INSTANCE_SWAP 属性和子组件插槽都用了动态 API（`getInstanceSwap()`、`findInstance()`、`findConnectedInstance()` 等）配合 `executeTemplate()`。任何插槽里都不应该有写死的组件内容。
- **规则和常见坑**——检查下面列出的常见错误（用字符串拼接模板结果、不必要的 `hasCodeConnect()` 判断、漏掉 `type === 'INSTANCE'` 检查等）
- **插值的包裹**——字符串（`getString`、`getEnum`、`textContent`）用引号包，实例/片段值（`executeTemplate().example`）用花括号包，插槽片段（`getSlot`）作为代码片段插在 `` figma.code`...` `` 里，布尔值用条件

如果有任何拿不准的地方，查阅 [api.md](references/api.md) 了解 API 细节，查阅 [advanced-patterns.md](references/advanced-patterns.md) 了解复杂的嵌套。

## 内联速查表

### `instance.*` 方法

| 方法 | 签名 | 返回 |
|---|---|---|
| `getString` | `(propName: string)` | `string` |
| `getBoolean` | `(propName: string, mapping?: { true: any, false: any })` | `boolean \| any` |
| `getEnum` | `(propName: string, mapping: { [figmaVal]: codeVal })` | `any` |
| `getInstanceSwap` | `(propName: string)` | `InstanceHandle \| null` |
| `getSlot` | `(propName: string)` | `ResultSection[] \| undefined` |
| `getPropertyValue` | `(propName: string)` | `string \| boolean` |
| `findInstance` | `(layerName: string, opts?: SelectorOptions)` | `InstanceHandle \| ErrorHandle` |
| `findText` | `(layerName: string, opts?: SelectorOptions)` | `TextHandle \| ErrorHandle` |
| `findConnectedInstance` | `(codeConnectId: string, opts?: SelectorOptions)` | `InstanceHandle \| ErrorHandle` |
| `findConnectedInstances` | `(selector: (node) => boolean, opts?: SelectorOptions)` | `InstanceHandle[]` |
| `findLayers` | `(selector: (node) => boolean, opts?: SelectorOptions)` | `(InstanceHandle \| TextHandle)[]` |

### InstanceHandle 的方法

| 方法 | 返回 |
|---|---|
| `hasCodeConnect()` | `boolean` |
| `executeTemplate()` | `{ example: ResultSection[], metadata: Metadata }` |
| `codeConnectId()` | `string \| null` |

### TextHandle 的属性

| 属性 | 类型 |
|---|---|
| `.textContent` | `string` |
| `.name` | `string` |

### SelectorOptions

```ts
{ path?: string[], traverseInstances?: boolean }
```

- `traverseInstances: true`——当目标在另一个嵌套实例里面时必须加。不加的话，`findInstance`/`findText` 只搜索当前实例自己的图层，遇到嵌套实例的边界就停下。
- `path: string[]`——当多个后代有相同的图层名时用来区分。列出到达目标的路径上必须出现的父图层名。

**例子：**

```ts
// Layer hierarchy:
//   A > C (instance) > "mychild"
// "mychild" sits inside nested instance C, so plain findInstance returns ErrorHandle.
instance.findInstance('mychild', { traverseInstances: true })

// Layer hierarchy:
//   A > C (instance) > "mychild"
//   A > D (instance) > "mychild"
// Two "mychild" layers exist — use path to pick the one under C.
instance.findInstance('mychild', { traverseInstances: true, path: ['C'] })
```

（代码注释意思：第一个例子——图层层级是 A > C（实例）> "mychild"；"mychild" 在嵌套实例 C 里面，所以普通的 findInstance 会返回 ErrorHandle。第二个例子——有两个 "mychild" 图层，分别在 C 和 D 下面；用 path 选出 C 下面的那个。）

**什么时候从父模板深入到嵌套实例里：** 只有当父代码组件（来自第 4 步）本身把这个嵌套图层当作一个 prop 值接收时（例如 `<C show={<B />} />`——A 把 B 转交给 C）。如果父组件只是组合了 C，而 C 在内部渲染 B，就用 `executeTemplate()` 解析 C，让 C 自己的模板去处理 B——不要在父级重复渲染 B。

### 导出结构

```ts
export default {
  example: figma.code`...`,                      // Required: ResultSection[]
  id: 'component-name',                         // Required: string
  imports: ['import { X } from "..."'],          // Optional: string[]
  metadata: { nestable: true, props: {} }        // Optional
}
```

（代码注释意思：example 必填，类型 ResultSection[]；id 必填，字符串；imports 可选，字符串数组；metadata 可选。）

## 规则和常见坑

1. **绝不要用字符串拼接模板结果。** `executeTemplate().example` 是一个 `ResultSection[]` 对象，不是字符串。用 `+` 或 `.join()` 会产生 `[object Object]`。永远在标签模板里插值：`` figma.code`${snippet1}${snippet2}` ``

2. **不要用 `hasCodeConnect()` 判断。** 在 `type === 'INSTANCE'` 检查之后，直接对任何实例调用 `executeTemplate()`。运行时会自动处理没有 Code Connect 的实例。

   ```ts
   // WRONG — hasCodeConnect() gate drops non-CC instances
   if (icon && icon.type === 'INSTANCE' && icon.hasCodeConnect()) {
     iconCode = icon.executeTemplate().example
   }

   // CORRECT — let the runtime handle all instances
   if (icon && icon.type === 'INSTANCE') {
     iconCode = icon.executeTemplate().example
   }
   ```

   （代码注释意思：WRONG（错误）——hasCodeConnect() 判断会丢掉没有 Code Connect 的实例；CORRECT（正确）——让运行时处理所有实例。）

3. **调用 `executeTemplate()` 之前检查 `type === 'INSTANCE'`。** `findInstance()`、`findConnectedInstance()` 和 `findText()` 失败时返回的是一个 `ErrorHandle`（为真值，但不是真正的节点）——而不是 `null`。一定要加类型检查避免崩溃：`if (child && child.type === 'INSTANCE') { ... }`

4. **当插槽有对应的组件属性时，优先用 `getInstanceSwap()` 而不是 `findInstance()`。** 图标被替换成另一个名字时，`findInstance('Star Icon')` 就失效了；不管插槽里是哪个实例，`getInstanceSwap('Icon')` 都能用。

5. **只在 Figma 属性类型是 `SLOT` 时才用 `getSlot()`。** 对于 **INSTANCE_SWAP** props，用 `getInstanceSwap()`（返回 `InstanceHandle`）。`getSlot()` 返回的是结构化的插槽片段，不是实例——绝不要对它的返回值调用 `executeTemplate()`。

6. **属性名区分大小写**，必须和 `get_context_for_code_connect` 返回的完全一致。

7. **正确处理多个模板数组。** 遍历子元素时，把每个结果放在单独的变量里，分别插值——不要用 `.map().join()`：
   ```ts
   // Wrong:
   items.map(n => n.executeTemplate().example).join('\n')

   // Correct — use separate variables:
   const child1 = items[0]?.executeTemplate().example
   const child2 = items[1]?.executeTemplate().example
   export default { example: figma.code`${child1}${child2}` }
   ```

   （代码注释意思：Wrong = 错误；Correct = 正确——用单独的变量。）

7. **绝不要写死插槽或子元素的内容。** 永远动态地解析子实例——INSTANCE_SWAP 属性用 `getInstanceSwap()`，直接子元素用 `findInstance()`/`findConnectedInstance()`——并通过 `executeTemplate()` 渲染它们。绝不要根据图层名构造 JSX（例如 `<StarIcon />`），也不要猜导入路径。如果一个实例没有 Code Connect，就省略它——不要加写死的备用内容。

   ```ts
   // WRONG — hardcodes the icon from its layer name
   example: figma.code`<Button icon={<StarIcon />}>Submit</Button>`

   // CORRECT — resolves dynamically, works for any swapped icon
   const icon = instance.findInstance('Icon')
   let iconCode
   if (icon && icon.type === 'INSTANCE') {
     iconCode = icon.executeTemplate().example
   }
   example: figma.code`<Button${iconCode ? figma.code` icon={${iconCode}}` : ''}>...</Button>`
   ```

   （代码注释意思：WRONG（错误）——根据图层名写死了图标；CORRECT（正确）——动态解析，对任何替换后的图标都有效。）

8. **尽量用一个代码 prop 表示每个 Figma 属性。** 代码组件的 `Props` 接口（来自第 4 步）是属性名的权威列表。对每个 Figma 属性，想清楚用第 5 步的 API 方法表示它的正确方式——名字直接匹配、值转换，或者任何合适的方式。如果完全没有合适的代码 prop，就省略它——不要编造 prop 名。

## 完整的例子

给定网址：`https://figma.com/design/abc123/MyFile?node-id=42-100`

**第 1 步：** 解析网址。
- `fileKey` = `abc123`
- `nodeId` = `42-100` → `42:100`

**第 2 步：** 用 `fileKey: "abc123"`、`nodeId: "42:100"`、`excludeMappingPrompt: true` 调用 `get_code_connect_suggestions`。
返回一个组件，`mainComponentNodeId: "42:100"`。如果返回为空，停下并告诉用户。如果返回了多个组件，对每一个重复第 3–6 步。

**第 3 步：** 用 `fileKey: "abc123"`、`nodeId: "42:100"`（来自第 2 步）、`clientFrameworks: ["react"]`、`clientLanguages: ["typescript"]` 调用 `get_context_for_code_connect`。

返回的属性包括：
- Label（TEXT）
- Variant（VARIANT）：Primary、Secondary
- Size（VARIANT）：Small、Medium、Large
- Disabled（BOOLEAN）
- Has Icon（BOOLEAN）
- Icon（INSTANCE_SWAP）

**第 4 步：** 搜索代码库 → 找到 `Button` 组件。阅读它的源码确认 props：`variant`、`size`、`disabled`、`icon`、`children`。导入路径：`"primitives"`。

**第 5 步：** 创建 `src/figma/primitives/Button.figma.ts`：

```ts
// url=https://figma.com/design/abc123/MyFile?node-id=42-100
// source=src/components/Button.tsx
// component=Button
import figma from 'figma'
const instance = figma.selectedInstance

const label = instance.getString('Label')
const variant = instance.getEnum('Variant', {
  'Primary': 'primary',
  'Secondary': 'secondary',
})
const size = instance.getEnum('Size', {
  'Small': 'sm',
  'Medium': 'md',
  'Large': 'lg',
})
const disabled = instance.getBoolean('Disabled')
const hasIcon = instance.getBoolean('Has Icon')
const icon = hasIcon ? instance.getInstanceSwap('Icon') : null
let iconCode
if (icon && icon.type === 'INSTANCE') {
  iconCode = icon.executeTemplate().example
}

export default {
  example: figma.code`
    <Button
      variant="${variant}"
      size="${size}"
      ${disabled ? 'disabled' : ''}
      ${iconCode ? figma.code`icon={${iconCode}}` : ''}
    >
      ${label}
    </Button>
  `,
  imports: ['import { Button } from "primitives"'],
  id: 'button',
  metadata: { nestable: true }
}
```

**第 6 步：** 把文件读回来，检查语法。

## 更多参考

高级用法（多层嵌套组件、用 `findConnectedInstances` 筛选、在父/子模板之间传递 metadata prop）：

- [api.md](references/api.md)——完整的 Code Connect API 参考
- [advanced-patterns.md](references/advanced-patterns.md)——高级嵌套、metadata props 和后代图层的用法
