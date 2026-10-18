# S 的中文技能市场

这个仓库是 S 自己的**插件市场**。插件市场就是一份目录，里面列出可以安装的插件。现在目录里有两个插件：`s` 和 `s-ui`。插件是一组技能。技能（skill）是一份写给 AI 助手看的说明书，文件名固定叫 `SKILL.md`，开头有名字和说明，后面是具体步骤。

技能正文是中文。同一份文件给 WorkBuddy、Cursor、Claude Code 用。改完合并进 `main` 分支之后，已经安装的应用可以收到更新。Codex 和 OpenCode 用各自的装法，读的也是这一份文件。

仓库是公开的，这是 S 自己的选择。

## 里面有什么

2 个插件，78 个技能。技能文件只存一份，放在各自插件的 `skills/`。几个应用的清单都指向这些文件夹，没有为每个应用再复制一份技能。两个子智能体的短文件在 `plugins/s/agents/`。

| 插件短名 | 数量 | 里面是什么 |
|---|---|---|
| `s` | 61 | s 的中文技能：做事原则、工作流程、TypeScript 写法 |
| `s-ui` | 17 | 界面设计、动画和选前端库。不含 Figma |

插件短名是给应用看的，只能用小写英文字母、数字和连字符。技能的名字保持中文。

目录长这样：

```text
.cursor-plugin/marketplace.json      Cursor 的市场目录
.claude-plugin/marketplace.json      Claude Code 的市场目录
.codebuddy-plugin/marketplace.json   WorkBuddy / CodeBuddy 的市场目录
.agents/plugins/marketplace.json     Codex 的市场目录
plugins/s/
  plugin.json                        Codex 和通用插件格式用的清单
  .cursor-plugin/plugin.json
  .claude-plugin/plugin.json
  .codebuddy-plugin/plugin.json
  LICENSE                            pstack 的 MIT 许可证全文
  LICENSE-cursor-team-kit            cursor-team-kit 的 MIT 许可证全文
  agents/
    专挑注释.md
    s助手.md
  skills/
    <技能名>/SKILL.md
plugins/s-ui/
  plugin.json
  .cursor-plugin/plugin.json
  .claude-plugin/plugin.json
  .codebuddy-plugin/plugin.json
  LICENSE-emilkowalski-skills
  LICENSE-impeccable
  LICENSE-ui-ux-pro-max
  LICENSE-vercel-agent-skills
  NOTICE-impeccable.md
  skills/
    <技能名>/SKILL.md
```

## 许可证

这些技能大部分改自 Lauren Tan 的 pstack（MIT 许可证，版权 © 2026 Lauren Tan）。许可证全文在 `plugins/s/LICENSE`。`专挑注释` 和 `s助手` 也来自这份许可证，原文是 pstack 的子智能体。

`清理代码腔`、`操作命令行`、`操作界面` 改自 Cursor 的 cursor-team-kit（作者 Eric Zakariasson，MIT 许可证，版权 © 2026 Cursor）。许可证全文在 `plugins/s/LICENSE-cursor-team-kit`。来源仓库是 https://github.com/cursor/plugins 。

`编写skill` 和 `定时循环` 是按 Cursor 公开文档写的，内置技能原文没有公开，标为自写。没有上游许可证可附。

`s-ui` 的许可证按来源分开，全文都在 `plugins/s-ui/`：

| 技能 | 来源 | 作者 | 许可证 |
|---|---|---|---|
| `Emil设计理念`、`Expo动画`、`Sonner用法`、`做动画`、`动画审查`、`动画性能`、`动画改进计划`、`动画术语表`、`手机原生手感`、`找动画机会`、`界面压力测试`、`选前端库`、`苹果式设计`、`多版本原型` | https://github.com/emilkowalski/skills （commit 2d22863） | Emil Kowalski | MIT，版权 © 2026 Emil Kowalski。全文 `LICENSE-emilkowalski-skills` |
| `精致界面设计` | https://github.com/pbakaus/impeccable （cursor-plugin/skills/impeccable，版本 4.6.0，commit 08d5b47） | Paul Bakaus | Apache 2.0，版权 © 2025 Paul Bakaus。全文 `LICENSE-impeccable`。第三方说明 `NOTICE-impeccable.md`（其中 iOS / Android 参考来自 ehmo 的 platform-design-skills，MIT） |
| `UIUX知识库` | https://github.com/nextlevelbuilder/ui-ux-pro-max-skill （commit 56ea9cf） | Next Level Builder | MIT，版权 © 2024 Next Level Builder。全文 `LICENSE-ui-ux-pro-max` |
| `网页设计规范` | https://github.com/vercel-labs/agent-skills （skills/web-design-guidelines，commit 063bee9） | Vercel | MIT。上游仓库没有单独的 LICENSE 文件，只在 README 里写了 MIT。摘录在 `LICENSE-vercel-agent-skills` |

