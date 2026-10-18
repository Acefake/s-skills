---
name: 原则-类型系统纪律
description: "在设计类型、审查函数签名或用任何静态类型语言写代码时使用。让非法状态无法表示，给有语义的基本类型打上标记，在边界上解析外部数据，穷尽所有变体，从权威的 schema 推导类型。"
disable-model-invocation: true
---

# 类型系统纪律

让编译器拒绝不可能的状态、不匹配的基本类型和没处理的变体。宁可通过设计让错误和特殊情况根本不存在，也不要让各种处理代码越来越多。TypeScript 的写法见 `TypeScript最佳实践` skill。

- **给有语义的基本类型打上标记（brand）。** `UserId` 和 `OrderId` 底层都是字符串，但不应该能互换。给它们各自一个类型，比如 TypeScript 里的品牌交叉类型（branded intersection），或者其他语言里的 newtype。在创建时校验一次，之后就信任这个类型。如果两个参数的基本类型相同、含义却不同，就给它们打上标记。
- **外部数据在解析之前都是没有类型的。** RPC 数据、JSON、进程间消息、命令行参数、配置文件、环境变量、数据库的行。在每个边界上都要有一个解析函数，把无结构的输入变成有类型的模型。校验该放在哪里，见 **boundary-discipline** 原则 skill。
- **从权威的 schema 推导类型。** 当某个 protocol buffer、OpenAPI 规范、GraphQL schema、数据库迁移、设计令牌文件或其他文件拥有某个数据形状时，就从它推导，而不是手写一个平行的类型。见 **encode-lessons-in-structure** 原则 skill。
