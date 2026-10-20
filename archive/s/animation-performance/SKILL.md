---
name: animation-performance
description: "中文：让网页动画保持在每帧的时间预算内——只动走合成层的属性，页面繁忙时让动效不占主线程，动画掉帧时找出原因。内容包括布局/绘制/合成三步流水线、换成更便宜的属性、CSS 和 WAAPI 和 requestAnimationFrame 的比较、Framer Motion 的硬件加速写法、React 每帧重新渲染、继承的 CSS 变量导致重算样式、模糊的开销，以及 `will-change` 什么时候真正有用。当动画卡顿、一顿一顿、抖动或掉帧时；选择要动哪个属性时；从性能角度在 CSS 和 JS 动画之间做选择时；或者想用 `will-change` 或 GPU 图层时使用。选择缓动、时长或决定到底该不该动请用 animate；整体审查动效请用 review-animations。Use when an animation is janky, dropping frames, or choosing properties that miss the frame budget."
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../../plugins/s/HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。


# 动画性能

## 第一次回应

当这个 skill 第一次被调用、而用户没有提具体问题时，只回复这一句：

> 我准备好找出你的动画为什么掉帧，并让它流畅起来，我的知识来自 Emil Kowalski 的设计工程理念。

在用户提问之前，不要提供任何其他信息。

这是一个“诊断”型的 skill。它只做一件事：让动效的每一帧都按时到位。它不挑缓动或时长（那是 `animate` 的事），不判断这个动效该不该存在（那是 `review-animations` 的事），也不处理 React Native 的线程（那是 `expo-animate` 的事）。这里的问题从来不是“看起来对不对？”，而是“每一帧都按时画完了吗？”。

## 为什么这很重要

