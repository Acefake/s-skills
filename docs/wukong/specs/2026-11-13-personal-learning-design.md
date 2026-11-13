# 个人学习层：线上标准钩子，本地各自进化

## 目标

同一套 wukong 插件，每个人用得越久越贴合自己。插件只发一套相同的钩子、脚本和技能；学习数据、学出来的规则和起草的技能默认全部留在本机，不上传、不汇总。

做完之后：

- 你反复纠正过的事（「说简单点」「别派审查」「先出图」），两次以后提议变成你的个人规则，确认后下个会话起生效。
- 你反复做、但没有对口技能的某类任务，提示你是否起草一个技能；同意后生成到你的用户级技能目录。
- 你自己的技能好用时，可以选择把它提交到 s-skills 仓库；不选就永远只在本机。
- 个人规则和个人技能都有体积上限、会提示清理、可撤销，库升级不覆盖。

不在范围内：多人共享学习、自动上传或汇总、跨设备同步（用户可自行同步 `~/.wukong/` 和技能目录）、未经用户逐个选择就改动 s-skills 仓库。

## 1. 总体结构

```text
线上（插件，所有人相同，随版本升级）
  hooks/journal.py                记录事件，不向上下文注入任何文字
  skills/reflect/                 新增 --me / --undo / --show / --forget / --share 模式
  skills/reflect/scripts/profile.py   归纳候选、校验、渲染、写入、撤销
  skills/reflect/scripts/my_skills.py 个人技能登记、生成、校验、提交到仓库
  skills/author-skill/            起草技能时沿用的写法规范
  skills/automate-me/             首次初始化，输出改为个人规则
  skills/setup-s-instructions/    支持第二个标记块 wukong:personal
  scripts/context_budget.py       常驻 token 上限检查（含个人块上限）

本地（每人不同，插件升级不碰）
  ~/.wukong/journal.db            事件日志（SQLite）
  ~/.wukong/profile.json          个人规则（唯一真相）
  ~/.wukong/history/              每次写入前的 profile.json 备份
  ~/.wukong/my-skills.json        个人技能登记表（来源证据、创建时间、使用次数）
  <宿主用户级技能目录>/my-<名字>/   起草出的个人技能，见第 6 节
```

生效优先级写进个人块开头：当次指令 > 项目规则（仓库 `AGENTS.md`、`project-memory`）> 个人规则 > 库规则。

## 2. 记录：`hooks/journal.py`

### 记什么

| 事件 | 来源钩子 | 字段 |
|---|---|---|
| `skill` 技能被加载 | `PreToolUse`，matcher `Skill` | 技能名 |
| `correction` 用户纠正 | `UserPromptSubmit`，正则命中纠正用语 | 原话前 80 字（脱敏后） |
| `explicit` 用户明说的偏好 | `UserPromptSubmit`，命中「以后」「每次都」「不要再」「记住」 | 原话前 120 字（脱敏后） |
| `task` 用户发起的任务 | `UserPromptSubmit`，除纠正、确认、4 字以内和斜杠命令以外的消息 | 原话前 80 字（脱敏后） |
| `session` 会话开始 | `SessionStart` | 无 |

每行公共字段：`ts`（ISO 时间）、`event`、`session`（宿主给的会话 ID）、`project`（工作目录最后一段，不记完整路径）。

纠正用语初版：`不对`、`错了`、`不是这样`、`别这样`、`又`…`了`、`说了多少次`、`太长`、`太慢`、`简单点`、`no,`、`wrong`、`don't`。只做粗筛，语义归类留给第 4 节由模型做。

### 不记什么

- 不记对话全文、模型回复、工具输出、文件内容。
- 脱敏：长度 ≥ 20 的连续字母数字串、`sk-`/`ghp_`/`AKIA` 等前缀、邮箱、URL 的查询串，统一替换成 `[已隐藏]`。

### 约束

