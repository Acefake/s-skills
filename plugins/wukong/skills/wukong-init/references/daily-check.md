# 日常全局提示词自检

每个主会话首次使用本库任一技能时，只读检查一次；其他技能复用结果，子智能体跳过。检查不阻塞原任务，不自动调用初始化技能，不写配置。

Claude Code 装了本插件的会话开始钩子时，会话开头的上下文里已有一行「wukong 版本（插件目录）。全局技能提示词……」，那就是检查结果：直接采用，需要提醒时提醒一次，不再重复下面的步骤。没有这一行才自己检查。

1. 以当前加载的插件为来源，读取其 `plugin.json` 版本和 `AGENTS.md` 规则。只有已加载的全局块版本和正文都与当前来源一致，才视为已同步；仅有标题、旧规则或语义近似不能证明是最新版。HTML 标记可能被宿主剥离，此时进入文件检查，不能据此认定缺失。
2. 无法确认时，Codex、Claude Code、WorkBuddy 可用现有 Python 3 运行 `python wukong-init/scripts/global_instructions.py --host codex` 、`--host claude-code` 或 `--host workbuddy`，不带 `--apply`，脚本路径相对本库 skills 目录；不在该目录时换成脚本绝对路径。以有效 JSON 的 `status` 为准：`configured` 为已配置，`missing`、`outdated` 才是缺失、过期。退出码 2 是检查结果；命令失败、无有效 JSON、返回 `error` 或解释器不可用都只算无法确认，不安装依赖、不绕过读取限制。Cursor 只核对可访问的真正 User Rules 或已加载的全局规则，不猜全局文件路径，也不把项目规则当成全局规则。
3. 明确缺失或过期时只提醒一次：“全局技能提示词缺失或需更新，可显式调用 wukong-init 初始化。” 无法检查时用“暂时无法确认全局技能提示词”，不能说已缺失。已知旧规则按过期处理；自定义等价规则无法核实版本时只说明待核验，不覆盖。随后继续原任务，不等待用户配置、不重复催促。

Codex 还要检查钩子，即使全局规则已同步也不跳过。上面的 `global_instructions.py` 会返回独立的 `hooks` 结果，可直接复用；没有运行过该脚本时运行 `python wukong-init/scripts/codex_hooks.py`。检查默认只读，不受 `AGENTS.override.md` 选择影响，沿用 `CODEX_HOME`。`outdated` 表示已注册钩子仍指向旧品牌目录或旧缓存版本；`missing` 表示没有记录用户输入的 wukong 钩子；`manual_review` 表示自定义命令需要人工核对。只提醒一次，不在日常检查中迁移或安装；用户要求修复后按 wukong-init 的 Codex 钩子步骤执行。`configured` 只说明注册路径正确，不证明宿主已批准、加载或实际记录过日志。

仅用户显式要求初始化或修复时，才加载 [wukong-init](../SKILL.md) 并按其步骤写入。
