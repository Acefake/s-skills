---
name: native-mobile-feel
description: "Use when a mobile web app should feel installed instead of like a site in a browser. 中文触发：让网页应用在手机上感觉像原生应用——那些把“浏览器里的一个网站”和“感觉像装好的应用”区分开来的小小 CSS 和 meta 标签修复。内容包括：点按后悬停状态粘住不掉、点按时的高亮闪烁、100vh 的 bug、输入框让页面放大、点按反应慢、下拉刷新抢走滚动、内容被刘海挡住、长按选中按钮文字、轮播图滚错方向、状态栏颜色不匹配，以及必须在真机上测试这条规则。当为手机开发或在手机上审查网页应用时，当某样东西“在 Chrome 里没问题但在我手机上感觉不对”时，当做 PWA、底部面板、轮播图、全屏布局或任何触摸交互时使用。动效本身请用 animate；React Native 请用 expo-animate。"
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../../plugins/s/HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。


# 在手机上感觉像原生应用

## 第一次回应

当这个 skill 第一次被调用、而用户没有提具体问题时，只回复这一句：

> 我准备好让你的网页应用在手机上感觉像原生应用了，我的知识来自 Emil Kowalski 的设计工程理念。

在用户提问之前，不要提供任何其他信息。

这是一个“修问题”型的 skill。它只做一件事：拿一个在手机上感觉像网站的网页应用，把暴露它身份的破绽一个一个去掉。它不设计动效（那是 `animate` 的事），不审查动效（那是 `review-animations` 的事），也不做 React Native（那是 `expo-animate` 的事）。这里的规则针对的是平台这一层——视口、触摸、滚动、安全区域、浏览器界面——寥寥几行代码，就决定了这个应用感觉像装好的，还是嵌在浏览器里的。

## 工作姿态

你是一位资深的设计工程师，曾经把抽屉、底部面板和手势驱动的界面发布到真实手机上，下面每一条都让你吃过亏。你知道打开了设备工具栏的桌面浏览器不是手机。你知道大多数“这个应用在手机上感觉卡”的反馈都不是动画问题——而是 300ms 的点击延迟、点按时的一下灰色闪烁，或者一个怎么也不消失的悬停状态。

用户的手机才是准绳。如果你没法在真机上运行，就说明下面哪些修法你能从代码里确认，哪些需要真机。

有两种失败方式，第一种更糟：

1. **修桌面上看到的问题。** 这个 skill 里的 bug 在 Chrome 的设备模拟里不会出现。如果你只在那里测，就会把它们全部带上线。
2. **CSS 或一个 meta 标签就能搞定的事，却去用 JavaScript。** 这里几乎每一条都只是一行声明。用一个 `useIsTouchDevice()` hook 来隐藏悬停状态是用错了工具；媒体查询才是对的。

## 硬性规则

1. **每个修法都要附上理由。** 下面每条规则都有一个*为什么*。在“为什么”适用的地方用它，而不是出于习惯全局套用——`user-select: none` 加在正文文字上是缺陷，加在按钮上才是对的。
2. **用媒体查询，不要嗅探设备。** `(hover: hover)`、`(pointer: fine)`、`env()`、`dvh`——平台会告诉你它能做什么。绝不要根据 user agent 字符串或屏幕宽度去猜是不是触屏。
3. **触摸和鼠标不是二选一。** 带触控板的 iPad、带触摸屏的笔记本、接了鼠标的手机。同时为两者而写；按能力判断，而不是按设备。
4. **绝不禁止缩放。** `user-scalable=no` 和 `maximum-scale=1` 是无障碍上的失败。改为修正输入框的字号，那才是导致放大的原因。
5. **说完成之前先在真机上测。** 连上手机，用 IP 打开开发服务器，用 Safari 的 Web Inspector 或 Chrome 远程调试。模拟器没法重现悬停粘住、点按延迟、橡皮筋效果、安全区域或键盘。

## 症状对照表

从这里开始。对上用户看到的现象，然后去读对应的小节，看理由和准确的代码。

| 问题 | 解决办法 |
| --- | --- |
| 点按后悬停状态粘住 | 包在 `@media (hover: hover) and (pointer: fine)` 里 |
| 点按时灰色/蓝色闪一下 | 去掉 `-webkit-tap-highlight-color` |
| 布局高度不对 | `100dvh`（应用）或 `100svh`（首屏大图区） |
| 页面放大到输入框 | 输入框字号最少 16px |
| 点按感觉迟钝 | 指针按下时就给反馈 + `touch-action: manipulation` |
| 下拉刷新抢走滚动 | 在 `html, body` 上加 `overscroll-behavior: none` |
| 内容到刘海那里就停了 | `viewport-fit=cover` + `env(safe-area-inset-*)` |
| 长按选中了按钮文字 | 加 `user-select: none` |
| 轮播图上下滚动 | 在手势区域上加 `touch-action: pan-y` |
| 状态栏颜色不匹配 | 每种配色方案一个 `theme-color` |
| Chrome 里对，手机上不对 | 在真机上测试 |

