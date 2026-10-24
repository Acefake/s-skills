---
name: pdf
description: "阅读、创建、填写和变换 PDF：提取文字和表格、扫描件 OCR、填写可填写或扁平表单，以及压平、合并、拆分、旋转、盖章和加密。Use when a task takes a .pdf as input or must produce one."
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。

本技能译自 [appautomaton/document-SKILLs](https://github.com/appautomaton/document-SKILLs)（MIT）。该仓库说明写明，内容改编自 Anthropic 的 skills。许可证全文见 [LICENSE-document-skills](../../LICENSE-document-skills)。

# PDF

pypdf、pdfplumber 和 reportlab 你已经会用。这个技能补上它们不提供的部分：会检查自己输入的填表脚本、按读者看到的样子查看页面的办法，以及会把内容静默放错位置的 PDF 行为。

## 运行脚本

`<skill>` 是包含本文件的目录。用绝对路径从用户的工作目录运行自带脚本，这样指向用户文件的相对路径仍然有效：

```bash
uv run <skill>/scripts/convert_pdf_to_images.py report.pdf pages
```

自己写的 Python 要声明依赖，用 `uv run --with pypdf script.py`，或写 PEP 723 头。渲染页面需要 poppler（`pdftoppm`）。OCR 还需要 Tesseract。

## 选哪个工具

| 任务 | 用什么 |
|---|---|
| 填表，可填写或扁平 | 一律看 [forms.md](forms.md)。每一步都有脚本。 |
| 文字 | pdfplumber，或命令行的 `pdftotext -layout`。页面上明明有字、提取却是空的，就是扫描件：看 [ocr.md](ocr.md)。 |
| 表格 | pdfplumber：看 [tables.md](tables.md) |
| 新建 PDF | reportlab：流式文档用 Platypus，精确摆放用 canvas |
| 合并、拆分、旋转、裁切、盖章、加密 | pypdf：能保住书签、链接和方向的调用见 [reference.md](reference.md) |
| 看某一页长什么样 | `scripts/convert_pdf_to_images.py` |

## 检查输出

创建或改过 PDF 之后，交付前渲染动过的页面并看图。检查文字在、读得清，没有被裁切或重叠，每个印章或值都在该在的位置：

```bash
uv run <skill>/scripts/convert_pdf_to_images.py out.pdf check --pages 1-3
```

中文是否缺字，取决于生成时有没有嵌入覆盖汉字的字体。见 [reference.md](reference.md) 的字体一节。用 LibreOffice 看别的办公文件时另说，这里渲染走的是 poppler。

## 会静默失败的坑

- **两套坐标系。** PDF 坐标从页面框的左下角起，单位是点。pdfplumber 和页面图片从左上角起。页面框不一定从 (0, 0) 开始，所以要读 `page.cropbox.left` 和 `.bottom`。
- **旋转过的页。** `/Rotate` 只在显示时转动页面。内容和表单域仍用未旋转的坐标。只用简单缩放和 y 翻转去摆放，会落在错误的位置。用 `scripts/pdf_coords.py` 转换框，盖章前调用 `page.transfer_rotation_to_content()`。
- **新建 PDF 里的非拉丁文字。** reportlab 自带字体把中文、西里尔文等画成黑块。注册并嵌入 TrueType 字体。见 [reference.md](reference.md#fonts-for-new-pdfs)。
- **合并。** `PdfWriter.append()` 保留书签和链接，用 `add_page()` 复制页面会丢掉它们。合并后同名表单域会变成一个域，填一个就填了两个。
- **AES 加密** 需要 `uv run --with 'pypdf[crypto]'`。没有它，pypdf 在打开或加密时抛出 `DependencyError`。

## 脚本

| 脚本 | 做什么 |
|---|---|
| `check_fillable_fields.py <pdf>` | 说明 forms.md 里哪条填表路径适用 |
| `extract_form_field_info.py <pdf> <out.json>` | 列出可填写域、所在页、框和接受的值 |
| `fill_fillable_fields.py <pdf> <values.json> <out.pdf>` | 检查过每个 id、页码和值之后再填 |
| `convert_pdf_to_images.py <pdf> <dir> [--pages] [--fields]` | 一页一页渲染成 PNG，可选地框出每个可填写域 |
| `check_bounding_boxes.py <fields.json> [pdf]` | 在填扁平表单之前找出重叠或太矮的框 |
| `create_validation_image.py <page> <fields.json> <png> <out.png>` | 把这些框画到页面图上，供目视检查 |
| `fill_pdf_form_with_annotations.py <pdf> <fields.json> <out.pdf>` | 用在各处渲染一致的文字填扁平表单 |
| `flatten_form.py <pdf> <out.pdf>` | 把填好的值画进页面，使其不能再改 |
| `pdf_coords.py <pdf> <page> <WxH> --to-pdf/--to-image <box>` | 在页面图像素和 PDF 点之间转换框 |

## 在不同软件里怎么用

步骤在 Cursor、OpenCode、Codex、Claude Code、WorkBuddy 里相同。脚本在本机终端跑。某个软件没有终端时，说明缺了哪一步，不要改流程去迁就它。

依赖：Python 3.12（推荐 `uv`）和 poppler。扫描件 OCR 另要 Tesseract 和对应语言包，中文简体是 `tesseract-ocr-chi-sim`。
