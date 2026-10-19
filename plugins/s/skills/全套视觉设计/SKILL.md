---
name: 全套视觉设计
description: "管品牌、设计令牌（token，可复用的颜色、字体、间距数值）、界面样式、标志、企业视觉识别（CIP，一套品牌物料）、幻灯片、横幅、图标、社交图片。标志 55 种风格，可用 Gemini、Atlas Cloud 或 MuAPI 生成。企业视觉识别 50 项以上的物料和样机。幻灯片是带 Chart.js 的 HTML。横幅 22 种风格，覆盖社交、广告、网页、印刷。图标 15 种风格，输出 SVG，用 Gemini 3.1 Pro。社交图片把 HTML 截成图，多平台。能做的事：设计标志、做企业视觉识别、生成样机、做幻灯片、设计横幅、生成图标、做社交图片和社交媒体图、定品牌。平台：Facebook、Twitter、LinkedIn、YouTube、Instagram、Pinterest、TikTok、Threads、Google Ads。和 `设计系统`、`UIUX知识库`、`shadcn组件` 的分工：这个管品牌物料和生成。`references/` 仍是英文。"
argument-hint: "[design-type] [context]"
license: MIT
metadata:
  author: claudekit
  version: "2.1.0"
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。


# 全套视觉设计

品牌物料和生成都在这一份里：品牌、令牌、界面、标志、企业视觉识别、幻灯片、横幅、社交图片、图标。

`references/` 里的长说明仍是英文。需要细节时再读，路径不要改。搜索词用英文，数据是英文的。

## 什么时候用

- 品牌识别、语气（品牌说话的口气）、素材
- 设计令牌（token，可复用的颜色、字体、间距数值）和规格
- 界面样式：用 shadcn/ui（一套现成组件）和 Tailwind（用类名写样式的 CSS 框架）写代码
- 标志设计和用 AI 生成
- 企业视觉识别（CIP，一套品牌物料）的交付物
- 演示文稿和路演幻灯片（pitch deck）
- 横幅：社交媒体、广告、网页、印刷
- 社交图片：Instagram、Facebook、LinkedIn、Twitter、Pinterest、TikTok

## 事先分清去哪做

| 任务 | 去哪 | 说明 |
|------|------|------|
| 品牌识别、语气、素材 | 本技能 | 颜色和字体用本技能自己的 `references/` 和脚本。配色、字体也可以查 `UIUX知识库`。本插件没有 `brand` |
| 令牌、规格、CSS 变量 | `设计系统` | 本插件里有 |
| shadcn/ui、Tailwind、写代码 | `shadcn组件` | 本插件没有 `ui-styling`。用 Tailwind 和 shadcn 写代码时查这里 |
| 做标志、用 AI 生成 | 标志（本技能自带） | `references/logo-design.md` |
| 企业视觉识别样机、交付物料 | 企业视觉识别（本技能自带） | `references/cip-design.md` |
| 演示文稿、路演幻灯片 | 幻灯片（本技能自带） | `references/slides.md` |
| 横幅、封面、页头 | 横幅（本技能自带） | `references/banner-sizes-and-styles.md` |
| 社交媒体图片 | 社交图片（本技能自带） | `references/social-photos-design.md` |
| SVG 图标、成套图标 | 图标（本技能自带） | `references/icon-design.md` |

## 脚本路径

这个技能和它的 `references/` 里写的脚本路径，都相对于包含这份 SKILL.md 的目录。包含这份 SKILL.md 的文件夹就是技能目录。`scripts/<file>` 就是本技能自己的 `scripts/`。工作目录保持在项目根目录。脚本会读写项目里的文件，例如 `docs/brand-guidelines.md`、`assets/design-tokens.json` 或 `src/`，这些相对项目根目录。

