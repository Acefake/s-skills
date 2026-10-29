import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawnSync } from "node:child_process";
import { test } from "node:test";
import assert from "node:assert/strict";
import { fileURLToPath } from "node:url";

const checker = fileURLToPath(new URL("./check-plan.mjs", import.meta.url));
const rule =
	"Verification follows the recorded s-router level; inapplicable checks name a reason.";

const validPlan = `# Demo

## How to read this
**Skill source.** Installed plugin root and version recorded.
One box is one unit of work and names the evidence. Check a box only when its evidence exists. See playbooks/.
${rule}

## Program checklist
### Arm the program
### Spawn owners
### PR mechanics
### Verdict and merge
### Boot recipe
Read the recorded skill source. /loop 1h status message

## PR 1
**Depends on.** None.
**Files.**
- [ ] Do the thing.
**Build.**
- [ ] Do the thing.
**You see.**
- [ ] Do the thing.
**Verification level.** 2
**Verify, unit.** ${rule}
- [ ] Check the thing.
**Verify, live.** n/a. No interactive behavior changes.
**Verify, perf.** n/a. No performance claim.
**Review gate.** None.
**Merge.**
- [ ] Merge when approved.

## Close the program
Close.

## Appendix Prototype evidence
Recorded.
`;

const runPlan = (example, expectedExit, plan = validPlan) => {
	const directory = mkdtempSync(join(tmpdir(), "check-plan-test-"));
	const file = join(directory, "plan.md");
	writeFileSync(file, plan + example);
	try {
		const result = spawnSync("node", [checker, file], { encoding: "utf8" });
		assert.equal(result.status, expectedExit, result.stderr);
		return result;
	} finally {
		rmSync(directory, { recursive: true, force: true });
	}
};

test("accepts ordinary, indented, and longer closing fences", () => {
	for (const indent of ["", " ", "  ", "   "])
		runPlan(`${indent}\`\`\`markdown\n## Example only\n${indent}\`\`\`\n`, 0);
	runPlan("```markdown\n## Example only\n````\n", 0);
});

test("accepts nested backticks and tilde info strings", () => {
	runPlan("````markdown\n```markdown\n## Example only\n```\n````\n", 0);
	runPlan("~~~markdown `info`\n## Example only\n ~~~\n", 0);
});

test("keeps mismatched, shorter, and suffixed closers inside the fence", () => {
	runPlan("````markdown\n~~~\n## Example only\n````\n", 0);
	runPlan("````markdown\n```\n## Example only\n````\n", 0);
	runPlan("````markdown\n``` info\n## Example only\n````\n", 0);
});

test("rejects headings and prose outside a proper close", () => {
	for (const suffix of ["  ", "\t"]) {
		const heading = runPlan(`\`\`\`markdown\n## Example only\n\`\`\`${suffix}\n## Example only\n`, 1);
		assert.ok(heading.stderr.includes('"## Example only" after Close the program is not an appendix'));
	}

	const prose = runPlan("```markdown\nThis prose has a mid-sentence colon: inside code\n```\nThis prose has a mid-sentence colon: bad.\n", 1);
	assert.ok(prose.stderr.includes("mid-sentence colon"));
});

test("rejects backtick info strings containing a backtick", () => {
	const result = runPlan("```markdown `invalid`\n## Example only\n```\n", 1);
	assert.ok(result.stderr.includes('"## Example only" after Close the program is not an appendix'));
});


test("accepts a level 0 document plan with diff review and no test lanes", () => {
 const plan = validPlan.replace("**Verification level.** 2", "**Verification level.** 0")
  .replace(`**Verify, unit.** ${rule}\n- [ ] Check the thing.`, "**Verify, unit.** n/a. Document-only change; review the diff.");
 runPlan("", 0, plan);
});

test("accepts two live scenarios without imposing ten lanes", () => {
 const plan = validPlan.replace("**Verify, live.** n/a. No interactive behavior changes.",
  "**Verify, live.** Browser behavior checks.\n- [ ] Lane 1. Save `first.png`. Pass when saved.\n- [ ] Lane 2. Save `second.png`. Pass when reopened.");
 runPlan("", 0, plan);
});

test("accepts each implementation verification level", () => {
	for (const level of [1, 2, 3])
		runPlan("", 0, validPlan.replace("**Verification level.** 2", `**Verification level.** ${level}`));
});

test("rejects scheduled checks in a block marked n/a", () => {
	runPlan("", 1, validPlan.replace("n/a. No performance claim.", "n/a. No performance claim.\n- [ ] Probe. Run anyway."));
});

test("rejects missing or invalid verification levels", () => {
 runPlan("", 1, validPlan.replace("**Verification level.** 2\n", ""));
 runPlan("", 1, validPlan.replace("**Verification level.** 2", "**Verification level.** 9"));
});

test("rejects level 0 plans that schedule tests", () => {
 runPlan("", 1, validPlan.replace("**Verification level.** 2", "**Verification level.** 0"));
});

test("rejects unexplained n/a and live scenarios without evidence", () => {
 runPlan("", 1, validPlan.replace("n/a. No performance claim.", "n/a."));
 runPlan("", 1, validPlan.replace("n/a. No interactive behavior changes.", "Browser checks.\n- [ ] Lane 1. Pass when saved."));
});

test("rejects duplicate or non-contiguous live scenario numbers", () => {
 for (const number of [1, 3]) {
  const plan = validPlan.replace("n/a. No interactive behavior changes.",
   `Browser checks.\n- [ ] Lane 1. Save \`a.png\`. Pass when saved.\n- [ ] Lane ${number}. Save \`b.png\`. Pass when saved.`);
  runPlan("", 1, plan);
 }
});

test("requires complete evidence when a perf check is applicable", () => {
 const plan = validPlan.replace("**Verify, perf.** n/a. No performance claim.",
  "**Verify, perf.** Latency comparison.\n- [ ] Metric. Latency.\n- [ ] Probe. Same request.\n- [ ] Baseline. Trunk.\n- [ ] Rule. Head meets budget.");
 runPlan("", 0, plan);
 runPlan("", 1, plan.replace("- [ ] Rule. Head meets budget.\n", ""));
});


test("accepts screenshot-only and document-only review gates", () => {
 for (const evidence of ["Review the requested screenshot in `screen.png`.", "Review the document diff in `proposal.md`."])
  runPlan("", 0, validPlan.replace("**Review gate.** None.", `**Review gate.** User review before merge.\n- [ ] ${evidence}`));
});

test("rejects an active review gate without a requirement or checklist", () => {
 runPlan("", 1, validPlan.replace("**Review gate.** None.", "**Review gate.**\n- [ ] Review the document."));
 runPlan("", 1, validPlan.replace("**Review gate.** None.", "**Review gate.** User reviews the document."));
});

test("rejects a disabled review gate that still schedules work", () => {
 runPlan("", 1, validPlan.replace("**Review gate.** None.", "**Review gate.** None.\n- [ ] Request approval anyway."));
});
