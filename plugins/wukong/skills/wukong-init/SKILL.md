---
name: wukong-init
description: "「/wukong-init」「初始化 s」「新机器配置 s」「初始化全局技能提示词」「修复全局技能规则」「配置子代理模型」。显式初始化或检查 Codex、Claude Code、Antigravity 的全局技能指令，并按宿主可用模型匹配检索、规划、审查、测试四个子代理角色，保留已有配置，写入前确认。Use when the user explicitly asks to set up, check, or repair wukong's global skill instructions or subagent role models on a host."
disable-model-invocation: true
---
本会话首次使用本库技能时，按[全局提示词自检](references/daily-check.md)只读检查一次。
## 运行环境适配

涉及宿主工具或子代理时，按需阅读[宿主适配](../../HOSTS.md)。

# 初始化 wukong

只在用户明确调用本技能或要求初始化、修复全局提示词时写入。普通任务缺失配置时只提醒，见[日常自检](references/daily-check.md)。全局提示词之后，按宿主可用模型为检索、规划、审查、测试四个子代理角色匹配模型（第 4 节）；其他子代理继承父会话模型。

## 1. 确认当前宿主并检查

需要询问宿主或确认写入时，按[初始化时的交互提问](references/interactive-confirmation.md)选择当前模式可用的工具。异步提问后等用户明确回复，不把工具返回当作确认。

根据当前会话工具和已加载配置识别 Codex、Claude Code 或 Antigravity；无法确定才询问。只处理当前宿主，不顺便配置其他软件。DeepSeek Harness（`dsh`）和 Hermes 没有全局提示词脚本：告诉用户本技能不适用，直接汇总。

用可用的 Python 3 运行本技能目录下的脚本，先不传 `--apply`：

```sh
python scripts/global_instructions.py --host codex
python scripts/global_instructions.py --host claude-code
python scripts/global_instructions.py --host antigravity
```

从本技能目录运行，或换为脚本绝对路径。默认只读。退出码 0 表示已配置，2 表示缺失或过期，1 表示错误。不要把这些状态全当作执行失败。无需安装依赖。

- Codex：使用实际 `CODEX_HOME`，默认 `~/.codex`；非空 `AGENTS.override.md` 优先，否则 `AGENTS.md`。
- Claude Code：使用实际 `CLAUDE_CONFIG_DIR` 下的 `CLAUDE.md`，默认 `~/.claude/CLAUDE.md`。
- Antigravity：启用 `wukong` 插件后自动加载 `rules/AGENTS.md`，脚本返回 `configured`（`bundled_by_plugin: true`），不重复写库块；第 4 节模型块写入 `~/.gemini/config/AGENTS.md`。

## 2. 初始化或更新

用户只要求检查时不写入，第 4 节也只跑 `--show`，再到第 5 节汇总。状态为 `configured` 时说明已是最新，不写入。`missing` 或 `outdated` 时先说明将改的位置和备份方式，用户明确同意后：

- Codex、Claude Code：对同一宿主追加 `--apply`。替换 wukong 标记块；完整匹配的已知无标记旧规则原位迁移为当前版本的标记块，不在末尾叠加新规则。用户其他内容保持不变。修改已有文件前保留首份 `.wukong.bak`。1.0.6 及更早写入的 `<!-- s-atlas:instructions:start -->` 与 `<!-- s-atlas:instructions:end -->` 视为同一段，应用时整段换成新标记。已有的 `.s-atlas.bak` 保留不动。标记残缺、编码无法读取或符号链接等异常时停止写入并说明实际问题，不整文件覆盖。

用户拒绝或跳过时记下“提示词未配置”，问是否仍配置子代理模型，同意才进入第 4 节，否则直接汇总。

提示词正文每次从当前插件的 [AGENTS.md](../../AGENTS.md) 读取，版本取自同一插件的 `plugin.json`，不从远端或其他缓存版本拼接。标记块同时记录版本和当前完整规则；版本或正文不同即为 `outdated`。检查返回的 `version` 表示本次期望版本，只有 `configured` 才表示目标已同步。

