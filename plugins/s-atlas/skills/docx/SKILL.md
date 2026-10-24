---
name: docx
description: "创建、修改、审阅和阅读 Word 文档（.docx），包括修订、批注、脚注、表格、图片和页面设置。给人读的正文先问上下文、按节写，再换一个没有上下文的读者挑没说清的地方。中文必须设置 w:eastAsia。Use when a task produces or modifies a .docx, reviews or redlines one, or needs its text, comments, or tracked changes read."
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。

本技能译自 [appautomaton/document-SKILLs](https://github.com/appautomaton/document-SKILLs)（MIT）。该仓库说明写明，内容改编自 Anthropic 的 skills。许可证全文见 [LICENSE-document-skills](../../LICENSE-document-skills)。

# Word 文档

Word 的功能你已经会用。这个技能补上代码里看不到的部分：一套能正确做修订和批注的库、能抓住未跟踪修改的校验、按读者看到的样子查看页面的办法，以及 docx-js 和 OOXML 里会静默生成坏文件的行为。

技术 Markdown、README、RFC 用 `technical-writing`。这里只处理 `.docx`。

## 运行脚本

`<skill>` 是包含本文件的目录。用绝对路径从用户的工作目录运行自带脚本，这样指向用户文件的相对路径仍然有效：

```bash
uv run <skill>/ooxml/scripts/unpack.py contract.docx unpacked
```

自己写的 Python 要声明依赖，用 `uv run --with defusedxml script.py`，或写 PEP 723 头。Node 脚本用 `NODE_PATH=<skill>/node_modules node build.js`。`<skill>/node_modules` 不存在时，在 `<skill>` 里执行一次 `npm install`。渲染页面需要 LibreOffice（`soffice`）和 poppler（`pdftoppm`）。阅读需要 pandoc。

## 选哪条流程

| 任务 | 用什么 |
|---|---|
| 读正文 | `pandoc --track-changes=all file.docx -t markdown`。它也会显示修订和批注。把 `all` 换成 `accept` 或 `reject`，看接受或拒绝之后的结果。 |
| 新建文档 | docx-js：先读 [docx-js.md](docx-js.md)。那里写了页面尺寸、样式和图片上会把文件弄坏的行为。 |
| 改别人的文档，或任何法律、学术、商务、正式文件 | 用修订，让每一处修改都能审。流程见下面的修订。 |
| 对本会话里你刚建的文档做小改 | 用同一套库，不跟踪。改完调用 `doc.save(require_tracking=False)`，它仍会检查架构。改动大就用 docx-js 重新生成。 |
| 批注、元数据、嵌入媒体、原始结构 | 解包后读 XML。[ooxml.md](ooxml.md) 里有写法。 |

## 写作过程

这份过程只用于给人读的正文。它不管 OOXML 是否合法。排版和校验仍按上面的流程做。

1. 先问上下文。读者是谁，这份文件要让人做出什么决定，已有的材料，不能写的内容，大概多长。缺了就问。不要用空话把篇幅填满。
2. 按节写。一次只写一节。写完停一下，用一两句话说明这一节要让读者带走什么，再写下节。不要把后面的节提前写完。
3. 换一个没有上下文的读者来看。这一轮不要带着刚才的对话和你知道的背景。只把这一节的文字交给它，让它标出没说清的地方、默认读者已经知道的地方、一个词可以有两种理解的地方。改到这个读者能独立读懂，再写下节。
4. 各节都通过之后，再跑本技能的校验和渲染。写作过程不能代替那两步。

## 修订流程

1. **读。** 用上面的 pandoc 转出文档，列出你要做的每一处修改。用周围的文字定位，不要用 markdown 行号，行号和 XML 对不上。
2. **解包。** `uv run <skill>/ooxml/scripts/unpack.py contract.docx unpacked` 会打印一个建议的 RSID。把它传给 `Document(..., rsid=...)`，让这一次会话的修改共用一个修订号。
3. **改。** 先读 [ooxml.md](ooxml.md)，再写一个使用 `Document` 库的脚本。多数修改用 `tracked_replace(old, new)`：它能跨 run 找到文字，并且只标记真正不同的词。相关的修改一批一批做，每批几个到十几个，失败时好定位。每批之前重新 grep `unpacked/word/document.xml`，因为每次保存行号都会变。
4. **保存。** `doc.save()` 拒绝写入有未跟踪修改的文档，也拒绝架构非法的 XML，并打印差异。改脚本，不要跳过校验。
5. **打包。** `uv run <skill>/ooxml/scripts/pack.py unpacked reviewed.docx` 重新打包，并检查 LibreOffice 能否打开。
6. **核对。** 运行 `pandoc --track-changes=all reviewed.docx -t markdown`，确认每一处打算做的修改都在，且没有别的改动。然后按下面检查输出。

要接受或拒绝已有修订，先调用 `doc.accept_all_changes()` 或 `doc.reject_all_changes()`，再做你自己的修改。

## 检查输出

1. **校验。** `uv run <skill>/ooxml/scripts/validate.py reviewed.docx --original contract.docx` 检查架构，并检查相对原稿的每一处修改都已跟踪。`doc.save()` 跑的是同一套检查。传入 `--author NAME`，允许直接改这位作者早先插入的文字。从零生成的文档不要传 `--original`，只检查架构。
2. **看页面。** `uv run <skill>/ooxml/scripts/render.py reviewed.docx pages` 为每一页打印一个 PNG 路径（范围用 `--pages 2-4`）。你创建或重排过的文档，交付前要读这些图。LibreOffice 会把 docx-js 的目录渲染成空的。Word 打开文件时才会填上。

渲染图能不能用来判断中文，取决于本机有没有 Noto CJK。见下一节。

## 中文和东亚字体

正文里有汉字时，必须同时写上西文字体和东亚字体。只写 `w:ascii` / `w:hAnsi` 时，Word 会去用主题里的东亚字体，LibreOffice 渲染时常落到没有汉字的字体上，字变成方框。

- 每个 `w:rFonts` 都写 `w:eastAsia`。优先用 Microsoft YaHei、Source Han Sans 或 SimSun。本机没有这些，就用已经安装的 Noto Sans CJK SC 或 Noto Serif CJK SC。
- docx-js 不要只写 `font: "Arial"`。写成带 `eastAsia` 的对象。示例和页面尺寸见 [docx-js.md](docx-js.md)。
- 新插入的中文 run 同样带上 `w:eastAsia`。不要假设主题会补上。
- 渲染检查用 LibreOffice。系统里要装好 Noto CJK（Debian/Ubuntu 是 `fonts-noto-cjk`）。没装时，渲染图不能用来判断缺字或换行。

```xml
<w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="Microsoft YaHei" w:cs="Arial"/>
```

## 会静默失败的坑

- **改到别人修订的中间。** 要删掉别人插入内容里的一段，把你的 `<w:del>` 嵌进去。不要直接改他们的文字。
- **用 pandoc 当编辑器。** 它会重写整篇文档，丢掉格式、批注和修订。只用它来读，不要用它产出交付文件。

## 在不同软件里怎么用

步骤在 Cursor、OpenCode、Codex、Claude Code、WorkBuddy 里相同。脚本在本机终端跑，不依赖某个聊天软件的专用工具。某个软件没有终端时，说明缺了哪一步，不要改流程去迁就它。

依赖：Python 3.12（推荐 `uv`）、Node.js（新建文档时）、LibreOffice、poppler、pandoc。看中文渲染还要 Noto CJK。
