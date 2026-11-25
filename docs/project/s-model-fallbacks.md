# 项目模型方案：省档

本项目采用最终确定的混合三档方案，当前选择省档。只使用 Claude Code、Codex 和 CodeBuddy；不使用 Cursor 或 GLM。省、中各一名独立评审，高两名。高写入工具时映射为“大”，新配置只展示省、中、高。

## 六角色目标

每行首选和次选属于同一个代理名额，按顺序使用，不同时启动。Codex 目标均使用 `serviceTier: default`。

| 角色 | 配置别名 | 首选 provider / model / options | 次选 provider / model / options |
| --- | --- | --- | --- |
| 检索与探索 | `t3:lookup` | `claudeAgent` / `claude-haiku-5-5` / `{"effort":"medium"}` | `codex` / `gpt-6-luna` / `{"reasoningEffort":"max","serviceTier":"default"}` |
| 方案设计 | `t3:design` | `claudeAgent` / `claude-sonnet-5-5` / `{"effort":"medium"}` | `codex` / `gpt-6.1-sol` / `{"reasoningEffort":"medium","serviceTier":"default"}` |
| 开发实现 | `t3:implementation` | `claudeAgent` / `claude-sonnet-5-5` / `{"effort":"medium"}` | `codex` / `gpt-6.1-sol` / `{"reasoningEffort":"medium","serviceTier":"default"}` |
| 专项攻坚 | `t3:hard` | `claudeAgent` / `claude-opus-5-5` / `{"effort":"medium"}` | `codex` / `gpt-6-astra` / `{"reasoningEffort":"medium","serviceTier":"default"}` |
| 验证测试 | `t3:test` | `codex` / `gpt-6.1-sol` / `{"reasoningEffort":"medium","serviceTier":"default"}` | `claudeAgent` / `claude-sonnet-5-5` / `{"effort":"medium"}` |
| 独立评审 | `t3:review` | `acpRegistry_codebuddy_code` / `deepseek-v4.1-flash` / `{}` | `codex` / `gpt-6.1-sol` / `{"reasoningEffort":"medium","serviceTier":"default"}` |

## 顺序备用

派发前读取本文件，核对当前宿主能力与目标完整参数。首选在目录中不可用或启动明确失败（额度耗尽、限流、模型或提供商不可用、认证失败）时，才使用本行次选；报告原始原因和实际目标。每个名额首选、次选各最多尝试一次，均失败则报告受阻，不猜第三个候选。

首选已开始工作，或超时、传输失败导致运行状态不明时，先对账；取消不再需要的已知任务并确认停止，核对遗留文件后才切换，避免两个写入者同时工作。代码报错、测试失败、评审发现问题或主观不满意不触发备用。

省档独立评审只有一个名额，次选不增加评审人数。不把本表的箭头或次选写成角色行的逗号列表。独立的只读检索可按模块或功能分工并发，但只在任务已授权并发时派发，不因为存在次选额外启动代理。

`wukong.t3.json` 只保存六个首选。现有解析器不读取此备用表，不实现自动故障转移；主代理按本文件和宿主工具规则执行备用。此配置只适用于本 T3 项目，不覆盖 Codex 或 Claude Code 的用户级原生配置。
