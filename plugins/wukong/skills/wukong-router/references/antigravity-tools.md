# Antigravity 宿主参考

仅在当前宿主是 Google Antigravity（CLI `agy`、Antigravity App 或 IDE）时阅读。任务流程与角色职责仍由对应技能定义；本文件集中维护平台差异。

## 插件安装与加载

Antigravity 原生识别本仓库的 `plugins/wukong`（`plugin.json`、`rules/AGENTS.md`、`hooks.json`、`skills/*/SKILL.md`）：

- 本地安装：`agy plugin install ./plugins/wukong`
- GitHub 远程安装：`agy plugin install https://github.com/Acefake/s-skills/tree/main/plugins/wukong`
- 开发零复制挂载：在 `~/.gemini/config/plugins.json` 的 `entries` 中注册 `~/s-skills/plugins`（Windows 可运行 `scripts/bootstrap.ps1` 自动配置）
- 校验与查看：`agy plugin validate plugins/wukong`、`agy plugin list`

启用插件后，Antigravity 自动加载 `rules/AGENTS.md` 全局规则和根 `hooks.json`（`SessionStart` 24 小时节流更新与日志、`PreInvocation` 提示词评估与轻提示），无需把库规则再复制一份到全局规则文件。

在 T3 Code 中以 `antigravity-acp` 运行时，若其独立数据目录未读取 `~/.gemini/config/plugins.json`，以当前会话实际发现的技能与工具为准；跨提供商或独立工作区委派另按 [T3 编排参考](t3-code-tools.md)。

## 全局规则、模型块与个人块

- **全局技能规则**：随插件 `rules/AGENTS.md` 自动加载。`global_instructions.py --host antigravity` 只读返回 `configured`（`bundled_by_plugin: true`），不重复写入 `~/.gemini/config/AGENTS.md`，避免规则加载两份占上下文。
- **子代理模型块与个人块**：写入 `~/.gemini/config/AGENTS.md`（独立全局规则文件，无需 frontmatter）。`models.py --host antigravity` 维护 `<!-- wukong:models:start -->` 块，`reflect --me` 维护 `<!-- wukong:personal:start -->` 块，互不干扰。

## 通用工具对照

| 通用动作 | Antigravity 中的做法 |
|---|---|
| 派一个子智能体 | `invoke_subagent`（`TypeName`、`Role`、`Prompt`）。完成后系统自动唤醒，不轮询；继续沟通已有子代理用 `send_message`，查看或终止用 `manage_subagents` |
| 能写文件的通用类型 | `TypeName: "self"`（继承父代理全部工具与配置）；需要定制系统提示词或权限时先用 `define_subagent` 定义再用 `invoke_subagent` 调用 |
| 只读探索 | `TypeName: "research"`（只读沙箱、无网络）；需要网络或 MCP 工具时改用 `self` 并在提示词中禁止修改文件 |
| 隔离工作区 | `invoke_subagent` 的 `Workspace` 参数：`"share"` 为共享底层仓库的独立工作副本（类似 git worktree），`"branch"` 为独立克隆；默认 `"inherit"` 共用工作区 |
| 向用户提问的工具 | `ask_question`（多选/单选卡片；简单是/否问题直接用文字问） |
| 后台命令与长进程 | `run_command`（超过 `WaitMsBeforeAsync` 自动转后台并唤醒，常驻服务设 `IsDaemon: true`，按需设 `NotificationTimeoutSeconds`）；管理用 `manage_task` |
| 指定模型 | `invoke_subagent` 的 `Model` 参数只接受 `inherit`、`pro`、`flash`、`flash_lite`（默认 `inherit`）。不写其他宿主的具体型号名 |
| 指定推理档位 | `invoke_subagent` 没有按次传推理档位的参数；不传档位，也不在模型块里写括号档位 |
| 让主对话定时醒来 | `schedule`（一次性 `DurationSeconds` 或周期 `CronExpression`；需要脱离当前任务常驻才设 `IsDaemon: true`）。不用 shell `sleep` 替代定时器 |
| 写 SKILL.md | 跑 `/author-skill`。全局技能放 `~/.gemini/config/skills/<技能名>/SKILL.md`，项目级放 `.agents/skills/<技能名>/SKILL.md` |

## 专项技能派发

子代理模型按[公共派发规则](../../run-plan/references/subagents.md#模型)取四角色模型块；没有模型块时默认映射：`检索` 用 `flash_lite` 或 `flash`，`规划` / `审查` 用 `pro`，`测试` 用 `flash`，写代码实现者保持 `inherit`。

- **deslop（注释审查子代理）**：`invoke_subagent`，`TypeName: "research"`，提示词写明先读 `skills/deslop/references/comment-sicko.md`，再审目标范围并只返回报告。
- **how / why**：`how` 探索者用 `research`（`检索` 角色），`why` 调查者需要 MCP 时用 `self` 并在提示词里禁止写文件；讲解者与综合者用 `self`（`规划` 角色）。
- **reflect / run-plan（并行群体作战）**：在一条回复里并行发起多个 `invoke_subagent`，等全部唤醒结果回来再综合。需要多模型视角时可在 `pro` 与 `flash` 间区分，若实际同系列或只有单一档位则如实说明没有跨系列换模。`reflect` 的审查者需要访问 MCP 时用 `self` 而非 `research`。
