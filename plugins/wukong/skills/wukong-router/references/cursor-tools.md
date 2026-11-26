# Cursor 宿主参考

仅在当前宿主需要工具、模型、子代理或安装配置时阅读。任务流程与角色职责仍由对应技能定义；本文件集中维护平台差异。按技能名分节的内容中，阶段和步骤编号指对应技能正文；不是要求每次读取全部章节。模型和工具以当前会话实际可用能力为准，保留已有用户配置。

文中 `agents/`、`skills/` 路径相对于插件根目录；派发或读取前解析成当前安装位置的绝对路径。按技能命名的章节对应原技能正文，角色职责不在这里重新定义。

## 使用边界

- 只执行当前任务已授权的动作；工具存在不扩大任务范围。
- 读取配置不等于配置已实际生效；真实派发、读取与运行结果分别记录。
- 缺少子代理、浏览器或持久调度能力时说明限制，能顺序完成的部分继续；不编造工具或假装已并行。

## 基本操作

- 插件使用仓库的 Cursor 市场入口；全局加载约定使用 User Rules。项目 Always 规则只对项目生效；显式初始化用 wukong-init。
- 子任务按当前 `Task` 工具支持的参数派发，模型名不能直接用于其他宿主。
- 使用云端任务前确认它是否需要本机文件、界面或登录态；需要本机状态时使用实际可用的本地能力。
- 当前版本不提供某工具或参数时说明替代方式，不以文档示例假装调用成功。

## 通用工具对照

以下为通用工具表中当前宿主的一列；技能正文中的通用动作按此映射。

| 通用动作 | 当前宿主对应能力 |
|---|---|
| 派一个子智能体 | `Task` 工具 |
| 能写文件的通用类型 | `subagent_type: "generalPurpose"` |
| 只读探索 | 同一个 `Task` 加 `readonly: true`（会去掉 MCP 工具） |
| 向用户提问的工具 | `AskQuestion` |
| 后台运行和取结果 | `run_in_background: true`；做完结果回到主对话 |
| 指定模型 | `model` 写具体模型名，不写就继承父级。写代码在这个名字确实可用时用 `grok-4.7-xhigh-fast`，文字、判断和最难的改动用 `claude-opus-5-5-xhigh`。这两个名字不要拿到别的软件里用 |
| 子智能体在哪里跑 | `environment: "cloud"` 放到云端；从非默认的已推送分支开始用 `cloud_base_branch`。需要用户电脑上的文件、界面或登录态时用 `environment: "local"`。云端状态在 Cursor 的后台面板看 |
| 让主对话定时醒来 | 用 `executing-plans` 的「反复检查直到通过」。菜单里有 `/loop` 时交给它：`/loop 1h`、`/loop until <检查>`，或不写间隔的动态模式。本技能不另做计时器 |
| 写 SKILL.md | 跑 `/author-skill`。菜单里有内置 `/create-skill` 时用它起草 |

## author-skill

斜杠菜单里如果有内置的 `/create-skill`，用它起草、测试、迭代。它认得 Cursor 自己的目录和校验。没有这条内置命令时，按上面的步骤写。

项目级放 `.cursor/skills/<技能名>/` 或 `.agents/skills/<技能名>/`。个人级放 `~/.cursor/skills/<技能名>/`。文档还写 Cursor 会为了兼容去读 `.claude/skills/`、`.codex/skills/`、`~/.claude/skills/`、`~/.codex/skills/`。

`name` 用小写英文、数字和连字符，并且等于目录名。本插件的技能名都是这种英文 kebab-case。新 skill 也按这个写，不要再用中文目录名。

## comment-sicko

本插件在 `agents/comment-sicko.md` 注册了这个子智能体。用 `Task`，`subagent_type: "comment-sicko"`，`readonly: true`。软件不认这个类型时，用 `generalPurpose`，`readonly: true`，提示词只写：先完整读对应技能的 SKILL.md，再审范围。

## how

每次都是 `Task`，`subagent_type: generalPurpose`，`readonly: true`。探索者的 `model` 用 `grok-4.7-xhigh-fast`，讲解者用 `claude-opus-5-5-xhigh`。这两个名字必须是这次真能传给 `Task` 的，不能传就省略 `model`。

