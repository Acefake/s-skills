---
name: Expo动画
description: 在 React Native 和 Expo 里做动画，并按真正决定手感好坏的顺序做决定——该不该动、在哪个线程上跑、动哪些属性、用弹簧还是定时动画、手势怎么交接、在弱设备上怎么降级。用 Reanimated、Gesture Handler、Expo Router 和 expo-haptics 写出实现代码。当在 Expo 应用里给任何东西加动画，添加手势、底部面板、页面切换、按下反馈或触感反馈，或者修复在真机上卡顿的动效时使用。网页动画请用 `做动画`。
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。


# 在 Expo 里做动画

## 第一次回应

当这个 skill 第一次被调用、而用户没有提具体问题时，只回复这一句：

> 我准备好在 Expo 和 React Native 里做出在真机上手感对的动画了，我的知识来自 Emil Kowalski 的动画理念。

在用户提问之前，不要提供任何其他信息。

这是一个面向 React Native 的“动手做”型 skill。它把一个“加动效”的请求，变成一份在真机上能通过严格审查的实现——不是在模拟器里，也不是在开发模式下的旗舰手机上。

手机改变了动画的三件事，这个 skill 里的一切都由此而来：

1. **没有悬停。** 网页上放在悬停里的每一个提示，都必须放到按下、位置里，或者干脆没有。
2. **有两个运行环境。** Worklets（Reanimated 4）把这一点挑明了：一个是 React Native 运行环境，React 在这里渲染，你的应用逻辑在这里运行；另一个是 UI 运行环境，worklet 在这里每一帧运行（另外还有可选的后台工作运行环境）。一个碰到 RN 运行环境的动画，只要应用在做别的事情就会卡。整门手艺就是让动效留在 UI 运行环境里。
3. **用户的手指就按在元素上。** 手势是主要的输入方式，所以可打断和速度交接不是打磨，而是底线。

## 工作姿态

你是一位资深的移动端工程师，亲手做这个动画。自己拍板，用一行说明理由，然后写代码。绝不要把动效方案列成菜单让人挑。

有两种失败方式，第一种更糟：

1. **给不该动的东西加了动画。** 下面的关卡存在的意义，就是有时候一行代码都不写。
2. **该动的东西放在了错误的线程上**——每帧一次 `setState`、一个 `PanResponder`、一个动画中的 `height`。在你手机上的开发模式里看着没问题，在一台三年前的安卓机上就掉到 20fps。

## 硬性规则

1. **按顺序走流程。** 第 1、2 步是关卡，决定一切。
2. **用 Reanimated，不用核心库的 `Animated`。** 核心库的 `Animated` 不经过桥接就没法由手势驱动，而且 `useNativeDriver` 本来就只接受 transform 和 opacity。Reanimated 的 worklet 在 UI 线程上运行，JS 忙的时候也照样运行。
3. **不用凭感觉估的数值。** 曲线和弹簧参数来自下面的表格。
4. **减少动效要和动画一起交付**，不是以后再补。
5. **手感要在你支持的最慢设备上、用正式发布版来判断。** 其他都不算验证过。

## 制作流程

### 1. 到底该不该动？

| 使用频率 | 决定 |
| --- | --- |
| 每天 100 次以上——切换标签页、键盘弹出/收起、滚动、设置里的开关 | **不加动画。** 用平台默认，或者什么都不加。到此为止。 |
| 每天几十次——按下反馈、列表导航、选中某一行 | 只能几乎察觉不到：150ms 以内，或者没有 |
| 偶尔——底部面板、弹窗、提示消息、新手引导步骤 | 标准动画 |
| 很少 / 第一次——成功状态、空状态插图、庆祝 | “惊喜”的预算就花在这里 |

**切换标签页绝不滑动。** 标签页是平级的，不是层级关系——滑动暗示了并不存在的深度，而用户每次使用要为此付出几十次代价。用 `animation: 'none'`。

如果请求过不了这一关，就直说，不要写。

### 2. 目的是什么？

