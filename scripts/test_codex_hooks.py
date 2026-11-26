"""Exercise Codex hook upgrade checks without touching the real user profile."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'plugins/wukong'
SCRIPT = PLUGIN / 'skills/wukong-init/scripts/codex_hooks.py'
RELATIVE = 'skills/prompt-sharpen/scripts/improve_hook.py'


class CodexHooksTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.home = Path(self.directory.name)
        self.target = self.home / '.codex/hooks.json'
        self.target.parent.mkdir()

    def run_cli(self, *args):
        env = dict(os.environ)
        env.pop('CODEX_HOME', None)
        result = subprocess.run([sys.executable, str(SCRIPT), '--home', str(self.home), *args],
                                env=env, capture_output=True, timeout=15)
        self.assertTrue(result.stdout, result.stderr.decode(errors='replace'))
        return result.returncode, json.loads(result.stdout)

    def fixture(self, name='s-atlas'):
        path = str(self.home / 'repo/plugins' / name / RELATIVE)
        return {'hooks': {'UserPromptSubmit': [{'matcher': '', 'hooks': [
            {'type': 'command', 'command': f'python3 "{path}" || python "{path}"',
             'commandWindows': f'python "{path}" || python3 "{path}"', 'timeout': 5}]}],
            'Stop': [{'hooks': [{'type': 'command', 'command': 'third-party stop'}]}]},
            'user-setting': {'keep': True}}

    def test_legacy_hook_is_detected_without_writing_then_migrated_idempotently(self):
        original = b'\xef\xbb\xbf' + json.dumps(self.fixture(), ensure_ascii=False, indent=2).replace('\n', '\r\n').encode()
        self.target.write_bytes(original)
        code, checked = self.run_cli()
        self.assertEqual(code, 2)
        self.assertEqual(checked['status'], 'outdated')
        self.assertEqual(self.target.read_bytes(), original)
        self.assertFalse(self.target.with_name('hooks.json.wukong.bak').exists())
        code, applied = self.run_cli('--apply')
        self.assertEqual(code, 0)
        self.assertTrue(applied['changed'])
        migrated = json.loads(self.target.read_text(encoding='utf-8-sig'))
        hook = migrated['hooks']['UserPromptSubmit'][0]['hooks'][0]
        current = (PLUGIN / RELATIVE).resolve().as_posix()
        self.assertEqual(hook['command'], f'python3 "{current}" || python "{current}"')
        self.assertEqual(migrated['hooks']['Stop'], self.fixture()['hooks']['Stop'])
        self.assertTrue(migrated['user-setting']['keep'])
        self.assertEqual(self.target.with_name('hooks.json.wukong.bak').read_bytes(), original)
        self.assertTrue(self.target.read_bytes().startswith(b'\xef\xbb\xbf'))
        self.assertNotIn(b'\n', self.target.read_bytes().replace(b'\r\n', b''))
        before = self.target.read_bytes()
        self.assertFalse(self.run_cli('--apply')[1]['changed'])
        self.assertEqual(self.target.read_bytes(), before)

    def test_other_legacy_name_and_windows_separators_are_migrated(self):
        value = self.fixture('s-wukong')
        hook = value['hooks']['UserPromptSubmit'][0]['hooks'][0]
        hook['commandWindows'] = hook['commandWindows'].replace('/', '\\')
        self.target.write_text(json.dumps(value), encoding='utf8')
        self.assertEqual(self.run_cli('--apply')[0], 0)
        self.assertNotIn('s-wukong', self.target.read_text(encoding='utf8'))

    def test_missing_hooks_are_reported_but_not_installed(self):
        code, result = self.run_cli('--apply')
        self.assertEqual(code, 2)
        self.assertEqual(result['status'], 'missing')
        self.assertFalse(self.target.exists())

    def test_custom_commands_and_third_party_hooks_are_not_rewritten(self):
        value = self.fixture()
        hook = value['hooks']['UserPromptSubmit'][0]['hooks'][0]
        hook['command'] = 'echo ' + hook['command']
        hook.pop('commandWindows')
        self.target.write_text(json.dumps(value), encoding='utf8')
        before = self.target.read_bytes()
        code, result = self.run_cli('--apply')
        self.assertEqual(code, 2)
        self.assertEqual(result['status'], 'manual_review')
        self.assertEqual(self.target.read_bytes(), before)

    def test_malformed_json_and_symlink_do_not_overwrite(self):
        self.target.write_bytes(b'{broken')
        self.assertEqual(self.run_cli('--apply')[0], 1)
        self.assertEqual(self.target.read_bytes(), b'{broken')
        self.target.unlink()
        other = self.home / 'real.json'
        other.write_text(json.dumps(self.fixture()), encoding='utf8')
        try:
            self.target.symlink_to(other)
        except OSError:
            self.skipTest('Symlink creation unavailable')
        before = other.read_bytes()
        self.assertEqual(self.run_cli('--apply')[0], 1)
        self.assertEqual(other.read_bytes(), before)

    def test_custom_codex_home_is_respected(self):
        custom = self.home / 'custom-codex'
        custom.mkdir()
        target = custom / 'hooks.json'
        target.write_text(json.dumps(self.fixture()), encoding='utf8')
        result = self.run_cli('--codex-home', str(custom), '--apply')
        self.assertEqual(result[0], 0)
        self.assertEqual(Path(result[1]['target']), target)
        self.assertFalse(self.target.exists())

    def test_global_upgrade_check_reports_hooks_without_migrating_them(self):
        self.target.write_text(json.dumps(self.fixture()), encoding='utf8')
        before = self.target.read_bytes()
        result = subprocess.run([sys.executable, str(SCRIPT.with_name('global_instructions.py')),
                                 '--host', 'codex', '--home', str(self.home), '--codex-home',
                                 str(self.target.parent), '--apply'], capture_output=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        value = json.loads(result.stdout)
        self.assertEqual(value['status'], 'configured')
        self.assertEqual(value['hooks']['status'], 'outdated')
        self.assertEqual(self.target.read_bytes(), before)

    def test_duplicate_json_keys_are_rejected_without_writing(self):
        before = b'{"hooks":{},"hooks":{}}'
        self.target.write_bytes(before)
        self.assertEqual(self.run_cli('--apply')[0], 1)
        self.assertEqual(self.target.read_bytes(), before)

    def test_old_cache_version_is_migrated_but_trust_state_is_not_changed(self):
        value = self.fixture('wukong/1.0.16')
        self.target.write_text(json.dumps(value), encoding='utf8')
        trust = self.target.parent / 'config.toml'
        trust.write_bytes(b'[hooks.state]\ntrusted_hash="keep-existing-approval"\n')
        before = trust.read_bytes()
        self.assertEqual(self.run_cli('--apply')[0], 0)
        self.assertNotIn('1.0.16', self.target.read_text(encoding='utf8'))
        self.assertEqual(trust.read_bytes(), before)

    def test_unquoted_old_script_requires_manual_review(self):
        value = self.fixture()
        hook = value['hooks']['UserPromptSubmit'][0]['hooks'][0]
        hook['command'] = hook['command'].replace('"', '')
        self.target.write_text(json.dumps(value), encoding='utf8')
        before = self.target.read_bytes()
        self.assertEqual(self.run_cli('--apply')[1]['status'], 'manual_review')
        self.assertEqual(self.target.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