## 中文名对照表

61 个技能。调用时用中文名。表里的「英文名」是以前的英文备份，技能文件里已经没有这一行。后加的 7 个没有英文备份，这一列写上游英文名。「原始 skill」是改写前的英文名。标 ⚠️ 的，表示它的 `references/` 参考文件还是英文。

| 中文名 | 英文名 | 原始 skill | 用途 |
|---|---|---|---|
| `测试驱动修bug` | `s-tdd` | `tdd` | 修 bug 时先写一个会失败的测试，再修到它通过（只在明确要求或很容易测时用）。 |
| `一步步教我` | `s-teach` | `teach` | 像老师一样，一步一步把一块工作讲到你真正弄懂。 |
| `技术写作` | `s-technical-writing` | `technical-writing` | 技术文档写作规范（原本针对英文写作），用于写文档、readme、PR 说明、提交信息。 |
| `按我习惯定制` | `s-automate-me` | `automate-me` | 从你的对话习惯里总结规则，做成一个“按你的方式工作”的专属 skill。 |
| `poteto工作模式` ⚠️ | `s-poteto-mode` | `poteto-mode` | s 的总入口：按任务类型匹配一套操作手册（playbook），照着步骤做，按需调用其他 skill，并用原则指导每个决定。 |
| `设置s模型` | `s-setup` | `setup-s` | 检测你能用的模型，按角色设置 s 用哪个模型、推理预算多大，写成一条始终生效的规则。 |
| `s使用帮助` | `s-poteto-help` | `poteto-help` | 回答“s 怎么用、该用哪个 skill”，给你一段可以直接发的提示词。 |
| `动手前磨清任务` | `s-sharpen` | `sharpen` | 开始前先想清楚：专家会怎么做、你真正想要什么、要求写得太死还是太含糊。 |
| `复述用户目标` | `s-in-your-own-words` | `in-your-own-words` | 让助手用自己的话复述你的目标和要解决的问题，确认它没理解错。 |
| `先画架构草图` | `s-architect` | `architect` | 写代码前先勾勒类型、函数签名和模块结构（多个模型并行设计），再照着草图实现。 |
| `多方案竞技场` | `s-arena` | `arena` | 同一个任务同时派出多个候选者，选一个做基础，再把其他候选的长处嫁接进来。 |
| `并行群体作战` | `s-swarm` | `swarm` | 同时派出 N 个并行工作者（分片或比赛），等全部完成，汇总成一份报告。 |
| `自定流程搞定` | `s-figure-it-out` | `figure-it-out` | 没有现成流程可用时（大迁移、复杂改动、通宵任务），自己设计一套严谨、可审计的做法。 |
| `TypeScript最佳实践` | `s-typescript-best-practices` | `typescript-best-practices` | 读写 .ts / .tsx 文件时的 TypeScript 规则：可辨识联合类型、品牌类型、不用 as 断言等，附代码示例。 |
| `清理代码注释` | `s-no-comments` | `no-comments` | 派出 `专挑注释`，删掉多余或掩盖问题的注释，并把注释里的限制改成代码强制执行。 |
| `根除重复错误` | `s-correct` | `correct` | 找出助手在这个仓库里反复犯的错，用架构、类型、lint、测试让它们不可能再犯。 |
| `决定记录日志` | `s-show-me-your-work` | `show-me-your-work` | 长时间或无人值守的工作中，用 TSV 日志记下每个决定（做了什么、为什么、证据、结果），最后自查并让另一个模型审一遍。 |
| `s做Bot界面` | `s-make-bot-ui` | `make-bot-ui` | 做一个按钮能通过 webhook 唤醒 Grok Bot 的网页界面，并放到 Tailscale 上访问。改名是为了和你自己的 `make-bot-ui` 区分。 |
| `多模型对抗审查` | `s-interrogate` | `interrogate` | 让多个不同的模型对抗式审查代码改动，再由主审把发现分成要处理 / 值得考虑 / 记录 / 驳回。 |
| `改动影响范围` | `s-blast-radius` | `blast-radius` | 找出一个改动在 diff 之外可能弄坏什么，并用真实运行的代码证明它安全所依赖的那个事实。 |
| `基准测试清单` | `s-benchmark-checklist` | `benchmark-checklist` | 报告性能数字之前的 7 个检查问题：限制因素、调优、物理极限、出错、可复现、是否重要、工作是否真的发生了。 |
| `创建验证skill` | `s-create-verification-skill` | `create-verification-skill` | 为项目生成一个“像用户一样操作应用并证明行为”的验证 skill，附功能地图。 |
| `维护验证skill` | `s-maintain-verification-skill` | `maintain-verification-skill` | 定期检查验证 skill 和功能地图是否还和应用对得上，只提交已证明的修正。 |
| `清理AI腔` | `s-unslop` | `unslop` | 按一份编号规则清单去掉文字里的 AI 腔（原本针对英文写作，例子保留英文并附中文意思）。和 `去AI腔` 作用相近，来源不同。管的是文字，不管代码。 |
| `清理代码腔` | `deslop` | `deslop` | 去掉 diff 里新引进的 AI 代码腔：多余注释、反常的防御或 `try/catch`、为了逃类型而用的 `any`、过深的嵌套。和 `清理AI腔` 不是同一件事。 |
| `操作命令行` | `control-cli` | `control-cli` | 搭一个本地驾驭装置，驱动并查看交互式命令行或 TUI。 |
| `操作界面` | `control-ui` | `control-ui` | 搭一个本地浏览器或 CDP 驾驭装置，驱动并查看网页、IDE 或 Electron 界面。 |
| `编写skill` | `create-skill` | `create-skill` | 自写。按 Cursor 的 Agent Skills 文档起草一份 `SKILL.md`。菜单里有内置 `/create-skill` 时用内置的。 |
| `定时循环` | `/loop` | `/loop` | 自写。按一个能判定通过或失败的条件反复检查。Cursor 菜单里有 `/loop` 时交给它。别的软件没有文档化的叫醒命令。 |
| `专挑注释` | `comment-sicko` | `comment-sicko` | 子智能体。被 `/清理代码注释` 派出去删注释。短文件在 `agents/专挑注释.md`。 |
| `s助手` | `poteto-agent` | `poteto-agent` | 子智能体。动手前完整读 `poteto工作模式`。短文件在 `agents/s助手.md`。 |
| `反思并改skill` | `s-reflect` | `reflect` | 用三个审查子智能体回看本次对话，总结出持久有用的经验，经你批准后改进对应的 skill。 |
| `代码怎么工作` | `s-how` | `how` | 探索代码库，讲清“X 是怎么工作的”、新代码该放在哪里。 |
| `代码为什么这样` ⚠️ | `s-why` | `why` | 查 git 历史、工单、文档、聊天、监控等来源，讲清代码为什么是现在这个样子，并标明可信度。 |
| `回想最近工作` | `s-recall` | `recall` | 从你的聊天记录和共享记录里，重建你最近在某件事上的工作进度，给一份简报。 |
| `补上对话进度` | `s-ketchup` | `ketchup` | 用几句大白话和小图，告诉你自从你上一条消息之后这个对话里发生了什么、哪些事需要你决定。 |
| `说人话重讲` | `s-bro` | `bro` | 把上一条消息用不带行话的大白话重新说一遍（很短）。 |
| `原则-质疑前提` | `s-principle-attack-the-premise` | `principle-attack-the-premise` | 同一个前提的修复失败两次以上，就先验证前提本身。 |
| `原则-守住边界` | `s-principle-boundary-discipline` | `principle-boundary-discipline` | 校验和错误处理集中在系统边界，内部信任类型。 |
| `原则-打造杠杆` | `s-principle-build-the-lever` | `principle-build-the-lever` | 不简单的工作，写个脚本或工具来做或来证明，而不是手工做。 |
| `原则-教训写进结构` | `s-principle-encode-lessons-in-structure` | `principle-encode-lessons-in-structure` | 同一条指示写第二次时，改成 lint、检查或脚本。 |
| `原则-穷尽设计空间` | `s-principle-exhaust-the-design-space` | `principle-exhaust-the-design-space` | 没有先例的设计，先做 2-3 个原型比较。 |
| `原则-体验优先` | `s-principle-experience-first` | `principle-experience-first` | 让用户满意优先于实现方便；少而精。 |
| `原则-解释数字` | `s-principle-explain-the-number` | `principle-explain-the-number` | 相信一个测出来的数字前，先找出限制它的因素。 |
| `原则-修根本原因` | `s-principle-fix-root-causes` | `principle-fix-root-causes` | 调试时修第一次出错的地方，而不是症状。 |
| `原则-基础优先` | `s-principle-foundational-thinking` | `principle-foundational-thinking` | 先定数据结构和脚手架，再写逻辑。 |
| `原则-守住上下文` | `s-principle-guard-the-context-window` | `principle-guard-the-context-window` | 大块内容交给子智能体，主线程只留摘要。 |
| `原则-偷懒守则` | `s-principle-laziness-protocol` | `principle-laziness-protocol` | 倾向删除和最小改动。 |
| `原则-操作幂等` | `s-principle-make-operations-idempotent` | `principle-make-operations-idempotent` | 操作运行多少次、中途崩在哪，都收敛到同一个结果。 |
| `原则-迁完再删旧API` | `s-principle-migrate-callers-then-delete-legacy-apis` | `principle-migrate-callers-then-delete-legacy-apis` | 新内部 API 上线时，同一轮迁移调用方并删掉旧的。 |
| `原则-减轻读者负担` | `s-principle-minimize-reader-load` | `principle-minimize-reader-load` | 减少要追踪的层数和要记住的状态。 |
| `原则-为领域建模` | `s-principle-model-the-domain` | `principle-model-the-domain` | 用状态机、类型模型等结构代替散落的条件判断。 |
| `原则-别卡着等人` | `s-principle-never-block-on-the-human` | `principle-never-block-on-the-human` | 可撤销的事直接做，再汇报；不可撤销的才问。 |
| `原则-结果导向` | `s-principle-outcome-oriented-execution` | `principle-outcome-oriented-execution` | 计划内的重写直接奔向目标架构，不留临时兼容代码。 |
| `原则-证明真能用` | `s-principle-prove-it-works` | `principle-prove-it-works` | 对照真实产物验证，不靠“能编译”或自我汇报。 |
| `原则-从头重新设计` | `s-principle-redesign-from-first-principles` | `principle-redesign-from-first-principles` | 整合新需求时，当它从一开始就存在那样重新设计。 |
| `原则-先分开共享状态` | `s-principle-separate-before-serializing-shared-state` | `principle-separate-before-serializing-shared-state` | 并发写同一状态时，先消除共享，再考虑加锁。 |
| `原则-可验证小单元` | `s-principle-sequence-verifiable-units` | `principle-sequence-verifiable-units` | 拆成每步都能检查的小单元，按能证明自己的顺序交付。 |
| `原则-先减后加` | `s-principle-subtract-before-you-add` | `principle-subtract-before-you-add` | 先删死代码和多余部分，再搭建。 |
| `原则-测行为不测实现` | `s-principle-test-behavior-not-implementation` | `principle-test-behavior-not-implementation` | 测试断言使用者能看到的行为，不绑定内部实现。 |
| `原则-类型系统纪律` | `s-principle-type-system-discipline` | `principle-type-system-discipline` | 让非法状态无法表示，在边界解析外部数据。 |

