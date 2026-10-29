### Bug fix

先读取并遵守[执行边界](../references/execution-boundaries.md)。以下步骤仅在已有任务授权和验证档位内执行。

**You own this task. Plan, review, verify.** Delegate investigation and the fix to subagents, stay in the lead. Pick each subagent's reasoning level and fast or standard speed for the job, per the Subagents section.

Be scientific. Every shipped line traces to runtime evidence. Belt-and-suspenders that "might help" is a hypothesis, not a fix. It does not ship. When evidence refutes a hypothesis, revert what it motivated. The smallest change the evidence justifies ships, nothing more.

1. Reproduce it yourself on the matching surface via the control skill (Non-negotiables), even when a debug or instrumentation protocol says to ask the user to reproduce. Ask the user only with a stated, specific reason the control surface cannot reach the target, and only after driving it as far as it goes. If it won't reproduce directly, synthesize the trigger, tighten conditions, or instrument until it fires.
2. Binary-search the cause. Form the candidate hypotheses, then rule them out until one survives. Seed them with `how` over the affected subsystem and the **why** skill for regression history. Each pass, take the split that cuts the most remaining problem space, get runtime evidence, eliminate. When program state is unclear, add instrumentation or logging and read it as the code runs. Don't guess. For a long or stubborn hunt, re-check on a cadence with `/timed-loop`. If the app cannot wake the main chat on a timer, follow that skill's per-app section. Confirm the surviving *mechanism* with runtime evidence before the step-3 architect/interrogate fan-out.
3. Plan the fix. Use `architect` only for substantial unresolved choices about ownership, state, or interfaces. A fix that crosses a function boundary but follows an established design does not need architecture exploration. Delegate implementation to a subagent using your configured bug-fix model (the `bug-fix` line in the s model config from setup-s-models; if the app cannot set a sub-agent model, omit it and say so. Do not paste a Cursor model slug into another app) with a specific scope.
4. Verify on the same surface. The original repro now passes. "Inconclusive" or wrong-surface is not a pass. Flag it. Unit tests show branch behavior, not bug absence.
5. When commits are authorized and TDD applies, put the failing repro before the fix in history. Otherwise preserve the local changes and repro evidence. See the **tdd** skill for the failing-test-first cadence when the bug has a cheap local test path. Skip it when the test would be expensive, integration-heavy, or unclear.
   This is the canonical **principle-sequence-verifiable-units** principle skill, the failing test first and the fix on top.
6. Run **Opening a PR** only when authorized; otherwise deliver local changes and verification results.

**Reply:** what was broken, root cause, fix, how you verified. Paste failing-then-passing repro output verbatim.
