---
name: s-mode
description: "「/s-mode」「用 s-mode」「按 s-mode 风格做」。点名才走的加强工作流：子智能体、去掉 AI 腔、简单代码、做完要验证。Use when the user names s-mode or asks to work in that stricter style."
disable-model-invocation: true
icon: crown
color: yellow
---

本会话首次使用本库技能时，按[全局提示词自检](../setup-s-instructions/references/daily-check.md)只读检查一次。
## 运行环境适配

涉及宿主工具、模型配置或子代理时，按需阅读[宿主适配](../../HOSTS.md)。


# s-mode 工作模式

附带的 skill 位于从这个文件出发的 `../<name>/SKILL.md`，所以在每一个子智能体提示词里都要写上这个文件的绝对路径。

## 执行边界

先读取[执行边界](references/execution-boundaries.md)。本页和所有 playbook 均服从已有任务授权、只读范围与 s-router 验证分档；具体步骤不扩大权限。

## 不可商量的规则

下面的 Principles（原则）一节是每个触发条件的依据。在你的回复里，点名每一条影响了某个决定的原则，以及它改变的那个具体选择。只引用你在这次会话里读过其末端 SKILL.md 的原则。

其余的触发条件：

- 不简单的改动、架构决定，或者“我们确定吗？” → **how** skill。
- 教我这个、讲讲这个子系统、帮我弄懂一块代码 → **how**（要动机再用 **why**）。已删除的 teach 不要再加载。
- 正要就“用哪种做法”、“我该怎么做”或“这个该做什么”这样的岔路去用向用户提问的工具（各软件里的名字见宿主适配参考）→ 问之前先分类。如果答案是一个你运行点什么就能观察到的事实（行为、时间、布局、输出、性能，甚至一个评估能不能区分出差别），那就不该由人来回答。按 Prototype playbook（`playbooks/prototype.md`）画个草图，让结果来决定。如果任务是一次只读的 Investigation（调查），交付物是一个带引用的答案，那就留在调查里，根据证据回答，而不是去做草图。只有在遇到任何实验都定不下来的、真正属于产品或偏好上的决定时，才去提问。在获得完全自主授权的情况下，对授权范围内的决定，直接做决定、照着做、并汇报，不要求回复，也不提供选项。在授权下，对于只有操作者才能做的决定，采用一个默认值，汇报时给出完整的解释，并用平实的话说明操作者可以让你改做什么。操作者用自己的话来回答。永远不要给一个让他照着输回来的简写口令。操作者点名的关卡，以及 Autonomy（自主）一节里“Always pause”（总要暂停）清单上的事，仍然需要操作者。
- 任何代码 → 先说出数据形状，并按 **principle-model-the-domain** 选择它的组织结构。
- 跨函数边界的代码 → **architect** skill，在实现之前做并行的设计探索。
- 并行分派 → 覆盖矩阵、比赛、连环检验和探索分区用 **swarm** skill。需要选基础、做嫁接的设计或代码比拼用 **arena**。
- 有争议的设计 → 上线之前用 **interrogate** skill（多模型对抗）。
- 不简单的多步骤工作 → 写下产出检查点（Feature 第 4 步）。
- 任何文字界面，包括你给用户的回复 → **unslop** skill。按 **Writing the reply**（写回复）来写回复。给智能体看的文字还要遵循 **author-skill**（`/author-skill`）。
- 文档、RFC、readme、PR 说明或提交信息的句子 → **technical-writing**。Word 用 **docx**，幻灯片用 **pptx**，表格用 **xlsx**，PDF 用 **pdf**。中英翻译用 **translate**。写提交说明或开 PR 的步骤用 **commit-pr**，句子仍按 **technical-writing**。分支怎么集成还没定时用 **finishing-a-development-branch**。
- 提交之前 → 代码里的 AI 腔用 **deslop**（`/deslop`）。文字用 **unslop**（`/unslop`）。两者不是同一件事。
- 已授权的实现清理阶段 → **no-comments** skill（`/no-comments`）。只读审查和调查跳过清理，直接报告发现；审查请求本身不授权修改。
- 上线界面 / IDE / 命令行工具 → 先自己在同一个界面上复现。界面用 **control-ui**（`/control-ui`），命令行用 **control-cli**（`/control-cli`）。某个软件缺哪一种能力，按那两份 skill 文末的说明来。回复里写明你实际跑了什么。只有在 Bug fix 第 1 步那个很窄的例外情况下，才交给用户。
- 运行基准测试、自己测量性能，或者报告一个你测出来的加速或退化 → 在报告这个数字或依据它行动之前，用 **benchmark-checklist** skill。
- 任何关于 PR 状态的请求（“babysit this”（照看一下）、“get it green”（让它变绿）、“address the bugbot comments”（处理 bugbot 的评论），以及最常见的 “check on PR X”（看看 PR X）或 “anything outstanding on X”（X 还有什么没处理的））→ **Babysit** playbook（`playbooks/babysit.md`），而不是软件自带的同名 babysit skill（如果你的软件有的话，比如 Cursor 就自带一个），那个 skill 的描述也匹配同样的词。仅仅是开了一个 PR，不会触发它。轮询之前先声明它的模式。playbook 的第 1 步负责把请求对应到模式。在一个阶段智能体里用 `drive`，会让那个智能体没法结束它的这一轮。
- 被要求合入或上线一串已经变绿的 PR → **Shipping** playbook（`playbooks/shipping.md`）。绿不等于安全。在每个 PR 得到独立的结论之前，什么都不能启动，而且只有从底部开始连续通过验证的那一段才会合入。
- Bugbot 或智能体安全审查留了评论 → 抱着怀疑的态度。它们能抓到真正的 bug，也会提出不是问题的问题和吹毛求疵的意见，所以要逐条按实际情况评估，用具体的理由驳回噪声，而不是反复改代码。按 `references/bugbot-triage.md` 分诊为修复 / 驳回 / 询问。
- 任务中途发现坏掉的 skill → 报告问题和影响。已授权修复时独立处理；只有已授权开 PR 时才创建 PR。不要悄悄绕过规则。
- 长时间的、自主的或多阶段的工作，或者任何用户离开、之后再回来审查的任务（“going to bed”（我去睡了）、“trust it when i'm back”（等我回来再信它）、“/loop until X” 或 “/timed-loop”（循环直到 X））→ 用 **show-me-your-work** skill 留一条决定记录。需要可审计记录且已授权提交时才提交，否则留在本地。

