"""plugins/s-wukong/evals 的用例结构要能被 claude plugin eval 读到。"""
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import marketplace_lib

ROOT = Path(__file__).resolve().parents[1]
EVALS = ROOT / 'plugins/s-wukong/evals'
GRADER_TYPES = {'llm', 'regex', 'tool_used', 'tool_order', 'file_exists', 'baseline'}


def frontmatter(text):
    match = re.match(r'---\n(.*?)\n---\n', text, re.S)
    return match.group(1) if match else ''


class EvalSuiteTest(unittest.TestCase):
    def cases(self):
        return sorted(p for p in EVALS.iterdir() if p.is_dir() and p.name != 'results')

    def test_every_case_has_a_prompt_and_graders(self):
        self.assertTrue(self.cases())
        for case in self.cases():
            prompt = case / 'prompt.md'
            config = case / 'case.yaml'
            self.assertTrue(prompt.is_file() or config.is_file(), case.name)
            if config.is_file():
                text = config.read_text(encoding='utf-8')
                self.assertIn('schema_version: "1.1"', text, case.name)
                self.assertIn(f'name: {case.name}', text, case.name)
            else:
                self.assertIn(f'name: {case.name}', frontmatter(prompt.read_text(encoding='utf-8')), case.name)
            graders = sorted((case / 'graders').glob('*.md'))
            self.assertTrue(graders, case.name)
            for grader in graders:
                kind = re.search(r'^type:\s*(\S+)', frontmatter(grader.read_text(encoding='utf-8')), re.M)
                self.assertIsNotNone(kind, grader)
                self.assertIn(kind.group(1), GRADER_TYPES, grader)

    def test_readme_lists_every_case(self):
        readme = (EVALS / 'README.md').read_text(encoding='utf-8')
        for case in self.cases():
            self.assertIn(f'`{case.name}`', readme)

    def test_eval_results_do_not_change_the_content_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            plugins = Path(tmp)
            (plugins / 'demo/evals/results/run').mkdir(parents=True)
            (plugins / 'demo/SKILL.md').write_text('x', encoding='utf-8')
            with patch.object(marketplace_lib, 'PLUGINS_DIR', plugins):
                before = marketplace_lib.content_hash('demo')
                (plugins / 'demo/evals/results/run/report.html').write_text('r', encoding='utf-8')
                self.assertEqual(before, marketplace_lib.content_hash('demo'))


if __name__ == '__main__':
    unittest.main()
