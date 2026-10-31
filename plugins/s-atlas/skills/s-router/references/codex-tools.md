# Codex 宿主参考

仅在当前宿主需要工具、模型、子代理或安装配置时阅读。任务流程与角色职责仍由对应技能定义；本文件集中维护平台差异。按技能名分节的内容中，阶段和步骤编号指对应技能正文；不是要求每次读取全部章节。模型和工具以当前会话实际可用能力为准，保留已有用户配置。

文中 `agents/`、`skills/` 路径相对于插件根目录；派发或读取前解析成当前安装位置的绝对路径。按技能命名的章节对应原技能正文，角色职责不在这里重新定义。

## 使用边界

- 只执行当前任务已授权的动作；工具存在不扩大任务范围。
- 读取配置不等于配置已实际生效；真实派发、读取与运行结果分别记录。
- 缺少子代理、浏览器或持久调度能力时说明限制，能顺序完成的部分继续；不编造工具或假装已并行。

## 基本操作

- 本地开发用仓库安装脚本将技能链接到项目 `.agents/skills/`，新会话确认发现的路径。
- 使用当前会话提供的子代理工具；未提供时不改配置强行启用，按顺序执行或报告能力缺失。
- 工作区、浏览器与定时能力先使用当前宿主提供的工具。原生创建的工作区由原生工具归档，不能凭目录名推断所有权。
- 定时请求只有在持久调度工具保存成功后才算建立；会话内等待不是持久任务。

## 通用工具对照

以下为原 s-mode 工具表中当前宿主的一列；技能正文中的通用动作按此映射。

| 通用动作 | 当前宿主对应能力 |
|---|---|
| 派一个子智能体 | 用话派。当前版本默认开启。直接说 “spawn two agents”、“delegate this work in parallel” 或 “use one agent per point”，并写明等齐再汇总。CLI 用 `/subagents` 看线程。IDE 有后台面板时，面板在输入框上方。也听从 `AGENTS.md` 和 skill 里要求分派的句子。[Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) |
| 能写文件的通用类型 | 内置 `worker`（实现和修复）。提示词的第一句要求先完整读`skills/s-mode/SKILL.md`。要固定模型就写 `~/.codex/agents/<name>.toml`（设过 `CODEX_HOME` 就用那个目录）。必填 `name`、`description`、`developer_instructions`。同名盖过内置。自定义智能体继承父级的权限、provider 和 MCP，不能改沙箱 |
| 只读探索 | 内置 `explorer`。提示词里可以要求不改文件。文档写明这不会变成单独的只读沙箱，子智能体继承父级这一轮的沙箱和审批 |
| 向用户提问的工具 | `request_user_input`（只有主对话能用，子智能体不能问） |
| 后台运行和取结果 | 提示词里写 “Wait for all, then summarize”。并发上限是 `~/.codex/config.toml` 里 `[agents].max_concurrent_threads_per_session`（旧名 `max_threads`），不写时由 Codex 自己选默认。没有文档化的单独取结果工具名 |
| 指定模型 | 见下面「Codex 怎么指定模型」。不要把 Cursor 的模型名写进来 |
| s 模型规则（`/setup-s-models`） | `~/.codex/AGENTS.md` 里标记的那一段；有 `AGENTS.override.md` 就改那个。单独模型再写 `~/.codex/agents/s-<角色>.toml` |
| 子智能体在哪里跑 | 子智能体文档没有 `environment` 或 `cloud_base_branch`。本地 Codex 跟父级同一套沙箱，在本机跑。ChatGPT Work 是另一套托管环境，不要套过来。从别的分支开始：把 SHA 写进提示词 |
| 让主对话定时醒来 | 使用 `timed-loop`。先检查当前宿主的持久调度能力；没有时使用会话内检查并明确限制。 |
| 写 SKILL.md | 跑 `/author-skill`。目录按本文件对应技能的章节 |


## architect

提示词里点名 `s-architect-runners-1` 和 `s-architect-runners-2`，或点名两个这次账号里真有的模型，写明等齐再汇总。

## arena

阶段 B 的提示词：Spawn one subagent per runner. Runner 1 is `s-arena-runners-1`. Runner 2 is `s-arena-runners-2`. Wait for all of them, then stop. 没有 toml 时，改成点名两个这次账号里真有的模型，并写上 `model_reasoning_effort`。文档举例 `gpt-6.1-sol` 和 `gpt-6-luna` 只在账号有它们时才用。

阶段 C：等齐之后再派一个。Spawn one subagent, `s-arena-cross-judge-pool-<n>`（或点名池里选中的模型）. It only scores. Do not edit files. Wait for it. 提示词禁止改文件，不会变成单独的只读沙箱。

`default_subagent_model` 拉不开多个参赛者。profile 不是每个参赛者一个。未核实：给单个子智能体选 profile。

