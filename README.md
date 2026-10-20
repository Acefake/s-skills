# s 中文技能

![s](plugins/s/icon.png)

一个独立维护的中文 AI 技能插件，版本 1.2.3。插件名是 `s`，不需要再装上游插件。活跃技能 **61** 个，随插件分发；另外 **38** 个在仓库根的 [`archive/s/`](archive/s/)，不进插件包。目录名和 frontmatter 的 `name` 都是英文小写 kebab-case，两者相同。说明直接以中文句子起头，中文句号后接英文 `Use when`；正文是中文。

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
/plugin install s@s-skills
```

Codex 在终端添加市场，再在应用的插件管理入口安装 `s`：

```text
codex plugin marketplace add Acefake/s-skills
```

Cursor 从插件市场导入 `https://github.com/Acefake/s-skills`，选择 `s`。各宿主的命令支持与入口以实际界面为准。安装或更新后开启新会话，确认技能路径和版本。

## 使用

点名技能，并说明目标和完成条件：

```text
用 poteto-mode 修复这个问题，复现后定位原因，修完运行实际流程验证。
用 how 解释这个模块的入口、数据流和关键文件。
用 impeccable 检查这个设置页，并给出具体改进。
```

支持插件命令的宿主也可以使用 `/s:技能名`，例如 `/s:poteto-mode`。Codex 可在技能选择器中选择相应技能。

原则、`setup-s-models`、`impeccable` 和译入的 Superpowers 流程可以按描述自动选用。`frontend-design` 只在点名时使用，日常做界面走 `impeccable`。工作模式和并行审查等复杂流程需要点名。自动选用不表示每轮都会执行；能不能做到还取决于宿主提供的工具。

- [全部活跃技能](plugins/s/skills/)
- [工作模式](plugins/s/skills/poteto-mode/SKILL.md)
- [模型设置](plugins/s/skills/setup-s-models/SKILL.md)
- [改名对照与回滚](RENAMES.md)
- [Codex、T3 与 Cursor 适配规则](plugins/s/HOSTS.md)

## 活跃技能

「手点」表示 frontmatter 里有 `disable-model-invocation: true`，需要点名才会加载。

### Superpowers

译自 Jesse Vincent 的 Superpowers（MIT），见 [LICENSE-superpowers](plugins/s/LICENSE-superpowers)。这 11 个都会自动选用。

| 技能 | 用途 |
|---|---|
| `using-superpowers` | 日常先查该用哪个技能 |
| `brainstorming` | 做功能前先把方案磨清 |
| `writing-plans` | 把活写成可执行计划 |
| `executing-plans` | 按写好的计划做 |
| `subagent-driven-development` | 用子智能体推进计划 |
| `systematic-debugging` | 按证据排错 |
| `verification-before-completion` | 声称完成前先拿证据 |
| `requesting-code-review` | 发起代码审查 |
| `receiving-code-review` | 处理审查意见 |
| `using-git-worktrees` | 用 worktree 隔开工作 |
| `finishing-a-development-branch` | 收尾开发分支 |

和 poteto 重叠、因此归档的三份是 `test-driven-development`、`dispatching-parallel-agents`、`writing-skills`。留下的是 `tdd`、`swarm`、`author-skill`。

### 界面

| 技能 | 调用 | 用途 |
|---|---|---|
| `impeccable` | 自动 | 做页面、改界面、做设计审查 |
| `frontend-design` | 手点 | 点名时给一份有主见的视觉方向，不带检查脚本 |

### 工作流程

| 技能 | 调用 | 用途 |
|---|---|---|
| `poteto-mode` | 手点 | 点名才走的加强工作流 |
| `s-agent` | 手点 | poteto 派出去写代码的子智能体 |
| `comment-sicko` | 手点 | 被清注释技能派去删注释 |
| `setup-s-models` | 自动 | 给各角色配模型和预算 |
| `how` | 手点 | 改之前讲清代码怎么串 |
| `why` | 手点 | 查为什么这样设计 |
| `architect` | 手点 | 动手前定类型和模块边界 |
| `swarm` | 手点 | 并行覆盖、比赛、分片验证 |
| `arena` | 手点 | 同一任务多方案再嫁接 |
| `interrogate` | 手点 | 多模型对抗审查 |
| `unslop` | 手点 | 去掉文字里的 AI 腔 |
| `deslop` | 自动 | 提交前清掉代码里的 AI 味 |
| `no-comments` | 手点 | 审查前删掉不该留的注释 |
| `technical-writing` | 手点 | 写文档、RFC、PR 说明 |
| `author-skill` | 手点 | 按规范写或大改 SKILL.md |
| `control-ui` | 自动 | 在真浏览器里操作界面取证 |
| `control-cli` | 自动 | 在本地操作命令行或 TUI |
| `benchmark-checklist` | 手点 | 报告性能数字前先审核 |
| `show-me-your-work` | 手点 | 长时间运行留下决定记录 |
| `figure-it-out` | 手点 | 没有现成 playbook 时现做一套 |
| `timed-loop` | 手点 | 按通过/失败条件反复醒来 |
| `reflect` | 手点 | 把这次对话的教训改进技能 |
| `tdd` | 手点 | 用户要求或测试很便宜时先写失败测试 |
| `ketchup` | 手点 | 补上你离开后这次对话的变化 |

### 原则

这 24 条都会自动选用。poteto 的原则索引会点名读它们。

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

## 维护

活跃技能只放在 `plugins/s/skills/<英文名>/SKILL.md`。归档技能放在 `archive/s/<英文名>/`。改完后同步调用策略、更新版本并检查：

```text
python scripts/update_skill_policies.py
python scripts/bump_plugin_version.py s
python scripts/check_marketplace.py
python -m unittest discover -s scripts -p "test_*.py"
claude plugin validate plugins/s
npx skills add . --list
```

要发 1.2.0 这种非补丁版本，先改锁文件和四份清单里的版本号，再跑 `scripts/check_marketplace.py`。补丁版本用 `bump_plugin_version.py`。

校验覆盖市场清单、版本锁、技能名称、调用策略和本地链接。技能是否实际触发、模型是否按配置委派，仍需通过真实会话验证。

## 来源与许可证

保留各技能的原作者署名、许可证及通知文件。来源包括工作流、设计和 Superpowers，详见 [LICENSE](plugins/s/LICENSE)、插件目录下的 `LICENSE-*`、`NOTICE-*` 和各技能内的来源说明。Superpowers 译文的许可证是 [LICENSE-superpowers](plugins/s/LICENSE-superpowers)。
