# 个人学习层：线上标准钩子，本地各自进化

## 目标

同一套 wukong 插件，每个人用得越久越贴合自己。插件只发一套相同的钩子、脚本和技能；学习数据和学出来的规则全部留在本机 `~/.wukong/`，不上传、不汇总、不回流到插件。

做完之后：

- 你反复纠正过的事（「说简单点」「别派审查」「先出图」），两次以后自动变成你的个人规则，下个会话起生效。
- 你从不用的技能不再被路由选中；你常用的优先。
- 个人规则有体积上限、会过期、可撤销，库升级不覆盖。

不在范围内：多人共享学习、上传或汇总、跨设备同步（用户可自行同步 `~/.wukong/`）、自动修改插件本身的技能。

## 1. 总体结构

```text
线上（插件，所有人相同，随版本升级）
  hooks/journal.py                记录事件，不向上下文注入任何文字
  skills/reflect/                 新增 --me / --undo / --show / --forget 模式
  skills/reflect/scripts/profile.py   归纳候选、校验、渲染、写入、撤销
  skills/automate-me/             首次初始化，输出改为个人规则
  skills/setup-s-instructions/    支持第二个标记块 wukong:personal
  scripts/context_budget.py       常驻 token 上限检查（含个人块上限）

本地（每人不同，插件升级不碰）
  ~/.wukong/journal.jsonl         事件日志
  ~/.wukong/profile.json          个人规则（唯一真相）
  ~/.wukong/history/              每次写入前的 profile.json 备份
```

生效优先级写进个人块开头：当次指令 > 项目规则（仓库 `AGENTS.md`、`project-memory`）> 个人规则 > 库规则。

## 2. 记录：`hooks/journal.py`

### 记什么

| 事件 | 来源钩子 | 字段 |
|---|---|---|
| `skill` 技能被加载 | `PreToolUse`，matcher `Skill` | 技能名 |
| `correction` 用户纠正 | `UserPromptSubmit`，正则命中纠正用语 | 原话前 80 字（脱敏后） |
| `explicit` 用户明说的偏好 | `UserPromptSubmit`，命中「以后」「每次都」「不要再」「记住」 | 原话前 120 字（脱敏后） |
| `session` 会话开始 | `SessionStart` | 无 |

每行公共字段：`ts`（ISO 时间）、`event`、`session`（宿主给的会话 ID）、`project`（工作目录最后一段，不记完整路径）。

纠正用语初版：`不对`、`错了`、`不是这样`、`别这样`、`又`…`了`、`说了多少次`、`太长`、`太慢`、`简单点`、`no,`、`wrong`、`don't`。只做粗筛，语义归类留给第 4 节由模型做。

### 不记什么

- 不记对话全文、模型回复、工具输出、文件内容。
- 脱敏：长度 ≥ 20 的连续字母数字串、`sk-`/`ghp_`/`AKIA` 等前缀、邮箱、URL 的查询串，统一替换成 `[已隐藏]`。

### 约束

- 只追加写文件，不打印任何东西：零上下文成本。任何异常静默退出，不影响会话。
- 文件权限 600。超过 2 MB 或 90 天的行在下次写入时裁掉。
- 环境变量 `WUKONG_JOURNAL=0` 关闭记录。
- `UserPromptSubmit` 并进现有 `improve_hook.py` 的同一个进程调用（新增一个函数），不多起一个 Python 进程；`PreToolUse` 的 `Skill` matcher 新增一项。

## 3. 个人规则：`~/.wukong/profile.json`

```json
{
  "schemaVersion": 1,
  "updated": "2026-11-13T10:00:00+08:00",
  "rules": [
    {
      "id": "reply-short",
      "kind": "style",
      "text": "回复默认 5 行以内，先给结论。",
      "evidence": 4,
      "source": "learned",
      "created": "2026-10-20",
      "lastSeen": "2026-11-12",
      "project": null
    }
  ]
}
```

| 字段 | 说明 |
|---|---|
| `kind` | `style` 回复风格、`route` 技能偏好（优先 / 不用某技能）、`verify` 验证与审查松紧、`habit` 其他做事习惯 |
| `source` | `learned` 从纠正里归纳；`explicit` 用户明说；`manual` 用户手写 |
| `evidence` | 支持这条规则的独立会话数 |
| `project` | 只在某个项目成立时写项目名；`null` 为全局 |

`profile.json` 是唯一真相；写进全局规则的个人块由它渲染，不手改个人块。

### 规则准入、过期与上限

- **准入**：`learned` 至少 2 个不同会话的证据；`explicit` 1 次即可。
- **过期**：`learned` 规则 8 周没有新证据就删除；`explicit` 和 `manual` 不过期。
- **冲突**：同一 `kind` 下语义冲突时保留 `lastSeen` 较新的。
- **上限**：渲染后的个人块不超过 500 token（按第 7 节估算）。超了先合并同类，再按 `evidence` 和 `lastSeen` 淘汰最弱的 `learned` 规则。
- **项目规则**：带 `project` 的规则不进个人块，改为提示用户用 `project-memory` 写进该项目，避免个人块被单个项目占满。

