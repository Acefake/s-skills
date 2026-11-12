# Claude Code 与 Codex：三档预设和顺序备用

当前宿主支持跨提供商编排时，配置预算默认使用本文件的省、中、高三档。先发现当前宿主的真实能力；不能把表中候选可用、推理参数受支持或两模型能力等价当成事实。这里只提供配置与派发约定，不实现底层服务自动故障转移。

仅原生 Codex 或 Claude Code 工具时，不套用跨厂商表，改用[原生三档](native-budget-profiles.md)。备用操作原则通用；下面 AGENTS.md、wukong.t3.json 双文件持久化只属于 T3。其他宿主使用其真正读取的规则文件。并发调查遵从[并发只读检索](../../wukong-mode/references/subagents.md#并发只读检索)，顺序备用不增加代理数量。

## 三档候选

每个单元格写“首选 → 次选”，箭头表示顺序备用，一次只启动其中一个。每个模型后的词是其独立推理档位。T3 按本机目录选模型时，候选与顺序以[模型白名单](model-allowlist.json)的推荐为准，本表只提供各档推理档位的参考；两者不一致时以白名单推荐的模型为准，档位按本表同模型的值，表里没有该模型就用模型默认档。

| 角色 | 省 | 中 | 高（工具预算名为“大”） |
| --- | --- | --- | --- |
| 检索与探索 | Haiku medium → Luna max | Luna max → Haiku high | Luna max → Haiku high |
| 方案设计 | Sonnet medium → Sol medium | Opus medium → Sol high | Opus medium → Astra medium |
| 开发实现 | Sonnet medium → Sol medium | Sonnet high → Sol high | Opus medium → Sol high |
| 专项攻坚 | Opus medium → Astra medium | Opus high → Astra medium | Opus high → Astra medium |
| 验证测试 | Sol medium → Sonnet medium | Sol medium → Sonnet medium | Sol high → Sonnet high |
| 独立评审 | DP4.1 Flash enabled → Sol medium，1 个 | DP4.1 Flash enabled → Sol medium，1 个 | 名额 1：DP4.1 Flash enabled → Sonnet medium；名额 2：Sol medium → Sonnet medium，共 2 个 |

Luna max 保留本预设来源用户的显式偏好，不是官方默认；向其他用户推荐时标明这一点，允许改为客户端建议的 high。预设是工程选择，没有项目评测证明其最优或备用与首选等价。复杂代码评审不默认使用 Haiku 或 Terra；Haiku 用于明确的检索、提取和整理，Terra 可单独用于视觉验收。

专项攻坚角色行只有一个名额，高档也按首选 → 次选配置。任务确需并发攻坚且已获授权时，由主代理另外明确分工，不把额外代理写成该行的逗号列表。独立评审名额遵从预算和任务授权，不能因为表中有次选就增加名额。可只用一个评审时，不自动启动另一个。Sol、Sonnet 评审默认 medium，DP 默认显式 enabled；高风险项明确说明原因后再考虑提供商支持的较高档位；不按预算机械升到 xhigh/max。

用户已选定 CodeBuddy DeepSeek-V4.1-Flash 作为首选评审，具体规则见[DeepSeek 评审](glm-review-trial.md)。省、中档一名评审，Sol 为次选；高档由 DeepSeek 与 Sol 各占一个独立名额。DP 使用 thought_level: enabled，不套用 medium 参数。此次已做一轮修复复核，不宣称全面评测通过。

## 模型与参数

| 简称 | T3 提供商实例候选 | 模型 ID | T3 options 参数 |
| --- | --- | --- | --- |
| Haiku | `claudeAgent` | `claude-haiku-5-5` | `effort` |
| Sonnet | `claudeAgent` | `claude-sonnet-5-5` | `effort` |
| Opus | `claudeAgent` | `claude-opus-5-5` | `effort` |
| Luna | `codex` | `gpt-6-luna` | `reasoningEffort` |
| Sol | `codex` | `gpt-6.1-sol` | `reasoningEffort` |
| Astra | `codex` | `gpt-6-astra` | `reasoningEffort` |
| DP4.1 Flash | `acpRegistry_codebuddy_code` | `deepseek-v4.1-flash` | `thought_level` |

实例 ID 仍须在当前能力目录确认，不能跨机器照抄。Codex 候选使用 `serviceTier: default`。每个备选保存自己的模型、提供商和 options，切换时重建完整目标，不能把 `effort` 与 `reasoningEffort` 混用。普通宿主只能选择其原生可派发目标；跨提供商备用需要支持它的编排环境。

## 首选失败后的操作

用户明确要求配置顺序备用，或明确采用含顺序备用的完整方案，才授权在这些候选间切换。不把仅接受首选模型视为接受备用，也不覆盖更高优先级的宿主限制。

1. 首选在目录中不可用或启动明确失败，例如额度耗尽、限流、模型/提供商不可用、认证失败，才尝试已确认的次选。报告原始原因和实际使用的模型与档位，不代办登录或修改凭据。
2. 若首选已开始工作，或超时、传输失败导致是否执行不明，先按宿主规则对账。T3 用 `task_cancel` 停止不再需要的已知任务；核验运行已停止及遗留文件，再把已完成工作、未完成目标和验证状态交给次选。没有确定运行状态前不启动第二个写入者。
3. 代码报错、测试失败、评审发现问题或主观不满意不属于模型不可用；留在原任务处理，不据此触发备用。
4. 每个名额最多尝试首选和次选各一次。次选也不可用则报告受阻，不循环重试，不临时猜第三个目标或偷偷改工具、权限、工作区。
5. 备用降低能力或改变检查覆盖时说明边界。若两个评审名额最终落到同一模型，仍须是独立会话，并说明已失去跨模型检查视角；若用户要求必须异构，则停止并报告无法满足。

两个模型都属于已授权候选时不再反复请求切换许可。高预算也不授权额外第三个候选。

## 持久化与解析边界

`s_models.py` 与 `t3_targets.py` 角色行里的逗号列表是派发列表，不能用来序列化备用，也不能写箭头模型名或把备用伪装为第二个评审。T3 的次选保存在 `wukong.t3.json`（schemaVersion 2）对应目标的 `fallback` 字段，格式见 [T3 模型目标配置](t3-config.md)。

高档独立评审用两个完整别名表达：角色行写 `独立评审: t3:review, t3:review2`，`targets.review` 保存 CodeBuddy DP 的完整首选及其 `fallback`，`targets.review2` 保存 Codex Sol 的完整首选及其 `fallback`。第二名额也必须通过别名明确 provider/model/options，不能直接追加裸模型名来假定其提供商。

配置方案展示并经最终写入确认后，用 `t3_targets.py configure` 同时写入每个名额的首选和次选；check 对两者都按能力目录校验，回读后如实报告。项目作用域与用户级全局默认各自保存自己的 `wukong.t3.json`，派发前根据 check/resolve 返回的 `scope` 与 `targetsPath` 判断来源，不跨作用域拼接。目标里的 provider 实例 ID 在另一台机器可能不同，换机器后重新按本机目录选择。

旧项目若仍用 `docs/project/s-model-fallbacks.md` 或宿主根目录的 `s-model-fallbacks.md` 记录次选，派发时继续按该文件执行；经用户确认后迁进 `fallback` 字段，迁移完删掉该文件及规则里指向它的说明，不让两处同时生效。

resolve 每项返回 `fallback`，解析器不自动切换。是否改用次选按上文「首选失败后的操作」由主代理判断，并按宿主工具定义派发次选目标。

## 官方资料与本预设的关系

- [Claude Code 推理设置](https://code.claude.com/docs/en/model-config#adjust-effort-level)：5.5 的 Haiku、Sonnet、Opus 默认 medium；验证和边界问题可使用 high。
- [OpenAI 模型选择](https://learn.chatgpt.com/docs/models)：区分模型与客户端起始推理档位。
- [Sol 模型页](https://developers.openai.com/api/docs/models/gpt-6.1-sol)：面向复杂编码，API 默认 medium。

这些来源支持模型定位和档位起点，不构成六角色表、评审准确率或跨提供商备用等价性的官方背书。使用时核对当前版本，不把来源日期之后的变化当成已验证。
