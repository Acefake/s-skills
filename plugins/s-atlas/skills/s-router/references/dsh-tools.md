# DeepSeek Harness 宿主参考

仅在当前会话是 DeepSeek Harness（命令 `dsh`）时阅读。这里只记录模型配置、技能目录和子代理模型能力。不改 Codex、Claude Code、Cursor、WorkBuddy 的写法。本文件不提供安装脚本，也不把 `s-atlas` 注册进 Harness 市场。真实客户端未在本仓库运行，文件校验通过不等于会话发现或派发已经验收。

家目录是 `$DSH_HOME`。没设置时是 `~/.dsh`。下文用 `$DSH_HOME` 表示这一处，不写死某台机器的路径。

## 技能目录

本地发现顺序以[技能子系统](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/skills.md)为准：

| 顺序 | 来源 | 根目录 |
|---|---|---|
| 1 | 项目 | `<项目>/.dsh/skills` |
| 2 | 项目 | `<项目>/.agents/skills` |
| 3 | 配置 | `customSkillDirs` |
| 4 | 用户 | `$DSH_HOME/skills`（跳过其中的 `.system`） |
| 5 | 用户 | `$DSH_AGENTS_HOME/skills`，没设置 `$DSH_AGENTS_HOME` 时是 `~/.agents/skills` |
| 6 | 随包 | 配置了 `bundledSkillDir` 才有 |

项目根是最近的含 `.git` 的祖先。技能名是 kebab-case。一个技能是 `<name>/SKILL.md`，或根目录下的扁平 `.md`。不递归扫描更深层的 `SKILL.md`。本仓库不代写 `customSkillDirs`。

## 多个 profile

profile 是 `$DSH_HOME/profiles/<name>/` 里已经存在的目录。文档里的出厂模板名有 `web`、`headless`、`sdk`、`sdk-minimal`、`acp`；以目录里实际有的为准，不把模板名当成用户已经装好的 profile。见[架构说明](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/architecture.md)和[CLI 帮助](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/cli-help.md)。

多于一个目录时，列出目录名，一次问用户用哪一个。只有一个就用它，并在回复里说出来。没有目录就不写标记段。

