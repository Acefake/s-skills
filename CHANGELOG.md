# 变更记录

## 1.0.32

### 修复

- 修复 Antigravity `PreInvocation` 钩子（`hooks/agy_hook.py`）在笼统提示词上附带 `systemMessage.metadata.user_markdown` 导致宿主静默丢弃整条 `injectSteps` 的问题：改为仅注入 `systemMessage`，并同步更新单元测试与钩子说明文档（可通过 `agy_hook.py --status` / `~/.wukong/prompt-hook-log.jsonl` 排查触发状态）。

## 1.0.31

### 删除

- 删除 `interrogate`（多模型对抗审查）。高风险改动的严审改为按 `requesting-code-review` 再派一个只读子代理复审，`architect` 草图的对抗审查同样走它。
- 删除 `apple-glass`、`theme-factory`、`html-mockup`、`automate-me`：界面风格、配色和静态设计稿由 `impeccable`（截图用 `control-ui`）承担，个人规则归纳由 `reflect --me` 承担。
- 合并 `no-comments` 进 `deslop`：只清注释时由 `deslop` 派 comment-sicko 只读审查，规则移到 `deslop/references/comment-sicko.md`，子代理定义同步改名。
- 合并 `unslop` 进 `technical-writing`：去 AI 腔清单移到 `technical-writing/references/unslop.md`，编号不变，各技能改为引用它。
- 合并 `finishing-a-development-branch` 进 `commit-pr`：集成方式未定时按 `commit-pr/references/finishing-branch.md` 核验、给出合并/PR/保留/丢弃选项并执行。全局规则路由表同步。
- 合并 `swarm` 进 `executing-plans`：并行群体作战移到 `executing-plans/references/swarm.md`，点名 swarm 时触发。
- 以上 9 个名字记入 `RETIRED_SKILLS`。技能总数 43 → 34，其中自动选用 20、点名 14。
- 移除 Cursor、WorkBuddy、CodeBuddy 宿主兼容：删除 `.cursor-plugin/` 清单、Cursor JSON Schema、`cursor-tools.md`、`workbuddy-tools.md`、WorkBuddy 本地链接与全局配置分支，并在 `check_supported_hosts` 中拦截退休宿主名与清单；分发宿主聚焦 Codex、Claude Code、Antigravity。
- 清理未使用的旧版文件与死代码：删除已改就地自检的 `brainstorming/spec-document-reviewer-prompt.md` 与 `writing-plans/plan-document-reviewer-prompt.md`，移除死函数 `improve_hook.build_context`、未使用导入/常量及过期检查分支。

### 新增

- `wukong-init` 新增第 4 步：按当前宿主能证实可派发的模型，为检索、规划、审查、测试四个子代理角色匹配模型（如 Claude Code 上检索 `haiku`、规划和审查 `opus`、测试 `sonnet`；不能按次选模或单模型宿主写 `继承`），整表确认后由新脚本 `scripts/models.py` 写入全局指令库块之后的 `<!-- wukong:models:start -->` 标记块。库块升级不碰它，`--show` 回读。
- 公共派发规则按「用户点名 → 模型块角色行 → 技能自带默认 → 继承」取模型；`how`、`why`、`reflect`、`executing-plans`（并行群体作战）、`requesting-code-review`、任务评审、只读检索与读项目的子代理各自标明角色。写代码的子代理仍继承父会话模型。角色模型被宿主拒绝时去掉模型重派一次。
- 四个角色带默认推理档位：检索 medium、规划 high、审查 high、测试 medium，派发时单独传给宿主的档位参数（Claude Code `effort`、Codex `model_reasoning_effort`、DeepSeek Harness `reasoning_effort`）；模型块某行写成 `opus（xhigh）` 可覆盖，`继承（high）` 只改档位。Antigravity、Hermes 不能按次传，不宣称已生效。`models.py --show` 输出每个角色实际的模型和档位。
- `global_instructions.py` 抽出通用受管块合并，个人块与模型块共用。
- `prompt-sharpen` 钩子触发可见性：只在提示词看起来笼统（短、只有泛化动作、没有文件、代码、数字等具体锚点）时，Claude Code 通过顶层 `systemMessage`、Antigravity 通过 `metadata.user_markdown` 在界面显示一行轻提示（不占模型上下文，`WUKONG_HOOK_NOTICE=0` 关闭）；同时将最近 50 条触发结果（含跳过原因，不存原文）记入 `~/.wukong/prompt-hook-log.jsonl`（`WUKONG_HOOK_LOG=0` 关闭），支持 `improve_hook.py --status` 与 `agy_hook.py --status` 随时排查。
- 正式支持 Google Antigravity 插件宿主：放行 `check_marketplace.py` 的 Antigravity 宿主校验，新增 [antigravity-tools.md](plugins/wukong/skills/wukong-router/references/antigravity-tools.md)，并在 `HOSTS.md`、`README.md`、`wukong-init`、`global_instructions.py`、`models.py`、`profile.py` 中接入 `--host antigravity`（插件自带 `rules/AGENTS.md` 不重复写库块，模型块与个人块写入 `~/.gemini/config/AGENTS.md`）。

