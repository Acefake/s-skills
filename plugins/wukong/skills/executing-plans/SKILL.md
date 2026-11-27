---
name: executing-plans
description: "「按这份计划做」「执行实现计划」「派子智能体逐个做计划里的任务」「先开个 worktree 再做」「反复跑这个检查直到通过」「多个子代理会写同一个文件」「/swarm 并行跑一遍」。手上已有书面计划要执行完，或要隔离工作区、让并行子代理别共用文件、循环检查到通过时用。只是写脚本、加 lint、迁移调用方、拆步骤或让我少问几句，不用本技能。Use when executing an already written implementation plan, running an explicitly requested parallel swarm, (in this or a follow-up session, or task by task with subagents), isolating work in a git worktree, keeping parallel subagents off shared files, or looping a check until it passes. Not for one-off scripts, lint rules, API migrations, planning, or general autonomy requests."
---

本会话首次使用本库技能时，按[全局提示词自检](../wukong-init/references/daily-check.md)只读检查一次。
## 运行环境适配

T3 Code 中先读 [T3 编排参考](../wukong-router/references/t3-code-tools.md)。独立检出由 T3 创建绑定；任务说明带齐上下文，不假定父历史或未提交文件可见。等待遵循返回的 `next`。

涉及宿主工具或子代理时，按需阅读[宿主适配](../../HOSTS.md)。找不到工具、类型或模型时读 [host-fallback.md](references/host-fallback.md)。

# 执行计划

把写好的计划做完，并留下能审的证据。按场景选下面一节，多数任务只用到一两节。

所有节都服从[执行边界](references/execution-boundaries.md)：工具可用不等于已授权，提交、推送、清理和对外写入看本次任务授权。

## 主会话按计划执行

开始时宣布：「我正在使用 executing-plans 技能来实现这份计划。」只有用户要求或已授权计划明确采用子代理时才换到下一节。

1. **审阅计划。** 读完计划，找出疑问。有担心先向用户提；没有就为条目建待办。
2. **逐任务执行。** 标 in_progress，严格按步骤做，只跑这一步涉及的验证，全量留到最后。按 code-style「交付前自审」审完整差异和关键调用方；按「交付前独立评审」判断是否需要只读子代理评审，发现先核实再改。标 completed。
3. **收尾。** 全部完成并验证后，审完整任务差异与集成关系，再按 `commit-pr` 的分支收尾验证、给选项、执行所选项。

出现下面情况立刻停下来问，不要猜：缺依赖、测试反复失败、计划有关键缺口、看不懂某条说明。协作者改了计划或根本做法要重来时，回到第 1 步。没有用户明确同意，不在 main/master 上开始实现。计划提到某个技能就去用它。

## 派子代理逐任务执行

计划里任务大多独立、已授权派子代理、希望同一会话持续推进时用。每项任务派一个全新实现者，任务后做一次评审（规格符合 + 代码质量），全部做完再做一次覆盖整个分支的终审。子代理不继承你的会话历史，只拿你写给它的内容；大段输出和长文件留在子代理里，主线程只收摘要（[guard-the-context-window](references/principles/guard-the-context-window.md)）。

流程：

1. 读计划，记下上下文和全局约束，建待办与[进度台账](references/progress-ledger.md)。派任务 1 前先做[计划预检](references/preflight-plan-review.md)。
2. 每项任务：按 [implementer-prompt.md](implementer-prompt.md) 派实现者；它提问就答，再重新派。实现者回报后按[状态处理](references/implementer-status.md)。
3. 写差异文件，按 [task-reviewer-prompt.md](task-reviewer-prompt.md) 派评审。有 Critical 或 Important 发现就派修复者，修完重新评审，直到规格符合且质量通过。通过后在待办和台账里标完成。
4. 全部任务完成后，用 `requesting-code-review` 的 [code-reviewer.md](../requesting-code-review/code-reviewer.md) 做终审，再按 `commit-pr` 的分支收尾。

