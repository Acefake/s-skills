# 层级与树渲染器

将 `diagram_type: "tree"` JSON 文件渲染为标准 Archify HTML 模板。

```bash
node archify/renderers/tree/render-tree.mjs input.tree.json output.html
```

渲染器使用内置的独立校验器，按 `archify/schemas/tree.schema.json` 校验
输入。若省略 `output.html`，它使用
`meta.output`，否则回退到 `tree.html`。`--layout-json` 打印已放置的
节点和连线，而不是写出 HTML。

## 输入

```json
{
  "schema_version": 1,
  "diagram_type": "tree",
  "meta": { "title": "Payment platform capabilities" },
  "nodes": [
    { "id": "platform", "label": "Payment platform" },
    { "id": "orders", "label": "Orders", "parent": "platform" }
  ]
}
```

节点有 `id`、`label`，以及可选的 `parent`、`sublabel`、`collapsed` 和
`sources`。子节点按声明顺序读取。连线只表示包含关系；
第一版不支持跨分支关系。

## 结构检查

层级恰好就是作者声明的样子；不会附加或推断任何东西。

| 代码 | 拒绝的输入 |
| --- | --- |
| `tree/missing-parent` | `parent` 指向未声明的节点 |
| `tree/root-count` | 没有 `parent` 的节点为零个或多于一个 |
| `tree/cycle` | 父链形成环；环下方的每个节点都不可达，因此这一条诊断覆盖它们全部 |
| `tree/duplicate-id` | 某个 id 被声明了两次 |

## 布局

每一代共享一条带：`layout.direction: "down"`（默认）时为一行，
`"right"` 时为一列。沿另一轴，每棵子树占据一段
连续区间，因此分支宽度和深度不等时也绝不重叠。父节点
居中于其第一个和最后一个子节点之上（若某个中间子节点距该中点
只有几个像素，则恰好对齐该子节点，使主干绝不出现折弯；绘制连线时也会把取整后在 2px 内对齐的主干吸附为直线）；向右布局时，
节点在其所在列内左对齐。

向下布局时，连续三个或更多叶子兄弟节点会在其父节点下
叠放为缩进列表，共享同一宽度并沿一条脊线连接，
而不是在行中展开。这使仓库这类真实层级在一屏的尺度下
保持可读；更短的连续叶子和所有分支保持行布局。叶子是安静的卡片；根和分支承载色调。

节点按其标签确定尺寸，介于 `layout.nodeW`（140）与 `layout.nodeMaxW`
（向下 220、向右 200）之间。标签和副标签在单词之间换行（CJK 可在任意
字符处换行），取保持相同行数的最窄宽度，使
长标签成为匀称的框；单个单词可在被拆分前把节点加宽到 1.5 × `nodeMaxW`，
因此不会截断任何内容。`gapX`/`gapY` 设置兄弟间距和代际
间距。

自动画布声明 `data-reader-fit="intrinsic-height"` 和 7.5px 的
阅读文字下限，因此较深的向右树会滚动，而不是缩小。

## 展开与折叠

每个有子节点的节点在其出向一侧有一个开关，它是节点之后一个独立的
可聚焦按钮，带有 `aria-expanded` 和本地化标签，
说明它隐藏了多少个后代。查看器模块
`viewer/tree-branches.js` 负责该状态：

- 折叠只隐藏后代及其连线。位置为完整的树
  计算一次，因此可见内容都不会移动，读者也不会丢失
  当前位置。折叠的节点显示为叠放卡片及其隐藏数量。
- 键盘：在开关上按 Enter/Space；ArrowLeft 折叠、ArrowRight 展开
  当前聚焦的分支节点。焦点保持在所使用的控件上。
- 只要有任何分支被折叠，左上角就会出现 **Expand all**，它
  恢复作者声明的层级。
- 通过 Finder、Node Outline、引导视图或
  分享链接选中被隐藏的节点时，会先展开其祖先节点。
- `collapsed: true` 只设置查看器的初始状态。SVG 始终包含
  完整的树。

导出范围是明确的：无论屏幕上折叠了什么，每次 SVG/PNG/JPEG/WebP 导出都是完整的树。
Export Cleanup 会从克隆中移除折叠状态，
并保持实时视图不变。

## 实测规模

`examples/archify-repository.tree.json`（31 个节点、深度 4、不平衡、四个
叠放列表）渲染约需 0.2s，并通过 showcase 关卡；
切换一次开关在几毫秒内即可完成 DOM 更新。
