---
name: setup-s-instructions
description: "「/setup-s-instructions」「初始化全局技能提示词」「修复全局技能规则」。显式初始化或检查 Codex、Claude Code、Cursor 的全局技能指令，保留已有配置。Use when the user explicitly requests global skill instruction setup, checking, or repair for Codex, Claude Code, or Cursor."
disable-model-invocation: true
---
# 初始化全局技能提示词

只在用户明确调用本技能或要求初始化、修复全局提示词时写入。普通任务缺失配置时只提醒，见[日常自检](references/daily-check.md)。模型选择由 setup-s-models 负责。

## 1. 确认当前宿主并检查

根据当前会话工具和已加载配置识别 Codex、Claude Code 或 Cursor；无法确定才询问。只处理当前宿主，不顺便配置其他软件。

用可用的 Python 3 运行本技能目录下的脚本，先不传 `--apply`：

```sh
python scripts/global_instructions.py --host codex
python scripts/global_instructions.py --host claude-code
python scripts/global_instructions.py --host cursor
```

从本技能目录运行，或换为脚本绝对路径。默认只读。退出码 0 表示已配置，2 表示缺失或过期，3 表示 Cursor 需要核验 User Rules，1 表示错误。不要把这些状态全当作执行失败。无需安装依赖。

- Codex：使用实际 `CODEX_HOME`，默认 `~/.codex`；非空 `AGENTS.override.md` 优先，否则 `AGENTS.md`。
- Claude Code：使用实际 `CLAUDE_CONFIG_DIR` 下的 `CLAUDE.md`，默认 `~/.claude/CLAUDE.md`。
- Cursor：全局配置使用 Settings → Rules → User Rules，不假定存在全局规则文件，也不写内部数据库。

## 2. 初始化或更新

用户要求检查时到此为止。用户要求初始化或修复时：

- Codex、Claude Code：对同一宿主追加 `--apply`。只维护 s-atlas 标记块；已有完整同款提示词不重复添加，用户其他内容保持不变。修改已有文件前保留首份 `.s-atlas.bak`。标记残缺、编码无法读取或符号链接等异常时停止写入并说明实际问题，不整文件覆盖。
- Cursor：读取脚本返回的 `block`。若当前工具能读取和编辑真正的全局 User Rules，保留原规则、按相同标记替换或追加，再读取核验；已有相同块则不写。标记残缺时停止。没有可用的设置编辑能力时，给出完整 block 和 User Rules 设置位置供用户粘贴，明确说明“尚未配置”，不能把生成文本当成完成。不要写 `.cursor/rules` 来冒充全局配置。

提示词正文取自插件根目录的 [AGENTS-snippet.md](../../AGENTS-snippet.md)，不在本技能另存副本。脚本也识别 [AGENTS.md](../../AGENTS.md) 的完整规则正文，以及省略两条专利路由的既有完整版本；空白、换行和行内代码反引号不影响识别。命中时保留原文，不追加标记块或创建备份。其他自定义改写不做关键词式猜测；若已有语义等价的用户规则但脚本未识别，先比较内容，避免追加重复或冲突指令；需要调整用户自己写的规则时说明冲突再处理。

## 3. 核验和报告

Codex、Claude Code 再执行一次不带 `--apply` 的检查，预期 configured；第二次 apply 应 changed=false。Cursor 以真实 User Rules 回读为准，无法回读则标记待核验。

报告宿主、目标位置、是否修改、备份位置（若创建）、未完成项。提示新会话会加载全局规则；不保证当前会话立即重载。不提交或公开用户的全局配置内容。
