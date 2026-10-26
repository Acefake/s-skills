# Workflow 渲染器

将 `diagram_type: "workflow"` 的 JSON 文件渲染为标准 Archify HTML
模板。

```bash
node archify/renderers/workflow/render-workflow.mjs input.workflow.json output.html
```

渲染器使用内置的独立校验器，按 `archify/schemas/workflow.schema.json`
校验输入。无需安装任何依赖。

若省略 `output.html`，渲染器使用 JSON 文件中必填的 `meta.output`
值。

渲染完成后，运行产物检查器：

```bash
node archify/scripts/check-render-output.mjs output.html
```

它能捕获在浏览器中最容易看到的最终 SVG 问题：非有限的
SVG 数值、意外出现的两点斜线箭头，以及穿过
图例的箭头。

## 输入

Workflow JSON 文件必须设置：

```json
{
  "schema_version": 2,
  "diagram_type": "workflow",
  "meta": {
    "title": "Agent Tool Call Workflow",
    "output": "agent-tool-call.html"
  },
  "lanes": [],
  "phases": [],
  "groups": [],
  "mainPath": [],
  "nodes": [],
  "edges": [],
  "cards": []
}
```

新的 workflow 使用 `schema_version: 2`。它的可读布局编译器把
每个 `col` 视为 `0..5` 内的逻辑层级（rank），并从测量后的
文档推导几何。`schema_version: 1` 仍是面向现有源文件的固定旧版契约；
有效的 v1 输出逐字节保留，绝不会被静默地
重新解释为 v2。

常见的 v2 情形应省略 `meta.viewBox`，让编译器使用内在的
测量边界。在 v1 中，省略时宽度仍固定为 720，高度由
泳道数量推导。完整的示例位于
`archify/examples/agent-tool-call.workflow.json`；其 `schema_version` 决定
适用哪份契约。

Schema 位于：

```text
archify/schemas/workflow.schema.json
```

## 迁移与布局回执 <a id="migration-and-layout-receipt"></a>

将现有 v1 源文件迁移到一个单独的 v2 文件：

```bash
node archify/bin/archify.mjs migrate workflow old.json new.json --to-schema 2 --json
```

以其 schema-v2 输出作为新的源文件再次运行该命令，是一次
幂等的验证过程：目标文件的字节和几何均保持不变。

如果某个旧版 v1 源文件仅仅因为 `meta.output` 缺失或不再
可移植而被阻断，请为单独的 v2 目标文件提供替代值：

```bash
node archify/bin/archify.mjs migrate workflow old.json new.json --to-schema 2 --output reports/workflow.html --json
```

`--output` 本身必须是可移植的 POSIX 相对 `.html` 路径。它只更新
已验证的目标候选稿；源文件字节保持不变，
所有与 output 无关的 schema 和编译器诊断仍会阻断迁移。

该命令默认绝不覆盖源文件。它把绝对的
`via[*][0]`、`labelAt[0]` 和 `channelX` 值从旧版空间映射到求解后的层级
空间，保留 y 坐标（除非报告的垂直约束需要
作者输入），仅在无歧义的包含性修复时扩大显式 viewBox，
并且只有在 v2 编译和产物
检查通过后才写入目标文件。有歧义的显式固定（pin）会直接失败，不生成目标文件。

迁移会保留 `semanticChecks`，并对照
完整的作者拓扑校验这些要求。临时布局规划可以省略已布线的连线，
但作者无需为了使用迁移而删除或放宽其契约。
完整的迁移后文档仍必须满足作者编写的每一项要求。

用以下命令查看稳定的、面向作者的 v2 规划：

```bash
node archify/bin/archify.mjs validate workflow input.workflow.json --layout-json
```

回执报告所选契约、测量得到的 `viewBox` 和
`requiredViewBox`、求解后的列、节点、连线、标签以及因果诊断。
它刻意省略求解器迭代和候选评分。一个完整规划
若被后期的布局、画布或文本检查拒绝，也会附带这份几何，并标为
`ok: false`；校验仍以非零状态退出，且不写入 HTML。其 `viewBox`
是被拒绝时尝试的画框，而 `requiredViewBox` 是同一被拒规划的测量
占用范围。标签使用其锚点坐标，
而不是标签遮罩的左上角。早期或不完整的失败只保留
契约和因果诊断。失败的几何是修复证据，
不代表接受；迁移失败报告也可能附带测量的画布证据，
但不会因此接受被拒绝的规划。

## 图例

