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

- Codex、Claude Code：对同一宿主追加 `--apply`。替换 s-atlas 标记块；完整匹配的已知无标记旧规则原位迁移为当前版本的标记块，不在末尾叠加新规则。用户其他内容保持不变。修改已有文件前保留首份 `.s-atlas.bak`。标记残缺、编码无法读取或符号链接等异常时停止写入并说明实际问题，不整文件覆盖。
- Cursor：读取脚本返回的 `block`。若当前工具能读取和编辑真正的全局 User Rules，保留原规则、按相同标记替换或追加，再读取核验；已有相同块则不写。标记残缺时停止。没有可用的设置编辑能力时，给出完整 block 和 User Rules 设置位置供用户粘贴，明确说明“尚未配置”，不能把生成文本当成完成。不要写 `.cursor/rules` 来冒充全局配置。

提示词正文每次从当前插件的 [AGENTS.md](../../AGENTS.md) 读取，版本取自同一插件的 `plugin.json`，不从远端或其他缓存版本拼接。标记块同时记录版本和当前完整规则；版本或正文不同即为 `outdated`。检查返回的 `version` 表示本次期望版本，只有 `configured` 才表示目标已同步。

[短规则](../../AGENTS-snippet.md) 和已登记的旧版完整规则（[v1](references/full-instructions-v1.txt)、[v2](references/full-instructions-v2.txt)、[v3](references/full-instructions-v3.txt)、[v4](references/full-instructions-v4.txt)） 仅用于识别迁移来源，包含省略两条专利路由的版本。识别允许空白、换行和行内代码反引号差异，但要求完整规则独占对应行。检查时报告 `outdated`，显式 `--apply` 后原位替换；保留块外内容、BOM、换行风格和首份备份。出现多个无标记规则块时停止写入，避免猜测该改哪一份。

其他自定义改写不做关键词式替换。遇到相似但无法完整识别的规则，先比较冲突和归属，不把它当作最新版或直接叠加。Cursor 同样使用脚本返回的当前版本 block；只能通过真实 User Rules 读取和更新能力完成迁移，没有能力时交付替换内容并标记待操作。

## 3. 核验和报告

Codex、Claude Code 再执行一次不带 `--apply` 的检查，预期 configured；第二次 apply 应 changed=false。Cursor 以真实 User Rules 回读为准，无法回读则标记待核验。

报告宿主、当前插件版本、目标位置、是否修改、备份位置（若创建）、未完成项。提示新会话会加载全局规则；不保证当前会话立即重载。不提交或公开用户的全局配置内容。
