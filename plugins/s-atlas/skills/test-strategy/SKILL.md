---
name: test-strategy
description: "给新功能、改动或整个项目定测试方案：每个行为放在哪一层测、用什么工具、哪些不测，并写出能直接跑的命令。覆盖 TypeScript/React、Vue、Go、Java。Use when deciding what to test and at which layer for a feature, change, or codebase in TypeScript, React, Vue, Go, or Java."
---
# 测试方案

先回答「哪个行为坏了会让用户或调用方吃亏」，再决定测试放在哪一层。测试是为了让改动敢合，不是为了覆盖率数字。

## 先看现状

动手前花几分钟读仓库，别凭印象：

1. 找已有的测试命令：`package.json` 的 scripts、`Makefile`、`go test ./...`、`mvn test` / `gradle test`、CI 配置。以仓库已经在用的为准。
2. 找已有的测试框架和约定：文件放哪（`*.test.ts`、`__tests__/`、`*_test.go`、`src/test/java`）、怎么造数据、有没有 testcontainers 或本地 docker-compose。
3. 跑一次现有测试，记下耗时和失败项。原本就红的测试先报告，不要顺手改。

新方案沿用这些约定。只有在现有工具确实做不到时才引入新工具，并说明理由。

## 分层

按风险把每个行为放到最低的、还能证明它的一层：

| 层 | 测什么 | 不测什么 |
|---|---|---|
| 单元 | 纯逻辑、解析、计算、状态机、边界值 | 框架本身、getter/setter、只转发的代码 |
| 组件 | 组件在真实 DOM 里的渲染和交互，按用户看到的文字和角色断言 | 内部 state、私有方法、样式类名 |
| 集成 | 跨模块或跨进程的契约：HTTP handler、数据库读写、消息队列，用真实依赖 | 已经被单元测试证明的分支组合 |
| 端到端 | 少数几条关键用户路径，从界面一路到后端 | 每个表单字段、每个错误分支 |

经验比例是多单元、适量集成、很少端到端。哪一层最便宜地抓住真实 bug，就多放哪一层。

## 各技术栈的默认做法

仓库已有选择时以仓库为准，下面是没有选择时的默认值。

### TypeScript / React

- 运行器用 Vitest（Vite 项目）或仓库已有的 Jest。
- 组件用 Testing Library：`getByRole`、`getByLabelText`、`findByText`，交互用 `@testing-library/user-event`，不要用 `fireEvent` 模拟点击。
- 网络用 MSW 在请求层拦截，不要 mock `fetch` 或自己的 API 模块。
- Hook 有独立逻辑时用 `renderHook`；逻辑能抽成纯函数就直接测纯函数。
- 类型本身也是测试：公共 API 的类型约束可以用 `expectTypeOf` 或 `tsc --noEmit` 检查。

### Vue

- 运行器用 Vitest，组件用 `@testing-library/vue`；需要访问实例时才用 `@vue/test-utils`。
- Pinia store 用 `createTestingPinia` 或真实 store 加初始状态，断言 store 对外的结果，而不是 action 被调用了几次。
- 网络同样用 MSW。

### Go

- 用标准库 `testing`，表驱动测试（`[]struct{ name string; ... }` 加 `t.Run`），子测试名写清场景。
- HTTP 用 `net/http/httptest`：`httptest.NewRecorder` 测 handler，`httptest.NewServer` 测客户端。
- 数据库用 testcontainers-go 或仓库已有的 docker-compose 起真库；只在边界抽接口，不为测试给每个结构体加接口。
- 并发代码一律带 `go test -race` 跑。
- 需要对比大块输出时用 golden 文件，加 `-update` 标志重新生成。
- 不确定的输入空间用 `testing.F` 做 fuzz。

### Java

- JUnit 5，断言用 AssertJ。
- Spring Boot 用切片测试：`@WebMvcTest` 测控制器，`@DataJpaTest` 测仓储，只在需要整条链路时用 `@SpringBootTest`。
- 数据库、Kafka、Redis 用 Testcontainers 起真实依赖，不要用 H2 冒充 MySQL/Postgres。
- Mockito 只用在系统边界（外部 HTTP、时钟、随机数），不 mock 自己的领域对象。
- 参数化用 `@ParameterizedTest`。

### 跨前后端

- 前端和 Go/Java 后端之间的契约，优先从一份源头生成类型（OpenAPI、protobuf、tRPC），再在后端加 handler 级集成测试，前端用 MSW 按同一份契约返回数据。
- 端到端测试见 `e2e-testing`。

## 写测试时的规矩

- 测行为，不测实现，见 `principle-test-behavior-not-implementation`。
- 每个测试只证明一件事，名字说清条件和预期，比如 `rejects expired token`、`TestTransfer_InsufficientFunds`。
- 不用 `sleep` 等异步结果，用框架的等待（`findBy*`、`waitFor`、`Eventually`、Awaitility）。
- 时间、随机数、ID 生成从外部注入，测试里固定下来。
- 测试数据就地构造，用小工厂函数；不要一个巨大的共享 fixture。
- 修 bug 时先写会失败的测试，见 `tdd`。

## 交付

给出一份短方案，然后按方案写测试：

1. 要测的行为清单，每条标出层级和理由。
2. 明确不测的部分和理由。
3. 新增或修改的测试文件。
4. 跑过的命令和结果：失败数、耗时，以及每个新测试在改动前会失败的证据（能拿到时）。
