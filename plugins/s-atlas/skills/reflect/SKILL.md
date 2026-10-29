---
name: reflect
description: "「/reflect」「把这次教训写进技能」。派三个审查者，把经验改成对现有 skill 的具体修改。Use when this conversation produced a lesson that should be written into an existing skill."
disable-model-invocation: true
---

本会话首次使用本库技能时，按[全局提示词自检](../setup-s-instructions/references/daily-check.md)只读检查一次。
## 运行环境适配

涉及宿主工具、模型配置或子代理时，按需阅读[宿主适配](../../HOSTS.md)。


# 反思

日常轻量经验建议与确认后保存用 [learn](../learn/SKILL.md)。本技能仍只在点名时深度复盘；不因学习建议而自动启动本流程。

从当前对话里挖出持久有用的经验，然后把它们落实成对 skill 的修改。

当用户说 “reflect” 或 “/reflect” 时调用。如果对话很琐碎、跑题了，或者已经被一个已有 skill 覆盖、而父智能体也正确地照着做了，就跳过。一次性的事情不算经验。

## 1. 找到当前的对话记录

在分派之前，到系统提示词里写明的 `agent-transcripts/` 目录里，找到这次对话的记录。不要对 `~/.cursor/projects/*/` 用通配符。那样会越过工作区的边界，读到无关项目里的私密对话。

```bash
ls -t <agent-transcripts>/*.jsonl <agent-transcripts>/*/*.jsonl <agent-transcripts>/*/subagents/*.jsonl 2>/dev/null | head -10
```

这覆盖了旧的扁平布局（`<id>.jsonl`）、现在的嵌套布局（`<id>/<id>.jsonl`），以及子智能体的布局（`<parent>/subagents/<child>.jsonl`）。对每个候选文件，读 JSONL 的第一行。选那个 `message.content[0].text` 里包含这次对话开头那条用户提示词的文件。如果一个都对不上，就改为传入一份紧凑的会话摘要。

## 2. 同时派出三个审查者

一条消息，三个子智能体，用能访问 MCP 的类型。会去掉 MCP 的只读模式不要用。审查者要去查对话记录里提到的工单、聊天线程和可观测性追踪记录。

每个审查者和综合者都对应 s 模型配置里的一个角色行。路径见文末。把模型设成那一行的值。没有这一行，判断和发散用更强的模型，工具视角用较快的写代码模型。值是 `auto` 或 `inherit-parent`，或者软件不能指定模型，就不设。软件拒绝了某个名字，就换同一系列里它接受的最接近的名字，并说一句。按 **s-mode** skill 里 “子智能体” 一节的规定，为每个子智能体的任务选择推理等级，以及快速还是标准速度。

| 视角 | 角色行 | 没有配置、而且软件能指定模型时 | 提示词模板 |
|---|---|---|---|
| 判断（Judgment） | `reflect judgment, divergent, synthesizer` | 判断力最强的模型。Cursor 上、并且 `claude-opus-5-5-xhigh` 可用时可以用这个名字 | `references/judgment-reviewer.md` |
| 工具（Tooling） | `reflect tooling` | 较快的写代码模型。Cursor 上、并且 `grok-4.7-xhigh-fast` 可用时可以用这个名字 | `references/tooling-reviewer.md` |
| 发散（Divergent） | `reflect judgment, divergent, synthesizer` | 同判断 | `references/divergent-reviewer.md` |

把每个模板原样传过去，在标明的地方替换成对话记录的路径或摘要。审查者在子智能体的回复正文里返回发现。派不出三个子智能体时，在主对话里按三个视角各写一遍，并说一句没有换模型。

## 3. 综合

再派一个子智能体，类型同样要能访问 MCP。模型取自 `reflect judgment, divergent, synthesizer` 那一行。没有这一行，或软件不能指定模型，就按上一节的规则。把 `references/synthesizer.md` 原样传过去，在标明的地方内联每个审查者的完整输出。它返回一份 Accepted / Rejected / Backlog 列表。

## 4. 结构化强制检查

如果某个 Accepted 条目用一条 lint 规则、一个脚本、一个元数据标记或一个运行时检查来强制执行会更可靠，就把它移到 Backlog。见 **principle-encode-lessons-in-structure** 原则 skill。

## 5. 应用

把综合者完整的 Accepted / Rejected / Backlog 输出展示出来，在应用任何 Accepted 修改之前，等待用户明确批准。用户挑选其中一部分，也可能改变落实的去向。对 skill 的修改会影响组织里以后的每一个智能体。不要自动应用。

Backlog 默认输出为待办草稿。只有用户已授权写入指定跟踪系统时才创建条目，并报告实际链接；授权不足或工具不可用时保留草稿，不声称已提交。Accepted 的应用仍按上面的批准范围执行。

严格按照每一条已批准条目的 Routing（去向）来做：

- 对已有 skill 的小修改（一条一行的要点、收紧一句话、改正一个过时的事实）：父智能体直接做。
- 对已有 skill 的实质性修改（一个新的小节、一张新的模式表、超过大约 10 行）：跑 `/author-skill` 做起草、测试、迭代。保留原有的 YAML `name` 和 `description`，改完用 **unslop** 过一遍文字。
- `tune description: <skill path>`（这个 skill 存在，但在该触发时没有触发）：用 `/author-skill` 做描述优化。只改 `description`，让它覆盖用户实际会说的那句话，改完读一遍确认没有把正文的触发条件写丢。
- `new skill: <kebab-name>`：交给 `/author-skill`。YAML 里写 `name` 和 `description`，正文照已有 skill 的形状写，再用 **unslop**。

如果你的环境带有 SKILL.md 校验工具，在宣布完成之前，对每个改动过的 skill 都运行一遍。

## 6. 给用户总结

简短的列表，不要开场白：

- 已应用的修改：`<skill path>`。改了什么，每条一行。
- 新建的 skill：`<skill path>`。每条一行（很少见）。
- 已提交到开发体验跟踪系统的待办：`<issue title>`（`<tags>`）。每条一行。
- 丢弃的：每个被拒绝的发现一行，附上综合者给的理由。

## 宿主适配

判断、发散和综合读 `reflect judgment, divergent, synthesizer`，工具视角读 `reflect tooling`。配置路径以 [setup-s-models](../setup-s-models/SKILL.md) 为准。三个审查者一条消息里同时派，等齐再派综合者。类型要能访问 MCP。写 SKILL.md 用 `/author-skill`。Claude Code、Codex、Cursor 按那份 skill 文末的目录说明放置。

Codex、Claude Code、Cursor 的工具和配置见[宿主适配](../../HOSTS.md)；按当前宿主读取对应参考。

### 派不出三个子智能体

在主对话里按三个视角各写一遍，并说一句没有换模型。
