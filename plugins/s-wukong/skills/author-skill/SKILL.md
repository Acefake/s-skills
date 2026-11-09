---
name: author-skill
description: "「/author-skill」「新建一个 skill」「大改 SKILL.md」。按目录、name、description 和步骤写技能说明。文字写完用 /unslop。Use when creating or substantially editing a SKILL.md."
disable-model-invocation: true
---

本会话首次使用本库技能时，按[全局提示词自检](../setup-s-instructions/references/daily-check.md)只读检查一次。
## 运行环境适配

涉及宿主工具、模型配置或子代理时，按需阅读[宿主适配](../../HOSTS.md)。


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

## 宿主适配


Codex、Claude Code、Cursor、WorkBuddy 的工具和配置见[宿主适配](../../HOSTS.md)；按当前宿主读取对应参考。