本插件没有 `brand`、`ui-styling`。不要去找 `../brand` 或 `../ui-styling`。参考文件里如果写了 `../design-system/scripts/`，旁边的技能文件夹叫 `设计系统`。品牌颜色和字体用本技能自己的 `references/` 和脚本。配色、字体也可以查 `UIUX知识库`。令牌和规格查 `设计系统`。用 Tailwind 和 shadcn 写代码时查 `shadcn组件`。

命令里写的是 `python3`。找不到 `python` 就试 `python3`。

## 标志设计（本技能自带）

55 种以上的风格，30 套配色，25 份行业指南。用 Gemini Nano Banana、Atlas Cloud、MuAPI 生成图片。

### 标志：生成设计简报

设计简报（design brief）就是动手前先写清品牌要什么。

```bash
python3 scripts/logo/search.py "tech startup modern" --design-brief -p "BrandName"
```

### 标志：搜风格、颜色、行业

搜索用 BM25（一种按词匹配打分的办法）。搜索词用英文，风格、颜色、行业这些数据是英文的。

```bash
python3 scripts/logo/search.py "minimalist clean" --domain style
python3 scripts/logo/search.py "tech professional" --domain color
python3 scripts/logo/search.py "healthcare medical" --domain industry
```

### 标志：用 AI 出图

**一定要**把生成出来的标志放在白底上。

```bash
python3 scripts/logo/generate.py --brand "TechFlow" --style minimalist --industry tech
python3 scripts/logo/generate.py --prompt "coffee shop vintage badge" --style vintage
python3 scripts/logo/generate.py --brand "TechFlow" --provider atlas
python3 scripts/logo/generate.py --brand "TechFlow" --provider muapi
python3 scripts/logo/generate.py --brand "TechFlow" --provider muapi --muapi-model nano-banana-pro
```

**注意：** 脚本报错，就直接改脚本。

生成之后，一定要问用户要不要做 HTML 预览。要的话，用本插件里的 `UIUX知识库` 做一页图库。

## 企业视觉识别（本技能自带）

50 项以上的交付物料，20 种风格，20 个行业。用 Gemini Nano Banana（Flash / Pro）。

样机（mockup）是套上真实场景的效果图，比如名片拍在桌上。

### 企业视觉识别：生成简报

```bash
python3 scripts/cip/search.py "tech startup" --cip-brief -b "BrandName"
```

### 企业视觉识别：按类别搜

```bash
python3 scripts/cip/search.py "business card letterhead" --domain deliverable
python3 scripts/cip/search.py "luxury premium elegant" --domain style
python3 scripts/cip/search.py "hospitality hotel" --domain industry
python3 scripts/cip/search.py "office reception" --domain mockup
```

### 企业视觉识别：生成样机

下面四段分别是：带标志（推荐）、整套物料、Pro 模型（文字用 4K）、不带标志。

```bash
# With logo (RECOMMENDED)
python3 scripts/cip/generate.py --brand "TopGroup" --logo /path/to/logo.png --deliverable "business card" --industry "consulting"

# Full CIP set
python3 scripts/cip/generate.py --brand "TopGroup" --logo /path/to/logo.png --industry "consulting" --set

# Pro model (4K text)
python3 scripts/cip/generate.py --brand "TopGroup" --logo logo.png --deliverable "business card" --model pro

# Without logo
python3 scripts/cip/generate.py --brand "TechFlow" --deliverable "business card" --no-logo-prompt
```

模型：`flash`（默认，编号 `gemini-2.5-flash-image`），`pro`（编号 `gemini-3-pro-image`）。要换编号，`flash` 用环境变量 `GEMINI_FLASH_IMAGE_MODEL`，`pro` 用 `GEMINI_PRO_IMAGE_MODEL`。

### 企业视觉识别：渲染成 HTML 演示

```bash
python3 scripts/cip/render-html.py --brand "TopGroup" --industry "consulting" --images /path/to/cip-output
```

**提示：** 还没有标志的话，先做上面的标志设计。

## 幻灯片（本技能自带）

做 HTML 幻灯片：用 Chart.js（图表库）画图，用设计令牌管颜色和字号，用文案公式写句子。

