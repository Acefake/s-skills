# html2pptx

`scripts/html2pptx.js` 在 Chromium 里渲染一张 HTML 幻灯片，读出每个东西落在哪，再用 PptxGenJS 把它重建成原生 PowerPoint 对象。文字保持可编辑，位置和浏览器一致。写幻灯片之前先读 `design.md`。

## 准备

- `<skill>/node_modules` 不存在时，在 `<skill>` 里执行一次 `npm install`。
- 幻灯片用这台机器上已经安装的 Google Chrome 渲染，不用下载。只有没有 Chrome 的机器（CI、容器）才在 `<skill>` 里执行一次 `npx playwright-core install chromium`。它会把大约 250 MB 的 Chromium 下载到 Playwright 的共享缓存，机器上已有 Chrome 时不要跑。
- 构建脚本从用户的工作目录运行：`NODE_PATH=<skill>/node_modules node build.js`，这样 `require('pptxgenjs')` 才能解析。

## 幻灯片 HTML

每张幻灯片是一份以 `<!DOCTYPE html>` 开头的完整 HTML。没有它，浏览器按怪异模式排版，html2pptx 会拒绝。body 就是幻灯片。它的尺寸必须和演示文稿版式一致：

| 版式 | body |
|---|---|
| `LAYOUT_16x9` | `width: 720pt; height: 405pt` |
| `LAYOUT_4x3` | `width: 720pt; height: 540pt` |
| `LAYOUT_16x10` | `width: 720pt; height: 450pt` |

body 设 `margin: 0`。在它上面设 `display: flex`，避免外边距折叠把溢出藏起来。

| HTML | 变成 |
|---|---|
| `<p>`、`<h1>`–`<h6>` | 一个文本框。里面的 `<b>`/`<strong>`、`<i>`/`<em>`、`<u>`、`<s>`、`<sup>`、`<sub>` 和 `<span>` 保留字重、样式、颜色、大小、字体和字距，`<br>` 在段落内换行。 |
| `<ul>`、`<ol>`，可以任意嵌套 | 一个由项目符号或编号段落组成的文本框。`<ol>` 遵守 `start` 和 `list-style-type`（decimal、lower/upper-alpha、lower/upper-roman）。 |
| 有背景或边框的 `<div>` | 一个形状。`border-radius` 给出圆角，`box-shadow` 给出外阴影，单边边框变成一条线。 |
| `<img>` | 一张图。路径相对 HTML 文件，`data:` URL 可以用。 |
| `class="placeholder"` | 什么都不画。它的位置返回给图表或表格。给它一个 `id`。 |

`<p>`、`<h1>`–`<h6>`、`<ul>` 和 `<ol>` 之外的文字到不了 PowerPoint。CSS 渐变和 SVG 也不会转换：先光栅化成 PNG（见下）。字体遵守 `design.md`。中文必须显式写 CJK 字体，并留出余量。

### html2pptx 会拒绝什么

它收集一张幻灯片上的每个问题，带上文件名一起抛出。全部修好再跑。

- 内容溢出 body，或 body 尺寸和版式不一致。
- 大于 12pt 的文字，结束位置距离底边不到 0.5 英寸。
- `<div>` 里有裸文字：用 `<p>` 包起来。
- 文字元素上有背景、边框或阴影：放到包着它的 `<div>` 上。
- `<div>` 上的 `background-image`：改用 `<img>`。
- CSS 渐变。
- 行内元素（`<span>`、`<b>` 等）上的外边距，PowerPoint 的 run 放不下。
- 段落以手打的项目符号字符开头：用 `<ul>`/`<ol>`。
- 宽度或高度为零的占位。

## 构建文稿

带 async `main` 的 CommonJS 脚本：

```javascript
const pptxgen = require('pptxgenjs');
const html2pptx = require('<skill>/scripts/html2pptx.js');

async function main() {
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';
  pptx.title = 'Quarterly review';

  await html2pptx('slides/01-title.html', pptx);

  const { slide, placeholders } = await html2pptx('slides/02-growth.html', pptx);
  const area = placeholders.find((p) => p.id === 'chart');
  slide.addChart(pptx.charts.BAR, [
    { name: 'Revenue', labels: ['Q1', 'Q2', 'Q3', 'Q4'], values: [4.5, 5.5, 6.2, 7.1] }
  ], { ...area, chartColors: ['C0392B'], showLegend: false, showValue: true });
  slide.addNotes('Growth came from renewals; new logos were flat.');

  await pptx.writeFile({ fileName: 'deck.pptx' });
}

main().catch((e) => { console.error(e.message); process.exit(1); });
```

`html2pptx(htmlFile, pptx, options)` 返回 `{ slide, placeholders }`，每个占位是以英寸为单位的 `{ id, x, y, w, h }`。选项：

