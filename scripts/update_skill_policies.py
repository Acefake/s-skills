"""Synchronize Codex invocation metadata without rewriting skill instructions."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def main():
    automatic = 0
    for path in (ROOT / 'plugins/s-atlas/skills').glob('*/SKILL.md'):
        text = path.read_text(encoding='utf-8')
        end = text.index('\n---', 3)
        implicit = not bool(re.search(r'^disable-model-invocation:\s*true\s*$', text[3:end], re.M))
        if implicit:
            automatic += 1
        policy = path.parent / 'agents/openai.yaml'
        policy.parent.mkdir(exist_ok=True)
        setting = '  allow_implicit_invocation: ' + str(implicit).lower()
        metadata = policy.read_text(encoding='utf-8') if policy.exists() else ''
        if re.search(r'^  allow_implicit_invocation:.*$', metadata, re.M):
            metadata = re.sub(r'^  allow_implicit_invocation:.*$', setting, metadata, flags=re.M)
        elif re.search(r'^policy:[ \t]*$', metadata, re.M):
            metadata = re.sub(r'^policy:[ \t]*$', 'policy:\n' + setting, metadata, count=1, flags=re.M)
        else:
            metadata = metadata.rstrip() + '\npolicy:\n' + setting + '\n'
        policy.write_text(metadata.lstrip('\n'), encoding='utf-8')
    print(f'Automatic skills: {automatic}')


if __name__ == '__main__':
    main()
