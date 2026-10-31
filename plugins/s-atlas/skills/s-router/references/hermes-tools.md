# Hermes 宿主参考

仅在当前会话是 Nous Research 的 Hermes agent（命令 `hermes`）时阅读。这里只记录模型配置、技能目录和子代理模型能力。不改 Codex、Claude Code、Cursor、WorkBuddy 的写法。本文件不提供安装脚本，也不把 `s-atlas` 注册进 Hermes 的技能市场。真实客户端未在本仓库运行，文件校验通过不等于会话发现或派发已经验收。

家目录是 `$HERMES_HOME`。没设置时是 `~/.hermes`。下文用这家目录表示当前选中的 profile，不写死某台机器的路径。

## 技能目录

主目录是这家的 `skills/`。一个技能是其中的 `SKILL.md`。官方示例按类别子目录放置，`skill_manage` 创建时的 `category` 可选，所以 `<name>/SKILL.md` 和 `<category>/<name>/SKILL.md` 都算技能目录。见[技能系统](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills)。

同一家还可以有 `skills.external_dirs` 和 `skills.create_dir`，写在 `config.yaml` 里。本技能只读这些路径，不改它们。项目技能在 `<项目>/.hermes/skills/` 和 `<项目>/.agents/skills/`，项目根是最近的含 `.git` 的祖先。项目技能要这个 profile 信任该仓库之后才会加载。优先级是项目，然后本地 `skills/`，然后 `skills.create_dir`，然后 `external_dirs`。

`hermes skills list` 列出已安装技能，不列出模型。

## 多个 profile

