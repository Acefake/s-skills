"""按宿主动态推荐角色模型：白名单筛选、推荐顺延和编号选择。"""
import copy
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / 'plugins/wukong/skills/setup-s-models/scripts'
sys.path.insert(0, str(SCRIPTS))
import t3_catalog as cat
import t3_targets as t3

EFFORT = [{'id': 'effort', 'values': ['low', 'medium', 'high'], 'default': 'medium'}]
REASONING = [{'id': 'reasoningEffort', 'values': ['low', 'medium', 'high'], 'default': 'low'},
             {'id': 'serviceTier', 'values': ['default', 'priority'], 'default': 'default'}]
THOUGHT = [{'id': 'thought_level', 'values': ['high', 'enabled'], 'default': 'enabled'},
           {'id': 'multitask', 'values': [False, True], 'default': False}]


def provider(pid, models, options=(), display=None, run=True, cross=True, omitted=0):
    return {'providerInstanceId': pid, 'displayName': display or pid, 'canRunChildTask': run,
            'canRunCrossProviderChildTask': cross, 'omittedModels': omitted,
            'models': [{'id': m, 'options': list(options)} for m in models]}


CLAUDE = provider('claudeAgent', ['claude-haiku-5-5', 'claude-sonnet-5-5', 'claude-opus-5-5',
                                  'claude-fable-5-2'], EFFORT, 'Claude')
CODEX = provider('codex', ['gpt-6-luna', 'gpt-6.1-sol', 'gpt-6-astra', 'gpt-6.1-terra'], REASONING, 'Codex')
CURSOR = provider('cursor', ['grok-4.7', 'composer-2.5', 'claude-opus-5-5', 'gemini-4-carbon'], EFFORT, 'Cursor')
CODEBUDDY = provider('acpRegistry_codebuddy_code', ['deepseek-v4.1-flash', 'glm-5.3', 'glm-5.3-flash', 'hy4std'],
                     THOUGHT, 'Codebuddy Code')
ANTIGRAVITY = provider('antigravity', ['gemini-3.8-flash-high'], display='Antigravity')
DEVIN = provider('acpRegistry_devin', ['swe-2-flash-medium'], display='Devin')


def caps(*providers, parent=('claudeAgent', 'claude-opus-5-5')):
    return {'inheritedProviderInstanceId': parent[0], 'inheritedModel': parent[1], 'inheritedOptions': [],
            'providers': copy.deepcopy(list(providers))}


def allowlist():
    return cat.load_allowlist(json.loads(cat.ALLOWLIST.read_text(encoding='utf-8')))


def keys(result, role):
    return [item['key'] for item in result['recommend'][role]['items']]


