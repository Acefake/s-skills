# 把 24 个 principle-* 并入所属技能：实现计划

## 目标

删除 24 个自动选用的 `principle-*` 技能目录。每条原则的正文原样迁到**唯一一个**所属技能的 `references/principles/<slug>.md`，全库所有引用改指向新位置，不留第二份副本。迁完后：

- 常驻上下文预算从 5,248 降到约 3,572（以 `context_budget.py` 实测为准），自动技能从 48 个降到 24 个，技能总数从 78 个降到 54 个。
- 每条原则的内容都保留：只去掉 frontmatter 和每份开头那行「全局提示词自检」，其余只改链接路径。删除旧目录前，脚本逐条核对正文。
- 原来走 principle 的触发场景改由所属技能承接，`trigger_cases.json` 全部指向实际存在的自动技能。
- `check_marketplace.py`、全量单元测试、链接检查、旧名检查都通过。仓库里除历史记录和退役名单外，不再出现 `principle-`，也不再有「原则 skill」之类把原则当独立技能的措辞。

## 全局约束

- 所有 Python 命令都用仓库的 `.venv/Scripts/python.exe`（3.12）。系统默认的 `python` 是 3.8，跑不了脚本里 3.10 以上的语法。
- 迁移由一个一次性脚本完成（任务 1），保证 24 份正文和全部引用按同一口径改写。脚本放在会话临时目录，不进仓库。
- 原地文件只改指向旧原则目录的链接和旧名字，其他链接一律不动，包括绝对路径、代码示例和 `url` 占位符。搬迁文件因为位置变了，才重算本地相对链接。
- 所属技能的 SKILL.md 新增原则索引节，每条一行：链接加上「何时读」。这一行是索引，不是正文副本。
- 24 个旧名字加入 `scripts/marketplace_lib.py` 的 `RETIRED_SKILLS`。此后技能文件里用反引号、加粗或 `/wukong:` 写出旧名，`check_marketplace.py` 会报错。裸名、路径和插件根目录文档由任务 6 的 grep 覆盖。
- 版本按 `bump_plugin_version.py wukong` 递增，README 和 `docs/architecture.md` 里的版本号由 bump 同步，不手改。提交和推送只在用户授权后按 `commit-pr` 做。
- `wukong-mode` 家族和其他点名技能这次都不删，只改它们里面的引用和措辞。

## 归属表（唯一位置）

| 所属技能 | 迁入 `references/principles/` 的原则 |
|---|---|
| `systematic-debugging` | `attack-the-premise`、`explain-the-number`（连同 `benchmark-checklist.md`）、`fix-root-causes` |
| `brainstorming` | `exhaust-the-design-space`、`experience-first`、`foundational-thinking`、`redesign-from-first-principles` |
| `writing-plans` | `outcome-oriented-execution`、`sequence-verifiable-units` |
| `test-strategy` | `test-behavior-not-implementation` |
| `subagent-driven-development` | `guard-the-context-window`、`never-block-on-the-human`、`separate-before-serializing-shared-state` |
| `code-style` | `boundary-discipline`、`build-the-lever`、`encode-lessons-in-structure`、`laziness-protocol`、`make-operations-idempotent`、`migrate-callers-then-delete-legacy-apis`、`minimize-reader-load`、`model-the-domain`、`prove-it-works`、`subtract-before-you-add`、`type-system-discipline` |

合计 24 条。代码设计类放在 `code-style`，因为全局规则要求「写或改代码时按 code-style」，写代码时它一定会被加载。

## 影响面

- **迁出**：`plugins/wukong/skills/principle-*/` 下 24 个目录，各含 `SKILL.md` 和 `agents/openai.yaml`；另有 `principle-explain-the-number/references/benchmark-checklist.md`。
- **脚本改写引用的文件**（相对 `plugins/wukong/`）：
  - `agents/wukong-agent.md`
  - `skills/` 下：`architect/SKILL.md`、`architect/references/rationale-template.md`、`brainstorming/SKILL.md`、`code-style/SKILL.md`、`figure-it-out/SKILL.md`、`impeccable/reference/optimize.md`、`no-comments/SKILL.md`、`refactor-architecture/SKILL.md`、`reflect/SKILL.md`、`requesting-code-review/code-reviewer.md`、`show-me-your-work/SKILL.md`、`subagent-driven-development/SKILL.md`、`systematic-debugging/SKILL.md`、`systematic-debugging/defense-in-depth.md`、`tdd/SKILL.md`、`test-strategy/SKILL.md`、`writing-plans/SKILL.md`、`wukong-agent/SKILL.md`、`wukong-mode/SKILL.md`、`wukong-mode/references/non-negotiable-rules.md`、`wukong-mode/playbooks/` 下 14 份、`wukong-review/SKILL.md`
