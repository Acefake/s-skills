---
name: orca-bots
description: "「用 Orca 建一套开发 bot」「帮我建几个 Orca bot」「建个审 PR 的 Orca bot」。一次提议多个开发 bot：PR 审查、Bug 排查、CI 分诊、依赖升级、发版检查，都用 Orca 内置模板。Use when the user wants to create one or more Orca bots for development work."
---

本会话首次使用本库技能时，按[全局提示词自检](../setup-s-instructions/references/daily-check.md)只读检查一次。

# 一次建好一组 Orca 开发 bot

这个技能只调用 Orca 自带的命令行。它不改 Orca 安装目录，也不碰 bot home 里由 Orca 写的 `AGENTS.md`、`CLAUDE.md`、`bot.json`。bot 只能由主人在 Orca 里按 Create bot 创建，代理能做的是提议：每个 bot 弹一张卡片，或者给出照着填的步骤。

可建的 bot、各自的设定和配套 bot 技能见[开发 bot 目录](references/catalog.md)。

## 1. 找到命令行

先试 `orca bot list`。找不到 `orca` 时，Windows 用 `"$LOCALAPPDATA/Programs/orca/resources/bin/orca.exe"`，其他系统在 Orca 安装目录的 `resources/bin` 下找。连不上 Orca 时，请用户先打开 Orca，然后停下。

## 2. 定要建哪几个

- 用户点了名的（如“审 PR 和 CI 的”），只建这几个。
- 用户说“一套”“全部”，或者没说具体哪个，就建目录里的全部 5 个。
- 去掉 `orca bot list` 里已经有的：同名，或者现有 bot 的用途已经覆盖。名字被占但用途不同时，在名字后面加项目名，例如 `pr-reviewer-web`。

先用一行告诉用户要建哪几个、跳过哪几个，然后接着做，不用等确认。每张卡片本身就要用户按一下才生效。

## 3. 提议

每个 bot 的提议命令长这样，设定从目录里取：

```bash
orca bot create --offer --template <模板 id> --name <name> \
  --purpose "<purpose>" --watches "<watches>" --does "<does>" --reports "<reports>"
```

按所在位置选一条路：

**A. 当前就在某个 bot 的聊天里**（`ORCA_AGENT_SESSION_ID` 有值，`orca bot chats` 能列出当前聊天）：对每个要建的 bot 依次运行一次提议命令。每次输出 `Your owner now sees a card` 就是一张卡片。某一个失败时，记下原因，继续下一个。

**B. 不在 bot 聊天里，但已经有 bot**：给其中一个发一封邮件，把所有提议命令一次交给它。Windows 上用 `orca.exe`，`orca.cmd` 不转发 `orchestration send`：

```bash
orca orchestration send --to bot:<已有 bot 名> --type handoff \
  --subject "提议 <N> 个新 bot" \
  --body "我的主人要这几个新 bot。请依次原样运行下面每条命令，只弹卡片，不做别的：
<命令 1>
<命令 2>
..."
```

**C. 一个 bot 都没有**：命令行建不了第一个。

1. 让用户在 Orca 侧栏打开 Bots，新建 bot，选列表里第一个 bot 的模板，按 Edit 换成中文设定，再按 Create bot。设定放进代码块，方便复制。
2. 用户说建好后，用 `orca bot list` 确认它在，然后对剩下的 bot 走 B，请这个新 bot 代为提议。

## 4. 建好以后

用户说卡片都按过了，再跑一次 `orca bot list`，核对每个 bot 是否都在。没按的列出来。

每个新 bot 第一次运行时，会自己问要盯哪些仓库，缺连接时还会弹出 GitHub、Linear 的 Connect 卡片。不要替它回答，也不要替它改 `SOUL.md`。把目录里每个 bot 的“提醒用户”转告给用户。

## 5. 放入 bot 技能

目录里每个 bot 都配了一份 bot 技能，放在 `assets/` 下。按 Orca 的约定，它要放到 bot home 的 `skills/<技能名>/SKILL.md`，Orca 下次开聊天时会自动挂上。对每个已建好的 bot：

1. 找 bot home：在 `~/.orca/bots/*/bot.json` 里找 `"name"` 等于 bot 名的那个，它所在的文件夹就是。找不到就记下，继续下一个。
2. 目标文件不存在：把 asset 原样复制过去，文件名改成 `SKILL.md`。
3. 目标文件已存在：先比较。相同就跳过；不同就把差异给用户看，等用户决定，不直接覆盖。

## 交付时说明

- 走了哪条路，卡片在哪个聊天里。
- 每个 bot：已建好、等按卡片，还是跳过（写原因）。
- 每个 bot 第一次运行前还要用户做什么：按 Create bot、点连接、回答仓库。
- bot 技能放进了哪些文件，哪些没放、为什么。
