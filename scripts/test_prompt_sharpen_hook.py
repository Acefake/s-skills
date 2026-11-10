"""Keep the optional prompt-sharpen hook aligned with the skill and its docs."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / 'plugins/wukong/skills/prompt-sharpen'
HOOK = SKILL_DIR / 'scripts/improve_hook.py'


def run_hook(payload):
    result = subprocess.run(
        [sys.executable, '-I', str(HOOK)],
        input=json.dumps(payload).encode('utf-8'),
        capture_output=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stderr.decode('utf-8', 'replace')
    out = result.stdout.decode('utf-8').strip()
    return json.loads(out)['hookSpecificOutput'] if out else None


def prompt_event(prompt):
    return {'hook_event_name': 'UserPromptSubmit', 'prompt': prompt}


def bash_event(command):
    return {'hook_event_name': 'PreToolUse', 'tool_name': 'Bash', 'tool_input': {'command': command}}


class PromptSharpenHookTest(unittest.TestCase):
    def test_prompt_gets_evaluation_that_names_the_skill(self):
        out = run_hook(prompt_event('把登录弄好一点'))
        self.assertEqual(out['hookEventName'], 'UserPromptSubmit')
        self.assertIn('把登录弄好一点', out['additionalContext'])
        self.assertIn('wukong:prompt-sharpen', out['additionalContext'])

    def test_quotes_and_backslashes_are_escaped_in_the_quoted_prompt(self):
        out = run_hook(prompt_event('改 "a\\b"'))
        self.assertIn('"改 \\"a\\\\b\\""', out['additionalContext'])

    def test_long_prompt_is_quoted_only_in_part(self):
        prompt = '甲' * 199 + '乙' + '丙' * 3000
        context = run_hook(prompt_event(prompt))['additionalContext']
        self.assertIn('甲' * 199 + '乙…（原话过长已截断，以原消息为准）"', context)
        self.assertNotIn('丙', context)

    def test_prompt_at_limit_is_quoted_whole(self):
        context = run_hook(prompt_event('甲' * 200))['additionalContext']
        self.assertIn('"' + '甲' * 200 + '"', context)
        self.assertNotIn('已截断', context)
        self.assertIn('已截断', run_hook(prompt_event('甲' * 201))['additionalContext'])

    def test_truncation_happens_before_escaping(self):
        context = run_hook(prompt_event('甲' * 198 + '\\"' + '丙' * 10))['additionalContext']
        self.assertIn('甲' * 198 + '\\\\\\"…', context)

    def test_bypass_prefixes_and_machine_events_stay_silent(self):
        for prompt in ('*直接做', '#记住这个', '/deslop', '', '   ',
                       '<task-notification>done</task-notification>',
                       '  <system-reminder>x</system-reminder>'):
            self.assertIsNone(run_hook(prompt_event(prompt)), prompt)

    def test_long_running_bash_gets_background_reminder(self):
        for command in ('npm run dev', 'pnpm start', 'tail -f app.log', 'vite', 'python -m http.server'):
            out = run_hook(bash_event(command))
            self.assertEqual(out['hookEventName'], 'PreToolUse', command)
            self.assertIn('run_in_background', out['additionalContext'], command)

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


if __name__ == '__main__':
    unittest.main()
