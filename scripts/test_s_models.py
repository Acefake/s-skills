"""setup-s-models 的规则脚本：生成、校验、写入都要结果固定。"""
import importlib.util
import re
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'plugins/s-atlas/skills/setup-s-models'
SCRIPT = SKILL / 'scripts/s_models.py'

spec = importlib.util.spec_from_file_location('s_models', SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def rows(budget, fast='sonnet', strong='opus', **kw):
    return m.render_rows(m.normalize_budget(budget), fast, strong, **kw)


def run(*argv):
    out, err = StringIO(), StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = m.main(list(argv))
    return code, out.getvalue(), err.getvalue()


class RenderTest(unittest.TestCase):
    def test_small_uses_strong_only_for_hardest_and_one_reviewer(self):
        r = rows('省')
        self.assertEqual([k for k, v in r.items() if v == 'opus'], ['最难的任务'])
        for key in ('竞技场参赛者', '竞技场交叉评审', '架构设计参赛者', '审问审查者'):
            self.assertEqual(r[key], 'sonnet')

    def test_medium_gives_judgment_to_strong_and_one_or_two_reviewers(self):
        r = rows('中')
        self.assertEqual(r['判断和写作'], 'opus')
        self.assertEqual(r['修 bug'], 'sonnet')
        self.assertEqual(r['审问审查者'], 'sonnet, opus')
        self.assertEqual(rows('中', strong='sonnet')['审问审查者'], 'sonnet')

    def test_large_is_exactly_fast_then_strong(self):
        self.assertEqual(rows('大')['竞技场参赛者'], 'sonnet, opus')
        self.assertEqual(rows('large')['竞技场参赛者'], 'sonnet, opus')

    def test_unlimited_adds_third_family_without_duplicates(self):
        self.assertEqual(rows('不限', third='haiku')['架构设计参赛者'], 'sonnet, opus, haiku')
        self.assertEqual(rows('不限', third='opus')['架构设计参赛者'], 'sonnet, opus')

    def test_single_model_still_meets_reviewer_count(self):
        r = rows('大', strong=None)
        self.assertEqual(set(v for k, v in r.items() if '参赛者' not in k and '评审' not in k and '审查者' not in k), {'sonnet'})
        self.assertEqual(r['审问审查者'], 'sonnet, sonnet')

    def test_inherit_mode_keeps_reviewer_counts(self):
        r = m.render_rows('省', None, None, inherit=True)
        self.assertTrue(all(v == m.INHERIT for v in r.values()))
        r = m.render_rows('大', None, None, inherit=True)
        self.assertEqual(r['审问审查者'], 'inherit-parent, inherit-parent')

    def test_skip_writes_inherit_budget_and_large_layout(self):
        block = m.render_block(m.INHERIT, rows('skip'))
        self.assertIn('# 预算: inherit-parent', block)
        self.assertIn('竞技场参赛者: sonnet, opus', block)

    def test_effort_may_only_go_down(self):
        self.assertEqual(m.budget_line('大', 'high'), '# 预算: 大（high）')
        with self.assertRaises(m.SModelsError):
            m.budget_line('省', 'max')

    def test_overrides_accept_old_english_keys(self):
        self.assertEqual(rows('省', overrides={'bug-fix': 'opus'})['修 bug'], 'opus')
        with self.assertRaises(m.SModelsError):
            rows('省', overrides={'不存在': 'opus'})

    def test_cli_refuses_override_that_breaks_reviewer_count(self):
        code, _, err = run('render', '--budget', '大', '--fast', 'sonnet', '--strong', 'opus', '--set', '审问审查者=sonnet')
        self.assertEqual(code, 1)
        self.assertIn('恰好 2', err)

    def test_missing_fast_model_is_an_error(self):
        code, _, err = run('render', '--budget', '省')
        self.assertEqual(code, 1)
        self.assertIn('--fast', err)


class CheckTest(unittest.TestCase):
    def test_rendered_blocks_pass_their_own_check(self):
        for budget in ('省', '中', '大', '不限', 'skip'):
            b = m.normalize_budget(budget)
            result = m.check_text(m.render_block(b, rows(budget)), ['sonnet', 'opus'])
            self.assertEqual(result['status'], 'ok', (budget, result['problems']))

    def test_missing_and_half_blocks(self):
        self.assertEqual(m.check_text('随便写点\n')['status'], 'missing')
        with self.assertRaises(m.SModelsError):
            m.check_text('# s 模型配置\n修 bug: sonnet\n')

    def test_wrong_count_bad_effort_and_unknown_model_are_problems(self):
        block = m.render_block('大', rows('大')).replace('审问审查者: sonnet, opus', '审问审查者: sonnet')
        block = block.replace('大（xhigh）', '大（max）').replace('修 bug: sonnet', '修 bug: gpt-x')
        problems = m.check_text(block, ['sonnet', 'opus'])['problems']
        self.assertTrue(any('审问审查者' in p for p in problems))
        self.assertTrue(any('max' in p for p in problems))
        self.assertTrue(any('gpt-x' in p for p in problems))

    def test_old_english_block_is_read_with_notes(self):
        old = '# s model configuration\n# budget: small (medium)\nbug-fix: opus\narena runners: sonnet\n# end s model configuration\n'
        result = m.check_text(old)
        self.assertEqual(result['budget'], '省')
        self.assertEqual(result['rows']['修 bug'], 'opus')
        self.assertTrue(any('旧英文' in n for n in result['notes']))


class WriteTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / 'rules' / 's-models.md'

    def block(self, budget='省'):
        return m.render_block(m.normalize_budget(budget), rows(budget))

    def test_preview_does_not_write(self):
        result = m.write_file(self.path, self.block(), apply=False)
        self.assertEqual(result['action'], 'create')
        self.assertFalse(self.path.exists())

    def test_replace_keeps_user_text_and_backs_up_once(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text('前面\n\n' + self.block('省') + '\n\n后面\n', encoding='utf-8')
        first = m.write_file(self.path, self.block('大'), apply=True)
        self.assertEqual(first['action'], 'replace')
        self.assertIsNotNone(first['backup'])
        text = self.path.read_text(encoding='utf-8')
        self.assertTrue(text.startswith('前面\n\n# s 模型配置'))
        self.assertTrue(text.endswith('# s 模型配置结束\n\n后面\n'))
        self.assertIn('大（xhigh）', text)
        second = m.write_file(self.path, self.block('中'), apply=True)
        self.assertIsNone(second['backup'])
        self.assertIn('省（medium）', Path(first['backup']).read_text(encoding='utf-8'))

    def test_rerun_with_same_block_is_unchanged(self):
        m.write_file(self.path, self.block(), apply=True)
        self.assertEqual(m.write_file(self.path, self.block(), apply=True)['action'], 'unchanged')

    def test_old_markers_are_replaced_and_crlf_kept(self):
        self.path.parent.mkdir(parents=True)
        old = '用户\r\n# s model configuration\r\nbug-fix: opus\r\n# end s model configuration\r\n'
        self.path.write_bytes(old.encode('utf-8'))
        m.write_file(self.path, self.block(), apply=True)
        data = self.path.read_bytes().decode('utf-8')
        self.assertNotIn('s model configuration', data)
        self.assertNotIn('\n', data.replace('\r\n', ''))
        self.assertTrue(data.startswith('用户\r\n# s 模型配置\r\n'))

    def test_half_block_refuses_to_write(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text('# s 模型配置\n修 bug: sonnet\n', encoding='utf-8')
        with self.assertRaises(m.SModelsError):
            m.write_file(self.path, self.block(), apply=True)
        self.assertEqual(self.path.read_text(encoding='utf-8'), '# s 模型配置\n修 bug: sonnet\n')


class ContractTest(unittest.TestCase):
    def test_script_roles_match_skill_template_and_role_keys(self):
        text = (SKILL / 'SKILL.md').read_text(encoding='utf-8')
        template = re.search(r'```\n(# s 模型配置\n.*?# s 模型配置结束)\n```', text, re.S).group(1).splitlines()
        self.assertEqual(template[:4], list(m.HEADER))
        keys = [line.split(':')[0] for line in template if not line.startswith('#')]
        self.assertEqual(tuple(keys), m.ROLE_KEYS)
        table = (SKILL / 'references/role-keys.md').read_text(encoding='utf-8')
        pairs = re.findall(r'^\| (.+?) \| (.+?) \|$', table, re.M)[1:]
        self.assertEqual({new: old for new, old in pairs}, {new: old for new, old, _ in m.ROLES})


if __name__ == '__main__':
    unittest.main()
