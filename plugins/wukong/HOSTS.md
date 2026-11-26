# 宿主适配

插件分发支持 **Codex、Claude Code、Antigravity**。Antigravity 原生加载插件根 `plugin.json`、`rules/AGENTS.md` 与 `hooks.json`（可用 `agy plugin install` 安装或通过 `~/.gemini/config/plugins.json` 挂载）。另有 **DeepSeek Harness**（命令 `dsh`）和 **Nous Research 的 Hermes agent**（命令 `hermes`）的工具参考。插件名为 `wukong`，仓库和市场名为 `s-skills`。版本以插件清单为准，技能以当前会话实际发现的目录为准。DeepSeek Harness 和 Hermes 没有市场安装包，也不走本仓库的安装脚本。

## 按需读取当前宿主

### T3 Code 编排环境

在 T3 Code 中运行时，底层仍按 Codex、Claude Code 等宿主读取技能；涉及子代理或工作区时，同时读取 [T3 Code 编排参考](skills/wukong-router/references/t3-code-tools.md)。这是工具适配，不新增市场安装包。T3 的能力目录不等于底层原生子代理的模型目录。

任务只涉及通用逻辑、文字或技能规则时，不必加载平台教程。需要安装配置、子代理、浏览器、工作区或定时能力时，只读当前宿主对应的参考：

| 宿主 | 平台参考 |
|---|---|
| Codex | [Codex 工具和配置](skills/wukong-router/references/codex-tools.md) |
| Claude Code | [Claude Code 工具和配置](skills/wukong-router/references/claude-code-tools.md) |
| Antigravity（`agy`） | [Antigravity 工具和配置](skills/wukong-router/references/antigravity-tools.md) |
| DeepSeek Harness（`dsh`） | [DeepSeek Harness 工具和配置](skills/wukong-router/references/dsh-tools.md) |
| Hermes agent | [Hermes 工具和配置](skills/wukong-router/references/hermes-tools.md) |

技能正文负责任务步骤、输入输出和验收；平台参考负责工具参数、配置位置和能力差异。子代理模型与推理档位按[公共派发规则](skills/executing-plans/references/subagents.md#模型)选择。

## 向用户提问的工具

技能里说“用宿主的提问工具”，指下表的工具。名字以当前会话的工具定义为准，定义里没有就不调用。

| 宿主 | 提问工具 | 备注 | 出处 |
|---|---|---|---|
| Claude Code | `AskUserQuestion` | | [claude-code-tools.md](skills/wukong-router/references/claude-code-tools.md) |
| Codex | `request_user_input` | 只有主对话能用，子智能体不能问 | [codex-tools.md](skills/wukong-router/references/codex-tools.md) |
| Antigravity | `ask_question` | 简单是/否直接用文字问 | [antigravity-tools.md](skills/wukong-router/references/antigravity-tools.md) |
| DeepSeek Harness（`dsh`） | 未确认 | 参考文件没有记录 | [dsh-tools.md](skills/wukong-router/references/dsh-tools.md) |
| Hermes agent | 未确认 | 参考文件没有记录 | [hermes-tools.md](skills/wukong-router/references/hermes-tools.md) |

没有提问工具时，在对话里列编号选项并等回复。沉默、“随便”不当作批准。

## 共同行为

- 不编造当前会话没有的工具、参数、模型或代理类型。使用实际可用的等价能力，并说明替代方式。
- 无法委派时能顺序完成的任务继续，报告缺少独立审查或并行；不把主线程自查称为独立审查。
- 原生工具创建的工作区由原生工具管理和归档；操作前确认实际路径、分支与归属。
- 浏览器截图和真实操作证明界面行为；文件检查或编译不能替代实际运行证据。
- 持久定时任务只有在宿主调度工具保存成功后才算建立；后台等待或会话内循环不是持久任务。
- 安装、发布、合并、发送消息和付费服务遵循当前任务授权。技能本身不扩大权限。
- 提交、推送、rebase 与清理同样遵循已有授权。设计、计划、验证和创建 worktree 不自动授权提交或改写历史；提交步骤按 `commit-pr`，验证强度按 `wukong-router`，TDD 适用性按 `tdd`。

## 项目技能安装与验证

Codex 本项目开发可在仓库根运行 `powershell -NoProfile -File scripts/install_local_skills.ps1`。脚本将技能链接到项目 `.agents/skills/`，并将本文件复制到 `.agents/HOSTS.md`。平台参考位于技能内，随目录链接一起提供，无需额外复制平台资料。重新打开会话确认实际发现路径。

分发入口以仓库 README 为准。运行 `python scripts/check_marketplace.py` 核对清单、版本锁、调用政策、公共引用和支持范围；运行 `python -m unittest discover -s scripts -p "test_*.py"` 检查发布与适配逻辑。

验证状态分别记录：文件校验、会话发现、实际读取、行为验证。一个阶段通过不代表其他阶段也已通过。真实宿主未运行时明确标记“未验证”。

## 全局技能提示词

显式调用 [wukong-init](skills/wukong-init/SKILL.md) 初始化当前宿主的全局指令，并按宿主可用模型写入检索、规划、审查、测试四个子代理角色的模型块，保留其他配置并幂等更新。Antigravity 启用插件时自动加载 `rules/AGENTS.md`（不重复写库块），模型块与个人块写入 `~/.gemini/config/AGENTS.md`。派发时怎么读模型块见[公共派发规则](skills/executing-plans/references/subagents.md#模型)。普通技能只按[日常自检](skills/wukong-init/references/daily-check.md)提醒，每会话一次，不自动写入。
