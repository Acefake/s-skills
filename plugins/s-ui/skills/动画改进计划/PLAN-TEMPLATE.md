# 计划模板

`动画改进计划` 写的每一份计划都按这个结构。执行者可能是一个能力较弱、毫无背景、毫无审美的模型——计划必须准确地包含一切。不要引用“上面的审计”或“我们讨论过的缓动”。

```markdown
# NNN — <Short imperative title>

- **Status**: TODO
- **Commit**: <output of `git rev-parse --short HEAD` when this plan was written>
- **Severity**: HIGH | MEDIUM | LOW
- **Category**: <audit category>
- **Estimated scope**: <n files, rough size>

## Problem

What is wrong, where, and why it matters to how the product feels. Cite every
location as `path/to/file.tsx:123` and include the current code verbatim:

​```css
/* src/components/dropdown.css:14 — current */
.dropdown { transition: all 400ms ease-in; }
​```

## Target

The exact end state. Every value spelled out — curves, durations, spring
configs, media queries. Never "use a nicer easing":

​```css
/* target */
.dropdown {
  transition: transform 200ms var(--ease-out), opacity 200ms var(--ease-out);
  transform-origin: var(--transform-origin);
}
​```

## Repo conventions to follow

How this codebase already does it, with one exemplar the executor should
imitate (token names, file placement, prop patterns):

- Easing tokens live in `src/styles/tokens.css`; add new curves there, e.g. `--ease-out: cubic-bezier(0.23, 1, 0.32, 1);`
- <exemplar file:line that already does this correctly>

## Steps

1. <One concrete edit per step: file, what changes, resulting code.>
2. …

## Boundaries

- Do NOT touch <files/components out of scope>.
- Do NOT change markup/structure — motion properties only (unless a step says otherwise).
- Do NOT add new dependencies.
- If a step doesn't match the code you find (drift since the commit stamp), STOP and report instead of improvising.

## Verification

- **Mechanical**: <exact commands — typecheck, lint, build — with expected outcome>.
- **Feel check**: run the UI, trigger <interaction>, and confirm:
  - <observable check, e.g. "the dropdown scales from its trigger, not from center">
  - <e.g. "spamming the toggle never restarts the animation from zero">
  - In DevTools, set playback to 10% (Animations panel) and confirm <detail>.
  - Toggle `prefers-reduced-motion` (Rendering panel) and confirm movement is dropped but opacity feedback remains.
- **Done when**: <machine- or eye-checkable completion criteria>.
```

（模板各部分的意思：标题“编号——简短的祈使句标题”；状态、写计划时的 commit、严重程度、类别、预计范围；**Problem 问题**：哪里错了、为什么影响产品手感，每个位置写成 `path/to/file.tsx:123` 并原样附上当前代码；**Target 目标**：准确的最终状态，每个数值都写出来，绝不写“用个好点的缓动”；**Repo conventions to follow 要遵循的仓库惯例**：这个代码库已有的做法，附一个执行者应该模仿的范例；**Steps 步骤**：每步一个具体修改——文件、改什么、改完的代码；**Boundaries 边界**：不要碰范围外的文件，只改动效属性不改结构，不加新依赖，如果某一步和你看到的代码对不上（commit 之后代码变了），就停下来报告，不要即兴发挥；**Verification 验证**：机械检查的准确命令和预期结果，亲自感受的检查——触发交互并确认可观察到的效果、在开发者工具里把播放速度调到 10% 确认细节、打开 `prefers-reduced-motion` 确认移动被去掉但透明度反馈还在，以及“什么时候算完成”。）

## 给计划作者的说明

- 每条发现一份计划。如果两条发现涉及的文件完全一样、修法模式也一样（例如在多个组件里替换同一个缓动 token），可以合并成一份计划。
- 每个数值都取自 [AUDIT.md](AUDIT.md)——绝不凭记忆估个大概。
- 亲自感受的检查不是可选的。动效可能在机械上正确，感觉却还是不对；给执行者（或审查执行者改动的人）具体的、在慢动作下要注意的东西。
- 写完计划后，新建或更新 `plans/README.md`，内容包括：计划表（编号、标题、严重程度、状态）、推荐的执行顺序，以及计划之间的任何依赖关系。
