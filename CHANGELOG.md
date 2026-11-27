# 变更记录

每个版本只列对使用者有影响的变化。细节见对应的 [GitHub Release](https://github.com/Acefake/s-skills/releases) 和提交历史。

## 1.0.35

- 新增点名技能 `handoff`（技能总数 34 → 35，自动 20、点名 15，常驻上下文预算不变）：把当前会话的目标、分支与精确提交状态、已验证证据、踩坑与下一步接续提示词压缩成紧凑交接文档。
- 优化 `reflect`：补齐单条明确教训的轻量快路（≤10 行修改跳过 3+1 子代理），前台暴露 `--add` 直接记个人规则，并修复 Antigravity 与 Windows 下的会话日志定位。
- 增强 `brainstorming`（先查代码再沿决策树前沿逐问澄清）与 `project-memory`（按需支持 `glossary.md` 领域术语表同步）。

## 1.0.34

- 文档只描述当前版本：重写 README、架构说明和全景图，精简 CHANGELOG 与 RENAMES，删除 `docs/wukong/` 下的历史计划和规格。

## 1.0.33

- `executing-plans` 的并行群体作战改为 Antigravity 原生群体协调者说明的中文译本；其他宿主改用可用的子代理派发。

## 1.0.32

- 修复 Antigravity 对笼统提示词静默丢弃评估提醒：钩子不再附带 `metadata.user_markdown`。

## 1.0.31

- 技能从 43 个精简到 34 个（自动 20、点名 14）：删除 `interrogate`、`apple-glass`、`theme-factory`、`html-mockup`、`automate-me`；`no-comments` 并入 `deslop`，`unslop` 并入 `technical-writing`，`finishing-a-development-branch` 并入 `commit-pr`，`swarm` 并入 `executing-plans`。
- 支持的宿主改为 Codex、Claude Code、Antigravity，移除 Cursor、WorkBuddy、CodeBuddy。
- `wukong-init` 按宿主给检索、规划、审查、测试四个子代理角色配模型和推理档位。
- `prompt-sharpen` 钩子在提示词笼统时显示一行提示，并记录最近 50 次触发结果；后台运行提醒不再匹配引号和 heredoc 里的命令。

## 1.0.30

- 初始化统一为 `wukong-init`，删除 `setup-s-instructions`、`setup-s-models` 和六角色模型配置；子代理默认继承当前会话模型。
- Antigravity 接入 `prompt-sharpen` 钩子。
- 修复 T3 Code 包装消息导致短回复误触发、使用日志误记。

## 1.0.29

- 删除 `orca-bots`。

## 1.0.28

- 五个 `orca-bot-*` 合并为 `orca-bots`。

## 1.0.27

- 新增五个 Orca bot 技能。

## 1.0.26

- 插件图标从 1.11 MB 压缩到 25.5 KB。

## 1.0.25

- `wukong-mode`、`wukong-agent`、`figure-it-out`、`timed-loop`、`using-git-worktrees`、`subagent-driven-development` 并入 `executing-plans`；删除 `pptx`、`pdf`、`xlsx`。
- 全景图改为单独维护，不再参与 `check_marketplace.py` 检查。

## 1.0.23

- 24 个 `principle-*` 并入所属技能的 `references/principles/`，常驻上下文约减少三分之一。

## 1.0.19

- 新增点名技能 `mcp-builder`、`remotion-create`、`theme-factory`。
- 本地使用日志先脱敏再截断，避免密钥前缀落盘。
- 会话开始钩子同进程检查全局规则，启动耗时约减半。

## 1.0.18

- Codex 钩子路径检查与迁移（`codex_hooks.py`）。

## 1.0.17

- 新增本地使用日志 `~/.wukong/journal.db` 和 `reflect --me` 个人规则。
- 常驻上下文设上限，`check_marketplace.py` 超限即失败。
- 低频技能改为点名调用；小改动归第 1 档，独立评审只在第 3 档或高风险改动时派。

## 1.0.16

- 写入确认统一用宿主的提问工具。

## 1.0.15

- 子代理模型推荐按本机可用模型计算，支持次选模型。

## 1.0.14

- 全局规则新增只读检索派发授权；提示词评估说明压缩到约 310 token。

## 1.0.13

- 适配 CodeBuddy。

## 1.0.12

- 插件名从 `s-wukong` 改为 `wukong`，六个 `s-` 技能改为 `wukong-` 前缀。

## 1.0.10

- 插件名从 `s-atlas` 改为 `s-wukong`。
