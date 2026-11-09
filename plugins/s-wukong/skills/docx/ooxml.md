# 编辑 Word 文档：Document 库和 OOXML

这份文件讲怎么改一份解包后的 `.docx`：做修订和批注的 Python `Document` 库，以及它底下的 XML 写法。

## 用这个库跑脚本

脚本把技能目录插到 `sys.path` 的最前面，这样导入不会和用户项目里的 `scripts` 包撞上。依赖写在 PEP 723 头里，用 `uv run` 跑：

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["defusedxml>=0.7", "lxml>=5"]
# ///
import sys
sys.path.insert(0, "<skill>")  # absolute path of the docx skill directory
from scripts.document import Document, DocxXMLEditor

doc = Document("unpacked", author="Claude", initials="C")
```

```bash
uv run edit.py
```

`Document` 的选项：

- `author` 和 `initials`：每处修改和批注上的审阅者名字。默认是 "Claude"/"C"。改成用户希望审阅者看到的名字。
- `rsid`：设成 `unpack.py` 打印的那个值，这样这一次会话的修改共用一个修订号。省略时会生成一个。
- `track_revisions=True`：在文件里打开修订，用户之后自己的修改也会被跟踪。

库改的是解包目录的一份临时副本。`doc.save()` 校验结果，再把它拷回去（或 `doc.save("other-dir")`）。

## 修订

### 替换文字：`tracked_replace`

几乎每次修改都用它。即使 Word 把一段文字拆进多个 run，它也能在段落里找到。格式变化、校对标记，以及中文或日文的脚本边界，都会拆 run。然后它只标记真正不同的字：

```python
body = doc["word/document.xml"]
body.tracked_replace("within 30 days", "within 45 days")      # marks 30 -> 45 only
body.tracked_replace("期限为30天", "期限为45天")                 # CJK is compared per character
body.tracked_replace("Acme Corp", "Acme Inc.", replace_all=True)
body.tracked_replace("the Seller", "the Vendor", scope=body.get_node(tag="w:p", contains="Section 4.2"))
body.tracked_replace(", without limitation,", "")              # deletion
```

- `old` 必须落在一个段落里，并且和它的可见文字完全一致。已删除的文字不会被搜索。制表符匹配 `"\t"`，换行匹配 `"\n"`。
- `old` 出现不止一次时，它会抛出并指出位置。用 `scope=` 缩小范围（任意元素：段落、表、单元格），或传 `replace_all=True`。
- 没变的文字保留原来的 run、格式和 RSID。插入的文字沿用它替换掉的那段的格式。新插入的中文要带 `w:eastAsia`，见文末字体一节。库沿用被替换文字的格式，原来没有东亚字体时，你要在 XML 里补上。
- 它返回新的 `w:del`/`w:ins` 元素，可以直接给 `doc.add_comment(start=..., end=...)`。
- 别人插入内容里的文字可以删除，这会把你的删除嵌进他们的插入里。只有修改碰到那次插入的开头或结尾时才能替换。改在中间时，用 `revert_insertion()` 拒绝整段插入，再插入改正后的文字。

### 删除整个 run 或段落

```python
body.suggest_deletion(body.get_node(tag="w:r", contains="text to delete"))
body.suggest_deletion(body.get_node(tag="w:p", contains="paragraph to delete"))
```

删除段落时，它的段落标记也会被标成删除。接受修改后，段落被去掉，而不是留下一个空行。正文、单元格或文本框的最后一段会保留段落标记，和 Word 一样。

### 插入段落

```python
target = body.get_node(tag="w:p", contains="existing list item")
pPr = tags[0].toxml() if (tags := target.getElementsByTagName("w:pPr")) else ""
body.insert_after(target, DocxXMLEditor.suggest_paragraph(f"<w:p>{pPr}<w:r><w:t>New item</w:t></w:r></w:p>"))
```

`suggest_paragraph` 用 `<w:ins>` 包住 run，并把段落标记标成插入。复用邻居的 `w:pPr`，列表编号和样式才保持。中文的新 run 写成带 `w:eastAsia` 的 `w:rFonts`，不要只写 `<w:t>`。

### 别人的修改

```python
ins = body.get_node(tag="w:ins", attrs={"w:id": "5"})
body.revert_insertion(ins)        # reject their insertion: nests a <w:del> inside it
dele = body.get_node(tag="w:del", attrs={"w:id": "3"})
body.revert_deletion(dele)        # reject their deletion: re-inserts the text after it
```

两者也接受段落或其他容器，会处理里面的每一次插入或删除。

### 全部接受或全部拒绝

```python
doc.accept_all_changes()   # or doc.reject_all_changes()
```

这些覆盖正文、页眉、页脚、脚注、尾注和批注，和 Word 的全部接受、全部拒绝一样。包括段落标记、移动、表行和格式修改。在你自己的修改之前调用。更早做的修改必须已经跟踪，后面的修改会对照已经定稿的文档来检查。

### 自己写 XML

没有合适的方法时，用显式的 `<w:del>`/`<w:ins>` 替换节点。库会给新元素填上 `w:id`、`w:author`、`w:date` 和 RSID：

```python
node = body.get_node(tag="w:r", contains="The report is monthly")
rpr = tags[0].toxml() if (tags := node.getElementsByTagName("w:rPr")) else ""
body.replace_node(node,
    f'<w:r>{rpr}<w:t xml:space="preserve">The report is </w:t></w:r>'
    f'<w:del><w:r>{rpr}<w:delText>monthly</w:delText></w:r></w:del>'
    f'<w:ins><w:r>{rpr}<w:t>quarterly</w:t></w:r></w:ins>')
