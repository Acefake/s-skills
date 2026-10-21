---
name: e2e-testing
description: "用 Playwright 给 React 或 Vue 前端写稳定的端到端测试，后端可以是 Node、Go 或 Java：选关键路径、按角色定位、准备数据和登录态、在本地和 CI 里跑、排查不稳定的测试。Use when writing, running, or fixing end-to-end browser tests for a web app, including flaky Playwright tests."
---
# 端到端测试

端到端测试最贵、最慢、最容易不稳定，所以只给最关键的几条用户路径写，而且每条都要稳。其余行为放到更低的层，见 `test-strategy`。

## 选路径

只挑坏了就不能上线的路径：注册登录、核心下单或提交、付款、权限边界。每条路径写一个测试，从用户入口走到能看见的结果。一个项目通常 5 到 20 条，不是几百条。

## 工具

默认 Playwright Test（`@playwright/test`）。仓库已经用 Cypress 就继续用 Cypress，下面的原则同样适用。

```bash
npm init playwright@latest   # 新项目
npx playwright test          # 跑全部
npx playwright test --ui     # 本地调试
npx playwright show-trace test-results/**/trace.zip
```

`playwright.config.ts` 至少要有：

- `webServer` 启动被测应用（`npm run dev`，或 Go/Java 后端加前端的组合命令），带 `url` 和 `reuseExistingServer: !process.env.CI`。
- `use: { baseURL, trace: 'on-first-retry', screenshot: 'only-on-failure' }`。
- CI 里 `retries: 2`，本地 `retries: 0`，这样本地能看见不稳定。

## 写法

- 定位用 `getByRole`、`getByLabel`、`getByText`，其次 `getByTestId`。不用 CSS 层级选择器和 XPath。
- 断言用会自动重试的 `expect(locator).toBeVisible()`、`toHaveText`、`toHaveURL`。不用 `waitForTimeout`。
- 一个测试独立完成，不依赖别的测试先跑；能并行跑。
- 用 Page Object 或小 helper 收拢重复步骤，但断言留在测试里。

## 数据和登录态

- 通过 API 准备数据，不要走界面造数据：在 `beforeEach` 或 fixture 里用 `request` 调后端接口，或调专门的测试种子接口。
- 登录做一次：在 `globalSetup` 或 setup project 里登录，`storageState` 存下来，其他测试复用。
- 每个测试用唯一数据（带随机后缀），避免并行时互相踩。
- 后端是 Go 或 Java 时，用 docker-compose 或 Testcontainers 起数据库和服务，测试结束不清理也能重跑。

## 网络

- 端到端默认打真实后端，不 mock，这是这一层存在的意义。
- 只有第三方服务（支付、短信、地图）用 `page.route` 拦截，返回固定响应。

## 修不稳定的测试

先连跑复现，再定原因，最后修根因：

```bash
npx playwright test path/to/spec.ts --repeat-each=20 --workers=4
```

常见原因和修法：

| 现象 | 原因 | 修法 |
|---|---|---|
| 偶尔找不到元素 | 断言没等，或用了 `isVisible()` 这种不重试的判断 | 换成 `await expect(locator).toBeVisible()` |
| 并行时失败、单跑通过 | 测试之间共享数据或账号 | 每个测试独立造数据 |
| CI 失败、本地通过 | 机器慢、时区、字体、视口不同 | 看 trace；固定 `timezoneId`、`locale`、`viewport` |
| 动画中途点击失败 | 元素还在移动 | 等目标状态出现；必要时用 `reducedMotion: 'reduce'` |

不要靠加大超时或加重试来压住不稳定。

## 交付

1. 覆盖的路径清单。
2. 新增的测试和配置文件。
3. 本地跑的结果，修不稳定测试时附上 `--repeat-each` 前后的通过次数。
4. CI 里怎么跑：需要的服务、环境变量、产物（trace、截图）上传到哪。
