# PDF 参考

明显的 API 调用会做错的地方。Python 用 `uv run --with pypdf script.py` 跑，按需要加上包。

## 坐标

| 来源 | 原点 | 单位 |
|---|---|---|
| PDF 内容、pypdf、reportlab、表单域的 `/Rect` | 页面框的左下角 | 点 |
| pdfplumber（`top`、`bottom`）、`pdftotext -bbox-layout` | 左上角 | 点 |
| 页面图片 | 左上角 | 像素 |

页面框不一定从 (0, 0) 开始。读 `page.cropbox.left` 和 `page.cropbox.bottom`，不要假设它从零开始。`/Rotate` 只在显示时转动页面：内容保持未旋转的坐标。`scripts/pdf_coords.py` 在页面图片和 PDF 点之间转换框，两件事都算进去。

## 带位置的文字

```python
import pdfplumber

with pdfplumber.open("in.pdf") as pdf:
    for w in pdf.pages[0].extract_words():
        print(w["text"], w["x0"], w["top"], w["x1"], w["bottom"])
```

- **命令行的版面文字：** `pdftotext -layout -f 1 -l 3 in.pdf out.txt` 让列并排保留。pypdf 的 `extract_text()` 按绘制顺序返回文字，那不一定是阅读顺序。
- **命令行的词框：** `pdftotext -bbox-layout in.pdf out.html` 写出 XHTML，每个块、行和词一个框。
- **pypdfium2 5.x** 快，并且不需要 poppler：`pdfium.PdfDocument("in.pdf")[0].get_textpage().get_text_range()`。PDF 坐标里的一个区域用 `get_text_bounded(left, bottom, right, top)`。`page.get_text()` 已经不存在。

## 合并和拆分

```python
from pypdf import PdfWriter

writer = PdfWriter()
for path in ["a.pdf", "b.pdf"]:
    writer.append(path)               # keeps bookmarks and links; add_page() drops them
writer.write("merged.pdf")
```

- `writer.append(path, pages=(0, 3))` 取一个页范围。
- 命令行：`pdfunite a.pdf b.pdf merged.pdf` 和 `pdfseparate -f 2 -l 5 in.pdf page-%d.pdf`（poppler）。
- 合并两份同名域的表单会把那些域连在一起，填一个就填了两个。先用 `scripts/flatten_form.py` 把每份表单压平。

## 印章、水印和页面编辑

```python
from pypdf import PdfReader, PdfWriter

stamp = PdfReader("stamp.pdf").pages[0]
writer = PdfWriter(clone_from="in.pdf")
for page in writer.pages:
    page.transfer_rotation_to_content()   # make content coordinates match what is displayed
    page.merge_page(stamp, over=False)     # over=False puts the stamp beneath the content
writer.write("stamped.pdf")
```

- **旋转过的页。** 没有 `transfer_rotation_to_content()` 时，印章会横着落在上面。
- **裁切。** 设置 `page.cropbox`，查看器显示的是它。除非你就是要丢掉外面的区域，否则别动 `page.mediabox`。
- **旋转。** `page.rotate(90)` 把页面按显示顺时针转。

<a id="fonts-for-new-pdfs"></a>

## 新建 PDF 的字体

reportlab 自带字体（Helvetica、Times、Courier）只覆盖西欧文字。中文、日文、韩文、西里尔文和其他文字会变成黑块。注册并嵌入一个覆盖这些文字的 TrueType 字体：

```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

pdfmetrics.registerFont(TTFont("Body", "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"))
c = canvas.Canvas("out.pdf")
c.setFont("Body", 14)
c.drawString(72, 720, "合同编号 Contract no. 2026-01")
c.save()
```

- `TTFont` 读 `.ttf` 和 TrueType 的 `.ttc`，字体集用 `subfontIndex=`。它读不了基于 CFF 的 OpenType，大多数 Noto CJK 文件属于这一类。LibreOffice 渲染 docx 和 pptx 时用的 `fonts-noto-cjk`，不能直接拿来当这里的 `TTFont`。
- `UnicodeCIDFont("STSong-Light")` 不需要字体文件，但它不嵌入，看起来取决于查看器。
- `pdffonts out.pdf` 列出每个字体以及它有没有嵌入。

## 加密

- **AES 需要额外的包。** 读或写 AES 加密的文件需要 `uv run --with 'pypdf[crypto]'`。没有它，pypdf 抛出 `DependencyError`。
- **空密码。** 很多受保护的 PDF 用户密码是空的，不用密码就能打开。检查 `reader.is_encrypted`，然后调用 `reader.decrypt(password)`。
- **加密：** `writer.encrypt(user_password, owner_password, algorithm="AES-256")`。不要用已经破掉的 RC4 算法。

## 图片和检查

- **嵌入的图片：** `pdfimages -list in.pdf` 显示每张图的尺寸和分辨率，`pdfimages -all in.pdf out/img` 按原始格式抽出它们。
- **文档信息：** `pdfinfo in.pdf` 给出页数、页面尺寸、加密和 PDF 版本。
- **损坏的文件：** `PdfWriter(clone_from=PdfReader("broken.pdf")).write("fixed.pdf")` 常常能修好坏掉的交叉引用表，因为 pypdf 默认读得比较宽容。
