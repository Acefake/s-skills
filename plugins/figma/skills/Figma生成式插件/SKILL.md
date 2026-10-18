---
name: Figma生成式插件
description: "**必须先做的前置步骤**——在调用 `create_generative_plugin` 或 `update_generative_plugin` 之前，先加载这个 skill。当用户要求新建、编写、修改、修复或扩展一个可重复使用的生成式 Figma 插件时使用。"
disable-model-invocation: false
---

> 翻译自 Figma 官方仓库 https://github.com/figma/mcp-server-guide （skills/figma-generative-plugins，commit f278942，对应 Cursor 插件编号 657）的 `figma-generative-plugins` skill，原作者 Figma，许可证：未注明许可证（仓库里没有找到 LICENSE 文件），仅供自用。
> 说明：工具名、文件名（`code.ts`、`ui.html`、`manifest.json`）和网址保持原样。参考文件 `references/authoring.md` 也已翻译成中文。
> 英文名备份：s-figma-generative-plugins

# 新建和更新生成式 Figma 插件

每次调用 `create_generative_plugin` 或 `update_generative_plugin` 之前，都要先加载这个 skill。对用户说话时，把做出来的东西叫“插件”。“生成式”这个词只是用来把这个账户插件库工具和其他插件系统区分开。

## 动手前检查

开始编写之前，确认请求适合这种插件：

- 插件运行在 Figma Design 编辑器里。
- 每个插件都必须为它的核心流程提供能用的界面。即使插件没有可调的输入项，也需要一个清楚的主操作按钮，以及有用的状态或校验提示。
- 绝不要把 API 密钥、OAuth 令牌、带签名的网址或其他秘密写进插件里。能访问插件的人都能读到它的源码。对于需要登录认证的集成，停下来，改为提供静态数据、不需要认证的公开接口，或者换一种架构。

## 新建流程

1. 弄清用户要的流程和有用的控件。只有当必需的输入或行为确实不明确时，才简短地问一个问题。
2. 确定 `planKey`。用户提供了就用用户的；否则调用 `whoami`。如果只有一个符合条件的套餐就自动用它；如果有几个差别明显的套餐，就请用户选。
3. 调用一次 `create_generative_plugin`，带上简短的名字、描述和 `planKey`。这会建出一个能运行的“画正方形”脚手架（初始模板），而不是用户要的最终插件。
4. 用返回的 `id` 调用 `get_generative_plugin`，然后读取每一个源文件 URI。这样你就清楚了脚手架的 manifest（插件配置文件）、界面消息约定和当前的 TypeScript 入口文件。
5. 用为用户需求完整编写的文件替换掉脚手架，实现所需的行为和界面。
6. 用返回的 `id` 调用 `update_generative_plugin`，带上一个 `files` 数组（里面是 `code.ts` 的完整替换内容；界面有变化时，再加上 `ui.html`），以及一条具体的 `commitMessage`（提交说明）。要改名字或描述时，用 `metadata`。

绝不要在 `create_generative_plugin` 之后就停下：必须把初始模板换成用户要的功能。

## 更新流程

1. 找到这个插件。需要时先调用 `list_generative_plugins`，再调用 `get_generative_plugin`。
2. 编辑之前，读取 get 工具返回的每一个源文件 URI。以这些文件为当前的准确版本。
3. 除非用户要求修改，否则保留现有的界面、控件、重新运行行为、校验和用户能看到的操作入口。
4. 调用 `update_generative_plugin`，为每一个改动过的现有文件提供完整的替换内容。入口文件用 `{ path: "code.ts", content: "..." }`，界面用 `{ path: "ui.html", content: "..." }`。没写到的文件会原样保留。

## 编写规则

- 在写替换文件之前，先读 [插件源码编写指南](references/authoring.md)。它讲了文件替换约定、界面/消息的生命周期、PropsKit 控件、动态页面兼容、字体、重新运行行为、限制工作量、几何定位，以及 Plugin API 的常见坑。
- 让插件的主操作一目了然，并且让无效的选择或输入状态能被看懂。
- `update_generative_plugin` 可以替换现有的 `code.ts` 和 `ui.html` 文件，但不能替换 `manifest.json`，也不能新建文件。在 `code.ts` 里保留 `figma.showUI(__html__, ...)`，当需要不同的控件时，替换 `ui.html`。
- 避免对画布做破坏性修改，除非这正是插件明确的目的，并且界面上说清楚了。
- 在异步工作和界面消息完成之前，不要关闭插件。
- `update_generative_plugin` 只要没返回错误，就当作成功。如果返回了版本号就记下来；成功的返回结果里也可能没有版本号。
- 遇到构建错误时，根据返回的编译器输出，对源码做最小的修正，然后重试一次。如果还是失败，就把错误报告出来，而不是一遍遍重写插件。

## 完成

报告插件的名字和 id，如果有返回版本号也一并报告，再简短描述它的界面和主操作。拼出并给出一个可以点击的网址，它会打开一个新的 Design 文件，里面已经准备好这个未发布的插件可以试用；把插件 id 原样填进 `try-tool-resource-content-id`：

`https://www.figma.com/file/new?try-tool-resource-content-id=<id>&try-tool-resource-type=gen_tool&type=design&mode=design`

给出这个新文件链接之后，问用户是否想改在一个现有的 Figma Design 文件里打开这个插件。如果是，就用用户已经给过的文件网址，或者请用户提供一个，然后在那个网址上加上同样的 `try-tool-resource-content-id` 和 `try-tool-resource-type` 查询参数。绝不要猜文件网址。
