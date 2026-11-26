# DeepSeek Harness 宿主参考

仅在当前会话是 DeepSeek Harness（命令 `dsh`）时阅读。这里只记录技能目录和子代理模型能力，不改 Codex、Claude Code、Cursor、WorkBuddy 的写法。

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

## 子代理模型

默认不传 `provider` 和 `model`，子代理继承父级路线。用户本次指定模型时，只有派出所用的工具 `modelSelection`（旧字段 `modelSelectionSettings`）为 `true`、且 `dsh --dump-config-schema` 声明了这个字段，才传 `provider` 和 `model`；否则报告不能按次指定。见[子代理工具说明](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/subagent/tool-subagent/README.md)。

推理档位的工具参数是 `reasoning_effort`，只有用户本次指定且工具真有这个字段才传。内置 DeepSeek 适配器的档位是 `off`、`low`、`high`、`max`。

## 未确认

- 真实 `dsh` 会话是否加载本插件。
- 用户 patch 把字段名留在 `modelSelectionSettings` 时，与当前 README 的 `modelSelection` 是否同时有效。以 schema 为准。
