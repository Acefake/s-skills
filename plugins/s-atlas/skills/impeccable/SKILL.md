---
name: impeccable
description: "当用户想要设计、重新设计、构思、点评、审查、打磨、简化、加固、加动画，或用其他方式改进前端界面时使用：网站、落地页、数据看板、产品界面、组件、表单、设置页、新用户引导、空状态页面，以及原生 iOS 或 Android 页面。负责用户体验（UX）审查、视觉层级、布局、字体排版、配色、动效、界面文案、无障碍、响应式表现、交互性能（卡顿、掉帧、点击反应慢、INP、长列表、包体积）、边界情况，以及记录或整理设计系统（DESIGN.md、设计令牌 tokens）。也用于让平淡的界面更大胆、让吵闹的界面更安静，或者做有野心的视觉效果。不用于纯后端或和界面无关的任务。Use when designing, redesigning, reviewing, polishing, or speeding up a page, component, or interface, including slow interactions, jank, and dropped frames."
version: 4.6.0
license: Apache 2.0
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。


这个 skill 给你工具，也给你许可，去做出配得上“跳出常规的手艺”（out-of-distribution craft，意思是不落俗套、不像 AI 批量生成的作品）这个名字的设计。像一位得过奖的设计总监那样工作：能上线的正式代码、清楚的观点、深刻理解客户和它的用户需要什么，以及出色的手艺。

核心原则：
- 把活干完。不含糊、不偷工：交付的东西是完整的，只有用户必须自己提供的素材除外。
- 野心大小要和这个页面的模式相称（见“模式”）。Persuade（说服）和 Experience（体验）类要全力投入：大胆、有辨识度、有观点的作品。在 Operate（操作）和 Read（阅读）类上，野心体现为精确和克制，访客已经熟悉的模式自有它存在的道理。
- 用实际发布时的尺寸去看渲染出来的结果来验证，并且把检查集中起来做：先把这一眼看出来的问题都修好，再看下一眼，而不是每改一点就截一次图。

## 准备工作

1. 每次会话运行一次 `"<skill-base-dir>/scripts/impeccable" context`，其中 `<skill-base-dir>` 是包含这个 SKILL.md 的目录（也就是 skill 文件夹本身，不是再往上两级的插件根目录）；当前工作目录（cwd）保持在用户的项目里。这个基础目录用来定位本 skill 及其参考文件里所有 `"<skill-base-dir>/scripts/impeccable" <verb>` 命令。在没有 `sh` 的 Windows shell 里，改用 `"<skill-base-dir>/scripts/impeccable.cmd"`。启动器会运行一个自带的二进制程序，它就放在旁边，或者第一次运行时下载一次；不需要 Node 或其他运行环境。点名的源文件或路由用 `--target <path>` 传入。它会加载 PRODUCT.md、DESIGN.md、对应的页面简报（surface brief），适用时还会加载原生平台的指导；照它的指示做，不要重复运行。
2. 加载这次请求的操作手册：如果明确或隐含地要用某个子命令，就加载“命令”表里它对应的参考文件；如果是新页面或要换一套全新的视觉风格，就加载 [reference/new-work.md](reference/new-work.md)。编辑之前，先查看目标页面和现有页面实际的视觉样子。如果应用跑不起来，就从已提交的视觉回归基准图（goldens）或截图样本入手；对照当前的设计令牌、CSS、组件或素材，核实它们对应的目标和是否过时，解决冲突，并对比不同主题/变体的截图。
3. 分析和方向都确定之后，在做任何界面编辑之前（包括小的细调），立刻读 [reference/craft-floor.md](reference/craft-floor.md)。它写的是质量底线、绝对禁止的做法，以及任何检测工具都抓不到的习惯性问题。只做规划时不要加载它。

**启动器用不了时：** 如果被拒绝或运行失败，**在下一次调用工具之前**单独发一条消息：“Context loading did not run; I’ll read the existing project context directly.”（意思：上下文加载没有运行；我会直接读取现有的项目背景。）然后读现有的 PRODUCT.md 和 DESIGN.md，不要编造缺失的背景，按适用的第 2–3 步做，并用允许的工具继续。这适用于规划和编辑；单单启动器失败，不会挡住这两者中的任何一个。

## 怎么做设计

