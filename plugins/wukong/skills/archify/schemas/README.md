# Archify JSON IR Schema 说明

每个类型化渲染器都消费一份 JSON 中间表示（IR），在进行任何布局工作之前，
它都会先按本文件夹中的某个 schema 进行校验。

## 文件

| Schema | 约束对象 | 结构数组 |
|--------|---------|-------------------|
| `workflow.schema.json` | `diagram_type: "workflow"` | `lanes`, `phases`, `groups`, `mainPath`, `nodes`, `edges` |
| `sequence.schema.json` | `diagram_type: "sequence"` | `participants`, `segments`, `messages`, `activations` |
| `dataflow.schema.json` | `diagram_type: "dataflow"` | `stages`, `nodes`, `flows` |
| `lifecycle.schema.json` | `diagram_type: "lifecycle"` | `mainPath`, `states`, `transitions` |
| `architecture.schema.json` | `diagram_type: "architecture"` | `components`, `boundaries`, `connections` |
| `erd.schema.json` | `diagram_type: "erd"` | `entities`, `relationships` |
| `tree.schema.json` | `diagram_type: "tree"` | `nodes`（每个都有一个 `parent`） |
| `class.schema.json` | `diagram_type: "class"` | `types`, `relationships` |
| `timeline.schema.json` | `diagram_type: "timeline"` | `events`（`lanes` 可选） |
| `waterfall.schema.json` | `diagram_type: "waterfall"` | `spans`（每个都有可选的 `parent`） |
| `common.schema.json` | 只有共享的 `$defs`（没有顶层文档） | — |

每个图 schema 都要求 `schema_version`、`diagram_type`、`meta`（含
`title` 和一个持久、可移植的 `output`）及其结构数组——但 `segments`、`activations`、ERD 和 class 的
`relationships`，以及 `cards` 是可选的——并在每一层都设置 `additionalProperties: false`，
因此未知字段会被拒绝，而不是被悄悄忽略。

每个 `meta` 对象还接受 `animation: "trace"`，用于在生成的 HTML 中按需启用
SVG/CSS 动画。省略它或设为 `"none"`，即得到默认的静态输出。
它还接受 `locale`，即任何格式正确的语言标签（schema 模式
`^[a-z]{2,3}(-[A-Za-z0-9]{2,8})*$`）。该字段选择查看器的固定 UI、
渲染器自有的默认图例与无障碍文案、文档标题后缀，
以及 `<html lang>` 值；它不会翻译编写的字符串。登记在
`locales/manifest.json` 中的内置语言目录（`en`、`zh-CN`、`zh-TW`、`es`、`ko`、`ar`）按标签
选择，不区分大小写；地区和文字变体是不同的
标签。任何其他标签都需要一个匹配的 `translations` 对象（见下文），否则
渲染器回退为英文并予以说明。
省略 `locale` 会保留旧有行为，解析为英文。
格式错误的 locale 标签会在 schema 校验时失败，而不会被猜测或
悄悄改写。

`meta.translations` 是可选的按键覆盖，以数据形式提供：一个对象，把
规范消息键（`locales/en.json`）映射到译文字符串，其中的
`{placeholder}` 标记必须与英文源一致。每条消息的解析顺序为：
有效的 `translations` 值 → `locale` 对应的内置语言目录 → 英文。
无法识别的键或不匹配的占位符绝不会替换一条有效的
较低优先级消息，也不会导致渲染失败；`validate`/`render`/`deliver`
会把被拒绝的条目以及最终解析覆盖率报告到 stderr。
`visual_preset` 接受 `classic`（稳定的默认值）、`signal-flow`（发光、
以动画为主的呈现）、`blueprint`（高对比度的工程评审）
或 `editorial`（温暖的出版风格设计评审与文档）。
预设只改变查看器样式；它们不会改变语义 ID 或几何。
Sequence 的 `meta` 还额外接受 `column_fit`。无论是否提供 `meta.viewBox`，默认值都是 `spread`。
显式的 `fixed` 保留历史上 108px 的列间距和 86px 的参与者
方框。`spread` 根据 viewBox 推导列距和方框宽度，
参与者卡片之间至少留 16px 的间隔，从而把
宽画布转化为列距和标签空间，而不是右侧的空白。
无论哪种方式，泳道顺序、ID 和消息语义都不变。