- `slide`：画到一张已有的幻灯片上。
- `screenshotPlaceholders: true`：同时把每个占位作为 PNG 放进 `placeholder.image`。
- `renderDelay: ms`：读页面之前等待。

一个浏览器服务每一次调用，空闲一秒后关闭。`html2pptx.close()` 立刻关掉它。

PptxGenJS 自己会写出一些 PowerPoint 能容忍、但架构拒绝的 XML：重复的段落属性、顺序不对的 presentation 部分，以及折线、面积、散点和雷达图的图表 XML。html2pptx 见过一份演示文稿之后，会在写文件时把这些都修好，包括你直接用 PptxGenJS 加进去的部分。

## PptxGenJS：你会用到的部分

**颜色**是不带 `#` 的十六进制：`'C0392B'`。带 `#` 会弄坏文件。

**图表。** `BAR`（横向用 `barDir: 'bar'`，堆叠用 `barGrouping: 'stacked'`）、`BAR3D`、`LINE`、`AREA`、`PIE`、`DOUGHNUT`、`SCATTER` 和 `RADAR` 都能产出合法文件。有用的选项：

- `chartColors: ['C0392B', 'B0B0B0']`
- `showValue`、`dataLabelPosition: 'outEnd'`
- `showLegend`、`legendPos: 'r'`
- `showTitle`、`title`
- `showCatAxisTitle`、`catAxisTitle`、`showValAxisTitle`、`valAxisTitle`
- `valAxisMinVal`、`valAxisMaxVal`、`valAxisMajorUnit`
- `catAxisLabelRotate`
- `lineSize`、`lineDataSymbol`
- `showPercent`（饼图）

数据是序列：`[{ name, labels, values }]`。饼图和圆环图只要一个序列。散点是例外：第一个序列放 X 值，后面每个序列只放 Y 值。

```javascript
slide.addChart(pptx.charts.SCATTER, [
  { name: 'X', values: [1, 2, 3, 4] },
  { name: 'Conversion', values: [2.1, 2.9, 3.2, 4.0] }
], { ...area, lineSize: 0, lineDataSymbol: 'circle', chartColors: ['C0392B'] });
```

**表格。** 行是字符串或 `{ text, options }` 单元格：

```javascript
slide.addTable([
  [{ text: 'Product', options: { bold: true, color: 'FFFFFF', fill: { color: '1F3A5F' } } },
   { text: 'Revenue', options: { bold: true, color: 'FFFFFF', fill: { color: '1F3A5F' } } }],
  ['Core', '$50M'],
  ['Add-ons', '$35M']
], { ...area, colW: [3, 2], fontSize: 14, border: { pt: 1, color: 'DDDDDD' } });
```

`colspan` 和 `rowspan` 放在单元格的 options 里。`autoPage: true` 把长表续到新幻灯片上。中文表格把字体设成 CJK 字体，列宽留余量。

**直接加的图片**要自己保持宽高比。用 `await sharp('photo.jpg').metadata()` 读像素尺寸，从 `w` 推出 `h`。

**演讲者备注：** `slide.addNotes('text')`。

## 把图标和渐变做成 PNG

用 Sharp 光栅化，然后在 HTML 里引用 PNG：`<img src="icon.png" style="width: 36pt; height: 36pt">`，或在 `<body>` 上用 `background-image: url('bg.png')`。

图标是任意 SVG：用户提供的，或你画的简单图形。里面用 `currentColor`，光栅化时再设颜色。

```javascript
const sharp = require('sharp');

const chartLine = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
  stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 5-6"/></svg>`;

async function iconPng(svg, color, file, size = 256) {
  const colored = svg.replaceAll('currentColor', `#${color}`);
  await sharp(Buffer.from(colored), { density: 300 }).resize(size, size).png().toFile(file);
}

async function gradientPng(from, to, file, width = 1920, height = 1080) {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}">
    <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#${from}"/><stop offset="1" stop-color="#${to}"/>
    </linearGradient></defs>
    <rect width="100%" height="100%" fill="url(#g)"/></svg>`;
  await sharp(Buffer.from(svg)).png().toFile(file);
}

async function main() {
  await iconPng(chartLine, '1F3A5F', 'icon.png');
  await gradientPng('1F3A5F', '0B1A2B', 'bg.png');
}

main().catch((e) => { console.error(e); process.exit(1); });
```

## 浏览器画出来的内容

占位里是 Chart.js、D3 或内联 SVG 画的图时，让 html2pptx 在渲染幻灯片时把它截下来：

```javascript
const { slide, placeholders } = await html2pptx('slide.html', pptx, {
  screenshotPlaceholders: true,
  renderDelay: 500  // let the script finish drawing; or turn its animation off
});
for (const p of placeholders) slide.addImage({ data: p.image, x: p.x, y: p.y, w: p.w, h: p.h });
```

有对应的原生类型时，优先用 PptxGenJS 的原生图表。原生图表保持可编辑，数据也留在文件里。
