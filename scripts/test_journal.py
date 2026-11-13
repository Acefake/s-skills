"""Cover the local usage journal: what it records, what it hides, and that it stays silent and safe."""
import importlib.util
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock

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

    def run_script(self, script, payload, env=None, args=()):
        result = subprocess.run(
            [sys.executable, '-I', str(script), *args], input=json.dumps(payload).encode('utf-8'),
            capture_output=True, timeout=60, env=env or self.env,
        )
        self.assertEqual(result.returncode, 0, result.stderr.decode('utf-8', 'replace'))
        return result.stdout.decode('utf-8')

    def rows(self):
        path = self.home / 'journal.db'
        if not path.exists():
            return []
        conn = sqlite3.connect(str(path))
        conn.row_factory = sqlite3.Row
        try:
            return [dict(r) for r in conn.execute('SELECT * FROM events ORDER BY id')]
        finally:
            conn.close()


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
    def test_hook_payloads_become_one_row_each(self):
        with mock.patch.dict(os.environ, {'WUKONG_HOME': str(self.home), 'WUKONG_JOURNAL': '1'}):
            self.journal.record({'hook_event_name': 'SessionStart', 'session_id': 's1', 'cwd': '/work/acme-api'})
            self.journal.record({'hook_event_name': 'PreToolUse', 'tool_name': 'Skill', 'tool_input': {'skill': 'wukong:tdd'}, 'session_id': 's1'})
            self.journal.record({'hook_event_name': 'PreToolUse', 'tool_name': 'Bash', 'tool_input': {'command': 'ls'}})
            self.journal.record(prompt('不对，别派审查了'))
        rows = self.rows()
        self.assertEqual([r['event'] for r in rows], ['session', 'skill', 'correction'])
        self.assertEqual(rows[0]['project'], 'acme-api')
        self.assertEqual((rows[1]['name'], rows[1]['via']), ('wukong:tdd', 'tool'))
        for row in rows:
            datetime.fromisoformat(row['ts'])
            self.assertAlmostEqual(row['at'], time.time(), delta=60)

    def test_database_is_private_and_versioned(self):
        self.run_script(HOOKS / 'journal.py', {'hook_event_name': 'SessionStart'})
        path = self.home / 'journal.db'
        if os.name == 'posix':
            self.assertEqual(self.home.stat().st_mode & 0o777, 0o700)
            for name in ('journal.db', 'journal.db-wal', 'journal.db-shm'):
                extra = self.home / name
                if extra.exists():
                    self.assertEqual(extra.stat().st_mode & 0o077, 0, name)
        conn = sqlite3.connect(str(path))
        try:
            self.assertEqual(conn.execute('PRAGMA user_version').fetchone()[0], self.journal.SCHEMA_VERSION)
            self.assertEqual(conn.execute('PRAGMA journal_mode').fetchone()[0].lower(), 'wal')
        finally:
            conn.close()

    def test_script_prints_nothing_and_survives_bad_input(self):
        self.assertEqual(self.run_script(HOOKS / 'journal.py', prompt('给订单服务加导出接口')), '')
        bad = subprocess.run([sys.executable, '-I', str(HOOKS / 'journal.py')], input=b'not json',
                             capture_output=True, timeout=30, env=self.env)
        self.assertEqual((bad.returncode, bad.stdout, bad.stderr), (0, b'', b''))
        self.assertEqual(len(self.rows()), 1)

    def test_switch_off(self):
        self.run_script(HOOKS / 'journal.py', {'hook_event_name': 'SessionStart'}, env=dict(self.env, WUKONG_JOURNAL='0'))
        self.assertFalse((self.home / 'journal.db').exists())

    def test_unwritable_home_fails_silently(self):
        blocker = Path(self.tmp.name) / 'file'
        blocker.write_text('x', encoding='utf-8')
        env = dict(self.env, WUKONG_HOME=str(blocker / 'sub'))
        self.assertEqual(self.run_script(HOOKS / 'journal.py', {'hook_event_name': 'SessionStart'}, env=env), '')

    def test_corrupt_database_fails_silently(self):
        self.home.mkdir(parents=True)
        (self.home / 'journal.db').write_bytes(b'not a database' * 100)
        self.assertEqual(self.run_script(HOOKS / 'journal.py', {'hook_event_name': 'SessionStart'}), '')

    def test_held_lock_gives_up_without_blocking_the_session(self):
        conn = self.journal.connect(self.home)
        conn.execute('BEGIN EXCLUSIVE')
        try:
            started = time.monotonic()
            self.assertEqual(self.run_script(HOOKS / 'journal.py', {'hook_event_name': 'SessionStart'}), '')
            self.assertLess(time.monotonic() - started, self.journal.LOCK_TIMEOUT + 3)
        finally:
            conn.execute('ROLLBACK')
            conn.close()
        self.assertEqual(self.rows(), [])

    def test_prompt_hook_records_through_the_same_process(self):
        out = self.run_script(IMPROVE, prompt('把登录页的报错提示改清楚一点'))
        self.assertIn('prompt-sharpen', out)
        self.assertEqual([r['event'] for r in self.rows()], ['task'])
        self.run_script(IMPROVE, {'hook_event_name': 'PreToolUse', 'tool_name': 'Bash', 'tool_input': {'command': 'npm run dev'}})
        self.assertEqual(len(self.rows()), 1)

    def test_session_hook_records_a_session(self):
        self.run_script(HOOKS / 'session_check.py', {'hook_event_name': 'SessionStart', 'session_id': 's9'})
        self.assertEqual([(r['event'], r['session']) for r in self.rows()], [('session', 's9')])


    def test_missing_sqlite_module_is_silent(self):
        code = ('import runpy, sys; sys.modules["sqlite3"] = None; sys.argv = [sys.argv[1]]; '
                'runpy.run_path(sys.argv[0], run_name="__main__")')
        result = subprocess.run([sys.executable, '-I', '-c', code, str(HOOKS / 'journal.py')],
                                input=json.dumps(prompt('给接口加分页')).encode('utf-8'),
                                capture_output=True, timeout=30, env=self.env)
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, b'', b''))
        self.assertFalse((self.home / 'journal.db').exists())

    @unittest.skipUnless(os.name == 'posix', 'POSIX permissions')
    def test_existing_loose_permissions_are_tightened(self):
        self.home.mkdir(mode=0o755)
        os.chmod(self.home, 0o755)
        self.run_script(HOOKS / 'journal.py', {'hook_event_name': 'SessionStart'})
        os.chmod(self.home / 'journal.db', 0o644)
        self.run_script(HOOKS / 'journal.py', {'hook_event_name': 'SessionStart'})
        self.assertEqual(self.home.stat().st_mode & 0o777, 0o700)
        self.assertEqual((self.home / 'journal.db').stat().st_mode & 0o777, 0o600)

    def test_hook_output_comes_before_the_journal(self):
        conn = self.journal.connect(self.home)
        conn.execute('BEGIN EXCLUSIVE')
        try:
            out = self.run_script(IMPROVE, prompt('把登录页的报错提示改清楚一点'))
        finally:
            conn.execute('ROLLBACK')
            conn.close()
        self.assertIn('prompt-sharpen', out)


