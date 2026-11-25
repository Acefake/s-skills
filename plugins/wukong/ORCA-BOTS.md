# Orca bot 创建流程

`orca-bot-*` 技能共用这份流程。它们只调用 Orca 自带的命令行，不改 Orca 安装目录，也不碰 bot home 里由 Orca 写的 `AGENTS.md`、`CLAUDE.md`、`bot.json`。bot 只能由主人在 Orca 里按下 Create bot 创建。代理能做的是提议：弹出一张卡片，或者把建议写成主人照着填的步骤。

## 1. 找到命令行

先试 `orca bot list`。找不到 `orca` 时，Windows 用 `"$LOCALAPPDATA/Programs/orca/resources/bin/orca.exe"`，其他系统在 Orca 安装目录的 `resources/bin` 下找 `orca`。命令连不上 Orca 时，请用户先打开 Orca 再重试，然后停下。

## 2. 查有没有现成的

看 `orca bot list` 的输出：

- 已有同名 bot，或者现有 bot 的用途已经覆盖这件事：不再新建，告诉用户用哪个，跳到第 5 步。
- 名字被占、用途不同：在技能给的名字后面加项目名，例如 `pr-reviewer-web`。

## 3. 按所在位置选一条路提议

技能正文给出模板 id 和 `name`、`purpose`、`watches`、`does`、`reports`。下面称它们为“设定”。

**A. 当前就在某个 bot 的聊天里**（环境变量 `ORCA_AGENT_SESSION_ID` 有值，且 `orca bot chats` 能列出当前聊天）：

```bash
orca bot create --offer --template <模板 id> --name <name> \
  --purpose "<purpose>" --watches "<watches>" --does "<does>" --reports "<reports>"
```

要接手已有工作区，加 `--worktree name:<工作区名>`，名字从 `orca worktree ps` 里取，可以重复加。输出里有 `Your owner now sees a card` 时，告诉用户去聊天里按 Create bot。

**B. 不在 bot 聊天里，但已经有别的 bot**：请那个 bot 替你提议。Windows 上用 `orca.exe`，`orca.cmd` 不转发 `orchestration send`：

```bash
orca orchestration send --to bot:<已有 bot 名> --type handoff \
  --subject "提议新 bot：<name>" \
  --body "我的主人要一个新 bot。请原样运行下面这条命令，只弹卡片，不做别的：<第 3 步 A 的完整命令>"
```

然后告诉用户去那个 bot 的聊天里按 Create bot。

**C. 一个 bot 都没有**：命令行建不了，把步骤交给用户：

1. 在 Orca 侧栏打开 Bots，新建 bot，选模板「<模板英文名>」。
2. 按 Edit，把名字和用途换成技能给的设定（见下面的代码块），再按 Create bot。

最后把设定放进一个代码块，方便复制。

## 4. 建好以后

用户说建好了，再跑一次 `orca bot list`，确认新 bot 在列表里。bot 第一次运行时会自己问要盯哪些仓库，并在缺连接时弹出 GitHub、Linear 的 Connect 卡片。不要替它回答，也不要替它改 `SOUL.md`。技能列出的连接，提醒用户在那张卡片上点连接。

## 5. 放入 bot 技能

每个 `orca-bot-*` 技能的 `assets/bot-skill.md` 是给 bot 自己用的技能。按 Orca 的约定，它放在 bot home 的 `skills/<技能名>/SKILL.md`，Orca 下次开聊天时会自动挂上。

1. 找 bot home：在 `~/.orca/bots/*/bot.json` 里找 `"name"` 等于 bot 名的那一个，它所在的文件夹就是。找不到时停下，告诉用户。
2. 目标文件不存在：把 `assets/bot-skill.md` 原样复制过去，文件名改成 `SKILL.md`。
3. 目标文件已存在：先比较内容。相同就跳过，不同就把差异给用户看，等他决定，不直接覆盖。
4. 告诉用户已放入哪个文件，下一次新开的聊天才会生效。

## 交付时说明

- 走了哪条路（A、B 或 C），卡片在哪个聊天里。
- 新 bot 叫什么，第一次运行前还要用户做什么（按 Create bot、点连接、回答仓库）。
- bot 技能放进了哪个文件，或者为什么没放。