## s-ui 的中文名

17 个技能。调用时用中文名，插件短名是 `s-ui`。这一列的英文名是上游 skill 名。不含任何 Figma 技能。

| 中文名 | 上游 skill | 用途 |
|---|---|---|
| `Emil设计理念` | `emil-design-eng` | Emil Kowalski 的界面打磨、组件和动画判断。 |
| `Expo动画` | `animate-expo` | 在 React Native / Expo 里做动画。网页动画用 `做动画`。 |
| `Sonner用法` | `ask-sonner` | Sonner 提示消息的安装、调用和常见问题。 |
| `UIUX知识库` | `ui-ux-pro-max` | 可搜索的界面风格、配色、字体和 UX 准则。数据文件保持英文。 |
| `做动画` | `animate` | 从零做一个网页动画，并写出实现。 |
| `动画审查` | `review-animations` | 按高手艺标准挑现有动画的问题。要明确调用才会用。 |
| `动画性能` | `animation-performance` | 让网页动画留在每帧的时间预算里。 |
| `动画改进计划` | `improve-animations` | 只读审计整个代码库的动效，写出给别人执行的计划。 |
| `动画术语表` | `animation-vocabulary` | 把口头描述的动效换成准确的英文术语。 |
| `手机原生手感` | `mobile-native` | 让网页在手机上少一点浏览器感。 |
| `找动画机会` | `find-animation-opportunities` | 找出该动、以及不该动的地方。只读。 |
| `界面压力测试` | `break-ui` | 用超长名字、空数据、emoji 等最坏情况把界面搞坏。 |
| `精致界面设计` | `impeccable` | 设计、审查、打磨网页和原生界面。参考文件保持英文。 |
| `网页设计规范` | `web-design-guidelines` | 按 Vercel 的网页界面规范检查代码。 |
| `选前端库` | `pick-ui-library` | 从一份带观点的清单里挑前端库。要明确调用才会用。 |
| `苹果式设计` | `apple-design` | 把苹果的界面和动效做法用到网页上。 |
| `多版本原型` | `prototype` | 同一块界面做几个真能切换的版本，再选定一个。 |

