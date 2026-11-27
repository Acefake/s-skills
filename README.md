<p align="center">
  <img src="plugins/wukong/icon.png" width="128" alt="wukong" />
</p>

<h1 align="center">wukong</h1>

<p align="center"><strong>把日常写代码的方式，写成技能。</strong></p>

<p align="center">先磨方案、再写计划、按计划做、审查后收尾；排错讲证据，改动要验证。<br />支持 Codex、Claude Code、Antigravity。</p>

<p align="center">当前版本 1.0.35，共 <strong>35</strong> 个技能：20 个按描述自动选用，15 个需点名调用。</p>

<p align="center">
  <a href="#安装">安装</a> ·
  <a href="#使用">使用</a> ·
  <a href="#技能一览">技能一览</a> ·
  <a href="docs/architecture.md">架构说明</a> ·
  <a href="docs/architecture/wukong-panorama.html">全景图</a> ·
  <a href="https://github.com/Acefake/s-skills/releases/latest">发行版</a>
</p>

---

## 安装

**Claude Code**

```text
/plugin marketplace add Acefake/s-skills
/plugin install wukong@s-skills
```

**Codex**

```text
codex plugin marketplace add Acefake/s-skills
```

再到应用的插件管理入口安装 `wukong`。

**Antigravity（`agy` CLI、App、IDE）**

```sh
agy plugin install https://github.com/Acefake/s-skills/tree/main/plugins/wukong   # 远程安装
agy plugin install ./plugins/wukong                                               # 克隆后本地安装
```

启用后自动加载 `rules/AGENTS.md` 和插件根 `hooks.json`。本机开发想直接挂载仓库目录，运行 `powershell -NoProfile -File scripts/bootstrap.ps1`，它会写入 `~/.gemini/config/plugins.json`；再用 `agy plugin validate plugins/wukong` 和 `agy plugin list` 核对。

**Codex 只对本项目生效**：克隆仓库后在 Windows PowerShell 运行。

```powershell
git clone https://github.com/Acefake/s-skills.git
cd s-skills
powershell -NoProfile -File scripts/install_local_skills.ps1
```

脚本把技能链接到 `.agents/skills/`，重复执行不覆盖已有文件。

安装或更新后开新会话。各宿主的入口以实际界面为准，差异见[宿主适配](plugins/wukong/HOSTS.md)。

## 初始化

装好后点名一次 `wukong-init`（`/wukong:wukong-init`）。它做两件事，整张表确认后才写入：

- **同步全局技能规则。** Codex 写入 `~/.codex/AGENTS.md`，Claude Code 写入 `~/.claude/CLAUDE.md`。Antigravity 随插件自动加载 `rules/AGENTS.md`，只把模型块和个人块写进 `~/.gemini/config/AGENTS.md`。规则正文见 [AGENTS.md](plugins/wukong/AGENTS.md)。
- **给四个子代理角色配模型。** 按当前宿主能派发的模型匹配检索、规划、审查、测试四个角色，每个角色带默认推理档位：检索、测试用 medium，规划、审查用 high。比如 Claude Code 上检索用 haiku，规划和审查用 opus，测试用 sonnet。写代码的子代理和其他子代理继承当前会话模型；你点名的模型优先。

规则只在你点名时写入，新会话才生效。平时每个会话只读检查一次，缺失或过期时提醒，不自动写。

Codex 不读插件自带的钩子。手动注册过钩子的话，插件更新后路径会指向旧版本目录，用 `python <当前插件>/skills/wukong-init/scripts/codex_hooks.py` 检查；确认预览后加 `--apply` 改写，再在新会话 `/hooks` 核对批准。

## 使用

点名技能，并说清目标和完成条件：

```text
用 systematic-debugging 修复这个问题，复现后定位原因，修完运行实际流程验证。
用 how 解释这个模块的入口、数据流和关键文件。
用 impeccable 检查这个设置页，并给出具体改进。
```

支持插件命令的宿主用 `/wukong:技能名`，Codex 在技能选择器里选。自动选用按描述匹配，不保证每轮触发；点名技能不会自己运行。

| 我想做什么 | 用 |
|---|---|
| 修 bug、报错、结果不对 | `systematic-debugging` |
| 做新功能、改行为 | `brainstorming`，再 `writing-plans` |
| 按写好的计划做、要并行 | `executing-plans` |
| 提交、开 PR、分支收尾 | `commit-pr` |
| 审 PR、分支或本地改动 | `wukong-review` |
| 写 README、文档、RFC、去 AI 腔 | `technical-writing` |
| 做页面、改界面 | `impeccable` |
| Word 文档 | `docx` |
| 发版 | `release` |
| 拿不准 | `wukong-router` |

