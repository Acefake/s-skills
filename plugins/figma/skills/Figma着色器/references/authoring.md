# 着色器源码编写指南

> （本文件是 `Figma着色器` 的参考文件，翻译自 Figma 官方仓库 https://github.com/figma/mcp-server-guide 的 `skills/figma-shaders/references/authoring.md`，许可证：未注明许可证，仅供自用。代码块保持原样；目录里的链接锚点沿用原文英文标题，在中文标题下可能跳不准。）

当你要写出完整的替换版 `main.ts`，并以 `{ path: "main.ts", content: "..." }` 的形式传给 `update_shader` 时，用这份参考。这个 MCP 流程不能直接替换 `features.json`，但 `update_shader.metadata.isAnimated` 和 `update_shader.metadata.usesMouse` 会更新它的能力字段。

## 目录

- [写之前先规划](#plan-before-writing)
- [必需的模块约定](#required-module-contract)
- [运行时生命周期](#runtime-lifecycle)
- [动画和鼠标输入](#animation-and-mouse-input)
- [WebGPU 常用写法](#webgpu-patterns)
- [控件和参数](#controls-and-parameters)
- [效果和填充的约定](#effect-and-fill-contracts)
- [WGSL 规则](#wgsl-rules)
- [构建前检查清单](#pre-build-checklist)

## 写之前先规划

写代码之前，把下面这些一起定好：

1. 种类：`effect` 或 `fill`。
2. 可见的控件：名字、类型、默认值、范围、单位，以及哪些值保持写死。
3. 能力：源码是否读取时间或鼠标输入，以及因此需要哪些元数据开关。
4. GPU 资源：着色器模块、缓冲区（buffer）、采样器、纹理、布局和渲染通道（pass）。
5. 绑定：每一个 WGSL 绑定都必须和 JavaScript 里的 bind group 对得上。
6. uniform（统一变量）布局：字段顺序、填充对齐和总字节数。
7. 透明度约定：效果用预乘透明度（premultiplied），填充用直通透明度（straight）。

在控件、uniform、WGSL 绑定和 JavaScript 资源都对齐之前，不要动笔。

## 必需的模块约定

写出合法的 TypeScript。构建过程会在进程内运行 TypeScript 和 ESLint，所以可以用类型标注和普通的函数内声明。

```javascript
import { defineProperties } from "figma:shaders"

export default function Effect() {}

export function setup(device, frame) {
  // Compile shader modules and allocate format-independent GPU resources.
  // Store persistent values on frame.state.
}

export function render(device, frame) {
  // Read frame.params, write uniforms, encode passes, and submit.
}

defineProperties(Effect, {
  // User-editable controls.
})
```

（代码注释意思：setup 里编译着色器模块、分配和格式无关的 GPU 资源，持久的值存在 frame.state 上；render 里读取 frame.params、写入 uniform、编码渲染通道并提交；defineProperties 里是用户可编辑的控件。）

规则：

- 唯一允许的 import 是从 `figma:shaders` 导入 `defineProperties`。
- `defineProperties` 放在模块顶层。
- 不要在模块顶层声明 `var`、`let` 或 `const`；运行时会去掉顶层声明，构建也会拒绝它们。把运行时常量放在 `setup`/`render` 里面，或者放在 `frame.state` 上。
- 着色器入口函数叫 `vs_main` 和 `fs_main`；计算着色器按惯例用 `main`。
- 每一个完整的 WGSL 模块字符串，第一条非空声明必须是 `diagnostic(off,derivative_uniformity);`。
- uniform 缓冲区的大小是 16 字节的倍数。
- 用 `queue.writeBuffer` 写入的缓冲区，需要 `GPUBufferUsage.COPY_DST`。
- 用 `writeTexture` 写入的纹理，需要 `GPUTextureUsage.COPY_DST`。
- 在 `render()` 里按需创建渲染管线，并按 `frame.output.format` 缓存。绝不要写死 `rgba8unorm`。

## 运行时生命周期

`device` 是一个真正的 `GPUDevice`。`frame` 提供：

| 字段 | 含义 |
| --- | --- |
| `frame.input` | 输入的 `GPUTexture`，或 `null`。效果可以采样它；填充绝不能。 |
| `frame.output` | 目标纹理。渲染到 `frame.output.createView()` 里。 |
| `frame.params` | 由 `defineProperties` 声明的值。 |
| `frame.state` | 持久的、可修改的存放处，用来放模块、缓冲区、采样器、布局和管线。 |
| `frame.time` | 以毫秒为单位的绝对动画时钟。 |
| `frame.deltaTime` | 距上一帧渲染过去的毫秒数。 |
| `frame.frame` | 从零开始的已渲染帧计数。 |
| `frame.mousePosition` | 图层内的鼠标位置。 |

尺寸用 `frame.output.width` 和 `frame.output.height`。和格式无关的资源，在 `setup` 里分配一次。实时参数写进缓冲区、依赖输入的 bind group 在 `render` 里创建，因为输入纹理可能会被重新创建。

可用的 JavaScript 包括 WebGPU 枚举、`Float32Array`、整数类型数组、`Math`、集合、JSON 和 promise。没有 DOM、`window`、`document`、`navigator`、`fetch`、console、定时器、动画帧、微任务、`Float64Array` 或 `Float16Array`。在 JavaScript 里用 `Math.sin`、`Math.max` 这类写法——不要用 WGSL 风格的裸数学函数。

## 动画和鼠标输入

动画和鼠标驱动的着色器，要求源码和配置元数据一致：

- 如果源码读取了 `frame.time`、`frame.deltaTime` 或 `frame.frame`，给 `update_shader` 传 `metadata: { isAnimated: true }`。
- 如果源码读取了 `frame.mousePosition`，传 `metadata: { usesMouse: true }`。
- 去掉某种能力的最后一处用法时，把它的元数据值设为 `false`。不写元数据，就保留配置里原来的值。

优先用绝对的 `frame.time` 时钟，而不是在 `frame.state` 里累加 `frame.deltaTime`；渲染跳帧时，绝对时间依然稳定。

`frame.mousePosition.x` 和 `.y` 是图层内的像素坐标。如果画面应该随图层一起缩放，就用输出尺寸把坐标归一化。

## WebGPU 常用写法

优先用一个六个顶点的全屏四边形，顶点数据交错存放裁剪空间位置和 UV 坐标：

```javascript
frame.state.quad = device.createBuffer({
  size: 6 * 4 * 4,
  usage: GPUBufferUsage.VERTEX,
  mappedAtCreation: true,
})
new Float32Array(frame.state.quad.getMappedRange()).set([
  -1, -1, 0, 1,  1, -1, 1, 1,  -1, 1, 0, 0,
  -1, 1, 0, 0,   1, -1, 1, 1,   1, 1, 1, 0,
])
frame.state.quad.unmap()
```

它的顶点布局是：

```javascript
buffers: [{
  arrayStride: 16,
  attributes: [
    { shaderLocation: 0, format: "float32x2", offset: 0 },
    { shaderLocation: 1, format: "float32x2", offset: 8 },
  ],
}]
```

只在输出格式变化时才创建渲染管线：

```javascript
if (frame.state.pipelineFormat !== frame.output.format) {
  frame.state.pipeline = device.createRenderPipeline({
    layout: "auto",
    vertex: {
      module: frame.state.shaderModule,
      entryPoint: "vs_main",
      buffers: [{
        arrayStride: 16,
        attributes: [
          { shaderLocation: 0, format: "float32x2", offset: 0 },
          { shaderLocation: 1, format: "float32x2", offset: 8 },
        ],
      }],
    },
    fragment: {
      module: frame.state.shaderModule,
      entryPoint: "fs_main",
      targets: [{ format: frame.output.format }],
    },
    primitive: { topology: "triangle-list" },
  })
  frame.state.pipelineFormat = frame.output.format
}
```

uniform 缓冲区只分配一次，每次渲染都写入。优先用 `vec4f` 槽位，让填充对齐一目了然：

```javascript
frame.state.uniforms = device.createBuffer({
  size: 16,
  usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST,
})
device.queue.writeBuffer(
  frame.state.uniforms,
  0,
  new Float32Array([frame.params.amount, frame.output.width, frame.output.height, 0]),
)
```

每次渲染都创建包含 `frame.input` 的 bind group。如果计算通道的结果要给渲染通道用，就在同一个命令编码器上把两个通道都编码好，再提交。

## 控件和参数

把用户会针对每个图层去调的值暴露出来。实现细节写死在 `setup` 或 `render` 里；不要自己发明模块顶层的常量。

| 类型 | 用途 | 关键结构 |
| --- | --- | --- |
| `boolean` | 开/关行为 | `{ type: "boolean", defaultValue: true }` |
| `string` | 只用于真正的自由文字 | `{ type: "string", defaultValue: "Hello" }` |
| `number` 滑块 | 有范围的连续值 | 包含 `min`、`max`、`step`、`control: "slider"` |
| `number` 输入框 | 自由的数值 | `control: "input"`，可选 `unit` |
| 数字下拉选择 | 模式/预设 | `control: "select"`，选项值用数字 `0,1,2...` |
| `color` | RGBA 控件 | 各通道是归一化的 `0..1` |
| `gradient` | 二到八个色标 | 位置按顺序，范围 `0..1`；打包成固定八个色标的 uniform 加一个数量 |
| `point` | 中心/原点 | 优先用 `mode: "canvas_and_ui"`、`unit: "%"` |
| `point-radius` | 中心加半径 | 半径百分比相对于图层较短的那条边 |
| `point-point-line` | 两个端点 | 需要随尺寸变化的几何形状，优先用百分比单位 |
| `point-angle-radius` | 极坐标控件 | 角度单位是度 |
| `color-point` | 位置和颜色绑在一起 | 一个视觉元素时，优先用它，而不是分开的两个控件 |

下拉菜单必须是数字选择。不要把 string 和 `control: "select"` 一起用；编辑几次后它会变得不稳定。

百分比位置是相对于图层的，用于 UV 时要除以 100。像素值是图层内的绝对像素，不会随图层缩放而变化。

## 效果和填充的约定

### 效果

- 在调用 `createView()` 之前，先判断 `frame.input == null` 的情况。
- 输入和输出都用预乘透明度。改变不透明度时，要把整个 RGBA 值一起缩放，而不只是 alpha。
- 采样偏移后的 UV 之前，先把它限制在范围内，除非你有意让越界读取变成透明。

```wgsl
let opacity = 0.5;
color *= opacity;
```

### 填充

- 不要绑定或采样 `frame.input`。
- 输出用直通透明度。改变不透明度时，只缩放 alpha 通道。

```wgsl
let opacity = 0.5;
color.a *= opacity;
```

## WGSL 规则

- `let` 是不可变的；会被修改的值和累加器用 `var`。
- 不要在函数里用 `const`。
- 不要给多个分量的 swizzle（如 `v.xy`）赋值。整个向量重新替换。
- 数组字面量用 `array(v1, v2)`，不是 `[v1, v2]`。
- 矩阵按列来构造。
- `select(falseValue, trueValue, condition)` 的参数顺序和 C 语言三元运算符相反。
- 避免保留字或容易混淆的名字，比如 `texture`、`sampler`、`sample`、`min`、`max`、`meta` 和 WGSL 关键字。
- 用 WGSL 内置变量，比如 `@builtin(position)`；绝不要用 GLSL 的 `gl_*` 名字。
- 对归一化 UV 做带过滤的采样用 `textureSample`，按整数像素读取用 `textureLoad`。
- `textureSample`、导数和 gather 操作必须在统一的控制流里执行（所有像素走同一分支）。如果某个分支里需要采样，就先采样再用 `select`，或者有意地用 `textureSampleLevel(..., 0.0)`/`textureLoad`。
- 优先用固定次数的循环。避免在隐式导数采样周围使用逐像素变化的循环次数或 break。

## 构建前检查清单

在用 `files: [{ path: "main.ts", content: source }]` 调用 `update_shader` 之前，检查：

1. 种类和现有资源一致。
2. 源码是完整的模块，不是差异补丁。
3. `metadata.isAnimated` 和是否用到 `frame.time`、`frame.deltaTime` 或 `frame.frame` 一致。
4. `metadata.usesMouse` 和是否用到 `frame.mousePosition` 一致。
5. 时间值按毫秒处理，并且最好来自绝对时钟。
6. 没有顶层的运行时声明。
7. 绑定和 bind group 条目完全对得上。
8. uniform 的大小和写入一致，并且按 16 字节对齐。
9. 管线跟踪 `frame.output.format`。
10. 效果会判断并采样输入；填充绝不绑定输入。
11. 透明度处理和种类一致。
12. WGSL 以 diagnostic 指令开头，并使用合法的入口函数名。
13. 没有被修改的 `let`、swizzle 赋值、方括号数组字面量、GLSL 内置变量，也没有在非统一控制流里做隐式导数采样。

遇到构建错误时，用最小的改动修好那个具体的编译错误，然后重试一次。
