---
name: Figma做动画
description: "`use_figma` MCP 工具的动效 / 动画知识——通过手动关键帧、动画样式、缓动和时间轴时长，让 Figma 节点动起来。只要任务涉及给节点添加、编辑或查看动画，就和 Figma插件基础 一起加载。也包括使用自定义动画样式。"
disable-model-invocation: false
---

> 翻译自 Figma 官方仓库 https://github.com/figma/mcp-server-guide （skills/figma-use-motion，commit f278942，对应 Cursor 插件编号 657）的 `figma-use-motion` skill，原作者 Figma，许可证：未注明许可证（仓库里没有找到 LICENSE 文件），仅供自用。
> 说明：参考文件 `references/` 一共约 49 KB，太大，保留英文原文。下面要求在 `skillNames` 里写的是原名 `figma-use-motion`（给 Figma 做使用统计用），保持原样。链接里的 `../figma-use/...` 已经改成 `../Figma插件基础/...`，正文里提到的其他 skill 也换成了中文名。
> 英文名备份：s-figma-use-motion

# use_figma —— 用于动效的 Figma 插件 API skill

`use_figma` MCP 工具的动效知识。[Figma插件基础](../Figma插件基础/SKILL.md) 讲的是 Plugin API 的基础规则——两个要一起加载。

**做动效时调用 `use_figma`，一定要传 `skillNames: "figma-use-motion"`（和 `figma-use` 一起，用逗号分隔）。** 只用于日志统计。

## 运行时的功能开关

调用者可能没有开通动效 API。不可用时，这个 skill 里提到的每一个动效属性和辅助函数都会报错 `"<name>" is not a supported API`。

**遇到这个错误就赶快收手。** 不要重试；告诉用户他没有开通动效功能，然后停下。否则你会白白浪费调用次数，还会用一模一样的重复失败把用户搞糊涂。

即使其他动效 API 能用，自定义动画样式也可能没有开通。可用性检查和退路做法见 [motion-custom-styles.md](references/motion-custom-styles.md)。

应用 `TextStagger` 之前，先通过 `figma.motion.figmaAnimationStyles()` 找到它。如果没有，就说明这次会话里文字动效不可用；不要跳过查找这一步，也不要悄悄换成整个图层的动效。

## 什么时候用这个 skill

只要 `use_figma` 任务涉及以下内容，就加载这个 skill：

- 给节点添加、编辑或删除关键帧（`manualKeyframeTracks`、`applyManualKeyframeTrack`、`removeManualKeyframeTrack`）。
- 让填充或描边颜色随时间变化。
- 应用、编辑或删除动画样式（`applyAnimationStyle`、`removeAnimationStyle`、`animationStyles`）。
- 查找、新建、编辑、整理、应用或删除**本地自定义动画样式**——保存在文件里、有名字、可重复使用的动效样式（`figma.getLocalCustomAnimationStylesAsync`、`figma.createCustomAnimationStyle`）。
- 让可编辑文字里的字符、单词、行或段落动起来，包括打字机式逐字出现，以及修改文字动画里的样式。写之前先加载 [text-animation.md](references/text-animation.md)。
- 通过 `node.timelines` / `node.setTimelineDuration(id, seconds)` 读取或设置时间轴时长。
- 为以上任何一项选择缓动。

静态的设计工作（画形状、做组件、变量、布局）只用 [Figma插件基础](../Figma插件基础/SKILL.md) 就行——这个 skill 只管“时间”这个维度。

## 开放的动效 API

- `node.manualKeyframeTracks` —— 读/写手动关键帧（包括填充、描边和效果的轨道）。
- `node.applyManualKeyframeTrack(field, track)` / `node.removeManualKeyframeTrack(field)` —— 添加、替换或删除一条手动关键帧轨道，不用重写整个对象。
- `node.animationStyles` —— 读/写应用在节点上的动画样式元数据。
- `node.applyAnimationStyle(styleId, presetData?)` / `node.removeAnimationStyle(id)` —— 应用一个找到的样式；用返回的/读回来的 `id` 删除一个已应用的样式实例。
- `node.timelines` —— 只读，所在顶层画框的时间轴列表，时长单位是秒。
- `node.setTimelineDuration(id, durationSeconds)` —— 设置所在顶层画框的时间轴时长。
- `node.animations` —— 只读，解析后的关键帧数据（目前只有手动轨道——见 [motion-patterns.md](references/motion-patterns.md)）。
- `figma.motion.figmaAnimationStyles()` —— 只读，Figma 官方自带的动画样式定义列表。
- 还有各种用来处理自定义动画样式的 API，见 [motion-custom-styles.md](references/motion-custom-styles.md)

编写自定义 `"figma:motion"` 预设模块的源码不在本 skill 范围内。在找到的 `TextStagger` 里配置 Position（位置）、Rotation（旋转）、Scale（缩放）、Opacity（不透明度）和 Blur（模糊）样式是支持的；这些是一个原生预设的属性，不是新的预设源码。如果请求需要编写新的预设模块，就说明这个限制；不要编造一个。

## 参考文档

根据任务内容按需加载：