```

每处修订都必须遵守：

- `<w:ins>` 和 `<w:del>` 在段落层级包住整个 `<w:r>`，不要包进 run 的内部。
- 删除的文字放在 `<w:delText>` 里，不放在 `<w:t>` 里。
- 只标记变化的部分。没变的文字留在原来的 run 里，属性也留着。
- 不要直接改别人的 `<w:ins>` 或 `<w:del>` 内部。要删掉他们插入内容的一部分，把你的 `<w:del>` 嵌进去。要恢复他们的删除，在它后面加你的 `<w:ins>`。

```xml
<!-- Rejecting part of Jane's insertion, then adding a replacement after it -->
<w:ins w:id="16" w:author="Jane Smith" w:date="2026-01-15T10:00:00Z">
  <w:r><w:t xml:space="preserve">in silence, </w:t></w:r>
  <w:del w:author="Claude"><w:r><w:delText>safe and sound</w:delText></w:r></w:del>
</w:ins>
<w:ins w:author="Claude"><w:r><w:t>soft and unbound</w:t></w:r></w:ins>

<!-- Restoring Jane's deletion -->
<w:del w:id="50" w:author="Jane Smith" w:date="2026-01-15T10:00:00Z">
  <w:r><w:delText>within 30 days</w:delText></w:r>
</w:del>
<w:ins w:author="Claude"><w:r><w:t>within 30 days</w:t></w:r></w:ins>
```

### `save()` 检查什么

结果不合法时 `doc.save()` 会抛出。它检查两件事：

- **架构：** XML 必须符合 OOXML 架构，忽略原文件里已经有的问题。
- **跟踪：** 拒绝每一处修订之后必须回到原文，所以没跟踪就做的修改会显示成差异，不管作者是谁。其他作者的插入也必须保住他们的文字。

错误会打印出不同的文字。常见原因是直接改文字，而不是通过 `<w:ins>`/`<w:del>`，以及改到别人的修订里面。自己的、不需要审阅的文档，用 `save(require_tracking=False)`，保留架构检查，去掉跟踪检查。`save(validate=False)` 两项都跳过。只用它查看一个坏掉的状态，不要用于交付。

## 批注

```python
para = body.get_node(tag="w:p", contains="paragraph text")
cid = doc.add_comment(start=para, end=para, text="Please confirm this date.")
doc.reply_to_comment(parent_comment_id=cid, text="Confirmed with finance.")

