---
name: finishing-a-development-branch
description: "实现已完成、全部测试通过，且需要决定如何集成工作时，通过呈现合并、PR 或清理的结构化选项来引导开发工作收尾。Use when implementation is done, tests pass, and you need to decide how to integrate the work."
---
本技能译自 Jesse Vincent 的 Superpowers（MIT）。许可证见上一级文件夹的 `LICENSE-superpowers`。

# 收尾开发分支

## 概述

通过呈现清晰选项并处理所选工作流，引导开发工作收尾。

**核心原则：** 核验测试 → 检测环境 → 呈现选项 → 执行选择 → 清理。

**开始时宣布：** 「我正在使用 finishing-a-development-branch 技能来完成这项工作。」

## 流程

### 步骤 1：核验测试

**在呈现选项之前，核验测试通过：**

```bash
# Run project's test suite
npm test / cargo test / pytest / go test ./...
```

**如果测试失败：**
```
Tests failing (<N> failures). Must fix before completing:

[Show failures]

Cannot proceed with merge/PR until tests pass.
```

停下。不要进入步骤 2。

**如果测试通过：** 继续步骤 2。

### 步骤 2：检测环境

**在呈现选项之前确定工作区状态：**

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
```

这决定展示哪一份菜单，以及清理如何进行：

| 状态 | 菜单 | 清理 |
|-------|------|---------|
| `GIT_DIR == GIT_COMMON`（普通仓库） | 标准 4 个选项 | 没有要清理的 worktree |
| `GIT_DIR != GIT_COMMON`，具名分支 | 标准 4 个选项 | 基于来源（见步骤 6） |
| `GIT_DIR != GIT_COMMON`，分离 HEAD | 缩减为 3 个选项（不含合并） | 不清理（由外部管理） |

### 步骤 3：确定基线分支

```bash
# Try common base branches
git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null
```

或询问：「这个分支是从 main 分出来的——对吗？」

### 步骤 4：呈现选项

**普通仓库和具名分支 worktree——精确呈现这 4 个选项：**

```
Implementation complete. What would you like to do?

1. Merge back to <base-branch> locally
2. Push and create a Pull Request
3. Keep the branch as-is (I'll handle it later)
4. Discard this work

Which option?
```

**分离 HEAD——精确呈现这 3 个选项：**

```
Implementation complete. You're on a detached HEAD (externally managed workspace).

1. Push as new branch and create a Pull Request
2. Keep as-is (I'll handle it later)
3. Discard this work

Which option?
```

**不要添加解释**——选项保持简短。

### 步骤 5：执行选择

#### 选项 1：本地合并

```bash
# Get main repo root for CWD safety
MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
cd "$MAIN_ROOT"

# Merge first — verify success before removing anything
git checkout <base-branch>
git pull
git merge <feature-branch>

# Verify tests on merged result
<test command>

# Only after merge succeeds: cleanup worktree (Step 6), then delete branch
```

然后：清理 worktree（步骤 6），再删除分支：

```bash
git branch -d <feature-branch>
```

#### 选项 2：推送并创建 PR

```bash
# Push branch
git push -u origin <feature-branch>
```

**不要清理 worktree**——用户需要它保持可用，以便根据 PR 反馈迭代。

#### 选项 3：保持原样

报告：「保留分支 <name>。Worktree 保留在 <path>。」

**不要清理 worktree。**

#### 选项 4：丢弃

**先确认：**
```
This will permanently delete:
- Branch <name>
- All commits: <commit-list>
- Worktree at <path>

Type 'discard' to confirm.
```

等待精确确认。

如果已确认：
```bash
MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
cd "$MAIN_ROOT"
```

然后：清理 worktree（步骤 6），再强制删除分支：
```bash
git branch -D <feature-branch>
```

### 步骤 6：清理工作区

**只对选项 1 和 4 运行。** 选项 2 和 3 始终保留 worktree。

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
WORKTREE_PATH=$(git rev-parse --show-toplevel)
```

**如果 `GIT_DIR == GIT_COMMON`：** 普通仓库，没有要清理的 worktree。完成。

**如果 worktree 路径位于 `.worktrees/` 或 `worktrees/` 之下：** 这个 worktree 由 Superpowers 创建——清理归我们。

```bash
MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
cd "$MAIN_ROOT"
git worktree remove "$WORKTREE_PATH"
git worktree prune  # Self-healing: clean up any stale registrations
```

**否则：** 宿主环境（harness）拥有这个工作区。不要移除它。如果你的平台提供退出工作区的工具，就用它。否则，把工作区留在原地。

## 速查

| 选项 | 合并 | 推送 | 保留 Worktree | 清理分支 |
|--------|-------|------|---------------|----------------|
| 1. 本地合并 | 是 | - | - | 是 |
| 2. 创建 PR | - | 是 | 是 | - |
| 3. 保持原样 | - | - | 是 | - |
| 4. 丢弃 | - | - | - | 是（强制） |

## 常见错误

**跳过测试核验**
- **问题：** 合并损坏的代码，创建会失败的 PR
- **修复：** 在提供选项之前始终核验测试

**开放式问题**
- **问题：** 「接下来我该做什么？」含糊不清
- **修复：** 精确呈现 4 个结构化选项（分离 HEAD 则为 3 个）

**为选项 2 清理 worktree**
- **问题：** 移除用户在 PR 迭代中需要的 worktree
- **修复：** 只为选项 1 和 4 清理

**在移除 worktree 之前删除分支**
- **问题：** `git branch -d` 失败，因为 worktree 仍引用该分支
- **修复：** 先合并，移除 worktree，再删除分支

**从 worktree 内部运行 git worktree remove**
- **问题：** 当 CWD 位于将被移除的 worktree 内部时，命令会静默失败
- **修复：** 在 `git worktree remove` 之前始终 `cd` 到主仓库根目录

**清理 harness 拥有的 worktree**
- **问题：** 移除 harness 创建的 worktree 会造成幽灵状态
- **修复：** 只清理 `.worktrees/` 或 `worktrees/` 之下的 worktree

**丢弃时没有确认**
- **问题：** 意外删除工作
- **修复：** 要求键入 "discard" 确认

## 危险信号

**绝不：**
- 在测试失败时继续
- 未在结果上核验测试就合并
- 未经确认就删除工作
- 没有明确请求就强制推送
- 在确认合并成功之前移除 worktree
- 清理不是你创建的 worktree（来源检查）
- 从 worktree 内部运行 `git worktree remove`

**始终：**
- 在提供选项之前核验测试
- 在呈现菜单之前检测环境
- 精确呈现 4 个选项（分离 HEAD 则为 3 个）
- 对选项 4 取得键入确认
- 只为选项 1 和 4 清理 worktree
- 在移除 worktree 之前 `cd` 到主仓库根目录
- 移除之后运行 `git worktree prune`
