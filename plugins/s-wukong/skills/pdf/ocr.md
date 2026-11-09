# 扫描版 PDF 的 OCR

`pdftotext` 或 `page.extract_text()` 对肉眼能看到文字的页面几乎什么都返回不了时，这份 PDF 需要 OCR。这需要 Tesseract 引擎（`brew install tesseract`，或 `apt-get install tesseract-ocr`），以及英语以外的语言数据（`brew install tesseract-lang`，中文简体例如 `apt-get install tesseract-ocr-chi-sim`）。用 `tesseract --list-langs` 检查。

用 `uv run --with pytesseract --with pdf2image --with Pillow ocr.py` 运行。页面一次渲染、一次识别，长文档的内存保持平的：

```python
import pytesseract
from pdf2image import convert_from_path, pdfinfo_from_path
from PIL import ImageFilter, ImageOps


def clean(image):
    """Greyscale, stretch contrast, remove speckle: helps on poor scans, rarely hurts on good ones."""
    return ImageOps.autocontrast(ImageOps.grayscale(image)).filter(ImageFilter.MedianFilter(3))


def ocr_pdf(path, lang="eng", dpi=300):
    pages = pdfinfo_from_path(path)["Pages"]
    for n in range(1, pages + 1):
        image = convert_from_path(path, dpi=dpi, first_page=n, last_page=n)[0]
        yield n, pytesseract.image_to_string(clean(image), lang=lang)


with open("scanned.txt", "w", encoding="utf-8") as out:
    for n, text in ocr_pdf("scanned.pdf", lang="eng"):
        out.write(f"--- Page {n} ---\n{text}\n")
```

## 怎样才认得准

- **分辨率。** 普通正文用 300 dpi。小字用 400。低于 200，准确率掉得很快。
- **语言。** 把页面上的每种语言都传进去，例如 `lang="chi_sim+eng"`。用英语模型认中文，会得到看起来很自信的胡话。
- **版面。** Tesseract 会猜每一页的版面。单块或单栏时，`config="--psm 6"` 常常更好。表格这类稀疏文字试 `--psm 11`。
- **位置。** `pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)` 返回每个词的框和 0 到 100 的置信度。用它定位文字，或标出大约低于 60 的词再核对。
- **可搜索的 PDF。** `pytesseract.image_to_pdf_or_hocr(image, extension="pdf")` 返回一页带隐形文字层的 PDF。用 pypdf 的 `PdfWriter.append` 把各页合起来。

OCR 的输出总有错。在依赖数字、人名或日期之前，对照页面图抽查。
