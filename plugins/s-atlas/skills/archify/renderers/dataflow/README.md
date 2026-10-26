# 数据流渲染器

将 `diagram_type: "dataflow"` 的 JSON 文件渲染为标准 Archify HTML
模板。

```bash
node archify/renderers/dataflow/render-dataflow.mjs input.dataflow.json output.html
```

渲染器使用内置的独立校验器，按 `archify/schemas/dataflow.schema.json`
校验输入。无需安装任何依赖。

若省略 `output.html`，渲染器使用 JSON 文件中必填的 `meta.output`
值。

## 输入

数据流 JSON 文件必须设置：

```json
{
  "schema_version": 1,
  "diagram_type": "dataflow",
  "meta": {
    "title": "Product Analytics Data Flow",
    "output": "product-analytics-dataflow.html",
    "viewBox": [940, 720]
  },
  "stages": [],
  "nodes": [],
  "flows": [],
  "cards": []
}
```

完整的示例位于
`archify/examples/product-analytics.dataflow.json`。

Schema 位于：

```text
archify/schemas/dataflow.schema.json
```

## 图例

默认的视觉图例从 `flows[].variant` 推导种类（省略
`variant` 即表示 `default`），并且只有在存在 database 节点时才添加 `database`。
支持的 `meta.legend.entries` 键按稳定顺序为 `emphasis`、
`security`、`dashed`、`database` 和 `default`。流变体仍然
仅具视觉作用，因为在这一部分中 Archify 没有经过编译的连线种类事实。
出现的 `database` 条目则不同：它来自确切的
`nodes[].type: "database"` 事实，因此会发布正常的 Semantic Legend
计数、可访问名称和键盘交互。在没有 database 节点时强制让 `database` 可见，
它仍只具视觉作用。

## 布局预算

| 常量 | 值 |
|----------|-------|
| viewBox | 省略时宽度会容纳所有阶段框和节点（包括作者编写的宽度），右侧留白 24px，最小 480px（五个默认宽度的阶段需要 1068）；高度默认 720，在全自动 showcase 中适配内容；schema 最小值 `[360, 360]` |
| 阶段（2–5） | 中心位于 x = 100 + 阶段×215；阶段带宽 168，标题位于 y 46 |
| 行顶部（`row` 0–4） | y = 128, 242, 356, 470, 584（加上 `yOffset`） |
| 默认节点 | 112×58 |
| 节点区域 | x 在 `[24, width − 24]` 内；y 在 `[104, height − 74 − node height]` 内 |
| 节点间距 | 任意两个节点之间 ≥10px（跨阶段和跨行检查） |
| 流长度 | 端点之间 ≥34px |
| 图例行 | y = 高度 − 36 |

流的路由预设：`straight`、`vertical-channel`、`bottom-channel`、
`top-channel`、显式 `via` 点，或默认的 `auto`（中点肘形折线）。

作者编写的 `meta.viewBox` 始终具有权威性。省略时，在 `standard` 和 `showcase` 中，
画布宽度都会容纳阶段框和节点，包括
显式的节点宽度。加大宽度无法修复左边缘溢出。

Showcase 的节点尺寸、排版、自动高度、端口桥接和标签
摆放，只在省略 `meta.viewBox` 以及每个节点的 `width` 时才生效。
作者编写的画布或节点宽度会保留那些既有的布局行为，
`standard` 也是如此。有效的质量档为
`process.env.ARCHIFY_QUALITY_PROFILE || meta.quality_profile`；公共 CLI 的
`--quality standard|showcase` 会设置该环境变量覆盖。

对于全自动 showcase，节点宽度可以在其阶段和
画布预算内增长，使辅助文本在桌面投影下保持可读。高度
跟随实际的节点边界、路由点和渲染出的标签底板，
在内容下方留出 24px，外加 74px 的阶段/图例预留。行和作者编写的路由
始终具有权威性；未启用的通道控件不会扩大画布。

拥挤的入向箭头可以让默认节点在其所在行的
剩余空间内垂直扩展，最高 104px。其行中心和文本组保持原位，因此
畅通的同行输出仍保持笔直。16px 的拐角间隙和 10px 的节点
间距仍被保留。显式的节点高度或 `yOffset`，或者关联的
路由、侧或标签固定，会保留原始框。空间限制仍可能
让非常密集的输入保持拥挤；不会删除任何关系或标签。

