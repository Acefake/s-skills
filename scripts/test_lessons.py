"""Exercise confirmed learning without touching the real user's experience store."""
import importlib.util
from concurrent.futures import ThreadPoolExecutor
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'plugins/s-atlas/skills/learn/scripts/lessons.py'


class LessonsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('lessons', SCRIPT)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name)
        self.project = self.home / 'project-a'
        self.record = dict(scope='project', when='修改 Vue 属性保存行为时',
                           lesson='保存后回读验证持久化，不只检查界面刷新。',
                           evidence='复现中刷新成功但重启后丢失。', keywords=['Vue', '保存'])

    def save(self, record=None, **kwargs):
        return self.module.save(record or self.record, home=self.home, project=self.project,
                                confirmed=True, **kwargs)

    def test_no_confirmation_means_no_write(self):
        with self.assertRaises(ValueError):
            self.module.save(self.record, home=self.home, project=self.project)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_empty_search_is_readonly(self):
        self.assertEqual(self.module.search('Vue', home=self.home, project=self.project), [])
        self.assertEqual(list(self.home.iterdir()), [])

    def test_confirm_save_reload_and_repeat_are_idempotent(self):
        first = self.save()
        original = Path(first['path']).read_bytes()
        second = self.save()
        self.assertTrue(first['changed'])
        self.assertFalse(second['changed'])
        self.assertEqual(first['id'], second['id'])
        self.assertEqual(Path(first['path']).read_bytes(), original)
        notes = self.module.search('Vue 保存', home=self.home, project=self.project)
        self.assertEqual([note['lesson'] for note in notes], [self.record['lesson']])

    def test_project_isolation_and_shared_global_records(self):
        self.save()
        global_record = dict(self.record, scope='global', lesson='报告测试时说明验证范围。')
        shared = self.save(global_record)
        other = self.module.search('Vue 保存', home=self.home, project=self.home/'project-b')
        self.assertEqual([note['id'] for note in other], [shared['id']])
        same = self.module.search('Vue 保存', home=self.home, project=self.project/'..'/'project-a')
        self.assertEqual(len(same), 2)

    def test_unrelated_records_are_not_returned_and_limit_is_bounded(self):
        for number in range(5):
            self.save(dict(self.record, lesson=f'持久化验证步骤 {number}'))
        self.assertEqual(self.module.search('账单支付', home=self.home, project=self.project), [])
        self.assertEqual(len(self.module.search('Vue', home=self.home, project=self.project)), 3)
        with self.assertRaises(ValueError):
            self.module.search('Vue', home=self.home, project=self.project, limit=100)

    def test_confirmed_replacement_retires_old_record_without_deleting_it(self):
        first = self.save()
        second = self.save(dict(self.record, lesson='先核对后端保存协议，再做回读验证。', supersedes=first['id']))
        third = self.save(dict(self.record, lesson='保存协议变化后重新验证回读。', supersedes=second['id']))
        self.assertTrue(Path(first['path']).is_file())
        self.assertTrue(Path(second['path']).is_file())
        result = self.module.search('Vue', home=self.home, project=self.project)
        self.assertEqual([note['id'] for note in result], [third['id']])

    def test_two_writers_cannot_replace_the_same_retired_lesson(self):
        old = self.save()
        def replace(number):
            try:
                return self.save(dict(self.record, lesson=f'已确认的新做法 {number}', supersedes=old['id']))
            except ValueError:
                return None
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(replace, (1, 2)))
        self.assertEqual(sum(result is not None for result in results), 1)
        notes = self.module.search('Vue', home=self.home, project=self.project)
        self.assertEqual(len(notes), 1)
        self.assertNotEqual(notes[0]['id'], old['id'])

    def test_historical_lesson_cannot_be_silently_reactivated(self):
        first = self.save()
        second = self.save(dict(self.record, lesson='已确认的新做法', supersedes=first['id']))
        with self.assertRaises(ValueError):
            self.save()
        restored = self.save(dict(self.record, supersedes=second['id']))
        self.assertTrue(restored['changed'])
        self.assertNotEqual(first['id'], restored['id'])
        notes = self.module.search('Vue', home=self.home, project=self.project)
        self.assertEqual([note['id'] for note in notes], [restored['id']])

    def test_invalid_scope_record_and_replacement_cannot_write(self):
        bad = [dict(self.record, scope='other'), dict(self.record, lesson=''),
               dict(self.record, keywords='Vue'), dict(self.record, supersedes='../other'),
               dict(self.record, supersedes='a'*64)]
        for record in bad:
            with self.subTest(record=record), self.assertRaises(ValueError):
                self.save(record)
        self.assertFalse((self.home/'.s-atlas').exists())

    def test_replacement_cannot_cross_projects(self):
        old = self.save()
        with self.assertRaises(ValueError):
            self.module.save(dict(self.record, supersedes=old['id']), home=self.home,
                             project=self.home/'project-b', confirmed=True)

    def test_interrupted_publish_leaves_no_partial_record(self):
        with patch.object(self.module.os, 'link', side_effect=OSError('unavailable')):
            with self.assertRaises(OSError):
                self.save()
        self.assertEqual(list((self.home/'.s-atlas').rglob('*.json')), [])
        self.assertEqual(list((self.home/'.s-atlas').rglob('*.tmp')), [])

    def test_cli_refuses_unconfirmed_save_and_new_process_can_recall(self):
        record_path = self.home/'candidate.json'
        record_path.write_bytes(b'\xef\xbb\xbf' + json.dumps(self.record).encode('utf-8'))
        command = [sys.executable, str(SCRIPT), '--home', str(self.home)]
        arguments = ['save', '--project', str(self.project), '--record', str(record_path)]
        rejected = subprocess.run(command+arguments, capture_output=True, text=True)
        self.assertNotEqual(rejected.returncode, 0)
        self.assertFalse((self.home/'.s-atlas').exists())
        accepted = subprocess.run(command+arguments+['--confirmed'], capture_output=True, text=True)
        self.assertEqual(accepted.returncode, 0, accepted.stderr)
        recalled = subprocess.run(command+['search','--project',str(self.project),'--query','Vue'],
                                  capture_output=True, text=True)
        self.assertEqual(recalled.returncode, 0, recalled.stderr)
        self.assertEqual(json.loads(recalled.stdout)[0]['lesson'], self.record['lesson'])


if __name__ == '__main__':
    unittest.main()
