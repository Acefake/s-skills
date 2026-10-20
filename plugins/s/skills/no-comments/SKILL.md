---
name: no-comments
description: "Use when you are about to review and comments that should not stay need to be removed first. 中文触发：派出 comment-sicko，修掉被采纳的问题，并为注释里声称的限制提出用代码强制执行的办法。"
disable-model-invocation: true
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。


# 不要注释

派出 **comment-sicko**。根据被采纳的发现采取行动。

尊重 comment-sicko 的新鲜视角。

## 范围

用调用方给出的文件或 diff。否则，就用当前分支相对基础分支（默认 `main`）的 diff，包括工作区里还没提交的改动。

## 步骤

1. 派 **comment-sicko**，把范围传给它。各软件怎么派，见文末。按 **poteto-mode** skill 里 “子智能体” 一节的规定，为子智能体选择推理等级和速度。不要把另一套注释规则复述进提示词。父对话不自己先改注释。第 2 步再审它交回来的报告。
2. 检查它的报告和 diff。拒绝这些情况：修改了应用代码、超出范围、删掉了受例外保护的内容、写错了 `MUST KILL` 的理由、把有意保留的代码当成有罪的标记。针对我们自己代码里出人意料之处的“需要重塑”标记，仍然要处理。不要恢复那些注释。一条保留（keep）只有在能证明它说的是我们改不了的东西时才成立。检查它漏掉的、范围内的 lint 和 TypeScript 抑制注释。与正确性或安全有关的抑制，仍然是要处理的 `MUST KILL`。只有在有确切的例外和限定范围内的证明时，才恢复被删的内容。在接受理由单薄的 `IMPORTANT` 或 `do not remove` 的删除或保留之前，先对它们涉及的符号运行 `/how` 或 `/why`。如果一个删除有歧义，不要恢复。如果一个保留被驳倒或者仍然有歧义，就删掉它。撤回一份被拒绝的报告，指出失败原因后重跑一次。如果第二次又被拒绝，就把它报告为未解决，并让 `/no-comments` 失败。
3. 对简单的已采纳标记直接修：删掉一条死路径、去掉一个参数，或者改用真正的 API。如果有修复需要设计形状，就对已采纳的这一批和周围的代码运行一次 `/architect`。停在草图阶段。架构负责定形状，第 4 步负责实现。
4. 在范围内实现最小的根本原因修复。去掉每一个被点名的绕过办法。如果根本原因超出范围，就在范围内落地最小的修复，把其余的报告为未解决。**principle-fix-root-causes** 和 **principle-redesign-from-first-principles** 这两个 skill 只指导意图。它们都不授权扩大范围，也不授权修范围外的实例。绝对不要硬加针对症状的防护。
5. 限制类注释会写着 `do not remove`、`do not change wording`（不要改措辞）或 `talk to X before changing`（改之前先找 X 谈）。关于我们改不了的东西的保留，就留着。提出范围内最便宜的类型、运行时检查、测试或 CI lint 办法。等待交互式批准。无人值守运行和评估运行需要调用方事先批准。如果批准了，就先写成代码强制执行，再删掉注释。否则就删掉注释，把这条限制报告为未解决，并画出范围外工作的草图。
6. 报告删除的数量、恢复的注释、重跑次数、架构草图、修复、提出的强制执行办法、已经写成代码的强制执行、没有被强制执行的限制，以及其他未解决的工作。

## 在不同软件里怎么用

规则在 [`comment-sicko`](../comment-sicko/SKILL.md)。派的时候只给范围，不要把那些规则再写一遍。

- **Cursor。** `Task`，`subagent_type: "comment-sicko"`（`agents/comment-sicko.md`）。软件不认这个类型时，用只读的 `generalPurpose`（`readonly: true`），提示词只写：先读 `skills/comment-sicko/SKILL.md`，再审这个范围。
- **OpenCode。** `subagent` 派内置 `explore`，或一个只读的自定义智能体。提示词只写：先读 `skills/comment-sicko/SKILL.md`，再审这个范围。
- **Codex。** 用话派一个子智能体，点名内置 `explorer`。提示词只写：先读 `skills/comment-sicko/SKILL.md`，再审这个范围。文档写明这不会变成单独的只读沙箱。
- **WorkBuddy 和 Claude Code。** `Agent`，`subagent_type: "Explore"`。提示词只写：先读 `skills/comment-sicko/SKILL.md`，再审这个范围。
