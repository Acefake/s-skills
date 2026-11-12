"""按当前宿主的能力目录和模型白名单，给六角色算推荐并校验编号选择；不写配置。"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

import t3_targets as t3

ALLOWLIST = Path(__file__).resolve().parents[1] / 'references/model-allowlist.json'
RECOMMEND_LIMIT = 4
INHERIT = {'n': None, 'key': 'inherit-parent', 'label': '跟随当前对话模型'}


def load_allowlist(data: dict) -> dict:
    """校验白名单结构；角色必须覆盖六角色且只引用已定义的模型。

    @throws ConfigError 结构、引用或 providerOnly 不一致时
    """
    if data.get('schemaVersion') != 1 or set(data) - {'schemaVersion', 'models', 'providerOnly', 'roles'}:
        raise t3.ConfigError('白名单必须是 schemaVersion: 1，且只含 models、providerOnly、roles')
    models = data.get('models')
    if not isinstance(models, dict) or not models:
        raise t3.ConfigError('白名单 models 必须是非空对象')
    for key, spec in models.items():
        spec = spec if isinstance(spec, dict) else {}
        providers = spec.get('providers')
        if (not isinstance(spec.get('model'), str) or not spec['model'] or not isinstance(spec.get('label'), str)
                or not isinstance(providers, list) or not providers
                or any(not isinstance(p, str) or not p for p in providers)):
            raise t3.ConfigError(f'白名单模型 {key} 需要 model、label 和非空 providers')
    roles = data.get('roles')
    if not isinstance(roles, dict) or set(roles) != set(t3.SIX_ROLES):
        raise t3.ConfigError('白名单 roles 必须正好覆盖六个角色')
    for role, order in roles.items():
        if (not isinstance(order, list) or not order or any(not isinstance(k, str) for k in order)
                or len(set(order)) != len(order) or set(order) - set(models)):
            raise t3.ConfigError(f'白名单角色 {role} 的顺序为空、重复或引用了未定义的模型')
    only = data.get('providerOnly', {})
    if not isinstance(only, dict):
        raise t3.ConfigError('白名单 providerOnly 必须是对象')
    for word, allowed in only.items():
        declared = {spec['model'] for spec in models.values() if word in spec['providers']}
        if (not isinstance(allowed, list) or any(not isinstance(m, str) for m in allowed)
                or not set(allowed) <= declared):
            raise t3.ConfigError(f'providerOnly.{word} 只能列出 models 里属于该提供商的模型')
    return data


def merge_snapshots(snapshots: list[dict]) -> dict:
    """以第一份为基础目录，把 search 结果的新模型并入同一提供商，并相应扣减省略数。

    只出现在 search 结果里的提供商不会加入，避免绕过基础目录的可运行状态。
    """
    base = copy.deepcopy(t3.capability_catalog(snapshots[0]))
    providers = {p['providerInstanceId']: p for p in base['providers']}
    for snapshot in snapshots[1:]:
        for extra in t3.capability_catalog(snapshot)['providers']:
            target = providers.get(extra['providerInstanceId'])
            if target is None:
                continue
            target.setdefault('models', [])
            known = {m['id'] for m in target['models']}
            added = [m for m in extra.get('models', []) if m['id'] not in known]
            target['models'].extend(copy.deepcopy(added))
            target['omittedModels'] = max(0, (target.get('omittedModels') or 0) - len(added))
    return base


def matches(provider: dict, word: str) -> bool:
    """识别词不区分大小写，命中实例 ID、driverKind 或显示名之一即可。"""
    word = word.lower()
    return any(word in str(provider.get(field) or '').lower()
               for field in ('providerInstanceId', 'driverKind', 'displayName'))


def runnable(caps: dict, provider: dict) -> bool:
    """与 model_capability 一致：能跑子任务，非父提供商还要能跨提供商。"""
    return provider.get('canRunChildTask') is True and (
        provider['providerInstanceId'] == caps.get('inheritedProviderInstanceId')
        or provider.get('canRunCrossProviderChildTask') is True)


def visible(allowlist: dict, provider: dict, model_id: str) -> bool:
    """providerOnly 限定的提供商只露出列出的模型，所有场景都适用。"""
    return all(model_id in allowed for word, allowed in allowlist.get('providerOnly', {}).items()
               if matches(provider, word))


def locate(allowlist: dict, spec: dict, providers: list[dict]) -> tuple[dict, dict] | None:
    """按 providers 识别词顺序找第一个可用的同名模型；未列出的提供商不参与。"""
    for word in spec['providers']:
        for provider in providers:
            if not matches(provider, word) or not visible(allowlist, provider, spec['model']):
                continue
            model = next((m for m in provider.get('models', []) if m['id'] == spec['model']), None)
            if model is not None:
                return provider, model
    return None


def entry(key: str | None, provider: dict, model: dict, label: str | None = None) -> dict:
    return {'n': None, 'key': key, 'providerInstanceId': provider['providerInstanceId'], 'model': model['id'],
            'label': label or model.get('label') or model['id'], 'options': model.get('options', [])}


def allowlisted(allowlist: dict, providers: list[dict]) -> tuple[dict, list[dict]]:
    """返回本机可用的白名单条目（按白名单顺序）和找不到的条目。"""
    found, missing = {}, []
    for key, spec in allowlist['models'].items():
        hit = locate(allowlist, spec, providers)
        if hit is not None:
            found[key] = entry(key, *hit, spec['label'])
            continue
        truncated = any(matches(p, w) and (p.get('omittedModels') or 0) > 0
                        for w in spec['providers'] for p in providers)
        missing.append({'key': key, 'model': spec['model'], 'maybeTruncated': truncated, 'search': spec['model']})
    return found, missing


def recommend(allowlist: dict, found: dict, everything: list[dict], parent: str | None) -> dict:
    """每个角色沿偏好顺序取本机可用的前 4 个；一个都没有时退回父提供商的完整目录。"""
    result = {}
    for role in t3.SIX_ROLES:
        items = [found[key] for key in allowlist['roles'][role] if key in found][:RECOMMEND_LIMIT]
        fallback = not items
        if fallback:
            same = [e for e in everything if e['providerInstanceId'] == parent]
            items = [INHERIT, *same[:RECOMMEND_LIMIT - 1]]
        result[role] = {'items': [{'n': i['n'], 'key': i['key'], 'label': i['label']} for i in items],
                        'fallbackToFull': fallback}
    return result


def build(allowlist: dict, caps: dict, show_all: bool = False) -> dict:
    """生成编号目录与每个角色的推荐。

    @param show_all 为真时在白名单之后追加本机其余可见模型
    @returns entries 为编号表；recommend 的 n 指向 entries；missing 为本机找不到的白名单模型
    """
    providers = [p for p in caps['providers'] if runnable(caps, p)]
    found, missing = allowlisted(allowlist, providers)
    taken = {(e['providerInstanceId'], e['model']) for e in found.values()}
    extras = [entry(None, p, m) for p in providers for m in p.get('models', [])
              if (p['providerInstanceId'], m['id']) not in taken and visible(allowlist, p, m['id'])]
    everything = [*found.values(), *extras]
    for n, item in enumerate(everything, 1):
        item['n'] = n
    roles = recommend(allowlist, found, everything, caps.get('inheritedProviderInstanceId'))
    full = show_all or any(role['fallbackToFull'] for role in roles.values())
    return {'schemaVersion': 1, 'entries': everything if full else list(found.values()),
            'recommend': roles, 'missing': missing}


def pick(catalog: dict, choice: str, options: dict) -> dict:
    """把用户填的编号或模型 ID 变成目标，并按该模型的能力校验参数。

    @throws ConfigError 编号或模型不在目录里、模型 ID 有歧义、参数非法时
    """
    entries = catalog['entries']
    if choice.isdigit():
        hits = [e for e in entries if e['n'] == int(choice)]
        if not hits:
            raise t3.ConfigError(f'编号 {choice} 不在本机目录里')
    else:
        hits = [e for e in entries if e['model'] == choice]
        if not hits:
            raise t3.ConfigError(f'模型 {choice} 不在本机可选目录里（不在白名单、被限制或本机没有）')
        if len(hits) > 1:
            raise t3.ConfigError(f'模型 {choice} 在多个提供商下都有，请改填编号')
    chosen = hits[0]
    definitions = {item['id']: item['values'] for item in chosen['options']}
    parsed = {key: coerce(value, definitions.get(key, [])) for key, value in options.items()}
    t3.validate_options({'id': chosen['model'], 'options': chosen['options']}, parsed)
    return {'providerInstanceId': chosen['providerInstanceId'], 'model': chosen['model'], 'options': parsed}


def coerce(value: str, allowed: list) -> str | bool:
    """命令行只能传文本；该参数接受布尔值时把 true/false 转成布尔。"""
    if value in ('true', 'false') and any(type(v) is bool for v in allowed):
        return value == 'true'
    return value


def main(argv: list[str] | None = None) -> int:
    """CLI 边界：读取快照与白名单，错误以 JSON 写到 stderr 并返回 1。"""
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('catalog', 'pick'):
        item = sub.add_parser(name)
        item.add_argument('--capabilities', type=Path, action='append', required=True,
                          help='第一份为不带 search 的基础快照，其余为 search 结果')
        item.add_argument('--allowlist', type=Path, default=ALLOWLIST)
        item.add_argument('--all', action='store_true', help='同时列出白名单外的本机模型')
        if name == 'pick':
            item.add_argument('--choice', required=True, help='编号或模型 ID')
            item.add_argument('--option', action='append', default=[], help='key=value')
    args = parser.parse_args(argv)
    try:
        caps = merge_snapshots([t3.load_json(path) for path in args.capabilities])
        catalog = build(load_allowlist(t3.load_json(args.allowlist)), caps, args.all)
        if args.command == 'catalog':
            result = catalog
        else:
            options = dict(parse_option(text) for text in args.option)
            result = {'schemaVersion': 1, 'target': pick(catalog, args.choice, options)}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError) as exc:
        print(json.dumps({'status': 'error', 'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


def parse_option(text: str) -> tuple[str, str]:
    key, sep, value = text.partition('=')
    if not sep or not key:
        raise t3.ConfigError(f'--option 需要 key=value: {text}')
    return key, value


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    sys.exit(main())
