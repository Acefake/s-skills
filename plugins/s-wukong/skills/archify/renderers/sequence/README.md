# 时序图渲染器

将 `diagram_type: "sequence"` JSON 文件渲染为标准 Archify HTML
模板。

```bash
node archify/renderers/sequence/render-sequence.mjs input.sequence.json output.html
```

渲染器使用内置的独立校验器，按 `archify/schemas/sequence.schema.json`
校验输入。无需安装任何依赖。

若省略 `output.html`，渲染器使用 JSON 文件中必填的 `meta.output`
值。

## 输入

时序图 JSON 文件必须设置：

```json
{
  "schema_version": 1,
  "diagram_type": "sequence",
  "meta": {
    "title": "Cache Miss Request Sequence",
    "output": "cache-miss-request.html",
    "viewBox": [920, 760]
  },
  "participants": [],
  "segments": [],
  "messages": [],
  "activations": [],
  "cards": []
}
```

时间线随 viewBox 高度缩放：更高的 `meta.viewBox` 能换来更多
消息空间，更矮的则会收缩可读区带，而不是裁切内容。完整的示例见
`archify/examples/cache-miss-request.sequence.json`。

schema 位于：

```text
archify/schemas/sequence.schema.json
```

## 图例

默认视觉图例从 `messages[].variant` 推导种类（省略
`variant` 即为 `default`）。支持的 `meta.legend.entries` 键按固定
顺序为 `emphasis`、`return`、`security`、`dashed` 和 `default`。这些是
视觉层面的消息键，不是 Semantic Lens 控件；标签/可见性覆盖
不会生成连线事实。

图例位于全部时间线内容的下方：最后一条消息及其注释、
激活条和分段框，间距 12px。没有 `meta.viewBox` 时，
画布高度贴合这些内容（没有固定的 760px 下限），并在靠后的
消息需要更多空间时增高。若作者给出的 `viewBox` 太矮，
`showcase` 会失败并给出应设置的确切高度，而 `standard` 会隐藏隐式
图例，而不是把它画在内容之上。生命线止于图例上方。
消息标签使用其线条的颜色；灰色的 default 和 return 线条保留
柔和的文字颜色。

## 布局预算

| 常量 | 值 |
|----------|-------|
| viewBox | 自动高度贴合内容 + 图例（可读区带最小 327px）；靠后的内容需要更多空间时更高；自动宽度对 2–3 个短标签参与者收紧到 560–800px（4 个及以上默认 920；长标签仍会加宽）。schema 最小值 `[480, 480]` |
| 参与者框 | `spread`（默认）：随 viewBox 变化的宽度，从 86px 到最多 190px；`fixed`：宽 86px；两者均高 60px，位于 y 72 |
| 参与者列 | `fixed`：中心位于 x = 62 + index×108；`spread`：各列在可用的 viewBox 宽度内分布，卡片间距至少 16px |
| 参与者数量 | 最后一个框必须止于 width − 40 或更早；放不下的布局按失败关闭处理 |
| 生命线 | 从 y 142 向下到 height − 65（画到图例正上方）；区带必须至少高 120px |
| 消息 `y` 范围 | `[160, height − 83]` |
| 消息间距 | 共享水平空间的消息之间垂直距离 ≥28px |
| 箭头跨度 | 两个参与者之间水平距离 ≥60px |
| 消息注释 | 箭头下方 7px 的上下文文字，在正常 Read 缩放下可见（Map 隐藏它但不改变时间线几何），以 11px 行距在相邻生命线之间的一个间隙内换行（取该消息跨越的最宽间隙；相差 0.5px 以内的间隙视为相等，取最左侧的那个，注释一向从那里开始），并避开激活条；过长的无断点文字在 `/ . - ? & = # _` 之后断行，否则可在任意字符处断行，因此每种导出都保留完整注释。在 `showcase` 下，触及后一条消息的注释以 `sequence/note-overlap` 失败，并给出那条消息所需的 `y`；超出画布内容上限的注释以 `sequence/note-canvas-limit` 失败，并给出所需的 `meta.viewBox[1]`；分段标签在四次向上移动后仍遮挡消息标签、路由或注释时以 `sequence/segment-label-overlap` 失败；每条诊断都会指出源路径，并在存在时提供经过验证的 `supportedFixes` 修改 |
| 分段 | y 像素范围，`to > from`，位于 `[72, lifeline bottom + 20]` 之内 |
| 图例 | 最后一行基线位于 height − 54；多出的行向上换行，并保持在时间线内容下方 12px |

