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


def load_template():
    source = Path(__file__).resolve().parents[3] / 'AGENTS-snippet.md'
    match = re.search(r'```text\s*\n(.*?)\n```', source.read_text(encoding='utf-8'), re.S)
    if not match:
        raise ConfigurationError('Canonical instruction block not found')
    return match.group(1).strip()


def managed_block():
    return f'{START}\n## s-atlas 全局技能规则\n\n{load_template()}\n{END}'


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
    # An existing canonical unmarked snippet already fulfils the contract.
    normalize = lambda value: re.sub(r'\s+', '', value)
    if normalize(load_template()) in normalize(text):
        return text
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
        return dict(status='user_rules_verification_required', changed=False, target='Cursor User Rules', block=managed_block())
    path = instruction_path(host, Path(home), codex_home, claude_config_dir)
    if path.is_symlink():
        raise ConfigurationError('Global instruction file is a symlink; inspect its destination before updating')
    original = path.read_bytes() if path.exists() else None
    text = original.decode('utf-8-sig') if original is not None else ''
    updated = merge_instructions(text).encode('utf-8')
    if original is not None and original.startswith(b'\xef\xbb\xbf'):
        updated = b'\xef\xbb\xbf' + updated
    changed = updated != original
    status = 'configured' if not changed else ('outdated' if START in text else 'missing')
    if apply and changed:
        write_preserving(path, original, updated)
        status = 'configured'
    return dict(status=status, changed=bool(apply and changed), target=str(path))


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
