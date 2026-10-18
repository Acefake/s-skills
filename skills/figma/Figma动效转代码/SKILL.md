---
name: Figma动效转代码
description: 把 Figma 里的动效和动画翻译成可以上线的应用代码。在根据 Figma 设计实现动画/动效时使用——用户说“implement this motion”（实现这个动效）、“add animation from Figma”（加上 Figma 里的动画）、“animate this component”（让这个组件动起来），或者给了一个节点带动画的 Figma 网址，或者 `get_design_context` 返回了动效数据、或提示你调用 `get_motion_context` 的时候。
disable-model-invocation: false
---

> 翻译自 Figma 官方仓库 https://github.com/figma/mcp-server-guide （skills/figma-implement-motion，commit f278942）的 `figma-implement-motion` skill，原作者 Figma，许可证：未注明许可证（仓库里没有找到 LICENSE 文件），仅供自用。
> 说明：参考文件 `references/` 一共约 45 KB，加上 SKILL.md 超过 30 KB，保留英文原文 ⚠️。工具名、字段名、代码保持原样。链接里的 `../figma-use/...` 已经改成 `../Figma插件基础/...`，正文里提到的其他 skill 也换成了中文名。
> 英文名备份：s-figma-implement-motion

# 实现动效

## 概述

这个 skill 指导你把 Figma 里的动画和过渡翻译成能运行的代码（motion.dev、CSS 关键帧，或者某个框架专用的库）。

Figma 通过两个工具提供动效：

- `get_motion_context`——权威的动效工具。返回完整的带动画节点清单、预先算好的代码片段（CSS `@keyframes` + motion.dev）、没有代码片段时的备用关键帧绑定，以及递归的时间轴协调提示（`timelineCohorts`）。**它是动画数据、以及哪些节点 ID 会动的唯一可信来源。**
- `get_design_context`——设计的**结构**：布局、尺寸、素材、样式、Code Connect 提示、截图上下文，有时还有带动画元素上的**动效位置标记**（`data-node-id`，拆分节点上还有 `data-motion-keys` / `data-motion-wrapper-for` / `data-motion-transform-template`）。它可能把一个带动画的节点渲染成普通元素（`div`、`p`、`span` 等），也可能渲染成动效元素（`motion.div`）；它不会把动画数值写进去。

**两者通过节点 id 关联起来，这就是整个工作流程。** `get_motion_context` 告诉你哪些节点会动，并给出关键帧数值、缓动、时间和代码片段。`get_design_context` 告诉你这些节点长什么样、放在哪里。对 `get_motion_context.nodes` 里的每个节点，在设计上下文里找到对应的 `data-node-id`，把动效合并进那个结构——当结构元素是普通元素时，加上或包一层 `motion.{tag}`。当设计上下文复用了一个 Figma 组件时，动效节点可能还带着 `fallbackNodeId`；只在先试过精确的 `nodeId` 之后，才把它当作备用。

## Skill 的边界

- 当交付物是用户代码仓库里的动效代码时，用这个 skill。
- 如果用户要求在 Figma 里面创建/编辑动画，切换到 [Figma插件基础](../Figma插件基础/SKILL.md)，按那个 skill 来做。
- 这个 skill 目前覆盖的是 `get_motion_context` 输出的**动画**（代码片段加上备用关键帧轨道，包括用预设做出、并被解析成这些形式的动效）。更广的交互式变体流程，在代码里可能还需要针对具体产品的状态处理。

## 前提条件

