<p align="center">
  <img src="plugins/wukong/icon.png?v=1.0.12" width="128" alt="wukong" />
</p>

<h1 align="center">wukong</h1>

<p align="center"><strong>把日常写代码的方式，写成技能。</strong></p>

<p align="center">先磨方案、再写计划、按计划做、审查后收尾；排错讲证据，改动要验证。<br />支持 Codex、Claude Code、Antigravity。</p>

<p align="center">当前版本 1.0.33，共 <strong>34</strong> 个技能：20 个按描述自动选用，14 个需点名调用。</p>

<p align="center">
  <a href="#安装">安装</a> ·
  <a href="#使用">使用</a> ·
  <a href="#技能一览">技能一览</a> ·
  <a href="docs/architecture.md">架构说明</a> ·
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

**Antigravity（`agy` CLI / App / IDE）**：插件目录原生兼容，支持直接安装或开发零复制挂载：

```sh
agy plugin install https://github.com/Acefake/s-skills/tree/main/plugins/wukong   # 远程直装
agy plugin install ./plugins/wukong                                               # 本地克隆后安装
```

启用后自动加载 `rules/AGENTS.md` 与插件根 `hooks.json`（含 `prompt-sharpen` 与 `SessionStart` 钩子）。本机开发想零复制挂载，可运行 `powershell -NoProfile -File scripts/bootstrap.ps1` 自动写入 `~/.gemini/config/plugins.json`；用 `agy plugin validate plugins/wukong` 和 `agy plugin list` 核对状态。

**Codex 本项目**：克隆仓库后在 Windows PowerShell 运行。

```powershell
git clone https://github.com/Acefake/s-skills.git
cd s-skills
powershell -NoProfile -File scripts/install_local_skills.ps1                     # Codex，只对本项目生效
```

脚本把技能链接到 `.agents/skills/`（Codex），重复执行不覆盖已有文件。各宿主的入口以实际界面为准，安装或更新后开新会话。宿主差异见 [宿主适配](plugins/wukong/HOSTS.md)。

### 从 s-atlas 或 s-wukong 升级

插件 1.0.12 起改名为 `wukong`，旧插件不会自动迁移。新旧同时装会出现两套技能，钩子也会各跑一遍，所以先卸旧的再装新的。Claude Code：

```text
/plugin uninstall s-atlas@s-skills
/plugin uninstall s-wukong@s-skills
/plugin marketplace update s-skills
/plugin install wukong@s-skills
```

没装过的那一行跳过即可。Codex 在插件管理入口卸载 `s-atlas` 或 `s-wukong` 后装 `wukong`；本地安装的 Codex 删掉 `.agents/skills/` 里的 `s-agent`、`s-init`、`s-mode`、`s-proposal`、`s-review`、`s-router` 后重跑安装脚本。

装好后开新会话，点名一次 `wukong-init`：它会把全局规则里的旧标记块原位换成 `wukong` 标记块，旧技能名一并更新。标记块外你自己写的提到 `s-atlas` 的句子不会被改，需要手动换成 `wukong`。旧版模型配置文件（如 `s-atlas.t3.json`、`s-wukong.t3.json`、`wukong.t3.json`）已不再读取，可手动删除。

Codex 还要检查以前手动注册的钩子：`python <当前插件>/skills/wukong-init/scripts/codex_hooks.py`。发现旧路径后，确认预览再加 `--apply`，脚本保留其他钩子及首份备份；不会自动添加缺失项或批准钩子。迁移后在新会话 `/hooks` 核对批准。`wukong-init` 与日常自检也会检查这一项，全局规则已同步不代表钩子路径仍有效。

## 初始化

装好后点名一次 `wukong-init`（`/wukong:wukong-init`）：它检查并同步全局技能规则，再按当前宿主能派发的模型给检索、规划、审查、测试四个子代理角色配模型，整张表确认后才写入。

- 全局规则写入：Codex 的 `AGENTS.md`，Claude Code 的 `~/.claude/CLAUDE.md`；Antigravity 随插件自动加载 `rules/AGENTS.md`（不重复写库块，模型块与个人块写在 `~/.gemini/config/AGENTS.md`）。规则正文见 [AGENTS.md](plugins/wukong/AGENTS.md)。
- 只在你点名时写入。平时每个会话只读检查一次，过期会提醒。新会话才生效。
- 子代理模型：检索、规划、审查、测试四个角色按宿主动态匹配（如 Claude Code 上检索 haiku、规划和审查 opus、测试 sonnet），每个角色带默认推理档位（检索、测试 medium，规划、审查 high），写在全局规则后的独立标记块里；写代码的子代理和其他子代理继承当前会话模型，你点名的模型优先。

## 使用

点名技能，并说清目标和完成条件：

