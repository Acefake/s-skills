# 插件钩子（仅 Claude Code）

装上插件后，[hooks.json](hooks.json) 自动注册下面这些钩子。钩子只加提醒或请求确认，出错时静默退出，不会让会话启动失败。需要本机有 `python3` 或 `python`（3.8 以上）。

| 事件 | 脚本 | 作用 |
| --- | --- | --- |
| `SessionStart` | [session_check.py](session_check.py) | 记下插件版本和目录，只读检查全局技能提示词是否缺失或过期，需要时提醒一次。不写任何配置 |
| `UserPromptSubmit` | [improve_hook.py](../skills/prompt-sharpen/scripts/improve_hook.py) | 含糊的需求加载 `prompt-sharpen`，详见[钩子说明](../skills/prompt-sharpen/references/hook.md) |
| `PreToolUse`（`Bash`） | [improve_hook.py](../skills/prompt-sharpen/scripts/improve_hook.py) | 长时间运行的命令提醒放后台 |
| `PreToolUse`（`Bash`） | [git_guard.py](git_guard.py) | 跳过提交钩子、强制推送、`reset --hard`、`git clean` 这几类命令先请用户确认。只问不拒绝，用户明确要求时批准即可 |

## 关闭

钩子不能单独停用，只能停用整个插件，或把 `~/.claude/settings.json` 的 `disableAllHooks` 设为 `true`（会同时关掉你所有的钩子）。

## Codex

Codex 不读插件自带的钩子。要用时，照[钩子说明](../skills/prompt-sharpen/references/hook.md)里的「Codex 手动配置」，把对应脚本加进 `~/.codex/hooks.json`。`git_guard.py` 的 `ask` 在 Codex 里是否被支持没有验证过。

## 提交前检查（给本仓库的维护者）

[scripts/git-hooks/pre-commit](../../../scripts/git-hooks/pre-commit) 在提交前运行 `check_marketplace`，内容变了没升版本就拦下。检查的是工作区，不是暂存区，只暂存部分改动时结果可能和实际提交的内容不一致。找不到 Python 3.10+ 或 jsonschema 时提示并放行，CI 仍会检查。它是 git 钩子，不随插件分发，启用：

```bash
git config core.hooksPath scripts/git-hooks
```