上游工具包里有一条 `/slides:create`。本插件没有这条命令。`references/slides-create.md` 仍是英文，里面写的是去调用 `slides` 技能，本插件也没有这个技能。做幻灯片按本文步骤，读下面列出的参考文件。令牌和幻灯片搜索用 `设计系统`。

做幻灯片时读 `references/slides-create.md`。

### 幻灯片：资料

| 主题 | 文件 |
|------|------|
| 制作指南 | `references/slides-create.md` |
| 版式 | `references/slides-layout-patterns.md` |
| HTML 模板 | `references/slides-html-template.md` |
| 文案 | `references/slides-copywriting-formulas.md` |
| 策略 | `references/slides-strategies.md` |

## 横幅设计（本技能自带）

社交、广告、网页、印刷，一共 22 种美术方向（art direction，画面怎么处理）。横幅这条用本技能的 `references/banner-sizes-and-styles.md`，风格和配色再查 `UIUX知识库`。用浏览器找参考、生成图片、截图，当前环境有就用。没有就用用户给的素材，或用 CSS 画出来，再用手头的预览和截图办法。

完整尺寸和风格读 `references/banner-sizes-and-styles.md`。

### 横幅：步骤

1. **问清需求** — 问用户：用途、平台、内容、品牌、风格、数量
2. **找参考** — 读 `references/banner-sizes-and-styles.md`，风格和配色查 `UIUX知识库`。要是能用浏览器，并且允许上网查，就收集 3 到 5 个参考
3. **设计** — 按平台的准确像素做 HTML/CSS 横幅。用用户给的素材，或用 CSS 画。当前环境要是能生成图片，也可以用
4. **导出** — 用手头的浏览器或截图，按准确像素存成 PNG。做不到就交出 HTML/CSS 源文件，PNG 标成还没导出
5. **给用户看** — 几个方案并排，按反馈改

### 横幅：常用尺寸

| 平台 | 类型 | 尺寸（px） |
|------|------|-----------|
| Facebook | 封面 | 820 x 312 |
| Twitter/X | 页头 | 1500 x 500 |
| LinkedIn | 个人封面 | 1584 x 396 |
| YouTube | 频道封面 | 2560 x 1440 |
| Instagram | 快拍（Story） | 1080 x 1920 |
| Instagram | 帖子 | 1080 x 1080 |
| Google Ads | 中矩形（Med Rectangle） | 300 x 250 |
| Website | 首屏（Hero） | 1920 x 600-1080 |

### 横幅：常用风格

| 风格 | 适合 |
|------|------|
| Minimalist（极简） | 软件服务（SaaS）、科技 |
| Bold Typography（大字） | 公告 |
| Gradient（渐变） | 现代品牌 |
| Photo-Based（照片） | 生活方式、电商 |
| Geometric（几何） | 科技、金融科技（fintech） |
| Glassmorphism（玻璃拟态） | 软件服务、应用 |
| Neon/Cyberpunk（霓虹、赛博） | 游戏、活动 |

### 横幅：设计时守这几条

- 安全区：要紧的内容放在画面中间 70% 到 80%
- 一条横幅只放一个行动按钮（CTA，叫人去点的那个），放右下角，高度至少 44px
- 字体最多两种。正文至少 16px，标题至少 32px
- 广告里文字面积低于 20%。Meta 超了会罚
- 印刷：300 DPI（每英寸点数），CMYK（印刷四色），出血 3 到 5 毫米

## 图标设计（本技能自带）

15 种风格，12 个类别。Gemini 3.1 Pro Preview 生成的是 SVG 文本。SVG 是矢量图，本质是 XML 文本。

### 图标：生成单个

```bash
python3 scripts/icon/generate.py --prompt "settings gear" --style outlined
python3 scripts/icon/generate.py --prompt "shopping cart" --style filled --color "#6366F1"
python3 scripts/icon/generate.py --name "dashboard" --category navigation --style duotone
```

