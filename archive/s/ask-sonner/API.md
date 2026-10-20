# Sonner API 参考

> （本文件是 `ask-sonner` 的参考文件，翻译自 Emil Kowalski 的仓库 https://github.com/emilkowalski/skills 的 `skills/ask-sonner/API.md`，许可证 MIT，仅供自用。属性名、类型和默认值保持原样。）

准确的属性、类型和默认值。传给 `toast()` 的选项，会覆盖通过 Toaster 的 `toastOptions` 设置的同名选项。

## `<Toaster />`

| 属性 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `theme` | `string` | `'light'` | `'light'`、`'dark'` 或 `'system'`。 |
| `richColors` | `boolean` | `false` | 让出错和成功状态更有颜色。 |
| `expand` | `boolean` | `false` | 提示消息默认展开（否则鼠标悬停时才展开）。 |
| `visibleToasts` | `number` | `3` | 同时可见的提示消息数量。 |
| `id` | `string` | – | Toaster 的 id，供 `toast()` 的 `toasterId` 选项指定。 |
| `position` | `string` | `'bottom-right'` | `top-left`、`top-center`、`top-right`、`bottom-left`、`bottom-center`、`bottom-right`。 |
| `closeButton` | `boolean` | `false` | 给所有提示消息加一个关闭按钮。 |
| `offset` | `string \| number \| object` | `'32px'` | 离屏幕边缘的距离。对象写法可以按边设置：`{ bottom: '24px', right: '16px' }`。 |
| `mobileOffset` | `string \| number \| object` | `'16px'` | 屏幕宽度小于 600px 时离边缘的距离。 |
| `swipeDirections` | `array` | 根据位置决定 | 允许滑动关闭的方向。 |
| `dir` | `string` | `'ltr'` | 文字方向。 |
| `hotkey` | `string` | `⌥/alt + T` | 让焦点跳到提示消息区域的键盘快捷键。 |
| `invert` | `boolean` | `false` | 浅色模式下用深色提示消息，反之亦然。 |
| `toastOptions` | `object` | – | 应用到每条提示消息的默认选项（下面任何一个 `toast()` 选项都可以）。 |
| `gap` | `number` | `14` | 展开时提示消息之间的间距。 |
| `icons` | `object` | – | 替换默认图标：`{ success, info, warning, error, loading }`；设为 `null` 就去掉那一个。 |

## `toast()` 选项

`toast(message, options)`——message 可以是字符串、JSX，或返回 JSX 的函数。返回这条提示消息的 id。

| 选项 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `description` | `ReactNode` | – | 显示在标题下面；也可以是返回 JSX 的函数。 |
| `closeButton` | `boolean` | `false` | 加一个关闭按钮。 |
| `invert` | `boolean` | `false` | 浅色模式下用深色提示消息，反之亦然。 |
| `duration` | `number` | `4000` | 多少毫秒后自动关闭。`Infinity` 表示一直显示。 |
| `position` | `string` | `'bottom-right'` | 这条提示消息的位置。 |
| `dismissible` | `boolean` | `true` | 如果是 `false`，用户无法关闭这条提示消息。 |
| `icon` | `ReactNode` | – | 文字前面的图标；设为 `null` 去掉默认图标。 |
| `action` | `ReactNode \| { label, onClick }` | – | 主按钮；点击后关闭提示消息，除非 `onClick` 调用了 `event.preventDefault()`。 |
| `cancel` | `ReactNode \| { label, onClick }` | – | 次要按钮；点击后关闭提示消息。 |
| `actionButtonStyle` | `object` | `{}` | 主按钮的样式。 |
| `cancelButtonStyle` | `object` | `{}` | 取消按钮的样式。 |
| `id` | `string` | – | 自定义 id；用同一个 id 再调用 `toast()` 会更新已有的提示消息。 |
| `testId` | `string` | – | 渲染成 `data-testid`，用于端到端测试。 |
| `toasterId` | `string` | – | 要在哪个 Toaster 里显示这条提示消息。 |
| `style` | `object` | – | 提示消息的行内样式。 |
| `classNames` | `object` | – | 各部分的类名：`{ toast, title, description, actionButton, cancelButton, closeButton }`。除非用了 `unstyled`，否则需要 `!important`。 |
| `unstyled` | `boolean` | `false` | 去掉所有默认样式。 |
| `onDismiss` | `(toast) => void` | – | 点关闭按钮或滑走提示消息时触发。 |
| `onAutoClose` | `(toast) => void` | – | 提示消息在 `duration` 之后自动关闭时触发。 |
| `containerAriaLabel` | `string` | `'Notifications'` | 提示消息容器的 ARIA 标签（给读屏软件用）。 |

## 函数

| 函数 | 作用 |
| --- | --- |
| `toast(message, opts?)` | 显示一条提示消息；返回它的 id。 |
| `toast.success / .error / .info / .warning(message, opts?)` | 带对应图标的分类提示消息。 |
| `toast.loading(message, opts?)` | 带加载圈的提示消息；按 id 更新它。 |
| `toast.promise(promise, { loading, success, error })` | 随 promise 结束而变化的加载中提示消息；`success`/`error` 可以是字符串、JSX、接收结果的函数，或者提示消息选项对象。 |
| `toast.custom((t) => jsx, opts?)` | 无样式提示消息——你的 JSX，Sonner 的行为。 |
| `toast.dismiss(id?)` | 关闭一条提示消息；不传 id 就关闭全部。 |
| `toast.getActiveToasts()` | 所有当前显示的提示消息，React 外也能用。 |
| `useSonner()` | React hook，返回 `{ toasts }`。 |
