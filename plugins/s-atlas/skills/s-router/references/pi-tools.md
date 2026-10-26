# Pi 工具对照

技能用动作来表达（"dispatch a subagent"、"create a todo"、"read a file"）。在 Pi 上，这些动作对应下面的工具。

| 技能要求的动作 | Pi 对应项 |
| --- | --- |
| 派发子代理（`Subagent (general-purpose):` 模板） | 如果已经安装，使用子代理工具，例如 `pi-subagents` 提供的 `subagent` |
| 任务跟踪（"create a todo"、"mark complete"） | 如果已经安装待办/任务工具就用它，否则在计划或 `TODO.md` 里跟踪任务 |

## 子代理

Pi 核心不自带标准子代理工具。`pi-subagents` 包是一个很合适的可选伴侣，它提供 `subagent` 工具，支持单代理、链式、并行、异步、分叉上下文，以及恢复/状态工作流。如果没有可用的子代理工具，不要编造 `Task` 调用；在当前会话里按顺序执行，或者说明可选的子代理能力没有安装。

## 任务列表

Pi 核心不自带标准任务列表工具。如果安装了待办/任务扩展，使用它文档中的工具。否则用 writing-plans 的计划文件、Markdown 清单，或仓库本地的 `TODO.md` 来跟踪任务。较旧的文档可能提到 `TodoWrite`；把它当作上面说的任务跟踪动作。
