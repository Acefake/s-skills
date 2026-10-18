# S 的中文技能库

这里放的是 S 自己用的一套中文 AI 技能。技能（skill）就是一份写给 AI 助手看的“做事说明书”：一个文件夹，里面主要是 `SKILL.md`。文件开头有名字和说明，后面是具体步骤。

这 104 个翻译过来的技能，文件夹名和正文里的名字都是中文。每个 `SKILL.md` 开头写了它来自哪个插件、原作者和许可证，并有一行 `英文名备份`。另外 5 个是 S 自己写的，内容是英文。**技能正文这次没有改。**

仓库地址：<https://github.com/Acefake/s-skills>

## 文件夹里有什么

技能按来源分开放。来源就是原来的插件或仓库。每个来源文件夹里放着该来源的许可证（允许别人怎么使用这些文字的法律说明）。技能正文里写“许可证在上一级文件夹”，所以许可证和技能文件夹是挨着的。

```
s-skills/
├── README.md                 这份说明
├── skills.json               分组和技能名单，安装脚本读它
├── 安装技能.cmd               在 Windows 上双击这个来安装或更新
├── scripts/
│   ├── install.ps1           真正做事的脚本（PowerShell）
│   ├── install.cmd           和上面那个双击文件一样，只是放在 scripts 里
│   ├── SSkills.ps1           安装脚本调用的内部文件
│   └── test-install.ps1      用来检查脚本是否按说的那样工作
└── skills/
    ├── pstack/               54 个，默认只装这一组
    ├── compound-engineering/ 15 个
    ├── superpowers/          1 个
    ├── ui-ux/                18 个，界面和动画
    ├── figma/                16 个，上游没有许可证
    └── my-skills/            5 个，S 自己写的
```

| 分组 id（安装时输入这个英文） | 数量 | 里面是什么 |
|---|---:|---|
| `pstack` | 54 | pstack 插件的全部技能。这是现在默认的一套。 |
| `compound-engineering` | 15 | 做计划、查 bug、提交代码、开 PR 这些。PR 就是“请别人把改动收进仓库”的申请。 |
| `superpowers` | 1 | 只有「完成前验证」：说做完之前要先真的跑一遍。 |
| `ui-ux` | 18 | Emil Kowalski 的设计和动画、impeccable、ui-ux-pro-max、Vercel 的网页规范。 |
| `figma` | 16 | Figma 官方技能。上游仓库没写许可证，见下面的说明。 |
| `my-skills` | 5 | 你自己的：`apple-design-2`、`design-a-grok-bot`、`make-bot-ui`、`routine-healthcheck`、`transcript-healthcheck`。 |

同一组里的技能如果互相引用，用的是“旁边那个文件夹”。装到软件里之后，它们仍然是邻居，这种引用还有效。

## 在 Windows 上安装和更新

脚本用你自己的用户文件夹，也就是 `C:\Users\你的用户名`。它不会把某一个用户名写死。

