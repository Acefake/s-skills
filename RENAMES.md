# 技能改名

1.2.0 把技能目录和 `name` 改成英文小写 kebab-case，文件夹名等于 `name`。
技能在 `plugins/s-atlas/skills/`，随插件分发。1.3.0 删掉了原来放在 `archive/s/` 的 39 个归档技能，名字留在 `scripts/marketplace_lib.py` 的 `RETIRED_SKILLS`。

活跃 61：原来的 50 个（含 frontend-design）加上 11 个开发流程技能。
归档 38：原来的 35 个，加上 3 个和现有技能重叠、因此不进 `skills/` 的开发流程技能。

`frontend-design`（原「有主见的界面」）保留为手点技能，`disable-model-invocation: true`。日常做界面仍自动用 `impeccable`。

1.2.1 把 `description` 改成中文在前、英文 `Use when` 在后。1.2.2 起直接写中文句子：`……。Use when ... .`。英文 `Use when` 接在中文句号后面。技能和 agent 说明用同一写法。

1.5.0 新增 `docx`、`pptx`、`xlsx`、`pdf`、`commit-pr`、`translate`。它们没有旧中文名。`teach` 仍然删除，讲解走 `how`（问动机再用 `why`）。`technical-writing` 从这一版起可以按描述自动选用，Word 文件不归它。

1.5.1 新增 `s-proposal`。1.5.2 新增 `s-review`（中文代码审查，默认只出报告）。它们没有旧中文名。

1.6.0 把插件名从 `s` 改为 `s-atlas`，目录从 `plugins/s/` 改为 `plugins/s-atlas/`。技能名仍用原来的 `s-` 前缀，例如 `s-review`、`s-proposal`。市场名仍是 `s-skills`，仓库名不变。安装命令是 `/plugin install s-atlas@s-skills`。当前插件版本 1.6.0，活跃技能 72 个。

## 回滚

要恢复一个已删除的技能，从 1.3.0 之前的提交里取回 `archive/s/<英文名>/`，放到 `plugins/s-atlas/skills/<英文名>/`，从 `RETIRED_SKILLS` 删掉它，把 `scripts/marketplace_lib.py` 里的 `EXPECTED_SKILL_COUNTS` 加一，然后更新版本锁。
整次改名可以回退 1.2.0 的提交。旧中文名不再作为目录或 `name` 使用。

## 旧名到新名

| 旧名 | 新名 | 状态 |
|---|---|---|
| s助手 | s-agent | 活跃 |
| 专挑注释 | comment-sicko | 活跃 |
| 设置s模型 | setup-s-models | 活跃 |
| 代码怎么工作 | how | 活跃 |
| 代码为什么这样 | why | 活跃 |
| 先画架构草图 | architect | 活跃 |
| 并行群体作战 | swarm | 活跃 |
| 多方案竞技场 | arena | 活跃 |
| 多模型对抗审查 | interrogate | 活跃 |
| 清理AI腔 | unslop | 活跃 |
| 清理代码腔 | deslop | 活跃 |
| 清理代码注释 | no-comments | 活跃 |
| 技术写作 | technical-writing | 活跃 |
| 编写skill | author-skill | 活跃 |
| 操作界面 | control-ui | 活跃 |
| 操作命令行 | control-cli | 活跃 |
| 基准测试清单 | benchmark-checklist | 活跃 |
| 决定记录日志 | show-me-your-work | 活跃 |
| 自定流程搞定 | figure-it-out | 活跃 |
| 定时循环 | timed-loop | 活跃 |
| 反思并改skill | reflect | 活跃 |
| 测试驱动修bug | tdd | 活跃 |
| 补上对话进度 | ketchup | 活跃 |
| 精致界面设计 | impeccable | 活跃 |
| 有主见的界面 | frontend-design | 活跃 |
| 原则-偷懒守则 | principle-laziness-protocol | 活跃 |
| 原则-基础优先 | principle-foundational-thinking | 活跃 |
| 原则-从头重新设计 | principle-redesign-from-first-principles | 活跃 |
| 原则-质疑前提 | principle-attack-the-premise | 活跃 |
| 原则-先减后加 | principle-subtract-before-you-add | 活跃 |
| 原则-减轻读者负担 | principle-minimize-reader-load | 活跃 |
| 原则-结果导向 | principle-outcome-oriented-execution | 活跃 |
| 原则-体验优先 | principle-experience-first | 活跃 |
| 原则-穷尽设计空间 | principle-exhaust-the-design-space | 活跃 |
| 原则-打造杠杆 | principle-build-the-lever | 活跃 |
| 原则-为领域建模 | principle-model-the-domain | 活跃 |
| 原则-守住边界 | principle-boundary-discipline | 活跃 |
| 原则-类型系统纪律 | principle-type-system-discipline | 活跃 |
| 原则-操作幂等 | principle-make-operations-idempotent | 活跃 |
| 原则-迁完再删旧API | principle-migrate-callers-then-delete-legacy-apis | 活跃 |
| 原则-先分开共享状态 | principle-separate-before-serializing-shared-state | 活跃 |
| 原则-证明真能用 | principle-prove-it-works | 活跃 |
| 原则-修根本原因 | principle-fix-root-causes | 活跃 |
| 原则-可验证小单元 | principle-sequence-verifiable-units | 活跃 |
| 原则-测行为不测实现 | principle-test-behavior-not-implementation | 活跃 |
| 原则-解释数字 | principle-explain-the-number | 活跃 |
| 原则-守住上下文 | principle-guard-the-context-window | 活跃 |
| 原则-别卡着等人 | principle-never-block-on-the-human | 活跃 |
| 原则-教训写进结构 | principle-encode-lessons-in-structure | 活跃 |
| 前端设计品味 | taste-skill | 已删 |
| 高端视觉设计 | premium-visual | 已删 |
| 全套视觉设计 | visual-suite | 已删 |
| 设计系统 | design-system | 已删 |
| UIUX知识库 | ui-ux-pro-max | 已删 |
| 网页设计规范 | web-design-guidelines | 已删 |
| 苹果式设计 | apple-design | 已删 |
| shadcn组件 | shadcn | 已删 |
| 选前端库 | pick-frontend-lib | 已删 |
| 界面压力测试 | break-ui | 已删 |
| 多版本原型 | prototype | 已删 |
| 手机原生手感 | native-mobile-feel | 已删 |
| s做Bot界面 | make-bot-ui | 已删 |
| 做动画 | animate | 已删 |
| 找动画机会 | find-animation-opportunities | 已删 |
| 动画审查 | review-animations | 已删 |
| 动画性能 | animation-performance | 已删 |
| 动画改进计划 | improve-animations | 已删 |
| 动画术语表 | animation-glossary | 已删 |
| Expo动画 | expo-animate | 已删 |
| Emil设计理念 | emil-design | 已删 |
| Sonner用法 | ask-sonner | 已删 |
| 动手前磨清任务 | sharpen | 已删 |
| 根除重复错误 | correct | 已删 |
| 改动影响范围 | blast-radius | 已删 |
| 回想最近工作 | recall | 已删 |
| 复述用户目标 | in-your-own-words | 已删 |
| 按我习惯定制 | automate-me | 已删 |
| 创建验证skill | create-verification-skill | 已删 |
| 维护验证skill | maintain-verification-skill | 已删 |
| TypeScript最佳实践 | typescript-best-practices | 已删 |
| 一步步教我 | teach | 已删 |
| 说人话重讲 | plain-language | 已删 |
| 自我改进 | self-improvement | 已删 |
| s使用帮助 | s-help | 已删 |
| （无旧中文名） | s-router | 活跃 |
| （无旧中文名） | brainstorming | 活跃 |
| （无旧中文名） | writing-plans | 活跃 |
| （无旧中文名） | executing-plans | 活跃 |
| （无旧中文名） | subagent-driven-development | 活跃 |
| （无旧中文名） | systematic-debugging | 活跃 |
| （无旧中文名，与 principle-prove-it-works 重叠） | verification-before-completion | 已删 |
| （无旧中文名） | requesting-code-review | 活跃 |
| （无旧中文名） | receiving-code-review | 活跃 |
| （无旧中文名） | using-git-worktrees | 活跃 |
| （无旧中文名） | finishing-a-development-branch | 活跃 |
| （无旧中文名，与 tdd 重叠） | test-driven-development | 已删 |
| （无旧中文名，与 swarm 重叠） | dispatching-parallel-agents | 已删 |
| （无旧中文名，与 author-skill 重叠） | writing-skills | 已删 |