[短规则](../../AGENTS-snippet.md)、[冻结的旧短规则](references/short-instructions-v1.txt) 和已登记的旧版完整规则（[v1](references/full-instructions-v1.txt)、[v2](references/full-instructions-v2.txt)、[v3](references/full-instructions-v3.txt)、[v4](references/full-instructions-v4.txt)、[v5](references/full-instructions-v5.txt)、[v6](references/full-instructions-v6.txt)、[v7](references/full-instructions-v7.txt)、[v8](references/full-instructions-v8.txt)、[v9](references/full-instructions-v9.txt)、[v10](references/full-instructions-v10.txt)）用于识别迁移来源，包含省略两条专利路由的版本。历史快照保留当时的技能名，不随品牌改名更新。识别允许空白、换行和行内代码反引号差异，但要求完整规则独占对应行。检查时报告 `outdated`，显式 `--apply` 后原位替换；保留块外内容、BOM、换行风格和首份备份。出现多个无标记规则块时停止写入，避免猜测该改哪一份。

上一代 `<!-- s-wukong:instructions:start -->` / `<!-- s-wukong:instructions:end -->` 标记也会原位迁移为 `wukong` 标记；已有的 `.s-wukong.bak` 和 `.s-atlas.bak` 均保留不动。

其他自定义改写不做关键词式替换。遇到相似但无法完整识别的规则，先比较冲突和归属，不把它当作最新版或直接叠加。

个人学习层另有一对标记 `<!-- wukong:personal:start -->` / `<!-- wukong:personal:end -->`，只由 `reflect --me` 等个人模式写入，放在库块之后。本技能更新库块时不读、不改个人块；个人块写入也不碰库块。

以前由已删除的 setup-s-models 写入的 `# s 模型配置` 标记段不再被任何技能读取。发现时告诉用户可以手动删掉，不自动改动；新的角色模型写在第 4 节的模型块里。

## 3. Codex 钩子升级

Codex 安装插件不会自动迁移用户级 `hooks.json`，已有全局规则也要查。`global_instructions.py --host codex` 会在 `hooks` 字段附带只读检查，也可单独运行本目录的 `scripts/codex_hooks.py`；它沿用 `CODEX_HOME`，也支持 `--codex-home`。这项结果与全局提示词状态分开报告，不能用提示词 `configured` 代替钩子检查。全局提示词的 `--apply` 不会顺带迁移钩子。