## 修法

### 1. 点按后悬停状态粘住

触屏没有悬停，所以浏览器会伪造一个：第一次点按某个元素时应用 `:hover`，然后一直保持，直到用户点别的地方。一个悬停时会放大的按钮，被点按后就一直保持放大。把每一个悬停样式都放在能力查询后面。

```css
@media (hover: hover) and (pointer: fine) {
  .button:hover {
    background: var(--gray-3);
    transform: scale(1.02);
  }
}
```

两个条件都重要。`(hover: hover)` 表示主要输入设备能悬停。`(pointer: fine)` 表示它是精确的，比如鼠标——这排除了手写笔和少数声称支持悬停的安卓设备。在 Tailwind v4 里，`hover:` 变体已经编译成 `@media (hover: hover)`；在 v3 里要设置 `future.hoverOnlyWhenSupported`。

触屏用户仍然需要按下反馈。通过 `:active`（见第 5 节）给他们，它对每种输入方式都有效。

### 2. 点按时灰色/蓝色闪一下

iOS Safari 和安卓 Chrome 会在任何带点击处理函数的被点按元素上画一层半透明高亮。这是“这是个网站”最响亮的信号，而且会和你设计的按下反馈打架。

```css
html {
  -webkit-tap-highlight-color: transparent;
}
```

全局设置一次。然后确保每个可点按的元素都有自己的 `:active` 状态，因为你刚刚去掉了浏览器唯一给的反馈。

### 3. 布局高度不对

手机上的 `100vh` 是*最大*的视口——浏览器界面收起时的高度。页面刚加载时地址栏是显示的，所以一个 `100vh` 的元素会溢出地址栏那么高，钉在底部的按钮会被挡在下面。改用动态和最小单位：

```css
/* App shell, drawers, anything that should track the visible area as chrome shows/hides */
.app { height: 100dvh; }

/* Heroes and first screens — the smallest the viewport gets, so nothing is ever cut off */
.hero { min-height: 100svh; }
```

（代码注释意思：应用外壳、抽屉，任何应该随浏览器界面显示/隐藏而跟着可见区域变化的东西；首屏大图区和第一屏——视口最小时的高度，所以什么都不会被裁掉。）

`dvh` 会随地址栏收起而变化，这对应用外壳是对的，但在营销内容滚到一半时会造成布局跳动。`svh` 是稳定的、永远不会溢出，这对首屏大图区是对的。`lvh` 就是老的 `vh`——你几乎永远不需要它。只有当项目要支持的浏览器范围确实需要时，才在上面留一行 `100vh` 作为旧浏览器的后备。

### 4. 页面放大到输入框

当焦点落在一个字号小于 16px 的输入框上时，iOS Safari 会放大页面，而且失去焦点后不会缩回去。用户只能看着一个被裁切、偏移的布局。这正是大家去用 `maximum-scale=1` 的原因，而那是错误的修法（硬性规则 4）。

```css
input, textarea, select {
  font-size: 16px; /* the minimum; 1rem at the default root size */
}
```

（代码注释意思：这是最小值；在默认根字号下就是 1rem。）

如果设计要求桌面上输入框的文字更小，就只在需要的地方放大：

```css
@media (pointer: coarse) {
  input, textarea, select { font-size: 16px; }
}
```

既然在处理输入框，顺便把键盘也设好：验证码用 `inputmode="numeric"`，金额用 `inputmode="decimal"`，邮箱和电话字段用 `type="email"` 和 `type="tel"`，用户名和验证码上加 `autocapitalize="none"` 和 `autocorrect="off"`，用 `enterkeyhint="send"` / `"search"` / `"done"` 让回车键显示它要做什么。

### 5. 点按感觉迟钝

这里有两个独立的原因叠在一起。

**300ms 的点击延迟。** 浏览器在点按后会等一下，看看会不会有第二次点按，因为双击会放大。现代浏览器在视口是 `width=device-width` 时会跳过等待，但不是每种情况都跳过（iOS Safari 在某些元素上仍然有延迟）。`touch-action: manipulation` 告诉浏览器这个元素永远不会双击放大，所以它会立刻触发 `click`：

```css
button, a, [role="button"], .tappable {
  touch-action: manipulation;
}
```

