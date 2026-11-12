# 角色模型弹窗选择：按宿主动态推荐 + 首选/次选

## 目标

配置 T3 六角色模型时，先读出当前宿主实际能用的模型，从白名单里按角色排好的顺序挑出本机有的前 4 个作推荐，再用弹窗让用户为每个角色选首选和次选。次选写进 `wukong.t3.json`，由脚本校验，`resolve` 能直接读到。

不在范围内：非 T3 宿主（`s_models.py`）、自动故障转移、管理认证。

## 1. 白名单与角色排序

新文件 `plugins/wukong/skills/setup-s-models/references/model-allowlist.json`，随技能发布。它只表达「哪些模型值得推荐、每个角色按什么顺序偏好」，不假设某台机器装了什么。

```json
{
  "schemaVersion": 1,
  "models": {
    "haiku":    {"model": "claude-haiku-5-5",    "label": "Haiku 5.5",           "providers": ["claudeAgent"]},
    "sonnet":   {"model": "claude-sonnet-5-5",   "label": "Sonnet 5.5",          "providers": ["claudeAgent"]},
    "opus":     {"model": "claude-opus-5-5",     "label": "Opus 5.5",            "providers": ["claudeAgent"]},
    "fable":    {"model": "claude-fable-5-2",    "label": "Fable 5.2",           "providers": ["claudeAgent"]},
    "luna":     {"model": "gpt-6-luna",          "label": "Luna 6",              "providers": ["codex"]},
    "sol":      {"model": "gpt-6.1-sol",         "label": "Sol 6.1",             "providers": ["codex"]},
    "astra":    {"model": "gpt-6-astra",         "label": "Astra 6",             "providers": ["codex"]},
    "terra":    {"model": "gpt-6.1-terra",       "label": "Terra 6.1",           "providers": ["codex"]},
    "grok":     {"model": "grok-4.7",            "label": "Grok 4.7",            "providers": ["cursor"]},
    "composer": {"model": "composer-2.5",        "label": "Composer 2.5",        "providers": ["cursor"]},
    "dsflash":  {"model": "deepseek-v4.1-flash", "label": "DeepSeek V4.1 Flash", "providers": ["codebuddy"]},
    "glm":      {"model": "glm-5.3",             "label": "GLM-5.3",             "providers": ["codebuddy"]},
    "glmflash": {"model": "glm-5.3-flash",       "label": "GLM-5.3 Flash",       "providers": ["codebuddy"]},
    "hy4":      {"model": "hy4std",              "label": "Hy4",                 "providers": ["codebuddy"]},
    "gemini":   {"model": "gemini-3.8-flash-high", "label": "Gemini 3.8 Flash High", "providers": ["antigravity"]},
    "swe2":     {"model": "swe-2-flash-medium",  "label": "SWE-2 Flash",         "providers": ["devin"]}
  },
  "providerOnly": {
    "cursor": ["grok-4.7", "composer-2.5"]
  },
  "roles": {
    "检索与探索": ["haiku", "luna", "dsflash", "composer", "glmflash", "gemini", "hy4", "sonnet", "swe2"],
    "方案设计":   ["opus", "sonnet", "sol", "astra", "fable", "glm", "grok", "dsflash"],
    "开发实现":   ["sonnet", "sol", "opus", "composer", "glm", "astra", "swe2", "dsflash"],
    "专项攻坚":   ["opus", "astra", "sol", "grok", "fable", "glm", "dsflash", "sonnet"],
    "验证测试":   ["sol", "sonnet", "terra", "dsflash", "glm", "haiku", "gemini"],
    "独立评审":   ["dsflash", "sol", "sonnet", "grok", "glm", "opus", "astra"]
  }
}
```

### 匹配规则（解决「别的电脑没有某家」）

- **按模型 ID 匹配，不写死实例 ID。** `providers` 里的名字是提供商的识别词，与本机目录中每个提供商的 `providerInstanceId`、`driverKind`、`displayName`（不区分大小写、包含即可）比对。例如 `codebuddy` 能匹配 `acpRegistry_codebuddy_code`。
- **同一模型多家可用时，按 `providers` 顺序选。** 没列在 `providers` 里的提供商即使有同名模型也不用。例如 Cursor 里也有 `claude-opus-5-5`，但 Opus 只列了 `claudeAgent`，所以本机没有 Claude 时 Opus 就算不可用，不会改走 Cursor。
- **`providerOnly` 限定某家只能出现哪些模型，所有场景都生效。** Cursor 只允许 Grok 4.7 和 Composer 2.5，包括 `--all`、编号表、零匹配时的完整目录和「其他」里填编号；其他 Cursor 模型一律不显示、不接受。
- **只算本机能派发的提供商。** 要求 `canRunChildTask`，跨提供商时还要求 `canRunCrossProviderChildTask`，与 `model_capability` 的判断一致。

