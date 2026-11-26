"""Check or write the four-role subagent model block; write only with an explicit --apply."""
import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from global_instructions import (  # noqa: E402
    MODELS_END,
    MODELS_START,
    ConfigurationError,
    _marker_span,
    instruction_path,
    merge_models,
    write_preserving,
)

ROLES = ('检索', '规划', '审查', '测试')
INHERIT = '继承'
TITLE = '## wukong 子代理模型'
LINE = re.compile(r'^(\S+?)\s*[:：]\s*(.+?)\s*$')
EFFORTS = ('low', 'medium', 'high', 'xhigh', 'max')
# 角色没写括号时，派发规则用这些默认档位；见 executing-plans/references/subagents.md。
DEFAULT_EFFORTS = {'检索': 'medium', '规划': 'high', '审查': 'high', '测试': 'medium'}
VALUE = re.compile(r'^([^\s（）()<>]+)\s*(?:[（(]\s*([a-z]+)\s*[)）])?$')


def split_value(value):
    """
    拆开一行的取值
    @param value 如 `opus`、`opus（xhigh）`、`继承（high）`
    @returns (模型, 档位或 None)，模型为 `继承` 时表示不传模型
    """
    match = VALUE.match(value.strip())
    if not match:
        raise ConfigurationError(f'Expected 模型 or 模型（档位）, got {value!r}')
    model, effort = match.groups()
    if effort is not None and effort not in EFFORTS:
        raise ConfigurationError(f'Unknown effort {effort!r}; use one of {", ".join(EFFORTS)}')
    return model, effort


def normalize(value):
    model, effort = split_value(value)
    return f'{model}（{effort}）' if effort else model


def render(host, choices):
    """
    生成模型块正文
    @param host 宿主 id
    @param choices 角色到模型的映射，四个角色必须齐全
    @returns 不含标记的正文
    """
    missing = [role for role in ROLES if role not in choices]
    if missing:
        raise ConfigurationError(f'Missing roles: {", ".join(missing)}')
    extra = sorted(set(choices) - set(ROLES))
    if extra:
        raise ConfigurationError(f'Unknown roles: {", ".join(extra)}')
    lines = [TITLE, f'宿主: {host}', *(f'{role}: {normalize(choices[role])}' for role in ROLES)]
    return '\n'.join(lines)


def parse(text):
    """
    读出已写入的模型块
    @param text 全局指令文件全文
    @returns 角色到模型的映射；没有模型块时为 None
    """
    span = _marker_span(text, MODELS_START, MODELS_END, 'models')
    if not span:
        return None
    body = text[span[0] + len(MODELS_START):span[1] - len(MODELS_END)]
    found = {}
    for line in body.splitlines():
        match = LINE.match(line.strip())
        if match and match.group(1) in ROLES:
            found[match.group(1)] = match.group(2)
    return found


def resolve(roles):
    """
    算出每个角色实际派发用的模型和档位
    @param roles 模型块里的角色行；None 表示没有模型块
    @returns 角色到 {model, effort} 的映射，model 为 None 表示继承父会话
    """
    resolved = {}
    for role in ROLES:
        model, effort = split_value(roles[role]) if roles and role in roles else (INHERIT, None)
        resolved[role] = dict(model=None if model == INHERIT else model, effort=effort or DEFAULT_EFFORTS[role])
    return resolved


def _prepare_file(path, body):
    if path.is_symlink():
        raise ConfigurationError('Global instruction file is a symlink; inspect its destination before updating')
    original = path.read_bytes() if path.exists() else None
    text = original.decode('utf-8-sig') if original is not None else ''
    updated = merge_models(text, body).encode('utf-8')
    if original is not None and original.startswith(b'\xef\xbb\xbf'):
        updated = b'\xef\xbb\xbf' + updated
    changed = updated != (original or b'')
    return path, original, updated, changed, (MODELS_START in text)


