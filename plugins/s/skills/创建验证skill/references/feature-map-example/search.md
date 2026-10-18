# 搜索笔记

“搜索”让用户可以按标题或正文文字找到笔记，查看一条匹配的笔记，并区分“没有匹配”和“搜索不可用”。

## Sub-features

- `search-open` 从浏览器每个受支持的入口打开搜索。
- `search-match` 返回标题和正文的匹配，不改变笔记数据。
- `search-open-result` 在笔记编辑器里打开一个结果。
- `search-empty` 对没有匹配的查询显示完整的空结果状态。
- `search-clear` 清除查询，恢复“最近的笔记”视图。
- `search-cli` 从终端返回同样的匹配笔记。

## How to get to it (user POV)

- 在浏览器工具栏里选择 `Search`（搜索）按钮。
- 焦点不在可编辑字段里时，在浏览器里按 `/`。
- 在终端里运行 `notes search <query>`。

## Driving it with control-notes

Preconditions:

- Notes 在 `http://127.0.0.1:4173` 运行正常。
- 用完即扔的数据目录里有 `Quarterly plan`，正文文字是 `Draft budget`（预算草稿）。
- `control-notes doctor` 报告了预期的 URL 和数据目录。

- **工具栏入口。** 选择 `Search` 按钮。运行 `control-notes browser click --role button --name "Search"`。出现一个名为 `Search notes` 的对话框，焦点在它的搜索框里。
- **键盘入口。** 关掉对话框，让页面获得焦点，然后按 `/`。运行 `control-notes browser press --key "/"`。出现同一个对话框，页面没有插入斜杠。
- **标题匹配。** 输入 `quarterly`。运行 `control-notes browser fill --role searchbox --name "Search notes" --value "quarterly"`。`Search results` 列表里有 `Quarterly plan`，没有 `Grocery list`。
- **正文匹配。** 把查询换成 `budget`。运行 `control-notes browser fill --role searchbox --name "Search notes" --value "budget"`。结果 `Quarterly plan` 仍然可见，并带有一段正文匹配的摘录。
- **打开结果。** 选择 `Quarterly plan`。运行 `control-notes browser click --role link --name "Quarterly plan"`。对话框关闭，编辑器标题显示为 `Quarterly plan`。
- **空结果状态。** 重新打开搜索，输入 `volcano`。运行 `control-notes browser fill --role searchbox --name "Search notes" --value "volcano"`。搜索完成后出现一个名为 `No matching notes` 的状态提示。
- **清除查询。** 选择 `Clear search`。运行 `control-notes browser click --role button --name "Clear search"`。搜索框变空，`Recent notes` 区域取代了结果列表。
- **命令行匹配。** 从终端搜索。运行 `control-notes cli -- notes search "quarterly" --format json`。退出码为 `0`，标准输出里有一个标题为 `Quarterly plan` 的对象。
- **命令行未匹配。** 搜索一个不存在的值。运行 `control-notes cli -- notes search "volcano" --format json`。退出码为 `0`，标准输出是 `[]`。
- **证明。** 采集有结果时的状态。运行 `control-notes browser snapshot --aria --path artifacts/search/results.aria.txt` 和 `control-notes browser screenshot --path artifacts/search/results.png`。两个产物都能看出是 Notes、查询内容和 `Quarterly plan`。

## Gotchas

- 编辑器或搜索框有焦点时按 `/`，会插入文字，而不是打开搜索。
- 结果会在短暂的防抖延迟之后更新。等待结果列表或空结果提示出现，而不是固定地等一段时间。
- 除非用户打开 `Include archived`（包括已归档），否则已归档的笔记不会出现在结果里。
- 命令行默认输出给人看的格式。要做稳定的断言，用 `--format json`。
- 打开一个结果会改变浏览器状态。证明另一个查询之前，先重新打开搜索。
