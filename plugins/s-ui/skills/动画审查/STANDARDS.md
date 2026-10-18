# 动画标准参考

审查背后的准确数值、曲线和规则。在发现里引用这些，而不是估个大概。提炼自 Emil Kowalski 的设计工程理念。

## 该不该动？（频率表）

| 频率 | 决定 |
| --- | --- |
| 每天 100 次以上（键盘快捷键、命令面板开关） | 不加动画。永远不加。 |
| 每天几十次（悬停效果、列表导航） | 去掉或大幅减弱 |
| 偶尔（弹窗、抽屉、提示消息） | 标准动画 |
| 很少 / 第一次（新手引导、反馈、庆祝） | 可以加点惊喜 |

**绝不给键盘触发的操作加动画**——它们每天重复几百次；动画会让它们显得慢、脱节。（Raycast 打开/关闭没有动画——对一天用几百次的东西来说，这是对的。）

动效的合理目的：空间一致性、状态提示、讲解、反馈、避免突兀的变化。对于经常看到的元素，“看着很酷”不成立。

## 缓动

决定顺序：
- 进场或退场 → **`ease-out`**（开头快，感觉灵敏）
- 在屏幕上移动 / 变形 → **`ease-in-out`**
- 悬停 / 颜色变化 → **`ease`**
- 持续运动（跑马灯、进度条） → **`linear`**
- 默认 → **`ease-out`**

**界面上绝不用 `ease-in`。** 它开头慢，恰好拖慢了用户正盯着看的那一刻。200ms 的 `ease-out` *感觉*比 200ms 的 `ease-in` 快。

CSS 自带的缓动太弱。用强力的自定义曲线：

```css
--ease-out: cubic-bezier(0.23, 1, 0.32, 1);        /* strong ease-out for UI */
--ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);    /* strong ease-in-out for on-screen movement */
--ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);     /* iOS-like drawer curve (Ionic) */
```

（代码注释意思：界面用的强力 ease-out；屏幕上移动用的强力 ease-in-out；类似 iOS 的抽屉曲线（来自 Ionic）。）

