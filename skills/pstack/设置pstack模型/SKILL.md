---
name: 设置pstack模型
description: "配置 pstack 在每个角色上用哪个模型、用多大的推理预算。检测你可用的模型，并写一条始终生效的规则，覆盖 skill 里的默认值。用于 /设置pstack模型、“配置 pstack 模型”、“pstack 预算”，或者修改 pstack 的模型选择。"
---

> 翻译自 pstack 插件（编号 9717366）的 `setup-pstack` skill，原作者 Lauren Tan（版权 © 2026 Lauren Tan），许可证 MIT（全文见上一级文件夹的 `LICENSE-pstack`），仅供自用。插件版本 0.15.25，原项目：https://github.com/cursor/plugins/tree/main/pstack 。
> 说明：这个 skill 没有 `disable-model-invocation`，AI 可以自己调用它。文中引用其他 skill 的地方（链接、加粗或反引号里的名字、`/命令`）已经换成这个中文名版里的中文名，链接也指向对应的中文名文件夹；没翻译的 skill 保持原名。中英文名对照见 README 的“中文名对照表”。代码块里的规则文件模板保持英文原样（角色名要和 poteto工作模式 用的一致）。模型名（slug，如 `claude-opus-5-5-xhigh`）和选项标签保持原样。AskQuestion 是向用户提选择题的工具。
> 英文名备份：s-setup-pstack

# 设置 pstack

写出 `~/.cursor/rules/pstack-models.mdc`，这是一条始终生效的规则，用来设定 pstack 在每个角色上用的模型。

## 步骤

### 1. 检测可用的模型

列出在这次会话里你可以传给 `Task` 子智能体的模型名（slug）。这是可靠的来源。如果 Cursor 还提供了能列出用户有权使用的模型的 API 或命令行工具，为了完整，优先用它。如果你一个也检测不到，就请用户把他有权限的模型名贴过来。永远不要写一个你没确认可用的真实模型名。别名 `inherit-parent` 和 `auto` 总是有效的，尽管它们不是检测出来的模型名。

### 2. 加载当前状态

默认的“角色到模型”的对应关系，就是下面第 5 步里展示的规则形状。如果 `~/.cursor/rules/pstack-models.mdc` 已经存在，就读它，把它的 `# budget` 行和各个角色的值当作当前的选择。否则就从那些默认值开始。如果某一行的角色不在第 5 步里，比如 `how critics`，那就是一个已经停用的角色。删掉它。

### 3. 预算、对应和确认

**(a) 询问预算。** 优先用 AskQuestion，而不是让用户自由输入。提供下面这四个选项，标签一字不改；如果规则里记录了当前的预算，就说出来。如果没有规则，就说明 `large` 和 skill 的默认值一致。

- `unlimited — max reasoning`（不限，最大推理）
- `large — xhigh reasoning`（大，很高推理）
- `medium — high reasoning`（中，高推理）
- `small — medium reasoning`（小，中等推理）

**(b) 应用预算。** 从 skill 的默认值建立工作用的表格；如果是重新运行，保留你按系列、列表或别名（`inherit-parent`、`auto`）改过的任何角色。`unlimited`、`large`、`medium` 和 `small` 会把每个真实模型名（包括评审组里的条目）的推理强度标记分别设为 `max`、`xhigh`、`high` 或 `medium`。推理强度标记是模型名的最后一段，或者如果最后是 `fast`，就是它前面那一段；强度的阶梯是 `max` > `xhigh` > `high` > `medium` > `low`。如果结果不是一个检测到的模型名，就用同一系列中、强度不超过目标的最高强度的已检测模型名；否则就把这个角色标为“需要选择”。`inherit-parent` 和 `auto` 不变。所以 `unlimited` 会把 `claude-opus-5-5-xhigh` 变成 `claude-opus-5-5-max`。Grok 的模型名最高只到 `xhigh`，所以在 `unlimited` 下，回退规则会让 Grok 停在 `xhigh`，`grok-4.7-xhigh-fast` 保持原样。`large` 让两个默认值都不变。`small` 把它们变成 `claude-opus-5-5-medium` 和 `grok-4.7-medium-fast`。

**(c) 展示各个角色并确认。** 展示每个角色和它的模型，把不在检测结果里的真实模型名标为“需要选择”。同时列出第 2 步删掉的每一行。问用户是原样接受，还是要修改某些角色，选项是检测到的模型，加上 `inherit-parent` 和 `auto`（两者的意思都是：这个角色用父级聊天的模型运行，用 Auto 的用户就是这样保持在 Auto 上的）。优先用 AskQuestion，而不是让用户自由输入。对于评审组类的角色（arena runners、architect runners、interrogate reviewers），值是一个列表，每个条目（包括别名条目）运行一个子智能体，所以列表的长度决定了数量。`arena cross-judge pool` 也是一个列表，但 Arena 会从中选一个值，尽可能选和父级不同系列的模型。`swarm workers` 是每个工作者的默认模型，除非比赛或对比为每一组指定了别的模型。

### 4. 校验

写进去的每个真实模型名都必须在检测结果里。`inherit-parent` 和 `auto` 总是能通过。如果某个选中的真实模型名不可用，就停下来再问一次。

### 5. 写规则

写出 `~/.cursor/rules/pstack-models.mdc`，带上 `alwaysApply: true`、一行写着所选标签及其目标强度的 `# budget`，以及每个角色一行，用和 poteto工作模式 一样的标签。覆盖整个文件，让重新运行保持幂等。形状如下：

```
---
description: pstack per-role model choices (overrides skill defaults)
alwaysApply: true
---
# pstack model configuration. One line per role. Delete a line to fall back to the skill default.
# `inherit-parent` or `auto` as a value: the role runs on the parent chat model (omit Task `model`). Alias entries in a panel list still count toward its fan-out.
# budget: large (xhigh)
feature, refactoring: grok-4.7-xhigh-fast
bug-fix: grok-4.7-xhigh-fast
perf-issue: grok-4.7-xhigh-fast
hillclimb: grok-4.7-xhigh-fast
judgment and prose: claude-opus-5-5-xhigh
hardest tasks: claude-opus-5-5-xhigh
how explorer: grok-4.7-xhigh-fast
how explainer: claude-opus-5-5-xhigh
why investigators: grok-4.7-xhigh-fast
why synthesizer: claude-opus-5-5-xhigh
reflect tooling: grok-4.7-xhigh-fast
reflect judgment, divergent, synthesizer: claude-opus-5-5-xhigh
arena runners: claude-opus-5-5-xhigh, grok-4.7-xhigh-fast
arena cross-judge pool: claude-opus-5-5-xhigh, grok-4.7-xhigh-fast
swarm workers: grok-4.7-xhigh-fast
architect runners: claude-opus-5-5-xhigh, grok-4.7-xhigh-fast
interrogate reviewers: claude-opus-5-5-xhigh, grok-4.7-xhigh-fast
```

### 6. 确认

告诉用户规则已经写好，并且它对新会话生效。重新运行这个 skill 就会更新它。

### 7. 提供一个验证 skill（可选）

检查这个项目有没有办法操作真实的应用来做证明（一个 `verify-*` skill，或者一个已有的测试工具）。如果没有，就提一次：“want a project-local verification skill, so agents can drive the app the way a user does and prove changes work? I can generate one with /创建验证skill.”（要不要一个放在项目里的验证 skill，让智能体能像用户一样操作应用、证明改动是好的？我可以用 /创建验证skill 生成一个。）如果用户说要，就调用 `/创建验证skill`（不管 pstack 装在哪里，工作区、用户还是插件，都能找到）。如果说不要，就继续往下做，不要强推。