changes = body.tracked_replace("30 days", "45 days")
doc.add_comment(start=changes[0], end=changes[-1], text="Extended per the March amendment.")
```

`start` 和 `end` 可以是段落、run 或修订元素。库会创建或更新 `comments.xml` 和它的配套部分，以及它们的关系和内容类型。来自 Word、LibreOffice、docx-js 和 pandoc 的文档都能用。

## 找节点

```python
body.get_node(tag="w:p", contains="specific text")             # text within the element
body.get_node(tag="w:del", attrs={"w:id": "1"})                 # attribute values
body.get_node(tag="w:p", line_number=42)                        # line where the tag opens
body.get_node(tag="w:r", contains="Section", line_number=range(2400, 2500))
```

`get_node` 必须正好匹配一个元素。`contains` 看的是单个元素的文字，所以跨 run 拆开的文字用 `tag="w:p"` 找，或直接用 `tracked_replace` 替换。行号指的是刚解包时的文件，所以每次保存之后重新 grep `word/document.xml`。

`doc["word/comments.xml"]`、`doc["word/header1.xml"]` 等给出其他部分的编辑器。每个编辑器的 `.dom` 是 minidom 文档，方法覆盖不到的操作用它。

## 插入图片

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["defusedxml>=0.7", "lxml>=5", "Pillow>=10"]
# ///
import shutil, sys
sys.path.insert(0, "<skill>")
from PIL import Image
from scripts.document import Document, DocxXMLEditor

doc = Document("unpacked")
body = doc["word/document.xml"]

# Copy the image into the working copy the library edits, under an unused name
media = doc.unpacked_path / "word" / "media"
media.mkdir(exist_ok=True)
n = 1
while (media / f"image{n}.png").exists():
    n += 1
shutil.copy("chart.png", media / f"image{n}.png")

# Full usable width (6.5 in on Letter with 1 in margins), keeping the aspect ratio
w, h = Image.open("chart.png").size
cx = int(6.5 * 914400)
cy = cx * h // w

rels = doc["word/_rels/document.xml.rels"]
rid = rels.get_next_rid()
rels.append_to(rels.dom.documentElement,
    f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/image{n}.png"/>')
types = doc["[Content_Types].xml"]
if not any(d.getAttribute("Extension").lower() == "png" for d in types.dom.getElementsByTagName("Default")):
    types.append_to(types.dom.documentElement, '<Default Extension="png" ContentType="image/png"/>')

# Drawing ids must be unique across the document
pic_id = 1 + max((int(e.getAttribute("id")) for e in body.dom.getElementsByTagName("wp:docPr")), default=0)

anchor = body.get_node(tag="w:p", contains="Second paragraph")
body.insert_after(anchor, DocxXMLEditor.suggest_paragraph(f'''<w:p><w:r><w:drawing>
  <wp:inline distT="0" distB="0" distL="0" distR="0">
    <wp:extent cx="{cx}" cy="{cy}"/>
    <wp:docPr id="{pic_id}" name="Picture {pic_id}"/>
    <a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
      <pic:pic>
        <pic:nvPicPr><pic:cNvPr id="{pic_id}" name="image{n}.png"/><pic:cNvPicPr/></pic:nvPicPr>
        <pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>
        <pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>
      </pic:pic>
    </a:graphicData></a:graphic>
  </wp:inline>
</w:drawing></w:r></w:p>'''))
doc.save()
```

`suggest_paragraph` 把这次插入做成修订。用户不想审这张图时，去掉它，静默插入。A4、1 英寸边距时，可用宽度是 6.27 英寸。

## XML 参考

### 容易踩到的架构规则

- **`<w:pPr>`：** 子元素顺序固定，从 `pStyle`、`keepNext`、`keepLines`、`pageBreakBefore`、`numPr` 开始，经过 `spacing`、`ind`、`jc`，以 `rPr`、`sectPr`、`pPrChange` 结束。
- **空白：** `<w:t>` 的文字以空格开头或结尾时，需要 `xml:space="preserve"`，否则空格会被丢掉。
- **文字编码：** `unpack.py` 写的是 UTF-8，弯引号、破折号和中文都可以直接打。`&#8220;`（“）这类实体也可以。`contains=` 搜索里，两种写法找到的是同一段文字。
- **设置：** 用 `Document(..., track_revisions=True)` 打开修订，它把 `<w:trackRevisions/>` 放在 `settings.xml` 里符合架构的位置：在 `w:proofState`、`w:attachedTemplate`、`w:documentType`、`w:mailMerge` 和 `w:revisionView` 之后，有哪个算哪个。
- **ID 和 RSID：** RSID 是 8 位十六进制。修订的 `w:id` 必须唯一。库会分配它们。