### 修复

- 后台运行提醒的误报：判断长命令前先去掉引号里的字符串和 heredoc 正文，`echo '… npm run dev …'` 或 `grep "tail -f"` 不再触发提醒；`bash -c '…'` 这类真正执行的引号脚本照常检查。
- 同步 `docs/architecture.md` 卡片数量说明（45 → 34）与 `wukong-panorama.html` 标题版本号。

## 1.0.30

### 新增

- Antigravity 接入 `prompt-sharpen` 钩子：插件根 `hooks.json` 新增 `wukong-prompt-sharpen`（`PreInvocation`），由 `hooks/agy_hook.py` 复用 `improve_hook.py` 评估 `lastUserInput`，按 `(conversationId, lastUserInput)` 去重避免多步工具循环和后台唤醒重复注入，并同进程写入本地使用日志。

### 删除

- 删除 `setup-s-models` 和六角色模型配置：技能不再读取 `# s 模型配置` 标记段、`t3:` 角色别名或 `wukong.t3.json`，子代理默认继承父会话模型，用户本次点名的模型优先。`how`、`why`、`interrogate`、`reflect`、`swarm` 保留各自内置的模型默认（判断用强模型、调查和写代码用快模型）。同时删除 `s_models.py`、`t3_targets.py`、`t3_catalog.py`、`t3_hosts.py` 及其测试，三个依赖角色行的评测用例，项目级 `AGENTS.md`、`wukong.t3.json`、`docs/project/s-model-fallbacks.md` 和 `docs/wukong/model-budget-profiles.md`。DeepSeek Harness 与 Hermes 参考只保留技能目录和子代理能力。
- 初始化统一为 `wukong-init`：`setup-s-instructions` 的脚本和参考并入 `wukong-init/`，原技能删除；两个旧名记入 `RETIRED_SKILLS`。会话开始钩子、日常自检和 Codex 钩子检查改指向 `wukong-init`。技能总数 45 → 43，其中自动选用 21、点名 22。

### 修改

- 收窄 `executing-plans` 描述，只在已有书面计划、隔离工作区、并行子代理共用文件、循环检查时触发；扩充 `code-style`（可重跑脚本、写成 lint、迁移旧接口、先定数据结构）、`brainstorming`（取舍范围、从头设计）、`e2e-testing`（Playwright 超时）、`writing-plans`（拆成可验证小步）、`requesting-code-review`（跑一遍证明）的触发语。sonnet 触发评测由 47/57 提升到 55/56。
- 新增评测 `no-init-on-unrelated`：无关请求不触发 `wukong-init`。

### 修复

- `improve_hook.py` 与 `journal.py` 解包 T3 Code 包装标签（`<t3_code_instructions>`、`<user_request>`、`<runtime_info>` 等）并跳过 `[T3 Code:` 与 `Delegated task ` 系统/代理消息，避免短回复误触发和日志误记。

## 1.0.29

### 删除

- 删除 `orca-bots`，不再提供 Orca bot 创建技能；名字记入 `RETIRED_SKILLS`。技能总数 46 → 45，其中自动选用 22、点名 23。

## 1.0.28

### 修改

- 把 `orca-bot-pr-review`、`orca-bot-bug-hunt`、`orca-bot-ci-triage`、`orca-bot-deps`、`orca-bot-release` 合并成一个自动选用的 `orca-bots`：一次对话就能提议多个开发 bot。用户点了名的只建那几个，说“一套”或没指定就建全部 5 个，已有的跳过。在 bot 聊天里依次弹卡片；已有 bot 时一封邮件把全部提议命令交给它；一个 bot 都没有时，先在界面里建第一个，再由它提议其余的。五个 bot 的设定收进 `references/catalog.md`，配套 bot 技能放在 `assets/`，原 `ORCA-BOTS.md` 并入技能正文。旧的五个名字记入 `RETIRED_SKILLS`。
- 技能总数 50 → 46，其中自动选用 23、点名 23。

