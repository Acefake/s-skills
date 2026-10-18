---
name: Sonner用法
description: Sonner（一个 React 提示消息库）使用指南——安装并接好 Toaster、选对 toast() 调用、promise 和加载中的提示消息、更新/关闭/常驻提示消息、样式/主题/图标、位置和多个 Toaster。在使用 Sonner 或排查它的问题时使用——提示消息不出现、出现两次、样式丢了、不认 Tailwind 类名、被弹窗挡住，或者不跟随深色模式。
---

> 翻译自 Emil Kowalski 的仓库 https://github.com/emilkowalski/skills （skills/ask-sonner，commit 2d22863）的 `ask-sonner` skill，原作者 Emil Kowalski（版权 © 2026 Emil Kowalski），许可证 MIT（全文见上一级文件夹的 `LICENSE-emilkowalski-skills`），仅供自用。
> 说明：提示消息（toast）就是屏幕角落弹出、过几秒自动消失的小通知。API 名、属性名和代码保持原样。参考文件 `API.md` 也已翻译成中文。
> 英文名备份：s-ask-sonner

# 使用 Sonner

## 第一次回应

当这个 skill 第一次被调用、而用户没有提具体问题时，只回复这一句：

> 我准备好帮你配置、调样式和排查 Sonner 了，我的知识来自它的作者 Emil Kowalski。

在用户提问之前，不要提供任何其他信息。