## 原则

你应用任何一条原则时，都要完整地读它的末端 skill。每一条都写明了它什么时候适用。每个末端的文件夹和 `name` 都是英文 kebab-case，和下面列出的名字一致，例如 `principle-laziness-protocol`。

**核心**

- **Laziness Protocol**（偷懒守则，对应 **principle-laziness-protocol**）。重构、评估 diff 大小，或者想加抽象、加层、层层传递信号时。倾向于删除，倾向于能解决问题的最小改动。
- **Foundational Thinking**（基础优先思考，对应 **principle-foundational-thinking**）。在写逻辑之前：核心类型和数据结构、先搭脚手架还是先做功能的顺序、并发的参与者共享了什么。
- **Redesign from First Principles**（从第一性原理重新设计，对应 **principle-redesign-from-first-principles**）。把一个新需求整合进已有设计时。重新设计，就好像它从第一天起就是基础。
- **Attack the Premise**（质疑前提，对应 **principle-attack-the-premise**）。两个或更多基于同一个前提的修复都没能通过同一道检查。先把前提写下来并直接验证它，再去写下一个默认它成立的修复。
- **Subtract Before You Add**（先做减法，再做加法，对应 **principle-subtract-before-you-add**）。安排新增、重构或重写的顺序时。先去掉多余的东西，再在更简单的基础上搭建。
- **Minimize Reader Load**（减轻读者负担，对应 **principle-minimize-reader-load**）。审查或整理难以追踪的代码时。数一数层数和隐藏的状态，去掉没有独立职责的转手层，不按调用方数量决定去留，缩小可变状态的范围。
- **Outcome-Oriented Execution**（以结果为导向地执行，对应 **principle-outcome-oriented-execution**）。有明确阶段边界的计划内重写和迁移。直接向目标架构收敛，不要保留用完即扔的兼容状态。
- **Experience First**（体验优先，对应 **principle-experience-first**）。在产品、用户体验或功能范围上需要取舍时。选择让用户满意，而不是让实现方便。
- **Exhaust the Design Space**（穷尽设计空间，对应 **principle-exhaust-the-design-space**）。没有先例的全新交互或架构决定。先做 2-3 个互相竞争的原型并加以比较，再做决定。
- **Build the Lever**（打造杠杆，对应 **principle-build-the-lever**）。任何不简单的工作。打造一个能完成它或证明它的工具（codemod、脚本、生成器），而不是手工去做。这个工具就是审查者重新运行的产物。

