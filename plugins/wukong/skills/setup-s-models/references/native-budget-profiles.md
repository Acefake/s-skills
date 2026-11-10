# 原生宿主：三档候选与顺序备用

只在当前工具能派发本厂商模型、没有已授权跨提供商编排能力时使用本文件。T3 中存在可用跨提供商工具时改读[混合方案](mixed-budget-profiles.md)。环境由实际工具与目标能力决定，不仅看父模型或应用名称。

原生宿主配置预算默认使用本文件的省、中、高三档。这些是工程预设，不是官方任务能力排名。用户配置和明确指定优先。先发现实际可用模型、参数及角色类型，再展示候选；不可用的表项必须标明，不能未经确认静默换型号或补造参数。用户接受三档设计不等于同意覆盖已有配置。

## Codex 原生

简称：Luna=`gpt-6-luna`，Sol=`gpt-6.1-sol`，Astra=`gpt-6-astra`。实际名称与档位必须被当前原生工具或已发现的角色文件支持；T3 能力目录不能证明原生支持。每格为首选 → 次选，一次只启动一个。

| 角色 | 省 | 中 | 高（工具预算“大”） |
| --- | --- | --- | --- |
| 检索与探索 | Luna high → Sol low | Luna high → Sol medium | Luna high → Sol medium |
| 方案设计 | Sol medium → Astra medium | Sol high → Astra medium | Astra medium → Sol high |
| 开发实现 | Sol medium → Astra medium | Sol high → Astra medium | Sol high → Astra medium |
| 专项攻坚 | Astra medium → Sol high | Astra high → Sol high | Astra high → Sol high |
| 验证测试 | Sol medium → Astra medium | Sol medium → Astra medium | Sol high → Astra medium |
| 独立评审 | Sol medium → Astra medium，1 名 | Sol medium → Astra medium，1 名 | 名额 1：Sol medium → Astra medium；名额 2：Astra medium → Sol medium，共 2 名 |

默认不延用 T3 混合预设中的 Luna max 个人偏好。若当前用户明确要求跨宿主保留 max，先核验支持后按其要求展示，不擅自降低。

有固定模型的自定义角色时，为首选与次选选择各自匹配的已发现角色；不能拿绑定 Sol 的角色来宣称已派 Astra。角色文件不能在备用触发时临时重写。原生工具不能逐次指定模型或推理时，使用其实际支持的匹配角色，否则明确报告继承父会话及未分流；不模拟跨提供商调度。

继承只适用于用户允许继承或正在确认候选方案的情形；执行已指定模型的任务时，缺少匹配角色就报告目标不可用，不能静默改为继承或其他型号。

## Claude Code 原生

简称 Haiku、Sonnet、Opus 对应当前工具实际允许的模型取值。工具只允许 `haiku/sonnet/opus` 时使用这些别名，不把 T3 完整 ID 或带括号的字符串传入 model。别名所指版本先核实；无法确认是 5.5 时不宣称本表已验证该版本。

| 角色 | 省 | 中 | 高（工具预算“大”） |
| --- | --- | --- | --- |
| 检索与探索 | Haiku medium → Sonnet medium | Haiku medium → Sonnet medium | Sonnet medium → Haiku high |
| 方案设计 | Sonnet medium → Opus medium | Opus medium → Sonnet high | Opus medium → Sonnet high |
| 开发实现 | Sonnet medium → Opus medium | Sonnet high → Opus medium | Opus medium → Sonnet high |
| 专项攻坚 | Opus medium → Sonnet high | Opus high → Sonnet high | Opus high → Sonnet high |
| 验证测试 | Sonnet medium → Opus medium | Sonnet medium → Opus medium | Sonnet high → Opus medium |
| 独立评审 | Sonnet medium → Opus medium，1 名 | Sonnet medium → Opus medium，1 名 | 名额 1：Sonnet medium → Opus medium；名额 2：Opus medium → Sonnet medium，共 2 名 |

高档检索次选 Haiku 只适合明确的查找与提取；复杂调用链任务不能未经说明降级为 Haiku 调查完备。主代理保留综合核验责任。

参数以当前 Agent 定义为准。存在独立 effort 字段才按其合法值传入；不存在时报告实际继承或无法设置，不能伪造已使用 medium。不能借 shell 启动别家 CLI 来填补原生宿主能力。

## 配置与运行

1. 先确认宿主、作用域和省、中、高预算，使用对应三档预设；用户已有配置或明确自定义时按其确认结果展示。一次展示六角色、每个名额的首选/次选、参数和人数。明确的角色档位覆盖通用预算映射；预设不随预算机械升到 xhigh/max。
2. 现有脚本只把各名额首选写入角色行，逗号仍表示独立名额。备用顺序不写成逗号模型列表。生成器须使用每行明确的角色档位，不重新套通用预算覆盖表内数值。
3. 项目级持久化备用时，预览 `docs/project/s-model-fallbacks.md` 和该宿主真正读取的规则文件中的入口。Codex 参考 AGENTS.md，Claude Code 参考 CLAUDE.md；以用户已选作用域及宿主适配的实际路径为准，不同时修改两家全局文件。用户级配置采用已确认宿主规则中的可读策略段或显式链接，不猜项目根路径。最终确认后写入并回读。
4. [顺序备用规则](mixed-budget-profiles.md#首选失败后的操作)同样适用：明确不可用才切换已授权次选，先停止并对账旧任务，单个候选最多尝试一次，失败后报告受阻。配额或提供商整体不可用时，同厂商备用不保证有效。
5. 高档两个名额必须使用独立会话。回退到同一模型时报告失去跨模型视角；用户要求必须异构时报告无法满足。不能派子代理时主代理顺序完成，并明确缺少独立评审或实际并行。

原生备用也是主代理读取策略后的选择，不是宿主内建自动故障转移。未持久化、未重启发现角色或未实测时分别标明边界。DP4.1、GLM、HY4 只属于另有相应提供商能力的编排方案，不能写成这些原生表的可用目标。
