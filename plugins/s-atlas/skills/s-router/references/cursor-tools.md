# Cursor 宿主参考

仅在当前宿主需要工具、模型、子代理或安装配置时阅读。任务流程与角色职责仍由对应技能定义；本文件集中维护平台差异。按技能名分节的内容中，阶段和步骤编号指对应技能正文；不是要求每次读取全部章节。模型和工具以当前会话实际可用能力为准，保留已有用户配置。

文中 `agents/`、`skills/` 路径相对于插件根目录；派发或读取前解析成当前安装位置的绝对路径。按技能命名的章节对应原技能正文，角色职责不在这里重新定义。

## 使用边界

- 只执行当前任务已授权的动作；工具存在不扩大任务范围。
- 读取配置不等于配置已实际生效；真实派发、读取与运行结果分别记录。
- 缺少子代理、浏览器或持久调度能力时说明限制，能顺序完成的部分继续；不编造工具或假装已并行。

## 基本操作

- 插件使用仓库的 Cursor 市场入口；全局加载约定使用 User Rules。项目 Always 规则只对项目生效；显式初始化用 setup-s-instructions。
- 子任务按当前 `Task` 工具支持的参数派发，模型名不能直接用于其他宿主。
- 使用云端任务前确认它是否需要本机文件、界面或登录态；需要本机状态时使用实际可用的本地能力。
- 当前版本不提供某工具或参数时说明替代方式，不以文档示例假装调用成功。

## 通用工具对照

以下为原 s-mode 工具表中当前宿主的一列；技能正文中的通用动作按此映射。

| 通用动作 | 当前宿主对应能力 |
|---|---|
| 派一个子智能体 | `Task` 工具 |
| 能写文件的通用类型 | `subagent_type: "s-agent"`，定义在 `agents/s-agent.md`。提示词要求先完整读`skills/s-mode/SKILL.md`。软件不认这个类型时，退回 `generalPurpose`，提示词写上同样的阅读要求 |
| 只读探索 | 同一个 `Task` 加 `readonly: true`（会去掉 MCP 工具） |
| 向用户提问的工具 | `AskQuestion` |
| 后台运行和取结果 | `run_in_background: true`；做完结果回到主对话 |
| 指定模型 | `model` 写具体模型名。写代码和 `swarm workers` 在这些名字确实可用时用 `grok-4.7-xhigh-fast`，文字、判断和最难的改动用 `claude-opus-5-5-xhigh`。不写 `model` 就继承父级。这两个名字不要拿到别的软件里用 |
| s 模型规则（`/setup-s-models`） | `~/.cursor/rules/s-models.mdc`，`alwaysApply: true`。frontmatter 的 description 是 `s per-role model choices (overrides skill defaults)` |
| 子智能体在哪里跑 | `environment: "cloud"` 放到云端；从非默认的已推送分支开始用 `cloud_base_branch`。需要用户电脑上的文件、界面或登录态时用 `environment: "local"`。云端状态在 Cursor 的后台面板看 |
| 让主对话定时醒来 | 跑 `/timed-loop`。菜单里有 `/loop` 时交给它：`/loop 1h`、`/loop until <检查>`，或不写间隔的动态模式。本技能不另做计时器 |
| 写 SKILL.md | 跑 `/author-skill`。菜单里有内置 `/create-skill` 时用它起草 |


## architect

没有 `architect runners` 时，一个 `claude-opus-5-5-xhigh`，一个 `grok-4.7-xhigh-fast`，而且这两个名字这次必须真能传给 `Task`。别名条目和被拒绝的条目，按本文件 arena 章节的系列规则处理：`claude-*` 一个系列；`grok-*`、`cursor-grok-*`、`composer-*` 一个系列；被拒绝的 `composer-*` 改用 `grok-4.7-xhigh-fast`；找不到系列就用 `claude-opus-5-5-xhigh`。

参赛者是 `Task`，`run_in_background: true`，`subagent_type: generalPurpose`，`model` 为该条目。

## arena

阶段 B：一条消息里 N 个 `Task`，`run_in_background: true`，`subagent_type: generalPurpose`（参赛者要写到自己的输出目录），`model` 为该条目。`auto` 或 `inherit-parent` 省略 `model`。

没有 `arena runners` 时，一个 `claude-opus-5-5-xhigh`，一个 `grok-4.7-xhigh-fast`，而且这两个名字这次必须真能传给 `Task`。

`Task` 拒绝了某个条目，就改用它所在系列的默认，并说一句。系列按前缀：`claude-*` 是一个系列；`grok-*`、`cursor-grok-*`、`composer-*` 是一个系列。被拒绝的 `composer-*` 改用 `grok-4.7-xhigh-fast`。找不到匹配的系列，就用 `claude-opus-5-5-xhigh`。连默认也被拒绝，就从报错里选同一系列里最接近的有效名字。别名条目不要拿去回退。