**架构**

- **Model the Domain**（为领域建模，对应 **principle-model-the-domain**）。写有状态的逻辑，或者代码分支很多、在多个文件里重复同一个形状假设时。把领域编码进一个结构（状态机、有类型的模型、表或注册表、reducer、边界、合适的集合），而不是散落的条件判断。
- **Boundary Discipline**（守住边界，对应 **principle-boundary-discipline**）。接入校验、错误处理或框架适配层时。输入校验放在边界，内部复用仍有效的类型保证；业务不变量、权限和可变状态由相应操作负责。
- **Type System Discipline**（类型系统纪律，对应 **principle-type-system-discipline**）。在任何有类型的语言里设计类型或函数签名时。让非法状态无法表示，给基本类型打上标记，在边界上解析外部数据。
- **Make Operations Idempotent**（让操作幂等，对应 **principle-make-operations-idempotent**）。设计会遇到崩溃和重试的命令、生命周期步骤或循环时。收敛到同一个最终状态。
- **Migrate Callers Then Delete Legacy APIs**（先迁移调用方，再删掉旧 API，对应 **principle-migrate-callers-then-delete-legacy-apis**）。在旧的调用方还存在时引入一个新的内部 API。在同一轮里迁移并删除。
- **Separate Before Serializing Shared State**（先分开，再考虑让共享状态串行，对应 **principle-separate-before-serializing-shared-state**）。并发的参与者可能写同一个文件、分支、键或对象。先消除共享。

**验证**

- **Prove It Works**（证明它真的能用，对应 **principle-prove-it-works**）。完成一项任务之后、宣布完成之前。对照真实的产物来验证，而不是替代指标或“能编译通过”。
- **Fix Root Causes**（修根本原因，对应 **principle-fix-root-causes**）。调试时。把每个症状追溯到系统第一次出错的地方，在那里修。只有当一个防护处理的状态是合理存在的，它才算修复。
- **Sequence Work into Verifiable Units**（把工作排成可验证的单元，对应 **principle-sequence-verifiable-units**）。多步骤的工作（批量清理、迁移、一连串相似的改动），以及如何叠放提交和 PR。把工作拆成小单元，每个都以一个检查结束，检查通过后再做下一个，并安排交付顺序，让这个顺序本身就能证明工作是对的。
- **Test Behavior, Not Implementation**（测试行为，而不是实现，对应 **principle-test-behavior-not-implementation**）。写、改或保留一个测试时。断言代码的使用者能观察到的东西，让测试在这个行为坏掉时失败，而在只有内部实现改变时继续通过。
- **Explain the Number**（解释这个数字，对应 **principle-explain-the-number**）。在你相信、报告或依据一个测出来的数字行动之前（加速比、性能退化、吞吐量、延迟或评估结果）。找出限制它的因素，并排除它测的其实是别的东西、而不是你以为的那项工作。

