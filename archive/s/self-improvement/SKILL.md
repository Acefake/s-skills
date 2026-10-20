---
name: self-improvement
description: "Use when recording a lesson in the project's .learnings/ files instead of editing a skill immediately. 中文触发：命令失败、用户纠正你、缺一项能力、知识过时，或找到更好的做法时，把教训记到项目的 .learnings/ 文件里，以后复用并按原因复查。和 `reflect` 不同：这里是记文件，不是当场改技能说明书。"
version: "4.0.2"
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../../plugins/s/HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。


# 自我改进

把学到的教训和出错记成 markdown 文件，方便以后接着改。以后的代理（agent，帮你干活的 AI）可以把这些记录整理成修复。重要的教训可以晋升（promote，写进以后每次都会读到的说明）到工作区记忆里。

记下、复查、复用、晋升、维护，这几步都在这份技能里。不需要配套技能，不需要单独的服务、插件，也不需要单独的记忆后端。

## 第一次使用：初始化

记任何东西之前，先确认项目根目录（或工作区根目录）里有 `.learnings/` 目录和下面这些文件。缺哪个就建哪个：

```bash
mkdir -p .learnings
[ -f .learnings/LEARNINGS.md ] || printf "# Learnings\n\nCorrections, insights, and knowledge gaps captured during development.\n\n**Categories**: correction | insight | knowledge_gap | best_practice\n\n---\n" > .learnings/LEARNINGS.md
[ -f .learnings/ERRORS.md ] || printf "# Errors\n\nCommand failures and integration errors.\n\n---\n" > .learnings/ERRORS.md
[ -f .learnings/FEATURE_REQUESTS.md ] || printf "# Feature Requests\n\nCapabilities requested by the user.\n\n---\n" > .learnings/FEATURE_REQUESTS.md
```

已有的文件不要覆盖。`.learnings/` 已经建好时，这几行等于什么都不做。

上面这段脚本照原样运行。里面的英文标题不要改。

不要记下密钥、令牌（token）、私钥、环境变量。也不要记下完整的源码或配置文件，除非用户明确要求记到这个程度。优先写短摘要，或打码后的片段。不要贴原始命令输出，也不要贴完整对话记录。

## 快速对照

| 情况 | 怎么做 |
|-----------|--------|
| 命令或操作失败 | 记到 `.learnings/ERRORS.md` |
| 用户纠正你 | 记到 `.learnings/LEARNINGS.md`，类别用 `correction`（纠正） |
| 用户要一个现在没有的功能 | 记到 `.learnings/FEATURE_REQUESTS.md` |
| API 或外部工具失败 | 记到 `.learnings/ERRORS.md`，写上对接细节 |
| 知识过时了 | 记到 `.learnings/LEARNINGS.md`，类别用 `knowledge_gap`（知识缺口） |
| 找到更好的做法 | 记到 `.learnings/LEARNINGS.md`，类别用 `best_practice`（更好的做法） |
| 反复出现、要简化或加固的模式 | 记到或更新 `.learnings/LEARNINGS.md`，写上 `Source: simplify-and-harden`，再加一个稳定的 `Pattern-Key`（模式键，用来把同一类问题对上） |
| 和已有条目很像 | 按 `Pattern-Key` 搜。确认是同一条结论、同一个范围。只有新发生一次才计数 |
| 要复用或晋升已经存下的知识 | 用下面的维护（Maintenance）复查相关的、到期该查的结论。一次性的、还没晋升的条目也算 |
| 来源、决定、依赖或任务变了 | 复查受影响的结论。不要因为放久了就当它过期 |
| 流程上的改进 | 晋升到 `AGENTS.md`（工作区） |
| 工具上的坑 | 晋升到 `TOOLS.md`（工作区） |
| 行为上的习惯 | 晋升到 `SOUL.md`（工作区） |

这些文件名是 OpenClaw 工作区用的。别的软件写到哪里，见文末「在不同软件里怎么用」。

## 记录格式

按模板追加一条。模板在 [assets/LEARNINGS.md](assets/LEARNINGS.md)、[assets/ERRORS.md](assets/ERRORS.md)、[assets/FEATURE_REQUESTS.md](assets/FEATURE_REQUESTS.md)。观察、上下文、建议怎么做、元数据，都要留着。写好的例子见 [references/examples.md](references/examples.md)。

