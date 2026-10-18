---
name: Figma幻灯片
description: "这个 skill 帮助 AI 助手在 Slides（幻灯片）场景下使用 Figma 的 use_figma MCP 工具。可以和 Figma插件基础 一起使用，Figma插件基础 提供了使用 use_figma 工具的基础知识。"
disable-model-invocation: false
---

> 翻译自 Figma 官方仓库 https://github.com/figma/mcp-server-guide （skills/figma-use-slides，commit f278942）的 `figma-use-slides` skill，原作者 Figma，许可证：未注明许可证（仓库里没有找到 LICENSE 文件），仅供自用。
> 说明：参考文件 `references/` 一共约 47 KB，太大，保留英文原文 ⚠️。下面要求在 `skillNames` 里写的是原名 `figma-use-slides`（给 Figma 做使用统计用），保持原样。链接里的 `../figma-use/...` 已经改成 `../Figma插件基础/...`，正文里提到的其他 skill 也换成了中文名。代码保持原样，代码注释的意思在后面用中文说明。
> 英文名备份：s-figma-use-slides

# use_figma —— 用于 Slides 的 Figma 插件 API skill

这个 skill 包含 `use_figma` MCP 工具在 Slides 里专用的知识。[Figma插件基础](../Figma插件基础/SKILL.md) skill 提供了通过 MCP 执行插件 API 的基础知识，以及这里没有讲到的更高级用法所需的完整 Figma 插件 API。

**为 Slides 操作调用 `use_figma` 时，一定要在用逗号分隔的 `skillNames` 参数里加上 `figma-use-slides`。如果这个 skill 是通过 MCP 资源加载的，必须在名字前面加上 `resource:`（例如 `resource:figma-use-slides`）。** 这是一个用来统计 skill 使用情况的日志参数——它不影响执行。

## 选择怎样搭建一套幻灯片

如果你的环境里还有 `generate_deck` 工具，每个幻灯片请求只选**一种**方法——不要对同一套幻灯片两个都调用。

### 什么时候用哪个

**`use_figma` + 这个 skill（默认）：** 能处理任何 Slides 任务——新幻灯片、修改已有的幻灯片、符合品牌的设计、参照文件的样式、反复打磨、演讲者备注，以及对布局、颜色和字体的完全创意控制。大多数请求用这个。

**`generate_deck`：** 用预先做好、精选过的模板，一次调用就生成一整套幻灯片。适合快速、简单、用户不需要定制设计、品牌匹配或参照文件样式的幻灯片。它不能用自定义模板，不能参照其他 Figma 文件来定设计方向，也不支持在对话里反复编辑或后续修改。

拿不准时，默认用 `use_figma` + 这个 skill——`generate_deck` 能做的它都能做，还能做更多。

### 选定一种，坚持到底

一旦为一套幻灯片选定了方法，就用这种方法完成整个请求。不要先用 `generate_deck` 生成一套，又再用 `use_figma` 创建或填充一个文件——用户最后会得到重复、互相冲突的东西，体验很混乱。

## 关键规则（Slides 专用）