一个 profile 是一套独立的家目录，有自己的 `config.yaml`、`SOUL.md` 和 `skills/`。`hermes profile list` 列出它们。默认 profile 就是 `$HERMES_HOME` 或 `~/.hermes`。具名 profile 在 `~/.hermes/profiles/<name>/`，并且目录里要有身份文件才会被认作 profile。见[Profiles](https://hermes-agent.nousresearch.com/docs/user-guide/profiles)。

`hermes profile list` 的结果多于一个（含默认）时，列出名字，一次问用户写哪一个。只有默认 profile 时用它，并在回复里说出来。命令失败时，改看 `$HERMES_HOME`（没设置就是 `~/.hermes`）以及它下面 `profiles/` 里带身份文件的目录；仍然多个就问。随后的只读命令和标记段都落在选中的那一家。带 profile 的命令用 `hermes -p <name>`。

## 标记段写在哪里

写在选中 profile 的 `SOUL.md`（`$HERMES_HOME/SOUL.md`，默认 `~/.hermes/SOUL.md`，具名 profile 则是该 profile 家目录里的 `SOUL.md`）。两头都有 `# s model configuration` 和 `# end s model configuration` 时，只替换中间。两头都没有时，追加到文件末尾。只看到一头就停，留下原文，包括用户原来的身份说明。

不写 `config.yaml`。它是模型、provider、终端等设置的结构化文件。注释不会进入系统提示。`model`、`providers`、旧的 `custom_providers`、`delegation` 和其他键都保持原样。见[配置](https://hermes-agent.nousresearch.com/docs/user-guide/configuration)。

`SOUL.md` 是这家目录里会注入父对话系统提示的全局身份文件，只从 `HERMES_HOME` 读取，不从工作目录发现。见[上下文文件](https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files)和 [SOUL.md 说明](https://hermes-agent.nousresearch.com/docs/guides/use-soul-with-hermes)。项目里的 `.hermes.md`、`AGENTS.md`、`CLAUDE.md` 只覆盖那个仓库，而且一次只加载一种。标记段要给所有会话的父对话读，所以放在 `SOUL.md`。

子代理的项目上下文不含 `SOUL.md`。标记段是给父对话决定怎么派的。改完 `SOUL.md` 后新开对话。

## 怎么列出可用模型

只读，不写配置：

- `hermes config get model --json`：当前 `provider` 和 `default`（有的文件用 `model` 这个键表示同一个模型名）。
- `hermes config get providers --json`：具名 provider。每个 provider 下的 `models`，以及 `default_model`。
- 旧配置还有顶层 `custom_providers`。`providers` 这个键不存在时，再运行 `hermes config get custom_providers --json`。运行时两者都能读；`hermes update` 会把列表迁到 `providers`。见[模型提供者](https://hermes-agent.nousresearch.com/docs/integrations/providers)。

具名 profile 在这些命令前加 `-p <name>`，读选中的那一家，而不是当前 shell 的默认 profile。

不要加 `--raw`。凭证字段会打出来。交互式 `hermes model` 和会话里的 `/model` 列出的是策展目录，不是端点的原始 `/models` 全量。本步骤不启动交互向导。见[配置模型](https://hermes-agent.nousresearch.com/docs/user-guide/configuring-models)。

未确认有非交互命令可以打印策展目录或端点 `/models` 的全量结果。`discover_models` 为真时，选择器会向端点查询；配置里的 `models` 仍是可以直接读到的名单。上面的命令给不出名字时，请用户把有权限的名字贴过来。这些名字用来向用户说明当前默认和已配置名单。默认的 `delegate_task` 不能按次接收它们，所以不写进 17 行。

## 子代理能不能按次指定模型

不能按角色各传一个模型。17 行都写 `inherit-parent`。派出时不传模型。

[委派说明](https://hermes-agent.nousresearch.com/docs/user-guide/features/delegation)写明：默认策略下 `delegate_task` 没有按任务的模型参数。设置了 `delegation.model` 时，同一批子代理都用这一个模型；省略则用父级模型。`delegation.provider` 同样是全体共用。本技能不写入、不清除这两个键。

可选插件 advanced-delegation 可以用 `model_map` 或 `profile_routes`，让模型在每次任务里选一个已经写好的路线名。模型只看见路线名和说明，看不见 provider 和模型字段。见[插件页](https://hermes-agent.nousresearch.com/docs/plugins/advanced-delegation)。这次工具参数里没有确认到可按角色传入的模型名之前，不把路线名写进 17 行，也不改 `delegation.backend`。看板的按任务模型是另一条功能，不是 `delegate_task` 的参数，本技能不使用它。

不把 17 个角色收成 `delegation.model` 这一个键。[PR 76480](https://github.com/NousResearch/hermes-agent/pull/76480) 曾描述 `hermes subagent model` 也写这个共用键；该 PR 已关闭且未合并，当前 CLI 参考里未确认有这条命令。不要运行它。

## 推理档位

父级档位是 `agent.reasoning_effort`。全体子代理共用的覆盖是 `delegation.reasoning_effort`。[配置模型](https://hermes-agent.nousresearch.com/docs/user-guide/configuring-models)写选择器从 `minimal` 到 `ultra`，并可以关闭推理。[委派插件](https://hermes-agent.nousresearch.com/docs/developer-guide/delegation-provider-plugin)写出 `none`、`minimal`、`low`、`medium`、`high`、`xhigh`。`max` 落在配置页的这个区间里。`ultra` 是区间上端，四个预算不用它。`none` 表示关掉推理。未合并的 [PR 76480](https://github.com/NousResearch/hermes-agent/pull/76480) 还写过 `reset` 用来去掉子代理覆盖；当前 CLI 参考未确认这条命令，不要运行。某个模型被目录标成没有推理控制时，选择器会跳过档位；未确认有非交互命令可以查询这一标记。

四个预算按下面映射。这次模型拒绝其中一档时，改用它接受的、不超过目标的最高档，并说明：

| 预算 | 档位 |
|---|---|
| `unlimited` | `max` |
| `large` | `xhigh` |
| `medium` | `high` |
| `small` | `medium` |

`# budget` 写成中文档名和映射后的档位，例如 `大（xhigh）`。旧行 `large (xhigh)` 与它相同。默认 `delegate_task` 不能按次传 `reasoning_effort`，所以派出时不传。`delegation.reasoning_effort` 会作用在之后的每一个子代理上；本技能不写这个键。用户跳过预算时，`# budget` 写 `inherit-parent`。

## 未确认

- 非交互的全量模型列表命令，以及非交互查询某个模型是否没有推理控制。
- 除 `SOUL.md` 以外、会在所有会话注入父对话的用户级规则文件。项目上下文文件不能代替它。
- advanced-delegation 未安装时，`delegate_task` 的参数列表里是否会出现路线字段。文档写的是默认策略没有按任务模型参数。
- 真实 Hermes 会话是否加载本插件、是否读到 `SOUL.md` 里的标记段。
- `hermes subagent` 是否存在。档位名称以配置页和委派文档为准，不依赖这条命令。
