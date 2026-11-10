# 宿主适配

插件分发支持 **Codex、Claude Code、Cursor、CodeBuddy、WorkBuddy**。CodeBuddy 和 WorkBuddy 同源，共用 `~/.codebuddy`，配置里统一写 `workbuddy`。模型配置另外识别 **DeepSeek Harness**（命令 `dsh`）和 **Nous Research 的 Hermes agent**（命令 `hermes`）。插件名为 `wukong`，仓库和市场名为 `s-skills`。版本以插件清单为准，技能以当前会话实际发现的目录为准。DeepSeek Harness 和 Hermes 没有市场安装包，也不走本仓库的安装脚本。

## 按需读取当前宿主

### T3 Code 编排环境

在 T3 Code 中运行时，底层仍按 Codex、Claude Code 等宿主读取技能；涉及模型设置、子代理或工作区时，同时读取 [T3 Code 编排参考](skills/wukong-router/references/t3-code-tools.md)。这是工具适配，不新增市场安装包。T3 的能力目录不等于底层原生子代理的模型目录。

T3 显式目标不可用时报告错误，不执行下文通用替代规则。用户明确授权了首选/次选时，按[顺序备用](skills/setup-s-models/references/mixed-budget-profiles.md)对账失败状态后，仅切换到已确认次选。跨提供商、额外设置、独立检出或用户点名委派时使用 T3；其他任务按参考选择原生执行。`t3:` 角色引用通过 `t3_targets.py` 解析，不能直接作为模型名。

T3 模型支持按底层宿主保存的用户级全局默认与项目级覆盖。全局用 `--host` 明确宿主，按 [T3 编排参考的路径表](skills/wukong-router/references/t3-code-tools.md) 遵从环境变量、规则文件名和格式；不使用统一全局目录。项目无模型段才继承所选宿主全局默认，有完整段则整段覆盖。规则与目标始终属于同一作用域；目标 JSON 不是宿主原生模型设置。更换机器仍须核对 provider 实例、模型及参数。

模型预设按能力选：[T3 混合三档](skills/setup-s-models/references/mixed-budget-profiles.md)、[Codex 与 Claude Code 原生三档](skills/setup-s-models/references/native-budget-profiles.md)。预设不授予跨厂商能力，不替代能力检测或最终配置确认。

新配置只展示省、中、高，高在通用脚本中规范为“大”；下文及宿主参考里的“大/不限”仍用于旧配置兼容，不是第四个预算选项。预设的显式角色档位优先于通用预算映射。

任务只涉及通用逻辑、文字或技能规则时，不必加载平台教程。需要安装配置、子代理、模型选择、浏览器、工作区或定时能力时，只读当前宿主对应的参考：

| 宿主 | 平台参考 |
|---|---|
| Codex | [Codex 工具和配置](skills/wukong-router/references/codex-tools.md) |
| Claude Code | [Claude Code 工具和配置](skills/wukong-router/references/claude-code-tools.md) |
| Cursor | [Cursor 工具和配置](skills/wukong-router/references/cursor-tools.md) |
| CodeBuddy、WorkBuddy | [CodeBuddy 与 WorkBuddy 工具和配置](skills/wukong-router/references/workbuddy-tools.md) |
| DeepSeek Harness（`dsh`） | [DeepSeek Harness 工具和配置](skills/wukong-router/references/dsh-tools.md) |
| Hermes agent | [Hermes 工具和配置](skills/wukong-router/references/hermes-tools.md) |

技能正文负责任务步骤、角色职责、输入输出和验收；平台参考负责工具参数、配置位置和能力差异。已有用户配置与本次授权优先，不用示例模型覆盖用户选择。

## 向用户提问的工具

技能里说“用宿主的提问工具”，指下表的工具。名字以当前会话的工具定义为准，定义里没有就不调用。

| 宿主 | 提问工具 | 备注 | 出处 |
|---|---|---|---|
| Claude Code | `AskUserQuestion` | | [claude-code-tools.md](skills/wukong-router/references/claude-code-tools.md) |
| Codex | `request_user_input` | 只有主对话能用，子智能体不能问 | [codex-tools.md](skills/wukong-router/references/codex-tools.md) |
| Cursor | `AskQuestion` | | [cursor-tools.md](skills/wukong-router/references/cursor-tools.md) |
| WorkBuddy | 未确认固定名字 | 用宿主实际提供的提问工具 | [workbuddy-tools.md](skills/wukong-router/references/workbuddy-tools.md) |
| DeepSeek Harness（`dsh`） | 未确认 | 参考文件没有记录 | [dsh-tools.md](skills/wukong-router/references/dsh-tools.md) |
| Hermes agent | 未确认 | 参考文件没有记录 | [hermes-tools.md](skills/wukong-router/references/hermes-tools.md) |

没有提问工具时，在对话里列编号选项并等回复。沉默、“随便”不当作批准。

