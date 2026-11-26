---
name: wukong-init
description: "「/wukong-init」「初始化 s」「新机器配置 s」「初始化全局技能提示词」「修复全局技能规则」。显式初始化或检查 Codex、Claude Code、Cursor、WorkBuddy 的全局技能指令，保留已有配置，写入前确认。Use when the user explicitly asks to set up, check, or repair wukong's global skill instructions on a host."
disable-model-invocation: true
---
本会话首次使用本库技能时，按[全局提示词自检](references/daily-check.md)只读检查一次。
## 运行环境适配

涉及宿主工具或子代理时，按需阅读[宿主适配](../../HOSTS.md)。

# 初始化 wukong

只在用户明确调用本技能或要求初始化、修复全局提示词时写入。普通任务缺失配置时只提醒，见[日常自检](references/daily-check.md)。本技能不配置模型：子代理默认继承父会话模型。

## 1. 确认当前宿主并检查

需要询问宿主或确认写入时，按[初始化时的交互提问](references/interactive-confirmation.md)选择当前模式可用的工具。异步提问后等用户明确回复，不把工具返回当作确认。

根据当前会话工具和已加载配置识别 Codex、Claude Code、Cursor 或 WorkBuddy；无法确定才询问。只处理当前宿主，不顺便配置其他软件。DeepSeek Harness（`dsh`）和 Hermes 没有全局提示词脚本：告诉用户本技能不适用，直接汇总。

用可用的 Python 3 运行本技能目录下的脚本，先不传 `--apply`：

```sh
python scripts/global_instructions.py --host codex
python scripts/global_instructions.py --host claude-code
python scripts/global_instructions.py --host cursor
python scripts/global_instructions.py --host workbuddy
```

从本技能目录运行，或换为脚本绝对路径。默认只读。退出码 0 表示已配置，2 表示缺失或过期，3 表示 Cursor 需要核验 User Rules，1 表示错误。不要把这些状态全当作执行失败。无需安装依赖。

- Codex：使用实际 `CODEX_HOME`，默认 `~/.codex`；非空 `AGENTS.override.md` 优先，否则 `AGENTS.md`。
- Claude Code：使用实际 `CLAUDE_CONFIG_DIR` 下的 `CLAUDE.md`，默认 `~/.claude/CLAUDE.md`。
- WorkBuddy：使用官方兼容的用户级 `~/.codebuddy/CODEBUDDY.md`，不写原生记忆或项目规则来冒充全局指令。
- Cursor：全局配置使用 Settings → Rules → User Rules，不假定存在全局规则文件，也不写内部数据库。

## 2. 初始化或更新

用户只要求检查时到此为止，跳到第 4 节汇总。状态为 `configured` 时说明已是最新，不写入。`missing` 或 `outdated` 时先说明将改的位置和备份方式，用户明确同意后：

- Codex、Claude Code、WorkBuddy：对同一宿主追加 `--apply`。替换 wukong 标记块；完整匹配的已知无标记旧规则原位迁移为当前版本的标记块，不在末尾叠加新规则。用户其他内容保持不变。修改已有文件前保留首份 `.wukong.bak`。1.0.6 及更早写入的 `<!-- s-atlas:instructions:start -->` 与 `<!-- s-atlas:instructions:end -->` 视为同一段，应用时整段换成新标记。已有的 `.s-atlas.bak` 保留不动。标记残缺、编码无法读取或符号链接等异常时停止写入并说明实际问题，不整文件覆盖。
- Cursor：读取脚本返回的 `block`。若当前工具能读取和编辑真正的全局 User Rules，保留原规则、按相同标记替换或追加，再读取核验；已有相同块则不写。标记残缺时停止。没有可用的设置编辑能力时，给出完整 block 和 User Rules 设置位置供用户粘贴，明确说明“尚未配置”，不能把生成文本当成完成。不要写 `.cursor/rules` 来冒充全局配置。

用户拒绝或跳过时记下“提示词未配置”，直接汇总。

提示词正文每次从当前插件的 [AGENTS.md](../../AGENTS.md) 读取，版本取自同一插件的 `plugin.json`，不从远端或其他缓存版本拼接。标记块同时记录版本和当前完整规则；版本或正文不同即为 `outdated`。检查返回的 `version` 表示本次期望版本，只有 `configured` 才表示目标已同步。

