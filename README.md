# s-atlas 中文技能

![s-atlas](plugins/s-atlas/icon.png)

一个独立维护的中文 AI 技能插件，版本 1.7.1。插件名是 `s-atlas`，不依赖其他插件。技能 **73** 个，全部随插件分发。目录名和 frontmatter 的 `name` 都是英文小写 kebab-case，两者相同。说明以用户会说的中文触发词起头，这些词放在前 100 个字里，中文句号后接英文 `Use when`；正文是中文。

旧中文名对照见 [RENAMES.md](RENAMES.md)。

## 安装

### Codex 本项目开发

克隆仓库后，在 Windows PowerShell 中运行：

```powershell
git clone https://github.com/Acefake/s-skills.git
cd s-skills
powershell -NoProfile -File scripts/install_local_skills.ps1
```

脚本把活跃技能链接到本项目的 `.agents/skills/`。重新打开项目会话后使用；修改源文件后无需重复复制技能。该方式只对本项目生效。

### 插件市场

Claude Code 和 WorkBuddy 在聊天中运行：

```text
/plugin marketplace add Acefake/s-skills
/plugin install s-atlas@s-skills
```

Codex 在终端添加市场，再在应用的插件管理入口安装 `s-atlas`：

```text
codex plugin marketplace add Acefake/s-skills
```

