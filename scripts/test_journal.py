"""Cover the local usage journal: what it records, what it hides, and that it stays silent."""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOKS = ROOT / 'plugins/wukong/hooks'
IMPROVE = ROOT / 'plugins/wukong/skills/prompt-sharpen/scripts/improve_hook.py'


def load():
    spec = importlib.util.spec_from_file_location('wukong_journal', HOOKS / 'journal.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prompt(text, session='s1'):
    return {'hook_event_name': 'UserPromptSubmit', 'prompt': text, 'session_id': session, 'cwd': '/work/acme-api'}


class JournalCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name) / 'wukong'
        self.env = dict(os.environ, WUKONG_HOME=str(self.home), WUKONG_JOURNAL='1')
        self.journal = load()

    def tearDown(self):
        self.tmp.cleanup()

    def run_script(self, script, payload, env=None):
        result = subprocess.run(
            [sys.executable, '-I', str(script)], input=json.dumps(payload).encode('utf-8'),
            capture_output=True, timeout=30, env=env or self.env,
        )
        self.assertEqual(result.returncode, 0, result.stderr.decode('utf-8', 'replace'))
        return result.stdout.decode('utf-8')

    def lines(self):
        path = self.home / 'journal.jsonl'
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]


class ClassifyTest(JournalCase):
    def test_prompt_kinds(self):
        classify = self.journal.classify_prompt
        self.assertEqual(classify('不对，回复太长了')[0], 'correction')
        self.assertEqual(classify('以后提交前都先跑 lint')[0], 'explicit')
        self.assertEqual(classify('给订单服务加一个导出接口')[0], 'task')
        self.assertEqual(classify('/deslop src'), ('skill', {'name': 'deslop', 'via': 'slash'}))

    def test_skipped_prompts(self):
        for text in ('可以', '好的。', '继续', 'OK', '修一下', '', '   ', '*直接做', '#记住', '/',
                     '<system-reminder>x</system-reminder>', None, 42):
            self.assertIsNone(self.journal.classify_prompt(text), text)

    def test_excerpt_is_short_and_redacted(self):
        text = '把 sk-abcdefghijklmnop1234 和 me@example.com 换掉，参考 https://x.io/a?token=1 ' + '长' * 200
        kind, extra = self.journal.classify_prompt(text)
        self.assertEqual(kind, 'task')
        self.assertLessEqual(len(extra['text']), self.journal.TASK_EXCERPT + 20)
        for secret in ('sk-abcdefghijklmnop1234', 'me@example.com', 'token=1'):
            self.assertNotIn(secret, extra['text'])
        self.assertIn('[已隐藏]', extra['text'])


class RecordTest(JournalCase):
    def test_hook_payloads_become_one_line_each(self):
        with mock.patch.dict(os.environ, {'WUKONG_HOME': str(self.home), 'WUKONG_JOURNAL': '1'}):
            self.journal.record({'hook_event_name': 'SessionStart', 'session_id': 's1', 'cwd': '/work/acme-api'})
            self.journal.record({'hook_event_name': 'PreToolUse', 'tool_name': 'Skill', 'tool_input': {'skill': 'wukong:tdd'}, 'session_id': 's1'})
            self.journal.record({'hook_event_name': 'PreToolUse', 'tool_name': 'Bash', 'tool_input': {'command': 'ls'}})
            self.journal.record(prompt('不对，别派审查了'))
        events = self.lines()
        self.assertEqual([e['event'] for e in events], ['session', 'skill', 'correction'])
        self.assertEqual(events[0]['project'], 'acme-api')
        self.assertEqual(events[1]['name'], 'wukong:tdd')
        for event in events:
            self.assertTrue(set(event) >= {'ts', 'event', 'session', 'project'})
            datetime.fromisoformat(event['ts'])

    def test_files_are_private(self):
        self.run_script(HOOKS / 'journal.py', {'hook_event_name': 'SessionStart'})
        if os.name == 'posix':
            self.assertEqual((self.home / 'journal.jsonl').stat().st_mode & 0o777, 0o600)
            self.assertEqual(self.home.stat().st_mode & 0o777, 0o700)

    def test_script_prints_nothing_and_survives_bad_input(self):
        self.assertEqual(self.run_script(HOOKS / 'journal.py', prompt('给订单服务加导出接口')), '')
        bad = subprocess.run([sys.executable, '-I', str(HOOKS / 'journal.py')], input=b'not json',
                             capture_output=True, timeout=30, env=self.env)
        self.assertEqual((bad.returncode, bad.stdout, bad.stderr), (0, b'', b''))
        self.assertEqual(len(self.lines()), 1)

    def test_switch_off(self):
        env = dict(self.env, WUKONG_JOURNAL='0')
        self.run_script(HOOKS / 'journal.py', {'hook_event_name': 'SessionStart'}, env=env)
        self.assertEqual(self.lines(), [])

    def test_unwritable_home_fails_silently(self):
        blocker = Path(self.tmp.name) / 'file'
        blocker.write_text('x', encoding='utf-8')
        env = dict(self.env, WUKONG_HOME=str(blocker / 'sub'))
        self.assertEqual(self.run_script(HOOKS / 'journal.py', {'hook_event_name': 'SessionStart'}, env=env), '')

    def test_prompt_hook_records_through_the_same_process(self):
        out = self.run_script(IMPROVE, prompt('把登录页的报错提示改清楚一点'))
        self.assertIn('prompt-sharpen', out)
        self.assertEqual([e['event'] for e in self.lines()], ['task'])
        self.run_script(IMPROVE, {'hook_event_name': 'PreToolUse', 'tool_name': 'Bash', 'tool_input': {'command': 'npm run dev'}})
        self.assertEqual(len(self.lines()), 1)

    def test_session_hook_records_a_session(self):
        self.run_script(HOOKS / 'session_check.py', {'hook_event_name': 'SessionStart', 'session_id': 's9'})
        self.assertEqual([(e['event'], e['session']) for e in self.lines()], [('session', 's9')])


class PruneTest(JournalCase):
    def write(self, records):
        self.home.mkdir(parents=True)
        path = self.home / 'journal.jsonl'
        path.write_text(''.join(json.dumps(r) + '\n' for r in records), encoding='utf-8')
        return path

    def test_old_lines_are_dropped(self):
        now = datetime.now(timezone.utc)
        old = (now - timedelta(days=120)).isoformat()
        new = (now - timedelta(days=1)).isoformat()
        path = self.write([{'ts': old, 'event': 'task'}, {'ts': new, 'event': 'skill'}])
        self.journal.prune(path, now)
        self.assertEqual([json.loads(l)['event'] for l in path.read_text().splitlines()], ['skill'])

    def test_large_file_is_cut_to_the_newest_lines(self):
        now = datetime.now(timezone.utc)
        record = {'ts': now.isoformat(), 'event': 'task', 'text': 'x' * 900}
        path = self.write([dict(record, n=i) for i in range(2600)])
        self.assertGreater(path.stat().st_size, self.journal.MAX_BYTES)
        self.journal.prune(path, now)
        kept = [json.loads(l)['n'] for l in path.read_text().splitlines()]
        self.assertLessEqual(path.stat().st_size, self.journal.KEEP_BYTES)
        self.assertEqual(kept[-1], 2599)
        self.assertEqual(kept, sorted(kept))

    def test_small_recent_file_is_untouched(self):
        now = datetime.now(timezone.utc)
        path = self.write([{'ts': now.isoformat(), 'event': 'task'}])
        before = path.read_bytes()
        self.journal.prune(path, now)
        self.assertEqual(path.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
