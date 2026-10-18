---
name: FigJam白板操作
description: "这个 skill 帮助 AI 助手在 FigJam（Figma 的在线白板）里使用 Figma 的 use_figma MCP 工具。可以和 Figma插件基础 一起用，后者提供使用 use_figma 工具的基础知识。"
disable-model-invocation: false
---

> 翻译自 Figma 官方仓库 https://github.com/figma/mcp-server-guide （skills/figma-use-figjam，commit f278942，对应 Cursor 插件编号 657）的 `figma-use-figjam` skill，原作者 Figma，许可证：未注明许可证（仓库里没有找到 LICENSE 文件），仅供自用。
> 说明：参考文件 `references/` 一共约 142 KB，太大，保留英文原文。下面要求在 `skillNames` 里写的是原名 `figma-use-figjam`（给 Figma 做使用统计用），保持原样。链接里的 `../figma-use/...` 已经改成 `../Figma插件基础/...`，正文里提到的其他 skill 也换成了中文名。
> 英文名备份：s-figma-use-figjam

# use_figma —— 用于 FigJam 的 Figma 插件 API skill

这个 skill 包含 `use_figma` MCP 工具在 FigJam 里的专门知识。[Figma插件基础](../Figma插件基础/SKILL.md) 这个 skill 提供通过 MCP 运行插件 API 的基础知识，以及完整的 Figma 插件 API，可用于这里没讲到的更高级的用法。

**在 FigJam 里调用 `use_figma` 时，一定要在用逗号分隔的 `skillNames` 参数里写上 `figma-use-figjam`。如果这个 skill 是通过 MCP resource 加载的，名字前面必须加 `resource:`（例如 `resource:figma-use-figjam`）。** 这是一个用来统计 skill 使用情况的日志参数——它不影响执行。

> **FigJam 的网址是 `figma.com/board/...`。** 不要在 FigJam 里调用 `figma.createPage()`——它会报错 `TypeError: figma.createPage no such property 'createPage' on the figma global object`。`createPage()` 只是 Design 文件（`figma.com/design/...`）的 API。FigJam 文件只有一个隐含的页面；改用 section（分区）来组织内容（见 [create-section](references/create-section.md)）。

## 查看 FigJam 文件

**`get_figjam` 是查看 FigJam 文件的工具。** 它以 XML 形式返回完整的节点树，包括页面、分区、便利贴、连接线和其他节点的 ID，后续调用 `use_figma` 时需要引用它们。

