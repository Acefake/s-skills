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
# 钩子会写本地使用日志；测试里关掉，不碰真实的 ~/.wukong。
os.environ['WUKONG_JOURNAL'] = '0'


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
                       '  <system-reminder>x</system-reminder>'):
            self.assertIsNone(run_hook(prompt_event(prompt)), prompt)

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
