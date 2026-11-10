"""校验 T3 目标、解析全局默认及项目覆盖；不调用 T3 或授予运行权限。"""
from __future__ import annotations

import argparse
import base64
import difflib
import json
import os
import re
import stat
import sys
import tempfile
from pathlib import Path

import s_models
import t3_hosts

TARGET_FILE = 'wukong.t3.json'
JOURNAL = '.wukong-t3.transaction.json'
LEGACY_TARGET_FILE = 's-atlas.t3.json'
LEGACY_JOURNAL = '.s-atlas-t3.transaction.json'
PREVIOUS_TARGET_FILE = 's-wukong.t3.json'
PREVIOUS_JOURNAL = '.s-wukong-t3.transaction.json'
ALIAS = re.compile(r'^[A-Za-z0-9_-]+$')
EFFORT_KEYS = ('reasoningEffort', 'reasoning_effort', 'effort')
ROLE_GROUPS = s_models.ROLE_GROUPS
SIX_ROLES = s_models.ROLE_KEYS
LEGACY_ROLE = s_models.LEGACY_ROLE


class ConfigError(ValueError):
    """配置或能力不满足派发条件。"""


def existing_or_current(project: Path, current: str, legacy: str) -> Path:
    """新文件名优先；只有旧文件时继续读旧文件。"""
    previous = {TARGET_FILE: PREVIOUS_TARGET_FILE, JOURNAL: PREVIOUS_JOURNAL}.get(current)
    for name in (current, previous, legacy):
        if name is not None and ((project / name).exists() or (project / name).is_symlink()):
            return project / name
    return project / current


def load_json(path: Path) -> dict:
    """读取 JSON 对象；格式错误由 CLI 边界报告。"""
    value = json.loads(path.read_text(encoding='utf-8-sig'), object_pairs_hook=unique_keys)
    if not isinstance(value, dict):
        raise ConfigError(f'{path} 必须是 JSON 对象')
    return value


def unique_keys(pairs: list) -> dict:
    """拒绝重复键，避免预览与实际解析选中不同目标。"""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ConfigError(f'JSON 重复键: {key}')
        result[key] = value
    return result


def validate_targets(config: dict) -> dict:
    """严格校验目标结构，拒绝权限字段和非字符串/布尔参数。"""
    if set(config) != {'schemaVersion', 'targets'} or type(config['schemaVersion']) is not int or config['schemaVersion'] != 1:
        raise ConfigError('目标配置必须是 schemaVersion: 1 和 targets')
    targets = config['targets']
    if not isinstance(targets, dict):
        raise ConfigError('targets 必须是对象')
    for alias, target in targets.items():
        if not ALIAS.fullmatch(alias) or not isinstance(target, dict):
            raise ConfigError(f'非法目标别名或内容: {alias}')
        if set(target) - {'providerInstanceId', 'model', 'options'}:
            raise ConfigError(f'{alias} 包含未知字段')
        for key in ('providerInstanceId', 'model'):
            if not isinstance(target.get(key), str) or not target[key].strip():
                raise ConfigError(f'{alias}.{key} 必须是非空字符串')
        options = target.get('options', {})
        if not isinstance(options, dict) or any(not key or type(value) not in (str, bool) for key, value in options.items()):
            raise ConfigError(f'{alias}.options 仅接受字符串键及字符串/布尔值')
    return targets


def capability_catalog(data: dict) -> dict:
    """接受能力对象或 MCP structuredContent 包装，不把截断目录当成全目录。"""
    value = data.get('structuredContent', data)
    if not isinstance(value, dict) or not isinstance(value.get('providers'), list):
        raise ConfigError('能力快照缺少 providers；请保存 orchestrator_capabilities 的结构化结果')
    for provider in value['providers']:
        validate_provider(provider)
    inherited = value.get('inheritedOptions') or []
    if not isinstance(inherited, list) or any(
        not isinstance(item, dict) or not isinstance(item.get('id'), str)
        or type(item.get('value')) not in (str, bool) for item in inherited
    ):
        raise ConfigError('能力快照 inheritedOptions 格式错误')
    return value