class RecommendTest(unittest.TestCase):
    def test_same_allowlist_adapts_to_three_machines(self):
        full = cat.build(allowlist(), caps(CLAUDE, CODEX, CURSOR, CODEBUDDY, ANTIGRAVITY, DEVIN))
        partial = cat.build(allowlist(), caps(CODEX, CODEBUDDY, ANTIGRAVITY, DEVIN, parent=('codex', 'gpt-6.1-sol')))
        codex = cat.build(allowlist(), caps(CODEX, parent=('codex', 'gpt-6.1-sol')))
        expected = {
            '检索与探索': (['haiku', 'luna', 'dsflash', 'composer'], ['luna', 'dsflash', 'glmflash', 'gemini'], ['luna']),
            '方案设计': (['opus', 'sonnet', 'sol', 'astra'], ['sol', 'astra', 'glm', 'dsflash'], ['sol', 'astra']),
            '开发实现': (['sonnet', 'sol', 'opus', 'composer'], ['sol', 'glm', 'astra', 'swe2'], ['sol', 'astra']),
            '专项攻坚': (['opus', 'astra', 'sol', 'grok'], ['astra', 'sol', 'glm', 'dsflash'], ['astra', 'sol']),
            '验证测试': (['sol', 'sonnet', 'terra', 'dsflash'], ['sol', 'terra', 'dsflash', 'glm'], ['sol', 'terra']),
            '独立评审': (['dsflash', 'sol', 'sonnet', 'grok'], ['dsflash', 'sol', 'glm', 'astra'], ['sol', 'astra']),
        }
        for role, (a, b, c) in expected.items():
            self.assertEqual(keys(full, role), a, role)
            self.assertEqual(keys(partial, role), b, role)
            self.assertEqual(keys(codex, role), c, role)
            self.assertFalse(codex['recommend'][role]['fallbackToFull'])

    def test_recommend_items_point_at_numbered_entries(self):
        result = cat.build(allowlist(), caps(CLAUDE, CODEX))
        entries = {entry['n']: entry for entry in result['entries']}
        for item in result['recommend']['方案设计']['items']:
            self.assertEqual(entries[item['n']]['key'], item['key'])
        self.assertEqual(entries[1]['options'], EFFORT)

    def test_claude_models_never_route_through_cursor(self):
        result = cat.build(allowlist(), caps(CURSOR, CODEX, parent=('codex', 'gpt-6.1-sol')))
        models = {(e['providerInstanceId'], e['model']) for e in result['entries']}
        self.assertNotIn(('cursor', 'claude-opus-5-5'), models)
        self.assertIn('opus', [item['key'] for item in result['missing']])
        self.assertEqual(keys(result, '专项攻坚'), ['astra', 'sol', 'grok'])

    def test_provider_only_applies_to_all_and_full_fallback(self):
        everything = cat.build(allowlist(), caps(CLAUDE, CURSOR), show_all=True)
        cursor = [e['model'] for e in everything['entries'] if e['providerInstanceId'] == 'cursor']
        self.assertEqual(sorted(cursor), ['composer-2.5', 'grok-4.7'])
        only_cursor = provider('cursor', ['gpt-x', 'composer-2.5', 'claude-opus-5-5'], EFFORT, 'Cursor')
        result = cat.build(allowlist(), caps(only_cursor, parent=('cursor', 'gpt-x')))
        self.assertTrue(result['recommend']['方案设计']['fallbackToFull'])
        self.assertEqual(keys(result, '方案设计'), ['inherit-parent', 'composer'])
        self.assertEqual([e['model'] for e in result['entries']], ['composer-2.5'])

    def test_no_allowlist_match_falls_back_to_parent_provider(self):
        kimi = provider('kimi', ['k2', 'k3', 'k4', 'k5'], EFFORT, 'Kimi')
        other = provider('other', ['o1'], EFFORT)
        result = cat.build(allowlist(), caps(kimi, other, parent=('kimi', 'k2')))
        role = result['recommend']['独立评审']
        self.assertTrue(role['fallbackToFull'])
        self.assertEqual([item['key'] for item in role['items']], ['inherit-parent', None, None, None])
        entries = {e['n']: e['model'] for e in result['entries']}
        self.assertEqual([entries[item['n']] for item in role['items'][1:]], ['k2', 'k3', 'k4'])
        self.assertIn('o1', entries.values())

    def test_unrunnable_and_non_cross_providers_are_skipped(self):
        disabled = provider('codex', ['gpt-6.1-sol'], REASONING, run=False)
        no_cross = provider('acpRegistry_codebuddy_code', ['deepseek-v4.1-flash'], THOUGHT, cross=False)
        result = cat.build(allowlist(), caps(CLAUDE, disabled, no_cross))
        models = [e['model'] for e in result['entries']]
        self.assertNotIn('gpt-6.1-sol', models)
        self.assertNotIn('deepseek-v4.1-flash', models)

    def test_display_name_matches_provider_word(self):
        renamed = provider('x1', ['swe-2-flash-medium'], display='Devin')
        result = cat.build(allowlist(), caps(CLAUDE, renamed))
        self.assertIn(('x1', 'swe-2-flash-medium'),
                      {(e['providerInstanceId'], e['model']) for e in result['entries']})

    def test_show_all_lists_non_allowlisted_models_after_allowlist(self):
        codex = provider('codex', ['gpt-6.1-sol', 'gpt-old'], REASONING)
        result = cat.build(allowlist(), caps(CLAUDE, codex), show_all=True)
        self.assertEqual(result['entries'][-1]['model'], 'gpt-old')
        self.assertIsNone(result['entries'][-1]['key'])
        self.assertNotIn('gpt-old', [e['model'] for e in cat.build(allowlist(), caps(CLAUDE, codex))['entries']])