`meta.views` 已停用。schema 仍接受旧的引导视图形态，使
现有文件继续通过校验，但渲染器会忽略它；不要编写它。

### 图例呈现契约

每个 `meta` 对象都接受相同的可选图例形态，且不会改变
该渲染器已选定的 schema 版本：

```json
"legend": {
  "mode": "auto",
  "entries": {
    "security": { "label": "restricted data", "visible": true }
  }
}
```

`mode` 为 `auto`（默认值）、`all` 或 `hidden`。`auto` 只包含
类型化 IR 中出现的类型；`all` 包含渲染器完整的稳定目录；
`hidden` 移除整个图例，并优先于条目覆盖。
省略显式 `viewBox` 的 Architecture 文档，会依据最终 SVG 布局所用的同一份
实测解析后的图例占用尺寸来确定自动 viewBox。
在所有渲染器中，省略 `meta.legend` 的旧文档使用一个
兼容安全的隐式 `auto`：若解析后的图例无法在不重叠的情况下放入
显式编写的 viewBox，Archify 会省略整个图例，
而不是把一个先前有效的 schema-v1 文档变成硬失败。
一旦作者添加了 `meta.legend`（包括显式的 `mode: "auto"`），
布局即视为有意为之，放不下的标签或区带会失败，并给出带路径前缀的
诊断。条目可以设置非空且有长度上限的 `label`、布尔值 `visible`，
或两者都设。
`visible: false` 移除一个已解析的条目，`visible: true` 强制把一个受支持
但未使用的类型放入可视图例。未知的类型和属性会在
严格校验中失败。

受支持的键由渲染器自有：

| 渲染器 | `meta.legend.entries` 键 |
|---|---|
| Architecture | `frontend`, `backend`, `database`, `cloud`, `security`, `messagebus`, `external` |
| Workflow | `frontend`, `backend`, `security`, `messagebus`, `database`, `cloud`, `external` |
| Sequence | `emphasis`, `return`, `security`, `dashed`, `default` |
| Dataflow | `emphasis`, `security`, `dashed`, `database`, `default` |
| Lifecycle | `start`, `active`, `waiting`, `decision`, `success`, `failure`, `neutral`, `external` |
| ERD | `pk`, `fk`, `uk`, `one`, `many`, `optional` |
| Class | `dependency`, `association`, `inheritance`, `realization`, `composition`, `aggregation` |

标签只用于呈现：它们不会重命名稳定的类型、改变
节点/关系，也不会产生 Semantic Lens 连线事实。Sequence 消息和
Dataflow 流 variant 条目是视觉键。由确切的已编译节点事实支撑的组件/状态条目
会获得交互式 Semantic Legend 桥接；
这包括存在真实 `nodes[].type: "database"` 事实时的 Dataflow `database`。

每个关系集合（`connections`、`edges`、`messages`、`flows` 和
`transitions`）都接受一个可选的、由作者控制的 `id`，使用共享的 ID
模式。渲染器会另外保留按源顺序生成的运行时键，而
编写的 ID 则启用一个稳定的 `#relation=<id>` 查看器链接，在数组
重新排序后依然有效。没有 ID 的文档仍然有效，其关系固定链接仅
在当前页面内有效。