def validate_provider(provider: dict) -> None:
    """验证解析器读取的能力字段；容许工具增加其他字段。"""
    if not isinstance(provider, dict) or not isinstance(provider.get('providerInstanceId'), str):
        raise ConfigError('能力快照提供商字段错误')
    models = provider.get('models', [])
    if not isinstance(models, list):
        raise ConfigError('能力快照 models 必须是列表')
    for model in models:
        if not isinstance(model, dict) or not isinstance(model.get('id'), str):
            raise ConfigError('能力快照模型 ID 错误')
        options = model.get('options', [])
        if not isinstance(options, list):
            raise ConfigError('能力快照模型 options 必须是列表')
        for option in options:
            if (not isinstance(option, dict) or not isinstance(option.get('id'), str)
                    or not isinstance(option.get('values'), list)):
                raise ConfigError('能力快照模型参数定义错误')


def model_capability(caps: dict, provider_id: str, model_id: str) -> dict:
    """精确查找可运行目标；缺少模型时提示重新搜索。"""
    provider = next((p for p in caps['providers'] if p.get('providerInstanceId') == provider_id), None)
    if provider is None or provider.get('canRunChildTask') is not True:
        raise ConfigError(f'提供商 {provider_id} 不可运行子任务')
    if provider_id != caps.get('inheritedProviderInstanceId') and provider.get('canRunCrossProviderChildTask') is not True:
        raise ConfigError(f'提供商 {provider_id} 不支持跨提供商委派')
    model = next((m for m in provider.get('models', []) if m.get('id') == model_id), None)
    if model is None:
        raise ConfigError(f'{provider_id} 未列出模型 {model_id!r}；目录可能截断，请用 search 重新发现，不自动换模型')
    return model


def validate_options(model: dict, options: dict) -> None:
    """按模型能力定义逐项校验，避免 Python 将 1 当成 True。"""
    definitions = {item['id']: item['values'] for item in model.get('options', [])}
    for key, value in options.items():
        allowed = definitions.get(key, [])
        if not any(type(value) is type(candidate) and value == candidate for candidate in allowed):
            raise ConfigError(f'模型 {model["id"]} 参数 {key}={value!r} 非法；合法选项: {allowed}')


def role_config(text: str) -> dict:
    """复用全宿主六角色校验；T3 新配置另外要求完整六行。"""
    lines = text.splitlines()
    span = s_models.find_block(lines)
    if span is None:
        raise ConfigError('没有 s 模型配置段')
    body = lines[span[0] + 1:span[1]]
    keys = [line.partition(':')[0].strip() for line in body
            if line.strip() and not line.lstrip().startswith('#')]
    if any(key in SIX_ROLES for key in keys):
        if len(keys) != len(SIX_ROLES) or set(keys) != set(SIX_ROLES):
            raise ConfigError('六角色配置存在缺失、未知、重复或混合旧角色')
    try:
        checked = s_models.check_text(text)
    except s_models.SModelsError as exc:
        raise ConfigError(str(exc)) from exc
    if checked['status'] != 'ok':
        raise ConfigError('; '.join(checked['problems']))
    return checked


def render_block(budget: str, rows: dict) -> str:
    """生成完整六角色标记段，拒绝依赖父提供商猜测缺失角色。"""
    if set(rows) != set(SIX_ROLES):
        raise ConfigError('必须明确指定完整六角色')
    header = (s_models.START, '# 六角色必须完整；inherit-parent 或 auto 可继承父会话。',
              '# 逗号分隔的列表，每一项派一个子代理。')
    text = '\n'.join([*header, s_models.budget_line(s_models.normalize_budget(budget)),
                      *(f'{key}: {rows[key]}' for key in SIX_ROLES), s_models.END])
    checked = role_config(text)
    if checked['status'] != 'ok':
        raise ConfigError('; '.join(checked['problems']))
    return text + '\n'