对于跨路由轴相距不到 16px 的相对自动端口，当直线路径
畅通时，未共享的端点可以与分散后的端点对齐。这会保留共享槽位、16px 拐角间隙、已占用
端口以及作者编写的路由/标签控件。当两端都已分散或
直接路径被阻挡时，保留现有的垂直桥接。
当障碍路由使某条分支的初始行进方向反转时，共享的
侧可以按已稳定路由的首次转折重新排列其现有槽位。这
在放置标签之前，最多尝试 16 个由两到八个端口组成的全自动组。只有当某条路由变直，且没有任何成员
增加长度或弯折、新增交叉、折回，或失去节点、边框或
走廊间隙时，该组才会被接受。显式的侧、路由和标签控件保留其槽位。

在路由和标签稳定之后，一次有界的过程可以在
保持其他所有路由和标签固定的同时重试这种对齐。它最多检查 16 个标签摆放位置；
直线路径必须保留端口间距以及一个畅通、邻近的标签位置。
网格修复在替换有效桥接之前也会保留路由节奏下限。
未固定的标签保持在其自身路由的 36px 遮罩间隙之内。如果某个
标签因为外来路由占据了其邻近槽位而仍位于节点内部，
有界的联合修复可以平移该路由并重新放置该标签。它
最多检查 16 个标签槽位和 16 个路由候选，且不新增弯折
或交叉。未解决的摆放保留其碰撞诊断。
显式的 `labelAt`、`labelDx`、`labelDy` 和 `labelSegment` 始终具有权威性，
包括零偏移。现有的有效标签会被保留。

如果某个完整的自动标签在路由后仍发生碰撞，其文本可以在
一条水平线段旁换行为两行。字号、措辞、分类
以及所有路由都保持不变。底板保持在该线段的跨度内，
并与每条路由至少相距 4px，而不是移到附近节点的上方。这
最后一项容量修复对每个受阻标签最多尝试八种按词边界的拆分和 64 个位置。
如果两行都放不下，原诊断保留。

## 设计规则

- 用阶段表示数据生命周期边界：source、ingest、process、store、
  consume。
- 按阶段索引和行索引放置节点；常见情形下不要手工摆放原始 SVG。
- 用流标签命名数据资产，而不是传输原语：
  `clickstream`、`identity map`、`normalized facts`、`feature vectors`。
- 用 `classification` 表达简短的敏感度或治理上下文：
  `PII touch`、`non-PII`、`approved only`、`batch`、`read-only`。
- 对 PII、策略、同意、访问控制或受限连接使用 `security`。
- 对主数据路径使用 `emphasis`，对异步或批量
  派生使用 `dashed`。
- 让标签足够短，以便在狭窄的预览中放得下。

Schema 违规会以非零状态退出，并给出带路径前缀、标注了
元素 id 或标签的消息。当渲染器能检测到
布局问题时也会失败，包括缺失阶段、重复的节点 ID、节点超出
可读的图区域（`dataflow/node-above-area` / `dataflow/node-below-area`；
低于区域的诊断只在抬高后的页面仍能放入目标视口时
才提供 `meta.viewBox[1]` 的抬高建议，并指出满足条件的高度范围 —
页面包含是被建模的轴，而投影后的文本可读性
由交付检查（`viewer/projected-text-readability`）单独报告），
节点重叠、标签与节点或其他
标签碰撞、标签宽于其节点、未知的流端点、缺失流
标签、短到无法阅读的流、穿过无关节点的流（2px Clean Flow
间隙），或超出 viewBox 的阶段。阶段框仍是有意的
可穿越容器。文本宽度
以 CJK 感知的方式估算：全角字形计为两个单位。

为了精致交付，将 `meta.quality_profile` 设为 `showcase`。未解决的真
X 交叉会以 `composition/proper-crossing` 失败；默认的 `standard`
将其保留为产物回执警告。在没有
作者编写的画布或节点宽度的自动 showcase 布局中，渲染器会比较畅通的绕行与
清晰分隔的跨越。它优先选择短而畅通的路由，但也可能保留
一条带不透明光晕的较短自动交叉，而不是一条沿外围的长
绕行。在比较交叉之前，有界的路由搜索会尝试修复
进入无关节点或共用有歧义走廊的自动路径。
它们会保留节点间隙和走廊分离；失败的搜索仍会
保留障碍诊断。两条交叉路径都需要匹配的
光晕；产物检查会验证
其几何，并报告 `resolvedCrossovers` 供视觉复核。提供的
`via`、非 auto 的 `route` 以及通道坐标保留其几何和
交叉诊断。共线的阶段走廊不在
真 X 规则范围内，但另一道关卡会在无关流重叠至少 8px 时，于 `standard` 下警告、于
`showcase` 下失败。共享的语义
端点、点接触以及更短的重叠仍然有效。Showcase 还会
拒绝任何短于 8px 的路由线段和任何短于 16px 的内部转折线段；
普通的 8–15px 端点短桩仍然有效。
