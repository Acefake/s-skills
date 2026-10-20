# 新建笔记

“新建笔记”让用户可以从浏览器或命令行保存一条带标题的笔记，取消一份没写完的草稿，并从另一个面向用户的视图确认保存好的笔记。

## Sub-features

- `create-open` 从浏览器的每个入口打开一个空白编辑器。
- `create-save` 持久保存标题和正文。
- `create-cancel` 丢弃一份没写完的浏览器草稿。
- `create-cli` 从终端创建同样形状的笔记。

## How to get to it (user POV)

- 在浏览器工具栏里选择 `New note`（新建笔记）按钮。
- 焦点不在可编辑字段里时，在浏览器里按 `n`。
- 在终端里运行 `notes create --title <title> --body <body>`。

## Driving it with control-notes

Preconditions:

- Notes 在 `http://127.0.0.1:4173` 运行正常。
- 没有标题为 `Release checklist`（发布检查清单）的笔记。
- `control-notes doctor` 报告了预期的 URL 和用完即扔的数据目录。

- **打开编辑器。** 选择 `New note`。运行 `control-notes browser click --role button --name "New note"`。出现一个名为 `Note editor` 的表单，焦点在 `Title` 文本框里。
- **输入内容。** 输入标题和正文。运行 `control-notes browser fill --role textbox --name "Title" --value "Release checklist"` 和 `control-notes browser fill --role textbox --name "Body" --value "Tag and publish"`。`Save note` 按钮变为可用。
- **保存笔记。** 选择 `Save note`。运行 `control-notes browser click --role button --name "Save note"`。出现一个名为 `Note saved` 的状态提示，标题显示为 `Release checklist`。
- **确认已持久保存。** 回到笔记列表，重新打开这条笔记。运行 `control-notes browser click --role link --name "All notes"` 和 `control-notes browser click --role link --name "Release checklist"`。编辑器显示保存过的两个值。
- **取消草稿。** 打开一条新笔记，输入 `Discard me`，然后选择 `Cancel`。运行 `control-notes browser click --role button --name "New note"`、`control-notes browser fill --role textbox --name "Title" --value "Discard me"` 和 `control-notes browser click --role button --name "Cancel"`。回到笔记列表，列表里没有 `Discard me` 链接。
- **命令行入口。** 创建第二条笔记。运行 `control-notes cli -- notes create --title "CLI note" --body "Created from terminal" --format json`。退出码为 `0`，标准输出里有新笔记的 ID 和标题。
- **证明。** 从 `All notes` 重新打开两条保存好的笔记。运行 `control-notes browser snapshot --aria --path artifacts/create-note/list.aria.txt` 和 `control-notes browser screenshot --path artifacts/create-note/list.png`。产物里显示 `Release checklist` 和 `CLI note`。

## Gotchas

- 文本框有焦点时按 `n`，会输入这个字符，而不是打开一个新编辑器。
- 保存时标题会被去掉首尾空格。断言渲染出来的标题，而不是草稿输入框里的值。
- 只有一个保存状态提示，不足以证明。要从列表重新打开笔记。
- 清理测试数据时删掉 `Release checklist` 和 `CLI note`，但保留它们的证明产物。