### 图标：一次出几版

```bash
python3 scripts/icon/generate.py --prompt "cloud upload" --batch 4 --output-dir ./icons
```

### 图标：一次导出多个尺寸

```bash
python3 scripts/icon/generate.py --prompt "user profile" --sizes "16,24,32,48" --output-dir ./icons
```

### 图标：常用风格

风格名是命令参数，保持英文，才能对上数据和 `--style`。

| 风格 | 适合 |
|------|------|
| outlined | 界面、网页应用 |
| filled | 手机应用、导航栏 |
| duotone | 市场物料、落地页 |
| rounded | 语气亲和的应用、健康 |
| sharp | 科技、金融科技、企业 |
| flat | Material 风格、接近 Google |
| gradient | 现代品牌、软件服务 |

**模型：** `gemini-3.1-pro-preview`。只出文本（SVG 是 XML 文本）。不用图片生成接口。

## 社交图片（本技能自带）

多平台社交图：先用 HTML/CSS 做，再截图导出。配色和字体查 `UIUX知识库`，令牌查 `设计系统`。品牌颜色和字体用本技能自己的 `references/` 和脚本。本插件没有 `brand`。截图用 Chrome 无界面模式（headless）、Playwright 或 Puppeteer，详见参考文件。

尺寸、模板、做法读 `references/social-photos-design.md`。

### 社交图片：步骤

1. **把步骤记下来** — 用手头的任务清单记下下面这些步骤。互不依赖的部分可以同时做
2. **拆开要求** — 从用户的话里取出：主题、平台、风格、品牌背景、要出现的内容
3. **先出几个方案** — 想 3 到 5 个，问用户选哪个
4. **设计** — 品牌颜色和字体用本技能的 `references/` 和脚本，令牌用 `设计系统`，版式和配色用 `UIUX知识库`。每个方案、每个尺寸各写一份 HTML
5. **导出** — 用 Chrome 无界面模式、Playwright 或 Puppeteer，按准确像素截图。工具要是支持设备缩放倍数（device scale factor），就用 2 倍。详见参考文件
6. **核对** — 用浏览器或看图工具打开导出的 PNG，检查。版式或样式有问题就改，再导出一次
7. **写报告** — 把设计决定的摘要写到 `plans/reports/`
8. **把文件归位** — 把输出文件和报告放进项目的素材目录

### 社交图片：常用尺寸

| 平台 | 尺寸（px） | 平台 | 尺寸（px） |
|------|-----------|------|-----------|
| IG 帖子 | 1080×1080 | FB 帖子 | 1200×630 |
| IG 快拍 | 1080×1920 | X 帖子 | 1200×675 |
| IG 轮播 | 1080×1350 | LinkedIn | 1200×627 |
| YT 缩略图 | 1280×720 | Pinterest | 1000×1500 |

## 整套怎么做

### 一整套品牌物料

1. **标志** → `scripts/logo/generate.py` → 生成几版标志
2. **企业视觉识别** → `scripts/cip/generate.py --logo ...` → 做交付物料的样机
3. **演示** → 读 `references/slides-create.md` → 做路演幻灯片。本插件没有 `/slides:create`，按本文幻灯片一节的步骤做

### 新建设计系统

1. **品牌** — 用本技能的 `references/` 和脚本定颜色、字体、语气。配色和字体也可以查 `UIUX知识库`。不要去找 `brand`
2. **令牌** — 用 `设计系统` 做语义令牌（semantic token，按用途起名的那一层）
3. **写进代码** — 用 `shadcn组件` 配 Tailwind 和 shadcn/ui。不要去找 `ui-styling`

## 参考文件

`references/` 仍是英文。`references/design-routing.md` 里的 `design-system` 是 `设计系统`，`ui-ux-pro-max` 是 `UIUX知识库`。用 Tailwind 和 shadcn 写代码时，里面的 `ui-styling` 改查 `shadcn组件`。`brand` 在本插件里没有对应技能，品牌颜色和字体用本技能自己的 `references/` 和脚本。不要调用那些英文技能，也不要去找 `../brand` 或 `../ui-styling`。

