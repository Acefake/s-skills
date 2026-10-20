"""Apply the repository's invocation policy and host entry point."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def main():
    automatic = 0
    for path in (ROOT / 'plugins/s/skills').glob('*/SKILL.md'):
        text = path.read_text(encoding='utf-8')
        end = text.index('\n---', 3)
        implicit = not bool(re.search(r'^disable-model-invocation:\s*true\s*$', text[3:end], re.M))
        implicit = implicit or path.parent.name.startswith('principle-') or path.parent.name == 'setup-s-models'
        if implicit:
            text = text.replace('disable-model-invocation: true', 'disable-model-invocation: false')
            text = text.replace(
                '`disable-model-invocation: false` 表示这个 skill 只能由用户主动调用，AI 不会自己调用它。',
                '本技能允许按描述匹配任务并自动加载，也可以主动点名调用。'
            )
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
        marker = '\n## 运行环境适配\n\n在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。\n'
        if marker not in text:
            end = text.index('\n---', 3) + 4
            text = text[:end] + marker + text[end:]
        path.write_text(text, encoding='utf-8')
    print(f'Automatic skills: {automatic}')


if __name__ == '__main__':
    main()