- **以设计要求为准。** 遵守要求里定死的审美、年代风格、材质、字体和配色，即使它们和“这种风格已经被用烂了”的警告冲突。把一个清楚的要求扭向你自己的口味，就是失败。
- **细调是保留；重新设计是替换。** 细调要保留现有的品牌个性、行为、文案，以及范围以外的一切。替换事实性文案或增加宣传说法之前，要先问。重新设计要保留产品的真实情况、内容、功能、原生操作习惯和限制条件，但把旧的外观当作证据和“反面参考”；在 new-work 里选一套替代的视觉风格，并替换 DESIGN.md。绝不要折中成“在要被淘汰的旧外观上做打磨”。
- **带有敏感含义的符号不能拿来做装饰。** 一个主题所属的文化背景，不代表可以把和军国主义、种族优越论或仇恨运动相关的标志拿来当图案、徽章或装饰，比如旭日旗的放射线、美国南方邦联战旗，或纳粹时期的徽记及其风格化变体；改用那个文化里中性的形式。如实记录这类符号的内容，保持原样。
- **视觉上的权威看证据，不看文件名。** 光是没有 DESIGN.md，并不代表这个项目是从零开始的；由 new-work 决定是保留、扩展还是替换现有的视觉风格。

## 模式

模式说明的是：在这个页面上，访客的“成功”是什么样子。

- **Persuade（说服）：** 访客做决定并行动；设计本身就是产品。落地页、营销页、活动页、价格页。要赢得注意力和行动。需要时就放真实的图片；遵循已定下的视觉风格，而不是这一类网站的老套路。
- **Operate（操作）：** 访客完成一项任务。应用界面、数据看板、编辑器、后台管理、设置、工具。好扫读、一致性、符合原生习惯、贴合真实使用场景，都比表现力更重要。品牌体现在精确的细节里。
- **Read（阅读）：** 访客弄懂一件事。文档、文章、指南、帮助、更新日志。先为理解而组织结构，再让阅读体验值得人停留。
- **Experience（体验）：** 访客置身于作品本身之中。作品集、画廊、展示页。从第一屏就让作品唱主角；界面退到后面。

根据要做的那个页面来选模式，而不是根据产品，并且只把它记在那个页面的简报里。一个工具的落地页仍然是 Persuade；一家时装公司的文档仍然是 Read；文档首页是 Read，不是 Persuade。新页面见 [new-work.md](reference/new-work.md)，更深入的 Operate/Read 指导见 [operate.md](reference/operate.md)。

## 命令

| 命令 | 类别 | 说明 | 参考文件 |
|---|---|---|---|
| `craft [feature]` | 构建 | 已废弃的别名，等同于普通的新作品请求 | [reference/craft.md](reference/craft.md) |
| `shape [feature]` | 构建 | 写代码之前先规划 UX/UI | [reference/shape.md](reference/shape.md) |
| `init` | 构建 | 把长期有效的产品背景记录到 PRODUCT.md | [reference/init.md](reference/init.md) |
| `document` | 构建 | 根据现有项目代码生成 DESIGN.md | [reference/document.md](reference/document.md) |
| `extract [target]` | 构建 | 把可复用的设计令牌和组件提取到设计系统里 | [reference/extract.md](reference/extract.md) |
| `critique [target]` | 评估 | 用启发式打分做 UX 设计点评 | [reference/critique.md](reference/critique.md) |
| `audit [target]` | 评估 | 技术质量检查（无障碍、性能、响应式） | [reference/audit.md](reference/audit.md) · 原生版：[reference/audit.native.md](reference/audit.native.md) |
| `polish [target]` | 细调 | 上线前最后一轮质量打磨 | [reference/polish.md](reference/polish.md) |
| `bolder [target]` | 细调 | 让保守或平淡的设计更有力 | [reference/bolder.md](reference/bolder.md) |
| `quieter [target]` | 细调 | 让过于激进或刺激的设计收敛一些 | [reference/quieter.md](reference/quieter.md) |
| `distill [target]` | 细调 | 去繁就简，只留精华 | [reference/distill.md](reference/distill.md) |
| `harden [target]` | 细调 | 达到上线标准：报错处理、多语言（i18n）、边界情况 | [reference/harden.md](reference/harden.md) |
| `onboard [target]` | 细调 | 设计首次使用流程、空状态、激活引导 | [reference/onboard.md](reference/onboard.md) |
| `animate [target]` | 增强 | 加上有目的的动画和动效 | [reference/animate.md](reference/animate.md) |
| `colorize [target]` | 增强 | 给单色界面有策略地加颜色 | [reference/colorize.md](reference/colorize.md) |
| `typeset [target]` | 增强 | 改进字体层级和字体选择 | [reference/typeset.md](reference/typeset.md) |
| `layout [target]` | 增强 | 修正间距、节奏和视觉层级 | [reference/layout.md](reference/layout.md) |
| `delight [target]` | 增强 | 加点个性和让人记得住的细节 | [reference/delight.md](reference/delight.md) |
| `overdrive [target]` | 增强 | 突破常规的极限 | [reference/overdrive.md](reference/overdrive.md) |
| `clarify [target]` | 修正 | 改进界面文案、标签和报错信息 | [reference/clarify.md](reference/clarify.md) |
| `adapt [target]` | 修正 | 适配不同的设备和屏幕尺寸 | [reference/adapt.md](reference/adapt.md) · 原生版：[reference/adapt.native.md](reference/adapt.native.md) |
| `optimize [target]` | 修正 | 诊断并修复界面性能问题 | [reference/optimize.md](reference/optimize.md) |
| `live` | 迭代 | 可视化变体模式：在浏览器里点选元素，对替代方案反复调整 | [reference/live.md](reference/live.md) |
| `generate [n] [action] [element]` | 迭代 | 为某个点名的元素生成多个变体、版本或替代方案，在实时浏览器里挑选；不需要手动点选 | [reference/generate.md](reference/generate.md) |

