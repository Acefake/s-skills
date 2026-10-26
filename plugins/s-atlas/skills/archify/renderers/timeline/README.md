# 事件时间线渲染器

将 `diagram_type: "timeline"` JSON 文件渲染为标准 Archify HTML 模板。

```bash
node archify/renderers/timeline/render-timeline.mjs input.timeline.json output.html
```

`--layout-json` 打印轴分段、断裂、刻度、泳道和已放置的
事件（含其毫秒时间戳和 x 位置），而不是 HTML。

## 输入

```json
{
  "schema_version": 1,
  "diagram_type": "timeline",
  "meta": { "title": "Payment failure incident", "evidence": "illustrative", "timezone": "Asia/Shanghai" },
  "lanes": [{ "id": "release", "label": "Release" }],
  "events": [{ "id": "deploy", "at": "2026-10-01T10:00:00+08:00", "title": "Deploy v2.4", "lane": "release" }]
}
```

- `at` 为 ISO 8601，带显式的 `Z` 或 `±HH:MM` 偏移（schema）。
  不可能存在的日期以 `timeline/invalid-timestamp` 失败。
- `meta.timezone` 是 IANA 时区（默认 `UTC`），用于所有刻度和标签；
  刻度落在该时区的墙钟时间上，因此 `+05:30` 时区按其自身的
  整点打刻度。未知时区以 `timeline/invalid-timezone` 失败。
- 跨越时区偏移变化时，日刻度保持在当地午夜，小时
  刻度使用真实的当地时刻。重复小时的两次出现都会保留；
  被跳过的小时或日期不会虚构刻度。事件时间戳和按实际经过时间
  成比例的间距保持不变，因此相邻日刻度之间可以相隔 23 或 25
  小时。现有的标签过滤仍会隐藏放不下的文字。
- 夏令时和时区调整不会把刻度固定在时间段起点的 UTC 偏移上：日刻度保持当地
  午夜，小时刻度仅对应真实存在的当地时刻。回拨产生的两个相同墙钟时刻都保留；
  跳过的小时或整天不补造刻度。事件时间与轴上的实际时间距离不变，因此相邻
  日刻度之间可以是 23 或 25 小时；空间不足的刻度文字仍按原有规则隐藏。
- `meta.evidence`（`observed` 或 `illustrative`）为必填，并以徽章形式绘制在
  画布左上角。
- 有 `lanes` 时，每个事件都必须指定一个已声明的泳道（`timeline/unknown-lane`）。
  `detail` 显示在 Semantic Passport 中；`kind`（`change`、`alert`、
  `action`、`recovery`）为卡片着色，并添加一个图例条目。

## 轴

事件按时间排序（时间相同则保持作者顺序）。x 与时间呈线性关系，
整张图只用一个比例尺；所有泳道共享同一条轴，因此同一
时刻在每个泳道中都只有一个 x，无论各时间戳以何种偏移书写。

`layout.breaks: "auto"`（默认）会压缩长于不同时间戳之间中位间隔 8 倍
且长于总跨度 10% 的平静时段（最多压缩能放下的最长八段，同时为成比例的时间保留空间）。
断裂是一条固定宽度的阴影带，轴上带有锯齿，
并标出省略的时长（`≈ 1 d 11 h`）；轴说明指出压缩了多少个时段，
每个断裂都带有 `data-break-ms` 和无障碍标签。
每个分段内部的比例尺是同一个常数，因此其中的距离保持
精确。`layout.breaks: "none"` 绘制一条完全成比例的轴。`layout.width`
（默认 960）是轴宽。

## 卡片

每个事件是其泳道线上的一个圆点，加上一张显示确切时间和标题的卡片。
卡片以其时刻为中心，位于泳道线的任一侧，
从线向外逐行排布：每张卡片选择能让它最贴近
线且不碰到更早卡片的那一侧（相持时放在下方），因此同时发生
和相近的事件会叠放而不是重印，一串密集事件会向两侧展开。
连接线绘制在所有卡片之后，所有圆点位于同一个共享光晕层上，因此相隔几秒的事件会合并为一个带描边的胶囊。卡片是安静的表面，带有表示其种类的
色调强调。标题在单词之间换行。在跨多天的轴上，刻度只在日期变化时
标出日期。

## 实测规模

`examples/archify-dev-activity.timeline.json` 是观测数据（来自本仓库 `origin/dev` 的 20 个 tag 和
merge 时间戳，包括相隔 19 s 的事件、
一个 `+05:30` 提交者偏移，以及五个被压缩的平静时段）。它
渲染约需 0.3s，并通过 showcase 关卡。