Hermes 克隆仓库后，在 `~/.hermes/config.yaml` 加外部技能目录，详见 [HOSTS.md](plugins/s-atlas/HOSTS.md#hermes)：

```yaml
skills:
  external_dirs:
    - ~/s-skills/plugins/s-atlas/skills
```

Cursor 从插件市场导入 `https://github.com/Acefake/s-skills`，选择 `s-atlas`。各宿主的命令支持与入口以实际界面为准。安装或更新后开启新会话，确认技能路径和版本。

### 让技能自动生效

短规则在 [`plugins/s-atlas/AGENTS-snippet.md`](plugins/s-atlas/AGENTS-snippet.md)。把它贴进全局指令：Claude Code 是 `~/.claude/CLAUDE.md`，Codex 是 `~/.codex/AGENTS.md`，OpenCode 是 `~/.config/opencode/AGENTS.md`，Cursor 建一条 Always 规则。Hermes 没有全局指令文件，放进项目根的 `AGENTS.md`，或追加到 `~/.hermes/SOUL.md`。规则要求动手前先看可用技能，用对得上的那个；拿不准就用 `s-router`。

要按任务查表，贴同目录的 [`plugins/s-atlas/AGENTS.md`](plugins/s-atlas/AGENTS.md)。用 DeepSeek V4.1 Flash 跑同样 10 条请求，Codex 不加时 7 条用对技能，加了 8 条；Hermes 不加时 5 条，加了 10 条。那次测量里 Codex 没用对的两条是 `how` 和 `technical-writing`。`how` 仍是手点。`technical-writing` 从 1.5.0 起按描述自动选用。

## 技能怎么被选中

![s-atlas 技能路由图：从一句话开始，经 AGENTS.md 和 s-router 走到四条路径。图表示路由形状，当前有哪些技能以下面的对照表为准](docs/s-skills-route.png)

一句话进来后，宿主先读 `AGENTS.md`，再由 `s-router` 从上往下判断：

1. 点名了技能：直接加载它。手点技能只有这样才会用。
2. 小改动（意图明确、只动 1–2 个文件、不改接口、数据结构或依赖）：走快路，跳过 `brainstorming` 和计划，只加载对口的能力技能，交付前实际验证。
3. 新功能或改行为：走主流程，`brainstorming` → `writing-plans` → `using-git-worktrees` → `executing-plans` 或 `subagent-driven-development` → 代码审查 → `finishing-a-development-branch`。
4. 跨模块、大迁移或要并行：点名 `s-mode`，按需配 `figure-it-out`、`refactor-architecture`、`swarm`、`arena`。

都不是时，按描述自动选能力技能。图下半部分列出每个技能何时用、做什么；彩色底是自动选用，白底虚线是手点。

## 使用

点名技能，并说明目标和完成条件：

```text
用 s-mode 修复这个问题，复现后定位原因，修完运行实际流程验证。
用 how 解释这个模块的入口、数据流和关键文件。
用 impeccable 检查这个设置页，并给出具体改进。
```

支持插件命令的宿主也可以使用 `/s-atlas:技能名`，例如 `/s-atlas:s-mode`。Codex 可在技能选择器中选择相应技能。

原则、`setup-s-models`、`impeccable`、`technical-writing`、`docx`、`pptx`、`xlsx`、`pdf`、`commit-pr`、`translate`、`s-proposal`、`s-review`，以及开发流程技能（`brainstorming` 到 `finishing-a-development-branch`）可以按描述自动选用。`s-review` 审 PR、分支或本地改动，默认只出报告。`frontend-design` 只在点名时使用，日常做界面走 `impeccable`。工作模式和并行审查等复杂流程需要点名。自动选用不表示每轮都会执行；能不能做到还取决于宿主提供的工具。

## 我想做什么

| 我想做什么 | 用哪个 skill |
|---|---|
| 修 bug、报错、结果不对 | `systematic-debugging` |
| 有便宜的测试点，先写失败测试再修 | `tdd` |
| 做新功能、改行为 | `brainstorming`，然后 `writing-plans` |
| 按写好的计划做 | `executing-plans` 或 `subagent-driven-development` |
| 做完了，还没决定合并、开 PR、留着还是丢掉 | `finishing-a-development-branch` |
| 写提交说明、提交、开 PR | `commit-pr` |
| 审 PR、分支或本地改动 | `s-review` |
| 写或改 Word（.docx） | `docx` |
| 做幻灯片（.pptx） | `pptx` |
| 做表格、公式（.xlsx） | `xlsx` |
| 读、填或生成 PDF | `pdf` |
| 写 README、写文档、RFC、PR 说明的句子 | `technical-writing` |
| 中文和英文互译，或中英对照 | `translate` |
| 教我这块代码怎么工作 | `how` |
| 问为什么这样设计 | `why` |
| 做页面、改界面、看卡顿 | `impeccable` |
| 点名要一份有主见的视觉方向 | `frontend-design` |
| 文件放哪、文档注释、代码质量 | `code-style` |
| 决定在哪一层测 | `test-strategy` |
| 写或修 Playwright 端到端测试 | `e2e-testing` |
| 点名走加强工作流 | `s-mode` |
| 找浅模块、出架构报告 | `refactor-architecture` |
| 画架构图、流程图、时序图、ER 图 | `archify` |
| 提交前清代码里的 AI 味 | `deslop` |
| 做事时的取舍（能删就删、先验证、别卡着等人等） | 24 条 `principle-*`，按描述自动选用 |

- [全部活跃技能](plugins/s-atlas/skills/)
- [工作模式](plugins/s-atlas/skills/s-mode/SKILL.md)
- [模型设置](plugins/s-atlas/skills/setup-s-models/SKILL.md)
- [改名对照与回滚](RENAMES.md)
- [Codex、Cursor、Hermes 等宿主适配规则](plugins/s-atlas/HOSTS.md)

## 活跃技能

「自动」是模型按描述自己选用；「手点」是 frontmatter 里有 `disable-model-invocation: true`，要点名才会加载。

### 自动选用（53 个）

| 技能 | 用途 |
|---|---|
| `s-router` | 日常先查该用哪个技能 |
| `brainstorming` | 做功能前先把方案磨清 |
| `writing-plans` | 把活写成可执行计划 |
| `executing-plans` | 按写好的计划做 |
| `subagent-driven-development` | 用子智能体推进计划 |
| `systematic-debugging` | 按证据排错 |
| `requesting-code-review` | 发起代码审查 |
| `receiving-code-review` | 处理审查意见 |
| `using-git-worktrees` | 用 worktree 隔开工作 |
| `finishing-a-development-branch` | 收尾开发分支 |
| `impeccable` | 做页面、改界面、做设计审查；`optimize` 守交互性能预算（INP、长任务、帧率、包体积） |
| `docx` | 创建、修订、批注和阅读 Word。中文设置 `w:eastAsia` |
| `pptx` | 用 HTML 或模板做幻灯片。中文指定 CJK 字体并留余量 |
| `xlsx` | 带公式的工作簿，保存后用 LibreOffice 重算 |
| `pdf` | 提取、填表、合并拆分、OCR 和新建 PDF |
| `code-style` | 按模块就近放文件、写文档注释、质量底线；覆盖 TS/React、Vue、Go、Java |
| `test-strategy` | 定每个行为在哪一层测、用什么工具；覆盖 TS/React、Vue、Go、Java |
| `e2e-testing` | 用 Playwright 写稳定的端到端测试，修不稳定的测试 |
| `tdd` | 修 bug 时有便宜的测试点就先写失败测试 |
| `setup-s-models` | 给各角色配模型和预算 |
| `archify` | 画架构图、流程图、时序图、ER 图等，出可交互单文件 HTML，需要 Node 18+ |
| `deslop` | 提交前清掉代码里的 AI 味 |
| `technical-writing` | 写 README、写文档、RFC、PR 说明的句子。Word 用 `docx` |
| `commit-pr` | 看 diff，写提交说明，推送并开 PR。集成方式还没定用 `finishing-a-development-branch` |
| `translate` | 中英翻译，可中英对照。代码、命令、路径不译 |
| `s-proposal` | 写中文方案：先问清目标，列提纲，再按固定结构起草打磨 |
| `s-review` | 中文代码审查：审 PR、分支或本地改动，带出处和严重程度，给合并结论 |
| `control-ui` | 在真浏览器里操作界面取证 |
| `control-cli` | 在本地操作命令行或 TUI |

Python 用 3.12，推荐 `uv`。docx 和 pptx 还要 Node.js（在技能目录里 `npm install` 一次）。看页面需要 LibreOffice 和 poppler。docx 阅读需要 pandoc。中文渲染检查要安装 Noto CJK（Debian/Ubuntu：`fonts-noto-cjk`）。PDF 的扫描件 OCR 另要 Tesseract。

#### 原则（24 个）

| 技能 | 用途 |
|---|---|
| `principle-laziness-protocol` | 能删就删，只留最小改动 |
| `principle-foundational-thinking` | 写逻辑前先定数据结构 |
| `principle-redesign-from-first-principles` | 新需求按第一性原理重做设计 |
| `principle-attack-the-premise` | 同一前提反复修不好就先验证前提 |
| `principle-subtract-before-you-add` | 先删多余的再加 |
| `principle-minimize-reader-load` | 减少读者要记住的层数 |
| `principle-outcome-oriented-execution` | 迁移直接走向目标结构 |
| `principle-experience-first` | 取舍时先顾使用体验 |
| `principle-exhaust-the-design-space` | 没先例时先做几个方案再选 |
| `principle-build-the-lever` | 不简单的活做成可再跑的工具 |
| `principle-model-the-domain` | 把领域写进一个结构 |
| `principle-boundary-discipline` | 校验放在系统边界 |
| `principle-type-system-discipline` | 让非法状态无法表示 |
| `principle-make-operations-idempotent` | 崩溃重试后仍落到同一结果 |
| `principle-migrate-callers-then-delete-legacy-apis` | 迁完调用方再删旧 API |
| `principle-separate-before-serializing-shared-state` | 并发写入前先去掉共享 |
| `principle-prove-it-works` | 完成前对照真实结果验证 |
| `principle-fix-root-causes` | 在第一次出错的地方修 |
| `principle-sequence-verifiable-units` | 拆成可验证的小步 |
| `principle-test-behavior-not-implementation` | 测使用者能看到的行为 |
| `principle-explain-the-number` | 相信数字前先解释它量的是什么 |
| `principle-guard-the-context-window` | 大块内容交给子智能体 |
| `principle-never-block-on-the-human` | 可撤销的事先做再给人看 |
| `principle-encode-lessons-in-structure` | 第二次出现的教训写成检查 |

### 手点（20 个）

| 技能 | 用途 |
|---|---|
| `frontend-design` | 点名时给一份有主见的视觉方向，不带检查脚本 |
| `s-mode` | 点名才走的加强工作流 |
| `s-agent` | 派出去写代码的子智能体 |
| `comment-sicko` | 被清注释技能派去删注释 |
| `how` | 改之前讲清代码怎么串 |
| `why` | 查为什么这样设计 |
| `architect` | 动手前定类型和模块边界 |
| `refactor-architecture` | 找浅模块和耦合，出 HTML 报告，再逐个追问定案 |
| `swarm` | 并行覆盖、比赛、分片验证 |
| `arena` | 同一任务多方案再嫁接 |
| `interrogate` | 多模型对抗审查 |
| `unslop` | 去掉文字里的 AI 腔 |
| `no-comments` | 审查前删掉不该留的注释 |
| `author-skill` | 按规范写或大改 SKILL.md |
| `benchmark-checklist` | 报告性能数字前先审核 |
| `show-me-your-work` | 长时间运行留下决定记录 |
| `figure-it-out` | 没有现成 playbook 时现做一套 |
| `timed-loop` | 按通过/失败条件反复醒来 |
| `reflect` | 把这次对话的教训改进技能 |
| `ketchup` | 补上你离开后这次对话的变化 |

## 维护

技能只放在 `plugins/s-atlas/skills/<英文名>/SKILL.md`。不再用的技能直接删除，名字记进 `scripts/marketplace_lib.py` 的 `RETIRED_SKILLS`，要找回去翻 git 历史。改完后同步调用策略、更新版本并检查：

```text
python scripts/update_skill_policies.py
python scripts/bump_plugin_version.py s-atlas
python scripts/check_marketplace.py
python -m unittest discover -s scripts -p "test_*.py"
claude plugin validate plugins/s-atlas
npx skills add . --list
```

要发 1.2.0 这种非补丁版本，先改锁文件和四份清单里的版本号，再跑 `scripts/check_marketplace.py`。补丁版本用 `bump_plugin_version.py`。

校验覆盖市场清单、版本锁、技能名称、调用策略和本地链接。技能是否实际触发、模型是否按配置委派，仍需通过真实会话验证。

## 来源与许可证

本插件包含的部分技能沿用了第三方开源许可证，许可证与声明文件见：

- [`brainstorming`、`writing-plans` 等开发流程技能：许可证](plugins/s-atlas/LICENSE-dev-workflow)
- [`frontend-design`：许可证](plugins/s-atlas/LICENSE-frontend-design)
- [`refactor-architecture`：许可证](plugins/s-atlas/LICENSE-refactor-architecture)
- [`deslop`、`control-cli`、`control-ui`：许可证](plugins/s-atlas/LICENSE-deslop-control)
- [`docx`、`pptx`、`xlsx`、`pdf`：许可证](plugins/s-atlas/LICENSE-document-skills)
- [`impeccable`：许可证](plugins/s-atlas/LICENSE-impeccable)
- [`impeccable`：声明](plugins/s-atlas/NOTICE-impeccable.md)
- [`archify`：许可证与声明](plugins/s-atlas/skills/archify/)
- [插件自身许可证](plugins/s-atlas/LICENSE)
