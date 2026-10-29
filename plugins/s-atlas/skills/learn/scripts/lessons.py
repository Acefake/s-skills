"""Read confirmed lessons; save only after the caller obtains specific approval."""
import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

FIELDS = {'scope', 'when', 'lesson', 'evidence', 'keywords', 'supersedes'}


def _text(value, field, maximum):
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ValueError(f'{field} must be nonempty text of at most {maximum} characters')
    return value.strip()


def _record(value, project):
    if not isinstance(value, dict) or set(value) - FIELDS:
        raise ValueError('Unknown lesson fields')
    scope = value.get('scope')
    if scope not in ('global', 'project'):
        raise ValueError('scope must be global or project')
    if scope == 'project' and not project:
        raise ValueError('Project lessons require the project root')
    keywords = value.get('keywords')
    if not isinstance(keywords, list) or not 1 <= len(keywords) <= 8:
        raise ValueError('keywords must contain 1 to 8 terms')
    note = dict(scope=scope, project=(os.path.normcase(str(Path(project).expanduser().resolve()))
                                    if scope == 'project' else None),
                when=_text(value.get('when'), 'when', 300),
                lesson=_text(value.get('lesson'), 'lesson', 1500),
                evidence=_text(value.get('evidence'), 'evidence', 500),
                keywords=sorted(set(_text(term, 'keyword', 50).casefold() for term in keywords)))
    supersedes = value.get('supersedes')
    if supersedes is not None and (not isinstance(supersedes, str) or not re.fullmatch('[a-f0-9]{64}', supersedes)):
        raise ValueError('supersedes must be a lesson ID')
    note['supersedes'] = supersedes
    identity = [note['scope'], note['project'],
                re.sub(r'\s+', '', note['when']).casefold(),
                re.sub(r'\s+', '', note['lesson']).casefold(), note['supersedes']]
    note['id'] = hashlib.sha256(json.dumps(identity, ensure_ascii=True).encode('ascii')).hexdigest()
    note['schema'] = 1
    return note


def _directory(home, scope, project):
    root = Path(home) / '.s-atlas/lessons'
    if scope == 'global':
        return root / 'global'
    key = hashlib.sha256(project.encode('utf-8')).hexdigest()
    return root / 'projects' / key


def _read(path, scope, project):
    if path.is_symlink():
        raise ValueError('Lesson files must not be symbolic links')
    value = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value, dict) or value.get('schema') != 1:
        raise ValueError('Unsupported lesson record')
    note = _record({key: value[key] for key in FIELDS if key in value}, value.get('project'))
    if (note['id'] != value.get('id') or path.stem != note['id']
            or note['scope'] != scope or note['project'] != project):
        raise ValueError('Lesson identity or scope does not match its storage location')
    return note


@contextmanager
def _replacement_guard(directory, note):
    if not note['supersedes']:
        yield
        return
    lock = directory / '.replace.lock'
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as error:
        raise ValueError('Another replacement is in progress; retry after it completes') from error
    os.close(fd)
    try:
        retired = {_read(path, note['scope'], note['project'])['supersedes']
                   for path in directory.glob('*.json')}
        if note['supersedes'] in retired:
            raise ValueError('This lesson was already replaced; review the current record before proposing another change')
        yield
    finally:
        lock.unlink()


def save(record, *, home, project=None, confirmed=False):
    """Publish one approved record atomically; retain prior records on replacement.

    confirmed attests that the caller received approval for this specific proposal;
    it is not independent evidence of human consent. Semantic deduplication and
    conflict review belong to the skill before this deterministic operation.
    """
    if not confirmed:
        raise ValueError('Obtain explicit approval for the specific lesson before saving')
    note = _record(record, project)
    directory = _directory(home, note['scope'], note['project'])
    if note['supersedes']:
        if note['supersedes'] == note['id']:
            raise ValueError('A lesson cannot replace itself')
        previous = directory / (note['supersedes'] + '.json')
        if not previous.is_file():
            raise ValueError('Replacement target does not exist in this scope')
        _read(previous, note['scope'], note['project'])
    path = directory / (note['id'] + '.json')
    if path.exists():
        _read(path, note['scope'], note['project'])
        if any(_read(other, note['scope'], note['project'])['supersedes'] == note['id']
               for other in directory.glob('*.json')):
            raise ValueError('This is a historical lesson; confirm replacement of the current record to restore it')
        return dict(id=note['id'], changed=False, path=str(path))
    directory.mkdir(parents=True, exist_ok=True)
    with _replacement_guard(directory, note):
        return _publish(directory, path, note)


def _publish(directory, path, note):
    fd, temporary = tempfile.mkstemp(suffix='.tmp', dir=directory)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(note, stream, ensure_ascii=True, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        try:
            # Linking a complete file is atomic and refuses to overwrite a racing writer.
            os.link(temporary, path)
            changed = True
        except FileExistsError:
            _read(path, note['scope'], note['project'])
            changed = False
    finally:
        os.unlink(temporary)
    return dict(id=note['id'], changed=changed, path=str(path))


def search(query, *, home, project=None, limit=3):
    """Return relevant active lessons from global and the current project only.

    No directories are created. Invalid stored records raise instead of being
    treated as trusted experience. Retired records remain on disk as history.
    """
    query = _text(query, 'query', 1000).casefold()
    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 5:
        raise ValueError('limit must be between 1 and 5')
    scopes = [('global', None)]
    if project:
        scopes.append(('project', os.path.normcase(str(Path(project).expanduser().resolve()))))
    notes = []
    for scope, root in scopes:
        directory = _directory(home, scope, root)
        for path in sorted(directory.glob('*.json')):
            notes.append(_read(path, scope, root))
    retired = {note['supersedes'] for note in notes if note['supersedes']}
    tokens = re.findall(r'[^\W_]+', query)
    matches = []
    for note in notes:
        if note['id'] in retired:
            continue
        content = (note['when'] + ' ' + note['lesson']).casefold()
        score = sum(3 for term in note['keywords'] if term in query)
        score += sum(1 for token in tokens if token in content)
        if score:
            matches.append((score, note['scope'] == 'project', note['id'], note))
    return [match[3] for match in sorted(matches, key=lambda item: item[:3], reverse=True)[:limit]]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', type=Path, default=Path.home())
    commands = parser.add_subparsers(dest='command', required=True)
    lookup = commands.add_parser('search')
    lookup.add_argument('--query', required=True)
    lookup.add_argument('--project', type=Path)
    lookup.add_argument('--limit', type=int, default=3)
    store = commands.add_parser('save')
    store.add_argument('--record', type=Path, required=True)
    store.add_argument('--project', type=Path)
    store.add_argument('--confirmed', action='store_true')
    args = parser.parse_args()
    try:
        if args.command == 'search':
            result = search(args.query, home=args.home, project=args.project, limit=args.limit)
        else:
            if not args.confirmed:
                raise ValueError('A specific lesson must be confirmed before saving')
            result = save(json.loads(args.record.read_text(encoding='utf-8-sig')), home=args.home,
                          project=args.project, confirmed=args.confirmed)
    except (ValueError, OSError, UnicodeError) as error:
        print(json.dumps(dict(status='error', error=str(error))))
        return 1
    print(json.dumps(result))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
