本技能译自 [appautomaton/document-SKILLs](https://github.com/appautomaton/document-SKILLs)（MIT）。该仓库说明写明，内容改编自 Anthropic 的 skills。许可证全文见 [LICENSE-document-skills](../../LICENSE-document-skills)。

# 编辑幻灯片 XML

只在 python-pptx 到不了的地方改 XML：主题颜色和字体、版式和母版、切换和动画、项目符号和编号的细节、图表内部、隐藏的幻灯片。文字和形状用 python-pptx，加、复制、重排或删除幻灯片用 `scripts/rearrange.py`，演讲者备注用 `scripts/notes.py`。这些会替你保持包的一致。

按循环做：解包，改一件事，运行 `<skill>/ooxml/scripts/validate.py unpacked --original deck.pptx`，修掉它报告的问题，然后打包。

## 东西在哪

| 部分 | 放什么 |
|---|---|
| `ppt/presentation.xml` | 幻灯片顺序（`<p:sldIdLst>`）和幻灯片尺寸 |
| `ppt/slides/slideN.xml` | 一张幻灯片的形状和文字 |
| `ppt/slides/_rels/slideN.xml.rels` | 这张幻灯片用到的东西：版式、图片、图表、链接、备注 |
| `ppt/slideLayouts/`、`ppt/slideMasters/` | 幻灯片继承的占位符和位置。这里一改，基于它的每张幻灯片都变。 |
| `ppt/theme/theme1.xml` | 配色（`<a:clrScheme>`）和字体（`<a:fontScheme>`） |
| `ppt/media/` | 图片 |
| `[Content_Types].xml` | 每个部分的类型 |

## 保持包完整

每个部分都通过关系到达，并在 `[Content_Types].xml` 里声明。增加一个部分要改三处：文件本身、使用它的那个部分上的关系（用它的 `r:id` 引用）、以及内容类型，扩展名用 `<Default>`，部分路径用 `<Override>`。删掉一个部分要把三处都撤掉。validate.py 会报告断掉的引用，以及没有任何东西指向的部分。

## 架构强制的规则

- **子元素顺序是固定的。** `<p:txBody>` 里依次是 `<a:bodyPr>`、`<a:lstStyle>`，然后是 `<a:p>` 段落。段落里先是 `<a:pPr>`，然后是它的 run，然后是 `<a:endParaRPr>`。
- **段落属性**（`<a:pPr>`）的子元素按这个顺序：间距（`lnSpc`、`spcBef`、`spcAft`），然后是项目符号的颜色、大小和字体，然后是项目符号本身（`buNone`、`buAutoNum` 或 `buChar`），然后是 `tabLst` 和 `defRPr`。
- **run 属性**（`<a:rPr>`）把大小和样式放在属性上：`sz` 的单位是百分之一磅（`2400` 是 24pt），还有 `b="1"`、`i="1"` 和 `u="sng"`。子元素里填充在前，字体随后写成 `<a:latin typeface="…"/>`，不要写成属性。中文再加 `<a:ea typeface="Microsoft YaHei"/>`，不要只写 latin。
- **单位。** 位置和尺寸用 EMU：每英寸 914400，每磅 12700。
- **形状 id**（`<p:cNvPr id>`）在一张幻灯片内唯一。
- **文字**是 UTF-8，任何字符都直接写。只转义 `&`、`<` 和 `>`。

## 一个文本形状

```xml
<p:sp>
  <p:nvSpPr>
    <p:cNvPr id="10" name="Callout"/>
    <p:cNvSpPr txBox="1"/>
    <p:nvPr/>
  </p:nvSpPr>
  <p:spPr>
    <a:xfrm><a:off x="914400" y="1371600"/><a:ext cx="4572000" cy="914400"/></a:xfrm>
    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
  </p:spPr>
  <p:txBody>
    <a:bodyPr wrap="square"/>
    <a:lstStyle/>
    <a:p>
      <a:pPr marL="285750" indent="-285750">
        <a:spcBef><a:spcPts val="600"/></a:spcBef>
        <a:buFont typeface="Arial"/>
        <a:buChar char="•"/>
      </a:pPr>
      <a:r>
        <a:rPr lang="en-US" sz="1800" b="1">
          <a:solidFill><a:srgbClr val="C0392B"/></a:solidFill>
          <a:latin typeface="Georgia"/>
        </a:rPr>
        <a:t>Churn fell to 4%</a:t>
      </a:r>
    </a:p>
  </p:txBody>
</p:sp>
```

中文 run 在 `<a:latin>` 后加东亚字体，并留出更宽的 `<a:ext>`，例如：

```xml
<a:rPr lang="zh-CN" sz="1800">
  <a:latin typeface="Arial"/>
  <a:ea typeface="Microsoft YaHei"/>
</a:rPr>
<a:t>流失率降到 4%</a:t>
```

## 坑

- **隐藏幻灯片**在 `<p:sld>` 上带 `show="0"`。它们仍然算在幻灯片顺序里。
- **备注属于一张幻灯片。** 两张幻灯片指向同一张备注会弄坏文件。
- **主题色**（`<a:schemeClr val="accent1"/>`）跟着主题走，`<a:srgbClr>` 是固定的。编辑模板时保留它的主题色，文稿才能跟着主题一起换风格。
