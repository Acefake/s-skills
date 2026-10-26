# Antigravity CLI（`agy`）工具对照

技能用动作来表达（"dispatch a subagent"、"create a todo"、"read a file"）。在 Antigravity CLI（`agy`）上，这些动作对应下面的工具。

| 技能要求的动作 | Antigravity CLI 对应项 |
|----------------------|----------------------|
| 派发子代理（`Subagent (general-purpose):` 模板） | 使用 `invoke_subagent`，并带上内置的 `TypeName`——需要完整能力的工作用 `self`，只读用 `research`（见 [子代理支持](#subagent-support)） |
| 任务跟踪（"create a todo"、"mark complete"） | 一份**任务产物**——`write_to_file`，并设置 `IsArtifact: true` 和 `ArtifactType: "task"`（见 [任务跟踪](#task-tracking)）。**不是** `manage_task`，后者管理后台进程。 |

<a id="task-tracking"></a>

## 任务跟踪

Antigravity **没有待办工具**（`manage_task` 管理的是后台进程——`list`/`kill`/`status`/`send_input`——它*不是*清单）。当技能要求创建待办列表或跟踪任务时，维护一份**任务产物**：用 `write_to_file` 保存的 markdown 清单（`IsArtifact: true`，`ArtifactMetadata.ArtifactType: "task"`），过程中用 `replace_file_content` / `multi_replace_file_content` 编辑。

任何多步任务开始时，创建任务产物，列出计划中的每一步。每完成一步，编辑该产物，把它标成完成（`- [x]`）。计划变了就更新清单。让它保持最新——它是剩余工作的事实来源；对话变长之后，每开始下一步之前先重读它。