def role_items(text: str, role: str) -> tuple[str, list, str]:
    """复用旧格式的结构校验，保留显式档位与预算档位的区别。"""
    lines = text.splitlines()
    span = s_models.find_block(lines)
    body = lines[span[0] + 1:span[1]] if span else []
    old = s_models.LEGACY_ENGLISH.get(role, role)
    exact = [line for line in body if line.partition(':')[0].strip() == old]
    if not exact and old in LEGACY_ROLE:
        exact = [line for line in body if s_models.LEGACY_ENGLISH.get(line.partition(':')[0].strip()) == old]
    canonical = s_models.OLD_TO_NEW.get(role, role)
    has_current = any(line.partition(':')[0].strip() == canonical for line in body)
    if exact and old in LEGACY_ROLE and not has_current:
        budget = [line for line in body if line.lstrip().startswith('#')]
        value = exact[-1].partition(':')[2].strip()
        validation_key = '独立评审' if old == '审问审查者' else '开发实现'
        checked = s_models.check_text('\n'.join([s_models.START, *budget, f'{validation_key}: {value}', s_models.END]))
        checked['rows'] = {canonical: value}
    else:
        checked = role_config(text)
    if checked['status'] != 'ok':
        raise ConfigError('; '.join(checked['problems']))
    key = s_models.OLD_TO_NEW.get(role, role)
    rows = checked['rows']
    if key not in rows:
        raise ConfigError(f'配置里没有角色 {role}，使用技能默认前需明确目标')
    default = checked['effort'] or 'xhigh'
    if key in (s_models.LIGHT_ROLE, '检索与探索'):
        default = s_models.EFFORTS[min(s_models.EFFORTS.index(default), 1)]
    return key, [s_models.split_item(item) for item in rows[key].split(',')], default


def effective_options(target: dict, model: dict, level: str | None, default: str) -> dict:
    """角色显式档位不与目标重复；仅在能力声明时映射预算。"""
    options = dict(target.get('options', {}))
    effort_keys = [key for key in EFFORT_KEYS if key in options]
    if len(effort_keys) > 1 or (level is not None and effort_keys):
        raise ConfigError('角色档位与目标 options 的推理设置冲突，只保留一处')
    if not effort_keys:
        definitions = [item['id'] for item in model.get('options', []) if item['id'] in EFFORT_KEYS]
        if len(definitions) > 1:
            raise ConfigError('模型有多个推理参数，请在目标 options 中明确选择')
        if definitions:
            options[definitions[0]] = level or default
        elif level:
            raise ConfigError('模型没有声明推理档位参数，不能应用显式档位')
    validate_options(model, options)
    return options


def resolve_item(name: str, level: str | None, default: str, targets: dict,
                 caps: dict, native_models: list, force: bool) -> dict:
    if name in s_models.FREE_VALUES:
        provider_id, model_id = caps.get('inheritedProviderInstanceId'), caps.get('inheritedModel')
        if not provider_id or not model_id:
            raise ConfigError('能力快照没有父提供商或模型，不能确认继承目标')
        model = model_capability(caps, provider_id, model_id)
        options = effective_options({}, model, level, default) if level else None
        if options is not None:
            options = {**parent_options(caps), **options}
            validate_options(model, options)
        target = {'options': options} if options is not None else {}
        native = model_id in native_models and level is None
    else:
        alias = name[3:] if name.startswith('t3:') else None
        if alias is not None and alias not in targets:
            raise ConfigError(f'目标别名不存在: {name}')
        source = targets[alias] if alias is not None else {
            'providerInstanceId': caps.get('inheritedProviderInstanceId'), 'model': name}
        provider_id, model_id = source['providerInstanceId'], source['model']
        model = model_capability(caps, provider_id, model_id)
        options = effective_options(source, model, level, default)
        if ('options' not in source and provider_id == caps.get('inheritedProviderInstanceId')
                and model_id == caps.get('inheritedModel')):
            options = {**parent_options(caps), **options}
            validate_options(model, options)
        target = {'providerInstanceId': provider_id, 'model': model_id, 'options': options}
        native = (provider_id == caps.get('inheritedProviderInstanceId') and model_id in native_models
                  and 'options' not in source and all(parent_options(caps).get(k) == v for k, v in options.items()))
    return {'executor': 'native' if native and not force else 'delegate_task', 'target': target}


