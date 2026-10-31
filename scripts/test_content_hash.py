"""content_hash 只应随插件源文件变化，不受 Python 运行产物影响。"""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import marketplace_lib


class ContentHashTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.plugins = Path(self._tmp.name)
        skill = self.plugins / 'demo/skills/sample'
        skill.mkdir(parents=True)
        (skill / 'SKILL.md').write_text('---\nname: sample\n---\n', encoding='utf-8')
        patcher = patch.object(marketplace_lib, 'PLUGINS_DIR', self.plugins)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.skill = skill

    def test_pycache_and_pyc_do_not_change_hash(self):
        before = marketplace_lib.content_hash('demo')
        cache = self.skill / 'scripts/__pycache__'
        cache.mkdir(parents=True)
        (cache / 'x.cpython-313.pyc').write_bytes(b'\x00pyc')
        (self.skill / 'stray.pyc').write_bytes(b'\x01')
        self.assertEqual(before, marketplace_lib.content_hash('demo'))

    def test_source_change_changes_hash(self):
        before = marketplace_lib.content_hash('demo')
        (self.skill / 'SKILL.md').write_text('---\nname: sample\n---\nmore\n', encoding='utf-8')
        self.assertNotEqual(before, marketplace_lib.content_hash('demo'))


if __name__ == '__main__':
    unittest.main()
