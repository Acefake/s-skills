# 合并执行类技能、删除 pptx/pdf/xlsx（1.0.24）

## 目标

1. 把 7 个技能合并成一个自动调用的执行技能 `executing-plans`：
   `wukong-mode`、`wukong-agent`、`figure-it-out`、`timed-loop`、`using-git-worktrees`、`executing-plans`、`subagent-driven-development`。
2. 删除 `pptx`、`pdf`、`xlsx`。`docx`、`remotion-create`、`theme-factory` 等其余技能不动。
3. 发布 1.0.24。

技能总数 54 → 45（-6 合并，-3 删除）。

## 明确不做

- 不动 swarm、show-me-your-work、automate-me、project-memory、wukong-proposal、why、interrogate、refactor-architecture、no-comments、unslop、architect、author-skill、mcp-builder。
- 不动个人学习层（journal、reflect）。
- 不改历史记录：`CHANGELOG.md` 旧条目、`RENAMES.md` 旧条目、`docs/wukong/plans|specs/` 旧文件。

## 合并后的 `executing-plans`

位置：`plugins/wukong/skills/executing-plans/`。自动调用（不设 `disable-model-invocation`）。description 一个，覆盖下面所有入口的触发词，写法照仓库其他技能：「中文触发词」+ 一句中文 + `Use when ...`。

`SKILL.md` 正文控制在约 10 KB 以内，按场景分节，每节写清何时用、怎么做，细节放 `references/`：

1. **主会话按计划执行**：原 `executing-plans` 正文。
2. **派子代理逐任务执行**：原 `subagent-driven-development` 正文精简；它的 `implementer-prompt.md`、`task-reviewer-prompt.md`、`references/`、`scripts/`、`agents/openai.yaml` 整体搬入（路径改到新技能下）。
3. **先隔离工作区**：原 `using-git-worktrees`，压成一节；宿主自带 worktree 时优先用宿主的。
4. **反复检查直到通过**：原 `timed-loop`，一小节；宿主有 `/loop` 或定时任务时用宿主的。
5. **没有现成流程时**：原 `figure-it-out`，一小节（现定一套可审计做法再执行）。
6. **严格模式要点**：从 `wukong-mode/SKILL.md` 和 `references/non-negotiable-rules.md` 只留真正必要、其他技能没覆盖的几条（做完必须验证、不留 AI 腔、代码从简等），合成一小节，不复制整份。

`wukong-mode` 的资源处理：
- 搬入新技能 `references/`：`subagents.md`（24 处外部引用，派发公共规则）、`host-fallback.md`、`execution-boundaries.md`、`non-negotiable-rules.md`（外部有 3 处引用；可精简）。
- 搬 `scripts/check-plan.mjs` 及其测试（有外部引用）；`orch`、`watch-pr`、`worktree-audit.sh`、`bootstrap.ts`、`package.json`、`bun.lock` 只在新技能正文确实用到时才搬，否则删除。
- `playbooks/` 全部删除。外部引用 `playbooks/orchestrate.md`、`playbooks/opening-a-pr.md`、`playbooks/refactoring.md` 的地方改成指向新技能的对应小节或 `wukong:commit-pr`、`refactor-architecture` 自身的说明。
- 其余 references（bugbot-triage、catch-up、playbook-routing、writing-the-reply）删除；外部若有引用，改写成一句直白要求。

`wukong-agent`：删除 `skills/wukong-agent/` 和 `plugins/wukong/agents/wukong-agent.md`。`agents/comment-sicko.md` 保留。

## 需要同步的地方

1. 所有活跃文件里对这 9 个旧技能名、`wukong-mode/...` 路径的引用，改为新技能或删除。用 `grep -rn` 找全，排除上面「不改历史记录」的文件和 `.agents/`、`.codebuddy/`。重点：`plugins/wukong/AGENTS.md`、`rules/AGENTS.md`、`HOSTS.md`、`hooks/git_guard.py`、`wukong-router/SKILL.md` 和 `references/*-tools.md`、`commit-pr`、`prompt-sharpen`、`writing-plans`、`brainstorming`、`setup-s-models` 引用处、`setup-s-instructions` 当前版本提示词（只改最新的 v9 和 short 版；旧版不改）。
2. `scripts/marketplace_lib.py`：`EXPECTED_SKILL_COUNTS["wukong"]` 改 45；9 个旧名加入 `RETIRED_SKILLS`。
3. `scripts/trigger_cases.json`：删掉旧技能用例，原 executing-plans / subagent-driven-development / using-git-worktrees 的正例改指向新的 `executing-plans`。
4. 测试里写死旧名的（如 `test_context_budget.py`）同步改。
5. `README.md`、`docs/architecture.md`、`docs/architecture/wukong-panorama.html`（卡片与技能一一对应，`check_marketplace.py` 会校验）；全景图 PNG 若有重截流程照做，做不了就说明。
6. `CHANGELOG.md` 新增 1.0.24 条目，只分新增 / 修改 / 修复（这次主要是"修改"：合并、删除）。

## 验收

依次跑通，全部通过：

```
python scripts/update_skill_policies.py
python scripts/bump_plugin_version.py wukong   # → 1.0.24
python scripts/check_marketplace.py
python -m unittest discover -s scripts -p "test_*.py"
python scripts/context_budget.py               # 记录前后数值，前值 3572
```

再确认：`grep -rn` 活跃文件里无旧技能名残留；新 `executing-plans/SKILL.md` 里每个相对链接都指向存在的文件。
