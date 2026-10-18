# 动画现成做法

最常遇到的几种情况的现成实现。从现成做法开始，再按需调整——不要从头重做。

曲线指的是 SKILL.md 里定义的 `--ease-out`、`--ease-in-out` 和 `--ease-drawer` 这几个 token。

---

## 按钮按下

任何可以按的元素。即时反馈，告诉用户界面“听到了”。

```css
.button {
  transition: transform 160ms var(--ease-out);
}

.button:active {
  transform: scale(0.97);
}
```

`scale()` 也会缩放子元素——文字和图标跟着一起缩，这才让它看起来像真的被按下去了。

这里不需要悬停判断：在触屏上 `:active` 就是真正的按下。任何 `:hover` 样式另外单独判断。

---

## 下拉菜单、气泡框、菜单、下拉选择

从触发它的元素里缩放出来，而不是凭空出现。

```css
.popover {
  transform-origin: var(--transform-origin); /* Base UI supplies this */
  transition:
    opacity 200ms var(--ease-out),
    transform 200ms var(--ease-out);
}

.popover[data-starting-style],
.popover[data-ending-style] {
  opacity: 0;
  transform: scale(0.95);
}
```

（代码注释意思：Base UI 会提供这个值。）

关键就在 `transform-origin`——面板应该看起来是从你点的那个东西里出来的。

---

## 提示框（tooltip）

和气泡框一样的结构，更快，再加上大多数实现都漏掉的那个细节。

```css
.tooltip {
  transform-origin: var(--transform-origin);
  transition:
    transform 125ms var(--ease-out),
    opacity 125ms var(--ease-out);
}

.tooltip[data-starting-style],
.tooltip[data-ending-style] {
  opacity: 0;
  transform: scale(0.97);
}

/* Once one tooltip is open, neighbours open instantly */
.tooltip[data-instant] {
  transition-duration: 0ms;
}
```

（代码注释意思：一旦有一个提示框打开了，旁边的提示框就立刻打开。）

一开始的延迟是为了防止误触发。之后，跳过延迟和动画，会让整个工具栏感觉更快。

---

## 弹窗（modal）

唯一保持居中的弹出层。

```css
.modal {
  transform-origin: center; /* exempt — not anchored to a trigger */
  transition:
    opacity 250ms var(--ease-out),
    transform 250ms var(--ease-out);
}

.modal[data-starting-style],
.modal[data-ending-style] {
  opacity: 0;
  transform: scale(0.96);
}

.backdrop {
  transition: opacity 250ms var(--ease-out);
}
```

（代码注释意思：例外——它不锚定在触发元素上。）

背景遮罩的透明度要和它一起动，让它们看起来是同一个表面。

---

## 抽屉 / 底部面板

```css
.drawer {
  transform: translateY(0);
  transition: transform 500ms var(--ease-drawer);
}

.drawer[data-closed] {
  transform: translateY(100%);
}
```

Vaul 就是这样先把抽屉藏起来，再让它动画进场的。

加上拖动之后，它就变成了一个手势问题——见下面的**拖动关闭**。

---

## 提示消息（toast）

```css
.toast {
  opacity: 1;
  transform: translateY(0);
  transition:
    opacity 400ms ease,
    transform 400ms ease;

  @starting-style {
    opacity: 0;
    transform: translateY(100%);
  }
}
```

- 用 `ease` 而不是 `ease-out`，比一般界面稍微慢一点：Sonner 之所以显得优雅，部分原因是它的动效是按这个组件的性格调的，而不是按通用的界面预算。
- 如果不能用 `@starting-style`，就退回到用“已挂载”标记：

```jsx
useEffect(() => { setMounted(true); }, []);
// <div data-mounted={mounted}>
```

当提示消息叠在一起、列表重新排布时，透明度变化要和高度变化配合好。这一对没有公式可套——调到感觉对为止，然后第二天再检查一遍。

---

## 手风琴 / 折叠

```css
.content {
  overflow: hidden;
  transition:
    height 200ms var(--ease-out),
    opacity 200ms var(--ease-out);
}
```

保持简短——这是少数每一帧都要付出布局代价的动画之一，所以时长长了不只是拖沓，还很耗性能。用 JS 测量内容高度（或者用一个能提供高度的无样式基础组件），而不是动画到 `auto`。

---

## 一组元素错开进场

用于用户偶尔才看到的列表或网格——不要用于用户整天滚来滚去的列表。

