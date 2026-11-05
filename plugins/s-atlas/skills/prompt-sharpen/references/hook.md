# 钩子（Claude Code 默认开启，Codex 需手动配置）

[improve_hook.py](../scripts/improve_hook.py) 让含糊的提示词更稳定地触发本技能。

| 宿主 | 状态 |
| --- | --- |
| Claude Code | 装上插件后由 [hooks.json](../../../hooks/hooks.json) 自动注册，默认开启。 |
| Codex | 实测不读取插件自带的 `hooks/hooks.json`，要在 `~/.codex/hooks.json` 里手动加，并在 `/hooks` 里批准一次，见下文。 |
| Cursor、WorkBuddy | 未验证有对应的钩子机制，仍靠点名或技能描述触发。 |

## 它做什么

- `UserPromptSubmit`：给每条提示词附一段评估说明。模型判断清楚就直接做，含糊才加载 `prompt-sharpen`。以 `*`、`#`、`/` 开头的提示词和系统消息不介入。
- `PreToolUse`（只匹配 `Bash`）：命令是 dev server、watch、`tail -f` 这类长时间运行的进程时，提醒用 `run_in_background`。

只加提醒，不改写提示词，不拦截工具，出错时静默退出。流程和绕过规则改写自 [severity1/claude-code-prompt-improver](https://github.com/severity1/claude-code-prompt-improver)（MIT，见 [LICENSE-prompt-improver](../../../LICENSE-prompt-improver)），只保留这两条，不含它的做法评估、工作流、计划模式等提醒，那些和 s-atlas 的技能路由、模型配置重复。

## 代价

每条提示词多带一段约 300 字的评估说明；后台提醒只在命中长命令时出现。需要本机有 `python3` 或 `python`，两者都没有时钩子报错但不影响对话。

## 单条跳过与关闭

- 单条跳过：提示词以 `*` 开头。
- 整体关闭：钩子不能单独停用，只能停用整个插件，或把 `~/.claude/settings.json` 的 `disableAllHooks` 设为 `true`（会同时关掉你所有的钩子）。

## Codex 手动配置

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
