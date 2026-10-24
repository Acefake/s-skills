本技能译自 [appautomaton/document-SKILLs](https://github.com/appautomaton/document-SKILLs)（MIT）。该仓库说明写明，内容改编自 Anthropic 的 skills。许可证全文见 [LICENSE-document-skills](../../LICENSE-document-skills)。

# 填写 PDF 表单

`<skill>` 是这个技能的目录。每条命令都从用户的工作目录运行。先弄清你拿到的是哪一种表单：

```bash
uv run <skill>/scripts/check_fillable_fields.py form.pdf
```

有可填写域的表单，通过那些域来填。扁平表单，例如扫描件或存成 PDF 的印刷表格，是把文字放在你从页面图上定位的框里。无论哪一种，最后都要渲染结果并看图，因为前面每一步都可以成功，而值落在错误的位置。

## 可填写的表单

**1. 列出域。**

```bash
uv run <skill>/scripts/extract_form_field_info.py form.pdf field_info.json
```

每条有 `field_id`、`type`、`page`（从 1 开始）和 `rect`（PDF 点）。每种类型再带上它接受的值：

| type | 接受的值 |
|---|---|
| `text` | 任意字符串 |
| `checkbox` | `checked_value`（常常是 `"/Yes"` 或 `"/On"`）或 `unchecked_value`（`"/Off"`） |
| `radio_group` | `radio_options` 里的一个 `value`，例如 `"/blue"` |
| `choice` | `choice_options` 里的一个 `value` 或 `text` |

**2. 把域和标签对上。** 域 id 常常没有意义，像 `Text12` 或 `topmostSubform[0].Page1[0].f1_03[0]`，所以看每个域在页面上的位置：

```bash
uv run <skill>/scripts/convert_pdf_to_images.py form.pdf pages --fields field_info.json
```

每个 `pages/page_<n>_fields.png` 用红框框出每个域，并标上它的 id。单选项标成 `id=value`。

**3. 写 `field_values.json`，** 只给要填的域：

```json
[
  {"field_id": "last_name", "page": 1, "value": "Simpson"},
  {"field_id": "over_18", "page": 1, "value": "/Yes"},
  {"field_id": "state", "page": 1, "value": "NY"}
]
```

**4. 填写。**

```bash
uv run <skill>/scripts/fill_fillable_fields.py form.pdf field_values.json filled.pdf
```

每个 id、页码和值都会先检查。有任何错误，它列出全部问题，什么都不写，并以状态 1 退出。

**5. 看结果。**

```bash
uv run <skill>/scripts/convert_pdf_to_images.py filled.pdf check
```

检查每一页：每个值落在打算填的域里，该勾的框勾上了，没有文字被裁切。两个已知限制：

- **列表框。** 多行列表框画出来时不会高亮选中项，虽然值已经存上。用 `PdfReader("filled.pdf").get_fields()[field_id]["/V"]` 确认。
- **其他文字体系。** 只要有文字超出西欧字符，脚本会让查看器用自己的字体来画，预览里可能看不到。告诉用户到他们的查看器里核对。中文属于这一类。

## 没有域的表单

这里你自己放每个值，在页面图上定位的框里写成文字注释。

**1. 渲染页面。**

```bash
uv run <skill>/scripts/convert_pdf_to_images.py form.pdf pages
```

记下每一页印出来的尺寸。`fields.json` 需要它。

**2. 在图上定位每个域。** 每个域给两个图像素框，`[left, top, right, bottom]`：一个框住印好的标签，一个框住值要放进去的空白。两个不能重叠，填写框要高到放得下文字。常见版式：

- **标签在框里面**（`│ Name:          │`）：填写区从标签延伸到框的右边缘。
- **标签在一条线前面**（`Email: ________`）：填写区在线上，占满线的宽度。
- **标签在线下面**（签名和日期）：填写区在线的上方。
- **标签在线上面**：填写区填满标签和线之间的空白。
- **复选框**（`Yes □  No □`）：填写框只盖住方块，不盖住标签。文字是 `"X"`。

**3. 写 `fields.json`：**

```json
{
  "pages": [{"page_number": 1, "image_width": 773, "image_height": 1000}],
  "form_fields": [
    {
      "page_number": 1,
      "description": "Applicant's last name",
      "field_label": "Last name",
      "label_bounding_box": [30, 125, 95, 142],
      "entry_bounding_box": [100, 125, 280, 142],
      "entry_text": {"text": "Johnson", "font_size": 12, "font_color": "000000"}
    },
    {
      "page_number": 1,
      "description": "Over 18: Yes",
      "field_label": "Yes",
      "label_bounding_box": [100, 525, 132, 540],
      "entry_bounding_box": [140, 525, 155, 540],
      "entry_text": {"text": "X"}
    }
  ]
}
```

`entry_text` 里，`font_size` 默认 12，`font_color` 默认黑。文字超出西欧字符时，加上 `"font_file"`，指向一个覆盖它的 TrueType 字体路径。没有的话，会试几个常见的系统字体。中文必须给 `font_file`。reportlab 读不了大多数 Noto CJK 的 CFF 文件，见 [reference.md](reference.md#fonts-for-new-pdfs)。

**4. 检查框，** 先自动，再目视：

```bash
uv run <skill>/scripts/check_bounding_boxes.py fields.json form.pdf
uv run <skill>/scripts/create_validation_image.py 1 fields.json pages/page_1.png pages/check_1.png
```

第一条报告重叠的框，以及相对字号太矮的填写框。第二条把填写框画成红的，标签框画成蓝的。看每一张校验图：

- 红框只盖住空白，不盖住印好的文字。
- 蓝框盖住标签。
- 复选框上，红框对准方块的中心。

改 `fields.json`，重复到两项都干净。

**5. 填写。**

```bash
uv run <skill>/scripts/fill_pdf_form_with_annotations.py form.pdf fields.json filled.pdf
```

比框更宽的文字会被缩小以适应，并给出警告。警告通常意味着框太小。脚本拒绝和页面不匹配的图像尺寸，这发生在图来自另一个工具或另一页时。

**6. 看结果，** 和可填写路径的第 5 步一样。每个值都必须在它的空白里，正向、可读。有一个偏了，就在 `fields.json` 里改它的框，再从原始的 `form.pdf` 重填。

## 压平

```bash
uv run <skill>/scripts/flatten_form.py filled.pdf final.pdf
```

这把填好的值画进页面内容，于是不能再改，并且在每个查看器里看起来一样。两种表单它都处理。用户要寄出一份填完的表，或想锁定它时，以及在合并可能域名冲突的表单之前，做压平。先看填好的文件。压平之后的错误只能靠重新填原始文件来修。

## 手工转换坐标

域的矩形是 PDF 点，原点在左下。页面图是像素，原点在左上，显示的是裁切过、并按 `/Rotate` 旋转后的页面。要在两者之间转换，例如在图上指出一个域的位置：

```bash
uv run <skill>/scripts/pdf_coords.py form.pdf 1 773x1000 --to-image 120,690,320,710
uv run <skill>/scripts/pdf_coords.py form.pdf 1 773x1000 --to-pdf 100,125,280,142
```
