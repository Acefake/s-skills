# 内置品牌标识

Archify 附带一个有界目录，包含 107 个常用品牌，可用于架构、
工作流、时序、数据流和生命周期节点。标识是作者可选的
身份信息：它绝不取代节点的语义 `type`、颜色、标签或
关系。

未知站点通过显式的两阶段工作流处理。先运行
`node bin/archify.mjs brands capture <url> --json`，再填写返回的、
固定摘要的 `brand` 值。常规的 render 和 validate 命令不会执行
未固定的抓取，内容变化或不可用时按失败关闭处理。

大多数矢量路径和品牌元数据由 Simple Icons 16.28.0 生成。
OpenAI 标识依据 OpenAI 官方品牌指南描摹。每个生成的
条目都在 `renderers/shared/generated-brand-marks.mjs` 中记录其来源，
以及上游提供时的指南和许可证元数据。

品牌名称和标志可能是其各自所有者的商标。Simple
Icons 的 CC0 许可证涵盖其收集工作，而非每一个底层商标或
作品。贡献者在添加或更新标识之前，必须审查已记录的来源、当前品牌指南
以及预期的指称性用途。Archify 不暗示任何赞助、背书或合作关系。

编辑 `catalog.json`，然后重新生成已提交的零运行时依赖包：

```bash
npm run generate:brand-marks
npm run check:brand-marks
```

绝不要手动编辑 `renderers/shared/generated-brand-marks.mjs`。