| 主题 | 文件 |
|------|------|
| 任务怎么分流 | `references/design-routing.md` |
| 标志设计指南 | `references/logo-design.md` |
| 标志风格 | `references/logo-style-guide.md` |
| 标志用色 | `references/logo-color-psychology.md` |
| 标志提示词 | `references/logo-prompt-engineering.md` |
| 企业视觉识别指南 | `references/cip-design.md` |
| 企业视觉识别物料 | `references/cip-deliverable-guide.md` |
| 企业视觉识别风格 | `references/cip-style-guide.md` |
| 企业视觉识别提示词 | `references/cip-prompt-engineering.md` |
| 幻灯片制作 | `references/slides-create.md` |
| 幻灯片版式 | `references/slides-layout-patterns.md` |
| 幻灯片模板 | `references/slides-html-template.md` |
| 幻灯片文案 | `references/slides-copywriting-formulas.md` |
| 幻灯片策略 | `references/slides-strategies.md` |
| 横幅尺寸和风格 | `references/banner-sizes-and-styles.md` |
| 社交图片指南 | `references/social-photos-design.md` |
| 图标设计指南 | `references/icon-design.md` |

## 脚本

| 脚本 | 干什么 |
|------|--------|
| `scripts/logo/search.py` | 搜标志的风格、颜色、行业 |
| `scripts/logo/generate.py` | 用 Gemini 生成标志 |
| `scripts/logo/core.py` | 标志数据的 BM25 搜索 |
| `scripts/cip/search.py` | 搜企业视觉识别的物料、风格、行业 |
| `scripts/cip/generate.py` | 用 Gemini 生成企业视觉识别样机 |
| `scripts/cip/render-html.py` | 把样机渲染成 HTML 演示 |
| `scripts/cip/core.py` | 企业视觉识别数据的 BM25 搜索 |
| `scripts/icon/generate.py` | 用 Gemini 3.1 Pro 生成 SVG 图标 |

## 先确认 Python

**Python：** 这个技能用 Python 脚本。Windows 上把 `python3` 换成 `python`（例如把 `python3 scripts/logo/search.py` 换成 `python scripts/logo/search.py`）。

找不到 `python` 就试 `python3`。

先看装了没有：

```bash
python3 --version || python --version
```

## 安装

```bash
export GEMINI_API_KEY="your-key"  # https://aistudio.google.com/apikey
pip install google-genai pillow

# Optional MuAPI provider (no extra Python package required)
export MUAPI_API_KEY="your-key"
```

MuAPI 用的是异步模型接口，以及查询预测结果的接口。鉴权看 [MuAPI API 参考](https://muapi.ai/docs/api-reference)。各模型当前的字段说明看 [nano-banana 模型约定](https://api.muapi.ai/api/v1/models/nano-banana) 或 [nano-banana-pro 模型约定](https://api.muapi.ai/api/v1/models/nano-banana-pro)。标志生成器支持文档里的这两种模型短名，会带上它们都要求的 `prompt`，以及可选的 `aspect_ratio`。Pro 模型还可以带可选的 `resolution`。这条只做标志的流程不改 `resolution`，用服务商的默认值。

> **Windows：** 装包用 `python -m pip install ...`。

## 和本插件里其他技能的分工

这个管品牌物料和生成。

- `设计系统`：令牌、规格、CSS 变量。本插件里有。
- `UIUX知识库`：配色、字体、界面知识。本插件里有。
- `shadcn组件`：用 Tailwind 和 shadcn/ui 写代码。本插件里有。

本插件没有 `brand`、`ui-styling`，也没有 `ui-ux-pro-max` 这个英文名。品牌颜色和字体用本技能自己的 `references/` 和脚本。不要去找 `../brand` 或 `../ui-styling`。
