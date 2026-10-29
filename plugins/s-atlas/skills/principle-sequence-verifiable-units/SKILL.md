---
name: principle-sequence-verifiable-units
description: "「拆成小步」「一步一验」「按什么顺序交」。批量清理、迁移或一串相似改动，每步停在可验证的状态。Use when multi-step work should be split into units you can verify one at a time."
disable-model-invocation: false
---

本会话首次使用本库技能时，按[全局提示词自检](../setup-s-instructions/references/daily-check.md)只读检查一次。
# 把工作排成可验证的单元

把工作排成一连串小单元，每个单元结束时都处在一个你能检查的状态；当前单元没变绿（通过）之前，不要往前走。

**为什么：** 在引起问题的那个单元就发现的破坏，定位起来很便宜。一批做完才发现的破坏会被埋住，而你已经在坏掉的基础上又往上搭了东西。把同样这些单元排成一份审查者可以重放的交付，就把“相信我”变成了“看它先变红，再变绿”。

**执行。** 在批量清理、迁移或任何一连串相似的改动里，每改一处都先验证，再开始下一处。先记录当前提交和已有工作区修改，作为比较基线；只有任务已授权整理分支时才 rebase，保留无关的未提交工作。验证强度按 s-router 分档，第0档只检查 diff。脚本完成的改动同样需要相应检查。

**交付。** 已授权提交或开 PR 时，按能证明工作的顺序组织改动。适用 TDD 时，可先放会失败的测试，再放修复；其他情况按实际验证方式组织。也可以先做减法再重塑、先记录基线再做处理。未授权提交时保留工作区修改，不因本原则自动提交。

这是 **principle-prove-it-works** 原则 skill（保证每个检查都是真实的）和 **principle-build-the-lever** 原则 skill（让每个单元的检查变便宜）在排序方面的补充。
