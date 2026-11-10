# T3 六角色模型方案：省、中、高

记录日期：2026-11-09。适用项目：`C:\Users\admin\s-skills`。

本文记录 Claude Code 与 Codex 混合使用的三档方案；实际应用状态以当前项目的 `AGENTS.md`、`wukong.t3.json` 和备用策略为准，安装插件不会自动覆盖它们。不再安排 Cursor，移除不限档选项；高档在现有配置工具中对应“大”。

模型分工结合官方的通用推理建议和用户偏好确定，不是经过项目对照测试的能力排名。预算主要影响模型选择和评审人数，不把所有模型统一升为 high、xhigh 或 max，也不保证两家额度消耗相等。

## 三档总览

下表适用于 T3 混合派发。只有本厂商模型的 Codex、Claude Code 分别使用[原生宿主三档方案](../../plugins/wukong/skills/setup-s-models/references/native-budget-profiles.md)。原生宿主不能直接使用本表的异厂商模型，DP 评审选择也不构成跨宿主调用授权。

表内格式为“模型 · 推理档位”。双模型条目表示两个独立参与者。

| 角色 | 省 | 中 | 高 |
| --- | --- | --- | --- |
| 检索与探索 | Haiku 5.5 · medium | Luna · max | Luna · max |
| 方案设计 | Sonnet 5.5 · medium | Opus 5.5 · medium | Opus 5.5 · medium |
| 开发实现 | Sonnet 5.5 · medium | Sonnet 5.5 · high | Opus 5.5 · medium |
| 专项攻坚 | Opus 5.5 · medium | Opus 5.5 · high | Opus 5.5 · high |
| 验证测试 | Sol · medium | Sol · medium | Sol · high |
| 独立评审 | DP4.1 Flash · enabled，1 个 | DP4.1 Flash · enabled，1 个 | DP4.1 Flash · enabled ＋ Sol · medium，2 个 |

Luna 的 max 保留用户此前的显式选择，不是官方默认或推荐起点。若重新以官方客户端建议作为起点，应选择 high；本次文档生成不替用户撤销此前选择。

## 每个角色的首选与次选

