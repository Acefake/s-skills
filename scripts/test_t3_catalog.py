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


if __name__ == '__main__':
    unittest.main()