- **先用 `get_figjam`**，再去写任何需要引用现有节点（页面 ID、分区 ID 等）的 `use_figma` 代码。不要试图通过运行一段查看脚本来找 ID——`use_figma` 里 `console.log` 的输出**不会返回给 AI 助手**（见 [Figma插件基础 关键规则 #4](../Figma插件基础/SKILL.md)）。只有 `return` 的值会返回。
- **`get_metadata` 在 FigJam 文件上不能用**——它只适用于设计模式，会立刻失败，报 "unsupported for FigJam files"。
- **`get_screenshot` 需要一个有效的 `nodeId`**——传空的 nodeId 会返回 "invalid nodeId" 错误。先从 `get_figjam` 拿到 ID。
- 如果之前某次 `use_figma` 调用忘了 `return` 某个 ID，现在又需要它，就调用 `get_figjam`，而不是重新跑查看脚本。

## 高效加载参考文档

只加载任务需要的参考文档——但如果确实需要加载好几个，**在同一批并行工具调用里一次读完**，不要分好几轮一个个读。对于典型的“做一块白板”任务，这意味着一条消息里同时读 `plan-board-content` 加上你要用到的 3-4 个具体节点类型的参考文档。

## 延迟加载的工具——一次性加载参数结构

Figma 的 MCP 工具（`use_figma`、`get_figjam`、`get_screenshot`、`get_metadata`、`create_new_file`、`whoami`）经常以“延迟加载工具”的形式出现，需要先用 `ToolSearch` 加载它们的参数结构才能调用。**用 `select:` 语法，在一次 `ToolSearch` 调用里加载所有参数结构**，而不是每个工具调用一次：

```
ToolSearch query="select:use_figma,get_figjam,get_screenshot,get_metadata,create_new_file"
```

六次依次调用 `ToolSearch`，就是在真正干活之前来回六趟。一次批量调用只来回一趟。

## 修改文字——标准做法

FigJam 里每一次修改文字（便利贴/形状/标签/表格单元格/连接线上的文字，以及单独的文字节点），都和 Design 文件一样按同一个做法：加载字体 → `await` → 修改 → 返回受影响的 ID。跳过加载会报错 `Cannot write to node with unloaded font "<family> <style>"`。见 [Figma插件基础 → gotchas.md → 标准的文字编辑做法](../Figma插件基础/references/gotchas.md#canonical-text-edit-recipe-font-load--await--mutate--return-ids)。FigJam 特有的注意点：各子图层的默认字体不一样（便利贴 → `Inter Medium`，形状 → `Inter Medium`，连接线 → 设置之前是无效的），所以一定要从 `node.text.fontName` 加载，而不是写死 `{ family: 'Inter', style: 'Regular' }`。

## 往 FigJam 白板里加图片

**`upload_assets` 是往 FigJam 文件里加图片唯一支持的方式。** 用 FigJam 的 `fileKey` 调用 `upload_assets`；工具会返回一次性的上传网址，你把原始图片字节 POST 上去，图片就会自动提交并放好。传 `nodeIds`（每个上传对应一项）可以把上传的图片作为填充挂到现有的 FigJam 节点上；不传 `nodeIds`，图片就作为新图层放到白板上。

完整的请求/返回结构，见 [Figma插件基础 → api-reference.md → Images](../Figma插件基础/references/api-reference.md#images)。

## 参考文档

- [plan-board-content](references/plan-board-content.md) - 任何关于白板内容的请求都要读它——白板模板、复盘会（retro）、头脑风暴、破冰、会议白板、框架搭建
  - 讲的是怎样规划生成的白板内容，包括按顺序的大纲、分区、意图和分层级的文字
  - 具体的 API 细节交给其他参考文档
- [create-section](references/create-section.md) —— 新建和配置 FigJam 分区（尺寸、命名、颜色、内容可见性、整理节点、分栏布局）
- [create-sticky](references/create-sticky.md) —— 新建和配置 FigJam 便利贴（颜色、尺寸、文字、作者是否显示、批量新建）
- [create-connector](references/create-connector.md) —— 新建和配置 FigJam 连接线（端点、箭头、线型、标签、颜色、连接图表）
- [create-text](references/create-text.md) —— 新建和配置 FigJam 文字节点（加载字体、预设字体和颜色、尺寸、列表、思维导图操作）
- [position-figjam-nodes](references/position-figjam-nodes.md) —— 在画布上摆放节点、调整尺寸、更换父节点（包括放进分区里）
- [create-shape-with-text](references/create-shape-with-text.md) —— 新建和配置带文字的 FigJam 形状（形状类型、颜色预设、按文字调整大小、图表布局）
- [create-code-block](references/create-code-block.md) —— 新建和配置 FigJam 代码块节点（语言、语法高亮、摆放、放进分区）
- [create-table](references/create-table.md) —— 新建和配置 FigJam 表格（行、列、单元格文字、颜色预设、调整大小）
- [edit-text](references/edit-text.md) —— 编辑现有的文字节点（加载字体、带样式的文字范围、查找替换、FigJam 默认的 Charcoal 炭灰色）
- [create-label](references/create-label.md) —— 新建和配置 FigJam 标签节点（带数字/字母的小圆形标注、序号、摆放）
- [batch-modify](references/batch-modify.md) —— 一次修改很多现有节点的做法（批量改样式、重新摆放、更新属性）
- [figjam-colors](references/figjam-colors.md) —— 每种节点类型（便利贴、分区、连接线、形状、标签）的 FigJam 标准调色板，以及 `hex/255` 写法规则和 `h()` 辅助函数