### 推荐怎么算

对每个角色，沿 `roles` 里的顺序往下找，**取本机可用的前 4 个**作为弹窗选项。顺序排得比 4 长，就是为了缺了哪家都还能补满。

| 情况 | 处理 |
|---|---|
| 本机可用的够 4 个 | 取前 4 个 |
| 不足 4 个、但至少 1 个 | 有几个放几个；「其他」可填编号表里的其他白名单模型。用户明确要看白名单外的本机模型时，`catalog` 和 `pick` 都加 `--all` |
| 该角色一个都没有 | 退回本机完整目录：第 1 个选项固定为「跟随当前对话模型（inherit-parent）」，其余用父会话所在提供商里的模型补满，并注明「白名单在本机没有匹配，未按能力排序」。选 inherit-parent 时角色行直接写 `inherit-parent`，不生成目标，也没有次选 |

示例（同一份白名单在三台机器上的推荐结果）：

| 角色 | 本机（全有） | 没有 Cursor 和 Claude | 只有 Codex |
|---|---|---|---|
| 检索与探索 | Haiku · Luna · DeepSeek Flash · Composer | Luna · DeepSeek Flash · GLM Flash · Gemini | Luna |
| 方案设计 | Opus · Sonnet · Sol · Astra | Sol · Astra · GLM · DeepSeek Flash | Sol · Astra |
| 开发实现 | Sonnet · Sol · Opus · Composer | Sol · GLM · Astra · SWE-2 | Sol · Astra |
| 专项攻坚 | Opus · Astra · Sol · Grok | Astra · Sol · GLM · DeepSeek Flash | Astra · Sol |
| 验证测试 | Sol · Sonnet · Terra · DeepSeek Flash | Sol · Terra · DeepSeek Flash · GLM | Sol · Terra |
| 独立评审 | DeepSeek Flash · Sol · Sonnet · Grok | DeepSeek Flash · Sol · GLM · Astra | Sol · Astra |

### 白名单本身的校验

- `roles` 只能引用 `models` 里的键，必须覆盖全部六个新角色名，同一角色内不重复。
- 每个模型的 `providers` 不能为空。
- `providerOnly` 里的模型必须与 `models` 中对应提供商的条目一致，不能列出白名单外的模型。
- 不合规时脚本报错，不静默忽略。

## 2. `t3_catalog.py`：读目录、算推荐、校验选择

```text
python t3_catalog.py catalog --capabilities <快照1> [--capabilities <快照2> ...] [--allowlist <文件>] [--all]
```

- 接收多份能力快照：一份不带 search 的基础调用，再加按白名单模型 ID 逐个 search 的结果（目录有截断，必须补搜）。按 `providerInstanceId + model` 去重。
- 按第 1 节的规则匹配，输出 JSON：
  - `entries`：本机可用的白名单模型，每项含编号 `n`、白名单键、实际提供商实例、模型 ID、显示名和 `options` 定义（档位取值和默认值）。`--all` 时追加本机其余可派发模型，标明不在白名单内。
  - `recommend`：每个角色算出的 0–4 个键，以及是否退回完整目录（`fallbackToFull`）。
  - `missing`：本机找不到的白名单模型。对应提供商仍有 `omittedModels > 0` 时，注明「可能被截断」并给出建议的 search 关键词。
- 不访问网络，只读传入的快照。
- `pick --choice <编号或模型ID> --option key=value` 用同样的快照和白名单重算目录后查找选择，返回 `{providerInstanceId, model, options}`；不在目录里（含被 `providerOnly` 隐藏的）、模型 ID 有歧义或参数非法时报错。
- 独立成模块，避免与 `t3_targets.py` 循环引用。

## 3. 弹窗流程（替换 SKILL.md「分步确认」第 3 步）

