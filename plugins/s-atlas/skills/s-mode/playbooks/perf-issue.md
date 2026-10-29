### Perf issue

先读取并遵守[执行边界](../references/execution-boundaries.md)。以下步骤仅在已有任务授权和验证档位内执行。

**You own the measurement story. Plan, review, verify the numbers.** Tie every fix to a measurement, don't read source instead of measuring.

1. Capture a baseline trace via the matching control skill. For React or Vue interaction latency, frame drops, or bundle size, use the budgets and measurement setup in `impeccable optimize` (`impeccable/reference/optimize.md`). Vet the baseline, and each later number, with the **benchmark-checklist** skill.
2. `how` to ground hypotheses. Don't claim a perf ceiling without running it first.
   Try the performance mantras in order, cheapest first:
   1. Don't do it. Stop work whose result nothing uses rather than cheapening it.
   2. Do it, but don't do it again.
   3. Do it less.
   4. Do it later.
   5. Do it when they're not looking.
   6. Do it concurrently.
   7. Do it cheaper.

   When an earlier mantra meets the target, stop.
3. Plan the fix from the trace. Use `architect` only for substantial unresolved choices about ownership, state, or interfaces. A fix that crosses a function boundary but follows an established design does not need architecture exploration. Delegate implementation to a subagent using your configured perf-issue model (the `perf-issue` line in the s model config from setup-s-models; if the app cannot set a sub-agent model, omit it and say so. Do not paste a Cursor model slug into another app). Pick each subagent's reasoning level and fast or standard speed for the job, per the Subagents section. Review the diff. Capture a post-fix trace.
   Apply the **principle-sequence-verifiable-units** principle skill, verifying each attempt before trying the next.
4. Parse and compare the artifacts (JSON to sqlite, diff). "Inconclusive" or wrong-surface is not a pass. Flag it.
5. Cite the measurement in the PR.
6. Run **Opening a PR** only when authorized; otherwise deliver local changes and verification results.

For sustained improvement against a metric rather than a one-off fix, use the Hillclimb playbook (`playbooks/hillclimb.md`).

**Reply:** baseline number, post-fix number, delta, artifact path.