要点：

- 持续执行：任务之间不停下来问「要继续吗」。只在无法解决的 BLOCKED、真正阻碍进展的歧义、或全部完成时停。可撤销的工作先做完再给人看（[never-block-on-the-human](references/principles/never-block-on-the-human.md)）。
- 多个子代理可能写同一文件、分支或键时，先分开再谈串行（[separate-before-serializing-shared-state](references/principles/separate-before-serializing-shared-state.md)）。
- 未授权提交时，报告未提交状态和改动文件，不为生成评审包而提交。`scripts/review-package BASE HEAD` 只含提交差异，必须另附暂存、未暂存和相关新文件内容；基线时已有的无关修改单独标明并保留。
- 派发规则（类型、模型、并发只读检索、新子代理还是恢复）读 [subagents.md](references/subagents.md)。

细则进入对应步骤前读：[reviewer-warnings](references/reviewer-warnings.md)（评审者标了无法从 diff 核实的条目）、[reviewer-prompts](references/reviewer-prompts.md)（评审与终审提示词）、[file-handoff](references/file-handoff.md)（文件交接）、[red-flags](references/red-flags.md)（开工前读；提问、评审失败、任务失败怎么处理）、[integration](references/integration.md)（要一起用的技能）、[example-workflow](references/example-workflow.md)（完整例子）。

## 先隔离工作区

功能或计划执行要和当前工作区隔开时用。核心顺序：先检测已有隔离，再用宿主原生工具，最后才回退到手工 `git worktree`，不和宿主对着干。

1. **检测。** 比较 `git rev-parse --git-dir` 与 `--git-common-dir` 的真实路径。不同且不在子模块里（`git rev-parse --show-superproject-working-tree` 无输出）说明已在 worktree，直接去第 4 步，不再嵌套创建。建之前先确认用户要隔离，拒绝就就地工作。
2. **原生工具优先。** 宿主有 `EnterWorktree`、`WorktreeCreate`、`/worktree` 或 `--worktree` 这类能力就用它，不要同时再跑 `git worktree add`，否则宿主看不见也管不了。
3. **手工回退。** 目录按「用户指定 > 已有的 `.worktrees/` 或 `worktrees/` > 默认 `.worktrees/`」选。创建前用 `git check-ignore -q <目录>` 确认已被忽略；没忽略时优先写进本地 `.git/info/exclude`，仓库约定要求改 `.gitignore` 才改，且只在已授权提交时才提交。然后 `git worktree add <目录>/<分支名> -b <分支名>`。沙箱拒绝创建时说明原因，改为就地工作。
4. **环境与基线，然后报告路径和结果。** 先复用已有依赖，确需安装才用仓库锁文件对应的包管理器。按 wukong-router 验证分档核验基线，第 0 档不跑测试；基线失败就报告并问是否继续，不通过清理来制造「干净」。

收尾清理 worktree 时：宿主创建的用宿主工具管，手工建的才用 git；归属不明、仍在使用或有未处理文件的保留并报告，不用 `reset --hard`、`git clean` 或强制删除。

## 并行群体作战

用户点名 `wukong-swarm`、`swarm`、要「并行跑一遍」「让一群智能体做」，或任务能拆成多个互不冲突的子块并配校验者协作时，调用 [wukong-swarm](../wukong-swarm/SKILL.md) 作为协调者拉起并行工作者并通过共享留言板协作（非 Antigravity 宿主改用宿主实际可用的子代理派发）。

## 反复检查直到通过

同一件检查要反复做，直到完成条件成立，或确实卡住。调用时带三样：要重复的提示词或技能、完成条件、间隔（可不写，由执行者判断何时再看）。

