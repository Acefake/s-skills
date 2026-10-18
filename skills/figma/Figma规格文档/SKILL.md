---
name: Figma规格文档
description: "新建、阅读、编辑、审查或评论 Figma spec（Figma 里的规格文档）时，必须用这个 skill。处理 PRD（产品需求文档）、brief（简报）、RFC（方案征求意见稿）或任何文档时都要先读它，不管是独立的 Figma spec，还是嵌在 Figma Design 或 FigJam 文件里的 Figma spec。"
disable-model-invocation: false
---

> 翻译自 Figma 官方仓库 https://github.com/figma/mcp-server-guide （skills/figma-spec，commit f278942，对应 Cursor 插件编号 657）的 `figma-spec` skill，原作者 Figma，许可证：未注明许可证（仓库里没有找到 LICENSE 文件），仅供自用。
> 说明：`figma.spec.*` 这类 API 名、字段名和代码块保持原样，代码里的英文注释在代码块后面加了中文解释。
> 英文名备份：s-figma-spec

# 使用 Figma spec

在使用任何 `figma.spec.*` API 之前，必须先调用 `whoami`，并确认目标文件所属的套餐（新文件则是目标套餐）有 `specs_enabled: true`。`whoami` 不会告诉你某个文件属于哪个套餐。如果套餐不清楚，必须问用户；绝不能从文件 key 或其他套餐的权限去推测。如果那个套餐的 `specs_enabled` 是 false 或者没有这个字段，就说明 Specs 功能不可用，然后停止流程。

一个原生的 Figma spec，就是放在 `SPEC_BLOCK` 节点下的 GitHub 风格 Markdown（GFM）。一个独立的 Figma spec 只是一份 spec；一个 FigJam 或 Design 文件里可以嵌入好几份 spec。

## 找到并选定 Figma spec

如果提供的网址里有 `node-id`，就用 `figma.getNodeByIdAsync` 找到它，并要求 `type === "SPEC_BLOCK"` 且 `specBlockType === "DOCUMENT"`。否则，用 `findAllWithCriteria({ types: ['SPEC_BLOCK'] })` 搜索当前页面，筛出 `specBlockType === "DOCUMENT"` 的（需要时用 `figma.spec.getContent` 查看内容），直到找到目标。如果不在当前页面，就用 `page.loadAsync()` 一次加载一个其他页面，重复查找，找到目标就停。

每次调用内容相关的方法，都要传入找到的根节点 ID。只有在确定文件里正好只有一份 Figma spec 时，才可以省略 `specNodeId`；否则省略会报错。绝不能退而求其次去编辑画布上普通的文字节点。

## 在画布上新建 Figma spec

```js
// Creates an embedded Figma spec on a Design or FigJam canvas (not a standalone Figma spec file).
const { specNodeId } = await figma.spec.createOnCanvasAsync({
  title: 'Untitled spec',
  content: '# Title\n\nA paragraph.\n',
})

const specNode = await figma.getNodeByIdAsync(specNodeId)
if (!specNode) throw new Error('The created Figma spec could not be resolved')

const after = await figma.spec.getContent({ specNodeId })
if (!after.markdown.includes('A paragraph.')) {
  throw new Error('The new Figma spec content was not applied')
}
```

（代码注释意思：在 Design 或 FigJam 画布上新建一份嵌入式 Figma spec（不是独立的 Figma spec 文件）。）

一定要传一个非空的 `title` 和一个 `content` 字符串（可以是 `''`）。`title` 是根节点的名字；想要的 `# H1` 一级标题要写在 `content` 里。

## 内容相关的方法