def parent_options(caps: dict) -> dict:
    """能力快照已校验的父参数。"""
    return {item['id']: item['value'] for item in caps.get('inheritedOptions', []) or []}


def resolve(text: str, role: str, config: dict, capabilities: dict,
            native_models: list | None = None, worktree: bool = False, delegate: bool = False) -> dict:
    """返回版本化解析结果；native_models 必须来自原生工具定义。"""
    targets = validate_targets(config)
    caps = capability_catalog(capabilities)
    key, items, default = role_items(text, role)
    resolved = [resolve_item(name, level, default, targets, caps, native_models or [], worktree or delegate)
                for name, level in items]
    return {'schemaVersion': 1, 'role': key, 'isolation': 'worktree' if worktree else 'shared', 'items': resolved}


def complete_role_config(text: str) -> dict:
    """T3 文件级校验要求旧键映射后仍覆盖全部六角色。"""
    checked = role_config(text)
    if set(checked['rows']) != set(SIX_ROLES):
        raise ConfigError('T3 配置检查要求完整六角色，旧配置也必须能映射全部六角色')
    return checked


def check(text: str, config: dict, capabilities: dict) -> dict:
    """校验全部已配置角色和未被引用的目标；不启动实际任务。"""
    targets = validate_targets(config)
    caps = capability_catalog(capabilities)
    for target in targets.values():
        model = model_capability(caps, target['providerInstanceId'], target['model'])
        validate_options(model, target.get('options', {}))
    checked = complete_role_config(text)
    for role in checked['rows']:
        resolve(text, role, config, caps)
    return {'schemaVersion': 1, 'status': 'ok', 'validation': 'capability-snapshot-only', 'notes': checked['notes']}


