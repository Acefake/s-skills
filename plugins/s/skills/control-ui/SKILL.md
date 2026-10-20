---
name: control-ui
description: "搭一个本地的浏览器或 CDP 驾驭装置，驱动并查看网页、IDE 或 Electron 界面。用于本地界面核对、截图、无障碍快照、性能剖析、视觉对比，或复现界面 bug。Use when you need to drive a real browser or desktop UI to collect evidence."
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。


# 操作界面

用本地的浏览器自动化，拿证据核对界面行为。仓库里已经有 Playwright、浏览器或 Electron 装置，就先用那个。没有，就围绕开发服务器或 Chromium 调试端口，临时搭一个。

## 用来做什么

- 复现依赖真实焦点、键盘、滚动、改变大小或绘制的界面 bug。
- 用截图和快照核对视觉或无障碍改动。
- 上线前检查本地的网页、IDE 或 Electron。
- 抓控制台日志、网络日志、CPU 剖析、trace 或堆快照。
- 为前后对比留下证据。

## 准备

1. 用仓库文档里的开发命令，在本地把应用跑起来。
2. 找已有装置：Playwright 测试、Cypress、Storybook、浏览器脚本、Electron 启动脚本，或快照工具。
3. 网页应用：用已有的浏览器工具连到本地 URL。
4. Electron 或 Chromium：支持的话打开远程调试端口。
5. 用稳定的应用标记选对页面，不要只靠标签页的顺序。
6. 优先用无障碍角色、标签和稳定的 `data-*` 选择器，不要用坐标。

## 通用网页装置

优先用仓库里已经装好的浏览器工具。仓库已经有 Playwright 时，一次临时探测可以这样写：

```javascript
import { chromium } from "playwright";

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
await page.goto("http://127.0.0.1:<port>");
await page.getByRole("button", { name: /submit/i }).click();
await page.screenshot({ path: "/tmp/ui-harness-after.png", fullPage: true });
await browser.close();
```

用户没要求的话，不要为了这次探测把 Playwright 加进项目依赖。用已有的开发依赖，或环境里已经有的浏览器工具。

## 通用 CDP 装置

Electron 或 Chromium 用 `--remote-debugging-port=<port>` 启动时，走 CDP：

```javascript
import { chromium } from "playwright";

const browser = await chromium.connectOverCDP("http://127.0.0.1:<debug-port>");
const pages = browser.contexts().flatMap((context) => context.pages());
let page;
for (const candidate of pages) {
  if (await candidate.locator("<app-root-selector>").count()) {
    page = candidate;
    break;
  }
}

if (!page) {
  console.log(await Promise.all(pages.map(async (p) => ({
    title: await p.title(),
    url: p.url(),
  }))));
  throw new Error("No matching app page found");
}

await page.screenshot({ path: "/tmp/ui-harness-cdp.png", fullPage: true });
await browser.close();
```

把 `<app-root-selector>` 换成当前仓库里稳定的标记，比如应用根节点、地标，或产品自己的 `data-*`。

## 操作循环

1. 动手前先抓一张页面快照或截图。
2. 从最新的页面结构里选目标。
3. 一次只做一个结构性动作：点击、输入、按键、拖拽、滚动、导航或改变大小。
4. 再抓一张新的快照或截图。
5. 核对预期的状态变化。
6. 用户要证据时，把前后的产物存下来。

## CDP 能做的

高层浏览器 API 不够用时，才用原始 CDP：

- 性能：CPU 剖析、trace、绘制闪烁、FPS、布局偏移。
- 内存：堆快照，以及为查泄漏而强制 GC。
- 网络：拦截请求、限速、关掉缓存、请求和响应日志。
- 绘制：视口、配色模拟、减弱动画、无障碍检查。
- 调试：控制台流、异常捕获、DOM 快照。

## 选哪一页

同一个调试端口上有多个窗口或标签页时：

- 优先用一个正面标记，比如应用根选择器。
- 必要时用一个反面标记，避开不该测的那一面。
- 没有页面对上时，列出已有页面的标题和 URL，不要猜。

## 边界

- 导航或结构变了之后，不要继续用过期的元素引用。
- 不要用坐标点击，除非点击前刚刚抓过一张截图。
- 测试数据放本地，用完即弃。
- 涉及隐私的工作区，用户没有明确同意，不要保存截图或堆快照。
- 不要写死别的仓库的选择器、端口或脚本路径。用当前仓库自己的标记。
- 做完关掉开发服务器、调试会话和临时配置。

## 在不同软件里怎么用

装置跑在能打开这个界面的那台机器上。Cursor、OpenCode、Codex 都用上面的 Playwright 或 CDP。子智能体在另一台机器上、而界面只在用户电脑上时，就在用户这台机器上跑，并写明跑在哪。

WorkBuddy 和 Claude Code 同样用本机浏览器工具。没有 Playwright 时，用环境里已经有的浏览器工具，不要为了这一次新加依赖。
