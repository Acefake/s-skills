"""Keep the optional prompt-sharpen hook aligned with the skill and its docs."""
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / 'plugins/wukong/skills/prompt-sharpen'
HOOK = SKILL_DIR / 'scripts/improve_hook.py'
# 钩子会写本地使用日志和状态日志；测试里默认关掉，不碰真实的 ~/.wukong。
DEFAULT_TEST_ENV = dict(os.environ, WUKONG_JOURNAL='0', WUKONG_HOOK_LOG='0')


def run_hook_raw(payload, env=None):
    result = subprocess.run(
        [sys.executable, '-I', str(HOOK)],
        input=json.dumps(payload).encode('utf-8'),
        capture_output=True,
        timeout=20,
        env=DEFAULT_TEST_ENV if env is None else env,
    )
    assert result.returncode == 0, result.stderr.decode('utf-8', 'replace')
    out = result.stdout.decode('utf-8').strip()
    return json.loads(out) if out else None


def run_hook(payload):
    raw = run_hook_raw(payload)
    return raw['hookSpecificOutput'] if raw else None


def prompt_event(prompt):
    return {'hook_event_name': 'UserPromptSubmit', 'prompt': prompt}


def bash_event(command):
    return {'hook_event_name': 'PreToolUse', 'tool_name': 'Bash', 'tool_input': {'command': command}}


