---
name: 代码导入Figma
description: 把本地的 HTML 或项目文件导入/上传到 Figma，选择做成可编辑的 Design 画框、可运行的 Code Layer（代码图层），还是独立的 Code 文件（也叫 Make），并修复导入后的预览。只在用户明确说要可编辑的 Design 图层、可运行的 Code Layer、独立的 Code/Make 文件，或者给出了作为导入目标的 Figma 文件 key/链接时使用。笼统的“写代码”或“做代码组件”请求，要先问清楚想要什么产出，才能用这个流程。
disable-model-invocation: false
---

> 翻译自 Figma 官方仓库 https://github.com/figma/mcp-server-guide （skills/figma-code-workflows，commit f278942，对应 Cursor 插件编号 657）的 `figma-code-workflows` skill，原作者 Figma，许可证：未注明许可证（仓库里没有找到 LICENSE 文件），仅供自用。
> 说明：工具名（`send_code_to_figma`、`generate_figma_design`、`html_to_figma` 等）、字段名保持原样；其他 skill 的名字已经换成中文名（如 `figma-generate-design` 写成 `Figma搭建页面`）。
> 英文名备份：s-figma-code-workflows

# 把项目导入 Figma

只有在用户明确要求某种 Figma 产出（独立的 Code/Make、可运行的 Code Layer，或可编辑的 Design 图层），或者给出了作为目标的 Figma 文件 key/链接时，才使用这个流程。笼统的“做一个代码项目”或“做一个代码组件”的请求，以及只是提到 Figma Code/Make 这些名字，都不算指明了产出。如果不清楚用户想要什么产出，就问用户是要本地代码还是 Figma 产出，然后等回答，再开始这个流程。

保护好用户的项目。每个工具的前提条件和参数，以它当前的说明和参数结构（schema）为准。

在几个主要阶段及时告诉用户进展：准备和验证项目、上传压缩包、在 Figma 里完成导入。出现待完成的导入、恢复工作和阻碍时随时报告；没有确认完成的阶段，不要说成已完成。

## 1. 选择产出和目标位置

先弄清用户想要的产出，然后按下表加载合适的 skill。如果产出不清楚，先问用户再继续。

| 输入 | 用户要的产出 | 下一步 |
| --- | --- | --- |
| 运行中的应用或静态 HTML | 没说——只说放进/导入 Figma | 问：**“要可编辑的设计图层，还是代码图层？”（原文："Editable design layers or a code layer?"）然后结束这一轮回复。** 等用户回答。 |
| 运行中的应用 | 可编辑的 Design 图层 | 加载 `Figma搭建页面`，然后在一个 Design 文件里调用 `generate_figma_design`。 |
| 静态 HTML | 可编辑的 Design 图层 | 在一个 Design 文件里调用 `html_to_figma`。 |
| 运行中的应用 | 可运行的 Code Layer 或独立的 Code/Make | 继续用这个 skill，调用 `send_code_to_figma`。 |
| 静态 HTML | 可运行的 Code Layer 或独立的 Code/Make | 继续用这个 skill，调用 `send_code_to_figma`。 |

即使 HTML 项目里的按钮都能用，只要用户没选产出，就仍然算不明确。一个 Design 链接只决定了目标位置，不决定产出。

在选择可运行的目标之前，先调用 `whoami`。只有当 `whoami.code_layers_enabled` 为 true 时，才选择或导入 Design 里的 Code Layer；否则用独立的 Code/Make，或者说明这个限制，并在更改用户明确给出的 Design 目标之前先问用户。

在套用“按页面数判断”的经验规则之前，先遵守用户明确说的“要代码图层”或“要独立文件”。可运行的代码配一个 Design 链接，就用 Code Layer。给的是独立 Code 链接，就用独立文件。如果没有目标位置，也没有明确选择代码图层/独立文件，就估算页面数：少于 10 个或不知道 → Code Layer；10 个或更多 → 独立文件。绝不要问用户要 Code Layer 还是独立文件，也不要让用户去数页面。在确定产出之后，明确的目标位置和链接优先。

用用户提供的文件网址。如果需要新文件，就用 `create_new_file`，带上选好的目标类型和用户选的套餐。

用户要代码图层但没给目标位置时，新建一个 Design 文件。

确认好的产出选择保持不变；新建文件之后，不要再让用户选一次。

对于可编辑的 Design 图层，按所选工具的说明来做：`generate_figma_design` 抓取运行中应用渲染出来的页面；`html_to_figma` 转换一个自带全部内容的静态 HTML 文档。检查生成的图层，并把 Design 链接给用户。只有可运行代码的产出才继续往下做。

## 2. 按导入工具的返回结果做

用选好的本地来源和目标位置，按 `send_code_to_figma` 当前的参数结构调用它。照着返回的准备和打包说明做；如果有要求，先保护好应用，并在上传前在本地验证。

对于准备、验证、上传、待完成的导入和配置恢复，都严格按照每次返回结果里的说明和返回的 `nextStep` 来做。先完成返回的前提条件再往下走，后续调用的参数要完整、原样传入。不要自己编一个缺失的恢复步骤。如果没有 `nextStep`，就按返回结果里的说明和工具当前的描述来做。

最后给出返回的文件/图层链接，只报告结果里已经确认的导入和预览情况。