阶段 C：参赛者都完成之后，再派一个 `Task`，`subagent_type: generalPurpose`，`readonly: true`，`model` 从 `arena cross-judge pool` 里选一个，优先和父级不同系列。没有这行时，从上面两个默认里选一个不同系列的。

## author-skill

斜杠菜单里如果有内置的 `/create-skill`，用它起草、测试、迭代。它认得 Cursor 自己的目录和校验。没有这条内置命令时，按上面的步骤写。

项目级放 `.cursor/skills/<技能名>/` 或 `.agents/skills/<技能名>/`。个人级放 `~/.cursor/skills/<技能名>/`。文档还写 Cursor 会为了兼容去读 `.claude/skills/`、`.codex/skills/`、`~/.claude/skills/`、`~/.codex/skills/`。

`name` 用小写英文、数字和连字符，并且等于目录名。本插件的技能名都是这种英文 kebab-case。新 skill 也按这个写，不要再用中文目录名。

## comment-sicko

本插件在 `agents/comment-sicko.md` 注册了这个子智能体。用 `Task`，`subagent_type: "comment-sicko"`，`readonly: true`。软件不认这个类型时，用 `generalPurpose`，`readonly: true`，提示词只写：先完整读对应技能的 SKILL.md，再审范围。

## how

每次都是 `Task`，`subagent_type: generalPurpose`，`readonly: true`。探索者的 `model` 是 `how explorer`，没有这行时用 `grok-4.7-xhigh-fast`。讲解者的 `model` 是 `how explainer`，没有这行时用 `claude-opus-5-5-xhigh`。这两个默认名必须是这次真能传给 `Task` 的。`auto` 或 `inherit-parent` 省略 `model`。

`Task` 拒绝了某个名字，就改用该角色的默认并说一句。连默认也被拒绝，就从报错里选同一系列里最接近的有效名字。`readonly: true` 会去掉 MCP。需要 MCP 时不要用这个只读参数，改成提示词里禁止写文件。

## interrogate

用 `Task`。每个审查者：`subagent_type: generalPurpose`，`readonly: true`，`model` 设为那一行的对应条目。`auto` 或 `inherit-parent` 省略 `model`。

没有这行配置时，Reviewer A 用 `claude-opus-5-5-xhigh`，Reviewer B 用 `grok-4.7-xhigh-fast`。这两个名字必须是这次真能传给 `Task` 的。

`Task` 拒绝了某个条目，就改用它所在系列的默认，并说一句。系列按前缀：`claude-*` 是一个系列；`grok-*`、`cursor-grok-*`、`composer-*` 是一个系列。被拒绝的 `composer-*` 改用 Reviewer B 的默认 `grok-4.7-xhigh-fast`。找不到匹配的系列，就用 Reviewer A 的默认 `claude-opus-5-5-xhigh`。连默认也被拒绝时，从报错里的有效名字里选最接近的，优先同一系列、同一推理档位，并另开一个 PR 更新默认表。别名条目不是模型名，不要对它做回退。

## reflect

三个 `Task`，外加综合时再一个 `Task`。每个都是 `subagent_type: generalPurpose`，`readonly: false`。`readonly: true` 会去掉 MCP。

| 视角 | 角色行 | 没有这行、并且名字这次可用时的 `model` |
|---|---|---|
| 判断 | `reflect judgment, divergent, synthesizer` | `claude-opus-5-5-xhigh` |
| 工具 | `reflect tooling` | `grok-4.7-xhigh-fast` |
| 发散 | `reflect judgment, divergent, synthesizer` | `claude-opus-5-5-xhigh` |
| 综合 | `reflect judgment, divergent, synthesizer` | `claude-opus-5-5-xhigh` |

`auto` 或 `inherit-parent` 省略 `model`。`Task` 拒绝了某个名字，就改用该行的默认并说一句。连默认也被拒绝，就从报错里选同一系列里最接近的有效名字。

## s-agent

本插件在 `agents/s-agent.md` 注册了这个子智能体，`is_background: true`。父对话用 `Task`，`subagent_type: "s-agent"`。软件不认这个类型时，用 `generalPurpose`，提示词的第一句要求先完整读 `s-mode` 的 `SKILL.md`。不要派 s-agent 去运行 playbook 本身。

## setup-s-models：配置位置

| 宿主 | 配置或工具 | 生效或限制 | 依据或说明 |
|---|---|---|---|
| Cursor | `~/.cursor/rules/s-models.mdc`。frontmatter 写 `description: s per-role model choices (overrides skill defaults)` 和 `alwaysApply: true`，下面接 setup-s-models 的标记段正文 | 会。新对话生效 | Cursor 的用户规则目录 |

## setup-s-models

这次对话在 Cursor 里时，按下面做。模型名通过 `Task` 的 `model` 参数传给子智能体。`inherit-parent` 和 `auto` 省略 `model`。

