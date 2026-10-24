---
name: technical-writing
description: "写 README、写文档、审查技术文档、RFC、PR 说明或提交信息时用的分层标准。这是 Markdown 和技术说明，Word 文件用 docx。Use when writing or reviewing a README, technical documentation, an RFC, a PR description, or a commit message."
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。


# 技术写作

要写得让一个疲惫的工程师第一遍就能看懂。四层规则都要用上。

这里管 Markdown、README、RFC、设计说明、PR 说明和提交信息的句子。`.docx` 用 `docx`，幻灯片用 `pptx`，表格用 `xlsx`，PDF 用 `pdf`。把一段现成文字译成另一种语言用 `translate`。不要用这份标准去排 Word 的字体和修订。

有三条规则高于这四层：

- **删掉每一个不起作用的词。** 去掉某个词句子照样成立，这个词就删。"In order to" 就是 "to"。"It is important to note that" 等于什么都没说。
- **用简短、日常的词。** 用 "Use"，不用 "utilize"。用 "Help"，不用 "facilitate"。用 "Do"，不用 "perform"。一个长词必须用准确性来换它的长度。
- **当一条规则让句子变差时，换个方法改这个句子，或者干脆别动它。** 一个遵守了所有规则、却读起来像机器写的句子，是失败的。

代码库就是词表。写真实的符号、文件、参数（flag）或命令名，而不是它的同义词或描述。

不要自造行话。用开发者会说出口的词："move"、"delete"、"a budget that only decreases"（一个只会减少的额度），而不是 "evacuate"、"ratchet" 或 "endgame"。用一个有名字的模式没问题，只要文档第一次出现时说明它是什么意思。如果发现新的问题词和替代词，在你的回复里把它们作为对 `unslop` 的“抽象比喻”规则的补充提出来，并附上改动（diff）。不要直接编辑那个 skill。

## 让节奏有变化

一份文档可能遵守了每一层规则，读起来却还是像机器写的：每句话都剪得很短，没有任何观点，没有任何具体的东西。

- 有意地混用长短句。短句点明一个要点。长一点的句子带着一个事实以及它的条件或后果。
- 一句一个意思，不等于每句一样长。把装了两个意思的句子拆开。装一个意思的长句就留着。
- 在文档类型允许的地方表达观点。“解释”类文档要权衡取舍，所以说出你对这些取舍的看法，而不是罗列优缺点。“参考”类文档保持干巴巴的。
- 要具体，不要空泛。不说 "schema changes can cause issues"（结构改动可能引起问题），而说 "a column rename fails the build"（改一个列名会让构建失败）。

## 先选文档类型（Diátaxis）

一份文档，一种类型。两个问题决定选哪种：内容是指导行动（做）还是帮助理解（想）？是服务于学习还是工作？

- 行动 + 学习：**教程（tutorial）**。
- 行动 + 工作：**操作指南（how-to）**。
- 理解 + 工作：**参考（reference）**。
- 理解 + 学习：**解释（explanation）**。

这个“指南针”可以用在整份文档上，也可以用在一句话上。

**教程：边做边学。** 让学习者成功是你的责任，不是他的。开头说学习者会做出什么，而不是会“学到”什么。每一步都要产生看得见的结果，要早，要多。告诉他应该看到什么：预期的输出、提示符的变化、某一行日志。把解释删到一个从句加一个链接。保持具体。用“我们”，写成命令："First, do x. Now, do y."（首先做 x。现在做 y。）

**操作指南：达成目标的步骤。** 解决人遇到的问题，而不是机器能执行的某个操作。假设读者有能力，跳过教学。只写行动：不跑题，不讲背景，不为了完整而完整。这些内容用链接给出。允许分岔和判断："If you want x, do y."（如果你想要 x，就做 y。）用任务给指南命名："How to calibrate the radar array"（怎样校准雷达阵列），而不是 "Radar array calibration"（雷达阵列校准）。

**参考：供查阅的事实。** 只描述。没有指令，没有说服，没有观点。要干巴巴、完整、肯定。陈述事实、选项、限制和错误，不含糊其辞。照着被描述对象的结构来组织，让代码和文档可以对照着看。把内容放在读者预期的位置。能从代码生成的就从代码生成。

**解释：理解和原因。** 一个有边界的话题，离开产品也能读懂。每个标题前面都应该能默默加上一个 "About..."（关于……）。围绕一个真实的“为什么”问题展开。提供背景：设计决定、历史、限制条件、替代方案。只有这里可以有观点，其他地方都不行。

不要混用类型：教程里不放参考表格，参考里不手把手教，操作指南里不争论。改为拆开并互相链接。

## 写给读者的句子（Google 开发者风格）

