"""按当前宿主的能力目录和模型白名单，给六角色算推荐并校验编号选择；不写配置。"""
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path

import t3_targets as t3

ALLOWLIST = Path(__file__).resolve().parents[1] / 'references/model-allowlist.json'
RECOMMEND_LIMIT = 4
INHERIT = {'n': None, 'key': 'inherit-parent', 'label': '跟随当前对话模型'}
SUBSCRIPTION_TIERS = ('low', 'medium', 'high')
PLAN_BUDGETS = ('省', '中', '高', '超高')
TIER_RANK = {'low': 0, 'medium': 1, 'high': 2}
EFFORT_ORDER = ('low', 'medium', 'high', 'xhigh', 'max')
EFFORT_KEYS = ('reasoningEffort', 'reasoning_effort', 'effort', 'thought_level')
HEAVY_RE = re.compile(r'(?:^|[-_.])(opus|astra|ultra|o3|o4|r1|pro-max|thinking)(?:$|[-_.])', re.I)
LIGHT_RE = re.compile(r'(?:^|[-_.])(haiku|flash|mini|lite|nano|luna|fast|instant|hy4)(?:$|[-_.])', re.I)
VERSION_RE = re.compile(r'(\d+)(?:[.-](\d+))?')
HIGH_FREQ_ROLES = {'检索与探索', '验证测试', '独立评审'}


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


def parse_version(model_id: str) -> tuple[int, int]:
    """提取模型 ID 中的主次版本号用于同档比较，找不到返回 (0, 0)。"""
    best = (0, 0)
    for m in VERSION_RE.finditer(model_id):
        major = int(m.group(1))
        minor = int(m.group(2)) if m.group(2) is not None else 0
        if major <= 99 and (major, minor) > best:
            best = (major, minor)
    return best


def classify_model(provider: dict, model: dict) -> dict:
    """按模型 ID 特征与实时 options 元数据生成能力画像，不依赖写死白名单。"""
    mid = model['id']
    if HEAVY_RE.search(mid):
        cap_tier = 'heavy'
    elif LIGHT_RE.search(mid):
        cap_tier = 'light'
    else:
        cap_tier = 'balanced'

    effort_key, effort_values = None, []
    for opt in model.get('options', []):
        if opt.get('id') in EFFORT_KEYS:
            effort_key = opt['id']
            effort_values = [v for v in opt.get('values', []) if isinstance(v, str)]
            break
    ranked = [v for v in EFFORT_ORDER if v in effort_values]
    max_effort = ranked[-1] if ranked else ('enabled' if 'enabled' in effort_values else None)
    return {
        'providerInstanceId': provider['providerInstanceId'],
        'providerName': provider.get('displayName') or provider['providerInstanceId'],
        'model': mid,
        'capTier': cap_tier,
        'version': parse_version(mid),
        'effortKey': effort_key,
        'effortValues': effort_values,
        'maxEffort': max_effort,
        'hasReasoning': effort_key is not None,
        'options': model.get('options', []),
    }


def resolve_provider_tier(provider: dict, provider_tiers: dict[str, str] | None) -> str:
    """按提供商识别词解析订阅额度档位（low/medium/high），支持 all 兜底，默认 medium。"""
    if not provider_tiers:
        return 'medium'
    for word, tier in provider_tiers.items():
        if word.lower() != 'all' and matches(provider, word):
            return tier
    return provider_tiers.get('all', 'medium')


def select_options(profile: dict, role: str, budget: str, sub_tier: str) -> dict:
    """结合角色、预算与订阅档位，从模型自身合法 options 中选出最优参数。"""
    chosen = {}
    for opt in profile['options']:
        if opt.get('id') == 'serviceTier' and 'default' in opt.get('values', []):
            chosen['serviceTier'] = 'default'
    key = profile['effortKey']
    vals = profile['effortValues']
    if not key or not vals:
        return chosen
    if key == 'thought_level':
        if budget in ('高', '超高') and 'high' in vals and sub_tier != 'low':
            chosen[key] = 'high'
        elif 'enabled' in vals:
            chosen[key] = 'enabled'
        else:
            chosen[key] = vals[0]
        return chosen

    desired_map = {
        '省': {'检索与探索': 'low', '专项攻坚': 'medium' if sub_tier == 'low' else 'high'},
        '中': {'检索与探索': 'low', '专项攻坚': 'high'},
        '高': {'检索与探索': 'medium', '方案设计': 'high', '开发实现': 'high', '专项攻坚': 'high', '独立评审': 'high'},
        '超高': {'检索与探索': 'medium', '方案设计': 'max', '开发实现': 'high', '专项攻坚': 'max', '验证测试': 'high', '独立评审': 'max'},
    }
    desired = desired_map[budget].get(role, 'medium')
    if sub_tier == 'low' and budget == '省' and desired in ('high', 'xhigh', 'max'):
        desired = 'medium'
    order = [v for v in EFFORT_ORDER if v in vals]
    if not order:
        chosen[key] = vals[0]
        return chosen
    if desired in order:
        chosen[key] = desired
        return chosen
    target_idx = EFFORT_ORDER.index(desired)
    lower = [v for v in order if EFFORT_ORDER.index(v) <= target_idx]
    chosen[key] = lower[-1] if lower else order[0]
    return chosen


