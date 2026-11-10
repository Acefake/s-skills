"""T3 用户级模型规则的宿主路径；不改写宿主原生模型设置或凭据。"""
import os
from pathlib import Path

HOSTS = ('codex', 'claude-code', 'cursor', 'workbuddy', 'dsh', 'hermes')
DIRECTORIES = {'codex': ('CODEX_HOME', '.codex'),
               'claude-code': ('CLAUDE_CONFIG_DIR', '.claude'),
               'cursor': (None, '.cursor'), 'workbuddy': (None, '.codebuddy'), 'dsh': ('DSH_HOME', '.dsh'),
               'hermes': ('HERMES_HOME', '.hermes')}


def global_root(host: str, override: Path | None = None) -> Path:
    """显式宿主及环境变量优先；不靠父提供商推断底层宿主。"""
    if host not in DIRECTORIES:
        raise ValueError('读取或写入全局默认必须用 --host 明确当前底层宿主')
    variable, directory = DIRECTORIES[host]
    selected = override or (os.environ.get(variable) if variable else None)
    return (Path(selected).expanduser() if selected else Path.home() / directory).resolve()


def rule_paths(root: Path, host: str | None = None) -> tuple[Path, ...]:
    """返回宿主允许的模型规则路径，供写入与事务恢复使用同一白名单。"""
    names = {'codex': ('AGENTS.md', 'AGENTS.override.md'),
             'claude-code': ('rules/s-models.md',), 'cursor': ('rules/s-models.mdc',),
             'workbuddy': ('rules/s-models.md',), 'dsh': ('AGENTS.md',),
             'hermes': ('SOUL.md',), None: ('AGENTS.md',)}
    return tuple(root / name for name in names[host])


def global_rules(root: Path, host: str) -> Path:
    """Codex 非空 override 优先；其他宿主按自己的规则文件读取。"""
    paths = rule_paths(root, host)
    if host == 'codex' and paths[1].exists() and paths[1].read_text(encoding='utf-8-sig').strip():
        return paths[1]
    return paths[0]


def project_rules(root: Path, host: str | None) -> Path:
    """Codex 项目与用户级遵从相同的非空 override 优先级。"""
    override = root / 'AGENTS.override.md'
    if host is None and override.exists() and override.read_text(encoding='utf-8-sig').strip():
        raise ValueError('项目存在非空 AGENTS.override.md，必须用 --host 明确宿主后再读写或恢复')
    return global_rules(root, 'codex') if host == 'codex' else root / 'AGENTS.md'
