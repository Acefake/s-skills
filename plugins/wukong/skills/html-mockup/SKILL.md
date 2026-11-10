---
name: html-mockup
description: "「先出图」「做个设计图」「效果图」「mockup」「美化一下给我看看」。改界面前用手写 HTML/CSS 画静态设计稿，无头 Chromium 截成 PNG/JPG 交付；也用于固定尺寸素材（安装器侧栏、横幅、OG 图、图标预览）。只出静态稿，驱动真实应用截图用 control-ui，按稿落地实现用 impeccable。Use when the owner wants a visual mockup before UI work, or a pixel-exact static asset."
---

本会话首次使用本库技能时，按[全局提示词自检](../setup-s-instructions/references/daily-check.md)只读检查一次。
# HTML 设计图（mockup）

用一页静态 HTML/CSS 画设计稿，无头 Chromium 截图成 PNG/JPG 给用户看。比生成图片可控：像素级对齐、真文字、真图片、能改一处重截。

## 边界

- 本技能只做静态设计稿和静态素材的截图。
- 要打开真实应用点一遍、截真实界面，用 `control-ui`。
- 用户选定方案后按图写代码，用 `impeccable`；点名要一套视觉方向，用 `frontend-design`。

## 何时用

- 改 UI 前先出图给用户挑（「先出图」）。
- 需要真实尺寸的静态素材（安装器侧栏 BMP、商店横幅、OG 图、图标预览）。

## 1. 先看现状再画

- 用户给了截图：先打开看清现在的样子、尺寸和问题点。
- 有仓库：找设计令牌（颜色、圆角、字体、间距的 CSS 变量）、图标和 logo（svg 优先）、现有组件长相。设计图必须用同一套令牌，不要自创配色。
- 记下目标尺寸：窗口 1440×900、手机 390×844，或素材的固定尺寸（如 NSIS 侧栏 164×314）。

## 2. 写 HTML

- 放在项目外的临时目录（如 `./.mockups/<主题>/`，记得加进 `.gitignore`；或系统临时目录）。素材（海报、logo.svg、截图）复制进同目录，用相对路径。
- 一个共享 `s.css` 放令牌和外壳（侧栏、标题栏），每个方案一个 html；或一页并排放 A/B 两案（`.row{display:flex;gap:40px}`）。
- 多方案时 2 个就够，差异要明显（例：海报墙 vs 品牌光晕），并给出推荐和理由。
- 重复结构（货架、网格）用脚本生成比手写快：字符串拼接加循环，写到 html。
- 中文字体：`font-family:"Noto Sans CJK SC",sans-serif`（Linux 需装 `fonts-noto-cjk`）；模拟 Windows 原生控件可加 `"Microsoft YaHei"`。
- 玻璃效果用 `backdrop-filter:blur() saturate()`；模糊着色背景用放大的海报 `filter:blur(36px) saturate(1.5) brightness(.55)`，并 `inset:-30px` 防白边。
- 只画用户要改的部分；不变的区域可以省略，或照原样保留作对比。
- 没有数据来源的东西别画（例：没有数据源就不要写「共 1,284 部」）。

## 3. 截图

在设计稿目录里装 Playwright 和 Chromium：

```bash
npm i -D playwright
npx playwright install chromium
# Linux 缺系统依赖时
npx playwright install-deps chromium
```

脚本 `shot.mjs`，按需改名单和尺寸：

```js
import { chromium } from 'playwright'

const b = await chromium.launch()
for (const [n, w, h, s] of [['home', 1440, 900, 1.25]]) {
  const p = await b.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: s })
  await p.goto(`file://${process.cwd()}/${n}.html`)
  await p.waitForTimeout(400) // 等图片和字体
  await p.screenshot({ path: `${n}.png` }) // 长页加 fullPage: true
}
await b.close()
```

- 预览用 deviceScaleFactor 1.25～2。要交付固定像素素材时用 3x 截，再用 PIL `resize(..., LANCZOS)` 缩到目标尺寸（BMP、ICO 用 PIL 存）。
- 转 jpg 减小体积：`Image.open(p).convert('RGB').save(j, quality=85)`。

## 4. 自查再发

- 自己打开截图检查：文字被压住、溢出或折行，对比度不够，留白不均，图片白边。修完重截。
- 把图发给用户，附一句话：方案差异、你的推荐、需要用户决定的事（选哪版、开不开工）。
- 记下 html 路径。用户确认后按图实现时，把 html 和截图路径交给实现者当规格。

## 5. 按图实现后

- 实现者对真实前端截图（构建后用假数据跑，可用 `control-ui`），放到同目录 `impl-*.png`，列出与设计图不一致之处及原因（数据源缺失、规范冲突等）。