- **手工改措辞**：
  - 上面文件中把原则称为 skill 的句子：`wukong-mode/SKILL.md:25,53,108`、`wukong-mode/references/non-negotiable-rules.md:5`、`code-style/SKILL.md:138`
  - 含「原则 skill」或「principle skill」的 `architect`、`figure-it-out`、`show-me-your-work`、`reflect`、14 份 playbook，以及迁入后的 `sequence-verifiable-units.md`
  - `agents/wukong-agent.md:13`、`wukong-agent/SKILL.md:19`、`architect/references/rationale-template.md:15`
- **脚本与测试**：`scripts/marketplace_lib.py`（`RETIRED_SKILLS`、`EXPECTED_SKILL_COUNTS`）、`scripts/check_marketplace.py`、`scripts/test_skill_resources.py`、`scripts/trigger_cases.json`、`scripts/install_local_skills.ps1`、`scripts/test_host_support.py`
- **清单与文档**：
  - `README.md`、`docs/architecture.md`、`docs/architecture/wukong-panorama.html`、`docs/s-skills-route.png`
  - `plugins/wukong/.claude-plugin/plugin.json`、`plugins/wukong/.cursor-plugin/plugin.json`、`plugins/wukong/plugin.json`
  - `.claude-plugin/marketplace.json`、`.cursor-plugin/marketplace.json`、`.agents/plugins/marketplace.json`（受 git 跟踪）
  - `plugin-versions.lock.json`（bump 更新）、`CHANGELOG.md`、`RENAMES.md`
- **本机残留**：`.agents/skills/principle-*`、`.codebuddy/skills/principle-*` 是指向旧目录的 Junction（git 忽略），删目录后会悬空。
- **不改**：`CHANGELOG.md` 的旧条目、`docs/wukong/specs/`、`docs/wukong/plans/` 下的历史文档。

---

## 任务 1：迁移正文、改写引用、核对后删除（脚本）

**文件**：新建 `<scratchpad>/migrate_principles.py`。

步骤 1：写脚本。