- 用 "you"（你）称呼读者，用现在时。只有真正以后才会发生的事才用 "will"。
- 说清谁做什么："the compiler checks"（编译器检查），而不是 "is checked"（被检查）。只有执行者不知道或无关紧要时，才可以用被动句。
- 把指令写成命令："Click Submit."（点击 Submit。）平实地陈述事实。绝不写 "should be done"（应该被完成）。
- 把条件放在指令前面："To delete the document, click Delete."（要删除文档，点击 Delete。）
- 先写常见情况。例外放在后面。
- 听起来像一个懂行的朋友。不用流行词，不用修辞手法，指令里不加 "please"，步骤里绝不写 "simply"、"easy" 或 "quickly"。要是真那么简单，读者就不会来看了。
- 不要预告（"we will soon support..." 我们很快会支持……），也不要让连续几句话用同样的短语开头。
- 链接文字要说明链接去哪里：页面标题或简短描述。绝不写 "click here"（点击这里）。与其链接到别处，不如在本页加一句背景说明。
- 标题要带出要点，而不只是话题（"Pick the mode first"（先选类型），而不是 "Modes"（类型））。用句首大写（sentence case）。任务类标题是一个单纯的动词短语（"Create an instance"）。概念类标题是一个名词短语。每页只有一个 h1，标题层级不跳级。
- 有先后顺序的用编号列表，其他的都用圆点列表。用一个完整的句子引出列表。各项保持结构一致。
- 代码用代码字体。界面元素用粗体。使用序列逗号（serial comma，列举三项以上时最后一个 and 前也加逗号）。不要写 "etc."，而是在一开始就说明这个列表不完整。

## 让陈述一次只装一件事（STE 规则）

- 一句话一条指令。其他地方一句话一个意思。
- 指令超过大约 20 个词、其他句子超过大约 25 个词，就拆开。
- 把警告或条件放在它要防护的那一步之前："If hot oil touches your skin, injuries can occur."（如果热油碰到皮肤，会造成伤害。）
- 保留 "the" 和 "a"："Remove backup file" 可以有两种理解。"Remove the backup file" 只有一种。
- 每个词只给一个意思、一个用途，然后一直保持。如果 "check" 表示检查，就不要再用它表示约束。
- 每种动作只选一个词并坚持用它：都用 "start"，而不是这里用 "start"、那里用 "initiate"。
- 把操作步骤写成直接的命令，绝不写成叙述，也绝不用被动："Install the component"（安装组件），而不是 "the component must be installed"（组件必须被安装）。
- 能避免就避免用 "-ing" 结尾的词。

## 不让任何句子有两种理解（Global English）

- 把 "only" 和 "not" 这类词紧挨着它修饰的词："only fails on growth" 和 "fails only on growth" 意思不一样。
- 拆开一长串名词："the proto import budget check script" 改成 "the script that checks the proto-import budget"。
- 让每个 "it"、"they" 和 "this" 都指向一个明显的东西。拿不准就重复那个名词。绝不要用 "this" 或 "which" 指代一整个从句。
- 不要省略动词："Phase 1 moves the converters and Phase 2 the runtime" 让 Phase 2 没有动词。给它加一个。
- 保留表示结构的小词，比如 "Ensure that the switch is off" 里的 "that"。绝不要为了少几个字牺牲清晰。
- 列举时如果能防止误读，就重复冠词：当它们是两样东西时，写 "the client and the host"，而不是 "the client and host"。
- 当一个句子可以有两种分组方式时，说清 "and" 或 "or" 连接的是哪几部分。"Both...and"、"either...or" 和 "if...then" 是不花成本的消歧义方法。
- 用句号，不用分号。把破折号（em dash）换成一个新句子。
- 括号里的文字要么是一个完整的语法单位，要么单独成句。绝不用 "(s)" 表示复数。
- 不用斜杠：写 "a, b, or both"，而不是 "a/b" 或 "and/or"。
- 每样东西在所有地方都只用一个名字。一份文档用 "the gate"、"the ratchet" 和 "the budget check" 指同一个东西，等于教了三样东西。没变的东西不要换着叫。
- 不用习语、口语、拉丁缩写和比喻。

## 语气和仓库方面的具体规定

- 这个 skill 处理的每一份文档，都要用 **unslop** skill 过一遍。那个 skill 负责“AI 腔”问题清单：AI 爱用的词、废话、含糊其辞、格式上的痕迹。
- PR 说明和提交信息也是写作。除了 Diátaxis，每一层都适用于它们。一份 PR 正文是一份审查者一分钟内能读完的简报。不要贴大批子智能体（swarm）的日志、SHA 列表或指标表格。给链接。
- 产品界面上的文字不是文档。那些要用你们产品自己的文案规范。
- 代码片段用 tab 缩进。写真实的路径。每一个关于数量或目录树的说法，在合入它的那次提交里都必须是真的，并附上重新生成它的命令。

## 实例

修改前：

> Configuration of the proto import ratchet budget script parameters is performed via budget.json. Note that it's important to remember that running with --write, which updates the committed budget to reflect the current count, should only be done when lowering it. If exceeded, CI fails.

（意思大致是：“proto 导入棘轮额度脚本参数的配置通过 budget.json 来执行。注意，重要的是要记住，带 --write 运行（它会更新已提交的额度以反映当前数量）只应该在降低额度时进行。如果超出，CI 会失败。”——又长又绕，用了行话 ratchet，还有被动句。）

修改后：

> `budget.mjs` reads the committed budget from `budget.json` and counts the files that import protos. If the count exceeds the budget, CI fails. Run `budget.mjs --write` only to lower the budget.

（意思：“`budget.mjs` 从 `budget.json` 读取已提交的额度，并统计导入了 proto 的文件数。如果数量超过额度，CI 就失败。只在要降低额度时运行 `budget.mjs --write`。”）