`Task` 拒绝了某个名字，就从报错里选同一系列里最接近的有效名字并说一句。`readonly: true` 会去掉 MCP。需要 MCP 时不要用这个只读参数，改成提示词里禁止写文件。

## interrogate

用 `Task`。每个审查者：`subagent_type: generalPurpose`，`readonly: true`。Reviewer A 用 `claude-opus-5-5-xhigh`，Reviewer B 用 `grok-4.7-xhigh-fast`；用户本次点名了模型就用点名的。这两个名字必须是这次真能传给 `Task` 的。

`Task` 拒绝了某个条目，就改用它所在系列的默认，并说一句。系列按前缀：`claude-*` 是一个系列；`grok-*`、`cursor-grok-*`、`composer-*` 是一个系列。被拒绝的 `composer-*` 改用 Reviewer B 的默认 `grok-4.7-xhigh-fast`。找不到匹配的系列，就用 Reviewer A 的默认 `claude-opus-5-5-xhigh`。连默认也被拒绝时，从报错里的有效名字里选最接近的，优先同一系列、同一推理档位，并另开一个 PR 更新默认表。

## reflect

三个 `Task`，外加综合时再一个 `Task`。每个都是 `subagent_type: generalPurpose`，`readonly: false`。`readonly: true` 会去掉 MCP。

| 视角 | 名字这次可用时的 `model` |
|---|---|
| 判断 | `claude-opus-5-5-xhigh` |
| 工具 | `grok-4.7-xhigh-fast` |
| 发散 | `claude-opus-5-5-xhigh` |
| 综合 | `claude-opus-5-5-xhigh` |

名字这次不可用就省略 `model`。`Task` 拒绝了某个名字，就从报错里选同一系列里最接近的有效名字并说一句。

## swarm

每个工作者一个 `Task`：`subagent_type: generalPurpose`，`environment: "cloud"`，`run_in_background: true`。`grok-4.7-xhigh-fast` 这次真能传给 `Task` 时用这个名字，否则省略 `model`。

只有工作者需要用户电脑上的文件、界面或登录态时，才改 `environment: "local"`。必须从一个非默认的、已推送的分支开始时，传 `cloud_base_branch`。

`Task` 拒绝了这个名字，就从报错里选同一系列里最接近的有效名字并说一句。

## executing-plans：反复检查

用 Cursor 内置的 `/loop`。它的原文没有公开。公开文档写的是：`/loop` 按给定间隔反复运行一条提示词或一个 skill；不写固定间隔时，由智能体决定何时醒来；想停就停。可以和 `/goal` 一起用。来源：[Agent Skills](https://cursor.com/docs/skills)、[Agent 概览](https://cursor.com/docs/agent/overview)。

斜杠菜单里有 `/loop` 时，把这次的提示词和间隔交给它，例如 `/loop 1h` 配上检查提示，或 `/loop until <完成条件>`。动态模式是不写死间隔、让它自己决定何时醒来。内置命令负责叫醒主对话。本技能不另做一套计时器。

菜单里没有 `/loop` 时，使用当前会话可用的检查与等待能力，由父对话决定是否继续；说明没有建立持久调度。

## why

每次都是 `Task`，`subagent_type: generalPurpose`，`readonly: false`。不要用 `readonly: true`，它会去掉 MCP，调查者和综合者的引用抽查会失效。

调查者的 `model` 用 `grok-4.7-xhigh-fast`，综合者用 `claude-opus-5-5-xhigh`。这两个名字必须是这次真能传给 `Task` 的，不能传就省略。拒绝了某个名字，就从报错里选同一系列里最接近的有效名字。

## show-me-your-work

一个 `Task`，`subagent_type: generalPurpose`，`readonly: true`，`model` 选和父级不同系列的名字。这次能用时，父级是 `grok-*` 就用 `claude-opus-5-5-xhigh`，父级是 `claude-*` 就用 `grok-4.7-xhigh-fast`。

## no-comments

`Task`，`subagent_type: "comment-sicko"`（`agents/comment-sicko.md`）。软件不认这个类型时，用只读的 `generalPurpose`（`readonly: true`），提示词只写：先读 `skills/no-comments/references/comment-sicko.md`，再审这个范围。