```python
"""一次性迁移：principle-* 正文搬进所属技能，并改写全库引用。在仓库根目录运行。

先搬、再改写、再逐条核对正文，全部一致后才删除旧目录；任何一步失败都不删。
"""
import filecmp
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path.cwd()
PLUGIN = ROOT / "plugins" / "wukong"
SKILLS = PLUGIN / "skills"
OWNERS = {
    "attack-the-premise": "systematic-debugging",
    "explain-the-number": "systematic-debugging",
    "fix-root-causes": "systematic-debugging",
    "exhaust-the-design-space": "brainstorming",
    "experience-first": "brainstorming",
    "foundational-thinking": "brainstorming",
    "redesign-from-first-principles": "brainstorming",
    "outcome-oriented-execution": "writing-plans",
    "sequence-verifiable-units": "writing-plans",
    "test-behavior-not-implementation": "test-strategy",
    "guard-the-context-window": "subagent-driven-development",
    "never-block-on-the-human": "subagent-driven-development",
    "separate-before-serializing-shared-state": "subagent-driven-development",
    "boundary-discipline": "code-style",
    "build-the-lever": "code-style",
    "encode-lessons-in-structure": "code-style",
    "laziness-protocol": "code-style",
    "make-operations-idempotent": "code-style",
    "migrate-callers-then-delete-legacy-apis": "code-style",
    "minimize-reader-load": "code-style",
    "model-the-domain": "code-style",
    "prove-it-works": "code-style",
    "subtract-before-you-add": "code-style",
    "type-system-discipline": "code-style",
}
assert len(OWNERS) == 24
SLUG = "|".join(sorted(OWNERS, key=len, reverse=True))
DAILY_CHECK = re.compile(r"^本会话首次使用本库技能时.*\n", re.M)
LINK = re.compile(r"\]\(([^)\s]+)\)")


def dest(slug: str) -> Path:
    return SKILLS / OWNERS[slug] / "references" / "principles" / f"{slug}.md"


CHECKLIST_OLD = SKILLS / "principle-explain-the-number" / "references" / "benchmark-checklist.md"
CHECKLIST_NEW = dest("explain-the-number").parent / "benchmark-checklist.md"


def rel(target: Path, source_file: Path) -> str:
    return Path(os.path.relpath(target, source_file.parent)).as_posix()


def is_local(target: str) -> bool:
    """只处理本地相对链接；网址、锚点、绝对路径和占位符原样保留。"""
    return not ("://" in target or target.startswith(("#", "/")) or re.match(r"[A-Za-z]:", target) or target == "url")


def remap(path: Path) -> Path:
    if path == CHECKLIST_OLD:
        return CHECKLIST_NEW
    m = re.fullmatch(rf"principle-({SLUG})", path.parent.name)
    if m and path.name == "SKILL.md" and path.parent.parent == SKILLS:
        return dest(m.group(1))
    return path


def rewrite_links(text: str, old_file: Path, new_file: Path, principles_only: bool) -> str:
    """principles_only=True：只改指向旧原则目录的链接（原地文件）。False：全部重算（搬迁文件）。"""
    def fix(m: re.Match) -> str:
        target = m.group(1)
        if not is_local(target):
            return m.group(0)
        local, sep, anchor = target.partition("#")
        old_target = Path(os.path.normpath(old_file.parent / local))
        new_target = remap(old_target)
        if principles_only and new_target == old_target:
            return m.group(0)
        return f"]({rel(new_target, new_file)}{sep}{anchor})"
    return LINK.sub(fix, text)


def rewrite_names(text: str, file: Path) -> str:
    """把加粗、反引号、链接文字、路径或裸写的 principle-x 换成指向新文件的写法。"""
    link = lambda m: f"[{m.group(1)}]({rel(dest(m.group(1)), file)})"
    text = re.sub(rf"\[principle-({SLUG})\]", r"[\1]", text)
    text = re.sub(rf"\*\*principle-({SLUG})\*\*", link, text)
    text = re.sub(rf"`principle-({SLUG})`", link, text)
    text = re.sub(rf"skills/principle-({SLUG})\b",
                  lambda m: f"skills/{OWNERS[m.group(1)]}/references/principles/{m.group(1)}.md", text)
    text = re.sub(rf"(?<![\w/\[-])principle-({SLUG})\b(?![\w/-])", link, text)
    return text


def normalize(text: str) -> str:
    """核对正文用：去掉链接目标和 principle- 前缀，剩下的文字必须逐字相同。"""
    text = LINK.sub("]()", text)
    text = re.sub(rf"\[(?:principle-)?({SLUG})\]\(\)", r"\1", text)
    text = re.sub(rf"\*\*principle-({SLUG})\*\*|`principle-({SLUG})`|principle-({SLUG})",
                  lambda m: next(g for g in m.groups() if g), text)
    return text


def write_lf(path: Path, text: str) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def in_principle_dir(path: Path) -> bool:
    return any(part.startswith("principle-") for part in path.relative_to(PLUGIN).parts)


# 1. 搬正文（搬迁文件位置变了，链接全部重算）
originals = {}
for slug in OWNERS:
    old = SKILLS / f"principle-{slug}" / "SKILL.md"
    raw = old.read_text(encoding="utf-8")
    assert raw.startswith("---\n"), old
    body = raw.split("\n---\n", 1)[1].lstrip("\n")
    body, n = DAILY_CHECK.subn("", body, count=1)
    assert n == 1, f"{old}: 没找到自检行"
    originals[slug] = body
    new = dest(slug)
    new.parent.mkdir(parents=True, exist_ok=True)
    assert not new.exists(), f"{new} 已存在"
    write_lf(new, rewrite_links(body, old, new, principles_only=False))
shutil.copy2(CHECKLIST_OLD, CHECKLIST_NEW)

# 2. 全库原地改写：只动指向旧原则的链接和旧名字
for file in sorted(PLUGIN.rglob("*.md")):
    if in_principle_dir(file):
        continue
    text = file.read_text(encoding="utf-8")
    new_text = rewrite_names(rewrite_links(text, file, file, principles_only=True), file)
    if new_text != text:
        write_lf(file, new_text)
        print("rewrote", file.relative_to(ROOT).as_posix())

# 3. 逐条核对正文，全部一致才删除旧目录
bad = [slug for slug in OWNERS
       if normalize(originals[slug]) != normalize(dest(slug).read_text(encoding="utf-8"))]
if not filecmp.cmp(CHECKLIST_OLD, CHECKLIST_NEW, shallow=False):
    bad.append("benchmark-checklist")
if bad:
    sys.exit(f"正文核对失败，未删除旧目录：{bad}")
for slug in OWNERS:
    shutil.rmtree(SKILLS / f"principle-{slug}")
print("moved and verified", len(OWNERS), "principles")
```

