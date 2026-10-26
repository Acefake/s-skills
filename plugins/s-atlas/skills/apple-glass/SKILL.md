---
name: apple-glass
description: "「影盒风格」「按 yingbox 的 UI 做」「Apple TV 风格界面」「用我那套 UI」。按影盒（yingbox）的设计语言做界面：深色优先、纯黑底、实色卡片、玻璃只给浮动控件、8pt 间距、令牌化、组件化。Use when building or restyling UI in yingbox, or when the owner asks for the yingbox / Apple TV look in another web or Vue project."
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。

# 影盒界面语言

这是主人在影盒（Acefake/yingbox）里定下来的界面语言：Apple TV（iOS 26）风格，深色优先，克制、留白多、颜色交给海报。下文是规则，`references/` 里是可以直接拷走的令牌和材质。

和其它界面技能的关系：`impeccable` 管通用质量（可用性、无障碍、性能），本技能管长相。两者都对得上时，长相按这里，质量按 `impeccable` 查。只在点名时才用 `frontend-design`，它会给出别的视觉方向，和这里冲突。

## 先判断在哪个仓库

- **在 yingbox 里**：仓库自己的 `AGENTS.md`「UI conventions」、`src/renderer/src/assets/styles/tokens.css`、`src/renderer/src/components/ui/` 是最新真相，本技能的副本可能落后。先读它们，用现成组件，跑 `pnpm check:style`。
- **在别的项目里**：把 [references/tokens.css](references/tokens.css) 拷成项目的令牌文件，按需从 [references/materials.css](references/materials.css) 拷玻璃、规格标签、渐进模糊和海报网格。再按 [references/components.md](references/components.md) 建最小一套组件。项目已有设计系统时，先问主人是整体换皮还是只借几条规则。

## 一、长相

1. **底色分层靠明度，不靠线。** 深色：纯黑底 `#000` → 侧栏 `#0e0e10` → 卡片 `#1c1c1e` → 次级控件 `#2c2c2e`。能用留白分开就不画分隔线。浅色：`#f5f5f7` 底上放白卡，层次靠柔和投影，不是把深色反过来。
2. **颜色交给内容。** 界面本身只有中性灰。强调蓝 `--accent` 只用于焦点、链接、开关；选中态用 `--bg-active` 填底，不加边框。主按钮深色下白底黑字（`--action-*`），一个区域最多一个（比如详情页的「播放」）。
3. **玻璃只给浮动控件。** 侧栏、圆钮、胶囊、浮层、播放器控制条用 `.yb-glass`；内容卡片一律实色。压在画面上的控件加 `.is-media`，两套主题都取深色玻璃。系统「降低透明度」或设置开关打开时，玻璃换成同层级实色、去掉 `backdrop-filter`（低配机器开销大）。
4. **压在画面上的区域（Hero）加 `.yb-on-media`**，局部切回深色令牌，浅色主题下也不会盖一层白雾。画面底部用渐进模糊 `.yb-pblur`（三层递增 blur + mask + 一层暗化），不是一张黑色渐变。
5. **字体用系统字体**（SF / 苹方，Windows 为 Segoe / 雅黑）。字号只用 `--text-*` 档（11/12/13/14/17/22/28/34，8、9 只给规格字标）。字重只用 400 / 500 / 600，700 只给大标题，规格字标可单独豁免。
6. **圆角**：角标 4、小控件 6、控件 10、卡片 14、海报和剧照横卡 18、弹窗 20、大浮层 28，胶囊和圆钮用 full。
7. **图标用 Phosphor**（MIT），256 视框。导航和按钮用 fill，细小控件（箭头、窗口键、搜索、关闭）用 bold；收藏、评分等切换图标选中时换 fill。不用 emoji 当状态图标。
8. **规格标签照 Apple TV**：4K、HDR10 是浅灰实心小方块；DOLBY VISION / ATMOS 是双行文字标，不用杜比商标图；CC、中字是描边方块；分级是圆标。
9. **分区标题**：粗体大字，可点时后面跟灰色 ›。演职员用圆头像。剧集和预告用横卡：剧照铺满，下半同图渐进模糊加暗化，文字压在上面。

## 二、硬规则（写代码时）

