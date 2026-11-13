"""Check global skill instructions; write only with an explicit --apply."""
import argparse
import json
import os
import re
import stat
import tempfile
from pathlib import Path

START = '<!-- wukong:instructions:start -->'
END = '<!-- wukong:instructions:end -->'
# 1.0.6 及更早写进用户配置的标记。读到时整段换成上面的新标记。
LEGACY_START = '<!-- s-atlas:instructions:start -->'
LEGACY_END = '<!-- s-atlas:instructions:end -->'
PREVIOUS_START = '<!-- s-wukong:instructions:start -->'
PREVIOUS_END = '<!-- s-wukong:instructions:end -->'
# 个人学习层写的块。和上面的库块分开：库升级不碰它，写它也不碰库块。
PERSONAL_START = '<!-- wukong:personal:start -->'
PERSONAL_END = '<!-- wukong:personal:end -->'


class ConfigurationError(Exception):
    """Existing configuration cannot safely be updated."""


def plugin_version():
    source = Path(__file__).resolve().parents[3] / 'plugin.json'
    return json.loads(source.read_text(encoding='utf-8'))['version']


def load_template():
    source = Path(__file__).resolve().parents[3] / 'AGENTS.md'
    introduction = '收到任务后，在读文件、跑命令、提问或作答之前：'
    _, found, body = source.read_text(encoding='utf-8').partition(introduction)
    if not found:
        raise ConfigurationError('Canonical full instruction body not found')
    return (introduction + body).strip()


def managed_block():
    return (f'{START}\n## wukong 全局技能规则\n'
            f'<!-- wukong:version: {plugin_version()} -->\n\n{load_template()}\n{END}')


def instruction_path(host, home, codex_home=None, claude_config_dir=None):
    if host == 'workbuddy':
        return home / '.codebuddy' / 'CODEBUDDY.md'
    if host == 'claude-code':
        directory = Path(claude_config_dir).expanduser() if claude_config_dir is not None else home / '.claude'
        return directory / 'CLAUDE.md'
    if host == 'codex':
        directory = Path(codex_home).expanduser() if codex_home is not None else home / '.codex'
        override = directory / 'AGENTS.override.md'
        if override.exists() and override.read_bytes().decode('utf-8-sig').strip():
            return override
        return directory / 'AGENTS.md'
    raise ValueError(f'Unsupported host: {host}')


def known_instruction_span(text):
    """Locate an intact known unmarked template without consuming user text."""
    source = Path(__file__).resolve().parents[3] / 'AGENTS-snippet.md'
    short = re.search(r'```text\s*\n(.*?)\n```', source.read_text(encoding='utf-8'), re.S)
    if not short:
        raise ConfigurationError('Legacy short instruction block not found')
    references = Path(__file__).resolve().parents[1] / 'references'
    previous = [path.read_text(encoding='utf-8')
                for path in sorted(references.glob('full-instructions-v*.txt'))]
    templates = [short.group(1), *(path.read_text(encoding='utf-8')
                 for path in sorted(references.glob('short-instructions-v*.txt')))]
    for full in [load_template(), *previous]:
        templates.extend((full, '\n'.join(line for line in full.splitlines()
                         if not (line.startswith('|') and any(
                             f'`{skill}`' in line for skill in ('patent-disclosure', 'patent-application'))))))
    # Retain offsets so whitespace and backtick normalization never changes surrounding content.
    offsets = [i for i, char in enumerate(text) if not char.isspace() and char != '`']
    candidate = ''.join(text[i] for i in offsets)
    spans = set()
    for template in templates:
        normalized = re.sub(r'[\s`]+', '', template)
        at = candidate.find(normalized)
        while at != -1:
            start, end = offsets[at], offsets[at + len(normalized) - 1] + 1
            before = text[text.rfind('\n', 0, start) + 1:start]
            after = text[end:].split('\n', 1)[0]
            if not before.strip() and not after.strip():
                spans.add((start, end))
            at = candidate.find(normalized, at + 1)
    # An older template may be an intact prefix of a newer one. Migrate the full block.
    spans = {span for span in spans if not any(
        other != span and other[0] <= span[0] and span[1] <= other[1] for other in spans)}
    if len(spans) > 1:
        raise ConfigurationError('Multiple unmarked instruction blocks; reconcile them before applying')
    return next(iter(spans), None)


def owned_markers(text):
    """Return one intact marker pair, including earlier plugin names."""
    pairs = ((START, END), (PREVIOUS_START, PREVIOUS_END), (LEGACY_START, LEGACY_END))
    present = [pair for pair in pairs if pair[0] in text or pair[1] in text]
    if len(present) > 1:
        raise ConfigurationError('Mixed plugin instruction markers; repair them before applying')
    if not present:
        return None
    start, end = present[0]
    if text.count(start) != 1 or text.count(end) != 1:
        raise ConfigurationError('Incomplete or duplicate instruction markers; repair them before applying')
    return start, end


def merge_instructions(text):
    block = managed_block().replace('\n', '\r\n' if '\r\n' in text else '\n')
    markers = owned_markers(text)
    if markers:
        start, end = markers
        start_at, end_at = text.index(start), text.index(end)
        if (end_at < start_at or (start_at and text[start_at - 1] != '\n')
                or text[start_at + len(start):].split('\n', 1)[0].strip()
                or (end_at and text[end_at - 1] != '\n')
                or text[end_at + len(end):].split('\n', 1)[0].strip()):
            raise ConfigurationError('Invalid instruction marker boundaries')
        return text[:start_at] + block + text[end_at + len(end):]
    span = known_instruction_span(text)
    if span:
        start, end = span
        return text[:start] + block + text[end:]
    newline = '\r\n' if '\r\n' in text else '\n'
    separator = (newline if text.endswith(newline) else newline * 2) if text else ''
    return text + separator + block + newline


