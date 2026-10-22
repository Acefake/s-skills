# HTML 报告格式

架构审查渲染成系统临时目录里的一个自包含 HTML 文件。Tailwind 和 Mermaid 都从 CDN 加载。Mermaid 负责图状关系，画得稳；手写 div 和内联 SVG 负责更有编辑感的图（体量图、剖面图）。两者混用：全靠 Mermaid 会显得千篇一律。

报告用中文写。架构名词第一次出现时可以在括号里带英文（如「接缝（seam）」），之后只用中文。

## 骨架

```html
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <title>{{仓库名}} 架构审查</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script type="module">
      import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
      mermaid.initialize({ startOnLoad: true, theme: "neutral", securityLevel: "loose" });
    </script>
    <style>
      /* Tailwind 不好表达的小层：虚线接缝、手绘感箭头等 */
      body { font-family: ui-sans-serif, system-ui, "PingFang SC", "Noto Sans SC", "Microsoft YaHei", sans-serif; }
      .seam { stroke-dasharray: 4 4; }
      .leak { stroke: #dc2626; }
      .deep { background: linear-gradient(135deg, #0f172a, #1e293b); }
    </style>
  </head>
  <body class="bg-stone-50 text-slate-900">
    <main class="max-w-5xl mx-auto px-6 py-12 space-y-12">
      <header>...</header>
      <section id="candidates" class="space-y-10">...</section>
      <section id="top-recommendation">...</section>
    </main>
  </body>
</html>
```

## 页头

仓库名、日期，以及一个紧凑的图例：实线框 = 模块，虚线 = 接缝，红箭头 = 泄漏，粗深色框 = 深模块。不写引言，直接进候选。

## 候选卡片

图是主角。文字少、直白，直接用 [VOCABULARY.md](VOCABULARY.md) 的词，不客套。

每个候选是一个 `<article>`：

- **标题**：短，点出要加深什么（例如「合并订单受理流水线」）。
- **徽章行**：推荐强度（`强烈推荐` = 翠绿，`值得一看` = 琥珀，`推测` = 石板灰），再加一个依赖类别标签（`进程内`、`可本地替代`、`端口与适配器`、`mock`）。
- **文件**：等宽列表，`font-mono text-sm`。
- **前 / 后对比图**：重点。两栏左右并排。画法见下文。
- **问题**：一句话。哪里疼。
- **方案**：一句话。改什么。
- **收益**：要点，每条不超过 12 个字。例如「测试只打一个接口」「定价逻辑不再泄漏」「删掉 4 个浅包装」。
- **ADR 提示**（有冲突时）：琥珀底色框里一行。

不写解释段落。图要一段话才能看懂，就重画图。

## 图的画法

按候选挑合适的画法，混着用。不要每张图都一个样，多样本身就是目的。

### Mermaid 图（依赖、调用流的主力）

要表达「X 调 Y 调 Z，看看这一团乱」时，用 Mermaid 的 `flowchart` 或 `graph`。外面包一层 Tailwind 卡片，别显得是硬塞进来的。用 classDef 把泄漏边标红、深模块标深色。时序图适合「之前：6 次往返；之后：1 次」。

```html
<div class="rounded-lg border border-slate-200 bg-white p-4">
  <pre class="mermaid">
    flowchart LR
      A[OrderHandler] --> B[OrderValidator]
      B --> C[OrderRepo]
      C -.泄漏.-> D[PricingClient]
      classDef leak stroke:#dc2626,stroke-width:2px;
      class C,D leak
  </pre>
</div>
```

### 手写框和箭头（Mermaid 布局不听话时）

模块用带边框和标签的 `<div>`，箭头用绝对定位在相对容器上的内联 SVG `<line>` 或 `<path>`。想让「之后」的图看起来是一个粗边框的深模块、内部灰掉时用这个，Mermaid 画不出那种分量。

### 剖面图（适合层层都浅）

叠几条横向色带（`h-12 border-l-4`）表示一次调用穿过的层。之前：6 条薄层，每层什么都不做。之后：1 条厚带，标上合并后的职责。

### 体量图（适合「接口和实现一样宽」）

每个模块两个矩形：一个代表接口面积，一个代表实现。之前：接口矩形几乎和实现一样高（浅）。之后：接口矩形矮，实现矩形高（深）。

### 调用图折叠

之前：函数调用树画成嵌套的框。之后：同一棵树折叠进一个框，已经变成内部的调用在框里淡显。

## 样式要求

- 偏杂志排版，不要企业仪表盘风。留白充足。标题可以用衬线（`font-serif` 配 stone/slate 好看）。
- 颜色克制：一个强调色（翠绿或靛蓝），红色表示泄漏，琥珀表示警告。
- 图高约 320px，前后对比能并排放下不用滚动。
- 图里的模块标签用 `text-xs uppercase tracking-wider`，读起来像示意图而不是界面。
- 脚本只有 Tailwind CDN 和 Mermaid 的 ESM 引入。报告其他部分是静态的：没有应用代码，除了 Mermaid 自身渲染没有交互。

## 首选建议

一张大一点的卡片。候选名、一句话说为什么、一个锚点链接跳到它的卡片。就这些。

## 语气

直白、简洁，但架构名词和动词直接取自 [VOCABULARY.md](VOCABULARY.md)。简洁不是漂移的借口。

**只用这些词：** 模块、接口、实现、深度、深、浅、接缝、适配器、杠杆、局部性。

**不要替换成：** 组件、服务、单元（指模块时）· API、签名（指接口时）· 边界（指接缝时）· 层、包装（指模块时）。

**合适的说法：**

- 「订单受理模块是浅的：接口几乎等于实现。」
- 「定价逻辑跨接缝泄漏。」
- 「加深：一个接口，一处测试。」
- 「两个适配器撑得起这个接缝：生产用 HTTP，测试用内存。」

**收益要点**用词表里的词讲好处：_「局部性：bug 集中在一个模块」_、_「杠杆：一个接口，N 个调用点」_、_「接口变小，实现吸收掉包装层」_。不要写「更好维护」「代码更干净」，这些词不在词表里，没资格占位置。

不打太极，不清嗓子，不写「值得注意的是……」。能写成要点就写成要点，能删的要点就删。词表里没有的词，先找一个有的，再考虑造新词。