每个语义节点集合（`components`、`nodes`、`participants` 和
`states`）还接受一个可选的 `brand`：要么是 `archify brands --json`
返回的规范字符串，要么是 `archify brands capture <url> --json` 返回的、
以摘要固定的 `{ "url", "sha256" }` 对象。已知 ID 和已知品牌
域名使用内置的矢量目录。未知 URL 必须在编写前通过该
显式命令采集；render 和 validate 绝不执行
未固定的网络采集。不安全、不可用、已变更或不受支持的内容
会以失败关闭，并给出品牌诊断。省略 `brand` 会保留先前的
输出。

## schema_version 策略

Workflow 支持 schema 版本 1 和 2。版本 1 仍是固定布局的
兼容契约；版本 2 选用可读的 workflow 编译器，
可通过 `archify migrate workflow ... --to-schema 2` 显式生成。
Lifecycle 只接受版本 3，即自动的主路径布局（见
[lifecycle 渲染器](../renderers/lifecycle/README.md)）。
其余三个图 schema 将 `schema_version` 固定为 `1`；它们
没有 schema 版本迁移命令。对于五种图类型中的任何一种，在源文件中修复
旧版缺失或不可移植的 `meta.output`，然后运行 `validate`。
专门针对 workflow 从 v1 到 v2 的迁移，`migrate workflow` 还接受
`--output reports/diagram.html`，把该可移植值写入单独的 v2
目标，而不改变旧的源文件。

Workflow 还接受可选的 `semanticChecks`。`allowedRoots` 和
`allowedTerminals` 封闭有意设置的图源点和汇点集合；
`requiredEdges` 要求确切的已编写关系；`requiredPaths`
要求有向可达性，同时允许中间节点。编译器
在布局之前评估这些事实，并返回类型化的 `workflow/*` 诊断。
该字段是增量的且不影响几何：省略它会保留现有
workflow 行为，而包含一个已满足的契约不会改变 SVG 或
布局回执的字节。

今天能通过校验的文件，在整个 2.x 发布线内都必须在其
声明的版本下继续通过校验并正常渲染。经过明确评审的
可移植输出加固是唯一的例外：省略
`meta.output` 的旧 v1 文档必须添加一个可移植的 POSIX 相对 `.html` 路径（例如
`reports/diagram.html`）；普通的显式 CLI 输出参数不能替代
这个持久的编写值。仅限 workflow 的 v1 到 v2 迁移命令可以
改为通过 `--output reports/diagram.html` 显式接收该值；它
只把该值写入其单独的、已校验的目标。增量的查看器、
无障碍和呈现改进可以增强生成的 HTML，但
它们绝不能重新解释已编写的 IR，或把一个先前有效、无 profile 的
v1 文件变成新的硬布局失败。破坏性的 IR 变更需要新
版本；增量的、向后兼容的字段则不需要。

## 共享定义（common.schema.json）

五个图 schema 引用 `common.schema.json#/$defs/...`：

- `id` — 元素标识符，模式为 `^[a-zA-Z][a-zA-Z0-9_-]*$`
- `point` — 由两个数字组成的 `[x, y]` 对（供 `via` 和 `labelAt` 使用）
- `componentType` — `frontend`、`backend`、`database`、`cloud`、`security`、
  `messagebus`、`external`
- `locale` — 格式正确的渲染器 locale 标签（内置语言目录列在
  `locales/manifest.json` 中；任何其他标签都需要一个匹配的 `translations` 对象）
- `translations` — 规范消息键 → 译文字符串，叠加在
  `locale` 对应的内置语言目录之上，再往下是英文