## 合并进 main 之后怎么装

市场短名是 `s-skills`。插件短名是 `s` 和 `s-ui`。`s@s-skills` 的意思是：市场 `s-skills` 里的插件 `s`。`s-ui@s-skills` 是同一个市场里的设计与动画插件。两个可以分开装。

还没合并、想先试用这条分支时，看下一节。

### WorkBuddy（腾讯，底层是 CodeBuddy Code）

在 WorkBuddy 的对话里输入：

```text
/plugin marketplace add Acefake/s-skills
/plugin install s@s-skills
/plugin install s-ui@s-skills
/reload-plugins
```

`/plugin` 是插件管理命令。`marketplace add` 是把这个 GitHub 仓库登记成一个市场。`install` 是安装里面的插件。只要设计与动画，可以不装 `s`，只留 `s-ui` 那一行。`/reload-plugins` 是重新加载插件，不用退出应用。

### Claude Code

命令和 WorkBuddy 一样，在对话里输入：

```text
/plugin marketplace add Acefake/s-skills
/plugin install s@s-skills
/plugin install s-ui@s-skills
/reload-plugins
```

也可以在终端里运行 `claude plugin marketplace add Acefake/s-skills`，然后 `claude plugin install s@s-skills` 和 `claude plugin install s-ui@s-skills`。只要其中一个插件，就只装那一个。

