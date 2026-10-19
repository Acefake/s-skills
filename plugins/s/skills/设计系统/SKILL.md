---
name: 设计系统
description: "做设计令牌（token，可复用的颜色、字体、间距数值）、组件规格和幻灯片。三层令牌从原始值到语义再到组件，配 CSS 变量、间距和字体阶梯、组件状态，以及符合品牌的演示文稿。和 `精致界面设计`、`UIUX知识库`、`全套视觉设计` 有重叠。这个专管令牌结构和幻灯片。`references/` 仍是英文。"
argument-hint: "[component or token]"
license: MIT
metadata:
  author: claudekit
  version: "1.0.0"
---

# 设计系统

令牌结构、组件规格、成系统的设计、幻灯片生成。

`references/` 里的长说明仍是英文。需要细节时再读，路径不要改。

## 什么时候用

- 建设计令牌
- 定组件的状态
- 做 CSS 变量体系
- 定间距和字体阶梯
- 把设计交给写代码的人
- 配 Tailwind 的主题
- **做幻灯片或演示文稿**

## 令牌结构

需要展开时读 `references/token-architecture.md`。

### 三层

```
Primitive (raw values)
       ↓
Semantic (purpose aliases)
       ↓
Component (component-specific)
```

原始值（primitive）是直接写下的色值这类数字。语义（semantic）是按用途起的别名。组件（component）是某个组件专用的。

**例子：**

```css
/* Primitive */
--color-blue-600: #2563EB;

/* Semantic */
--color-primary: var(--color-blue-600);

/* Component */
--button-bg: var(--color-primary);
```

## 脚本放在哪

这个技能和它的 `references/` 里写的脚本路径，都相对于包含这份 `SKILL.md` 的目录，不是相对于用户的项目。`scripts/<file>` 就是本技能自己的 `scripts/`。工作目录保持在项目根目录。脚本会读写项目里的文件，例如 `docs/brand-guidelines.md`、`assets/design-tokens.json` 或 `src/`，这些相对项目根目录。

本插件没有把上游的 `brand`、`ui-styling` 装成挨在旁边的技能。不要去找 `../brand` 或 `../ui-styling`。配色、字体、界面知识查 `UIUX知识库`。用 shadcn 写组件时查 `shadcn组件`。品牌物料、标志、横幅查 `全套视觉设计`。

## 先跑这两条

**生成令牌：**

```bash
node scripts/generate-tokens.cjs --config tokens.json -o tokens.css
```

**检查有没有把数值写死：**

```bash
node scripts/validate-tokens.cjs --dir src/
```

## 参考文件

| 主题 | 文件 |
|-------|------|
| 令牌结构 | `references/token-architecture.md` |
| 原始令牌 | `references/primitive-tokens.md` |
| 语义令牌 | `references/semantic-tokens.md` |
| 组件令牌 | `references/component-tokens.md` |
| 组件规格 | `references/component-specs.md` |
| 状态和变体 | `references/states-and-variants.md` |
| 接上 Tailwind | `references/tailwind-integration.md` |

## 组件规格长什么样

| 属性 | 默认 | 悬停 | 按下 | 禁用 |
|----------|---------|-------|--------|----------|
| 背景 | primary | primary-dark | primary-darker | muted |
| 文字 | white | white | white | muted-fg |
| 边框 | none | none | none | muted-border |
| 阴影 | sm | md | none | none |

## 脚本

| 脚本 | 干什么 |
|--------|---------|
| `generate-tokens.cjs` | 从 JSON 令牌配置生成 CSS |
| `validate-tokens.cjs` | 检查代码里写死的数值 |
| `search-slides.py` | 用 BM25 搜索幻灯片做法，并给结合上下文的建议 |
| `slide-token-validator.py` | 检查幻灯片 HTML 是否只用了令牌 |
| `fetch-background.py` | 从 Pexels 或 Unsplash 取图 |

## 模板

| 模板 | 干什么 |
|----------|---------|
| `design-tokens-starter.json` | 三层结构的起步 JSON |

## 幻灯片

用设计令牌、Chart.js，再加上一套按上下文做决定的办法，做符合品牌的演示文稿。

上游工具包里有一条斜杠命令，本插件没有这条命令。做幻灯片就按下面的步骤，不要去调用它：