def _role_score(profile: dict, role: str, budget: str, sub_tier: str,
                avoid_provider: str | None = None,
                allowlist_rank: int | None = None,
                gen_lag: int = 0) -> float:
    cap = profile['capTier']
    # 角色×预算的能力偏好分
    table = {
        '省': {
            '检索与探索': {'light': 100, 'balanced': 55, 'heavy': 5},
            '方案设计': {'balanced': 100, 'heavy': 60, 'light': 45},
            '开发实现': {'balanced': 100, 'light': 50, 'heavy': 40},
            '专项攻坚': {'heavy': 105, 'balanced': 90, 'light': 30},
            '验证测试': {'balanced': 95, 'light': 80, 'heavy': 30},
            '独立评审': {'balanced': 95, 'light': 85, 'heavy': 45},
        },
        '中': {
            '检索与探索': {'light': 100, 'balanced': 60, 'heavy': 10},
            '方案设计': {'balanced': 95, 'heavy': 92, 'light': 35},
            '开发实现': {'balanced': 100, 'heavy': 65, 'light': 35},
            '专项攻坚': {'heavy': 110, 'balanced': 85, 'light': 20},
            '验证测试': {'balanced': 100, 'light': 70, 'heavy': 35},
            '独立评审': {'balanced': 95, 'light': 80, 'heavy': 75},
        },
        '高': {
            '检索与探索': {'light': 95, 'balanced': 75, 'heavy': 15},
            '方案设计': {'heavy': 110, 'balanced': 85, 'light': 20},
            '开发实现': {'balanced': 100, 'heavy': 90, 'light': 25},
            '专项攻坚': {'heavy': 115, 'balanced': 80, 'light': 15},
            '验证测试': {'balanced': 100, 'light': 65, 'heavy': 55},
            '独立评审': {'heavy': 105, 'balanced': 95, 'light': 65},
        },
        '超高': {
            '检索与探索': {'light': 90, 'balanced': 85, 'heavy': 25},
            '方案设计': {'heavy': 120, 'balanced': 80, 'light': 15},
            '开发实现': {'heavy': 110, 'balanced': 95, 'light': 15},
            '专项攻坚': {'heavy': 125, 'balanced': 75, 'light': 10},
            '验证测试': {'balanced': 100, 'heavy': 90, 'light': 45},
            '独立评审': {'heavy': 120, 'balanced': 90, 'light': 40},
        },
    }
    score = float(table[budget][role][cap])

    # 订阅额度稀缺保护与分流
    if sub_tier == 'low':
        if cap == 'heavy' and budget == '省':
            score -= 200  # 入门订阅省档严禁烧旗舰
        elif cap == 'heavy' and budget == '中' and role != '专项攻坚':
            score -= 40
        if role in HIGH_FREQ_ROLES and budget in ('省', '中'):
            score -= 28  # 高频角色尽量分流到充裕池
    elif sub_tier == 'high':
        if role in HIGH_FREQ_ROLES:
            score += 22
        else:
            score += 10
    else:  # medium
        if role in HIGH_FREQ_ROLES and budget in ('省', '中'):
            score += 10

    # 推理能力与同提供商同档代际优先：老一代扣分（-6/代），不因不同厂商版本号起点不同而偏置
    if profile['hasReasoning']:
        score += 12 if role in ('方案设计', '专项攻坚', '独立评审') else 4
    score -= gen_lag * 6.0

    # 跨提供商多样性加分（用于独立评审避开开发实现、或次选容灾）
    if avoid_provider and profile['providerInstanceId'] != avoid_provider:
        score += 24

    # 白名单仅做同代微调（最大 +0.8），绝不让旧版白名单压过新版同档模型
    if allowlist_rank is not None:
        score += max(0.0, (8 - allowlist_rank) * 0.1)
    return score