| 文档 | 什么时候加载 | 讲什么 |
|-----|-------------|----------------|
| [motion-patterns.md](references/motion-patterns.md) | 添加/编辑动效动画 | 手动关键帧、填充/描边动画、应用动画样式、时间轴时长 |
| [motion-custom-styles.md](references/motion-custom-styles.md) | 任何关于可重复使用的命名动效样式的工作 | 查找、新建、编辑、整理、应用、删除和验证本地自定义动画样式 |
| [text-animation.md](references/text-animation.md) | 新建/编辑文字逐渐出现、打字机效果或错开出现的文字 | 原生 `TextStagger`、分组/顺序、组合的文字样式、时间、编辑/删除、保持文字可编辑 |
| [motion-easing.md](references/motion-easing.md) | 设置动画缓动 | 关键帧缓动对象、自定义三次贝塞尔/弹簧、`HOLD`、在动画样式里设置缓动 |

## 验证动画

`get_screenshot` 只显示时间轴的**静止状态**，从来不显示运动。要检查运动，就用 `export_video` 导出视频再抽帧——但它在服务器上渲染，**又慢又贵（大约 10 秒到几分钟）**，所以每次渲染都要物尽其用。

**渲染之前先规划——成本随“像素 × 帧数”增长，所以两者都不要超过需要：**

1. **先挑好时刻。** 你需要的是每个*阶段*一帧（比如每个错开的步骤一帧，或者开始 / 中间 / 停稳），而不是流畅的播放——通常 4–6 帧。这个数量决定了你的 fps（每秒帧数）。
2. **尺寸按你必须看清的东西来定。** 先从小的开始——`constraint: { type: 'WIDTH', value: 320 }`、`quality: "low"`——但这个尺寸下文字和小元素会糊，所以需要判断细节时把 `WIDTH` 调高（768 以上）。不写 `constraint` = 原尺寸（1 倍；服务器最多限制到 10 倍 / 4096px）。
3. **fps 设得刚好够抽到那些帧：** `fps: 5` 能覆盖几帧；10 是上限。再高只会让渲染变臃肿。

**具体操作：** `export_video` 只能用在**顶层画框**上，动画要在它的子节点上（传那个画框，而不是你打了关键帧的子孙节点）。它会返回一个 `jobId`，状态是 `status: "processing"`——再用 `{ fileKey, jobId }` 调用它来查询进度。然后在本地用 `ffmpeg -ss <t> -i anim.mp4 -frames:v 1 frame_<t>.png` 抽帧——抽帧是免费的，所以既然已经付了渲染的代价，就把每一帧有用的信息都挖出来，而不是重新导出。如果没有 `ffmpeg` 这类抽帧工具，就跳过导出，改为根据关键帧推理。

**反复改到对为止。** 导出是用来诊断的，不是用来签字验收的：如果帧不对（顺序错、时间偏、缺了元素、遮罩把合成画面盖成空白），就修好关键帧/样式再重新导出。把*所有*帧都看完，把所有修改合成一轮再重新渲染——每次渲染都有实实在在的开销，所以要让每一次都值，而不是每改一小处就重新导出。

对于很小或者一眼就能看出对错的修改，完全跳过导出。

## 动手前检查清单

除了 [Figma插件基础 的动手前检查清单](../Figma插件基础/SKILL.md#8-pre-flight-checklist)，还要确认：

- [ ] 缓动用的是公开的 `{ type: 'EASE_OUT', easingFunctionCubicBezier?: …, easingFunctionSpring?: … }` 结构——不是 `OUT_CUBIC` 这种内部场景图名字。
- [ ] 先慢后快再慢（ease-in-out）用的是准确的公开枚举值 `EASE_IN_AND_OUT`（或 `EASE_IN_AND_OUT_BACK`）；绝不要写成无效的别名 `EASE_IN_OUT`。
- [ ] 被动画的节点不是顶层画框（页面的直接子节点）。改为给它的子孙节点做动画。
- [ ] 在公开的 Plugin API 里，时间轴的值以秒为单位。用 `setTimelineDuration` 延长；除非用户要求，绝不缩短。
- [ ] 文字内部的动效，用的是在现有文字节点上找到的 `TextStagger`。保留字符、格式、换行和无关的动画；它的 `duration` 是整个错开过程的总时长，不是每个字符的时间。
- [ ] 变换类关键帧字段用的是公开名字（`TRANSLATION_X`、`TRANSLATION_Y`、`ROTATION`、`SCALE_X`、`SCALE_Y`、`SCALE_XY`），不是内部的 `MOTION_*` 场景图名字。
- [ ] 手动关键帧字段来自 [motion-patterns.md](references/motion-patterns.md#animatable-fields) 里公开的允许列表；生成的/内部的场景图字段会故意报错。
- [ ] 返回了被修改的节点 ID（按 `Figma插件基础` 规则 15）。
- [ ] 当动效是否正确不是一眼能看出来、并且有抽帧工具（`ffmpeg`）时，用 `export_video` + 抽帧来验证——渲染小尺寸、低 `fps`，反复改到对为止（见上面“验证动画”一节）。`get_screenshot` 只显示静止状态。
