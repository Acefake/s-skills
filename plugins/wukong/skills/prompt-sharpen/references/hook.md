# 钩子（Claude Code、Antigravity 默认开启，Codex 需手动配置）

[improve_hook.py](../scripts/improve_hook.py) 让含糊的提示词更稳定地触发本技能。

| 宿主 | 状态 |
| --- | --- |
| Claude Code | 装上插件后由 [hooks.json](../../../hooks/hooks.json) 自动注册，默认开启。 |
| Antigravity | 挂载插件后由插件根 [hooks.json](../../../hooks.json) 注册 `PreInvocation`（经 [agy_hook.py](../../../hooks/agy_hook.py) 复用同一套评估规则，按会话与用户输入去重，每轮用户消息只注入一次），默认开启。 |
| Codex | 实测不读取插件自带的 `hooks/hooks.json`，要在 `~/.codex/hooks.json` 里手动加，并在 `/hooks` 里批准一次，见下文。 |

## 它做什么

- `UserPromptSubmit`：给每条提示词附一段评估说明。模型结合对话判断是否存在影响结果的关键缺口；有缺口则加载 `prompt-sharpen` 后研究，必要时才提问。不能只因有动作就放行，也不能只因提示词短就介入。明确要求优化提示词时加载；信息足够时直接执行。以 `*`、`#`、`/` 开头的提示词、系统消息、「可以」「继续」这类确认，以及 4 个字以内的消息不介入，这不影响显式斜杠命令由宿主路由技能。
- `PreToolUse`（只匹配 `Bash`）：命令是 dev server、watch、`tail -f` 这类长时间运行的进程时，提醒用 `run_in_background`。

只加提醒，不改写提示词，不拦截工具，出错时静默退出。同一进程还会往本地写使用日志，不进对话，说明见[插件钩子](../../../hooks/README.md#本地使用日志)。流程和绕过规则改写自 [severity1/claude-code-prompt-improver](https://github.com/severity1/claude-code-prompt-improver)（MIT，见 [LICENSE-prompt-improver](../../../LICENSE-prompt-improver)），只保留这两条，不含它的做法评估、工作流、计划模式等提醒，那些和 wukong 的技能路由重复。

## 代价

每条未跳过的提示词（确认和极短消息除外）都会额外携带约 180 token 的精简评估说明，保留缺口判断标准，不再重复引用用户原话。后台提醒只在命中长命令时出现。需要本机有 `python3` 或 `python`，两者都没有时钩子报错但不影响对话。修改源码不证明已安装的插件缓存或现有会话已热更新；以新一轮实际注入的文本为准，不为刷新擅自重写钩子配置或信任信息。

## 单条跳过、可见性与关闭

- 单条跳过：提示词以 `*` 开头。
- 界面可见提示：只在提示词看起来笼统时显示（不超过 30 个字、只有「优化」「改一下」「看看」这类泛化动作、没有文件名、路径、代码、数字或引号里的具体对象，且不是问句），Claude Code 通过顶层 `systemMessage`、Antigravity 通过 `metadata.user_markdown` 显示一行 `[wukong] prompt-sharpen：需求可能不够具体，已提醒先澄清`（仅展示给用户，不占模型上下文）。这只是粗判，给模型的评估说明不变，是否真加载 `prompt-sharpen` 仍由模型结合对话决定。设环境变量 `WUKONG_HOOK_NOTICE=0` 可关闭界面提示。Codex 对顶层 `systemMessage` 的兼容尚未实测；若在 Codex 侧未展示或有兼容性提示，可设 `WUKONG_HOOK_NOTICE=0` 并改用下方本地状态日志核对。
- 本地状态排查（全宿主通用，含 Codex）：钩子会把最近 50 条触发结果（时间、入口、结果如 `injected` / `skipped:short` / `skipped:confirmation` / `skipped:prefix`，不存提示词正文）记到 `~/.wukong/prompt-hook-log.jsonl`（`WUKONG_HOOK_LOG=0` 关闭）。随时运行下面任一命令核对最近是否触发：

```sh
python <插件目录>/skills/prompt-sharpen/scripts/improve_hook.py --status
python <插件目录>/hooks/agy_hook.py --status --limit 20
```

- 整体关闭：Claude Code 不能单独停用单个钩子，需停用整个插件或把 `~/.claude/settings.json` 的 `disableAllHooks` 设为 `true`（会同时关掉所有钩子）；Antigravity 可在插件根 `hooks.json` 中把 `wukong-prompt-sharpen` 设为 `"enabled": false`。

## Codex 手动配置

升级或插件改名后，先运行当前插件的 `skills/wukong-init/scripts/codex_hooks.py` 检查旧路径。默认只读；明确授权迁移后加 `--apply`，只修已注册的已知内置命令，不安装缺失项、不改其他插件，保留首份 `hooks.json.wukong.bak`。`CODEX_HOME` 和 `--codex-home` 可指定实际配置目录。迁移后需要在新会话 `/hooks` 核对并批准；路径检查通过不等于运行时已经生效。

在 `~/.codex/hooks.json` 的 `UserPromptSubmit` 和 `PreToolUse` 数组里各加一项，已有其他钩子时并进去，不要覆盖。`<路径>` 换成本机 `improve_hook.py` 的绝对路径；Windows 上 `commandWindows` 用 `python`，其余用 `command`：

```json
{ "matcher": "", "hooks": [{ "type": "command", "command": "python3 \"<路径>/improve_hook.py\" || python \"<路径>/improve_hook.py\"", "commandWindows": "python \"<路径>/improve_hook.py\" || python3 \"<路径>/improve_hook.py\"", "timeout": 5 }] }
```

`PreToolUse` 那一项的 `matcher` 写 `"Bash"`。Codex 对新增钩子要求用户批准：新会话里打开 `/hooks`，核对来源后批准，否则钩子不会运行。脚本读取的字段（`hook_event_name`、`prompt`、`tool_name`、`tool_input.command`）和输出格式（`hookSpecificOutput.additionalContext`）在 Codex 里一致，已在 Codex 0.166 上实测：含糊提示词会触发，清楚的不会。

## 在 Claude Code 用户配置里自行注册

不想装插件、或插件钩子没生效时，在 `~/.claude/settings.json` 的 `hooks` 里加这两项，路径换成本机的 `improve_hook.py`：

```json
{
  "hooks": {
    "UserPromptSubmit": [
      { "hooks": [{ "type": "command", "command": "python3 \"<路径>/improve_hook.py\" || python \"<路径>/improve_hook.py\"", "timeout": 5 }] }
    ],
    "PreToolUse": [
      { "matcher": "Bash", "hooks": [{ "type": "command", "command": "python3 \"<路径>/improve_hook.py\" || python \"<路径>/improve_hook.py\"", "timeout": 5 }] }
    ]
  }
}
```

插件钩子和用户配置里的同一条会各跑一次，两处只留一处。新会话才生效。