## author-skill

按上面的步骤写。文档化的项目位置包括 `.agents/skills/<技能名>/SKILL.md`。个人目录没有在这次核对的 Codex 文档里写成唯一路径时，先放仓库里的 `skills/<技能名>/SKILL.md`，并告诉用户。

## comment-sicko

用话派一个只读的子智能体，点名内置 `explorer`，或一个自定义智能体。提示词写明先完整读对应技能的 SKILL.md，不要改应用代码。这句话不会变成单独的只读沙箱。

## how

探索用内置 `explorer`，或 `s-how-explorer`。讲解用 `s-how-explainer`，或在提示词里点名模型。复杂情况写成：Spawn one explorer subagent per angle. Each uses model \<怎么工作的探索者，或旧键 how explorer\> with model_reasoning_effort \<档位\>. Wait for all, then spawn one explainer on model \<怎么工作的讲解者，或旧键 how explainer\>. 中文键优先。没有 toml、也点不出两个不同模型时，说一句这次没有换模型。提示词里的「不要改文件」不会变成单独的只读沙箱。

## interrogate

用话派，不要找 `Task` 的 `model` 参数。提示词写成：Spawn one subagent per reviewer. Reviewer A is `<name-a>`（或 “uses model \<A\> with model_reasoning_effort \<档位\>”）. Reviewer B is `<name-b>`. Wait for both. Do not edit files. Return each reviewer's findings.

`<name-a>` 是 `~/.codex/agents/s-interrogate-reviewers-1.toml` 的 `name`。文件里的 `model` 和 `model_reasoning_effort` 优先于口头点名。没有这些文件时，在提示词里点名两个这次账号里真有的模型。文档举例 `gpt-6.1-sol` 和 `gpt-6-luna` 只在账号有它们时才用。`[agents].default_subagent_model` 是全体一个默认，拉不开两个审查者。profile 是整次进程的覆盖，不是每个审查者一个。未核实：给单个子智能体选 profile。

提示词里的「不要改文件」不会变成单独的只读沙箱。

## reflect

提示词写成：Spawn three subagents. Judgment and divergent use `s-reflect-judgment-divergent-synthesizer`（或 model \<判断模型\>). Tooling uses `s-reflect-tooling`（或 model \<写代码模型\>). Wait for all three. Then spawn one synthesizer on the judgment model. 自定义智能体继承父级 MCP。提示词可以要求审查者不要改 skill 文件；这不会变成单独的只读沙箱。模型名用这次账号里真有的。

## s-agent

用话派一个子智能体，点名内置 `worker`，或一个自定义智能体。提示词的第一句要求先完整读 `s-mode` 的 `SKILL.md`。不要派它去运行 playbook 本身。

## setup-s-models：配置位置