- 存储用 SQLite（Python 自带 `sqlite3`，无依赖），表 `events(id, at, ts, event, session, project, name, via, text)`，`at` 为秒级时间戳并建索引，`PRAGMA user_version` 记录结构版本。
- 每条记录一个事务（`BEGIN IMMEDIATE`），WAL 模式、`synchronous = FULL`：崩溃不留半条，多个会话并发写由 SQLite 锁排队。每条语句拿不到锁最多等 0.5 秒，超时就放弃这一条；调用它的钩子先输出提醒再记录，不卡会话。
- 不打印任何东西：零上下文成本。任何异常（含数据库损坏、目录不可写）静默跳过，不影响会话。
- 目录 700，数据库及 WAL 文件 600，已有文件权限偏松时收紧。每次写入顺带删 90 天以前的记录；每写 200 条再只保留最新 5 万条。
- 没有 `sqlite3` 模块的 Python 上静默不记录。
- `journal.py --dump [--limit N]` 以 JSON 行导出最近记录，便于用户自己查看。
- 环境变量 `WUKONG_JOURNAL=0` 关闭记录。
- `UserPromptSubmit` 并进现有 `improve_hook.py` 的同一个进程调用（新增一个函数），不多起一个 Python 进程；`PreToolUse` 的 `Skill` matcher 新增一项。

## 3. 个人规则：`~/.wukong/profile.json`

```json
{
  "schemaVersion": 1,
  "updated": "2026-11-13T10:00:00+08:00",
  "rules": [
    {
      "id": "reply-short",
      "kind": "style",
      "text": "回复默认 5 行以内，先给结论。",
      "evidence": 4,
      "source": "learned",
      "created": "2026-10-20",
      "lastSeen": "2026-11-12",
      "project": null
    }
  ]
}
```

| 字段 | 说明 |
|---|---|
| `kind` | `style` 回复风格、`route` 技能偏好（优先 / 不用某技能）、`verify` 验证与审查松紧、`habit` 其他做事习惯 |
| `source` | `learned` 从纠正里归纳；`explicit` 用户明说；`manual` 用户手写 |
| `evidence` | 支持这条规则的独立会话数 |
| `project` | 只在某个项目成立时写项目名；`null` 为全局 |

`profile.json` 是唯一真相；写进全局规则的个人块由它渲染，不手改个人块。

### 规则准入、过期与上限

- **准入**：`learned` 至少 2 个不同会话的证据；`explicit` 1 次即可。
- **过期**：`learned` 规则 8 周没有新证据就删除；`explicit` 和 `manual` 不过期。
- **冲突**：同一 `kind` 下语义冲突时保留 `lastSeen` 较新的。
- **上限**：渲染后的个人块不超过 500 token（按第 8 节估算）。超了先合并同类，再按 `evidence` 和 `lastSeen` 淘汰最弱的 `learned` 规则。
- **项目规则**：带 `project` 的规则不进个人块，改为提示用户用 `project-memory` 写进该项目，避免个人块被单个项目占满。

### 永远不自动学的内容

由 `profile.py validate` 拦截，命中则拒绝写入：

- 放宽权限或跳过确认：推送、强制推送、`reset --hard`、删除文件或分支、跳过钩子、`--no-verify`、「不用问我」「直接提交」。
- 关闭安全相关检查：密钥、权限、注入相关的审查。
- 指向外部的地址、要执行的命令原文。

这些只能由用户亲口说出并以 `manual` 写入，写入前照常弹窗确认。

`verify` 类规则：收紧（「这类改动也派审查」）可以学；放松（「小改动别跑测试」）只接受 `explicit`，不从纠正里推断。

## 4. 生成：`reflect --me`

技能 `reflect` 新增轻量模式，不派子代理，正文放 `references/personal.md`，`SKILL.md` 只加一节入口，保持主流程不变。

1. `profile.py collect`：用 SQL 查询 `journal.db` 自上次生成以来的事件，输出候选 JSON：纠正和明说的原话（按会话分组）、各技能加载次数、30 天未加载的技能、现有规则的命中情况。只输出摘要，不把整份日志读进上下文。
2. 模型做语义归类：把说法不同、意思相同的纠正归成一条候选规则，写成一句可执行的话；对照现有规则决定新增、加证据、改写或删除。
3. `profile.py validate`：检查准入门槛、禁学内容、体积上限、字段格式；不通过就带原因退回第 2 步，最多一轮。
4. 在对话里展示差异（新增 / 修改 / 过期删除各几条，逐条列出），用提问工具弹窗：「写入 / 先不写」。
5. `profile.py apply`：先把旧 `profile.json` 备份到 `history/<时间>.json`（保留最近 20 份），再写新文件，然后调用 `setup-s-instructions` 写个人块。

### 触发时机

