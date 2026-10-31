setup-s-models 写出配置时用左列。各技能读取时左列优先，没有再读右列。

| 中文键 | 旧英文键 |
|---|---|
| 写功能和重构 | feature, refactoring |
| 修 bug | bug-fix |
| 性能问题 | perf-issue |
| 爬坡优化 | hillclimb |
| 判断和写作 | judgment and prose |
| 最难的任务 | hardest tasks |
| 怎么工作的探索者 | how explorer |
| 怎么工作的讲解者 | how explainer |
| 为什么的调查者 | why investigators |
| 为什么的综合者 | why synthesizer |
| 反思的工具视角 | reflect tooling |
| 反思的判断、发散和综合 | reflect judgment, divergent, synthesizer |
| 竞技场参赛者 | arena runners |
| 竞技场交叉评审 | arena cross-judge pool |
| 群体作战的工作者 | swarm workers |
| 架构设计参赛者 | architect runners |
| 审问审查者 | interrogate reviewers |

## 行值格式

每一项可以是 `模型`，也可以是 `模型（档位）`，例如 `sonnet（medium）`、`opus（high）`、`inherit-parent（high）`。档位只能是 `low`、`medium`、`high`、`xhigh`、`max`。逗号分隔的列表里，每一项各带各的档位。

读取时先去掉括号里的档位，剩下的当模型名用，括号里的档位当这个角色的起始推理等级。宿主能随派发传推理档位时（Claude Code 的 `Agent` 工具有 `effort`）必须传；不能传就只用模型名，不要把括号原样当模型名交给宿主。没有括号时，起始等级取 `# 预算` 括号里的档位。