在 T3 Code 里用的是底层宿主已发现的技能，子代理和工作区按 [T3 编排参考](plugins/wukong/skills/wukong-router/references/t3-code-tools.md)。wukong 不接管 T3 的持续台账、PR 等待和定时执行。

## 验证分档

按改动定档。同一份代码已经验证过就复用，不重跑。

| 档 | 适用 | 验证 |
|---|---|---|
| 0 | 文案、注释、文档措辞、样式数值、配置值；只读任务；用户说不用测 | 不跑测试，看 diff |
| 1 | 意图明确、1–2 个文件且不改接口、数据结构或依赖的小改动，含这种范围的修 bug | lint 或类型检查，加已有测试 |
| 2 | 其他修 bug、加功能、改行为 | 有便宜稳定的测试点就先写失败测试，再验证所在模块 |
| 3 | 跨模块、改接口或依赖、迁移；非第 0 档的提交或合并前 | 全量测试一次 |

代码改动交付前先自审：第 0、1 档只看 diff，第 2 档起再看关键调用方。第 3 档，或涉及权限、并发、共享状态、数据删除的改动，自审后再派只读子代理独立评审。

提交、推送、改写历史、外部消息和清理工作区，都只按你已有的授权执行。细则见 [wukong-router](plugins/wukong/skills/wukong-router/SKILL.md)。

## 钩子

Claude Code 和 Antigravity 装上插件后自动注册。钩子只加提醒或请求确认，不改写你的输入：

- **会话开始**：记下插件版本，只读检查全局技能规则是否缺失或过期。
- **每条提示词**：附一段评估说明，缺口明显时才加载 `prompt-sharpen`；提示词笼统时界面显示一行「需求可能不够具体，已提醒先澄清」。以 `*`、`#`、`/` 开头的消息，「可以」「继续」这类确认，以及 4 个字以内的消息不介入。
- **执行 Bash 前**：长时间运行的命令提醒放后台，引号和 heredoc 里出现的命令不算；强制推送、`--no-verify`、`reset --hard`、`git clean` 先请你确认。
- **本地使用日志**：记下加载了哪些技能、你的纠正和任务摘要，存在本机 `~/.wukong/journal.db`，不上传、不进对话。`reflect --me` 用它归纳个人规则；`WUKONG_JOURNAL=0` 关闭。

Antigravity 另把每次提示词评估的结果写进 `~/.wukong/prompt-hook-log.jsonl`，用 `python hooks/agy_hook.py --status` 查看。

说明和关闭方法见[钩子说明](plugins/wukong/hooks/README.md)。Codex 要手动配置，见 [Codex 配置](plugins/wukong/skills/prompt-sharpen/references/hook.md)。

## 技能一览

「点名」的技能在 frontmatter 里带 `disable-model-invocation: true`，只在你点名或已授权的工作流派发时运行。按分区看卡片见[全景图](docs/architecture/wukong-panorama.html)。

### 入口与配置（2）

| 技能 | 调用 | 用途 |
|---|---|---|
| `wukong-router` | 自动 | 拿不准该用哪个技能、或任务跨模块时先查；同时定验证档位 |
| `wukong-init` | 点名 | 同步全局技能规则，按宿主给四个子代理角色配模型和推理档位，写入前确认 |

### 工作模式（3）

| 技能 | 调用 | 用途 |
|---|---|---|
| `architect` | 点名 | 写代码前定类型、函数签名和模块边界，实现中一直参与 |
| `show-me-your-work` | 点名 | 长时间或无人值守的工作，每个决定记一行 |
| `handoff` | 点名 | 把当前目标、分支与提交状态、已验证结论和踩坑压缩成跨会话交接文档与下一会话提示词 |

### 开发主流程（15）