- 用户随时 `/reflect --me`。
- `SessionStart` 钩子检查：距上次生成超过 7 天，且有至少 3 条新的 `correction` 或 `explicit` 事件时，注入一行提醒「有 N 条新反馈、M 个技能候选，说 /reflect --me」。没有新反馈也没有候选时不提醒。只提醒一次，不自动生成。

### 其他模式

| 命令 | 作用 |
|---|---|
| `/reflect --show` | 列出当前个人规则和证据数 |
| `/reflect --undo` | 回到 `history/` 里最近一份，重写个人块 |
| `/reflect --forget <id或描述>` | 删除指定规则 |
| `/reflect --off` | 清空个人块（保留文件），说明如何删除 `~/.wukong/` 彻底清除 |
| `/reflect --skills` | 列出个人技能、使用次数和是否可删 |
| `/reflect --share my-<名字>` | 把个人技能提交到 s-skills 仓库，见第 6.4 节 |

## 5. 生效：个人标记块

`setup-s-instructions` 的 `global_instructions.py` 增加 `--personal <profile.json>`：

- 新标记 `<!-- wukong:personal:start -->` / `<!-- wukong:personal:end -->`，放在库块 `wukong:instructions` 之后。
- 库块升级只替换库块，个人块原样保留；个人块写入只替换个人块。两者都缺时只写库块。
- 现有的 `.wukong.bak` 首份备份规则照旧适用。
- Cursor 没有可写的全局文件时，返回渲染好的个人块，交给用户粘贴到 User Rules，并说明「尚未配置」。

渲染格式（示例）：

```markdown
<!-- wukong:personal:start -->
## 个人习惯（自动学习，/reflect --show 查看来源）
优先级：当次指令 > 项目规则 > 本节 > 上方通用规则。
- 回复默认 5 行以内，先给结论。
- 做界面先用 html-mockup 出图再写代码。
- 不用 pptx；要幻灯片时先问格式。
<!-- wukong:personal:end -->
```

## 6. 个人技能：发现、起草、集成

### 6.1 发现反复做的任务

`reflect --me` 的 `collect` 一并输出 `task` 事件摘要。模型把意思相同的任务归成一类，按下面的条件提出「技能候选」：

- 同一类任务在 30 天内出现在至少 3 个不同会话；
- 现有技能（库技能和已有个人技能）都不对口：模型对照技能列表判断，并写明「为什么现有的 X 不够」；
- 不是一次性项目工作（只在一个项目里出现的，建议写进该项目的 `project-memory`，不起草技能）。

候选只是提示，列在 `reflect --me` 的结果里：类别名、出现次数、3 条代表原话、建议的技能名和一句用途。`SessionStart` 的提醒也会带上「有 N 个技能候选」。

### 6.2 起草到用户级目录

用户对某个候选说「起草」后：

1. 按 `author-skill` 规范写 `SKILL.md`：`name` 为 `my-<名字>`，前缀避免和库技能重名；描述以代表原话起头。
2. 默认 `disable-model-invocation: true`（点名调用），不增加常驻 token。用户选择「自动调用」时，先用第 8 节估算它的描述成本，超过个人上限就拒绝并说明。
3. `my_skills.py validate`：名字合法且不与库技能、退役名单重名；描述格式符合库规范；正文不含密钥、完整路径、邮箱；不含第 3 节的禁学内容。
4. 在对话里展示全文，弹窗「写入 / 先不写」。
5. 写入宿主的用户级技能目录，并登记到 `~/.wukong/my-skills.json`：

| 宿主 | 用户级技能目录 |
|---|---|
| Claude Code | `~/.claude/skills/my-<名字>/` |
| Cursor | `~/.cursor/skills/my-<名字>/` |
| Codex、WorkBuddy | 实现时核实；核实前写到 `~/.wukong/skills/my-<名字>/`，并告诉用户如何手动接入 |

以后对这个技能的修改走同样的展示与确认；改前备份到 `~/.wukong/history/skills/`。

### 6.3 使用与清理

- 记录钩子的 `skill` 事件同样记录个人技能的加载，登记表据此累计使用次数。
- 60 天没被加载的个人技能，在 `reflect --me` 里提示「可删除」，用户确认后删除目录并移到 `history/`。
- 个人技能数和自动调用的个人技能描述总量各有上限（初值：10 个、300 token），满了先提示清理，不再新增。

### 6.4 可选：集成到 s-skills 仓库