步骤 2：运行。

```bash
cd /c/Users/admin/s-skills && .venv/Scripts/python.exe -I "<scratchpad>/migrate_principles.py"
```

预期：最后一行是 `moved and verified 24 principles`。`rewrote` 行应覆盖影响面里「脚本改写引用」的全部文件，外加 24 份新文件中互相引用的那些。退出码非 0 时旧目录还在，修好脚本后用 `git checkout -- plugins && git clean -fd plugins/wukong/skills/*/references/principles` 还原再跑。

步骤 3：检查结果。

```bash
ls plugins/wukong/skills | grep -c '^principle-'                                  # 预期 0
find plugins/wukong/skills -path '*references/principles/*.md' | wc -l           # 预期 25
git diff -- plugins/wukong/skills/archify plugins/wukong/skills/why plugins/wukong/skills/project-memory   # 预期无输出：无关链接没被改
```

步骤 4：抽查 diff。
- `wukong-mode/SKILL.md:34` 变为 `[model-the-domain](../code-style/references/principles/model-the-domain.md)`。
- `requesting-code-review/code-reviewer.md:64` 变为 `skills/code-style/references/principles/laziness-protocol.md`。
- `systematic-debugging/defense-in-depth.md:3` 变为 `[边界原则](../code-style/references/principles/boundary-discipline.md)`。

## 任务 2：改掉把原则当独立技能的措辞

步骤 1：通用替换。只改 plugins 下含这两个短语的文件：

```bash
cd /c/Users/admin/s-skills
git grep --untracked -l -E "原则 ?skill|principle skill" -- plugins | xargs sed -i -E 's/原则 ?skill/原则/g; s/principle skill/principle/g'
```

步骤 2：逐句手改。

- `wukong-mode/SKILL.md:25` 和 `wukong-mode/references/non-negotiable-rules.md:5`：把「只引用你在这次会话里读过其末端 SKILL.md 的原则。」改为「只引用你在这次会话里读过其原则文件的原则。」
- `wukong-mode/SKILL.md:53`：把整句「你应用任何一条原则时，都要完整地读它的末端 skill。每一条都写明了它什么时候适用。每个末端的文件夹和 `name` 都是英文 kebab-case，和下面列出的名字一致，例如 `principle-laziness-protocol`。」改为「你应用任何一条原则时，都要完整地读它的原则文件。下表每条链接指向所属技能 `references/principles/` 下的文件，每份都写明了它什么时候适用。」注意：脚本会先把句中的 `principle-laziness-protocol` 改成链接，改句时以文件现状为准。
- `wukong-mode/SKILL.md:108`：「就去读那条原则的 skill」改为「就去读那条原则的文件」。
- `code-style/SKILL.md:138`：「细则在各原则技能里，这里只列必须过的几条：」改为「细则在下面「设计原则」列出的文件里，这里只列必须过的几条：」
- `agents/wukong-agent.md:13` 和 `wukong-agent/SKILL.md:19`：「用到哪条原则，就去读那条 `principle-*` skill。」改为「用到哪条原则，就去读它所在技能 `references/principles/` 下的文件，`wukong-mode` 的原则表列出了全部入口。」后半句不动。
- `architect/references/rationale-template.md:15`：脚本改过的「（例如 `per [boundary-discipline](...)`）」整段改为「（例如「按 code-style 的 boundary-discipline」）」。

步骤 3：确认没有残留。

```bash
git grep --untracked -n -E "原则 ?skill|原则的 ?skill|原则技能|末端 ?(SKILL|skill)|principle skill|principle-\*" -- plugins   # 预期无输出
```

## 任务 3：所属技能加原则索引节，补描述

在下面 6 个 SKILL.md 中，`code-style` 的节插在「## 交付前自审」之前，其余放在文件末尾：

`systematic-debugging/SKILL.md`：

```markdown
## 原则

- [fix-root-causes](references/principles/fix-root-causes.md)：调试时把症状追到系统第一次出错的地方。
- [attack-the-premise](references/principles/attack-the-premise.md)：共享同一前提的两次修复都失败时，先写下前提并直接验证。
- [explain-the-number](references/principles/explain-the-number.md)：相信、报告或按测量数字行动前，先找出限制因素；基准测试按其中的清单做。
```