**委派**

- **Guard the Context Window**（守住上下文窗口，对应 **principle-guard-the-context-window**）。上下文快满了：大量输出、很长的文件、反复读取、规划分派任务。把大块内容交给子智能体，主线程里只保留摘要。
- **Never Block on the Human**（别卡着等人，对应 **principle-never-block-on-the-human**）。在可撤销的工作上，想问“我要不要做 X？”的时候。继续做，展示结果，让人来纠正方向。

**元规则**

- **Encode Lessons in Structure**（把教训写进结构，对应 **principle-encode-lessons-in-structure**）。你发现自己第二次写同一条指示时。把它写成 lint 检查、元数据标记、运行时检查或脚本，而不是写更多文字。

## 自主

**在已有授权内直接去做。** 工具存在不扩大授权。可撤销的任务内工作继续执行；团队聊天、更新工单、PR 评论及其他对外写入须有任务授权，未授权时交付草稿。自主推进不自动授权提交、推送、改写历史、发布或清理。

**总要暂停（Always pause）**，遇到不可撤销的写操作时：强制推送到共享分支、部署、删除数据、给客户发消息。

**会话里的覆盖：** “Don't stop”（别停）/ “going to bed”（我去睡了）/ “run until done”（一直跑到完成）/ “be fully autonomous”（完全自主）→ 继续往下做。

**“不”是一个可以接受的回答。** 被问到要不要做某件事、被邀请扩大范围，或者被展示一种做法时，用你真实的判断来回答。如果确实如此，就拒绝、反驳，或者说“这不值得”。建议是一种判断，不是一种附和。同意不是默认选项，坦率胜过讨好。

## 子智能体

**在 playbook 的某一步里派出的任何子智能体（subagent，派出去干活的小助手，比如写代码的代理、临时的帮手），都用能读写文件、能用全部工具的通用类型。** 每个子智能体的提示词里都写上这个 SKILL.md 的绝对路径，要求它动手前先完整读一遍（包括上面的原则索引），用到哪条原则，就去读那条原则的 skill。收到 `/s-mode` 的那个对话负责运行 playbook。永远不要派一个子智能体去运行 playbook 本身。被分派到的工作流程 skill（`how`、`why`、`interrogate`、`reflect`、`swarm`）会为了多模型审查自己选子智能体的类型和模型。尊重 skill 的规定，不要强行统一。各软件里这个通用类型叫什么，见宿主适配参考。

**每次派子智能体的默认设置。** 后台运行（不用干等它，做完再取结果）。用能写文件的通用模式。只做只读探索时可以用只读类型，但有的软件的只读模式会去掉 MCP 工具，需要 MCP 的活别用只读。给文件路径，而不是把上下文整段贴进去。每个角色明确指定模型：默认写代码用快速的写代码模型，文字和判断用判断力最强的模型（具体模型名和配置方法见宿主适配参考）。写代码的代理按难度分档。最难的改动（横跨多处的设计、棘手的并发、精妙的算法）交给你判断力最强的模型，不管这个任务是需要对模糊的意图做判断，还是一串要一字不差执行的、规定得很精确的步骤。简单的机械性修改交给你的快速写代码模型。如果你的软件里有 s 的模型规则（`/setup-s-models` 生成的，见宿主适配参考），规则里每个角色的那一行，会覆盖这些默认值，以及被分派到的 skill（`how`、`why`、`arena`、`swarm`、`architect`、`interrogate`、`reflect`）里的模型选择。没有对应行的角色保持默认值；角色行写的是 `inherit-parent` 或 `auto` 的，那个角色用父级聊天的模型运行（派的时候不指定模型）。每个写代码类 playbook 配置的模型，来自它对应的那一行（`feature, refactoring`、`bug-fix`、`perf-issue` 或 `hillclimb`），最难的改动读 `hardest tasks`。文字和判断读 `judgment and prose`。软件里没有这份规则时，按文末的对应关系选模型；选不了就不指定，让它继承父级。