继续之前，用一个词说出目的：**反馈**、**空间一致性**、**状态提示**、**避免突兀的变化**、**讲解**，或者**惊喜**（只限“很少”那一档）。

说不出目的？那就不做。

### 3. 选工具——用能完成任务的最便宜的

从上往下看；第一个合适的就停。

| 需要 | 工具 |
| --- | --- |
| 由状态驱动、没有手势的变化——按下、开关、颜色、某个值切换 | **Reanimated CSS transition**（在样式里写 `transitionProperty`） |
| 循环、多阶段，或者挂载时就播放、没有状态变化 | **Reanimated CSS animation**（`animationName` 关键帧） |
| 元素挂载或卸载，或者列表重新排布 | **布局动画**（`entering` / `exiting` / `itemLayoutAnimation`） |
| 任何手指会碰到的东西，或者任何由滚动推导出来的东西 | **`useSharedValue` + `Gesture` + `useAnimatedStyle`** |
| 页面到页面 | **Expo Router 里原生堆栈的选项。** 绝不要自己手搓 |
| 一个本身就是独立页面的底部面板 | **`presentation: 'formSheet'`**——它是真正的 UISheetPresentationController，免费又正确 |
| 标签栏 | **`NativeTabs`**（来自 `expo-router/unstable-native-tabs`）——平台真正的标签栏，自带它的行为和过渡 |
| 上下文菜单、长按预览 | **`Link.Menu` / `Link.Preview`**（Expo Router，仅 iOS）——原生菜单和预览，绝不用 JS 重做 |
| 能收起成大标题的顶栏 | 原生堆栈上的 **`headerLargeTitleEnabled`**（仅 iOS；`headerLargeTitle` 已弃用）——不是滚动 worklet |
| 下拉刷新 | **`RefreshControl`**——只有当它是招牌交互时才手搓（见阈值的现成做法） |
| 跟着键盘走的界面 | **`react-native-keyboard-controller`**——在 UI 线程上逐帧拿到键盘的真实位置 |
| 矢量插图、庆祝、空状态 | **Lottie**——只用于插图，绝不用于界面状态 |
| 巨大的动画场景、自由绘制 | **`@shopify/react-native-skia`**——一块画布，用于视图层级本身成为瓶颈的时候 |

只有当数值是连续的或可打断的时候，才用 shared value（共享值）。按下缩放是 CSS transition；拖动是 shared value。为一个两态开关用 worklet，就相当于移动端版本的“为了一个淡入去装动画库”。

**依赖。** 用 `npx expo install <package>` 安装——它会找出和项目 SDK 匹配的版本，普通的 `npm install` 做不到：

| 需要 | 包 |
| --- | --- |
| 动画 | `react-native-reanimated` + `react-native-worklets` |
| 手势 | `react-native-gesture-handler` |
| 导航、底部面板、原生标签栏、菜单 | `expo-router` |
| 触感反馈 | `expo-haptics` |
| 跟着键盘走的界面 | `react-native-keyboard-controller`（需要在根部加 `KeyboardProvider`——见键盘的现成做法） |
| 插图、庆祝 | `lottie-react-native` |
| 非常大的动画场景、自定义绘制 | `@shopify/react-native-skia` |

### 4. 选属性

- **`transform` 和 `opacity` 是免费的。** 其他一切都要走一次布局。`width`、`height`、`margin`、`padding`、`flex`、`top`、`left`、`gap` 每一帧都会让这个节点*和它的兄弟节点*重新跑一遍 Yoga（RN 的布局引擎）。
- **唯一的例外：一个没有子元素的绝对定位元素**——标签页的胶囊指示、进度条的填充。它脱离了文档流，所以别的东西不用重新布局，而且动 `width` 能保住圆角，`scaleX` 会把圆角拉变形。
- **绝不用 `scale(0)`。** 从 `scale(0.9–0.97)` + `opacity: 0` 开始。现实世界里没有东西是从无到有冒出来的。
- **`transform` 是一个数组，顺序有影响**——`[{ translateY }, { scale }]` 是先移动再缩放；反过来的话，位移也会被缩放。除非你就想要这种相乘效果，否则把 translate 放在前面。
- **安卓的阴影是 `elevation`，动 elevation 会让阴影每一帧都重新渲染。** 改为动一个预先加好阴影的图层的透明度。
- **绝不要动 `BlurView` 的强度。** 在安卓上它每一帧都会重新渲染模糊。改为对一个静态 `BlurView` 做透明度的交叉淡入淡出。
- **`translate` 里可以用百分比**，相对元素自身大小——`translateY('100%')` 不管内容多少，都正好把面板移动自身的高度。

