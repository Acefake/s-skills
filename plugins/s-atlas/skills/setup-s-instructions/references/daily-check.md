# 日常全局提示词自检

每个主会话首次使用本库任一技能时，只读检查一次；其他技能复用结果，子智能体跳过。检查不阻塞原任务，不自动调用初始化技能，不写配置。

1. 先看已加载的全局指令。出现“s-atlas 全局技能规则”及当前技能优先规则，或可确认已有语义等价规则，视为已配置。HTML 标记可能被宿主剥离，不能仅凭标记缺失判断未配置。
2. 无法确认时，Codex、Claude Code 可用现有 Python 3 运行 `python setup-s-instructions/scripts/global_instructions.py --host codex` 或 `--host claude-code`，不带 `--apply`，脚本路径相对本库 skills 目录；不在该目录时换成脚本绝对路径。以有效 JSON 的 `status` 为准：`configured` 为已配置，`missing`、`outdated` 才是缺失、过期。退出码 2 是检查结果；命令失败、无有效 JSON、返回 `error` 或解释器不可用都只算无法确认，不安装依赖、不绕过读取限制。Cursor 只核对可访问的真正 User Rules 或已加载的全局规则，不猜全局文件路径，也不把项目规则当成全局规则。
3. 明确缺失或过期时只提醒一次：“全局技能提示词缺失或需更新，可显式调用 setup-s-instructions 初始化。” 无法检查时用“暂时无法确认全局技能提示词”，不能说已缺失。已有等价规则不提醒。随后继续原任务，不等待用户配置、不重复催促。

仅用户显式要求初始化或修复时，才加载 [setup-s-instructions](../SKILL.md) 并按其步骤写入。
