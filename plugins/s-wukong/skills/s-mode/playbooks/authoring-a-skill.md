### Authoring or modifying a skill

先读取并遵守[执行边界](../references/execution-boundaries.md)。以下步骤仅在已有任务授权和验证档位内执行。

**You own the skill's voice.**

1. Write the SKILL.md with `/author-skill`, then run `/unslop`. Cursor uses its built-in `/create-skill` when that command is in the menu. The skill says which.
2. Validate the skill: frontmatter has `name` and `description`, referenced files exist, cross-skill links resolve.
3. Follow s-router verification levels. Prose-only rule edits are level 0: review the diff without running tests. For executable changes, use the applicable existing checks.
4. Run **Opening a PR** only when authorized; otherwise deliver local edits and the diff review.

When in doubt, delete. Keep only prose that changes a decision. Tell it to do the thing and skip the reason. Explain only when the rule is confusing without one. Match tone to scope. Point at structural sources (types, READMEs, config) per the **principle-encode-lessons-in-structure** principle skill. Delegate to other skills by path. Don't restate. A workflow you keep hitting but isn't captured → propose a new skill.

**Reply:** summary of the skill, key design decisions, validation notes.
