# 变更记录

## 1.0.17

### 新增

- 本地使用日志（个人学习层第 1 期）：`hooks/journal.py` 把会话开始、技能加载、用户纠正、明说的偏好和任务摘要写进本机 SQLite 数据库 `~/.wukong/journal.db`。每条一个事务，多会话并发写不丢数据；不打印、不占上下文、不上传；原话只留前 80 字并脱敏，90 天以前或超过 5 万条自动删除，`WUKONG_JOURNAL=0` 关闭，`journal.py --dump` 查看。设计见 `docs/wukong/specs/2026-11-13-personal-learning-design.md`。
- 个人规则（个人学习层第 2 期）：`reflect --me` 读本机使用日志，把反复出现的纠正和明说的偏好归纳成个人规则，展示差异并确认后写进全局规则里单独的 `wukong:personal` 块；库块升级不碰它。`reflect/scripts/profile.py` 负责准入（学来的至少 2 个会话）、8 周过期、500 token 上限、禁学内容（推送、跳过确认、密钥、网址、命令，以及从纠正里推断的放松验证）、备份 20 份；另有 `--show`、`--undo`、`--forget`、`--off`。
- 常驻上下文上限：`scripts/context_budget.py` 估算每个会话常驻的 token（自动技能描述、全局规则、钩子注入），`check_marketplace` 超过 5650 就失败。本版实测约 5380，1.0.16 约 6980。

### 改动

- 低频技能改为点名调用（`disable-model-invocation: true`，Codex 同步关闭隐式调用）：`docx`、`pptx`、`xlsx`、`pdf`、`technical-writing`、`html-mockup`、`apple-glass`、`archify`。不再常驻技能列表，用时直接点名，如「用 docx 做一份报告」。全局规则和 `wukong-router` 的路由表同步改为「点名时加载，未点名直接做」，触发用例去掉这些点名技能。
- 删除 `translate`、`frontend-design`、`patent-disclosure`、`patent-application`。翻译由模型直接做，界面设计用 `impeccable`。全局规则去掉对应行，旧版规则冻结为 `full-instructions-v8.txt`，已安装的无标记规则仍能原位迁移。
- 合并三个附属技能，正文移入宿主技能的 `references/`：`comment-sicko` → `no-comments`（同名子代理保留，改读新路径），`benchmark-checklist` → `principle-explain-the-number`，`ketchup` → `wukong-mode` 的 `catch-up.md`（autopilot 剧本的补进度回复照旧）。
- `apple-glass` 改为通用的 Apple TV 风格界面语言，去掉影盒专属的仓库、路径和检查命令，类名前缀 `yb-` 改为 `ag-`。
- 技能从 82 个减到 75 个：48 个自动，27 个点名。
- 小任务提速：只动一两个文件、不改接口的修 bug 归第 1 档，不强制先写失败测试；第 0、1 档自审只看 diff。独立评审子代理只在第 3 档（跨模块、改接口或依赖、迁移）或涉及权限、并发、共享状态、数据删除时派，原先任何修 bug 哪怕一行都会派。
- 全局规则「只读检索派发」细则移到 `wukong-router`，全局只留一句授权；旧规则冻结为 `full-instructions-v9.txt`。
- prompt-sharpen 钩子跳过「可以」「继续」这类确认和 4 个字以内的消息，这些消息不再附约 300 token 的评估说明。

## 1.0.16

### 修复

- 写入确认也用提问工具弹窗：共用的交互提问规则原先写「只有工具允许用于写入确认时才用它」，Codex 等宿主的提问工具没有写明这一点，于是写入确认退回了文字提问。现在先在对话里展示差异，再用同一提问工具给出「确认写入 / 先不写」等选项，只有工具不可用、报错或宿主明确禁止时才退回文字。
- `setup-s-models` 只拉一次能力目录就计算推荐，只对 `catalog` 标为可能截断的缺失模型补搜；原流程按白名单逐个 search，每次都返回全部提供商，白白占用大量上下文。

## 1.0.15

### 改动

- `setup-s-models` 在 T3 中按本机目录推荐角色模型：新增 `references/model-allowlist.json`（白名单、各角色偏好顺序、`providerOnly`），`scripts/t3_catalog.py catalog` 合并能力快照与 search 结果，每个角色沿偏好顺序取本机可用的前 4 个，缺哪家就往后补；白名单零匹配时退回本机完整目录，首项为 inherit-parent。Cursor 只露出 Grok 4.7 与 Composer 2.5，Claude 模型只走 Claude。
- 配置流程第 3 步改为弹窗：先问全部用推荐 / 逐个选 / 只改几个，再每个角色一次提问选首选模型、首选档位、次选模型、次选档位；用户填的编号或模型 ID 由 `t3_catalog.py pick` 校验。
- `wukong.t3.json` 升到 schemaVersion 2，目标可带 `fallback` 保存顺序次选；check 同时校验次选，resolve 每项返回 `fallback`，角色行的显式档位只作用于首选。schemaVersion 1 仍可读取，configure 写入统一为 2。原先只记在 `s-model-fallbacks.md` 的次选，可经确认后迁进 `fallback`。

## 1.0.14

### 改动

- 全局规则新增「只读检索派发」：预计读十个文件以上或大日志、只要结论且问题明确的只读调查，默认授权并发 2 个（三条独立边界才 3 个）「检索与探索」子代理，摘要约 30 行内；小范围、查完要改、需判断语义的仍由主代理直接查。该授权不含改文件、测试、提交，实现类子代理仍需用户要求。
- `wukong-mode` 并发只读检索和 T3 编排参考同步引用这条授权。已安装用户同步全局规则后生效。
- 提示词评估钩子的说明从约 440 token 压到约 310 token，判断标准不变；原话只引用前 200 字，长粘贴和交接摘要不再整段重复进上下文。
- T3 编排参考只保留派发时要用的角色、解析、路由与等待规则；模型目标格式、宿主路径表、作用域继承和配置写入移到 `setup-s-models/references/t3-config.md`，每次 T3 派发少读约 3k token。

## 1.0.13

### 改动

- 适配 CodeBuddy（CLI 与 IDE）：它会读取 `.claude-plugin` 清单，所以不新增清单，直接用 `/plugin marketplace add Acefake/s-skills` 和 `/plugin install wukong@s-skills`。README、宿主适配和 WorkBuddy 参考同步说明，CodeBuddy 与 WorkBuddy 共用 `~/.codebuddy`，宿主 id 仍是 `workbuddy`。
- 市场校验不再把 CodeBuddy 当作退役宿主；仍拒绝重复的 `.codebuddy-plugin` 清单。

## 1.0.12

### 改动

- 插件名从 `s-wukong` 改为 `wukong`，目录迁至 `plugins/wukong`，安装 id 为 `wukong@s-skills`；市场和仓库名称不变。
- 六个 `s-` 技能统一改为 `wukong-agent`、`wukong-init`、`wukong-mode`、`wukong-proposal`、`wukong-review`、`wukong-router`；其他技能名不变。
- 保留旧品牌全局规则、模型目标和事务的识别能力；冻结历史规则样本，避免无标记旧规则迁移时重复追加。
- 更新悟空 logo，并同步宿主清单、安装说明与架构证据链接。

## 1.0.10

### 改动

- 插件名从 s-atlas 改为 s-wukong，目录为 `plugins/s-wukong`。安装 id 从 `s-atlas@s-skills` 改为 `s-wukong@s-skills`。
- 仓库地址仍是 https://github.com/Acefake/s-skills ，marketplace 名仍是 s-skills。各技能自己的名字不变。
