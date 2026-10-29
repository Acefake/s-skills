"""Exercise global initialization against isolated user homes."""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'plugins/s-atlas/skills/setup-s-instructions/scripts/global_instructions.py'


class GlobalInstructionsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('global_instructions', SCRIPT)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.home = Path(self.directory.name)

    def test_check_missing_does_not_create_files(self):
        result = self.module.sync_global('codex', home=self.home)
        self.assertEqual(result['status'], 'missing')
        self.assertFalse(result['changed'])
        self.assertEqual(list(self.home.iterdir()), [])

    def test_create_global_codex_and_repeat_without_changes(self):
        result = self.module.sync_global('codex', home=self.home, apply=True)
        path = self.home / '.codex/AGENTS.md'
        self.assertTrue(result['changed'])
        first = path.read_bytes()
        self.assertIn('s-atlas 全局技能规则', first.decode('utf-8'))
        result = self.module.sync_global('codex', home=self.home, apply=True)
        self.assertFalse(result['changed'])
        self.assertEqual(first, path.read_bytes())

    def test_preserve_existing_unicode_crlf_and_backup(self):
        path = self.home / '.claude/CLAUDE.md'
        path.parent.mkdir()
        original = '用户自己的偏好\r\n不要改已有规则。\r\n'.encode('utf-8')
        path.write_bytes(original)
        self.module.sync_global('claude-code', home=self.home, apply=True)
        self.assertTrue(path.read_bytes().startswith(original))
        self.assertEqual(path.with_name(path.name + '.s-atlas.bak').read_bytes(), original)
        first = path.read_bytes()
        self.module.sync_global('claude-code', home=self.home, apply=True)
        self.assertEqual(path.read_bytes(), first)

    def test_existing_unmarked_template_is_not_duplicated(self):
        path = self.home / '.codex/AGENTS.md'
        path.parent.mkdir()
        original = ('User rules\n\n' + self.module.load_template() + '\n').encode('utf-8')
        path.write_bytes(original)
        result = self.module.sync_global('codex', home=self.home, apply=True)
        self.assertFalse(result['changed'])
        self.assertEqual(path.read_bytes(), original)

    def test_nonempty_override_is_the_effective_codex_target(self):
        home = self.home / 'custom-codex'
        home.mkdir()
        base = home / 'AGENTS.md'
        override = home / 'AGENTS.override.md'
        base.write_text('base remains', encoding='utf-8')
        override.write_text('override remains\n', encoding='utf-8')
        result = self.module.sync_global('codex', home=self.home, codex_home=home, apply=True)
        self.assertEqual(Path(result['target']), override)
        self.assertEqual(base.read_text(encoding='utf-8'), 'base remains')
        self.assertTrue(override.read_text(encoding='utf-8').startswith('override remains\n'))

    def test_empty_override_does_not_hide_base_configuration(self):
        home = self.home / '.codex'
        home.mkdir()
        (home / 'AGENTS.override.md').write_text(' \n', encoding='utf-8')
        result = self.module.sync_global('codex', home=self.home, apply=True)
        self.assertEqual(Path(result['target']), home / 'AGENTS.md')

    def test_update_only_owned_block(self):
        path = self.home / '.claude/CLAUDE.md'
        path.parent.mkdir()
        original = 'before\n' + self.module.START + '\nold rules\n' + self.module.END + '\nafter\n'
        path.write_text(original, encoding='utf-8')
        check = self.module.sync_global('claude-code', home=self.home)
        self.assertEqual(check['status'], 'outdated')
        self.assertEqual(path.read_text(encoding='utf-8'), original)
        self.module.sync_global('claude-code', home=self.home, apply=True)
        final = path.read_text(encoding='utf-8')
        self.assertTrue(final.startswith('before\n'))
        self.assertTrue(final.endswith('\nafter\n'))
        self.assertNotIn('old rules', final)

    def test_malformed_markers_do_not_modify_existing_file(self):
        path = self.home / '.codex/AGENTS.md'
        path.parent.mkdir()
        original = ('user\n' + self.module.START + '\nunclosed\n').encode('utf-8')
        path.write_bytes(original)
        with self.assertRaises(self.module.ConfigurationError):
            self.module.sync_global('codex', home=self.home, apply=True)
        self.assertEqual(path.read_bytes(), original)

    def test_utf8_bom_is_preserved(self):
        path = self.home / '.codex/AGENTS.md'
        path.parent.mkdir()
        original = b'\xef\xbb\xbf' + '偏好\n'.encode('utf-8')
        path.write_bytes(original)
        self.module.sync_global('codex', home=self.home, apply=True)
        self.assertTrue(path.read_bytes().startswith(original))

    def test_duplicate_or_inline_markers_cannot_overwrite_user_content(self):
        path = self.home / '.claude/CLAUDE.md'
        path.parent.mkdir()
        start, end = self.module.START, self.module.END
        for original in (f'{start}\n{start}\n{end}\n', f'user {start}\nrules\n{end}', f'{start}\nrules{end}'):
            path.write_bytes(original.encode('utf-8'))
            with self.assertRaises(self.module.ConfigurationError):
                self.module.sync_global('claude-code', home=self.home, apply=True)
            self.assertEqual(path.read_bytes(), original.encode('utf-8'))
        self.assertFalse(path.with_name(path.name + '.s-atlas.bak').exists())

    def test_cli_reports_missing_apply_configured_and_cursor_without_writing_globals(self):
        environment = dict(os.environ)
        environment.pop('CODEX_HOME', None)
        command = [sys.executable, '-X', 'utf8', str(SCRIPT), '--home', str(self.home)]
        def run(*arguments):
            result = subprocess.run(command + list(arguments), capture_output=True, encoding='utf-8', env=environment)
            return result.returncode, json.loads(result.stdout)
        code, result = run('--host', 'codex')
        self.assertEqual((code, result['status']), (2, 'missing'))
        self.assertEqual(list(self.home.iterdir()), [])
        code, result = run('--host', 'codex', '--apply')
        self.assertEqual((code, result['changed']), (0, True))
        code, result = run('--host', 'codex', '--apply')
        self.assertEqual((code, result['changed']), (0, False))
        code, result = run('--host', 'codex')
        self.assertEqual((code, result['status']), (0, 'configured'))
        code, result = run('--host', 'cursor', '--apply')
        self.assertEqual((code, result['changed']), (3, False))
        self.assertFalse((self.home / '.cursor').exists())

    def test_cursor_does_not_write_guessed_global_files(self):
        for apply in (False, True):
            result = self.module.sync_global('cursor', home=self.home, apply=apply)
            self.assertEqual(result['status'], 'user_rules_verification_required')
            self.assertFalse(result['changed'])
            self.assertIn(self.module.START, result['block'])
        self.assertEqual(list(self.home.iterdir()), [])

    def test_unsupported_host_cannot_write(self):
        with self.assertRaises(ValueError):
            self.module.sync_global('other', home=self.home, apply=True)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_daily_links_resolve_and_new_skill_is_explicit(self):
        skills = ROOT / 'plugins/s-atlas/skills'
        guide = skills / 'setup-s-instructions/references/daily-check.md'
        self.assertTrue(guide.is_file())
        for path in skills.glob('*/SKILL.md'):
            if path.parent.name == 'setup-s-instructions':
                self.assertIn('disable-model-invocation: true', path.read_text(encoding='utf-8'))
                self.assertIn('allow_implicit_invocation: false', (path.parent/'agents/openai.yaml').read_text(encoding='utf-8'))
            else:
                self.assertIn('../setup-s-instructions/references/daily-check.md', path.read_text(encoding='utf-8'), str(path))

    def run_cli(self, host, *, environment=None, apply=False):
        variables = dict(os.environ)
        for key in ('CODEX_HOME', 'CLAUDE_CONFIG_DIR'):
            variables.pop(key, None)
        variables.update(environment or {})
        command = [sys.executable, '-X', 'utf8', str(SCRIPT), '--host', host, '--home', str(self.home)]
        if apply:
            command.append('--apply')
        result = subprocess.run(command, cwd=self.home, capture_output=True, encoding='utf-8', env=variables)
        return result.returncode, json.loads(result.stdout)

    def test_owned_block_at_bom_start_is_configured_and_can_be_updated(self):
        path = self.home / '.codex/AGENTS.md'
        path.parent.mkdir()
        original = b'\xef\xbb\xbf' + self.module.managed_block().encode('utf-8') + b'\nuser suffix\n'
        path.write_bytes(original)
        result = self.module.sync_global('codex', home=self.home, apply=True)
        self.assertFalse(result['changed'])
        self.assertEqual(path.read_bytes(), original)
        outdated = b'\xef\xbb\xbf' + (self.module.START + '\nold\n' + self.module.END).encode('utf-8') + b'\nuser suffix\n'
        path.write_bytes(outdated)
        self.module.sync_global('codex', home=self.home, apply=True)
        self.assertEqual(path.read_bytes(), original)

    def test_cli_honors_custom_global_directories_for_both_file_hosts(self):
        for host, key, filename in (('codex', 'CODEX_HOME', 'AGENTS.md'), ('claude-code', 'CLAUDE_CONFIG_DIR', 'CLAUDE.md')):
            with self.subTest(host=host):
                directory = self.home / (host + '-custom')
                code, result = self.run_cli(host, environment={key: str(directory)}, apply=True)
                self.assertEqual(code, 0)
                self.assertEqual(Path(result['target']), directory / filename)
                self.assertTrue((directory / filename).is_file())
        self.assertFalse((self.home / '.codex').exists())
        self.assertFalse((self.home / '.claude').exists())

    def test_empty_codex_home_environment_uses_home_default(self):
        code, result = self.run_cli('codex', environment={'CODEX_HOME': ''}, apply=True)
        self.assertEqual(code, 0)
        self.assertEqual(Path(result['target']), self.home / '.codex/AGENTS.md')
        self.assertFalse((self.home / 'AGENTS.md').exists())

    def test_readonly_check_preserves_outdated_file_and_creates_no_backup(self):
        path = self.home / '.claude/CLAUDE.md'
        path.parent.mkdir()
        original = ('prefix\r\n' + self.module.START + '\r\nold\r\n' + self.module.END + '\r\nsuffix\r\n').encode('utf-8')
        path.write_bytes(original)
        result = self.module.sync_global('claude-code', home=self.home)
        self.assertEqual(result['status'], 'outdated')
        self.assertFalse(result['changed'])
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(list(path.parent.iterdir()), [path])

    def test_updates_preserve_crlf_suffix_and_first_backup(self):
        path = self.home / '.claude/CLAUDE.md'
        path.parent.mkdir()
        original = 'user original\r\n'.encode('utf-8')
        path.write_bytes(original)
        self.module.sync_global('claude-code', home=self.home, apply=True)
        outdated = ('prefix\r\n' + self.module.START + '\r\nold\r\n' + self.module.END + '\r\nsuffix\r\n').encode('utf-8')
        path.write_bytes(outdated)
        self.module.sync_global('claude-code', home=self.home, apply=True)
        updated = path.read_bytes()
        self.assertTrue(updated.startswith(b'prefix\r\n'))
        self.assertTrue(updated.endswith(b'\r\nsuffix\r\n'))
        self.assertNotIn(b'\n', updated.replace(b'\r\n', b''))
        self.assertEqual(path.with_name(path.name + '.s-atlas.bak').read_bytes(), original)
        self.assertFalse(self.module.sync_global('claude-code', home=self.home, apply=True)['changed'])

    def test_unreadable_encoding_is_reported_without_modification(self):
        path = self.home / '.codex/AGENTS.md'
        path.parent.mkdir()
        original = 'user rules'.encode('utf-16')
        path.write_bytes(original)
        code, result = self.run_cli('codex', apply=True)
        self.assertEqual((code, result['status']), (1, 'error'))
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(list(path.parent.iterdir()), [path])

    def test_atomic_replace_failure_preserves_original_and_cleans_temporary_file(self):
        path = self.home / '.codex/AGENTS.md'
        path.parent.mkdir()
        original = b'user original\n'
        path.write_bytes(original)
        with patch.object(self.module.os, 'replace', side_effect=PermissionError('blocked')):
            with self.assertRaises(PermissionError):
                self.module.sync_global('codex', home=self.home, apply=True)
        self.assertEqual(path.read_bytes(), original)
        backup = path.with_name(path.name + '.s-atlas.bak')
        self.assertEqual(backup.read_bytes(), original)
        self.assertEqual(set(path.parent.iterdir()), {path, backup})

    def test_concurrent_edit_is_not_replaced_by_stale_read(self):
        path = self.home / '.codex/AGENTS.md'
        path.parent.mkdir()
        path.write_bytes(b'user changed this meanwhile\n')
        with self.assertRaises(self.module.ConfigurationError):
            self.module.write_preserving(path, b'stale read\n', b'generated replacement\n')
        self.assertEqual(path.read_bytes(), b'user changed this meanwhile\n')
        self.assertFalse(any(p.name.startswith('AGENTS.md.') and p.suffix != '.bak' for p in path.parent.iterdir()))

    def test_cli_json_supports_unicode_paths_on_legacy_windows_console(self):
        home = self.home / '用户😀'
        environment = dict(os.environ, PYTHONIOENCODING='gbk')
        environment.pop('CODEX_HOME', None)
        command = [sys.executable, str(SCRIPT), '--host', 'codex', '--home', str(home), '--apply']
        result = subprocess.run(command, capture_output=True, encoding='utf-8', env=environment)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(Path(json.loads(result.stdout)['target']), home / '.codex/AGENTS.md')
        cursor = subprocess.run([sys.executable, str(SCRIPT), '--host', 'cursor', '--home', str(home)],
                                capture_output=True, encoding='utf-8', env=environment)
        self.assertEqual(cursor.returncode, 3, cursor.stderr)
        self.assertEqual(json.loads(cursor.stdout)['block'], self.module.managed_block())


if __name__ == '__main__':
    unittest.main()
