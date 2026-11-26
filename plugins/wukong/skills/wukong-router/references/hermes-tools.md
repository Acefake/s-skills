# Hermes 宿主参考

仅在当前会话是 Nous Research 的 Hermes agent（命令 `hermes`）时阅读。这里只记录技能目录和子代理模型能力，不改 Codex、Claude Code、Antigravity 的写法。

家目录是 `$HERMES_HOME`。没设置时是 `~/.hermes`。下文用这家目录表示当前选中的 profile，不写死某台机器的路径。

## 技能目录

主目录是这家的 `skills/`。一个技能是其中的 `SKILL.md`。官方示例按类别子目录放置，`skill_manage` 创建时的 `category` 可选，所以 `<name>/SKILL.md` 和 `<category>/<name>/SKILL.md` 都算技能目录。见[技能系统](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills)。

同一家还可以有 `skills.external_dirs` 和 `skills.create_dir`，写在 `config.yaml` 里。本技能只读这些路径，不改它们。项目技能在 `<项目>/.hermes/skills/` 和 `<项目>/.agents/skills/`，项目根是最近的含 `.git` 的祖先。项目技能要这个 profile 信任该仓库之后才会加载。优先级是项目，然后本地 `skills/`，然后 `skills.create_dir`，然后 `external_dirs`。

`hermes skills list` 列出已安装技能，不列出模型。

## 多个 profile

一个 profile 是一套独立的家目录，有自己的 `config.yaml`、`SOUL.md` 和 `skills/`。`hermes profile list` 列出它们。默认 profile 就是 `$HERMES_HOME` 或 `~/.hermes`。具名 profile 在 `~/.hermes/profiles/<name>/`，并且目录里要有身份文件才会被认作 profile。见[Profiles](https://hermes-agent.nousresearch.com/docs/user-guide/profiles)。

`hermes profile list` 的结果多于一个（含默认）时，列出名字，一次问用户写哪一个。只有默认 profile 时用它，并在回复里说出来。命令失败时，改看 `$HERMES_HOME`（没设置就是 `~/.hermes`）以及它下面 `profiles/` 里带身份文件的目录；仍然多个就问。随后的只读命令和标记段都落在选中的那一家。带 profile 的命令用 `hermes -p <name>`。

## 子代理模型

默认策略下 `delegate_task` 没有按任务的模型参数，派出时不传模型，子代理继承父级或 `delegation.model`。见[委派说明](https://hermes-agent.nousresearch.com/docs/user-guide/features/delegation)。不替用户改 `config.yaml` 的 `delegation` 键。

## 未确认

- 真实 Hermes 会话是否加载本插件。
- advanced-delegation 未安装时，`delegate_task` 的参数列表里是否会出现路线字段。
