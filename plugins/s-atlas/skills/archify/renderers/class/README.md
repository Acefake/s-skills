# 类与接口渲染器

将 `diagram_type: "class"` JSON 文件渲染为标准 Archify HTML 模板。

```bash
node archify/renderers/class/render-class.mjs input.class.json output.html
```

渲染器使用内置的独立校验器，按 `archify/schemas/class.schema.json` 校验
输入。无需安装任何依赖。若省略
`output.html`，它使用 `meta.output`，否则回退到当前工作目录下的
`class.html`。`--layout-json` 打印已放置的类型和
路由，而不是写出 HTML。

## 输入

```json
{
  "schema_version": 1,
  "diagram_type": "class",
  "meta": { "title": "Payment module types" },
  "types": [],
  "relationships": [],
  "cards": []
}
```

一个类型在 `label` 中给出名称，带有 `kind`、一个 `row`/`col` 网格单元（或
绝对 `pos`），以及可选的 `sublabel`、`attributes`、`methods` 和 `sources`。
作者只选择讲解所需的成员；一个类型也可以不显示任何成员。

| `kind` | 标题 | 配色族 |
| --- | --- | --- |
| `class` | 仅名称 | backend |
| `abstract` | `«abstract»`，名称斜体 | backend |
| `interface` | `«interface»` | frontend |
| `enum` | `«enumeration»`；`attributes` 即为常量 | messagebus |
| `record` | `«record»` | database |

属性为 `{ name, type?, visibility?, static? }`，绘制为
`+ name: Type`。方法为 `{ name, parameters?, returns?, visibility?,
static?, abstract? }`，绘制为 `+ name(parameters): Returns`。可见性
使用 UML 符号：`+` public、`#` protected、`~` package、`-` private；
静态成员加下划线，抽象方法为斜体。接口
属性描述属性契约（例如 TypeScript 的
`interface Person { name: string }`）；它们不意味着存储的实现
状态。接口也可以声明静态常量。

## 关系

每条关系都读作 `from` -> `to`，且 `kind` 决定全部记法，因此
实现关系绝不会看起来像调用箭头：

| `kind` | 含义 | 线条 | 标记 |
| --- | --- | --- | --- |
| `dependency` | `from` 使用 `to` | 虚线 | `to` 端开放箭头 |
| `association` | `from` 持有对 `to` 的引用 | 实线 | `to` 端开放箭头 |
| `inheritance` | `from` 继承 `to` | 实线 | `to` 端空心三角 |
| `realization` | `from` 实现接口 `to` | 虚线 | `to` 端空心三角 |
| `composition` | `from` 拥有 `to` 及其生命周期 | 实线 | `from` 端实心菱形 |
| `aggregation` | `from` 聚合 `to` 但不拥有它 | 实线 | `from` 端空心菱形 |

语义检查：实现关系从非接口指向接口
（`class/realization-target`）；继承绝不跨越接口边界
（`class/inheritance-kind`）；继承不能形成环
（`class/inheritance-cycle`）；关系不能把一个类型连接到它自身。

## 布局

`layout.mode: "grid"`（默认）按 `row`/`col` 把类型放在与 ERD 渲染器共享的
分带网格上：每列取其最宽的类型，每行取其最高的类型。类型在所在行带内居中，因此同一行
两个类型之间的关系是一条直线。半步的 `col`（例如 `1.5`）把一个类型居中放在
两列之间，且不参与任一列的尺寸计算，超类型正是借此对称地位于两个子类型之上；它同时占用两个相邻单元格。`layout.gapX`/`gapY`（默认 128/84）
为标记和标签留出空间；`layout.typeW`（180）是自动宽度的最小值，
`layout.typeMaxW`（300）是最大值。

成员绝不会被截断。没有 `width` 的类型会增宽到其最宽成员，
最多到 `typeMaxW`；更长的成员换行。换行的方法按格式化工具的
输出排版：`name(` 结束第一行，参数再缩进一级（在逗号后
断行），`): Return` 收尾。可见性符号和类型
注解使用柔和墨色，使成员名承载这一行。作者给出的 `width`
具有决定性，只有放不进它的标题才是错误
（`class/title-text-capacity`）。

只要两个类型不是左右并排，泛化关系就垂直布线，
使超类型位于其子类型之上。同一种类的两条或更多自动
泛化关系指向同一个超类型，且子类型位于其下方并留有
至少 40px 间隙时，绘制为一条层级总线：一个三角和
一条主干，一条位于间隙中部的水平总线，以及通往每个子类型的下垂线。
总线从超类型向外绘制，因此虚线的实现总线保持同一
虚线相位。其 `data-motion-path` 携带从源到目标的路由，使查看器
标记和流向叠加层沿关系的语义方向移动。会穿过其他类型的
总线回退为普通路由。

主干还会与完整场景中的其他关系共同检查：同一个主干组可以共享端口和线段。
主干候选若与其他组或普通关系争用标记空间、重叠走廊或形成内部交叉，
整组关系回退到现有路由器，以独立端口和走廊重新规划；无冲突的
其他主干保留。每轮回退后重新检查剩余主干，且只删除冲突组，不反复恢复尝试。
类型位置、关系种类和方向、显式 `via`、端口、路由及标签位置保持作者的控制。
此检查决定是否保留自动主干，不承诺固定路线周围满足全部自动间距或任意布局都能成功。
固定路线之间的冲突和无法绕开的复杂交叉仍遵循现有路由约束，不会修改作者指定的几何。

其他所有关系都使用共享的正交路由器
（`../architecture/routing.mjs`）以及共享的 Clean Flow、交叉、走廊、
节奏和标签避让关卡。

标签放在空间最大的线段上：水平段的上方，
垂直段的旁边。`labelAt`、`labelDx`/`labelDy` 和 `labelSegment` 可覆盖此行为。

`via: []` 与省略 `via` 等价，在主干选择和回退路由前统一按无路径点处理。
非空 `via` 仍是显式几何；其他路由与标签控制不变，原始 JSON 不会被改写。

## 阅读与导出

自动画布声明 `data-reader-fit="intrinsic-height"` 和 7.5px 的
阅读文字下限，与 ERD 相同，因此较高的模型会滚动，而不是把
成员缩小到难以辨认。图例列出出现的关系种类，并以各自的记法
绘制；悬停或聚焦某一项会使其他种类变暗。每个
类型都是可聚焦的节点，其护照显示其 kind 和 `sublabel`；提供的
`sources` 作为仓库证据显示。记法位于 SVG 自身的
`<style>` 和标记中，因此 SVG/PNG 导出会保留它。

## 实测规模

`examples/payment-processors.class.json`（11 个类型、10 条关系、较长的
签名）渲染约需 0.2s，并在 1440px 桌面阅读器中以 7.5px 的
投影文字最小值通过 showcase 关卡。更宽的模型需要更多行
而不是更多列，才能保持在该下限之上。