- **不写裸值。** 字号、圆角、间距、时长、z-index、阴影、颜色全部引用令牌。间距只用 `--space-*`（4、8、12、16、20、24、32、40、48、64、80，加半档 2、6、10、14、28）；负值写 `calc(var(--space-n) * -1)`；`0` 和 `1px` 发丝线可以写裸值。确属布局偏移的，同一行末尾写 `/* style-tokens: layout（原因） */`。
- **控件高度**：按钮、分段切换、筛选胶囊用三档 28 / 36 / 44（`--control-height-sm|md|lg`）；输入框和下拉用两档 28 / 36（`size` sm / md）。
- **动效**：按下 100ms、悬停与淡入淡出 150ms、弹窗和面板 240ms、宽度和进度 350ms；缓动用 `--ease-out` / `--ease-spring`。系统「减少动态效果」时这些时长归零。
- **层级**用 `--z-*`：组件内的局部档（2…45）和全局 fixed 档（1100…10000）分开。遮罩和窗口成对时，窗口写 `calc(var(--z-…) + 1)`。toast 和确认框放浏览器 top layer（popover / modal `<dialog>`）。
- **不手写原生控件。** 组件库之外不写 `<button>`、`<input>`（file / range / hidden 除外）、`<select>`、`<textarea>`，用组件库里对应的组件；图片或卡片这类点击目标用无样式的 `Pressable`。不写静态 `style="..."`，动态 `:style` 可以。
- **组件样式可覆盖。** 组件库里状态和修饰选择器包进 `:where()`，页面一个 class 就能改尺寸和颜色。
- **等待反馈每种等待只用一种**：用户点出来的等待，用按钮自带的 loading（保持可聚焦，`aria-busy`，挡住重复点击，不设 `disabled`）；后台工作，内容后面放三个点；首屏结构已知时用骨架；知道总量就用真的 `role="progressbar"`。刷新或追加时，新内容到之前旧内容不动，滚动位置不跳。
- **键盘**：输入框回车提交要避开输入法上屏（`isComposing` / keyCode 229）。Esc 只关最上面一层，输入法组字时不关。
- **长列表走虚拟网格。** 无限滚动、聚合搜索、收藏、队列这类不定长列表，统一用一个虚拟网格组件，列数从 `grid-template-columns` 读。
- **优先图标按钮**，图标按钮必须带 `label`（读屏用，也当 tooltip 显示）。

组件清单和接口：[references/components.md](references/components.md)。外壳、Hero、详情页、海报墙、货架这些页面级做法：[references/patterns.md](references/patterns.md)。

## 三、步骤

1. 读需求，确认是新页面、改样式还是新组件。在 yingbox 里先读仓库的 UI 约定和 `components/ui/index.ts`，在别的项目里先确认令牌文件放在哪。
2. 能用现成组件就不新写。真缺一个组件时，放进组件库目录，状态选择器包 `:where()`，补中文 doc 注释，从组件库的入口导出。
3. 写样式只引用令牌。拿不准用哪档时，取最近的一档，别新增令牌；确实缺一档，先在令牌文件里加，并写一行注释说明它给谁用。
4. 跑检查。在 yingbox 里跑 `pnpm check:style`（会对照只减不增的基线）。别的项目跑本技能自带的检查：

   ```bash
   node <本技能目录>/scripts/check-style.mjs --src src --tokens src/styles/tokens.css --ui src/components/ui
   ```

   它查裸字号、裸圆角、裸间距、字面时长、数字 z-index、令牌文件以外的颜色字面量、多余字重，以及组件库外的原生控件和静态 `style=""`。同一行写 `style-tokens:` 注释就跳过那一行。
5. 两套主题都截图看：深色是主场，浅色也要能用。再打开「降低透明度」和「减少动态效果」各看一遍。浏览器截图和驱动用 `control-ui`。
6. 交付时说清改了哪些页面、用了哪些组件、是否新加了令牌。

## 不要

- 不要给内容卡片加玻璃，也不要在玻璃元素上再写 `background` / `backdrop-filter` / `box-shadow`，否则会盖掉材质。
- 不要用彩色大色块做装饰，不要渐变按钮，不要给选中态加描边。
- 不要把浅色主题做成深色的反相。
- 不要用杜比等商标图，用文字标。
- 不要为了「更像 Apple」引入别的 UI 库；影盒已去掉 ant-design-vue，新代码也不要引回来。