默认图例从 `nodes[].type` 推导组件种类。支持的
`meta.legend.entries` 键按稳定顺序为 `frontend`、`backend`、
`security`、`messagebus`、`database`、`cloud` 和 `external`。标签和
可见性可通过共享图例契约覆盖；只有存在已渲染节点支撑的种类
才会获得 Semantic Legend 控件。

## 布局契约 <a id="layout-contracts"></a>

### 固定 v1

| 常量 | 值 |
|----------|-------|
| viewBox | 默认 `[720, auto]` — 自动高度 = 52 + 泳道数×104 + (泳道数−1)×20 + 124 |
| 泳道框 | x 40，宽 640，高 104，间距 20；第一条泳道顶部位于 y 52 |
| 泳道标题条 | 每条泳道顶部 30px；节点框必须保持在其下方 |
| 列中心（`col` 0–5） | x = 88, 220, 300, 430, 500, 625 |
| 阶段标题 | 可选的 `phases[]` 渲染在第一条泳道上方，跨越 `fromCol..toCol` |
| 泳道分组 | 可选的 `groups[]` 在单条泳道内框出并行工作或分支工作 |
| 异常泳道 | 为重试、拒绝、回退或失败路径设置 `lane.variant: "exception"` |
| 主路径检查 | 可选的 `mainPath[]` 检查主流程（happy path）步骤有对应的连线且不向后移动 |
| 默认节点 | 92×52（设置 `tag` 时高 68） |
| 节点间距 | 同一泳道内节点之间 ≥8px |
| 连线长度 | 直线段必须跨越 ≥28px |
| 图例行 | y = 泳道底部 + 44；viewBox 高度必须 ≥ 图例 y + 18 |

列中心间距为 132 / 80 / 130 / 70 / 125 px：第 1↔2 列（80px）和
第 3↔4 列（70px）无法在同一泳道中同时容纳默认宽度 92px 的节点。此类
无效的 v1 源文件会收到一条因果性的 `workflow/column-capacity` 诊断以及
一项已验证的迁移到 v2 的修复；v1 绝不会回落到自适应布局。

### 可读 v2 <a id="readable-v2"></a>

| 不变量 | 契约 |
|----------|----------|
| 逻辑列 | `col` 是 `0..5` 内的整数；像素中心是测量输出 |
| 相邻层级基线 | 在文档特定约束之前，中心距离为 120px |
| 同泳道节点间隙 | 节点垂直区间重叠时 ≥8px |
| 相对的直接连线 | 净间隙 ≥`max(28px, measured label mask width + 8px)` |
| 自动路由节奏 | 直接段 ≥28px；端点短桩 ≥8px；内部转折段 ≥16px |
| 隐式 viewBox | 内在内容边界加上契约留白 |
| 显式 viewBox | 包含容量；过小的输入会报告精确的 `requiredViewBox` 及其贡献项 |
| 泳道测量 | 同列垂直堆叠（两个或更多不同的 `yOffset` 值）会让隐式、未固定的 workflow 启用逐泳道测量。显式的 `meta.viewBox`、`via`、`labelAt`、`channelX` 或 `channelY`，以及没有堆叠的 workflow，为兼容起见保留共享高度的 v2 几何。 |

未固定的 v2 草稿在重叠的同泳道节点之间为路由预留 32px，
省略的节点宽度可从 92px 增长到 200px 以容纳其文本。带有
显式 `meta.viewBox` 或绝对 `via`、`labelAt`、`channelX` 或
`channelY` 固定的文档，在编译和迁移规划中都保留现有的宽度默认值和 8px 层级间隙
约束。作者编写的宽度始终
具有权威性。

自动 showcase 画布会按桌面阅读下限检查副标签，
但不会把文本放大到超出其现有的 8px 槽位。如果画布无法让
该槽位保持可读，`workflow/sublabel-readability` 会报告所需的字号
和画布宽度。standard 质量档和显式画布保留其之前的
文本适配行为以及现有的构图/浏览器质量检查。

编译器只对实际相关或重叠的
同泳道节点施加约束，因此无关泳道中的宽节点不会撑大每一个
层级。旧版中心只是正确性约束之后的软偏好，不是
几何承诺。阶段框和分组框从求解后的层级带推导。
自动路由只规范化一次，同一份最终场景同时驱动
校验和 SVG 序列化。长的自动标签会比较直接间隙
增长与一条合法通道，而不是加宽下游每一个层级。测量得到的
多行图例参与内在高度和显式 viewBox
容量的计算。