```text
用 systematic-debugging 修复这个问题，复现后定位原因，修完运行实际流程验证。
用 how 解释这个模块的入口、数据流和关键文件。
用 impeccable 检查这个设置页，并给出具体改进。
```

支持插件命令的宿主用 `/wukong:技能名`，Codex 在技能选择器里选。自动选用按描述匹配，不保证每轮触发；点名的技能不会自己运行。

在 T3 Code 中可使用底层宿主已发现的技能，派发与委派按 [T3 编排参考](plugins/wukong/skills/wukong-router/references/t3-code-tools.md)。不新增市场安装包，持续编排台账与 PR 等待尚未接入。

| 我想做什么 | 用 |
|---|---|
| 修 bug、报错、结果不对 | `systematic-debugging` |
| 做新功能、改行为 | `brainstorming`，再 `writing-plans` |
| 按写好的计划做 | `executing-plans` |
| 提交、开 PR、分支收尾 | `commit-pr` |
| 审 PR、分支或本地改动 | `wukong-review` |
| 写 README、文档、RFC、去 AI 腔 | `technical-writing` |
| 做页面、改界面 | `impeccable` |
| Word 文档 | `docx` |
| 发版 | `release` |
| 拿不准 | `wukong-router` |

## 验证分档

按改动定档，同一份代码已验证就复用，不重跑。代码改动交付前先自审（第 0、1 档只看 diff）；第 3 档或涉及权限、并发、共享状态、数据删除时，再加只读独立评审。

| 档 | 适用 | 验证 |
|---|---|---|
| 0 | 文案、注释、文档措辞、样式数值、配置值；只读任务；用户说不用测 | 不跑测试，看 diff |
| 1 | 意图明确、1–2 个文件且不改接口、数据结构或依赖的小改动，含这种范围的修 bug | lint 或类型检查，加已有测试 |
| 2 | 其他修 bug、加功能、改行为 | 有便宜稳定的测试点就先写失败测试，再验证所在模块 |
| 3 | 跨模块、改接口或依赖、迁移；非第 0 档的提交或合并前 | 全量测试一次 |

提交、推送、改写历史、外部消息和清理工作区，都只按你已有的授权执行。细则见 [wukong-router](plugins/wukong/skills/wukong-router/SKILL.md)。

## 钩子（Claude Code 与 Antigravity 自动启用）

装上插件后自动注册，只加提醒或请求确认，不改写你的输入：

- 会话开始：记下插件版本，检查全局技能提示词是否过期。
- 每条提示词附一段评估说明，含糊时才加载 `prompt-sharpen`；提示词看起来笼统时，界面上会显示一行「需求可能不够具体，已提醒先澄清」；以 `*`、`#`、`/` 开头的、「可以」「继续」这类确认和 4 个字以内的消息不介入。
- 长时间运行的命令：提醒放到后台（引号和 heredoc 里出现的命令不算）。
- 强制推送、`--no-verify`、`reset --hard`、`git clean`：先请你确认。
- 本地使用日志：记下加载了哪些技能、你的纠正和任务摘要，存在本机 `~/.wukong/journal.db`（SQLite），不上传、不进对话。供以后的个人学习使用，`WUKONG_JOURNAL=0` 关闭。

说明和关闭方法见 [钩子说明](plugins/wukong/hooks/README.md)。Codex 要手动配置，见 [Codex 配置](plugins/wukong/skills/prompt-sharpen/references/hook.md)。

## 技能一览

[全景图（单独维护，可能滞后）](docs/architecture/wukong-panorama.html) · [架构说明](docs/architecture.md) · [组件关系图](docs/architecture/wukong.html)

「点名」的技能在 frontmatter 里带 `disable-model-invocation: true`，由你点名或已授权的工作流派发。

### 入口与配置（2）

| 技能 | 调用 | 用途 |
|---|---|---|
| `wukong-router` | 自动 | 日常先查该用哪个技能 |
| `wukong-init` | 点名 | 显式初始化全局技能提示词，并按宿主匹配四个子代理角色的模型，写入前确认 |

### 工作模式（2）

| 技能 | 调用 | 用途 |
|---|---|---|
| `architect` | 点名 | 动手前定类型和模块边界 |
| `show-me-your-work` | 点名 | 长时间运行留下决定记录 |

### 开发主流程（15）

