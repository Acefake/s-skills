"""版本号在锁文件、清单、README 与架构文档之间保持一致，宿主档位分组不被写错。"""
import re
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import bump_plugin_version
import check_marketplace
import marketplace_lib

REPO = Path(__file__).resolve().parents[1]


class DocVersionTest(unittest.TestCase):
    def make_repo(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        for rel in {r for r, _ in marketplace_lib.DOC_VERSION_REFS['wukong']}:
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(REPO / rel, root / rel)
        return root

    def test_repo_docs_match_lock(self):
        lock = marketplace_lib.load_lock()['plugins']['wukong']['version']
        for rel, found in marketplace_lib.doc_versions('wukong'):
            self.assertEqual(found, lock, rel)

    def test_stale_doc_version_is_reported(self):
        root = self.make_repo()
        readme = root / 'README.md'
        readme.write_text(re.sub(r'当前版本 \d+\.\d+\.\d+', '当前版本 0.0.1', readme.read_text(encoding='utf-8')), encoding='utf-8')
        with patch.object(marketplace_lib, 'ROOT', root), patch.object(check_marketplace, 'ROOT', root):
            problems = check_marketplace.Problems()
            check_marketplace.check_versions(problems)
        self.assertTrue(any('README.md says version 0.0.1' in item for item in problems.items), problems.items)

    def test_set_doc_versions_rewrites_every_doc(self):
        root = self.make_repo()
        with patch.object(marketplace_lib, 'ROOT', root):
            marketplace_lib.set_doc_versions('wukong', '9.9.9')
            self.assertEqual({v for _, v in marketplace_lib.doc_versions('wukong')}, {'9.9.9'})

    def test_bump_script_imports_doc_updater(self):
        self.assertIs(bump_plugin_version.set_doc_versions, marketplace_lib.set_doc_versions)


if __name__ == '__main__':
    unittest.main()