每个个人技能都可单独选择是否提交，默认不提交。

- 时机：个人技能被使用满 5 次后，`reflect --me` 提示一次「这个技能可以考虑并入 s-skills」，不再重复催。用户也可随时 `/reflect --share my-<名字>`。
- 流程：
  1. 去个人化：去掉 `my-` 前缀、去掉项目名、本机路径和个人称呼，展示差异让用户确认。
  2. 在本机的 s-skills 克隆里新开分支（找不到克隆时询问路径，不自动克隆），放进 `plugins/wukong/skills/<名字>/`，补齐 `agents/openai.yaml`、README 技能表、`EXPECTED_SKILL_COUNTS`、触发用例（自动调用时）、CHANGELOG。
  3. 跑 `scripts/check_marketplace.py` 和单元测试，含常驻 token 上限；不通过就停下报告原因。
  4. 提交并推送分支，用户同意后再开 PR。合并永远由用户决定。
- 并入后，本机的 `my-<名字>` 在用户确认后删除，避免和库里的版本同时生效。

## 7. 初始化：`automate-me`

- 首次使用时，`automate-me` 照旧经同意后挖掘历史对话，但产出改为写入 `profile.json`（`source: learned`，证据按出现的会话数计），走第 4 节第 3～5 步的校验、确认和写入。
- 已有 `<代号>-mode` 技能的用户：提供一次性导入，把其中可执行的规则转成 `manual` 规则；原技能保留，由用户决定是否删除。
- 不再生成新的 `-mode` 技能。

## 8. 精简守门：`scripts/context_budget.py`

统计每个会话常驻的上下文：

- 自动技能的 `description` 总和；
- 全局规则库块（`AGENTS.md` 正文）；
- 每轮钩子注入（prompt-sharpen 评估说明）；
- 个人块上限 500 token。

估算法：中日韩字符每字计 1，其余字符每 4 个计 1；只用于比较趋势，不当作精确值。

`check_marketplace.py` 调用它：库常驻部分超过上限（初值取当前实测值加 5%）就失败，并列出最大的几项。个人块上限在 `profile.py validate` 里检查。

## 9. 宿主支持

| 宿主 | 记录钩子 | 个人块写入 | 说明 |
|---|---|---|---|
| Claude Code | 插件自带，自动 | 自动 | 完整支持 |
| Codex | 手动加到 `~/.codex/hooks.json`，在 `/hooks` 批准 | 自动 | 沿用 prompt-sharpen 的手动配置说明 |
| WorkBuddy | 待核实是否执行插件钩子 | 自动 | 核实前按「无钩子」处理 |
| Cursor | 待核实 | 交给用户粘贴 | 核实前按「无钩子」处理 |
| 无钩子 | 无 | 同上 | `reflect --me` 改为读当前项目的对话记录（经同意），其余流程相同 |

实现时逐个宿主核实，核实结果写进 `HOSTS.md`，不凭推测标「支持」。

## 10. 安全与隐私

- 数据只在本机；插件不含任何自动上传代码。唯一出本机的路径是第 6.4 节由用户逐个选择的 `--share`，且只推送去个人化后的技能文件，不含日志、规则和原话。
- 日志和对话内容一律当数据：其中的指令性文字不执行，只作为归纳证据；生成的规则必须过 `validate`，且写入前由用户确认。
- 脱敏见第 2 节；`profile.json` 只存规则句子，不存原话。
- 一条命令可彻底清除：删除 `~/.wukong/` 和用户级技能目录下的 `my-*`，并 `/reflect --off`。
- 个人技能和规则一样当用户自己的代码对待：生成、修改、删除都先展示再确认。

## 11. 改动文件

