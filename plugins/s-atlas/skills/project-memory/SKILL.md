---
name: project-memory
description: "「更新项目文档」「同步项目记录」「建项目档案」「架构文档过期了」「/project-memory」。在项目里建立并维护架构、规范、决策记录；代码有改动后按 diff 只更新受影响的部分。Use when creating or syncing a project's architecture, conventions, and decision records after code changes."
---

本会话首次使用本库技能时，按[全局提示词自检](../setup-s-instructions/references/daily-check.md)只读检查一次。
## 运行环境适配

涉及宿主工具、模型配置或子代理时，按需阅读[宿主适配](../../HOSTS.md)。

# 项目记录

让项目里的架构、规范和决策记录跟着代码走。文字按 [technical-writing](../technical-writing/SKILL.md) 写。

「按 diff 判断、最小改动、不写推测」这套规则改写自 [ondatra-ai/awesome-claude-mcp 的 update-memory](https://github.com/ondatra-ai/awesome-claude-mcp)（MIT，见 [LICENSE-update-memory](../../LICENSE-update-memory)）。

## 三种模式

| 模式 | 什么时候 | 写入 |
| --- | --- | --- |
| `init` | 项目还没有记录，首次建档 | 新建文件；改 `CLAUDE.md`、`AGENTS.md` 前先给出 diff |
| `sync` | 代码有改动后，默认模式 | 只改受影响的部分 |
| `check` | 怀疑记录过期，只想知道哪里失实 | 不写，只出报告 |

用户没说模式时：项目已有记录就用 `sync`，没有就问要不要 `init`。

## 记录放哪里

仓库已有规范优先：

- 项目里已经有约定的位置（`docs/architecture.md`、`memory-bank/`、`docs/project_notes/` 等），就沿用，并在索引里登记为权威位置。
- 没有约定时用 `docs/project/`：

| 文件 | 内容 |
| --- | --- |
| `README.md` | 索引，以及「每个主题的权威位置」表 |
| `architecture.md` | 模块划分、入口、数据流、外部依赖 |
| `conventions.md` | 命名、目录、测试、提交等实际在用的规范，每条标出依据文件 |
| `decisions/NNNN-标题.md` | 一条决策一个文件：背景、决定、取舍 |

- `CLAUDE.md`、`AGENTS.md` 里只放一行指向记录的指针，不放内容，免得撑大每次会话的上下文。
- 每个主题只有一个权威位置，其他地方用链接引用，不复制。

模板见[记录模板](references/templates.md)。

## sync

看这次改动，判断它是否影响记录里的任何一节。

### 读什么

- 用户指定了范围就按范围；没指定，先看暂存区的 `git diff --cached`，没有暂存再看 `git diff` 和最近的提交。
- 再读现有记录。不要通读整个仓库。

### 逐项检查

**仓库结构**
- 新增、改名、删除了目录或关键文件。
- 新增了一类文件的放置规则。

**关键概念**
- 引入了新术语、新框架或新方法。
- 已有术语的定义变了。

**开发环境**
- 构建、测试、检查的命令变了。
- 新增了环境变量或依赖。
- CI 配置变了。

**规范**
- 出现了新的命名或结构规则。
- 出现了新的工作流约定。

**决策**
- 做出了重大取舍，或推翻了旧决策。

### 怎么改

1. 读 diff。
2. 读现有记录。
3. 逐节判断这次改动有没有需要反映的内容。
4. 有：做最小改动。没有：不动文件，并说一句「无需更新」。
5. 重大取舍写成 `decisions/` 下的新文件，不覆盖旧决策；旧决策被推翻时，在旧文件里标注「已被 NNNN 取代」。

### 规则

- **最小改动**：没受 diff 影响的部分，不整理、不重写。
- **不写推测**：只写代码库里现在已有的内容。
- **有依据**：每条规范和结论都能指到一个文件或提交；指不到就不写。
- **不随便删**：只有对应的代码或文件已被删除，才删记录。
- **沿用原样**：保持现有的格式、语气和详细程度。
- **只写现状**：不写提交说明，不写更新日志。历史留给 git。
- 改了记录，在交付说明里列出改了哪几节。

## init

1. **读项目。** 入口文件、配置、目录结构、README、近期提交、测试和构建命令。小项目自己读；大项目按[公共派发规则](../s-mode/references/subagents.md)派只读检索子智能体，各读一块再汇总，角色读 s 模型配置里的「怎么工作的探索者」。派不出子智能体就自己读，并说一句没有换模型。
2. **先给目录和要点。** 列出要建的文件，以及每份的要点，让用户确认。已有记录位置的话，沿用它。
3. **确认后再写。** 先写 `architecture.md`、`conventions.md`、索引；有明确的历史取舍时再补 `decisions/`。
4. **补指针。** 在 `CLAUDE.md`、`AGENTS.md` 里加一行指针；改之前先给出 diff。
5. **只写看得见的。** 看不出来的部分标「待补」，不要编。

## check

只读。对照代码找出：

- 记录里提到、但代码里已经不存在的文件、命令、模块。
- 代码里已有、但记录里没有的重要模块或命令。
- 两处写法互相矛盾的条目。

报告按严重程度排序，每项带记录里的位置和代码里的证据。不修改任何文件；用户要修，再走 `sync`。

## 与其他技能的关系

- [how](../how/SKILL.md) 是一次性讲解，不留记录。它的结论可以作为 `init` 的素材。
- [archify](../archify/SKILL.md) 画图。`architecture.md` 可以引用图，但不由本技能生成。
- [prompt-sharpen](../prompt-sharpen/SKILL.md) 会先读这些记录；记录越准，它越少需要现查。
- [commit-pr](../commit-pr/SKILL.md)：项目有记录时，提交前可以先跑一次 `sync`。
