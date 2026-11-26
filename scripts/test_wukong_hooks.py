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
HOOKS = ROOT / 'plugins/wukong/hooks'
PRE_COMMIT = ROOT / 'scripts/git-hooks/pre-commit'
# 钩子会写本地使用日志；测试里关掉，不碰真实的 ~/.wukong。
os.environ['WUKONG_JOURNAL'] = '0'


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
            self.assertIn('wukong 9.9.9（ROOT）', message)
            self.assertIn(text, message)

    def test_unreadable_check_says_so_and_still_names_the_version(self):
        for broken in (None, {'status': 'error'}, {}):
            message = self.check.build_message(broken, root='ROOT', version='1.2.3')
            self.assertIn('wukong 1.2.3', message)
            self.assertIn('暂时无法确认', message)

    def test_script_injects_session_context_with_the_plugin_version(self):
        out = run_script('session_check', {'hook_event_name': 'SessionStart', 'source': 'startup'})
        version = json.loads((ROOT / 'plugins/wukong/plugin.json').read_text(encoding='utf-8'))['version']
        self.assertEqual(out['hookEventName'], 'SessionStart')
        self.assertIn('wukong ' + version, out['additionalContext'])
        self.assertIn('全局技能提示词', out['additionalContext'])

    def test_missing_check_script_yields_no_result(self):
        self.check.CHECK = Path(tempfile.gettempdir()) / 'no-such-global-instructions.py'
        try:
            self.assertIsNone(self.check.run_check())
        finally:
            self.check.CHECK = load('session_check').CHECK

    def test_in_process_check_respects_claude_config_dir(self):
        gi_path = ROOT / 'plugins/wukong/skills/wukong-init/scripts/global_instructions.py'
        spec = importlib.util.spec_from_file_location('gi_test', gi_path)
        gi = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gi)
        with tempfile.TemporaryDirectory() as tmp:
            old_dir = os.environ.get('CLAUDE_CONFIG_DIR')
            os.environ['CLAUDE_CONFIG_DIR'] = tmp
            try:
                missing = self.check.run_check()
                self.assertEqual(missing['status'], 'missing')
                (Path(tmp) / 'CLAUDE.md').write_text(gi.managed_block() + '\n', encoding='utf-8')
                configured = self.check.run_check()
                self.assertEqual(configured['status'], 'configured')
            finally:
                if old_dir is None:
                    os.environ.pop('CLAUDE_CONFIG_DIR', None)
                else:
                    os.environ['CLAUDE_CONFIG_DIR'] = old_dir


class RegistrationTest(unittest.TestCase):
    def test_hooks_json_wires_every_script_with_a_python_fallback(self):
        hooks = json.loads((HOOKS / 'hooks.json').read_text(encoding='utf-8'))['hooks']
        self.assertEqual(set(hooks), {'SessionStart', 'UserPromptSubmit', 'PreToolUse'})
        self.assertEqual(hooks['PreToolUse'][0]['matcher'], 'Bash')
        commands = [h['command'] for entries in hooks.values() for e in entries for h in e['hooks']]
        self.assertIn('Skill', [entry.get('matcher') for entry in hooks['PreToolUse']])
        for script in ('hooks/session_check.py', 'hooks/git_guard.py', 'hooks/journal.py', 'skills/prompt-sharpen/scripts/improve_hook.py'):
            matching = [c for c in commands if '${CLAUDE_PLUGIN_ROOT}/' + script in c]
            self.assertTrue(matching, script)
            self.assertTrue(all(c.startswith('python3 ') and '|| python ' in c for c in matching), script)
            self.assertTrue((ROOT / 'plugins/wukong' / script).is_file(), script)

    def test_daily_check_points_at_the_session_hook(self):
        text = (ROOT / 'plugins/wukong/skills/wukong-init/references/daily-check.md').read_text(encoding='utf-8')
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


