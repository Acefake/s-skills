# CodeBuddy DeepSeek-V4.1-Flash 评审

用户已在 2026-11-09 的修复复核后明确选择 DP4.1 Flash 首选评审。此选择是用户的工作流偏好，不代表已证明其总体准确率、速度或成本优于 Sol。保留本文件名以兼容已有链接。

## 三档安排

| 预算 | 首选 | 次选与名额 |
| --- | --- | --- |
| 省 | DP4.1 Flash enabled | Sol medium；1 个名额 |
| 中 | DP4.1 Flash enabled | Sol medium；1 个名额 |
| 高 | 名额 1：DP4.1 Flash enabled；名额 2：Sol medium | 各自次选 Sonnet medium；共 2 个名额 |

首选不可用才用次选，遵从[顺序备用](mixed-budget-profiles.md)。不同时启动备用；高档需要独立会话，不因候选模型数增加名额。若两名评审均回退 Sonnet，报告跨模型视角丢失。省档实现仍为 Sonnet medium，次选 Sol medium。

## 接入参数

2026-11-09 本会话能力目录列出的目标如下，实际派发前重新核对当前实例和工具：

```json
{
  "providerInstanceId": "acpRegistry_codebuddy_code",
  "model": "deepseek-v4.1-flash",
  "options": { "thought_level": "enabled" }
}
```

本次 CodeBuddy 目录暴露的 `thought_level` 值为 low、high、max、enabled，默认 max。试用显式指定 enabled，不继承 max，也不声称这是 DeepSeek 官方对代码评审的推荐。不能映射为 medium、max，也不能传 Claude 的 effort 或 Codex 的 reasoningEffort。底层 API 的 reasoning_effort 与 CodeBuddy thought_level 的映射未确认。

评审任务明确禁止编辑、提交、发布、安装依赖或其他外部写入。不要为了只读评审设置 mode、sandbox 或放宽运行权限；只读约束写在任务中，不声称工具提供了独立只读沙箱。

## 与 Sol 的对照验证

用户授权试用评审后，优先选真实且边界清楚的代码差异。没有这类差异时报告本轮未做质量对照，不用算术回传、提示词文案差异或模型自评分代替代码评审质量评估。

1. 固定同一基准和任务差异，提供原始需求、相关约束、文件位置和已有验证结果。Sol medium 与 DeepSeek enabled 使用相同材料，允许读取相同的必要调用方和失败路径。
2. 在独立会话中评审，互相不提供对方的发现。只读检查，不运行测试或改文件；候选问题由主代理另行核实。高档占用两个既有名额；省、中档这轮属于额外授权的对照实验，不能当成日常自动双评审。
3. 两者都按“位置、触发条件、实际影响、依据”报告发现。无发现也明确检查范围，不把泛泛的改进建议算缺陷。
4. 主代理逐条核实有效发现、误报和重复项。漏报只相对于已知缺陷及核实后的发现集合统计，没有完整缺陷答案时不能报告完整召回率。记录读取范围、耗时及工具确实返回的 token/额度数据；没有用量数据就标为未知。
5. 比较多份有代表性的差异，包括无已知问题的样本，避免以单个命中或单个失败决定模型优劣。记录语言、规模、风险及未覆盖场景。比较结果用于后续校准用户已选方案，不把一次成功复核说成等价替代证明；实际配置写入仍按 setup-s-models 的最终确认执行。

只完成一次对照时报告观察结果，不宣称 DeepSeek 等价替代 Sol。CodeBuddy 目录可调用、模型成功启动和评审质量分别记录。模型限流或鉴权失败时记录本轮未完成，不偷偷换模型补齐所谓对照结果。

## 可用性与历史记录

2026-11-09 用户反馈 GLM 评审过慢，取消该次试用，改用 CodeBuddy 的 deepseek-v4.1-flash。HY4 目录有 hy4free 与 hy4std 两个独立目标，不把显示名 HY4 当成模型 ID，也不擅自选择套餐。此次优先测试 DeepSeek。

本次目录提供 thought_level: low/high/max/enabled，默认 max。试用显式设置 enabled，避免继承 max；不宣称 enabled 等价于其他提供商的 medium。保留文件名是为了已有链接可继续访问，正文规则以本版为准。

## 本次复核记录

DeepSeek 4.1 已完成只读修复复核，确认两项已复现场景覆盖，并指出恢复终态回读缺失。该项已补失败回归并修复，T3 测试现为 29 项通过；符号链接用例明确执行为 ok，未跳过。备份保留首次前像是既有行为，已明确说明，未改成覆盖用户原有备份。没有记录完整 token 用量，也没有等条件的速度对比。
