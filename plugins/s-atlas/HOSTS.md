# 宿主适配

本仓库只支持 **Codex、Claude Code、Cursor**。插件名为 `s-atlas`，仓库和市场名为 `s-skills`。版本以插件清单为准，技能以当前会话实际发现的目录为准。

## 按需读取当前宿主

任务只涉及通用逻辑、文字或技能规则时，不必加载平台教程。需要安装配置、子代理、模型选择、浏览器、工作区或定时能力时，只读当前宿主对应的参考：

| 宿主 | 平台参考 |
|---|---|
| Codex | [Codex 工具和配置](skills/s-router/references/codex-tools.md) |
| Claude Code | [Claude Code 工具和配置](skills/s-router/references/claude-code-tools.md) |
| Cursor | [Cursor 工具和配置](skills/s-router/references/cursor-tools.md) |

技能正文负责任务步骤、角色职责、输入输出和验收；平台参考负责工具参数、配置位置和能力差异。已有用户配置与本次授权优先，不用示例模型覆盖用户选择。

## 共同行为

- 不编造当前会话没有的工具、参数、模型或代理类型。使用实际可用的等价能力，并说明替代方式。
- 模型配置只修改用户选定作用域内属于本技能的标记段或角色文件，保留其他内容。具体路径和模型字段按平台参考，不在各技能重复定义。
- 无法委派时能顺序完成的任务继续，报告缺少独立审查或并行；不把主线程自查称为独立审查。
- 原生工具创建的工作区由原生工具管理和归档；操作前确认实际路径、分支与归属。
- 浏览器截图和真实操作证明界面行为；文件检查或编译不能替代实际运行证据。
- 持久定时任务只有在宿主调度工具保存成功后才算建立；后台等待或会话内循环不是持久任务。
- 安装、发布、合并、发送消息和付费服务遵循当前任务授权。技能本身不扩大权限。
- 提交、推送、rebase 与清理同样遵循已有授权。设计、计划、验证和创建 worktree 不自动授权提交或改写历史；提交步骤按 `commit-pr`，验证强度按 `s-router`，TDD 适用性按 `tdd`。

## 项目技能安装与验证

Codex 本项目开发可在仓库根运行 `powershell -NoProfile -File scripts/install_local_skills.ps1`。脚本将技能链接到项目 `.agents/skills/`，并将本文件复制到 `.agents/HOSTS.md`。平台参考位于技能内，随目录链接一起提供，无需额外复制平台资料。重新打开会话确认实际发现路径。

分发入口以仓库 README 为准。运行 `python scripts/check_marketplace.py` 核对清单、版本锁、调用政策、公共引用和支持范围；运行 `python -m unittest discover -s scripts -p "test_*.py"` 检查发布与适配逻辑。

验证状态分别记录：文件校验、会话发现、实际读取、行为验证。一个阶段通过不代表其他阶段也已通过。真实宿主未运行时明确标记“未验证”。

## 全局技能提示词

显式调用 [setup-s-instructions](skills/setup-s-instructions/SKILL.md) 初始化当前宿主的全局指令，保留其他配置并幂等更新。普通技能只按[日常自检](skills/setup-s-instructions/references/daily-check.md)提醒，每会话一次，不自动写入。Cursor 使用真正的全局 User Rules；项目 Always 规则不能替代全局配置。

## 经确认的经验

Codex、Claude Code、Cursor 均可按 [learn](skills/learn/SKILL.md) 使用本机 `~/.s-atlas/lessons`。这是插件自己的经验目录，不是任一宿主的原生记忆；不同项目按规范化根路径隔离，跨机器不自动同步。只读查询无需保存授权，每条经验写入或替换仍须明确确认。不编造自动加载、后台学习或其他客户端已经验收的结果。
