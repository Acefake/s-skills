# 生命周期渲染器

将 `diagram_type: "lifecycle"` JSON 文件渲染为标准 Archify HTML
模板。

```bash
node archify/renderers/lifecycle/render-lifecycle.mjs input.lifecycle.json output.html
```

渲染器使用内置的独立校验器，按 `archify/schemas/lifecycle.schema.json`
校验输入。无需安装任何依赖。
若省略 `output.html`，渲染器使用 JSON 文件中必填的 `meta.output`
值。

## 输入

```json
{
  "schema_version": 3,
  "diagram_type": "lifecycle",
  "meta": { "title": "Deployment Release Lifecycle", "output": "deployment-release.html" },
  "mainPath": ["queued", "building", "verifying", "ready", "live"],
  "states": [],
  "transitions": [],
  "cards": []
}
```

完整示例见 `archify/examples/deployment-release.lifecycle.json`。

- `mainPath` 是从初始状态出发的正常路径。每一对相邻状态
  都需要一条转换；第一条这样的转换绘制为主行。
- `states[]` 只承载含义：`id`、`type`、`label`，以及可选的 `sublabel`、
  `tag`、`step`、`icon`、`brand` 和 `sources`。
- `transitions[]` 承载 `from`、`to`，以及可选的 `id`、`label`、`note` 和
  `variant`。没有任何路由或标签位置控制项。

## 布局 <a id="layout"></a>

几何完全由结构决定：

| 元素 | 放置方式 |
|---------|-----------|
| 主路径 | 一行，从左到右。每个间隙都容纳其转换标签。第一个状态带有 UML 初始标记。 |
| 回环与跳转 | 两个不相邻的主路径状态之间的转换（或回到更早状态的转换，或自转换）绘制为行上方的弧线。较短的弧嵌套在较长的弧内；端口经过排序，使外层竖线绝不穿过内层弧线。 |
| 其他状态 | 按与主路径的距离每级一行。状态从它在上一行所连接的状态下方开始；相互重叠的状态并排排列。 |
| 行与行之间 | 正交路由穿过共享间隙。水平段占用各自的轨道，选择时使交叉最少；接近垂直的路由吸附为直线，或加宽为可读的折弯。 |
| 共享出口 | 若某目标恰好有一组来自至少两个主路径阶段、标签、注释和 variant 完全相同的出口，则这些出口共享一个出口：相邻阶段获得一个虚线复合框，如同 UML 超状态；不相邻阶段共享一条带连接点的总线。其他出口保留独立的连接线和各自的标签。若同一目标有多组符合条件，则所有出口都保持独立。 |
| 同一下层行 | 相邻状态左右相连，平行转换围绕共享边呈扇形展开（每对状态最多五条）。密集的平行标签和注释会加大其泳道间距和该下层行的高度以保持避让；其他状态对从行下方绕回。 |
| 标签 | 位于主路径箭头上方、弧线和回环段上，否则放在靠近下层状态的线段旁。每个标签都避开其他路由、状态和标签；若无法避开，下层行和路由的间距会增大并重新布局，最多五轮。主路径间隙会在其最小行宽超出文字可读性预算之前停止增长；间隙仍能容纳其转换文字。 |

每条路由都带有交叉光晕，因此无法避免的交叉（例如
两个重叠的回环）仍然清晰可读。线条为正交线，带圆角。
把不同的注释保留在其原始转换上。绝不要为了让不同出口
符合共享条件而删除或复制注释。布局重试之后，最终的宽度和标签避让
检查仍然适用。

## 图例与状态标记

状态颜色取决于 `states[].type`：active 和 start 为青色，waiting 为琥珀色，
decision 为紫色，success 为绿色，failure 为玫红色，neutral 和 external 为石板灰。
第一个主路径状态带有初始标记；没有出向转换的状态
作为终态获得双边框。默认图例从已渲染的状态推导
种类，始终列出初始标记，并在存在终态时添加一个
不可交互的 `final` 条目。支持的
`meta.legend.entries` 键按固定顺序为 `start`、`active`、`waiting`、
`decision`、`success`、`failure`、`neutral` 和 `external`。

状态装饰共用一条顶部栏：左侧是类型徽记和 `step`，
右上角是品牌标识。只有读者应当注意的状态才有
默认徽记：`waiting`（沙漏）、`decision`（菱形）、`success`（对勾）、
`failure`（叉号）和 `external`；`start`、`active` 和 `neutral` 状态
没有徽记，除非 `icon` 设置了一个；但作为终态时例外，会获得停止徽记，
使每个结果都有标记。状态宽度会从 140px 增长到 220px，以便在首选字号
（标签 12px、副标签 9px、标签 tag 8px）下容纳其文字，之后才缩小
文字。

## 校验

schema 违规会以非零码退出，并输出带路径前缀的消息。渲染器还会
拒绝：重复的状态 id、未知或重复的 `mainPath` 状态、
没有转换的 `mainPath` 步骤、未知的转换端点、放不进最宽状态的
状态文字、在桌面上宽于其最小文字所允许宽度的画布
（`lifecycle/too-wide`）、经过各轮间距调整后仍无法放置的标签
（`lifecycle/label-unplaced`），以及两个相邻状态之间超过五条的平行
转换（`lifecycle/crowded-side-transitions`）。每种失败都是带类型的诊断，
并附有支持的修复方式。

最终的产物检查应用共享的构图关卡（正交
线段、交叉、走廊、标签避让和路由节奏）。同一
共享出口总线的路由声明 `data-composition-junction`；它们只能共享该
水平总线、来自同一源端口的相同首段短线，以及在它们
终止于同一状态时汇入该状态的合并下垂线。内部的垂直段
仍受走廊检查约束。

## 设计规则

- 把主路径当作故事：最多约六个阶段。
- 把中断、等待和退出放在主路径之外；由渲染器放置它们。
- 多个阶段共享的出口只给一个标签，例如 “cancel”。
- 可恢复的失败需要一条真实的返回转换。
- 完成使用 `success`，失败出口使用 `failure`，暂停使用
  `waiting`，质量关卡使用 `decision`。