1. 最好先安装 [Git for Windows](https://git-scm.com/download/win)。Git 是用来从网上复制和更新这套文件的工具。没有 Git 也能装，脚本会改用网页上的压缩包；压缩包在老版本 Windows PowerShell 里偶尔会把中文文件夹名解坏，所以更推荐 Git。
2. 把这个仓库下载到电脑上。可以用浏览器下载压缩包再解压，也可以让 Git 克隆（clone，就是把网上的仓库复制到本机）。
3. 双击仓库里的 `安装技能.cmd`。如果中文文件名打不开，改双击 `scripts\install.cmd`。
4. 第一个问题直接回车：只装 `pstack` 这 54 个。想全装就输入 `all`。想自己挑，就输入英文 id，用逗号分开，例如 `pstack,figma,my-skills`。
5. 第二个问题直接回车：装进电脑上已经检测到的软件。没检测到的不会动。想指定就输入编号或英文 id，例如 `cursor,opencode`。输入 `all` 会连没检测到的软件一起装，并新建文件夹。
6. 看最后一段中文总结。

以后要更新，再双击一次。脚本会先去 GitHub 拿最新副本（这个仓库是公开的，不需要登录），再覆盖它自己以前装过的技能。

如果双击没反应：在仓库文件夹里按住 Shift，右键，选“在此处打开 PowerShell 窗口”，粘贴下面这一行再回车。

```
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1
```

`ExecutionPolicy` 是 Windows 用来拦住陌生脚本的开关。`Bypass` 只对这一次生效，不会改电脑的总设置。

只看会做什么、先不改文件：

```
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1 -Preview
```

## 会装到哪里

脚本只往下面这些**用户级**文件夹里复制。用户级的意思是：这个 Windows 用户打开的所有项目都能用，不是只对某一个项目生效。装进去的是一个个技能文件夹，不再套来源那一层，这样 WorkBuddy、Cursor、Codex、OpenCode、Claude Code 用的是同一套文件夹。

| 软件 | 英文 id | 技能文件夹 | 怎样判断“已经安装了这个软件” | 依据 |
|---|---|---|---|---|
| WorkBuddy | `workbuddy` | `%USERPROFILE%\.workbuddy\skills` | 存在 `.workbuddy` 文件夹 | 腾讯云社区文章和 WorkBuddy 自带的创建技能示例用这个路径。官方技能市场页面只说“用户配置目录”，没有写死完整路径。 |
| CodeBuddy | `codebuddy` | `%USERPROFILE%\.codebuddy\skills` | 存在 `.codebuddy` 文件夹 | [workbuddy.cn 上的 CodeBuddy 说明](https://www.workbuddy.cn/docs/cli/skills) 写的是这个目录。WorkBuddy 和 CodeBuddy 共用一套引擎时会读到。没检测到就不会默认装。 |
| Cursor | `cursor` | `%USERPROFILE%\.cursor\skills` | 存在 `.cursor` 文件夹 | [Cursor 官方文档](https://cursor.com/docs/skills) |
| Codex（现行） | `codex` | `%USERPROFILE%\.agents\skills` | 存在 `.codex` 文件夹 | [OpenAI 现在的说明](https://learn.chatgpt.com/docs/build-skills) 把用户技能放在这里。 |
| Codex（旧目录） | `codex-legacy` | `%USERPROFILE%\.codex\skills` | 存在 `.codex` 文件夹 | OpenAI 说过这是旧位置，但旧版本还能读到。`npx skills` 1.7.2 装 Codex 时也用这里。默认不装，免得和现行目录重复。 |
| OpenCode | `opencode` | `%USERPROFILE%\.config\opencode\skills` | 存在 `.config\opencode` 文件夹 | [OpenCode 官方文档](https://opencode.ai/docs/skills/)。在 Windows 上，`~` 就是你的用户文件夹，不是 `%APPDATA%`。 |
| Claude Code | `claude` | `%USERPROFILE%\.claude\skills` | 存在 `.claude` 文件夹 | [Claude Code 官方文档](https://code.claude.com/docs/en/skills) |

`%USERPROFILE%` 就是你的用户文件夹，例如 `C:\Users\你的用户名`。

有两件事需要知道：

- Cursor 还会顺便读取 Claude Code、Codex 的技能文件夹。OpenCode 也会读取 Claude Code 和 `.agents\skills`。几个都装了的话，列表里可能看到重复的技能，内容是一样的。觉得烦，就下次只选一个软件。
- 有人报告 OpenCode 在 Windows 上读不到 `.agents\skills`，但读得到 `.config\opencode\skills`。所以 OpenCode 单独装一份。

## 再运行一次时，脚本会做什么

- 你这次选中的分组：装上新的，或把以前装过的更新成仓库里的版本。
- 以前装过、这次没选、仓库里还在的：留着，不删也不更新。
- 以前是这个脚本装的，但仓库里已经没有这个名字了：删掉。
- 不是这个脚本装的文件夹：不动。
- 如果要覆盖的文件夹不是这个脚本创建的，先把它挪到备份里。备份在 `%LOCALAPPDATA%\s-skills\backups`（一般是 `C:\Users\你的用户名\AppData\Local\s-skills\backups`）。AppData 是 Windows 放软件自己数据的隐藏文件夹。备份不放在技能目录里，免得软件把备份又当成一份技能。
- 每个软件的技能目录里会有一个 `s-skills-installed.json`。这是脚本的记账本，记下哪些技能和许可证是它复制的。不要删这个文件，否则下次脚本会以为那些文件夹是你自己的。

## 另一种办法：`npx skills`

[skills](https://github.com/vercel-labs/skills) 是 Vercel 做的一个安装命令，用法像 `npx skills add Acefake/s-skills`。`npx` 会临时下载并运行一个 Node.js 程序。2026-10-18 用它的 1.7.2 版在本机试过：

- 它能从这个仓库的 `skills/分组/技能名/SKILL.md` 布局里**找到**技能，包括中文名。布局因此保持这样，没有为了迁就它再改一遭。
- 真正安装时，它会把名字里不是英文小写、数字、点、下划线的字都去掉。中文名会变成同一个文件夹 `unnamed-skill`，104 个中文技能会互相覆盖。所以**不要用它来装这套中文技能**。
- 英文名的 `my-skills`（例如 `make-bot-ui`）可以被它正常安装。
- 这一版支持很多软件。和你有关的全局目录是：Cursor `~/.cursor/skills`，Claude Code `~/.claude/skills`，Codex `~/.codex/skills`，OpenCode `~/.config/opencode/skills`，CodeBuddy `~/.codebuddy/skills`。它没有 WorkBuddy。

请继续用上面的 `安装技能.cmd`。

## 中文名在有的软件里可能叫不出来

常见的技能规范要求名字只用小写英文字母、数字和短横线 `-`。这套翻译用的是中文名，正文没有改回英文。WorkBuddy 可以按中文名用。Cursor、Claude Code 也许能读到文件夹，但不一定能用 `/中文名` 这种命令叫出来。这里没有在那些软件里实际点过，只是按它们写下来的规则提醒你。

## 来源、作者和许可证

许可证是原作者允许别人怎么使用这些文字的说明。翻译时保留了原作者和许可证。下面的版本号是翻译当时用的那一版。

| 来源 | 作者 | 许可证 | 当时的版本 | 地址 |
|---|---|---|---|---|
| pstack | Lauren Tan | MIT | 插件 9717366，版本 0.15.25 | <https://github.com/cursor/plugins/tree/main/pstack> |
| Compound Engineering | Kieran Klaassen、Trevin Chow（Every） | MIT | 插件 680，版本 3.29.0 | <https://github.com/EveryInc/compound-engineering-plugin> |
| Superpowers | Jesse Vincent | MIT | 插件 684，版本 6.1.1 | 插件市场里的 Superpowers |
| Emil Kowalski skills | Emil Kowalski | MIT | commit `2d22863` | <https://github.com/emilkowalski/skills> |
| impeccable | Paul Bakaus | Apache 2.0 | commit `08d5b47` | <https://github.com/pbakaus/impeccable> |
| ui-ux-pro-max | Next Level Builder | MIT | commit `56ea9cf` | <https://github.com/nextlevelbuilder/ui-ux-pro-max-skill> |
| Vercel agent-skills | Vercel | 仓库没有单独的 LICENSE 文件，README 末尾写了 MIT | commit `063bee9` | <https://github.com/vercel-labs/agent-skills> |
| Figma 官方 skills | Figma | **没有找到许可证** | commit `f278942` | <https://github.com/figma/mcp-server-guide> |
| my-skills | S 自己 | 没有单独的许可证文件 |  | 本仓库 `skills/my-skills` |

MIT 的大意是：可以自己用、可以改，但要保留原作者和许可证原文。Apache 2.0 还要求留下 NOTICE，并说明改过什么。impeccable 的技能正文里已经写了“这是中文翻译”。

Figma 那一组在上游仓库里找不到 LICENSE 文件。S 知道这一点，仍然决定放进这个公开仓库给自己用。说明写在 `skills/figma/NOTICE-figma.md`。不要把“仓库是公开的”理解成“可以随便拿去商用或再发布”。

`my-skills` 是 S 自己写的，不在下面的对照表里。

## 中文名对照表

共 104 个。“英文名”是英文名版 `skills-backup-zh/` 里的名字；“原始 skill”是原插件或原仓库里的名字（英文原版正文里提到别的 skill 时，用的是这个原名；这个中文名版里已经换成了中文名）。标 ⚠️ 的表示参考文件还是英文。

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
