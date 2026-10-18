# 插件源码编写指南

> （本文件是 `Figma生成式插件` 的参考文件，翻译自 Figma 官方仓库 https://github.com/figma/mcp-server-guide 的 `skills/figma-generative-plugins/references/authoring.md`，许可证：未注明许可证，仅供自用。代码块保持原样；目录里的链接锚点沿用原文英文标题，在中文标题下可能跳不准。）

当你要为 `update_generative_plugin` 写出完整的 `code.ts` 和 `ui.html` 替换内容时，用这份参考。

## 目录

- [部署边界](#deployment-boundary)
- [规划产品约定](#plan-the-product-contract)
- [入口文件和界面生命周期](#entrypoint-and-ui-lifecycle)
- [PropsKit 界面](#propskit-ui)
- [兼容动态页面的 Plugin API](#dynamic-page-compatible-plugin-api)
- [编写规则](#authoring-rules)
- [构建前检查清单](#pre-build-checklist)

## 部署边界

MCP 的更新接口接收一个 `files` 数组，里面是现有源文件的完整替换内容：

```json
[
  { "path": "code.ts", "content": "<complete TypeScript entrypoint>" },
  { "path": "ui.html", "content": "<complete plugin UI>" }
]
```

它可以替换 `code.ts` 和 `ui.html`。它不能替换 `manifest.json`，不能新建缺失的文件，也不接受差异补丁（diff）。没写到的文件会原样保留，所以只放改动过的文件。只改元数据的更新，可以用空的 `files` 数组，加上 `metadata.name` 和/或 `metadata.description`。

在 create/get 之后：

1. 读取 manifest、界面和当前入口文件的 URI。
2. 确认 manifest 的目标是 `editorType: ["figma"]`，包含能用的界面，并且使用动态页面访问方式。
3. 如果现有的界面消息约定适合用户要的流程，就保留它。
4. 需要不同的控件时，替换 `ui.html` 并更新 `code.ts`，让两边的消息约定一致。
5. 如果现有的 manifest 本身就不兼容，而用户要的行为又需要改它，就把这个限制说出来；`update_generative_plugin` 修不了它。

不要加入工具没法部署的 import、额外源文件、构建配置或依赖。

## 规划产品约定

写代码之前，先定下来：

- 主操作是什么，它是新建、转换还是检查图层。
- 必需的选择状态和输入状态。
- 界面控件、默认值、校验和状态提示文字。
- 从界面 → 沙盒（sandbox，插件里能调用 Figma 的那一侧）和从沙盒 → 界面发送的消息。
- 哪些操作可以重复做，哪些会关闭插件。
- 具体新建/修改哪些图层，放在哪里，选中什么，视口怎么变。
- 预计最大工作量，以及怎样限制它。
- 重新运行数据或轻量的保存偏好是否有用。

每个插件都需要能用的界面。即使是零参数的操作，也需要一个清楚的主按钮，加上有用的禁用/出错/成功提示。

## 入口文件和界面生命周期

只有沙盒这一侧能调用 `figma.*`。只有界面 iframe 这一侧能使用 DOM/浏览器 API。两边只能通过消息通信。

`code.ts` 负责调用 Plugin API，并用 `__html__` 加载单独的界面：

```ts
const PANEL_WIDTH = 280

type UiMessage =
  | { type: 'resize'; height: number }
  | { type: 'run'; count: number }

figma.showUI(__html__, { width: PANEL_WIDTH, height: 240 })

figma.ui.onmessage = async (message: UiMessage) => {
  if (message.type === 'resize') {
    figma.ui.resize(PANEL_WIDTH, Math.max(120, Math.min(900, Math.round(message.height))))
    return
  }
  if (message.type === 'run') {
    // Validate, mutate, report status. Close only for a genuinely one-shot flow.
  }
}
```

（代码注释意思：校验、修改、报告状态。只有真正一次性的流程才关闭插件。）

`ui.html` 负责 DOM，并向沙盒发送消息：

```html
<!doctype html>
<html>
<head>
  <script>
    try {
      window.localStorage.getItem('x')
    } catch (e) {
      const store = new Map()
      const shim = {
        getItem: (key) => store.has(key) ? store.get(key) : null,
        setItem: (key, value) => { store.set(key, String(value)) },
        removeItem: (key) => { store.delete(key) },
        clear: () => { store.clear() },
        key: (index) => Array.from(store.keys())[index] ?? null,
        get length() { return store.size },
      }
      Object.defineProperty(window, 'localStorage', { value: shim, configurable: true })
    }
  </script>
</head>
<body>
  <div id="plugin-root">
    <fig-content>
      <fig-field>
        <label>Count</label>
        <fig-input-number id="count" value="3" min="1" max="100"></fig-input-number>
      </fig-field>
    </fig-content>
    <fig-footer>
      <label id="status">Ready</label>
      <fig-button id="run" type="submit">Create layers</fig-button>
    </fig-footer>
  </div>
  <script>
    const post = (message) => parent.postMessage({ pluginMessage: message }, '*')
    document.getElementById('run').addEventListener('click', () => {
      post({ type: 'run', count: Number(document.getElementById('count').value) })
    })
    const root = document.getElementById('plugin-root')
    new ResizeObserver(() => {
      post({ type: 'resize', height: Math.ceil(root.getBoundingClientRect().height) })
    }).observe(root)
  </script>
</body>
</html>
```

在异步操作和消息完成之前，不要关闭插件。可以重复使用的面板就一直开着；只有在一次性操作完成后，或显示了终止性的错误后，才关闭。

## PropsKit 界面

有 PropsKit 的 `fig-*` 控件可用时，就用它们，而不是用原始的 HTML 对应元素。面板的结构是 `<fig-content>` 后面跟 `<fig-footer>`。

- 用 `<fig-field>` 包住控件，里面放一个 `<label>` 子元素。
- 用 `<fig-group name="…">` 把相关的控件分组。
- 状态和操作放在 `<fig-footer>` 里；选择/输入条件不满足时，禁用操作按钮。
- 标签、分组、状态、操作、通知和重新运行名称，都用句首大写（sentence case）。
- 当一个控件直接对应编辑器里的某个属性时，用 Figma 官方的属性叫法。
- 在提交时读取 `.value`，除非实时更新本身就是用户要的行为。
- 优先用 `change` 而不是 `input`，避免频繁折腾场景图（scenegraph）。对于颜色/填充选择器，要么在提交时读取，要么有意地两个事件都监听。

推荐的控件：

| 输入 | 控件 |
| --- | --- |
| 有范围的数字 | `<fig-slider text>` |
| 数字输入 | `<fig-input-number>` |
| 文字 | `<fig-input-text>`；长文字加 `multiline` |
| 颜色 | `<fig-input-color picker="figma-native">` |
| 渐变 | `<fig-input-gradient experimental="modern">` |
| 调色板 | `<fig-input-palette min="2" max="8">` |
| 开关（是/否） | `<fig-switch>` |
| 少量选项 | `<fig-options options="A, B, C">` |
| 大量选项 | `<fig-dropdown>`，直接放 `<option>` 子元素 |
| 二维坐标点 | `<fig-joystick fields>` |
| 上传图片 | `<fig-image upload>` |
| 上传其他文件 | `<fig-input-file>` |
| 主操作 | 放在 `<fig-footer>` 里的 `<fig-button type="submit">` |

PropsKit 专用的规则：

- `<fig-options>` 接收用逗号分隔的选项；不要加子选项。
- `<fig-dropdown>` 直接接收 `<option>` 子元素；绝不要在里面套一个 HTML `<select>`。
- `<fig-joystick>` 的值是 `"X% Y%"` 这样的字符串。
- 颜色值是十六进制；在创建填充（paint）之前，把各通道换算成 `0..1` 的归一化数值。
- PropsKit 渐变色标的位置/不透明度是 `0..100`；Plugin API 里的值是 `0..1`。
- 能预览的图片用 `<fig-image upload>`，CSV/JSON/文本/二进制文件用 `<fig-input-file>`。
- 自定义元素的样式用 Figma 的 token（`--figma-color-*`、`--spacer-*`、`--font-family`），不要用固定颜色。

## 兼容动态页面的 Plugin API

新建出来的脚手架已经使用动态页面访问方式（页面按需加载）。源码要保持兼容：

- 优先使用 `getNodeByIdAsync`、`getStyleByIdAsync`、本地样式的异步读取方法、变量的异步读取方法、`getMainComponentAsync` 和 `getInstancesAsync`。
- 使用异步设置方法，比如 `setFillStyleIdAsync`、`setStrokeStyleIdAsync`、`setEffectStyleIdAsync`、`setGridStyleIdAsync`、`setTextStyleIdAsync`、`setReactionsAsync` 和 `setVectorNetworkAsync`。
- `figma.currentPage` 是已经加载好的。在遍历另一个页面的子节点之前，先调用 `await page.loadAsync()`。
- 切换页面用 `await figma.setCurrentPageAsync(page)`，绝不要直接赋值。
- 只有真正针对整个文档的操作才加载所有页面；那样可能又慢又占内存。
- 处理好每一个 promise。避免 `forEach(async ...)`；用 `for...of` 或有数量限制的 `Promise.all`。
- 不要用 `as any` 或计算属性访问的方式绕过已弃用的 API。

如果拿到的 manifest 没有动态页面访问方式，源码仍然照兼容的 API 来写，但不要声称 manifest 已经迁移了——MCP 更新改不了它。

## 编写规则

### 字体

在修改文字字符或依赖字体的属性之前，先调用 `await figma.loadFontAsync(fontName)`。混合字体的情况，要检查各个文字范围并加载每一种需要的字体。不要假定非默认字体一定存在；字体不可用时，给出有用的状态/错误提示。

### 填充和不可变数组

- 填充（fills）、描边（strokes）和效果（effects）都是不可变数组：先复制、再修改、再重新赋值。
- 颜色用 `0..1` 归一化的 RGB。填充的透明度放在 `opacity` 里。
- `setBoundVariableForPaint` 返回一个新的填充；要接住它并重新赋值。
- 来自 PropsKit 的渐变值，需要转换成 Plugin API 的渐变类型和归一化的色标。

### 几何尺寸和摆放

- 用 `node.resize(width, height)` 改尺寸；`width` 和 `height` 是只读的。
- `resize()` 可能会重置自动布局的尺寸模式；改完后重新设回你想要的尺寸模式。
- 换父节点时会保留相对的 `x`/`y` 值。在 `appendChild`、`insertChild` 或编组到新父节点之后，再设置坐标。
- 新建的顶层产出放在 `figma.viewport.center` 附近，不要放在页面原点。
- 只选中/显示有意义的结果。避免出乎意料地把视口从用户正在做的地方拉走。
- 图标用 `figma.createNodeFromSvg` 从 SVG 导入；不要用旋转的基础线条拼出来。

### 选择和校验

- 在修改之前，校验选中的数量和图层支持的能力。
- 用能力检查，比如 `'fills' in node`；给不支持的字段赋值会报错。
- 能禁用界面操作时就禁用，并在沙盒里再校验一次，因为面板显示之后选择可能会变。
- 保留无关的子节点和属性。只跟踪和更新插件自己产出的东西。
- 破坏性的行为要在界面和给用户看的文字里说清楚。

### 限制工作量

- 对用户提供的数量和尺寸设定上下限。
- 避免没有边界的遍历或两两比较的平方级工作量。
- 大型操作要分批处理，并发送进度/状态消息。
- 不要发需要认证的网络请求，也不要写进秘密。能访问的人都能读到源码。
- 只有当需求真的需要、并且接口允许浏览器访问时，才可以用不需要认证的公开接口。

### 重新运行和保存

每个插件都必须能重新运行。插件打开时调用 `figma.root.setRelaunchData(...)`，这样在什么都没选中时也能找到它。一次运行新建或修改了图层之后，还要把重新运行数据挂到受影响的最外层图层上——比如选中的父节点或新建的顶层画框——而不是挂到每个生成的子节点上。

只用插件数据保存小的、不敏感的偏好设置。不要保存上传的文件、凭据、根据旧选择得来的过期 ID，或破坏性操作的确认。给数据结构加版本号，并能容忍缺失或旧版本的数据。

## 构建前检查清单

在调用 `update_generative_plugin` 之前，检查：

1. 每个 `files` 条目都是现有 `code.ts` 或 `ui.html` 的完整替换内容。
2. 已经理解拿到的 manifest 的限制，没有暗含无法部署的 manifest 修改或新建文件。
3. 插件有能用的界面和清楚的主操作。
4. 界面和沙盒两边的消息类型完全一致。
5. 在合适的地方，两边都校验了输入和选择状态。
6. 每个异步 API 都 await 了，并遵守了动态页面的规则。
7. 修改文字之前已经加载了字体。
8. 填充数组是复制后重新赋值的，颜色是归一化的。
9. 换了父节点的/新建的产出有经过考虑的坐标和视口位置。
10. 工作量有限制，没有写进秘密。
11. 成功/出错/状态的反馈用户看得到，并且用的是“插件”和“图层”这样的词，而不是内部行话。
12. 插件按照实际的交互方式保持打开或关闭。

遇到构建错误时，用最小的改动修好报告的源码问题，然后重试一次。