class AgyPluginCompatTest(unittest.TestCase):
    def test_rules_agents_md_matches_plugin_agents_md(self):
        plugin = ROOT / 'plugins/wukong'
        self.assertEqual((plugin / 'rules/AGENTS.md').read_bytes(), (plugin / 'AGENTS.md').read_bytes())

    def test_root_hooks_json_registers_session_start(self):
        data = json.loads((ROOT / 'plugins/wukong/hooks.json').read_text(encoding='utf-8'))
        handlers = data['wukong-session']['SessionStart']
        self.assertTrue(any('hooks/agy_hook.py' in h['command'] for h in handlers))
        pre_handlers = data['wukong-prompt-sharpen']['PreInvocation']
        self.assertTrue(any('hooks/agy_hook.py' in h['command'] for h in pre_handlers))

    def test_agy_hook_pre_invocation_injects_once_per_turn_and_skips_short(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, WUKONG_HOME=tmp, WUKONG_AUTO_UPDATE='0', WUKONG_JOURNAL='0', WUKONG_HOOK_LOG='1')
            env.pop('WUKONG_HOOK_NOTICE', None)

            def run_pre(payload):
                proc = subprocess.run(
                    [sys.executable, '-I', str(HOOKS / 'agy_hook.py')],
                    input=json.dumps(payload).encode('utf-8'),
                    capture_output=True, timeout=20, env=env,
                )
                self.assertEqual(proc.returncode, 0, proc.stderr.decode('utf-8', 'replace'))
                return json.loads(proc.stdout.decode('utf-8'))

            # First invocation of a vague turn injects systemMessage + user_markdown notice.
            turn1 = {
                'hookEventName': 'PreInvocation',
                'conversationId': 'conv-1',
                'invocationNum': 0,
                'lastUserInput': '<t3_code_instructions>x</t3_code_instructions><user_request>把登录页改一下</user_request><runtime_info>y</runtime_info>',
            }
            out1 = run_pre(turn1)
            steps = out1.get('injectSteps') or []
            self.assertEqual(len(steps), 1)
            self.assertIn('wukong:prompt-sharpen', steps[0]['systemMessage']['systemMessage'])
            self.assertIn('prompt-sharpen', steps[0]['systemMessage'].get('metadata', {}).get('user_markdown', ''))

            # Subsequent invocation in the same turn (or wakeup) stays silent.
            turn1_step2 = dict(turn1, invocationNum=2)
            self.assertEqual(run_pre(turn1_step2), {})

            # Short/confirmation turn stays silent.
            turn2 = {
                'hookEventName': 'PreInvocation',
                'conversationId': 'conv-1',
                'invocationNum': 0,
                'lastUserInput': '继续<runtime_info>y</runtime_info>',
            }
            self.assertEqual(run_pre(turn2), {})

            # New substantive turn injects again; WUKONG_HOOK_NOTICE=0 hides user_markdown.
            turn3 = {
                'hookEventName': 'PreInvocation',
                'conversationId': 'conv-1',
                'invocationNum': 0,
                'lastUserInput': '帮我优化一下首页加载速度',
            }
            quiet_env = dict(env, WUKONG_HOOK_NOTICE='0')
            proc3 = subprocess.run(
                [sys.executable, '-I', str(HOOKS / 'agy_hook.py')],
                input=json.dumps(turn3).encode('utf-8'),
                capture_output=True, timeout=20, env=quiet_env,
            )
            self.assertEqual(proc3.returncode, 0)
            out3 = json.loads(proc3.stdout.decode('utf-8'))
            self.assertIn('wukong:prompt-sharpen', out3['injectSteps'][0]['systemMessage']['systemMessage'])
            self.assertNotIn('metadata', out3['injectSteps'][0]['systemMessage'])

            # Status log records once per turn (not repeated for deduped step 2) and --status prints it.
            log_file = Path(tmp) / 'prompt-hook-log.jsonl'
            rows = [json.loads(line) for line in log_file.read_text(encoding='utf-8').splitlines() if line.strip()]
            self.assertEqual([r['outcome'] for r in rows], ['injected', 'skipped:confirmation', 'injected'])
            self.assertTrue(all(r['via'] == 'agy_hook' for r in rows))
            status = subprocess.run(
                [sys.executable, '-I', str(HOOKS / 'agy_hook.py'), '--status'],
                capture_output=True, timeout=20, env=env,
            )
            self.assertEqual(status.returncode, 0)
            self.assertIn('agy_hook/PreInvocation', status.stdout.decode('utf-8'))

    def test_agy_hook_pre_invocation_records_journal_once_per_turn(self):
        import sqlite3
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, WUKONG_HOME=tmp, WUKONG_AUTO_UPDATE='0', WUKONG_JOURNAL='1')

            def run_pre(payload):
                proc = subprocess.run(
                    [sys.executable, '-I', str(HOOKS / 'agy_hook.py')],
                    input=json.dumps(payload).encode('utf-8'),
                    capture_output=True, timeout=20, env=env,
                )
                self.assertEqual(proc.returncode, 0, proc.stderr.decode('utf-8', 'replace'))
                return json.loads(proc.stdout.decode('utf-8'))

            turn1 = {
                'hookEventName': 'PreInvocation',
                'conversationId': 'conv-j',
                'cwd': str(ROOT),
                'invocationNum': 0,
                'lastUserInput': '<user_request>给订单列表加导出接口</user_request><runtime_info>m</runtime_info>',
            }
            run_pre(turn1)
            run_pre(dict(turn1, invocationNum=1))
            run_pre(dict(turn1, invocationNum=0, lastUserInput='继续'))

            db = Path(tmp) / 'journal.db'
            self.assertTrue(db.exists())
            conn = sqlite3.connect(str(db))
            try:
                rows = conn.execute('SELECT event, session, text FROM events ORDER BY id').fetchall()
            finally:
                conn.close()
            self.assertEqual(rows, [('task', 'conv-j', '给订单列表加导出接口')])

    def test_agy_hook_malformed_input_does_not_trigger_session_start(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, WUKONG_HOME=tmp, WUKONG_AUTO_UPDATE='0', WUKONG_JOURNAL='1')
            for raw in (b'', b'not json', b'{}'):
                proc = subprocess.run(
                    [sys.executable, '-I', str(HOOKS / 'agy_hook.py')],
                    input=raw, capture_output=True, timeout=20, env=env,
                )
                self.assertEqual(proc.returncode, 0)
                self.assertEqual(json.loads(proc.stdout.decode('utf-8')), {})
            self.assertFalse((Path(tmp) / 'journal.db').exists())

    def test_agy_hook_claim_user_turn_cleans_tmp_on_replace_failure_and_serializes(self):
        from concurrent.futures import ThreadPoolExecutor
        from unittest import mock
        hook = load('agy_hook')
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / 'agy-prompt-state.json'
            with mock.patch.object(hook.os, 'replace', side_effect=PermissionError('busy')):
                self.assertTrue(hook._claim_user_turn('conv-err', '把登录页改一下', path=state))
            self.assertEqual(list(Path(tmp).glob('*.tmp')), [])

            def claim(i):
                return hook._claim_user_turn(f'conv-{i}', f'帮我处理任务编号 {i}', path=state)

            with ThreadPoolExecutor(max_workers=8) as pool:
                results = list(pool.map(claim, range(12)))
            self.assertTrue(all(results))
            saved = json.loads(state.read_text(encoding='utf-8'))
            self.assertEqual(len(saved), 12)
            self.assertEqual(list(Path(tmp).glob('*.tmp')), [])
            self.assertEqual(list(Path(tmp).glob('*.lock')), [])

    def test_agy_hook_outputs_empty_json_and_respects_throttle_and_clean_check(self):
        from unittest import mock
        hook = load('agy_hook')
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / 'agy-update.json'
            with mock.patch.dict(os.environ, {'WUKONG_AUTO_UPDATE': '0'}):
                self.assertFalse(hook.maybe_auto_update(path=state))
            with mock.patch.dict(os.environ, {'WUKONG_AUTO_UPDATE': '1'}), \
                 mock.patch.object(hook, 'is_clean_branch', return_value=False) as clean_mock, \
                 mock.patch.object(hook, 'trigger_background_pull') as pull_mock:
                self.assertFalse(hook.maybe_auto_update(now=1000, path=state))
                clean_mock.assert_called_once()
                pull_mock.assert_not_called()
                # Throttled within 24h: does not re-check git status or pull.
                self.assertFalse(hook.maybe_auto_update(now=1100, path=state))
                self.assertEqual(clean_mock.call_count, 1)
            with mock.patch.dict(os.environ, {'WUKONG_AUTO_UPDATE': '1'}), \
                 mock.patch.object(hook, 'is_clean_branch', return_value=True), \
                 mock.patch.object(hook, 'trigger_background_pull') as pull_mock:
                self.assertTrue(hook.maybe_auto_update(now=1000 + 90000, path=state))
                pull_mock.assert_called_once()

        env = dict(os.environ, WUKONG_AUTO_UPDATE='0', WUKONG_JOURNAL='0')
        proc = subprocess.run(
            [sys.executable, '-I', str(HOOKS / 'agy_hook.py')],
            input=b'{"hookEventName":"SessionStart"}',
            capture_output=True, timeout=20, env=env,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(json.loads(proc.stdout.decode('utf-8')), {})

    def test_agy_hook_lock_prevents_concurrent_pull_and_reclaims_stale_lock(self):
        from unittest import mock
        hook = load('agy_hook')
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / 'agy-update.json'
            lock = state.with_suffix('.lock')
            # Active lock held by another session: skips without pulling.
            lock.write_text('99999', encoding='utf-8')
            now = lock.stat().st_mtime + 10
            with mock.patch.dict(os.environ, {'WUKONG_AUTO_UPDATE': '1'}), \
                 mock.patch.object(hook, 'is_clean_branch', return_value=True), \
                 mock.patch.object(hook, 'trigger_background_pull') as pull_mock:
                self.assertFalse(hook.maybe_auto_update(now=now, path=state))
                pull_mock.assert_not_called()
            # Stale lock (> STALE_LOCK_SECONDS): reclaimed and pulls once, then lock is released.
            stale_now = lock.stat().st_mtime + hook.STALE_LOCK_SECONDS + 5
            with mock.patch.dict(os.environ, {'WUKONG_AUTO_UPDATE': '1'}), \
                 mock.patch.object(hook, 'is_clean_branch', return_value=True), \
                 mock.patch.object(hook, 'trigger_background_pull') as pull_mock:
                self.assertTrue(hook.maybe_auto_update(now=stale_now, path=state))
                pull_mock.assert_called_once()
                self.assertFalse(lock.exists())

    def test_agy_hook_rejects_detached_head(self):
        from unittest import mock
        hook = load('agy_hook')
        with mock.patch.object(hook, '_git_output', side_effect=[(0, ''), (0, 'HEAD')]):
            self.assertFalse(hook.is_clean_branch(ROOT))
        with mock.patch.object(hook, '_git_output', side_effect=[(0, ''), (0, 'main')]):
            self.assertTrue(hook.is_clean_branch(ROOT))


if __name__ == '__main__':
    unittest.main()
