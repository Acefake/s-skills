# 切换器

> （本文件是 `prototype` 的参考文件，翻译自 Emil Kowalski 的仓库 https://github.com/emilkowalski/skills 的 `skills/prototype/PICKER.md`，许可证 MIT，仅供自用。下面的代码必须原样照抄，所以保持英文原样；代码注释的意思在后面用中文说明。）

切换器的外观**不是设计决定**——它就是这份规格。原样照抄下面的标签、CSS 和接线；每次唯一会变的是版本名字和数量。它在每个项目里都保持一模一样，所以永远看起来是框架工具界面，而不是被评判的设计的一部分。不要用项目的 token、字体或颜色给它重新设计样式。

它是一个浮在底部正中的深色胶囊。深色玻璃效果放在任何页面上——浅色或深色——都行，所以它不跟随主题。

## 标签

先是滑动的高亮 span，然后每个版本一个按钮，一条细分隔线，最后是重播按钮（只有当至少一个版本有可以重新触发的动效时才放）：

```html
<nav class="proto-picker" aria-label="Prototype variants">
  <span class="proto-picker-highlight" aria-hidden="true"></span>
  <button class="proto-picker-item" data-active aria-current="true">Quiet</button>
  <button class="proto-picker-item">Editorial</button>
  <button class="proto-picker-item">Playful</button>
  <span class="proto-picker-divider" aria-hidden="true"></span>
  <button class="proto-picker-item proto-picker-replay" aria-label="Replay animation (R)">↻</button>
</nav>
```

在框架里，保留类名和结构；只换渲染语法。

## 样式

```css
.proto-picker {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 2147483647;
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 4px;
  border-radius: 999px;
  background: rgba(10, 10, 10, 0.82);
  -webkit-backdrop-filter: blur(12px) saturate(1.4);
  backdrop-filter: blur(12px) saturate(1.4);
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.08) inset,
    0 8px 24px rgba(0, 0, 0, 0.24),
    0 2px 6px rgba(0, 0, 0, 0.12);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-size: 13px;
  line-height: 1;
  -webkit-font-smoothing: antialiased;
  user-select: none;
  -webkit-user-select: none;
}

.proto-picker-highlight {
  position: absolute;
  top: 4px;
  left: 0;
  height: 28px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.12);
  will-change: transform;
}

/* The slide is enabled only after first paint (data-ready), so load doesn't animate. */
.proto-picker[data-ready] .proto-picker-highlight {
  transition:
    transform 250ms cubic-bezier(0.23, 1, 0.32, 1),
    width 250ms cubic-bezier(0.23, 1, 0.32, 1);
}

@media (prefers-reduced-motion: reduce) {
  .proto-picker[data-ready] .proto-picker-highlight { transition: none; }
}

.proto-picker-item {
  position: relative; /* sits above the highlight */
  display: flex;
  align-items: center;
  height: 28px;
  padding: 0 12px;
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: rgba(255, 255, 255, 0.55);
  font: inherit;
  cursor: pointer;
  transition: color 150ms ease-out;
}

.proto-picker-item:hover {
  color: rgba(255, 255, 255, 0.85);
}

.proto-picker-item:active {
  transform: scale(0.97);
}

.proto-picker-item:focus-visible {
  outline: 2px solid rgba(255, 255, 255, 0.4);
  outline-offset: 2px;
}

.proto-picker-item[data-active] {
  color: #fff;
}

.proto-picker-divider {
  width: 1px;
  height: 16px;
  margin: 0 4px;
  background: rgba(255, 255, 255, 0.12);
}

.proto-picker-replay {
  padding: 0 10px;
  font-size: 14px;
}

.proto-picker[data-position="top"] {
  bottom: auto;
  top: 24px;
}
```

（代码注释意思：滑动效果只在第一次绘制之后（data-ready）才启用，这样加载时不会有动画；relative 定位让按钮叠在高亮上面。）

## 规则

