# 插件钩子（Claude Code 与 Antigravity 自动启用）

装上插件后，[hooks.json](hooks.json) 自动注册下面这些钩子。钩子只加提醒或请求确认，出错时静默退出，不会让会话启动失败。需要本机有 `python3` 或 `python`（3.8 以上）。

| 事件 | 脚本 | 作用 |
| --- | --- | --- |
| `SessionStart` | [session_check.py](session_check.py) | 记下插件版本和目录，只读检查全局技能提示词是否缺失或过期，需要时提醒一次。不写任何配置 |
| `UserPromptSubmit` | [improve_hook.py](../skills/prompt-sharpen/scripts/improve_hook.py) | 含糊的需求加载 `prompt-sharpen`，详见[钩子说明](../skills/prompt-sharpen/references/hook.md) |
| `PreToolUse`（`Bash`） | [improve_hook.py](../skills/prompt-sharpen/scripts/improve_hook.py) | 长时间运行的命令提醒放后台 |
| `SessionStart`、`UserPromptSubmit`、`PreToolUse`（`Skill`） | [journal.py](journal.py) | 本地使用日志，见下文。前两个事件在 `session_check.py`、`improve_hook.py` 的同一进程里记录，不多起进程 |
| `PreToolUse`（`Bash`） | [git_guard.py](git_guard.py) | 跳过提交钩子、强制推送、`reset --hard`、`git clean` 这几类命令先请用户确认。只问不拒绝，用户明确要求时批准即可 |

## 本地使用日志

[journal.py](journal.py) 给个人学习层攒数据，`reflect --me` 用它归纳个人规则。它不打印任何东西，所以不占对话上下文；出错、一次记录等锁总共超过 3 秒或 Python 没有 `sqlite3` 模块时静默跳过；钩子先输出提醒再记录，记录慢了也不影响提醒。

- 位置：SQLite 数据库 `~/.wukong/journal.db`，设了 `WUKONG_HOME` 时放在那个目录。目录权限 700，数据库及 WAL 文件只有你自己能读写；已有的目录或数据库权限偏松时会自动收紧。
- 稳定性：每条记录是一个事务，崩溃不会写出半条；多个会话同时写由 SQLite 加锁排队，不丢数据。用 Python 自带的 `sqlite3`，不需要装依赖。
- 记什么：会话开始、加载了哪个技能（含斜杠命令）、你的纠正（「不对」「太长了」等）、你明说的偏好（「以后」「记住」等）、你发起的任务。每条带时间、会话 ID 和项目目录名。
- 原话只留前 80 字（明说的偏好 120 字），先脱敏再截断：密钥、JWT、邮箱、URL 查询串和疑似令牌的高熵长串替换成 `[已隐藏]`，保留普通技能名与文件路径。确认类回复（「可以」「继续」）、4 个字以内的消息和系统消息不记。
- 不记：模型回复、工具输出、文件内容、完整路径。
- 裁剪：每次写入顺带删掉 90 天以前的记录；每写 200 条再检查一次，只保留最新 5 万条。
- 查看：`python3 <插件目录>/hooks/journal.py --dump --limit 50`，按 JSON 行输出最近的记录。
- 关闭：环境变量 `WUKONG_JOURNAL=0`。彻底清除：删除 `~/.wukong/`。
- 不上传：插件里没有任何上传代码。

## 关闭

钩子不能单独停用，只能停用整个插件，或把 `~/.claude/settings.json` 的 `disableAllHooks` 设为 `true`（会同时关掉你所有的钩子）。

## Antigravity

Antigravity 直接加载插件根 [hooks.json](../hooks.json)（[agy_hook.py](agy_hook.py)）：

- `SessionStart`：24 小时节流后台 `git pull --ff-only`（仅干净具名分支，`WUKONG_AUTO_UPDATE=0` 关闭）并记一次 `session` 日志。
- `PreInvocation`：复用 [improve_hook.py](../skills/prompt-sharpen/scripts/improve_hook.py) 评估 `lastUserInput`，按 `(conversationId, lastUserInput)` 去重，每轮新用户消息只在首次调用时通过 `injectSteps` 注入一次评估提醒并记本地使用日志（无时间戳包装的纯 Antigravity 中连续两轮发送完全相同的原文会跳过第二次）。当前 Antigravity 仅注入 `systemMessage`，不附带 `metadata.user_markdown`（当前宿主遇到该字段会整条丢弃 `injectSteps`）；每次触发结果写入 `~/.wukong/prompt-hook-log.jsonl`（可用 `python hooks/agy_hook.py --status` 查看，`WUKONG_HOOK_LOG=0` 关闭）；可在插件根 `hooks.json` 中将 `wukong-prompt-sharpen` 设为 `"enabled": false` 单独关闭。

## Codex

Codex 不读插件自带的钩子。要用时，照[钩子说明](../skills/prompt-sharpen/references/hook.md)里的「Codex 手动配置」，把对应脚本加进 `~/.codex/hooks.json`。加了 `improve_hook.py` 就会同时记录本地使用日志；Codex 没有 `Skill` 工具，技能加载只能从斜杠命令记到。`git_guard.py` 的 `ask` 在 Codex 里是否被支持没有验证过。

从旧品牌或旧缓存升级时，用当前插件的 `skills/wukong-init/scripts/codex_hooks.py` 检查用户级注册路径；显式 `--apply` 才迁移。日常自检和 `wukong-init` 都会提示这项状态，不再只检查全局规则。迁移不会修改宿主钩子信任信息，仍需在 `/hooks` 核对批准；没有日志时不能仅凭插件已启用就宣称自动记录生效。

## 提交前检查（给本仓库的维护者）

[scripts/git-hooks/pre-commit](../../../scripts/git-hooks/pre-commit) 在提交前运行 `check_marketplace`，内容变了没升版本就拦下。检查的是工作区，不是暂存区，只暂存部分改动时结果可能和实际提交的内容不一致。找不到 Python 3.10+ 或 jsonschema 时提示并放行，CI 仍会检查。它是 git 钩子，不随插件分发，启用：

```bash
git config core.hooksPath scripts/git-hooks
```