Issue #250 的形状已有不需要作者指定泳道
尺寸的 v2 表示。把三个阶段放在一条带分组的泳道中，省略 `meta.viewBox`，并让
它们的偏移围绕零居中：

```json
{
  "schema_version": 2,
  "diagram_type": "workflow",
  "meta": { "title": "stack", "output": "stack.html" },
  "lanes": [{ "id": "cage", "label": "one cage" }],
  "groups": [{ "id": "g", "label": "cage", "lane": "cage", "fromCol": 1, "toCol": 3 }],
  "nodes": [
    { "id": "a", "lane": "cage", "col": 2, "type": "security", "label": "stageA", "yOffset": -90 },
    { "id": "b", "lane": "cage", "col": 2, "type": "security", "label": "stageB", "yOffset": 0 },
    { "id": "c", "lane": "cage", "col": 2, "type": "security", "label": "stageC", "yOffset": 90 }
  ],
  "edges": [
    { "from": "a", "to": "b", "fromSide": "bottom", "toSide": "top" },
    { "from": "b", "to": "c", "fromSide": "bottom", "toSide": "top" }
  ]
}
```

隐式可读 v2 垂直堆叠若测量得到的泳道高度超过
104px 基线，会声明 `data-reader-fit="width-first"`；任何隐式
可读 v2 画布若以全宽显示会溢出 1440×900 桌面页面，也同样声明。桌面查看器使用
可用的阅读宽度和正常的页面滚动来保持高阶段可读，
并沿用现有的 1.5× 自动放大上限。这只改变显示
尺寸：规范 SVG 几何和显式 `meta.viewBox` 的 workflow 保留其
作者契约。Embed、Present 和打印保留其现有的适配模式。
`visual-check` 仍会检查可读性、水平包含和裁切；
该声明不会削弱节点或路由校验。

作者编写的 `via`、`labelAt`、`channelX` 和 `channelY` 在 v2 中是绝对硬固定；
不可行的固定会返回 `workflow/explicit-pin-conflict`，而不是被
静默移动。`fromSide` 和 `toSide` 仍是方向约束。路由
预设会限制自动候选族，但其本身不是绝对
坐标固定。当任一端点侧被省略时，v2 编译器会选择
一个可行的侧；作者指定的侧会把该端点限制在所命名的端口。
不可行的预设会返回 `workflow/route-preset-conflict`，并附带实际
被违反的 `evidence.invariant`。对于节点间隙，它还会指出节点、
线段、端点角色和所需间隙。利用该障碍修改
相连的布局位置或路由约束，然后重新校验；仅靠最小线段
长度并不能确立一条畅通路径。`workflow/route-preset-conflict`
的具体替代方案会在当前质量档下重新规划完整 workflow
来检验。

## 设计规则

- 用泳道表示归属或运行时边界。
- 用阶段标题表示高层叙事节拍，例如 Intake、Plan、Execute 和 Report。
- 用分组表示泳道内的并行检查、分支处理或有界工作；每个分组必须至少包含一个节点。
- 对于堆叠在一个容器内的顺序阶段，使用一条 v2 泳道和一个分组，把各阶段放在同一列，并省略 `meta.viewBox`。`yOffset` 相对于泳道内容区域的中心，因此三阶段堆叠应以 `-90 / 0 / 90` 居中，而不是 `0 / 90 / 180`。在路由和画布由编译器负责时，编译器只扩展该泳道。
- 对人工等待、拒绝、重试、回退和失败泳道使用 `lane.variant: "exception"`，而不是把这些路径混入主流程。
- 当图有清晰的主流程时设置 `mainPath`；渲染器会校验相邻 id 有对应连线且从左向右移动。
- 用泳道 ID 和 `0..5` 内的 `col` 索引放置节点，而不是原始 SVG 坐标。
- 保留语义连线标签。可读 v2 会分配测量得到的标签间隙；
  当标签放不下时，修复所报告的容量或路由约束，
  而不是删除含义。
- 用标签表达决策、审批、协议、异步追踪、返回路径，
  以及任何无法完全由端点推断出的其他关系含义。
- 在使用原始 `via` 点之前，优先使用路由预设 — `drop`（在泳道之间弯折；`bias` 0–1 选择位置）、
  `outside-right`、`return-left`、`bottom-channel` 和 `up-channel`。
  `straight` 和默认的 `auto` 覆盖其余情况。
- 让 workflow 示例保持足够紧凑，以便在狭窄的聊天/浏览器
  预览中渲染良好。

### 可选的语义检查

布局校验无法从标签或卡片推断领域事实。当源
证据确立了根节点、终端节点、必需的直接关系或
必需的有向可达性时，把这些事实编码到 `semanticChecks` 中：

