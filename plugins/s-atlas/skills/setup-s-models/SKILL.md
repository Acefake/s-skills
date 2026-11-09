---
name: setup-s-models
description: "「/setup-s-models」「配置 s 模型」「s 的预算」。一步步选定预算和各角色模型，写到当前软件会读的位置。Use when configuring which model and reasoning budget s uses for each role."
---

本会话首次使用时按[日常自检](../setup-s-instructions/references/daily-check.md)只读检查，不自动写配置。

# 设置 s 的模型

普通模式和 T3 统一使用六角色：检索与探索、方案设计、开发实现、专项攻坚、验证测试、独立评审。角色只决定已授权任务的模型，不代表启动六个代理。角色分工和旧键映射见[角色键对照](references/role-keys.md)，具体路径与工具见[宿主适配](../../HOSTS.md)。

用户选择 Claude Code 与 Codex 混合使用、三档预算或首选/次选方案时，读取[混合三档与顺序备用](references/mixed-budget-profiles.md)。这是可选预设，不覆盖已有模型与显式档位；高对应工具中的“大”，原有不限档仍可使用。预设中的显式角色档位优先于下面的通用预算映射。配置备用顺序不授权额外并行代理。

用户通过 T3 编排使用 DeepSeek-V4.1-Flash 评审时，读取[DeepSeek 评审](references/glm-review-trial.md)。此预设由用户选择 DP4.1 Flash enabled 首选、Sol medium 备用；高档 DP 与 Sol 各一名。用户选型不代表总体效果已验证，不自动覆盖项目已有配置。

## 检测当前环境

按实际派发工具选择预设：T3 支持相应跨提供商目标时使用混合三档；仅本厂商原生工具时读取[原生三档](references/native-budget-profiles.md)，不得把 DP、Claude 或 Codex 的异厂商模型直接填进去。只有继承能力时说明未分流。现有模型配置优先，不因安装预设自动覆盖。

先发现当前宿主能派发的模型和参数，再推荐，不能沿用父模型就声称已检测全部。T3 中读取全部连接 Agent 的可运行/禁用状态并补查候选目录，使用 [T3 编排参考](../s-router/references/t3-code-tools.md)；不能先要求用户在预设两家组合中选。普通宿主按自身工具定义核实可派发模型，不假定能跨提供商。

Codex 固定角色文件要与已确认的新角色、模型及档位一致，文件名按下表英文键转为连字符；不自动删除用户旧 TOML。Claude Code 的模型以当前 Agent 工具接受的值为准，每次派发都要传可用的 effort。DSH 读取所选 profile 的可派发模型与 reasoning_effort，标记段只写 $DSH_HOME/AGENTS.md（未设置时 ~/.dsh/AGENTS.md），不放 profile 子目录；Hermes 读取所选 profile 的模型，不能按次选模则六行均写 inherit-parent，写 SOUL.md，不改 YAML。多个 profile 时先确认一个。

## 分步确认

按[交互提问](../setup-s-instructions/references/interactive-confirmation.md)选择当前模式可用工具，一次一步。有 request_user_input_async 时优先使用，返回只表示已展示，等待实际回答。没有可用工具才编号提问并说明原因。

1. **确认环境与作用域。** 检测到的环境优先列出，同时允许选择 Codex、Claude Code、Cursor、WorkBuddy、DSH、Hermes。T3 明确当前项目，普通宿主确认用户级或项目级实际读取路径。不能靠猜测创建全局文件。
2. **选择预算。** 说明已有预算，再让用户选。用户明确采用三档预设时展示省、中、高，高映射为工具预算“大”；省、中各 1 名评审，高 2 名，思考按预设逐行配置。其他配置流程保留以下四个选项：
   - 省：评审只派 1 个快模型，最难的活用强模型，最省额度
   - 中：评审派 1-2 个，判断类用强模型
   - 大：评审派 2 个（一快一强），默认
   - 不限：评审 2 个以上，思考最深，最费额度
3. **展示完整六行。** 解释推荐模型及参数依据。采用混合预设时按参考文件逐项展示首选、次选、推理档位、切换条件和独立名额数，不能把次选写成并行列表。未选择预设时，通用生成规则为：检索与探索使用轻量档；开发实现和验证测试使用常规档；专项攻坚使用复杂档。省预算方案设计使用常规档，其他预算使用复杂档；独立评审按预算生成。省只派一个评审，常规起始 medium，专项攻坚高一级 high；中 high，大 xhigh，不限 max，检索与探索最多 medium。这是生成器的预算映射，不是各模型的官方推荐。用户可给任何角色显式指定模型。接受预览不授权写入。
4. **展示完整变更并确认写入。** 单独展示标记段或双文件差异，再取得明确写入确认。沉默、预选、随便、都行不算同意。写完回读校验，说明路径、是否需要新会话以及未验证的运行边界。

已有配置默认保留。旧十五/十七角色精确读取继续支持；多个旧角色合并为一个新角色时，模型或档位不同就报冲突，不自动选择一个丢弃其他值。新中文键优先；只有用户明确重新分配时才使用 --replace-roles。接受六角色设计本身不授权改写用户配置。

## 生成与验证

普通宿主使用 scripts/s_models.py，T3 使用 scripts/t3_targets.py，角色定义与预算由同一个通用模块维护。用已有 Python 环境，不为配置安装依赖。

普通模式预览：

```text
python scripts/s_models.py render --budget 省 --light <已确认轻量模型> --fast <常规模型> --strong <复杂模型> --models <已确认名单> --role-effort
python scripts/s_models.py write <规则文件> --budget 省 --light <轻量模型> --fast <常规模型> --strong <复杂模型> --models <名单> --role-effort --json
```

write 默认只预览，保留标记外内容及原模型；单行修改用 --set 角色=值，冲突迁移应先确认具体新值，全部重分配经用户明确同意后加 --replace-roles。确认写入后同一命令加 --apply。--inherit 明确将六行改成继承，仍需完整预览和确认。check <文件> --models <名单> 通过才报告静态配置完成。

T3 的 render 必须给出六行目标，configure 校验目标 JSON 与角色，默认只预览双文件差异；最终确认才加 --apply。只写项目 AGENTS.md 和 s-atlas.t3.json，实际 provider/model/options 按能力定义确认。它不配置其他宿主的认证，也不改变六角色的通用分工。

下面是通用六行模板，不是已确认的模型选择：

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