class SnapshotTest(unittest.TestCase):
    def test_search_snapshots_are_merged_without_duplicates(self):
        base = caps(provider('claudeAgent', ['claude-opus-5-5'], EFFORT, omitted=3))
        search = caps(provider('claudeAgent', ['claude-opus-5-5', 'claude-haiku-5-5'], EFFORT))
        merged = cat.merge_snapshots([base, {'structuredContent': search}])
        ids = [m['id'] for m in merged['providers'][0]['models']]
        self.assertEqual(ids, ['claude-opus-5-5', 'claude-haiku-5-5'])
        missing = {item['key']: item for item in cat.build(allowlist(), merged)['missing']}
        self.assertTrue(missing['sonnet']['maybeTruncated'])
        self.assertEqual(missing['sonnet']['search'], 'claude-sonnet-5-5')
        self.assertFalse(missing['luna']['maybeTruncated'])

    def test_search_only_provider_is_ignored(self):
        merged = cat.merge_snapshots([caps(CLAUDE), caps(provider('ghost', ['m']))])
        self.assertEqual([p['providerInstanceId'] for p in merged['providers']], ['claudeAgent'])


class AllowlistTest(unittest.TestCase):
    def broken(self, change):
        data = json.loads(cat.ALLOWLIST.read_text(encoding='utf-8'))
        change(data)
        with self.assertRaises(t3.ConfigError):
            cat.load_allowlist(data)

    def test_invalid_allowlists_are_rejected(self):
        self.broken(lambda d: d['roles']['方案设计'].append('nope'))
        self.broken(lambda d: d['roles'].pop('独立评审'))
        self.broken(lambda d: d['roles']['方案设计'].append('opus'))
        self.broken(lambda d: d['models']['opus'].update(providers=[]))
        self.broken(lambda d: d['providerOnly']['cursor'].append('claude-opus-5-5'))
        self.broken(lambda d: d.update(schemaVersion=2))


class PickTest(unittest.TestCase):
    def setUp(self):
        self.catalog = cat.build(allowlist(), caps(CLAUDE, CODEX, CURSOR))

    def test_pick_by_number_or_model_id_validates_options(self):
        first = cat.pick(self.catalog, '1', {'effort': 'high'})
        self.assertEqual(first, {'providerInstanceId': 'claudeAgent', 'model': 'claude-haiku-5-5',
                                 'options': {'effort': 'high'}})
        sol = cat.pick(self.catalog, 'gpt-6.1-sol', {'reasoningEffort': 'medium', 'serviceTier': 'default'})
        self.assertEqual(sol['providerInstanceId'], 'codex')
        with self.assertRaises(t3.ConfigError):
            cat.pick(self.catalog, 'gpt-6.1-sol', {'reasoningEffort': 'ultra'})

    def test_pick_rejects_unknown_hidden_and_out_of_range_choices(self):
        for choice in ('claude-opus-5-5x', 'gemini-4-carbon', '99', '0'):
            with self.assertRaises(t3.ConfigError, msg=choice):
                cat.pick(self.catalog, choice, {})

    def test_pick_converts_boolean_option_text(self):
        catalog = cat.build(allowlist(), caps(CLAUDE, CODEBUDDY))
        target = cat.pick(catalog, 'glm-5.3', {'multitask': 'true', 'thought_level': 'enabled'})
        self.assertIs(target['options']['multitask'], True)


class CliTest(unittest.TestCase):
    def run_cli(self, *argv):
        out, err = StringIO(), StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = cat.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def test_catalog_and_pick_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            base, search = Path(tmp, 'base.json'), Path(tmp, 'search.json')
            base.write_text(json.dumps(caps(CLAUDE)), encoding='utf-8')
            search.write_text(json.dumps(caps(CODEX)), encoding='utf-8')
            code, out, _ = self.run_cli('catalog', '--capabilities', str(base), '--capabilities', str(search))
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(out)['recommend']['验证测试']['items'][0]['key'], 'sonnet')
            code, out, _ = self.run_cli('pick', '--capabilities', str(base), '--choice', 'claude-sonnet-5-5',
                                        '--option', 'effort=medium')
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(out)['target']['model'], 'claude-sonnet-5-5')
            code, _, err = self.run_cli('pick', '--capabilities', str(base), '--choice', '42')
            self.assertEqual(code, 1)
            self.assertIn('编号', json.loads(err)['error'])

    def test_plan_command_runs_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp, 'base.json')
            base.write_text(json.dumps(caps(CLAUDE, CODEX, CODEBUDDY)), encoding='utf-8')
            code, out, err = self.run_cli(
                'plan', '--capabilities', str(base),
                '--budget', '省',
                '--tier', 'claudeAgent=low', '--tier', 'codex=low', '--tier', 'codebuddy=high',
            )
            self.assertEqual(code, 0, err)
            data = json.loads(out)
            self.assertEqual(data['budget'], '省')
            self.assertEqual(data['recommendedBudget'], '中')
            self.assertEqual(set(data['roles']), set(t3.SIX_ROLES))
            # Claude is low-tier in 省 budget: must never assign opus to high-frequency roles.
            for role in ('检索与探索', '方案设计', '开发实现', '验证测试', '独立评审'):
                self.assertNotEqual(data['roles'][role]['primary']['model'], 'claude-opus-5-5', role)


