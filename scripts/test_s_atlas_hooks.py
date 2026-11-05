"""Cover the plugin hooks: session check, git guard, registration and the pre-commit script."""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOKS = ROOT / 'plugins/s-atlas/hooks'
PRE_COMMIT = ROOT / 'scripts/git-hooks/pre-commit'


def load(name):
    spec = importlib.util.spec_from_file_location(name, HOOKS / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_script(name, payload):
    result = subprocess.run(
        [sys.executable, '-I', str(HOOKS / (name + '.py'))],
        input=json.dumps(payload).encode('utf-8'), capture_output=True, timeout=30,
    )
    assert result.returncode == 0, result.stderr.decode('utf-8', 'replace')
    out = result.stdout.decode('utf-8').strip()
    return json.loads(out)['hookSpecificOutput'] if out else None


def bash(command):
    return {'hook_event_name': 'PreToolUse', 'tool_name': 'Bash', 'tool_input': {'command': command}}


class GitGuardTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.guard = load('git_guard')

    def test_risky_commands_ask_with_the_matching_reason(self):
        cases = {
            'git commit --no-verify -m x': 'no-verify',
            'git commit -n -m x': 'no-verify',
            'git commit -anm x': 'no-verify',
            'git push --force origin main': 'force-push',
            'git push -f': 'force-push',
            'git push origin +main': 'force-push',
            'git push --force-with-lease': 'force-push',
            'git -C repo push -f': 'force-push',
            'git reset --hard HEAD~1': 'reset-hard',
            'git clean -fd': 'clean',
            'git status && git push -f origin main': 'force-push',
            'cd x; git reset --hard': 'reset-hard',
            'git add .\ngit commit --no-verify -m x': 'no-verify',
            '/usr/bin/git push --force': 'force-push',
            'FOO=1 git push -f': 'force-push',
            'sudo git reset --hard': 'reset-hard',
            'timeout 30 git push -f': 'force-push',
            'git push -o x -f': 'force-push',
            'git commit -m x -n': 'no-verify',
            'git commit -nm x': 'no-verify',
            "git commit -F - <<'EOF'\ndon't\nEOF\ngit push -f": 'force-push',
        }
        for command, key in cases.items():
            self.assertEqual(self.guard.find_risk(command), key, command)

    def test_ordinary_commands_pass(self):
        for command in (
            'git commit -m "fix: 不要用 --no-verify"', 'git commit -am "x"', 'git commit --amend',
            'git push origin main', 'git push -u origin HEAD', 'git reset --soft HEAD~1', 'git reset HEAD file',
            'git clean -n', 'git clean --dry-run -fd', 'git status', 'git log -n 5', 'ls -la',
            'echo "git push -f"', 'git diff --stat', 'npm run build', "git commit -m \"it's fine\"",
            'git commit -m "-n"', 'git commit -m -n', 'git commit -mConfig', 'git commit -m x -- -n',
            'git commit -F -n', 'git push -o -f', 'git commit -Sabc -m x',
            'echo git reset --hard', 'grep -rn git clean docs', 'python tool.py git push -f',
            "cat > a.md <<'EOF'\ngit reset --hard\nEOF",
        ):
            self.assertIsNone(self.guard.find_risk(command), command)

    def test_heredoc_message_with_a_flag_word_does_not_trigger(self):
        command = 'git commit -m "$(cat <<\'EOF\'\nfeat: x\n\n说明 --no-verify 的用法 git push -f\nEOF\n)"'
        self.assertIsNone(self.guard.find_risk(command))

    def test_unbalanced_quotes_fail_open(self):
        self.assertIsNone(self.guard.find_risk('git commit -m "unterminated'))

    def test_script_answers_ask_and_stays_silent_otherwise(self):
        out = run_script('git_guard', bash('git push --force origin main'))
        self.assertEqual((out['hookEventName'], out['permissionDecision']), ('PreToolUse', 'ask'))
        self.assertIn('强制推送', out['permissionDecisionReason'])
        self.assertIsNone(run_script('git_guard', bash('git status')))
        self.assertIsNone(run_script('git_guard', {'hook_event_name': 'PreToolUse', 'tool_name': 'Read', 'tool_input': {'command': 'git push -f'}}))
        bad = subprocess.run([sys.executable, '-I', str(HOOKS / 'git_guard.py')], input=b'not json', capture_output=True, timeout=30)
        self.assertEqual((bad.returncode, bad.stdout), (0, b''))


class SessionCheckTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.check = load('session_check')

    def test_message_covers_every_status(self):
        for status, text in (('configured', '最新'), ('outdated', '需更新'), ('missing', '缺失')):
            message = self.check.build_message({'status': status, 'version': '9.9.9'}, root='ROOT')
            self.assertIn('s-atlas 9.9.9（ROOT）', message)
            self.assertIn(text, message)

    def test_unreadable_check_says_so_and_still_names_the_version(self):
        for broken in (None, {'status': 'error'}, {}):
            message = self.check.build_message(broken, root='ROOT', version='1.2.3')
            self.assertIn('s-atlas 1.2.3', message)
            self.assertIn('暂时无法确认', message)

    def test_script_injects_session_context_with_the_plugin_version(self):
        out = run_script('session_check', {'hook_event_name': 'SessionStart', 'source': 'startup'})
        version = json.loads((ROOT / 'plugins/s-atlas/plugin.json').read_text(encoding='utf-8'))['version']
        self.assertEqual(out['hookEventName'], 'SessionStart')
        self.assertIn('s-atlas ' + version, out['additionalContext'])
        self.assertIn('全局技能提示词', out['additionalContext'])

    def test_missing_check_script_yields_no_result(self):
        self.check.CHECK = Path(tempfile.gettempdir()) / 'no-such-global-instructions.py'
        try:
            self.assertIsNone(self.check.run_check())
        finally:
            self.check.CHECK = load('session_check').CHECK


class RegistrationTest(unittest.TestCase):
    def test_hooks_json_wires_every_script_with_a_python_fallback(self):
        hooks = json.loads((HOOKS / 'hooks.json').read_text(encoding='utf-8'))['hooks']
        self.assertEqual(set(hooks), {'SessionStart', 'UserPromptSubmit', 'PreToolUse'})
        self.assertEqual(hooks['PreToolUse'][0]['matcher'], 'Bash')
        commands = [h['command'] for entries in hooks.values() for e in entries for h in e['hooks']]
        for script in ('hooks/session_check.py', 'hooks/git_guard.py', 'skills/prompt-sharpen/scripts/improve_hook.py'):
            matching = [c for c in commands if '${CLAUDE_PLUGIN_ROOT}/' + script in c]
            self.assertTrue(matching, script)
            self.assertTrue(all(c.startswith('python3 ') and '|| python ' in c for c in matching), script)
            self.assertTrue((ROOT / 'plugins/s-atlas' / script).is_file(), script)

    def test_daily_check_points_at_the_session_hook(self):
        text = (ROOT / 'plugins/s-atlas/skills/setup-s-instructions/references/daily-check.md').read_text(encoding='utf-8')
        self.assertIn('会话开始钩子', text)


@unittest.skipUnless(shutil.which('sh'), 'sh is required to run the pre-commit script')
class PreCommitTest(unittest.TestCase):
    def run_in_repo(self, stub_exit, python=None, via_path=False):
        """Run the hook in a throwaway repo whose check_marketplace.py exits with stub_exit.

        A stub jsonschema.py in the repo satisfies the interpreter probe, so the test does
        not depend on the real dependency being installed.
        """
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / 'repo'
            subprocess.run(['git', 'init', '-q', str(repo)], check=True)
            (repo / 'scripts').mkdir()
            (repo / 'jsonschema.py').write_text('', encoding='utf-8')
            (repo / 'scripts/check_marketplace.py').write_text(
                'import sys\nprint("stub check")\nsys.exit(%d)\n' % stub_exit, encoding='utf-8')
            env = dict(os.environ)
            env.pop('PRE_COMMIT_PYTHON', None)
            if via_path:
                bin_dir = Path(tmp) / 'bin'
                bin_dir.mkdir()
                wrapper = bin_dir / 'python3'
                wrapper.write_text('#!/bin/sh\nexec "%s" "$@"\n' % Path(sys.executable).as_posix(), encoding='utf-8')
                wrapper.chmod(0o755)
                env['PATH'] = str(bin_dir) + os.pathsep + env['PATH']
            elif python:
                env['PRE_COMMIT_PYTHON'] = python
            return subprocess.run(['sh', str(PRE_COMMIT)], cwd=repo, env=env, capture_output=True, timeout=60)

    def test_failing_check_blocks_the_commit_with_the_fix_command(self):
        result = self.run_in_repo(1, python=sys.executable)
        self.assertEqual(result.returncode, 1)
        self.assertIn('bump_plugin_version.py', result.stderr.decode('utf-8', 'replace'))

    def test_passing_check_lets_the_commit_through(self):
        self.assertEqual(self.run_in_repo(0, python=sys.executable).returncode, 0)

    def test_interpreter_is_found_on_path_when_not_given(self):
        self.assertEqual(self.run_in_repo(1, via_path=True).returncode, 1)
        self.assertEqual(self.run_in_repo(0, via_path=True).returncode, 0)

    def test_unusable_interpreter_skips_with_a_notice_instead_of_blocking(self):
        result = self.run_in_repo(1, python='no-such-python-interpreter')
        self.assertEqual(result.returncode, 0)
        self.assertIn('跳过版本检查', result.stderr.decode('utf-8', 'replace'))

    def test_script_is_executable_in_the_git_index(self):
        listing = subprocess.run(['git', 'ls-files', '-s', 'scripts/git-hooks/pre-commit'], cwd=ROOT, capture_output=True, text=True).stdout
        self.assertTrue(listing.startswith('100755') or not listing, listing)


if __name__ == '__main__':
    unittest.main()