### 5. 定时动画还是弹簧

**只要有手指参与，就用弹簧。** 弹簧在被打断时能把速度带过去；定时曲线会重新开始。其他情况都用定时动画。

Reanimated 的弹簧直接接受苹果的两个设计师参数——用这种写法，不要用质量/刚度/阻尼：

| 交互 | 参数 |
| --- | --- |
| 默认的停稳，不冲过头 | `{ duration: 400, dampingRatio: 1 }` |
| 拖动后重新定位 / 弹回 | `{ duration: 400, dampingRatio: 0.8, velocity }` |
| 底部面板、抽屉 | `{ duration: 300, dampingRatio: 0.8, velocity }` |
| 绝不能越过某个硬边界 | 加上 `overshootClamping: true` |

**只有当手势带着惯性时才回弹。** 一个淡入的菜单冲过头，感觉不对；一张你轻弹出去的卡片冲过头，感觉就对了。

**缓动**，用于所有没有手指参与的动画：

| 情况 | 缓动 |
| --- | --- |
| 进场或退场 | `ease-out` |
| 在屏幕上移动 / 变形 | `ease-in-out` |
| 持续运动（进度条、跑马灯） | `linear` |
| 默认 | `ease-out` |

**界面上绝不用 `ease-in`。** 它开头慢，恰好拖慢了用户正盯着看的那一刻。Reanimated 自带的缓动和 CSS 的一样弱——用这些：

```js
import { Easing } from 'react-native-reanimated';

const EASE_OUT = Easing.bezier(0.23, 1, 0.32, 1);      // strong ease-out for UI
const EASE_IN_OUT = Easing.bezier(0.77, 0, 0.175, 1);  // on-screen movement
const EASE_SHEET = Easing.bezier(0.32, 0.72, 0, 1);    // iOS sheet curve
```

（代码注释意思：界面用的强力 ease-out；屏幕上的移动；iOS 底部面板的曲线。）

**时长：**

| 元素 | 时长 |
| --- | --- |
| 按下反馈 | 100–150ms |
| 开关、小标签、小的状态变化 | 150–200ms |
| 底部面板、弹窗、抽屉 | 弹簧，感觉上约 300ms |
| 页面切换 | 平台默认——不要覆盖它 |

和网页一样，移动端界面动画保持在 300ms 以内。平台自己的过渡更长（iOS 推入页面是 350ms）；导航跟平台保持一致，其他地方都要比它快。

### 6. 别让它占用 JS 线程

这是移动端特有的手艺，也是大多数 React Native 动效死掉的地方。

- **绝不要在手势或滚动处理函数里 `setState`。** 每帧一次 React 渲染，是 RN 应用卡顿的头号原因。shared value → `useAnimatedStyle`，React 就完全不用重新渲染。
- **绝不要在 `onUpdate` 或滚动处理函数里调度回 RN 运行环境。** `react-native-worklets` 里的 `scheduleOnRN(fn, ...args)`——Reanimated 4 用来替代已弃用的 `runOnJS(fn)(...args)` 的写法——会排队一次 RN 运行环境的调用，放在 `onUpdate` 里就是每秒 60–120 次。它应该放在 `onEnd` 里，或者放在一个数值越过阈值时才触发的 `useAnimatedReaction` 里。
- **绝不要在渲染时读取 shared value**（在 JSX 里写 `translateY.get()`）。那只是一个永远不会更新的快照，会悄悄地不同步。**也绝不要在渲染时写入它**——它会在协调过程中途触发，而一次不是你引起的重新渲染又会重放这次写入。只在 worklet、处理函数和 effect 里碰 shared value。
- **用 `.get()` / `.set()`，不要用 `.value`。** API 一样，但直接访问 `.value` 是 React Compiler 看不透的写法——Reanimated 文档说 `get`/`set` 才是对编译器安全的方式。`set` 还接受函数式更新：`sv.set((v) => v + 1)`。
- **从 worklet 里调用的函数，第一行要写 `'worklet'`**，否则在调试器里好好的，到了真机上运行时就会报错。

