---
name: s使用帮助
description: 指导用户完成 s 的设置、使用 /poteto工作模式，以及为一个任务挑选合适的 skill、playbook 或原则。输入 /s使用帮助 加上你的问题。
disable-model-invocation: true
---

# Poteto 帮助

回答用户关于 s 的问题，给他一段可以直接发送的提示词，并附上答案出处的那个文件的链接。如果是一个求助的问题，不要开始干活。用户问的是“怎么做”，而一次 s 运行要花真实的 token，所以让用户自己去发那段提示词。

一条要求干活的消息，比如 “use s to fix this bug”（用 s 修这个 bug），不是求助问题。读 [`poteto工作模式`](../poteto工作模式/SKILL.md)，按它来干活，并提一次：用 Custom Mode（自定义模式）可以让它一直开着。

这个文件把各种问题对应到存放答案的 skill 和指南页面。细节以那些文件为准。在引用你要指向的文件之前，先读它；当它和这份对应表不一致时，相信它。这里的链接指向已安装的插件，用户可能打不开，所以给用户这个文件的公开副本：`https://github.com/Acefake/s-skills/blob/main/plugins/s/` 后面接上它的路径。

## 弄清楚他们需要什么

从消息和对话里推断需求。一个点了名的情况，比如“哪个 skill 用来审查 PR？”，直接去对应的那一节。如果需求还是不清楚，就问一个选择题，选项如下，然后只回答他们选的那一节：

- 安装设置
- 用 `/poteto工作模式` 开始一个任务
- 为某个情况挑一个 skill
- 修好一次出了问题的运行
- 把 s 变成自己的

检查那些会改变答案的状态，只有当它确实改变答案时才提：

- 没有 `~/.cursor/rules/s-models.mdc`，说明这个用户还没运行过 `/设置s模型`，所以每个角色都用它的默认模型。
- 项目里没有 `verify-*` skill 或其他操作应用的测试工具，说明智能体没有用脚本操作应用的办法。当问题是关于证明一个改动能用时，提一下 `/创建验证skill`。

当模型规则不存在、而且这一点很重要时，问用户现在要不要为每个角色挑一个模型，并选一个推理预算。在这些情况下它很重要：用户是新手，问题是关于设置或成本的，或者答案取决于运行的是哪些模型。每次对话最多问一次。如果需求也不清楚，就把两个问题一起问。给两个选择：

- 现在：给他们 `/设置s模型` 让他们输入，同时也回答他们的问题。
- 以后：回答他们的问题，再加一行说明：在他们运行 `/设置s模型` 之前，每个角色都保持默认模型。

## 安装设置

1. 在聊天里用 `/add-plugin s` 安装，或者从侧边栏的 Customize 里安装。
2. 运行 [`/设置s模型`](../设置s模型/SKILL.md)。它会询问推理预算，给每个角色对应一个模型，并写一条规则。这条规则对新的对话生效。
3. 用 `/poteto工作模式`、一个目标和一个能判定通过或失败的检查，开始一个真实的任务。

在用户调用某个 skill 之前，安装不会改变任何东西。只有 `/设置s模型` 会根据用户的话自动加载。细节见 [README](../../README.md) 和[指南第 1 页](../../docs/guide/01-setup.md)。按照 [`references/prompting.md`](references/prompting.md)，主动提出和他们一起斟酌第一条提示词。

如果担心的是成本，就说清楚 token 花在了哪里、怎样少花一些。s 会在子智能体和审查组上多花 token。重新运行 `/设置s模型`，选一个更小的预算或更便宜的模型。设成 `auto` 或 `inherit-parent` 的角色会用聊天本身的模型运行，当聊天用的是 Auto 或更便宜的模型时，这样能省 token。更短的审查组列表会运行更少的子智能体，每个条目一个。把 `/poteto工作模式` 留给需要严谨的工作。

s 是为 Cursor 打造的。它的 skill 用的是 Agent Skills 格式，所以其他工具也能读。但大多数工作流程类的 skill，包括 `/poteto工作模式`、`/代码怎么工作`、`/代码为什么这样` 和 `/一步步教我`，都会派出按角色指定模型的 Cursor 子智能体，而 Custom Mode 和 `/loop` 都是 Cursor 的功能，所以在其他工具里这些部分可能用不了。