## 1.0.27

### 新增

- 5 个自动选用的 Orca bot 技能：`orca-bot-pr-review`、`orca-bot-bug-hunt`、`orca-bot-ci-triage`、`orca-bot-deps`、`orca-bot-release`。它们只调用 Orca 自带的命令行：选 Orca 内置模板（`pr-review`、`bug-investigation`、`ci-failures`、`dependency-updates`、`release`），把名字和用途换成中文设定，再提议创建。在 bot 聊天里用 `orca bot create --offer` 弹卡片；已有别的 bot 时发邮件请它弹卡片；一个 bot 都没有时给出在 Orca 界面里创建的步骤。建好后把 `assets/bot-skill.md` 放进 bot home 的 `skills/<名>/SKILL.md`，目标已存在且内容不同时先问用户。共用流程在 `plugins/wukong/ORCA-BOTS.md`。
- 技能总数 45 → 50，其中自动选用 27、点名 23。

## 1.0.26

### 修改

- 压缩插件图标 `plugins/wukong/icon.png`（1254×1254 1.11 MB → 512×512 25.5 KB，保留透明背景并去除冗余元数据），删除已无活跃引用的旧全景图 `docs/s-skills-route.png`（1.46 MB）。

## 1.0.25

### 修改

- 把 `wukong-mode`、`wukong-agent`、`figure-it-out`、`timed-loop`、`using-git-worktrees`、`subagent-driven-development` 并入自动调用的 `executing-plans`：一个技能覆盖主会话按计划执行、派子代理逐任务执行、隔离工作区、循环检查、没有现成流程时先定可审计做法，以及严格模式要点。原 `subagent-driven-development` 的提示词模板、`references/`、`scripts/` 整体搬入；`subagents.md`、`host-fallback.md`、`execution-boundaries.md` 搬入 `references/`，`non-negotiable-rules.md` 的必要内容并入「严格模式要点」。`wukong-mode` 的 `playbooks/`、`bugbot-triage`、`catch-up`、`playbook-routing`、`writing-the-reply`、`orch`、`watch-pr`、`worktree-audit.sh`、`check-plan.mjs` 等不再保留，`agents/wukong-agent.md` 一并删除。全库对这些技能和路径的引用改指 `executing-plans`。
- 删除 `pptx`、`pdf`、`xlsx`；`docx` 自带 OOXML 脚本，不受影响。
- 技能总数 54 → 45，其中自动选用 22、点名 23；旧版全局规则冻结为 `full-instructions-v10.txt`，无标记旧配置仍可原位迁移。
- 全景图改为单独维护：`check_marketplace.py` 不再校验全景卡片，README 和架构说明不再内嵌全景 PNG。

## 1.0.23

### 改动

- 24 个 `principle-*` 不再作为自动技能常驻，正文原样迁入所属技能的 `references/principles/`：调试类归 `systematic-debugging`，设计类归 `brainstorming`，计划类归 `writing-plans`，测试类归 `test-strategy`，子代理协作类归 `subagent-driven-development`，代码设计类归 `code-style`。所属技能新增原则索引节，全库引用改为指向新文件。常驻上下文约 5,248 → 约 3,572 token，自动技能 48 → 24，技能总数 78 → 54。
- `install_local_skills.ps1` 会清理指向已删除技能的悬空 Junction，安装冲突被拒时不清理。

## 1.0.19

### 新增

- `mcp-builder`（设计工具契约、实现并联调 MCP 服务）、`remotion-create`（用 Remotion 编排并渲染视频）、`theme-factory`（统一配色和字体，附十套预设）。三者都为点名调用（`disable-model-invocation: true`，Codex 同步关闭隐式调用）；`mcp-builder`、`theme-factory` 改编自 Anthropic Agent Skills（Apache 2.0），署名见 `docs/third-party-licenses.md`。共 78 个技能，其中 48 个按描述自动选用、30 个点名。

### 改动

