# 用 docx-js 创建 Word 文档

docx-js（npm 包 `docx`，v9）用 JavaScript 对象构建 `.docx`。这份文件写的是它的 API 里，靠猜会产出坏掉或出乎意料结果的部分。

## 运行脚本

写成 CommonJS（`require`），把 `await` 放进 async 函数里。Node 直接跑的 `.js` 不是模块，拒绝顶层 `await`。让 Node 找到这个技能的包，并从用户的工作目录运行，输出才落在那里：

```bash
NODE_PATH=<skill>/node_modules node build.js
```

`<skill>/node_modules` 不存在时，在 `<skill>` 里执行一次 `npm install`。

## 一份完整文档

下面每个写法都出现在这个例子里。它能干净地通过校验，渲染结果也符合预期。从它开始，删掉你不需要的部分。正文含中文时，不要照抄里面的 `font: "Arial"`，按后面的东亚字体一节改。

```javascript
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, LevelFormat,
  Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType, VerticalAlign,
  ImageRun, ExternalHyperlink, InternalHyperlink, Bookmark, TableOfContents,
  Header, Footer, PageNumber, PageBreak, FootnoteReferenceRun,
} = require("docx");

const LETTER = { width: 12240, height: 15840 };     // 8.5 x 11 in, in DXA
const MARGIN = 1440;                                 // 1 in
const CONTENT = LETTER.width - 2 * MARGIN;           // 9360 DXA of usable width

const border = { style: BorderStyle.SINGLE, size: 4, color: "BFBFBF" };
const cell = (text, width, opts = {}) => new TableCell({
  width: { size: width, type: WidthType.DXA },
  borders: { top: border, bottom: border, left: border, right: border },
  shading: opts.fill ? { fill: opts.fill, type: ShadingType.CLEAR, color: "auto" } : undefined,
  verticalAlign: VerticalAlign.CENTER,
  children: [new Paragraph({ children: [new TextRun({ text, bold: opts.bold })] })],
});

async function main() {
  const doc = new Document({
    features: { updateFields: true },  // Word refreshes the TOC and page fields on open
    styles: {
      default: {
        document: { run: { font: "Arial", size: 22 } },  // 11 pt body
        title: { run: { font: "Arial", size: 48, bold: true } },
        heading1: { run: { font: "Arial", size: 32, bold: true }, paragraph: { spacing: { before: 360, after: 120 } } },
        heading2: { run: { font: "Arial", size: 26, bold: true }, paragraph: { spacing: { before: 240, after: 80 } } },
      },
      paragraphStyles: [
        { id: "Note", name: "Note", basedOn: "Normal", run: { italics: true, color: "595959" } },
      ],
    },
    numbering: {
      config: [
        { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
        { reference: "steps", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      ],
    },
    footnotes: {
      1: { children: [new Paragraph("Source: internal finance report, Q3 2026.")] },
    },
    sections: [{
      properties: { page: { size: LETTER, margin: { top: MARGIN, right: MARGIN, bottom: MARGIN, left: MARGIN } } },
      headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun("Quarterly review")] })] }) },
      footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
        children: [new TextRun({ children: ["Page ", PageNumber.CURRENT, " of ", PageNumber.TOTAL_PAGES] })] })] }) },
      children: [
        new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun("Quarterly Review")] }),
        new TableOfContents("Contents", { hyperlink: true, headingStyleRange: "1-2" }),
        new Paragraph({ children: [new PageBreak()] }),
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new Bookmark({ id: "results", children: [new TextRun("Results")] })] }),
        new Paragraph({ children: [
          new TextRun("Revenue grew 18%"), new FootnoteReferenceRun(1), new TextRun(". See "),
          new ExternalHyperlink({ link: "https://example.com", children: [new TextRun({ text: "the dashboard", style: "Hyperlink" })] }),
          new TextRun("."),
        ] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun("Enterprise up 24%")] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun("Consumer flat")] }),
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("By region")] }),
        new Table({
          width: { size: CONTENT, type: WidthType.DXA },
          columnWidths: [CONTENT / 2, CONTENT / 2],
          rows: [
            new TableRow({ tableHeader: true, children: [cell("Region", CONTENT / 2, { bold: true, fill: "D9E2F3" }), cell("Growth", CONTENT / 2, { bold: true, fill: "D9E2F3" })] }),
            new TableRow({ children: [cell("EMEA", CONTENT / 2), cell("12%", CONTENT / 2)] }),
          ],
        }),
        new Paragraph({ alignment: AlignmentType.CENTER, children: [
          new ImageRun({ type: "png", data: fs.readFileSync("chart.png"), transformation: { width: 400, height: 200 },
            altText: { name: "chart", description: "Revenue by quarter" } }),
        ] }),
        new Paragraph({ children: [
          new ImageRun({ type: "svg", data: fs.readFileSync("logo.svg"), transformation: { width: 100, height: 50 },
            fallback: { type: "png", data: fs.readFileSync("chart.png") } }),
        ] }),
        new Paragraph({ numbering: { reference: "steps", level: 0 }, children: [new TextRun("Review the figures")] }),
        new Paragraph({ numbering: { reference: "steps", level: 0 }, children: [new TextRun("Approve the budget")] }),
        new Paragraph({ style: "Note", children: [
          new TextRun("Back to "), new InternalHyperlink({ anchor: "results", children: [new TextRun({ text: "Results", style: "Hyperlink" })] }),
        ] }),
      ],
    }],
  });
  fs.writeFileSync("report.docx", await Packer.toBuffer(doc));
}

main();
```