## 用 `/poteto工作模式` 开始一个任务

`/poteto工作模式` 会把任务对应到一个 playbook（操作手册），把这个 playbook 的步骤复制到待办清单里，并在步骤需要时运行其他 skill。它跳过的步骤会以 `skip: <reason>` 的形式留在清单里。一条好的提示词会说明目标，以及怎样判断它完成了。它不会列出 skill，因为手写的顺序往往会漏掉或打乱 playbook 本来会保留的步骤。在帮用户斟酌提示词之前，先读 [`references/prompting.md`](references/prompting.md)。[指南第 2 页](../../docs/guide/02-poteto-mode.md)里有例子。

`/poteto工作模式` 会不会一直开着，取决于用户怎样启动它：

- 在 `/poteto工作模式` 上按 Enter，会把这个 skill 附加到一条消息上。随着对话往下进行，它的作用会逐渐变弱。
- 在 Mac 上按 Option+Enter，在 Windows 上按 Alt+Enter，或者在 skill 条目上选 Use as Mode，会把它变成一个 Custom Mode。在用户退出这个模式之前，它每一轮都留在上下文里，而且不会掺和到随便聊聊的轮次里。
- Cursor 的文档列出了 Agents Window 和命令行工具里的 Custom Mode。在其他地方，每开始一个新任务都用 `/poteto工作模式`。