| 技能 | 调用 | 用途 |
|---|---|---|
| `prompt-sharpen` | 自动 | 需求含糊时先读项目、再问清缺口，改写成能直接执行的提示词 |
| `project-memory` | 自动 | 在项目里建立并维护架构、规范、决策记录，改动后按 diff 只更新受影响的部分 |
| `brainstorming` | 自动 | 做功能前先把方案磨清；含 4 条原则 |
| `writing-plans` | 自动 | 把活写成可执行计划；含 2 条原则 |
| `executing-plans` | 自动 | 按写好的计划做：主会话或子智能体逐任务执行、隔离工作区、循环检查、没有现成流程时先定可审计做法；含 3 条原则 |
| `systematic-debugging` | 自动 | 按证据排错；含 4 条原则 |
| `tdd` | 自动 | 修 bug 时有便宜的测试点就先写失败测试 |
| `test-strategy` | 自动 | 定每个行为在哪一层测、用什么工具；覆盖 TS/React、Vue、Go、Java；含 1 条原则 |
| `code-style` | 自动 | 按模块就近放文件、写文档注释、质量底线；覆盖 TS/React、Vue、Go、Java；含 11 条设计原则 |
| `deslop` | 自动 | 提交前清掉代码里的 AI 味；只清注释时派 comment-sicko 只读审查 |
| `requesting-code-review` | 自动 | 发起代码审查 |
| `receiving-code-review` | 自动 | 处理审查意见 |
| `wukong-review` | 自动 | 中文代码审查：审 PR、分支或本地改动，带出处和严重程度，给合并结论 |
| `commit-pr` | 自动 | 看 diff，写提交说明，推送并开 PR；集成方式还没定时先收尾分支，给出合并、PR、保留或丢弃的选项 |
| `release` | 点名 | 显式发版：确认版本，写只含新增、改动、修复的发版说明，打 tag 并创建 GitHub Release |

### 专项技能（15）

| 技能 | 调用 | 用途 |
|---|---|---|
| `how` | 点名 | 改之前讲清代码怎么串 |
| `why` | 点名 | 查为什么这样设计 |
| `refactor-architecture` | 点名 | 找浅模块和耦合，出 HTML 报告，再逐个追问定案 |
| `archify` | 点名 | 画架构图、流程图、时序图、ER 图等，出可交互单文件 HTML，需要 Node 18+ |
| `impeccable` | 自动 | 做页面、改界面、做设计审查；`optimize` 守交互性能预算（INP、长任务、帧率、包体积） |
| `mcp-builder` | 点名 | 设计工具契约，实现 MCP 服务并联调 |
| `remotion-create` | 点名 | 用 React 编排视频镜头、字幕和音轨，渲染并抽查成片 |
| `control-ui` | 自动 | 在真浏览器里操作界面取证 |
| `control-cli` | 自动 | 在本地操作命令行或 TUI |
| `e2e-testing` | 自动 | 用 Playwright 写稳定的端到端测试，修不稳定的测试 |
| `docx` | 点名 | 创建、修订、批注和阅读 Word。中文设置 `w:eastAsia` |
| `technical-writing` | 点名 | 写 README、文档、RFC、PR 说明的句子，附去 AI 腔清单。Word 用 `docx` |
| `wukong-proposal` | 自动 | 写中文方案：先问清目标，列提纲，再按固定结构起草打磨 |
| `author-skill` | 点名 | 按规范写或大改 SKILL.md |
| `reflect` | 点名 | 把这次对话的教训改进技能；`--me` 把本机使用日志归纳成个人规则，`--show`/`--undo`/`--forget`/`--off`/`--on` 查看、撤销、删除、关闭、打开 |

`docx` 技能需要 Python 3.12、Node.js（在技能目录里 `npm install` 一次）、LibreOffice、poppler；读 docx 要 pandoc，中文渲染检查要 Noto CJK。`archify` 需要 Node 18+。

## 维护

技能只放在 `plugins/wukong/skills/<英文名>/SKILL.md`。不再用的技能直接删，名字记进 `scripts/marketplace_lib.py` 的 `RETIRED_SKILLS`，要找回去翻 git 历史。校验脚本需要 Python 3.10 及以上。

```text
python -m pip install -r requirements-dev.txt
python scripts/update_skill_policies.py
python scripts/bump_plugin_version.py wukong
python scripts/check_marketplace.py
python -m unittest discover -s scripts -p "test_*.py"
claude plugin validate plugins/wukong
git config core.hooksPath scripts/git-hooks   # 提交前自动检查版本和哈希
```

- 非补丁版本（如 1.1.0）：先改锁文件和已登记清单里的版本号，再跑 `scripts/check_marketplace.py`；补丁版本用 `bump_plugin_version.py`。
- 发版点名 `release`：确认版本，写只含新增、改动、修复的说明，打 tag 并创建 GitHub Release。
- 新增自动选用的技能，先在 `scripts/trigger_cases.json` 补一条触发用例；改了描述就跑触发评测（会产生实际调用，不进 CI）：`python scripts/eval_triggers.py --model haiku --jobs 6 --repeat 3`。
- 宿主里的真实行为用 [evals](plugins/wukong/evals/README.md) 的 `claude plugin eval` 用例检查。
- 改名对照与回滚见 [RENAMES.md](RENAMES.md)。

## 许可证

wukong 按 [LICENSE](plugins/wukong/LICENSE) 发布；第三方组件见[许可证与声明](docs/third-party-licenses.md)。
