SKILL.md「原生图编写」只保留五步骨架。写候选稿、选字段、跑 finalize 和修复时，按下面的全文执行。

## 原生图编写 <a id="native-diagram-authoring"></a>

普通生成使用此路径。只有当分支参考资料所述的触发条件成立时才去读它们。

1. 根据问题从 `architecture`、`workflow`、`sequence`、`dataflow`、`lifecycle`、`erd`、`class`、`tree`、`timeline` 或 `waterfall` 中选择一种。
2. 直接使用类型路由表中的确切 schema 和示例路径，不要列出它们的目录。把 [Authoring defaults](authoring-defaults.md) 和该模式的示例放在一个有界批次中读取，与项目文档和完整 schema 分开，以免任何一方被截断；在写之前补回任何缺失的小节。对于 Architecture，使用匹配的 showcase 示例。对于 Architecture 以外的每种模式，还要读该模式的 schema 和通用 schema。在选用任何新字段、枚举或受约束文本之前，先读相关的 schema 定义，尤其是边界种类。示例教的是形状，不是事实。使用全新的 ID、措辞和布局。直接写候选稿，不做前置的 help、doctor、起始校验、临时图或输出路径列举。只为明确要求的标志查询品牌；对于用户提供了 URL 的未知标志，阅读 [Brand marks](brand-marks.md)。
3. 一旦所请求的范围以及（对真实代码库而言）[源码证据](repository-authoring.md) 都已覆盖，就直接写出完整候选稿，不要在散文中规划坐标。在定坐标之前，先按 Authoring defaults 选择 Architecture 的抽象层级和相连布局：展示主要用户旅程和必要的分支，保留控制角色和改变行为的条件，并为实际的关系标签留出足够空间。节点、关系、来源、视图、卡片或边界的数量都不是目标，也不是上限。先用自动路由；只有对必要的分支、回程、用户提供的几何或经测量的修复，才加显式路由。把 `meta.quality_profile` 设为 `"showcase"`，除非用户要求密集的 `standard`。对于 ERD，使用表优先布局：在 `entities[].attributes` 中展示每一个物理列，保留其 SQL 类型和源码注释，标明每个列承担的每一种键角色（`key` 接受一个角色或一个列表，因此连接表的列是 `["pk", "fk"]`，且每个 `fk` 列还需要像 `"orders.id"` 这样的 `references`），绝不把列挪进卡片来代替表。在放置之前先把表归入功能域，给每个域一个简洁的 `tag`，并把其成员放在由网格单元构成的一个实心矩形中——单行、单列或填满的矩形块，不能是 L 形或对角线。带 tag 的表总是需要 `row`/`col`，因为绝对坐标没有网格单元，而一个其表未填满一个矩形的域无法画成色带：渲染器会报告 `erd/domain-not-drawn`，而不是发布一张无法标出该域的图。多域 schema 最好读成每列一个域——每个 `tag` 一条竖向连续区——因为阅读器会把宽画布放大到阅读器宽度，把高画布缩小直到页面放得下，所以宽排布才是在笔记本视口内保持完整且清晰的那一种。大约超过 8 张表或 50 个字段的 schema 优先 ERD 本身就是一张密集图：以 `standard` 编写其首个全字段版本，只有在布局仍然可读时才升级。
4. 写完完整的首个候选稿后，直接运行 `finalize`。它的第一道关卡是 showcase 校验；成功的初稿不需要单独的预校验。命令运行期间保持候选稿不变：

   ```bash
   node bin/archify.mjs finalize <type> <candidate.json> <output.html> --quality showcase --json
   ```

   对于有仓库支撑的候选稿，在初稿中就包含证据，并使用完整的首条命令：`node bin/archify.mjs finalize <type> <candidate.json> <output.html> --repo-root <repo-root> --quality showcase --json`。传入与 `meta.quality_profile` 匹配的 `--quality`，例如密集的首版 ERD 用 `standard`。

   通过回执证明其中包含的 `validate`、`deliver`、严格 `check` 和真实浏览器 `browser-check` 关卡都已通过。使用它的紧凑摘要；只有针对单独请求或聚焦的失败诊断才运行独立命令。

5. 非零退出绝不是成功。阅读紧凑的 stdout 或 `evidence.summaryReceipt`，然后[修复失败的关卡](delivery-contract.md#failed-finalize-and-candidate-repair)，包括其修复次数上限。保留所请求的含义和源码证据。对于多条缠绕的 Architecture 路由，阅读 [Architecture layout repair](architecture-layout-repair.md)；对于经测量的字段或几何失败，阅读 [Authoring contract](authoring-contract.md)。编辑相连的邻域，然后重新运行第 4 步中的完整 `finalize` 命令。一旦某次运行到达了 `browser-check`，输出路径就拥有了那份证据：之后的每次运行都要给它自己的 `--out-dir <folder>/review-<n>`。

在首个候选稿之前，使用编写参考资料和相关的仓库源码，而不是 Archify 的实现或测试。如果经过聚焦修复后诊断信息仍然无法据以行动，再去查看 Archify 的实现。