references/ 和 assets/ 仍是英文，模板标题不要改，否则和初始化脚本对不上。

记下的时候，每条可以反复用的结论都加上下面的维护（Maintenance）块。如果还推不出结论，就写 `Claim: unknown — needs triage`，不要编一条规则。旧条目仍然算有效记录。只在新记一条，或相关复查碰到它时，才补上元数据。不要一次性把旧记录全部迁移。

## 维护（Maintenance）

过去发生过的事不会过期。要维护的是可以反复用的推论或指示，不是“这件事发没发生过”。这叫按原因看上下文会不会失效（cause-aware context decay）。三个 `.learnings/` 文件都适用，包括一次性的、还没晋升的条目。

真不真、有没有用，是两件事。一件真事，对当前任务可能没用。一条好用的变通办法，现在可能已经不对了。

### 类型决定怎么复查

| 类型 | 查什么 |
|------|-------|
| `reality` | 读当前的权威来源，或检查当前环境里、这条范围内的事实。 |
| `decision` | 找到一条权威的、适用的、后来取代它的决定。确认范围，以及它是不是已经生效。放久了，或者另一个团队做了别的选择，都不能算取代它。 |
| `dependency` | 先确认相关的版本或配置。再在那个环境里做一次有代表性的行为验证。升级只是触发一次检查，不会自动让这条退役。 |
| `relevance` | 看它对当前任务或项目还有没有用、适不适用。很久没用，不能证明它是错的。 |

原因还没定下来时，用 `unknown`。一条结论有多个原因时，每个都查，或者把不同的结论拆成各自的维护（Maintenance）块。不要从优先级、状态、重复次数，或 `Pattern-Key` 的正则匹配，去猜语义上的类型或复查节奏。会话扫描（sweep，把一段会话翻一遍找错误）可能把不相关的错误混在一起。分诊（triage，先分类再决定怎么处理）时再给结论分类。原来那次扫描留着，并链回去。

### 节奏决定什么时候复查

- `fast`：变化快。每次要用到它之前都查一下。
- `medium`：工作还在进行时，到相关任务或项目的节点再看。
- `slow`：比较稳。偶尔在相关的大改动或里程碑时复查。
- `durable`：预计会一直成立。权威来源、前提，或适用性被质疑时再查。
- `unknown`：还没有靠得住的节奏。靠它之前先分诊。

这些是定性的节奏，不是统一的半衰期，不是到期日，也不是删除规则。给这条结论写一个具体的触发条件。相关事件压过节奏，`durable` 的结论也一样。相关事件包括：来源更新、被新决定取代、依赖或配置变了、项目或任务换了、出现矛盾。不需要定时任务，也不需要后台自己去复查。

### 写在原条目旁边的轻量元数据

```markdown
### Maintenance
- Claim: reusable inference/instruction, or unknown — needs triage
- Scope: applicable project/task/environment and limits, or unknown
- Authority: source path/section, decision ID, environment, or unknown
- Decay: reality | decision | dependency | relevance | unknown / fast | medium | slow | durable | unknown
- Revalidate: event/cadence; specific check to perform
- Validation: pending | verified | unresolved | contradicted
- Evidence: none yet; when checked, actual date, source/version/configuration, check and result (including failures/conflicts)
- Disposition: retain | revise | externalize | retire; reason and task applicability
- Guidance: none, or target file + section and source-learning ID
```

上面这块照抄，字段名不要译。各字段的意思：

- `Claim`：可以反复用的推论或指示。还不知道就写 `unknown — needs triage`（需要分诊）。
- `Scope`：适用的项目、任务、环境，以及边界。不知道就写 `unknown`。
- `Authority`：来源路径和章节、决定的 ID，或环境。不知道就写 `unknown`。
- `Decay`：类型和节奏。取值就是上面两节里的那些词。
- `Revalidate`：什么事件或节奏会触发复查，以及具体要做哪项检查。
- `Validation`：`pending` 待查，`verified` 已核实，`unresolved` 还没定论，`contradicted` 已被反证。
- `Evidence`：还没有就写 `none yet`。查过就写真实日期、来源、版本或配置、检查内容和结果。失败和冲突也要写。
- `Disposition`：`retain` 留用，`revise` 改正，`externalize` 外置（不把容易变的细节写死，改成去哪里查），`retire` 退役（从当前指导里拿掉，历史还留着）。写上原因，以及还适不适合当前任务。
- `Guidance`：没有就写 `none`。有就写目标文件、章节，和来源学习的 ID。

