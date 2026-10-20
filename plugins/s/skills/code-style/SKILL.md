---
name: code-style
description: "写、改或审查 TypeScript、React、Vue、Go、Java 代码时遵守的个人代码规范：按模块就近放文件、导出符号和模块入口写文档注释、代码质量的底线。和仓库已有规范冲突时以仓库为准。Use when writing, changing, or reviewing TypeScript, React, Vue, Go, or Java code, to apply the owner's module layout, doc comment, and quality rules."
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。

# 代码规范

这是本插件主人自己的规范，写代码和审代码都按这个来。仓库已经有明确的规范（lint 配置、CONTRIBUTING、现有目录结构）时，以仓库为准，冲突处在回复里说一句。

## 一、按模块放文件

一个模块的所有东西放在同一个目录里：组件、逻辑、类型、样式、接口调用、测试、文档。按业务能力分，不按技术类型分。改一个功能只需要打开一个目录。

### 规则

- 目录名是业务名词：`order`、`billing`、`user-profile`，不是 `components`、`utils`、`services`、`models`。
- 模块对外只暴露一个入口（`index.ts`、Go 包的导出符号、Java 包里的 public 类），其他模块只能从入口引用，不能伸进内部文件。
- 测试和被测代码放在一起。
- 只被一个模块用的东西留在这个模块里。被两个以上模块用、且确实稳定了，才提到 `shared/`（或 `internal/platform`、`common`），不要提前抽。
- 模块之间单向依赖，不准循环。发现循环就把共同部分下沉，或者用事件、接口反转。
- 文件按职责命名，一个文件一个主要导出。

### TypeScript / React

```text
src/
  features/
    order/
      index.ts              # 对外入口，只导出公开的组件、hook、类型
      OrderList.tsx
      OrderList.test.tsx
      OrderList.module.css
      useOrders.ts
      useOrders.test.ts
      order.api.ts          # 这个模块的请求
      order.types.ts
      order.schema.ts       # 边界校验（zod 等）
  shared/                   # 至少两个模块在用的稳定代码
  app/                      # 路由、全局 provider、组装
```

### Vue

```text
src/
  modules/
    order/
      index.ts
      OrderList.vue
      OrderList.spec.ts
      useOrders.ts          # 组合式函数
      order.store.ts        # Pinia store，只放这个模块的状态
      order.api.ts
      order.types.ts
  shared/
  app/
```

### Go

按领域分包，不按层分包：

```text
internal/
  order/
    order.go                # 领域类型和核心逻辑
    service.go
    repository.go           # 包内定义需要的接口，实现也放这里或 postgres.go
    handler.go              # HTTP 入口
    order_test.go
    doc.go                  # 包文档
  billing/
  platform/                 # 数据库连接、日志、配置等基础设施
cmd/
  api/main.go               # 只做组装
```

接口在使用方的包里定义，越小越好。

### Java

按功能分包（package by feature），不按 controller/service/repository 分层建顶层包：

```text
com.example.app.order
  OrderController.java
  OrderService.java
  OrderRepository.java
  Order.java
  package-info.java         # 包文档
com.example.app.billing
com.example.app.shared
```

只有模块入口类是 `public`，其余类用包级可见性。

## 二、文档注释

导出的、别人会调用的东西都写文档注释；不明显的内部函数也写。文档注释说契约：做什么、参数和返回值的含义、会抛什么错或返回什么错误、前置条件和副作用、为什么这样设计（代码看不出来时）。不复述代码。

### 必须写

- 每个模块入口：模块负责什么、不负责什么、主要用法。TS 写在 `index.ts` 顶部，Go 写在 `doc.go`，Java 写在 `package-info.java`。
- 每个导出的函数、类、类型、组件、hook、组合式函数。
- 组件的 props、emits、slots 的含义。
- 复杂度不明显的内部函数：有算法、并发、缓存、重试、性能取舍的。

### 格式

- TypeScript：TSDoc `/** ... */`，用 `@param`、`@returns`、`@throws`、`@example`。类型已经说清的不必在 `@param` 里重复类型。
- Vue：`<script setup>` 里给 `defineProps`、`defineEmits` 的每个字段写 `/** */`。
- Go：GoDoc，以符号名开头的完整句子：`// ParseOrder parses ...`。包注释写在 `doc.go`：`// Package order ...`。
- Java：Javadoc，用 `@param`、`@return`、`@throws`；公共 API 上写 `{@code}` 示例。

### 不要写

- 叙述步骤的行内注释（`// 第一步：取数据`）、注释掉的代码、改动记录、和代码重复的话。
- 行内注释只留「为什么」：外部约束、绕不开的坑、看起来不对但是对的写法。

`no-comments`、`comment-sicko`、`deslop` 清注释时，按这一节保留文档注释。

## 三、质量底线

- 类型严格：TS 开 `strict`，不用 `any` 和 `as` 绕类型；Go 不用空接口兜底；Java 不用原始类型。外部输入在边界解析成类型，见 `principle-boundary-discipline`、`principle-type-system-discipline`。
- 错误不吞：TS 不写空 `catch`；Go 每个 `err` 都处理或带上下文返回（`fmt.Errorf("load order %s: %w", id, err)`）；Java 不 catch 了只打日志又继续。
- 函数短而单一，嵌套不超过三层，用提前返回。
- 命名用业务词，不用 `data`、`info`、`handle2`、`temp`。
- 不留死代码、未用的导出、TODO 不带负责人和 issue。
- 改动带测试，见 `test-strategy`。
- 提交前格式化和 lint 全过：Prettier + ESLint、`gofmt` + `go vet`（有 golangci-lint 就跑）、仓库配置的 Java 格式化和检查（Spotless、Checkstyle 等）。
- 界面代码同时满足 `ui-performance`。

## 审查时

按一、二、三节逐项看 diff，每条问题写出文件、行和改法。只是不合个人偏好、但仓库规范允许的，标成建议，不算阻塞。