在 [easing.dev](https://easing.dev/) 或 [easings.co](https://easings.co/) 找曲线——不要从头手调。

## 时长

| 元素 | 时长 |
| --- | --- |
| 按钮按下的反馈 | 100–160ms |
| 提示框、小气泡框 | 125–200ms |
| 下拉菜单、下拉选择 | 150–250ms |
| 弹窗、抽屉 | 200–500ms |
| 营销 / 讲解类 | 可以更长 |

**规则：界面动画保持在 300ms 以内。** 180ms 的下拉菜单比 400ms 的感觉更灵敏。转得更快的加载圈会让加载感觉更快（实际时间一样）。第一个之后的提示框立即出现（跳过延迟和动画），会让工具栏感觉更快。

## 物理感

- **绝不用 `scale(0)`。** 从 `scale(0.9–0.97)` + `opacity: 0` 开始。现实世界里没有东西是从无到有冒出来的。
- **感知原点的气泡框。** 从触发元素缩放出来，而不是从中心：
  ```css
  .popover { transform-origin: var(--transform-origin); } /* Base UI */
  ```
  **弹窗例外**——它们出现在视口中央，保持 `transform-origin: center`。
- **按钮按下反馈。** `:active` 上 `transform: scale(0.97)`，`transition: transform 160ms ease-out`。轻微（0.95–0.98）。适用于任何可按的元素。

## 弹簧

因为模拟物理，所以感觉自然；没有固定时长——它们根据参数自然停稳。用于：带惯性的拖动、“有生命感”的元素（灵动岛）、可打断的手势、装饰性的跟随鼠标。

```js
// Apple-style (easier to reason about) — recommended
{ type: "spring", duration: 0.5, bounce: 0.2 }

// Traditional physics (more control)
{ type: "spring", mass: 1, stiffness: 100, damping: 10 }
```

（代码注释意思：苹果风格（更容易理解）——推荐；传统物理参数（控制更多）。）

回弹保持轻微（0.1–0.3）；大多数界面里不要回弹——只留给拖动关闭和好玩的交互。弹簧被打断时能保持速度（关键帧会从零重新开始），所以非常适合用户可能在运动途中反向的手势。

鼠标交互：用 `useSpring` 做插值，而不是把数值直接绑定到鼠标位置（直接绑定 = 生硬、没有惯性）。只在动效是装饰性的时候这么做。

## 可打断性

CSS **transition** 可以在动画途中被打断并重新定目标；**关键帧**会从零重新开始。对于任何被快速触发的东西（不断添加的提示消息、开关），transition 更流畅。

```css
/* Interruptible — good for dynamic UI */
.toast { transition: transform 400ms ease; }

/* Not interruptible — avoid for dynamic UI */
@keyframes slideIn { from { transform: translateY(100%); } to { transform: translateY(0); } }
```

（代码注释意思：第一种可打断——适合动态界面；第二种不可打断——动态界面避免使用。）

不用 JS 做进场，用 `@starting-style`：

```css
.toast {
  opacity: 1; transform: translateY(0);
  transition: opacity 400ms ease, transform 400ms ease;
  @starting-style { opacity: 0; transform: translateY(100%); }
}
```

老办法：`useEffect(() => setMounted(true), [])` + `data-mounted` 属性。

## 不对称的时间

用户做决定的地方慢，系统响应的地方快。

```css
.overlay { transition: clip-path 200ms ease-out; }            /* release: fast */
.button:active .overlay { transition: clip-path 2s linear; }  /* press: slow, deliberate */
```

（代码注释意思：松手——快；按住——慢、刻意。）

## 性能

- **只动 `transform` 和 `opacity`**——它们跳过布局/绘制，在 GPU 上运行。`padding`/`margin`/`height`/`width`/`top`/`left` 会触发全部三个渲染步骤。
- **不要用父元素上的 CSS 变量去驱动子元素的 transform**——那会让所有子元素重新计算样式。直接在元素上设置 `transform`。
  ```js
  element.style.setProperty('--swipe-amount', `${d}px`); // bad: recalc on all children
  element.style.transform = `translateY(${d}px)`;        // good: only this element
  ```
  （代码注释意思：第一种不好——所有子元素重算；第二种好——只影响这个元素。）
- **Framer Motion 的简写不走硬件加速。** `x`/`y`/`scale` 通过 rAF 在主线程上运行，高负载下会掉帧。用完整的 transform 字符串：
  ```jsx
  <motion.div animate={{ x: 100 }} />                          // drops frames under load
  <motion.div animate={{ transform: "translateX(100px)" }} />  // hardware accelerated
  ```
  （代码注释意思：第一行高负载下掉帧；第二行硬件加速。）
- **高负载下 CSS 动画比 JS 好**——它们不在主线程上运行；基于 rAF 的动画在浏览器加载/执行脚本/绘制时会卡。预先定好的运动用 CSS，动态的/可打断的用 JS。
- **WAAPI** 给你 JS 的控制力和 CSS 的性能（硬件加速、可打断、不用库）：
  ```js
  element.animate([{ clipPath: 'inset(0 0 100% 0)' }, { clipPath: 'inset(0 0 0 0)' }],
    { duration: 1000, fill: 'forwards', easing: 'cubic-bezier(0.77, 0, 0.175, 1)' });
  ```

## 变换和 clip-path

- **`translate` 的百分比**相对元素自身大小——`translateY(100%)` 不管尺寸多少，都正好移动元素自身的高度（Sonner/Vaul 就是这样给提示消息/抽屉定位的）。优先用它，而不是写死的 px。
- **`scale()` 也会缩放子元素**（字体、图标、内容）——对按下反馈来说这是好事。
- **3D**：`rotateX/Y` + `transform-style: preserve-3d`，不用 JS 就能做出纵深/环绕/翻转。
- **`clip-path: inset(t r b l)`** 是一个强大的动画工具：每个值从对应的那一边往里裁。用途：滚动时揭开（`inset(0 0 100% 0)` → `inset(0 0 0 0)`）、长按删除的覆盖层、无缝的标签页颜色过渡（复制一份 + 裁剪选中的副本）、对比滑块。

## 手势和拖动

- **按惯性关闭**：不要要求越过某个距离阈值——计算速度（`Math.abs(distance)/elapsedMs`）；如果 `> ~0.11` 就关闭。轻弹一下就应该够了。
- **边界处的阻尼**：拖过自然边缘时，拖得越远动得越少（真实的东西在停下之前会先变慢）。
- **拖动一开始就捕获指针**，这样指针离开范围时拖动还能继续。
- **防多点触控**：拖动开始后忽略额外的触点（`if (isDragging) return`）——防止跳动。
- **用摩擦代替硬停**——允许拖过头，但阻力越来越大，而不是一堵看不见的墙。

## 遮掩不完美的交叉淡入淡出

如果调了缓动/时长之后，交叉淡入淡出还是能看到两个重叠的状态，就在过渡期间加一点轻微的 `filter: blur(2px)`，把它们融合成一次被感知为整体的变化。模糊保持在 20px 以内（重度模糊很耗性能，在 Safari 上尤其如此）。

## 错开

一组元素进场时错开；每个之间 30–80ms。更长的延迟会显得慢。错开只是装饰——播放时绝不能挡住交互。

```css
.item { opacity: 0; transform: translateY(8px); animation: fadeIn 300ms ease-out forwards; }
.item:nth-child(2) { animation-delay: 50ms; }
.item:nth-child(3) { animation-delay: 100ms; }
@keyframes fadeIn { to { opacity: 1; transform: translateY(0); } }
```

## 无障碍

```css
@media (prefers-reduced-motion: reduce) {
  .element { animation: fade 0.2s ease; } /* keep opacity/color, drop transform-based motion */
}
@media (hover: hover) and (pointer: fine) {
  .element:hover { transform: scale(1.05); } /* gate hover motion — touch fires false hovers on tap */
}
```

（代码注释意思：保留透明度/颜色，去掉基于 transform 的运动；给悬停动效加判断——触屏点按时会触发假的悬停。）

```jsx
const reduce = useReducedMotion();
const closedX = reduce ? 0 : '-100%';
```

减少动效的意思是动画更少、更温和，不是一个都没有——保留有助于理解的过渡，去掉移动/位置变化。

## 调试（手感拿不准时在审查里建议）

- **慢动作**：把时长调大 2–5 倍，或者用开发者工具的动画检查器。检查颜色交叉淡入淡出是否干净、缓动有没有突然停住、`transform-origin` 对不对、协同的属性是否保持同步。
- **逐帧**：Chrome 开发者工具的 Animations 面板能看出协同属性之间的时间偏差。
- **手势用真机**（抽屉、滑动）——连上手机，用 IP 访问开发服务器，用 Safari 远程开发者工具。
- **第二天用新鲜的眼光看**——开发时看不见的瑕疵，过后会冒出来。

## 一致性

动效要和组件的性格相符：活泼的可以更弹；专业的仪表盘应该干练、快速。Sonner 感觉对，部分原因是缓动、时长、设计甚至名字都很协调——稍微慢一点，用 `ease` 而不是 `ease-out`，显得优雅。进场/退场列表里透明度 + 高度的配合靠反复试，没有公式——调到感觉对为止。