def _reason_text(profile: dict, sub_tier: str, role: str, is_fallback: bool = False,
                 cross_from: str | None = None) -> str:
    cap_cn = {'light': '轻量快模', 'balanced': '主力编码', 'heavy': '旗舰强推理'}[profile['capTier']]
    tier_cn = {'low': '入门池', 'medium': '标准池', 'high': '充裕池'}[sub_tier]
    parts = [cap_cn, tier_cn]
    if profile['hasReasoning']:
        parts.append(f"支持 {profile['effortKey']}")
    if is_fallback and cross_from and profile['providerInstanceId'] != cross_from:
        parts.append('跨提供商容灾')
    elif not is_fallback and role == '独立评审' and cross_from and profile['providerInstanceId'] != cross_from:
        parts.append('与实现跨提供商')
    return ' · '.join(parts)


def smart_plan(caps: dict, budget: str = '中', provider_tiers: dict[str, str] | None = None,
               allowlist: dict | None = None) -> dict:
    """按模型能力画像 + 订阅额度 + 四档预算（省/中/高/超高）生成完整六角色推荐方案。"""
    if budget not in PLAN_BUDGETS:
        raise t3.ConfigError(f'未知预算 {budget!r}：请使用 省、中、高、超高')
    if provider_tiers:
        for k, v in provider_tiers.items():
            if v not in SUBSCRIPTION_TIERS:
                raise t3.ConfigError(f'订阅档位 {k}={v!r} 无效：请使用 low、medium、high')

    providers = [p for p in caps['providers'] if runnable(caps, p)]
    resolved_tiers = {p['providerInstanceId']: resolve_provider_tier(p, provider_tiers) for p in providers}

    # 根据订阅池自动推荐默认预算
    tier_values = list(resolved_tiers.values())
    if tier_values and all(t == 'low' for t in tier_values):
        recommended_budget = '省'
    elif tier_values and all(t == 'high' for t in tier_values):
        recommended_budget = '高'
    else:
        recommended_budget = '中'

    warnings = []
    if tier_values and all(t == 'low' for t in tier_values) and budget in ('高', '超高'):
        warnings.append('当前所有可用提供商均为入门额度（low），使用高/超高档极易触发限流，建议降为省/中档或仅对专项攻坚升档。')

    # 收集所有可见模型的能力画像
    profiles = []
    allow_ranks: dict[str, dict[tuple[str, str], int]] = {r: {} for r in t3.SIX_ROLES}
    if allowlist is not None:
        found, _ = allowlisted(allowlist, providers)
        for role in t3.SIX_ROLES:
            for idx, key in enumerate(allowlist['roles'][role]):
                if key in found:
                    allow_ranks[role][(found[key]['providerInstanceId'], found[key]['model'])] = idx
    for p in providers:
        for m in p.get('models', []):
            if allowlist is not None and not visible(allowlist, p, m['id']):
                continue
            profiles.append(classify_model(p, m))

    # 计算每个模型在「同提供商 + 同能力档位」内的代际落后步数（0 = 最新代）
    group_versions: dict[tuple[str, str], list[tuple[int, int]]] = {}
    for pf in profiles:
        g = (pf['providerInstanceId'], pf['capTier'])
        group_versions.setdefault(g, [])
        if pf['version'] not in group_versions[g]:
            group_versions[g].append(pf['version'])
    for g in group_versions:
        group_versions[g].sort(reverse=True)
    for pf in profiles:
        pf['genLag'] = group_versions[(pf['providerInstanceId'], pf['capTier'])].index(pf['version'])

    def pick_best(role: str, avoid_provider: str | None = None,
                  exclude_pairs: set[tuple[str, str]] | None = None,
                  min_sub_rank: int | None = None) -> dict | None:
        excluded = exclude_pairs or set()
        candidates = [pf for pf in profiles if (pf['providerInstanceId'], pf['model']) not in excluded]
        if not candidates:
            return None
        # 入门订阅省档严禁选 heavy（除非本机只有 heavy）
        if budget == '省':
            non_low_heavy = [pf for pf in candidates
                             if not (pf['capTier'] == 'heavy' and resolved_tiers[pf['providerInstanceId']] == 'low')]
            if non_low_heavy:
                candidates = non_low_heavy

        def key_fn(pf):
            st = resolved_tiers[pf['providerInstanceId']]
            s = _role_score(pf, role, budget, st, avoid_provider=avoid_provider,
                            allowlist_rank=allow_ranks[role].get((pf['providerInstanceId'], pf['model'])),
                            gen_lag=pf['genLag'])
            if min_sub_rank is not None and TIER_RANK[st] >= min_sub_rank:
                s += 10
            return (s, pf['version'], pf['model'])

        return max(candidates, key=key_fn)

    def make_target(pf: dict, role: str, is_fallback: bool = False, cross_from: str | None = None) -> dict:
        st = resolved_tiers[pf['providerInstanceId']]
        return {
            'providerInstanceId': pf['providerInstanceId'],
            'model': pf['model'],
            'options': select_options(pf, role, budget, st),
            'capTier': pf['capTier'],
            'subscriptionTier': st,
            'reason': _reason_text(pf, st, role, is_fallback=is_fallback, cross_from=cross_from),
        }

    # 先决定「开发实现」，以便「独立评审」优先跨提供商
    order = ('开发实现', '检索与探索', '方案设计', '专项攻坚', '验证测试', '独立评审')
    role_plans: dict[str, dict] = {}
    impl_provider: str | None = None

    for role in order:
        avoid = impl_provider if role == '独立评审' else None
        primary_pf = pick_best(role, avoid_provider=avoid)
        if primary_pf is None:
            role_plans[role] = {'primary': INHERIT, 'fallback': None}
            continue
        if role == '开发实现':
            impl_provider = primary_pf['providerInstanceId']
        primary_pair = (primary_pf['providerInstanceId'], primary_pf['model'])
        primary_tier_rank = TIER_RANK[resolved_tiers[primary_pf['providerInstanceId']]]
        fb_pf = pick_best(role, avoid_provider=primary_pf['providerInstanceId'],
                          exclude_pairs={primary_pair}, min_sub_rank=primary_tier_rank)
        plan_entry = {
            'primary': make_target(primary_pf, role, is_fallback=False, cross_from=avoid),
            'fallback': make_target(fb_pf, role, is_fallback=True,
                                    cross_from=primary_pf['providerInstanceId']) if fb_pf else None,
        }
        if role == '独立评审' and budget in ('高', '超高'):
            second_pf = pick_best(role, avoid_provider=primary_pf['providerInstanceId'],
                                  exclude_pairs={primary_pair})
            if second_pf is not None:
                second_pair = (second_pf['providerInstanceId'], second_pf['model'])
                second_fb = pick_best(role, avoid_provider=second_pf['providerInstanceId'],
                                      exclude_pairs={primary_pair, second_pair})
                plan_entry['secondReviewer'] = {
                    'primary': make_target(second_pf, role, is_fallback=False,
                                           cross_from=primary_pf['providerInstanceId']),
                    'fallback': make_target(second_fb, role, is_fallback=True,
                                            cross_from=second_pf['providerInstanceId']) if second_fb else None,
                }
        role_plans[role] = plan_entry

    ordered_roles = {role: role_plans[role] for role in t3.SIX_ROLES}
    return {
        'schemaVersion': 1,
        'budget': budget,
        'recommendedBudget': recommended_budget,
        'providerTiers': resolved_tiers,
        'warnings': warnings,
        'roles': ordered_roles,
    }