`dsh --profile <name> --dump-config` 和 `dsh --profile <name> --dump-config-schema` 只对选中的、已经存在的 profile 运行。dump 会补齐缺失的 profile 文件，所以不要对 `profiles/` 里没有的名字运行。见[CLI 参考](https://github.com/deepseek-ai/deepseek-harness/blob/master/apps/cli/reference/README.md)。

标记段放在家目录的 `AGENTS.md`，不放进某个 profile 目录。`dsh-agent-instructions` 读的是进程的 `$DSH_HOME`，文档没有 profile 级指令文件。用户要求按 profile 分开写时，说明这一点是未确认，标记段仍然不写进 patch。

## 标记段写在哪里

写在 `$DSH_HOME/AGENTS.md`。写出的两头是 `# s 模型配置` 和 `# s 模型配置结束`。这两头，或旧标记 `# s model configuration` 和 `# end s model configuration`，都在时只替换中间，并写成中文标记和中文键。两头都没有时，追加到文件末尾。只看到一头就停，留下原文。旧起始行只要以 `# s model configuration` 开头就算。

不写 `$DSH_HOME/cordis.patch.yml`，也不写 `$DSH_HOME/profiles/<profile>/cordis.patch.yml`。这两份是顶层 YAML 数组，条目形如 `id`、`name`、`config`。后一层按 `id` 替换整段 `config`，注释不会被 [agent-instructions](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/context/agent-instructions/README.md) 注入对话。家目录还有一份共享的 `$DSH_HOME/cordis.patch.yml`，盖过每个 profile 自己的那一层。这些文件原样保留。

同一段不写进 `~/.agents/AGENTS.md`。两份用户全局文件内容不同时会一起注入。只维护 `$DSH_HOME/AGENTS.md`。

这条指令在新会话注入。外部修改要等下一次成功的文件读写、会话恢复，或进入下一步时才会被重新读到。写完告诉用户新开对话。profile 可以关掉指令插件；dump 里没有 `@deepseek-ai/dsh-agent-instructions` 时，说明文件已写上，这次 profile 未必会读，并记为未确认。

## 怎么列出可用模型

1. 会话里有 `list_subagent_models` 时，用它的返回。省略 `provider` 和 `model`。工具把空字符串当成显式选择而报错时，改成真正省略这两个字段再试一次，并说明这次工具的行为。这个工具只在 `modelDiscovery` 打开时注册。
2. 从选中 profile 的 `dsh --dump-config` 读取允许路线。当前包文档里，路线在宿主设置 `subagent-model-selection`（dump 中的 id 常见写法是 `subagent-model-selection-settings`）的 `allowedModels`，每项有 `provider` 和 `model`。
3. 父级当前路由看 id 为 `agent-default-model`、`name` 为 `@deepseek-ai/dsh-agent-default-model` 的条目，字段是 `config.provider`、`config.model`、`config.reasoningEffort`。这是父级默认，不等于子代理允许列表。见[配置目录](https://deepseek-harness.github.io/deepseek-harness/en/reference/config-catalog)。
4. 文档没有非交互的 `dsh models` 一类全量目录命令。模型选择器是界面。未确认还有别的列出命令。上面三步都给不出名字时，请用户把有权限的名字贴过来。不编造，也不抄别的软件里的名字。

角色行在允许按次选择时写成 `<provider>/<model>`。派出时拆回 `provider` 和 `model` 两个字段。占位符不是真实模型名。

## 子代理能不能按次指定模型

以这次 dump 和 schema 为准，不把出厂模板当成用户机器的现状。[子代理工具说明](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/subagent/tool-subagent/README.md)的当前字段是：

- `modelSelection` 默认 `false`。为 `true` 时，工具才有可选的 `provider`、`model`、`reasoning_effort`。
- `modelDiscovery` 默认 `false`，并且和 `modelSelection` 分开。为 `true` 时才注册 `list_subagent_models`。
- 较早的讨论和一部分目录页面写的是 `modelSelectionSettings`。dump 或 schema 里如果仍是这个名字，`true` 同样表示打开选择。两个名字都以本次输出为准。都看不到就写未确认。

同时满足下面四条，才把确认过的 `<provider>/<model>` 写进角色行：

1. 用来派出的那一个工具（出厂的 spawn；出厂的 fork 关掉选择）`modelSelection` 为 `true`，或旧字段 `modelSelectionSettings` 为 `true`。
2. `--dump-config-schema` 声明了这个字段。schema 没有、dump 却有，写未确认，17 行用 `inherit-parent`。
3. 工具的委派后端支持 `agentOptions`。文档写明进程内 spawn、fork 和 DSH SDK 支持；ACP、Codex、Claude Code 后端会在挂载时失败。dump 里的后端对不上这两组时，写未确认，用 `inherit-parent`。
4. 有一条已经启用、且 `allowedModels` 非空的子代理模型选择设置。没有记录到的会话策略时，显式的 provider 和 model 只允许父代理当前路线。那不能按角色换模型，17 行写 `inherit-parent`。文档允许只提交 `reasoning_effort`：`provider` 和 `model` 必须成对出现，也可以只提交档位，由父级或配置补上路线。

Web 和 Desktop 预设在 spawn 上打开选择和发现，fork 上两者都关。headless、SDK、ACP 的出厂配置不带发现工具。用户的 patch 可以改这些默认值，所以仍以 dump 为准。

第 4 条不满足、前三条满足时：17 行写 `inherit-parent`，派出时不传 `provider` 和 `model`，只传映射后的 `reasoning_effort`。前三条有任一条不满足，或 schema 对不上：17 行写 `inherit-parent`，这三个字段都不传，并说明这次子代理的模型和档位都跟父级走。`agent-default-model` 的 `reasoningEffort` 只描述父级默认，不改那一行。

允许路线在顶层会话创建时采样一次，之后改设置不影响这个会话。写完标记段后新开对话。

## 推理档位

父级默认和子代理字段都叫推理档位：配置里是 `reasoningEffort`，工具参数是 `reasoning_effort`。省略时用该模型自己的默认。

内置 DeepSeek 适配器的档位是 `off`、`low`、`high`、`max`。没有 `medium`，也没有 `xhigh`。见[提供者指南](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/user/guide/providers.md)和 [model-info.ts](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/llm/llm-deepseek/src/model-info.ts)。自定义 provider 以该模型声明的 `reasoningEfforts` 的键为准；声明为 `false` 或没有声明时，这个模型没有可选档位。

预算先映射：不限 → `max`，大 → `xhigh`，中 → `high`，省 → `medium`。旧档名 `unlimited`、`large`、`medium`、`small` 相同。目标不在这次声明的档位里时，按 `off` < `low` < `medium` < `high` < `xhigh` < `max` < `ultra` 选不超过目标的最高已声明档，并说明替换。没有这样的档位时，不传 `reasoning_effort`，用模型默认。内置 DeepSeek 因此是：不限 → `max`，大 → `high`，中 → `high`，省 → `low`。

只有这次工具真有 `reasoning_effort` 字段才在派出时传递。没有这个字段时，`# 预算` 仍写用户选的中文档名和映射后的档位，例如 `大（high）`。旧行 `# budget` 与 `# 预算` 是同一行；`large (xhigh)` 与 `大（xhigh）` 是同一档。重写时写成 `# 预算`。并说明子代理不会收到这个参数。不把档位写进 `cordis.patch.yml`。

## 未确认

- 非交互的全量模型目录命令。
- profile 级指令文件。本次只确认家目录 `AGENTS.md` 和项目链。
- 用户 patch 把字段名留在 `modelSelectionSettings` 时，与当前 README 的 `modelSelection` 是否同时有效。以 schema 为准；schema 对不上就按不能按次指定处理。
- 空字符串参数在当前版本是否仍会被当成显式选择。遇到报错再按上面的方式省略字段。
- 真实 `dsh` 会话是否加载本插件、是否读到标记段。