class PromptSharpenHookTest(unittest.TestCase):
    def test_prompt_gets_compact_evaluation_that_names_the_skill(self):
        prompt = '把登录弄好一点'
        out = run_hook(prompt_event(prompt))
        self.assertEqual(out['hookEventName'], 'UserPromptSubmit')
        context = out['additionalContext']
        self.assertIn('wukong:prompt-sharpen', context)
        self.assertNotIn(prompt, context)
        self.assertLess(len(context), 260)
        for criterion in ('目标', '范围', '约束', '验收', '没文件名不算缺口', '只说了动作'):
            self.assertIn(criterion, context)

    def test_long_prompt_produces_fixed_size_context(self):
        short_context = run_hook(prompt_event('改一下登录页'))['additionalContext']
        long_prompt = '甲' * 199 + '乙' + '丙' * 3000
        long_context = run_hook(prompt_event(long_prompt))['additionalContext']
        self.assertEqual(long_context, short_context)
        self.assertNotIn('甲', long_context)
        self.assertNotIn('丙', long_context)

    def test_bypass_prefixes_and_machine_events_stay_silent(self):
        for prompt in ('*直接做', '#记住这个', '/deslop', '', '   ',
                       '<task-notification>done</task-notification>',
                       '  <system-reminder>x</system-reminder>',
                       '<runtime_info>In case you are asked</runtime_info>',
                       '[T3 Code: the agent in T3 thread "demo" sent this message, not the user.] Act now',
                       'Delegated task node:delegated-task:abc finished'):
            self.assertIsNone(run_hook(prompt_event(prompt)), prompt)

    def test_t3_wrapped_user_request_is_unwrapped_before_evaluation(self):
        short_wrapped = (
            '<t3_code_instructions>long rules...</t3_code_instructions>\n\n'
            '<user_request>\n提交\n</user_request><runtime_info>meta</runtime_info>'
        )
        self.assertIsNone(run_hook(prompt_event(short_wrapped)))
        vague_wrapped = (
            '<USER_REQUEST>\n'
            '<t3_code_instructions>mention </runtime_info> literally</t3_code_instructions>\n\n'
            '<user_request>\n把登录页改一下\n</user_request><runtime_info>meta</runtime_info>\n'
            '</USER_REQUEST>\n<ADDITIONAL_METADATA>time</ADDITIONAL_METADATA>'
        )
        out = run_hook(prompt_event(vague_wrapped))
        self.assertIsNotNone(out)
        self.assertIn('wukong:prompt-sharpen', out['additionalContext'])
        self.assertIsNone(run_hook(prompt_event('推送<runtime_info>model info</runtime_info>')))
        # Ordinary prompts mentioning <user_request>...</user_request> inline must not be truncated.
        inline_tag = '帮我把 <user_request>foo</user_request> 这段正则改成支持多行'
        out_inline = run_hook(prompt_event(inline_tag))
        self.assertIsNotNone(out_inline)
        self.assertIn('wukong:prompt-sharpen', out_inline['additionalContext'])

    def test_confirmations_and_very_short_prompts_stay_silent(self):
        for prompt in ('可以', '好的。', '继续', '按你说的做', 'OK', 'lgtm', '修一下', ' 嗯 '):
            self.assertIsNone(run_hook(prompt_event(prompt)), prompt)
        for prompt in ('可以把登录改一下吗', '修一下登录页', '继续优化首页性能'):
            self.assertIsNotNone(run_hook(prompt_event(prompt)), prompt)

    def test_long_running_bash_gets_background_reminder(self):
        for command in ('npm run dev', 'pnpm start', 'tail -f app.log', 'vite', 'python -m http.server'):
            out = run_hook(bash_event(command))
            self.assertEqual(out['hookEventName'], 'PreToolUse', command)
            self.assertIn('run_in_background', out['additionalContext'], command)

    def test_quoted_or_heredoc_mentions_do_not_trigger_background_reminder(self):
        for command in (
            "echo '{\"command\":\"npm run dev\"}' | python hook.py",
            'grep -n "tail -f" README.md',
            "cat <<'EOF' > notes.md\nrun npm run dev later\nEOF",
        ):
            self.assertIsNone(run_hook(bash_event(command)), command)
        for command in ('cd web && npm run dev', 'bash -c "npm run dev"', "sh -lc 'tail -f app.log'"):
            out = run_hook(bash_event(command))
            self.assertIn('run_in_background', out['additionalContext'], command)

    def test_only_vague_prompts_show_user_notice(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, WUKONG_HOME=tmp, WUKONG_JOURNAL='0', WUKONG_HOOK_LOG='0')
            env.pop('WUKONG_HOOK_NOTICE', None)
            for prompt in ('帮我把性能优化一下', '把登录页改一下', 'make it better please'):
                out = run_hook_raw(prompt_event(prompt), env=env)
                self.assertIn('需求可能不够具体', out.get('systemMessage', ''), prompt)
            for prompt in (
                '把 README 里的版本号从 1.0.30 改成 1.0.31',
                '优化 `parseDate` 的报错信息',
                '按推荐的改，误报也一起修',
                '给 src/login.tsx 加个记住密码的选项',
                '优化提示词的钩子都能正确触发了吗',
                '这个能优化一下吗？',
            ):
                out = run_hook_raw(prompt_event(prompt), env=env)
                self.assertNotIn('systemMessage', out, prompt)
                self.assertIn('wukong:prompt-sharpen', out['hookSpecificOutput']['additionalContext'], prompt)

    def test_short_commands_and_other_tools_stay_silent(self):
        self.assertIsNone(run_hook(bash_event('ls -la')))
        self.assertIsNone(run_hook({'hook_event_name': 'PreToolUse', 'tool_name': 'Read', 'tool_input': {'command': 'npm run dev'}}))

    def test_bad_input_exits_quietly(self):
        result = subprocess.run([sys.executable, '-I', str(HOOK)], input=b'not json', capture_output=True, timeout=20)
        self.assertEqual((result.returncode, result.stdout), (0, b''))
        self.assertIsNone(run_hook({'hook_event_name': 'Stop'}))

    def test_plugin_registers_the_hook_by_default(self):
        hooks = json.loads((ROOT / 'plugins/wukong/hooks/hooks.json').read_text(encoding='utf-8'))['hooks']
        self.assertEqual(hooks['PreToolUse'][0]['matcher'], 'Bash')
        for event in ('UserPromptSubmit', 'PreToolUse'):
            commands = [h['command'] for entry in hooks[event] for h in entry['hooks']]
            self.assertTrue(any('${CLAUDE_PLUGIN_ROOT}/skills/prompt-sharpen/scripts/improve_hook.py' in c for c in commands), event)

    def test_skill_and_docs_point_at_the_hook(self):
        skill = (SKILL_DIR / 'SKILL.md').read_text(encoding='utf-8')
        self.assertIn('references/hook.md', skill)
        self.assertNotIn('本库不装钩子', skill)
        self.assertNotIn('默认不装', skill)
        doc = (SKILL_DIR / 'references/hook.md').read_text(encoding='utf-8')
        self.assertIn('scripts/improve_hook.py', doc)
        self.assertIn('~/.codex/hooks.json', doc)
        self.assertIn('commandWindows', doc)
        self.assertIn('../../../LICENSE-prompt-improver', doc)
        self.assertTrue((ROOT / 'plugins/wukong/LICENSE-prompt-improver').is_file())

    def test_user_notice_toggle_and_status_log_cli(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, WUKONG_HOME=tmp, WUKONG_JOURNAL='0', WUKONG_HOOK_LOG='1')
            env.pop('WUKONG_HOOK_NOTICE', None)

            # Default: UserPromptSubmit includes top-level systemMessage for the user.
            out = run_hook_raw(prompt_event('把登录页改一下'), env=env)
            self.assertIn('prompt-sharpen', out.get('systemMessage', ''))

            # PreToolUse never attaches the prompt-sharpen user notice.
            bash_out = run_hook_raw(bash_event('npm run dev'), env=env)
            self.assertNotIn('systemMessage', bash_out)

            # WUKONG_HOOK_NOTICE=0 suppresses systemMessage while keeping additionalContext.
            quiet_env = dict(env, WUKONG_HOOK_NOTICE='0')
            quiet_out = run_hook_raw(prompt_event('把登录页改一下'), env=quiet_env)
            self.assertNotIn('systemMessage', quiet_out)
            self.assertIn('wukong:prompt-sharpen', quiet_out['hookSpecificOutput']['additionalContext'])

            # Skipped prompts still record reason without storing prompt text.
            self.assertIsNone(run_hook_raw(prompt_event('继续'), env=env))
            self.assertIsNone(run_hook_raw(prompt_event('提交'), env=env))
            self.assertIsNone(run_hook_raw(prompt_event('*直接做'), env=env))

            log_file = Path(tmp) / 'prompt-hook-log.jsonl'
            rows = [json.loads(line) for line in log_file.read_text(encoding='utf-8').splitlines() if line.strip()]
            self.assertEqual([r['outcome'] for r in rows], [
                'injected', 'injected', 'skipped:confirmation', 'skipped:short', 'skipped:prefix',
            ])
            for row in rows:
                self.assertNotIn('把登录页改一下', json.dumps(row, ensure_ascii=False))

            # --status prints readable summary.
            status = subprocess.run(
                [sys.executable, '-I', str(HOOK), '--status', '--limit', '5'],
                capture_output=True, timeout=20, env=env,
            )
            self.assertEqual(status.returncode, 0, status.stderr.decode('utf-8', 'replace'))
            text = status.stdout.decode('utf-8')
            self.assertIn('prompt-sharpen 钩子状态', text)
            self.assertIn('状态日志：开启', text)
            self.assertIn('injected', text)
            self.assertIn('skipped:prefix', text)

    def test_status_log_disabled_trimming_and_corrupt_lines(self):
        import importlib.util
        import tempfile
        spec = importlib.util.spec_from_file_location('wukong_improve_hook', HOOK)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        with tempfile.TemporaryDirectory() as tmp:
            # WUKONG_HOOK_LOG=0 writes no status log and shows disabled in --status.
            disabled_env = dict(os.environ, WUKONG_HOME=tmp, WUKONG_JOURNAL='0', WUKONG_HOOK_LOG='0')
            self.assertIsNotNone(run_hook_raw(prompt_event('把登录页改一下'), env=disabled_env))
            log_file = Path(tmp) / 'prompt-hook-log.jsonl'
            self.assertFalse(log_file.exists())
            status_disabled = subprocess.run(
                [sys.executable, '-I', str(HOOK), '--status'],
                capture_output=True, timeout=20, env=disabled_env,
            )
            self.assertEqual(status_disabled.returncode, 0)
            self.assertIn('状态日志：关闭（WUKONG_HOOK_LOG=0）', status_disabled.stdout.decode('utf-8'))

            # skipped:empty and skipped:machine are recorded when logging is enabled.
            enabled_env = dict(os.environ, WUKONG_HOME=tmp, WUKONG_JOURNAL='0', WUKONG_HOOK_LOG='1')
            self.assertIsNone(run_hook_raw(prompt_event('   '), env=enabled_env))
            self.assertIsNone(run_hook_raw(prompt_event('<system-reminder>x</system-reminder>'), env=enabled_env))
            rows = [json.loads(line) for line in log_file.read_text(encoding='utf-8').splitlines() if line.strip()]
            self.assertEqual([r['outcome'] for r in rows], ['skipped:empty', 'skipped:machine'])

            # Exceeding LOG_TRIM_THRESHOLD trims back to MAX_LOG_ENTRIES (2 rows already exist).
            prev_log = os.environ.get('WUKONG_HOOK_LOG')
            os.environ['WUKONG_HOOK_LOG'] = '1'
            try:
                remaining = mod.LOG_TRIM_THRESHOLD - len(rows) + 1
                for i in range(remaining):
                    mod.record_hook_status('UserPromptSubmit', f'injected:{i}', path=log_file)
            finally:
                if prev_log is None:
                    os.environ.pop('WUKONG_HOOK_LOG', None)
                else:
                    os.environ['WUKONG_HOOK_LOG'] = prev_log
            trimmed = [line for line in log_file.read_text(encoding='utf-8').splitlines() if line.strip()]
            self.assertEqual(len(trimmed), mod.MAX_LOG_ENTRIES)
            self.assertEqual(json.loads(trimmed[-1])['outcome'], f'injected:{remaining - 1}')

            # Corrupt, non-dict, and non-string session entries do not crash --status.
            with log_file.open('a', encoding='utf-8') as handle:
                handle.write('not-json\n[1, 2, 3]\n"plain-string"\n')
                handle.write(json.dumps({'ts': '2026-01-01', 'via': 'test', 'event': 'UserPromptSubmit',
                                         'outcome': 'injected', 'session': 123456789, 'project': 42}) + '\n')
            status_corrupt = subprocess.run(
                [sys.executable, '-I', str(HOOK), '--status', '--limit', '10'],
                capture_output=True, timeout=20, env=enabled_env,
            )
            self.assertEqual(status_corrupt.returncode, 0, status_corrupt.stderr.decode('utf-8', 'replace'))
            self.assertIn('session=12345678', status_corrupt.stdout.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