def _marker_span(text, start, end):
    """Return (start_at, end_after) of one well-formed marker pair, or None."""
    if start not in text and end not in text:
        return None
    if text.count(start) != 1 or text.count(end) != 1:
        raise ConfigurationError('Incomplete or duplicate personal markers; repair them before applying')
    start_at, end_at = text.index(start), text.index(end)
    if (end_at < start_at or (start_at and text[start_at - 1] != '\n')
            or text[end_at + len(end):].split('\n', 1)[0].strip()):
        raise ConfigurationError('Invalid personal marker boundaries')
    return start_at, end_at + len(end)


def merge_personal(text, body):
    """Replace, insert or (for an empty body) remove the personal block only."""
    newline = '\r\n' if '\r\n' in text else '\n'
    span = _marker_span(text, PERSONAL_START, PERSONAL_END)
    body = body.strip()
    if not body:
        if not span:
            return text
        start_at, end_after = span
        tail = text[end_after:]
        if tail.startswith(newline):
            tail = tail[len(newline):]
        head = text[:start_at]
        if head.endswith(newline * 2):
            head = head[:-len(newline)]
        return head + tail
    block = f'{PERSONAL_START}\n{body}\n{PERSONAL_END}'.replace('\n', newline)
    if span:
        start_at, end_after = span
        return text[:start_at] + block + text[end_after:]
    library_end = next((marker for marker in (END, PREVIOUS_END, LEGACY_END) if marker in text), None)
    if library_end:
        at = text.index(library_end) + len(library_end)
        return text[:at] + newline * 2 + block + text[at:]
    separator = (newline if text.endswith(newline) else newline * 2) if text else ''
    return text + separator + block + newline


def write_preserving(path, original, updated):
    path.parent.mkdir(parents=True, exist_ok=True)
    if original is not None:
        backup = path.with_name(path.name + '.wukong.bak')
        try:
            with backup.open('xb') as stream:
                stream.write(original)
        except FileExistsError:
            pass
    mode = stat.S_IMODE(path.stat().st_mode) if original is not None else None
    fd, temporary = tempfile.mkstemp(prefix=path.name + '.', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(updated)
        if mode is not None:
            os.chmod(temporary, mode)
        current = path.read_bytes() if path.exists() else None
        if current != original:
            raise ConfigurationError('Configuration changed during initialization; rerun the check')
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def sync_global(host, *, home, codex_home=None, claude_config_dir=None, apply=False):
    if host == 'cursor':
        return dict(status='user_rules_verification_required', changed=False, target='Cursor User Rules', version=plugin_version(), block=managed_block())
    path = instruction_path(host, Path(home), codex_home, claude_config_dir)
    if path.is_symlink():
        raise ConfigurationError('Global instruction file is a symlink; inspect its destination before updating')
    original = path.read_bytes() if path.exists() else None
    text = original.decode('utf-8-sig') if original is not None else ''
    updated = merge_instructions(text).encode('utf-8')
    if original is not None and original.startswith(b'\xef\xbb\xbf'):
        updated = b'\xef\xbb\xbf' + updated
    changed = updated != original
    status = 'configured' if not changed else ('outdated' if any(marker in text for marker in (START, PREVIOUS_START, LEGACY_START)) or known_instruction_span(text) else 'missing')
    if apply and changed:
        write_preserving(path, original, updated)
        status = 'configured'
    return dict(status=status, changed=bool(apply and changed), target=str(path), version=plugin_version())


def sync_personal(host, body, *, home, codex_home=None, claude_config_dir=None, apply=False):
    """Write the personal block; an empty body removes it. Cursor gets the block to paste."""
    if host == 'cursor':
        block = f'{PERSONAL_START}\n{body.strip()}\n{PERSONAL_END}' if body.strip() else ''
        return dict(status='user_rules_verification_required', changed=False, target='Cursor User Rules', block=block)
    path = instruction_path(host, Path(home), codex_home, claude_config_dir)
    if path.is_symlink():
        raise ConfigurationError('Global instruction file is a symlink; inspect its destination before updating')
    original = path.read_bytes() if path.exists() else None
    text = original.decode('utf-8-sig') if original is not None else ''
    updated = merge_personal(text, body).encode('utf-8')
    if original is not None and original.startswith(b'\xef\xbb\xbf'):
        updated = b'\xef\xbb\xbf' + updated
    changed = updated != (original or b'')
    if apply and changed:
        write_preserving(path, original, updated)
    return dict(status='configured' if apply or not changed else 'outdated', changed=bool(apply and changed), target=str(path))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', required=True, choices=('codex', 'claude-code', 'cursor', 'workbuddy'))
    parser.add_argument('--apply', action='store_true', help='Explicitly initialize or update the owned block')
    parser.add_argument('--home', type=Path, default=Path.home())
    parser.add_argument('--codex-home', type=Path, default=os.environ.get('CODEX_HOME') or None)
    parser.add_argument('--claude-config-dir', type=Path, default=os.environ.get('CLAUDE_CONFIG_DIR') or None)
    args = parser.parse_args()
    try:
        result = sync_global(args.host, home=args.home, codex_home=args.codex_home,
                             claude_config_dir=args.claude_config_dir, apply=args.apply)
    except (ConfigurationError, OSError, UnicodeError) as error:
        print(json.dumps(dict(status='error', error=str(error))))
        return 1
    print(json.dumps(result))
    return 0 if result['status'] == 'configured' else (3 if args.host == 'cursor' else 2)


if __name__ == '__main__':
    raise SystemExit(main())
