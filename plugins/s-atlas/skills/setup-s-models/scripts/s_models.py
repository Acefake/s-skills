"""Render, check and write the s model block deterministically.

The skill asks the questions; this script owns the rules: which role gets the
fast or strong model, how many reviewers each budget sends, the budget line,
and how an existing block is replaced without touching the rest of the file.

    python s_models.py render --budget 省 --fast sonnet --strong opus
    python s_models.py check ~/.claude/rules/s-models.md
    python s_models.py write ~/.claude/rules/s-models.md --budget 大 --fast sonnet --strong opus --role-effort
    python s_models.py write ... --apply      # only this flag writes

Exit codes: 0 ok, 1 check problems or refused write, 2 bad arguments.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

START = '# s 模型配置'
END = '# s 模型配置结束'
OLD_START = '# s model configuration'
OLD_END = '# end s model configuration'
INHERIT = 'inherit-parent'
FREE_VALUES = (INHERIT, 'auto')

FAST = 'fast'
STRONG = 'strong'
REVIEW = 'review'

# (中文键, 旧英文键, 分组)。顺序就是写出顺序，和 SKILL.md 的模板一致。
ROLES = (
    ('写功能和重构', 'feature, refactoring', FAST),
    ('修 bug', 'bug-fix', FAST),
    ('性能问题', 'perf-issue', FAST),
    ('爬坡优化', 'hillclimb', FAST),
    ('判断和写作', 'judgment and prose', STRONG),
    ('最难的任务', 'hardest tasks', STRONG),
    ('怎么工作的探索者', 'how explorer', FAST),
    ('怎么工作的讲解者', 'how explainer', STRONG),
    ('为什么的调查者', 'why investigators', FAST),
    ('为什么的综合者', 'why synthesizer', STRONG),
    ('反思的工具视角', 'reflect tooling', FAST),
    ('反思的判断、发散和综合', 'reflect judgment, divergent, synthesizer', STRONG),
    ('竞技场参赛者', 'arena runners', REVIEW),
    ('竞技场交叉评审', 'arena cross-judge pool', REVIEW),
    ('群体作战的工作者', 'swarm workers', FAST),
    ('架构设计参赛者', 'architect runners', REVIEW),
    ('审问审查者', 'interrogate reviewers', REVIEW),
)
ROLE_KEYS = tuple(key for key, _, _ in ROLES)
OLD_TO_NEW = {old: new for new, old, _ in ROLES}
HARDEST = '最难的任务'

# 预算：中文名 → (目标推理档位, 评审项数下限, 上限)。上限 None 表示不封顶。
BUDGETS = {
    '省': ('medium', 1, 1),
    '中': ('high', 1, 2),
    '大': ('xhigh', 2, 2),
    '不限': ('max', 2, None),
}
BUDGET_ALIASES = {
    'small': '省', 'medium': '中', 'large': '大', 'unlimited': '不限',
    'skip': INHERIT, INHERIT: INHERIT,
}
EFFORTS = ('low', 'medium', 'high', 'xhigh', 'max')

HEADER = (
    START,
    '# 一行一个角色。删掉一行就用技能默认。',
    '# inherit-parent 或 auto：跟父对话的模型，派子代理时不传模型。',
    '# 逗号分隔的列表，每一项派一个子代理。竞技场交叉评审从中选一项。',
)


class SModelsError(Exception):
    """Input or file state the script refuses to act on."""


def normalize_budget(name: str) -> str:
    value = name.strip()
    if value in BUDGETS or value == INHERIT:
        return value
    if value.lower() in BUDGET_ALIASES:
        return BUDGET_ALIASES[value.lower()]
    raise SModelsError(f'未知预算 {name!r}：用 省、中、大、不限 或 inherit-parent')


def budget_line(budget: str, effort: str | None = None) -> str:
    if budget == INHERIT:
        return f'# 预算: {INHERIT}'
    target = BUDGETS[budget][0]
    actual = effort or target
    if actual not in EFFORTS:
        raise SModelsError(f'未知推理档位 {actual!r}：用 {"、".join(EFFORTS)}')
    if EFFORTS.index(actual) > EFFORTS.index(target):
        raise SModelsError(f'实际档位 {actual} 高于预算 {budget} 的目标 {target}，只能下调')
    return f'# 预算: {budget}（{actual}）'


ITEM_RE = re.compile(r'^(.*?)\s*[（(]\s*([a-z]+)\s*[）)]$')


def split_item(item: str) -> tuple[str, str | None]:
    """'sonnet（medium）' → ('sonnet', 'medium'); no suffix → (item, None)."""
    match = ITEM_RE.match(item.strip())
    return (match.group(1), match.group(2)) if match else (item.strip(), None)


def role_effort(budget: str, key: str, effort: str | None = None) -> str:
    """Starting level of one role: the budget level, hardest tasks one step up."""
    rule = '大' if budget == INHERIT else budget
    base = effort or BUDGETS[rule][0]
    if key == HARDEST and EFFORTS.index(base) < len(EFFORTS) - 1:
        return EFFORTS[EFFORTS.index(base) + 1]
    return base


def add_efforts(rows: dict[str, str], budget: str, effort: str | None) -> dict[str, str]:
    """Append （档位） to every item that does not already carry one."""
    out = {}
    for key, value in rows.items():
        level = role_effort(budget, key, effort)
        items = []
        for item in value.split(','):
            name, existing = split_item(item)
            items.append(f'{name}（{existing or level}）')
        out[key] = ', '.join(items)
    return out


def review_items(budget: str, fast: str, strong: str, third: str | None) -> list[str]:
    """Reviewer list for one budget. Fast first, then strong, then the third family."""
    rule = '大' if budget == INHERIT else budget
    distinct = [fast] + ([strong] if strong != fast else [])
    if rule == '省':
        return [fast]
    if rule == '中':
        return distinct
    if rule == '大':
        return distinct if len(distinct) == 2 else [fast, fast]
    items = distinct + ([third] if third and third not in distinct else [])
    return items if len(items) >= 2 else [fast, fast]


def render_rows(budget: str, fast: str | None, strong: str | None,
                third: str | None = None, inherit: bool = False,
                overrides: dict[str, str] | None = None) -> dict[str, str]:
    """Role → value. `inherit` means the host cannot pick a model per dispatch."""
    rule = '大' if budget == INHERIT else budget
    if inherit:
        low = BUDGETS[rule][1]
        rows = {key: (', '.join([INHERIT] * low) if group == REVIEW else INHERIT)
                for key, _, group in ROLES}
    else:
        if not fast:
            raise SModelsError('缺少 --fast：给出这次确认可用的快模型，或改用 --inherit')
        strong = strong or fast
        rows = {}
        for key, _, group in ROLES:
            if group == REVIEW:
                rows[key] = ', '.join(review_items(budget, fast, strong, third))
            elif group == STRONG and (rule != '省' or key == HARDEST):
                rows[key] = strong
            else:
                rows[key] = fast
    for key, value in (overrides or {}).items():
        if key in OLD_TO_NEW:
            key = OLD_TO_NEW[key]
        if key not in rows:
            raise SModelsError(f'未知角色 {key!r}')
        if not value.strip():
            raise SModelsError(f'角色 {key} 不能设成空值')
        rows[key] = value.strip()
    return rows


def render_block(budget: str, rows: dict[str, str], effort: str | None = None) -> str:
    lines = list(HEADER) + [budget_line(budget, effort)]
    lines += [f'{key}: {rows[key]}' for key in ROLE_KEYS]
    lines.append(END)
    return '\n'.join(lines)


# ---------- reading an existing file ----------

def find_block(lines: list[str]) -> tuple[int, int] | None:
    """Index of start and end line of the managed block, or None if absent."""
    starts = [i for i, line in enumerate(lines)
              if line.strip() == START or line.strip().startswith(OLD_START)]
    ends = [i for i, line in enumerate(lines)
            if line.strip() in (END, OLD_END)]
    if not starts and not ends:
        return None
    if len(starts) != 1 or len(ends) != 1 or ends[0] < starts[0]:
        raise SModelsError('标记段不完整或有多段：只看到一头、或起止各不止一个。请手动检查后再运行')
    return starts[0], ends[0]


def parse_block(lines: list[str]) -> tuple[str | None, dict[str, str], list[str]]:
    """Return (raw budget text, Chinese-keyed rows, notes about the source)."""
    budget, rows, notes = None, {}, []
    english: dict[str, str] = {}
    for line in lines:
        text = line.strip()
        match = re.match(r'#\s*(预算|budget)\s*[:：]\s*(.+)$', text)
        if match:
            budget = match.group(2).strip()
            if match.group(1) == 'budget':
                notes.append('预算行是旧英文写法，重写时会换成中文')
            continue
        if not text or text.startswith('#'):
            continue
        key, sep, value = text.partition(':')
        if not sep:
            notes.append(f'无法识别的行：{text}')
            continue
        key, value = key.strip(), value.strip()
        if key in ROLE_KEYS:
            if key in rows:
                notes.append(f'角色 {key} 出现了不止一次，以最后一次为准')
            rows[key] = value
        elif key in OLD_TO_NEW:
            english[OLD_TO_NEW[key]] = value
            notes.append(f'旧英文键 {key!r}，重写时会换成 {OLD_TO_NEW[key]}')
        else:
            notes.append(f'不在 17 个角色里的键 {key!r}，重写时不会写回')
    for key, value in english.items():
        rows.setdefault(key, value)
    return budget, rows, notes


def parse_budget_text(text: str | None) -> tuple[str | None, str | None]:
    """'大（xhigh）' or 'large (xhigh)' → ('大', 'xhigh')."""
    if not text:
        return None, None
    match = re.match(r'^(\S+?)\s*[（(]\s*([a-z]+)\s*[）)]$', text)
    name, effort = (match.group(1), match.group(2)) if match else (text, None)
    try:
        return normalize_budget(name), effort
    except SModelsError:
        return None, effort


def check_text(text: str, models: list[str] | None = None) -> dict:
    lines = text.splitlines()
    problems: list[str] = []
    span = find_block(lines)
    if span is None:
        return {'status': 'missing', 'problems': ['没有 s 模型配置段'], 'notes': []}
    start, end = span
    raw_budget, rows, notes = parse_block(lines[start + 1:end])
    if lines[start].strip() != START:
        notes.append('起止标记是旧英文写法，重写时会换成中文')
    budget, effort = parse_budget_text(raw_budget)
    if raw_budget is None:
        problems.append('缺少 # 预算 行')
    elif budget is None:
        problems.append(f'预算 {raw_budget!r} 无法识别')
    elif budget != INHERIT:
        target = BUDGETS[budget][0]
        if effort is None:
            problems.append(f'预算行缺少括号里的档位，例如 {budget}（{target}）')
        elif effort not in EFFORTS or EFFORTS.index(effort) > EFFORTS.index(target):
            problems.append(f'预算 {budget} 的档位 {effort} 不合法：只能是 {target} 或更低')
    for key, _, group in ROLES:
        value = rows.get(key)
        if value is None:
            notes.append(f'缺少角色 {key}，会用技能默认')
            continue
        raw_items = [item.strip() for item in value.split(',')]
        if any(not item for item in raw_items):
            problems.append(f'{key} 有空项')
            continue
        split = [split_item(item) for item in raw_items]
        items = [name for name, _ in split]
        for name, level in split:
            if not name:
                problems.append(f'{key} 有只写档位没写模型的项')
            elif level is not None and level not in EFFORTS:
                problems.append(f'{key} 的档位 {level} 不合法：用 {"、".join(EFFORTS)}')
        if group != REVIEW and len(items) != 1:
            problems.append(f'{key} 只能写一个模型，现在是 {len(items)} 项')
        if group == REVIEW and budget in BUDGETS:
            _, low, high = BUDGETS[budget]
            if len(items) < low or (high is not None and len(items) > high):
                want = f'恰好 {low}' if low == high else (f'{low} 到 {high}' if high else f'至少 {low}')
                problems.append(f'{key} 在预算 {budget} 下应为{want} 项，现在是 {len(items)} 项')
        if models is not None:
            unknown = [item for item in items if item not in FREE_VALUES and item not in models]
            if unknown:
                problems.append(f'{key} 用了这次未确认的模型：{", ".join(unknown)}')
    return {'status': 'ok' if not problems else 'problems',
            'budget': budget, 'effort': effort, 'rows': rows,
            'problems': problems, 'notes': notes}


# ---------- writing ----------

def read_file(path: Path) -> tuple[str, str]:
    if not path.exists():
        return '', '\n'
    data = path.read_bytes().decode('utf-8-sig')
    return data, '\r\n' if '\r\n' in data else '\n'


def merged_text(existing: str, block: str) -> tuple[str, str]:
    """Return (new text, action) where action is create / append / replace / unchanged."""
    lines = existing.splitlines()
    span = find_block(lines)
    if span is None:
        if not existing.strip():
            return block + '\n', 'create'
        return existing.rstrip('\r\n') + '\n\n' + block + '\n', 'append'
    start, end = span
    new_lines = lines[:start] + block.split('\n') + lines[end + 1:]
    text = '\n'.join(new_lines) + '\n'
    if text.replace('\r\n', '\n') == existing.replace('\r\n', '\n'):
        return text, 'unchanged'
    return text, 'replace'


def write_file(path: Path, block: str, apply: bool) -> dict:
    existing, newline = read_file(path)
    text, action = merged_text(existing, block)
    result = {'path': str(path), 'action': action, 'applied': False, 'backup': None}
    if not apply or action == 'unchanged':
        return result
    path.parent.mkdir(parents=True, exist_ok=True)
    if existing:
        backup = path.with_name(path.name + '.s-models.bak')
        if not backup.exists():
            backup.write_bytes(path.read_bytes())
            result['backup'] = str(backup)
    path.write_bytes(text.replace('\n', newline).encode('utf-8'))
    result['applied'] = True
    return result


# ---------- command line ----------

def parse_sets(values: list[str]) -> dict[str, str]:
    overrides = {}
    for item in values:
        key, sep, value = item.partition('=')
        if not sep:
            raise SModelsError(f'--set 要写成 角色=值，收到 {item!r}')
        overrides[key.strip()] = value
    return overrides


def add_render_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('--budget', required=True, help='省、中、大、不限，或 inherit-parent（跳过）')
    parser.add_argument('--fast', help='写代码类用的快模型')
    parser.add_argument('--strong', help='判断类用的强模型；不给就和快模型相同')
    parser.add_argument('--third', help='不限预算时第三个系列的模型')
    parser.add_argument('--effort', help='宿主没有目标档时实际使用的档位（只能下调）')
    parser.add_argument('--role-effort', action='store_true',
                        help='每个角色值后加（档位）：宿主能随派发传档位时用，如 Claude Code 的 Agent effort')
    parser.add_argument('--inherit', action='store_true', help='宿主不能按次传模型：全部写 inherit-parent')
    parser.add_argument('--set', action='append', default=[], metavar='角色=值', help='覆盖某一行，可重复')


def block_from_args(args: argparse.Namespace) -> str:
    budget = normalize_budget(args.budget)
    rows = render_rows(budget, args.fast, args.strong, args.third, args.inherit, parse_sets(args.set))
    if args.role_effort:
        rows = add_efforts(rows, budget, args.effort)
    block = render_block(budget, rows, args.effort)
    # --set 可能把评审行改成不合预算的项数；生成的段必须先过自己的校验。
    problems = check_text(block)['problems']
    if problems:
        raise SModelsError('生成的配置不合规则：' + '；'.join(problems))
    return block


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Render, check and write the s model block')
    sub = parser.add_subparsers(dest='command', required=True)
    render = sub.add_parser('render', help='只输出标记段')
    add_render_arguments(render)
    check = sub.add_parser('check', help='只读校验一个文件')
    check.add_argument('file')
    check.add_argument('--models', help='这次确认可用的模型，逗号分隔；给了就校验名字')
    write = sub.add_parser('write', help='替换或追加标记段，默认只预览')
    write.add_argument('file')
    add_render_arguments(write)
    write.add_argument('--apply', action='store_true', help='真正写入；不加只报告会做什么')
    for item in (render, check, write):
        item.add_argument('--json', action='store_true', help='输出 JSON')
    args = parser.parse_args(argv)
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    try:
        if args.command == 'render':
            block = block_from_args(args)
            print(json.dumps({'block': block}, ensure_ascii=False) if args.json else block)
            return 0
        if args.command == 'check':
            text, _ = read_file(Path(args.file).expanduser())
            models = [m.strip() for m in args.models.split(',')] if args.models else None
            result = check_text(text, models)
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(f'状态: {result["status"]}')
                for line in result['problems']:
                    print(f'问题: {line}')
                for line in result['notes']:
                    print(f'提示: {line}')
            return 0 if result['status'] == 'ok' else 1
        block = block_from_args(args)
        result = write_file(Path(args.file).expanduser(), block, args.apply)
        result['block'] = block
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            verb = '已写入' if result['applied'] else '将会'
            print(f'{verb}: {result["action"]} {result["path"]}')
            if result['backup']:
                print(f'备份: {result["backup"]}')
            if not args.apply and result['action'] != 'unchanged':
                print('未写入。确认后加 --apply 再运行。')
            print(block)
        return 0
    except SModelsError as exc:
        print(f'错误: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