### 段落和 run

```xml
<w:p>
  <w:pPr><w:pStyle w:val="Heading2"/><w:jc w:val="center"/></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>Bold heading text</w:t></w:r>
</w:p>
<!-- run formatting: <w:i/> italic, <w:u w:val="single"/> underline,
     <w:highlight w:val="yellow"/>, <w:rFonts w:ascii="Courier New" w:hAnsi="Courier New"/> -->
<w:p><w:r><w:br w:type="page"/></w:r></w:p>   <!-- page break -->
```

中文 run 把注释里的 `w:rFonts` 写成带东亚字体的形式：

```xml
<w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="Microsoft YaHei" w:cs="Arial"/>
```

优先 Microsoft YaHei、Source Han Sans 或 SimSun。渲染检查要装 Noto CJK。

### 列表

```xml
<w:p>
  <w:pPr>
    <w:pStyle w:val="ListParagraph"/>
    <w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr>
  </w:pPr>
  <w:r><w:t>First item</w:t></w:r>
</w:p>
```

`w:ilvl` 是嵌套层级。另一个 `w:numId` 在 `numbering.xml` 里定义，开始一份单独的列表。要延续已有列表，复制已有项的 `w:pPr`。

### 表格

```xml
<w:tbl>
  <w:tblPr><w:tblStyle w:val="TableGrid"/><w:tblW w:w="0" w:type="auto"/></w:tblPr>
  <w:tblGrid><w:gridCol w:w="4680"/><w:gridCol w:w="4680"/></w:tblGrid>
  <w:tr>
    <w:tc><w:tcPr><w:tcW w:w="4680" w:type="dxa"/></w:tcPr><w:p><w:r><w:t>Cell 1</w:t></w:r></w:p></w:tc>
    <w:tc><w:tcPr><w:tcW w:w="4680" w:type="dxa"/></w:tcPr><w:p><w:r><w:t>Cell 2</w:t></w:r></w:p></w:tc>
  </w:tr>
</w:tbl>
```

### 超链接和书签

```xml
<w:hyperlink r:id="rId5"><w:r><w:rPr><w:rStyle w:val="Hyperlink"/></w:rPr><w:t>External link</w:t></w:r></w:hyperlink>
<w:hyperlink w:anchor="myBookmark"><w:r><w:rPr><w:rStyle w:val="Hyperlink"/></w:rPr><w:t>Internal link</w:t></w:r></w:hyperlink>
<w:bookmarkStart w:id="0" w:name="myBookmark"/><w:r><w:t>Target</w:t></w:r><w:bookmarkEnd w:id="0"/>
```

- **外部链接：** 需要 `word/_rels/document.xml.rels` 里的一条关系：`<Relationship Id="rId5" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" Target="https://example.com/" TargetMode="External"/>`。
- **Hyperlink 样式：** `styles.xml` 没定义它时，链接看起来像普通文字：

```xml
<w:style w:type="character" w:styleId="Hyperlink">
  <w:name w:val="Hyperlink"/><w:basedOn w:val="DefaultParagraphFont"/><w:uiPriority w:val="99"/><w:unhideWhenUsed/>
  <w:rPr><w:color w:val="467886" w:themeColor="hyperlink"/><w:u w:val="single"/></w:rPr>
</w:style>
```

### 加内容时要更新的部分

- `word/_rels/document.xml.rels`：每个新部分、图片或外部链接一条 `Relationship`。
- `[Content_Types].xml`：每种扩展名一条 `Default`（`png`、`jpeg`），每个新的 XML 部分一条 `Override`。加之前先查，重复的条目会弄坏包。
