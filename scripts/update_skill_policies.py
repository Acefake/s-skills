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
        implicit = implicit or path.parent.name.startswith('原则-') or path.parent.name in (
            'TypeScript最佳实践', '设置s模型'
        )
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
        if path.parent.name == 's使用帮助':
            text = re.sub(r'\[([^\]]+)\]\(../../docs/guide/[^)]+\)', r'\1（见[使用入口](../../HOSTS.md)）', text)
            text = text.replace('](../../README.md)', '](../../HOSTS.md)')
            text = text.replace('只有 `/设置s模型` 会根据用户的话自动加载。', '`/设置s模型`、TypeScript 最佳实践和原则类技能允许根据任务自动加载。')
            text = text.replace('其他的在用户输入它们、或者 `/poteto工作模式` 运行它们时才加载', '其余工作流在用户点名、或者 `/poteto工作模式` 运行它们时才加载')
        path.write_text(text, encoding='utf-8')
    print(f'Automatic skills: {automatic}')


if __name__ == '__main__':
    main()