- `prompt-sharpen` 的每条提示词评估说明不再复述用户原话，缺口判断标准保留，约 318 → 约 184 token；加上三个新技能改为点名调用，常驻上下文实测约 5380 → 约 5250（上限 5650）。
- 本地使用日志先脱敏再截断，修复密钥落在截断位置时前缀原样写入 `journal.db` 的问题；新增 JWT、`Bearer` 请求头和 `token`/`password`/`api_key` 键值的脱敏；技能名、日期文件名和仓库路径不再被当成长串抹掉，`token: 中文说明` 这类文字也不再被吞掉。
- `SessionStart` 钩子改为同进程加载全局规则检查，不再嵌套起第二个 Python 进程，实测启动耗时约 286 ms → 约 150 ms。

### 修复

- `scripts/install_local_skills.ps1` 能识别并迁移指向本仓库旧插件目录（`plugins/s-atlas`、`plugins/s-wukong`）的 Junction，并清理其中已退役技能的残留链接；指向其他位置的链接和真实目录仍然拒绝，且校验先于任何清理。
- `docs/architecture.md` 的专项技能数量与「专利」旧描述与实际不符。

## 1.0.18

### 修复

- Codex：补齐钩子升级检测与迁移（`codex_hooks.py`），日常自检和 `wukong-init` 会提示旧路径钩子。

## 1.0.17

### 新增

- 本地使用日志（个人学习层第 1 期）：`hooks/journal.py` 把会话开始、技能加载、用户纠正、明说的偏好和任务摘要写进本机 SQLite 数据库 `~/.wukong/journal.db`。每条一个事务，多会话并发写不丢数据；不打印、不占上下文、不上传；原话只留前 80 字并脱敏，90 天以前或超过 5 万条自动删除，`WUKONG_JOURNAL=0` 关闭，`journal.py --dump` 查看。设计见 `docs/wukong/specs/2026-11-13-personal-learning-design.md`。
- 个人规则（个人学习层第 2 期）：`reflect --me` 读本机使用日志，把反复出现的纠正和明说的偏好归纳成个人规则，展示差异并确认后写进全局规则里单独的 `wukong:personal` 块；库块升级不碰它。`reflect/scripts/profile.py` 按规则引用的日志编号自己算来源和证据（学来的至少 2 个会话，明说的 1 次），并负责 8 周过期、500 token 上限、禁学内容（推送、跳过确认、发布、密钥、网址、命令，以及从纠正里推断的放松测试或审查；中英文和全角写法都拦）、拒绝能破坏规则块的文字、加锁写入、写入失败不改规则、备份 20 份；另有 `--show`、`--undo`、`--forget`、`--off`、`--on`，用户亲口要求的规则走 `add`。
- 常驻上下文上限：`scripts/context_budget.py` 估算每个会话常驻的 token（自动技能描述、全局规则、钩子注入），`check_marketplace` 超过 5650 就失败。本版实测约 5380，1.0.16 约 6980。

### 改动

- 低频技能改为点名调用（`disable-model-invocation: true`，Codex 同步关闭隐式调用）：`docx`、`pptx`、`xlsx`、`pdf`、`technical-writing`、`html-mockup`、`apple-glass`、`archify`。不再常驻技能列表，用时直接点名，如「用 docx 做一份报告」。全局规则和 `wukong-router` 的路由表同步改为「点名时加载，未点名直接做」，触发用例去掉这些点名技能。
- 删除 `translate`、`frontend-design`、`patent-disclosure`、`patent-application`。翻译由模型直接做，界面设计用 `impeccable`。全局规则去掉对应行，旧版规则冻结为 `full-instructions-v8.txt`，已安装的无标记规则仍能原位迁移。
- 合并三个附属技能，正文移入宿主技能的 `references/`：`comment-sicko` → `no-comments`（同名子代理保留，改读新路径），`benchmark-checklist` → `principle-explain-the-number`，`ketchup` → `wukong-mode` 的 `catch-up.md`（autopilot 剧本的补进度回复照旧）。
- `apple-glass` 改为通用的 Apple TV 风格界面语言，去掉影盒专属的仓库、路径和检查命令，类名前缀 `yb-` 改为 `ag-`。
- 技能从 82 个减到 75 个：48 个自动，27 个点名。
- 小任务提速：只动一两个文件、不改接口的修 bug 归第 1 档，不强制先写失败测试；第 0、1 档自审只看 diff。独立评审子代理只在第 3 档（跨模块、改接口或依赖、迁移）或涉及权限、并发、共享状态、数据删除时派，原先任何修 bug 哪怕一行都会派。
- 全局规则「只读检索派发」细则移到 `wukong-router`，全局只留一句授权；旧规则冻结为 `full-instructions-v9.txt`。
- prompt-sharpen 钩子跳过「可以」「继续」这类确认和 4 个字以内的消息，这些消息不再附约 300 token 的评估说明。

