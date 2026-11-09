# 编写契约 <a id="authoring-contract"></a>

只有在快速编写路径要求更多细节之后才阅读本参考。schema 和示例仍然是权威依据。

## 构图修复 <a id="composition-repair"></a>

纠正已编写概览图的抽象层级时，在重新分组之前，先把每个受影响的角色、关系方向、协议、边界、条件和来源引用映射到保留下来的节点或关系上。启动时的引用并不能证明某种消息协议。保留每条主张已核查过的证据。用户提供或已商定的拓扑保持不变；仅仅为了减少走线，不足以成为合并的理由。只包围一个节点的边界需要明确的隔离事实，且绝不能只是重复该节点的标签。

## 标签修复 <a id="label-repair"></a>

当关系标签发生碰撞时，先移动标签，再调整路径或间距，然后在保留含义的前提下缩短措辞。只有当两个端点已完全隐含该措辞、且它不传达任何协议、动作、方向、同步或异步行为、或跨边界机制时，才可省略措辞。间距指净间隙，而不是中心距离；以测量得到的遮罩宽度为准。初稿间隙预算见 [Layout and routing](authoring-defaults.md#layout-and-routing)。

对于比例失调的子标签，保持其确切的角色或协议简洁，并把补充事实放进注释或卡片。保留每一项必需的职责、协议和边界事实。使用 [Layout and routing](authoring-defaults.md#layout-and-routing) 中的初稿节点宽度预算。

## Schema 查阅 <a id="schema-lookup"></a>

同时阅读模式 schema 和 `schemas/common.schema.json`。模式 schema 使用 `$ref`，因此共享枚举定义在 common 文件中。

- `componentType`：`frontend`、`backend`、`database`、`cloud`、`security`、`messagebus`、`external`
- 实体关系文档使用 `entities` 和 `relationships`；`key` 接受 `pk`、`fk` 或 `uk`，`fromCardinality`/`toCardinality` 接受 `one` 或 `many`。
- `variant`：`default`、`emphasis`、`security`、`dashed`
- 关系 ID 使用共享的标识符模式，且在其所属集合中必须唯一。

不要臆造字段。在写入任何新字段、枚举或受约束文本之前，先阅读其 schema 定义，包括 common 中的 `$ref` 目标。尤其要检查边界类型、仓库标识和来源引用的结构。示例演示的是结构；它并不列举所有合法值。ID、措辞、事实和布局都要重新编写。

## 工作流布局契约 <a id="workflow-layout-contracts"></a>

新工作流使用 schema v2；当现有源文件必须保留固定几何时，保持 schema v1。在两个版本中，`col` 都保持在 `0..5` 范围内，并且绝不能把删除语义连线标签当作间距修复手段。存在绝对坐标时，不要只修改 `schema_version`：遵循规范的 [migration and layout-receipt contract](../renderers/workflow/README.md#migration-and-layout-receipt)。完整的规范性不变量位于工作流渲染器的 [layout contracts](../renderers/workflow/README.md#layout-contracts) 中。对于堆叠在同一容器中的顺序阶段，使用一个 v2 泳道和分组，省略 `meta.viewBox`，并用对称的 `yOffset` 值（例如 `-90 / 0 / 90`）让节点围绕泳道内容居中。保留语义连线标签，并依据编译器诊断采取行动。

## 图例契约 <a id="legend-contract"></a>

省略 `meta.legend` 即得到如实的默认值：`auto` 只列出类型化 IR 中实际存在的语义类别。渲染器参考图使用 `mode: "all"`，或用 `mode: "hidden"` 移除完整图例。在 `entries` 下，只有所选模式 schema 列出的键才合法；每个键接受 `label`、`visible` 或两者兼有。`visible: true` 可以显示一个未使用但受支持的约定，而 `visible: false` 会隐藏它。`hidden` 不能被覆盖。

标签覆盖只改变面向读者的措辞。绝不能从散文推断类别，也绝不能用图例来弥补缺失的节点、状态、消息或流。长标签会被测量并换行为确定性的多行。Architecture 隐式的自动 viewBox 依据同一测量占位增长，自动的 ERD 画布也以同样方式确定尺寸，因此其默认图例始终位于生成内容之中。为了向后兼容，没有 `meta.legend` 的旧文档可以省略一个无法放进其显式 viewBox 的隐式 auto 图例；这绝不会改变其类型化拓扑。编写了 `meta.viewBox` 的 ERD 保持该固定区域，并报告容量，而不是丢弃图例。添加 `meta.legend` 会使呈现变为有意为之且严格：如果其解析后的标签无法放进编写的 viewBox，就缩短或隐藏它们，或依据发出的诊断加宽 viewBox。

## 语言一致性 <a id="language-consistency"></a>

选择一种主编写语言。用户的明确选择优先；否则使用请求的语言，或在请求本身与语言无关时使用对话的主导语言。另外单独选择查看器的 locale。始终写入匹配的 `meta.locale`，形式为格式正确的语言标签：英语为 `"en"`，简体中文为 `"zh-CN"`，西班牙语为 `"es"`，其他语言使用相应的其他标签。渲染器直接使用编写的 locale，而不从图中字符串推断语言。省略它的文档仍然有效，并默认为英语。

`meta.locale` 只控制渲染器拥有的读者界面：`<html lang>`、文档标题后缀、默认 SVG 描述和焦点标签、默认图例标签，以及固定的查看器控件、状态、无障碍名称和错误。它绝不翻译编写的内容。要单独把主语言应用到标题、副标题、节点和关系文案、边界、泳道、分组、图例标签覆盖和卡片上。双语图仍然要为查看器选择一个主 locale；先遵循明确的主语言请求，其次依据提示中的顺序或对话的主导语言。

内置的查看器目录登记在 `locales/manifest.json` 中：当前为 `en`、`zh-CN`、`zh-TW`、`es`、`ko` 和 `ar`。对于这些语言，仅凭 `meta.locale` 即可选中完整目录。标签匹配不区分大小写（`zh-cn` 会选中 `zh-CN`），但地区和书写系统变体是不同的：`zh-Hant`、`es-MX` 或 `ko-KR` 不会选中任何内置目录。

`meta.translations` 是可选的逐键覆盖：一个对象，把渲染器的规范消息键（`locales/en.json`，或 `renderers/shared/i18n.mjs` 中的 `catalogKeys()`）映射到译文字符串，译文中的 `{placeholder}` 占位符必须与英文原文完全一致。每条消息的解析顺序为：有效的 `meta.translations` 值 → 所选内置目录 → 英语。对于内置 locale，只提供本图需要改变措辞的键；其余语言内容保持不变。省略该字段或提供 `{}` 表示不覆盖。对于没有内置目录的语言，在此处提供目录。复用 `examples/locales/` 或先前已审阅目录中合适的译文，翻译缺失的键，并用英文原文核对键和占位符。

未知的键或占位符不匹配的值会被拒绝，并保留较低优先级的消息；它会在 stderr 上报告为 `i18n/invalid-translation`，并在 `validate --json`、`deliver` 和 `finalize` 回执的 `diagnostics[]` 中作为警告报告。在非英语 locale 中仍解析为英语的键会报告为 `i18n/translation-coverage`，并附带缺失的键及其英文原文；恰好补上这些键即可修复缺口。覆盖率描述的是最终解析出的目录，而不是覆盖的规模。

对于无法提供 `meta.translations` 的所请求语言，不要写入一个既没有内置目录也没有译文的 `meta.locale`。让每一条面向读者的编写字符串保持所请求的语言，省略 `meta.locale` 以便渲染器安全地使用英语，并明确告诉用户：固定的查看器 UI 和 `<html lang>` 仍为英语，产物并未完全本地化。该回退只适用于渲染器拥有的界面；它绝不允许编写的文案回退为英语。不要静默地用 `zh-CN` 替代另一种语言或另一种中文 locale，也不要在未披露其未经审阅的情况下机器翻译 `meta.translations` 的值。

保持产品名称、代码标识符、命令、协议、API 路径和环境名称原样不变。这些术语可以在本地化文案中保留英文，但周围的解释性散文仍必须使用所选语言。渲染器拥有的默认图例标签遵循 `meta.locale`；只有当图需要不同的领域措辞时才编写 `meta.legend.entries.*.label` 覆盖，并让该编写的覆盖使用主语言。

## 视觉预设默认值 <a id="visual-preset-default"></a>

默认省略 `meta.visual_preset`。渲染器随后在浅色和深色两种配色模式下都以 `classic` 打开图。配色模式与视觉预设是相互独立的查看器状态：切换 Light / Dark 必须保留当前预设。只有当用户明确要求该视觉风格时，才编写 `signal-flow`、`blueprint` 或 `editorial`。

## 工程配置默认值 <a id="engineering-profile-default"></a>

对于普通的系统架构，省略 `meta.engineering_profile`。区域、集群和安全边界的措辞本身并不会启用工程配置。只有当用户明确要求生产部署拓扑、所有权交接或故障即关闭（fail-closed）的部署审查，且来源事实已知时，才启用 `deployment-ownership`。一旦启用，不要仅仅为了通过校验而移除工程配置；应修复编写的事实，或如实报告诊断。

## 标题层级 <a id="title-hierarchy"></a>

使用一个简洁的标题，让图本身承担解释。默认省略 `meta.subtitle`，并且绝不能用它重述标题、节点、连线或卡片。只有当用户明确要求副标题时，才加入一行简短的辅助说明；省略或空白的副标题绝不能在生成的查看器中留下空的可视行。

## 可执行的几何规则 <a id="executable-geometry-rules"></a>

为笔记本电脑和外接显示器生成一个响应式产物，保留编写的 SVG/viewBox、比例、语义几何和正常文档流。当完整的图需要更多高度时，使用有意义的内容行以及 Reader 声明的可读页面滚动行为；适配视口并不授权使用替代拓扑或更小的字体。

- 节点锚点从边的中点开始。`left`/`right` 改变水平方向的端点；`top`/`bottom` 改变垂直方向的端点。对于自动的 Architecture 关系，若两个相对端口之间无遮挡、且轴向偏移小于 16px，在两个端点都保留 16px 角部留白的前提下，它们可以共享同一条水平或垂直轴线。如果恰好只有一个端点属于展开组，则只移动其未共享的对端；两端都被展开的关系保持各自独立的端口和外侧桥接，除非一对相互对向的关系能够在保持端点间距、标签以及所有周边路径和障碍物净距的同时，共同使用各自独立的直线通道。
- 边是一种方向契约。路径的第一段和最后一段必须垂直于该边，并在指定方向上分别朝外/朝内。
- 在架构图和数据流图中，显式的 `route: "straight"` 请求一条直接线段；当端点边未被固定时，它可以是斜线。产物检查器会保留这一意图；显式边、不透明节点净距和其他质量门禁仍然适用。`via` 优先，并保留现有规则，包括数据流要求 via 线段必须正交。
- 自动端口展开（Automatic Port Spread）是架构图、工作流图和数据流图的默认渲染器行为。共享的自动端点以 16px 角部留白确定性地、对称地展开。它不适用于时序消息、单条关系，或显式的 `via`、`channelX`、`channelY`、`labelAt` 或非 `auto` 路径。
- 展示级路径节奏：每条非零线段必须至少 8px；每条内部线段必须至少 16px。当展开的端口几乎平行时，路由器使用 24px 的端点短桩和 16px 的外侧桥接，而不是制造一个微小的折弯。
- 展示级路径紧凑度：当显式 Architecture 路径的正交长度至少是考虑障碍物的合法路径的 2.5 倍、多出至少 200px、并且有控制点超出内容包络至少 96px 时，判定失败，报告 `composition/excessive-route-detour`。证据会记录两个长度、比率、超出量、边界和偏离量。应移除不必要的 `via` 或把诊断出的通道向内移动，而不是扩大画布。在同一外侧通道上重叠至少 32px 的相关关系被视为有意的总线，仍然有效。
- 共享的端点通道只有在语义上仍然无歧义时才允许。不相关的共线重叠达到 8px 或以上，展示级判定失败。
- 容器边框是有意的可穿越几何，但沿结构边框长距离行走的连线不是。
- 连线穿过不相关的不透明节点始终是硬性失败，与质量配置无关。

### 显式 `via` 坐标 <a id="explicit-via-coordinates"></a>

使用解析后的出发锚点 `S = [sx, sy]` 和到达锚点 `T = [tx, ty]`。锚点从边的中点开始，但自动路由和端口展开可能按上文所述移动它们；不要假设从自动路径中复制来的锚点就是新编写的显式路径的锚点。显式 `via` 路径不会获得自动端口展开。

对于第一个路径点 `F = via[0]` 和最后一个路径点 `L = via[via.length - 1]`，使用以下对齐方式和方向（SVG 的 y 向下增大）：

| 边 | 出发（`fromSide`）：`S` → `F` | 到达（`toSide`）：`L` → `T` |
| --- | --- | --- |
| `top` | `F[0] === sx`, `F[1] < sy` | `L[0] === tx`, `L[1] < ty` |
| `bottom` | `F[0] === sx`, `F[1] > sy` | `L[0] === tx`, `L[1] > ty` |
| `left` | `F[1] === sy`, `F[0] < sx` | `L[1] === ty`, `L[0] < tx` |
| `right` | `F[1] === sy`, `F[0] > sx` | `L[1] === ty`, `L[0] > tx` |

例如，给定底部出发锚点 `S = [180, 160]` 和左侧到达锚点 `T = [360, 260]`，下面这个关系片段向下离开，并向右进入目标：

```json
{
  "from": "source",
  "to": "target",
  "fromSide": "bottom",
  "toSide": "left",
  "via": [[180, 200], [300, 200], [300, 260]]
}
```

完整路径为 `[180, 160] → [180, 200] → [300, 200] → [300, 260] → [360, 260]`。只把第一个路径点改为 `[200, 200]` 会使出发变成斜线；把它改为 `[180, 120]` 虽保持 x 对齐，却会向上穿过源节点离开，而不是从其底部向外离开。两者都违反 `fromSide: "bottom"`，并产生 `clean-flow/endpoint-side-direction`。该示例只确立端点方向：仍须让整条路径避开不相关的节点，并应用上面的其他几何规则。

### 间距与标签 <a id="spacing-and-labels"></a>

在展示级 Architecture 中，未固定的连接标签在无冲突时保持其默认位置。如果发生碰撞，渲染器会沿现有路径尝试一组有限的邻近位置，在解析后的画布内避开节点、边界标题、其他标签和其他路径。显式的 `labelAt`、`labelDx`、`labelDy` 或 `labelSegment`（包括零值）会禁用这一回退。路径和拓扑保持不变；如果没有空闲的邻近位置，校验会报告原始碰撞。在添加控制之前，用 `--layout-json` 检查解析后的标签。标准放置保持其现有行为。

间距建议指的是框之间的净间隙，而不是中心距离。宽 165px 的节点之间若中心距离为 200px，只剩 35px 的净间隙。

对于关系标签，要求：

```text
clear gap > label mask width + 8px breathing room
label mask width ≈ 6.5px × ASCII units + 13px
CJK characters count as two units
```

关系标签是语义数据。如果间隙太小，先移动标签，再调整路径或间距，然后在保留含义的前提下缩短措辞。只省略两个端点已完全隐含、且不携带任何协议、动作、方向、同步/异步行为或跨边界机制的措辞。保留每一个有意义的标签。删除它不是间距修复。如果某条关系因为其端点已完全隐含其含义而一开始就不带标签，要解释该措辞为何多余；这是语义编写上的选择，而不是间距修复。在 workflow v2 中，先让编译器分配其测量得到的遮罩，再应用经诊断的 `labelAt`、`labelDx`/`labelDy` 或 `labelSegment`。一次只应用一项经诊断的几何控制，除非多条连线共享一条受限通道。在那种情况下，依据测量的几何规划最小的联动修改，并一并校验。Architecture/workflow 通过 `validate <type> <candidate.json> --layout-json` 提供布局证据；其他类型则使用校验诊断和渲染出的 SVG 几何。在添加手动路径之前，检查是否有不必要的、由代理添加的控制禁用了自动端口展开；保留用户要求的路径意图。使用上面测量得到的净距规则，而不是猜测坐标。

### 修复证据 <a id="repair-evidence"></a>

对于架构图，`validate architecture <input.json> --layout-json` 会公开解析后的组件框、边界框、连接点和标签位置。可测量但被拒绝的布局同样会返回这些字段，并带有 `ok: false`、`contract: "archify-architecture-layout-v1"`、诊断以及退出码 1。这是修复证据，而不是产物验收；它不写出 HTML。格式错误的输入或实现故障会保留普通的失败回执，不带布局。

对 `layout/boundary-out-of-bounds`，使用测量出的失败边。左/上的负坐标需要向内移动；增大 viewBox 的宽/高只能解决右/下溢出。边界可以让成员跨行换行。保持真实的成员关系不变，并在移动成员后重新检查相连的路径。

自动架构画布除了节点、框和标签之外也包含路径点。编写的 viewBox 仍具权威性。在展示级中，`layout/route-out-of-bounds` 会标识被裁切的路径点；负坐标需要向内调整路径，而右/下溢出也可以通过更大的编写画布解决。扩大画布后要重新检查桌面端可读性。

当多个交叉/通道诊断涉及相同的节点时，在添加路径控制之前，先整体考虑它们的放置。应用一个连贯的修复并校验；独立的标签微调无法解决共享的布局瓶颈。按 code、subject 和阶段比较诊断，而不只是比较总数。

### 修复顺序 <a id="repair-order"></a>

1. 修复缺失/无效的 `meta.quality_profile` 和 schema 错误。
2. 修复节点重叠或越界放置。
3. 修复连线穿过节点和端点方向错误。
4. 修复交叉、含混的通道、沿边框走线、过度绕行和路径节奏。
5. 修复标签与节点、标签与标签、再到标签与路径的净距。
6. 修复超出画布的标签：用 `labelAt`/`labelDx`/`labelDy`/`labelSegment` 移动标签，或加宽 `meta.viewBox`。建议的 `labelDx`/`labelDy` 值会替换编写的字段；它们不会叠加到该字段上。

每次编辑后，按交付契约的要求重新运行完整的 `finalize`；只在两次 finalize 之间做针对性诊断时使用 `validate`。按稳定的 `code`、确切的 `subject`、测量的 `evidence` 和 `supportedFixes` 使用 `diagnostics[]`。如果诊断给出了 `labelAt`，就使用该点，而不是估算另一个偏移。

## 各模式的放置 <a id="mode-placement"></a>

### Architecture <a id="architecture"></a>

依据 [Composition and meaning](authoring-defaults.md#composition-and-meaning) 选择概览还是机制细节。使用一条明显的主阅读路径；当所请求的拓扑需要空间时，它可以跨越有意义的行。让概览在所选抽象层级上保持可读；当实现细节能回答读者的问题时，再展开它们。只对真实的所有权、信任、进程或部署边界进行分组。边界不能替代关系。

在 schema 支持时，优先使用网格放置。自由位置适用于有限的例外，而不适用于在散文层面规划坐标。当外部参与者在事实上位于系统边界之外时，要把它们放在边界之外。边界被绘制为包围其全部成员的带内边距的框，因此要把成员放成一个紧凑、轴对齐的簇（不留可让非成员落入带内边距框内的空槽），并让每个非成员都位于该框之外；在展示级质量下，`layout/boundary-encloses-non-member` 会报告被该框吞入的组件。标准级保持其现有验收行为。

### Workflow <a id="workflow"></a>

泳道表达职责或阶段。列 `0..5` 表达逻辑上的推进。新工作流从 `readable-v2` 开始；只为兼容旧几何而保留 `fixed-v1`。在 readable-v2 中，当不同的 `yOffset` 值为节点的完整矩形、标签和相连路径留出空间时，节点可以共享同一个 `(lane, col)`。保持主流程（happy path）单调推进，保留语义连线标签，并把重试和异常返回路由到主泳道通道之外。

#### 工作流视口修复 <a id="workflow-viewport-repair"></a>

当 `viewer/viewport-overflow` 包含 `workflowLanes` 时，在修改源文件之前，先检查渲染出的最高的框及其节点跨度。测量值为 CSS 像素；节点上方/下方的空间包含泳道标题和走线，因此不是可移除空间的预算。框 ID 标识的是渲染后的泳道索引。

运行 `validate workflow <source.json> --layout-json`，把这些框与源文件中的泳道和节点对应起来。检查是否有许多步骤共享最后一个逻辑列并使用了较大的 `yOffset` 值。readable-v2 会在偏移周围保留对称空间。对于同列垂直堆叠、隐式画布、且没有绝对路径或标签固定的情况，它会独立测量每条泳道。其他情况为兼容起见保留共享高度的几何；参见规范的 [lane measurement contract](../renderers/workflow/README.md#readable-v2)。

在源文件的所有权和显式几何允许的情况下，把步骤重新分布到各个逻辑列和有意义的泳道上，并保持主路径单调推进。保留每一个必需的节点、关系、标签和语义检查。如果所有权或绝对固定阻止重排，就报告该约束，而不是合并泳道或自动移动固定点。校验修改后的 JSON，交付一个新的 HTML，然后重新运行浏览器检查并查看首屏；仅凭静态检查通过并不能确定视口适配。这些是修复方向，而不是保证的坐标。

### Sequence <a id="sequence"></a>

参与者按对话角色排序。消息拥有自己的垂直顺序。使用 return/async/security 变体是为了表达含义，而不是装饰；时序图不使用自动端口展开。分段的 `from`/`to` 边缘必须与每条消息箭头（`message.y`）保持至少 4px 的距离：沿箭头走的边缘会让读者无法判断该消息属于哪个阶段，展示级质量会报告 `sequence/segment-message-border-run`。标准级保持其现有验收行为。

初稿结构：每条消息都需要 `id`、`from`、`to`、`label`，以及至少为 160 的整数 `y`。`from` 和 `to` 必须是不同的参与者——不支持自消息（`sequence/self-message-unsupported`）。可选的阶段带是 `segments[]`，只含 `from`、`to` 和 `label`（分段没有 `id`）。在参与者上臆造 `pos`/`size` 会导致 schema 校验失败——仅靠顺序就能放置它们。省略 `meta.viewBox`，这样自动高度会适配时间线 + 图例（最小 327px 的可读带），而不是固定的 760px 下限；并且在标签放得下时，2–3 个参与者的跨度会紧凑排布在 920px 默认值以内（4 个及以上保持 920px；长标签仍会加宽）。

### Dataflow <a id="dataflow"></a>

阶段表达转换或保管关系。行把并行的数据流分开。给每条流一个简洁的数据契约或移动标签；依据必需的 [Dataflow authoring defaults](authoring-defaults.md#presentation-and-modes) 选择其视觉约定。

初稿结构：声明 `stages[]`（每项为一个 `{label}`），然后用整数 `stage` 和 `row` 放置每个节点——不用 `pos`/`size`。流为 `flows[]`，必须包含 `from`、`to` 和非空的 `label`。

省略 `meta.viewBox`，即可在任一质量配置下让画布宽度适配所有阶段和节点，包括显式的节点宽度。宽度取内容 + 24px 右侧内边距，最小 480px（五个默认阶段仍需约 1068）；左边缘溢出仍需要修复节点。编写的 viewBox 保持固定。展示级的节点增长、可读字体、内容高度、端口桥接和有限的标签放置，只在画布和所有节点宽度都省略时才生效。`--quality` 会覆盖 `meta.quality_profile`；没有它时，若设置了 `ARCHIFY_QUALITY_PROFILE`，渲染器就使用它，否则使用 JSON 中的配置。

### ERD <a id="erd"></a>

把 schema ERD 既当作表目录，也当作关系图。如果 schema 有超过 8 张表或 50 个字段，它就是一张密集的全量 schema 图：从 `meta.quality_profile: "standard"` 开始，以免为了反复进行展示级路径修复而牺牲完整的字段可见性。在 `attributes` 中包含每一个物理列，保留源 SQL 类型，并把字段的中文注释以 `SQL_TYPE｜中文备注` 的形式保留在类型字符串中，因为 schema 没有单独的注释属性。默认查看器在 `read` 级别显示这些行；不要依赖悬停/聚焦或卡片来展示物理字段。卡片可以解释约束、推断出的关系或领域规则，但绝不能替代字段列表。

在放置框之前，依据经核实的表名、注释、模块路径和外键含义，把表划分到各个功能领域。把领域名称放进 `tag`，并给每个领域一个由网格单元组成的实心矩形：单独一行、单独一列，或一个填满的矩形块——不能是 L 形或对角线——且矩形的每个单元都放着该领域的一张表。同一 tag 的所有表保持在一起；不要在成员之间穿插不相关的表。填满这样一个矩形的领域会被绘制为位于其表后方的带标签色带，因此无需逐个阅读框即可看出分组；表未填满一个矩形的 tag 不会得到色带，而由于色带是唯一绘制领域名称的地方，渲染器会报告 `erd/domain-not-drawn`，而不是发布一张无法标出该领域名称的图。绝对坐标根本没有网格单元，因此带 tag 的表始终需要 `row`/`col`。把父表/核心表排向共享边界，并把它们的直接子表放在旁边或下方。列从左到右阅读，行从上到下阅读，因此相邻列之间的关系是一条笔直的通道。绝不要在两个对齐的锚点之间放置不相关的实体；路由器可以绕开它，但畅通的通道更短、更易读。关联表有两个父表：把它放在两者旁边或之间的单元中，而不是放在其中一个的下方、且它与另一个之间隔着堆叠的表；并让共享其领域 tag 的每张表都位于一个由单元组成的实心矩形中。关系必须连接两个不同的实体；像 manager_id 这样的自引用保持为外键列（可选地配一张卡片），而不是一条 `employees`→`employees` 连线。这种常规分组布局使用 `row`/`col`，只有在诊断指出具体的几何问题之后才使用显式的 `pos`/`via`。

在 `key` 中写明一列承担的每一种键角色，在 `references` 中写明真实的引用。一列往往同时承担不止一种角色——关联表的 `tenant_id` 既是主键的一部分，又是指向 `tenant.id` 的外键——因此 `key` 接受一个角色或一个列表（`["pk", "fk"]`），丢掉一个角色就等于声明得比 schema 少。多对多关系是关于模型的真实事实，因此要写明它，并在存在关联表时标出该表。关系有两端，每一端声明自己的最大值，因此 `many` 对 `one` 的外键需要同时有 `fromCardinality` 和 `toCardinality`；`fromOptional`/`toOptional` 只把同一端的最小值从一降到零（可选的 `one` 端读作零或一，可选的 `many` 端读作零或多），而 `identifying: false` 绘制非标识性的虚线并拥有该虚线——schema 会拒绝在其旁边把关系绘制为实线的 `variant`。鸦脚朝向它所描述的实体张开，因此所绘制的符号表达的是该端的最大值，而不是行进方向。

一张表的一条边只能容纳有限数量的端点：端口之间最多展开 `(side
extent - 32) / (ends - 1)` 的距离，而基数符号高 14 个单位。关系端点数超过该空间所能容纳的数量即为 `layout/marker-capacity`，它会指出是哪张表、哪条边，以及解决办法——添加字段让该边更高、把关系分散开，或减少汇入数量。绝不能通过隐藏基数来修复它。

当模型必须在笔记本视口内完整阅读时，给每个领域各一列。Reader 会把宽画布放大到阅读宽度，并把高画布缩窄直到整页放得下，因此同样的十一张表，若堆叠为四个水平领域而不是四个垂直领域，就要付出文字尺寸的代价。在长关系必须穿过某个领域的地方，留出网格中一整格空位：穿过被占用单元的走线会被迫折弯，而低于内部下限的折弯会导致 `composition/short-interior-segment` 失败。

自动画布的尺寸保证默认图例始终位于生成内容之中，而作者用 `meta.viewBox` 固定的画布会报告其图例容量，而不是丢弃图例；色带、端口和读者契约参见 [`../renderers/erd/README.md`](../renderers/erd/README.md)。

### Tree <a id="tree"></a>

树回答"这是如何分解的？"：一个根节点，其他每个节点恰好指定一个 `parent`。连接只表示包含关系；不要用树表示调用、数据移动或跨分支依赖。不做任何推断：缺失的父节点（`tree/missing-parent`）、零个或多个根（`tree/root-count`）、父级环（`tree/cycle`，它也涵盖滞留在其下方的每个节点）以及重复的 id 都会被拒绝。子节点按声明顺序阅读。

对浅而均衡的分解使用 `layout.direction: "down"`（默认），对深的或叶子很多的树（例如仓库布局）使用 `"right"`；向右的树让每个父节点与其第一个子节点对齐，并在阅读器中垂直滚动。标签在词与词之间换行。`collapsed: true` 让一个分支在查看器中初始为折叠状态；它绝不会从产物中移除内容，并且每次导出都是完整的树。对于真实的代码库，让每个节点都以观察到的路径为依据，并附上 `sources`。参见 [`../renderers/tree/README.md`](../renderers/tree/README.md)。

### Class <a id="class"></a>

类图解释一个模块内部的契约：存在哪些类型、哪些成员对解释有意义，以及类型之间如何关联。选择问题所需的成员；一个类型可以不显示任何成员。每个类型声明其 `kind`（`class`、`abstract`、`interface`、`enum`、`record`）；除 `class` 外的每种 kind 都会绘制其 UML 关键字，因此接口绝不会被读作空类。对于真实的代码库，让每个类型、成员和关系都以仓库证据为依据，并附上 `sources`。

每条关系按 `from` -> `to` 阅读，其 `kind` 决定表示法：`dependency`（`from` 使用 `to`，虚线开放箭头）、`association`（`from` 持有一个 `to`，实线开放箭头）、`inheritance`（`from` 继承 `to`，实线空心三角）、`realization`（`from` 实现接口 `to`，虚线空心三角）、`composition` 和 `aggregation`（`from` 是整体，在 `from` 处为实心或空心菱形）。Realization 必须从非接口指向接口；inheritance 绝不能跨越接口边界；继承环会被拒绝。

把类型放在 `row`/`col` 网格上，超类型位于其子类型之上。两个或更多指向同一超类型的自动泛化会绘制为一条层级总线，只带一个三角。成员绝不会被截断：类型会增宽到其最宽成员，上限为 `layout.typeMaxW`，更长的成员在参数边界处换行。参见 [`../renderers/class/README.md`](../renderers/class/README.md)。

初稿结构：类型使用 `row`/`col`（不用 `pos`/`size`），字段放进 `attributes[]`，操作放进 `methods[]`，其中 `parameters` 是一个字符串，例如 `"msg: Message"`（而不是对象数组）。枚举成员是只有 `name` 的 attributes。关系需要 `id`、`from`、`to` 和 `kind`。

### Timeline <a id="timeline"></a>

时间线回答"什么时候发生了什么，彼此相隔多久？"。每个事件都需要一个 ISO 8601 的 `at`，带有显式的 `Z` 或 `±HH:MM` 偏移；没有偏移的时间戳会被拒绝，而不是被猜测。`meta.timezone`（IANA，默认 `UTC`）是刻度和标签的显示时钟，轴标题会写明它。`meta.evidence` 为必需：记录下来的事件（日志、git 历史、告警寻呼记录）用 `observed`，解释性输入用 `illustrative`。绝不能把编造的或近似的时间标为 observed，也绝不能用输入中不包含的事件填补空白。

用 `lanes` 表示来源或类别（发布、监控、响应）；此时每个事件都要指定其中一个。每个事件的可见文本是 `title`（不是 `label`）。`kind`（`default`、`change`、`alert`、`action`、`recovery`）只决定卡片的颜色；臆造诸如 `milestone` 的值会导致 schema 校验失败。无论编写顺序如何，事件都按时间顺序绘制；同时发生和相近的事件会堆叠。默认情况下，长于中位间隔 8 倍且超过跨度 10% 的平静期，会被绘制为固定宽度的断层，并标注被省略的时长；`layout.breaks: "none"` 保持一条按比例的轴。参见 [`../renderers/timeline/README.md`](../renderers/timeline/README.md)。

### Waterfall <a id="waterfall"></a>

瀑布图针对一个请求、作业或代理运行回答"时间都花在哪儿了？"。每个 span 都有 `id`、`name`、`start`，以及以 `meta.unit`（`us`、`ms`、`s`；默认 `ms`）为单位的 `end` 或 `duration`，另可选 `parent`、`status`、`service` 和 `detail`。条形的位置和长度只来自这些数字。`meta.evidence` 为必需：只有记录下来的计时（trace 导出、日志、性能分析器、计时运行）才用 `measured`；否则用 `illustrative`。绝不能从代码结构推断时长，也绝不能把估算的数字当作测量值呈现。

没有记录结束时间的 span 必须为 `status: "incomplete"`；它被绘制为一直延伸到最后记录时刻的开放下界。相互矛盾的 end/duration、早于开始的结束、缺失的父级或父级环都会被拒绝。百分比始终是"占墙钟总时长的比例"；父级和子级时长是包含关系，绝不相加。除非输入写明了依赖关系，否则不要标注关键路径或等待时间。参见 [`../renderers/waterfall/README.md`](../renderers/waterfall/README.md)。

### Lifecycle <a id="lifecycle"></a>

Schema v3 是唯一的生命周期契约。`mainPath` 列出从初始状态开始的主流程；每一对相邻状态都需要一个转换。渲染器掌控全部几何：主路径是一行，回到较早阶段（或向前跳过）的转换变成其上方的弧线，其他每个状态位于其分支来源状态的下方，每离开主路径一步就下移一行。只有当等价出口的标签、注释和变体都相同，并且对该目标恰好有一组来自至少两个主路径阶段的出口符合条件时，它们才共享一个箭头。相邻的阶段会得到一个组合框；不相邻的阶段共享一条总线。其他出口保持分离，包括在其原始转换上带有不同注释的出口。不要为了强行共享而移除或复制注释。没有泳道、列、尺寸或路由控制。布局重试会保留转换文字的最小间隙，并在主路径行的最小宽度将超过原始文字可读性预算时停止加宽该行；最终的宽度和标签净距检查仍然适用。

让主路径只包含读者要跟随的阶段，最多约六个状态，并保持转换标签简短。可恢复的失败需要一个回到活动状态的真实转换；写着"重试"的卡片不是拓扑。

依据读者应注意到的内容为每个状态选择 `type`，因为颜色和角落标记随之而定：等待某人、时间或输入的暂停用 `waiting`；审核或分支点用 `decision`；好或坏的结果用 `success` 或 `failure`；搁置的状态和既非好也非坏的结果用 `neutral`；工作由外部方持有时用 `external`；其他情况用 `active`。从 Mermaid `stateDiagram` 转换时，`[*] -->` 指定第一个 `mainPath` 状态；带有 `--> [*]` 的状态是一个结果（`success`、`failure` 或 `neutral`；当它没有其他出向转换时绘制为终态）；`<<choice>>` 变为 `decision` 状态。把组合状态 `state X { ... }` 展平为其内部状态，并以同一个标签从每个内部状态重复其出口；共享该出口的相邻主路径阶段会被自动加框。并发区域（`--`）没有生命周期形式：每个区域各画一张生命周期图。

## 仓库证据 <a id="repository-evidence"></a>

当图必须反映真实代码时，在编写之前先检查仓库的入口点、运行时边界、存储、传输方式和部署配置。只记录你实际核实过的证据。`--repo-root <path>` 被所有图类型的 `render`、`validate`、`deliver` 和 `preview` 接受，也被架构图的 `compare` 和工作流的 `migrate` 接受；每种模式都以相同方式核实 `meta.repository` 和节点 `sources`。迁移有来源支撑的工作流需要同样的 `--repo-root`，以便在替换目标之前核实其候选稿。绝不能仅凭文件相邻或命名推断运行时因果关系。

声明 `meta.repository.url` 和一个完整的 40 字符 `revision`，然后把 `sources` 附加到该模式的节点集合上（Architecture 的 `components[]`、Workflow 和 Data Flow 的 `nodes[]`、Sequence 的 `participants[]`、Lifecycle 的 `states[]`），包含相对于仓库的 `path`，以及可选的 `line`、`end_line` 和 `label`。核实读取的是该提交下的 blob，与工作区中的修改无关。核实会忽略本地 Git replacement 引用，包括由 `GIT_REPLACE_REF_BASE` 选中的那些，并始终读取固定 SHA 下的原始对象。它不会更改仓库配置，也不会删除 replacement 引用。在每种链接模式下，都要求有匹配的本地 origin、可用的提交、有界的路径、blob 以及有效的行范围。核实在本地进行，不发出任何远程请求；它既不能证明公开可用性，也不能证明当前读者的访问权限。

`link_mode` 默认为 `web`。GitHub、Gitee 和 GitLab 的 HTTPS 仓库 URL 会生成固定到 revision 的链接；公共主机 github.com、gitee.com 和 gitlab.com 会自动选择提供方。可选的 `provider: "github"`、`"gitee"` 或 `"gitlab"` 必须与公共主机一致。自建 GitLab 主机要声明 `provider: "gitlab"`；Archify 绝不会联系主机来探测其代码托管平台类型。现有的 GitHub 声明和默认交付回执字段保持兼容。

GitLab URL 可以包含嵌套组（`group/subgroup/project`）。源链接使用 `<url>/-/blob/<revision>/<path>#L<line>-<end_line>`，仓库链接使用 `<url>/-/tree/<revision>`。带行范围的 Markdown 源文件（`.md`、`.markdown`）会链接到纯文本视图（`?plain=1`），以便高亮所引用的行，而不是显示渲染后的文档。GitLab 仓库路径与 GitHub 一样，比较时不区分大小写。

```json
{
  "url": "https://gitee.com/team/service",
  "revision": "0123456789abcdef0123456789abcdef01234567",
  "provider": "gitee"
}
```

```json
{
  "url": "https://git.example.com/platform/payments/service",
  "revision": "0123456789abcdef0123456789abcdef01234567",
  "provider": "gitlab"
}
```

对于内部或不受支持的代码托管平台，选择 `link_mode: "local-only"`。查看器保留 SRC 标记、可搜索的文件路径、行范围和 revision 标签，但不带仓库或源文件超链接。证据回执会添加 `linkMode: "local-only"`。`url` 仍为必需，作为期望的 origin 标识；local-only 禁用的是链接，而不是标识核实。不支持没有 origin 的仓库。

```json
{
  "url": "http://git.internal:3000/Platform/Services/service",
  "revision": "0123456789abcdef0123456789abcdef01234567",
  "link_mode": "local-only"
}
```

Local-only 接受 HTTP(S)、`git@host:path` 和 `ssh://git@host[:port]/path` 地址，包括嵌套命名空间。声明一个不含凭据的地址；检出仓库 origin 上的 HTTP(S) 凭据在标识比较时会被忽略，并在诊断中被脱敏。主机名比较不区分大小写；仓库路径保留大小写，GitHub 和 GitLab 除外。末尾的斜杠会被规范化去除。只有 GitHub、Gitee 和 GitLab（gitlab.com，或用 `provider: "gitlab"` 声明的主机）会规范化末尾的 `.git`，并把同一主机上的标准 HTTPS/443 与 Git SSH/22 视为匹配；不会推断位于其他主机或端口上的 GitLab SSH 端点。对于其他主机，使用实际的克隆地址：传输方式、端口、`.git` 后缀，以及相对远端路径与绝对路径都必须匹配。例如，`git@host:Team/repo` 与 `ssh://git@host/Team/repo` 不同；`git@host:/Team/repo` 与后者匹配。SCP 风格的路径保留字面的百分号转义，而 URI 路径会对其解码。不会猜测 SSH 主机别名和代码托管平台特有的浏览/克隆前缀。本版本未实现 Gitea/Forgejo/Bitbucket 的网页链接；在有经过测试的链接提供方之前，请使用 local-only。未知的网页提供方会以诊断失败，而不是生成猜测的链接。

## 手工放置回退 <a id="hand-placed-fallback"></a>

只在没有任何渲染器能运行时使用。从 `assets/template.html` 开始，保留语义 CSS 类，保留内联 SVG/无障碍结构，并执行交付视觉检查清单。绝不能引入会破坏深色/浅色一致性的内联字面颜色。

## 节点图标 <a id="node-icons"></a>

对于特定领域的图，可以在架构组件、工作流/数据流节点、时序参与者或生命周期状态上设置可选的 `icon`。日常概念选择 `calendar`、`clock`、`person`、`briefcase`、`flag` 或 `moon`；完整目录（包括现有的技术和生命周期符号）为 `common.schema.json#/$defs/nodeIcon`。使用 `icon: "none"` 隐藏角落符号。省略 `icon` 则保持基于类型的默认值；生命周期的 `start`、`active` 和 `neutral` 状态默认没有符号。这些内联 SVG 符号由渲染器拥有，并随图一起导出；不接受 URL 和原始 SVG。

图标选择只改变角落符号。节点的类型仍然决定颜色和语义分组；品牌标志保持独立。对于假期工作流，把 `type: "backend", icon: "calendar"` 与 `meta.legend.entries.backend.label: "假期"` 搭配使用，并为调休补班使用 `icon: "briefcase"` 加上合适的图例标签。让节点标签保持有意义：图标是装饰性的，并对辅助技术隐藏。

完整的工作流示例参见 [holiday planning](../examples/holiday-planning.workflow.json)。