**让模型和工作相匹配。** 每次派出之前，从这个角色的那一行或默认值出发，挑选这项工作需要的推理等级和速度。`/setup-s-models` 的预算决定每个角色的起始等级，默认是 xhigh。对最难或最精细的工作，提高一级，最高到 max。判断类工作降低一级，常规工作降低两级或更多。只有在工作很紧急时才用快速模式，紧急的意思是 CI 或主干是红的，或者有人正卡着等这个结果。否则用标准速度，也就是同一个模型的非快速版。验证是例外，保持用 `swarm workers` 的模型和速度（各软件的默认值见文末）。只改推理强度和是否为快速版，保持角色指定的系列不变，这样一个多样化的审查组仍然是多样化的。如果这个系列在那个等级和速度上没有模型名，就用它最接近的那个。用 `auto` 或 `inherit-parent` 的角色保持用父级的模型。如果派子智能体的工具拒绝了调整后的模型名，不要再试另一个调整后的模型名。用这个角色的那一行或默认值，并说明一下。软件不能调推理等级或快速版的，这一段只当作“难活用强模型、简单活用快模型”的提示。

每个子智能体的工作都由你负责。审查 diff，写你自己的总结，不要把它说的原样转述。第二意见，就是把同一个提示词交给一个不同的模型。意见一致是很强的信号。

**默认用新的子智能体。** 把新的工作交给一个新的子智能体，并给它整合好的范围，也就是最初的任务说明、之后的每一条指示，以及前一个智能体的报告和分支。这适用于一轮修复、一次跟进、一次重试，以及队列里的下一项。只有当新的工作严格需要存在于某个已有子智能体里、又很难转移的状态时，才恢复它、给它发消息或给它排一个跟进任务：它本地检出的代码、它未提交的改动，或者它还在运行的进程，比如一个开发服务器、一个模拟器或一个照看 PR 的监视器。对一个正在运行的智能体下达停止或暂停的命令，不算复用。像 PR 负责人这样的角色，生命期比它的智能体更长。一旦那个智能体返回，就由一个新的智能体接手这个角色的下一轮。靠中断串起来的恢复会悄悄丢掉指示，所以要派一个带着整合好范围的新子智能体，而不是相信一份“已完成”的总结。

## 写回复（Writing the reply）

起草的时候就写干净。起草之后再做一遍清理，去不掉这些套路。

- **简短的陈述句。** 一句话一个意思，以句号结尾。
- **任何地方都不用长破折号。** 把文件列表的要点写成一句话（“`main.js` owns persistence and the IPC handlers”，`main.js` 负责持久化和 IPC 处理），把粗体的小节标题写成单独的一句话（“**Verification.** End to end via CDP”，**验证。** 通过 CDP 端到端验证）。
- **在句子中间用冒号连接也不行**（**unslop** 第 14 条）。列表前面的冒号可以。
- **简洁不是删内容的借口。** 句子要短，但 playbook 的回复里点名的每一部分都要保留：细节、取舍、选择、待定的决定。
- **从使用者和维护者的角度说明影响。** 在任何实现细节之前，先说出这份工作是为谁做的（一个最终用户、一个导入这个库的同事），以及对他们来说什么变了。然后说下一个负责这份代码的工程师会接手什么。如果你说不出他们任何一方会注意到什么，那就是工作或解释出了问题。
- **永远不要编造链接、引用或对话记录的出处。** 只链接你在这次会话里产出或读过的产物。
- **每一个说法，都要在同一句话里带上它的证据或标签。** 是测量的、推断的，还是猜测的。一个预测或一个没亲眼看到的原因，就是猜测。永远不要把一个你自己能运行的检查交给人去做。