`brainstorming/SKILL.md`：

```markdown
## 原则

- [exhaust-the-design-space](references/principles/exhaust-the-design-space.md)：没有先例的界面交互或架构决定，先做两三个原型再选。
- [experience-first](references/principles/experience-first.md)：产品和范围取舍选让人用着顺的，少做但做好。
- [foundational-thinking](references/principles/foundational-thinking.md)：写逻辑前先定核心类型和数据结构。
- [redesign-from-first-principles](references/principles/redesign-from-first-principles.md)：新需求要整合进已有设计时重做这一层，不补在旧形状上。
```

`writing-plans/SKILL.md`：

```markdown
## 原则

- [sequence-verifiable-units](references/principles/sequence-verifiable-units.md)：多步工作每步停在可验证的状态。
- [outcome-oriented-execution](references/principles/outcome-oriented-execution.md)：目标已定的重写和迁移直接走向目标结构，不留过渡代码。
```

`test-strategy/SKILL.md`：

```markdown
## 原则

- [test-behavior-not-implementation](references/principles/test-behavior-not-implementation.md)：写、改或保留测试时，断言使用者能看到的东西。
```

`subagent-driven-development/SKILL.md`：

```markdown
## 原则

- [guard-the-context-window](references/principles/guard-the-context-window.md)：大段输出、长文件和计划只在主线程留摘要。
- [never-block-on-the-human](references/principles/never-block-on-the-human.md)：可撤销的工作做完再给人看，不为能自己答的问题停下。
- [separate-before-serializing-shared-state](references/principles/separate-before-serializing-shared-state.md)：多个参与者可能写同一文件、分支、键或对象时，先消除共享。
```

`code-style/SKILL.md`：

```markdown
## 设计原则

按场景读对应文件：

- [boundary-discipline](references/principles/boundary-discipline.md)：加校验、错误处理或框架适配时，防护集中在边界，业务放纯函数。
- [type-system-discipline](references/principles/type-system-discipline.md)：设计类型或签名时，在边界解析外部数据，穷尽变体。
- [model-the-domain](references/principles/model-the-domain.md)：同一数据形状或状态判断在多处重复时，收成一个结构。
- [minimize-reader-load](references/principles/minimize-reader-load.md)：代码难追时，去掉没有独立职责的转手层，缩小可变状态。
- [laziness-protocol](references/principles/laziness-protocol.md)：重构或评估改动时，留能解决问题的最小改动。
- [subtract-before-you-add](references/principles/subtract-before-you-add.md)：新增、重构或重写前，先删死代码和多余校验。
- [migrate-callers-then-delete-legacy-apis](references/principles/migrate-callers-then-delete-legacy-apis.md)：引入新内部 API 时，同一轮迁完调用方并删掉旧的。
- [make-operations-idempotent](references/principles/make-operations-idempotent.md)：命令、生命周期或循环中断重跑要落到同一结果。
- [build-the-lever](references/principles/build-the-lever.md)：不简单的活做成可再跑的工具。
- [encode-lessons-in-structure](references/principles/encode-lessons-in-structure.md)：同一教训第二次出现，写成 lint、标记或脚本。
- [prove-it-works](references/principles/prove-it-works.md)：宣布完成前，对照真实产物核验。
```

description 只补触发词。`check_marketplace.py` 要求：以「…」引号短语开头，第 100 个字符内闭合，中文句在前、`Use when` 在后。下面三条都满足，整行替换：

- `systematic-debugging`：
  `description: "「修 bug」「报错了」「测试失败」「结果不对」「按钮没反应」「这个数字靠谱吗」。先查根因再改。bug-fix 和 fix bug 也走这里。Use when you hit any bug, test failure, unexpected behavior, or a suspicious measured number before proposing a fix, including 修 bug, 报错, bug-fix, and fix bug."`
- `code-style`：
  `description: "「文件放哪」「补文档注释」「看代码规范」「校验放哪」「类型怎么设计」「能删就删」。写或改 TypeScript、React、Vue、Go、Java 时按模块就近放文件，含边界校验、类型、领域建模、幂等、迁移旧接口等设计原则。仓库已有规范优先。Use when writing, changing, or reviewing TypeScript, React, Vue, Go, or Java code, to apply the owner's module layout, doc comment, quality, and design rules."`
- `subagent-driven-development`：
  `description: "「在这个会话里派子智能体做」「按计划逐个任务做」「多个子代理会写同一文件」。任务互相独立时用。要换会话按检查点做，用 executing-plans。Use when you are executing an implementation plan of independent tasks in the current session, or parallel agents might write the same file."`