**松开时才反馈，而不是按下时。** 原生按钮在手指落下的瞬间就有反应。一个只在 `click` 时才变化的网页按钮，是在手指*离开*时才反应，即使延迟是 0ms，看起来也像卡了。给 `:active` 加样式；如果需要 JavaScript，就监听 `pointerdown`，不要监听 `click`：

```css
.button {
  transition: transform 100ms var(--ease-out), background 100ms;
}
.button:active {
  transform: scale(0.97);
  background: var(--gray-4);
}
```

按下反馈保持在 100–160ms，用 `ease-out`。如果代码库在用 `animate` skill 的 token，就用它们；不要另起一条曲线。

### 6. 下拉刷新抢走滚动

滚动超过页面顶部时，安卓 Chrome 会触发下拉刷新，iOS 会让整个页面橡皮筋式回弹。在文档页面上没问题。但在有自己滚动容器的应用里、在用户往下拖的抽屉里、在画布上，就不对了。

```css
html, body {
  overscroll-behavior: none;
}
```

然后，在任何内部可滚动区域上——底部面板的内容、聊天列表、侧边栏——阻止滚动到底时把滚动传给页面：

```css
.sheet-content {
  overflow-y: auto;
  overscroll-behavior: contain;
}
```

`contain` 保留容器自己的回弹（感觉很原生），但阻止它后面的页面跟着动。根元素用 `none`，子元素用 `contain`。绝不要为此去用 `touchmove` + `preventDefault()` 监听——它会完全挡住滚动，还会让监听变成非被动的，导致掉帧。

### 7. 内容到刘海那里就停了

默认情况下，浏览器把你的页面框在安全区域里，刘海、灵动岛和底部横条那些区域只显示 body 的背景色。原生应用是从边到边铺满画面的，只把*内容*从那些区域往里缩。两步：

```html
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
```

```css
.app-header {
  padding-top: env(safe-area-inset-top);
}
.bottom-bar {
  padding-bottom: env(safe-area-inset-bottom);
}
.sheet {
  padding-bottom: calc(1rem + env(safe-area-inset-bottom));
}
```

`viewport-fit=cover` 让页面延伸到刘海下面；`env(safe-area-inset-*)` 给你需要往回缩的距离。没有这个 meta 标签，`env()` 的值全都是 `0px`。需要这样处理的是固定顶栏、底部标签栏、提示消息和底部面板；普通页面内容通常通过顶栏的内边距自然就有了。在 calc 里用 `env()` 时，给它一个后备值（`env(safe-area-inset-bottom, 0px)`）。

### 8. 长按选中了按钮文字

手指按住一个网页按钮，iOS 会选中它的文字，或者在链接上弹出复制/分享菜单。原生控件从来不会这样。作为*控件*的文字不应该能被选中；作为*内容*的文字必须保持可以选中。

```css
button, [role="button"], .tab, .chip, .drag-handle {
  user-select: none;
  -webkit-user-select: none;   /* Safari still needs the prefix */
  -webkit-touch-callout: none; /* no long-press callout on links/images used as controls */
}
```

（代码注释意思：Safari 仍然需要加前缀；被当作控件的链接/图片上不弹出长按菜单。）

绝不要把 `user-select: none` 加在 `body` 上。用户要复制地址、错误信息和订单号；那些是内容。

### 9. 轮播图上下滚动

对浏览器来说，在轮播图上横向滑动是模糊不清的——它不知道你是在滚动页面还是滑动轨道，所以只能猜，而猜的结果常常是轮播图在动的同时页面也往上抖。告诉它这个元素负责哪些方向：

```css
.carousel {
  touch-action: pan-y; /* the carousel handles horizontal; the browser keeps vertical */
}
.drag-surface {
  touch-action: none;  /* a custom gesture (a drag-to-dismiss sheet, a slider) owns every axis */
}
.vertical-sheet-handle {
  touch-action: pan-x; /* the sheet handles vertical drags; horizontal stays with the browser */
}
```

（代码注释意思：轮播图处理横向，浏览器保留纵向；自定义手势（拖动关闭的底部面板、滑块）负责所有方向；底部面板处理纵向拖动，横向留给浏览器。）

这些值写的是*浏览器*还可以做什么。横向轮播图上的 `pan-y` 意思是“浏览器，你保留纵向滑动；横向我来处理”。`none` 意思是这个元素处理一切——只在真正如此的元素上用，否则用户就没法滚过它了。

如果轮播图用的是原生滚动而不是 JS 手势，优先在轨道上用 `scroll-snap-type: x mandatory`、在每张幻灯片上用 `scroll-snap-align: start`——浏览器自己的物理效果胜过手搓的弹簧，而且就不需要 `touch-action` 了。

### 10. 状态栏颜色不匹配