```js
// READ — returns specNodeId, markdown, title, etc.
// The body is `markdown`, not `content`.
const before = await figma.spec.getContent({ specNodeId: chosenSpec.id })
const page = await figma.spec.getContent({
  specNodeId: before.specNodeId,
  offset: 100,
  maxLines: 50,
})

// REPLACE — clears + recreates the document; use only for an empty first draft.
await figma.spec.setContent({
  specNodeId: before.specNodeId,
  content: '# Title\n\nA paragraph.\n',
})

// EDIT — find/replace; each oldText must match exactly once.
await figma.spec.editContent({
  specNodeId: before.specNodeId,
  edits: [{ oldText: 'First paragraph.', newText: 'Edited first paragraph.' }],
})

const after = await figma.spec.getContent({ specNodeId: before.specNodeId })
if (!after.markdown.includes('Edited first paragraph.')) {
  throw new Error('The targeted Figma spec edit was not applied')
}
```

（代码注释意思：READ 读取——返回 specNodeId、markdown、title 等，正文在 `markdown` 里，不在 `content` 里；REPLACE 替换——清空并重建整份文档，只用于空白的初稿；EDIT 编辑——查找替换，每个 oldText 必须正好匹配一次。）

- 编辑之前和确认写入之后，都用同一个 `specNodeId` 调用 **`getContent`**；不要靠截图。
- 默认使用对多人同时编辑安全、只改一小处的 **`editContent`**。
- 只有在空白初稿，或者明确要求替换整份文档时，才使用会破坏原内容的 **`setContent`**。

## 关键规则

1. **`editContent` 要求正好匹配一次。** `oldText` 匹配零次或多次都会失败，并且不做任何修改。加上前后文让它变得唯一。
2. **Markdown 以普通字符串传入。** 绝不要用 `Buffer`/base64 编码它，也不要用 `atob()` 解码。base64 只用于 Markdown 里图片的 data URL。
3. **Markdown 和节点遍历分开处理。** `figma.spec.*` 负责内容；节点遍历只能看到文档根节点和嵌入画布的分支。
4. **保留评论标记。** 围绕同一段文字、相互交叠的 `[comment:<uuid>]…[/comment:<uuid>]` 标记对要原样保留，否则评论串可能脱离或消失。拿不准时，把带标记的那一段原样复制，在它周围编辑。
5. **使用别人也能打开的引用。** 共享的 Figma spec 必须用 GitHub 永久链接这类链接，绝不能用只在本机有效的路径或 `localhost` 网址。

## 格式

- 标题块始终放在最前面，格式是 H1，即使文字为空也一样。绝不要删除它，也不要在它前面插入别的块。
- 表格的表头行优先用粗体。
- 下划线用 `<ins>`，包括组合格式：`<ins>**bold and underlined**</ins>`。不要用 `<u>`，它只在导入 HTML 时有效。

## 图片

图片在 `setContent` 或 `editContent` 里用 GFM 的图片语法：

- `![alt](data:image/png;base64,...)` 会把字节内容解码并上传。
- `![alt](https://host/img.png)` 由服务器去抓取；不允许的网站会被拒绝。

`getContent` 输出的图片网址格式是 `https://<host>/spec/<fileKey>/image/<sha>?w=<width>&h=<height>`。

## 评论

挂在具体文字上的评论串用 `figma.spec.comments.*`。当你对某处修改拿不准时，优先留评论，而不是不声不响地改掉。

```js
const comment = await figma.spec.comments.create({
  specNodeId: before.specNodeId,
  anchorText: 'the exact rendered text to anchor to', // MUST appear exactly once
  contextText: 'a longer unique substring containing anchorText', // optional; disambiguates repeats
  message: 'Comment body (markdown).',
})

const { root, replies, hasMore } = await figma.spec.comments.getThread({ uuid: comment.uuid })
await figma.spec.comments.reply({ uuid: comment.uuid, message: 'A reply.' })
```

（代码注释意思：anchorText 必须正好出现一次；contextText 可选，用来区分重复的文字。）

- `anchorText` 在渲染后的 Figma spec 里必须正好匹配一次。用一段包含它、更长的 `contextText` 来区分重复的文字。
- `getThread` 和 `reply` 需要根评论的 UUID，它显示在 `[comment:<uuid>]` 标记里；绝不要把回复的 UUID 传给 `reply`。
