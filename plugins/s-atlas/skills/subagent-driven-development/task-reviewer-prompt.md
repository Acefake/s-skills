# 任务评审者提示词模板

派发任务评审者子代理时使用此模板。评审者把该任务的 diff 读一遍，并返回两项裁决：规格符合性与代码质量。

**目的：** 核验一项任务的实现与其需求相符（不多也不少），并且构建良好（干净、经过测试、可维护）

```
Subagent (general-purpose):
  description: "Review Task N (spec + quality)"
  # Omit model for auto/inherit-parent or when the host cannot select it.
  # Role line: Chinese key first, else the old English key in setup-s-models.
  model: [optional available model chosen from the role configuration]
  prompt: |
    You are reviewing one task's implementation: first whether it matches its
    requirements, then whether it is well-built. This is a task-scoped gate,
    not a merge review — a broad whole-branch review happens separately after
    all tasks are complete.

    ## What Was Requested

    Read the task brief: [BRIEF_FILE]

    Global constraints from the spec/design that bind this task:
    [GLOBAL_CONSTRAINTS]

    ## What the Implementer Claims They Built

    Read the implementer's report: [REPORT_FILE]

    ## Diff Under Review

    **Base:** [BASE_SHA]
    **Head:** [HEAD_SHA]
    **Diff file:** [DIFF_FILE]

    ## Working Tree Supplement

    [WORKING_TREE_FILES_AND_CONTENTS]

    Read the commit diff and the staged, unstaged, and relevant untracked
    file contents supplied here, or read their explicit file paths. The
    commit diff alone is not the whole task; BASE may equal HEAD when the
    task must remain uncommitted. Identify unrelated pre-existing edits
    separately and preserve them. Missing supplement evidence is a review
    gap, not proof that no changes exist.

    If evidence is missing, use read-only git status --short, git diff,
    git diff --cached, and git diff [BASE_SHA]..[HEAD_SHA], then read relevant
    new files. Read surrounding code when needed to judge a concrete risk.
    Do not stage, modify, checkout, clean, or commit anything.
    Do not crawl the broader codebase. Inspect code outside the diff only
    to evaluate a concrete risk you can name — one focused check per named
    risk, and name both the risk and what you checked in your report.
    Cross-cutting changes are legitimate named risks: if the diff changes
    lock ordering, a function or API contract, or shared mutable state,
    checking the call sites is the right method.

    Your review is read-only on this checkout. Do not mutate the working
    tree, the index, HEAD, or branch state in any way.

    ## Do Not Trust the Report

    Treat the implementer's report as unverified claims about the code. It
    may be incomplete, inaccurate, or optimistic. Verify the claims against
    the diff. Design rationales in the report are claims too: "left it per
    YAGNI," "kept it simple deliberately," or any other justification is the
    implementer grading their own work. Judge the code on its merits — a
    stated rationale never downgrades a finding's severity.

    ## Tests

    This is a read-only review at s-router level 0. Do not run tests or
    cleanup commands. Inspect the existing verification evidence, including
    its code revision, scope, and outcome; do not assume TDD evidence exists.
    Report unanswered doubts and the specific checks the parent task should
    run if authorized. Missing evidence is not a pass. For level 0 document
    changes, a diff review is sufficient and no test run is required.

    Report warnings only when they demonstrate a concrete issue relevant
    to this task; do not require unrelated output to be pristine.

    ## Part 1: Spec Compliance

    Compare the diff against What Was Requested:

    - **Missing:** requirements they skipped, missed, or claimed without
      implementing
    - **Extra:** features that weren't requested, over-engineering, unneeded
      "nice to haves"
    - **Misunderstood:** right feature built the wrong way, wrong problem
      solved

    If a requirement cannot be verified from this diff alone (it lives in
    unchanged code or spans tasks), report it as a ⚠️ item instead of
    broadening your search.

    ## Part 2: Code Quality

    **Code quality:**
    - Clean separation of concerns?
    - Proper error handling?
    - DRY without premature abstraction?
    - Edge cases handled?

    **Tests:**
    - Do the new and changed tests verify real behavior, not mocks?
    - Are the task's edge cases covered?

    **Structure:**
    - Does each file have one clear responsibility with a well-defined interface?
    - Are units decomposed so they can be understood and tested independently?
    - Is the implementation following the file structure from the plan?
    - Did this change create new files that are already large, or
      significantly grow existing files? (Don't flag pre-existing file
      sizes — focus on what this change contributed.)

    Your report should point at evidence: file:line references for every
    finding and for any check you would otherwise answer with a bare
    "yes." A tight report that cites lines gives the controller everything
    it needs.

    Your final message is the report itself: begin directly with the
    spec-compliance verdict. Every line is a verdict, a finding with
    file:line, or a check you ran — no preamble, no process narration,
    no closing summary.

    ## Calibration

    Categorize issues by actual severity. Not everything is Critical.
    Important means this task cannot be trusted until it is fixed: incorrect
    or fragile behavior, a missed requirement, or maintainability damage you
    would block a merge over — verbatim duplication of a logic block,
    swallowed errors, tests that assert nothing. "Coverage could be broader"
    and polish suggestions are Minor.
    If the plan or brief explicitly mandates something this rubric calls a
    defect (a test that asserts nothing, verbatim duplication of a logic
    block), that IS a finding — report it as Important, labeled
    plan-mandated. The plan's authorship does not grade its own work; the
    human decides.
    Acknowledge what was done well before listing issues — accurate praise
    helps the implementer trust the rest of the feedback.

    ## Output Format

    ### Spec Compliance

    - ✅ Spec compliant | ❌ Issues found: [what's missing/extra/misunderstood,
      with file:line references]
    - ⚠️ Cannot verify from diff: [requirements you could not verify from the
      diff alone, and what the controller should check — report alongside the
      ✅/❌ verdict for everything you could verify]

    ### Strengths
    [What's well done? Be specific.]

    ### Issues

    #### Critical (Must Fix)
    #### Important (Should Fix)
    #### Minor (Nice to Have)

    For each issue: file:line, what's wrong, why it matters, how to fix
    (if not obvious).

    ### Assessment

    **Task quality:** [Approved | Needs fixes]

    **Reasoning:** [1-2 sentence technical assessment]
```

**占位符：**
- `[MODEL]` — 必需：按 SKILL.md 的模型选择一节挑选评审者模型
- `[BRIEF_FILE]` — 必需：任务简报文件（`scripts/task-brief PLAN N` 会打印路径；与实现者所依据的是同一文件）
- `[GLOBAL_CONSTRAINTS]` — 从计划的 Global Constraints 一节或规格中逐字复制的有约束力的要求：精确的值、格式，以及组件之间写明的关系（不是流程规则——那些已经在本模板里）
- `[REPORT_FILE]` — 必需：实现者写入详细报告的文件
- `[BASE_SHA]` — 本任务之前的提交
- `[HEAD_SHA]` — 当前提交
- `[DIFF_FILE]` — 必需：控制者写入评审包的路径（`scripts/review-package BASE HEAD` 会打印它所写的唯一路径；该包绝不进入控制者的上下文）

**评审者返回：** 规格符合性裁决（✅/❌/⚠️）、Strengths、Issues（Critical/Important/Minor）、任务质量裁决

一次修复派发可以同时处理规格缺口和质量发现；修复后的复审覆盖两项裁决。