## 删除原因

| 新名 | 原因 |
|---|---|
| taste-skill | 和 impeccable 重叠，偏落地页 |
| premium-visual | 同一类视觉方向，且本来就只允许点名 |
| visual-suite | 品牌、幻灯片、横幅，范围过宽 |
| design-system | 和 impeccable 的令牌、设计系统重叠 |
| ui-ux-pro-max | 查表用，和 impeccable 抢同一句「做个页面」 |
| web-design-guidelines | 检查清单，impeccable 已覆盖审查 |
| apple-design | 单一风格，s-mode 不读 |
| shadcn | 只有项目用 shadcn 才需要 |
| pick-frontend-lib | 偶尔选型 |
| break-ui | 偶发 |
| prototype | s-mode 读的是原则 principle-exhaust-the-design-space，不读这份 |
| native-mobile-feel | 只做手机网页手感时才用 |
| make-bot-ui | 只做 webhook 机器人界面 |
| animate | 动画整批删掉；要恢复时先从 git 历史拿这一份 |
| find-animation-opportunities | 动画整批 |
| review-animations | 动画整批 |
| animation-performance | 动画整批 |
| improve-animations | 动画整批 |
| animation-glossary | 查词，低频 |
| expo-animate | 只做 Expo |
| emil-design | 和动画审查重复 |
| ask-sonner | 只服务一个 toast 库 |
| sharpen | s-mode 不读；日常用 brainstorming |
| correct | s-mode 不读 |
| blast-radius | s-mode 不读 |
| recall | s-mode 不读 |
| in-your-own-words | s-mode 不读 |
| automate-me | s-mode 不读 |
| create-verification-skill | s-mode 不读 |
| maintain-verification-skill | s-mode 不读 |
| typescript-best-practices | s-mode 不读；写 TS 多时优先从 git 历史拿回 |
| teach | s-mode 不读；how 和 why 已覆盖 |
| plain-language | 普通对话可以代替 |
| self-improvement | 和 reflect 重叠，s-mode 只读 reflect |
| s-help | s-mode 不读；目录改由 README 表格承担 |
| test-driven-development | 与 s-mode 点名的 tdd 重叠，只留 tdd |
| dispatching-parallel-agents | 与 s-mode 点名的 swarm 重叠，只留 swarm |
| writing-skills | 与 s-mode 点名的 author-skill 重叠，只留 author-skill |
| verification-before-completion | 与 s-mode 点名的 principle-prove-it-works 重叠，只留 principle-prove-it-works |
