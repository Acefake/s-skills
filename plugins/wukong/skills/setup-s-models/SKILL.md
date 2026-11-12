---
name: setup-s-models
description: "「/setup-s-models」「配置 s 模型」「s 的预算」。一步步选定预算和各角色模型，写到当前软件会读的位置。Use when configuring which model and reasoning budget s uses for each role."
---

本会话首次使用时按[日常自检](../setup-s-instructions/references/daily-check.md)只读检查，不自动写配置。

# 设置 s 的模型

普通模式和 T3 统一使用六角色：检索与探索、方案设计、开发实现、专项攻坚、验证测试、独立评审。角色只决定已授权任务的模型，不代表启动六个代理。角色分工和旧键映射见[角色键对照](references/role-keys.md)，具体路径与工具见[宿主适配](../../HOSTS.md)。

配置预算统一展示省、中、高三档，不要求用户额外选择“三档预设”。支持跨提供商编排时读取[混合三档与顺序备用](references/mixed-budget-profiles.md)，仅原生工具时读取[原生三档](references/native-budget-profiles.md)。高写入工具时映射为“大”；旧“大/不限”配置仍可读取，但“不限”不再作为新配置的预算选项。已有模型与显式档位优先，预设中的显式角色档位优先于通用预算映射。配置备用顺序不授权额外并行代理。

用户通过 T3 编排使用 DeepSeek-V4.1-Flash 评审时，读取[DeepSeek 评审](references/glm-review-trial.md)。此预设由用户选择 DP4.1 Flash enabled 首选、Sol medium 备用；高档 DP 与 Sol 各一名。用户选型不代表总体效果已验证，不自动覆盖项目已有配置。

## 检测当前环境

按实际派发工具选择预设：T3 支持相应跨提供商目标时使用混合三档；仅本厂商原生工具时读取[原生三档](references/native-budget-profiles.md)，不得把 DP、Claude 或 Codex 的异厂商模型直接填进去。只有继承能力时说明未分流。现有模型配置优先，不因安装预设自动覆盖。

先发现当前宿主能派发的模型和参数，再推荐，不能沿用父模型就声称已检测全部。T3 中读取全部连接 Agent 的可运行/禁用状态并补查候选目录，使用 [T3 编排参考](../wukong-router/references/t3-code-tools.md) 和 [T3 模型目标配置](references/t3-config.md)；不能先要求用户在预设两家组合中选。普通宿主按自身工具定义核实可派发模型，不假定能跨提供商。

Codex 固定角色文件要与已确认的新角色、模型及档位一致，文件名按下表英文键转为连字符；不自动删除用户旧 TOML。Claude Code 的模型以当前 Agent 工具接受的值为准，每次派发都要传可用的 effort。DSH 读取所选 profile 的可派发模型与 reasoning_effort，标记段只写 $DSH_HOME/AGENTS.md（未设置时 ~/.dsh/AGENTS.md），不放 profile 子目录；Hermes 读取所选 profile 的模型，不能按次选模则六行均写 inherit-parent，写 SOUL.md，不改 YAML。多个 profile 时先确认一个。

## 分步确认

按[交互提问](../setup-s-instructions/references/interactive-confirmation.md)选择当前模式可用工具，一次一步。有 request_user_input_async 时优先使用，返回只表示已展示，等待实际回答。没有可用工具才编号提问并说明原因。

1. **确认环境与作用域。** 检测到的环境优先列出，同时允许选择 Codex、Claude Code、Cursor、WorkBuddy、DSH、Hermes。T3 提供“用户级全局默认”和“当前项目”两个作用域，用户已明确指定时沿用；用户级必须识别底层宿主，传 `--host` 并按 [T3 模型目标配置](references/t3-config.md) 的宿主路径表写入，不使用统一的全局模型目录。普通宿主同样确认实际读取路径。T3 目标 JSON 供编排器读取，不冒充宿主原生模型配置。
   Hermes 多 profile 时先确认一个。具名 profile 的家目录须在所有 configure/check/resolve/recover 命令中显式传 `--global-dir <已确认的 profile home>`，例如 `~/.hermes/profiles/<name>`；只有确认进程 `HERMES_HOME` 已指向该 profile home 时才可省略，不能仅选择名称却写入默认家目录。