一开始写 `Validation: pending`、`Evidence: none yet`、`Disposition: retain — provisional, not validated`，除非已有真实证据，可以写得更进一步。试着复查过，不等于验证通过。证据拿不到，或互相冲突，就保持 `unresolved`。写上尝试日期、卡住的原因、下次怎么查。不要把一次成功验证的日期往前推。后面追加结果时，过去的证据保留日期和范围。`Status` 管这个问题有没有解决、有没有晋升。`Validation` 管这条结论有没有证据撑着。`Disposition` 管现在还用不用这条指导。三者互不代表对方。

### 复查、复用、晋升这一圈

1. **挑选。** 按区域、文件、关键词或来源 ID，选出和当前任务相关的条目。再加上在自然停顿点上受影响的、到期该查的结论。不要每回合把整本日志审一遍。也不要只挑 `pending`、已晋升，或重复出现的条目。
2. **分诊。** 旧的、混在一起的条目：找出可以反复用的结论、范围、权威来源、类型和节奏、触发条件。不知道的就明确写不知道。一次事故解决了，恢复成功了，或者又发生了一次，都不能证明这是一条到处都成立的规则。
3. **检查。** 复用或晋升之前，先看还适不适用，触发条件有没有发生，证据是不是到期该查了。需要时按类型做对应的检查。记下真实证据，不要只写打算跑哪条命令。证据缺失或冲突时，不要把这条结论当成 `verified` 去讲，也不要拿去晋升。把不确定说出来。去找来源，或用一个范围收窄的备用办法。被卡住时，不要拿掉安全措施。
4. **选择。** `retain`：有证据且有用，或者明确写着先临时留用、还没验证，同时被卡住。`revise`：用证据改正，或把范围收窄。`externalize`：把容易变的细节换成一条能用的“去哪里查”的指示。`retire`：有证据说明为什么，就从当前指导里排除。外置要写清去哪看、读什么或测什么、拿不到或冲突时怎么办。一句含糊的“去看文档”不够。把这条检索路径当成已验证之前，先确认它真的能用。
5. **记下并传出去。** 追加一条带日期的复查笔记。写上结果、原因、证据。改了的话，写旧结论 → 新结论。保留原来的观察、解决记录、晋升目标和日期、以前的复查。用源链接去更新已经晋升出去的指导。改过的规则旁边留着来源学习 ID（source-learning ID）。退役的话，写一条退役说明，指向保留下来的历史。不要因为跑了一次复查，就把 `Recurrence-Count` 或 `Last-Seen` 往上加。

不要抹掉学习或晋升的历史。不要因为放久了就删。不要因为旧了或没用过，就改用户偏好、削弱安全策略，或重写技能资源文件。创建或修改技能，要有明确的、限定范围的批准。批准了这次接入，不等于以后可以改技能。如果要改的目标文件超出已经允许的范围，把建议的改动记在源条目里，标成 `pending`，并说明现在仍然生效的是哪条指导。不要一声不吭当成已经改好了。

