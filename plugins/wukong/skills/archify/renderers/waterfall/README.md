# 执行瀑布图渲染器

将 `diagram_type: "waterfall"` JSON 文件渲染为标准 Archify HTML 模板。

```bash
node archify/renderers/waterfall/render-waterfall.mjs input.waterfall.json output.html
```

`--layout-json` 打印轴、比例尺、刻度以及每一行的时间和条形
几何，而不是 HTML。

## 输入

```json
{
  "schema_version": 1,
  "diagram_type": "waterfall",
  "meta": { "title": "Checkout request", "evidence": "illustrative", "unit": "ms" },
  "spans": [
    { "id": "request", "name": "POST /checkout", "start": 0, "end": 1200 },
    { "id": "auth", "name": "Authenticate caller", "start": 0, "duration": 100, "parent": "request" }
  ]
}
```

一个 span 给出 `start`，以及 `end` 或 `duration` 之一（只有两者一致时才可同时给出），
单位为 `meta.unit`（`us`、`ms` 或 `s`；默认 `ms`），从共同的追踪
原点起算。`parent`、`status`（`ok`、`error`、`cancelled`、`incomplete`）、
`service`、`detail` 和 `sources` 为可选。`meta.evidence`
（`measured` / `illustrative`）为必填，并以徽章形式绘制。

| 代码 | 拒绝的输入 |
| --- | --- |
| `waterfall/invalid-timing` | end 早于 start、end 与 duration 不一致，或非 `incomplete` 的 span 没有 end/duration（负值由 schema 判定失败） |
| `waterfall/missing-parent` | `parent` 指向未声明的 span |
| `waterfall/cycle` | 父链接形成环 |
| `waterfall/duplicate-id` | 某个 id 被声明了两次 |

没有 end 的 `incomplete` span 会画到追踪中最后一个已记录的时刻，
主体为虚线、末端开放，并标注 `incomplete, ≥ X`——这是一个
下限，绝不是测得的时长。允许有多个根 span。

## 布局

各行按深度优先排列：每个 span 后面紧跟按开始顺序排列的子 span，
并在名称列中以树形引导线缩进，因此从左侧读出嵌套关系，
从条形读出时间。一个线性比例尺把追踪从最早的
开始到最晚的结束映射到 `layout.width`（默认 760 px）上；刻度使用 1/2/2.5/5
步长。不同行上相互重叠的条形表示并发工作。

有子 span 的 span 在其时间范围上绘制为着色、带描边的括号；
自身执行工作的 span 是实心条，因此着色方式把包含性
汇总与叶子工作区分开。颜色表示 `service`：每个服务按首次出现的顺序获得
自己的配色族（没有服务的 span 继承其父 span 的服务；无归属的 span 为中性色），
并在名称列中显示一个圆点；出现多于一个服务时还有一个图例
条目。服务颜色共五种；超过
五个服务时颜色循环，共享同一颜色的服务共享一个图例条目
（`gateway · inventory`），因此图例绝不会把一种颜色绑定到并不独占它的
单个服务。红色保留给 `status: "error"`。

每个条形在其末端之后标出确切时长；画布在轴外为最宽的标签预留
空间，因此短操作也保有标签。
标题栏给出墙钟总时长和范围。Semantic Passport 显示
确切的开始–结束、时长，以及 "N% of T wall-clock" 形式的占比；父 span 的时长
是包含性的，绝不会与其子 span 相加。不绘制关键路径或
等待时间：输入没有可支撑它们的依赖模型。

## 实测规模

`examples/example-rebuild.waterfall.json` 是一条实测追踪：来自一次
本地运行的 25 个 span，该运行通过三个并发 worker 渲染并检查了八个内置示例
（从子进程启动到退出，使用 `performance.now()` 偏移）。
它渲染约需 0.2s，并通过 showcase 关卡。