| 技能 | 调用 | 用途 |
|---|---|---|
| `prompt-sharpen` | 自动 | 需求有关键缺口时先读项目自行补齐，必要时才提问并改写请求 |
| `project-memory` | 自动 | 建立并维护项目的架构、规范、决策记录，改动后按 diff 只更新受影响的部分 |
| `brainstorming` | 自动 | 动手前摸清意图、需求和设计，取舍范围；含 4 条原则 |
| `writing-plans` | 自动 | 把多步任务或迁移拆成每步都能验证的计划；含 2 条原则 |
| `executing-plans` | 自动 | 按写好的计划做：主会话或子代理逐任务执行、隔离工作区、循环检查；点名 swarm 时按 Antigravity 原生群体协调者并行派工，其他宿主改用子代理派发；含 3 条原则 |
| `systematic-debugging` | 自动 | 先复现、查根因再改；含 4 条原则 |
| `tdd` | 自动 | 修 bug 时有便宜的测试点就先写失败测试 |
| `test-strategy` | 自动 | 定每个行为在哪一层测、用什么工具；覆盖 TS/React、Vue、Go、Java；含 1 条原则 |
| `code-style` | 自动 | 按模块就近放文件、文档注释、边界校验、类型设计、交付前自审；覆盖 TS/React、Vue、Go、Java；含 11 条设计原则 |
| `deslop` | 自动 | 提交前清掉 diff 里的代码腔；只清注释时派 comment-sicko 只读审查 |
| `requesting-code-review` | 自动 | 完成后核对是否满足需求并拿出验证证据，按风险派独立评审 |
| `receiving-code-review` | 自动 | 落实评审意见前先核验 |
| `wukong-review` | 自动 | 中文代码审查：审 PR、分支或本地改动，带出处和严重程度，给合并结论 |
| `commit-pr` | 自动 | 看 diff 写提交说明，推送并开 PR；集成方式没定时先核验，再给合并、PR、保留或丢弃的选项 |
| `release` | 点名 | 按插件清单的版本打 tag，写只含新增、改动、修复的发版说明，创建 GitHub Release |

### 专项技能（15）

| 技能 | 调用 | 用途 |
|---|---|---|
| `how` | 点名 | 讲子系统的架构、入口和运行流程 |
| `why` | 点名 | 查设计理由和取舍，带引用 |
| `refactor-architecture` | 点名 | 找浅模块和耦合，出 HTML 报告，再逐个追问定案 |
| `archify` | 点名 | 画架构图、流程图、时序图、ER 图等，出校验过的单文件 HTML；需要 Node 18+ |
| `impeccable` | 自动 | 做页面、改界面、设计审查；`optimize` 守交互性能预算（INP、长任务、帧率、包体积） |
| `control-ui` | 自动 | 在真浏览器里操作界面取证 |
| `control-cli` | 自动 | 在本地驱动命令行或 TUI |
| `mcp-builder` | 点名 | 设计工具契约，实现 MCP 服务并联调 |
| `remotion-create` | 点名 | 用 React 编排视频镜头、字幕和音轨，渲染并抽查成片 |
| `e2e-testing` | 自动 | 用 Playwright 写稳定的端到端测试，修偶发失败和超时 |
| `docx` | 点名 | 创建、修订、批注和阅读 Word；中文设置 `w:eastAsia` |
| `technical-writing` | 点名 | README、文档、RFC、PR 说明的写作标准，附去 AI 腔清单 |
| `wukong-proposal` | 自动 | 写中文方案：先问清目标和读者，列提纲，再起草打磨 |
| `author-skill` | 点名 | 按规范写或大改 SKILL.md |
| `reflect` | 点名 | 把这次对话的教训改成对现有技能的修改（单条小改走轻量快路，多处教训走深度复盘）；`--add` 直接记一条个人规则，`--me` 把本机使用日志归纳成个人规则，`--show`、`--undo`、`--forget`、`--off`、`--on` 查看、撤销、删除、关闭、打开 |

`docx` 需要 Python 3.12、Node.js（在技能目录里 `npm install` 一次）、LibreOffice 和 poppler；读 docx 要 pandoc，中文渲染检查要 Noto CJK。

## 维护

技能只放在 `plugins/wukong/skills/<英文名>/SKILL.md`。不再用的技能直接删，名字记进 `scripts/marketplace_lib.py` 的 `RETIRED_SKILLS`。校验脚本需要 Python 3.10 及以上。

```text
python -m pip install -r requirements-dev.txt
python scripts/update_skill_policies.py
python scripts/bump_plugin_version.py wukong
python scripts/check_marketplace.py
python -m unittest discover -s scripts -p "test_*.py"
claude plugin validate plugins/wukong
git config core.hooksPath scripts/git-hooks   # 提交前自动检查版本和哈希
```

- 补丁版本用 `bump_plugin_version.py`。非补丁版本（如 1.1.0）先改锁文件和已登记清单里的版本号，再跑 `check_marketplace.py`。
- 发版点名 `release`。
- 新增自动选用的技能，先在 `scripts/trigger_cases.json` 补一条触发用例。改了描述就跑触发评测：`python scripts/eval_triggers.py --model haiku --jobs 6 --repeat 3`。它会产生实际调用，不进 CI。
- 宿主里的真实行为用 [evals](plugins/wukong/evals/README.md) 的 `claude plugin eval` 用例检查。

## 许可证

wukong 按 [LICENSE](plugins/wukong/LICENSE) 发布；第三方组件见[许可证与声明](docs/third-party-licenses.md)。
