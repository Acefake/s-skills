"""Check existing Codex wukong hooks; migrate owned command paths only with --apply."""
import argparse
import copy
import json
import os
import re
from pathlib import Path

from global_instructions import ConfigurationError, write_preserving

PLUGIN = Path(__file__).resolve().parents[3]
SCRIPTS = ('skills/prompt-sharpen/scripts/improve_hook.py', 'hooks/journal.py',
           'hooks/session_check.py', 'hooks/git_guard.py')
PYTHON = r'(?:python(?:3)?|py(?: -3)?)'
COMMAND = re.compile(r'^\s*' + PYTHON + r'\s+"([^"\r\n]+)"'
                     r'(?:\s*\|\|\s*' + PYTHON + r'\s+"([^"\r\n]+)")?\s*$')


def script_name(path):
    """Recognize shipped scripts beneath current or known previous plugin directory names."""
    normalized = path.replace('\\', '/')
    for relative in SCRIPTS:
        pattern = r'.+/(?:s-atlas|s-wukong|wukong)(?:/\d+\.\d+\.\d+)?/' + re.escape(relative)
        if re.fullmatch(pattern, normalized):
            return relative
    return None


def migrate_command(command):
    """Return (replacement, script, ambiguous); do not rewrite custom shell commands."""
    if not isinstance(command, str):
        return command, None, False
    mentioned = [script_name(path) for path in re.findall(r'"([^"\r\n]+)"', command)]
    mentioned = [name for name in mentioned if name]
    if not mentioned:
        normalized = command.replace('\\', '/')
        unquoted = any('/' + name + '/' + relative in normalized
                       for name in ('s-atlas', 's-wukong', 'wukong') for relative in SCRIPTS)
        return command, None, unquoted
    match = COMMAND.fullmatch(command)
    if not match:
        return command, None, True
    paths = [path for path in match.groups() if path is not None]
    names = [script_name(path) for path in paths]
    if not all(names) or len(set(names)) != 1:
        return command, None, True
    replacement = command
    for path in paths:
        replacement = replacement.replace('"' + path + '"', '"' + (PLUGIN / names[0]).as_posix() + '"')
    return replacement, names[0], False


def inspect_hooks(value):
    """Build a migration preview, preserving unrelated events, commands and metadata."""
    if not isinstance(value, dict) or not isinstance(value.get('hooks', {}), dict):
        raise ConfigurationError('Expected a JSON object with a hooks object')
    updated = copy.deepcopy(value)
    changes, manual = [], []
    prompt_recording = False
    for event, groups in updated.get('hooks', {}).items():
        if not isinstance(groups, list):
            raise ConfigurationError('Hook event entries must be arrays')
        for group_index, group in enumerate(groups):
            if not isinstance(group, dict) or not isinstance(group.get('hooks', []), list):
                raise ConfigurationError('Expected hook groups containing a hooks array')
            for index, hook in enumerate(group.get('hooks', [])):
                if not isinstance(hook, dict) or hook.get('type') != 'command':
                    continue
                for field in ('command', 'commandWindows'):
                    before = hook.get(field)
                    after, script, ambiguous = migrate_command(before)
                    location = '%s:%d:%d:%s' % (event, group_index, index, field)
                    if ambiguous:
                        manual.append(location)
                    if event == 'UserPromptSubmit' and script in (SCRIPTS[0], 'hooks/journal.py'):
                        prompt_recording = True
                    if before != after:
                        hook[field] = after
                        changes.append(dict(location=location, script=script, target=str(PLUGIN / script)))
    status = ('manual_review' if manual else 'outdated' if changes
              else 'configured' if prompt_recording else 'missing')
    return updated, dict(status=status, changes=changes, manual_review=manual,
                         prompt_recording=prompt_recording)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ConfigurationError('Duplicate JSON key: ' + key)
        result[key] = value
    return result


def sync_hooks(home, codex_home=None, apply=False):
    """Check without writes; explicit migration keeps a backup and rejects unsafe files."""
    directory = Path(codex_home).expanduser() if codex_home else Path(home) / '.codex'
    path = directory / 'hooks.json'
    if path.is_symlink():
        raise ConfigurationError('Hooks file is a symlink; inspect its destination before updating')
    result = dict(status='missing', target=str(path), changed=False)
    if not path.exists():
        return result
    original = path.read_bytes()
    value = json.loads(original.decode('utf-8-sig'), object_pairs_hook=unique_object)
    updated, preview = inspect_hooks(value)
    result.update(preview)
    if not apply or preview['status'] != 'outdated':
        return result
    for change in preview['changes']:
        if not Path(change['target']).is_file():
            raise ConfigurationError('Replacement script is missing: ' + change['target'])
    text = json.dumps(updated, ensure_ascii=False, indent=2) + '\n'
    if b'\r\n' in original:
        text = text.replace('\n', '\r\n')
    encoded = text.encode('utf-8')
    if original.startswith(b'\xef\xbb\xbf'):
        encoded = b'\xef\xbb\xbf' + encoded
    write_preserving(path, original, encoded)
    result.update(status='configured' if preview['prompt_recording'] else 'missing', changed=True,
                  backup=str(path.with_name(path.name + '.wukong.bak')), approval_required=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', type=Path, default=Path.home())
    parser.add_argument('--codex-home', type=Path, default=os.environ.get('CODEX_HOME') or None)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    try:
        result = sync_hooks(args.home, args.codex_home, args.apply)
    except (ConfigurationError, OSError, UnicodeError, ValueError) as error:
        print(json.dumps(dict(status='error', changed=False, error=str(error))))
        return 1
    print(json.dumps(result))
    return 0 if result['status'] == 'configured' else 2


if __name__ == '__main__':
    raise SystemExit(main())
