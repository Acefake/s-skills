"""T3 配置的用户可见行为与失败恢复。"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'plugins/s-atlas/skills/setup-s-models/scripts'
sys.path.insert(0, str(SCRIPTS))
import s_models as models
import t3_targets as t3


def catalog():
    return {'inheritedProviderInstanceId': 'codex', 'inheritedModel': 'sol',
            'inheritedOptions': [{'id': 'reasoningEffort', 'value': 'medium'}],
            'providers': [
                {'providerInstanceId': 'codex', 'canRunChildTask': True,
                 'canRunCrossProviderChildTask': True, 'models': [
                     {'id': 'sol', 'options': [{'id': 'reasoningEffort', 'values': ['medium', 'high']}]},
                     {'id': 'plain', 'options': []}]},
                {'providerInstanceId': 'claude', 'canRunChildTask': True,
                 'canRunCrossProviderChildTask': True, 'models': [
                     {'id': 'sonnet', 'options': [{'id': 'effort', 'values': ['medium', 'high']}]},
                     {'id': '["workbuddy","model"]', 'options': []}]}]}


def config(model='sonnet', options=None):
    return {'schemaVersion': 1, 'targets': {'review': {
        'providerInstanceId': 'claude', 'model': model,
        'options': {'effort': 'medium'} if options is None else options}}}


def block(value='t3:review'):
    return t3.render_block('省', {role: value for role in t3.SIX_ROLES})


class ResolveTest(unittest.TestCase):
    def resolve(self, text=None, targets=None, caps=None, **kw):
        return t3.resolve(text or block(), '修 bug', targets or config(), caps or catalog(), **kw)

    def test_cross_provider_maps_options_and_route(self):
        result = self.resolve()['items'][0]
        self.assertEqual(result['executor'], 'delegate_task')
        self.assertEqual(result['target'], {'providerInstanceId': 'claude', 'model': 'sonnet',
                                           'options': {'effort': 'medium'}})

    def test_native_requires_explicit_native_model_support(self):
        result = self.resolve(block('sol'), native_models=['sol'])['items'][0]
        self.assertEqual(result['executor'], 'native')
        self.assertEqual(self.resolve(block('sol'), native_models=['sol'], worktree=True)
                         ['items'][0]['executor'], 'delegate_task')

    def test_explicit_options_force_t3_even_on_same_provider(self):
        targets = config()
        targets['targets']['review'] = {'providerInstanceId': 'codex', 'model': 'sol',
                                       'options': {'reasoningEffort': 'medium'}}
        self.assertEqual(self.resolve(targets=targets, native_models=['sol'])['items'][0]['executor'],
                         'delegate_task')

    def test_inherit_omits_target_and_budget_override(self):
        result = self.resolve(block('inherit-parent'))['items'][0]
        self.assertEqual(result['target'], {})

    def test_same_model_effort_override_preserves_other_parent_options(self):
        caps = catalog()
        caps['inheritedOptions'].append({'id': 'serviceTier', 'value': 'default'})
        caps['providers'][0]['models'][0]['options'].append({'id': 'serviceTier', 'values': ['default', 'priority']})
        for value in ('sol（high）', 'inherit-parent（high）'):
            item = self.resolve(block(value), caps=caps)['items'][0]
            self.assertEqual(item['target']['options'], {'reasoningEffort': 'high', 'serviceTier': 'default'})

    def test_malformed_capability_is_a_configuration_error(self):
        caps = catalog()
        caps['providers'][0]['models'][0]['options'] = None
        with self.assertRaises(t3.ConfigError):
            self.resolve(caps=caps)

    def test_special_model_id_is_not_split(self):
        result = self.resolve(targets=config('["workbuddy","model"]', {}))['items'][0]
        self.assertEqual(result['target']['model'], '["workbuddy","model"]')
        self.assertEqual(result['target']['options'], {})

    def test_conflicting_explicit_efforts_rejected(self):
        with self.assertRaisesRegex(t3.ConfigError, '冲突'):
            self.resolve(block('t3:review（high）'))

    def test_unavailable_or_invalid_target_is_rejected(self):
        for mutate in (
            lambda c: c['targets']['review'].update(model='unknown'),
            lambda c: c['targets']['review'].update(options={'reasoningEffort': 'medium'}),
            lambda c: c.update(schemaVersion=2),
            lambda c: c['targets']['review'].update(options={'effort': 1}),
            lambda c: c['targets']['review'].update(runtimeMode='full-access'),
        ):
            data = config()
            mutate(data)
            with self.subTest(data=data), self.assertRaises(t3.ConfigError):
                self.resolve(targets=data)

    def test_disabled_provider_and_cross_provider_denial(self):
        for key in ('canRunChildTask', 'canRunCrossProviderChildTask'):
            caps = catalog()
            caps['providers'][1][key] = False
            with self.subTest(key=key), self.assertRaises(t3.ConfigError):
                self.resolve(caps=caps)

    def test_duplicate_json_keys_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'data.json'
            path.write_text('{"schemaVersion":1,"schemaVersion":2}', encoding='utf-8')
            with self.assertRaisesRegex(t3.ConfigError, '重复键'):
                t3.load_json(path)

    def test_unsupported_explicit_effort_is_not_downgraded(self):
        with self.assertRaises(t3.ConfigError):
            self.resolve(block('sol（max）'))

    def test_legacy_resolver_refuses_alias_as_model(self):
        with self.assertRaisesRegex(models.SModelsError, 't3_targets'):
            models.resolve_role(models.render_block('省', models.render_rows('省', 't3:review', 't3:review')), '修 bug')

    def test_six_roles_and_legacy_callers(self):
        self.assertEqual(len(t3.role_config(block())['rows']), 6)
        self.assertEqual(self.resolve()['role'], '开发实现')

    def test_legacy_config_remains_readable_but_conflicting_merge_fails(self):
        text = '\n'.join([models.START, '# 预算: 省（medium）',
                          *(f'{key}: {"plain" if key == "最难的任务" else "sol"}'
                            for key, _, _ in models.LEGACY_ROLES), models.END])
        self.assertEqual(t3.resolve(text, '修 bug', config(), catalog())['items'][0]['target']['model'], 'sol')
        with self.assertRaisesRegex(t3.ConfigError, '冲突'):
            t3.resolve(text, '专项攻坚', config(), catalog())

    def test_six_role_review_budget_is_enforced(self):
        rows = {role: 'sol' for role in t3.SIX_ROLES}
        rows['独立评审'] = 'sol, sol'
        with self.assertRaises(t3.ConfigError):
            t3.render_block('省', rows)

    def test_legacy_single_reflect_tooling_remains_single_under_large_budget(self):
        text = '\n'.join([models.START, '# 预算: 大（xhigh）',
                          '反思的工具视角: sol（medium）', models.END])
        result = t3.resolve(text, 'reflect tooling', config(), catalog())
        self.assertEqual(len(result['items']), 1)
        self.assertEqual(result['items'][0]['target']['model'], 'sol')

    def test_six_role_large_budget_allows_two_reviewers(self):
        rows = {role: 'sol' for role in t3.SIX_ROLES}
        rows['独立评审'] = 'sol, sol'
        text = t3.render_block('大', rows)
        self.assertEqual(t3.role_config(text)['rows']['独立评审'], 'sol, sol')

    def test_high_two_provider_review_aliases_configure_and_resolve(self):
        rows = {role: 't3:review' for role in t3.SIX_ROLES}
        rows['独立评审'] = 't3:review, t3:review2'
        targets = config()
        targets['targets']['review2'] = {'providerInstanceId': 'codex', 'model': 'sol',
                                         'options': {'reasoningEffort': 'medium'}}
        text = t3.render_block('高', rows)
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory).resolve()
            rules = project / 'AGENTS.md'
            t3.configure(rules, project, text, targets, catalog(), apply=True)
            result = t3.resolve(rules.read_text(encoding='utf-8'), '独立评审',
                                t3.load_json(project / t3.TARGET_FILE), catalog())
        self.assertEqual([item['target']['providerInstanceId'] for item in result['items']],
                         ['claude', 'codex'])
        self.assertEqual([item['target']['options'] for item in result['items']],
                         [{'effort': 'medium'}, {'reasoningEffort': 'medium'}])

    def test_mixed_duplicate_missing_and_malformed_six_roles_rejected(self):
        for text in (block().replace('开发实现:', '修 bug:'),
                     block().replace('开发实现:', '方案设计:'),
                     block().replace('开发实现: t3:review\n', ''),
                     block().replace('省（medium）', '省')):
            with self.subTest(text=text), self.assertRaises(t3.ConfigError):
                t3.role_config(text)


class ConfigureTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.rules = self.root / 'AGENTS.md'
        self.rules.write_bytes(b'keep me\r\n')

    def configure(self, apply=False):
        return t3.configure(self.rules, self.root, block(), config(), catalog(), apply)

    def test_preview_then_apply_is_idempotent_and_preserves_other_text(self):
        preview = self.configure()
        self.assertIn('keep me', preview['rules'])
        self.assertFalse((self.root / 's-atlas.t3.json').exists())
        self.assertEqual(self.rules.read_bytes(), b'keep me\r\n')
        self.configure(True)
        self.assertTrue(self.rules.read_bytes().startswith(b'keep me\r\n'))
        self.assertEqual(self.configure(True)['changed'], False)

    def test_second_replace_failure_rolls_back(self):
        original = t3.atomic_write
        def fail_rules(path, data):
            if path == self.rules and b't3:review' in data:
                raise OSError('simulated disk failure')
            original(path, data)
        with patch.object(t3, 'atomic_write', side_effect=fail_rules):
            with self.assertRaises(OSError):
                self.configure(True)
        self.assertEqual(self.rules.read_bytes(), b'keep me\r\n')
        self.assertFalse((self.root / 's-atlas.t3.json').exists())

    def test_backup_dangling_symlink_does_not_write_outside_project(self):
        outside = self.root / 'outside'
        backup = self.rules.with_name(self.rules.name + '.s-models.bak')
        try:
            backup.symlink_to(outside)
        except OSError as exc:
            self.skipTest(str(exc))
        with self.assertRaises((t3.ConfigError, OSError)):
            self.configure(True)
        self.assertFalse(outside.exists())
        self.assertEqual(self.rules.read_bytes(), b'keep me\r\n')
        self.assertFalse((self.root / t3.JOURNAL).exists())

    def test_recover_retains_journal_if_restored_file_changes_later(self):
        target = self.root / t3.TARGET_FILE
        target.write_bytes(b'new')
        entries = [
            {'path': str(target.resolve()), 'before': t3.encode(b'old'), 'after': t3.encode(b'new')},
            {'path': str(self.rules.resolve()), 'before': t3.encode(b'keep me\r\n'), 'after': t3.encode(b'new rules')},
        ]
        journal = self.root / t3.JOURNAL
        journal.write_text(json.dumps({'schemaVersion': 1, 'entries': entries}))
        original = t3.atomic_write
        def save_restored_file(path, data):
            original(path, data)
            if path == self.rules:
                target.write_bytes(b'external edit')
        with patch.object(t3, 'atomic_write', side_effect=save_restored_file):
            with self.assertRaisesRegex(t3.ConfigError, '回读'):
                t3.recover(self.root)
        self.assertEqual(target.read_bytes(), b'external edit')
        self.assertTrue(journal.exists())

    def test_recover_preserves_edit_between_restoring_files(self):
        target = self.root / t3.TARGET_FILE
        target.write_bytes(b'new')
        entries = [
            {'path': str(target.resolve()), 'before': t3.encode(b'old'), 'after': t3.encode(b'new')},
            {'path': str(self.rules.resolve()), 'before': t3.encode(b'keep me\r\n'), 'after': t3.encode(b'new rules')},
        ]
        journal = self.root / t3.JOURNAL
        journal.write_text(json.dumps({'schemaVersion': 1, 'entries': entries}))
        original = t3.atomic_write
        def external_save(path, data):
            original(path, data)
            if path == target:
                self.rules.write_bytes(b'external edit')
        with patch.object(t3, 'atomic_write', side_effect=external_save):
            with self.assertRaisesRegex(t3.ConfigError, '外部修改'):
                t3.recover(self.root)
        self.assertEqual(self.rules.read_bytes(), b'external edit')
        self.assertTrue(journal.exists())

    def test_recover_refuses_to_overwrite_third_party_edits(self):
        with patch.object(t3, 'recover', side_effect=OSError('crash')):
            with patch.object(t3, 'atomic_write', side_effect=OSError('disk')):
                with self.assertRaises(OSError):
                    self.configure(True)
        self.rules.write_text('external edit', encoding='utf-8')
        with self.assertRaisesRegex(t3.ConfigError, '外部修改'):
            t3.recover(self.root)
        self.assertEqual(self.rules.read_text(), 'external edit')

    def test_recover_rejects_path_outside_project(self):
        outside = self.root.parent / 'unrelated.md'
        entry = {'path': str(outside), 'before': None, 'after': t3.encode(b'bad')}
        (self.root / t3.JOURNAL).write_text(json.dumps({'schemaVersion': 1, 'entries': [entry]}))
        with self.assertRaisesRegex(t3.ConfigError, '范围外'):
            t3.recover(self.root)

    def test_recover_restores_interrupted_first_file_write(self):
        target = self.root / t3.TARGET_FILE
        target.write_bytes(b'new targets')
        entries = [
            {'path': str(target), 'before': None, 'after': t3.encode(b'new targets')},
            {'path': str(self.rules), 'before': t3.encode(b'keep me\r\n'), 'after': t3.encode(b'new rules')},
        ]
        (self.root / t3.JOURNAL).write_text(json.dumps({'schemaVersion': 1, 'entries': entries}))
        self.assertEqual(t3.recover(self.root)['status'], 'recovered')
        self.assertFalse(target.exists())
        self.assertEqual(self.rules.read_bytes(), b'keep me\r\n')

    def test_cli_preview_and_apply(self):
        from contextlib import redirect_stdout, redirect_stderr
        from io import StringIO
        candidate = self.root / 'candidate.md'
        candidate.write_text(block(), encoding='utf-8')
        targets = self.root / 'candidate.json'
        targets.write_text(json.dumps(config()), encoding='utf-8')
        caps = self.root / 'capabilities.json'
        caps.write_text(json.dumps(catalog()), encoding='utf-8')
        args = ['configure', '--project', str(self.root), '--rules', str(self.rules),
                '--capabilities', str(caps), '--block', str(candidate), '--targets', str(targets)]
        for suffix, applied in (([], False), (['--apply'], True)):
            output = StringIO()
            with redirect_stdout(output), redirect_stderr(StringIO()):
                self.assertEqual(t3.main(args + suffix), 0)
            self.assertEqual(json.loads(output.getvalue())['applied'], applied)
        with redirect_stdout(StringIO()):
            self.assertEqual(t3.main(['check', '--project', str(self.root), '--rules', str(self.rules),
                                     '--capabilities', str(caps)]), 0)

    def test_candidate_cannot_inject_rules_outside_block(self):
        with self.assertRaisesRegex(t3.ConfigError, '只能包含'):
            t3.configure(self.rules, self.root, 'extra rule\n' + block(), config(), catalog(), True)
        self.assertEqual(self.rules.read_bytes(), b'keep me\r\n')


if __name__ == '__main__':
    unittest.main()
