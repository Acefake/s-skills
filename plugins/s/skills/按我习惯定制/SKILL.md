---
name: 按我习惯定制
description: "用于“automate me（把我自动化）”、“创建/更新/刷新我的 -mode skill”、“把我的偏好或工作方式变成/记录成一个 skill”，或者希望智能体按用户的工作方式来做事时。起草或修改一个个人专属的 -mode skill，用清理AI腔收文字，可选择从最近的对话记录里提取新的证据。"
disable-model-invocation: true
---

# 把我自动化（Automate me）

一个有引导的流程，把用户的工作习惯变成一个智能体会遵守的 skill。产出是一个为他量身定做的 `-mode` skill（例如 `jay-mode`、`priya-mode`）。

这个 skill 协调两样东西：一轮直接进行的挖掘（见第 1 步），以及 **清理AI腔** skill（负责文字规范）。编写 SKILL.md 那一步用 **编写skill**（`/编写skill`）。它安排先后顺序，不代替这些步骤。

## 流程

### 0. 检查有没有已有的 skill

查找和用户代号匹配的 `*-mode/SKILL.md`。Cursor 看 `.cursor/skills/` 和 `~/.cursor/skills/`。Claude Code 看 `.claude/skills/` 和 `~/.claude/skills/`。WorkBuddy、Codex、OpenCode 的个人 skill 目录这里不确定，再在当前仓库里搜 `*-mode/SKILL.md`。mode skill 可能放在个人分类目录里，不一定在最顶层。如果已经有一个，就用这个软件的提问工具确认意图（名字见 poteto工作模式 文末的表；没有这种工具就在对话里问）。除非用户已经说了“更新我的 skill”之类的话：

- 更新已有的 skill（重复运行时的默认选项）
- 从头重新做（很少见，做之前先问为什么）

更新模式会改变后面的流程：
- 第 1 步只挖掘这个 skill 上次修改之后的历史（`git log -1 --format=%cI <path>`）。
- 第 2 步问的是哪些变了或缺了，而不是从零开始要记录什么。
- 第 4 步直接编辑已有的文件。保留用户没有否定的部分。有新证据的部分就修改。只有真正的新规则才加新章节。

### 1. 挖掘他的历史

在分头挖掘之前，先找到当前工作区的对话记录。系统提示里写明了这个工作区的 `agent-transcripts/` 目录。只用那个路径。不要对 `~/.cursor/projects/*/` 用通配符搜索。那样会越过工作区的边界，读到无关项目里的私人聊天。

在这个范围内，查看最近的智能体对话，找出反复出现的模式。把历史切成几片，同时派多个子智能体去挖掘（例如最近 2-4 周，分成 3 片，每片都有足够的材料）。按 **poteto工作模式** skill 里 “Subagents” 一节的规定，为每个子智能体的任务选择推理等级，以及快速还是标准速度。每个负责一片的挖掘子智能体，从上层提供的、限定在工作区内的路径读取对话记录，寻找下面这些信号，并返回一份简短的结构化清单，列出它看到的模式和证据出处。默认值得寻找的信号：

- 回复偏好（长度、语气、格式、“说简单点”之类的纠正）
- 分派习惯（子智能体、模型、专门的工作流程、并行）
- 验证态度（“完成”指什么、单元测试还是真实复现、审查者）
- 代码和文字规范（风格、引用的原则、lint/格式化工具）
- 流程习惯（worktree、提交、PR、审查/合并工具）
- 元偏好（在任务中途修 skill、提议新 skill）

在把一个信号提升为规则之前，先在各片之间交叉核对。在 2 片或更多片里都出现的模式，可信度高。只出现一次的信号很弱，通常会被丢掉。

### 2. 直接问用户

挖掘会漏掉那些还没出现过的意图。用这个软件的提问工具做结构化的多选题（名字见 poteto工作模式 文末的表）。没有这种工具，就在对话里列出选项。不要让用户从零开始打字。

形式：一两个问题，每个 4-6 个选项，分类问题用 `allow_multiple: true`（允许多选）。先问大的（“哪些方面最重要？”），再针对用户选中的方面，给出具体选项继续问。结构化的几轮问完后，再在聊天里问一个开放式问题，补上选项漏掉的东西。

不要一下子甩出 20 个问题。

### 3. 把发现归类

把收集到的所有信号分成几个章节。常见的有这些（只用适用的）：

- **回复风格（Response style）**：长度、语气、格式。
- **自主程度（Autonomy）**：不问就做多少事、MCP 工具的使用。
- **先弄懂（Understand first）**：确定范围或调查一个改动时用哪些 skill。
- **子智能体（Subagents）**：默认做法、并行、什么模型做什么任务、专门的工作流程。
- **文字/代码规范（Prose / code discipline）**：原则、lint 工具、风格指南。
- **审查和验证（Review and verify）**：复现态度、验证类 skill、实时测试工具。
- **流程（Process）**：git worktree、提交、PR、审查/合并工具。
- **Skills**：写 skill 的习惯、先修 skill、提议新 skill。

