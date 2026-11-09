# 手动引导用的短规则

初始化生成的完整规则来自当前插件的 [AGENTS.md](AGENTS.md)，并记录 `plugin.json` 版本。下面的短规则只用于手动引导和旧配置识别，不代表已同步到当前版本。插件更新后执行只读检查；显式初始化或更新会原位迁移已知旧规则。

推荐显式调用 [setup-s-instructions](skills/setup-s-instructions/SKILL.md) 初始化全局提示词。也可手动把下面这段贴进 Codex 的实际 `CODEX_HOME` 下生效的 `AGENTS.override.md` 或 `AGENTS.md`（默认 `~/.codex`）、Claude Code 的实际 `CLAUDE_CONFIG_DIR` 下的 `CLAUDE.md`（默认 `~/.claude/CLAUDE.md`），Cursor 的全局 User Rules，或 WorkBuddy 的兼容文件 `~/.codebuddy/CODEBUDDY.md`。项目约定文件或 Cursor 项目 Always 规则只对项目生效。要按任务查表，用同目录的 [AGENTS.md](AGENTS.md)。

```text
收到任务后，在读文件、跑命令、提问或作答之前，先看当前可用的技能，用对得上的那一个。拿不准该用哪个，先用 s-router。只改文案、注释、样式数值或配置值时直接改，不跑测试；其他改动测试跑多少按 s-router 的「验证分档」，跑过的不重跑。
```