- **原样照抄。** 这些数值就是规格。不用项目字体、不用品牌色、不切换主题、不加额外的阴影或边框。
- **高亮滑动；版本切换保持即时。** 选中的胶囊在按钮之间动画移动（250ms，强力 ease-out），作为切换器本身的空间反馈——但正在预览的版本切换时仍然没有任何过渡。`width` 过渡是“只动 transform/opacity”规则的有意例外：这个元素只有 28px 高、绝对定位、没有依赖它布局的元素，所以绘制开销可以忽略不计。
- **唯一允许的修改：** 如果某个版本占据了屏幕底部正中（提示消息堆叠、底部面板、底部栏），就设置 `data-position="top"`，让切换器永远不挡住作品。它的其他任何东西都不能移动或改变。
- **重播按钮是有条件的。** 只有当至少一个版本有值得重新触发的进场或状态动画时，才显示重播按钮和它的分隔线；静态的比较用更短的胶囊。

## 行为约定

不管框架怎么渲染，约定都是固定的：

- 数字键 `1–N` 和 `←`/`→` 切换版本；`R` 重播。焦点在输入框、文本框、下拉选择或可编辑区域里，或者按住了修饰键时，忽略按键事件。
- 点击某一项就切换到它；任何时候都正好有一项带着 `data-active` 和 `aria-current="true"`，高亮滑到它那里。
- 选择通过网址参数（`?v=2`）在刷新后保留，没有就默认第 1 个版本。高亮的初始位置不带动画（`data-ready` 在第一次绘制之后才加上）。
- 切换时重新挂载版本（让进场动画重新播放）；重播键只重新挂载、不切换。

## 参考接线

独立 HTML 分支就原样照抄；在框架里，保持同样的行为，但用框架习惯的写法表达（用 state 代替 `innerHTML`，用带 key 的重新挂载代替 `requestAnimationFrame`，用 ref + layout effect 来测量高亮）。

```js
// `variants` is an array of render functions, one per variant, in picker order.
const stage = document.getElementById('stage');
const picker = document.querySelector('.proto-picker');
const highlight = picker.querySelector('.proto-picker-highlight');
const items = [...picker.querySelectorAll('.proto-picker-item:not(.proto-picker-replay)')];
const replay = picker.querySelector('.proto-picker-replay');
let current = 0;

function moveHighlight() {
  const el = items[current];
  highlight.style.width = el.offsetWidth + 'px';
  highlight.style.transform = `translateX(${el.offsetLeft}px)`;
}

function mount(i) {
  stage.innerHTML = '';
  // Clear first, render next frame, so entrance animations re-run.
  requestAnimationFrame(() => { stage.innerHTML = variants[i](); });
}

function setActive(i) {
  if (i < 0 || i >= variants.length) return;
  current = i;
  items.forEach((el, j) => {
    el.toggleAttribute('data-active', j === i);
    if (j === i) el.setAttribute('aria-current', 'true');
    else el.removeAttribute('aria-current');
  });
  moveHighlight();
  const url = new URL(location);
  url.searchParams.set('v', i + 1);
  history.replaceState(null, '', url);
  mount(i);
}

items.forEach((el, i) => el.addEventListener('click', () => setActive(i)));
replay?.addEventListener('click', () => mount(current));
window.addEventListener('resize', moveHighlight);

document.addEventListener('keydown', (e) => {
  if (/^(INPUT|TEXTAREA|SELECT)$/.test(e.target.tagName) || e.target.isContentEditable) return;
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  const num = parseInt(e.key, 10);
  if (num >= 1 && num <= variants.length) setActive(num - 1);
  else if (e.key === 'ArrowRight') setActive((current + 1) % variants.length);
  else if (e.key === 'ArrowLeft') setActive((current - 1 + variants.length) % variants.length);
  else if (e.key === 'r' || e.key === 'R') mount(current);
});

setActive((parseInt(new URLSearchParams(location.search).get('v'), 10) || 1) - 1);
// Enable the slide only after first paint, so load doesn't animate.
requestAnimationFrame(() => requestAnimationFrame(() => picker.setAttribute('data-ready', '')));
```

（代码注释意思：`variants` 是一个渲染函数数组，每个版本一个，按切换器里的顺序；先清空，下一帧再渲染，这样进场动画会重新播放；滑动效果只在第一次绘制之后才启用，这样加载时不会有动画。）