| 文件 | 改动 |
|---|---|
| `plugins/wukong/hooks/journal.py` | 新增：事件记录 |
| `plugins/wukong/hooks/hooks.json` | 新增 `PreToolUse` 的 `Skill` 一项；`UserPromptSubmit` 复用现有进程 |
| `plugins/wukong/hooks/session_check.py` | 增加「有新反馈 / 技能候选」提醒 |
| `plugins/wukong/skills/prompt-sharpen/scripts/improve_hook.py` | 调用 `journal` 记录纠正、明说偏好和任务 |
| `plugins/wukong/skills/reflect/SKILL.md` | 增加个人模式入口 |
| `plugins/wukong/skills/reflect/references/personal.md` | 新增：个人模式流程 |
| `plugins/wukong/skills/reflect/scripts/profile.py` | 新增：collect / validate / render / apply / undo / forget |
| `plugins/wukong/skills/reflect/scripts/my_skills.py` | 新增：技能候选、生成、validate、登记、清理、share |
| `plugins/wukong/skills/reflect/references/share.md` | 新增：提交到仓库的步骤与去个人化清单 |
| `plugins/wukong/skills/setup-s-instructions/scripts/global_instructions.py` | 支持个人标记块 |
| `plugins/wukong/skills/setup-s-instructions/SKILL.md` | 说明个人块 |
| `plugins/wukong/skills/automate-me/SKILL.md` | 输出改为 `profile.json`，增加导入旧 `-mode` |
| `scripts/context_budget.py` | 新增：常驻 token 估算与上限 |
| `scripts/check_marketplace.py` | 调用常驻上限检查 |
| `plugins/wukong/hooks/README.md`、`HOSTS.md`、`README.md`、`CHANGELOG.md` | 文档 |

## 12. 测试

- `journal.py`：各事件格式正确；脱敏覆盖密钥、邮箱、URL 查询串；90 天和 5 万条裁剪；8 个进程并发写不丢一条；锁被占用时很快放弃且不影响钩子输出；数据库损坏时静默；`--dump` 输出；`WUKONG_JOURNAL=0` 不写；任何异常不输出、不报错；不向 stdout 打印。
- `profile.py validate`：`learned` 单会话证据被拒；禁学内容（推送、`--no-verify`、「不用问我」等）被拒；`verify` 放松类只接受 `explicit`；超 500 token 时按规则淘汰。
- 过期：`learned` 超 8 周删除，`explicit`/`manual` 保留。
- `apply` / `undo`：写入前备份；`undo` 恢复上一版并重写个人块；`history/` 只留 20 份。
- `global_instructions.py`：库块升级不改个人块；个人块写入不改库块；两块顺序固定；旧标记迁移逻辑不受影响。
- `my_skills.py`：3 个会话以下不出候选；与库技能、退役名单、已有个人技能重名被拒；默认点名；自动调用超上限被拒；60 天未用提示删除；个数上限生效。
- `share`：去个人化清掉 `my-` 前缀、本机路径、项目名；`check_marketplace` 不通过时不提交；未经同意不推送、不开 PR。
- `context_budget.py`：估算对中英混排稳定；超上限时 `check_marketplace` 失败并列出最大项。
- 端到端（Claude Code）：纠正两次「太长了」→ `/reflect --me` → 弹窗确认 → 新会话个人块里出现对应规则。
- 端到端：同类任务出现在 3 个会话 → `/reflect --me` 列出候选 → 起草 → 确认 → `~/.claude/skills/my-<名字>/` 生成，新会话可点名调用。

## 13. 分期

| 期 | 内容 | 验收 |
|---|---|---|
| 1 | `context_budget.py` + `journal.py` + 钩子注册（已完成，1.0.17） | 正常使用一周，日志有事件、会话无可见变化、常驻 token 未增加 |
| 2 | `profile.py` + `reflect --me/--show/--undo/--forget/--off` + 个人块写入（已完成，1.0.17） | 端到端测试通过；手动跑一次能生成合理规则 |
| 3 | 技能候选 + 起草到用户级目录 + `--skills` + 清理 | 端到端测试通过；候选误报可接受（用户觉得有用的占一半以上） |
| 4 | `--share` 提交到仓库 | 一个个人技能走完去个人化、检查、推送分支 |
| 5 | `automate-me` 改造 + `SessionStart` 提醒 + 宿主核实 | 新用户首次初始化可用；各宿主支持情况和用户级技能目录写进 `HOSTS.md` |

第 1 期攒两到三周真实数据后再定第 2 期的纠正用语和归类提示词，不凭空调参。

## 14. 待定

- 纠正用语正则的初版是否偏宽：第 1 期结束后按日志里的误报率调整。
- 500 token 上限是否合适：第 2 期按实际规则条数再定。
- 「同类任务」的归类粒度和 3 个会话的门槛：第 3 期按实际候选质量调整。
- 个人技能上限（10 个、300 token）是否合适。
- WorkBuddy、Cursor 的钩子能力，Codex、WorkBuddy 的用户级技能目录：第 5 期逐个核实。