## 1.0.16

### 修复

- 写入确认也用提问工具弹窗：共用的交互提问规则原先写「只有工具允许用于写入确认时才用它」，Codex 等宿主的提问工具没有写明这一点，于是写入确认退回了文字提问。现在先在对话里展示差异，再用同一提问工具给出「确认写入 / 先不写」等选项，只有工具不可用、报错或宿主明确禁止时才退回文字。
- `setup-s-models` 只拉一次能力目录就计算推荐，只对 `catalog` 标为可能截断的缺失模型补搜；原流程按白名单逐个 search，每次都返回全部提供商，白白占用大量上下文。

## 1.0.15

### 改动

- `setup-s-models` 在 T3 中按本机目录推荐角色模型：新增 `references/model-allowlist.json`（白名单、各角色偏好顺序、`providerOnly`），`scripts/t3_catalog.py catalog` 合并能力快照与 search 结果，每个角色沿偏好顺序取本机可用的前 4 个，缺哪家就往后补；白名单零匹配时退回本机完整目录，首项为 inherit-parent。Cursor 只露出 Grok 4.7 与 Composer 2.5，Claude 模型只走 Claude。
- 配置流程第 3 步改为弹窗：先问全部用推荐 / 逐个选 / 只改几个，再每个角色一次提问选首选模型、首选档位、次选模型、次选档位；用户填的编号或模型 ID 由 `t3_catalog.py pick` 校验。
- `wukong.t3.json` 升到 schemaVersion 2，目标可带 `fallback` 保存顺序次选；check 同时校验次选，resolve 每项返回 `fallback`，角色行的显式档位只作用于首选。schemaVersion 1 仍可读取，configure 写入统一为 2。原先只记在 `s-model-fallbacks.md` 的次选，可经确认后迁进 `fallback`。

## 1.0.14

### 改动

- 全局规则新增「只读检索派发」：预计读十个文件以上或大日志、只要结论且问题明确的只读调查，默认授权并发 2 个（三条独立边界才 3 个）「检索与探索」子代理，摘要约 30 行内；小范围、查完要改、需判断语义的仍由主代理直接查。该授权不含改文件、测试、提交，实现类子代理仍需用户要求。
- `wukong-mode` 并发只读检索和 T3 编排参考同步引用这条授权。已安装用户同步全局规则后生效。
- 提示词评估钩子的说明从约 440 token 压到约 310 token，判断标准不变；原话只引用前 200 字，长粘贴和交接摘要不再整段重复进上下文。
- T3 编排参考只保留派发时要用的角色、解析、路由与等待规则；模型目标格式、宿主路径表、作用域继承和配置写入移到 `setup-s-models/references/t3-config.md`，每次 T3 派发少读约 3k token。

## 1.0.13

### 改动

- 适配 CodeBuddy（CLI 与 IDE）：它会读取 `.claude-plugin` 清单，所以不新增清单，直接用 `/plugin marketplace add Acefake/s-skills` 和 `/plugin install wukong@s-skills`。README、宿主适配和 WorkBuddy 参考同步说明，CodeBuddy 与 WorkBuddy 共用 `~/.codebuddy`，宿主 id 仍是 `workbuddy`。
- 市场校验不再把 CodeBuddy 当作退役宿主；仍拒绝重复的 `.codebuddy-plugin` 清单。

## 1.0.12

### 改动

- 插件名从 `s-wukong` 改为 `wukong`，目录迁至 `plugins/wukong`，安装 id 为 `wukong@s-skills`；市场和仓库名称不变。
- 六个 `s-` 技能统一改为 `wukong-agent`、`wukong-init`、`wukong-mode`、`wukong-proposal`、`wukong-review`、`wukong-router`；其他技能名不变。
- 保留旧品牌全局规则、模型目标和事务的识别能力；冻结历史规则样本，避免无标记旧规则迁移时重复追加。
- 更新悟空 logo，并同步宿主清单、安装说明与架构证据链接。

## 1.0.10

### 改动

- 插件名从 s-atlas 改为 s-wukong，目录为 `plugins/s-wukong`。安装 id 从 `s-atlas@s-skills` 改为 `s-wukong@s-skills`。
- 仓库地址仍是 https://github.com/Acefake/s-skills ，marketplace 名仍是 s-skills。各技能自己的名字不变。