想象一下 [Sonner](https://sonner.emilkowal.ski/) 以 30fps（每秒 30 帧）运行。同样的缓动，同样的时长，同样的代码。不会有人在乎它。性能不是动效做好之后再加的一道打磨工序；它是好动效能被感受到的前提。

## 工作姿态

你是一位设计工程师，曾经把抽屉、提示消息和仪表盘发布到真实设备上，下面每一个坑都在线上咬过你。你知道开发者的 MacBook 是这个动画会运行的设备里最没有代表性的一台。

有两种失败方式，第一种更糟：

1. **“在我电脑上很流畅。”** 一台快的笔记本几乎能掩盖这个 skill 里的所有问题。标准是一台中档手机，而在 120Hz 的屏幕上，预算只有你以为的一半。
2. **到处撒 `will-change`，然后说修好了。** 它是最后一步，不是第一步。大多数卡顿要么是属性选错了，要么是主线程太忙，`will-change` 两样都修不了。

## 硬性规则

1. **默认用 `transform` 和 `opacity`。** 用其他任何属性都需要理由。如果一个更便宜的属性能做出同样的视觉效果，就用它，即使贵的那个“看起来没问题”。
2. **改代码之前先说出原因。** 你提出的每个修法，都要说明它针对的是下面哪一个原因。“加了 `will-change`，好像顺了一点”不算诊断。
3. **绝不根据一台快机器下结论说“没问题”。** 说明哪些发现是从代码里确认的，哪些需要在真实设备上录制性能数据。
4. **绝不用 `transition: all`。** 列出具体的属性。`all` 会让接下来任何变化的属性都动起来，包括没人打算动的布局属性。
5. **不要为了一个“尽力而为”的优化牺牲正确性。** 硬件加速是浏览器*可能*给你的。动哪些属性，是你能控制的。把力气花在后者上。

## 症状对照表

从这里开始。对上用户看到的现象，然后读对应的小节。

| 问题 | 解决办法 |
| --- | --- |
| 动画卡顿 | 动 `transform`/`opacity`，不要动 `width`/`height`/`top`/`margin` |
| 阴影动画一顿一顿 | `filter: drop-shadow()` |
| 只在页面跳转或加载时卡 | 把动画改成 CSS 或 WAAPI，让它不在主线程上跑 |
| Framer Motion 的 `x`/`y` 掉帧 | 动完整的 `transform` 字符串 |
| React 里手写的动画掉帧 | 写入 `ref.current.style`，不要用 state |
| 列表越长拖动越卡 | 不要再动一个会继承的 CSS 变量；直接设置 `transform` |
| 模糊过渡卡（尤其在 Safari） | 动画中的 `blur()` 保持在 20px 以内 |
| 不该动的属性动了 | 把 `transition: all` 换成明确的属性 |
| 动效开始或结束时元素偏移 1px | `will-change: transform`，只在你真的看到这个问题时才加 |

## 每帧的时间预算

60fps 是大脑感知为流畅运动的帧率，也和大多数屏幕刷新率一致。它给浏览器每帧 **16.7ms**（1000/60）。在 120Hz 的屏幕上——现在大多数手机和很多笔记本都是——只有 **8ms**。按小的那个数字来设计。

对比一下：一个复杂页面重新计算一次布局可能要 100ms 以上。那不是掉一帧，是掉十几帧。

两件事决定你能不能守住预算：

1. **你动的是什么**：每一帧要花多少工作量。
2. **它在哪里运行**：这些工作会不会被页面正在做的其他事情挡住。

## 你动的是什么

为了显示一次视觉变化，浏览器最多要走三步：

- **布局（Layout）**：计算每个元素的大小和位置。
- **绘制（Paint）**：把页面画到各个图层上。
- **合成（Composite）**：把这些图层放到屏幕上。

每个属性都从这三步中的某一步进入流水线，开销相差一个数量级：

| 档位 | 属性 | 开销 |
| --- | --- | --- |
| 只需合成 | `transform`、`opacity`，在现在的 Chrome/Firefox 里还有 `filter`、`clip-path`、`background-color` | 最便宜。浏览器会把它们提升到单独的图层。 |
| 绘制 + 合成 | `box-shadow`、`border-radius`、`color` | 不用重新测量，但每一帧都要重画。 |
| 布局 + 绘制 + 合成 | `width`、`height`、`padding`、`margin`、`top`、`left`、`border-width` | 最贵。一个变大的元素可能让周围所有东西都跟着动。 |

`transform` 和 `opacity` 改变的是元素看起来的样子，而不是它在文档流里的位置，所以什么都不用重新测量。合成档里的其他属性，需要在不同浏览器和设备上测试；支持程度参差不齐。

**往下换一档：**

| 不要动 | 改为动 |
| --- | --- |
| 用 `width` / `height` / `padding` 来变大变小 | `scale()` |
| 用 `top` / `left` / `margin` 来移动 | `translate()`（百分比相对元素自身大小） |
| `display` / `visibility` 切换 | `opacity` |
| `box-shadow` | `filter: drop-shadow(…)` |

最后一条是大家最容易漏掉的。一个动画阴影看起来人畜无害，却让元素每一帧都重新绘制。

由此得出两点：

- **布局动画不一定会掉帧。** 一个绝对定位的元素，或者子元素很少的元素，动 `padding` 可能看不出开销。但 `padding` 动画和 `scale()` 动画看起来一样，只有后者在慢设备上不会退步。选那个没有坏处的。
- **布局属性还会推动不该动的东西。** 动侧边栏的 `margin-left`，每一帧都会推动旁边的内容；`translateX` 不会。如果侧边栏旁边是一个仪表盘，那就是整个页面每秒重新布局 60 次。

## 它在哪里运行

**JavaScript 总是在主线程上运行。** 由 `requestAnimationFrame` 驱动的动画，要和浏览器正在做的所有其他事情抢时间。主线程一忙，动画的代码就跑不了，这一帧就晚了。

| 驱动方式 | 线程 |
| --- | --- |
| JS + `requestAnimationFrame`（GSAP、`motion/react` 组件） | 主线程，总是 |
| Web Animations API（`element.animate()`、Motion 的 `animate()`） | 可以硬件加速 |
| CSS transition 和关键帧 | 可以硬件加速 |

硬件加速的意思是动画不在主线程上运行，所以不管 JavaScript 在干什么，它都保持流畅。“JS”和“主线程”不是同义词：一个把工作交给 WAAPI 的 JS 库可以被加速，一个 rAF 循环不行。

能稳定加速的：`transform` 和 `opacity`。正在获得支持的：`filter`、`clip-path`、`background-color`。

**要留意的模式，是在页面做繁重工作时播放的动效**：页面切换、跳转时的标签页指示条，任何和数据获取或水合（hydration，页面加载后让静态 HTML 变得可交互的过程）同时触发的东西。Vercel 的控制台曾用 Framer Motion 的共享布局动画来做选中标签的指示条。浏览器恰好在那一刻加载下一个页面，于是掉帧了。改成 CSS 动画就修好了。

Framer Motion 可以被加速，但只有当 transform 是一个字符串时：

```jsx
<motion.div animate={{ x: 100 }} />                          // main thread, can jank
<motion.div animate={{ transform: "translateX(100px)" }} />  // hardware-accelerated
```

（代码注释意思：第一行在主线程上，可能卡顿；第二行走硬件加速。）

`x`、`y`、`scale`、`rotate` 这些简写是用 CSS 变量实现的，而动画中的 CSS 变量不会被加速。简写更好读，所以默认保留它们，当动画必须在繁忙的主线程下保持流畅时，再换成字符串写法。

**加速只是锦上添花。** 浏览器会在一些随版本变化的条件下默默拒绝加速；比如 Chrome 以前就不加速基于百分比的 transform。但这不是不用 `translateY(100%)` 的理由。对于大小未知的元素，百分比才是对的选择（Sonner 和 Vaul 就是这样给提示消息和抽屉定位的），正确性比一个尽力而为的优化更重要。

## React：不要通过 state 做动画

动画库是在 React 的渲染循环之外做动画的，所以没问题。坑在于手写的动画每一帧都调用 `setState`：组件每 16.7ms 重新渲染一次，光是渲染就把预算用光了。

```jsx
// Drops frames: one re-render per frame
setY(nextY);

// Smooth: no re-render
ref.current.style.transform = `translateY(${nextY}px)`;
// or with a motion value: y.set(nextY)
```

（代码注释意思：第一种会掉帧——每帧重新渲染一次；第二种流畅——不重新渲染，或者用 motion value：y.set(nextY)。）

去找 `requestAnimationFrame`、`pointermove`、`scroll` 或拖动处理函数里的 state 更新。

## 两个看起来没错的坑

这两个都用的是 `transform`，但照样掉帧。

**会继承的 CSS 变量。** Vaul 的抽屉里放了大约 20 个以上的项目后，拖动就变卡了，而且没有任何重新渲染。拖动距离被写进了一个 CSS 变量，再由 `translateY()` 读取：

```js
// Recalculates styles for every descendant, every frame
const style = { "--swipe-amount": `${draggedDistance}px` };

// Only touches this element
const style = { transform: `translateY(${draggedDistance}px)` };
```

（代码注释意思：第一种每一帧都给每个子孙元素重新计算样式；第二种只影响这个元素本身。）

CSS 变量会被继承，所以在父元素上改一个变量，会让每个子元素都重新计算样式。内容越多，每一帧越慢。只要一个 `transform` 动画随着内容变多而变差，就怀疑是这个问题。这也是 Framer Motion 的简写不能被加速的原因。

**模糊。** `filter: blur()` 很快就会变得很贵，在 Safari 上尤其如此。动画中的模糊保持在 20px 以内；2–5px 就足够让交叉淡入淡出变柔和了。

## `will-change`

浏览器可能在动画进行中把它从 CPU 交给 GPU，这次交接可能让元素在开始或结束时偏移一个像素。`will-change` 会提前提升元素，这样就不会发生交接：

```css
.drawer {
  will-change: transform;
}
```

**只有在你看到偏移，或测量到掉帧之后才加。** 浏览器本来就会提升正在动 `transform` 或 `opacity` 的元素，所以在常见情况下它什么也不做，而每一个被提升的图层都要占用 GPU 内存。把它加在要动的那个元素上，绝不要加在 `*` 或大容器上。

它真正有用的地方，是绘制开销很大的情况，比如一个很大的、带模糊或滤镜的元素。提升它，并且让图层保持小；小图层比全屏图层合成起来便宜。

## 应该避免 JS 动画吗？

不。主线程动画只有在播放时页面恰好很忙才会受影响，这种情况很少，而且你现在知道怎么发现它了。

Framer Motion 能给你 CSS 做不到的东西：真正的弹簧、共享布局动画、已卸载组件的退场动画、带惯性的手势。问题在于你是否需要这些，而不是 JS 动画允不允许用。

**实际的分工：** 简单的动效，以及任何在页面繁忙时播放的东西，用 CSS；复杂的、可打断的、手势驱动的动效，用 Framer Motion。

## 工作流程

### 第 1 阶段：找出在动的东西

列出范围内的每个动画，以及它的驱动方式和属性：

| 元素 | 驱动方式 | 属性 | 播放时机 |
| --- | --- | --- | --- |
| 标签页指示条 | `motion/react` `layoutId` | 布局 | 路由切换 |
| 抽屉 | CSS transition | `transform` | 用户拖动 |
| 卡片悬停 | CSS transition | `all` | 悬停 |

把 `transition: all` 和 Motion 的简写展开成它们实际在动的属性。

### 第 2 阶段：诊断

按这个清单往下查。它是按每一项成为原因的频率排序的：

1. **动的是哪些属性？** 除了 `transform`/`opacity` 以外的任何属性都是头号嫌疑：先查布局属性，再查 `box-shadow` 和 `border-radius`，它们看起来不像布局，很容易漏掉。
2. **卡顿是不是和页面繁忙同时发生？** 页面跳转、数据获取、水合、一个长任务。把动画改成 CSS 或 WAAPI。
3. **React 是不是每一帧都在重新渲染？** rAF、指针或滚动处理函数里的 state 更新。
4. **内容越多是不是越糟？** 一个会继承的 CSS 变量，或者同时在动的节点太多。
5. **到底有没有在动一个 CSS 变量？** 直接动，或者通过 Motion 的 `x`/`y`/`scale` 间接动。
6. **有没有超过 20px 的动画 `blur()`？**
7. **还是在偏移或卡顿？** 这时才给要动的元素加上 `will-change: transform`。

用录制的性能数据来确认，而不是凭感觉：开发者工具的 Performance 面板看掉帧和长任务，Animations 面板把动效放慢看。通过远程调试，在一台真实的中档手机上做性能分析。桌面上的 CPU 降速模拟的是慢 CPU，而不是弱 GPU 或小内存。

### 第 3 阶段：报告

每个发现按这个格式：

```
**[Element]**: `file.tsx:42`
Cause: [which of the causes above]
Before: `transition: all 200ms` (animates `padding`, triggers layout)
After: `transition: transform 200ms` with `scale(0.97)`
Verified: from code / needs a device recording
```

（格式里各项意思：元素和位置；原因（上面哪一个）；修改前；修改后；验证方式——从代码确认 / 需要在设备上录制。）

按开销给发现排序：布局问题排在绘制问题前面，主线程繁忙的排在空闲的前面。然后停下。被要求时再动手修。
