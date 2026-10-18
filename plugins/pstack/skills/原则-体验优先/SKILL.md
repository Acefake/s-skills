---
name: 原则-体验优先
description: "在产品、用户体验或功能范围上需要取舍时使用。选择让用户满意，而不是让实现方便；宁可做少量打磨好的功能，也不要做很多粗糙的功能。"
disable-model-invocation: true
---

> 翻译自 pstack 插件（编号 9717366）的 `principle-experience-first` skill，原作者 Lauren Tan（版权 © 2026 Lauren Tan），许可证 MIT（全文见上一级文件夹的 `LICENSE-pstack`），仅供自用。插件版本 0.15.25，原项目：https://github.com/cursor/plugins/tree/main/pstack 。
> 说明：`disable-model-invocation: true` 表示这个 skill 只能由用户主动调用，AI 不会自己调用它。
> 英文名备份：s-principle-experience-first

# 体验优先

当实现上的方便和让用户满意冲突时，选让用户满意。

- 每一个功能、控件和选项都必须有存在的理由
- 做得少，做得好（打磨好的三个功能，胜过粗糙的十个功能）
- 先做原型再定下来（设计决定在用完即扔的 HTML 里试，比在正式代码里便宜）
- 把细节做对（过渡、对齐、间距、反馈、出错时的状态）
- 收紧核心流程（每个功能都应该服务于主要工作流程，否则就别挡路）

用户是任何使用这份工作成果的人。对界面来说，就是最终用户。对一个库或内部 API 来说，就是导入它的同事。下一个维护这份代码的工程师也是用户。用同样的方式考虑他们的体验，并且从他们的角度说明影响。

基础要为体验服务。Foundational thinking（基础优先思考）管的是工作的*顺序*。这条原则管的是*目标*。
