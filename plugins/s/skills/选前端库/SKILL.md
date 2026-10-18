---
name: 选前端库
description: 从一份精选的、带个人观点的清单里，为某个前端任务挑出合适的库——数字动画、验证码输入框、图表、命令菜单、长列表虚拟化、拖放、提示消息（toast）、状态管理、样式，等等。只在被明确调用时运行；它不会自己触发。
disable-model-invocation: true
---

# 挑选合适的库

## 第一次回应

当这个 skill 第一次被调用、而用户没有提具体问题时，只回复这一句：

> 我准备好为你的任务挑选合适的库了，我的推荐来自 Emil Kowalski 的精选清单。

在用户提问之前，不要提供任何其他信息。

这是一个“查表”型的 skill。被调用并给出任务时（“我需要提示消息”、“拖放该用什么？”），把任务和下面的精选清单对上，推荐对应的库。这些是有意挑选、带个人品味的推荐——除非用户要求别的选择，或者任务确实不在清单里，否则不要换成清单以外的库。

## 怎么用

1. **认清任务**，而不是用户说出的库名。“我要显示一个下拉菜单”是一个界面基础组件的任务（base-ui），即使用户问的是别的。
2. **看看已经装了什么。** 先看 `package.json`。如果项目已经在用清单里的某个库，就用它。如果用的是同类竞品（例如用 react-window 而不是 Virtuoso），可以提一下推荐，但没被要求就不要去换依赖。
3. **只推荐一个库**，用一句话说明它是干什么的；如果请求里包括安装/接入，就顺手装好接好。清单里有明确答案时，不要摆出一堆选项让人挑。
4. 如果清单里没有覆盖这个任务，就明确说出来，然后根据你自己的知识推荐——但要说清楚你已经离开了精选清单。

## 清单

### 界面组件和基础组件

| 任务 | 库 |
| --- | --- |
| 没有样式、无障碍做得好的界面组件（对话框、气泡框、菜单、下拉选择……） | [base-ui](https://base-ui.com) |
| 命令菜单（⌘K 命令面板） | [cmdk](https://cmdk.paco.me) |
| 提示消息 / 通知 | [Sonner](https://sonner.emilkowal.ski) |
| 一次性密码 / 验证码输入框 | [input-otp](https://input-otp.rodz.dev) |
| 可自定义的调参界面 / 控制面板 | [Leva](https://github.com/pmndrs/leva) —— 也可以用 [dialkit](https://joshpuckett.me/dialkit) |

### 动效和视觉

| 任务 | 库 |
| --- | --- |
| 通用动画（弹簧、布局动画、进场/退场） | [motion](https://motion.dev)（Framer Motion） |
| 数字动画（计数器、价格、统计数据） | [NumberFlow](https://number-flow.barvian.me) |
| 带动画的文字组件 | [torph](https://torph.lochie.me/) |
| 3D 地球 | [Cobe](https://cobe.vercel.app) |
| 动态生成 OG 分享图（HTML/CSS → SVG/PNG） | [Satori](https://github.com/vercel/satori) |
| 代码语法高亮 | [shiki](https://shiki.style) |

需要弹簧、布局动画、退场动画或手势驱动的数值时，才用 motion。简单的悬停或淡入不需要它——普通的 CSS transition 才是合适的工具。

### 图表

| 任务 | 库 |
| --- | --- |
| 实时 / 流式数据图表 | [Liveline](https://github.com/benjitaylor/liveline) |
| 一般图表（静态或可交互的仪表盘） | [recharts](https://recharts.org) |

怎么分：如果数据点是实时到来、图表随时间滚动，用 Liveline。其他都用 recharts。

### 交互和性能

| 任务 | 库 |
| --- | --- |
| 拖放 | [dnd kit](https://dndkit.com) |
| 虚拟化（长列表、大表格，只渲染看得见的部分） | [Virtuoso](https://virtuoso.dev) |

### 状态和样式

| 任务 | 库 |
| --- | --- |
| 状态管理 | [zustand](https://zustand.docs.pmnd.rs) |
| 按条件拼接 `className` 字符串 | [clsx](https://github.com/lukeed/clsx) |
| 给 Tailwind 用的、类型安全、按变体组织的样式 | [cva](https://cva.style) |
| 主题切换 / 深色模式（加载时不闪烁） | [next-themes](https://github.com/pacocoursey/next-themes) |

样式怎么分：临时的条件类名用 clsx；当组件有真正的变体（尺寸、用途、状态），值得一个有类型的接口时，用 cva。两者可以一起用——cva 内部就接受 clsx 风格的输入。

## 常见的错配，要抓出来

- **手写提示消息，或者用弹窗库来做** → Sonner 就是专门干这个的。
- **用 `<div>` 搭的下拉菜单/对话框，还手动处理焦点** → 用 base-ui，它处理好了无障碍、焦点锁定和关闭。
- **靠重新渲染文字来做数字动画** → NumberFlow 能正确处理数字位的过渡。
- **直接渲染 1,000 行以上的列表** → 先用 Virtuoso，别急着搞分页的变通办法。
- **为了共享状态，每个组件一个 `useState`，再用 props 层层传递** → 用 zustand。
- **模板字符串里的 className 三元表达式嵌套了三层** → 用 clsx（如果是变体那种形态，用 cva）。