class ConcurrencyTest(JournalCase):
    def test_parallel_writers_lose_nothing(self):
        writer = (
            'import importlib.util, sys\n'
            'spec = importlib.util.spec_from_file_location("j", sys.argv[1]); j = importlib.util.module_from_spec(spec)\n'
            'spec.loader.exec_module(j)\n'
            'for i in range(25):\n'
            '    j.record({"hook_event_name": "UserPromptSubmit", "prompt": "任务编号 %s-%d 给接口加分页" % (sys.argv[2], i), "session_id": sys.argv[2]})\n'
        )
        procs = [subprocess.Popen([sys.executable, '-I', '-c', writer, str(HOOKS / 'journal.py'), 'w%d' % n], env=self.env)
                 for n in range(8)]
        for proc in procs:
            self.assertEqual(proc.wait(timeout=120), 0)
        rows = self.rows()
        self.assertEqual(len(rows), 200)
        self.assertEqual({r['session'] for r in rows}, {'w%d' % n for n in range(8)})


class PruneTest(JournalCase):
    def insert(self, conn, ages_in_days):
        now = time.time()
        for age in ages_in_days:
            at = int(now - age * 86400)
            conn.execute('INSERT INTO events (at, ts, event) VALUES (?, ?, ?)', (at, 'x', 'task'))

    def test_old_rows_are_dropped(self):
        conn = self.journal.connect(self.home)
        try:
            self.insert(conn, [120, 91, 89, 1])
            self.journal.prune(conn)
            self.assertEqual(conn.execute('SELECT count(*) FROM events').fetchone()[0], 2)
        finally:
            conn.close()

    def test_row_cap_keeps_the_newest(self):
        conn = self.journal.connect(self.home)
        try:
            with mock.patch.object(self.journal, 'MAX_ROWS', 10):
                self.insert(conn, [0] * 25)
                self.journal.prune(conn)
            ids = [r[0] for r in conn.execute('SELECT id FROM events ORDER BY id')]
            self.assertEqual(ids, list(range(16, 26)))
        finally:
            conn.close()

    def test_old_rows_go_on_every_append_even_below_the_cadence(self):
        conn = self.journal.connect(self.home)
        self.insert(conn, [200, 1])
        conn.close()
        self.journal.append({'at': int(time.time()), 'ts': 'x', 'event': 'task'}, self.home)
        self.assertEqual(len(self.rows()), 2)

    def test_prune_runs_periodically_on_append(self):
        with mock.patch.object(self.journal, 'PRUNE_EVERY', 3):
            conn = self.journal.connect(self.home)
            self.insert(conn, [200])
            conn.close()
            with mock.patch.object(self.journal, 'MAX_ROWS', 1):
                self.journal.append({'at': int(time.time()), 'ts': 'x', 'event': 'task'}, self.home)
                self.assertEqual([r['id'] for r in self.rows()], [2])
                self.journal.append({'at': int(time.time()), 'ts': 'x', 'event': 'task'}, self.home)
        self.assertEqual([r['id'] for r in self.rows()], [3])


