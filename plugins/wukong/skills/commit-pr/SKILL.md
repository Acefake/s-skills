---
name: commit-pr
description: "「提交」「帮我 commit」「开个 PR」「写提交说明」「做完了怎么合」「开 PR 还是合并」「收尾这个分支」。看 diff，写 conventional commit，需要时推送并开 PR；还没定集成方式时，先核验再给出合并、PR、保留或丢弃的选项。Use when writing a commit message, making a commit, opening a pull request, or deciding how to integrate a finished branch."
---

本会话首次使用本库技能时，按[全局提示词自检](../wukong-init/references/daily-check.md)只读检查一次。
## 运行环境适配

涉及宿主工具或子代理时，按需阅读[宿主适配](../../HOSTS.md)。

# 提交并开 PR

这个技能做两件事：写提交说明，以及在用户要开 PR 时写标题和正文并推上去。

实现做完、测试过了，但还没选定本地合并、开 PR、留着还是丢掉时，先按[分支收尾](references/finishing-branch.md)核验、给出选项并执行所选动作；选了「创建 PR」再回到下面第 3 节。用户已经点名要提交或开 PR，直接从下面开始。

句子按 `technical-writing` 写。这里不重写那套写作规则。PR 正文的分节按仓库已有的 PR 模板；没有模板时写清改了什么、为什么改、怎么验证。

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

- 合并、保留还是丢弃由[分支收尾](references/finishing-branch.md)决定，不在提交步骤里顺手做。
- 不改产品代码来让检查变绿。
- 不把某个聊天软件的按钮或菜单写进步骤。
- 软衔接（不强行打断提交）：如果本次改动影响了架构、目录、术语或规范且项目已有记录，收尾提一句可用 [project-memory](../project-memory/SKILL.md) `sync` 同步；如果本次刚解决过值得复用的踩坑，收尾提一句可用 [reflect](../reflect/SKILL.md) 沉淀。

## 宿主适配

步骤在 Codex、Claude Code、Antigravity 里相同。都用本机的 git。某个软件没有终端或没有 `gh` 时，说明缺了哪一步，把标题和正文写出来交给用户，不要换成那个软件自己的一套说法。

Codex、Claude Code、Antigravity 的工具和配置见[宿主适配](../../HOSTS.md)；按当前宿主读取对应参考。