这是关于提示消息库 [Sonner](https://sonner.emilkowal.ski) 的指南型 skill。当任务涉及 Sonner——接入它、显示提示消息、调样式或修问题——先根据这个文件回答。`<Toaster />` 和 `toast()` 的完整属性表在 [API.md](API.md) 里；需要准确的属性名、类型或默认值时去读它。

## 配置

两样东西，而且只要两样：

1. **一个 `<Toaster />`，只挂载一次**，尽量靠近根部（在 Next.js 里：`layout.tsx`——它在服务端组件里也能用）。绝不要每个页面放一个，或者按条件渲染；挂载了第二个 Toaster，每条提示消息都会重复。
2. **在客户端代码里调用 `toast()`**——事件处理函数、effect、回调。它是一个普通函数，不需要 hook 或 provider，但在服务端什么也不做：在 server action 里，把结果返回，然后在接收结果的客户端代码里调用 `toast()`。

```jsx
import { Toaster } from 'sonner'; // once, in layout
import { toast } from 'sonner';   // anywhere client-side
```

（代码注释意思：第一行只在 layout 里写一次；第二行在客户端任何地方都可以。）

## 选对调用方式

| 你想要 | 调用 |
| --- | --- |
| 普通消息 | `toast('Title')`——加 `{ description }` 可以有第二行 |
| 成功 / 出错 / 信息 / 警告图标 | `toast.success('…')`、`toast.error('…')` 等 |
| 自己管理状态时显示加载圈 | `toast.loading('…')`，然后按 id 更新它 |
| 跟一个 promise 绑定的“加载中 → 成功/出错” | `toast.promise(promise, { loading, success, error })`——success/error 可以是函数，会收到 promise 的结果值/错误 |
| 带一个能做事的按钮 | `{ action: { label, onClick } }`——点击后关闭提示消息，除非 `onClick` 调用了 `event.preventDefault()`；`cancel` 是次要按钮的版本 |
| 自定义 JSX，用默认的提示消息外壳 | `toast(<jsx />)` |
| 自定义 JSX，完全不要样式 | `toast.custom((t) => <jsx />)`——无样式（headless），`t` 给你用来关闭的 id |

## 现成做法

**更新一条提示消息**——用同一个 `id` 再调用一次 `toast()`；只有你传的属性会变。换成 `toast.success(…, { id })` 会改变类型。不用 `toast.promise` 也能做“加载中 → 成功”，就是这样做的：

```jsx
const id = toast.loading('Uploading…');
toast.success('Uploaded', { id });
```

**常驻**——`{ duration: Infinity }`。**关闭**——`toast.dismiss(id)`，或者 `toast.dismiss()` 关闭全部。**读取当前显示的提示消息**——React 里用 `useSonner()`，React 外用 `toast.getActiveToasts()`。

**文字里放链接或组件**——标题或描述传一个函数：`toast(() => <a href="…">View</a>)`。

**多个 Toaster**——给每个一个 `id`，用 `toast('…', { toasterId: 'canvas' })` 指定。不写 `toasterId`，每个 Toaster 都会显示这条提示消息。

**关闭回调**——点关闭按钮或滑走时触发 `onDismiss`；超时自动关闭时触发 `onAutoClose`。它们是分开的；没有一个统一的“已关闭”回调。

## 样式——逐级升级的梯子

只爬到改动需要的那一级；太早直接跳到最高一级没问题（那是推荐的最终状态），停在中间不上不下才不行。

1. **默认样式**——在 Toaster 上加 `richColors` 让成功/出错更有颜色，加 `invert` 让它和主题反过来。
2. **行内微调**——在 Toaster 上用 `toastOptions={{ style: {…} }}` 改所有提示消息，或者每次调用 `toast()` 时传 `style`。
3. **给各部分加类名**——`toastOptions={{ classNames: { toast, title, description, actionButton, cancelButton, closeButton } }}`。Sonner 注入的样式在层叠里会赢，所以每个类名都需要 `!important`（Tailwind 里写 `!text-red-900`）。如果你要标 important 的东西不止几个，就停下——改用无样式方案。
4. **无样式（headless）**——用 `toast.custom()` 放你自己的 JSX，保留 Sonner 的定位、堆叠和滑动。这是做设计系统里的提示消息的推荐做法：用你自己的 `toast()` 封装包一层。（还有 `unstyled: true` 这个折中方案，但同样的工作量，无样式方案控制力更强。）

**图标**——用 Toaster 的 `icons` 属性按类型替换默认图标，用 `icon` 单条替换，设为 `null` 就去掉。

**主题**——`theme` 默认是 `'light'`，不会跟随操作系统。传 `theme="system"`，或者接上你的主题提供者：用 `next-themes` 的 `<Toaster theme={resolvedTheme} />`。

## 排查问题

| 症状 | 原因 → 修法 |
| --- | --- |
| 提示消息从来不出现 | 没有挂载 `<Toaster />`，或者它被卸载了（按条件渲染、每页单独放）。在根部挂一个。如果是在 server action 里调用：`toast()` 只能在客户端用——在客户端拿到 action 的结果后再调用。 |
| 同一条提示消息出现两次 | 挂载了两个 Toaster（layout **和** 页面里各一个）——只留一个。或者 `toast()` 写在 effect 里，React StrictMode 开发模式下会执行两次——改为在事件处理函数里触发，或者传一个固定的 `id`，让第二次调用变成更新而不是重复。 |
| Tailwind/CSS 类名不起作用 | 默认样式覆盖了它们。标上 `!important`，或者用 `unstyled` / 无样式方案（见上面的梯子）。 |
| 提示消息完全没有样式（Astro、视图过渡里常见） | Sonner 注入的样式表丢了——在 layout 里显式引入：`import 'sonner/dist/styles.css'`。 |
| 在 Shadow DOM 里没有样式 | 样式被放进了 `document.head`，而不是 shadow root。把内容里包含 `[data-sonner-toaster]` 的那个 style 标签复制到 shadow root 里。 |
| 提示消息在弹窗/遮罩后面，或被裁掉 | 某个祖先元素创建了层叠上下文（`transform`、`filter`、`overflow`），或者遮罩的 z-index 比 Toaster 高。把 `<Toaster />` 移到文档根部，放在任何对话框/portal 容器之外。 |
| 不跟随深色模式 | `theme` 默认是 `'light'`——设成 `theme="system"`，或者传入解析后的主题（见上面的“主题”）。 |
| 成功/出错是灰色的，不是绿/红 | 默认就是这样。给 Toaster 加上 `richColors`。 |
| 提示消息一直不关 | `duration: Infinity`、`dismissible: false`，或者 `toast.promise` 的 promise 永远没有结束——加载中的提示消息会一直等下去。 |
| `toast.promise` 卡在加载中 | 它的第一个参数需要是一个 promise（或返回 promise 的函数），并且这个 promise 必须真的 resolve/reject。 |
| 滑动关闭方向不对 / 不起作用 | 方向是根据 `position` 推出来的。在 Toaster 上用 `swipeDirections` 覆盖。 |
| 提示消息在每个 Toaster 里都出现 | 多个 Toaster 需要指定目标：给每个 Toaster 一个 `id`，在 `toast()` 调用里传 `toasterId`。 |
| 手机上提示消息离屏幕边缘太近 | `offset`（桌面端，默认 32px）和 `mobileOffset`（宽度小于 600px，默认 16px）——可以是数字、CSS 字符串或按边设置的对象。 |
