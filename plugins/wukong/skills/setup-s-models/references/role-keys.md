# 六角色与旧键兼容

所有宿主新生成配置使用下表中文键，英文键用于宿主角色文件命名与兼容读取。

| 中文键 | 英文键 |
|---|---|
| 检索与探索 | lookup and exploration |
| 方案设计 | design |
| 开发实现 | implementation |
| 专项攻坚 | specialist |
| 验证测试 | verification |
| 独立评审 | review |

## 旧配置读取

旧中文与旧英文键继续读取，映射由 scripts/s_models.py 的 LEGACY_ROLES 与 ROLE_GROUPS 维护。检索和简单任务、how explorer、why investigators 对应检索与探索；judgment and prose、how explainer、why synthesizer、reflect judgment, divergent, synthesizer 对应方案设计；feature, refactoring 和 bug-fix 对应开发实现；perf-issue、hillclimb、hardest tasks 对应专项攻坚；swarm workers 对应验证测试；interrogate reviewers 与 reflect tooling 对应独立评审。

旧角色的精确请求仍读取原行；合并旧行时不同模型或档位必须报冲突。明确的新中文行优先，不自动丢弃其他旧选择。读取旧键不代表再生成十五行。Codex 新角色文件分别为 s-lookup-and-exploration、s-design、s-implementation、s-specialist、s-verification、s-review（评审列表按宿主规则加序号）；不自动删除用户的旧角色文件。

## 行值格式

首选/次选不使用逗号行值表示。逗号各项是独立派发名额；顺序备用与项目策略的持久化见[混合三档与顺序备用](mixed-budget-profiles.md)。现有解析器不自动故障转移。

只有本厂商工具的宿主选[原生三档](native-budget-profiles.md)。当前宿主能力先于候选型号，显式角色档位先于通用预算；不存在可用次选时报告，不伪造跨厂商回退。

每项可写 模型 或 模型（档位），例如 sonnet（medium）、inherit-parent（high）。逗号分隔的评审项各带各的档位。档位为 low、medium、high、xhigh、max；宿主按自己的参数与合法值映射，不能把括号原样传给 model。

普通模式执行 python scripts/s_models.py resolve <规则文件> <角色> --json；T3 别名执行 scripts/t3_targets.py resolve，参考 [T3 编排参考](../../wukong-router/references/t3-code-tools.md)。检索与探索未指定档位时最多 medium；专项攻坚生成时比预算起始高一级，最高 max。显式档位优先。

角色名与人数分开：只有独立评审的列表长度受预算约束，其他角色不会因为定义存在就自动运行。派发仍需要任务授权。
