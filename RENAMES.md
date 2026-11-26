# 退役技能对照

插件名是 `wukong`，目录是 `plugins/wukong/`，市场和仓库名是 `s-skills`。技能目录名等于 frontmatter 里的 `name`，全部为英文小写 kebab-case。

退役的技能名都记在 `scripts/marketplace_lib.py` 的 `RETIRED_SKILLS` 里，`check_marketplace.py` 会拦下对它们的引用。下表说明遇到旧名时现在该用什么。

## 并入现有技能

| 旧名 | 现在用 | 内容在哪 |
|---|---|---|
| `wukong-mode`、`wukong-agent`、`figure-it-out`、`timed-loop`、`using-git-worktrees`、`subagent-driven-development`、`dispatching-parallel-agents` | `executing-plans` | `SKILL.md` 与 `references/` |
| `swarm` | `executing-plans` | `references/swarm.md` |
| `no-comments` | `deslop` | `references/comment-sicko.md`，子代理在 `plugins/wukong/agents/comment-sicko.md` |
| `unslop` | `technical-writing` | `references/unslop.md` |
| `finishing-a-development-branch` | `commit-pr` | `references/finishing-branch.md` |
| `setup-s-instructions` | `wukong-init` | `scripts/global_instructions.py` |
| `test-driven-development` | `tdd` | |
| `writing-skills` | `author-skill` | |
| `teach` | `how`，问动机用 `why` | |
| `self-improvement`、`learn`、`automate-me` | `reflect`，个人规则用 `reflect --me` | |
| `interrogate` | `requesting-code-review` | |
| `sharpen` | `prompt-sharpen`、`brainstorming` | |
| `frontend-design`、`taste-skill`、`ui-ux-pro-max`、`web-design-guidelines`、`design-system`、`apple-glass`、`html-mockup`、`theme-factory` | `impeccable` | |
| `benchmark-checklist` | `systematic-debugging` | `references/principles/benchmark-checklist.md` |

## 原则并入所属技能

24 个 `principle-<名>` 不再是独立技能。正文在所属技能的 `references/principles/<名>.md`：

| 技能 | 原则 |
|---|---|
| `brainstorming` | exhaust-the-design-space、experience-first、foundational-thinking、redesign-from-first-principles |
| `code-style` | boundary-discipline、build-the-lever、encode-lessons-in-structure、laziness-protocol、make-operations-idempotent、migrate-callers-then-delete-legacy-apis、minimize-reader-load、model-the-domain、prove-it-works、subtract-before-you-add、type-system-discipline |
| `executing-plans` | guard-the-context-window、never-block-on-the-human、separate-before-serializing-shared-state |
| `systematic-debugging` | attack-the-premise、explain-the-number、fix-root-causes |
| `test-strategy` | test-behavior-not-implementation |
| `writing-plans` | outcome-oriented-execution、sequence-verifiable-units |

`verification-before-completion` 与 `prove-it-works` 重叠，用 `code-style` 的 `prove-it-works`。

## 删除且没有替代

`animate`、`animation-glossary`、`animation-performance`、`apple-design`、`arena`、`ask-sonner`、`blast-radius`、`break-ui`、`correct`、`create-verification-skill`、`emil-design`、`expo-animate`、`find-animation-opportunities`、`improve-animations`、`in-your-own-words`、`ketchup`、`maintain-verification-skill`、`make-bot-ui`、`native-mobile-feel`、`orca-bot-bug-hunt`、`orca-bot-ci-triage`、`orca-bot-deps`、`orca-bot-pr-review`、`orca-bot-release`、`orca-bots`、`patent-application`、`patent-disclosure`、`pdf`、`pick-frontend-lib`、`plain-language`、`pptx`、`premium-visual`、`prototype`、`recall`、`review-animations`、`s-help`、`setup-s-models`、`shadcn`、`translate`、`typescript-best-practices`、`visual-suite`、`xlsx`。

## 恢复一个退役技能

1. 用 `git log --all -- 'plugins/*/skills/<名>/' 'archive/s/<名>/'` 找到它最后存在的提交，取回目录放到 `plugins/wukong/skills/<名>/`。
2. 从 `RETIRED_SKILLS` 删掉这个名字，把 `EXPECTED_SKILL_COUNTS` 加一。
3. 按当前规范改写 `SKILL.md`，运行 `python scripts/bump_plugin_version.py wukong` 和 `python scripts/check_marketplace.py`。
