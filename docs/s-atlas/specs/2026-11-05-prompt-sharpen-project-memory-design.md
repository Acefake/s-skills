# 新增 prompt-sharpen 与 project-memory 设计

日期:2026-11-05

## 目标

把两个成熟的社区做法改写成 s-atlas 风格的自动选用技能:

1. `prompt-sharpen`:你给一句粗略需求,它先读懂当前项目,再问清缺口,产出一版带项目上下文的提示词。
2. `project-memory`:在被维护的项目里建立并维护架构、规范、决策记录,按每次改动增量更新。

两者衔接:`project-memory` 的记录越准,`prompt-sharpen` 越少需要现查。

## 来源与取舍

| 来源 | 许可 | 取用 | 不取用 |
|---|---|---|---|
| [severity1/claude-code-prompt-improver](https://github.com/severity1/claude-code-prompt-improver) | MIT | 先研究再提问的四阶段流程;问题要有依据、2 到 4 个具体选项、一题一个决策点;1 到 6 题的数量分档 | 钩子和 Python nudge 引擎(只支持部分宿主,且未经验证对行为有改善);TodoWrite、Task/Explore 的硬依赖 |
| [ondatra-ai/awesome-claude-mcp 的 update-memory](https://github.com/ondatra-ai/awesome-claude-mcp) | MIT | 按 diff 判断要不要改;最小改动;不写推测内容;只在对应代码删除时才删记录;只写现状不写历史 | 绑定 CLAUDE.md 一个文件、强制暂存 |
| claude-memory-skill、Memory Bank、memory-manage | MIT | 只借思路:每个主题只有一个权威位置;记录分层;全量/按变更/单模块三种更新范围。不复制文本 | 其余实现 |

随附许可证文件:`plugins/s-atlas/LICENSE-prompt-improver`、`plugins/s-atlas/LICENSE-update-memory`,README 许可证区加链接。

## 共同约束

- 两个都自动选用:没有 `disable-model-invocation`,`agents/openai.yaml` 里 `allow_implicit_invocation: true`,放进 README「自动选用」表(57 个变 59 个)。
- 不新增模型角色键。检索用已有的「检索和简单任务」,复杂探索用「怎么工作的探索者」,不改 setup-s-models。
- 提问用宿主的提问工具,名称以 `HOSTS.md` 为准,不在技能里写死某个宿主的工具名。
- 派不出子智能体时,在主对话里自己读,并说明没有换模型。

## prompt-sharpen

触发词:「优化提示词」「把这句话说清楚再做」「/prompt-sharpen」。

流程:

1. **读项目记录。** 先看 `project-memory` 产出的记录和 `CLAUDE.md`、`AGENTS.md`、README、近期提交。够用就不再扫代码。
2. **补缺口。** 只对没答案的缺口做定向检索(目标文件、已有模式、相关测试、近期改动)。简单缺口自己读,多处才派检索子智能体。每个子任务的提示词里带上对话里已有的文件路径、报错、已做的决定,子智能体看不到前文。
3. **分流。**
   - 需求已清楚:直接给出改写稿,不提问。
   - 有缺口且能从项目查到:用查到的写进改写稿,在稿里标明「假设」。
   - 必须你拍板的:问 1 到 6 个问题,每题 2 到 4 个来自检索的具体选项,说明取舍。
4. **产出。** 一份可直接执行的提示词,固定包含:目标、涉及的文件和模块、必须遵守的规范(引用记录里的条目)、验收标准、明确不做什么、列出的假设。
5. **交接。** 你确认后按该提示词执行;你说「只要提示词」就停在产出,不执行。需求涉及新功能或改行为时,交给 `brainstorming`,不在这里设计。

边界:不改文件、不跑命令,检索只读。

## project-memory

触发词:「建项目档案」「同步项目记录」「更新架构文档」「/project-memory」。

### 记录位置与布局

- 项目里已有约定就沿用(`docs/architecture.md`、`memory-bank/`、`docs/project_notes/` 等),并把它登记为权威位置。仓库已有规范优先。
- 没有约定时默认 `docs/project/`:
  - `architecture.md`:模块划分、入口、数据流、外部依赖。
  - `conventions.md`:命名、目录、测试、提交等实际在用的规范,每条标注依据文件。
  - `decisions/NNNN-标题.md`:一条决策一个文件,写背景、决定、取舍。
  - `README.md`:索引和「各主题的权威位置」表。
- `CLAUDE.md`、`AGENTS.md` 只放一行指向 `docs/project/` 的指针,不放内容,避免撑大每次会话的上下文。

### 三种模式

| 模式 | 做什么 | 写入 |
|---|---|---|
| `init` | 扫项目生成初稿。小项目自己读,大项目派并行检索,各读一块,汇总。先给目录和每份的要点,确认后写 | 新建文件;改 `CLAUDE.md`/`AGENTS.md` 前先给 diff |
| `sync` | 读 `git diff`(暂存或指定范围),逐份判断这次改动是否影响记录,只改受影响的部分 | 最小改动 |
| `check` | 只读。对照代码找记录里已过期、已失实、缺失的条目,出报告 | 不写 |

### sync 规则(取自 update-memory)

- 看 diff,不看全仓库。没影响就不动文件,并说明「无需更新」。
- 只写现状:不写推测,不写提交说明或更新日志。
- 只有对应代码或文件已删除才删记录。
- 沿用现有格式、语气和详细程度,不整段重写没受影响的部分。
- 每条规范和结论必须能指到一个文件或提交;指不到的不写。
- 新增的重大取舍写成 `decisions/` 新文件,不覆盖旧决策;决策被推翻时在旧文件标注「已被 NNNN 取代」。

### 与现有技能的关系

- `how` 是一次性讲解,不留记录;`project-memory` 负责留。`how` 的结论可作为 `init` 的素材。
- `archify` 画图,可被 `architecture.md` 引用,不由本技能生成。
- `technical-writing` 管句子怎么写,`project-memory` 管写什么、何时改,写作时遵循它。
- 第一版不改 `commit-pr`,只在 `project-memory` 里说明提交前可以跑一次 `sync`。

## 要改的文件

沿用 `automate-me` 新增时的清单:

- 新增 `plugins/s-atlas/skills/prompt-sharpen/{SKILL.md,agents/openai.yaml,references/}`
- 新增 `plugins/s-atlas/skills/project-memory/{SKILL.md,agents/openai.yaml,references/}`,`references/` 放记录模板和 sync 判断清单
- 新增 `plugins/s-atlas/LICENSE-prompt-improver`、`LICENSE-update-memory`
- 更新 `README.md`(手点表、技能数量、许可证链接)、`docs/architecture.md`、`docs/architecture/s-atlas.architecture.json` 和对应 html、`docs/s-skills-route.png`
- 更新 `plugins/s-atlas/skills/s-router/SKILL.md` 路由表:提示词优化、建项目档案分别指向新技能
- 更新 `scripts/marketplace_lib.py` 的技能清单、`scripts/trigger_cases.json` 增加触发用例
- 用 `scripts/bump_plugin_version.py s-atlas` 发布新版本,同步各 `plugin.json`、marketplace 文件和 `plugin-versions.lock.json`

## 验证

- 跑 `scripts` 下的校验和单测:`check_marketplace.py`、`test_skill_resources.py`、`test_trigger_cases.py`、`test_version_docs.py`、`test_host_support.py`。
- 实测:拿本仓库当样本,跑一次 `project-memory init`,再随便改一处后跑 `sync`,确认只动受影响的部分;再对一句模糊需求跑 `prompt-sharpen`,确认改写稿引用的文件真实存在。

## 未决项

- 无阻塞项。默认记录位置为 `docs/project/`,项目已有约定时沿用。如要换默认位置,只改 `project-memory` 的布局一节。