`segments[].from/to` 和 `activations[].from/to` 是 y 像素坐标，不是
参与者 id；激活同样要求 `to > from`。

### 列适配

无论是否提供 `meta.viewBox`，时序图默认都是 `meta.column_fit: "spread"`。
显式的 `"fixed"` 保留历史上的 86px 框和 108px 列间距。
要保留历史上的固定坐标，必须显式设置 `meta.column_fit: "fixed"`。
当宽 viewBox 否则会在右侧留下空白，或者有意义的参与者标签
放不进固定的 86px 框时，使用 `"spread"`。spread 从 viewBox 推导框宽
和列距，同时保留参与者顺序、生命线和消息语义。参与者卡片保留至少 16px
间距。能容纳这些卡片的窄画布可把左边距从 62px 缩小到 40px；
普通画布保持 62px，右边距保持 40px。窄到容不下这些边距和间距的框
会直接失败，而不会放大作者给出的 viewBox。

产物检查器根据渲染出的参与者、路由和文字报告 `composition.sequenceColumnSpace`。
固定布局中右侧有大片未使用区域时，可能在 `finalize` 中产生
`inspect-sequence-width` 建议；这只是建议，不是新的警告或失败。
有界的作者修复方式以及显式 fixed 的保留规则，见 [Sequence width review](../../references/delivery-contract.md#sequence-width-review)。

## 设计规则

- 消息目前要求 `from` 和 `to` 是不同的参与者。虽然
  schema-v1 接受相同的 ID，但本渲染器不绘制自调用环，
  并以 `sequence/self-message-unsupported` 拒绝它们，指出消息
  路径和参与者。增大列距无法修复自消息。
  请把内部步骤的措辞、归属和顺序保留在某个实际交互的注释里，
  或保留在一张显式排序的卡片中。绝不要仅为通过校验而虚构另一个
  参与者或更改目标。这些作者选择需要语义审查，不作为自动修复提供。
- 把参与者排在顶部，按读者应遵循的故事顺序排列。
- 时间向下推进。
- 主请求路径使用 `emphasis`。
- 认证、授权同意、权限和策略调用使用 `security`。
- 安静的响应消息使用 `return`。
- 异步追踪、事件、日志和非阻塞工作使用 `dashed`。
- 把分段用作浅色背景参考；分段标签保持简短，并让每个框边与每条消息箭头至少相距 4px。在结束一个阶段之前，既要检查箭头，也要检查完整的换行注释。`validate` 和 `check` 在 `composition.sequenceNoteBorders` 中把交叉作为审查证据报告，不会阻止定稿。所提供的 `supportedFixes` 修改只延伸指名的底边；没有可单独应用的修改时，要同时调整阶段边界和消息间距，保留完整注释和消息顺序。
- 标签保持简洁，但在为了放进固定框而缩短有意义的参与者标签之前，
  先尝试 `meta.column_fit: "spread"`。

schema 违规会以非零码退出，并输出带路径前缀、注明元素 id 或标签的
消息。渲染器还会在能检测到布局问题时失败，包括：缺少参与者、参与者 ID 重复、
参与者标签宽于其框、消息端点未知、消息超出可读时间线、
水平重叠的消息之间垂直间距过小、分段或激活范围无效，
或参与者超出 viewBox。共享的 Clean Flow 契约把参与者标题视为
语义框，同时明确允许消息穿过中间的生命线、激活条和分段框。文字宽度按 CJK 感知方式估算：
全角字形计为两个单位。

要精修交付，将 `meta.quality_profile` 设为 `showcase`。此时无关消息之间的真正
X 形交叉会以 `composition/proper-crossing` 失败；默认的
`standard` 将它们保留为产物回执中的警告。消息仍可穿过
中间的生命线。共线走廊不受真正 X 交叉规则约束，
但另有一道关卡：当无关消息重叠至少 8px 时，在 `standard` 下警告、在 `showcase` 下失败。
共享的语义端点、点接触以及更短的重叠仍然有效。showcase 还会拒绝
任何短于 8px 的路由线段，以及任何短于 16px 的内部转折线段；普通的 8–15px 端点
短桩仍然有效。