- Figma MCP 服务器已连接并且能访问。
- 已从用户给的 Figma 网址里解析出节点 ID。网址格式：`https://figma.com/design/:fileKey/:fileName?node-id=1-2`——取出 `fileKey`（`/design/` 后面那一段）和 `nodeId`（`node-id` 查询参数的值，例如 `42-15`）。
- 目标代码库。动效的输出格式会根据技术栈调整（见 [框架推荐](#框架推荐)）。

## 选用哪个工具

实现动效时，两个工具都要用，各有分工：

| 情况 | 工具 | 原因 |
|---|---|---|
| 了解静态结构、素材、样式、Code Connect 或视觉布局 | `get_design_context` | 给出组件/页面的代码参考和素材网址，你需要它们才能正确放置带动画的节点。 |
| 获取任何节点的动画数据 | `get_motion_context` | 专门为动效做的，是时间、缓动、代码片段和关键帧的唯一可信来源。 |
| 节点上有动效标记（`data-motion-keys`、`data-motion-wrapper-for`） | 用标记决定拆分后的*位置*，用 `get_motion_context` 取*数值* | 拆分标记告诉你哪条轨道放在哪个元素上；关键帧/缓动/时间和带动画节点的清单来自 `get_motion_context`。 |

需要一次调用就拿到所有子孙节点的动效时，`get_motion_context` 接受 `recursive: true`（上限 500 个节点）。

## 必须遵守的工作流程

### 第 1 步：确认有静态设计上下文

```
get_design_context(fileKey=":fileKey", nodeId="<node-id>")
```

如果这个节点已经调用过 `get_design_context`，就复用那次的输出。如果没有，现在正常调用。

把它当作**结构的依据**——层级、尺寸、样式、素材、Code Connect 提示、截图上下文，以及它碰巧带上的任何动效位置标记（第 3 步）。带动画节点的清单和动画数值来自 `get_motion_context`（第 2 步）。

### 第 2 步：获取权威的动效数据

```
get_motion_context(fileKey=":fileKey", nodeId="<node-id>", recursive=true)
```

返回结果的结构（每个带动画的节点一条）：

- `codeSnippets`——预先生成的 CSS `@keyframes` 和 motion.dev 字符串。**直接用它们。** 不要从备用轨道数据重新生成。
- `textAnimations`——这些文字组动画一定要实现。如果同时也有 `codeSnippets`，两个都要用上；代码片段不能代替 `textAnimations`。
  - 用 `derivedTimingInfo`：每个组从 `startMs + orderPosition * staggerStepMs` 开始，播放 `groupDurationMs` 那么久。`startMs` 已经包含了 `delayMs`；不要再加一次。`presetDurationMs` 指的是整个错开序列的总长，不是每个组的。
  - 根据 `grouping` 和 `order` 计算 `orderPosition`，不要总是用字符的下标（`CENTER_OUT` 是让对称的两两一起开始）。给 Motion.dev 用时把毫秒换成秒，并把给定的缓动套进 `groupDurationMs` 里，弹簧也一样。
- `keyframeBindings`——绑定好的关键帧轨道，包括从预设得出、被解析成轨道数据的动效；只在两种代码片段格式都没有时，作为备用数据提供。
- `motionSummary`——用自然语言描述动画，每个字段一行。**只在没有代码片段时才有**（只有关键帧绑定、代码生成没法表达成 CSS/motion.dev 的动效）。有它时就照它来做；只要有代码片段，就忽略它。
- `fallbackNodeId`——可选的备用 id，用来匹配组件化的设计上下文。如果 `nodeId` 是像 `I4005:6111;30:8005` 这样带实例前缀的 id，D2R（设计转代码）可能会改用背后组件的 id 来渲染可复用的组件主体，比如 `4002:3957`。这种情况下，如果按精确的 `nodeId` 查不到，`fallbackNodeId` 就是要找的那个 `data-node-id`。

递归的返回结果里还有 `timelineCohorts`——一个**顶层**数组（不是每个节点各有一个），列出共用一条时间轴的节点：`{ rootNodeId, durationMs, loopMode: 'once' | 'loop' | 'boomerang', memberNodeIds[] }`。对于多个节点协同的动效，用 `durationMs`（÷1000 得到秒）和 `loopMode`，从同一个共享的生命周期驱动所有 `memberNodeIds`——不要根据兄弟节点的顺序去推断时间。

对 AI 来说重要的实现细节：

- 有代码片段时，`motionSummary`、`timelineDurationMs` 和 `transformOrigin` 可能会被省略，以减小数据量——代码片段里已经带了时长 + transform-origin（motion.dev 的 `duration` / `style={{ transformOrigin }}`，或者 CSS 的 `animation` / `transform-origin`），时间轴组里也带了 `durationMs`。字段缺失从来不代表“没有动画”。
- 递归的返回结果会给完全重复的代码片段去重。一个代码片段可能被替换成一条注释，指向第一个动效完全相同的节点；复用同一个组件、变体、class 或常量，而不是再写第二份动画。
- MCP 服务器会根据 `clientFrameworks` 推断给 CSS 还是 motion.dev 的代码片段；如果返回结果里只有一种代码片段格式，就把那种格式改写成适合用户技术栈的样子，而不是以为另一种格式失败了。

### 第 3 步：合并静态和动效上下文

- 从 `get_motion_context.nodes` 出发，而不是从静态 JSX 里看得见的 `motion.*` 标签出发。**返回的每个节点都是带动画的。** 先按精确的 `nodeId` / `data-node-id` 把每个动效节点对应回 `get_design_context`。当且仅当没有精确匹配时，才试 `fallbackNodeId` / `data-node-id`。两个 id 都失败之后，才退回到按节点名/类型和截图位置来对应。
- **精确 id 匹配优先于 `fallbackNodeId`。** `fallbackNodeId` 指向 D2R 可能在可复用组件里输出的背后组件 id。这个组件的每个实例都共用它。如果精确的 `nodeId` 在设计上下文里存在，就把动效加在那里，忽略备用 id。这对根实例的动画至关重要：同一个组件的一个实例，旋转或移动的方式可能和另一个实例不同，把那个动效加到共享的组件主体上，会让所有实例都错误地动起来。
- **把每个动效节点加到对应的设计上下文结构上，以 `data-node-id` 为键。** 对应的 `data-node-id` 是结构上的锚点，不一定就是最终接收动效的那个 DOM 元素。根据代码片段的形式和位置标记，决定动效是加在这个元素本身、一个包装层、一个内部元素，还是一个内联的 SVG 路径上。`get_design_context` 可能已经输出了去掉数值的 `motion.{tag}`，也可能输出一个普通的结构元素（`div`、`p`、`span`、组件根元素等）。如果它是普通元素，而代码片段的目标是这个元素本身，就把它转成合适的 `motion.{tag}`，或者加一个动效包装层，同时保留节点的文字、子元素、class/样式、属性和 `data-node-id`。加载 [references/examples-and-anti-examples.md](references/examples-and-anti-examples.md) 看这个合并步骤的例子。
- **组件化的子节点动效通常靠备用 id 匹配。** 当设计上下文把一个 Figma 实例提取成一个可复用的 React 组件时，组件主体里的子节点通常带的是背后组件的 id（`4002:3957`），而动效上下文报告的是实时的实例 id（`I4005:6111;30:8005`）。这种情况下，用 `fallbackNodeId` 找到组件主体里的 `data-node-id`，但要让动效只作用于你正在实现的那个渲染出来的实例。如果有多个实例、只有一个的根动效不同，精确 id 匹配能让每个实例的动效保持分开。
- 拆分节点带有 `data-motion-keys` / `data-motion-wrapper-for` 标记——见下面的 _处理交错的变换_。
- **保留 `display: contents` 包装层——除非这个组本身有动画。** 对布局透明的组包装层会以 `contents`（Tailwind 的 `contents`）的形式出现，通常旁边还有不起作用的 `absolute`/`inset-[…]`（这些在 `contents` 盒子上什么也不做）。对于_静态_的组，保留 `display: contents`，让子元素相对于最近的真实祖先定位——把包装层的 `inset` 改成一个定位盒子，会把子元素挂到一个更小的盒子里，导致它们渲染得太小/往里偏。对于_有动画_的组（组节点本身有动效），`display: contents` 带不了变换——把它换成一个真正的定位包装层，把组的动效加在那里。实现这种情况之前先加载 [references/gotchas.md](references/gotchas.md)。
- **`get_motion_context` 是完整的带动画节点清单。** 有些带动画的节点会渲染成普通（非 `motion`）元素——组件实例的根（普通的定位 `<div>`）、文字（`<p>`）、遮罩——它们仍然带着 `data-node-id`。遍历动效结果里的每个节点，把它的动效加到 `data-node-id` 匹配的元素上，按需包装或转换。如果一个带动画的节点在输出里根本没有对应元素（例如一个带动画的遮罩被压平成静态的 `mask-image`），不要悄悄丢掉它——留一条 `// TODO: <nodeId> motion unsupported` 注释，并在你的总结里指出来。
- 如果一个节点出现在动效上下文里，却不在静态 JSX 里，就加上表示它所需的元素——设计上下文的代码只是参考，不是完整的动画清单。
- 设计上下文和动效上下文冲突时（时间/缓动/动画数值），以 `get_motion_context` 为准。
- **路径级的 SVG 动效：把 SVG 内联，给真正的 `<path>` 做动画。** 当 `get_motion_context` 的目标是一个矢量图形的路径（`PATH_TRIM`、`motion.path`、`stroke-dasharray`），而设计上下文把它渲染成了 `<img>` 时，把 SVG 内联，把代码片段加到 `<path>` 上，同时保留布局包装层。这种情况的完整做法见 [references/svg-and-path-motion.md](references/svg-and-path-motion.md)（motion.path、`pathLength="1"`、包装层+路径的分层、CSS 路径裁剪）。

#### 处理交错的变换

一个**同时**带有静态基础变换和动画变换的节点，会被拆到几层嵌套的元素里，让两者正确地叠加而不是互相打架：一个没有 id、带着 `data-motion-wrapper-for="<nodeId>"` 的 `motion.div`（外层包装），包着一个静态变换的 div（例如 `rotate-45` + `hypot()` 尺寸——或者由包装层自己带着 `data-motion-transform-template="<css>"`），里面再包着内层节点（`data-node-id`）。保持 `wrapper > static-transform div > inner`（包装层 > 静态变换 div > 内层）这种嵌套——把它压平会弄坏尺寸和基础变换。

- **按 `data-motion-keys` 放置轨道。** 包装层的 `data-motion-keys`（变换轨道——`x`/`y`/`rotate`/`scaleX`/`scaleY`/`skewX`）放在外层包装上；内层元素的 `data-motion-keys` 放在内层元素上。
- **重新应用 `data-motion-transform-template`。** 如果包装层带着它，设置 `transformTemplate={(_, generated) => "<css> " + generated}`，让动画变换叠加在那个静态布局变换之上。
- **用静态基础值抵消动画变换（避免转两次）。** `get_motion_context` 给的是节点的_绝对_变换，已经包含了那几层 div 施加的静态基础值。在 `rotate-45` 基础上的一个 `[45, 125, 125]` 的 `rotate` 代码片段，意思是包装层要动画的是**偏移量** `[0, 80, 80]`（= 绝对值 − 45），而不是绝对值——否则 45° 会被加两次，元素静止时就停在 90°。没有静态基础值的轨道（例如从 0 开始的 `x`/`y`）原样通过。见交错变换的例子。
- **让布局变换和 Motion 变换分开。** 对每个动画化 `rotate`、`scale` 或 `skew` 的 `motion.*` 元素，确认它没有同时依赖像 `-translate-x-1/2` 或 `-translate-y-1/2` 这样的 Tailwind 布局变换来居中/定位。这些工具类和 Motion.dev 内联写入的 CSS `transform` 属性是同一个，所以 Motion 的变换可能会抹掉布局的平移。如果两个都需要，把元素拆成一个带居中/定位变换的静态布局包装层，和一个带动画 rotate/scale/opacity 的内层 `motion.*` 元素；或者把布局偏移写进 Motion 本身（`x: "-50%"`），并让它在每个关键帧里都存在。

### 第 4 步：在代码里加上动效

- **代码片段里有 motion.dev？** 对 React 目标，原样使用 motion.dev 代码。从 `motion/react` 导入——除非代码库已经在用别的动效库（Framer Motion、React Spring、GSAP），那种情况下把代码片段改写成适合那个库的。改写成另一种技术栈或选库时，加载 [references/framework-recommendations.md](references/framework-recommendations.md)。
- **有 CSS 关键帧？** 用于原生/非 React 的目标，或者代码库里没有 React 动效库的时候。
- **没有代码片段（只有关键帧绑定）？** 根据 `keyframeBindings` + `motionSummary` 搭出等效的 motion.dev/CSS，循环时间取时间轴组的 `durationMs` / `loopMode`，`transformOrigin` / 时长从结构化字段里读。这种情况很少——通常都有代码片段，SwiftUI/iOS 也有（它们拿到的是 CSS 格式）。

### 第 5 步：验证

- 加新的动效导入之前，先看组件已有的动效导入/约定。如果用户已经在用 Framer Motion / React Spring / anime.js，就去适配它，而不是硬塞 motion.dev。
- 在把改动批量应用到很多节点之前，先抽查一个动画能从头到尾跑通（刷新、观察、迭代）。
- 加载 [references/gotchas.md](references/gotchas.md)，它讲了 Figma 动效输出里出现过的具体 bug 和边界情况，并修正生成代码里出现的这类情况。

## 关键规则

这些是一般原则。具体的坑（旋转轴心、HOLD 的含义、颜色插值等）放在分好类的 [参考文件](#参考文件) 里。当这个 skill 的正文提到某个链接的参考文件、而情况又适用时，先加载那个文件再继续。

1. **尊重工具输出的*数值*，而不是它的布局。** 保留 `codeSnippets` 里精确的时间、缓动、关键帧数值和 `transformOrigin`——有代码片段时，不要从 `keyframeBindings` 或结构化字段重新生成（重新生成会在自定义贝塞尔缓动、弹簧近似和过冲数值上丢失精度）。`transformOrigin` 是**每个元素各自的**：每个缩放/旋转的节点都要用它自己的——包括嵌套的缩放元素，不只是最外层的包装——否则元素会绕默认的中心转，从错误的角变大/旋转（见“每个元素各自的 `transformOrigin`”那个例子）。但代码片段只是一个节点的数据，不是拿来复制粘贴的模板：当很多节点共用它时，按第 7 条规则把它提取出来，而不是把代码块粘贴 N 次。
2. **匹配用户已有的动效技术栈。** 加依赖之前，先看组件的导入和旁边的其他动画。如果用户已经有 Framer Motion、React Spring、anime.js、GSAP——就把输出改写成适合他们技术栈的，而不是硬塞 motion.dev。
3. **遵守 `prefers-reduced-motion`。** 加上的任何动效，在 `@media (prefers-reduced-motion: reduce)` 下都必须减弱或关闭——通常是跳过 `animate`（渲染初始/静止状态），或者把时长缩到接近零。这是无障碍的默认要求，不是可选项。
4. **批量之前，先把一个动画从头到尾验证一遍。** 构建、刷新，看完整的一轮时间轴——确认每个带动画的节点都在它的关键帧轨道说的时间出现。“渲染没报错”不等于“渲染正确”。批量做的时候，动效的错误会叠加——一个节点上的缓动错了很容易发现；同样的 bug 出现在二十个节点上，要花好几个小时去理清。
5. **不要编造动效。** 如果结果里某个节点没有动效数据，就让它保持静止。不要从设计的其他地方借缓动/时长的默认值，也不要“因为组件的其他部分都在动”就自动给它加动画。
6. **下载素材，引用本地文件。** `get_design_context` / `get_motion_context` 返回的素材是会过期的网址（`/api/mcp/asset/...`），通常是 SVG。用 `curl -L` 把每个素材下载到项目里，引用下载下来的文件，或者把内容内联（例如在 SwiftUI 上内联 SVG，通过 `NSImage(data:)` 渲染）。不要在应用代码里引用临时的素材网址。对于路径级的 SVG 动效，把 SVG 内联，给真正的路径做动画，而不是把它藏在一个 `<img>` 后面。不要把下载的 SVG 文件当成图片交给 `Read` 工具：SVG 不是支持的图片格式，读取可能会失败或卡住。
7. **把重复的动效提取出来——绝不要给每个元素复制粘贴一份代码片段。** 很多节点通常共用*同一个*动画，只是错开的延迟、偏移或目标值不同。把共享的动效**只实现一次**——一个可复用的动画组件，或者一个以变化的值为参数的 `variants` 对象——从映射的数组渲染（`items.map(...)`），并把重复的字面量（时长、缓动数组、偏移）提取成有名字的常量。动画的*数值*仍然原样来自代码片段（第 1 条规则）；*代码*保持不重复（DRY）。同一个过渡对象粘贴 15 次以上（本该 150 行却写了 800 行）是低质量的结果——还原度和可维护性都会被评判。

## 框架推荐

第 2 条规则讲了总体态度：优先用用户已有的技术栈。如果没有，默认这样：

- **React**：[motion.dev](https://motion.dev)（`motion` 包）。工具直接返回 motion.dev 代码——用它。
- **原生 / 非 React 的网页**：CSS `@keyframes` 配合 `animation` 简写，工具会直接返回。
- **SwiftUI**：原生的 `.animation(...)` 修饰符，从 **CSS** 代码片段翻译过来（`get_motion_context` 不输出 SwiftUI 代码，但 SwiftUI/iOS 客户端仍然会拿到 CSS 格式；只有没有代码片段时，才退回到 `keyframeBindings` / `motionSummary` / 时间轴组）。**只用真实存在的 SwiftUI API**——没有哪个修饰符能直接接收 Figma/CSS 的缓动，所以要加载 [references/framework-recommendations.md](references/framework-recommendations.md#swiftui-translation)，把缓动对应到 SwiftUI 的等价物，并去核实而不是编造。这条路径还在变化中；拿不准时和用户确认。

**对于成熟的效果类型，优先用库，而不是手写 CSS。** 像玻璃/毛玻璃、彩带、粒子系统、基于物理的交互、跟随滚动的动效这类效果，都有久经考验的库实现，处理跨浏览器差异、无障碍和性能都比生成的关键帧好得多。加载 [references/framework-recommendations.md](references/framework-recommendations.md) 查看完整的“按效果类型选库”表。把这些作为建议提出来，而不是硬性要求——由用户决定。

## 例子

需要完整的例子或失败模式时，加载 [references/examples-and-anti-examples.md](references/examples-and-anti-examples.md)。它覆盖了简单的合并流程、需要加上 `motion.*` 的普通文字元素、交错的静态+动画变换、路径级的 SVG 动效，以及反面例子：重建 DOM、节点 id/位置错位、漏掉每个元素各自的 `transformOrigin`。

## 参考文件

六份深入的资料，按需获取。一般的前端问题（性能、单位、无障碍的具体做法）由上面的关键规则处理——这些参考文件只关注 Figma 特有的信息。如果这个 skill 在某条正文指示里提到了其中一个文件，在继续那部分任务之前先加载那个文件。

- [references/examples-and-anti-examples.md](references/examples-and-anti-examples.md)——完整的例子和失败模式。在应用合并工作流、处理交错变换，或者检查生成的实现是否重建了 DOM、调换了节点位置、或丢了 `transformOrigin` 时加载。
- [references/gotchas.md](references/gotchas.md)——Figma 特有的动效 bug 和修法。嵌套组上的旋转/缩放原点、HOLD 缓动的含义、保留 CUSTOM_SPRING、独立轴缩放的歧义、颜色插值。排查意外的运行时表现时加载。**加载这个文件时，一定同时加载 [references/motion-lint-rules.md](references/motion-lint-rules.md)**——坑的条目引用了具体的检查规则，必须告诉用户。
- [references/svg-and-path-motion.md](references/svg-and-path-motion.md)——实现以 SVG 矢量路径为目标的动效（内联素材、`motion.path`、`pathLength="1"`、包装层+路径的分层、CSS 路径裁剪）。当一个矢量图形的代码片段的目标是路径、而不是包装层的变换时加载。
- [references/framework-recommendations.md](references/framework-recommendations.md)——motion.dev、CSS 关键帧、SwiftUI 的默认做法，“按效果类型选库”表（玻璃、彩带、粒子、物理、跟随滚动）。在手写一个效果之前加载。
- [references/unsupported-and-fallbacks.md](references/unsupported-and-fallbacks.md)——目前还不能干净导出的 Figma 动效功能（文字动画、路径动画、遮罩/布尔运算、变体/过渡）。包括退回到视频/lottie 的建议。当工具的返回结果看起来不完整时加载。**加载这个文件时，一定同时加载 [references/motion-lint-rules.md](references/motion-lint-rules.md)**——不支持的条目引用了具体的检查规则，必须告诉用户。
- [references/motion-lint-rules.md](references/motion-lint-rules.md)——检查规则：已知的导出限制（错误和警告），必须告诉用户。生成动效代码时加载，检查是否有正在生效的限制适用。