复查结果和出处的例子，读 [references/examples.md#maintenance-examples](references/examples.md#maintenance-examples)。

## ID

格式：`TYPE-YYYYMMDD-XXX`

- TYPE：`LRN`（学习）、`ERR`（错误）、`FEAT`（功能）
- YYYYMMDD：当天日期
- XXX：顺序号，或随机 3 个字符（例如 `001`、`A7B`）

例子：`LRN-20250115-001`、`ERR-20250115-A3F`、`FEAT-20250115-002`

## 解决

问题修好之后，更新这条：

1. 把 `**Status**: pending` 改成 `**Status**: resolved`
2. 在 Metadata 后面加上解决块：

```markdown
### Resolution
- **Resolved**: 2025-01-16T09:00:00Z
- **Commit/PR**: abc123 or #42
- **Notes**: Brief description of what was done
```

这块照抄结构，字段名不要译。`Resolved` 写解决时间。`Commit/PR` 写对应的提交或合并请求。`Notes` 短写做了什么。

其他状态值：

- `in_progress`：正在处理
- `wont_fix`：决定不处理（在 Resolution 的备注里写原因）
- `promoted`：已经写进工作区文件（`SOUL.md`、`TOOLS.md`、`AGENTS.md`）

晋升时把 Resolution 块留着。一次修好，只说明那次事故里发生了什么。可以反复用的规则，要另外走维护（Maintenance）来验证。

## 晋升

一条教训适用面比较广（不是只修一次的补丁）时，把它写进工作区文件。以后每次会话都会带上它。

### 什么时候晋升

- 这条教训跨多个文件或功能都适用
- 任何贡献者（人或 AI）都该知道
- 能挡住反复犯的错
- 记录的是这个项目自己的约定

### 晋升写到哪

| 目标 | 写什么 |
|--------|-------------------|
| `SOUL.md` | 行为准则、说话方式、原则 |
| `TOOLS.md` | 工具能做什么、怎么用、对接时的坑 |
| `AGENTS.md` | 流程、委派方式、自动化规则 |

如果这条教训只属于你正在做的某个项目仓库（不是整个工作区），就写到那个项目自己的代理说明文件（例如它的 `AGENTS.md`）。

### 怎么晋升

1. **先复查。** 先按维护（Maintenance）复查这条限定了范围的结论。只晋升有证据、有用的指导。没解决的假设，或只是重复出现，都不够。
2. **提炼再写上。** 往合适的目标文件加一条短的、范围明确的规则，或一条能用的“去哪里查”的指示。旁边写上 `Source: .learnings/<file>.md#<entry-ID>`。路径用从目标文件出发的真实相对路径。就算页面渲染出来的锚点和 ID 不一样，这个 ID 也还能搜到。
3. **回写原条目。** 设上 `**Status**: promoted`。追加晋升日期，以及目标文件和章节。把 `Guidance` 设成那个位置。已有的解决记录和更早的晋升历史都留着。以后再改，就顺着这条双向链接走。

### 晋升例子

**学习记录**（写得很长）：

> 项目用 pnpm workspaces。试过 `npm install`，失败了。
> 锁文件是 `pnpm-lock.yaml`。必须用 `pnpm install`。

**写进 TOOLS.md**（确认这条查法真的能用之后，改成外置指示）：

```markdown
## Build & Dependencies
- Before installing, read this repo's `package.json` `packageManager` field and lockfile. Use the declared manager; if missing or conflicting, consult the build instructions/maintainer before installing. Source: .learnings/LEARNINGS.md#LRN-20250115-002
```

**学习记录**（写得很长）：

> 改 API 端点时，必须重新生成 TypeScript 客户端。
> 忘了这一步，运行时类型会对不上。

**写进 AGENTS.md**（写成能照做的步骤）：

```markdown
## After API Changes
1. Regenerate client: `pnpm run generate:api`
2. Check for type errors: `pnpm tsc --noEmit`
Source: .learnings/LEARNINGS.md#LRN-20250116-001 (scope: this repo's current generator/configuration)
```

## Pattern-Key

`Pattern-Key` 是三个日志文件里用来去重、用来数重复次数的稳定键。用关键词 grep 会漏掉意思一样、措辞不同的条目。共用一把键就不会漏。键要可靠，`Recurrence-Count` 和晋升规则才用得上。

**格式**：`area.symptom`。正好两级，小写，用连字符。例如 `deps.module-not-found`。症状写得够通用，以后还能再碰上。键里不要放文件名、版本号或主机名。

| Area | 范围 | 例子 |
|------|-------|--------------|
| `api` | 外部 API 或服务的行为 | `api.rate-limit`、`api.schema-mismatch`、`api.missing-endpoint` |
| `auth` | 凭证、令牌、权限范围 | `auth.token-expired`、`auth.missing-scope` |
| `build` | 编译、打包、CI | `build.type-error`、`build.missing-artifact` |
| `config` | 配置文件、环境变量、设置 | `config.missing-env`、`config.invalid-json` |
| `deps` | 包管理器、依赖 | `deps.module-not-found`、`deps.npm-error`、`deps.version-conflict` |
| `fs` | 文件系统 | `fs.no-such-file`、`fs.permission-denied` |
| `net` | 网络连通 | `net.connection-refused`、`net.timeout` |
| `runtime` | 上面没覆盖到的语言或运行时错误 | `runtime.type-error`、`runtime.python-exception` |
| `shell` | Shell 或命令行本身的问题 | `shell.command-not-found`、`shell.nonzero-exit` |
| `simplify` / `harden` | 从 simplify-and-harden 这条输入来的代码质量模式 | `simplify.dead_code`、`harden.input_validation` |

**规则：**

1. **先复用，再新造。** 运行 `grep -rh "Pattern-Key:" .learnings/ | sort -u`。有接近的就用接近的，不要新开一把键。
2. **手写的条目一把键。** OpenClaw 自动扫进来的条目可以带好几把。不相关的结论分开分诊，并链回保留下来的那次扫描。
3. **新区域少造。** 只有好几条都会共用同一个区域时才新造。
4. **笼统的扫描键**（`runtime.error`、`runtime.failure`）意思是还没分类。分诊时换成具体的键。

## 重复

要记的东西和已有条目很像时：

1. **先按键搜。** 运行 `grep -n "Pattern-Key: area.symptom" .learnings/*.md`。这是默认的去重检查。换一种说法、关键词搜不到的，它也能抓住。
2. **退回关键词搜。** 对没有键的旧条目，用 `grep -ri "keyword" .learnings/`。
3. **合并，不要再抄一条。** 确认是同一条结论、同一个范围，不只是键碰巧一样。真的是新发生一次，才把 `Recurrence-Count` 加一，设置 `Last-Seen`，并链上证据。复查或重读不算重复发生。
4. **问题一直反复，就提高优先级。**
5. **考虑系统性修复。** 反复出现通常说明：
   - 缺知识（晋升到 `TOOLS.md` 或 `SOUL.md`）
   - 缺自动化（写进 `AGENTS.md`）
   - 架构问题（开一条技术债工单）

## Simplify & Harden

任务里如果给了 simplify（简化）或 harden（加固）的候选，就在这里收进来。不需要别的技能。手写记录走同一套重复计数和维护规则。

### 怎么收进来

1. 从任务摘要里读 `simplify_and_harden.learning_loop.candidates`。
2. 每条候选用 `pattern_key` 当稳定的去重键。
3. 在 `.learnings/LEARNINGS.md` 里搜已有的同一把键：
   - `grep -n "Pattern-Key: <pattern_key>" .learnings/LEARNINGS.md`
4. 找到了：
   - 只有同一条、限定了范围的结论又新发生一次，才把 `Recurrence-Count` 加一，并更新 `Last-Seen`
   - 用 `See Also` 链到相关条目或任务
5. 没找到：
   - 新建一条 `LRN-...`
   - 设置 `Source: simplify-and-harden`
   - 设置 `Pattern-Key`、`Recurrence-Count: 1`，以及 `First-Seen` 和 `Last-Seen`

### 晋升规则（写回系统提示的反馈）

下面几条都成立时，才考虑把反复出现的模式晋升：

- `Recurrence-Count >= 3`
- 至少出现在 2 个不同任务里
- 发生在 30 天的窗口内

这些是候选信号，不是证明，也不是到期作废的规则。晋升前先走维护（Maintenance）。一次性的学习即使达不到这些门槛，也仍然要做维护。

晋升目标：工作区的 `SOUL.md`、`TOOLS.md` 或 `AGENTS.md`。模式只属于某个项目时，写那个项目自己的代理说明文件。

晋升后的规则写成短的预防规则：写代码之前做什么，写的时候做什么。不要写成很长的事故复盘。

## 定期复查

在自然的停顿点上，用维护（Maintenance）复查相关的、到期该查的结论。不要每回合把整本日志看一遍。

### 什么时候复查

- 开始一项大任务之前
- 做完一个功能之后
- 正在做的这块以前有过教训
- 还在活跃开发时，每周一次

### 快速看状态

```bash
# Count pending items
grep -h "Status\*\*: pending" .learnings/*.md | wc -l

# List pending high-priority items
grep -B5 "Priority\*\*: high" .learnings/*.md | grep "^## \["

# Find learnings for a specific area
grep -l "Area\*\*: backend" .learnings/*.md
```

上面三条分别是：数还有多少 `pending`；列出 `Priority` 为 `high` 且还待处理的条目标题；找出某个 Area（例子是 `backend`）的文件。注释和命令保持原样。换区域时，只改 `backend` 这个值。

### 复查时做什么

- 已经修好的，标成解决
- 相关的、到期该查的结论，不管什么状态都复查，包括一次性的、还没晋升的学习
- 当前指导按情况选择 `retain`、`revise`、`externalize` 或 `retire`，历史留着
- 有证据、适用的学习，带上来源链接再晋升
- 把相关条目连起来
- 反复出现的问题往上升级处理

## 触发词

注意到下面这些，就记下来。

**纠正**（记成学习，类别 `correction`）：

- "No, that's not right..."（不对，不是这样）
- "Actually, it should be..."（其实应该是）
- "You're wrong about..."（你搞错了）
- "That's outdated..."（这个过时了）

**功能请求**（记成功能请求）：

- "Can you also..."（能不能再）
- "I wish you could..."（要是你能……就好了）
- "Is there a way to..."（有没有办法）
- "Why can't you..."（为什么你不能）

**知识缺口**（记成学习，类别 `knowledge_gap`）：

- 用户给了你以前不知道的信息
- 你引用的文档过时了
- API 的实际行为和你以为的不一样

**错误**（记成错误条目）：

- 命令返回非零退出码
- 异常或堆栈
- 输出或行为出乎意料
- 超时或连接失败

## 优先级

| 优先级 | 什么时候用 |
|----------|-------------|
| `critical` | 挡住核心功能，有丢数据的风险，或是安全问题 |
| `high` | 影响大，碰到常用流程，或反复出现 |
| `medium` | 影响中等，有变通办法 |
| `low` | 小麻烦，边界情况，有了更好 |

## Area

用来按代码区域过滤教训：

| Area | 范围 |
|------|-------|
| `frontend` | 界面、组件、客户端代码 |
| `backend` | API、服务、服务端代码 |
| `infra` | CI/CD、部署、Docker、云 |
| `tests` | 测试文件、测试工具、覆盖率 |
| `docs` | 文档、注释、README |
| `config` | 配置文件、环境、设置 |

## 最佳做法

1. **马上记。** 刚出问题，上下文最清楚。
2. **写具体。** 以后的代理要能很快看懂。
3. **写上复现步骤。** 错误尤其要写。
4. **链上相关文件。** 修起来更容易。
5. **给出具体改法。** 不要只写 `investigate`（再去查查）。
6. **类别用统一的。** 才能过滤。
7. **有证据的指导再晋升。** 先确认范围和有用。出处留着。
8. **按原因和节奏复查。** 光是放得久，既不能证明它错了，也不能证明它没用。

## gitignore

**教训只留在本机**（每个开发者自己的）：

```gitignore
.learnings/
```

这个仓库默认就是这样，免得不小心把敏感的、或很杂的本地日志提交进去。

**教训跟仓库走**（全团队共享）：

不要写进 `.gitignore`。教训会变成共享知识。

**混合**（模板入库，条目忽略）：

```gitignore
.learnings/*.md
!.learnings/.gitkeep
```

## 升级和卸载

升级前先读 `CHANGELOG.md`。里面有每个版本的说明。钩子如果有改动，要重新复制钩子，并重启网关（gateway）。钩子命令只在 OpenClaw 里用，见文末。

要关掉或删掉这个技能，按 [references/uninstall.md](references/uninstall.md) 做。`.learnings/` 是用户数据，删之前先看一遍。已经晋升到 `SOUL.md`、`TOOLS.md`、`AGENTS.md` 的内容会留着，要手动删。

## 抽成技能

一条教训也许值得做成可以反复用的技能时，用 [assets/SKILL-TEMPLATE.md](assets/SKILL-TEMPLATE.md)。抽成技能是可选的。维护不依赖它。创建或修改技能资源之前，要先拿到明确的、限定范围的批准。

模板里有候选标准、辅助命令、质量门槛，以及双向出处。抽之前先复查这条限定了范围的结论。一次事故解决了，或只是重复出现，都不算验证通过。以后再改这些资源文件，每次都要自己的范围批准。

## 在不同软件里怎么用

日志目录 `.learnings/` 在哪个软件里都一样，放在项目根目录。

### OpenClaw

OpenClaw 把工作区里的说明文件注入每一次会话，并自动加载技能。不需要改 OpenClaw 核心。

这份技能在 `archive/s/self-improvement/`，不随插件分发。poteto 读的是 `reflect`。

上游说明它改自 https://github.com/pskoett/pskoett-ai-skills （同一仓库里的原技能在 https://github.com/pskoett/pskoett-ai-skills/tree/main/skills/self-improvement ）。

如果还是要单独安装，用下面三种里的一种。

**用 OpenClaw 自带的安装器（推荐）。** 装进当前正在用的 OpenClaw 工作区：

```bash
openclaw skills install @pskoett/self-improving-agent
```

**用 ClawHub 的命令行**（先运行 `npm i -g clawhub`）。装进当前目录下的 `./skills`，不是工作区：

```bash
clawhub install @pskoett/self-improving-agent
```

**手动。** 技能在仓库的 `self-improving-agent/` 子目录里。复制那个文件夹，不是仓库根目录：

```bash
git clone https://github.com/pskoett/self-improving-agent.git /tmp/self-improving-agent-repo
cp -r /tmp/self-improving-agent-repo/self-improving-agent ~/.openclaw/skills/self-improving-agent
```

OpenClaw 会把这些文件注入每一次会话：

```
~/.openclaw/workspace/
├── AGENTS.md          # Multi-agent workflows, delegation patterns
├── SOUL.md            # Behavioral guidelines, personality, principles
├── TOOLS.md           # Tool capabilities, integration gotchas
├── MEMORY.md          # Long-term memory (main session only)
├── memory/            # Daily memory files
│   └── YYYY-MM-DD.md
└── .learnings/        # This skill's log files
    ├── LEARNINGS.md
    ├── ERRORS.md
    └── FEATURE_REQUESTS.md
```

目录树里的英文注释意思是：`AGENTS.md` 放多代理的流程和委派方式；`SOUL.md` 放行为准则、说话风格和原则；`TOOLS.md` 放工具能做什么，以及对接时的坑；`MEMORY.md` 是长期记忆，只在主会话里用；`memory/` 放按天的记忆文件；`.learnings/` 是这份技能的日志。

在 OpenClaw 工作区里建日志目录：

```bash
mkdir -p ~/.openclaw/workspace/.learnings
```

然后建日志文件，或从 `assets/` 复制：

- `LEARNINGS.md`：纠正、知识缺口、更好的做法
- `ERRORS.md`：命令失败、异常
- `FEATURE_REQUESTS.md`：用户要的、现在还没有的能力

晋升目标是 `SOUL.md`、`TOOLS.md`、`AGENTS.md`。

| 学到的类型 | 晋升到 | 例子 |
|---------------|------------|---------|
| 行为习惯 | `SOUL.md` | "Be concise, avoid disclaimers"（说短一点，少写免责声明） |
| 流程改进 | `AGENTS.md` | "Spawn sub-agents for long tasks"（长任务分给子代理） |
| 工具上的坑 | `TOOLS.md` | "Git push needs auth configured first"（`git push` 前要先配好认证） |

跨会话工具只有 OpenClaw 有：

- **sessions_list**：看正在进行的和最近的会话
- **sessions_history**：读另一个会话的记录
- **sessions_send**：把一条教训发给另一个会话
- **sessions_spawn**：拉起一个子代理做后台工作

只在可信的环境里用。只有用户明确要跨会话分享时才用。优先发短的、去掉敏感内容的摘要，加上相关文件路径。不要发原始对话、密钥，或完整的命令输出。

想在会话开始时自动提醒，并在会话结束时检测错误，可以打开这个可选钩子。它只负责提醒，以及记下可能的错误。它不强制执行这套流程，也不复查结论对不对。

```bash
cp -r ~/.openclaw/skills/self-improving-agent/hooks/openclaw ~/.openclaw/hooks/self-improvement
openclaw hooks enable self-improvement
```

它在 `agent:bootstrap` 时触发：注入提醒；如果自动检测到的错误还等着复查，再加一条待分诊说明。它也在 `command:new` 和 `command:reset` 时触发：把刚结束的会话记录扫一遍，把错误模式写进 `<workspace>/.learnings/ERRORS.md`。这是可选的，只有 `.learnings/` 存在时才跑。OpenClaw 没有“每次调用工具”的钩子事件，所以错误检测发生在会话结束时。细节在 `references/openclaw-integration.md`，仍是英文。里面也写了这次扫描抓不到什么。

### Cursor、Claude Code、Codex、OpenCode、WorkBuddy

不要跑 openclaw 命令，也不要复制钩子。日志仍写在项目的 `.learnings/`。

要把教训变成以后每次都生效的规则时：

- Claude Code 和 WorkBuddy 写 `CLAUDE.md`
- Codex 和仓库共用说明写 `AGENTS.md`
- Cursor 写项目里的规则文件（`.cursor/rules`）

这些软件不会自动扫错误。看到失败、被纠正、知识过时，就按正文自己记一条。
