---
name: author-skill
description: "「/author-skill」「新建一个 skill」「大改 SKILL.md」。按目录、name、description 和步骤写技能说明。文字写完用 /unslop。Use when creating or substantially editing a SKILL.md."
disable-model-invocation: true
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。


# 编写 skill

写出或改好一份技能说明书。Cursor 内置的 `/create-skill` 原文没有公开。下面的步骤按 [Cursor 的 Agent Skills 文档](https://cursor.com/docs/skills) 写。文档里有、原文里没有的细节，以文档为准。

## 步骤

1. 问清这个 skill 什么时候该被用上，以及做完长什么样。
2. 建一个目录，里面放 `SKILL.md`。目录名和 frontmatter 的 `name` 必须相同。
3. frontmatter 至少写 `name` 和 `description`。`description` 以用户会说的话起头，用「」括上，放在前 100 个字里。中文句子写完，句号后接英文 `Use when`。
4. 正文写步骤、边界，以及需要时的例子。长参考放进 `references/`，可执行的东西放进 `scripts/`，模板放进 `assets/`。正文里用相对路径点它们。
5. 只有明确要求“只有点名才加载”时，才加 `disable-model-invocation: true`。
6. 只在某类文件上才该出现时，加 `paths`（glob）。文档里的旧字段 `globs` 还能用，新文件写 `paths`。
7. 写完用 `/unslop` 过文字。然后自己读一遍：`name` 是否等于目录名，`description` 是否还在。

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
description: "「用户会说的这句话」。做什么。Use when <the English trigger>."
---
```

## 在不同软件里怎么用

### Cursor

斜杠菜单里如果有内置的 `/create-skill`，用它起草、测试、迭代。它认得 Cursor 自己的目录和校验。没有这条内置命令时，按上面的步骤写。

项目级放 `.cursor/skills/<技能名>/` 或 `.agents/skills/<技能名>/`。个人级放 `~/.cursor/skills/<技能名>/`。文档还写 Cursor 会为了兼容去读 `.claude/skills/`、`.codex/skills/`、`~/.claude/skills/`、`~/.codex/skills/`。

`name` 用小写英文、数字和连字符，并且等于目录名。本插件的技能名都是这种英文 kebab-case。新 skill 也按这个写，不要再用中文目录名。

### OpenCode

按上面的步骤写。个人 skill 不要假设写进某个家目录就会被自动加载。项目里可以放 `.opencode/skills/<技能名>/SKILL.md`（V2 也认旧的 `.opencode/skill/`）。写完告诉用户怎么让这次会话读到它。

### Codex

按上面的步骤写。文档化的项目位置包括 `.agents/skills/<技能名>/SKILL.md`。个人目录没有在这次核对的 Codex 文档里写成唯一路径时，先放仓库里的 `skills/<技能名>/SKILL.md`，并告诉用户。

### WorkBuddy 和 Claude Code

Claude Code 的个人 skill 放 `~/.claude/skills/<技能名>/SKILL.md`，项目级放 `.claude/skills/`。WorkBuddy 的个人目录这次没有单独的文档，先放仓库的 `skills/<技能名>/SKILL.md`，并告诉用户怎么加载。两处都用上面的 frontmatter。