```css
.item {
  opacity: 0;
  transform: translateY(8px);
  animation: fadeIn 300ms var(--ease-out) forwards;
}

.item:nth-child(2) { animation-delay: 50ms; }
.item:nth-child(3) { animation-delay: 100ms; }
.item:nth-child(4) { animation-delay: 150ms; }

@keyframes fadeIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

错开只是装饰——它在播放时绝不能挡住交互。

---

## 长按确认

用于破坏性操作，普通的点一下太容易误触。

```css
.overlay {
  clip-path: inset(0 100% 0 0);
  transition: clip-path 200ms var(--ease-out); /* release: snappy */
}

.button:active .overlay {
  clip-path: inset(0 0 0 0);
  transition: clip-path 2s linear;             /* press: slow and deliberate */
}

.button:active {
  transform: scale(0.97);
}
```

（代码注释意思：松手时干脆；按住时慢而刻意。）

这里用 `linear` 是对的——填充是一个进度指示，进度不应该有缓动。

---

## 带颜色过渡的标签页指示条

给标签列表里的每个颜色过渡单独调时间，总是对不准。改用裁剪。

把标签列表复制一份。把副本的样式设成选中状态——不同的背景、不同的文字颜色。裁剪副本，只露出选中的那个标签，切换时对裁剪做动画：

```css
.tabs-active-copy {
  clip-path: inset(0 60% 0 20%); /* driven by the active tab's position */
  transition: clip-path 250ms var(--ease-in-out);
}
```

（代码注释意思：由选中标签的位置来驱动。）

文字和背景同时变化，完全同步，因为它们是一个正在被露出来的元素，而不是两种颜色在插值。

---

## 滚动时出现

只用于营销页面。不要用在用户每天都要用的功能界面上。

```css
.reveal {
  clip-path: inset(0 0 100% 0);
  transition: clip-path 600ms var(--ease-in-out);
}

.reveal[data-visible] {
  clip-path: inset(0 0 0 0);
}
```

用 `IntersectionObserver` 触发，或者用 Motion 的 `useInView` 加 `{ once: true, margin: "-100px" }`。只触发一次——每次滚过都重新播放动画，就是界面在跟读者作对。

---

## 拖动关闭

手势的做法。用弹簧，不用时长，因为用户可能在运动途中反向。

```js
// Dismiss on a flick, not just on distance
const timeTaken = Date.now() - dragStartTime.current;
const velocity = Math.abs(swipeAmount) / timeTaken;

if (Math.abs(swipeAmount) >= SWIPE_THRESHOLD || velocity > 0.11) {
  dismiss();
}
```

（代码注释意思：轻弹就关闭，不只看拖动距离。）

```js
// Set transform on the dragged element directly.
// Driving it through a CSS variable on the parent recalcs styles for every child.
element.style.transform = `translateY(${distance}px)`;
```

（代码注释意思：直接在被拖动的元素上设置 transform；通过父元素上的 CSS 变量来驱动，会让每个子元素都重新计算样式。）

区分好的拖动和差的拖动的四个细节：

- **拖动一开始就捕获指针**，这样指针离开元素范围时拖动还能继续。
- **防多点触控**——有新的触点时 `if (isDragging) return`，否则拖动途中换手指会让元素跳一下。
- **越过边界后加阻尼**——拖过自然边缘时，拖得越远，元素动得越少。真实的东西在停下之前会先变慢。
- **是摩擦，不是墙**——允许拖过头，但阻力越来越大，而不是直接不让拖。

用弹簧收尾，这样被打断的拖动能保留它的速度：

```js
{ type: "spring", duration: 0.5, bounce: 0.2 }
```

---

## 遮掩一个怎么调都不顺的交叉淡入淡出

当两个状态在过渡中明显重叠，怎么调缓动和时长都解决不了时，就把接缝模糊掉：

```css
.content {
  transition:
    filter 200ms ease,
    opacity 200ms ease;
}

.content.transitioning {
  filter: blur(2px);
  opacity: 0.7;
}
```

不加模糊，眼睛看到的是两个不同的东西在互换。加了模糊，它们会融合成一次被感知为整体的变化。保持在 20px 以内——重度模糊很耗性能，在 Safari 上尤其如此。

---

## 用程序控制，不用库

当动效需要 JS 控制、但又不想加依赖时，WAAPI 能给你 CSS 级别的性能：

```js
element.animate(
  [{ clipPath: 'inset(0 0 100% 0)' }, { clipPath: 'inset(0 0 0 0)' }],
  { duration: 1000, fill: 'forwards', easing: 'cubic-bezier(0.77, 0, 0.175, 1)' }
);
```

硬件加速、可打断、不增加打包体积。
