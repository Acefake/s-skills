# S 的中文技能市场

这个仓库是 S 自己的**插件市场**。插件市场就是一份目录，里面列出可以安装的插件。每个插件是一组技能。技能（skill）是一份写给 AI 助手看的说明书，文件名固定叫 `SKILL.md`，开头有名字和说明，后面是具体步骤。

技能正文是中文。S 把同一份文件装进 WorkBuddy、Cursor、Claude Code。改完合并进 `main` 分支之后，已经安装的应用可以收到更新。Codex 和 OpenCode 没有和前三个完全一样的安装入口，仓库里也给它们准备了可用的装法。

仓库是公开的，这是 S 自己的选择。

## 里面有什么

6 个插件，一共 109 个技能。技能文件只存一份，放在对应插件的 `skills/` 里面。三个应用的清单都指向这些文件夹，没有为每个应用再复制一份技能。

| 插件短名 | 数量 | 里面是什么 |
|---|---|---|
| `pstack` | 54 | pstack 的中文技能：做事原则、工作流程、TypeScript 写法 |
| `compound-engineering` | 15 | Compound Engineering 的中文技能：做计划、查 bug、提交、审查 |
| `superpowers` | 1 | Superpowers 里译出的「完成前验证」 |
| `ui-ux` | 18 | 界面设计：impeccable、ui-ux-pro-max、Vercel 的网页设计规范、Emil Kowalski 的 15 个技能 |
| `figma` | 16 | Figma 官方技能的中文版 |
| `s-own` | 5 | S 自己写的技能，正文保持英文，没有改过 |

插件短名是给应用看的，只能用小写英文字母、数字和连字符。技能的名字保持中文（S 自己的那 5 个保持原来的英文名）。

目录长这样：

```text
.cursor-plugin/marketplace.json      Cursor 的市场目录
.claude-plugin/marketplace.json      Claude Code 的市场目录
.codebuddy-plugin/marketplace.json   WorkBuddy / CodeBuddy 的市场目录
.agents/plugins/marketplace.json     Codex 的市场目录
plugins/<插件短名>/
  plugin.json                        Codex 和通用插件格式用的清单
  .cursor-plugin/plugin.json
  .claude-plugin/plugin.json
  .codebuddy-plugin/plugin.json
  CREDITS.md                         这个插件的作者和许可证说明
  skills/
    <技能名>/SKILL.md
    LICENSE-...                      上游许可证，放在技能的上一级
```

技能正文里写着「许可证全文见上一级文件夹」。所以上游的 `LICENSE-*` 和 impeccable 的 `NOTICE-impeccable.md` 放在 `skills/` 里，和技能文件夹并排，没有改这些文件里的字。

## 作者和许可证

翻译时用的版本记在每个 `SKILL.md` 开头。这里是总表。

