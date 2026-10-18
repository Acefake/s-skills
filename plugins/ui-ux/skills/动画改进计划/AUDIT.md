# 动画审计手册

> （本文件是 `动画改进计划` 的参考文件，翻译自 Emil Kowalski 的仓库 https://github.com/emilkowalski/skills 的 `skills/improve-animations/AUDIT.md`，许可证 MIT，仅供自用。代码块和数值保持原样。）

八个审计类别、每一类要找什么，以及在发现和计划里要引用的准确目标数值。提炼自 Emil Kowalski 的设计工程理念（[emilkowal.ski](https://emilkowal.ski/)）。这里出现的数值绝不要估个大概——照抄。

## 1. 目的和频率

每个动画都必须回答“为什么要动？”——空间一致性、状态提示、反馈、讲解，或者避免突兀的变化。对于经常看到的元素，“看着很酷”不算目的。

| 频率 | 决定 |
| --- | --- |
| 每天 100 次以上（键盘快捷键、命令面板开关） | 不加动画。永远不加。 |
| 每天几十次（悬停效果、列表导航） | 去掉或大幅减弱 |
| 偶尔（弹窗、抽屉、提示消息） | 标准动画 |
| 很少 / 第一次（新手引导、反馈、庆祝） | 可以加点惊喜 |

要找的：键盘触发的操作上的动画、带打开/关闭过渡的命令面板（Raycast 没有——这是对的）、经常被碰到的列表项或悬停状态上的装饰性动效。最有力的修法往往是**删掉这个动画**。

## 2. 缓动和时长

缓动的决定顺序：

- 进场或退场 → **`ease-out`**（开头快，感觉灵敏）
- 在屏幕上移动 / 变形 → **`ease-in-out`**
- 悬停 / 颜色变化 → **`ease`**
- 持续运动（跑马灯、进度条） → **`linear`**
- 默认 → **`ease-out`**

**界面上用了 `ease-in` 一定算一条发现**——它开头慢，恰好拖慢了用户正盯着看的那一刻。CSS 自带的缓动对精心设计的动效来说太弱了；计划应该引入强力的自定义曲线（作为 token，符合仓库惯例）：

```css
--ease-out: cubic-bezier(0.23, 1, 0.32, 1);        /* strong ease-out for UI */
--ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);    /* strong ease-in-out for on-screen movement */
--ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);     /* iOS-like drawer curve */
```

（代码注释意思：界面用的强力 ease-out；屏幕上移动用的强力 ease-in-out；类似 iOS 的抽屉曲线。）

时长预算——**界面动画保持在 300ms 以内**：

| 元素 | 时长 |
| --- | --- |
| 按钮按下的反馈 | 100–160ms |
| 提示框、小气泡框 | 125–200ms |
| 下拉菜单、下拉选择 | 150–250ms |
| 弹窗、抽屉 | 200–500ms |
| 营销 / 讲解类 | 可以更长 |

要找的：任何地方的 `ease-in`、进场时用了光秃秃的 `ease`/`linear`、界面元素时长超过 300ms、工具栏里每个提示框都有延迟 + 动画（第一个之后，后面的应该立即出现）。

## 3. 物理感和原点

- **绝不用 `scale(0)`**——现实世界里没有东西是从无到有冒出来的。目标：`scale(0.9–0.97)` + `opacity: 0`。
- **气泡框/下拉菜单/提示框从触发元素缩放出来**，而不是从中心：
  ```css
  .popover { transform-origin: var(--transform-origin); } /* Base UI */
  ```
  **弹窗例外**——它们居中出现；那里用 `transform-origin: center` 是对的。不要报告它。
- **按下反馈**：`:active` 上 `transform: scale(0.97)`，配合 `transition: transform 160ms ease-out`。保持轻微（0.95–0.98）。

要找的：`scale(0)`、没有初始 transform 的纯淡入进场、锚定触发元素的元素上用了 `transform-origin: center`（或者没设）、没有按下反馈的可按元素。

## 4. 可打断性

CSS **transition** 在动画途中会从当前状态重新定目标；**关键帧**会从零重新开始。任何会被快速触发、或在运动途中可以反转的东西（提示消息堆叠、开关、拖动、展开/收起），都必须用 transition 或弹簧。

- 不用 JS 做进场：`@starting-style`（老办法：在 `useEffect` 里设置一个 `data-mounted` 属性）。
- 手势驱动的动效应该用弹簧——它们被打断时能带着速度。
- 弹簧参数，苹果风格（推荐）：`{ type: "spring", duration: 0.5, bounce: 0.2 }`。回弹保持轻微（0.1–0.3）；明显的回弹只留给拖动关闭和好玩的时刻。
- **不对称的时间**：用户刻意操作的阶段（按下、按住、破坏性确认）动得慢一些；系统的响应要干脆。按下和松开用对称的时间，算一条发现。

要找的：提示消息/开关/快速触发的界面上的 `@keyframes`、用固定时长关键帧做补间的手势处理函数、没有基于速度关闭的拖动（按 `Math.abs(distance)/elapsedMs > ~0.11` 关闭，而不是只看距离阈值）、拖动边界处硬停而不是阻力逐渐增大。

## 5. 性能

- **只动 `transform` 和 `opacity`。** `width`/`height`/`margin`/`padding`/`top`/`left` 会触发布局 + 绘制 + 合成。
- **`transition: all`** 会在 GPU 之外动到不想动的属性——一定算一条发现。
- **Framer Motion 的 `x`/`y`/`scale` 简写不走硬件加速**——它们在主线程上运行，高负载下会掉帧。目标：完整的 transform 字符串，`animate={{ transform: "translateX(100px)" }}`。
- **不要用父元素上的 CSS 变量去驱动子元素的 transform**——那会让所有子元素重新计算样式。直接在元素上设置 `transform`。
- 在高负载下，CSS（和 WAAPI）比基于 rAF 的 JS 好——预先定好的运动用 CSS，动态的、手势驱动的运动用 JS/弹簧。
- 过渡中的 `filter: blur()` 保持在 20px 以内——重度模糊很耗性能，在 Safari 上尤其如此。

要找的：`transition: all`、动画中的布局属性、繁忙页面上 Framer Motion 的简写属性、用 `setProperty('--x', …)` 驱动子元素 transform、本可以用 CSS 却用 rAF 循环做的事。

## 6. 无障碍

```css
@media (prefers-reduced-motion: reduce) {
  .element { animation: fade 0.2s ease; } /* keep opacity/color, drop movement */
}
@media (hover: hover) and (pointer: fine) {
  .element:hover { transform: scale(1.05); } /* touch fires false hovers on tap */
}
```

（代码注释意思：保留透明度/颜色，去掉移动；触屏点按时会触发假的悬停。）

减少动效的意思是动画更少、更温和，**不是一个都没有**——保留有助于理解的过渡，去掉位置变化。在 JS 里：用 `useReducedMotion()`，根据结果切换 transform 的值。

要找的：没有 `prefers-reduced-motion` 处理的移动、没加判断的 `:hover` 动效、把所有反馈都砍光的减少动效实现。

## 7. 一致性和 token

- 动效应该和产品的性格相符——活泼的可以更弹，仪表盘要保持干练。不同组件之间性格不一致，算一条发现。
- 曲线和时长应该作为共用的 token。五个手敲的、几乎一样的 cubic-bezier，算一条“需要整合”的发现。
- 本该有 **30–80ms 错开**的地方，一组元素却同时进场。错开只是装饰——绝不能挡住交互。
- 一个能看到两个重叠状态的突兀交叉淡入淡出，可以在过渡期间用轻微的 `filter: blur(2px)` 来遮掩。

要找的：重复的、几乎一样的缓动/时长，一个干练应用里出现一个很弹的组件，没有错开的列表/网格进场，看得出明显“双重曝光”的交叉淡入淡出。

## 8. 错过的机会

这是“新增”类——现在没动但应该动的地方：

- 瞬移的状态变化（内容切换、布局跳动），一个短暂的过渡就能避免突兀。
- 在空间上有关联的界面（从触发元素出现的面板），却没有动效说明它从哪来。
- 很少出现、情绪强烈的时刻（第一次运行、成功、庆祝），却一点都没用上允许的惊喜预算。
- 用 `translate` 百分比（`translateY(100%)` = 元素自身的高度）和 `clip-path: inset()` 揭开效果作为工具——不要写死像素偏移。

最多报告几条，要基于你实际观察到的用户体验缝隙——而不是一份愿望清单。