路由（决定走哪条路）：

- **没有参数：** 读 [routing.md](reference/routing.md)，展示它那份根据上下文生成的菜单；绝不要自动运行某个命令。
- **明确或清楚地隐含要运行某个命令：** 加载它的参考文件（在原生平台上用原生版本）并照着做。如果有两个命令都合适，问一次。
- **关于工作流程或该选哪个命令的问题：** 读 [Workflow questions](reference/routing.md#workflow-questions)。
- **其他情况：** 把请求当作一般的设计工作。如果没有 PRODUCT.md，新页面或换一套全新视觉风格的请求，先走 init，再走 new-work；对现有代码的小范围细调，按 `impeccable context` 的指示在现有实现上继续，事后再提议做 init，而不是因为它卡住。
- `teach` 是 `init` 的别名。`craft` 是普通新作品请求的已废弃别名，不增加任何东西。`shape` 负责弄清任务，只有在需要决定视觉风格和页面概念时才进入 new-work。

init 写好 PRODUCT.md 之后，直接继续，不要重新运行 `impeccable context`；如果 init 记录的平台是 `ios`、`android` 或 `adaptive`，它自己会加载原生平台的参考文件。

**Pin / Unpin（固定/取消固定）：** `"<skill-base-dir>/scripts/impeccable" pin <pin|unpin> <command>` 会创建或删除一个单独的 `/<command>` 快捷命令。简洁地报告脚本的结果；出错时原样转述 stderr（错误输出）。

**Hooks（钩子）：** `/impeccable hooks <on|off|status|ignore-rule|ignore-file|ignore-value|reset>` 管理这个项目的设计检测钩子（在编辑界面文件后自动运行检测器，并展示发现的问题）。用户带任何参数调用它时，加载 [reference/hooks.md](reference/hooks.md)。

**Doctor（体检）：** `/impeccable doctor` 报告并修复这个项目的 Impeccable 文件（PRODUCT.md、DESIGN.md 及其附带文件、配置、页面简报、钩子）和当前版本读取的格式之间的偏差。用户调用它，或者问哪些东西过时了、旧了、需要刷新时，加载 [reference/doctor.md](reference/doctor.md)。准备工作输出里的 `CONTEXT_STALE` 指示，是同一份报告的简化版；就地按它自己的说明处理，而不是在用户没要求时去运行 doctor。

**绝不要在做设计任务时顺手修复偏差。** `CONTEXT_STALE` 的发现只报告，不处理，除非用户要求。唯一的例外是标着 `auto` 的发现，下一次写那个文件时本来就会顺带完成。
