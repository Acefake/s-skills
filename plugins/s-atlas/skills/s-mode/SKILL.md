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

其余触发条件的全文在 [non-negotiable-rules.md](references/non-negotiable-rules.md)。下表只负责对上技能或 playbook。对上某一行之后，先读该文件里的对应段落，再执行。

| 触发 | 去向 |
| --- | --- |
| 不简单的改动、架构决定，或「我们确定吗」 | **how** |
| 教我、讲子系统、弄懂一块代码 | **how**；要动机用 **why**。已删除的 teach 不再加载 |
| 正要问用户用哪种做法、该怎么做、该做什么 | 先读 [non-negotiable-rules.md](references/non-negotiable-rules.md) 的提问分类。能观察的事实走 [prototype.md](playbooks/prototype.md)；只读调查留在调查里 |
| 任何代码 | 先说出数据形状，按 **principle-model-the-domain** 选结构 |
| 跨函数边界的代码 | **architect**，实现前做并行设计探索 |
| 并行分派 | 覆盖、比赛、连环检验、探索分区用 **swarm**；选基础或比拼用 **arena** |
| 有争议的设计 | 上线前用 **interrogate** |
| 不简单的多步骤工作 | 写下产出检查点（Feature 第 4 步） |
| 任何文字界面，包括给用户的回复 | **unslop**，并先读 [writing-the-reply.md](references/writing-the-reply.md)。给智能体的文字还要遵循 **author-skill** |
| 文档、RFC、readme、PR 说明或提交信息的句子 | **technical-writing**。Word 用 **docx**，幻灯片用 **pptx**，表格用 **xlsx**，PDF 用 **pdf**，中英翻译用 **translate**。提交或开 PR 的步骤用 **commit-pr**，集成方式还没定用 **finishing-a-development-branch** |
| 提交之前 | 代码里的 AI 腔用 **deslop**，文字用 **unslop** |
| 已授权的实现清理 | **no-comments**。只读审查和调查不清理，直接报告 |
| 上线界面、IDE 或命令行 | 先在同一个界面上复现。界面用 **control-ui**，命令行用 **control-cli**。回复里写明实际跑了什么 |
| 基准、自测性能，或报告加速或退化 | 行动前用 **benchmark-checklist** |
| 任何关于 PR 状态的请求 | [babysit.md](playbooks/babysit.md)，不要走软件自带的同名 skill。只是开了 PR 不会触发 |
| 合入或上线一串已经变绿的 PR | [shipping.md](playbooks/shipping.md)。绿不等于可以合入 |
| Bugbot 或智能体安全审查的评论 | [bugbot-triage.md](references/bugbot-triage.md)，分诊为修复、驳回或询问 |
| 任务中途发现坏掉的 skill | 按 [non-negotiable-rules.md](references/non-negotiable-rules.md) 报告。已授权才修，已授权开 PR 才开 PR |
| 长时间、自主、多阶段，或人离开后回来再审 | **show-me-your-work** 留决定记录 |

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

派发前先读 [subagents.md](references/subagents.md)。模型、推理等级、速度、后台运行和角色默认档位以该文件为准。

**在 playbook 的某一步里派出的任何子智能体（subagent，派出去干活的小助手，比如写代码的代理、临时的帮手），都用能读写文件、能用全部工具的通用类型。** 每个子智能体的提示词里都写上这个 SKILL.md 的绝对路径，要求它动手前先完整读一遍（包括上面的原则索引），用到哪条原则，就去读那条原则的 skill。收到 `/s-mode` 的那个对话负责运行 playbook。永远不要派一个子智能体去运行 playbook 本身。被分派到的工作流程 skill（`how`、`why`、`interrogate`、`reflect`、`swarm`）会为了多模型审查自己选子智能体的类型和模型。尊重 skill 的规定，不要强行统一。各软件里这个通用类型叫什么，见宿主适配参考。

每个子智能体的工作都由你负责。审查 diff，写你自己的总结，不要把它说的原样转述。第二意见，就是把同一个提示词交给一个不同的模型。意见一致是很强的信号。

**默认用新的子智能体。** 把新的工作交给一个新的子智能体，并给它整合好的范围，也就是最初的任务说明、之后的每一条指示，以及前一个智能体的报告和分支。这适用于一轮修复、一次跟进、一次重试，以及队列里的下一项。只有当新的工作严格需要存在于某个已有子智能体里、又很难转移的状态时，才恢复它、给它发消息或给它排一个跟进任务：它本地检出的代码、它未提交的改动，或者它还在运行的进程，比如一个开发服务器、一个模拟器或一个照看 PR 的监视器。对一个正在运行的智能体下达停止或暂停的命令，不算复用。像 PR 负责人这样的角色，生命期比它的智能体更长。一旦那个智能体返回，就由一个新的智能体接手这个角色的下一轮。靠中断串起来的恢复会悄悄丢掉指示，所以要派一个带着整合好范围的新子智能体，而不是相信一份“已完成”的总结。

## 写回复（Writing the reply）

给用户的回复和代码注释，按 [writing-the-reply.md](references/writing-the-reply.md) 写。起草之前先读完该文件。

## Playbook（操作手册）