预算和确认用 `AskQuestion`。四个选项用 setup-s-models 的中文标签：省、中、大、不限，并带上该技能里的额度提示。检测不到模型时，请用户把有权限的名字贴过来。

写入 `~/.cursor/rules/s-models.mdc`，覆盖整个文件。frontmatter 用这两行：

```
description: s per-role model choices (overrides skill defaults)
alwaysApply: true
```

`grok-4.7-xhigh-fast` 和 `claude-opus-5-5-xhigh` 只有这次真的能传给 `Task` 才写进文件。两个都在、预算是「大」时，角色行就是下面这份，评审列表 2 项。其他档按 setup-s-models 改列表长度和后缀，改完的名字必须仍在检测结果里。

```
feature, refactoring: grok-4.7-xhigh-fast
bug-fix: grok-4.7-xhigh-fast
perf-issue: grok-4.7-xhigh-fast
hillclimb: grok-4.7-xhigh-fast
judgment and prose: claude-opus-5-5-xhigh
hardest tasks: claude-opus-5-5-xhigh
how explorer: grok-4.7-xhigh-fast
how explainer: claude-opus-5-5-xhigh
why investigators: grok-4.7-xhigh-fast
why synthesizer: claude-opus-5-5-xhigh
reflect tooling: grok-4.7-xhigh-fast
reflect judgment, divergent, synthesizer: claude-opus-5-5-xhigh
arena runners: claude-opus-5-5-xhigh, grok-4.7-xhigh-fast
arena cross-judge pool: claude-opus-5-5-xhigh, grok-4.7-xhigh-fast
swarm workers: grok-4.7-xhigh-fast
architect runners: claude-opus-5-5-xhigh, grok-4.7-xhigh-fast
interrogate reviewers: claude-opus-5-5-xhigh, grok-4.7-xhigh-fast
```

检测不到这两个名字时，用检测到的写代码模型和判断模型填同一张表，并说明默认名这次不可用。写完告诉用户：新开一个对话后，这条规则才会生效。

各 skill 在 Cursor 里的 `Task` 参数（`subagent_type`、`readonly`、`environment`、`cloud_base_branch`、`run_in_background`）写在本文件中对应技能的章节，这里不另做一套。

## swarm

每个工作者一个 `Task`：`subagent_type: generalPurpose`，`environment: "cloud"`，`run_in_background: true`，`model` 用第 4 步选的名字。`auto` 或 `inherit-parent` 省略 `model`。没有这行配置、并且 `grok-4.7-xhigh-fast` 这次真能传给 `Task` 时，用这个名字。

只有工作者需要用户电脑上的文件、界面或登录态时，才改 `environment: "local"`。必须从一个非默认的、已推送的分支开始时，传 `cloud_base_branch`。

`Task` 拒绝了配置的名字，就改用 `grok-4.7-xhigh-fast` 并说一句。连这个默认也被拒绝，就从报错里选同一系列里最接近的有效名字。

## timed-loop

用 Cursor 内置的 `/loop`。它的原文没有公开。公开文档写的是：`/loop` 按给定间隔反复运行一条提示词或一个 skill；不写固定间隔时，由智能体决定何时醒来；想停就停。可以和 `/goal` 一起用。来源：[Agent Skills](https://cursor.com/docs/skills)、[Agent 概览](https://cursor.com/docs/agent/overview)。

斜杠菜单里有 `/loop` 时，把这次的提示词和间隔交给它，例如 `/loop 1h` 配上检查提示，或 `/loop until <完成条件>`。动态模式是不写死间隔、让它自己决定何时醒来。内置命令负责叫醒主对话。本技能不另做一套计时器。

菜单里没有 `/loop` 时，使用当前会话可用的检查与等待能力，由父对话决定是否继续；说明没有建立持久调度。

## why

每次都是 `Task`，`subagent_type: generalPurpose`，`readonly: false`。不要用 `readonly: true`，它会去掉 MCP，调查者和综合者的引用抽查会失效。

调查者的 `model` 是 `why investigators`，没有这行时用 `grok-4.7-xhigh-fast`。综合者的 `model` 是 `why synthesizer`，没有这行时用 `claude-opus-5-5-xhigh`。这两个默认名必须是这次真能传给 `Task` 的。`auto` 或 `inherit-parent` 省略 `model`。拒绝了某个名字，就改用该角色的默认；连默认也被拒绝，就从报错里选同一系列里最接近的有效名字。

## show-me-your-work

一个 `Task`，`subagent_type: generalPurpose`，`readonly: true`，`model` 选和父级不同系列的名字。这次能用时，父级是 `grok-*` 就用 `claude-opus-5-5-xhigh`，父级是 `claude-*` 就用 `grok-4.7-xhigh-fast`。

## no-comments

`Task`，`subagent_type: "comment-sicko"`（`agents/comment-sicko.md`）。软件不认这个类型时，用只读的 `generalPurpose`（`readonly: true`），提示词只写：先读 `skills/comment-sicko/SKILL.md`，再审这个范围。
