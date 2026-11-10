# T3 Code 编排参考

T3 是底层宿主之上的编排环境。先确认任务授权，再选择工具；工具存在不授权自动并行。普通任务仍由主代理完成。参数以当前会话工具定义为准。

## 模型与配置

第一次 T3 委派前调用一次 `orchestrator_capabilities`，发生错误或用户要求切换提供商后才重新发现。目录截断时用 `search` 精确查询目标；合并查询结果时按提供商实例与模型 ID 去重，并保留同一次确认的父模型信息。模型目录只证明可选接口，认证和真实运行另行验证。

T3 新配置使用六角色；旧十五角色保留读取兼容，其他宿主同步使用六角色。裸模型名仅在当前提供商解析；`inherit-parent`/`auto` 默认继承父模型和参数。角色可写 `t3:implementation`，由同一作用域目录中 `wukong.t3.json` 的命名目标解析：

```json
{
  "schemaVersion": 1,
  "targets": {
    "implementation": {
      "providerInstanceId": "codex",
      "model": "gpt-6.1-sol",
      "options": { "reasoningEffort": "medium" }
    }
  }
}
```

示例不是推荐覆盖值；使用本次能力目录确认的实例、模型和参数。`options` 仅接受目录支持的字符串或布尔值，不接受权限或命令字段。复杂模型 ID 原样放 JSON，不用逗号分割。

推荐前扫描全部连接的 Agent 实例，展示可运行与禁用状态，按模型关键词补查被截断的候选目录；不要只保存父提供商的能力片段来推导角色。模型选择不等于平均使用所有 Agent。

六角色职责与旧调用映射：

| 新角色 | 负责内容 | 对应旧角色 |
|---|---|---|
| 检索与探索 | 定位代码、调用链、只读调查 | 检索和简单任务、怎么工作的探索者、为什么的调查者 |
| 方案设计 | 需求、架构、拆任务与综合判断 | 判断和写作、怎么工作的讲解者、为什么的综合者、反思的判断、发散和综合 |
| 开发实现 | 功能、修 bug、重构 | 写功能和重构、修 bug |
| 专项攻坚 | 难题、性能和复杂架构 | 性能问题、爬坡优化、最难的任务 |
| 验证测试 | 复现、回归与实际产物验证 | 群体作战的工作者 |
| 独立评审 | 独立检查风险和失败路径 | 审问审查者、反思的工具视角 |

读新配置时，旧角色调用名映射到对应新行。读旧配置时仍可按原角色精确派发；若用新角色请求合并读取多个旧行且模型不同则报冲突，要求用户明确选择。新写入必须完整六行；六行与十五行混写时报错。映射只决定模型选择，不授权委派、运行测试或更改只读任务范围。

用生成器输出候选标记段，不手工凑旧十五行：

```text
python <scripts>/t3_targets.py render --budget 省 --set 检索与探索=t3:lookup --set 方案设计=t3:design --set 开发实现=t3:implementation --set 专项攻坚=t3:hard --set 验证测试=t3:test --set 独立评审=t3:review
```

返回 JSON 的 `block` 是候选内容。六行都必须明确提供，允许共用目标。省预算独立评审只有一项；专项攻坚的目标可显式选择高一级推理，其他角色不因此多派代理。检索与探索默认推理最高 medium。

本次用户指定优先于项目角色，项目角色优先于全局角色。用户级全局配置必须用 `--host` 明确当前底层宿主，不以子任务目标 provider 代替宿主。宿主根目录遵从下表，`--global-dir` 仅显式覆盖该宿主根目录，不统一文件名或格式。

| 底层宿主 | 根目录 | 自动加载的模型规则 |
| --- | --- | --- |
| Codex | `$CODEX_HOME`，默认 `~/.codex` | 非空 `AGENTS.override.md` 优先，否则 `AGENTS.md`；只替换模型段 |
| Claude Code | `$CLAUDE_CONFIG_DIR`，默认 `~/.claude` | `rules/s-models.md`，普通 Markdown |
| Cursor | `~/.cursor` | `rules/s-models.mdc`；首次创建加 `description`、`alwaysApply: true` frontmatter，已有内容保留 |
| WorkBuddy | `~/.codebuddy` | `rules/s-models.md`，普通 Markdown |
| DSH | `$DSH_HOME`，默认 `~/.dsh` | `AGENTS.md`，不写 profile patch YAML |
| Hermes | `$HERMES_HOME`，默认 `~/.hermes` | `SOUL.md`，不写 config YAML；多 profile 先确认，具名 profile 的四类命令均传 `--global-dir <选中 profile home>`，除非已确认 HERMES_HOME 指向该目录 |

