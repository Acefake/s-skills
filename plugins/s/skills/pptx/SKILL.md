---
name: pptx
description: "创建、修改和阅读 PowerPoint（.pptx）：用 HTML 做新幻灯片、套模板、复制或重排、改幻灯片 XML、读写备注。中文要显式指定 CJK 字体，并留出余量，因为中文更宽。Use when a task produces or modifies a .pptx, or needs its text, layout, or notes read."
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。

本技能译自 [appautomaton/document-SKILLs](https://github.com/appautomaton/document-SKILLs)（MIT）。该仓库说明写明，内容改编自 Anthropic 的 skills。许可证全文见 [LICENSE-document-skills](../../LICENSE-document-skills)。

# PowerPoint

python-pptx 和 PptxGenJS 你已经会用。这个技能补上一个转换器，把 HTML 幻灯片变成可编辑的原生 PowerPoint 对象，一组让套模板可靠的脚本，以及检查文稿是否合法、看起来是否正确的步骤。

## 运行脚本

`<skill>` 是包含本文件的目录。用绝对路径从用户的工作目录运行自带脚本，这样指向用户文件的相对路径仍然有效：

```bash
uv run <skill>/scripts/thumbnail.py deck.pptx
```

自己写的 Python 要声明依赖，用 `uv run --with python-pptx script.py`，或写 PEP 723 头。Node 脚本用 `NODE_PATH=<skill>/node_modules node build.js`。`<skill>/node_modules` 不存在时，在 `<skill>` 里执行一次 `npm install`。渲染需要 LibreOffice（`soffice`）和 poppler（`pdftoppm`）。

## 选哪条流程

| 任务 | 流程 |
|---|---|
| 读文稿文字 | `uv run --with 'markitdown[pptx]' python -m markitdown deck.pptx` |
| 没有模板的新文稿 | 下面的 html2pptx。先读 `html2pptx.md` 和 `design.md`。 |
| 从模板做新文稿 | 下面的模板流程 |
| 改已有文稿 | 文字和形状用 python-pptx。python-pptx 到不了的地方用幻灯片 XML（`ooxml.md`）。 |
| 演讲者备注 | `scripts/notes.py` |

markitdown 从 1 给幻灯片编号（`<!-- Slide number: 1 -->`）。这里的每个脚本都从 0 数。要沿用已有文稿的外观，从解包文件的 `ppt/theme/theme1.xml` 读 `<a:clrScheme>`、`<a:fontScheme>`，并看缩略图网格。

## 中文和 CJK 字体

幻灯片上有汉字时，必须显式指定 CJK 字体。拉丁字体没有汉字，两边都会退回各自的系统字体，宽度一对不上，浏览器里刚好的文字到 PowerPoint 里就溢出。

- HTML 写 `font-family: "Microsoft YaHei", "Noto Sans CJK SC", sans-serif` 这一类本机和观众机器都有的字体。不要只写 Arial。
- 幻灯片 XML 里，`<a:latin>` 旁边写 `<a:ea typeface="Microsoft YaHei"/>`。可用的名字还有 Source Han Sans、SimSun、Noto Sans CJK SC。
- 中文比同样意思的英文宽。文本框留出余量，少写几个字，或把框加宽、字号降一档。不要卡到刚好放下。
- 渲染检查前安装 Noto CJK（Debian/Ubuntu 是 `fonts-noto-cjk`）。没装时 LibreOffice 会换字体，溢出和缺字都看不准。

细节在 [design.md](design.md) 的字体一节。

## 新文稿：html2pptx

1. 先定设计系统（`design.md`）：调色、字号阶梯、网格。写代码前用两句话写下来。
2. 每张幻灯片一个 HTML 文件，遵守 `html2pptx.md`。图表和表格的区域用 `class="placeholder"` 标出。
3. 写构建脚本：每张幻灯片调用 `html2pptx()`，在占位处用 PptxGenJS 加图表和表格，再调用 `pptx.writeFile({ fileName })`。html2pptx 会一次抛出一张幻灯片上的全部问题。都修好再重跑。
4. 按下面检查输出。

## 从模板做新文稿

1. **看模板。** 用 markitdown 抽出文字，并用 `uv run <skill>/scripts/thumbnail.py template.pptx grid` 做缩略图网格。看这些图。
2. **清点版式。** 按从 0 开始的下标列出每一张和它的用途，例如「12：两栏，每栏标题加要点」。
3. **把内容对上版式。** 先数每张幻灯片有几块内容，再选槽位数量正好的版式：
   - 两块用两栏，三块用三栏
   - 只有真有图时才用图片版式
   - 只有真的引语、并且带来源时才用引语版式
   - 四块或更多就拆到多张，或收成一张列表

   不要留空占位，也不要编填充文字去占一个槽。
4. **组装幻灯片。** 复制出来的是完整的一张，带图表、嵌入的工作簿、备注和链接：
   ```bash
   uv run <skill>/scripts/rearrange.py template.pptx working.pptx 0,12,12,31,40
   ```
5. **清点文字。** 读完整份 `inventory.json`：
   ```bash
   uv run <skill>/scripts/inventory.py working.pptx inventory.json
   ```
6. **写替换文件**（格式见下），然后应用：
   ```bash
   uv run <skill>/scripts/replace.py working.pptx replacements.json output.pptx
   ```
7. 按下面检查输出。

### 清单和替换

`inventory.json` 把 `slide-N` 映射到 `shape-N`，都从 0 开始。形状先按上到下、再按左到右排序，不写幻灯片号。每个形状有以英寸为单位的 `left`、`top`、`width`、`height`，以及 `paragraphs`。它还会带上：

- `placeholder_type`（`TITLE`、`CENTER_TITLE`、`SUBTITLE`、`BODY`、`OBJECT` 等），只在占位符上有
- `default_font_size`，版式设了字号时
- `overflow`、`overlap`、`warnings`，检测到时

段落只列出和默认值不同的属性。

替换文件形状相同，每个要填的形状带 `paragraphs`：

```json
{
  "slide-0": {
    "shape-0": {"paragraphs": [{"text": "Revenue grew 18%", "bold": true}]},
    "shape-1": {"paragraphs": [
      {"text": "Renewals drove two thirds of growth"},
      {"text": "Churn fell to 4%", "bullet": true, "level": 0}
    ]}
  }
}
```

- 段落字段：
  - `text`、`bold`、`italic`、`underline`
  - `font_size`、`font_name`
  - `color`（`"C0392B"`）或 `theme_color`（`"ACCENT_1"`）
  - `alignment`（`LEFT`、`CENTER`、`RIGHT`、`JUSTIFY`）
  - `space_before`、`space_after`、`line_spacing`（磅）
  - 带 `level` 的 `bullet`
- 清单里这个槽已有的属性要带上，模板的样式才保得住。中文的 `font_name` 写成上面的 CJK 字体，不要留成 Calibri。
- 不要自己打项目符号字符。带项目符号的段落会自动左对齐。
- **列出的每一张幻灯片上，每个文本形状都会先清空再填。** 文件里没写到的形状会变成空的，模板残留文字就这样去掉。没列出的幻灯片不动。
- 键不存在时 replace.py 什么都不保存（「Shape 'shape-9' not found on 'slide-0'. Available shapes: …」）。新文字比旧文字更溢出时也不保存（「Text overflow worsened: slide-0/shape-2: …」）。缩短文字，或换一个更宽的版式。中文更容易触发这条。

## 编辑幻灯片 XML

先读 `ooxml.md`。然后解包，每次修改后校验，再打包：

```bash
uv run <skill>/ooxml/scripts/unpack.py deck.pptx unpacked
uv run <skill>/ooxml/scripts/validate.py unpacked --original deck.pptx
uv run <skill>/ooxml/scripts/pack.py unpacked edited.pptx
```

## 演讲者备注

```bash
uv run <skill>/scripts/notes.py deck.pptx                    # print {"slide-0": "…", …}
uv run <skill>/scripts/notes.py deck.pptx notes.json -o out.pptx
```

JSON 把幻灯片键映射到纯文本，一行一段。空字符串清掉该张的备注，没列出的幻灯片保持原样。html2pptx 构建里改用 `slide.addNotes('…')`。

## 检查输出

文稿要校验通过，并且每一张都被看过，才算做完。

1. **校验。** 新文稿运行 `uv run <skill>/ooxml/scripts/validate.py deck.pptx`。改过的文稿或从模板做的，加上 `--original template.pptx`，这样只报告新问题。它列出的都要修。

   复制出来的幻灯片上，validate.py 也会报告模板里已经有的架构错误。追这些之前，先和源幻灯片比一下。
2. **看。** 运行 `uv run <skill>/ooxml/scripts/render.py deck.pptx pages`，读每一张图。看这些：
   - 文字被裁切、重叠，或挤到边上
   - 对比太弱
   - 残留的模板文字，或空的占位
   - 不在网格上的东西
   - 中文缺字，或因为比英文宽而溢出

   `thumbnail.py deck.pptx grid --outline-placeholders` 给出总览，每个文本框都有轮廓。
3. 修，然后重复，直到两步都干净。没有 Noto CJK 时，不要用渲染图判断中文。

## 会静默失败的坑

- PptxGenJS 的颜色不要带 `#`。`'#C0392B'` 会弄坏文件。
- 浏览器里放得下的文字，字体被替换后会在 PowerPoint 里溢出。遵守 `design.md` 里的字体规定。
- 用手复制一张幻灯片的 XML 会丢掉图表，并让多张幻灯片共用备注。用 `rearrange.py`。
- 除了 markitdown 的输出，幻灯片下标到处都从 0 开始。

## 在不同软件里怎么用

步骤在 Cursor、OpenCode、Codex、Claude Code、WorkBuddy 里相同。脚本在本机终端跑。某个软件没有终端时，说明缺了哪一步，不要改流程去迁就它。

依赖：Python 3.12（推荐 `uv`）、Node.js、LibreOffice、poppler。本机没有 Chrome 时，html2pptx 还要按 [html2pptx.md](html2pptx.md) 装一次 Chromium。看中文渲染还要 Noto CJK。