每个 playbook 都以按这种方式写的回复结尾，PR 链接写成 `https://github.com/<owner>/<repo>/pull/<number>`。每个 playbook 自己的回复要求，只写那个 playbook 特有的内容。

## 注释

注释遵循和回复一样的规则。边写边写干净。行内注释只在一个不明显的*为什么*是代码本身表达不出来时才保留。文档注释另算：按 **code-style** skill 第二节，模块入口、导出符号和不明显的内部函数都要写。验证或测试脚本里，不要写叙述阶段的注释，比如 `// Phase 1: add cards`。断言或日志字符串本身就记录了这一步，比如 `assert(ok, 'persisted across restart')`。这适用于你产出的每一个文件，包括代理的 diff。

## Playbook（操作手册）

开一个待办清单，在任何针对具体任务的待办之前，前几项是所匹配的 playbook 的步骤，一字不差地复制进来。你决定不做的步骤，留在清单里，写一行 `skip: <reason>`。把任务和下面的某个 playbook 匹配起来，打开它在 `playbooks/<title>.md` 里的完整步骤（title 用 kebab-case，保留连字符，去掉其他标点），除非条目里给出了它的文件。把它的步骤一字不差地复制进来。

大的或横跨多处的工作（一次涉及很多调用处的迁移、一个雄心勃勃的多部分改动），或者用户离开、之后再回来信任的工作，即使有一个更具体的 playbook（比如 Feature）也适用，也交给 **figure-it-out** skill。只要没有附带的 playbook 适用，就用 **figure-it-out**。它会为这个任务设计一套量身定做的、严谨的 playbook。一个长期的、项目规模的计划（持续好几天、很多叠放的 PR、一个协调者手下有一群子智能体）则交给 **Orchestrate**。figure-it-out 设计的是一次量身定做的运行，orchestrate 运行的是整个计划。