2. **选择预算。** 说明已有预算，再只展示以下三个选项。高映射为工具预算“大”，思考按适用宿主的三档预设逐行配置，不把全局档位机械套给每个角色。旧配置为“不限”时说明它是历史档位，未确认新档位前不迁移。
   - 省：1 名评审；常规任务优先节省额度，专项攻坚保留强模型
   - 中：1 名评审；增强方案设计与开发实现
   - 高：2 名独立评审；复杂任务使用更强模型
3. **选定并展示完整六行。** T3 按下面的弹窗流程从本机目录选首选和次选；非 T3 宿主没有跨提供商目录，按适用宿主的参考文件推荐。
   - 先保存一份不带 search 的 `orchestrator_capabilities` 结果，直接运行 `python scripts/t3_catalog.py catalog --capabilities <基础快照>`，推荐只来自[模型白名单](references/model-allowlist.json)。只对 `missing` 中标为 `maybeTruncated` 的模型按其 `search` 补搜，把结果追加为后续 `--capabilities` 重跑；没有这类条目就不搜，每次 search 都会返回全部提供商，逐个搜索会浪费大量上下文。每个角色按白名单偏好顺序取本机可用的前 4 个作推荐，缺哪家就往后补；白名单在本机零匹配时退回本机完整目录，首项为 inherit-parent（该角色行直接写 `inherit-parent`，不生成目标、不过 `pick`，也没有次选）。推荐不足 4 个时只放这几个，「其他」可填编号表里的其他白名单模型；用户明确要看白名单外的本机模型时，`catalog` 与 `pick` 都加 `--all`，两者保持一致，否则编号对不上。`providerOnly` 限定的提供商（Cursor 只有 Grok 4.7、Composer 2.5）在任何场景都不露出其他模型。
   - 先问总开关：全部用推荐 / 逐个角色选 / 只改某几个角色。全部用推荐时，每个角色取推荐第 1 个作首选，推荐里第一个不同提供商的作次选（没有就取第 2 个，只有 1 个就不设次选），档位按所选预算预设。
   - 逐个选时先在对话里贴出 `entries` 编号表，再每个角色提问一次、四题：首选模型、首选档位、次选模型、次选档位。模型题的选项是该角色的推荐，当前值标「（当前）」；次选题去掉首选并补「不设次选」；档位题列该模型的推荐档、默认档、高一档、低一档，模型没有档位参数时省略。「其他」填编号或模型 ID。高档独立评审的第 2 个名额再问一次。
   - 每个选择都用 `python scripts/t3_catalog.py pick --capabilities <同上> --choice <编号或模型ID> --option <key=value>` 转成目标，报错时只重问这一题。次选不能与首选完全相同；同一提供商时提醒额度耗尽会一起失效。首选写成目标字段，次选写进该目标的 `fallback`。
   - 解释推荐依据，逐项展示首选、次选、推理档位、切换条件和独立名额数，不能把次选写成并行列表。Cursor、WorkBuddy、DSH、Hermes 没有匹配预设时，按 HOSTS.md 的实际能力生成六行，不套用 Codex 或 Claude 的原生表；只有继承能力时明确展示 inherit-parent 和未分流。用户可给任何角色显式指定模型。旧脚本仍能读取“大/不限”，通用生成器的中档允许 1-2 名评审；这不改变本配置流程省、中各 1 名、高 2 名的规则。已有显式角色档位优先，用户接受预览不授权写入。
4. **展示完整变更并确认写入。** 单独展示标记段或双文件差异，再取得明确写入确认。沉默、预选、随便、都行不算同意。写完回读校验，说明路径、是否需要新会话以及未验证的运行边界。
   Hermes 具名 profile 预览须展示完整 `rulesPath`、`targetsPath`，确认均属于选中 profile；最终 apply 与 check 沿用同一 `--global-dir`。

已有配置默认保留。旧十五/十七角色精确读取继续支持；多个旧角色合并为一个新角色时，模型或档位不同就报冲突，不自动选择一个丢弃其他值。新中文键优先；只有用户明确重新分配时才使用 --replace-roles。接受六角色设计本身不授权改写用户配置。

用户明确要求应用最终三档方案或重新分配时，对比已有六行与所选档位的完整预设，再按确认结果更新全部目标；不能只替换一个过期模型，或把全局指令版本更新称为模型配置已迁移。