这几个技能本来就是自动选用，`agents/openai.yaml` 不用动。

## 任务 4：校验脚本、测试、触发用例、安装脚本

**`scripts/marketplace_lib.py`**：
- 在 `RETIRED_SKILLS` 中按字母序加入 24 个 `principle-<slug>`。
- 第 33 行 `"wukong": 78` 改为 `"wukong": 54`。

**`scripts/check_marketplace.py`**：
- 删掉第 412–413 行「without the principle- prefix」的 `elif` 分支。
- 第 405 行的 docstring 改为 `"""Return references to retired skills."""`。

**`scripts/test_skill_resources.py`**：把 `test_principle_without_prefix_is_reported` 换成下面的测试。这里的旧名是测试夹具，任务 6 的 grep 会把这个文件排除在外。

```python
    def test_retired_principle_is_reported(self):
        active = {'code-style'}
        archived = {'principle-fix-root-causes'}
        problems = skill_reference_problems('按 **principle-fix-root-causes** 原则。', active, archived)
        self.assertEqual(len(problems), 1, problems)
        self.assertEqual(skill_reference_problems('按 `code-style` 的原则。', active, archived), [])
```

**`scripts/trigger_cases.json`** 第 33–55 行：`prompt` 不变，`expect` 按下表改。

| 行 | 新 expect | 行 | 新 expect |
|---|---|---|---|
| 33 | `["systematic-debugging"]` | 45 | `["brainstorming"]` |
| 34 | `["systematic-debugging"]` | 46 | `["brainstorming"]` |
| 35 | `["code-style"]` | 47 | `["none"]` |
| 36 | `["code-style"]` | 48 | `["code-style"]` |
| 37 | `["code-style"]` | 49 | `["code-style"]` |
| 38 | `["systematic-debugging"]` | 50 | `["none"]` |
| 39 | `["wukong-review", "deslop", "code-style"]` | 51 | `["writing-plans", "code-style"]` |
| 40 | `["test-strategy", "tdd"]` | 52 | `["brainstorming"]` |
| 41 | `["brainstorming"]` | 53 | `["subagent-driven-development"]` |
| 42 | `["writing-plans"]` | 54 | `["code-style"]` |
| 43 | `["requesting-code-review", "code-style"]` | 55 | `["code-style"]` |
| 44 | `["code-style"]` | | |

第 47、50 行分别是「日志交给子代理只给摘要」和「可撤销的先做再看」，由全局规则覆盖，不该由某个技能抢答。

**`scripts/install_local_skills.ps1`**：清理挂在「校验之后」的已有清理阶段，这样遇到冲突、拒绝安装时，什么都不会被删。

1. 在 `Test-IsLegacySkillJunction` 函数之后加：

```powershell
# 指向本仓库当前技能目录、但技能已被删除的 Junction：目标不存在才算。
function Test-IsRemovedSkillJunction {
    param(
        [System.IO.FileSystemInfo]$Item,
        [string]$SourceRoot
    )
    if ($Item.LinkType -ne 'Junction') {
        return $false
    }
    $rawTarget = @($Item.Target) | Where-Object { $_ } | Select-Object -First 1
    if (-not $rawTarget) {
        return $false
    }
    $normalizedTarget = ([System.IO.Path]::GetFullPath([string]$rawTarget)).TrimEnd('\')
    $prefix = ([System.IO.Path]::GetFullPath($SourceRoot)).TrimEnd('\') + '\'
    return $normalizedTarget.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase) -and -not (Test-Path -LiteralPath $normalizedTarget)
}
```

2. 把校验循环之后那段清理的条件，从 `if (Test-IsLegacySkillJunction -Item $entry -LegacyRoots $legacySourceRoots) {` 改为：

```powershell
    if ((Test-IsLegacySkillJunction -Item $entry -LegacyRoots $legacySourceRoots) -or (Test-IsRemovedSkillJunction -Item $entry -SourceRoot $sourceRoot)) {
```

**`scripts/test_host_support.py`** 的 `test_codex_install_migrates_legacy_junctions_and_protects_foreign_entries`：

1. 在 `dangling_legacy_junction` 定义之后加：

```python
            def dangling_junction(name, target):
                # 目标先建后删，只留下悬空 Junction。
                target.mkdir(parents=True)
                junction(dest_skills/name, target)
                target.rmdir()
```

