---
name: project-skills
description: "「/project-skills」「提取项目技能」「给这个项目生成专属 skill」「同步项目里的 skills」「检查项目技能过期」。从当前代码库提炼项目专属的高频重复工作流并落盘为项目级 SKILL.md（init），或在代码演进后核对并更新、淘汰过期的项目技能（sync）。Use when extracting project-specific workflows from a repository into local SKILL.md files (init), or auditing and syncing existing project-level skills against codebase changes (sync)."
disable-model-invocation: true
---

本会话首次使用本库技能时，按[全局提示词自检](../wukong-init/references/daily-check.md)只读检查一次。
## 运行环境适配

涉及宿主工具或子代理时，按需阅读[宿主适配](../../HOSTS.md)。

# 提取与维护项目级技能

从当前代码库里挖出**只属于这个项目、以后还会反复执行**的工作流，沉淀为项目本地的 `SKILL.md`；代码演进后定期核对、更新或淘汰过期的项目技能。

## 两种模式

| 模式 | 什么时候 | 动作 |
|---|---|---|
| `init` | 项目还没有项目级技能，首次从仓库提炼 | 侦察高信号源 → 过滤出 3–5 个候选 → 用户勾选后落盘 |
| `sync` | 项目已有本地技能，代码改过或怀疑过期 | 核对失效路径/命令/流程、发现新候选与该淘汰的旧技能 → 确认后最小改动更新或删除 |

用户没指明模式时：若仓库里已存在 `.agents/skills/` 或 `.claude/skills/` 下的技能，默认走 `sync`（可顺带提新候选）；否则走 `init`。

## 职责分工（不重复造轮子）

- **静态现状**（架构、目录、术语表、历史决策）归 [project-memory](../project-memory/SKILL.md)，不做成技能。
- **跨项目个人偏好与通用技能改进**归 [reflect](../reflect/SKILL.md)。
- **单个 `SKILL.md` 写法与去 AI 腔标准**严格遵循 [author-skill](../author-skill/SKILL.md)。

## 落盘位置

只维护一份权威目录，绝不同时写两份重复副本：

- 仓库里已有 `.agents/skills/` 或 `.claude/skills/` 时，沿用已有位置。
- 都没有时在候选表里请用户确认位置：默认跨 Codex / Antigravity 推荐 `.agents/skills/<技能名>/SKILL.md`，纯 Claude Code 团队用 `.claude/skills/<技能名>/SKILL.md`；若供 Codex 使用，同步写入 `agents/openai.yaml`。

## `init`：首次提取

### 1. 只读侦察 5 类高信号源

不要盲读整个仓库，聚焦以下 5 类来源（大项目按[公共派发规则](../run-plan/references/subagents.md)派只读检索子代理分块扫，模型取「检索」角色）：

1. **重复新增套路**：同类功能每次新增要同步改哪些文件（如新接口/路由/权限/schema/i18n/前端模块）。
2. **脚本、构建与发布链**：`package.json` scripts、`Makefile`、`scripts/`、`.github/workflows/`、部署与代码生成命令。
3. **高频踩坑历史**：近期 `git log -n 40` 里反复 `fix:` 的同类问题、已有 `AGENTS.md` / `CLAUDE.md` / `docs/project/`。
4. **本地联调、测试与造数**：测试库 seed、mock 服务、环境变量约定、特殊端到端跑法。
5. **已有项目技能**：核对是否已有类似技能，避免重复提议。

### 2. 三条硬门槛过滤（宁缺毋滥）

每条候选必须同时满足以下 3 条，单次最多推荐 **3–5 个**：

1. **高频复现**：未来会反复执行 ≥3 次的动作流；一次性背景说明踢给 `project-memory` 或 `AGENTS.md`。
2. **项目专属**：通用 `wukong` 技能覆盖不了，包含本仓库具体文件路径、真实命令、内部约定和坑位。
3. **可验证**：有明确输入、改动清单与可执行的验收命令。

### 3. 候选表确认（HARD-GATE）

<HARD-GATE>
在展示候选表并得到用户明确勾选（含技能名、落盘目录与触发策略）之前，不创建任何 `SKILL.md` 文件。
</HARD-GATE>

候选表需列清：

| 候选技能名 | 触发策略（默认点名或 `paths` 限定） | 解决的重复工作 | 依据文件 / 命令 | 建议落盘路径 |
|---|---|---|---|---|

- 默认优先设为点名（`disable-model-invocation: true`）或用 `paths`（glob）限定目录，避免撑大该项目的常驻上下文。
- 不够格做成技能但有价值的发现，单独列一节建议放进 `AGENTS.md` 或 `project-memory`。

### 4. 按规范落盘与事实核验

对用户勾选的每一项：

1. 按 [author-skill](../author-skill/SKILL.md) 的省、准、稳准则起草 `SKILL.md`（控制在 500 行内；长参考放 `references/`，可复用脚本放 `scripts/`，模板放 `assets/`）。
2. 逐条核对正文引用的**每一个文件路径、脚本命令、环境变量与配置键**均真实存在于当前仓库，绝不凭记忆编造。
3. 按[去 AI 腔清单](../tech-doc/references/unslop.md)过一遍文字。

## `sync`：增量检查、更新与淘汰

1. **读取现状**：列出项目本地技能目录下全部 `SKILL.md`，对照目标范围的改动（用户指定范围，或 `git diff` / 近期提交 / 当前目录树）。
2. **四项核查**：
   - **失效引用**：技能里提到的文件、脚本、命令、参数或环境变量已删除或改名；
   - **流程漂移**：框架升级、目录重构或 CI 变更导致步骤与现状不符；
   - **淘汰候选**：已被 lint/hook/脚本自动接管、或长期不再需要的项目技能（做减法）；
   - **新增候选**：近期演进出的新高频专属套路（同样过 3 条硬门槛）。
3. **先报告，确认后再改**：输出只读审计表（保留 / 更新 / 新增 / 删除，每条附仓库证据），等用户批准后再执行最小改动或删除，不重写未受影响的部分。

## 交付说明

完成后简短回报：

- 新建、更新或删除的项目技能路径清单；
- 建议提交到仓库与团队共享，还是留在本地忽略（如含个人环境路径）；
- 未做成技能、建议补充到 `AGENTS.md` 或 `project-memory` 的要点。