def atomic_write(path: Path, data: bytes) -> None:
    """同目录替换并保留原文件模式，写入内容先 fsync。"""
    fd, temporary = tempfile.mkstemp(prefix=path.name + '.', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        if path.exists():
            os.chmod(temporary, stat.S_IMODE(path.stat().st_mode))
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def snapshot(path: Path) -> bytes | None:
    return path.read_bytes() if path.exists() else None


def encode(data: bytes | None) -> str | None:
    return base64.b64encode(data).decode('ascii') if data is not None else None


def recover(project: Path, host: str | None = None) -> dict:
    """先检查全部前像，逐项恢复并回读；冲突时保留事务记录。"""
    journal = existing_or_current(project, JOURNAL, LEGACY_JOURNAL)
    if not journal.exists():
        return {'status': 'no-pending-transaction'}
    entries = recovery_entries(project, load_json(journal), host)
    restored = []
    for entry in entries:
        path = Path(entry['path'])
        old = base64.b64decode(entry['before']) if entry['before'] is not None else None
        new = base64.b64decode(entry['after'])
        current = snapshot(path)
        if current not in (old, new):
            raise ConfigError(f'{path} 存在外部修改，保留事务记录，请人工核对')
        restored.append((path, old, current))
    for path, old, expected in restored:
        if snapshot(path) != expected:
            raise ConfigError(f'{path} 存在外部修改，保留事务记录，请人工核对')
        if old is None:
            path.unlink(missing_ok=True)
        else:
            atomic_write(path, old)
    if any(snapshot(path) != old for path, old, _ in restored):
        raise ConfigError('恢复后回读不一致，保留事务记录，请人工核对')
    journal.unlink()
    return {'status': 'recovered'}


def recovery_entries(project: Path, data: dict, host: str | None = None) -> list:
    """恢复记录只能操作所选作用域及宿主的配置文件，拒绝篡改或残缺记录。"""
    if set(data) != {'schemaVersion', 'entries'} or type(data['schemaVersion']) is not int or data['schemaVersion'] != 1:
        raise ConfigError('事务记录格式错误，保留文件，请人工核对')
    entries = data['entries']
    if not isinstance(entries, list) or not 1 <= len(entries) <= 2:
        raise ConfigError('事务记录 entries 必须包含一到两个文件')
    seen = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {'path', 'before', 'after'}:
            raise ConfigError('事务记录字段错误')
        if not isinstance(entry['path'], str):
            raise ConfigError('事务记录路径错误')
        path = Path(entry['path'])
        allowed = {*t3_hosts.rule_paths(project, host), project / TARGET_FILE,
                   project / PREVIOUS_TARGET_FILE, project / LEGACY_TARGET_FILE}
        if path not in allowed or path.resolve() != path or path in seen:
            raise ConfigError('事务记录包含项目范围外路径、链接或重复路径')
        seen.add(path)
        for key in ('before', 'after'):
            value = entry[key]
            if key == 'before' and value is None:
                continue
            if not isinstance(value, str):
                raise ConfigError('事务记录内容错误')
            base64.b64decode(value, validate=True)
    return entries


def create_exclusive(path: Path, data: bytes) -> None:
    """独占创建并持久化；写入失败仅删除本次创建的残缺文件。"""
    created = False
    try:
        with path.open('xb') as stream:
            created = True
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    except OSError:
        if created:
            path.unlink(missing_ok=True)
        raise


def write_pair(project: Path, changes: list, host: str | None = None) -> None:
    """先持久化恢复记录，再写目标与角色；普通失败立即回滚。"""
    journal = project / JOURNAL
    entries = [{'path': str(path), 'before': encode(old), 'after': encode(new)} for path, old, new in changes]
    data = json.dumps({'schemaVersion': 1, 'entries': entries}).encode('utf-8')
    create_exclusive(journal, data)
    try:
        for path, old, new in changes:
            if snapshot(path) != old:
                raise ConfigError(f'{path} 在预览后被修改，请重新预览')
            if old is not None:
                backup = path.with_name(path.name + '.s-models.bak')
                if backup.is_symlink():
                    raise ConfigError(f'{backup} 备份路径不能是符号链接')
                try:
                    # 保留首次前像；本次事务的前像另存于 journal。
                    create_exclusive(backup, old)
                except FileExistsError:
                    if backup.is_symlink():
                        raise ConfigError(f'{backup} 备份路径不能是符号链接')
            atomic_write(path, new)
        if any(snapshot(path) != new for path, _, new in changes):
            raise ConfigError('写入后回读不一致，保留事务记录以供恢复')
        journal.unlink()
    except (OSError, ConfigError):
        recover(project, host)
        raise


def configure(rules: Path, project: Path, block: str, config: dict, capabilities: dict,
              apply: bool = False, host: str | None = None, scope: str = 'project') -> dict:
    """预览完整差异；apply 后双文件写入，绝不自行获取用户批准。"""
    if scope not in ('project', 'user') or (scope == 'user' and host not in t3_hosts.HOSTS):
        raise ConfigError('必须选择有效作用域；用户级配置还需明确宿主')
    project, rules = project.resolve(), rules.resolve()
    if project.exists() and not project.is_dir():
        raise ConfigError(f'配置根路径不是目录: {project}')
    if scope == 'project' and not project.is_dir():
        raise ConfigError(f'项目目录不存在或不是目录: {project}')
    expected_rules = (t3_hosts.global_rules(project, host) if scope == 'user'
                      else t3_hosts.project_rules(project, host))
    if rules != expected_rules:
        raise ConfigError('规则路径必须匹配所选作用域与宿主')
    if existing_or_current(project, JOURNAL, LEGACY_JOURNAL).exists():
        raise ConfigError('存在未完成事务，请先 recover 并重新预览')
    target_path = project / TARGET_FILE
    legacy_target = existing_or_current(project, TARGET_FILE, LEGACY_TARGET_FILE)
    if legacy_target.exists() and not target_path.exists():
        raise ConfigError(f'请先把 {legacy_target.name} 改名为 {TARGET_FILE}，再写入')
    if target_path.is_symlink():
        raise ConfigError('项目目标文件不能是符号链接')
    checked = role_config(block)
    if checked['status'] != 'ok' or set(checked.get('rows', {})) != set(SIX_ROLES):
        raise ConfigError('候选标记段必须是合法的完整六角色配置')
    lines = block.strip().splitlines()
    if s_models.find_block(lines) != (0, len(lines) - 1):
        raise ConfigError('候选文件只能包含模型标记段，不能带其他规则')
    originals = {p: snapshot(p) for p in (rules, target_path)}
    existing, newline, bom = s_models.read_file(rules)
    if snapshot(rules) != originals[rules]:
        raise ConfigError('配置在读取期间被修改，请重新预览')
    if host == 'cursor' and scope == 'user' and not existing.strip():
        existing = '---\ndescription: s per-role model choices (overrides skill defaults)\nalwaysApply: true\n---\n' + existing
    merged, _ = s_models.merged_text(existing, block.strip())
    check(merged, config, capabilities)
    rules_data = (s_models.BOM if bom else b'') + merged.replace('\n', newline).encode('utf-8')
    target_data = (json.dumps(config, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    changes = [(p, originals[p], data) for p, data in ((target_path, target_data), (rules, rules_data))]
    changes = [entry for entry in changes if entry[1] != entry[2]]
    diffs = [''.join(difflib.unified_diff((old or b'').decode('utf-8-sig').splitlines(True),
             new.decode('utf-8-sig').splitlines(True), fromfile=str(p), tofile=str(p))) for p, old, new in changes]
    if apply and changes:
        if scope == 'user':
            project.mkdir(parents=True, exist_ok=True)
            rules.parent.mkdir(parents=True, exist_ok=True)
        write_pair(project, changes, host)
    return {'schemaVersion': 1, 'changed': bool(changes), 'applied': apply and bool(changes),
            'rules': merged, 'targets': config, 'diff': '\n'.join(diffs)}


def main(argv: list[str] | None = None) -> int:
    """CLI 的文件与 JSON 错误边界；默认 configure 仅预览。"""
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    render = sub.add_parser('render')
    render.add_argument('--budget', required=True)
    render.add_argument('--set', action='append', required=True, help='角色=模型或t3:别名，明确指定六行')
    for name in ('check', 'resolve', 'configure', 'recover'):
        item = sub.add_parser(name)
        item.add_argument('--project', type=Path, help='项目根；project 作用域必填')
        item.add_argument('--scope', choices=('project', 'user'), default='project')
        item.add_argument('--host', choices=t3_hosts.HOSTS, help='全局配置的当前底层宿主，不能用目标提供商代替')
        item.add_argument('--global-dir', type=Path, help='覆盖所选宿主的配置根目录；默认遵从宿主环境变量')
        if name == 'recover':
            continue
        item.add_argument('--rules', type=Path, help='所选作用域及宿主的规则文件，省略时自动定位')
        item.add_argument('--capabilities', type=Path, required=True)
        if name == 'resolve':
            item.add_argument('--role', required=True)
            item.add_argument('--native-model', action='append', default=[])
            item.add_argument('--worktree', action='store_true')
            item.add_argument('--delegate', action='store_true')
        if name == 'configure':
            item.add_argument('--targets', type=Path, required=True)
            item.add_argument('--block', type=Path, required=True)
            item.add_argument('--apply', action='store_true')
    args = parser.parse_args(argv)
    try:
        result = execute(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, s_models.SModelsError) as exc:
        print(json.dumps({'status': 'error', 'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


def scope_paths(args) -> tuple[Path, Path]:
    """显式绑定写入/读取目录；全局模型规则不冒充底层宿主原生规则。"""
    if args.scope == 'project' and args.project is None:
        raise ConfigError('project 作用域必须指定 --project')
    root = t3_hosts.global_root(args.host, args.global_dir) if args.scope == 'user' else args.project.resolve()
    if root.exists() and not root.is_dir():
        raise ConfigError(f'配置根路径不是目录: {root}')
    if args.scope == 'project' and not root.is_dir():
        raise ConfigError(f'项目目录不存在或不是目录: {root}')
    default = (t3_hosts.global_rules(root, args.host) if args.scope == 'user'
               else t3_hosts.project_rules(root, args.host))
    rules = (getattr(args, 'rules', None) or default).resolve()
    if rules != default:
        raise ConfigError('--rules 必须匹配所选作用域与宿主的规则路径；规则文件不支持符号链接')
    return root, rules


def read_scope(root: Path, rules: Path) -> tuple[str, dict, Path]:
    """读取同一作用域的一对文件；未完成事务不允许被当成有效配置。"""
    if existing_or_current(root, JOURNAL, LEGACY_JOURNAL).exists():
        raise ConfigError(f'{root} 存在未完成事务，请先 recover')
    target_path = existing_or_current(root, TARGET_FILE, LEGACY_TARGET_FILE)
    if target_path.is_symlink():
        raise ConfigError(f'目标文件不能是符号链接: {target_path}')
    text = rules.read_text(encoding='utf-8-sig') if rules.exists() else ''
    span = s_models.find_block(text.splitlines())
    if span is None and target_path.exists():
        raise ConfigError(f'孤立目标文件 {target_path} 没有对应模型规则段，请先核对作用域')
    if span is not None:
        complete_role_config(text)
    config = load_json(target_path) if target_path.exists() else {'schemaVersion': 1, 'targets': {}}
    return text, config, target_path


def selected_scope(args) -> tuple[str, str, dict, Path, Path]:
    """项目完整模型段优先；无模型段才使用用户级配置，不跨作用域借别名。"""
    root, rules = scope_paths(args)
    text, config, target_path = read_scope(root, rules)
    scope = args.scope
    # find_block 同时拒绝残缺标记，不能将损坏配置误判为未配置。
    if scope == 'project' and s_models.find_block(text.splitlines()) is None:
        root = t3_hosts.global_root(args.host, args.global_dir)
        rules = t3_hosts.global_rules(root, args.host).resolve()
        if rules not in t3_hosts.rule_paths(root, args.host):
            raise ConfigError('全局规则路径不能是指向其他目录的符号链接')
        text, config, target_path = read_scope(root, rules)
        scope = 'user'
    return scope, text, config, rules, target_path


def execute(args) -> dict:
    if args.command == 'render':
        return {'schemaVersion': 1, 'block': render_block(args.budget, s_models.parse_sets(args.set))}
    if args.command == 'recover':
        root, _ = scope_paths(args)
        return recover(root, args.host if args.scope == 'user' or args.host == 'codex' else None)
    caps = load_json(args.capabilities)
    if args.command == 'configure':
        root, rules = scope_paths(args)
        result = configure(rules, root, args.block.read_text(encoding='utf-8-sig'),
                           load_json(args.targets), caps, args.apply,
                           args.host if args.scope == 'user' or args.host == 'codex' else None, args.scope)
        return {**result, 'scope': args.scope, 'rulesPath': str(rules), 'targetsPath': str(root / TARGET_FILE)}
    scope, text, config, rules, target_path = selected_scope(args)
    if args.command == 'check':
        result = check(text, config, caps)
    else:
        result = resolve(text, args.role, config, caps, args.native_model, args.worktree, args.delegate)
    return {**result, 'scope': scope, 'rulesPath': str(rules), 'targetsPath': str(target_path)}


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    sys.exit(main())