1. **新建的 Slides 文件带有默认的浅色主题。** 通过 `create_new_file` 创建 Slides 文件时，会自动初始化一个默认的浅色主题。这个主题只是结构上的脚手架——你应该用你为这套幻灯片定的设计方向，覆盖主题里的颜色变量和文字样式。不要依赖默认浅色主题的设计令牌，也不要被它影响。
2. **必须先 `appendChild`，再设置 `x`/`y`——每个节点、每一层嵌套都是。** 新建的节点会被悄悄地自动挂到一个位于绝对坐标 `(240, 240)` 的幻灯片上下文里（幻灯片网格的 `GRID_PADDING`）。在 `appendChild` 之前写 `x`/`y`，会让这个值相对那个隐藏的原点保存；之后挂到真正的父节点上时，节点会落在 `(intended − 240, intended − 240)`（意思是“想要的位置减 240”）。这个 bug 是**时有时无的**——同一个脚本里有些框不受影响，所以一次测试能用并不能证明你是安全的。**识别特征：** 如果任何节点最后落在离你设定的位置 `(−240, −240)` 的地方，就是你的代码在最后一次 `appendChild` 之前设置了 `x`/`y`。**不要**试图把 240 加回去来补偿——重试时结果会更糟。改正顺序才对。见 [slide-gotchas.md](references/slide-gotchas.md#position-after-appendchild-critical) 里的辅助函数写法，用了它顺序就不可能写错。
3. **SLIDE_GRID 和 SLIDE_ROW 是不透明的节点**——不要访问它们的 `.fills`、`.effects` 或布局属性。只有 `SLIDE` 节点（类型 `'SLIDE'`）扩展了 `BaseFrameMixin`。**例外：** `SLIDE_ROW.name` 是可以设置的——插件就是这样给幻灯片分区改名的（例如 `slideRow.name = "Intro"`）。见 [slide-lifecycle.md](references/slide-lifecycle.md)。
4. **`get_metadata` 在 Slides 文件上不能用。** 用只读的 `use_figma` 脚本来做验证。在 `closePlugin()` 的输出里返回创建的节点位置，并确认没有重叠的边界框。
5. **不要在 Slides 里调用 `figma.createPage()`。** 它会抛出 `TypeError: figma.createPage no such property 'createPage' on the figma global object`——`createPage()` 只是 Design 文件的 API（`figma.com/design/...`）；Slides 的网址是 `figma.com/slides/...`。改用幻灯片网格（`SLIDE_GRID` / `SLIDE_ROW` / `SLIDE`）来组织幻灯片结构——见 [slide-lifecycle.md](references/slide-lifecycle.md) 和 [slide-grid.md](references/slide-grid.md)。
6. **绝不要为了重做而删除已有的幻灯片。** 被要求改进、重新设计或换样式时，就地修改已有的幻灯片。只有当用户明确要求“从头开始”或“完全重做”时，才删除幻灯片。

## 设计思考

不是每个任务都需要同样深度的设计思考。做任何事之前，先判断你处在哪一档：

- **内容/属性修改**——改文字、换一个颜色、更新一个数字、修对齐、调整元素大小。跳过设计思考。直接改，并和已有的保持一致。
- **结构性的添加**——加幻灯片、重做某一部分的布局、换整套幻灯片的配色、引入一个新的视觉元素。这也包括要求“改进”、“重新设计”或“换样式”——这些是对已有内容的就地修改，不是新做一套。设计思考适用，但用*继承*模式：已有的幻灯片就是你的设计语言。检查它，匹配它的配色、字体、空间习惯和图案。延续这套幻灯片已有的性格，而不是重新发明。
- **新建一套幻灯片**——从零或从一个空白文件开始做。完整的设计思考适用，如下所述。

对已有幻灯片做结构性添加时：改之前先运行检查脚本（见下文）并截图。“用什么配色？”和“用什么字体处理？”的答案已经在文件里了——你的任务是读出来并保持一致。[slide-design.md](references/slide-design.md) 里的设计原则描述的是你要*匹配*的东西，而不是你要*选择*的东西。

### 新幻灯片的设计过程

为一套新幻灯片写任何 Plugin API 代码之前，先决定它应该给人什么*感觉*。Figma 用户对视觉的期望很高——一套看起来像是从普通模板生成器里出来的幻灯片，会因为错误的原因显得扎眼。

1. **读懂需求。** 这套幻灯片要传达什么，给谁看？投资人路演、团队复盘、产品发布、技术深度讲解，都需要不同的视觉处理。设计应该和内容分不开。
2. **看看有没有设计语言。** 发明任何东西之前，先看用户已经给了你什么。提示里的品牌规范——配色、字体规格、logo 规则、语气描述——都是已经做好的设计决定。一个参照 Figma 文件的链接是一套你应该研究、而不是扫一眼的设计语言。用户给的输入越具体，你自己该发明的就越少。当用户提供了参照时，你的角色就从*设计师*变成*诠释者*：提取出设计语言，忠实地用到新内容上。
3. **对剩下的部分表明立场。** 如果用户给了完整的品牌体系，你的创作空间在布局、节奏和构图上——而不在颜色或字体上。如果他们只给了一页幻灯片作灵感，你的空间更大，但仍应呼应它的性格。如果他们什么都没给，那每个决定都归你——选一个配色故事、一种字体处理、一种组织空间的方式，并在每一页上贯彻到底。一套有清晰观点（哪怕是安静的观点）的幻灯片，永远比每个决定都求稳的那套好看。“表明立场”的范围和用户提供的东西成反比。
4. **给它一个标志。** 每套好的幻灯片都至少有一个元素，你脱离上下文看到也能认出来：一套独特的配色、一种出人意料的布局节奏、一种反复出现的形状语言。照着品牌规范做时，这个标志应该*来自*那套品牌语言——放大已有的东西，而不是加进外来的东西。从零设计时，开始搭建之前先决定标志是什么。

### 阅读参照文件

当用户提供一个 Figma 文件的链接作为参照时，设计任何东西之前先研究它。你要提取什么，取决于它是什么文件：

- **Slides 文件**：`get_metadata` 在 Slides 文件上不能用。用 `get_screenshot` 截取单页幻灯片作视觉参照，并用带参照文件 `fileKey` 的 `use_figma` 运行只读脚本，提取主题变量、配色、字体选择和布局模式。
- **Design 文件**：`get_design_context` 给你全面的设计数据——颜色、字体、布局结构。`get_screenshot` 给你视觉参照。两个都用。

在参照文件里要看什么：配色（哪个色相为主、强调色是什么、深色/浅色背景怎么用）、字体选择（字体家族、字重、层级怎么处理）、空间习惯（内容锚定在哪里、留白多少、东西会不会超出边缘）、以及任何反复出现的图案（形状、线条处理、装饰元素）。这些是你继承的决定——其他的都归你。

跟参照跟得多紧，取决于用户要的是什么。“做成像这样的”意思是用新内容复制这套设计语言。“拿这个作灵感”意思是呼应它的性格，但做成你自己的。“这是我们的品牌幻灯片”意思是提取品牌体系并一致地应用。拿不准时，离参照近一点——让用户要求你偏离一点，比让用户要求你撤回和他们品牌冲突的自创决定容易。

加载 [slide-design.md](references/slide-design.md)，获取关于颜色、字体、布局模式、构图以及要避免什么的具体指导。当你有参照文件或品牌规范时，把 slide-design.md 的原则当作用户*没有*做的那些决定的默认值——而不是用来推翻他们已经做了的决定。

## 搭建幻灯片的工作流程

搭建 5 页或更多的新幻灯片时，用这个两阶段的工作流程。专门就搭建幻灯片而言，它取代 [Figma插件基础](../Figma插件基础/SKILL.md) 第 6 节里一般的逐步推进工作流程——原则仍然适用，但节奏变了。

### 第 1 阶段——设计和计划

完成上面的设计思考过程（读懂需求、看看有没有设计语言、表明立场、给它一个标志），然后**在写任何 `use_figma` 代码之前**，做出一份覆盖整套幻灯片的计划：

1. **逐页计划。** 每一页：它的目的/内容、用空间语言描述的布局方式（例如“标题锚定在左上，规格卡片占满右边三分之一，装饰性圆形超出右上边缘”），以及背景处理（深色/浅色/渐变）。计划时**不要**算像素坐标——用空间语言描述布局。坐标计算在生成代码时再做。
2. **共享的常量。** 声明你要用的字体家族和样式，把配色写成有名字的角色（primary、accent、bgDark、surface、textPrimary、textMuted 等），以及反复出现的图案或标志元素。
3. **检查布局是否多样。** 按顺序读一遍各页的计划。如果布局描述感觉重复——“两栏、两栏、网格、两栏”——在搭建之前就重新安排。这是让布局多样化代价最低的时候。反面模式见 [slide-design.md](references/slide-design.md)。
4. **代码开头部分。** 写出你会粘贴在每个搭建脚本开头的可复用开头部分：一个 `const C = { ... }` 配色对象、一个 `Promise.all([...])` 加载字体的代码块，以及来自 [slide-gotchas.md](references/slide-gotchas.md#position-after-appendchild-critical) 的 `addFrame`/`addText`/`addRect` 辅助函数。

### 第 2 阶段——搭建

大批量地执行计划。目标是让“先想再搭”的循环次数最少——而不是让每个脚本里的元素最少。

- **每次 `use_figma` 调用做 3–5 页。** 结构相似的幻灯片（例如一系列产品功能页）可以放在同一批里。每页幻灯片都是一棵独立的子树——不存在跨页的依赖，所以大批量是安全的。
- **批次之间不要重新计划。** 设计在第 1 阶段已经定了。如果一批成功并通过了验证，立刻进入下一批。只有在某一批失败、或者出现需要改变做法的视觉问题时，才重新计划。
- 在每个搭建脚本的开头**粘贴代码开头部分**（颜色、字体、辅助函数）。从第 1 阶段原样复制——不要重新推导。
- 用 [slide-gotchas.md](references/slide-gotchas.md#batch-validation-script) 里确定性的批次验证脚本**验证每一批**。它会在约 3 秒内检查重叠的元素、被裁掉的文字和超出边界的节点。如果检查通过，不用截图直接继续。如果失败，截取受影响的页面，修好再继续。
- **只在检查点截图**——第一批之后（验证视觉体系：颜色、字体、设计方向），以及最后一批之后（整体质量）。每个检查点用内联的 `await slide.screenshot()` 截取 1–2 页有代表性的幻灯片，而不是单独调用 `get_screenshot`。
- 和往常一样，每个搭建脚本都要**返回所有创建的节点 ID**。

## 分区

一个分区就是幻灯片网格里的一个横排——每一排都是一个分区。分区名会显示在编辑器里（在那一排旁边）和演讲者视图里（让演讲者能在各组之间跳转）。它们是给编辑幻灯片的人用的组织工具——在哪里分开由用户决定，而不是你。

### 被要求整理一套幻灯片时

“整理这套幻灯片”意思不明确——可能是分组、调整顺序、去重或重新组织结构。在去用 `AskUserQuestion` 之前，先读一遍幻灯片。

**默认：提出方案，不要问。** 大多数幻灯片都有线索——首尾的标题页、编了号的使用场景、重复出现的 *Before / After*（之前 / 之后）组合、过渡页（“Then X enters the chat”，意思是“然后 X 登场了”）、一页 *Thank you*（谢谢）。有线索时，选一种分区方式，用一条确认消息提出来。方案里有边界的选择（一排 *Use Cases* 还是三排、过渡页放在哪里）是可以撤回的——选一个继续往下走。

**退路：没有线索时再问。** 如果幻灯片顺序随意、或者没有主线，就问哪些范围的页面放在一起、叫什么名字。不要用平均切成三份来代替阅读。

### 命名 + 范围

名字要短（1–3 个词）、具体（*Demo* 胜过 *Show & tell*），并在同一套幻灯片里保持一致。通常两到五个分区；只有很长或重复的幻灯片才更多。分区名不是幻灯片标题——它们帮人找到一组，而不是描述其内容。

### 给分区改名

`getSlideGrid()` 返回 `SlideNode[][]`——里面的数组是普通的 JS 幻灯片数组，**不是** `SLIDE_ROW` 节点。在这些数组上设置 `.name` 会悄悄地什么也不做。要给分区改名，遍历节点树，在真正的 `SLIDE_ROW` 上设置 `.name`：

```js
const slideGrid = figma.currentPage.children.find(c => c.type === "SLIDE_GRID");
slideGrid.children[0].name = "Intro";
```

## 演讲者备注

演讲者备注是演讲者给每页幻灯片准备的私人伴侣。它们显示在演讲者视图里（只有演讲者能看到，观众看不到），在现场演讲时用作讲稿、提示单或要点参考。

### 什么时候写演讲者备注

- **被要求时**：如果用户要求为一套幻灯片写演讲者备注、演讲提示、要点或讲稿，就为每一页有实质内容的幻灯片写备注（跳过分区分隔页或纯装饰的页面，除非有话要说）。
- **准备好直接演讲的幻灯片**：如果用户明确要求一套能直接现场演讲的幻灯片，演讲者备注就有用。当备注能帮演讲者理解幻灯片上看不出来的节奏、过渡或背景时，就加上。
- **内容少或以视觉为主的页面**：如果一页幻灯片围绕一张图表、图片、比喻或一个引人思考的问题，备注可以帮忙说明演讲者该说什么。当视觉上下文重要时，对图片多、图表多或视觉上内容少的页面用截图或 `node.screenshot()`，但不要默认给每页都截图——图片会消耗上下文预算。
- **没要求就不要加备注**：普通的幻灯片修改、布局工作或更新已有的幻灯片时，除非用户要求，不要填写演讲者备注。加备注会改变演讲的流程，可能让幻灯片的主人感到意外。

### 好的演讲者备注是什么样的

演讲者备注是给*演讲者*的，不是给观众的。它们应该像一位信得过的同事凑过来小声说“这里这么讲”。好的备注：

- **补充幻灯片，而不是重复它。** 如果幻灯片上写着“Revenue grew 40%”（收入增长了 40%），备注就不应该再写“Revenue grew 40%”。它应该说*为什么*增长、观众应该带走什么、或者这通常会引出什么问题。
- **简洁、一眼能扫到。** 演讲者说到一半往下看一眼，需要立刻找到自己讲到哪了。用简短的要点，不要用密密麻麻的段落。每个要点一个意思。
- **包含过渡。** 最好的备注会告诉演讲者怎样在页面之间*过渡*：“After the applause dies down...”（等掌声停下后……）或者“This builds on the previous point — call back to the 40% figure.”（这是接着上一点讲的——呼应一下 40% 那个数字。）
- **带上幻灯片带不了的背景。** 数据来源（“Source: Q4 FY25 internal metrics, not yet public”，意思是“来源：25 财年第四季度内部指标，尚未公开”）、注意事项（“Skip this slide if the CFO is in the room”，意思是“如果 CFO 在场就跳过这页”）、时间提示（“This is the halfway point — you should be at ~10 minutes”，意思是“这里是一半——你应该讲到第 10 分钟左右”），以及预计会被问到的问题（“They'll ask about margins — see appendix slide 14”，意思是“他们会问利润率——见附录第 14 页”）。
- **符合这场演讲的语气。** 投资人路演的备注要精确、排练过。团队复盘的备注随意、灵活。主题演讲的备注可能包含舞台提示。让语气和场合相配。

### 演讲者备注里要避免的

- **完整的讲稿**：一大段文字的备注会让人照着念，演讲效果会很糟。如果用户明确要讲稿，就写一份，但默认用要点。
- **为观众排版**：观众看不到备注。不要为了让非演讲者好读而优化它们。
- **和幻灯片重复**：如果幻灯片一看就懂（带联系方式的“Thank You”），就不需要备注。让一页的备注空着完全没问题。

### 格式

`slide.speakerNotes` 接收一个 markdown 字符串。优先用项目符号列表作为主要结构；加粗适合用来强调演讲者不该跳过的关键短语。支持的 markdown（列表、加粗、斜体、删除线）和不支持的（标题、代码块、行内代码、链接）完整列表见 [slide-properties.md](references/slide-properties.md#supported-formatting)。

## 检查 Slides 文件

目前还没有专门读取 Slides 文件的工具。用带只读脚本的 `use_figma` 来检查，用 `get_screenshot` / `await node.screenshot()` 获取视觉上下文。

- **创建之前先检查。** 创建任何东西之前，先运行一个只读的 `use_figma`，弄清已经有什么——幻灯片、文字、组件、命名习惯。[Figma插件基础](../Figma插件基础/SKILL.md) 第 6 节的“先检查”做法在这里也适用。
- **`get_metadata` 在 Slides 文件上不能用**——它只支持 `figma`（Design）编辑器类型。
- **`console.log()` 的输出不会返回**——只有 `return` 的值会传回来。一定要 `return` 你需要的数据。
- **用 `get_screenshot` 获取视觉上下文**——传一个有效的 `nodeId` 就能拿到截图。你也可以在 `use_figma` 脚本里内联使用 `await node.screenshot()`。

### 快速检查脚本

**列出这套幻灯片里的所有页面：**
```js
const grid = figma.getSlideGrid();
return grid.map((row, rowIdx) =>
  row.map((slide, colIdx) => ({
    id: slide.id,
    name: slide.name,
    row: rowIdx,
    col: colIdx,
    isSkipped: slide.isSkippedSlide,
    speakerNotes: slide.speakerNotes,
  }))
);
```

**获取某一页幻灯片里的文字内容：**
```js
const slide = figma.getNodeById("TARGET_SLIDE_ID");
// findAllWithCriteria uses an indexed type lookup — much faster than
// findAll(n => n.type === 'TEXT') on slides with many shapes/images.
const textNodes = slide.findAllWithCriteria({ types: ["TEXT"] });
const fontsToLoad = new Set();
for (const t of textNodes) {
  if (t.fontName !== figma.mixed) {
    fontsToLoad.add(JSON.stringify(t.fontName));
  } else {
    const segments = t.getStyledTextSegments(["fontName"]);
    for (const seg of segments) fontsToLoad.add(JSON.stringify(seg.fontName));
  }
}
for (const f of fontsToLoad) {
  await figma.loadFontAsync(JSON.parse(f));
}
return textNodes.map(t => ({
  id: t.id,
  name: t.name,
  characters: t.characters,
  x: t.x,
  y: t.y,
  width: t.width,
  height: t.height,
}));
```

（代码注释意思：findAllWithCriteria 用的是按类型建了索引的查找——在有很多形状/图片的幻灯片上，比 findAll(n => n.type === 'TEXT') 快得多。）

## 参考文档

只加载你的任务需要的参考文件：

- [slide-gotchas](references/slide-gotchas.md)——Slides 特有的坑（坐标偏移、不透明的节点类型、验证的变通办法）
- [slide-lifecycle](references/slide-lifecycle.md)——创建、复制、删除和重新排序幻灯片和幻灯片排
- [slide-grid](references/slide-grid.md)——使用幻灯片网格布局（`getSlideGrid`、`setSlideGrid`）
- [slide-content](references/slide-content.md)——在幻灯片里搭建内容（文字、形状、自动布局——SlideNode 扩展了 BaseFrameMixin）
- [slide-properties](references/slide-properties.md)——幻灯片专用的属性（`speakerNotes`、`isSkippedSlide`、`focusedSlide`、`focusedNode`、`slideThemeId`、`InteractiveSlideElementNode`）
- [slide-design](references/slide-design.md)——让幻灯片视觉上有趣、多变的设计原则（配色策略、字体、布局多样性、空间构图、反面模式）