DeepSeek Harness 和 Hermes 的 6 个角色行与现有四个宿主相同。写出的标记段是 `# s 模型配置` 到 `# s 模型配置结束`，只替换这一段。旧标记 `# s model configuration` 到 `# end s model configuration` 是同一段，读取仍然有效；重写时换成中文标记和中文键。角色键的对照在 [角色键对照](skills/setup-s-models/references/role-keys.md)。两家的配置 YAML 都不放这段：`cordis.patch.yml` 和 `config.yaml` 里的其他条目保持原样。

| 宿主 | 标记段 | 技能目录 | 列出可用模型 | 多个 profile |
|---|---|---|---|---|
| DeepSeek Harness | `$DSH_HOME/AGENTS.md`（未设置时是 `~/.dsh/AGENTS.md`） | `$DSH_HOME/skills/<name>/SKILL.md` | 选中 profile 的 `dsh --dump-config`，以及会话里的 `list_subagent_models` | 问用户用 `profiles/` 里的哪一个目录 |
| Hermes | 选中 profile 的 `SOUL.md` | 该 profile 家目录下的 `skills/` | 只读 `hermes config get` 的 `model` 与 `providers`（或旧的 `custom_providers`） | `hermes profile list` 多于一个时问用户 |

子代理不能按次接收模型时，6 行写 `inherit-parent`，派出时不传模型。没有显式角色档位时，推理起点按预算映射：不限 → `max`，大 → `xhigh`，中 → `high`，省 → `medium`；专项攻坚在起点上提高一级、最高 max，检索与探索最高 medium。显式角色档位或确认预设优先。宿主不能逐次传推理时继承并说明未设置，不能把预算目标报成实际生效。旧档名 `unlimited`、`large`、`medium`、`small` 相同。宿主没有的档位按该参考改到不超过目标的最高档。判断步骤、依据和未确认项在上面两份参考里。

## 共同行为

三档模型按[公共派发规则](skills/wukong-mode/references/subagents.md)选择，当前宿主确认可派发的模型才可写入配置。新增“检索与探索”角色，英文键 `lookup and exploration`；旧配置可按原角色精确读取，合并冲突需用户确认，缺少轻量行时沿用原角色。新配置共 6 行，允许三档共用模型。不能按次选模时全部使用继承模式，不声称已分流。重新配置默认保留已有角色选择，用户明确选择重新分配才加 `--replace-roles`，修改单行用 `--set`。模型或参数被拒绝时报告错误并交回主线程，不自动换型号。

- 不编造当前会话没有的工具、参数、模型或代理类型。使用实际可用的等价能力，并说明替代方式。
- 模型配置只修改用户选定作用域内属于本技能的标记段或角色文件，保留其他内容。具体路径和模型字段按平台参考，不在各技能重复定义。
- 无法委派时能顺序完成的任务继续，报告缺少独立审查或并行；不把主线程自查称为独立审查。
- 原生工具创建的工作区由原生工具管理和归档；操作前确认实际路径、分支与归属。
- 浏览器截图和真实操作证明界面行为；文件检查或编译不能替代实际运行证据。
- 持久定时任务只有在宿主调度工具保存成功后才算建立；后台等待或会话内循环不是持久任务。
- 安装、发布、合并、发送消息和付费服务遵循当前任务授权。技能本身不扩大权限。
- 提交、推送、rebase 与清理同样遵循已有授权。设计、计划、验证和创建 worktree 不自动授权提交或改写历史；提交步骤按 `commit-pr`，验证强度按 `wukong-router`，TDD 适用性按 `tdd`。

## 项目技能安装与验证

Codex 本项目开发可在仓库根运行 `powershell -NoProfile -File scripts/install_local_skills.ps1`。脚本将技能链接到项目 `.agents/skills/`，并将本文件复制到 `.agents/HOSTS.md`。平台参考位于技能内，随目录链接一起提供，无需额外复制平台资料。重新打开会话确认实际发现路径。

WorkBuddy 本机项目安装使用同一脚本加 `-HostName workbuddy`，链接到 `.codebuddy/skills/`。共享说明采用哈希记录管理；可以更新未被用户修改的受管副本，已有其他内容则停止并保留。它不是市场插件安装，也不配置云端技能库。CodeBuddy 的 CLI 与 IDE 走插件市场：`/plugin marketplace add Acefake/s-skills`、`/plugin install wukong@s-skills`。

分发入口以仓库 README 为准。运行 `python scripts/check_marketplace.py` 核对清单、版本锁、调用政策、公共引用和支持范围；运行 `python -m unittest discover -s scripts -p "test_*.py"` 检查发布与适配逻辑。

验证状态分别记录：文件校验、会话发现、实际读取、行为验证。一个阶段通过不代表其他阶段也已通过。真实宿主未运行时明确标记“未验证”。

## 全局技能提示词

显式调用 [setup-s-instructions](skills/setup-s-instructions/SKILL.md) 初始化当前宿主的全局指令，保留其他配置并幂等更新。普通技能只按[日常自检](skills/setup-s-instructions/references/daily-check.md)提醒，每会话一次，不自动写入。Cursor 使用真正的全局 User Rules；项目 Always 规则不能替代全局配置。想一次完成全局指令和模型配置，显式调用 [wukong-init](skills/wukong-init/SKILL.md)，它只做顺序编排。