### 永远不自动学的内容

由 `profile.py validate` 拦截，命中则拒绝写入：

- 放宽权限或跳过确认：推送、强制推送、`reset --hard`、删除文件或分支、跳过钩子、`--no-verify`、「不用问我」「直接提交」。
- 关闭安全相关检查：密钥、权限、注入相关的审查。
- 指向外部的地址、要执行的命令原文。

这些只能由用户亲口说出并以 `manual` 写入，写入前照常弹窗确认。

`verify` 类规则：收紧（「这类改动也派审查」）可以学；放松（「小改动别跑测试」）只接受 `explicit`，不从纠正里推断。

## 4. 生成：`reflect --me`

技能 `reflect` 新增轻量模式，不派子代理，正文放 `references/personal.md`，`SKILL.md` 只加一节入口，保持主流程不变。

1. `profile.py collect`：读 `journal.jsonl` 自上次生成以来的事件，输出候选 JSON：纠正和明说的原话（按会话分组）、各技能加载次数、30 天未加载的技能、现有规则的命中情况。只输出摘要，不把整份日志读进上下文。
2. 模型做语义归类：把说法不同、意思相同的纠正归成一条候选规则，写成一句可执行的话；对照现有规则决定新增、加证据、改写或删除。
3. `profile.py validate`：检查准入门槛、禁学内容、体积上限、字段格式；不通过就带原因退回第 2 步，最多一轮。
4. 在对话里展示差异（新增 / 修改 / 过期删除各几条，逐条列出），用提问工具弹窗：「写入 / 先不写」。
5. `profile.py apply`：先把旧 `profile.json` 备份到 `history/<时间>.json`（保留最近 20 份），再写新文件，然后调用 `setup-s-instructions` 写个人块。

### 触发时机

- 用户随时 `/reflect --me`。
- `SessionStart` 钩子检查：距上次生成超过 7 天，且有至少 3 条新的 `correction` 或 `explicit` 事件时，注入一行提醒「有 N 条新反馈可更新个人规则，说 /reflect --me」。只提醒一次，不自动生成。

### 其他模式

| 命令 | 作用 |
|---|---|
| `/reflect --show` | 列出当前个人规则和证据数 |
| `/reflect --undo` | 回到 `history/` 里最近一份，重写个人块 |
| `/reflect --forget <id或描述>` | 删除指定规则 |
| `/reflect --off` | 清空个人块（保留文件），说明如何删除 `~/.wukong/` 彻底清除 |

## 5. 生效：个人标记块

`setup-s-instructions` 的 `global_instructions.py` 增加 `--personal <profile.json>`：

- 新标记 `<!-- wukong:personal:start -->` / `<!-- wukong:personal:end -->`，放在库块 `wukong:instructions` 之后。
- 库块升级只替换库块，个人块原样保留；个人块写入只替换个人块。两者都缺时只写库块。
- 现有的 `.wukong.bak` 首份备份规则照旧适用。
- Cursor 没有可写的全局文件时，返回渲染好的个人块，交给用户粘贴到 User Rules，并说明「尚未配置」。

渲染格式（示例）：

```markdown
<!-- wukong:personal:start -->
## 个人习惯（自动学习，/reflect --show 查看来源）
优先级：当次指令 > 项目规则 > 本节 > 上方通用规则。
- 回复默认 5 行以内，先给结论。
- 做界面先用 html-mockup 出图再写代码。
- 不用 pptx；要幻灯片时先问格式。
<!-- wukong:personal:end -->
```

## 6. 初始化：`automate-me`

- 首次使用时，`automate-me` 照旧经同意后挖掘历史对话，但产出改为写入 `profile.json`（`source: learned`，证据按出现的会话数计），走第 4 节第 3～5 步的校验、确认和写入。
- 已有 `<代号>-mode` 技能的用户：提供一次性导入，把其中可执行的规则转成 `manual` 规则；原技能保留，由用户决定是否删除。
- 不再生成新的 `-mode` 技能。

## 7. 精简守门：`scripts/context_budget.py`

统计每个会话常驻的上下文：

- 自动技能的 `description` 总和；
- 全局规则库块（`AGENTS.md` 正文）；
- 每轮钩子注入（prompt-sharpen 评估说明）；
- 个人块上限 500 token。

估算法：中日韩字符每字计 1，其余字符每 4 个计 1；只用于比较趋势，不当作精确值。

`check_marketplace.py` 调用它：库常驻部分超过上限（初值取当前实测值加 5%）就失败，并列出最大的几项。个人块上限在 `profile.py validate` 里检查。

