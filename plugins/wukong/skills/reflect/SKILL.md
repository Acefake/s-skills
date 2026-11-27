---
name: reflect
description: "「/reflect」「把这次教训写进技能」「把这条记成我的规则」「/reflect --me」「更新我的个人规则」。把对话教训沉淀到现有 skill（单条小改走快路，长会话复盘派三视角审查），或按个人模式即时记录/从日志归纳个人规则。Use when a lesson should be written into an existing skill, or the user wants to record a personal rule immediately or update, show, undo, or remove personal rules learned from the local journal."
disable-model-invocation: true
---

本会话首次使用本库技能时，按[全局提示词自检](../wukong-init/references/daily-check.md)只读检查一次。
## 运行环境适配

涉及宿主工具或子代理时，按需阅读[宿主适配](../../HOSTS.md)。

# 反思

从当前对话里挖出持久有用的经验，按范围落到个人规则或现有 skill。

当用户说 “reflect” 或 “/reflect” 时调用。先按场景选路径：

1. **个人模式（即时记一条 / 跨会话归纳）**：带 `--add`、`--me`、`--show`、`--undo`、`--forget`、`--off`、`--on`，或用户说「把这条记成我的规则」「以后记住……」「更新 / 查看 / 撤销 / 删掉 / 关掉我的个人规则」时，不派子代理、不改任何 skill，直接按[个人模式](references/personal.md)执行（下面的第 1～6 步都不适用）。
2. **小教训快路（对现有 skill 的单条小改）**：意图明确的单条教训、刚解决的环境/配置坑，且只涉及单个已知 skill 的小改动（约 10 行以内）时，跳过下面的 3 审查者 + 综合者流程，主会话直接起草改动并按第 5～6 步展示给用户批准后落实。
3. **深度复盘（长会话 / 多问题 / 拿不准去向）**：按下面第 1～6 步派三视角审查者并综合。

如果对话很琐碎、跑题了，或者已经被一个已有 skill 覆盖、而父智能体也正确地照着做了，就跳过。一次性的事情不算经验。沉淀每条技能或个人规则前，先核对它的**生效条件与例外边界**——怎么写才不会在正常场景下误伤，避免规则越积越僵。

## 1. 找到当前的对话记录

在分派之前，定位本次对话的记录文件；只读当前会话或当前工作区的记录，不要用通配符跨工作区扫描其他项目的私密对话：

- **Antigravity**：直接使用当前会话的 `transcript.jsonl`（`<appDataDir>/brain/<conversation-id>/.system_generated/logs/transcript.jsonl`），按 `type: "USER_INPUT"` 与 `content` 核对开头提示词。
- **Claude Code / Codex**：到系统提示词写明的 `agent-transcripts/` 或当前会话记录目录，按扁平（`<id>.jsonl`）、嵌套（`<id>/<id>.jsonl`）或子代理布局（`<parent>/subagents/<child>.jsonl`）找到最近文件（macOS/Linux 可用 `ls -t ... | head -10`，Windows 用 PowerShell `Get-ChildItem ... | Sort-Object LastWriteTime -Descending | Select-Object -First 10`），读首行核对开头用户提示词。

如果都对不上或路径不可读，改为传入一份紧凑的会话摘要。

## 2. 同时派出三个审查者

一条消息，三个子智能体。只有当对话记录里实际提到外部工单、聊天线程或可观测性追踪时，才选用能访问 MCP 的类型；纯本地代码、配置或技能复盘直接使用只读子代理类型即可。

