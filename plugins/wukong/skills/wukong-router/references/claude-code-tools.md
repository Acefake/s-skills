# Claude Code 宿主参考

仅在当前宿主需要工具、模型、子代理或安装配置时阅读。任务流程与角色职责仍由对应技能定义；本文件集中维护平台差异。按技能名分节的内容中，阶段和步骤编号指对应技能正文；不是要求每次读取全部章节。模型和工具以当前会话实际可用能力为准，保留已有用户配置。

文中 `agents/`、`skills/` 路径相对于插件根目录；派发或读取前解析成当前安装位置的绝对路径。按技能命名的章节对应原技能正文，角色职责不在这里重新定义。

本文 `~/.claude` 是默认用户配置目录；设置了 `CLAUDE_CONFIG_DIR` 时使用该实际目录。全局技能提示词由 wukong-init 显式初始化，日常只读检查。

## 使用边界

- 只执行当前任务已授权的动作；工具存在不扩大任务范围。
- 读取配置不等于配置已实际生效；真实派发、读取与运行结果分别记录。
- 缺少子代理、浏览器或持久调度能力时说明限制，能顺序完成的部分继续；不编造工具或假装已并行。

## 基本操作

- 安装使用仓库的 Claude Code 插件市场入口；全局约定放在 `~/.claude/CLAUDE.md`，项目约定放项目的 `CLAUDE.md`。
- 使用当前会话实际提供的 `Agent` 等工具；角色只读要求和文件归属应明确写入任务。
- 模型使用已有角色配置或当前账号可用的名称；无法独立指定时继承父会话。
- 浏览器和持续监测只使用已提供的能力；持久调度与当前会话后台任务分别报告。

## 通用工具对照

以下为通用工具表中当前宿主的一列；技能正文中的通用动作按此映射。

| 通用动作 | 当前宿主对应能力 |
|---|---|
| 派一个子智能体 | `Agent` 工具（旧版叫 `Task`，现在 `Task` 仍可当别名用） |
| 能写文件的通用类型 | `subagent_type: "general-purpose"` |
| 只读探索 | 派 `Explore`（只读探索）或 `Plan`（只读规划） |
| 向用户提问的工具 | `AskUserQuestion` |
| 后台运行和取结果 | `run_in_background: true`（新版默认就是后台）；做完会通知主对话。专门取结果的工具名不确定，按本软件实际工具来 |
| 指定模型 | `model` 只能写这次 `Agent` 定义里列出的取值（本会话验证过：`sonnet`、`opus`、`haiku`、`fable`；带括号如 `sonnet（medium）` 会被 `InputValidationError` 拒绝）。完整模型 ID 是否可用以工具定义为准，定义里没有就不要写；不写就继承父级 |
| 指定推理档位 | `effort` 字段（`low`、`medium`、`high`、`xhigh`、`max`），只有这次会话的 `Agent` 定义里有这个字段才传。按[公共派发规则](../../run-plan/references/subagents.md#模型)取角色档位，**每次派检索、规划、审查、测试都要传**，不传时子代理用工具默认档，不是父会话的档。实现者等其他子代理不传 |
| 子智能体在哪里跑 | 不确定有没有云端参数。没有就在本机跑，SHA 写在任务说明里 |
| 让主对话定时醒来 | 使用 `run-plan` 的「反复检查直到通过」。先检查当前宿主的持久调度能力；没有时使用会话内检查并明确限制。 |
| 写 SKILL.md | 跑 `/author-skill`。个人 skill 可以放在 `~/.claude/skills/<名字>/SKILL.md` |

## author-skill

Claude Code 的个人 skill 放 `~/.claude/skills/<技能名>/SKILL.md`，项目级放 `.claude/skills/`。使用对应技能正文定义的 frontmatter。

## comment-sicko

派一个只读子智能体，Claude Code 使用当前会话支持的 `Explore` 角色。提示词要求先完整读对应技能的 SKILL.md。没有只读类型时，用通用类型，并在提示词里禁止写应用代码。

## how

探索派 `Explore`。讲解用 `Agent`，`model` 为 `opus` （完整 ID 仅当 `Agent` 定义允许）；探索用 `sonnet` 或 `haiku`。需要 MCP 时不要用 `Explore`。

## reflect

`Agent`，`subagent_type: "general-purpose"`。判断、发散和综合的 `model` 用 `opus`，工具视角用 `sonnet`（完整 ID 仅当 `Agent` 定义允许）。需要 MCP 时不要改用 `Explore`。

## 推理档位

Claude Code 的模型名没有 `-medium` 这类档位后缀，别名只有 `sonnet`、`opus`、`haiku`，档位是另一个独立参数。派的时候不写模型或写 `inherit`，就跟父对话走。

## run-plan：并行群体作战

`Agent`，`subagent_type: "general-purpose"`，`run_in_background: true`。模型用 `sonnet`（完整 ID 仅当 `Agent` 定义允许），不写就跟父级。不确定有没有云端参数。没有就在本机跑，SHA 写在任务说明里。

## run-plan：反复检查

未核实当前 Claude Code 是否提供持久调度命令；先检查当前会话能力。用一个后台盯梢的子智能体，或自己过一会儿再跑同一条检查，并写明用了哪一种。

## why

`Agent`，`subagent_type: "general-purpose"`。调查的 `model` 用 `sonnet`，综合用 `opus`（完整 ID 仅当 `Agent` 定义允许）。需要 MCP 时不要改用 `Explore`。

## worklog

父级是 `sonnet` 就用 `opus`。派不出子智能体时，在主对话里换一种角度再看一遍日志，并说一句没有换模型。

## deslop：注释审查子代理

`Agent`，`subagent_type: "Explore"`。提示词只写：先读 `skills/deslop/references/comment-sicko.md`，再审这个范围。