- `portableOutputPath` — `meta.output` 使用的可移植 POSIX 相对 `.html` 路径；
  参见
  [交付契约](../references/delivery-contract.md#output-path-contracts) 中的两条输出路径边界
- `brandMark` — 一个可选的内置品牌 ID 或显式的 HTTP(S) 站点 URL
- `variant` — `default`、`emphasis`、`security`、`dashed`（sequence 消息
  在本地用 `return` 扩展此列表）
- `legendMode` 和 `legendEntry` — 共享的严格模式以及标签/可见性
  覆盖形态，供每个渲染器自有的键映射使用
- `guidedViews` — 已停用的 `meta.views` 形态，仍被接受但会被忽略
- `cards` — 渲染在 SVG 下方的摘要卡片块

Lifecycle 状态的 `type` 是模式特有的（`start`/`active`/`waiting`/...），
保留在 `lifecycle.schema.json` 中。

JSON Schema 定义是可移植契约中能以结构表达的
预检部分。随附的生成式校验器包装器和 CLI 还会额外强制
基于字节的组件限制以及完整的运行时路径契约；需要
相同跨平台接受边界的使用方应使用该包装器。

## 运行时校验

在开发阶段，`scripts/generate-validators.mjs` 使用 ajv 的 draft 2020-12 独立生成器，
以 `strict: true` 和 `allErrors: true` 编译全部五个
schema。生成的 `renderers/shared/generated-validators.mjs`
已提交并随技能一起发布，因此运行时校验不依赖 npm 或
网络。`renderers/shared/validator.mjs` 会在渲染器自身的布局检查之前
应用匹配的独立校验器。
随后共享加载器会检查 JSON Schema 在此处无法简洁表达的
跨集合事实：重复的视图 ID、重复的焦点 ID、在图的语义集合中
不存在的焦点 ID，以及该模式关系集合中重复的已编写
关系 ID。

全部五种模式都支持可选启用、按修订固定的仓库证据。
`meta.repository` 写明仓库 URL 和完整提交 SHA，以及可选的
`provider`（`github`、`gitee` 或 `gitlab`）和 `link_mode`（`web` 或 `local-only`；参见
编写契约）；一个节点可以带一到三个 `sources`，包含仓库相对的 POSIX 路径、可选的行
范围和可选的标签。sources 编写在该模式自己的节点
集合上——Architecture `components`、Workflow 和 Data Flow `nodes`、
Sequence `participants`、Lifecycle `states`——已核实的载荷以
节点 id 为键。先由 schema 检查形态，然后渲染器要求
`--repo-root`：本地 Git origin 必须匹配，且 Git 必须证明该提交、
blob 和所请求的行。已核实的证据嵌入在规范
SVG 之外，供 Semantic Passport 和 Node Finder 使用；普通文档和视觉
导出不携带任何仓库证据。

## 视觉质量与工程真实性

`meta.quality_profile` 和 `meta.engineering_profile` 回答不同的
问题。`quality_profile` 在全部五种模式中可用，控制
Archify 评判构图的严格程度。`engineering_profile` 是一个可选的、
仅限 Architecture 的语义契约；省略它会保留普通的 v1
行为。

第一个工程 profile 是 `deployment-ownership`。只有当
用户想要一次以失败关闭的部署评审、且来源事实已知时才启用它。
它要求每个非 external 组件都在 `tag` 中写明归属者，并且恰好属于
一个 `region`；文档必须同时包含 `region` 和
`security-group` 边界；每个 `database` 都必须位于某个
`security-group` 内；每个安全组的成员必须来自同一个
region；每条区域或安全组成员关系发生变化的连线
都必须在 `label` 中写明真实的跨越机制。

该 profile 只校验已编写的 IR。它不会发现基础设施、
推断归属者，也不会证明图与实际运行环境一致。若某个事实
未知，就不要设置该 profile，或者先获取该事实，而不是捏造它。

`npm test` 以检查模式运行生成器，当已提交的
校验器与其 schema 不一致时失败。

## 错误格式

schema 违规会以非零状态退出。每个 ajv 错误单独报告一行，
内容为实例路径——并注明最近的外层元素的 `id` 或
`label`——随后是消息和参数：

```text
workflow schema validation failed:
  /nodes/3 (id/label: "router") must NOT have additional properties {"additionalProperty":"colour"}
```

schema 捕获形态错误（类型、枚举、范围、未知字段）；几何
问题（如重叠和标签碰撞）由渲染器负责。
