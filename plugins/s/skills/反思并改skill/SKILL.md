---
name: 反思并改skill
description: 在当前对话记录上同时派出三个审查子智能体，找出值得记住的经验，并把每一条都落实成对某个已有 skill 的具体修改。在用户说 reflect（反思）时使用。
disable-model-invocation: true
---

# 反思

从当前对话里挖出持久有用的经验，然后把它们落实成对 skill 的修改。

当用户说 “reflect” 或 “/反思并改skill” 时调用。如果对话很琐碎、跑题了，或者已经被一个已有 skill 覆盖、而父智能体也正确地照着做了，就跳过。一次性的事情不算经验。

## 1. 找到当前的对话记录

在分派之前，到系统提示词里写明的 `agent-transcripts/` 目录里，找到这次对话的记录。不要对 `~/.cursor/projects/*/` 用通配符。那样会越过工作区的边界，读到无关项目里的私密对话。

```bash
ls -t <agent-transcripts>/*.jsonl <agent-transcripts>/*/*.jsonl <agent-transcripts>/*/subagents/*.jsonl 2>/dev/null | head -10
```

这覆盖了旧的扁平布局（`<id>.jsonl`）、现在的嵌套布局（`<id>/<id>.jsonl`），以及子智能体的布局（`<parent>/subagents/<child>.jsonl`）。对每个候选文件，读 JSONL 的第一行。选那个 `message.content[0].text` 里包含这次对话开头那条用户提示词的文件。如果一个都对不上，就改为传入一份紧凑的会话摘要。

## 2. 同时派出三个审查者

一条消息，三个 `Task` 调用，`subagent_type: generalPurpose`，用智能体模式（`readonly: false`）。审查者需要 MCP 访问权限，去查对话记录里提到的工单、聊天线程和可观测性追踪记录，而 readonly 会去掉 MCP。

每个审查者和综合者都对应 `s-models.mdc` 规则里的一个角色行，以及一个默认值。把 `model` 设成那一行的值；如果这条规则或那一行不存在，就设成默认值。如果值是 `auto` 或 `inherit-parent`，就不设 `model`。如果 Task 工具拒绝某个模型名，就用默认的并说明一下。如果它连默认的也拒绝，就从它的报错信息里选同一系列中最接近的有效模型名。按 **poteto工作模式** skill 里 “Subagents” 一节的规定，为每个子智能体的任务选择推理等级，以及快速还是标准速度。

| 视角 | 角色行 | 默认 `model` | 提示词模板 |
|---|---|---|---|
| 判断（Judgment） | `reflect judgment, divergent, synthesizer` | `claude-opus-5-5-xhigh` | `references/judgment-reviewer.md` |
| 工具（Tooling） | `reflect tooling` | `grok-4.7-xhigh-fast` | `references/tooling-reviewer.md` |
| 发散（Divergent） | `reflect judgment, divergent, synthesizer` | `claude-opus-5-5-xhigh` | `references/divergent-reviewer.md` |

把每个模板原样传过去，在标明的地方替换成对话记录的路径或摘要。审查者在 `Task` 的回复正文里返回发现。

## 3. 综合

一个 `Task` 调用，`subagent_type: generalPurpose`，`model` 取自 `reflect judgment, divergent, synthesizer` 那一行（默认 `claude-opus-5-5-xhigh`），用智能体模式（`readonly: false`）。它会通过 MCP 抽查引用，而 readonly 会去掉 MCP。把 `references/synthesizer.md` 原样传过去，在标明的地方内联每个审查者的完整输出。它返回一份 Accepted / Rejected / Backlog 列表。

## 4. 结构化强制检查

如果某个 Accepted 条目用一条 lint 规则、一个脚本、一个元数据标记或一个运行时检查来强制执行会更可靠，就把它移到 Backlog。见 **encode-lessons-in-structure** 原则 skill。

## 5. 应用

把综合者完整的 Accepted / Rejected / Backlog 输出展示出来，在应用任何 Accepted 修改之前，等待用户明确批准。用户挑选其中一部分，也可能改变落实的去向。对 skill 的修改会影响组织里以后的每一个智能体。不要自动应用。

把每个 Backlog 条目提交到你们团队的开发体验（devex）或待办跟踪系统里，不用等待。只有 Accepted 列表需要等批准。

严格按照每一条已批准条目的 Routing（去向）来做：

- 对已有 skill 的小修改（一条一行的要点、收紧一句话、改正一个过时的事实）：父智能体直接做。
- 对已有 skill 的实质性修改（一个新的小节、一张新的模式表、超过大约 10 行）：交给 Cursor 自带的 `create-skill` skill，跑它的“起草 / 测试 / 迭代”循环。
- `tune description: <skill path>`（这个 skill 存在，但在该触发时没有触发）：交给 `create-skill`，跑它的描述优化循环。
- `new skill via create-skill: <kebab-name>`：把创建工作交给 `create-skill`。不要临时自己编一个形状。

如果你的环境带有 SKILL.md 校验工具，在宣布完成之前，对每个改动过的 skill 都运行一遍。

## 6. 给用户总结

简短的列表，不要开场白：

- 已应用的修改：`<skill path>`。改了什么，每条一行。
- 新建的 skill：`<skill path>`。每条一行（很少见）。
- 已提交到开发体验跟踪系统的待办：`<issue title>`（`<tags>`）。每条一行。
- 丢弃的：每个被拒绝的发现一行，附上综合者给的理由。
