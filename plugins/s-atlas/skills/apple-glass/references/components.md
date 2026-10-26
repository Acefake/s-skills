# 组件清单

影盒的组件都在 `src/renderer/src/components/ui/`（Vue 3 `<script setup>`），从 `@/components/ui` 统一导出。别的项目照这份清单建最小一套，React 也按同样的名字和职责来。

## 按钮与点击目标

| 组件 | 用途与要点 |
|---|---|
| `UiButton` | 文字按钮，可带图标。`variant`：`primary`（白底黑字，一区最多一个）、`secondary`（灰底，默认）、`glass`（玻璃底，浮在画面或浮层上）、`plain`、`danger`。`size` sm/md/lg 对应 28/36/44。`pressed` 用于切换按钮。`loading` 显示转圈，保持可聚焦。 |
| `UiIconButton` | 只有图标的按钮，`label` 必填（读屏 + tooltip）。有 `overlay` 变体给画面上的圆钮。优先用它而不是文字按钮。 |
| `UiMenuButton` | 工具条上的「更多」菜单。菜单底色 `--menu-bg`，比玻璃更不透明，压在海报上也读得清。 |
| `UiPressable` | 无样式按钮，给图片、卡片这类点击目标。内容没有文字时传 `label`。 |
| `UiNavItem` | 侧栏、设置、手机底栏的导航项。`collapsed` 隐藏文字改成 tooltip；`layout="stack"` 给手机底栏；`current` 取 `page` / `pressed` / `none`。 |
| `UiListRow` | 可点击的多行列表行，`role` / `aria-*` 透传（比如 `menuitemradio`）。 |
| `UiSegmented` | 分段切换（标签页），滑块用 `--control-bg`。 |
| `UiChip` | 小灰胶囊（演员、标签）。`size="md"` 加 `count` 是页面筛选胶囊。删除按钮另放一个 `UiIconButton`，不塞进胶囊里。 |

## 表单

`UiInput`（`size` sm/md，`variant` default/filled，`icon` 或 `#leading`，`clearable` + `@clear`，`invalid`）、`UiTextarea`（`autosize`）、`UiSelect`（`options` 或 `<option>` 插槽）、`UiSwitch`、`UiCheckbox`、`UiRadio`。

- 都支持 `v-model`，也支持 `:value` / `:checked` 加原生事件。
- `UiInput` / `UiSelect` 把 `class` 放在外壳上，其余属性和监听放在原生元素上，并暴露 `focus()`。
- 外壳共用 `.ui-field`：36 高，`--radius-md`，1px `--border-default`，聚焦时边框变 `--accent` 并加 `--focus-ring`；校验失败用 `--danger` 和 `--focus-ring-danger`。样式见 `materials.css`。

## 媒体

| 组件 | 用途与要点 |
|---|---|
| `UiPosterCard` + `.ui-poster-grid` | 海报卡和海报网格。圆角 `--radius-card`（18）。悬停时封面上移 4px 并放大 1.02，操作按钮淡入；`hover: none` 的设备上一直显示。`thumb` 走缩略图协议，加载失败回落原图。`preview` 接悬停预览。网格是 `repeat(auto-fill, minmax(var(--poster-min-width), 1fr))`，横版加 `.is-landscape`（最小 260）。 |
| `UiEpisodeCard` | 剧集或预告横卡：剧照铺满，下半 `.yb-pblur` 渐进模糊加暗化，标题、副标题、进度条、底部说明压在上面，右下角「更多」。 |
| `UiMediaRow` | 影片结果行：海报、标题、元信息、规格标签、★评分、备注，可带进度。`dense` 给搜索行。AI 助手的结果卡和统一搜索的结果行都用它。 |
| `UiShelf` | 横向货架：`UiSectionHeader` 加一排可横滚的卡片，溢出时右上角出左右滚动键；也可切成网格。 |
| `UiSectionHeader` | 分区标题：粗体大字，`more` 时后面跟灰色 ›，点了发 `more`。右侧插槽放计数、滚动键。 |
| `UiSpecBadge` | 规格标签（4K / HDR10 / DOLBY VISION / ATMOS / CC / 中字 / 16+）。映射只有一处 `spec-badge.ts`：`videoRangeSpec` 管探测出的动态范围，`releaseSpecs` 管发布名和文件名，`mediaSpecs` 管片库条目；先信探测，再看文件名。海报墙格子不建组件实例时，直接写 `.yb-spec` 类。 |
| `UiVirtualGrid` | 虚拟网格：`class` 写网格或列表类，`:items`，`:item-key`，默认插槽 `{ item }`，列表用 `tag="ul"`。列数从 `grid-template-columns` 读，要求行高一致，容器的上下内边距归它管。 |

## 反馈

- `UiIcon`：`name`、`size`（sm/md/lg = 14/16/18）、`filled`。块级显示，在按钮里居中。图标路径由脚本从 Phosphor 生成，不手改。
- `v-tooltip`：全局唯一的浮层，`--control-bg` 底，`--z-max`。
- `toast.success / error / warning / info(text)` 返回关闭函数；`toast.loading(text)` 要手动关。
- `await confirmDialog({ title, content, okText, danger, onOk })` 返回 `boolean`；`onOk` 抛错时对话框不关，并显示错误。
- `UiLoadingDots`（后台工作，放在内容后面）、`UiSkeleton`（首屏骨架，减少动态效果时不动）。

## 写新组件时

1. 放进组件库目录，文件名 `Ui<名字>.vue`，从 `index.ts` 导出。
2. 顶部写中文 doc 注释：它是什么、什么时候用、有哪些变体。
3. 状态和修饰选择器包 `:where()`。
4. 只引用令牌；需要玻璃就加 `.yb-glass` 类，不要自己写模糊。
5. 可交互的组件给出 `:focus-visible` 焦点环（图片目标用 `--focus-ring-offset`）。