## 页面尺寸

docx-js 默认是 **A4**（11906 × 16838 DXA）。美国文档要像上面那样显式设成 Letter。每个宽度都取决于这个选择，1440 DXA = 1 英寸：

| 页面，1 英寸边距 | `size` | 可用宽度 | 两列 | 三列 |
|---|---|---|---|---|
| Letter | `{ width: 12240, height: 15840 }` | 9360 | `[4680, 4680]` | `[3120, 3120, 3120]` |
| A4 | `{ width: 11906, height: 16838 }` | 9026 | `[4513, 4513]` | `[3009, 3009, 3008]` |

横向时，在 `size` 上加 `orientation: PageOrientation.LANDSCAPE`，数字仍用纵向的。docx-js 会自己对调。`TabStopPosition.MAX` 是 9026，也就是 A4 的右边界。Letter 上右对齐制表要用 9360。

## 样式

- 通过 `styles.default` 改内置样式：`document`、`title`、`heading1` … `heading6`、`listParagraph`、`hyperlink`。用 id `Heading1` 再定义一条 `paragraphStyles`，会在内置样式旁边写出第二个 Heading1，Word 用哪一个是不确定的。
- 自己的样式用 `paragraphStyles` 和 `characterStyles`，用你自己的 id，然后用 `style: "Note"` 应用。
- 标题必须用 `heading: HeadingLevel.HEADING_n`，不要再加自定义 `style`，否则目录找不到它们。
- 尺寸单位是半磅：`size: 22` 是 11 pt。

## 中文：设置 eastAsia

有汉字时，默认样式和每个 `TextRun` 都写成字体对象，带上 `eastAsia`。只写字符串 `"Arial"` 不会设置 `w:eastAsia`。优先 Microsoft YaHei、Source Han Sans 或 SimSun。本机没有，就用已安装的 Noto Sans CJK SC。

```javascript
const cjk = { ascii: "Arial", hAnsi: "Arial", eastAsia: "Microsoft YaHei" };
// styles.default.document.run = { font: cjk, size: 22 }
// new TextRun({ text: "季度回顾", font: cjk, size: 22 })
```

这会写成：

```xml
<w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="Microsoft YaHei"/>
```

渲染检查用 LibreOffice，并且要装好 Noto CJK（`fonts-noto-cjk`）。没装时，图上的方框不能说明文件里没设字体。

## 文字

- 一行一个 `Paragraph`。`TextRun` 里的 `\n` 不会换行。
- run 选项：`bold`、`italics`、`underline: { type: UnderlineType.SINGLE }`、`strike`、`superScript`、`subScript`、`smallCaps`、`color: "C00000"`、`font`、`size`。
- `highlight: "yellow"` 还会写一个通不过架构校验的 `w:highlightCs`。旁边传 `highlightComplexScript: false`。
- 符号直接写成 `TextRun` 里的普通字符（"✓ ✗ © ™"）。`SymbolRun` 的码比如 `F0FC` 只在 Wingdings 字体里表示勾。

## 列表

用带 `LevelFormat.BULLET` 或 `LevelFormat.DECIMAL` 的编号配置，不要自己打一个 "•"。那看起来像列表，行为不是列表。共用一个 `reference` 的段落延续同一序列，换一个 reference 就从 1 重新开始。所以每个各自编号的列表用自己的 reference。

## 表格

- 在表上设 `columnWidths`，每个单元格设相同的 `width`（类型 `WidthType.DXA`）。宽度加起来等于你所选页面尺寸的可用宽度。
- 单元格底纹用 `type: ShadingType.CLEAR`。`ShadingType.SOLID` 在 Word 里把单元格涂成黑的。
- 边框放在单元格上，不放在表上。每个单元格至少要有一个 `Paragraph`。

## 链接、书签、目录

- **书签：** 用段落里的 `new Bookmark({ id, children })` 建立目标，用 `new InternalHyperlink({ anchor: id, … })` 指向它。`Paragraph` 上的 `bookmark:` 选项会被静默忽略。
- **目录：** `TableOfContents` 插入一个域，Word 更新域时才填上。`features: { updateFields: true }` 让 Word 在打开时提议更新，并提示文档「包含可能引用其他文件的域」。并没有别的文件，告诉用户接受是安全的。没有目录的文档不要加这个设置。LibreOffice 和 `render.py` 会把目录显示成空的，这是预期。

## 图片

- `type` 必填（`png`、`jpg`、`gif`、`bmp`、`svg`）。
- `transformation` 的单位是像素。保持源图的宽高比，宽度不要超出页面。
- `svg` 还需要一个光栅 `fallback: { type: "png", data }`，否则 docx-js 抛出 "Cannot read properties of undefined (reading 'type')"。
- `altText` 可选。给了它就要带 `name`，否则绘图通不过架构校验。

## 脚注

在 `Document` 的 `footnotes` 里按编号定义，用 `new FootnoteReferenceRun(n)` 引用。没有可以导入的 `Footnote` 类。

## 分页和节

- **分页：** `new PageBreak()` 只在段落的 children 里有效。标题要从新页开始时，在段落上用 `pageBreakBefore: true`。
- **节：** `sections` 里的每一项从新页开始，有自己的尺寸、方向、边距、页眉和页脚。
- **页眉和页脚：** 它们接受段落。页码放在 run 的 children 里，`PageNumber.CURRENT` 和 `PageNumber.TOTAL_PAGES`，像例子那样和普通字符串混在一起。