1. **总开关（1 题）：** 全部用推荐 / 逐个角色选 / 只改某几个角色。选「全部用推荐」时，每个角色取推荐第 1 个作首选，推荐里第一个与首选不同提供商的作次选（没有就取第 2 个，只有 1 个就不设次选），档位用所选预算的预设档位，然后直接跳到第 4 步预览。
2. **对话里先贴编号表**（来自 `catalog`），让「其他」有编号可填。
3. **每个角色弹 1 次窗、4 题：**

   | 题 | 选项（最多 4 个） | 「其他」可填 |
   |---|---|---|
   | 首选模型 | 该角色的动态推荐；当前值加「（当前）」标记 | 编号表里的编号 |
   | 首选档位 | 该模型的推荐档、默认档、高一档、低一档（去重后不足 4 个就少放；模型没有档位参数时跳过本题） | 该模型支持的任意档位 |
   | 次选模型 | 推荐中去掉首选，再补「不设次选」 | 编号 |
   | 次选档位 | 同首选档位 | 同上 |

   - 档位选项按推荐的第 1 个模型生成。用户换了模型而档位不被支持时，只补问这一题。
   - 次选与首选完全相同时重问。同一提供商时提示「额度耗尽会一起失效」，但允许。
   - 高档独立评审的第 2 个名额再弹 1 次。
   - 编号和档位由脚本校验，不由模型判断。
4. 第 4 步「完整预览 + 单独写入确认」保持现有流程不变。

## 4. 目标文件 schemaVersion 2

```json
{
  "schemaVersion": 2,
  "targets": {
    "lookup": {
      "providerInstanceId": "claudeAgent", "model": "claude-haiku-5-5", "options": {"effort": "medium"},
      "fallback": {"providerInstanceId": "codex", "model": "gpt-6-luna", "options": {"reasoningEffort": "max", "serviceTier": "default"}}
    }
  }
}
```

- `fallback` 可选，字段与首选相同，但不能再嵌套 `fallback`，也不能与首选完全相同。
- 写入的是本机实际匹配到的 `providerInstanceId`。换机器后 `check` 会报「提供商不可用」，需要在新机器上重新跑一遍这个流程，不跨机器猜测实例 ID。
- `validate_targets`、`check` 和 `configure` 对首选和次选都按能力目录校验（提供商可运行、模型存在、options 合法）。次选不可用时报错，不静默丢弃。
- `resolve` 输出增加 `fallback` 字段（没有次选时为 `null`）。是否切换到次选，仍按现有备用规则由主代理决定。
- 读取兼容 v1；写入一律输出 v2。v1 文件出现 `fallback` 字段时报错。
- `render` 为每个角色生成独立别名（现有 `t3:lookup` 等），避免两个角色共用一个目标时次选被连带改掉。
- `docs/project/s-model-fallbacks.md` 不再作为次选的数据来源。现有项目由用户确认后迁移进 JSON，迁移完删掉该文件和 AGENTS.md 里指向它的说明。

## 5. 改动文件

| 文件 | 改动 |
|---|---|
| `setup-s-models/references/model-allowlist.json` | 新增 |
| `setup-s-models/scripts/t3_catalog.py` | 新增：`catalog`、`pick` 命令 |
| `setup-s-models/scripts/t3_targets.py` | v2 读写；`fallback` 校验；`resolve` 输出次选 |
| `scripts/test_t3_catalog.py`、`scripts/test_t3_targets.py` | 补测试，见下节 |
| `setup-s-models/SKILL.md` | 第 3 步改为弹窗流程 |
| `setup-s-models/references/t3-config.md`、`mixed-budget-profiles.md` | 删除「schemaVersion 1 无备用字段」相关说明，改为 v2；三档表改为引用白名单排序 |

## 6. 测试

- `catalog` 动态推荐：用三份构造的快照覆盖第 1 节示例表的三种机器（全有 / 没有 Cursor 和 Claude / 只有 Codex），断言每个角色的推荐结果。
- 匹配：识别词匹配实例 ID 和 displayName；同一模型多家可用时按 `providers` 顺序选；不可运行或不支持跨提供商的提供商被跳过；没有 Claude 时 Opus 不改走 Cursor。
- `providerOnly`：`--all`、零匹配退回和编号输入下，Cursor 只出现 Grok 4.7 和 Composer 2.5，填其他 Cursor 模型的编号或 ID 时报错。
- 目录：多份快照去重；截断提示；角色零匹配时退回完整目录且首项为 inherit-parent；`--all`。
- 白名单校验：未知键、缺角色、角色内重复、`providers` 为空。
- v2：首选和次选都合法时通过；次选模型不存在、options 非法、与首选相同、嵌套 `fallback` 时报错；`resolve` 返回次选；v1 仍可读；v1 带 `fallback` 时报错。
- 弹窗本身靠技能文字驱动，不写自动化测试。现有 `evals/setup-models-first-turn` 走 Claude Code 原生宿主，不经过 T3 目录，不加针对弹窗的检查项。
