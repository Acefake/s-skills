---
name: 编写skill
description: "按 Agent Skills 的形状写一份 SKILL.md：目录、YAML 的 name 和 description、正文步骤。用于 /编写skill、新建或大改一个 skill。文字写完用 /清理AI腔。"
disable-model-invocation: true
---

# 编写 skill

写出或改好一份技能说明书。Cursor 内置的 `/create-skill` 原文没有公开。下面的步骤按 [Cursor 的 Agent Skills 文档](https://cursor.com/docs/skills) 写。文档里有、原文里没有的细节，以文档为准。

## 步骤

1. 问清这个 skill 什么时候该被用上，以及做完长什么样。
2. 建一个目录，里面放 `SKILL.md`。目录名和 frontmatter 的 `name` 必须相同。
3. frontmatter 至少写 `name` 和 `description`。`description` 写成智能体能用来判断“该不该用”的那句话，包含用户真会说的说法。
4. 正文写步骤、边界，以及需要时的例子。长参考放进 `references/`，可执行的东西放进 `scripts/`，模板放进 `assets/`。正文里用相对路径点它们。
5. 只有明确要求“只有点名才加载”时，才加 `disable-model-invocation: true`。
6. 只在某类文件上才该出现时，加 `paths`（glob）。文档里的旧字段 `globs` 还能用，新文件写 `paths`。
7. 写完用 `/清理AI腔` 过文字。然后自己读一遍：`name` 是否等于目录名，`description` 是否还在。

目录形状：

```text
<技能名>/
  SKILL.md
  scripts/
  references/
  assets/
```

frontmatter 的最小形状：

```markdown
---
name: <技能名>
description: <做什么，以及什么时候用>
---
```

## 在不同软件里怎么用

### Cursor

斜杠菜单里如果有内置的 `/create-skill`，用它起草、测试、迭代。它认得 Cursor 自己的目录和校验。没有这条内置命令时，按上面的步骤写。

项目级放 `.cursor/skills/<技能名>/` 或 `.agents/skills/<技能名>/`。个人级放 `~/.cursor/skills/<技能名>/`。文档还写 Cursor 会为了兼容去读 `.claude/skills/`、`.codex/skills/`、`~/.claude/skills/`、`~/.codex/skills/`。

Cursor 文档要求内置流程里的 `name` 用小写英文、数字和连字符，并且等于目录名。本插件的技能用中文名，这是 S 自己的选择，不要把已有中文技能改成英文。新写给 Cursor 市场、又要避开中文名限制的 skill，跟用户确认再用英文目录名。

### OpenCode

按上面的步骤写。个人 skill 不要假设写进某个家目录就会被自动加载。项目里可以放 `.opencode/skills/<技能名>/SKILL.md`（V2 也认旧的 `.opencode/skill/`）。写完告诉用户怎么让这次会话读到它。

### Codex

按上面的步骤写。文档化的项目位置包括 `.agents/skills/<技能名>/SKILL.md`。个人目录没有在这次核对的 Codex 文档里写成唯一路径时，先放仓库里的 `skills/<技能名>/SKILL.md`，并告诉用户。

### WorkBuddy 和 Claude Code

Claude Code 的个人 skill 放 `~/.claude/skills/<技能名>/SKILL.md`，项目级放 `.claude/skills/`。WorkBuddy 的个人目录这次没有单独的文档，先放仓库的 `skills/<技能名>/SKILL.md`，并告诉用户怎么加载。两处都用上面的 frontmatter。