def sync_models(host, choices, *, home, codex_home=None, claude_config_dir=None, apply=False):
    """Write the model block into the host global instruction file."""
    body = render(host, choices)
    block = f'{MODELS_START}\n{body}\n{MODELS_END}'
    path = instruction_path(host, Path(home), codex_home, claude_config_dir)
    # 先校验并算好全部目标文件，全部通过后再写入，避免 Codex 切换时写一半。
    primary = _prepare_file(path, body)
    pending = [primary]
    if host == 'codex':
        # Codex 只读其中一份；另一份里留下的模型块一并清掉，免得切换后读到旧值。
        directory = Path(codex_home).expanduser() if codex_home is not None else Path(home) / '.codex'
        for other in (directory / 'AGENTS.md', directory / 'AGENTS.override.md'):
            if other != path and other.exists():
                if other.is_symlink():
                    raise ConfigurationError('Global instruction file is a symlink; inspect its destination before updating')
                other_text = other.read_bytes().decode('utf-8-sig')
                if MODELS_START in other_text or MODELS_END in other_text:
                    pending.append(_prepare_file(other, ''))
    changed = any(item_changed for _, _, _, item_changed, _ in pending)
    if apply:
        for target_path, original, updated, item_changed, _ in pending:
            if item_changed:
                write_preserving(target_path, original, updated)
    status = 'configured' if apply or not changed else ('outdated' if primary[4] else 'missing')
    return dict(status=status, changed=bool(apply and changed), target=str(path), block=block)


def read_models(host, *, home, codex_home=None, claude_config_dir=None):
    """Return the configured roles, or None when the host file has no model block."""
    path = instruction_path(host, Path(home), codex_home, claude_config_dir)
    if path.is_symlink():
        raise ConfigurationError('Global instruction file is a symlink; inspect its destination before updating')
    if not path.exists():
        return None
    return parse(path.read_bytes().decode('utf-8-sig'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', required=True, choices=('codex', 'claude-code', 'antigravity'))
    parser.add_argument('--set', action='append', default=[], metavar='角色=模型',
                        help=f'repeat for {", ".join(ROLES)}; use {INHERIT} to inherit the parent model')
    parser.add_argument('--show', action='store_true', help='Print the current block and exit')
    parser.add_argument('--apply', action='store_true', help='Explicitly write the model block')
    parser.add_argument('--home', type=Path, default=Path.home())
    parser.add_argument('--codex-home', type=Path, default=os.environ.get('CODEX_HOME') or None)
    parser.add_argument('--claude-config-dir', type=Path, default=os.environ.get('CLAUDE_CONFIG_DIR') or None)
    args = parser.parse_args()
    paths = dict(home=args.home, codex_home=args.codex_home, claude_config_dir=args.claude_config_dir)
    try:
        if args.show:
            target = str(instruction_path(args.host, **paths))
            current = read_models(args.host, **paths)
            resolved = resolve(current)
            if current is None:
                print(json.dumps(dict(status='missing', target=target, roles=None, resolved=resolved)))
                return 2
            missing = [role for role in ROLES if role not in current]
            if missing:
                print(json.dumps(dict(status='outdated', target=target, roles=current, missing=missing, resolved=resolved)))
                return 2
            print(json.dumps(dict(status='configured', target=target, roles=current, resolved=resolved)))
            return 0
        choices = {}
        for item in args.set:
            role, found, model = item.partition('=')
            if not found:
                raise ConfigurationError(f'Expected 角色=模型, got {item!r}')
            key = role.strip()
            if key in choices:
                raise ConfigurationError(f'Duplicate role in --set: {key!r}')
            choices[key] = model.strip()
        result = sync_models(args.host, choices, apply=args.apply, **paths)
    except (ConfigurationError, OSError, UnicodeError) as error:
        print(json.dumps(dict(status='error', error=str(error))))
        return 1
    print(json.dumps(result))
    return 0 if result['status'] == 'configured' else 2


if __name__ == '__main__':
    raise SystemExit(main())