各宿主根目录另存 `wukong.t3.json`，只供 T3 解析器读取，不是宿主原生模型字段。Codex 的原生 `agents/*.toml` 仍按原生流程配置；T3 别名不可填进原生 TOML 的 model。Cursor 本机用户规则文件与设置里的云同步 User Rules 不同，不操作内部设置数据库。官方路径依据：[Codex](https://learn.chatgpt.com/docs/agent-configuration/agents-md)、[Claude Code](https://code.claude.com/docs/en/memory#user-level-rules)、[Cursor](https://prod.cursor.com/help/customization/rules)、[WorkBuddy](https://www.workbuddy.cn/docs/cli/codebuddy-dir)。文件层验证不证明这些客户端已实际加载。

项目无模型段时，check/resolve 使用 `--host` 对应宿主的全局默认；项目有完整模型段时整段覆盖全局，不按行混合，不跨作用域借别名。Codex 项目根也优先读取、写入非空 `AGENTS.override.md`，空 override 则使用 AGENTS.md。项目规则与项目根目标配对，用户规则与宿主根目标配对。残缺标记、缺角色、缺目标、无模型段却存在孤立目标文件、未完成事务均报错，不静默降级。项目路径必须已经存在且是目录；笔误路径不能被当成新项目或全局继承入口。没有任何配置时报告缺少模型段，由主代理明确技能默认目标。返回的 `scope`、`rulesPath`、`targetsPath` 表明实际来源。

角色显式括号档位与目标 options 中的推理设置同时存在时报冲突。没有显式设置时映射预算；轻量角色默认最高 medium。目标没有推理选项时不伪造参数；显式档位不支持时报错。预算不是金额上限。

解析脚本位于 `../../setup-s-models/scripts/t3_targets.py`（相对本文）。保存能力对象或包含 `structuredContent` 的 MCP 结果为临时 `capabilities.json`，再执行：

```text
python <scripts>/t3_targets.py check --host <底层宿主> --project <项目根> --capabilities <能力快照>
python <scripts>/t3_targets.py resolve --host <底层宿主> --project <项目根> --capabilities <能力快照> --role "修 bug"
```

`resolve` 输出 `schemaVersion`、角色、隔离方式及每项的 `executor` 与 `target`。`--native-model` 可重复，只填当前原生工具实际接受的模型。需要隔离加 `--worktree`，用户点名 T3 或额外设置加 `--delegate`。未列出原生支持时保守输出 T3 路由；不能用 T3 目录推断原生工具支持。

同提供商同模型无覆盖时可继承参数；切换目标时按新模型构造合法 `target.options`，空对象清除父参数。不得将 Codex 的 `reasoningEffort` 原样带给仅支持 `effort` 的模型。脚本输出的 target 用于委派；原生执行应按原生工具定义传参，不能直接照搬 target。

## 设置与写入

先确认项目作用域、预算，展示完整六行和每个目标，再展示双文件差异并单独取得最终写入确认。脚本不代替确认：

```text
python <scripts>/t3_targets.py configure --host <底层宿主> --project <项目根> --capabilities <能力快照> --block <候选标记段文件> --targets <候选目标JSON>
python <scripts>/t3_targets.py configure --scope user --host <底层宿主> --capabilities <能力快照> --block <候选标记段文件> --targets <候选目标JSON>
```

默认只预览。确认后用同一命令加 `--apply`。只写所选作用域的模型规则标记段与 `wukong.t3.json`，保留其他规则、换行和 BOM；首次全局预览不创建目录。`--scope project` 为默认且要求已存在的 `--project`，使用项目根 AGENTS.md（Codex 非空 override 优先）；`--scope user` 不要求项目路径，但必须传 `--host`。`--rules` 可省略，提供时必须匹配所选作用域与宿主路径。为与事务路径白名单保持一致，读取和写入规则均不支持符号链接，遇到链接明确报错。更换作用域不移动或清除原配置。Cursor 新建或仅含空白的本机规则补入 frontmatter，已有非空内容保留。

用户级 check/recover 同样传 `--scope user --host <底层宿主>`；项目读取命令传 `--host` 才能在需要时继承该宿主全局默认。所有示例均显式传宿主。不指定宿主仅兼容无非空 override 的项目自有配置；遇到非空 AGENTS.override.md 或需要全局时明确报错，不静默选择文件。自定义宿主根目录时所有命令传同一 `--global-dir`。模型规则由宿主加载给代理，T3 命名目标由 s 技能解析；原生模型配置仍走对应宿主流程，不自动扩展跨提供商能力。

Hermes 具名 profile 的完整路径示例（先确认 profile 已存在；占位符换成实际目录，四类命令保持相同目录）：

```text
python <scripts>/t3_targets.py configure --scope user --host hermes --global-dir <profile-home> --capabilities <快照> --block <候选段> --targets <候选目标>
python <scripts>/t3_targets.py check --scope user --host hermes --global-dir <profile-home> --capabilities <快照>
python <scripts>/t3_targets.py resolve --project <项目根> --host hermes --global-dir <profile-home> --capabilities <快照> --role "修 bug"
python <scripts>/t3_targets.py recover --scope user --host hermes --global-dir <profile-home>
```

目标 JSON（含旧文件名）的读取同样拒绝有效及悬空符号链接，不能通过链接把其他作用域的别名带入本作用域。全局根路径已存在却不是目录时，在预览阶段即报错。事务记录和首份备份独占创建，普通写入或 fsync 失败只清理本次创建的残缺文件，不删除其他写入者已有的记录。进程被强制终止或磁盘故障导致无法清理时仍需人工核对，不能保证任意外部编辑器并发写入的原子互斥。

写入前校验全部候选内容，按目标文件、角色文件顺序替换，保留备份。`.wukong-t3.transaction.json` 是中断恢复记录，不应提交；建议由项目本地忽略规则管理。存在记录时停止新配置，先检查文件，再运行 `recover --host <底层宿主> --project <项目根>` 恢复原内容；若文件有外部改动则拒绝覆盖，人工对账。失败写入不声明成功；回读后再执行 check。目标文件不含认证信息，可按项目约定提交。项目里若仍是改名前的 `s-atlas.t3.json` 或 `s-wukong.t3.json`，检查和解析仍读该文件；写入前先把它改名为 `wukong.t3.json`。旧的 `.s-atlas-t3.transaction.json` 或 `.s-wukong-t3.transaction.json` 仍可用 `recover` 处理。

`.s-models.bak` 保留首次创建时的前像，不是每次更新的最新备份；存在时不覆盖。每次事务的即时前像在事务记录中，成功后事务记录删除。恢复会逐项检查并做终态回读，冲突可能留下部分已恢复文件，须结合保留的事务记录人工对账；这些检查不提供对任意外部编辑器的原子互斥。

## 派发选择

用户已授权多个独立调查时，按[并发只读检索](../../wukong-mode/references/subagents.md#并发只读检索)拆成多个任务并发提交。一个任务的首选/次选仍只启动一个，不用新顶层线程代替子代理，不把目录列出多个目标当成同时启动授权。

- 同提供商、原生工具支持的模型，且没有额外参数和隔离要求：用原生子代理并等待。
- 跨提供商、用户指定额外设置、独立 worktree 或点名 `delegate_task`：用 T3 `delegate_task`，设置放 `target.options`。
- 后台任务使用 T3 委派。工作流仅在用户要求时使用。
- 不可用提供商、模型、参数或隔离方式报错；没有用户明确授权的顺序备用时，不自动换模型、提供商、原生工具、工作流或 CLI。用户明确配置首选/次选时，按[顺序备用规则](../../setup-s-models/references/mixed-budget-profiles.md)核对候选和失败状态后切换；模型备用不授权改变隔离、权限、工具或工作流。

委派不带父历史。任务说明必须包含目标、文件所有权、输入、限制、已有决定、验证与交付要求。只读评审要明确禁止编辑、测试、提交和外部写入；运行权限字段默认不传，不能用权限模式代替只读任务约束。

## 等待与取消

保存 taskId、返回的运行与线程 ID、链接、实际模型和参数。严格执行返回的 `next`：要求等待完成唤醒时结束本回合，不轮询 task_status、不 sleep、不用定时器或监视器代替通知。

仅本回合需要结果时使用 `mode: wait`。问题、审批或超时按返回状态处理；超时不取消任务，沉默不批准请求。用户才能提供的登录信息使用 `request_secret`，不放进聊天或子任务说明。

取消不再需要或被替换的委派用 `task_cancel`，不能用线程中断。失败后检查遗留改动和运行状态，再决定是否重试。响应丢失时先对账，不能因为没收到 taskId 就直接重复派发。`clientRequestId` 仅作为关联字段，不假定未声明的幂等保证。

新一轮委派评审必须新建 `delegate_task`，带上原发现、修复与异议；不发送旧线程消息代替复审。小发现由主代理修复，不为此新增委派。结果需主代理核验，配置检查通过不等于真实产物完成。

## 工作区与线程

独立检出由 `delegate_task` 的 `isolation: worktree` 创建与绑定，不在 shell 或子任务说明中创建检出。基于父提交，未提交文件不带入；任务依赖未提交代码或目标配置时先解决依赖，不能擅自提交或退回共享写入。共享写入必须划清文件所有权，不能隔离则串行。

只有用户明确要求新顶层线程时使用线程创建工具；子代理不等于新顶层线程。新线程按 `workspaceStrategy` 规则选基准，与委派 worktree 的父提交规则区分。讨论已有线程前先读线程；回复引用工具返回的完整 link，不拼接链接。

首版不接持续台账、PR 等待、远程机器和定时执行；涉及这些任务时遵从当前会话 T3 工具规则，不宣称已由 s 自动实现。
