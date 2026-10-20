# 值得照抄的提示词

换上真实的路径、skill 和完成检查。随意的措辞也可以。（提示词保持英文原样，后面附中文意思。）

## 理解

- `/poteto-mode read <thread>. restate the underlying issue in your own words, in plain english.`（读这个讨论串，用你自己的话、平实的英文复述背后的问题。）
- `/in-your-own-words <long or messy ask>`（复述一个又长又乱的请求。）
- `/sharpen <your task>`（把你的任务磨清楚。）
- `/poteto-mode investigate why <symptom>. give me what we know, what data you used, and your best hypotheses. don't change any code yet.`（调查为什么出现某个症状。告诉我已知什么、你用了什么数据、你最好的假设。先别改任何代码。）
- `use /how to understand <subsystem>. then use /why to find out why it broke recently.`（用 /how 弄懂某个子系统，再用 /why 找出它最近为什么坏了。）
- `/recall my work on <topic> from last week, then read <issue>.`（回想我上周在某个话题上的工作，然后读某个问题单。）
- `/teach me why you implemented it this way and not <other way>. what did you trade off?`（教我你为什么这样实现、而不是用另一种方式。你做了什么取舍？）
- `/poteto-mode take over this branch. read the decision log, find what's done, and continue. don't redo finished work.`（接手这个分支。读决定日志，找出做完了什么，然后继续。不要重做已完成的工作。）

## 构建

- Bug：`/poteto-mode <symptom>. repro first, then fix and verify.`（某个症状。先复现，再修复并验证。）
- 应用里的 bug：`/poteto-mode repro this with /verify-<app>. if it repros on main, fix it and show me a video as proof.`（用验证 skill 复现。如果在 main 上能复现，就修好它，给我看一段视频作为证明。）
- 有便宜测试的 bug：`/poteto-mode repro <bug> first. if there's a cheap test path, /tdd it. then fix and rerun.`（先复现 bug。如果有便宜的测试路径，就用 /tdd。然后修复并重跑。）
- 功能：`/poteto-mode add <behavior>. <current output> stays byte-identical. verify both.`（加某个行为。当前的输出要逐字节保持不变。两者都要验证。）
- 重构：`/poteto-mode move <code> into one module, zero behavior change. record the current output first and prove it's unchanged after.`（把某段代码移进一个模块，行为零改变。先记录当前输出，之后证明它没变。）
- 性能：`/poteto-mode <operation> takes <time> on <fixture>. trace it, fix the measured cause, show me before and after.`（某个操作在某份测试数据上要花多长时间。追踪它，修掉测出来的原因，给我看前后对比。）

## 设计和计划

- `/poteto-mode prototype a few options for <feature>. take screenshots or videos for me to compare.`（给某个功能做几个方案的原型。截图或录视频让我比较。）
- `/poteto-mode we need <feature>. /architect it first, and answer open questions with prototypes. let me review before proceeding.`（我们需要某个功能。先用 /architect 设计，用原型回答还没解决的问题。继续之前让我先审查。）
- `/poteto-mode write a tutorial for how i would use <new package> first. then /teach me why it beats the current one.`（先写一份我会怎样使用某个新包的教程。然后用 /teach 告诉我它为什么比现在的好。）
- `ask /arena for a second opinion on this thread and our approach.`（让 /arena 对这个讨论串和我们的做法给出第二意见。）
- `/poteto-mode turn this design into a plan. small verifiable PRs, each with its own verification steps.`（把这个设计变成一份计划。小而可验证的 PR，每个都有自己的验证步骤。）
- `/poteto-mode plan the migration of <library> to <target>. small verifiable PRs. the result must match the original exactly, bugs included.`（规划把某个库迁移到某个目标。小而可验证的 PR。结果必须和原来完全一致，连 bug 都一样。）

## 审查和上线

- `/interrogate the whole branch, but skeptically. don't change anything yet. no nitpicks unless it's a real bug or regression.`（审问整个分支，但要带着怀疑。先别改任何东西。除非是真正的 bug 或退化，否则不要吹毛求疵。）被驳回的部分也要读。
- `/swarm check every package under <dir> against its check script. one worker per package. one report.`（用每个包自己的检查脚本检查某个目录下的每个包。每个包一个工作者。一份报告。）
- `/poteto-mode open the pr. small ordered commits, evidence in the description.`（开 PR。小而有序的提交，证据写在说明里。）
- `/poteto-mode babysit this pr. get it green.`（照看这个 PR，让它变绿。）只看状态的话：`/poteto-mode check on pr <number>. anything outstanding?`（看看某个 PR。还有什么没处理的吗？）
- `/poteto-mode land the stack.`（把这一串 PR 合入。）

## 离开和回来

- `/poteto-mode im going to bed. <goal> in a fresh worktree off <base>. done means <checks>. keep a decision log. don't ask me before committing. keep going until the checks pass. if you're truly stuck after a few hours, stop and write up why.`（我去睡了。在从某个基础分支开的新 worktree 里完成某个目标。完成的意思是通过某些检查。记一份决定日志。提交之前不用问我。一直做到检查通过。如果几个小时后真的卡住了，就停下来写清楚原因。末尾加上 `/timed-loop`。Cursor 菜单里有 `/loop` 时，那一句是 `/loop until done`。别的软件按 `/timed-loop` 的说明。）
- `/show-me-your-work catch me up on what you did last night.`（告诉我你昨晚做了什么。）先读它的 Attention 部分。
- `/poteto-mode full autopilot on this queue. each item is independent.`（对这个队列全自动驾驶。每一项都是独立的。）
- `/poteto-mode autopilot these changes but stack them, don't ship. i'll land the stack.`（自动完成这些改动，但把它们叠起来，别上线。我自己来合入。）
- `/reflect capture what we learned so the next run doesn't repeat it.`（把我们学到的记下来，让下一次运行不再重蹈覆辙。）只批准那些会改变以后某个决定的修改。
- `/plain-language` 用平实的话把上一条回复重新说一遍。
