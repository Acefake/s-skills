本技能译自 Jesse Vincent 的 Superpowers（MIT）。许可证见上一级文件夹的 `LICENSE-superpowers`。

## 派发子代理需要多智能体支持

把下面的内容加到你的 Codex 配置（`~/.codex/config.toml`）里：

```toml
[features]
multi_agent = true
```

这会为 `swarm` 和 `subagent-driven-development` 这类技能启用 `spawn_agent`、`wait_agent` 和 `close_agent`。使用 subagent-driven-development 时，实现者子代理和审查者子代理做完全部工作后，你应当总是关闭它们。

## 环境检测

创建工作树或收尾分支的技能，在继续之前应当用只读 git 命令检测自己所处的环境：

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
BRANCH=$(git branch --show-current)
```

- `GIT_DIR != GIT_COMMON` → 已经在一个链接的工作树里（跳过创建）
- `BRANCH` 为空 → detached HEAD（不能从沙箱里分支、推送或创建 PR）

参见 `using-git-worktrees` 的 Step 0 和 `finishing-a-development-branch` 的 Step 1，了解每个技能如何使用这些信号。

## Codex App 收尾

当沙箱阻止分支/推送操作时（外部管理的工作树里处于 detached HEAD），代理提交全部工作，并告知用户使用 App 的原生控件：

- **"Create branch"** — 为分支命名，然后通过 App 界面提交、推送、创建 PR
- **"Hand off to local"** — 把工作交到用户的本地检出

代理仍然可以运行测试、暂存文件，并给出建议的分支名、提交信息和 PR 描述，供用户复制。
