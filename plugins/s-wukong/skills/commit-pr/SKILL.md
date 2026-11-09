---
name: commit-pr
description: "「提交」「帮我 commit」「开个 PR」「写提交说明」。看 diff，写 conventional commit，需要时推送并开 PR。分支怎么集成还没定，用 finishing-a-development-branch。Use when writing a commit message, making a commit, or opening a pull request."
---

本会话首次使用本库技能时，按[全局提示词自检](../setup-s-instructions/references/daily-check.md)只读检查一次。
## 运行环境适配

涉及宿主工具、模型配置或子代理时，按需阅读[宿主适配](../../HOSTS.md)。


# 提交并开 PR

这个技能做两件事：写提交说明，以及在用户要开 PR 时写标题和正文并推上去。

实现做完、测试过了，但还没选定本地合并、开 PR、留着还是丢掉时，用 `finishing-a-development-branch`。不要在这里替它做那个选择，也不要重复它的四项菜单。用户已经点名要提交或开 PR，才从下面开始。

句子按 `technical-writing` 写。这里不重写那套写作规则。处于 `s-mode` 时，PR 正文的分节以那份 opening-a-pr playbook 为准，本技能不另写一套分节。

## 1. 看状态和 diff

在写说明之前先看：

```bash
git status
git diff
git diff --staged
git log -8 --oneline
```

只提交这次任务相关的文件。不要带上密钥、本机配置、或 diff 里不属于这次改动的文件。近期提交的语言和格式是默认。这个仓库的说明常用中文，就用中文。别的仓库跟它自己的近期提交走。

用户没要求执行提交时，只给出说明草稿，不运行 `git commit`。

## 2. 提交说明

用 Conventional Commits：

```text
type(scope): subject
```

`type` 用 `feat`、`fix`、`docs`、`refactor`、`test`、`chore`、`perf` 之一。`scope` 是区域，有真实范围就写。subject 用祈使句，短，不加句号。能点出一个真正承载改动的名字时就点出它。

正文写为什么，不写文件清单。标题已经说过的不要再重复。一次提交只装一件可以单独说清的事。混在一起的改动拆开。

```bash
git add <paths>
git commit -m "$(cat <<'EOF'
type(scope): subject

为什么要改。
EOF
)"
```

提交失败就看钩子的输出，修完再提交。不要用 `--no-verify` 跳过，除非用户明确要求。

## 3. 推送并开 PR

用户要开 PR，或明确说推上去时才推送。先确认当前分支不是受保护的主干。没有上游时：

```bash
git push -u origin HEAD
```

PR 标题沿用提交说明的 `type(scope): subject`，不加句号。正文给一个没看过对话的审查者：为什么改、改了什么、怎么证明它能用。短句。不贴大段日志，不贴无关的 SHA。有仓库的 PR 模板就按模板填，没有就用这三块，空的一块删掉：

```markdown
## 为什么

## 改了什么

## 怎么验证
```

用当前环境里可用的 PR 入口。有内置的创建 PR 工具就用它，并把它标成可以审查，不要停在草稿。没有内置工具、仓库在 GitHub 上时：

```bash
gh pr create --title "type(scope): subject" --body "$(cat <<'EOF'
## 为什么

## 改了什么

## 怎么验证
EOF
)"
```

开完把 PR 的 URL 给用户。开 PR 本身不等于去盯检查或去合并。

## 边界

- 不决定合并、保留还是丢弃。那是 `finishing-a-development-branch`。
- 不改产品代码来让检查变绿。
- 不把某个聊天软件的按钮或菜单写进步骤。

## 宿主适配

步骤在 Codex、Claude Code、Cursor、WorkBuddy 里相同。都用本机的 git。某个软件没有终端或没有 `gh` 时，说明缺了哪一步，把标题和正文写出来交给用户，不要换成那个软件自己的一套说法。

Codex、Claude Code、Cursor、WorkBuddy 的工具和配置见[宿主适配](../../HOSTS.md)；按当前宿主读取对应参考。