## 生成与验证

普通宿主使用 scripts/s_models.py，T3 使用 scripts/t3_targets.py，角色定义与预算由同一个通用模块维护。用已有 Python 环境，不为配置安装依赖。

应用三档预设时，先把下例占位符换为已确认的首选与每项实际档位；六个 --set 都必须提供。省、中的评审值仅一项，高的评审值为两个首选（每项各带档位）。--fast 只满足通用生成器的输入要求，六行最终值由 --set 指定：

```text
python scripts/s_models.py render --budget <所选档位> --fast <常规首选模型> --models <已确认名单> --set "检索与探索=<首选与档位>" --set "方案设计=<首选与档位>" --set "开发实现=<首选与档位>" --set "专项攻坚=<首选与档位>" --set "验证测试=<首选与档位>" --set "独立评审=<本档首选评审项>"
```

值使用 模型（档位），如 sonnet（medium）；已有显式档位时不再套 --role-effort 的通用预算映射。该选项仍可用于用户明确选择的通用生成，不用于自动实现三档表。高可作为 CLI 输入，输出预算名规范为“大”。

把 render 换为 write <规则文件>、保留上述全部参数并加 --json，即为写入预览。write 默认保留标记外内容及未显式覆盖的原模型；单行修改用 --set 角色=值，冲突迁移应先确认具体新值，全部重分配经用户明确同意后可加 --replace-roles。确认写入后同一命令加 --apply。--inherit 明确将六行改成继承，仍需完整预览和确认。check <文件> --models <名单> 通过才报告静态配置完成。

T3 的 render 必须给出六行目标，configure 校验目标 JSON 与角色，默认只预览双文件差异；最终确认才加 --apply。项目级使用 `--scope project --host <底层宿主> --project <项目根>`，用户级使用 `--scope user --host <底层宿主>`；只写所选作用域和宿主的模型规则及 `wukong.t3.json`。遵从 `CODEX_HOME`、`CLAUDE_CONFIG_DIR`、`DSH_HOME`、`HERMES_HOME`；`--global-dir` 是已选宿主根目录的显式覆盖，不改变其规则文件名与格式。首次用户级预览不创建目录。实际 provider/model/options 按能力定义确认，它不配置认证。

派发时先运行 `t3_targets.py resolve --host <底层宿主> --project <项目根> --capabilities <快照> --role <角色>`。项目无模型段时读取该宿主用户级默认；项目有完整模型段时整段覆盖全局，不跨作用域借别名或按行补齐。项目配置损坏或目标不可用时报错，不静默降级。check/resolve 返回 `scope`、`rulesPath`、`targetsPath`，报告实际来源；自定义宿主根目录时每次传同一 `--global-dir`。能力快照校验不能证明客户端加载、认证和真实调用成功。

下面是普通宿主的六行模板，不是已确认的模型选择。T3 不得按注释删行：必须使用 render 生成完整六行（头注释为“六角色必须完整”），旧键配置映射后也须覆盖全部六角色，才能通过文件级 check/resolve：

```
# s 模型配置
# 一行一个角色。删掉一行就用技能默认。
# inherit-parent 或 auto：跟父对话的模型，派子代理时不传模型。
# 逗号分隔的列表，每一项派一个子代理。
# 预算: 省（medium）
检索与探索: <已确认模型或 inherit-parent>
方案设计: <已确认模型或 inherit-parent>
开发实现: <已确认模型或 inherit-parent>
专项攻坚: <已确认模型或 inherit-parent>
验证测试: <已确认模型或 inherit-parent>
独立评审: <一项或多项已确认条目>
# s 模型配置结束
```

模型可写 模型（档位），解析后分别传给宿主，不把带括号整串作为模型名。普通配置缺失角色时由调用者明确默认；T3 新配置必须完整六行。预算控制分工、推理和评审人数，不是金额上限；目录和文件校验不证明实际模型调用成功。

Codex、Cursor、WorkBuddy 把推理目标写进模型名后缀：仅限当前宿主的已发现目录确有这种命名时；模型与档位分别传参的工具不得伪造后缀。
Claude Code、DeepSeek Harness 和 Hermes 不改名字后缀，按实际支持的参数传递档位；不能按次设置时明确说明。