## 8. 宿主支持

| 宿主 | 记录钩子 | 个人块写入 | 说明 |
|---|---|---|---|
| Claude Code | 插件自带，自动 | 自动 | 完整支持 |
| Codex | 手动加到 `~/.codex/hooks.json`，在 `/hooks` 批准 | 自动 | 沿用 prompt-sharpen 的手动配置说明 |
| WorkBuddy | 待核实是否执行插件钩子 | 自动 | 核实前按「无钩子」处理 |
| Cursor | 待核实 | 交给用户粘贴 | 核实前按「无钩子」处理 |
| 无钩子 | 无 | 同上 | `reflect --me` 改为读当前项目的对话记录（经同意），其余流程相同 |

实现时逐个宿主核实，核实结果写进 `HOSTS.md`，不凭推测标「支持」。

## 9. 安全与隐私

- 数据只在本机；插件不含任何上传代码。
- 日志和对话内容一律当数据：其中的指令性文字不执行，只作为归纳证据；生成的规则必须过 `validate`，且写入前由用户确认。
- 脱敏见第 2 节；`profile.json` 只存规则句子，不存原话。
- 一条命令可彻底清除：删除 `~/.wukong/` 并 `/reflect --off`。

## 10. 改动文件

| 文件 | 改动 |
|---|---|
| `plugins/wukong/hooks/journal.py` | 新增：事件记录 |
| `plugins/wukong/hooks/hooks.json` | 新增 `PreToolUse` 的 `Skill` 一项；`UserPromptSubmit` 复用现有进程 |
| `plugins/wukong/hooks/session_check.py` | 增加「有新反馈」提醒 |
| `plugins/wukong/skills/prompt-sharpen/scripts/improve_hook.py` | 调用 `journal` 记录纠正与明说偏好 |
| `plugins/wukong/skills/reflect/SKILL.md` | 增加个人模式入口 |
| `plugins/wukong/skills/reflect/references/personal.md` | 新增：个人模式流程 |
| `plugins/wukong/skills/reflect/scripts/profile.py` | 新增：collect / validate / render / apply / undo / forget |
| `plugins/wukong/skills/setup-s-instructions/scripts/global_instructions.py` | 支持个人标记块 |
| `plugins/wukong/skills/setup-s-instructions/SKILL.md` | 说明个人块 |
| `plugins/wukong/skills/automate-me/SKILL.md` | 输出改为 `profile.json`，增加导入旧 `-mode` |
| `scripts/context_budget.py` | 新增：常驻 token 估算与上限 |
| `scripts/check_marketplace.py` | 调用常驻上限检查 |
| `plugins/wukong/hooks/README.md`、`HOSTS.md`、`README.md`、`CHANGELOG.md` | 文档 |

## 11. 测试

- `journal.py`：各事件格式正确；脱敏覆盖密钥、邮箱、URL 查询串；超 2 MB / 90 天裁剪；`WUKONG_JOURNAL=0` 不写；任何异常不输出、不报错；不向 stdout 打印。
- `profile.py validate`：`learned` 单会话证据被拒；禁学内容（推送、`--no-verify`、「不用问我」等）被拒；`verify` 放松类只接受 `explicit`；超 500 token 时按规则淘汰。
- 过期：`learned` 超 8 周删除，`explicit`/`manual` 保留。
- `apply` / `undo`：写入前备份；`undo` 恢复上一版并重写个人块；`history/` 只留 20 份。
- `global_instructions.py`：库块升级不改个人块；个人块写入不改库块；两块顺序固定；旧标记迁移逻辑不受影响。
- `context_budget.py`：估算对中英混排稳定；超上限时 `check_marketplace` 失败并列出最大项。
- 端到端（Claude Code）：纠正两次「太长了」→ `/reflect --me` → 弹窗确认 → 新会话个人块里出现对应规则。

## 12. 分期

| 期 | 内容 | 验收 |
|---|---|---|
| 1 | `context_budget.py` + `journal.py` + 钩子注册 | 正常使用一周，日志有事件、会话无可见变化、常驻 token 未增加 |
| 2 | `profile.py` + `reflect --me/--show/--undo/--forget` + 个人块写入 | 端到端测试通过；手动跑一次能生成合理规则 |
| 3 | `automate-me` 改造 + `SessionStart` 提醒 + 宿主核实 | 新用户首次初始化可用；各宿主支持情况写进 `HOSTS.md` |

第 1 期攒两到三周真实数据后再定第 2 期的纠正用语和归类提示词，不凭空调参。

## 13. 待定

- 纠正用语正则的初版是否偏宽：第 1 期结束后按日志里的误报率调整。
- 500 token 上限是否合适：第 2 期按实际规则条数再定。
- WorkBuddy、Cursor 的钩子能力：第 3 期逐个核实。