- `outdated`：展示 `changes`；仅在用户授权修复钩子后加 `--apply`。迁移只改已知 Python 调用中指向 `s-atlas`、`s-wukong` 或旧 `wukong` 缓存的内置脚本路径，目标取当前脚本所属插件；保留其他钩子、元数据、BOM、换行风格和首份 `hooks.json.wukong.bak`，第二次运行不再写入。
- `missing`：不自动安装钩子。需要启用时按 [Codex 手动配置](../prompt-sharpen/references/hook.md#codex-手动配置) 给出完整预览，获得安装授权再添加。
- `manual_review`、`error`：不写文件，报告自定义命令、无效 JSON 或符号链接等实际问题；不做全文件字符串替换。

迁移不会修改 Codex 的 `trusted_hash` 或代替用户批准。写入后检查路径，再提示在新会话 `/hooks` 核对并批准变更。只有看到宿主真实触发及日志新增，才能报告“自动记录已生效”；手动脚本测试要单独说明，不能冒充宿主触发。

## 4. 子代理模型

四个角色，其他子代理（写代码的实现者等）一律继承父会话模型：

| 角色 | 谁派它 | 匹配原则 | 默认档位 |
|---|---|---|---|
| 检索 | 只读检索派发、`how` 探索、`why` 调查、`prompt-sharpen` 与 `project-memory` 读项目 | 快而便宜 | medium |
| 规划 | `how` 讲解、`why` 综合、`reflect` 判断/发散/综合、`executing-plans` 并行群体作战的方案综合 | 判断力最强 | high |
| 审查 | `requesting-code-review`、`executing-plans` 任务评审与终审、`reflect` 工具视角 | 强，且尽量与父会话不同系列 | high |
| 测试 | 并行群体作战的验证工作者、复现、回归与实测验证 | 快，输出留在子代理里 | medium |

**先查现状。** 运行 `python scripts/models.py --host <宿主> --show`，已有模型块时默认保留，用户要求重配才继续。

**再按宿主匹配。** 只用本会话能证实可派发的模型名：派子代理工具定义里列出的取值、宿主列模型的命令，或用户贴出的名字。不按厂商或型号前缀猜。

| 宿主 | 可用模型从哪来 | 默认匹配 |
|---|---|---|
| Claude Code | `Agent` 工具 `model` 的取值（如 `opus`、`sonnet`、`haiku`） | 检索 `haiku`，规划、审查 `opus`，测试 `sonnet`；没有的取值改用相邻一档 |
| Codex | 账号里真有的模型，见[Codex 参考](../wukong-router/references/codex-tools.md#codex-怎么指定模型) | 规划、审查用最强的，检索、测试用较快的；无法确认名字就写 `继承` |
| Antigravity | `invoke_subagent` 的 `Model` 枚举（`inherit`、`pro`、`flash`、`flash_lite`） | 检索 `flash_lite`（或 `flash`），规划、审查 `pro`，测试 `flash`；无按次档位参数，不写括号 |
| T3 Code | 底层宿主的原生工具；跨提供商委派另按 [T3 编排参考](../wukong-router/references/t3-code-tools.md) | 写底层宿主能派发的名字，不写 T3 目录里的提供商模型 |

只有一个可用模型或无法区分强弱时，四行都写 `继承`，不硬凑分档。

**档位默认不写。** 派发规则按上表的默认档位传；用户想改某个角色时才写成 `模型（档位）`，如 `审查: opus（xhigh）`，取值 `low`、`medium`、`high`、`xhigh`、`max`。模型是 `继承` 但要改档位时写 `继承（high）`。宿主没有档位参数（Antigravity、Hermes）时不写括号。预览表里把每个角色的实际档位一并列出。

**展示后一次确认。** 把整张「角色 → 模型」表贴出来，按[交互提问](references/interactive-confirmation.md)单独请求写入确认；用户改某一行就改后再展示。确认后运行：

```sh
python scripts/models.py --host <宿主> --set 检索=<模型> --set 规划=<模型> --set 审查=<模型> --set 测试=<模型> --apply
```

不带 `--apply` 是只读预览；`--show` 的 `resolved` 给出每个角色实际派发用的模型和档位。脚本把块写在全局提示词库块之后（`<!-- wukong:models:start -->` 到 `<!-- wukong:models:end -->`），保留其他内容和首份 `.wukong.bak`，库块升级不会碰它。

## 5. 核验和汇总

Codex、Claude Code 再执行一次不带 `--apply` 的检查，预期 `configured`；第二次 apply 应 changed=false。Antigravity 库块随插件加载，所有宿主的模型块都用 `--show` 回读。

报告：

- 宿主与当前插件版本。
- 提示词：状态、位置、是否修改、备份位置（若创建）。
- 子代理模型：四个角色的最终取值、写入位置，哪些是 `继承` 及原因。
- Codex 钩子：检查状态、迁移与备份位置，以及是否仍需宿主批准或真实事件验证。
- 未完成项，以及提示“新会话才会加载全局规则”，不保证当前会话立即重载。

任一步失败、被拒绝或被跳过，就停下报告哪一项已完成、哪一项未完成，不回滚已完成的步骤。不提交或公开用户的全局配置内容。
