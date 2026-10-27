# 贴进全局指令的短规则

把下面这段贴进 Claude Code 的 `~/.claude/CLAUDE.md`、Codex 的 `~/.codex/AGENTS.md`、OpenCode 的 `~/.config/opencode/AGENTS.md`，或项目根的 `AGENTS.md`。Cursor 做成一条 Always 规则。Hermes 追加到 `~/.hermes/SOUL.md`。要按任务查表，用同目录的 [AGENTS.md](AGENTS.md)。

```text
收到任务后，在读文件、跑命令、提问或作答之前，先看当前可用的技能，用对得上的那一个。拿不准该用哪个，先用 s-router。只改文案、注释、样式数值或配置值时直接改，不跑测试；其他改动测试跑多少按 s-router 的「验证分档」，跑过的不重跑。
```
