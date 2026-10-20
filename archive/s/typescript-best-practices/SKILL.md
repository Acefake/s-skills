---
name: typescript-best-practices
description: "Use when reading or changing TypeScript. 中文触发：TypeScript 最佳实践。读或改任何 .ts 或 .tsx 文件时使用。"
paths: ["**/*.ts", "**/*.tsx"]
disable-model-invocation: false
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../../plugins/s/HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。


# TypeScript 最佳实践

先应用 **type-system-discipline** 原则 skill。

| 规则 | 概要 |
|------|---------|
| 可辨识联合类型（Discriminated unions） | 用一个 `kind` 字面量作为判别字段来表示各种变体，让不可能的状态无法被表示。不要用一堆可选字段拼成的对象。 |
| 品牌类型（Branded types） | 用 `& { readonly __brand: "X" }` 给基本类型打上标记，让它们不会被混用。在边界上校验一次。 |
| 构造式建模（Constructive modeling） | 把形状建成非法的值根本构造不出来的样子。非空用 `[T, ...T[]]`，偶数长度用 `[T, T][]`，范围用 `start` 加 `duration`。不是靠运行时防护，也不是寄希望于细化类型（refinement types）。 |
| 最简单的完全类型（Simplest total type） | 只要对它的每个操作都还是完全的（对所有输入都有定义），就保持 `T[]`。只有当宽松的类型迫使你用 `!`、类型断言或“不应该发生”的抛错时，才加强成 `NonEmpty<T>`。 |
| 用 `unknown` 而不是 `any` | 外部数据是 `unknown`。 |
| 先用 schema，再写类型守卫 | 在手写一个逐个属性检查的类型守卫之前，先用仓库里的运行时 schema 库，并从 schema 推导出类型，比如 `z.infer`。 |
| 不用 `as` 断言 | 每一个 `as` 都是一个等着发生的运行时崩溃。只在校验之后才做断言。 |
| 收窄的优先顺序 | 按判别字段 switch > `in` 运算符 > `typeof`/`instanceof` > 自定义类型守卫 > `as`。 |
| 类型守卫 | 必须真的验证它所声称的。一个撒谎的守卫比 `as` 更糟，因为 bug 藏在一个声称安全的名字后面。命名为 `isX` 或 `hasX`。 |
| 穷尽检查 | 在 default 分支里内联写 `const _exhaustive: never = x;`，这样新增一个变体时编译器就会报错。 |
| 用 `satisfies` 而不是 `as` | 校验值的同时，不会把字面量类型放宽。 |
| 边界校验 | 在数据进入的地方解析它，变成一个有名字的领域类型。`Record<string, unknown>`（不管怎么写）到那次解析就止步。在内部信任类型。见 **boundary-discipline** 原则 skill。 |
| 从 schema 推导的类型 | 在声明一个新的 interface 之前，先考虑 `Pick`/`Omit`/`Parameters`/`ReturnType`/`Awaited`/`typeof`。 |
| 对象参数 | 传对象，而不是按位置传参，这样参数的顺序自己就说明了含义。在热路径上（每帧渲染、分词器、解析器）跳过这条。 |
| 真实的测试 | 能运行的就不要模拟。优先用框架真实的测试基础设施，并带上泄漏/资源释放检查；在一个运行中的构建里验证界面。只模拟那些你没法在本地运行的东西。 |
| 结构化的遥测 | 优先用结构化的日志诊断，带上足够的上下文，让人能凭一个 id 去调试。上线的代码里不要有 `console.log`。 |

示例：`references/patterns.md`。
