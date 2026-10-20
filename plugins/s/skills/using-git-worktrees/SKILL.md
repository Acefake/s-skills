---
name: using-git-worktrees
description: "中文：开始需要与当前工作区隔离的功能开发时，或在执行实现计划之前，通过原生工具或 git worktree 回退确保存在隔离工作区。Use when you are starting feature work that must be isolated from the current workspace, or before executing an implementation plan."
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。

本技能译自 Jesse Vincent 的 Superpowers（MIT）。许可证见上一级文件夹的 `LICENSE-superpowers`。

# 使用 Git Worktree

## 概述

确保工作发生在隔离的工作区中。优先使用你所在平台的原生 worktree 工具。只有在没有原生工具时，才回退到手工 git worktree。

**核心原则：** 先检测已有的隔离。然后使用原生工具。然后再回退到 git。绝不与 harness 对抗。

**开始时宣布：** 「我正在使用 using-git-worktrees 技能来建立隔离工作区。」

## 步骤 0：检测已有隔离

**在创建任何东西之前，检查你是否已经处在隔离工作区中。**

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
BRANCH=$(git branch --show-current)
```

**子模块防护：** `GIT_DIR != GIT_COMMON` 在 git 子模块内部同样为真。在得出「已经在 worktree 中」的结论之前，确认你并不在子模块里：

```bash
# If this returns a path, you're in a submodule, not a worktree — treat as normal repo
git rev-parse --show-superproject-working-tree 2>/dev/null
```

**如果 `GIT_DIR != GIT_COMMON`（且不是子模块）：** 你已经在一个链接的 worktree 中。跳到步骤 2（项目设置）。不要再创建另一个 worktree。

按分支状态报告：
- 在分支上：「已在隔离工作区 `<path>`，分支 `<name>`。」
- 分离 HEAD：「已在隔离工作区 `<path>`（分离 HEAD，由外部管理）。收尾时需要创建分支。」

**如果 `GIT_DIR == GIT_COMMON`（或在子模块中）：** 你在普通仓库检出中。

用户是否已经在你的指令里表明了 worktree 偏好？如果没有，在创建 worktree 之前先征得同意：

> 「要我建立一个隔离 worktree 吗？它可以保护你当前的分支不被改动。」

尊重任何已经声明的偏好，不必再问。如果用户拒绝同意，就地工作并跳到步骤 2。

## 步骤 1：创建隔离工作区

**你有两种机制。按此顺序尝试。**

### 1a. 原生 Worktree 工具（首选）

用户已经要求隔离工作区（步骤 0 的同意）。你是否已经有创建 worktree 的办法？它可能是名为 `EnterWorktree`、`WorktreeCreate` 的工具，一条 `/worktree` 命令，或一个 `--worktree` 标志。如果有，就用它，并跳到步骤 2。

原生工具会自动处理目录放置、分支创建和清理。在已有原生工具时使用 `git worktree add`，会产生 harness 看不见、也管不了的幽灵状态。

只有在没有可用的原生 worktree 工具时，才进入步骤 1b。

### 1b. Git Worktree 回退

**仅当步骤 1a 不适用时才使用**——你没有可用的原生 worktree 工具。用 git 手工创建 worktree。

#### 目录选择

按此优先级。用户的明确偏好始终优先于观察到的文件系统状态。

1. **检查你的指令里是否声明了 worktree 目录偏好。** 如果用户已经指定，直接使用，不必询问。

2. **检查是否已有项目本地的 worktree 目录：**
   ```bash
   ls -d .worktrees 2>/dev/null     # Preferred (hidden)
   ls -d worktrees 2>/dev/null      # Alternative
   ```
   如果找到，就用它。如果两者都存在，`.worktrees` 优先。

3. **如果没有其他可用指导**，默认使用项目根目录下的 `.worktrees/`。

#### 安全核验（仅项目本地目录）

**创建 worktree 之前必须核验目录已被忽略：**

```bash
git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/dev/null
```

**如果未被忽略：** 加入 .gitignore，提交该改动，然后继续。

**为何关键：** 防止意外把 worktree 内容提交进仓库。

#### 创建 Worktree

```bash
# Determine path based on chosen location
path="$LOCATION/$BRANCH_NAME"