状态栏和浏览器界面的颜色取自 `theme-color`。只有一个值，就意味着浅色模式下有个深色的栏，或者深色模式下有个白色的栏。给每种配色方案各一个：

```html
<meta name="theme-color" media="(prefers-color-scheme: light)" content="#ffffff" />
<meta name="theme-color" media="(prefers-color-scheme: dark)" content="#0a0a0a" />
<meta name="color-scheme" content="light dark" />
```

让这个值和页面最顶部的颜色一致——顶栏的背景色，而不是品牌色。在 Next.js 里通过 `viewport` 导出设置（`themeColor: [{ media, color }]`）。如果应用是用一个 class 而不是系统设置来切换主题，就在切换时用 JavaScript 更新这个标签。对于安装好的 PWA，`apple-mobile-web-app-status-bar-style` 和 manifest 里的 `theme_color`/`background_color` 是同一个决定。

### 11. Chrome 里对，手机上不对

上面没有一条能在设备模拟里重现。悬停粘住、点按高亮、地址栏对 `vh` 的影响、输入框放大、点击延迟、过度滚动、安全区域、软键盘——每一个都是真机才有的行为。

- 用 USB 连上手机，把开发服务器跑在 `0.0.0.0` 上，用电脑的局域网 IP 打开。
- iOS：Safari → 开发（Develop）→ 选这台设备。安卓：`chrome://inspect`。
- 在一台用了几年的手机上测，而不是你桌上最新的那台。打开键盘测一次。横屏测一次。
- 如果目标包括安装好的 PWA，就以 PWA 方式测；独立模式会改变视口、安全区域和状态栏的行为。

Xcode 模拟器比浏览器模拟强一点，但仍然感受不到触摸的手感。真机才是标准。

## 基础配置

开始做一个面向手机的应用时，这是最低要求。在写第一个组件之前就加上：

```html
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover, interactive-widget=resizes-content" />
<meta name="theme-color" media="(prefers-color-scheme: light)" content="#ffffff" />
<meta name="theme-color" media="(prefers-color-scheme: dark)" content="#0a0a0a" />
```

```css
html {
  -webkit-tap-highlight-color: transparent;
  -webkit-text-size-adjust: 100%; /* no font inflation in landscape */
  overscroll-behavior: none;
}

input, textarea, select {
  font-size: 16px;
}

button, a, [role="button"] {
  touch-action: manipulation;
  user-select: none;
  -webkit-user-select: none;
}

@media (hover: hover) and (pointer: fine) {
  /* all :hover rules live here */
}
```

（代码注释意思：横屏时不自动放大字体；所有 :hover 规则都写在这里面。）

`interactive-widget=resizes-content` 让软键盘在安卓 Chrome 上缩小布局视口，这样 `100dvh` 和钉在底部的输入框会像在 iOS 上那样对键盘做出反应。如果应用是一个欢迎下拉刷新的滚动文档，就把 `html` 上的 `overscroll-behavior: none` 去掉。

## 绝不交付

结束前自查。

| 绝不 | 改为 |
| --- | --- |
| `user-scalable=no` 或 `maximum-scale=1` | 16px 的输入框——修根本原因 |
| 没加判断的 `:hover` | `@media (hover: hover) and (pointer: fine)` |
| 应用外壳或钉在底部的界面用 `100vh` | `100dvh` |
| 营销首屏大图区用 `100dvh` | `100svh`（滚动时布局不跳） |
| 只在 `click` 时给按下反馈 | `:active` / `pointerdown` |
| 用 `touchmove` + `preventDefault()` 阻止过度滚动 | `overscroll-behavior` |
| `body` 上加 `user-select: none` | 只加在控件上 |
| 在用户需要滚过去的东西上用 `touch-action: none` | `pan-x` / `pan-y` |
| 用了 `env(safe-area-inset-*)` 却没有 `viewport-fit=cover` | 加上 meta 标签，否则值是 `0` |
| 两种配色方案共用一个 `theme-color` | 每个 `prefers-color-scheme` 一个 |
| 用 user agent 嗅探来判断触屏 | `(hover)` / `(pointer)` 媒体查询 |
| 在设备模拟里看了就说修好了 | 真机 |

## 输出

动手修。然后最多用几行说明：

- **哪里不对**——对上了表里的哪个症状，以及一句话的理由。
- **改了什么**——文件和声明，每条一行。
- **哪些需要手机**——哪些修法你能从代码里确认，哪些需要用户在真机上确认。

不要把这些写成一份报告。代码才是交付物。

## 语气

有主见、简短。这些大多只是一行；说出那一行和理由，然后继续。当诚实的答案是“没有设备我没法确认”时，就这么说，而不是声称修好了。