多方向调查可按[并发只读检索](../../plugins/wukong/skills/wukong-mode/references/subagents.md#并发只读检索)分模块、功能或证据并发拆任务。该规则在委派已授权时适用，不增加评审名额或把备用一起启动；没有串行对照不宣称固定加速倍数。

上表列出首选。完整的三档首选/次选表及切换规则已接入技能，见[混合三档与顺序备用](../../plugins/wukong/skills/setup-s-models/references/mixed-budget-profiles.md)。每个角色名额都有独立备用，一次只启动首选或次选之一。

首选明确不可用时才使用次选；任务已部分执行或状态不明时先核对和停止旧任务，避免重复写入。每个名额最多尝试两个候选。高档两名评审各有备用，不把备用计为额外评审者。

这是技能级的编排约定，不是现有 JSON 解析器的自动故障转移。实际项目配置与跨会话备用策略由各项目独立保存；应用时按技能预览完整配置和策略文件，再确认写入。

## 1. 省

日常实现使用 Sonnet，难题才调用 Opus。Haiku 承担明确条件下的查找、提取和整理，Sol 负责运行验证，DP4.1 Flash enabled 独立评审，次选 Sol medium。

Haiku 没有覆盖到的复杂调用链调查由主代理处理，必要时明确指定 Luna；不能把 Haiku 的整理结果直接视为调查完备。专项攻坚角色只在遇到难题时使用，不要求每项任务都调用。

## 2. 中

设计交给 Opus，Sonnet 以 high 承担实现，Sol 运行验证，DP4.1 Flash enabled 独立评审，次选 Sol medium。评审会话独立于实现和验证会话，自行读取完整任务差异，检查必要的调用链和失败路径，不能只依据完成报告。

Luna 负责主调查。条件明确的提取、日志归类和材料整理可明确交给 Haiku medium，每个子任务只选一个执行者。此分支是人工派发约定，固定六角色配置不自动实现任务路由。

## 3. 高

Opus 负责设计和实现，Sol 负责验证。专项攻坚首选 Opus high，明确不可用时使用次选 Astra medium，仍为一个名额。任务确需并发攻坚且已获授权时，再由主代理另行拆分互不冲突的范围，不自动双派。

独立评审由 DP4.1 Flash enabled 与 Sol medium 各占一个名额，分别检查需求与行为遗漏、调用链与失败路径。两者次选均为 Sonnet medium。独立会话评审，不启动第三个名额。

明确的提取整理任务仍可指定 Haiku medium。高档增加模型能力与检查视角，不默认使用 xhigh 或 max。

## 模型 ID 与参数

| 简称 | 提供商实例 | 模型 ID | T3 目标中的推理参数 |
| --- | --- | --- | --- |
| Haiku 5.5 | `claudeAgent` | `claude-haiku-5-5` | `effort` |
| Sonnet 5.5 | `claudeAgent` | `claude-sonnet-5-5` | `effort` |
| Opus 5.5 | `claudeAgent` | `claude-opus-5-5` | `effort` |
| Luna | `codex` | `gpt-6-luna` | `reasoningEffort` |
| Sol | `codex` | `gpt-6.1-sol` | `reasoningEffort` |
| Astra | `codex` | `gpt-6-astra` | `reasoningEffort` |

所有 Codex 目标使用 `serviceTier: default`。上表参数名用于本项目 T3 目标配置，不是底层 API 请求结构。模型 ID 与推理参数分开传递。

## 档位调整与评审范围

medium、high 是本方案的明确起始配置。遇到并发、权限、事务、迁移或跨模块接口改动，应先扩大检查范围、补齐上下文和失败路径，再决定是否提高推理。低预算不能免除必要的风险检查；需要增加评审时应说明超出当前预算方案。

xhigh 或 max 只在具体任务需要且比较结果支持时启用。强模型默认档位和弱模型高档位不能直接按名称比较。

验证测试负责复现、运行检查和回传真实产物证据，修复交回实现角色。独立评审默认使用 DP4.1 Flash enabled，省、中档次选 Sol medium，高档配合一个 Sol medium；Haiku 只做辅助筛查。这是基于模型定位与用户偏好的工程选择，不是官方评审模型推荐，也没有证明 medium 与 high 的漏报率相同。

评审不常驻 high。遇到并发、权限、事务、迁移或复杂失败路径时，针对负责该风险的评审者明确升到 high，并说明原因。普通任务保留 medium，减少不必要的推理消耗。

Terra 6.1 不设为默认代码评审者；任务包含截图、布局或界面操作时，可明确安排它承担视觉验收。此用途不替代代码行为检查。

## CodeBuddy DeepSeek 评审

技能已接入[DeepSeek 评审规则](../../plugins/wukong/skills/setup-s-models/references/glm-review-trial.md)，省、中档 DP 首选、Sol 次选，高档 DP 与 Sol 共两个独立名额。

实际目标为 acpRegistry_codebuddy_code / deepseek-v4.1-flash，显式 thought_level: enabled。当前目录默认 max，因此不能省略该选项，也不把 enabled 等价为 medium。GLM 因用户反馈慢而取消，HY4 未做本轮实测。

DP 已成功完成真实修复复核，指出的终态回读缺失已复现并修复，29 项 T3 测试通过。用户据此选定它为首选，但本轮不是同样输入的完整模型质量或速度基准。实际项目 JSON 与备用策略仍需最终确认后写入。

## 官方依据与方案边界

以下资料在本会话中核对过：

- [Claude Code 模型与推理设置](https://code.claude.com/docs/en/model-config#adjust-effort-level)：Haiku、Sonnet、Opus 5.5 默认均为 medium；high 用于重验证或容易出现边界情况的任务；max 应先测试收益。
- [Claude API 逐模型推理建议](https://platform.claude.com/docs/en/build-with-claude/effort#recommended-effort-levels)：区分 API 与 Claude Code 默认值；Sonnet 的明确代理编码任务可从 medium 开始，较难或较长任务使用 high。
- [OpenAI 客户端模型选择](https://learn.chatgpt.com/docs/models)：Luna 从 high、Astra 从 Light 即 low 起步；Sol 从客户端默认起步，根据任务调整。
- [Sol API 模型页](https://developers.openai.com/api/docs/models/gpt-6.1-sol)：API 默认 medium。

Astra medium 是为高档难题调查显式选择的档位，不是对官方客户端 low 起始建议的转述。官方资料没有给出本文六角色组合的最优解，本方案需要通过真实任务逐步校准。

## 历史验证记录

2026-11-09 调整前省档的冒烟测试结果，不能作为本版三档方案的验证结果：

| 角色 | 结果 |
| --- | --- |
| 检索与探索 | Luna `max` 成功启动，正确回传校验值 |
| 方案设计 | Claude 返回周额度已用尽，提示上海时间 19:00 重置 |
| 开发实现 | Sol `medium` 成功启动，正确回传校验值 |
| 专项攻坚 | Astra `high` 成功启动，正确回传校验值 |
| 验证测试 | Composer `fastMode: false` 成功启动，正确回传校验值 |
| 独立评审 | Claude 返回周额度已用尽，提示上海时间 19:00 重置 |

此次冒烟测试仅验证委派、指定模型和参数、结果回传，没有验证实际开发、测试或代码评审质量。额度状态是测试时的记录。
