---
name: Figma与SwiftUI
description: "SwiftUI ↔ Figma 互相转换。只要用户提到 Swift、SwiftUI、iOS、iPhone 或 iPad 就使用——两个方向都算：把 Figma 设计转成 SwiftUI（设计 → 代码），或者把 SwiftUI 的视图/页面/token 推回 Figma 文件（代码 → 设计）。触发说法例如：'用 SwiftUI 实现这个 Figma 设计'、'用 Swift 做这个页面'、'把这个 SwiftUI 视图推到 Figma'、'在 Figma 文件里照搬我的 Swift 代码'，或者 Figma 网址和 `.swift` 文件 / `.xcodeproj` 一起出现的时候。它会把你引到对应方向的参考文档；走代码 → 设计这条路时，要和 `Figma插件基础` 一起加载。"
disable-model-invocation: false
---

> 翻译自 Figma 官方仓库 https://github.com/figma/mcp-server-guide （skills/figma-swiftui，commit f278942，对应 Cursor 插件编号 657）的 `figma-swiftui` skill，原作者 Figma，许可证：未注明许可证（仓库里没有找到 LICENSE 文件），仅供自用。
> 说明：参考文件 `references/` 里的两个文件（约 56 KB）太大，保留英文原文。链接里指向的其他 skill（`Figma插件基础`、`Figma搭建页面`、`Figma设计系统` 等）已经换成中文名，链接也指向对应的中文名文件夹。
> 英文名备份：s-figma-swiftui

# Figma ↔ SwiftUI

Figma 设计和 SwiftUI 代码之间的双向转换。这个文件只是一个“路由”（指路牌）——真正的指导写在下面的参考文档里。

## 选择方向

| 方向 | 什么时候 | 参考文档 |
|---|---|---|
| **设计 → 代码** | 用户想根据 Figma 文件/画框，在自己的 iOS 项目里写出 SwiftUI | [references/design-to-code.md](references/design-to-code.md) |
| **代码 → 设计** | 用户想把 SwiftUI 的视图/页面/token 推进 Figma 文件 | [references/code-to-design.md](references/code-to-design.md) |

如果请求不明确——Figma 网址和 `.swift` 文件都有，又没有动词说清楚——先问用户是哪个方向，再加载参考文档。

## 共同背景（两个方向都适用）

不管哪个方向，下面这些都成立；各方向的参考文档默认你已经知道这些。

1. **`get_design_context` 是读取 Figma 的工具。** 传入 `clientLanguages: "swift"` 和 `clientFrameworks: "swiftui"`，让返回结果以 Swift 的角度来写。网址 → 工具参数：`figma.com/design/:fileKey/:fileName?node-id=:nodeId` → 用 `fileKey`，把 `nodeId` 里的 `-` 换成 `:`。对于 `figma.com/design/:fileKey/branch/:branchKey/:fileName`，把 `branchKey` 当作 `fileKey` 用。
2. **`get_design_context` 输出里的 React+Tailwind 代码只是结构参考，不能照抄。** 它只是近似地还原画面。绝不要把 `position: absolute` / 按像素定位的画框 / `mix-blend-mode` 叠层，逐字翻成 SwiftUI 或 Figma——两个方向上，截图才是标准答案。
3. **iOS HIG（苹果人机界面指南）里的语义颜色是 token，不是十六进制色值。** `var(--backgrounds/primary, …)`、`var(--labels/secondary, …)`、`var(--separators/non-opaque, …)` 等，在 SwiftUI 里对应 `Color(.systemBackground)`、`Color.secondary`、`Color(.separator)`，在 Figma 里对应某个语义变量集合里的变量。保留这种对应关系；丢掉写死的 RGBA 值。
4. **SF Symbols（苹果的系统图标）在两个方向上都按名字来回对应——绝不按字符编码。** 设计 → 代码：`get_design_context` 会在返回结果里把 Figma 中的 SF Symbol 字形替换回 `<SFSymbol>{Image(systemName: "...")}</SFSymbol>` 这样的包装。原样使用这些名字。代码 → 设计：在 `use_figma` 里调用 `figma.util.getSfSymbolCharacter(name)`，把图标名转换成对应的字符——绝不要手动去查字符编码。
5. **认出背后的 iOS 常见模式，而不是只看节点/视图的字面名字。** 同样的模式在两个方向上反复出现：大标题 + 返回箭头 + 右侧操作 = `NavigationStack` 的界面框架；底部一排“图标+文字” = `TabView`；一行行等高、左右带装饰的重复行 = `List`。去对应这些系统模式，而不是用基础元素从头拼出来。
6. **代码 → 设计时，`use_figma` 就是 API。** 在任何 `use_figma` 调用之前，一定要先加载 [`Figma插件基础`](../Figma插件基础/SKILL.md)。如果任务是做一整个页面，还要加载 [`Figma搭建页面`](../Figma搭建页面/SKILL.md)；如果涉及做组件或设计系统，还要加载 [`Figma设计系统`](../Figma设计系统/SKILL.md)。

## 参考文档

| 文档 | 什么时候加载 |
|---|---|
| [references/design-to-code.md](references/design-to-code.md) | 把 Figma 设计/画框转成 SwiftUI |
| [references/code-to-design.md](references/code-to-design.md) | 把 SwiftUI 视图/页面/token 推进 Figma |