class DumpTest(JournalCase):
    def test_dump_prints_recent_events_as_json_lines(self):
        for i in range(3):
            self.run_script(HOOKS / 'journal.py', prompt('第 %d 个任务：给接口加分页' % i))
        out = self.run_script(HOOKS / 'journal.py', {}, args=('--dump', '--limit', '2'))
        items = [json.loads(line) for line in out.splitlines()]
        self.assertEqual(len(items), 2)
        self.assertTrue(items[0]['text'].startswith('第 1 个'))
        self.assertNotIn('id', items[0])

    def test_dump_handles_unusual_directory_names(self):
        # Windows 文件名不允许 ?，只在 POSIX 上测它。
        name = 'we#ird?dir%20' if os.name == 'posix' else 'we#ird dir%20'
        env = dict(self.env, WUKONG_HOME=str(Path(self.tmp.name) / name))
        self.run_script(HOOKS / 'journal.py', prompt('给接口加分页和排序'), env=env)
        out = self.run_script(HOOKS / 'journal.py', {}, env=env, args=('--dump',))
        self.assertEqual(json.loads(out)['event'], 'task')

    def test_dump_without_database_prints_nothing(self):
        self.assertEqual(self.run_script(HOOKS / 'journal.py', {}, args=('--dump',)), '')


if __name__ == '__main__':
    unittest.main()