git worktree add "$path" -b "$BRANCH_NAME"
cd "$path"
```

**沙箱回退：** 如果 `git worktree add` 因权限错误失败（沙箱拒绝），告诉用户沙箱阻止了 worktree 创建，你改为在当前目录工作。然后就地运行设置和基线测试。

## 步骤 2：项目设置

自动检测并运行合适的设置：

```bash
# Node.js
if [ -f package.json ]; then npm install; fi

# Rust
if [ -f Cargo.toml ]; then cargo build; fi

# Python
if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
if [ -f pyproject.toml ]; then poetry install; fi

# Go
if [ -f go.mod ]; then go mod download; fi
```

## 步骤 3：核验干净基线

运行测试，确保工作区从干净状态开始：

```bash
# Use project-appropriate command
npm test / cargo test / pytest / go test ./...
```

**如果测试失败：** 报告失败，询问是继续还是调查。

**如果测试通过：** 报告就绪。

### 报告

```
Worktree ready at <full-path>
Tests passing (<N> tests, 0 failures)
Ready to implement <feature-name>
```

## 速查

| 情形 | 动作 |
|-----------|--------|
| 已在链接的 worktree 中 | 跳过创建（步骤 0） |
| 在子模块中 | 按普通仓库处理（步骤 0 防护） |
| 有原生 worktree 工具 | 使用它（步骤 1a） |
| 没有原生工具 | Git worktree 回退（步骤 1b） |
| 存在 `.worktrees/` | 使用它（核验已被忽略） |
| 存在 `worktrees/` | 使用它（核验已被忽略） |
| 两者都存在 | 使用 `.worktrees/` |
| 两者都不存在 | 检查指令文件，然后默认 `.worktrees/` |
| 目录未被忽略 | 加入 .gitignore 并提交 |
| 创建时出现权限错误 | 沙箱回退，就地工作 |
| 基线期间测试失败 | 报告失败并询问 |
| 没有 package.json/Cargo.toml | 跳过依赖安装 |

## 常见错误

### 与 harness 对抗

- **问题：** 平台已经提供隔离时仍使用 `git worktree add`
- **修复：** 步骤 0 检测已有隔离。步骤 1a 让位于原生工具。

### 跳过检测

- **问题：** 在已有 worktree 内部再创建一个嵌套 worktree
- **修复：** 创建任何东西之前始终先跑步骤 0

### 跳过忽略核验

- **问题：** worktree 内容被跟踪，污染 git status
- **修复：** 创建项目本地 worktree 之前始终使用 `git check-ignore`

### 臆测目录位置

- **问题：** 造成不一致，违反项目约定
- **修复：** 遵循优先级：明确指令 > 已有的项目本地目录 > 默认

### 在测试失败时继续

- **问题：** 无法区分新 bug 与既有问题
- **修复：** 报告失败，取得明确许可后再继续

## 危险信号

**绝不：**
- 当步骤 0 检测到已有隔离时仍创建 worktree
- 在已有原生 worktree 工具时使用 `git worktree add`（例如 `EnterWorktree`）。这是第一大错误——如果你有它，就用它。
- 跳过步骤 1a，直接跳到步骤 1b 的 git 命令
- 在未核验已被忽略的情况下创建 worktree（项目本地）
- 跳过基线测试核验
- 未询问就在测试失败时继续

**始终：**
- 先跑步骤 0 检测
- 优先原生工具，而不是 git 回退
- 遵循目录优先级：明确指令 > 已有的项目本地目录 > 默认
- 对项目本地目录核验已被忽略
- 自动检测并运行项目设置
- 核验干净的测试基线
