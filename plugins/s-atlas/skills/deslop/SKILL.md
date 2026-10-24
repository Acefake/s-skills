---
name: deslop
description: "「/deslop」「提交前清一下 AI 味」「去掉多余的 any」。清这次 diff 里的代码腔：多余注释、不该有的防御、过深嵌套。文字腔用 /unslop，只清注释用 /no-comments。Use when a diff needs AI-flavored code removed before commit: extra comments, needless guards, any-casts, or deep nesting."
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。


# 去掉代码腔

对照 `main` 看 diff，删掉这条分支新引进的 AI 代码腔。

`/unslop` 管的是文字。这个 skill 管的是代码。两份都要留着，不要互相代替。

## 重点看这些

- 多余的行内注释，或者和这个文件当地写法不一致的注释。符合 `code-style` 第二节的文档注释要保留，缺了还要补上
- 在本来可信的路径上，显得反常的防御检查或 `try/catch`
- 只为绕过类型问题而把值转成 `any`
- 嵌套太深、用提前返回就能变直的代码
- 和当前文件、周围代码库不一致的其他写法

## 边界

- 行为保持不变，除非是在修一个明确的 bug。
- 改动要小、要集中，不要大范围重写。
- 最后的总结写短，一两句到三句。

## 在不同软件里怎么用

做法不依赖聊天软件。对当前仓库跑 `git diff main`（或这次真正的基础分支），只动 diff 里新出现的代码腔。

Cursor、OpenCode、Codex 都按上面的清单改。WorkBuddy 和 Claude Code 同样。没有 git diff 时，就看用户指出的文件。
