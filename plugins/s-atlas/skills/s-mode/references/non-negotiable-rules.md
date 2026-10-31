调度表在 SKILL.md「不可商量的规则」。对上某一行之后，按下面的全文执行。文中的「自主」一节和「写回复」一节仍在 SKILL.md；写回复的细则在 writing-the-reply.md。

## 不可商量的规则

下面的 Principles（原则）一节是每个触发条件的依据。在你的回复里，点名每一条影响了某个决定的原则，以及它改变的那个具体选择。只引用你在这次会话里读过其末端 SKILL.md 的原则。

其余的触发条件：

- 不简单的改动、架构决定，或者“我们确定吗？” → **how** skill。
- 教我这个、讲讲这个子系统、帮我弄懂一块代码 → **how**（要动机再用 **why**）。已删除的 teach 不要再加载。
- 正要就“用哪种做法”、“我该怎么做”或“这个该做什么”这样的岔路去用向用户提问的工具（各软件里的名字见宿主适配参考）→ 问之前先分类。如果答案是一个你运行点什么就能观察到的事实（行为、时间、布局、输出、性能，甚至一个评估能不能区分出差别），那就不该由人来回答。按 Prototype playbook（`playbooks/prototype.md`）画个草图，让结果来决定。如果任务是一次只读的 Investigation（调查），交付物是一个带引用的答案，那就留在调查里，根据证据回答，而不是去做草图。只有在遇到任何实验都定不下来的、真正属于产品或偏好上的决定时，才去提问。在获得完全自主授权的情况下，对授权范围内的决定，直接做决定、照着做、并汇报，不要求回复，也不提供选项。在授权下，对于只有操作者才能做的决定，采用一个默认值，汇报时给出完整的解释，并用平实的话说明操作者可以让你改做什么。操作者用自己的话来回答。永远不要给一个让他照着输回来的简写口令。操作者点名的关卡，以及 Autonomy（自主）一节里“Always pause”（总要暂停）清单上的事，仍然需要操作者。
- 任何代码 → 先说出数据形状，并按 **principle-model-the-domain** 选择它的组织结构。
- 跨函数边界的代码 → **architect** skill，在实现之前做并行的设计探索。
- 并行分派 → 覆盖矩阵、比赛、连环检验和探索分区用 **swarm** skill。需要选基础、做嫁接的设计或代码比拼用 **arena**。
- 有争议的设计 → 上线之前用 **interrogate** skill（多模型对抗）。
- 不简单的多步骤工作 → 写下产出检查点（Feature 第 4 步）。
- 任何文字界面，包括你给用户的回复 → **unslop** skill。按 **Writing the reply**（写回复）来写回复。给智能体看的文字还要遵循 **author-skill**（`/author-skill`）。
- 文档、RFC、readme、PR 说明或提交信息的句子 → **technical-writing**。Word 用 **docx**，幻灯片用 **pptx**，表格用 **xlsx**，PDF 用 **pdf**。中英翻译用 **translate**。写提交说明或开 PR 的步骤用 **commit-pr**，句子仍按 **technical-writing**。分支怎么集成还没定时用 **finishing-a-development-branch**。
- 提交之前 → 代码里的 AI 腔用 **deslop**（`/deslop`）。文字用 **unslop**（`/unslop`）。两者不是同一件事。
- 已授权的实现清理阶段 → **no-comments** skill（`/no-comments`）。只读审查和调查跳过清理，直接报告发现；审查请求本身不授权修改。
- 上线界面 / IDE / 命令行工具 → 先自己在同一个界面上复现。界面用 **control-ui**（`/control-ui`），命令行用 **control-cli**（`/control-cli`）。某个软件缺哪一种能力，按那两份 skill 文末的说明来。回复里写明你实际跑了什么。只有在 Bug fix 第 1 步那个很窄的例外情况下，才交给用户。
- 运行基准测试、自己测量性能，或者报告一个你测出来的加速或退化 → 在报告这个数字或依据它行动之前，用 **benchmark-checklist** skill。
- 任何关于 PR 状态的请求（“babysit this”（照看一下）、“get it green”（让它变绿）、“address the bugbot comments”（处理 bugbot 的评论），以及最常见的 “check on PR X”（看看 PR X）或 “anything outstanding on X”（X 还有什么没处理的））→ **Babysit** playbook（`playbooks/babysit.md`），而不是软件自带的同名 babysit skill（如果你的软件有的话，比如 Cursor 就自带一个），那个 skill 的描述也匹配同样的词。仅仅是开了一个 PR，不会触发它。轮询之前先声明它的模式。playbook 的第 1 步负责把请求对应到模式。在一个阶段智能体里用 `drive`，会让那个智能体没法结束它的这一轮。
- 被要求合入或上线一串已经变绿的 PR → **Shipping** playbook（`playbooks/shipping.md`）。绿不等于安全。在每个 PR 得到独立的结论之前，什么都不能启动，而且只有从底部开始连续通过验证的那一段才会合入。
- Bugbot 或智能体安全审查留了评论 → 抱着怀疑的态度。它们能抓到真正的 bug，也会提出不是问题的问题和吹毛求疵的意见，所以要逐条按实际情况评估，用具体的理由驳回噪声，而不是反复改代码。按 `references/bugbot-triage.md` 分诊为修复 / 驳回 / 询问。
- 任务中途发现坏掉的 skill → 报告问题和影响。已授权修复时独立处理；只有已授权开 PR 时才创建 PR。不要悄悄绕过规则。
- 长时间的、自主的或多阶段的工作，或者任何用户离开、之后再回来审查的任务（“going to bed”（我去睡了）、“trust it when i'm back”（等我回来再信它）、“/loop until X” 或 “/timed-loop”（循环直到 X））→ 用 **show-me-your-work** skill 留一条决定记录。需要可审计记录且已授权提交时才提交，否则留在本地。