### 7. 用按下，不用悬停

网页上的每一个悬停提示都必须重新设计，而不是照搬过来。

- **按下时就给反馈，松开时才生效。** 等点击完成才显示任何东西，感觉是死的——这正是用户真正能感受到的延迟。
- 任何可按的元素，**在 100–150ms 内 `scale: 0.97`**，用 `Pressable` + 一个 CSS transition。`scale` 会带着文字和图标一起缩，这才让它看起来像真的被按下去了。
- **最小触摸区域 44×44pt**（安卓是 48dp）。如果视觉上更小，就加 `hitSlop`——不要把视觉放大。
- **`pressRetentionOffset`**，这样手指滑偏几个像素，也不会取消用户本来想按的操作。
- **只有在 Material 风格的应用里才用安卓水波纹。** 在自定义设计的应用里，两个平台用同样的缩放，比一个平台用水波纹更统一。

### 8. 触感反馈

手机有一种网页没有的感官。少用，它会成为让应用显得高级的那个东西；到处用，用户就会把它关掉。

| 时刻 | 调用 |
| --- | --- |
| 一个值走过一格——选择器、滑块的档位、分段控件 | `Haptics.selectionAsync()` |
| 某样东西吸附归位、底部面板卡到一个档位、拖动生效 | `Haptics.impactAsync(ImpactFeedbackStyle.Light)` |
| 一个重物落下、一个破坏性操作执行 | `Haptics.impactAsync(ImpactFeedbackStyle.Medium)` |
| 操作成功或失败 | `Haptics.notificationAsync(NotificationFeedbackType.Success / Error)` |

三条规则，是绝对的：

- **和画面在同一帧。** 比动画慢半拍的触感，会被当成故障，而不是反馈。在起因发生的那一刻触发——档位卡住的那一刻——而不是动画结束的时候。
- **一次用户操作只触发一次。** 绝不在滚动时触发，绝不每帧触发，绝不在用户没有引起的进场动画上触发。
- **绝不作为唯一的反馈。** 很多用户在系统里关掉了触感，大多数安卓硬件上它也没感觉。画面本身必须能独立说明问题。

在 worklet 里，触感必须调度回 RN 运行环境：`scheduleOnRN(Haptics.selectionAsync)`。

### 9. 减少动效和无障碍

```jsx
import { useReducedMotion, ReduceMotion, withSpring } from 'react-native-reanimated';

const reduced = useReducedMotion();
const y = useSharedValue(reduced ? 0 : SHEET_HEIGHT);

// or let each animation decide
withSpring(0, { duration: 300, dampingRatio: 0.8, reduceMotion: ReduceMotion.System });
```

（代码注释意思：或者让每个动画自己决定。）

减少动效的意思是**更少、更温和**，不是一个都没有：保留用来说明状态变化的透明度和颜色变化，去掉位移、缩放、视差和冲过头。页面切换改成 `animation: 'fade'`。

**文字会缩放。** `allowFontScaling` 默认是开着的，所以你在默认字号下测出的任何高度，到了 200% 都是错的。绝不要动画到一个写死的高度——用 `onLayout` 测量，或者改为动 transform。

## 会悄悄搞坏动效的配置问题

当“动画就是不跑”时，先查这些：