[短规则](../../AGENTS-snippet.md)、[冻结的旧短规则](references/short-instructions-v1.txt) 和已登记的旧版完整规则（[v1](references/full-instructions-v1.txt)、[v2](references/full-instructions-v2.txt)、[v3](references/full-instructions-v3.txt)、[v4](references/full-instructions-v4.txt)、[v5](references/full-instructions-v5.txt)、[v6](references/full-instructions-v6.txt)、[v7](references/full-instructions-v7.txt)、[v8](references/full-instructions-v8.txt)、[v9](references/full-instructions-v9.txt)、[v10](references/full-instructions-v10.txt)）用于识别迁移来源，包含省略两条专利路由的版本。历史快照保留当时的技能名，不随品牌改名更新。识别允许空白、换行和行内代码反引号差异，但要求完整规则独占对应行。检查时报告 `outdated`，显式 `--apply` 后原位替换；保留块外内容、BOM、换行风格和首份备份。出现多个无标记规则块时停止写入，避免猜测该改哪一份。

上一代 `<!-- s-wukong:instructions:start -->` / `<!-- s-wukong:instructions:end -->` 标记也会原位迁移为 `wukong` 标记；已有的 `.s-wukong.bak` 和 `.s-atlas.bak` 均保留不动。

其他自定义改写不做关键词式替换。遇到相似但无法完整识别的规则，先比较冲突和归属，不把它当作最新版或直接叠加。Cursor 同样使用脚本返回的当前版本 block；只能通过真实 User Rules 读取和更新能力完成迁移，没有能力时交付替换内容并标记待操作。

个人学习层另有一对标记 `<!-- wukong:personal:start -->` / `<!-- wukong:personal:end -->`，只由 `reflect --me` 等个人模式写入，放在库块之后。本技能更新库块时不读、不改个人块；个人块写入也不碰库块。

以前由已删除的 setup-s-models 写入的 `# s 模型配置` 标记段不再被任何技能读取。发现时告诉用户可以手动删掉，不自动改动。

## 3. Codex 钩子升级

Codex 安装插件不会自动迁移用户级 `hooks.json`，已有全局规则也要查。`global_instructions.py --host codex` 会在 `hooks` 字段附带只读检查，也可单独运行本目录的 `scripts/codex_hooks.py`；它沿用 `CODEX_HOME`，也支持 `--codex-home`。这项结果与全局提示词状态分开报告，不能用提示词 `configured` 代替钩子检查。全局提示词的 `--apply` 不会顺带迁移钩子。

- `outdated`：展示 `changes`；仅在用户授权修复钩子后加 `--apply`。迁移只改已知 Python 调用中指向 `s-atlas`、`s-wukong` 或旧 `wukong` 缓存的内置脚本路径，目标取当前脚本所属插件；保留其他钩子、元数据、BOM、换行风格和首份 `hooks.json.wukong.bak`，第二次运行不再写入。
- `missing`：不自动安装钩子。需要启用时按 [Codex 手动配置](../prompt-sharpen/references/hook.md#codex-手动配置) 给出完整预览，获得安装授权再添加。
- `manual_review`、`error`：不写文件，报告自定义命令、无效 JSON 或符号链接等实际问题；不做全文件字符串替换。

迁移不会修改 Codex 的 `trusted_hash` 或代替用户批准。写入后检查路径，再提示在新会话 `/hooks` 核对并批准变更。只有看到宿主真实触发及日志新增，才能报告“自动记录已生效”；手动脚本测试要单独说明，不能冒充宿主触发。

## 4. 核验和汇总

Codex、Claude Code、WorkBuddy 再执行一次不带 `--apply` 的检查，预期 `configured`；第二次 apply 应 changed=false。Cursor 以真实 User Rules 回读为准，无法回读则标记待核验。

报告：

- 宿主与当前插件版本。
- 提示词：状态、位置、是否修改、备份位置（若创建）。
- Codex 钩子：检查状态、迁移与备份位置，以及是否仍需宿主批准或真实事件验证。
- 未完成项，以及提示“新会话才会加载全局规则”，不保证当前会话立即重载。

任一步失败、被拒绝或被跳过，就停下报告哪一项已完成、哪一项未完成，不回滚已完成的步骤。不提交或公开用户的全局配置内容。
