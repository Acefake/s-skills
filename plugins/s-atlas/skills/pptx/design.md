本技能译自 [appautomaton/document-SKILLs](https://github.com/appautomaton/document-SKILLs)（MIT）。该仓库说明写明，内容改编自 Anthropic 的 skills。许可证全文见 [LICENSE-document-skills](../../LICENSE-document-skills)。

# 设计一套幻灯片

写 HTML 之前先读这份。幻灯片是隔着房间、几秒内读完的。下面每个选择都为那个读者服务。不为他服务的选择就是装饰，去掉。

先定系统：调色、字号阶梯、网格。写任何 HTML 之前用两句话写下来，然后每一张都用它，没有例外。看起来像设计过，一致性占了大部分。

## 原则

**一张幻灯片一个点。** 标题写成一句话（「续约带动收入增长 18%」），不要写成话题（「收入」）。幻灯片上其余的东西都支撑这句话。一张需要两个标题，就做成两张。

**三层层级。** 用标题、正文和注释（来源、脚注、坐标轴标签）。用字号和字重分开它们，每张不要超过三种字号。大约 1.5 倍的台阶才读得出差别。

| 角色 | 16:9（720 × 405pt） |
|---|---|
| 结论 / 大数字 | 54–72pt |
| 标题 | 28–36pt |
| 正文 | 16–20pt |
| 注释 | 11–12pt |

正文不要低于 14pt。14pt 放不下，就删字。中文更宽，先删字，不要把字号压到 14pt 以下。

**网格。** 每一边的外边距用 36–48pt。内容区分成 12 列，每个左边缘都落在网格线上。标题在每张上的位置相同，内容变、框不动。图表或表格配文字时用大约 40/60 的两栏，文字在图旁边。不要把图表堆在一段文字下面，也不要为了不加一张而把版式塞满。

**颜色：一个强调色，少用。** 调色从接近白或接近黑的背景、一种文字色、注释用的次级灰、以及一个强调色搭起来。强调色只用在眼睛该落下的地方：关键数字、被标出的柱、当前步骤。到处都是强调色，就没有强调。

- 浅底上用接近黑的文字（`1A1A1A`、`222831`），不用纯 `000000`。它读起来像印刷，不像屏幕。
- 文字和背景的对比至少 4.5:1。灰字放在带色的面板上，通常就是在这里失败。
- 有品牌时，用它的主色当强调色，其余保持中性。
- 没有品牌时，选一个适合题材、又不落俗套的强调色。金融不必是海军蓝。

**克制。** 一个形状要靠承担结构才有位置：把相关项收成一块的面板、分开章节的线、标出当前项的条。除非品牌要求，否则不要投影、渐变、剪贴画图标和装饰性的角上形状。留白是结构的一部分，不要填满它。

**图表要说明那个点。** 每张图回答标题的那句判断。

- 提供上下文的序列用灰，重要的那条用强调色。
- 直接标数值或序列名，不要用图例。
- 柱状图从零开始。
- 删掉网格线，或把它们做得很淡。
- 粒度要能看出形状：一个月以内用天，两年以内用月，再长用年。一张图只有一个数据点，说明聚合错了。

**重复。** 反复出现的元素要完全一样：同一位置、尺寸、颜色和间距。只用少数几种版式（封面、章节分隔、一句话、文字加图、满版图表或表格），然后复用。

## 字体

html2pptx 在这台机器的浏览器里量文字，PowerPoint 在观众的机器上画它。任何一边缺了这个字体，就会换上宽度不同的替代字体，原来放得下的文字就会溢出。所以只用两边都确定有的字体：

**Arial、Georgia、Verdana、Trebuchet MS、Times New Roman、Courier New。**

全文用一个家族，靠字号和字重拉开差别，或者标题一个家族、正文一个家族。能用的搭配：

- 标题 Georgia、正文 Arial：偏编辑
- 全文 Arial，标题加粗：中性，最稳
- 全文 Trebuchet MS：更亲切
- Courier New 只用于代码或等宽数字

不要用 Impact 这种只有一个字重的展示字体。PowerPoint 会假造粗体，文字变宽。

中文、日文、韩文不能靠上面的拉丁字体，它们没有这些字形，两边都会退回各自的系统字体。必须显式写出观众机器上有的 CJK 字体，例如面向 Windows 观众的 Microsoft YaHei，或 Source Han Sans、SimSun、Noto Sans CJK SC。HTML 里写 `font-family: "Microsoft YaHei", "Noto Sans CJK SC", sans-serif`。幻灯片 XML 里在 `<a:latin>` 旁边加 `<a:ea typeface="Microsoft YaHei"/>`。每个文本框都留出余量，因为中文更宽，然后仔细看渲染出来的页面。

渲染检查用 LibreOffice。系统里要装 Noto CJK（Debian/Ubuntu 是 `fonts-noto-cjk`）。没装时，渲染图不能用来判断中文是否缺字或溢出。

## 一份起步样式

把上面的系统放进 CSS 变量，每张幻灯片只负责排布。按这里写，能通过 html2pptx 的校验。中文幻灯片把 `font-family` 换成上一节的 CJK 字体，不要沿用 Arial。

```html
<style>
:root {
  --bg: #FAFAF7; --text: #1A1A1A; --muted: #6B6B6B; --accent: #C0392B; --panel: #F0EDE6;
  --headline: 32pt; --body: 18pt; --note: 11pt; --margin: 40pt;
}
body {
  width: 720pt; height: 405pt; margin: 0; display: flex; flex-direction: column;
  background: var(--bg); color: var(--text); font-family: Arial, sans-serif;
}
h1 { font-size: var(--headline); margin: var(--margin) var(--margin) 16pt; }
p, ul, ol { font-size: var(--body); margin: 0 var(--margin) 10pt; line-height: 1.3; }
.note { font-size: var(--note); color: var(--muted); }
.accent { color: var(--accent); }
.columns { display: flex; gap: 24pt; margin: 0 var(--margin); }
.columns > .text { width: 40%; } .columns > .figure { width: 60%; }
.columns p, .columns ul { margin-left: 0; margin-right: 0; }
.panel { background: var(--panel); padding: 14pt; }
</style>
```