```bash
/slides:create "10-slide investor pitch for ClaudeKit Marketing"
```

### 以这些文件为准

| 文件 | 干什么 |
|------|---------|
| `docs/brand-guidelines.md` | 品牌身份、口气、颜色 |
| `assets/design-tokens.json` | 令牌定义（原始值到语义再到组件） |
| `assets/design-tokens.css` | CSS 变量（幻灯片里引入） |
| `assets/css/slide-animations.css` | CSS 动画库 |

### 搜索幻灯片做法（BM25）

```bash
# Basic search (auto-detect domain)
python scripts/search-slides.py "investor pitch"

# Domain-specific search
python scripts/search-slides.py "problem agitation" -d copy
python scripts/search-slides.py "revenue growth" -d chart

# Contextual search (Premium System)
python scripts/search-slides.py "problem slide" --context --position 2 --total 9
python scripts/search-slides.py "cta" --context --position 9 --prev-emotion frustration
```

如果找不到 `python`，就试 `python3`。搜索词用英文，数据文件是英文的。

### 做决定时用的 CSV

| 文件 | 干什么 |
|------|---------|
| `data/slide-strategies.csv` | 15 套幻灯片结构、情绪弧线和节拍 |
| `data/slide-layouts.csv` | 25 种版式、组件变体和动画 |
| `data/slide-layout-logic.csv` | 目标对应到版式，以及要不要打破重复 |
| `data/slide-typography.csv` | 内容类型对应到字体阶梯 |
| `data/slide-color-logic.csv` | 情绪对应到用色 |
| `data/slide-backgrounds.csv` | 幻灯片类型对应到图片类别（Pexels / Unsplash） |
| `data/slide-copy.csv` | 25 个文案公式（PAS、AIDA、FAB） |
| `data/slide-charts.csv` | 25 种图表及 Chart.js 配置 |

### 决定的顺序

```
1. Parse goal/context
        ↓
2. Search slide-strategies.csv → Get strategy + emotion beats
        ↓
3. For each slide:
   a. Query slide-layout-logic.csv → layout + break_pattern
   b. Query slide-typography.csv → type scale
   c. Query slide-color-logic.csv → color treatment
   d. Query slide-backgrounds.csv → image if needed
   e. Apply animation class from slide-animations.css
        ↓
4. Generate HTML with design tokens
        ↓
5. Validate with slide-token-validator.py
```

### 打破重复（Duarte 的火花线）

好的演示会在两种情绪之间交替：

```
"What Is" (frustration) ↔ "What Could Be" (hope)
```

系统在大约三分之一和三分之二的位置计算该不该换情绪。

### 每一页都必须

1. 引入 `assets/design-tokens.css`，这是唯一的数值来源
2. 用 CSS 变量：`var(--color-primary)`、`var(--slide-bg)` 等
3. 图表用 Chart.js，不要只用 CSS 画柱子
4. 有导航（键盘方向键、点击、进度条）
5. 内容居中
6. 为说服和转化服务

### 接上 Chart.js

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>

<canvas id="revenueChart"></canvas>
<script>
new Chart(document.getElementById('revenueChart'), {
    type: 'line',
    data: {
        labels: ['Sep', 'Oct', 'Nov', 'Dec'],
        datasets: [{
            data: [5, 12, 28, 45],
            borderColor: '#FF6B6B',  // Use brand coral
            backgroundColor: 'rgba(255, 107, 107, 0.1)',
            fill: true,
            tension: 0.4
        }]
    }
});
</script>
```

### 令牌怎么算合规

```css
/* CORRECT - uses token */
background: var(--slide-bg);
color: var(--color-primary);
font-family: var(--typography-font-heading);

/* WRONG - hardcoded */
background: #0D0D0D;
color: #FF6B6B;
font-family: 'Space Grotesk';
```

### 一份能跑的例子

上游例子的路径（本技能目录里不一定有这份 HTML，没有就不要编造）：

```
assets/designs/slides/claudekit-pitch-251223.html
```

## 做到这些

1. 组件里不要写原始十六进制颜色，一律引用令牌
2. 语义层用来切换主题（浅色 / 深色）
3. 组件令牌用来按组件单独调整
4. 需要控制透明度时用 HSL
5. 每个令牌的用途写下来
6. **幻灯片必须引入 design-tokens.css，并且只用 `var()`**