- 完成条件必须是每次都能跑的检查：测试通过、CI 绿、diff 为零、旧调用方为零。「再做四小时」不是完成条件。
- 宿主有 `/loop` 或持久定时任务时用宿主的，不另做计时器；没有时用会话内检查，并说明限制。工具和配置见[宿主适配](../../HOSTS.md)。
- 卡住的出口：试过几轮、证据说明再试同一种做法不会变，就停下写明原因，不改写目标。

## 没有现成流程时

任务和任何现有技能都对不上，且是大迁移、或人离开后要回来审的活：先设计一套做法，再执行。要交付的首先是这套流程本身，严谨程度和任务相称，并留一条可审计的决定记录。

1. **定框架。** 说清「完成」的判断条件（写成能被证伪的检查，见 [prove-it-works](../code-style/references/principles/prove-it-works.md)）、量化范围、严谨程度。单向门和影响面大的事要更严；可撤销的低风险步骤可以松。长时间运行前把框架和取舍讲出来，可撤销的工作直接做。
2. **设计流程。** 拆成可独立合入的最小单元，最不确定、风险最高的先做；脚手架和验证先于功能，并在改动前采好基线。单向门决定用 `architect`；已定下来的机械活不再比方案。只在接缝处并行派发，每个工作者独占 worktree 或分支。把阶段列表写下来，人审的就是它。
3. **跑循环。** 每个单元一次实验：说出假设、做最小改动、对真实产物按判断条件测量，有进展就留，没有就撤回（[sequence-verifiable-units](../writing-plans/references/principles/sequence-verifiable-units.md)）。用检查产物验证，不靠自我汇报。委派出去的活配评审，工作者钻关卡空子就重来并收紧约定；关卡本身错了就单独改关卡。结论只有 VERIFIED、NOT VERIFIED、INCONCLUSIVE，无法确定不算通过，不藏负面结果。
4. **留记录。** 用 `show-me-your-work` 记录这次运行，边做边记，每完成一步记一行。
5. **验证并交回。** 在真实产品上（不只是验证工具上）对照判断条件检查整体。反复出现的纠正写成关卡、lint 规则、检查或脚本（[encode-lessons-in-structure](../code-style/references/principles/encode-lessons-in-structure.md)）。回复写明：做法与严谨程度及理由、记录路径、已验证与未解决的部分。

## 严格模式要点

用户明确要求更严的工作方式，或任务长时间无人值守时，在上面各节之外再守这些。其余规则由对应技能负责，不在这里重复。

- **做完必须验证。** 宣布完成前对照真实产物验证，不拿替代指标或「能编译」当证明；没验证的明说。
- **数据形状先行。** 写任何代码前先说出数据形状，按 [model-the-domain](../code-style/references/principles/model-the-domain.md) 选结构。代码从简，倾向删除和最小改动。
- **文字去 AI 腔。** 给用户的回复、文档和提交信息按 `technical-writing`（含去 AI 腔清单）；代码里的 AI 味提交前用 `deslop` 清。
- **提问前先分类。** 答案是运行一下就能观察到的事实（行为、耗时、布局、输出），就做个草图让结果来决定，不问人。只有实验定不下来的产品或偏好决定才提问。完全自主时，授权范围内的决定直接做并汇报，操作者点名的审批关卡仍要遵守。
- **可以说「不」。** 被邀请扩大范围时按真实判断回答，必要时拒绝，不为附和而同意。
- **性能数字。** 报告测出来的加速或退化前，先按 [explain-the-number](../systematic-debugging/references/principles/explain-the-number.md) 走一遍。
- **上线界面或命令行。** 先在同一个界面上复现：界面用 `control-ui`，命令行用 `control-cli`，并写明实际跑了什么。
- **PR 与分支。** 提交、开 PR 和集成方式未定的分支收尾都用 `commit-pr`。任务中途发现某个技能本身坏了，报告问题和影响，已授权才修，已授权开 PR 才开。
- **长时间或无人值守。** 用 `show-me-your-work` 留决定记录；需要可审计记录且已授权提交时才提交，否则留在本地。
