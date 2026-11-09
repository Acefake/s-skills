---
name: release
description: "「发版」「发布新版本」「创建 Release」「打 tag」「写发版说明」「/release」。按插件清单里的版本打 tag，写只含新增、改动、修复的发版说明，创建 GitHub Release。只在点名时用。Use when the user explicitly asks to publish a release: tag the manifest version and create a GitHub Release whose notes list only what was added, changed and fixed."
disable-model-invocation: true
---

本会话首次使用本库技能时，按[全局提示词自检](../setup-s-instructions/references/daily-check.md)只读检查一次。
## 运行环境适配

涉及宿主工具、模型配置或子代理时，按需阅读[宿主适配](../../HOSTS.md)。

# 发版

只在用户点名发版时运行。点名发版就是授权推送 tag 和创建 Release，不授权改版本号以外的代码，也不授权改写历史。句子按 `technical-writing`。

## 1. 确认可以发

先看 `git status`、当前分支和远端：

- 工作区有未提交的内容，或不在默认分支：停下报告，不替用户提交。要提交按 `commit-pr`。
- `git fetch origin` 后，本地 HEAD 必须和 `origin/<默认分支>` 是同一个提交。本地领先或落后都停下：tag 会把它指向的提交一起推上去，推错了没有恢复办法。
- 版本号取插件清单里的 `version`（本库是 `plugins/<插件>/plugin.json`，和 `plugin-versions.lock.json` 一致）。用户没要求时不改它。清单还没升版本而内容有变，先问用户，再按仓库的升版本脚本做。
- 目标 tag 已存在，或版本号比已有 tag 低（用 `git tag --sort=-v:refname` 看最新的）：停下问用户，不覆盖，不强制推送 tag。内容和最近的 tag 相比没有变化（`git diff <上一个 tag> --stat` 为空）时也停下。
- 跑仓库自带的检查（本库是 `scripts/check_marketplace.py`），没过不发。测试强度按 `s-router` 验证分档，发版属第 3 档；同一提交已经跑过的结果直接引用。

## 2. 写发版说明

范围是上一个 tag 到 HEAD 的提交（`git log <上一个 tag>..HEAD`），必要时看 diff。没有上一个 tag（首次发布）时，按当前内容写「新增」。

只写三栏，空栏整栏删掉：

- **新增**：用户能用到的新能力。
- **改动**：已有行为变了什么。
- **修复**：原来哪里不对，现在怎样。

规则：

- 每条一句话，写用户能看到的变化，不写过程。
- 不写 SHA、PR 号、文件清单、内部重构和测试，除非它改变了用户能看到的行为。
- 不用「优化」「完善」「提升」这类说不出具体变化的词。
- 提交说明和实际 diff 对不上时，以 diff 为准。
- 不确定归哪一栏，或不确定对用户有没有影响的条目，先问用户，不猜。

说明存成临时文件，不放进仓库。

## 3. 创建 tag 和 Release

推 tag 之前，把版本、目标提交的短 SHA 和说明全文展示一次。说明里有拿不准的条目才停下问；用户点名发版时，其余情况直接继续。已开启 immutable releases 的仓库，推出去的 tag 不能再改或删。

```bash
git tag -a v<版本> -m "<插件> <版本>"
git push origin v<版本>
gh release create v<版本> --title "<插件> <版本>" --notes-file <说明文件> --verify-tag
```

标题用「插件名 版本号」，例如 `s-wukong 1.0.0`。预发布版本加 `--prerelease`。tag 推送或 Release 创建失败时停下报告，不重试覆盖，不删了重来；tag 已推上去而 Release 没建成，补建 Release 即可。

没有 `gh` 或没有写权限时，把说明和上面的命令交给用户，不换别的发布方式。

## 4. 核对并交付

`gh release view v<版本>` 看说明正文；`git ls-remote --tags origin 'v<版本>^{}'` 取 tag 指向的提交，和 `git rev-parse HEAD` 比较（附注 tag 要看 `^{}` 那一行，不带它得到的是 tag 对象的 SHA）。把 Release 的 URL 给用户，并提醒：已安装的用户要更新才会拿到新版（Claude Code：`claude plugin marketplace update <市场>`，再 `claude plugin update <插件>@<市场>`）。

## 边界

- 不决定版本号怎么升，不改代码来让检查变绿。
- 不删除已有的 Release 或 tag。需要删时，用户要点名对象。
- 推送分支、开 PR、合并不在这里，那是 `commit-pr` 和 `finishing-a-development-branch`。
- 不把某个聊天软件的按钮或菜单写进步骤。

## 宿主适配

步骤在 Codex、Claude Code、Cursor、WorkBuddy 里相同，都用本机的 git 和 `gh`。某个软件没有终端或没有 `gh` 时，说明缺了哪一步，把说明和命令写出来交给用户。

Codex、Claude Code、Cursor、WorkBuddy 的工具和配置见[宿主适配](../../HOSTS.md)；按当前宿主读取对应参考。
