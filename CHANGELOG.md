# 变更记录

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
