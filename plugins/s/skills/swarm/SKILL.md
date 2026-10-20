---
name: swarm
description: "同时派出 N 个并行的工作者，等它们全部完成，交回一份报告。用于 /swarm、“swarm this”（让一群智能体来做），或者需要并行覆盖、比赛、连环检验和探索的时候。Use when you need parallel coverage, a race, chained checks, or sharded exploration."
disable-model-invocation: true
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。


# 群体作战

## 开始

在启动任何东西之前，先开一个待办清单，每个阶段一条。

1. 定框架
2. 分派
3. 汇总
4. 报告

## 阶段 A：定框架

1. 说明“完成”的判断标准，以及这群工作者必须交回的产物或报告。
2. 选择形状。可以切成几片分头做，也可以让 N 个工作者拿着完全相同的任务说明比赛，或者两者混合。如果是比赛或混合形状，在派出之前先声明用 `first pass`（第一个通过的）、`rank all`（全部排名）还是 `best-of`（选最好的）。
4. 从当前软件的 s 模型配置里 `swarm workers` 那一行选工作者的模型。路径见文末。没有这份配置或没有这一行，就用一个较快的写代码模型；软件不能指定模型，就省略，让工作者跟父对话走。`auto` 或 `inherit-parent` 也省略。软件拒绝了某个名字，就换同一系列里它接受的最接近的名字，并说一句。模型之间的比赛，事先写明每一组用的模型。按 **poteto-mode** skill 里 “子智能体” 一节的规定，为每个子智能体的任务选择推理等级，以及快速还是标准速度。Cursor 上、并且 `grok-4.7-xhigh-fast` 确实可用时，没有配置可以用这个名字。别的软件不要照抄它。
5. 工作者要写东西时，给每个工作者一个它自己的可写输出位置。当工作者要验证或测量某些提交时，每份任务说明都要写明确切的 SHA（提交编号）。测量类的任务说明还要写明方法（采样次数、一次采样是什么、顺序）。工作者要在结果里把这两样都记录下来。

## 阶段 B：分派

在一条消息里派出全部 N 个工作者。用能写文件的通用类型。软件能后台运行就后台运行。软件能把子智能体放到别的机器上、而且这个任务不需要本机的文件、界面或登录态时，就放到那边；否则在本机跑。模型按第 4 步（`auto` 或 `inherit-parent` 就不设）。

工作者必须从一个非默认的、已推送的分支开始时，用这个软件实际支持的参数。Cursor 的参数名是 `cloud_base_branch`。别的软件没有这个参数，就在任务说明里写明 SHA，或先自己切到那个分支。不要发明参数名。

每份任务说明都要能独立看懂。写上目标、范围、确切的那一片或那一组比赛、怎么验证、要报告什么。报告用 `PASS`（通过）、`ISSUES`（有问题）或 `BLOCKED`（被卡住），并附上证据。能证明有缺陷的工作者报告 `ISSUES`，并列出它能证明的每一个问题，而不只是第一个。

如果有工作者掉线了，就用剩下的 N-1 个继续，并注明这一点。

## 阶段 C：汇总

读最终结果。如果一个结果没有记录它的任务说明里写明的 SHA 和方法，就丢掉它，并重新派一次那个工作者。第二次还缺，就记为一个缺口。缺口不算通过。如果是做覆盖，每一个必需的片都要有结果。如果是比赛，就用事先声明的选择规则：第一个通过、全部排名或选最好的。不要把工作者的原始输出直接贴出来。

## 阶段 D：报告

在聊天里交回一份汇总报告，包括表格、每个问题一句话的说明、缺口或掉线情况，以及（如果是比赛）用的是哪条规则。

## 在不同软件里怎么用

角色行是 `swarm workers`。配置路径以 [setup-s-models](../setup-s-models/SKILL.md) 为准。一条消息里把 N 个工作者都派出去。

### Cursor（原版参数）

每个工作者一个 `Task`：`subagent_type: generalPurpose`，`environment: "cloud"`，`run_in_background: true`，`model` 用第 4 步选的名字。`auto` 或 `inherit-parent` 省略 `model`。没有这行配置、并且 `grok-4.7-xhigh-fast` 这次真能传给 `Task` 时，用这个名字。

只有工作者需要用户电脑上的文件、界面或登录态时，才改 `environment: "local"`。必须从一个非默认的、已推送的分支开始时，传 `cloud_base_branch`。

`Task` 拒绝了配置的名字，就改用 `grok-4.7-xhigh-fast` 并说一句。连这个默认也被拒绝，就从报错里选同一系列里最接近的有效名字。

### OpenCode

每个工作者调一次 `subagent`，`background: true`。agent ID 用 `s-swarm-workers`（`~/.config/opencode/agents/s-swarm-workers.md`，`mode: subagent`，`model` 等于角色行）。没有这个文件时用内置 `general`。`general` 不能再派子智能体，提示词里也要写明工作者不要再往下派。

工具页没有 `environment` 和 `cloud_base_branch`。全在本机子会话里跑，SHA 写在 prompt 里。不要在调用上传 `model`（工具页没有这个参数；issue 里的写法未核实，见 poteto 文末）。

文档：[Tools](https://opencode.ai/v2/docs/tools)、[Agents](https://opencode.ai/v2/docs/agents/)。

### Codex

提示词写成：Spawn N subagents in parallel. Each is `s-swarm-workers`（或 “each uses model \<模型\> with model_reasoning_effort \<档位\>”）. Wait for all of them, then summarize. 文件在 `~/.codex/agents/s-swarm-workers.toml`。没有文件时点名这次账号里真有的较快模型。文档举例 `gpt-6-luna` 只在账号有它时才用。

没有 `cloud_base_branch`。SHA 写在提示词里。未核实：有没有把子智能体放到另一台机器的参数。子智能体文档只写了跟父级同一套沙箱。并发很多时，看 `[agents].max_concurrent_threads_per_session`，不写则由 Codex 自己选默认。

文档：[Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)。

### WorkBuddy

`Agent`，`subagent_type: "general-purpose"`，`run_in_background: true`，做完用 `TaskOutput` 取结果。没有云端参数，全在本机跑，SHA 写在任务说明里。模型省略，或用 `"lite"`。

### Claude Code

`Agent`，`subagent_type: "general-purpose"`，`run_in_background: true`。模型用 `sonnet` 或完整 ID，不写就跟父级。不确定有没有云端参数。没有就在本机跑，SHA 写在任务说明里。

### 派不出子智能体

在主对话里一片一片做，做完再汇总。不要假装已经并行了。