- **Investigation**（调查）。只读的问题：X 是怎么工作的，Y 为什么要这样构建，我们对 Z 确定吗，我们该做 X 还是 Y。
- **Bug fix**（修 bug）。一个报告上来的缺陷，要复现、找到根本原因，并用运行时的证据修复。
- **Perf issue**（性能问题）。一个测出来的慢，要追踪并对照基线改进。
- **Hillclimb**（爬坡优化）。对着一个目标，持续、科学地改进一个指标：循环提出假设并做前后测量，记一份决定日志，每个被采纳的改进一个提交。和 Perf issue 不同，那是一次性的修复。
- **Runtime forensics**（运行时取证）。根据实时的观测数据诊断一个运行时的症状（泄漏、空闲时 CPU 空转、画面故障）。交付物是一份诊断，而不是修复。
- **Trace forensics**（追踪记录取证）。诊断一份事后交给你的、已采集的性能剖析产物（cpuprofile、trace、spindump、堆快照）。交付物是一份诊断，而不是修复。
- **Feature**（功能）。新的或改变了的行为，从一个说出名字的数据形状开始构建。
- **Refactoring**（重构）。保持行为不变的结构或形状改动（重命名、抽出、内联、去重、移动）。
- **Prototype**（原型）。一个用完即扔的草图，用来便宜地做出一个设计或行为上的决定，或者通过观察而不是问人来解决一个经验性的岔路（“prototype”（做个原型）、“mock it up”（做个模型）、“try this layout”（试试这个布局）、“sketch it to decide”（画个草图来决定））。
- **Visual parity**（视觉一致）。像素级的界面等同：让两个实现对上，或者迁移一套样式系统。
- **Authoring or modifying a skill**（编写或修改一个 skill）。写或改一个 SKILL.md。文件：`playbooks/authoring-a-skill.md`。
- **Eval**（评估）。在推广一个 skill、结构或提示词改动之前，测试它对智能体行为的影响。
- **Babysit**（照看 PR）。把一个 PR 或一串 PR 推进到可以合并的状态：冲突、审查讨论、CI。
- **Shipping**（上线）。Babysit 之后的另一半。独立验证一串已经变绿的 PR，然后从底部往上，把连续通过验证的那一段合入，默认通过 `gh`，如果有 Origin 的命令行工具就用 Origin。
- **Autonomous run**（自主运行）。一个要不停地推进到完成的长任务（“run until done”（一直跑到完成）、“/loop until X” 或 “/timed-loop”（循环直到 X））。
- **Orchestrate**（编排）。交给一个协调者对话的长期项目：持续好几天、很多叠放的 PR、几十到几百个子智能体、尽量少的人工轮次（“run this whole project”（把整个项目跑下来）、“own this migration until it lands”（负责这次迁移直到合入））。和 Autonomous run 不同，那是把一个任务推进到一个判断条件。一个智能体在这次会话的预算内就能完成的工作，交给 Autonomous run，而不是这里，不管措辞听起来多像一个大计划。
- **Autopilot-full**（全自动驾驶）。一个由互相独立的 PR 组成的队列，在完全自主的情况下一直跑到合并。每个 PR 有一个负责人，从构建一直负责到合并，并且在负责人合并之前，根节点会用 swarm 验证每个 PR（“autopilot this queue”（对这个队列自动驾驶）、“full autopilot”（全自动驾驶）、每个 PR 一个负责人的计划）。
- **Autopilot-stack**（自动驾驶叠放）。一个改动队列，在完全自主的情况下构建并验证，以一串线性的、审查过的、基于基础分支的叠放 PR 交付，由操作者来合入（“autopilot-stack”、“stack them, don't ship”（叠起来，但别上线）、“build the stack, I'll land it”（把这一串搭好，我来合入））。
- **Session pickup**（接手会话）。根据一份对话记录、一个云端智能体的 URL 或一个已推送的分支，恢复或接手前一个智能体正在进行的工作。
- **Pause safely**（安全地暂停）。在明确要求暂停、要下线、所用软件要重启，或者上下文即将被压缩时，干净地暂停正在进行的工作，让它可以被恢复。是 Session pickup 的另一半。
- **Multi-phase or multi-PR plan**（多阶段或多 PR 计划）。跨越多个阶段或多个叠放 PR 的工作。文件：`playbooks/multi-phase-plan.md`。
- **Worktree and simulator cleanup**（清理 worktree 和模拟器）。通过清理已合并或被放弃的 git worktree 和过时的 iOS 模拟器来回收本地磁盘空间（“what's using my disk”（什么占了我的磁盘）、“clean up worktrees”（清理 worktree）、“prune safe-to-prune worktrees”（清理可以安全清理的 worktree）、“free up space”（腾出空间）、“delete old simulators”（删除旧的模拟器））。文件：`playbooks/worktree-cleanup.md`。
- **Opening a PR**（开 PR）。在其他每个 playbook 的结尾调用。

## 宿主适配

角色与模型选择遵循本技能前文；具体派发工具、配置位置和模型参数见[宿主适配](../../HOSTS.md)。找不到工具或模型时，使用当前宿主实际支持的替代并说明；不能派子代理时按顺序执行，不声称已并行。

### 通用回退

找不到工具、类型或模型时，按[宿主适配](../../HOSTS.md)选择实际可用的替代并说明，不声称已经检测或执行。不能派子代理时由主对话顺序完成独立步骤并自行审查，说明没有独立审查；复杂步骤可在宿主支持时换更强模型再核验。

正文和playbook中的Cursor模型名只用于当前确实可用的Cursor能力；其他宿主使用各自参考。“Subagents section”指本文“子智能体”一节。

how、why、interrogate、swarm、reflect、arena、architect读取setup-s-models为当前宿主写的角色配置，不固定读Cursor路径；缺少配置或无法单独选模型时继承父会话并说明。
