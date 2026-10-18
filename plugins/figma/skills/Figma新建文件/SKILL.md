---
name: Figma新建文件
description: "当用户想新建一个 Figma Design（设计）、FigJam（白板）或 Slides（幻灯片）文件时，一定要用这个 skill。每次调用 `create_new_file` 工具之前，都必须先调用这个 skill。"
disable-model-invocation: false
---

> 翻译自 Figma 官方仓库 https://github.com/figma/mcp-server-guide （skills/figma-create-new-file，commit f278942，对应 Cursor 插件编号 657）的 `figma-create-new-file` skill，原作者 Figma，许可证：未注明许可证（仓库里没有找到 LICENSE 文件），仅供自用。
> 说明：MCP 是让 AI 调用外部工具的一种协议。工具名（如 `create_new_file`、`whoami`、`use_figma`）、参数名和代码块保持原样。
> 英文名备份：s-figma-create-new-file

# 在 Figma 里新建文件

用 `create_new_file` 这个 MCP 工具新建 Figma Design、FigJam 或 Slides 文件的步骤。

## 第 1 步：确定 `planKey` 和 `editorType`

如果用户为这个任务提供或选好了 `planKey`，就用它。否则，调用 `whoami`，查看返回的套餐（plan）列表。

- 没有套餐：告诉用户没法新建文件。
- 只有一个套餐：用它的 `key` 作为 `planKey`。
- 有多个套餐：把可用的套餐列给用户看，请用户选一个，然后用那个套餐的 `key` 作为 `planKey`。

根据用户要的文件类型推断 `editorType`：从工具公布的输入枚举值里选。如果不清楚，请用户说明文件类型。

## 第 2 步：调用 create_new_file

调用 `create_new_file` 工具，带上三个必填参数：

- `fileName`：必填。如果用户没给名字，自己起一个简短的。
- `planKey`：必填。用第 1 步确定的 `planKey`。
- `editorType`：必填。用第 1 步选好的 `editorType`。
- `projectId`：可选。想把文件建在某个特定项目里时才设置。

```json
{
  "fileName": "Quarterly planning",
  "planKey": "team::1234567890",
  "editorType": "design"
}
```

- 后续调用其他工具（比如 `use_figma`）时，用 `create_new_file` 工具返回结果里的 `file_key`。

## 第 3 步：（仅限 Slides）处理空网格

新建的 Slides 文件里一张幻灯片都没有：`figma.getSlideGrid()` 返回 `[]`。在从幻灯片读取属性（比如主题 token）之前，先调用 `figma.createSlide()`，或者处理好“为空”的情况。第一次调用 `createSlide()` 会自动建好第 0 行并插入这张幻灯片。