谈到这个时，附上 [Cursor 的 skill 文档](https://cursor.com/docs/skills)的链接。在对话中途说 “new task”（新任务），会让这个模式去匹配一个新的 playbook。`/poteto工作模式` 在它的 playbook 步骤派出子智能体时，已经在用 `poteto-agent`。如果想让你自己派出的子智能体也是同样的风格，就用 `subagent_type: "poteto-agent"` 派出它。

## 挑一个 skill

默认答案是 `/poteto工作模式`，它会在步骤需要时运行大多数其他 skill。当用户想要的某样东西比 playbook 给的更多或更少时，就直接点名一个 skill。推荐之前先读这个 skill，并给一条示例提示词。

| 用户想要 | Skill |
|---|---|
| 严谨地完成任何不简单的任务 | [`/poteto工作模式`](../poteto工作模式/SKILL.md) |
| 在智能体开始之前，确认它理解了自己的目标和问题 | [`/复述用户目标`](../复述用户目标/SKILL.md) |
| 开始之前把任务的目标定得更高：更专业、更注重结果、不过度规定 | [`/动手前磨清任务`](../动手前磨清任务/SKILL.md) |
| 知道代码现在是怎么工作的，或者新代码该放在哪里 | [`/代码怎么工作`](../代码怎么工作/SKILL.md) |
| 知道代码为什么是这个形状，或者某个数字是从哪来的 | [`/代码为什么这样`](../代码为什么这样/SKILL.md) |
| 理解一个改动或子系统，听一个浅显的讲解 | [`/一步步教我`](../一步步教我/SKILL.md) |
| 补上自己最近在某个话题上的工作进度 | [`/回想最近工作`](../回想最近工作/SKILL.md) |
| 用几句平实的话和小图，补上自己上一条消息之后这个对话里的变化，并有足够的背景来决定每个需要处理的事项 | [`/补上对话进度`](../补上对话进度/SKILL.md) |
| 知道一个小 diff 会在它之外弄坏什么 | [`/改动影响范围`](../改动影响范围/SKILL.md) |
| 在写跨函数边界的代码之前，先定下类型和模块形状 | [`/先画架构草图`](../先画架构草图/SKILL.md) |
| 就一份任务说明拿到好几次尝试，并合并成最好的一个 | [`/多方案竞技场`](../多方案竞技场/SKILL.md) |
| 以云端智能体的方式，分片并行检查，或者让工作者比赛 | [`/并行群体作战`](../并行群体作战/SKILL.md) |
| 让不同的模型审查一个 diff，并试着把它弄坏 | [`/多模型对抗审查`](../多模型对抗审查/SKILL.md) |
| 当有一个便宜的本地测试时，先写测试再修 bug | [`/测试驱动修bug`](../测试驱动修bug/SKILL.md) |
| 在 `.ts` 或 `.tsx` 的工作中应用 TypeScript 规则 | [`/TypeScript最佳实践`](../TypeScript最佳实践/SKILL.md) |
| 在审查之前删掉注释，用一个没写过这些注释的审查者 | [`/清理代码注释`](../清理代码注释/SKILL.md) |
| 把文字里的 AI 腔清理掉 | [`/清理AI腔`](../清理AI腔/SKILL.md) |
| 按标准写文档、RFC、README、PR 说明或提交信息 | [`/技术写作`](../技术写作/SKILL.md) |
| 用平实的话再听一遍上一条回复 | [`/说人话重讲`](../说人话重讲/SKILL.md) |
| 给智能体一种用脚本操作应用、证明行为的办法 | [`/创建验证skill`](../创建验证skill/SKILL.md) |
| 让一个验证 skill 和它的功能地图重新和应用对上 | [`/维护验证skill`](../维护验证skill/SKILL.md) |
| 在报告一个性能数字或依据它行动之前先审核它 | [`/基准测试清单`](../基准测试清单/SKILL.md) |
| 进行一次大的或横跨多处的改动，或者一次要离开一阵后回来审查的改动 | [`/自定流程搞定`](../自定流程搞定/SKILL.md) |
| 在运行期间记一份决定日志，之后再审查它 | [`/决定记录日志`](../决定记录日志/SKILL.md) |
| 为每个角色挑一个模型，并选一个推理预算 | [`/设置s模型`](../设置s模型/SKILL.md) |
| 把自己的工作习惯变成一个个人专属的模式 skill | [`/按我习惯定制`](../按我习惯定制/SKILL.md) |
| 把一个完成的任务教会的东西变成对 skill 的修改 | [`/反思并改skill`](../反思并改skill/SKILL.md) |
| 让智能体不再在这个仓库里重复犯同样的错误 | [`/根除重复错误`](../根除重复错误/SKILL.md) |
| 做一个页面，让它的按钮通过 webhook 唤醒 Grok Bot | [`/s做Bot界面`](../s做Bot界面/SKILL.md) |
| 在 s 里找到方向 | `/s使用帮助` |

如果和这个 skill 同级的某个 skill 目录不在表里，就读它的 frontmatter，按它的描述来对应。`原则-*` 目录（原插件里叫 `principle-*`）在下面的“原则”部分讲。

容易混淆的：

- `/代码怎么工作` 解释代码做了什么。`/代码为什么这样` 解释原因。`/一步步教我` 运行其中一个或两个，并把结果讲得浅显明白。
- `/多方案竞技场` 给每个工作者同样的任务说明，然后合并最好的部分。`/并行群体作战` 把工作切成几片或者组织一场比赛，然后返回一份报告。
- `/先画架构草图` 定下设计后会马上开始实现。加上 “with checkpoint”（带检查点），就能在它写代码之前先审查设计。
- `/多模型对抗审查` 审查 diff。`/改动影响范围` 寻找 diff 之外的破坏，并证明让这个改动安全的那一个事实。
- `/回想最近工作` 跨越最近的多次对话重建上下文。`/补上对话进度` 只覆盖这次对话里、用户上一条消息之后的内容。要接着某一次具体的对话或某个分支做，是 Session pickup playbook 的事。
- `/自定流程搞定` 设计一次严谨的运行。Orchestrate playbook 运行一个持续好几天、涉及很多个 PR 的项目。Autonomous run playbook 把一个任务一直推进到完成条件。

不在 s 里的：

- `/deslop`、`control-cli` 和 `control-ui` 在 `cursor-team-kit` 插件里。
- `/loop` 和 `/create-skill` 是 Cursor 自带的。
- s 没有 `/orchestrate` skill。Orchestrate 是 `/poteto工作模式` 里的一个 playbook。如果斜杠菜单里出现了 `/orchestrate`，那是别的插件提供的。

## Playbook 和原则

playbook 是 `/poteto工作模式` 里面的步骤清单，不是 skill，所以没有斜杠命令。在 `/poteto工作模式` 里，描述任务就会选中一个，下面这些说法会直接点名一个：

- “babysit this pr”（照看这个 PR）或 “check on pr 123”（看看 PR 123）运行 Babysit。它会把 PR 推进到可以合并的状态，然后停在那里。除非用户要求 merge、land 或 ship（合并、合入、上线），否则它不会合并。
- “land the stack”（把这一串 PR 合入）运行 Shipping。
- “take over this branch”（接手这个分支）运行 Session pickup。
- “pause safely”（安全地暂停）运行 Pause safely。
- “full autopilot on this queue”（对这个队列全自动驾驶）运行 Autopilot-full。“stack them, don't ship”（叠起来，但别上线）运行 Autopilot-stack。
- “run the eval playbook”（运行评估 playbook）运行 Eval。

如果没有 `/poteto工作模式`，像 “babysit this pr” 这样的说法，可能会改为启动 Cursor 自己做同样事情的 skill。[`poteto工作模式`](../poteto工作模式/SKILL.md) 的 Playbooks 一节列出了每个 playbook 以及它什么时候适用。[指南第 6 页](../../docs/guide/06-verify-and-ship.md)讲了开 PR、照看 PR 和合入 PR。

s 没有做计划的 skill。Cursor 的 Plan Mode 可以和它一起用。对于跨越多个阶段或多个叠放 PR 的工作，让 `/poteto工作模式` 做一个计划，会运行 [Multi-phase plan playbook](../poteto工作模式/playbooks/multi-phase-plan.md)，它只写计划，不去实现。对于设计上的问题，Prototype playbook 或 `/先画架构草图` 会先在代码里把它定下来。

原则是只有一条规则的 skill，`/poteto工作模式` 会读它们，并在回复里引用。用户很少直接调用某一条。他们改为用名字来引导，比如 “apply prove it works. show me the real output.”（应用“证明它真的能用”。给我看真实的输出。）输入 `/原则-<中文名>`（原插件里是 `/principle-<name>`，比如 `/原则-证明真能用`）仍然可以按需加载一条。[指南第 8 页](../../docs/guide/08-principles.md)列出了它们。

## 修好一次出了问题的运行

| 症状 | 修法 |
|---|---|
| 几轮之后模式不再起作用了 | 它是用 Enter 启动的。把它作为 Custom Mode 启动，或者每个任务都用 `/poteto工作模式` 开始。 |
| 一个问题被当成了上一个任务的下一步 | 说 “new task”（新任务），或者说这一轮不需要这个模式。 |
| 新的模型选择没有效果 | `/设置s模型` 写的规则对新对话生效。开一个新对话。 |
| 运行花的钱比预期多 | 见“安装设置”下面关于成本的那一段。 |
| 某个 skill 没有自己加载 | 只有 `/设置s模型` 会根据用户的话自动加载。其他的在用户输入它们、或者 `/poteto工作模式` 运行它们时才加载，而 `/poteto工作模式` 不会运行每一个 skill。 |
| 并行的智能体互相覆盖了 | 给每个智能体它自己的 worktree，或者把它们作为云端智能体运行，每个都有自己的机器。 |
| 一次通宵运行有进展，但什么都没完成 | `/loop` 需要一个能判定通过或失败的检查，而不是一段时长。见[指南第 7 页](../../docs/guide/07-overnight.md)。 |
| 回复凭一次绿色的构建就声称成功 | 要求看真实的命令、流程、存储的值或性能剖析。这就是 prove-it-works（证明它真的能用）原则。 |

对于跑偏的运行，[`references/prompting.md`](references/prompting.md) 里有一句话就能用的引导。[指南第 10 页](../../docs/guide/10-recipes-and-pitfalls.md)有更多的坑和值得照抄的做法。

## 把 s 变成自己的

- [`/按我习惯定制`](../按我习惯定制/SKILL.md) 根据用户自己的历史，起草一个个人专属的模式 skill，和 `/poteto工作模式` 一起用。
- 在一次会话之后运行 [`/反思并改skill`](../反思并改skill/SKILL.md)，把这次会话的教训变成用户批准的 skill 修改。
- `/poteto工作模式 write a skill for <workflow>`（为某个工作流程写一个 skill）会运行编写 skill 的 playbook。评估 playbook 会对一次 skill 修改做盲测。
- 在单独的 PR 里修一个表现不对的 skill，而不是在它出错时所在的功能工作里修。

[指南第 9 页](../../docs/guide/09-make-it-yours.md)讲了这里的每一项。

## 回复

先给答案。最多在一个代码块里给一条示例提示词，如果 [`references/recipes.md`](references/recipes.md) 里有合适的，就照着改，然后附上那个文件的链接。除非用户要的是整张地图，否则要简短。