| 插件 | 上游 | 作者 | 许可证 |
|---|---|---|---|
| `pstack` | Cursor 插件 pstack，编号 9717366，版本 0.15.25 | Lauren Tan，版权 © 2026 Lauren Tan | MIT，文件 `LICENSE-pstack` |
| `compound-engineering` | Compound Engineering，编号 680，版本 3.29.0 | Kieran Klaassen 和 Trevin Chow，版权 © 2025 Every | MIT，文件 `LICENSE-compound-engineering` |
| `superpowers` | Superpowers，编号 684，版本 6.1.1 | Jesse Vincent，版权 © 2025 Jesse Vincent | MIT，文件 `LICENSE-superpowers` |
| `ui-ux` | [impeccable](https://github.com/pbakaus/impeccable) commit 08d5b47 | Paul Bakaus，版权 © 2025 Paul Bakaus | Apache 2.0。要同时保留 `LICENSE-impeccable` 和 `NOTICE-impeccable.md`。中文版是翻译，算对原文的改动 |
| `ui-ux` | [ui-ux-pro-max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) commit 56ea9cf | Next Level Builder，版权 © 2024 | MIT，文件 `LICENSE-ui-ux-pro-max` |
| `ui-ux` | [Emil Kowalski skills](https://github.com/emilkowalski/skills) commit 2d22863 | Emil Kowalski，版权 © 2026 Emil Kowalski | MIT，文件 `LICENSE-emilkowalski-skills` |
| `ui-ux` | [Vercel agent-skills](https://github.com/vercel-labs/agent-skills) commit 063bee9 | Vercel | 上游仓库没有单独的 LICENSE 文件，README 末尾写了 MIT。说明在 `LICENSE-vercel-agent-skills` |
| `figma` | [Figma mcp-server-guide](https://github.com/figma/mcp-server-guide) commit f278942 | Figma | 上游仓库没有许可证文件。S 知道这一点，仍然选择放进这个公开仓库，只给自己用 |
| `s-own` | S 自己的备份 `my-skills/` | S | 备份里没有单独的许可证文件 |

每个插件目录里的 `CREDITS.md` 重复了这一插件对应的说明，这样应用把插件复制到本机缓存之后，许可证还在插件里面。

## 中文名对照表

104 个翻译技能。「英文名」是英文名备份里的名字，每个 `SKILL.md` 开头有一行 `英文名备份：s-...`。「原始 skill」是上游插件或仓库里的英文名。标 ⚠️ 的，表示它的 `references/` 参考文件还是英文（那些文件太大，翻译时留了原文）。

| 中文名 | 英文名 | 原始 skill | 用途 |
|---|---|---|---|
| `全自动开发` ⚠️ | `s-lfg` | `lfg`（CE 680） | 全自动把一个需求从头做到完成；改代码的话最后会自动推送并开好 PR。只在明确要“全自动”时用。 |
| `头脑风暴` ⚠️ | `s-ce-brainstorm` | `ce-brainstorm`（CE 680） | 头脑风暴：把模糊的想法整理成“要做什么”的需求。 |
| `做计划` ⚠️ | `s-ce-plan` | `ce-plan`（CE 680） | 做计划：把多步骤的工作拆成清楚的步骤（只做计划，不写代码）。 |
| `按计划实现` ⚠️ | `s-ce-work` | `ce-work`（CE 680） | 照着计划或明确的要求去实现，并在本地验证。 |
| `查bug` ⚠️ | `s-ce-debug` | `ce-debug`（CE 680） | 排查 bug：先找到根本原因，再（经同意）先写测试后修复。 |
| `简化代码` | `s-ce-simplify-code` | `ce-simplify-code`（CE 680） | 把刚写好的代码变简单、好读，功能完全不变。 |
| `代码审查` ⚠️ | `s-ce-code-review` | `ce-code-review`（CE 680） | 审查代码改动或 PR，找 bug、回归问题、测试和规范问题。默认只报告，不改代码。 |
| `处理PR意见` ⚠️ | `s-ce-resolve-pr-feedback` | `ce-resolve-pr-feedback`（CE 680） | 处理别人在 PR 上留下的审查意见：判断、修复、回复、标记解决。 |
| `提交代码` | `s-ce-commit` | `ce-commit`（CE 680） | 帮你把改动提交（commit）到本地，写好提交说明。不推送。 |
| `提交推送开PR` ⚠️ | `s-ce-commit-push-pr` | `ce-commit-push-pr`（CE 680） | 提交 + 推送 + 开 PR 一次做完；也可以只帮你写 PR 说明。 |
| `测试驱动修bug` | `s-tdd` | `tdd`（pstack 9717366） | 修 bug 时先写一个会失败的测试，再修到它通过（只在明确要求或很容易测时用）。 |
| `完成前验证` | `s-verification-before-completion` | `verification-before-completion`（Superpowers 684） | 说“做完了/修好了/通过了”之前，必须先真的跑命令验证。 |
| `大白话解释` | `s-wtf` | `wtf`（CE 680） | 没看懂上一条消息（或某个文件、链接、段落）时，用大白话重新解释。 |
| `解释代码` | `s-ce-explain` | `ce-explain`（CE 680） | 根据证据解释代码“怎么工作、为什么这样”，或者回顾一段时间里做了什么。 |
| `一步步教我` | `s-teach` | `teach`（pstack 9717366） | 像老师一样，一步一步把一块工作讲到你真正弄懂。 |
| `去AI腔` | `s-ce-noslop` | `ce-noslop`（CE 680） | 改写或检查文字，去掉“AI 腔”，让人一读就懂。 |
| `技术写作` | `s-technical-writing` | `technical-writing`（pstack 9717366） | 技术文档写作规范（原本针对英文写作），用于写文档、readme、PR 说明、提交信息。 |
| `文档审查` ⚠️ | `s-ce-doc-review` | `ce-doc-review`（CE 680） | 从多个角色的角度审查需求文档、计划或规格说明，找出会影响结果的问题。 |
| `交接单` | `s-ce-handoff` | `ce-handoff`（CE 680） | 写一份交接单，让另一个 AI 助手（或新的对话）能接着做；也可以从交接单续接。 |
| `按我习惯定制` | `s-automate-me` | `automate-me`（pstack 9717366） | 从你的对话习惯里总结规则，做成一个“按你的方式工作”的专属 skill。 |
| `网页设计规范` | `s-web-design-guidelines` | `web-design-guidelines`（Vercel） | 按 Vercel 的《网页界面规范》检查界面代码（规范内容运行时从网上读取）。 |
| `精致界面设计` ⚠️ | `s-impeccable` | `impeccable`（impeccable） | 设计、点评、打磨前端界面的一整套方法，避免做出“AI 味”的千篇一律界面。 |
| `UIUX知识库` ⚠️ | `s-ui-ux-pro-max` | `ui-ux-pro-max`（ui-ux-pro-max） | 带数据库的 UI/UX 设计知识库：用脚本按产品类型查风格、配色、字体、图表建议。 |
| `苹果式设计` | `s-emil-apple-design` | `apple-design`（Emil Kowalski） | 苹果式流畅界面和有物理感的动效（弹簧、手势、惯性、半透明材质、字体排版），用在网页上。改名是为了和你自己的 `apple-design-2` 区分。 |
| `界面压力测试` | `s-break-ui` | `break-ui`（Emil Kowalski） | 用最坏情况的真实数据（超长名字、空列表、emoji 等）搞坏界面，列出坏点和修法。 |
| `选前端库` | `s-pick-ui-library` | `pick-ui-library`（Emil Kowalski） | 按任务从精选清单里推荐前端库（提示消息、拖放、图表等）。只在你明确叫它时才用。 |
| `Emil设计理念` | `s-emil-design-eng` | `emil-design-eng`（Emil Kowalski） | Emil 的设计工程理念：界面打磨、组件设计、动画该不该做、用什么缓动和时长；审查时用“修改前 / 修改后 / 原因”表格。 |
| `做动画` | `s-animate` | `animate`（Emil Kowalski） | 从零做一个动画：按顺序决定该不该动、为什么动、用什么工具、什么曲线和时长，然后直接写代码。 |
| `Expo动画` ⚠️ | `s-animate-expo` | `animate-expo`（Emil Kowalski） | 给 Expo / React Native 手机应用加动画（Reanimated、手势等）。 |
| `动画性能` | `s-animation-performance` | `animation-performance`（Emil Kowalski） | 排查和避免动画卡顿：只动 transform 和 opacity、少触发重排等。 |
| `动画术语表` | `s-animation-vocabulary` | `animation-vocabulary`（Emil Kowalski） | 动画术语表：把“想要的感觉”翻译成准确的动画词汇（术语保留英文，附中文解释）。 |
| `Sonner用法` | `s-ask-sonner` | `ask-sonner`（Emil Kowalski） | 回答关于 Sonner（React 提示消息库）的用法问题。 |
| `找动画机会` | `s-find-animation-opportunities` | `find-animation-opportunities`（Emil Kowalski） | 在现有界面里找出哪些地方该加动画、哪些不该加，给出带数值的建议（只提建议，不改代码）。 |
| `动画改进计划` | `s-improve-animations` | `improve-animations`（Emil Kowalski） | 全面审查代码库里的动画，写出按优先级排序的审计结果，以及交给其他助手执行的实现计划。 |
| `动画审查` | `s-review-animations` | `review-animations`（Emil Kowalski） | 按 Emil 的标准审查动画代码，列出问题和修法。只在你明确叫它时才用。 |
| `多版本原型` | `s-emil-prototype` | `prototype`（Emil Kowalski） | 为一块界面做出几个真正不同的版本，放在切换器后面让你实时比较、选定。只在你明确叫它时才用。改名是为了和 `ce-prototype` 区分。 |
| `手机原生手感` | `s-mobile-native` | `mobile-native`（Emil Kowalski） | 让手机网页 / 应用的手感像原生应用（触摸反馈、滚动、手势、安全区域等）。 |
| `写Swift` | `s-write-swift` | `write-swift`（Emil Kowalski） | 怎样写好现代 Swift：值类型、Swift 6 并发、协议和泛型、性能、测试等。 |
| `Figma新建文件` | `s-figma-create-new-file` | `figma-create-new-file`（Figma） | 在 Figma 里新建设计 / 白板 / 幻灯片文件的步骤。 |
| `Figma设计稿转代码` | `s-figma-design-to-code` | `figma-design-to-code`（Figma） | 把 Figma 设计准确地写成代码（必须先读的前置步骤）。 |
| `代码导入Figma` | `s-figma-code-workflows` | `figma-code-workflows`（Figma） | 把本地 HTML 或项目导入 Figma，选择做成可编辑设计图层还是可运行的代码图层。 |
| `Figma规格文档` | `s-figma-spec` | `figma-spec`（Figma） | 新建、阅读、编辑、评论 Figma 里的规格文档（需求文档、方案等）。 |
| `Figma与SwiftUI` ⚠️ | `s-figma-swiftui` | `figma-swiftui`（Figma） | Figma 和 SwiftUI（苹果 iOS 界面代码）之间互相转换的“指路牌”。 |
| `Figma生成式插件` | `s-figma-generative-plugins` | `figma-generative-plugins`（Figma） | 新建和修改可重复使用的生成式 Figma 插件。 |
| `Figma着色器` | `s-figma-shaders` | `figma-shaders`（Figma） | 新建和修改 Figma 里的着色器效果和着色器填充（显卡逐像素计算的特效）。 |
| `FigJam白板操作` ⚠️ | `s-figma-use-figjam` | `figma-use-figjam`（Figma） | 在 FigJam 白板里用 `use_figma` 工具做便利贴、连接线、分区等。 |
| `Figma做动画` ⚠️ | `s-figma-use-motion` | `figma-use-motion`（Figma） | 在 Figma 里给图层做动画：关键帧、动画样式、缓动、时间轴。 |
| `Figma插件基础` ⚠️ | `s-figma-use` | `figma-use`（Figma） | 用 `use_figma` 工具在 Figma 里执行插件代码的基础规则（每次调用 `use_figma` 前必须先读）。 |
| `Figma幻灯片` ⚠️ | `s-figma-use-slides` | `figma-use-slides`（Figma） | 在 Figma Slides 里用 `use_figma` 做幻灯片：设计思路、搭建流程、分区、演讲者备注。 |
| `Figma搭建页面` ⚠️ | `s-figma-generate-design` | `figma-generate-design`（Figma） | 根据代码或描述，用设计系统的组件和变量在 Figma 里搭建或更新整个页面 / 弹窗 / 面板。 |
| `Figma设计系统` ⚠️ | `s-figma-generate-library` | `figma-generate-library`（Figma） | 根据代码库在 Figma 里搭建或更新设计系统：变量、组件、变体、主题。 |
| `Figma生成图表` ⚠️ | `s-figma-generate-diagram` | `figma-generate-diagram`（Figma） | 用 Mermaid 在 FigJam 里生成流程图、时序图、ER 图、状态图、甘特图（调用 `generate_diagram` 前必须先读）。 |
| `Figma组件对应代码` ⚠️ | `s-figma-code-connect` | `figma-code-connect`（Figma） | 写 Code Connect 模板文件（`.figma.ts`），把 Figma 组件对应到代码。 |
| `Figma动效转代码` ⚠️ | `s-figma-implement-motion` | `figma-implement-motion`（Figma） | 把 Figma 里做好的动画写成真正的代码（motion.dev、CSS 关键帧等）。 |
| `poteto工作模式` ⚠️ | `s-poteto-mode` | `poteto-mode`（pstack 9717366） | pstack 的总入口：按任务类型匹配一套操作手册（playbook），照着步骤做，按需调用其他 skill，并用原则指导每个决定。 |
| `设置pstack模型` | `s-setup-pstack` | `setup-pstack`（pstack 9717366） | 检测你能用的模型，按角色设置 pstack 用哪个模型、推理预算多大，写成一条始终生效的规则。 |
| `pstack使用帮助` | `s-poteto-help` | `poteto-help`（pstack 9717366） | 回答“pstack 怎么用、该用哪个 skill”，给你一段可以直接发的提示词。 |
| `动手前磨清任务` | `s-sharpen` | `sharpen`（pstack 9717366） | 开始前先想清楚：专家会怎么做、你真正想要什么、要求写得太死还是太含糊。 |
| `复述用户目标` | `s-in-your-own-words` | `in-your-own-words`（pstack 9717366） | 让助手用自己的话复述你的目标和要解决的问题，确认它没理解错。 |
| `先画架构草图` | `s-architect` | `architect`（pstack 9717366） | 写代码前先勾勒类型、函数签名和模块结构（多个模型并行设计），再照着草图实现。 |
| `多方案竞技场` | `s-arena` | `arena`（pstack 9717366） | 同一个任务同时派出多个候选者，选一个做基础，再把其他候选的长处嫁接进来。 |
| `并行群体作战` | `s-swarm` | `swarm`（pstack 9717366） | 同时派出 N 个并行工作者（分片或比赛），等全部完成，汇总成一份报告。 |
| `自定流程搞定` | `s-figure-it-out` | `figure-it-out`（pstack 9717366） | 没有现成流程可用时（大迁移、复杂改动、通宵任务），自己设计一套严谨、可审计的做法。 |
| `TypeScript最佳实践` | `s-typescript-best-practices` | `typescript-best-practices`（pstack 9717366） | 读写 .ts / .tsx 文件时的 TypeScript 规则：可辨识联合类型、品牌类型、不用 as 断言等，附代码示例。 |
| `清理代码注释` | `s-no-comments` | `no-comments`（pstack 9717366） | 派出专挑注释毛病的子智能体，删掉多余或掩盖问题的注释，并把注释里的限制改成代码强制执行（需要原插件的 comment-sicko 子智能体）。 |
| `根除重复错误` | `s-correct` | `correct`（pstack 9717366） | 找出助手在这个仓库里反复犯的错，用架构、类型、lint、测试让它们不可能再犯。 |
| `决定记录日志` | `s-show-me-your-work` | `show-me-your-work`（pstack 9717366） | 长时间或无人值守的工作中，用 TSV 日志记下每个决定（做了什么、为什么、证据、结果），最后自查并让另一个模型审一遍。 |
| `pstack做Bot界面` | `s-pstack-make-bot-ui` | `make-bot-ui`（pstack 9717366） | 做一个按钮能通过 webhook 唤醒 Grok Bot 的网页界面，并放到 Tailscale 上访问。改名是为了和你自己的 `make-bot-ui` 区分。 |
| `多模型对抗审查` | `s-interrogate` | `interrogate`（pstack 9717366） | 让多个不同的模型对抗式审查代码改动，再由主审把发现分成要处理 / 值得考虑 / 记录 / 驳回。 |
| `改动影响范围` | `s-blast-radius` | `blast-radius`（pstack 9717366） | 找出一个改动在 diff 之外可能弄坏什么，并用真实运行的代码证明它安全所依赖的那个事实。 |
| `基准测试清单` | `s-benchmark-checklist` | `benchmark-checklist`（pstack 9717366） | 报告性能数字之前的 7 个检查问题：限制因素、调优、物理极限、出错、可复现、是否重要、工作是否真的发生了。 |
| `创建验证skill` | `s-create-verification-skill` | `create-verification-skill`（pstack 9717366） | 为项目生成一个“像用户一样操作应用并证明行为”的验证 skill，附功能地图。 |
| `维护验证skill` | `s-maintain-verification-skill` | `maintain-verification-skill`（pstack 9717366） | 定期检查验证 skill 和功能地图是否还和应用对得上，只提交已证明的修正。 |
| `清理AI腔` | `s-unslop` | `unslop`（pstack 9717366） | 按一份编号规则清单去掉文字里的 AI 腔（原本针对英文写作，例子保留英文并附中文意思）。和 `去AI腔` 作用相近，来源不同。 |
| `反思并改skill` | `s-reflect` | `reflect`（pstack 9717366） | 用三个审查子智能体回看本次对话，总结出持久有用的经验，经你批准后改进对应的 skill。 |
| `代码怎么工作` | `s-how` | `how`（pstack 9717366） | 探索代码库，讲清“X 是怎么工作的”、新代码该放在哪里。 |
| `代码为什么这样` ⚠️ | `s-why` | `why`（pstack 9717366） | 查 git 历史、工单、文档、聊天、监控等来源，讲清代码为什么是现在这个样子，并标明可信度。 |
| `回想最近工作` | `s-recall` | `recall`（pstack 9717366） | 从你的聊天记录和共享记录里，重建你最近在某件事上的工作进度，给一份简报。 |
| `补上对话进度` | `s-ketchup` | `ketchup`（pstack 9717366） | 用几句大白话和小图，告诉你自从你上一条消息之后这个对话里发生了什么、哪些事需要你决定。 |
| `说人话重讲` | `s-bro` | `bro`（pstack 9717366） | 把上一条消息用不带行话的大白话重新说一遍（很短）。 |
| `原则-质疑前提` | `s-principle-attack-the-premise` | `principle-attack-the-premise`（pstack 9717366） | 同一个前提的修复失败两次以上，就先验证前提本身。 |
| `原则-守住边界` | `s-principle-boundary-discipline` | `principle-boundary-discipline`（pstack 9717366） | 校验和错误处理集中在系统边界，内部信任类型。 |
| `原则-打造杠杆` | `s-principle-build-the-lever` | `principle-build-the-lever`（pstack 9717366） | 不简单的工作，写个脚本或工具来做或来证明，而不是手工做。 |
| `原则-教训写进结构` | `s-principle-encode-lessons-in-structure` | `principle-encode-lessons-in-structure`（pstack 9717366） | 同一条指示写第二次时，改成 lint、检查或脚本。 |
| `原则-穷尽设计空间` | `s-principle-exhaust-the-design-space` | `principle-exhaust-the-design-space`（pstack 9717366） | 没有先例的设计，先做 2-3 个原型比较。 |
| `原则-体验优先` | `s-principle-experience-first` | `principle-experience-first`（pstack 9717366） | 让用户满意优先于实现方便；少而精。 |
| `原则-解释数字` | `s-principle-explain-the-number` | `principle-explain-the-number`（pstack 9717366） | 相信一个测出来的数字前，先找出限制它的因素。 |
| `原则-修根本原因` | `s-principle-fix-root-causes` | `principle-fix-root-causes`（pstack 9717366） | 调试时修第一次出错的地方，而不是症状。 |
| `原则-基础优先` | `s-principle-foundational-thinking` | `principle-foundational-thinking`（pstack 9717366） | 先定数据结构和脚手架，再写逻辑。 |
| `原则-守住上下文` | `s-principle-guard-the-context-window` | `principle-guard-the-context-window`（pstack 9717366） | 大块内容交给子智能体，主线程只留摘要。 |
| `原则-偷懒守则` | `s-principle-laziness-protocol` | `principle-laziness-protocol`（pstack 9717366） | 倾向删除和最小改动。 |
| `原则-操作幂等` | `s-principle-make-operations-idempotent` | `principle-make-operations-idempotent`（pstack 9717366） | 操作运行多少次、中途崩在哪，都收敛到同一个结果。 |
| `原则-迁完再删旧API` | `s-principle-migrate-callers-then-delete-legacy-apis` | `principle-migrate-callers-then-delete-legacy-apis`（pstack 9717366） | 新内部 API 上线时，同一轮迁移调用方并删掉旧的。 |
| `原则-减轻读者负担` | `s-principle-minimize-reader-load` | `principle-minimize-reader-load`（pstack 9717366） | 减少要追踪的层数和要记住的状态。 |
| `原则-为领域建模` | `s-principle-model-the-domain` | `principle-model-the-domain`（pstack 9717366） | 用状态机、类型模型等结构代替散落的条件判断。 |
| `原则-别卡着等人` | `s-principle-never-block-on-the-human` | `principle-never-block-on-the-human`（pstack 9717366） | 可撤销的事直接做，再汇报；不可撤销的才问。 |
| `原则-结果导向` | `s-principle-outcome-oriented-execution` | `principle-outcome-oriented-execution`（pstack 9717366） | 计划内的重写直接奔向目标架构，不留临时兼容代码。 |
| `原则-证明真能用` | `s-principle-prove-it-works` | `principle-prove-it-works`（pstack 9717366） | 对照真实产物验证，不靠“能编译”或自我汇报。 |
| `原则-从头重新设计` | `s-principle-redesign-from-first-principles` | `principle-redesign-from-first-principles`（pstack 9717366） | 整合新需求时，当它从一开始就存在那样重新设计。 |
| `原则-先分开共享状态` | `s-principle-separate-before-serializing-shared-state` | `principle-separate-before-serializing-shared-state`（pstack 9717366） | 并发写同一状态时，先消除共享，再考虑加锁。 |
| `原则-可验证小单元` | `s-principle-sequence-verifiable-units` | `principle-sequence-verifiable-units`（pstack 9717366） | 拆成每步都能检查的小单元，按能证明自己的顺序交付。 |
| `原则-先减后加` | `s-principle-subtract-before-you-add` | `principle-subtract-before-you-add`（pstack 9717366） | 先删死代码和多余部分，再搭建。 |
| `原则-测行为不测实现` | `s-principle-test-behavior-not-implementation` | `principle-test-behavior-not-implementation`（pstack 9717366） | 测试断言使用者能看到的行为，不绑定内部实现。 |
| `原则-类型系统纪律` | `s-principle-type-system-discipline` | `principle-type-system-discipline`（pstack 9717366） | 让非法状态无法表示，在边界解析外部数据。 |

S 自己的 5 个技能不在上表里。文件夹名和说明书里的名字如下：

| 文件夹 | 说明书里的名字 |
|---|---|
| `apple-design-2` | `Apple Design` |
| `design-a-grok-bot` | `Design a Grok Bot` |
| `make-bot-ui` | `Make Bot UI` |
| `routine-healthcheck` | `Routine healthcheck` |
| `transcript-healthcheck` | `Transcript healthcheck` |

## 装到每个应用

等这些文件合并进 GitHub 上的 `main` 分支之后，再用下面的命令。市场短名是 `s-skills`。

六个插件都要装的话，把下面每个插件短名都装一次：`pstack`、`compound-engineering`、`superpowers`、`ui-ux`、`figma`、`s-own`。

### WorkBuddy（腾讯，底层是 CodeBuddy Code）

在 WorkBuddy 的对话里输入：

```text
/plugin marketplace add Acefake/s-skills
```

`/plugin` 是插件管理命令。`marketplace` 是市场。`add` 是把这个 GitHub 仓库登记成一个市场。登记之后还要安装具体插件：

```text
/plugin install pstack@s-skills
/plugin install compound-engineering@s-skills
/plugin install superpowers@s-skills
/plugin install ui-ux@s-skills
/plugin install figma@s-skills
/plugin install s-own@s-skills
```

`pstack@s-skills` 的意思是：市场 `s-skills` 里的插件 `pstack`。装完运行：

```text
/reload-plugins
```

这是重新加载插件，不用退出应用。

### Claude Code

命令和 WorkBuddy 一样，在 Claude Code 的对话里输入：

```text
/plugin marketplace add Acefake/s-skills
/plugin install pstack@s-skills
```

其余五个插件把短名换掉。也可以在终端里运行 `claude plugin marketplace add Acefake/s-skills`，然后 `claude plugin install pstack@s-skills`。装完在对话里运行 `/reload-plugins`。

### Cursor

Cursor 用仓库里的 `.cursor-plugin/marketplace.json` 把整个仓库当成一个市场。

团队版（Teams 或 Enterprise，需要管理员）：

1. 打开 Cursor 的 Dashboard，进入 Plugins & MCPs（插件和 MCP）。
2. 在 Team Marketplaces（团队市场）里选 Import from Repo（从仓库导入）。
3. 粘贴 `https://github.com/Acefake/s-skills`。
4. 确认它列出了上面 6 个插件，保存。
5. 在 Cursor 侧边栏的 Customize（自定义）里安装要用的插件。安装时可选「只给自己」或「这个项目」。

个人用的 Cursor 也可以在 Customize → Plugins 里找 Import marketplace / Add marketplace（导入市场），粘贴同一个仓库地址。2026-10-18 的官方文档把导入步骤写在团队市场那一节；个人界面上的入口名称以你本机菜单为准。导入这一步我没有在 Cursor 里点过。

不想走市场时，可以用下面的「skills 命令」把技能装进 Cursor。

### Codex

Codex 现在有插件市场。官方说明写在 [Build plugins](https://developers.openai.com/plugins/build/plugins)。这个仓库按那个格式放了 `.agents/plugins/marketplace.json`。在终端：

```text
codex plugin marketplace add Acefake/s-skills
```

然后打开 Codex，输入 `/plugins`，在市场列表里安装插件。装完新开一个对话再用。

Codex 还会顺带读取 `.claude-plugin/marketplace.json` 和 `.cursor-plugin/marketplace.json`。这三个文件都列出了同一批插件，所以 Codex 里可能看到重复的条目。装其中一个即可。这一重复我没有在 Codex 里打开确认过。

Codex 的 IDE 扩展不支持插件。要用插件，打开 Codex 命令行，或 ChatGPT 桌面版里的 Codex。

### OpenCode

OpenCode 到 2026-10-18 还没有官方的插件市场（官方仓库里仍是一条待做的需求）。它会从本机的技能文件夹读取 `SKILL.md`。用下面的 skills 命令装到 OpenCode。

### skills 命令（Codex、OpenCode、也可以给 Cursor）

[vercel-labs/skills](https://github.com/vercel-labs/skills) 是一个安装技能的命令行工具。它会在仓库里找 `SKILL.md`。这个仓库的 Claude 市场清单写了每个插件的路径，它能顺着路径找到 `plugins/<插件>/skills/<技能名>/`。

装到当前用户、所有项目都能用（`-g` 就是 global，全局）：

```text
npx skills add Acefake/s-skills -g -a codex -a opencode -a cursor -y
```

`-a` 后面是应用的短名。只要其中几个，就删掉不用的。`-y` 是不用再逐个确认。

以后更新：

```text
npx skills update -g
```

这条路看的是 GitHub 上的文件有没有变，不看插件版本号。插件市场那条路才看版本号，见下一节。

只看仓库里有哪些技能、先不安装：

```text
npx skills add Acefake/s-skills --list
```

## 装上之后怎么调用

应用会把插件短名加在技能名前面，中间用冒号。这叫命名空间，用来避免两个插件里的技能撞名。

在 WorkBuddy 和 Claude Code 里，输入：

```text
/pstack:先画架构草图
/compound-engineering:做计划
/superpowers:完成前验证
/ui-ux:精致界面设计
/figma:Figma插件基础
```

斜杠 `/` 是调用命令。冒号前面是插件短名，后面是技能的中文名。没有别的命令占用这个中文名时，只打 `/做计划` 往往也能用。助手也可以在任务对得上技能开头的说明时，自己去读那份说明书。

Cursor 里在对话输入 `/`，搜索技能的中文名。官方文档写的形式是 `/技能名`。如果列表里显示成带插件短名的，就选带短名的那一项。

Codex 里输入 `@`，选择插件或其中的技能。

OpenCode 把技能交给内置的 skill 工具，按说明书开头的说明决定要不要读全文。这 109 个文件没有额外写 OpenCode 专用的开关，所以不一定出现成一条 `/中文名` 命令。直接说出技能的中文名，让它按那份说明书做。

## 中文名能不能被认出来

技能文件夹和说明书里的 `name` 都是中文（S 自己的 5 个除外）。插件短名是英文。下面是 2026-10-18 对照官方文档和已知问题后的判断。标了「未实测」的，是没有在那个应用里真正安装过。

- **WorkBuddy / CodeBuddy。** 官方文档要求插件短名是英文短横线格式，没有要求技能名必须是英文。调用形式是 `插件短名:技能名`。S 原来的备份说明里写过：中文名可以在 WorkBuddy 里直接用。这次没有在 WorkBuddy 里安装验证。
- **Claude Code。** 官方文档写：插件里的技能，命令最后一段用说明书里的 `name`，所以形式上会是 `/pstack:先画架构草图`。个人技能文件夹（`~/.claude/skills/中文名/`）可以保留中文。插件这条路径上有一个已报告的问题：[claude-code#66554](https://github.com/anthropics/claude-code/issues/66554)。从 2.1.94 起，插件技能名里英文、数字、下划线、连字符以外的字符会被换成连字符 `-`。中文每个字都会变成一个 `-`，字数相同的技能会撞成同一个名字，助手按中文名去调用会得到 Unknown skill。例如「一步步教我」和「说人话重讲」都是五个字，会挤成同一个 `pstack:-----`。个人技能不受这个影响。这个问题我没有在本机的 Claude Code 里复现，只核对了问题报告和当时的改动说明。技能正文因此没有改成英文名。
- **Cursor。** 官方文档把技能 `name` 写成小写英文加连字符，并且要和文件夹名一致。Cursor 命令行会给不合这个格式的名字打警告（名字超过 64 字、不是小写短横线、名字和文件夹不一致、说明超过 1024 字、正文大约超过 5000 个词）。文档写的是警告，没有写「直接拒绝加载」。中文名会触发「不是小写短横线」和「名字与文件夹不一致」这两类警告。能否在插件里真正跑起来，未实测。
- **skills 命令。** 我读了 2026-10-18 的 `vercel-labs/skills` 源码。它清理名字时只去掉会扰乱终端的控制字符，中文会留下来。发现技能时会读 `.claude-plugin/marketplace.json`，再进入每个插件的 `skills/`。本地用 skills 命令 1.5.18 跑过 `npx skills add <仓库目录> --list`，它列出 109 个技能，中文名都在，没有被丢掉。真正写进 Codex、OpenCode 或 Cursor 的安装目录这一步未实测。
- **Codex 插件。** 官方示例里的技能名是英文短横线。中文文件夹放进 Codex 插件之后能不能点开，未实测。装不上时，用上面的 skills 命令，目标应用写 `codex`。
- **OpenCode。** 官方文档只要求 `name` 和 `description`，没有要求英文。它从 `~/.config/opencode/skills/<名字>/SKILL.md` 读取。未实测。

如果某个应用把中文插件技能压坏了，同一批文件仍可以用 skills 命令装到那个应用的个人技能目录。Claude Code 的个人技能路径目前会保留中文名。那是另一条安装方式，不会走插件版本号。

## 更新怎么发生

分两条路。

**插件市场（WorkBuddy、Claude Code、Codex 的插件安装）。** 应用把插件复制到本机的一个缓存目录。WorkBuddy 和 Claude Code 的官方文档写明：已经安装的插件，要等它的**版本号**变了，才会换成新的一份。版本号写在每个插件的四份清单里（`plugin.json`、`.cursor-plugin/plugin.json`、`.claude-plugin/plugin.json`、`.codebuddy-plugin/plugin.json`），像 `1.0.0`。市场目录里故意不再写一遍版本号。官方文档说两处都写的话，以 `plugin.json` 为准，并且校验命令会警告它们不一致。

所以：改了某个插件里的技能或许可证之后，要让别人的应用收到，必须把该插件的版本号加大，再合并。只合并文件、不改版本号，WorkBuddy 和 Claude Code 会继续用旧缓存。

加大版本号：

```text
python3 scripts/bump_plugin_version.py pstack
```

把 `pstack` 换成改过的插件短名。一次改了多个插件：

```text
python3 scripts/bump_plugin_version.py --all
```

脚本只把最后一位加 1，例如 `1.0.0` 变成 `1.0.1`。它同时改四份清单和 `plugin-versions.lock.json`。这个 lock 文件记下「这一版对应的文件内容指纹」。内容变了却没加大版本号时，`python3 scripts/check_marketplace.py` 会失败，GitHub 上的检查也会失败。

想把 `1.0.1` 改成 `1.1.0` 或 `2.0.0`：手动改 lock 文件里的 `version`，以及该插件四份清单里的 `version`，再跑检查。内容指纹对得上、五处版本号一致，检查就会通过。

**Cursor 团队市场**的官方文档另外说：打开 Enable Auto Refresh（自动刷新）之后，仓库一推送，Cursor 会重新读市场（大约最多每 10 分钟一次），跟的是新的提交。这需要仓库安装了 Cursor 的 GitHub App。个人导入的刷新方式以 Cursor 当时的界面为准。

**skills 命令**不看 `1.0.0` 这种版本号。`npx skills update -g` 会对照 GitHub 上的文件重新装。

### 第三方市场默认不会自动更新

WorkBuddy / CodeBuddy 和 Claude Code 都是：官方市场默认自动更新，**别人的市场默认关闭**。这个仓库属于后者。关掉时，合并新版本之后，要自己在对话里运行：

```text
/plugin marketplace update s-skills
```

或者按插件更新，例如在终端运行 `claude plugin update pstack@s-skills`（WorkBuddy 里是对应的 `codebuddy` 命令，对话里也可以用 `/plugin` 的更新入口）。

打开自动更新：

1. 在对话里运行 `/plugin`。
2. 进入市场（Marketplaces）那一页。
3. 选中 `s-skills`。
4. 选择「启用自动更新」（Enable auto-update）。

Claude Code 还可以写进设置文件。用户自己的设置一般是 `~/.claude/settings.json`，只对某一个项目生效则是项目里的 `.claude/settings.json`：

```json
{
  "extraKnownMarketplaces": {
    "s-skills": {
      "source": {
        "source": "github",
        "repo": "Acefake/s-skills"
      },
      "autoUpdate": true
    }
  }
}
```

`extraKnownMarketplaces` 是「额外已知市场」。`autoUpdate: true` 是允许这个市场在后台检查更新。官方文档写明：市场文件本身没有开关，只能由使用的人或管理员打开。

WorkBuddy 的官方文档写了同一套界面开关，也写了第三方市场默认关闭。它给出的设置示例里有 `extraKnownMarketplaces`，示例中没有 `autoUpdate` 这一项。界面开关是文档明确写了的。设置文件里加 `autoUpdate` 能否被 WorkBuddy 认，未实测。

两边都可以用环境变量关掉所有自动更新：`DISABLE_AUTOUPDATER=1`。如果只想关掉应用自己的更新、仍要插件更新，再加 `FORCE_AUTOUPDATE_PLUGINS=1`。

自动更新打开之后，新版本会在一次新对话开始后的后台检查里下载。当前这场对话仍用旧的，看到提示后再运行 `/reload-plugins`，或下次启动时用新的。

## 卸掉

WorkBuddy 和 Claude Code，在对话里：

```text
/plugin uninstall pstack@s-skills
```

六个都卸掉时，对每个短名做一次。连市场一起去掉：

```text
/plugin marketplace remove s-skills
```

去掉市场时，从它装上的插件会一起卸掉。

Cursor：在 Customize 里找到已安装的插件，选卸载。团队市场由管理员在 Dashboard 的 Team Marketplaces 里移除。

Codex：在 `/plugins` 里对插件选卸载。终端里移除市场：

```text
codex plugin marketplace remove s-skills
```

skills 命令装上的，按应用卸：

```text
npx skills remove --agent opencode --skill '*' -g
```

把 `opencode` 换成 `codex` 或 `cursor` 即可。不加 `--skill '*'` 时，命令会让你选择要卸哪些。

## 改完怎么自己检查

```text
pip install "jsonschema>=4.20"
python3 scripts/check_marketplace.py
```

检查这些事：Cursor 的两份清单符合官方 JSON Schema；Claude Code 和 CodeBuddy 的市场字段符合官方文档里的名字规则和 `./plugins/...` 路径；Codex 的市场带有 `source.path`、`policy` 和 `category`；六个插件的四份清单版本号一致；技能内容的指纹和 lock 文件一致；104 个翻译技能的文件夹名和 `name` 一致，并且上一级真的有它点名的许可证文件。

准备这个仓库时还跑过官方命令 `claude plugin validate`（Claude Code 2.1.302）。市场目录和六个插件都显示 Validation passed。这个命令接受了中文技能名。它检查的是清单格式，不会模拟上面说的「中文被换成连字符」那种运行时行为。Cursor 的清单另外用官方 JSON Schema 校验过。CodeBuddy 自己的 `codebuddy plugin validate` 这次没有跑。`.codebuddy-plugin/` 里的清单和已经通过 Claude 校验的 `.claude-plugin/` 清单内容相同，字段按 CodeBuddy 官方文档填写。
