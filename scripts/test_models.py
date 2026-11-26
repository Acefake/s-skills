"""wukong-init 的子代理模型块：只动自己的标记段，可重复执行。"""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'plugins/wukong/skills/wukong-init/scripts'
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location('wukong_models', SCRIPTS / 'models.py')
models = importlib.util.module_from_spec(spec)
spec.loader.exec_module(models)
gi = models.sys.modules['global_instructions']

CHOICES = {'检索': 'haiku', '规划': 'opus', '审查': 'opus', '测试': 'sonnet'}


class ModelBlockTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.home = Path(tmp.name)
        self.path = self.home / '.claude/CLAUDE.md'
        self.path.parent.mkdir(parents=True)

    def sync(self, choices=CHOICES, apply=True):
        return models.sync_models('claude-code', choices, home=self.home, apply=apply)

    def test_render_requires_all_four_roles(self):
        with self.assertRaises(models.ConfigurationError):
            models.render('claude-code', {'检索': 'haiku'})
        with self.assertRaises(models.ConfigurationError):
            models.render('claude-code', {**CHOICES, '提交': 'haiku'})
        with self.assertRaises(models.ConfigurationError):
            models.render('claude-code', {**CHOICES, '审查': 'a\nb'})

    def test_effort_is_optional_and_validated(self):
        self.assertEqual(models.split_value('opus（xhigh）'), ('opus', 'xhigh'))
        self.assertEqual(models.split_value('opus(high)'), ('opus', 'high'))
        self.assertEqual(models.split_value('继承（high）'), ('继承', 'high'))
        self.assertEqual(models.split_value('sonnet'), ('sonnet', None))
        for bad in ('opus（turbo）', 'opus（high', 'a b', ''):
            with self.assertRaises(models.ConfigurationError, msg=bad):
                models.split_value(bad)
        body = models.render('claude-code', {**CHOICES, '审查': 'opus(xhigh)'})
        self.assertIn('审查: opus（xhigh）', body)

    def test_resolve_fills_role_default_efforts(self):
        resolved = models.resolve({**CHOICES, '审查': 'opus（xhigh）', '测试': '继承'})
        self.assertEqual(resolved['检索'], {'model': 'haiku', 'effort': 'medium'})
        self.assertEqual(resolved['规划'], {'model': 'opus', 'effort': 'high'})
        self.assertEqual(resolved['审查'], {'model': 'opus', 'effort': 'xhigh'})
        self.assertEqual(resolved['测试'], {'model': None, 'effort': 'medium'})
        self.assertEqual(models.resolve(None)['审查'], {'model': None, 'effort': 'high'})

    def test_check_without_apply_writes_nothing(self):
        result = self.sync(apply=False)
        self.assertEqual(result['status'], 'missing')
        self.assertFalse(self.path.exists())

    def test_apply_is_idempotent_and_readable(self):
        self.assertTrue(self.sync()['changed'])
        self.assertFalse(self.sync()['changed'])
        self.assertEqual(models.read_models('claude-code', home=self.home), CHOICES)
        changed = {**CHOICES, '测试': models.INHERIT}
        self.assertEqual(self.sync(changed, apply=False)['status'], 'outdated')
        self.sync(changed)
        self.assertEqual(models.read_models('claude-code', home=self.home)['测试'], '继承')

    def test_block_sits_after_library_block_and_keeps_other_content(self):
        library = f'{gi.START}\nrules\n{gi.END}'
        personal = f'{gi.PERSONAL_START}\nme\n{gi.PERSONAL_END}'
        self.path.write_text(f'mine\n\n{library}\n\n{personal}\n', encoding='utf-8')
        self.sync()
        text = self.path.read_text(encoding='utf-8')
        self.assertTrue(text.startswith('mine\n'))
        self.assertLess(text.index(gi.END), text.index(models.MODELS_START))
        self.assertLess(text.index(models.MODELS_END), text.index(gi.PERSONAL_START))
        self.assertTrue(self.path.with_name('CLAUDE.md.wukong.bak').exists())

    def test_library_update_leaves_model_block_alone(self):
        self.path.write_text(f'{gi.START}\nold rules\n{gi.END}\n', encoding='utf-8')
        self.sync()
        before = models.read_models('claude-code', home=self.home)
        gi.sync_global('claude-code', home=self.home, apply=True)
        self.assertEqual(models.read_models('claude-code', home=self.home), before)
        self.assertEqual(gi.sync_global('claude-code', home=self.home)['status'], 'configured')

    def test_retired_hosts_are_rejected(self):
        for host in ('cursor', 'workbuddy'):
            with self.subTest(host=host), self.assertRaises(ValueError):
                models.sync_models(host, CHOICES, home=self.home, apply=True)

    def test_cli_round_trip(self):
        command = [sys.executable, str(SCRIPTS / 'models.py'), '--host', 'claude-code', '--home', str(self.home)]
        sets = [arg for role, model in CHOICES.items() for arg in ('--set', f'{role}={model}')]
        first = subprocess.run(command + sets, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(first.returncode, 2, first.stdout + first.stderr)
        applied = subprocess.run(command + sets + ['--apply'], capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
        shown = subprocess.run(command + ['--show'], capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(shown.returncode, 0, shown.stdout + shown.stderr)
        self.assertEqual(json.loads(shown.stdout)['roles'], CHOICES)

    def test_show_reports_outdated_for_partial_or_empty_model_block(self):
        command = [sys.executable, str(SCRIPTS / 'models.py'), '--host', 'claude-code', '--home', str(self.home), '--show']
        # Partial block (missing 审查, 测试)
        self.path.write_text(f'{models.MODELS_START}\n## wukong 子代理模型\n检索: haiku\n规划: opus\n{models.MODELS_END}\n', encoding='utf-8')
        partial = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(partial.returncode, 2, partial.stdout + partial.stderr)
        data = json.loads(partial.stdout)
        self.assertEqual(data['status'], 'outdated')
        self.assertEqual(data['missing'], ['审查', '测试'])

        # Empty block (markers exist, 0 roles)
        self.path.write_text(f'{models.MODELS_START}\n## wukong 子代理模型\n{models.MODELS_END}\n', encoding='utf-8')
        empty = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(empty.returncode, 2, empty.stdout + empty.stderr)
        data_empty = json.loads(empty.stdout)
        self.assertEqual(data_empty['status'], 'outdated')
        self.assertEqual(data_empty['missing'], list(models.ROLES))

    def test_duplicate_set_role_is_rejected(self):
        command = [sys.executable, str(SCRIPTS / 'models.py'), '--host', 'claude-code', '--home', str(self.home)]
        sets = [arg for role, model in CHOICES.items() for arg in ('--set', f'{role}={model}')]
        dup = subprocess.run(command + sets + ['--set', '检索=sonnet'], capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(dup.returncode, 1, dup.stdout + dup.stderr)
        self.assertEqual(json.loads(dup.stdout)['status'], 'error')

    def test_codex_clears_stale_model_block_on_inactive_file(self):
        codex_dir = self.home / '.codex'
        codex_dir.mkdir()
        agents = codex_dir / 'AGENTS.md'
        override = codex_dir / 'AGENTS.override.md'
        # Initially write to AGENTS.md
        models.sync_models('codex', CHOICES, home=self.home, apply=True)
        self.assertIn(models.MODELS_START, agents.read_text(encoding='utf-8'))
        # Now create non-empty AGENTS.override.md; preview must not modify either file.
        override.write_text('custom override\n', encoding='utf-8')
        preview = models.sync_models('codex', CHOICES, home=self.home, apply=False)
        self.assertEqual(preview['status'], 'missing')
        self.assertIn(models.MODELS_START, agents.read_text(encoding='utf-8'))
        # Applying writes to override and removes the stale block from AGENTS.md.
        applied = models.sync_models('codex', CHOICES, home=self.home, apply=True)
        self.assertTrue(applied['changed'])
        self.assertIn(models.MODELS_START, override.read_text(encoding='utf-8'))
        self.assertNotIn(models.MODELS_START, agents.read_text(encoding='utf-8'))

    def test_preserves_crlf_and_utf8_bom_and_rejects_broken_markers(self):
        self.path.write_bytes(b'\xef\xbb\xbfkeep\r\n')
        self.sync()
        raw = self.path.read_bytes()
        self.assertTrue(raw.startswith(b'\xef\xbb\xbf'))
        self.assertIn(b'\r\n', raw)
        self.assertNotIn(b'\n', raw.replace(b'\r\n', b''))

        self.path.write_text(f'{models.MODELS_START}\n检索: haiku\n', encoding='utf-8')
        with self.assertRaises(models.ConfigurationError):
            models.read_models('claude-code', home=self.home)
        with self.assertRaises(models.ConfigurationError):
            self.sync()

    def test_symlink_is_rejected_on_read_and_sync(self):
        real = self.home / 'real.md'
        real.write_text('keep\n', encoding='utf-8')
        try:
            self.path.symlink_to(real)
        except OSError:
            self.skipTest('symlinks need extra rights on Windows')
        with self.assertRaises(models.ConfigurationError):
            models.read_models('claude-code', home=self.home)
        with self.assertRaises(models.ConfigurationError):
            self.sync()

    def test_antigravity_writes_and_reads_gemini_config_agents_md(self):
        agy_choices = {'检索': 'flash_lite', '规划': 'pro', '审查': 'pro', '测试': 'flash'}
        command = [sys.executable, str(SCRIPTS / 'models.py'), '--host', 'antigravity', '--home', str(self.home)]
        sets = [arg for role, model in agy_choices.items() for arg in ('--set', f'{role}={model}')]
        applied = subprocess.run(command + sets + ['--apply'], capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
        target = self.home / '.gemini/config/AGENTS.md'
        self.assertTrue(target.is_file())
        self.assertIn('宿主: antigravity', target.read_text(encoding='utf-8'))
        shown = subprocess.run(command + ['--show'], capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(shown.returncode, 0, shown.stdout + shown.stderr)
        shown_data = json.loads(shown.stdout)
        self.assertEqual(shown_data['roles'], agy_choices)
        self.assertEqual(Path(shown_data['target']), target)

    def test_antigravity_models_and_personal_blocks_coexist(self):
        agy_choices = {'检索': 'flash_lite', '规划': 'pro', '审查': 'pro', '测试': 'flash'}
        models.sync_models('antigravity', agy_choices, home=self.home, apply=True)
        gi.sync_personal('antigravity', '## 我的偏好\n- 回复精简', home=self.home, apply=True)
        target = self.home / '.gemini/config/AGENTS.md'
        text = target.read_text(encoding='utf-8')
        self.assertIn(models.MODELS_START, text)
        self.assertIn(gi.PERSONAL_START, text)
        self.assertEqual(models.read_models('antigravity', home=self.home), agy_choices)
        # Updating models preserves personal block, and removing personal preserves models.
        models.sync_models('antigravity', {**agy_choices, '测试': '继承'}, home=self.home, apply=True)
        self.assertIn('回复精简', target.read_text(encoding='utf-8'))
        gi.sync_personal('antigravity', '', home=self.home, apply=True)
        self.assertNotIn(gi.PERSONAL_START, target.read_text(encoding='utf-8'))
        self.assertEqual(models.read_models('antigravity', home=self.home)['测试'], '继承')

    def test_show_reports_error_on_invalid_model_value_and_includes_target(self):
        command = [sys.executable, str(SCRIPTS / 'models.py'), '--host', 'claude-code', '--home', str(self.home), '--show']
        missing = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(missing.returncode, 2)
        self.assertEqual(Path(json.loads(missing.stdout)['target']), self.path)

        self.path.write_text(f'{models.MODELS_START}\n## wukong 子代理模型\n检索: haiku\n规划: opus\n审查: opus（turbo）\n测试: sonnet\n{models.MODELS_END}\n', encoding='utf-8')
        bad = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(bad.returncode, 1, bad.stdout + bad.stderr)
        self.assertEqual(json.loads(bad.stdout)['status'], 'error')

    def test_codex_inactive_broken_marker_aborts_before_mutating_active_file(self):
        codex_dir = self.home / '.codex'
        codex_dir.mkdir()
        agents = codex_dir / 'AGENTS.md'
        override = codex_dir / 'AGENTS.override.md'
        agents.write_text(f'base\n{models.MODELS_START}\n检索: haiku\n', encoding='utf-8')
        original_override = 'custom override\n'
        override.write_text(original_override, encoding='utf-8')
        with self.assertRaises(models.ConfigurationError):
            models.sync_models('codex', CHOICES, home=self.home, apply=True)
        self.assertEqual(override.read_text(encoding='utf-8'), original_override)


if __name__ == '__main__':
    unittest.main()