2. 在 `junction(dest_skills/'foreign', foreign_target)` 之后加：

```python
            dangling_junction('removed-skill', plugin/'skills/removed-skill')
            dangling_junction('foreign-gone', root/'other-repo/skills/gone')
```

3. 在第一次成功安装的断言之后（`self.assertTrue(foreign_target.is_dir())` 之后）加：

```python
            self.assertFalse(os.path.lexists(str(dest_skills/'removed-skill')))
            self.assertTrue(os.path.lexists(str(dest_skills/'foreign-gone')))
```

4. 在场景一的 `dangling_legacy_junction('stale')` 之后加 `dangling_junction('removed-later', plugin/'skills/removed-later')`；在该场景的 `self.assertTrue(os.path.lexists(str(dest_skills/'stale')))` 之后加：

```python
            self.assertTrue(os.path.lexists(str(dest_skills/'removed-later')))
```

## 任务 5：文档、全景图、清单与版本

1. **`README.md`**：
   - 删掉「### 原则 principle-*（24）」整节，从标题到 `</details>`，即第 219–251 行。仓库里没有指向这一节的锚点。
   - 第 11 行只改数字：`<strong>78</strong>` 改为 `<strong>54</strong>`，`48 个` 改为 `24 个`。保留 `当前版本 1.0.22`，由 bump 同步。
   - 第 139 行 `78 个技能卡片` 改为 `54 个技能卡片`。
   - 在 `code-style` 那一行的用途末尾加「；含 11 条设计原则」。在 `systematic-debugging`、`brainstorming`、`writing-plans`、`test-strategy`、`subagent-driven-development` 的行末加「；含 N 条原则」，N 按归属表填。
2. **`docs/architecture.md`**：
   - 第 5 行只改数字，`78` 改为 `54`，`48` 改为 `24`，版本号由 bump 同步。
   - 第 7、21 行的 `78` 改为 `54`。
   - 第 11 行「下半部分以五个分栏」改为「四个分栏」，并删掉「原则卡省略共同的 `principle-` 前缀，实际目录名不变。」。
   - 删掉表格里「做事原则 | 24」那一行。表后加一句：「原则不再单独成卡，正文在所属技能的 `references/principles/`。」
   - 第 81 行「下方五栏」改为「下方四栏」。截图尺寸在第 5 步导出后按实测值回填。
3. **`docs/architecture/wukong-panorama.html`**：
   - 删掉 24 个 `class="skill-card principle auto"` 卡片、「做事原则」分栏及其标题，以及 `.principle{…}`、`.principles .card-title strong{…}`、`.principles .policy{…}` 这三条样式。
   - 把剩余分栏改为四栏布局。
   - `<h1>` 里的 `78 个技能` 改为 `54 个技能`。
   - 所有 `1.0.19` 改为 bump 后的新版本号。
   - `48 个自动选用 / 30 个显式调` 改为 `24 个自动选用 / 30 个显式调`。
   - 第二节标题里提到独立原则分区的文字一并删掉。
4. **宿主清单里的技能数**：以下位置的 `78 个` 改为 `54 个`，其余文字不动。「做事原则」保留，内容还在。
   - `plugins/wukong/.claude-plugin/plugin.json:4`
   - `plugins/wukong/.cursor-plugin/plugin.json:4`
   - `plugins/wukong/plugin.json:5`、`:23`、`:24`
   - `.claude-plugin/marketplace.json:4`、`:12`
   - `.cursor-plugin/marketplace.json:7`、`:14`
   - `.agents/plugins/marketplace.json:9`
5. **版本**：运行 `.venv/Scripts/python.exe scripts/bump_plugin_version.py wukong`。它会同步清单、锁文件，以及 README、架构文档里的版本号。然后把全景图里的版本号改成同一个值。
6. **`docs/s-skills-route.png`**：在会话临时目录里用 Playwright 导出，宽 4500，整页截图。

   ```bash
   cd "<scratchpad>" && npm i -D playwright && npx playwright install chromium
   node -e "const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:4500,height:1000}});await p.goto('file:///C:/Users/admin/s-skills/docs/architecture/wukong-panorama.html');await p.screenshot({path:'C:/Users/admin/s-skills/docs/s-skills-route.png',fullPage:true});await b.close();})()"
   .venv/Scripts/python.exe -c "from PIL import Image;print(Image.open('C:/Users/admin/s-skills/docs/s-skills-route.png').size)"
   ```

   用 Read 打开 PNG 看一眼，确认没有空栏、错位或残留的原则卡。再把实测尺寸回填到 `docs/architecture.md:81`。
