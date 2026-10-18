---
name: Figma着色器
description: "**必须先做的前置步骤**——在调用 `create_shader` 或 `update_shader` 之前，先加载这个 skill。当用户要求在 Figma 里新建、编写、修改、修复或反复调整着色器（shader）效果、着色器填充、自定义效果、自定义填充或程序化着色器时使用。"
disable-model-invocation: false
---

> 翻译自 Figma 官方仓库 https://github.com/figma/mcp-server-guide （skills/figma-shaders，commit f278942，对应 Cursor 插件编号 657）的 `figma-shaders` skill，原作者 Figma，许可证：未注明许可证（仓库里没有找到 LICENSE 文件），仅供自用。
> 说明：着色器（shader）是在显卡上运行、逐个像素计算颜色的小程序。工具名、字段名和网址保持原样。参考文件 `references/authoring.md` 也已翻译成中文。
> 英文名备份：s-figma-shaders

# 新建和更新 Figma 着色器

每次调用 `create_shader` 或 `update_shader` 之前，都要先加载这个 skill。它讲的是通过 Figma MCP 服务器，编写账户库里的着色器。只是读取或应用一个现有的着色器，不需要这个 skill。

着色器分两种：

- `effect`（效果）会采样并变换它下面已经渲染好的图层。用于模糊、扭曲、发光、调色、像素化、半色调网点或其他后期处理。
- `fill`（填充）不需要输入图像，自己生成像素。用于渐变、图案、噪点、纹理和程序化生成的背景。

更新时不要悄悄换种类。传给 `update_shader` 的 `kind` 必须和现有着色器一致。

## 新建流程

1. 判断请求是效果还是填充。只有从想要的视觉效果看不出区别时才问。
2. 确定 `planKey`。用户提供了就用用户的；否则调用 `whoami`。如果只有一个符合条件的套餐就自动用它；如果有几个差别明显的套餐，就请用户选。
3. 调用一次 `create_shader`，带上简短的名字、描述、选好的 `kind` 和 `planKey`。这会建出一个初始脚手架，而不是用户要的最终着色器。
4. 用返回的 `id` 调用 `get_shader`，然后读取每一个源文件 URI。如果客户端读不了 MCP resources，就改用 `includeSource: true` 调用 `get_shader`。这样你就清楚了运行时的 import 和脚手架固定的元数据约定。
5. 为用户要的效果，写出完整的替换版 `main.ts`。
6. 用返回的 `id`、同样的 `kind`、`files: [{ path: "main.ts", content: "..." }]` 和一条具体的 `commitMessage` 调用 `update_shader`。要改名字、描述或动画能力时，用 `metadata`。源码读取了与时间相关的帧输入时，设 `metadata.isAnimated: true`；读取了 `frame.mousePosition` 时，设 `metadata.usesMouse: true`。

绝不要在 `create_shader` 之后就停下：初始脚手架只是一个结构上的起点。

## 更新流程

1. 用 `list_shaders` 找到着色器，然后调用 `get_shader`。用它的 `type`（`effect` 或 `fill`）作为更新时必填的种类。
2. 编辑之前，读取 `get_shader` 返回的每一个源文件 URI。如果客户端读不了 MCP resources，就用 `includeSource: true` 调用它。以这些文件为当前的准确版本。
3. 除非用户要求修改，否则保留现有的控件和行为。
4. 调用 `update_shader`，在 `files` 数组里放完整的替换版 `main.ts`，不要放差异补丁或片段。只改元数据时，`files` 数组才可以为空。

## 编写规则

- 写替换版 `main.ts` 之前，先读 [着色器源码编写指南](references/authoring.md)。它包含必需的模块结构、WebGPU 生命周期、支持的参数结构、效果/填充的透明度规则，以及 WGSL 出错排查清单。
- 动画元数据要和源码一致。如果 `main.ts` 读取了 `frame.time`、`frame.deltaTime` 或 `frame.frame`，设 `metadata.isAnimated: true`；如果读取了 `frame.mousePosition`，设 `metadata.usesMouse: true`。去掉最后一处这类用法时，把对应的值设为 `false`。虽然 `features.json` 这个固定的配置文件不能直接替换，`update_shader` 会把这些元数据字段写进去。
- 动画优先用 `frame.time`，这样跳帧不会改变结果。它是一个以毫秒为单位的绝对时钟；需要时用 `Number(frame.time) * 0.001` 换算成秒。
- 用户很可能针对每个图层去调的数值，做成控件；实现细节就写死。
- 数值范围要有上下限，默认值要在视觉上有用。
- 对于效果，要有意识地采样输入图像。对于填充，不要假定有输入图像。
- `update_shader` 只要没返回错误，就当作成功。如果返回了版本号就记下来；成功的返回结果里也可能没有版本号。
- 遇到构建错误时，根据返回的编译器输出，对源码做最小的修正，然后重试一次。如果还是失败，就把错误报告出来，而不是一遍遍重写着色器。
- 如果工具报告动画或鼠标输入不可用，就把它当作最终的功能限制：不要重试，也不要想办法绕过。改为提议编写一个静态着色器，它暴露出来的属性可以在 Motion 模式里打关键帧。

## 完成

报告着色器的名字、种类和 id，如果有返回版本号也一并报告。简短说明加了哪些控件或行为。拼出并给出一个可以点击的网址，它会打开一个新的 Design 文件，里面已经准备好这个未发布的着色器可以试用；把着色器 id 原样填进 `try-tool-resource-content-id`。根据着色器种类设置 `try-tool-resource-type`：效果用 `gen_effect`，填充用 `gen_fill`。

`https://www.figma.com/file/new?try-tool-resource-content-id=<id>&try-tool-resource-type=<gen_effect|gen_fill>&type=design&mode=design`

给出这个新文件链接之后，问用户是否想改在一个现有的 Figma Design 文件里打开这个着色器。如果是，就用用户已经给过的文件网址，或者请用户提供一个，然后在那个网址上加上同样的 `try-tool-resource-content-id` 和确定好的 `try-tool-resource-type` 查询参数。绝不要猜文件网址。

把类型占位符换成唯一一个值；返回的网址里不要带尖括号或竖线。