**poteto工作模式** skill 展示了大致的样子。读它来把握粒度。不要照抄它的内容。用户的规则和 poteto工作模式 的不一样。

### 4. 起草 skill

编写那一步跑 `/编写skill`。放置方式：

- 路径：保留已有 mode skill 所在的位置。新的 mode：Cursor 放 `.cursor/skills/<handle>-mode/SKILL.md`，用户要个人 skill 就放 `~/.cursor/skills/<handle>-mode/`。Claude Code 对应 `.claude/skills/` 和 `~/.claude/skills/`。WorkBuddy、Codex、OpenCode 的个人目录这里不确定，先写仓库里的 `skills/<handle>-mode/SKILL.md`，并告诉用户按该软件的方式加载。不要假装写进某个没确认过的家目录就会自动生效。
- 代号（handle）：用户的名字，或者他选的标识。
- Frontmatter 的 `description`：在用户的名字 + `/<handle>-mode` + “按他的风格工作” 时触发，而不是在 “写代码” 或 “审查 PR” 这类通用关键词上触发。
- Frontmatter 至少要有 `name` 和 `description`。`description` 保持为一个 YAML 值。当标点或换行需要时，给它加引号，或者用 `description: >-` 加缩进的续行。
- Frontmatter 默认写 `disable-model-invocation: true`。只有用户明确希望他的 mode 每一轮都生效时，才去掉。

### 5. 反复打磨文字

对每一行都用上 **清理AI腔** skill。软件自带的编写 skill 如果还有写作指南，也照着做。

把草稿给用户看，接受反馈。要做好多次修改的准备。狠心地删。mode skill 不是一本使用手册。

### 6. 落地

在一个从 main 分出来的 worktree 里工作。提交并开一个 PR。不要直接推送到 main。

## 防护规则

- **不要只根据一次对话下结论。** 说过一次、另一次又被推翻的偏好是噪音。要多次出现才能写成规则。
- **不要耍小聪明。** 复述其他 skill 的内容、自造比喻、给智能体读者写“诗意”的文字，只有成本没有好处。保持可操作。
- **引用，不要内嵌。** 用户依赖的其他 skill，应该以路径引用的形式出现，而不是贴摘录。他在别处维护的原则文档也一样。
- **章节越少越好。** 只有当用户在某方面有具体的、和默认不同的规则时，才加这一节。“沟通要清楚”不算一节。“段落要短。比较选项时用表格。只有各项真正并列时才用圆点列表。”才算。
- **规则里的称呼要通用。** 祈使句里用 “the user”（用户）或 “the human”（人类），不用作者的名字。
- **不要硬凑对称。** 如果用户没有值得写下来的流程规则，就整个跳过“流程”这一节。

## 评估

`-mode` skill 是主观的产出。编写 skill 那种“测试/迭代”的基准循环在这里没什么用。和用户一起凭感觉检查：读起来像他吗？漏了什么吗？然后就发布。

只有当这个 skill 的触发准确度在实际使用中确实成了问题时，才去做一轮描述（description）优化。

## 什么时候不用

- 用户想要一个针对具体任务的 skill（而不是工作习惯）：不用挖掘。跑 `/编写skill`。
- 用户想记录一个很窄的流程（例如“我是怎么写提交信息的”）。那是一个普通 skill，不是 mode skill。

## 在不同软件里怎么用

提问工具和「写 SKILL.md」那一行，以 [poteto工作模式](../poteto工作模式/SKILL.md) 文末的表为准。挖掘时的并行子智能体也按那张表里 Cursor、OpenCode、Codex 的派法：Cursor 用 `Task`、`subagent_type: generalPurpose`、`readonly: true`，模型用较快的写代码模型（`grok-4.7-xhigh-fast` 这次可用才用这个名字）；OpenCode 用 `subagent` 加 `background: true`，内置 `explore` 或 `s-how-explorer`；Codex 用话派，点名一个这次账号里真有的较快模型，等齐再汇总。WorkBuddy 用 `Explore`，Claude Code 用 `Explore`。

Cursor 的 skill 目录是 `.cursor/skills/` 和 `~/.cursor/skills/`。Claude Code 是 `.claude/skills/` 和 `~/.claude/skills/`。WorkBuddy、Codex、OpenCode 的个人 skill 目录这里不确定，新文件先放在仓库的 `skills/<代号>-mode/SKILL.md`。编写用 `/编写skill`。文字用 **清理AI腔**。