7. **`CHANGELOG.md`** 顶部新增（版本号用 bump 后的值）：

   ```markdown
   ## 1.0.23

   ### 改动

   - 24 个 `principle-*` 不再作为自动技能常驻，正文原样迁入所属技能的 `references/principles/`：调试类归 `systematic-debugging`，设计类归 `brainstorming`，计划类归 `writing-plans`，测试类归 `test-strategy`，子代理协作类归 `subagent-driven-development`，代码设计类归 `code-style`。所属技能新增原则索引节，全库引用改为指向新文件。常驻上下文约 5,248 → 约 3,572 token，自动技能 48 → 24，技能总数 78 → 54。
   - `install_local_skills.ps1` 会清理指向已删除技能的悬空 Junction，安装冲突被拒时不清理。
   ```

8. **`RENAMES.md`** 末尾追加：`1.0.23 把 24 个 principle-* 并入所属技能的 references/principles/，名字留在 RETIRED_SKILLS。`

## 任务 6：验收

全部符合预期才算完成。

```bash
cd /c/Users/admin/s-skills
.venv/Scripts/python.exe scripts/check_marketplace.py                       # 预期：无 problem，退出码 0
.venv/Scripts/python.exe -m unittest discover -s scripts -p "test_*.py"     # 预期：OK（含新增的 Junction 断言）
.venv/Scripts/python.exe scripts/context_budget.py | tail -1                # 预期：total 约 3,572，低于 5650
.venv/Scripts/python.exe scripts/context_budget.py | grep -c principle      # 预期：0
git grep --untracked -n "principle-" -- . ":!CHANGELOG.md" ":!RENAMES.md" ":!docs/wukong/specs" ":!docs/wukong/plans" ":!scripts/marketplace_lib.py" ":!scripts/test_skill_resources.py"   # 预期：无输出
git grep --untracked -n -E "原则 ?skill|原则的 ?skill|原则技能|末端 ?(SKILL|skill)|principle skill" -- plugins   # 预期：无输出
git grep --untracked -n -E "principles/[a-z-]+\.md\)\**[^.。]{0,25}(skill|技能)" -- plugins                      # 预期：无输出（链接后紧跟 skill 的说法）
git grep --untracked -n -E "78 个" -- . ":!CHANGELOG.md" ":!RENAMES.md" ":!docs/wukong"                          # 预期：无输出
```

全量链接检查，覆盖插件目录、README 和架构文档，有坏链时退出码为 1：

```bash
.venv/Scripts/python.exe -I - <<'EOF'
import re, sys
from pathlib import Path
files = list(Path("plugins/wukong").rglob("*.md")) + [Path("README.md"), Path("docs/architecture.md")]
bad = []
for f in files:
    t = re.sub(r"```.*?```", "", f.read_text(encoding="utf-8"), flags=re.S)
    t = re.sub(r"`[^`\n]*`", "", t)
    for target in re.findall(r"\]\(([^)\s]+)\)", t):
        if "://" in target or target.startswith(("#", "/")) or target == "url":
            continue
        if not (f.parent / target.split("#")[0]).exists():
            bad.append(f"{f}: {target}")
print("\n".join(bad) or "all links ok")
sys.exit(1 if bad else 0)
EOF
```

本机安装：

```powershell
powershell -NoProfile -File scripts/install_local_skills.ps1
powershell -NoProfile -File scripts/install_local_skills.ps1 -HostName workbuddy
(Get-ChildItem .agents/skills, .codebuddy/skills | Where-Object Name -like 'principle-*').Count   # 预期 0
```

在线触发评测要调用模型、会产生费用，用户同意后才跑：`.venv/Scripts/python.exe scripts/eval_triggers.py`。结构测试只能证明用例集合合法，证明不了第 35–37 行（做成脚本、写成 lint、崩溃重跑）真的会命中 `code-style`，这三条最好实测一次。

最后按 `code-style` 的「交付前自审」审完整 diff，再按 `requesting-code-review` 派一个只读评审，范围：
- 正文核对的结果
- 所有新链接
- 措辞改写
- `trigger_cases` 映射
- 安装脚本和新测试

## 发布到各宿主（仓库外）

改完仓库后，已安装的插件（当前会话加载的是 1.0.16）仍是旧版。要按 `release` 发版，再在各宿主更新插件，新的预算才会生效。这一步按用户的发版习惯另行执行。