模型按[公共派发规则](../executing-plans/references/subagents.md#模型)：判断、发散和综合是「规划」角色，工具视角是「审查」角色。没有模型块时，判断和发散用更强的模型，工具视角用较快的写代码模型；软件不能指定模型就不设，继承父会话。软件拒绝了技能默认名，就换同一系列里它接受的最接近的名字并说一句；拒绝了模型块角色名或用户点名时按[公共派发规则](../executing-plans/references/subagents.md#模型)处理。

| 视角 | 没有模型块、而且软件能指定模型时 | 提示词模板 |
|---|---|---|
| 判断（Judgment） | 判断力最强的模型 | `references/judgment-reviewer.md` |
| 工具（Tooling） | 较快的写代码模型 | `references/tooling-reviewer.md` |
| 发散（Divergent） | 同判断 | `references/divergent-reviewer.md` |

把每个模板原样传过去，在标明的地方替换成对话记录的路径或摘要。审查者在子智能体的回复正文里返回发现。派不出三个子智能体时，在主对话里按三个视角各写一遍，并说一句没有换模型。

## 3. 综合

再派一个子智能体（按第 2 步同样的原则，仅在需要核查外部系统时选带 MCP 的类型）。模型同判断视角。把 `references/synthesizer.md` 原样传过去，在标明的地方内联每个审查者的完整输出。它返回一份 Accepted / Rejected / Backlog 列表。

## 4. 结构化强制检查

如果某个 Accepted 条目用一条 lint 规则、一个脚本、一个元数据标记或一个运行时检查来强制执行会更可靠，就把它移到 Backlog。见 [encode-lessons-in-structure](../code-style/references/principles/encode-lessons-in-structure.md) 原则。

## 5. 应用

把综合者完整的 Accepted / Rejected / Backlog 输出展示出来，在应用任何 Accepted 修改之前，等待用户明确批准。用户挑选其中一部分，也可能改变落实的去向。对 skill 的修改会影响组织里以后的每一个智能体。不要自动应用。

Backlog 默认输出为待办草稿。只有用户已授权写入指定跟踪系统时才创建条目，并报告实际链接；授权不足或工具不可用时保留草稿，不声称已提交。Accepted 的应用仍按上面的批准范围执行。

严格按照每一条已批准条目的 Routing（去向）来做：

- 对已有 skill 的小修改（一条一行的要点、收紧一句话、改正一个过时的事实）：父智能体直接做。
- 对已有 skill 的实质性修改（一个新的小节、一张新的模式表、超过大约 10 行）：跑 `/author-skill` 做起草、测试、迭代。保留原有的 YAML `name` 和 `description`，改完按[去 AI 腔清单](../technical-writing/references/unslop.md)过一遍文字。
- `tune description: <skill path>`（这个 skill 存在，但在该触发时没有触发）：用 `/author-skill` 做描述优化。只改 `description`，让它覆盖用户实际会说的那句话，改完读一遍确认没有把正文的触发条件写丢。
- `new skill: <kebab-name>`：交给 `/author-skill`。YAML 里写 `name` 和 `description`，正文照已有 skill 的形状写，再按[去 AI 腔清单](../technical-writing/references/unslop.md)过一遍。

如果你的环境带有 SKILL.md 校验工具，在宣布完成之前，对每个改动过的 skill 都运行一遍。

## 6. 给用户总结

简短的列表，不要开场白：

- 已应用的修改：`<skill path>`。改了什么，每条一行。
- 新建的 skill：`<skill path>`。每条一行（很少见）。
- 已提交到开发体验跟踪系统的待办：`<issue title>`（`<tags>`）。每条一行。
- 丢弃的：每个被拒绝的发现一行，附上综合者给的理由。

## 宿主适配

深度复盘时三个审查者一条消息里同时派，等齐再派综合者；纯本地复盘优先用只读子代理，需查外部系统时才选带 MCP 的类型。写 SKILL.md 用 `/author-skill`。Claude Code、Codex、Antigravity 按那份 skill 文末的目录说明放置。

Codex、Claude Code、Antigravity 的工具和配置见[宿主适配](../../HOSTS.md)；按当前宿主读取对应参考。

### 派不出三个子智能体

在主对话里按三个视角各写一遍，并说一句没有换模型。
