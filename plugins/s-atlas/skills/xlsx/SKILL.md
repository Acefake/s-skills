---
name: xlsx
description: "「做表格」「做个 Excel」「写 xlsx」「加公式」「CSV 转成表」。创建、修改、分析 .xlsx 和 .xlsm。派生数字写成单元格公式，保存后用 LibreOffice 重算。Use when a task produces or modifies a spreadsheet, turns CSV or TSV into one, or needs its values, formulas, or formatting read."
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。

# Excel 工作簿

openpyxl 和 pandas 你已经会用。这个技能补上代码里看不到的部分：一步重算，报告工作簿里实际错了什么，以及 openpyxl 和 LibreOffice 会静默弄坏文件的行为。

## 运行脚本

`<skill>` 是包含本文件的目录。用绝对路径从用户的工作目录运行自带脚本，这样指向用户文件的相对路径仍然有效：

```bash
uv run <skill>/scripts/recalc.py model.xlsx
```

自己写的 Python 要声明依赖，用 `uv run --with openpyxl script.py`，或写 PEP 723 头。重算需要 LibreOffice（`soffice`）。

## 选哪个工具

- **openpyxl** 用于任何要交付的工作簿：公式、格式、图表、数据验证、批注。它会保留所加载文件里的图表、图片、批注、数据验证和条件格式。它丢掉自己不建模的东西，例如形状、文本框、切片器和表单控件。编辑带这些对象的工作簿之前先看清楚。
- **pandas** 用于分析和批量读取。它的写出只保留值，所以不要用它去改一份还会继续用的工作簿。
- `.xlsm` 要用 `load_workbook(path, keep_vba=True)` 加载，否则保存时宏会丢。

## 公式，不是算好的值

凡是派生出来的数，都写成表里的公式，这样输入一变，工作簿仍然是对的。只把没有表格形式的计算放在 Python 里，然后写成一个标了名的输入格。

```python
ws["B10"] = "=SUM(B2:B9)"          # not ws["B10"] = df["Sales"].sum()
ws["C5"] = "=(C4-C2)/C2"           # growth, from the cells it depends on
ws["D3"] = "=B3*(1+$B$1)"          # assumptions live in their own cells
```

## 检查输出

openpyxl 写出的公式没有缓存值，所以文件在重算之前不算完成。每次保存碰到了公式，都跑下面这条，交付前先修掉它报告的问题：

```bash
uv run <skill>/scripts/recalc.py model.xlsx
```

它在 LibreOffice 里重算，把值写回文件，并打印 JSON。干净时退出码是 0，有问题时是 1，跑不起来时是 2。

| 字段 | 含义和修法 |
|---|---|
| `errors` | 按类型列出的错误值，例如 `{"#DIV/0!": {"count": 3, "locations": ["Model!C7", …]}}`，每种最多 50 个位置。修这些单元格的公式。 |
| `missing_prefix` | 比文件格式要求更新的函数没写前缀（见下）。文件不会被改写，每条里的 `fix` 是改好的公式。 |
| `circular_references` | 互相依赖的单元格组。LibreOffice 把这些显示成 `#VALUE!`，先解开循环。 |
| `uncalculated` | LibreOffice 没算出值的公式。通常是它没实现的函数。工作簿在 Excel 里可能仍然能算，要告诉用户。 |

链接到其他工作簿时它会停下来，因为重算会覆盖链接过来的值。只有用户接受这一点时才传 `--force`。

## 会静默失败的坑

- **函数前缀。** 比 Excel 2007 新的函数要带前缀存储。写成 `=_xlfn.XLOOKUP(…)`、`=_xlfn.TEXTJOIN(…)`、`=_xlfn.IFS(…)`，以及 `=_xlfn._xlws.FILTER(…)` 和 `=_xlfn._xlws.SORT(…)`。没有前缀时，Excel 和 LibreOffice 都显示 `#NAME?`。recalc 会在造成损害之前抓住这些。LibreOffice 低于 24.8（`soffice --version`）没有 XLOOKUP、XMATCH、FILTER、SORT、SORTBY、UNIQUE、SEQUENCE 和 LET，所以即使加了前缀，recalc 也会标出来。工作簿在 Excel 里仍然能算，告诉用户，不要为了这个改写公式。
- **插入或删除行列。** `insert_rows`、`delete_rows`、`insert_cols`、`delete_cols` 会移动单元格，但不会改写引用它们的公式。在上方插入一行之后，`=SUM(B1:B4)` 仍然是 `=SUM(B1:B4)`。自己改写受影响的公式，或者把表排成不需要插入。
- **`data_only=True`** 读的是缓存值。用这种方式打开后再保存，会把每个公式永久换成它上一次的值。
- **动态数组。** openpyxl 写不出溢出公式。FILTER、SORT、UNIQUE、SEQUENCE 会落在一个单元格里，Excel 还会给它们加上 `@`。优先用每个单元格返回一个值的公式。
- **下标。** 行和列从 1 开始。用 `get_column_letter` 和 `column_index_from_string`。不要用手从字母数到 Z 以后。

## 图表

属于工作簿的图表用 openpyxl 自带的图表（`openpyxl.chart`），它们保持和单元格的链接。只有图表要拿到别处去时，才渲染 matplotlib 图片。

## 已有的工作簿和模板

改之前先看文件，字体、填充、数字格式、列宽和版式都按它的来。它的习惯压过下面的一切。

单元格里有中文时，字体写成本机有的 CJK 字体（Microsoft YaHei、Source Han Sans、SimSun，或已安装的 Noto Sans CJK SC）。不要只写 Calibri，否则 LibreOffice 打开时汉字会变成方框。要看渲染时，系统里要有 Noto CJK（`fonts-noto-cjk`）。重算本身不检查缺字。

## 财务模型

用户或模板没有另外规定时：

- **按角色设字体颜色：** 手写输入用蓝 `0000FF`，公式用黑，链接到其他表用绿 `008000`，链接到其他文件用红 `FF0000`。关键假设用黄 `FFFF00` 填充。
- **数字格式：**
  - 货币：`$#,##0;($#,##0);-`，单位写在表头，例如 "Revenue ($mm)"。
  - 百分比：`0.0%`。
  - 倍数：`0.0x`。
  - 负数：用括号。
  - 年份：写成文本，这样 "2026" 不会变成 "2,026"。
- **结构：** 每个假设单独占一个标了名的单元格，被引用，不要写进公式里。每一期预测用和前一期相同的公式。
- **来源：** 每个手写数字都在单元格批注或相邻单元格里给出处，例如 "Source: Company 10-K, FY2025, p. 45"。

## 在不同软件里怎么用

步骤在 Cursor、OpenCode、Codex、Claude Code、WorkBuddy 里相同。脚本在本机终端跑。某个软件没有终端时，说明缺了哪一步，不要改流程去迁就它。

依赖：Python 3.12（推荐 `uv`）和 LibreOffice。看中文时还要 Noto CJK。
