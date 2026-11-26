---
name: theme-factory
description: "「给 PPT 换套主题」「统一网页和报告的配色字体」。为一份或多份产物选用或定制视觉主题。Use when applying a shared color and typography theme to slides, documents, reports, or web pages."
disable-model-invocation: true
---

本会话首次使用本库技能时，按[全局提示词自检](../wukong-init/references/daily-check.md)只读检查一次。

# 统一配色和字体

改编自 [Anthropic 的 theme-factory](https://github.com/anthropics/skills/tree/main/skills/theme-factory)，本文和主题表已中文化并调整。版权和许可见 [LICENSE.txt](LICENSE.txt)。

1. 查看已有品牌规范、目标媒介和现有文档样式。用户已指定主题时直接应用。缺少主题时，从[十套预设](references/themes.md)挑出符合场景的选项，也可以按品牌主色定制。在需要选择时，用一页代表性内容展示色板、标题和正文效果。
2. 给颜色明确分配背景、正文、强调、边框等用途。状态和图表再分配对照色，保留文字或符号提示。确定标题和正文的字体、字号与字重。检查中文字符覆盖情况，给缺少的字体设置中文回退。
3. 把主题应用到已有样式系统。PPT 用母版或主题，文档用段落和字符样式，网页用设计令牌或 CSS 自定义属性。原有内容与信息层级可直接沿用。
4. 打开实际导出的文件或页面，抽查标题、密集正文、图表、链接和交互状态。确认前景与背景对比足够，字体替换后没有断行或溢出。交付时记录选用的色值、字体和回退字体。
