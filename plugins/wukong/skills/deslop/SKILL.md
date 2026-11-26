---
name: deslop
description: "「/deslop」「提交前清一下 AI 味」「去掉多余的 any」「审查前先删注释」「只清注释」。清这次 diff 里的代码腔：多余注释、不该有的防御、过深嵌套；只清注释时派 comment-sicko 只读审查后再改。文字腔用 technical-writing。Use when a diff needs AI-flavored code removed before commit: extra comments, needless guards, any-casts, or deep nesting, including a comment-only pass with the comment-sicko reviewer."
---

本会话首次使用本库技能时，按[全局提示词自检](../wukong-init/references/daily-check.md)只读检查一次。
## 运行环境适配

涉及宿主工具或子代理时，按需阅读[宿主适配](../../HOSTS.md)。

# 去掉代码腔

对照 `main` 看 diff，删掉这条分支新引进的 AI 代码腔。

文字里的 AI 腔归 `technical-writing` 的[去 AI 腔清单](../technical-writing/references/unslop.md)。这个 skill 管的是代码，两者不要互相代替。

## 重点看这些

- 多余的行内注释，或者和这个文件当地写法不一致的注释。符合 `code-style` 第二节的文档注释要保留，缺了还要补上
- 在本来可信的路径上，显得反常的防御检查或 `try/catch`
- 只为绕过类型问题而把值转成 `any`
- 嵌套太深、用提前返回就能变直的代码
- 和当前文件、周围代码库不一致的其他写法

## 边界

- 行为保持不变，除非是在修一个明确的 bug。
- 改动要小、要集中，不要大范围重写。
- 最后的总结写短，一两句到三句。

## 只清注释：派 comment-sicko

用户要求审查前先删注释、只清注释，或 diff 里注释很多时，派只读的 **comment-sicko** 子代理（规则见 [comment-sicko.md](references/comment-sicko.md)），收集候选删除和理由，父任务核实后在已授权范围内修改。尊重它的新鲜视角，派的时候只给范围，不把规则再写一遍。

范围用调用方给出的文件或 diff；否则用当前分支相对基础分支（默认 `main`）的 diff，包括工作区里还没提交的改动。

### 步骤

1. 派 **comment-sicko**，把范围传给它。各宿主怎么派，见宿主适配参考，派发细则见[公共派发规则](../executing-plans/references/subagents.md)。不要把另一套注释规则复述进提示词。父对话不自己先改注释。第 2 步再审它交回来的报告。
2. 检查报告中的文件、行号和理由。子代理不得修改文件。拒绝超出范围、违反保留例外、理由不实或误判有意保留代码的建议。核实范围内的 lint 和 TypeScript 抑制注释；涉及正确性或安全时，先确认根因和修复方式。删除理由或约束真实性仍有歧义时，保留原注释并报告未解决事项。需要进一步理解符号时，按已授权工作流调用 `/how` 或 `/why`。报告不合格时指出原因并重跑一次；仍不合格则报告未解决，不执行相关删除。
3. 对简单的已采纳标记直接修：删掉一条死路径、去掉一个参数，或者改用真正的 API。如果有修复需要设计形状，就对已采纳的这一批和周围的代码运行一次 `/architect`。停在草图阶段。架构负责定形状，第 4 步负责实现。
4. 在范围内实现最小的根本原因修复。去掉每一个被点名的绕过办法。如果根本原因超出范围，就在范围内落地最小的修复，把其余的报告为未解决。[fix-root-causes](../systematic-debugging/references/principles/fix-root-causes.md) 和 [redesign-from-first-principles](../brainstorming/references/principles/redesign-from-first-principles.md) 这两条原则 只指导意图。它们都不授权扩大范围，也不授权修范围外的实例。绝对不要硬加针对症状的防护。
5. 限制类注释会写着 `do not remove`、`do not change wording`（不要改措辞）或 `talk to X before changing`（改之前先找 X 谈）。受保留例外保护的注释继续保留。需要用类型、运行时检查、测试或 CI lint 替代约束时，先确认已有授权；未授权时提出具体方案并等待批准，无人值守运行同样需要事先授权。等效约束落实并验证后，才删除原注释。未获批准、无法落实或尚未验证时，保留原注释并报告未解决事项。
6. 报告删除的数量、恢复的注释、重跑次数、架构草图、修复、提出的强制执行办法、已经写成代码的强制执行、没有被强制执行的限制，以及其他未解决的工作。

## 宿主适配

做法不依赖聊天软件。对当前仓库跑 `git diff main`（或这次真正的基础分支），只动 diff 里新出现的代码腔。

Codex、Claude Code、Antigravity 都按上面的清单改。没有 git diff 时，就看用户指出的文件。

Codex、Claude Code、Antigravity 的工具和配置见[宿主适配](../../HOSTS.md)；按当前宿主读取对应参考。