class SmartPlanTest(unittest.TestCase):
    def test_unseen_future_models_are_classified_and_ranked_by_capability(self):
        future_a = provider('futureA', ['alpha-7-mini', 'alpha-7.2-pro', 'alpha-7.2-opus'], EFFORT, 'Future A')
        future_b = provider('futureB', ['beta-4-flash', 'beta-4-neon', 'beta-4-r1'], REASONING, 'Future B')
        plan = cat.smart_plan(caps(future_a, future_b, parent=('futureA', 'alpha-7.2-pro')), budget='中')
        self.assertEqual(plan['roles']['检索与探索']['primary']['capTier'], 'light')
        self.assertEqual(plan['roles']['专项攻坚']['primary']['capTier'], 'heavy')
        self.assertEqual(plan['roles']['开发实现']['primary']['capTier'], 'balanced')
        # 独立评审优先与开发实现跨提供商
        self.assertNotEqual(
            plan['roles']['独立评审']['primary']['providerInstanceId'],
            plan['roles']['开发实现']['primary']['providerInstanceId'],
        )

    def test_entry_level_subscription_protects_quota_and_warns_on_high_budget(self):
        plan_low = cat.smart_plan(
            caps(CLAUDE, CODEX, CODEBUDDY),
            budget='省',
            provider_tiers={'claudeAgent': 'low', 'codex': 'low', 'codebuddy': 'high'},
            allowlist=allowlist(),
        )
        # 省档入门订阅池高频角色优先分流到充裕池 codebuddy，高频角色不烧旗舰
        self.assertEqual(plan_low['roles']['检索与探索']['primary']['providerInstanceId'], 'acpRegistry_codebuddy_code')
        self.assertEqual(plan_low['roles']['独立评审']['primary']['providerInstanceId'], 'acpRegistry_codebuddy_code')
        for role in ('检索与探索', '方案设计', '开发实现', '验证测试', '独立评审'):
            self.assertNotEqual(plan_low['roles'][role]['primary']['capTier'], 'heavy', role)
        # 低频专项攻坚仍保留旗舰（但思考档位受限于入门省档）
        self.assertEqual(plan_low['roles']['专项攻坚']['primary']['capTier'], 'heavy')

        # 全部提供商都是入门额度时，默认推荐省档；强选高/超高弹出限流预警
        all_low = cat.smart_plan(
            caps(CLAUDE, CODEX),
            budget='超高',
            provider_tiers={'all': 'low'},
            allowlist=allowlist(),
        )
        self.assertEqual(all_low['recommendedBudget'], '省')
        self.assertTrue(all_low['warnings'])
        self.assertIn('secondReviewer', all_low['roles']['独立评审'])
        self.assertNotEqual(
            all_low['roles']['独立评审']['primary']['providerInstanceId'],
            all_low['roles']['独立评审']['secondReviewer']['primary']['providerInstanceId'],
        )

    def test_newer_unlisted_generation_outranks_older_allowlisted_model_without_hurting_terra(self):
        codex_new = provider('codex', ['gpt-6-luna', 'gpt-6.1-sol', 'gpt-6.2-sol', 'gpt-6.1-terra', 'gpt-6-astra'],
                             REASONING, 'Codex')
        plan = cat.smart_plan(
            caps(codex_new, parent=('codex', 'gpt-6.2-sol')),
            budget='省',
            provider_tiers={'codex': 'low'},
            allowlist=allowlist(),
        )
        self.assertEqual(plan['roles']['检索与探索']['primary']['model'], 'gpt-6-luna')
        self.assertEqual(plan['roles']['开发实现']['primary']['model'], 'gpt-6.2-sol')
        self.assertEqual(plan['roles']['专项攻坚']['primary']['model'], 'gpt-6-astra')
        # 单宿主 Codex 下 terra 不被 sol 6.2 跨家族误伤，用于独立评审/验证测试错开 sol
        self.assertEqual(plan['roles']['独立评审']['primary']['model'], 'gpt-6.1-terra')
        self.assertEqual(plan['roles']['验证测试']['primary']['model'], 'gpt-6.1-terra')

    def test_all_other_single_hosts_allocate_dynamically(self):
        # 1. 纯 Claude：开发用 sonnet，评审错开家族用 fable，攻坚用 opus，检索用 haiku
        claude_plan = cat.smart_plan(caps(CLAUDE, parent=('claudeAgent', 'claude-sonnet-5-5')), budget='省')
        self.assertEqual(claude_plan['roles']['检索与探索']['primary']['model'], 'claude-haiku-5-5')
        self.assertEqual(claude_plan['roles']['开发实现']['primary']['model'], 'claude-sonnet-5-5')
        self.assertEqual(claude_plan['roles']['专项攻坚']['primary']['model'], 'claude-opus-5-5')
        self.assertEqual(claude_plan['roles']['独立评审']['primary']['model'], 'claude-fable-5-2')

        # 2. 纯 CodeBuddy：开发用 glm-5.3，评审错开家族用带思考参数的 deepseek-v4.1-flash
        cb_plan = cat.smart_plan(caps(CODEBUDDY, parent=('acpRegistry_codebuddy_code', 'glm-5.3')),
                                 budget='省', allowlist=allowlist())
        self.assertEqual(cb_plan['roles']['开发实现']['primary']['model'], 'glm-5.3')
        self.assertEqual(cb_plan['roles']['独立评审']['primary']['model'], 'deepseek-v4.1-flash')

        # 3. 纯 Antigravity：多模型时自动按家族/档位错开
        agy = provider('antigravity', ['gemini-4-flash', 'gemini-4-neon', 'gemini-4-ultra'], THOUGHT, 'Antigravity')
        agy_plan = cat.smart_plan(caps(agy, parent=('antigravity', 'gemini-4-neon')), budget='省')
        self.assertEqual(agy_plan['roles']['检索与探索']['primary']['model'], 'gemini-4-flash')
        self.assertEqual(agy_plan['roles']['开发实现']['primary']['model'], 'gemini-4-neon')
        self.assertEqual(agy_plan['roles']['专项攻坚']['primary']['model'], 'gemini-4-ultra')
        self.assertNotEqual(agy_plan['roles']['独立评审']['primary']['model'], 'gemini-4-neon')

        # 4. 纯 Devin 单模型：优雅降级并发出单模提示
        devin_plan = cat.smart_plan(caps(DEVIN, parent=('acpRegistry_devin', 'swe-2-flash-medium')), budget='省')
        self.assertEqual(devin_plan['roles']['开发实现']['primary']['model'], 'swe-2-flash-medium')
        self.assertIsNone(devin_plan['roles']['开发实现']['fallback'])
        self.assertTrue(any('1 个可用模型' in w for w in devin_plan['warnings']))

    def test_schema_v3_dynamic_policy_resolves_latest_models_at_runtime_without_editing_config(self):
        block = (
            '# s 模型配置\n'
            '# 预算: 省（medium）\n'
            '检索与探索: t3:lookup\n'
            '方案设计: t3:design\n'
            '开发实现: t3:implementation\n'
            '专项攻坚: t3:hard\n'
            '验证测试: t3:test\n'
            '独立评审: t3:review\n'
            '# s 模型配置结束\n'
        )
        dynamic_cfg = {
            'schemaVersion': 3,
            'mode': 'dynamic',
            'budget': '省',
            'providerTiers': {'codex': 'low'},
            'targets': {},
        }
        # 同一份配置文件，宿主机从 6.1 升级到 6.3 后自动解析到最新代，无需改配置
        snap_61 = caps(provider('codex', ['gpt-6-luna', 'gpt-6.1-sol', 'gpt-6.1-terra', 'gpt-6-astra'], REASONING, 'Codex'),
                       parent=('codex', 'gpt-6.1-sol'))
        snap_63 = caps(provider('codex', ['gpt-6-luna', 'gpt-6.1-sol', 'gpt-6.3-sol', 'gpt-6.1-terra', 'gpt-6-astra'], REASONING, 'Codex'),
                       parent=('codex', 'gpt-6.3-sol'))
        self.assertEqual(t3.check(block, dynamic_cfg, snap_61)['status'], 'ok')
        self.assertEqual(t3.resolve(block, '开发实现', dynamic_cfg, snap_61)['items'][0]['target']['model'], 'gpt-6.1-sol')
        self.assertEqual(t3.resolve(block, '开发实现', dynamic_cfg, snap_63)['items'][0]['target']['model'], 'gpt-6.3-sol')
        self.assertEqual(t3.resolve(block, '独立评审', dynamic_cfg, snap_63)['items'][0]['target']['model'], 'gpt-6.1-terra')

        # 允许在 targets 里仅锁定某一个别名，其余仍保持全动态
        pinned = {**dynamic_cfg, 'targets': {'hard': {'providerInstanceId': 'codex', 'model': 'gpt-6.3-sol', 'options': {'reasoningEffort': 'high'}}}}
        self.assertEqual(t3.resolve(block, '专项攻坚', pinned, snap_63)['items'][0]['target']['model'], 'gpt-6.3-sol')
        self.assertEqual(t3.resolve(block, '开发实现', pinned, snap_63)['items'][0]['target']['model'], 'gpt-6.3-sol')

        # 规则段预算与 v3 budget 不一致时 check 报错
        mismatched = {**dynamic_cfg, 'budget': '中'}
        with self.assertRaises(t3.ConfigError):
            t3.check(block, mismatched, snap_63)

        # configure(v3, apply=True) 往返必须保留 schemaVersion: 3，且读回后 check 仍通过
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            rules = project / 'AGENTS.md'
            res = t3.configure(rules, project, block, dynamic_cfg, snap_63, apply=True)
            self.assertTrue(res['applied'])
            written = json.loads((project / t3.TARGET_FILE).read_text(encoding='utf-8'))
            self.assertEqual(written['schemaVersion'], 3)
            self.assertEqual(written['mode'], 'dynamic')
            self.assertEqual(t3.check(rules.read_text(encoding='utf-8'), written, snap_63)['status'], 'ok')

        # 高预算下手工 pin review 时，review2 自动避开已 pin 的评审目标，不重复派同一个模型
        high_block = block.replace('省（medium）', '大（xhigh）').replace('独立评审: t3:review', '独立评审: t3:review, t3:review2')
        high_cfg = {
            'schemaVersion': 3,
            'mode': 'dynamic',
            'budget': '高',
            'providerTiers': {'claudeAgent': 'high', 'codex': 'high'},
            'targets': {'review': {'providerInstanceId': 'codex', 'model': 'gpt-6-astra', 'options': {'reasoningEffort': 'high'}}},
        }
        both = caps(CLAUDE, CODEX)
        self.assertEqual(t3.check(high_block, high_cfg, both)['status'], 'ok')
        review_items = t3.resolve(high_block, '独立评审', high_cfg, both)['items']
        self.assertEqual(len(review_items), 2)
        self.assertNotEqual(review_items[0]['target']['model'], review_items[1]['target']['model'])

        # 反向手工 pin review2 时，动态 review 也避开 review2，不重复派同一个模型
        high_cfg_pin2 = {
            'schemaVersion': 3,
            'mode': 'dynamic',
            'budget': '高',
            'providerTiers': {'claudeAgent': 'high', 'codex': 'high'},
            'targets': {'review2': {'providerInstanceId': 'codex', 'model': 'gpt-6-astra', 'options': {'reasoningEffort': 'high'}}},
        }
        self.assertEqual(t3.check(high_block, high_cfg_pin2, both)['status'], 'ok')
        review_items_2 = t3.resolve(high_block, '独立评审', high_cfg_pin2, both)['items']
        self.assertEqual(len(review_items_2), 2)
        self.assertNotEqual(review_items_2[0]['target']['model'], review_items_2[1]['target']['model'])

        # 档位后缀归并进同一家族
        self.assertEqual(cat.model_family('gemini-3.8-flash-high'), cat.model_family('gemini-4-flash'))

    def test_ultra_budget_alias_in_s_models(self):
        import s_models
        self.assertEqual(s_models.normalize_budget('超高'), '不限')
        self.assertEqual(s_models.normalize_budget('ultra'), '不限')


if __name__ == '__main__':
    unittest.main()