| 宿主 | 配置或工具 | 生效或限制 | 依据或说明 |
|---|---|---|---|
| Codex | 在 `~/.codex/AGENTS.md` 里维护 `# s 模型配置` 到 `# s 模型配置结束` 这一段。旧标记 `# s model configuration` 到 `# end s model configuration` 是同一段，读取仍然有效，重写时换成中文标记和中文键。设过 `CODEX_HOME` 就用那个目录。同目录已有 `AGENTS.override.md` 时，Codex 读的是 override 而不是 `AGENTS.md`，就改 override 里的同一段。需要单独模型的角色，再写 `~/.codex/agents/s-<角色>.toml`，见下面 Codex 一节 | 会读 `AGENTS.md` 这一段，也会读 `agents/` 里的自定义智能体。只替换标记之间的内容，只覆盖 `s-` 开头的智能体文件 | [AGENTS.md](https://developers.openai.com/codex/guides/agents-md)，[Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) |

## setup-s-models：模型配置

这里说的是本地 Codex（CLI、IDE、桌面应用）。ChatGPT Work 是另一套托管环境，不要把它的界面套过来。

官方文档：[Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)、[配置进阶](https://learn.chatgpt.com/docs/config-file/config-advanced)、[AGENTS.md](https://developers.openai.com/codex/guides/agents-md)。当前版本默认能派子智能体。没有 Cursor 那种带 `model` 参数的 `Task` 工具。

角色行仍写在 `~/.codex/AGENTS.md`（或 `AGENTS.override.md`）的标记段里。需要单独模型的角色，再写自定义智能体：

- 路径：`~/.codex/agents/s-<角色>.toml`。设过 `CODEX_HOME` 就用那个目录下的 `agents/`。项目里可以用 `.codex/agents/`。只覆盖 `s-` 开头的文件。`<角色>` 仍按旧英文键生成，不用中文键：空格和逗号替换成连字符，连续连字符合并：`how explorer` 是 `s-how-explorer.toml`，列表角色再加 `-1`、`-2`。配置块里的键用中文，没有中文键再读旧英文键。`name` 字段等于不带扩展名的文件名。
- `inherit-parent` 和 `auto` 不写文件。
- 必填 `name`、`description`、`developer_instructions`。`name` 是派出时用的名字，和文件名保持一致最省事，以 `name` 为准。
- 同时写 `model` 和 `model_reasoning_effort`。模型名必须是这次账号里真有的。文档举例是 `gpt-6.1-sol`（重活）和 `gpt-6-luna`（快、窄），账号没有这两个名字就不要写。推理档位用 `# 预算`（旧行 `# budget`）的目标：不限对 `max`，大对 `xhigh`，中对 `high`，省对 `medium`。旧档名 `unlimited`、`large`、`medium`、`small` 相同。文档列出的档位还有 `ultra` 和 `low`。只有该模型支持这个档位才写入；不支持就写它支持的、不超过目标的最高档，并告诉用户。文档建议 GPT-6 Luna 从 `high` 起，GPT-6 Astra 从 `low` 起。
- 只读角色把「不要改文件」写进 `developer_instructions`。文档写明：这句话不会变成单独的只读沙箱。子智能体继承父级这一轮的沙箱和审批。自定义智能体继承父级的权限、provider 和 MCP，文件里不能改这些。
- 内置 `worker` 做实现，`explorer` 做读得多的探索，`default` 是通用兜底。同名自定义智能体会盖过内置。

多样性不要只靠 `[agents].default_subagent_model`。那是全体一个默认值。文档里的解析顺序是：自定义文件里写了 `model` 或 `model_reasoning_effort` 时，文件优先；文件应用前，每个字段先按「这次派出时点名的值 → `[agents]` 的对应默认 → 父级」解析。文件只写了 `model`、没写推理档位时，会保留刚才解析到的档位。`default_subagent_model` 和 `default_subagent_reasoning_effort` 可以不写。并发上限是 `max_concurrent_threads_per_session`（旧名 `max_threads`），不写时由 Codex 自己选默认。这些键在 `~/.codex/config.toml` 的 `[agents]` 里。示例配置里还有一段注释掉的 `[agents.<role>]`，用 `description` 和 `config_file` 指向 toml。Subagents 页说放进 `agents/` 目录、用 `name` 识别即可。

profile 是整次进程的覆盖：`codex --profile <name>` 先读 `~/.codex/config.toml`，再盖上 `~/.codex/<name>.config.toml` 的顶层键。Codex 0.134.0 起不再读 `config.toml` 里的 `[profiles.<name>]`，也不再支持顶层 `profile = "..."`。不要把 profile 当成某个子智能体的模型开关。未核实：能不能给一个被派的子智能体单独选 profile。文档没有这么写。

## swarm

提示词写成：Spawn N subagents in parallel. Each is `s-swarm-workers`（或 “each uses model \<模型\> with model_reasoning_effort \<档位\>”）. Wait for all of them, then summarize. 文件在 `~/.codex/agents/s-swarm-workers.toml`。没有文件时点名这次账号里真有的较快模型。文档举例 `gpt-6-luna` 只在账号有它时才用。

没有 `cloud_base_branch`。SHA 写在提示词里。未核实：有没有把子智能体放到另一台机器的参数。子智能体文档只写了跟父级同一套沙箱。并发很多时，看 `[agents].max_concurrent_threads_per_session`，不写则由 Codex 自己选默认。

## timed-loop

先检查当前宿主是否提供持久调度或唤醒工具；有则按用户授权保存完成条件，没有时才使用下面的会话内检查。在提示词里写明完成条件和“做完这一轮就停，由父对话再决定要不要再派”。需要守着时，用一个子智能体反复跑检查，父对话等它返回再决定。CLI 的 `/subagents` 用来看线程，不是计时器。

## why

自定义智能体继承父级的 MCP，文件里不能改 MCP。调查可以点名内置 `explorer`，或 `s-why-investigators`。综合点名 `s-why-synthesizer`。提示词写成：Spawn one subagent per evidence source. Each uses model \<为什么的调查者，或旧键 why investigators\>. Wait for all, then spawn one synthesizer on model \<为什么的综合者，或旧键 why synthesizer\>. 中文键优先。Do not edit files. 模型名用这次账号里真有的。提示词禁止改文件，不会变成单独的只读沙箱。

## show-me-your-work

提示词里点名另一个这次账号里真有的模型，或点名一个已经写好、模型不同的自定义智能体。`default_subagent_model` 拉不开系列。

## no-comments

用话派一个子智能体，点名内置 `explorer`。提示词只写：先读 `skills/comment-sicko/SKILL.md`，再审这个范围。文档写明这不会变成单独的只读沙箱。