```json
"semanticChecks": {
  "allowedRoots": ["request", "resource_catalog"],
  "allowedTerminals": ["reply", "audit_log"],
  "requiredEdges": [
    { "from": "dispatch", "to": "dispatch_ledger" }
  ],
  "requiredPaths": [
    { "from": "event_ledger", "to": "runtime_host" }
  ]
}
```

当存在 `allowedRoots` 或 `allowedTerminals` 时，它分别是零入边或零出边节点的完整允许
列表。`requiredEdges`
要求恰好一个作者指定的方向；`requiredPaths` 允许中间
节点，但遵循作者编写的连线方向。这些检查在布局之前运行，不会
改变 SVG 或回执字节，并且绝不能仅仅为了解决某个
路由或构图诊断而被削弱。领域事实未知的字段应省略。

Schema 违规会以非零状态退出，并给出带路径前缀、标注了
元素 id 或标签的消息。当渲染器能检测到
布局问题时也会失败，包括节点重叠、节点超出其泳道、无效的
阶段/分组列范围、空分组、断裂的 `mainPath` 步骤、未知的连线
目标、标签与节点或其他标签碰撞、标签宽于其
节点、图例超出 viewBox，或直线箭头过短而无法
清晰阅读。共享的 Clean Flow Gate 还会拒绝以 2px 间隙穿过无关
节点的连线；泳道、阶段和分组仍是有意的
可穿越容器。文本宽度以 CJK 感知的方式估算：全角字形
计为两个单位。

诊断是因果性的：层级容量失败会抑制由此衍生的短
连线、端点方向和标签重叠发现。`supportedFixes[]` 可以
包含经编译器修复搜索检验的具体编辑，或来自共享构图检查的通用修复
指导。通用指导不是已验证的
编辑。任何编辑之后，都要重新运行完整的 `finalize` 命令。当标签的存在并不导致
失败的不变量时，诊断绝不会
建议删除语义标签。

为了精致交付，将 `meta.quality_profile` 设为 `showcase`。此时无关的真
X 交叉会以 `composition/proper-crossing` 失败；默认的 `standard`
将其保留为产物回执警告。共线的泳道走廊不在
真 X 规则范围内，但另一道关卡会在无关连线重叠至少 8px 时，于 `standard` 下警告、于
`showcase` 下失败。V1 保留其作者编写的
共享端点契约。V2 还会检查共享端点，包括显式
控制的路由：长的或混合样式的主干、逆流、真内部 X
交叉以及重叠的独立箭头均不豁免。固定会被
保留，而不会被静默修复；未解决的 v2 走廊/箭头碰撞
在 `standard` 下警告，在 `showcase` 下失败。

V2 仅在两条关系共享实际的源端口或目标端口、有效
变体、描边宽度和角色时，才允许至多 24 个 SVG 单位的同向共享终端短桩。非终端重叠绝不算此类短桩；
前向共线的途经点不会把长主干拆分成被允许的小段。
兼容的短合流可以共享其终端箭头。自动路由会
考虑分离的端口，在争用节点处为绝对路由预留，并优先选择
畅通路径而非更短但有歧义的路径。拥挤的自动走廊可以使用
有界的局部调整，而不移动节点或改变显式坐标。

SVG 携带 `data-layout-contract="readable-v2"` 以及每条连线的角色，使
产物检查对实际可见的路径几何应用相同的分类，
而不是过时的构图点元数据。这些内部输出属性不会
新增作者 schema 字段。其他图类型保留其现有规则。
V2 真交叉诊断在编译器/layout-JSON 回执和最终 HTML 检查中都会保留关系 ID、交点
和受支持的修复；
`standard` 报告警告，而 `showcase` 拒绝该交叉。两种分析都会
合并前向共线的途经点而不重写作者路径；真实的弯折
和折返仍视为端点接触，而不会被合并成 X。

较旧的逐连线 `data-composition-routing="workflow-v2-auto"` 标记仍然
保留，以兼容没有根布局
契约的第一轮导出 HTML 以及较旧的产物检查器。仅有标记的产物保留其
较窄的自动配对交叉/逆流策略；根 `readable-v2`
契约在存在时具有权威性，并且还会检查显式路由。在不淘汰该导出格式的情况下，
不要把仅标记路径当作死代码删除。
Showcase 还会
拒绝任何短于 8px 的路由线段和任何短于 16px 的内部转折线段；
普通的 8–15px 端点短桩对固定泳道间距仍然有效。