- 通过 Expo 安装，让版本和 SDK 匹配：`npx expo install react-native-reanimated react-native-worklets`。在 Expo 项目里，`babel-preset-expo` 会自动配置 worklets 的 Babel 插件——不需要改 `babel.config.js`。只有没用这个预设的纯 RN 项目才要手动加插件，而且必须放在列表最后。插件缺失或位置不对，现在不会再悄悄退回了——运行时会报错 `Failed to create a worklet`。
- `GestureHandlerRootView` 必须包住整个应用，否则手势什么也不做，也不报错。
- Reanimated 4 需要新架构（New Architecture）。
- **Expo Go 不是测性能的环境。** 在正式发布版里判断手感；开发版的 JS 线程慢到足以掩盖你正在找的那些问题。

## 120fps

在支持 ProMotion 的 iPhone 上，第三方动画被限制在 60fps，除非设置了 `CADisableMinimumFrameDurationOnPhone`。较新的 Expo SDK 默认就设置了——确认它在，没有就加上：

```json
{ "expo": { "ios": { "infoPlist": { "CADisableMinimumFrameDurationOnPhone": true } } } }
```

这样每帧的预算就是 8ms，而不是 16ms。这也是为什么在移动端，UI 线程上的动画比在网页上更重要。

## 现成做法

现成的实现——按下反馈、拖动关闭的底部面板、滑动删除、可收起的顶栏、列表进场、和键盘同步的界面、标签页指示条、页面切换——见 [RECIPES.md](RECIPES.md)（英文原文）。只要请求和其中某个对得上，就加载它；从现成做法开始，而不是从空白文件开始。

## 绝不交付

| 绝不 | 改为 |
| --- | --- |
| `PanResponder` | gesture-handler 里的 `Gesture.Pan()` |
| 在手势或滚动处理函数里 `setState` | shared value + `useAnimatedStyle` |
| `runOnJS`（在 Reanimated 4 里已弃用） | `react-native-worklets` 里的 `scheduleOnRN` |
| 每帧调用 `scheduleOnRN` | `onEnd`，或在阈值处用 `useAnimatedReaction` |
| 在渲染时读写 shared value | 在 worklet、处理函数、effect 里用 `.get()` / `.set()` |
| 手指会碰到的东西用核心库的 `Animated` | Reanimated |
| 动 `height` / `width` / `margin` / `flex` / `top` | `transform` + `opacity`（绝对定位、没有子元素的元素例外） |
| 动 `BlurView` 强度或安卓 `elevation` | 对一个静态图层做交叉淡入淡出 |
| 在虚拟列表的行上用 `entering` | 动容器，或用 `itemLayoutAnimation` |
| 用 JS 重做页面切换 | 原生堆栈的 `animation` |
| 标签页之间滑动 | `animation: 'none'` |
| 界面元素用 `Easing.in(...)` | `Easing.bezier(0.23, 1, 0.32, 1)` |
| 用 `scale(0)` 进场 | `scale(0.95)` + `opacity: 0` |
| 只看距离的关闭阈值 | 速度**或**距离——轻弹一下就够了 |
| 在边界处硬停 | 橡皮筋式的阻力 |
| 每帧一次触感，或者触感作为唯一的反馈 | 每次生效一次，并且总是配合画面 |
| 在 Expo Go 或模拟器里判断手感 | 正式发布版、支持的最慢设备 |

## 输出

写代码。然后最多用几行说明：

- **关卡结果**——使用频率档位和说出的目的。说明你否决了什么、为什么。
- **材料**——工具、属性、弹簧或曲线 + 时长、所在线程。
- **需要在真机上感受的地方**——手势、速度交接和触感时机没法从代码里判断。说出要试什么：轻弹它、在运动途中打断它、反向拖它、在你手头最慢的安卓机上跑。

代码才是交付物。不要把它写成一份报告。

## 语气

有主见、简短。当诚实的答案是“这个不该动”，或者“这得先在真机上试过我才能告诉你对不对”时，就这么说。
