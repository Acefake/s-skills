"""T3 配置的用户可见行为与失败恢复。"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'plugins/wukong/skills/setup-s-models/scripts'
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

    def test_cli_render_outputs_complete_six_roles(self):
        from contextlib import redirect_stdout
        from io import StringIO
        args = ['render', '--budget', '省']
        for role in t3.SIX_ROLES:
            args += ['--set', role + '=t3:review']
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(t3.main(args), 0)
        self.assertEqual(set(t3.role_config(json.loads(output.getvalue())['block'])['rows']), set(t3.SIX_ROLES))

    def test_cli_render_rejects_missing_sets_and_partial_roles(self):
        from contextlib import redirect_stdout, redirect_stderr
        from io import StringIO
        with redirect_stderr(StringIO()), self.assertRaises(SystemExit) as caught:
            t3.main(['render', '--budget', '省'])
        self.assertEqual(caught.exception.code, 2)
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            self.assertEqual(t3.main(['render', '--budget', '省', '--set', '开发实现=t3:review']), 1)

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


class ScopedConfigTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.user = self.root / 'user'
        self.project = self.root / 'project'
        self.project.mkdir()
        self.candidate = self.root / 'candidate.md'
        self.candidate.write_text(block(), encoding='utf-8')
        self.targets = self.root / 'candidate.json'
        self.targets.write_text(json.dumps(config()), encoding='utf-8')
        self.caps = self.root / 'caps.json'
        self.caps.write_text(json.dumps(catalog()), encoding='utf-8')

    def cli(self, command, *extra, ok=True, host='codex'):
        from contextlib import redirect_stdout, redirect_stderr
        from io import StringIO
        output, error = StringIO(), StringIO()
        args = [command, '--global-dir', str(self.user), *(['--host', host] if host else []), *extra]
        if command != 'recover':
            args += ['--capabilities', str(self.caps)]
        with redirect_stdout(output), redirect_stderr(error):
            code = t3.main(args)
        self.assertEqual(code, 0 if ok else 1, error.getvalue())
        return json.loads(output.getvalue() if ok else error.getvalue())

    def install(self, apply=True):
        return self.cli('configure', '--scope', 'user', '--block', str(self.candidate),
                        '--targets', str(self.targets), *(['--apply'] if apply else []))

    def test_global_preview_apply_and_cross_project_inheritance(self):
        self.assertTrue(self.install(False)['changed'])
        self.assertFalse(self.user.exists())
        self.install()
        self.assertFalse(self.install()['changed'])
        for name in ('project', 'another'):
            project = self.root / name
            project.mkdir(exist_ok=True)
            (project / 'AGENTS.md').write_text('unrelated instructions', encoding='utf-8')
            result = self.cli('resolve', '--project', str(project), '--role', '修 bug')
            self.assertEqual(result['scope'], 'user')
            self.assertEqual(result['items'][0]['target']['model'], 'sonnet')
            self.assertEqual(Path(result['targetsPath']), self.user / t3.TARGET_FILE)

    def test_project_aliases_override_and_never_borrow_global_alias(self):
        self.install()
        (self.project / 'AGENTS.md').write_text(block(), encoding='utf-8')
        targets = {'schemaVersion': 1, 'targets': {'review': {
            'providerInstanceId': 'codex', 'model': 'sol',
            'options': {'reasoningEffort': 'medium'}}}}
        (self.project / t3.TARGET_FILE).write_text(json.dumps(targets), encoding='utf-8')
        result = self.cli('resolve', '--project', str(self.project), '--role', '修 bug')
        self.assertEqual(result['scope'], 'project')
        self.assertEqual(result['items'][0]['target']['model'], 'sol')
        (self.project / t3.TARGET_FILE).unlink()
        self.assertIn('别名不存在', self.cli('resolve', '--project', str(self.project),
                                         '--role', '修 bug', ok=False)['error'])

    def test_broken_project_and_pending_global_transaction_do_not_fall_back(self):
        self.install()
        rules = self.project / 'AGENTS.md'
        rules.write_text(block().replace('开发实现: t3:review\n', ''), encoding='utf-8')
        self.cli('check', '--project', str(self.project), ok=False)
        rules.unlink()
        (self.user / t3.JOURNAL).write_text('{}', encoding='utf-8')
        self.assertIn('事务', self.cli('check', '--project', str(self.project), ok=False)['error'])

    def test_user_recovery_restores_interrupted_write(self):
        self.install()
        rules = self.user / 'AGENTS.md'
        before = rules.read_bytes()
        rules.write_bytes(b'interrupted')
        entry = {'path': str(rules), 'before': t3.encode(before), 'after': t3.encode(b'interrupted')}
        (self.user / t3.JOURNAL).write_text(json.dumps({'schemaVersion': 1, 'entries': [entry]}))
        self.assertEqual(self.cli('recover', '--scope', 'user')['status'], 'recovered')
        self.assertEqual(rules.read_bytes(), before)

    def test_invalid_global_target_never_creates_directory(self):
        self.targets.write_text(json.dumps(config('unknown')), encoding='utf-8')
        self.cli('configure', '--scope', 'user', '--block', str(self.candidate),
                 '--targets', str(self.targets), '--apply', ok=False)
        self.assertFalse(self.user.exists())

    def test_user_write_failure_rolls_back_both_files(self):
        original = t3.atomic_write
        def fail_rules(path, data):
            if path == self.user / 'AGENTS.md':
                raise OSError('simulated user config failure')
            original(path, data)
        with patch.object(t3, 'atomic_write', side_effect=fail_rules):
            self.cli('configure', '--scope', 'user', '--block', str(self.candidate),
                     '--targets', str(self.targets), '--apply', ok=False)
        self.assertEqual(list(self.user.iterdir()), [])

    def test_project_does_not_read_broken_global_and_rejects_partial_marker(self):
        self.install()
        (self.user / t3.TARGET_FILE).write_text('invalid json', encoding='utf-8')
        rules = self.project / 'AGENTS.md'
        rules.write_text(block(), encoding='utf-8')
        (self.project / t3.TARGET_FILE).write_text(json.dumps(config()), encoding='utf-8')
        self.assertEqual(self.cli('check', '--project', str(self.project))['scope'], 'project')
        rules.write_text(block().replace(models.END, ''), encoding='utf-8')
        self.cli('check', '--project', str(self.project), ok=False)

    def test_each_host_uses_its_own_rule_path_and_format(self):
        for host, relative in (('claude-code', 'rules/s-models.md'),
                               ('workbuddy', 'rules/s-models.md'),
                               ('dsh', 'AGENTS.md'), ('hermes', 'SOUL.md')):
            with self.subTest(host=host):
                self.user = self.root / host
                result = self.cli('configure', '--host', host, '--scope', 'user',
                                  '--block', str(self.candidate), '--targets', str(self.targets))
                self.assertFalse(self.user.exists())
                self.assertEqual(Path(result['rulesPath']), self.user / relative)
                self.cli('configure', '--host', host, '--scope', 'user', '--block', str(self.candidate),
                         '--targets', str(self.targets), '--apply')
                text = (self.user / relative).read_text(encoding='utf-8')
                self.assertEqual(text, block())
                result = self.cli('resolve', '--host', host, '--project', str(self.project), '--role', '修 bug')
                self.assertEqual(Path(result['rulesPath']), self.user / relative)

    def test_codex_override_preserves_bom_crlf_and_other_instructions(self):
        self.user.mkdir()
        rules = self.user / 'AGENTS.override.md'
        original = models.BOM + b'keep instructions\r\n'
        rules.write_bytes(original)
        self.install()
        self.assertEqual(self.cli('check', '--scope', 'user')['rulesPath'], str(rules))
        self.assertTrue(rules.read_bytes().startswith(original))
        self.assertFalse((self.user / 'AGENTS.md').exists())

    def test_cursor_adds_mdc_frontmatter_once_and_preserves_existing_fields(self):
        result = self.cli('configure', '--host', 'cursor', '--scope', 'user',
                          '--block', str(self.candidate), '--targets', str(self.targets))
        self.assertIn('alwaysApply: true', result['rules'])
        self.assertFalse(self.user.exists())
        self.cli('configure', '--host', 'cursor', '--scope', 'user',
                 '--block', str(self.candidate), '--targets', str(self.targets), '--apply')
        rules = self.user / 'rules' / 's-models.mdc'
        text = rules.read_text(encoding='utf-8').replace('alwaysApply: true', 'alwaysApply: true\ncustom: keep')
        rules.write_text(text, encoding='utf-8')
        result = self.cli('configure', '--host', 'cursor', '--scope', 'user',
                          '--block', str(self.candidate), '--targets', str(self.targets), '--apply')
        self.assertFalse(result['changed'])
        self.assertEqual(rules.read_text(encoding='utf-8'), text)

    def test_host_env_directories_and_missing_host(self):
        for host, variable in (('codex', 'CODEX_HOME'), ('claude-code', 'CLAUDE_CONFIG_DIR'),
                               ('dsh', 'DSH_HOME'), ('hermes', 'HERMES_HOME')):
            with self.subTest(host=host), patch.dict(t3.os.environ, {variable: str(self.user)}):
                self.assertEqual(t3.t3_hosts.global_root(host), self.user)
        with self.assertRaisesRegex(ValueError, '--host'):
            t3.t3_hosts.global_root(None, self.user)

    def test_nested_host_rule_recovery_stays_in_selected_host_paths(self):
        self.cli('configure', '--host', 'claude-code', '--scope', 'user',
                 '--block', str(self.candidate), '--targets', str(self.targets), '--apply')
        rules = self.user / 'rules' / 's-models.md'
        before = rules.read_bytes()
        rules.write_bytes(b'interrupted')
        entry = {'path': str(rules), 'before': t3.encode(before), 'after': t3.encode(b'interrupted')}
        journal = self.user / t3.JOURNAL
        journal.write_text(json.dumps({'schemaVersion': 1, 'entries': [entry]}))
        self.cli('recover', '--host', 'claude-code', '--scope', 'user')
        self.assertEqual(rules.read_bytes(), before)

    def test_missing_project_is_rejected_for_all_commands_without_creating_it(self):
        missing = self.root / 'typo'
        for command, extra in (('configure', ('--block', str(self.candidate), '--targets', str(self.targets), '--apply')),
                               ('check', ()), ('resolve', ('--role', '修 bug')), ('recover', ())):
            with self.subTest(command=command):
                result = self.cli(command, '--project', str(missing), *extra, ok=False)
                self.assertIn('项目目录不存在', result['error'])
                self.assertFalse(missing.exists())

    def test_project_codex_override_is_written_resolved_and_recovered(self):
        ignored = self.project / 'AGENTS.md'
        ignored.write_text('ignored instructions', encoding='utf-8')
        rules = self.project / 'AGENTS.override.md'
        rules.write_text('active instructions', encoding='utf-8')
        self.cli('configure', '--project', str(self.project), '--block', str(self.candidate),
                 '--targets', str(self.targets), '--apply')
        result = self.cli('resolve', '--project', str(self.project), '--role', '修 bug')
        self.assertEqual(Path(result['rulesPath']), rules)
        self.assertEqual(ignored.read_text(encoding='utf-8'), 'ignored instructions')
        before = rules.read_bytes()
        rules.write_bytes(b'interrupted')
        entry = {'path': str(rules), 'before': t3.encode(before), 'after': t3.encode(b'interrupted')}
        (self.project / t3.JOURNAL).write_text(json.dumps({'schemaVersion': 1, 'entries': [entry]}))
        self.cli('recover', '--project', str(self.project))
        self.assertEqual(rules.read_bytes(), before)

    def test_codex_empty_project_override_falls_back_to_agents(self):
        rules = self.project / 'AGENTS.override.md'
        rules.write_text('  \n', encoding='utf-8')
        self.cli('configure', '--project', str(self.project), '--block', str(self.candidate),
                 '--targets', str(self.targets), '--apply')
        self.assertEqual(Path(self.cli('check', '--project', str(self.project))['rulesPath']),
                         self.project / 'AGENTS.md')
        self.assertEqual(rules.read_text(encoding='utf-8'), '  \n')

    def test_nonempty_project_override_requires_host_for_all_commands(self):
        override = self.project / 'AGENTS.override.md'
        override.write_text('active rules', encoding='utf-8')
        for command, extra in (('configure', ('--block', str(self.candidate), '--targets', str(self.targets), '--apply')),
                               ('check', ()), ('resolve', ('--role', '修 bug')), ('recover', ())):
            with self.subTest(command=command):
                result = self.cli(command, '--project', str(self.project), *extra, ok=False, host=None)
                self.assertIn('--host', result['error'])
                self.assertEqual(override.read_text(encoding='utf-8'), 'active rules')
                self.assertFalse((self.project / 'AGENTS.md').exists())
                self.assertFalse((self.project / t3.TARGET_FILE).exists())

    def test_orphan_project_target_is_reported_without_parsing_or_fallback(self):
        self.install()
        (self.project / t3.TARGET_FILE).write_text('invalid json', encoding='utf-8')
        result = self.cli('check', '--project', str(self.project), ok=False)
        self.assertIn('孤立目标文件', result['error'])

    def test_cursor_whitespace_rule_gets_frontmatter_and_keeps_bom(self):
        rules = self.user / 'rules' / 's-models.mdc'
        rules.parent.mkdir(parents=True)
        rules.write_bytes(models.BOM + b' \r\n')
        self.cli('configure', '--host', 'cursor', '--scope', 'user', '--block', str(self.candidate),
                 '--targets', str(self.targets), '--apply')
        raw = rules.read_bytes()
        self.assertTrue(raw.startswith(models.BOM + b'---\r\n'))
        self.assertIn(b'alwaysApply: true\r\n', raw)

    def test_project_target_symlinks_never_read_or_fall_back(self):
        self.install()
        outside = self.root / 'outside.json'
        outside.write_text(json.dumps(config()), encoding='utf-8')
        for name in (t3.TARGET_FILE, t3.PREVIOUS_TARGET_FILE, t3.LEGACY_TARGET_FILE):
            link = self.project / name
            for destination in (outside, self.root / 'missing.json'):
                with self.subTest(name=name, dangling=not destination.exists()):
                    try:
                        link.symlink_to(destination)
                    except OSError as exc:
                        self.skipTest(str(exc))
                    try:
                        for rule_text in ('', block()):
                            (self.project / 'AGENTS.md').write_text(rule_text, encoding='utf-8')
                            for command, extra in (('check', ()), ('resolve', ('--role', '修 bug'))):
                                result = self.cli(command, '--project', str(self.project), *extra, ok=False)
                                self.assertIn('符号链接', result['error'])
                    finally:
                        link.unlink()

    def test_user_target_symlink_cannot_borrow_another_scope(self):
        self.install()
        target = self.user / t3.TARGET_FILE
        outside = self.root / 'outside.json'
        outside.write_bytes(target.read_bytes())
        target.unlink()
        try:
            target.symlink_to(outside)
        except OSError as exc:
            self.skipTest(str(exc))
        self.assertIn('符号链接', self.cli('check', '--scope', 'user', ok=False)['error'])

    def test_default_host_roots_use_the_home_directory(self):
        with patch.dict(t3.os.environ, {}, clear=True), patch.object(Path, 'home', return_value=self.root):
            for host, directory in (('codex', '.codex'), ('claude-code', '.claude'), ('cursor', '.cursor'),
                                     ('workbuddy', '.codebuddy'), ('dsh', '.dsh'), ('hermes', '.hermes')):
                self.assertEqual(t3.t3_hosts.global_root(host), self.root / directory)

    def test_user_root_file_is_rejected_during_preview(self):
        self.user.write_text('keep file', encoding='utf-8')
        result = self.cli('configure', '--scope', 'user', '--block', str(self.candidate),
                          '--targets', str(self.targets), ok=False)
        self.assertIn('不是目录', result['error'])
        self.assertEqual(self.user.read_text(encoding='utf-8'), 'keep file')

    def test_named_hermes_profile_is_used_for_write_read_and_recovery(self):
        self.user = self.root / 'hermes' / 'profiles' / 'chosen'
        self.cli('configure', '--scope', 'user', '--host', 'hermes', '--block', str(self.candidate),
                 '--targets', str(self.targets), '--apply')
        result = self.cli('resolve', '--host', 'hermes', '--project', str(self.project), '--role', '修 bug')
        self.assertEqual(Path(result['rulesPath']), self.user / 'SOUL.md')
        self.assertEqual(self.cli('check', '--host', 'hermes', '--scope', 'user')['status'], 'ok')
        self.assertEqual(self.cli('recover', '--host', 'hermes', '--scope', 'user')['status'],
                         'no-pending-transaction')
        self.assertFalse((self.root / 'hermes' / 'SOUL.md').exists())

    def test_partial_legacy_check_is_rejected(self):
        (self.project / 'AGENTS.md').write_text('\n'.join([
            models.START, '# 预算: 省（medium）', '修 bug: sol', models.END]), encoding='utf-8')
        for command, extra in (('check', ()), ('resolve', ('--role', '修 bug'))):
            result = self.cli(command, '--project', str(self.project), *extra, ok=False)
            self.assertIn('六角色', result['error'])

    def test_complete_legacy_file_still_passes_check_and_resolve(self):
        text = '\n'.join([models.START, '# 预算: 省（medium）',
                          *(key + ': sol' for key, _, _ in models.LEGACY_ROLES), models.END])
        (self.project / 'AGENTS.md').write_text(text, encoding='utf-8')
        self.assertEqual(self.cli('check', '--project', str(self.project))['status'], 'ok')
        result = self.cli('resolve', '--project', str(self.project), '--role', '方案设计')
        self.assertEqual(result['items'][0]['target']['model'], 'sol')

    def test_rule_symlink_reports_explicit_error(self):
        destination = self.project / 'CLAUDE.md'
        destination.write_text(block(), encoding='utf-8')
        try:
            (self.project / 'AGENTS.md').symlink_to(destination)
        except OSError as exc:
            self.skipTest(str(exc))
        self.assertIn('符号链接', self.cli('check', '--project', str(self.project), ok=False)['error'])


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
        self.assertFalse((self.root / 'wukong.t3.json').exists())
        self.assertEqual(self.rules.read_bytes(), b'keep me\r\n')
        self.configure(True)
        self.assertTrue(self.rules.read_bytes().startswith(b'keep me\r\n'))
        self.assertEqual(self.configure(True)['changed'], False)

    def test_journal_fsync_failure_leaves_no_pending_transaction_or_data_changes(self):
        with patch.object(t3.os, 'fsync', side_effect=OSError('journal fsync failed')):
            with self.assertRaises(OSError):
                self.configure(True)
        self.assertFalse((self.root / t3.JOURNAL).exists())
        self.assertFalse((self.root / t3.TARGET_FILE).exists())
        self.assertEqual(self.rules.read_bytes(), b'keep me\r\n')
        self.configure(True)

    def test_existing_journal_is_never_deleted_by_exclusive_write_failure(self):
        journal = self.root / t3.JOURNAL
        journal.write_bytes(b'other writer')
        with self.assertRaises(FileExistsError):
            t3.write_pair(self.root, [])
        self.assertEqual(journal.read_bytes(), b'other writer')

    def test_failed_backup_is_removed_and_existing_data_is_preserved(self):
        backup = self.rules.with_name(self.rules.name + '.s-models.bak')
        original = t3.os.fsync
        failed = False
        def fail_backup_once(fd):
            nonlocal failed
            if backup.exists() and not failed:
                failed = True
                raise OSError('backup fsync failed')
            original(fd)
        with patch.object(t3.os, 'fsync', side_effect=fail_backup_once):
            with self.assertRaises(OSError):
                self.configure(True)
        self.assertTrue(failed)
        self.assertFalse(backup.exists())
        self.assertFalse((self.root / t3.TARGET_FILE).exists())
        self.assertFalse((self.root / t3.JOURNAL).exists())
        self.assertEqual(self.rules.read_bytes(), b'keep me\r\n')

    def test_legacy_target_name_is_read_and_not_overwritten(self):
        for name in ('s-atlas.t3.json', 's-wukong.t3.json'):
            with self.subTest(name=name):
                legacy = self.root / name
                original = json.dumps(config())
                legacy.write_text(original, encoding='utf-8')
                self.assertEqual(t3.existing_or_current(self.root, t3.TARGET_FILE, t3.LEGACY_TARGET_FILE), legacy)
                with self.assertRaises(t3.ConfigError) as caught:
                    self.configure()
                self.assertIn(name, str(caught.exception))
                self.assertFalse((self.root / 'wukong.t3.json').exists())
                self.assertEqual(legacy.read_text(encoding='utf-8'), original)
                legacy.unlink()

    def test_previous_plugin_transaction_blocks_new_write(self):
        journal = self.root / '.s-wukong-t3.transaction.json'
        journal.write_text('{}', encoding='utf-8')
        with self.assertRaisesRegex(t3.ConfigError, 'recover'):
            self.configure(True)
        self.assertEqual(self.rules.read_bytes(), b'keep me\r\n')
        self.assertFalse((self.root / 'wukong.t3.json').exists())

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
        self.assertFalse((self.root / 'wukong.t3.json').exists())

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