开一个待办清单，在任何针对具体任务的待办之前，前几项是所匹配的 playbook 的步骤，一字不差地复制进来。你决定不做的步骤，留在清单里，写一行 `skip: <reason>`。把任务和下面的某个 playbook 匹配起来，打开它在 `playbooks/<title>.md` 里的完整步骤（title 用 kebab-case，保留连字符，去掉其他标点），除非条目里给出了它的文件。把它的步骤一字不差地复制进来。

大的或横跨多处的工作（一次涉及很多调用处的迁移、一个雄心勃勃的多部分改动），或者用户离开、之后再回来信任的工作，即使有一个更具体的 playbook（比如 Feature）也适用，也交给 **figure-it-out** skill。只要没有附带的 playbook 适用，就用 **figure-it-out**。它会为这个任务设计一套量身定做的、严谨的 playbook。一个长期的、项目规模的计划（持续好几天、很多叠放的 PR、一个协调者手下有一群子智能体）则交给 **Orchestrate**。figure-it-out 设计的是一次量身定做的运行，orchestrate 运行的是整个计划。

下表只用于选定文件。每条的完整触发说明在 [playbook-routing.md](references/playbook-routing.md)。选定后打开表中的 playbook，把它的步骤一字不差地复制进待办清单。

| Playbook | 何时使用 | 文件 |
| --- | --- | --- |
| Investigation（调查） | 只读问题：怎么工作、为什么这样建、对不对、该选哪条 | [investigation.md](playbooks/investigation.md) |
| Bug fix（修 bug） | 报告上来的缺陷：复现、找根因、用运行时证据修 | [bug-fix.md](playbooks/bug-fix.md) |
| Perf issue（性能问题） | 一次测出来的慢，对照基线改完即止 | [perf-issue.md](playbooks/perf-issue.md) |
| Hillclimb（爬坡优化） | 对着一个指标持续提假设、做前后测量，每个采纳的改进一个提交 | [hillclimb.md](playbooks/hillclimb.md) |
| Runtime forensics（运行时取证） | 泄漏、空闲 CPU、画面故障等现场症状。交付诊断 | [runtime-forensics.md](playbooks/runtime-forensics.md) |
| Trace forensics（追踪记录取证） | 事后拿到的 cpuprofile、trace、spindump、堆快照。交付诊断 | [trace-forensics.md](playbooks/trace-forensics.md) |
| Feature（功能） | 新的或改变了的行为，从一个说出名字的数据形状开始 | [feature.md](playbooks/feature.md) |
| Refactoring（重构） | 行为不变的重命名、抽出、内联、去重、移动 | [refactoring.md](playbooks/refactoring.md) |
| Prototype（原型） | 用草图决定设计或行为，或用观察解决经验岔路 | [prototype.md](playbooks/prototype.md) |
| Visual parity（视觉一致） | 像素级对齐两个实现，或迁移一套样式系统 | [visual-parity.md](playbooks/visual-parity.md) |
| Authoring or modifying a skill | 写或改一个 SKILL.md | [authoring-a-skill.md](playbooks/authoring-a-skill.md) |
| Eval（评估） | 推广 skill、结构或提示词改动之前，测它对智能体行为的影响 | [eval.md](playbooks/eval.md) |
| Babysit（照看 PR） | 把 PR 推进到可合并：冲突、审查、CI。不要走软件自带的同名 skill | [babysit.md](playbooks/babysit.md) |
| Shipping（上线） | 独立验证已经变绿的一串 PR，从底部合入连续通过的一段 | [shipping.md](playbooks/shipping.md) |
| Autonomous run（自主运行） | 一个任务不停做到完成条件 | [autonomous-run.md](playbooks/autonomous-run.md) |
| Orchestrate（编排） | 多天、很多叠放 PR、一群子智能体的项目。一次会话能做完的交给 Autonomous run | [orchestrate.md](playbooks/orchestrate.md) |
| Autopilot-full（全自动驾驶） | 互相独立的 PR 队列，每个 PR 一个负责人，一直做到合并 | [autopilot-full.md](playbooks/autopilot-full.md) |
| Autopilot-stack（自动驾驶叠放） | 队列建成审查过的线性叠放 PR，由操作者合入 | [autopilot-stack.md](playbooks/autopilot-stack.md) |
| Session pickup（接手会话） | 凭对话记录、云端智能体 URL 或已推送分支接手前一个智能体的工作 | [session-pickup.md](playbooks/session-pickup.md) |
| Pause safely（安全地暂停） | 暂停、下线、宿主重启或上下文即将压缩时，把工作留成可恢复的状态 | [pause-safely.md](playbooks/pause-safely.md) |
| Multi-phase or multi-PR plan | 跨越多个阶段或多个叠放 PR | [multi-phase-plan.md](playbooks/multi-phase-plan.md) |
| Worktree and simulator cleanup | 回收已合并或放弃的 worktree，以及过时的 iOS 模拟器 | [worktree-cleanup.md](playbooks/worktree-cleanup.md) |
| Opening a PR（开 PR） | 其他每个 playbook 的结尾调用 | [opening-a-pr.md](playbooks/opening-a-pr.md) |

## 宿主适配

角色与模型的调度见「子智能体」和 [subagents.md](references/subagents.md)。具体派发工具、配置位置和模型参数见[宿主适配](../../HOSTS.md)。

找不到工具、类型或模型时，先读 [host-fallback.md](references/host-fallback.md)，再使用当前宿主实际支持的替代并说明。不能派子代理时，由主对话按顺序完成独立步骤并自行审查，说明没有独立审查，也说明这一轮是顺序完成的。
