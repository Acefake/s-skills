"""Check global skill instructions; write only with an explicit --apply."""
import argparse
import json
import os
import re
import stat
import tempfile
from pathlib import Path

START = '<!-- s-atlas:instructions:start -->'
END = '<!-- s-atlas:instructions:end -->'


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
    return (f'{START}\n## s-atlas 全局技能规则\n'
            f'<!-- s-atlas:version: {plugin_version()} -->\n\n{load_template()}\n{END}')


def instruction_path(host, home, codex_home=None, claude_config_dir=None):
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
    templates = [short.group(1)]
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


def merge_instructions(text):
    block = managed_block().replace('\n', '\r\n' if '\r\n' in text else '\n')
    if START in text or END in text:
        if text.count(START) != 1 or text.count(END) != 1:
            raise ConfigurationError('Incomplete or duplicate s-atlas markers; repair them before applying')
        start, end = text.index(START), text.index(END)
        if (end < start or (start and text[start - 1] != '\n')
                or text[start + len(START):].split('\n', 1)[0].strip()
                or (end and text[end - 1] != '\n')
                or text[end + len(END):].split('\n', 1)[0].strip()):
            raise ConfigurationError('Invalid s-atlas marker boundaries')
        return text[:start] + block + text[end + len(END):]
    span = known_instruction_span(text)
    if span:
        start, end = span
        return text[:start] + block + text[end:]
    newline = '\r\n' if '\r\n' in text else '\n'
    separator = (newline if text.endswith(newline) else newline * 2) if text else ''
    return text + separator + block + newline


def write_preserving(path, original, updated):
    path.parent.mkdir(parents=True, exist_ok=True)
    if original is not None:
        backup = path.with_name(path.name + '.s-atlas.bak')
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
    status = 'configured' if not changed else ('outdated' if START in text or known_instruction_span(text) else 'missing')
    if apply and changed:
        write_preserving(path, original, updated)
        status = 'configured'
    return dict(status=status, changed=bool(apply and changed), target=str(path), version=plugin_version())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', required=True, choices=('codex', 'claude-code', 'cursor'))
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
