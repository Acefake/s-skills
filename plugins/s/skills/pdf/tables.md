本技能译自 [appautomaton/document-SKILLs](https://github.com/appautomaton/document-SKILLs)（MIT）。该仓库说明写明，内容改编自 Anthropic 的 skills。许可证全文见 [LICENSE-document-skills](../../LICENSE-document-skills)。

# 用 pdfplumber 提取表格

脚本用 `uv run --with pdfplumber script.py` 运行。pdfplumber 从页面的**左上角**量起（`top` 向下增大），和 pypdf、reportlab 的左下角原点不同。

## 选策略

`page.extract_tables(table_settings)` 用三种方式找单元格边，每个轴单独设置：

| 表看起来像 | 设置 |
|---|---|
| 有线的网格，每个单元格都有边 | 默认，两个轴都是 `"lines"` |
| 没有线，靠空白对齐的列 | `{"vertical_strategy": "text", "horizontal_strategy": "text"}` |
| 只有行与行之间有线 | `{"vertical_strategy": "text", "horizontal_strategy": "lines"}` |
| 检测一直失败 | 下面的显式线条 |

显式线条也要把策略设成 `"explicit"`。否则 pdfplumber 会把它们加到自己检测到的线上，页面上任何一根杂线都会变成额外的一列：

```python
import pdfplumber

with pdfplumber.open("report.pdf") as pdf:
    page = pdf.pages[0]
    rows = page.extract_table({
        "vertical_strategy": "explicit",
        "horizontal_strategy": "explicit",
        "explicit_vertical_lines": [72, 172, 272, 372],         # x positions
        "explicit_horizontal_lines": [100, 125, 150, 175, 200],  # distances from the top
    })
```

位置从 `page.chars` 或 `page.extract_words()` 读，它们的 `x0` 和 `top` 用同一套坐标。要把检测限制在一个区域，先用 `page.crop((x0, top, x1, bottom))` 裁切。

## 看 pdfplumber 看到了什么

表抽错了，先把检测到的边画出来看图，再去调数字：

```python
import pdfplumber

with pdfplumber.open("report.pdf") as pdf:
    page = pdf.pages[0]
    page.to_image(resolution=150).debug_tablefinder({"vertical_strategy": "text"}).save("debug.png")
```

红线是检测到的边，圆圈是它们的交点，阴影是找到的单元格。通常调的是 `snap_tolerance` 和 `join_tolerance`（合并几乎对齐的边）、`intersection_tolerance`，以及文本策略的 `min_words_vertical` 和 `min_words_horizontal`。

## 跨页的表

pdfplumber 一页一页工作。把行接起来，并丢掉后面几页顶部重复的表头：

```python
import pdfplumber

with pdfplumber.open("report.pdf") as pdf:
    header, rows = None, []
    for page in pdf.pages:
        for table in page.extract_tables():
            if header is None:
                header, table = table[0], table[1:]
            elif table and table[0] == header:
                table = table[1:]
            rows.extend(table)
```

## 什么都不生效时

- `page.extract_text()` 什么都不返回：表是一张图。用 [ocr.md](ocr.md)。
- 合并单元格除了第一格之外都返回 `None`。按版式从左边或上边填上。
- 非常大的文档：在循环里处理每一页，不要先全部收集起来。pdfplumber 会缓存解析过的页，用完一页就调用 `page.close()`。