### Cursor

Cursor 用仓库里的 `.cursor-plugin/marketplace.json` 把整个仓库当成一个市场。

团队版（Teams 或 Enterprise，需要管理员）：

1. 打开 Cursor 的 Dashboard，进入 Plugins & MCPs（插件和 MCP）。
2. 在 Team Marketplaces（团队市场）里选 Import from Repo（从仓库导入）。
3. 粘贴 `https://github.com/Acefake/s-skills`。
4. 确认它列出了插件 `s` 和 `s-ui`，保存。
5. 在 Cursor 侧边栏的 Customize（自定义）里安装要的插件。安装时可选「只给自己」或「这个项目」。只要设计与动画，装 `s-ui`。

个人用的 Cursor 也可以在 Customize → Plugins 里找 Import marketplace / Add marketplace（导入市场），粘贴同一个仓库地址。2026-10-18 的官方文档把导入步骤写在团队市场那一节；个人界面上的入口名称以你本机菜单为准。导入这一步我没有在 Cursor 里点过。

不想走市场时，可以用下面的「skills 命令」把技能装进 Cursor。

### Codex

Codex 现在有插件市场。官方说明写在 [Build plugins](https://developers.openai.com/plugins/build/plugins)。这个仓库按那个格式放了 `.agents/plugins/marketplace.json`。在终端：

```text
codex plugin marketplace add Acefake/s-skills
```

然后打开 Codex，输入 `/plugins`，安装 `s` 或 `s-ui`。装完新开一个对话再用。

Codex 还会顺带读取 `.claude-plugin/marketplace.json` 和 `.cursor-plugin/marketplace.json`。这三个文件都列了同样的两个插件，所以 Codex 里可能看到重复的条目。装其中一个来源即可。这一重复我没有在 Codex 里打开确认过。

Codex 的 IDE 扩展不支持插件。要用插件，打开 Codex 命令行，或 ChatGPT 桌面版里的 Codex。

### OpenCode

OpenCode 到 2026-10-18 还没有官方的插件市场。它会从本机的技能文件夹读取 `SKILL.md`。用下面的 skills 命令装到 OpenCode。

### skills 命令（Codex、OpenCode、也可以给 Cursor）

[vercel-labs/skills](https://github.com/vercel-labs/skills) 是一个安装技能的命令行工具。它会在仓库里找 `SKILL.md`。这个仓库的 Claude 市场清单写了插件路径，它能顺着路径找到 `plugins/s/skills/<技能名>/` 和 `plugins/s-ui/skills/<技能名>/`。只装设计与动画时，用 `--skill` 点名，或者装完再卸掉 `s` 里的技能。`--list` 会把两个插件的技能列在一起。

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

## 合并前先试这条分支

分支名是 `cursor/add-s-ui-plugin-2463`。不带分支名时，装到的是 `main`。`main` 上已经有 `s`。这条分支加上 `s-ui`。要在合并前试用，用下面带分支的命令。

**WorkBuddy。** 官方文档对 Git 地址写了「地址后面加 `#` 再加分支或标签」。用完整地址：

```text
/plugin marketplace add https://github.com/Acefake/s-skills.git#cursor/add-s-ui-plugin-2463
/plugin install s-ui@s-skills
/reload-plugins
```

WorkBuddy 文档里的 GitHub 短写例子是 `owner/repo`，没有写 `#分支`。完整 Git 地址这一条是文档写了的。我没有在 WorkBuddy 里跑过这条命令。

**Claude Code。** 官方文档写明 GitHub 短写可以加 `#分支`：

```text
/plugin marketplace add Acefake/s-skills#cursor/add-s-ui-plugin-2463
/plugin install s-ui@s-skills
/reload-plugins
```

**Codex。** 官方命令可以用 `--ref` 指定分支：

```text
codex plugin marketplace add Acefake/s-skills --ref cursor/add-s-ui-plugin-2463
```

然后在对话里用 `/plugins` 安装 `s-ui`。我没有在 Codex 里跑过。

**OpenCode，以及合并前给 Cursor / Codex 装技能。** skills 命令用 `#` 后面跟分支名（分支名里有斜杠，所以整段要加引号）：

```text
npx skills add "Acefake/s-skills#cursor/add-s-ui-plugin-2463" -g -a opencode -a cursor -a codex -y
```

只要其中一个应用，就只留一个 `-a`。先看有哪些技能、不安装：

```text
npx skills add "Acefake/s-skills#cursor/add-s-ui-plugin-2463" --list
```

不要用 `https://github.com/Acefake/s-skills/tree/cursor/add-s-ui-plugin-2463`。这个命令把 `tree/` 后面的第一段当成分支名，斜杠后面当成子目录，会指错地方。

**Cursor 的市场导入。** 官方文档写的是粘贴仓库地址，没有写导入时怎么选分支。导入后跟的是仓库的默认分支 `main`。合并前 `main` 还没有 `s-ui`，所以这条导入先不要做。合并前想在 Cursor 里试用，用上面的 skills 命令，`-a cursor`。

## 装上之后怎么调用

应用会把插件短名加在技能名前面，中间用冒号。这叫命名空间，用来避免和别的插件撞名。

在 WorkBuddy 和 Claude Code 里，输入：

```text
/s:先画架构草图
/s-ui:做动画
```

斜杠 `/` 是调用命令。冒号前面是插件短名，后面是技能的中文名。没有别的命令占用这个中文名时，只打 `/先画架构草图` 或 `/做动画` 往往也能用。助手也可以在任务对得上技能开头的说明时，自己去读那份说明书。

Cursor 里在对话输入 `/`，搜索技能的中文名。官方文档写的形式是 `/技能名`。如果列表里显示成带插件短名的，就选带短名的那一项。

Codex 里输入 `@`，选择插件或其中的技能。

OpenCode 把技能交给内置的 skill 工具，按说明书开头的说明决定要不要读全文。这 78 个文件没有额外写 OpenCode 专用的开关，所以不一定出现成一条 `/中文名` 命令。直接说出技能的中文名，让它按那份说明书做。

## 中文名能不能被认出来

技能文件夹和说明书里的 `name` 都是中文。插件短名是英文。下面是 2026-10-18 对照官方文档和已知问题后的判断。标了「未实测」的，是没有在那个应用里真正安装过。

- **WorkBuddy / CodeBuddy。** 官方文档要求插件短名是英文短横线格式，没有要求技能名必须是英文。调用形式是 `插件短名:技能名`。S 原来的备份说明里写过：中文名可以在 WorkBuddy 里直接用。这次没有在 WorkBuddy 里安装验证。
- **Claude Code。** 官方文档写：插件里的技能，命令最后一段用说明书里的 `name`，所以形式上会是 `/s:先画架构草图`。个人技能文件夹（`~/.claude/skills/中文名/`）可以保留中文。插件这条路径上有一个已报告的问题：[claude-code#66554](https://github.com/anthropics/claude-code/issues/66554)。从 2.1.94 起，插件技能名里英文、数字、下划线、连字符以外的字符会被换成连字符 `-`。中文每个字都会变成一个 `-`，字数相同的技能会撞成同一个名字，助手按中文名去调用会得到 Unknown skill。例如「一步步教我」和「说人话重讲」都是五个字，会挤成同一个 `s:-----`。个人技能不受这个影响。这个问题我没有在本机的 Claude Code 里复现，只核对了问题报告和当时的改动说明。技能正文因此没有改成英文名。
- **Cursor。** 官方文档把技能 `name` 写成小写英文加连字符，并且要和文件夹名一致。Cursor 命令行会给不合这个格式的名字打警告（名字超过 64 字、不是小写短横线、名字和文件夹不一致、说明超过 1024 字、正文大约超过 5000 个词）。文档写的是警告，没有写「直接拒绝加载」。中文名会触发「不是小写短横线」和「名字与文件夹不一致」这两类警告。能否在插件里真正跑起来，未实测。
- **skills 命令。** 它清理名字时只去掉会扰乱终端的控制字符，中文会留下来。发现技能时会读 `.claude-plugin/marketplace.json`，再进入插件的 `skills/`。本地用 skills 命令 1.5.18 对这个仓库目录跑过 `--list`，它列出 78 个技能，中文名都在。真正写进 Codex、OpenCode 或 Cursor 的安装目录这一步未实测。
- **Codex 插件。** 官方示例里的技能名是英文短横线。中文文件夹放进 Codex 插件之后能不能点开，未实测。装不上时，用上面的 skills 命令，目标应用写 `codex`。
- **OpenCode。** 官方文档只要求 `name` 和 `description`，没有要求英文。它从 `~/.config/opencode/skills/<名字>/SKILL.md` 读取。未实测。

如果某个应用把中文插件技能压坏了，同一批文件仍可以用 skills 命令装到那个应用的个人技能目录。Claude Code 的个人技能路径目前会保留中文名。那是另一条安装方式，不会走插件版本号。

## 更新怎么发生

分两条路。

**插件市场（WorkBuddy、Claude Code、Codex 的插件安装）。** 应用把插件复制到本机的一个缓存目录。WorkBuddy 和 Claude Code 的官方文档写明：已经安装的插件，要等它的**版本号**变了，才会换成新的一份。版本号写在 `s` 的四份清单里（`plugin.json`、`.cursor-plugin/plugin.json`、`.claude-plugin/plugin.json`、`.codebuddy-plugin/plugin.json`），现在是 `1.1.2`。市场目录里故意不再写一遍版本号。官方文档说两处都写的话，以 `plugin.json` 为准，并且校验命令会警告它们不一致。

所以：改了 s 里的技能或许可证之后，要让别人的应用收到，必须把版本号加大，再合并。只合并文件、不改版本号，WorkBuddy 和 Claude Code 会继续用旧缓存。

加大版本号：

```text
python3 scripts/bump_plugin_version.py s
```

或者：

```text
python3 scripts/bump_plugin_version.py --all
```

现在只有 `s`，两条命令效果一样。脚本只把最后一位加 1，例如 `1.1.0` 变成 `1.1.1`。它同时改四份清单和 `plugin-versions.lock.json`。这个 lock 文件记下「这一版对应的文件内容指纹」。内容变了却没加大版本号时，`python3 scripts/check_marketplace.py` 会失败，GitHub 上的检查也会失败。内容没变时，脚本不改版本号。

想把 `1.0.1` 改成 `1.1.0` 或 `2.0.0`：手动改 lock 文件里的 `version`，以及该插件四份清单里的 `version`，再跑检查。内容指纹对得上、五处版本号一致，检查就会通过。

**Cursor 团队市场**的官方文档另外说：打开 Enable Auto Refresh（自动刷新）之后，仓库一推送，Cursor 会重新读市场（大约最多每 10 分钟一次），跟的是它正在跟踪的那个分支上的新提交。这需要仓库安装了 Cursor 的 GitHub App。个人导入的刷新方式以 Cursor 当时的界面为准。

**skills 命令**不看 `1.0.0` 这种版本号。`npx skills update -g` 会对照 GitHub 上的文件重新装。如果当初是用 `#分支名` 装的，更新仍对着那条分支，合并进 `main` 之后要改成从 `Acefake/s-skills` 重装一次。

### 第三方市场默认不会自动更新

WorkBuddy / CodeBuddy 和 Claude Code 都是：官方市场默认自动更新，**别人的市场默认关闭**。这个仓库属于后者。关掉时，合并新版本之后，要自己在对话里运行：

```text
/plugin marketplace update s-skills
```

或者按插件更新，例如在终端运行 `claude plugin update s@s-skills`（WorkBuddy 里是对应的 `codebuddy` 命令，对话里也可以用 `/plugin` 的更新入口）。

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
/plugin uninstall s@s-skills
/plugin uninstall s-ui@s-skills
```

连市场一起去掉：

```text
/plugin marketplace remove s-skills
```

去掉市场时，从它装上的插件会一起卸掉。

Cursor：在 Customize 里找到已安装的 `s` 或 `s-ui`，选卸载。团队市场由管理员在 Dashboard 的 Team Marketplaces 里移除。

Codex：在 `/plugins` 里对 `s` 或 `s-ui` 选卸载。终端里移除市场：

```text
codex plugin marketplace remove s-skills
```

skills 命令装上的，按应用卸：

```text
npx skills remove --agent opencode --skill '*' -g
```

把 `opencode` 换成 `codex` 或 `cursor` 即可。不加 `--skill '*'` 时，命令会让你选择要卸哪些。

## 插件里的脚本在 Windows 上怎么跑

`plugins/s/skills/poteto工作模式/scripts/` 里的测试要用 [Bun](https://bun.sh)。`决定记录日志/scripts/log.sh` 和 `poteto工作模式/scripts/worktree-audit.sh` 是 bash。Windows 的 PowerShell 跑不了它们，请用 Git Bash 或 WSL。`worktree-audit.sh` 还需要本机有 `git`、`jq` 和 `rg`。`check-plan.mjs` 和 `watch-pr` 是 Node，PowerShell 里可以用 `node` 跑。这些脚本这次在 Linux 上跑过。Windows 上没有这台机器，只根据命令差异做了修改，没有在 PowerShell 或 Git Bash 里实际跑过。

## 改完怎么自己检查

```text
pip install "jsonschema>=4.20"
python3 scripts/check_marketplace.py
```

检查这些事：Cursor 的两份清单符合官方 JSON Schema；Claude Code 和 CodeBuddy 的市场字段符合官方文档里的名字规则和 `./plugins/<插件短名>` 路径；Codex 的市场带有 `source.path`、`policy` 和 `category`；每个插件的四份清单版本号一致；技能内容的指纹和 lock 文件一致；78 个技能的文件夹名和 `name` 一致。

准备这个仓库时还跑过官方命令 `claude plugin validate`（Claude Code 2.1.302）。市场目录、`s` 和 `s-ui` 都显示 Validation passed。这个命令接受了中文技能名。它检查的是清单格式，不会模拟上面说的「中文被换成连字符」那种运行时行为。Cursor 的清单另外用官方 JSON Schema 校验过。CodeBuddy 自己的 `codebuddy plugin validate` 这次没有跑。`.codebuddy-plugin/` 里的清单和已经通过 Claude 校验的 `.claude-plugin/` 清单内容相同，字段按 CodeBuddy 官方文档填写。