def main(argv: list[str] | None = None) -> int:
    """CLI 边界：读取快照与白名单，错误以 JSON 写到 stderr 并返回 1。"""
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('catalog', 'pick', 'plan'):
        item = sub.add_parser(name)
        item.add_argument('--capabilities', type=Path, action='append', required=True,
                          help='第一份为不带 search 的基础快照，其余为 search 结果')
        item.add_argument('--allowlist', type=Path, default=ALLOWLIST)
        if name in ('catalog', 'pick'):
            item.add_argument('--all', action='store_true', help='同时列出白名单外的本机模型')
        if name == 'pick':
            item.add_argument('--choice', required=True, help='编号或模型 ID')
            item.add_argument('--option', action='append', default=[], help='key=value')
        if name == 'plan':
            item.add_argument('--budget', default='中', choices=PLAN_BUDGETS, help='省 / 中 / 高 / 超高')
            item.add_argument('--tier', action='append', default=[],
                              help='提供商订阅档位，如 claudeAgent=low、codex=medium、all=low')
    args = parser.parse_args(argv)
    try:
        caps = merge_snapshots([t3.load_json(path) for path in args.capabilities])
        allow = load_allowlist(t3.load_json(args.allowlist)) if args.allowlist and args.allowlist.is_file() else None
        if args.command == 'plan':
            tiers = dict(parse_option(text) for text in args.tier)
            result = smart_plan(caps, budget=args.budget, provider_tiers=tiers, allowlist=allow)
        else:
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
