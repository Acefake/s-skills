"""setup-s-models 的规则脚本：生成、校验、写入都要结果固定。"""
import importlib.util
import json
import os
import stat
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
        self.assertEqual(r['审问审查者'], 'sonnet')

    def test_medium_gives_judgment_to_strong_and_one_or_two_reviewers(self):
        r = rows('中')
        self.assertEqual(r['判断和写作'], 'opus')
        self.assertEqual(r['修 bug'], 'sonnet')
        self.assertEqual(r['审问审查者'], 'sonnet, opus')
        self.assertEqual(rows('中', strong='sonnet')['审问审查者'], 'sonnet')

    def test_large_is_exactly_fast_then_strong(self):
        self.assertEqual(rows('大')['审问审查者'], 'sonnet, opus')
        self.assertEqual(rows('large')['审问审查者'], 'sonnet, opus')

    def test_unlimited_adds_third_family_without_duplicates(self):
        self.assertEqual(rows('不限', third='haiku')['审问审查者'], 'sonnet, opus, haiku')
        self.assertEqual(rows('不限', third='opus')['审问审查者'], 'sonnet, opus')

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
        self.assertIn('审问审查者: sonnet, opus', block)

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


class RoleEffortTest(unittest.TestCase):
    def test_every_item_carries_budget_level_hardest_one_up(self):
        r = m.add_efforts(rows('省'), '省', None)
        self.assertEqual(r['修 bug'], 'sonnet（medium）')
        self.assertEqual(r['最难的任务'], 'opus（high）')
        self.assertEqual(m.add_efforts(rows('不限'), '不限', None)['最难的任务'], 'opus（max）')

    def test_each_reviewer_item_has_its_own_level(self):
        r = m.add_efforts(rows('大'), '大', None)
        self.assertEqual(r['审问审查者'], 'sonnet（xhigh）, opus（xhigh）')

    def test_existing_level_is_kept_and_actual_effort_is_used(self):
        r = m.add_efforts({**rows('中'), '修 bug': 'sonnet（low）'}, '中', 'medium')
        self.assertEqual(r['修 bug'], 'sonnet（low）')
        self.assertEqual(r['写功能和重构'], 'sonnet（medium）')

    def test_inherit_rows_can_carry_level(self):
        r = m.add_efforts(m.render_rows('中', None, None, inherit=True), '中', None)
        self.assertEqual(r['修 bug'], 'inherit-parent（high）')

    def test_cli_role_effort_block_passes_check_with_model_names(self):
        code, out, _ = run('render', '--budget', '大', '--fast', 'sonnet', '--strong', 'opus', '--role-effort')
        self.assertEqual(code, 0)
        self.assertIn('最难的任务: opus（max）', out)
        result = m.check_text(out, ['sonnet', 'opus'])
        self.assertEqual(result['status'], 'ok', result['problems'])

    def test_check_rejects_bad_level_and_unknown_model_inside_suffix(self):
        block = m.render_block('省', rows('省')).replace('修 bug: sonnet', '修 bug: sonnet（ultra）')
        self.assertTrue(any('ultra' in p for p in m.check_text(block)['problems']))
        block = m.render_block('省', rows('省')).replace('修 bug: sonnet', '修 bug: gpt-x（high）')
        self.assertTrue(any('gpt-x' in p for p in m.check_text(block, ['sonnet', 'opus'])['problems']))

    def test_every_consumer_skill_points_to_the_value_format(self):
        for name in ('interrogate', 'swarm', 'why', 'how', 'reflect'):
            text = (ROOT / f'plugins/s-atlas/skills/{name}/SKILL.md').read_text(encoding='utf-8')
            self.assertIn('../setup-s-models/references/role-keys.md', text, name)

    def test_docs_tell_dispatchers_to_pass_effort(self):
        tools = (ROOT / 'plugins/s-atlas/skills/s-router/references/claude-code-tools.md').read_text(encoding='utf-8')
        self.assertIn('每次派发都要传', tools)
        keys = (SKILL / 'references/role-keys.md').read_text(encoding='utf-8')
        self.assertIn('模型（档位）', keys)
        self.assertIn('--role-effort', (SKILL / 'SKILL.md').read_text(encoding='utf-8'))


class ResolveTest(unittest.TestCase):
    def block(self, role_effort=True, budget='大'):
        r = rows(budget)
        if role_effort:
            r = m.add_efforts(r, m.normalize_budget(budget), None)
        return m.render_block(m.normalize_budget(budget), r)

    def test_splits_model_and_level_per_item(self):
        result = m.resolve_role(self.block(), '审问审查者')
        self.assertEqual(result['items'], [{'model': 'sonnet', 'effort': 'xhigh'}, {'model': 'opus', 'effort': 'xhigh'}])

    def test_plain_rows_fall_back_to_budget_level(self):
        result = m.resolve_role(self.block(role_effort=False, budget='中'), '修 bug')
        self.assertEqual(result['items'], [{'model': 'sonnet', 'effort': 'high'}])

    def test_inherit_means_no_model_and_old_keys_work(self):
        text = '# s model configuration\n# budget: small (medium)\nbug-fix: inherit-parent\n# end s model configuration\n'
        self.assertEqual(m.resolve_role(text, 'bug-fix')['items'], [{'model': None, 'effort': 'medium'}])

    def test_missing_budget_defaults_to_xhigh_and_errors_are_clear(self):
        text = '# s 模型配置\n修 bug: sonnet\n# s 模型配置结束\n'
        self.assertEqual(m.resolve_role(text, '修 bug')['items'][0]['effort'], 'xhigh')
        with self.assertRaises(m.SModelsError):
            m.resolve_role(text, '审问审查者')
        with self.assertRaises(m.SModelsError):
            m.resolve_role('没有配置\n', '修 bug')

    def test_cli_resolve_prints_model_and_level(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'r.md'
            path.write_text(self.block(), encoding='utf-8')
            code, out, _ = run('resolve', str(path), '最难的任务')
        self.assertEqual((code, out.strip()), (0, 'opus\tmax'))

    def test_claude_code_doc_does_not_promise_unverified_full_ids(self):
        tools = (ROOT / 'plugins/s-atlas/skills/s-router/references/claude-code-tools.md').read_text(encoding='utf-8')
        self.assertNotIn('，或完整 ID。', tools)
        self.assertIn('InputValidationError', tools)


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
        old = '# s model configuration\n# budget: small (medium)\nbug-fix: opus\ninterrogate reviewers: sonnet\n# end s model configuration\n'
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
        self.assertNotIn('\r\r', data)
        self.assertTrue(data.startswith('用户\r\n# s 模型配置\r\n'))

    def test_append_to_crlf_file_keeps_user_lines_and_bom(self):
        self.path.parent.mkdir(parents=True)
        original = b'\xef\xbb\xbf# my rules\r\nkeep me\r\n'
        self.path.write_bytes(original)
        result = m.write_file(self.path, self.block(), apply=True)
        self.assertEqual(result['action'], 'append')
        data = self.path.read_bytes()
        self.assertTrue(data.startswith(b'\xef\xbb\xbf# my rules\r\nkeep me\r\n\r\n# s '))
        self.assertNotIn(b'\r\r', data)
        self.assertNotIn(b'\n', data.replace(b'\r\n', b''))
        self.assertEqual(Path(result['backup']).read_bytes(), original)
        self.assertEqual(m.write_file(self.path, self.block(), apply=True)['action'], 'unchanged')

    def test_replace_keeps_form_feed_and_trailing_blank_lines(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_bytes(('a\fb\n\n' + self.block('省') + '\n\nend\n\n').encode('utf-8'))
        m.write_file(self.path, self.block('大'), apply=True)
        data = self.path.read_bytes().decode('utf-8')
        self.assertTrue(data.startswith('a\fb\n\n# s 模型配置'))
        self.assertTrue(data.endswith('# s 模型配置结束\n\nend\n\n'))

    def test_read_only_file_is_refused_without_leftovers(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text('用户\n', encoding='utf-8')
        os.chmod(self.path, stat.S_IREAD)
        self.addCleanup(os.chmod, self.path, stat.S_IREAD | stat.S_IWRITE)
        with self.assertRaises(m.SModelsError):
            m.write_file(self.path, self.block(), apply=True)
        self.assertEqual(sorted(p.name for p in self.path.parent.iterdir()), ['s-models.md'])

    def test_half_block_refuses_to_write(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text('# s 模型配置\n修 bug: sonnet\n', encoding='utf-8')
        with self.assertRaises(m.SModelsError):
            m.write_file(self.path, self.block(), apply=True)
        self.assertEqual(self.path.read_text(encoding='utf-8'), '# s 模型配置\n修 bug: sonnet\n')


class ThreeTierTest(unittest.TestCase):
    def test_light_only_changes_new_role_and_keeps_reviewers(self):
        for budget in ('省', '中', '大', '不限'):
            original = rows(budget)
            actual = rows(budget, light='small')
            self.assertEqual(actual['检索和简单任务'], 'small')
            self.assertEqual({k: v for k, v in actual.items() if k != '检索和简单任务'},
                             {k: v for k, v in original.items() if k != '检索和简单任务'})
        self.assertEqual(rows('不限', light='small', third='extra')['审问审查者'], 'sonnet, opus, extra')

    def test_default_inherit_and_override(self):
        self.assertEqual(rows('中')['检索和简单任务'], 'sonnet')
        self.assertEqual(m.render_rows('中', None, None, inherit=True)['检索和简单任务'], 'inherit-parent')
        self.assertEqual(rows('中', light='small', overrides={'lookup and simple tasks': 'auto'})['检索和简单任务'], 'auto')

    def test_light_effort_is_capped_but_explicit_level_is_kept(self):
        r = m.add_efforts(rows('大', light='small'), '大', None)
        self.assertEqual(r['检索和简单任务'], 'small（medium）')
        self.assertEqual(r['写功能和重构'], 'sonnet（xhigh）')
        self.assertEqual(m.add_efforts(rows('大'), '大', 'low')['检索和简单任务'], 'sonnet（low）')
        r = rows('大', overrides={'检索和简单任务': 'small（high）'})
        self.assertEqual(m.add_efforts(r, '大', None)['检索和简单任务'], 'small（high）')

    def test_resolve_plain_light_caps_budget_and_accepts_english_key(self):
        block = m.render_block('大', rows('大', light='small'))
        expected = [{'model': 'small', 'effort': 'medium'}]
        self.assertEqual(m.resolve_role(block, 'lookup and simple tasks')['items'], expected)
        block = block.replace('检索和简单任务: small', '检索和简单任务: small（high）')
        self.assertEqual(m.resolve_role(block, '检索和简单任务')['items'][0]['effort'], 'high')

    def test_old_config_keeps_original_roles_without_light_error(self):
        current = m.render_block('大', rows('大'))
        old = '\n'.join(line for line in current.splitlines() if not line.startswith('检索和简单任务:'))
        result = m.check_text(old, ['sonnet', 'opus'])
        self.assertEqual(result['status'], 'ok', result['problems'])
        self.assertNotIn('检索和简单任务', result['rows'])
        self.assertEqual(m.resolve_role(old, '修 bug')['items'][0]['model'], 'sonnet')
        with self.assertRaises(m.SModelsError):
            m.resolve_role(old, '检索和简单任务')

    def test_cli_light_validation_and_render(self):
        code, out, _ = run('render', '--budget', '中', '--fast', 'normal', '--strong', 'complex', '--light', 'small', '--role-effort')
        self.assertEqual(code, 0)
        self.assertIn('检索和简单任务: small（medium）', out)
        self.assertEqual(m.check_text(out, ['normal', 'complex', 'small'])['status'], 'ok')
        self.assertEqual(m.check_text(out, ['normal', 'complex'])['status'], 'problems')
        code, _, _ = run('render', '--budget', '中', '--fast', 'normal', '--light', 'small', '--set', '检索和简单任务=small（ultra）')
        self.assertEqual(code, 1)
        code, _, err = run('render', '--budget', '大', '--fast', 'normal', '--role-effort', '--effort', 'ultra')
        self.assertEqual(code, 1)
        self.assertIn('未知推理档位', err)
        code, _, err = run('render', '--budget', '省', '--fast', 'normal', '--role-effort', '--effort', 'high')
        self.assertEqual(code, 1)
        self.assertIn('只能下调', err)

    def test_write_preserves_existing_roles_and_set_wins(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'rules.md'
            old = m.render_block('中', rows('中', overrides={'修 bug': 'chosen（low）'}))
            old = '\n'.join(line for line in old.splitlines() if not line.startswith('检索和简单任务:'))
            source = '用户前文\n' + old + '\n用户后文\n'
            path.write_text(source, encoding='utf-8')
            args = ('write', str(path), '--budget', '中', '--fast', 'normal', '--strong', 'complex', '--light', 'small', '--json')
            code, out, _ = run(*args)
            self.assertEqual(code, 0)
            preview = json.loads(out)
            self.assertFalse(preview['applied'])
            self.assertIn('修 bug: chosen（low）', preview['block'])
            self.assertIn('检索和简单任务: small', preview['block'])
            self.assertEqual(path.read_text(encoding='utf-8'), source)
            code, out, _ = run(*args, '--set', '修 bug=override', '--apply')
            self.assertEqual(code, 0)
            self.assertIn('修 bug: override', path.read_text(encoding='utf-8'))
            self.assertTrue(path.read_text(encoding='utf-8').startswith('用户前文\n'))
            self.assertTrue(path.read_text(encoding='utf-8').endswith('用户后文\n'))
            self.assertEqual(run(*args, '--set', '修 bug=override', '--apply')[0], 0)
            self.assertEqual(run(*args, '--replace-roles', '--apply')[0], 0)
            self.assertIn('修 bug: normal', path.read_text(encoding='utf-8'))

    def test_existing_light_choice_is_preserved_and_can_be_changed_explicitly(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'rules.md'
            path.write_text(m.render_block('中', rows('中', light='chosen')), encoding='utf-8')
            args = ('write', str(path), '--budget', '中', '--fast', 'normal', '--light', 'new', '--json')
            code, out, _ = run(*args)
            self.assertEqual(code, 0)
            self.assertIn('检索和简单任务: chosen', json.loads(out)['block'])
            code, out, _ = run(*args, '--set', 'lookup and simple tasks=new')
            self.assertEqual(code, 0)
            self.assertIn('检索和简单任务: new', json.loads(out)['block'])

    def test_budget_change_does_not_silently_rewrite_preserved_reviewers(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'rules.md'
            original = m.render_block('大', rows('大'))
            path.write_text(original, encoding='utf-8')
            args = ('write', str(path), '--budget', '省', '--fast', 'normal', '--strong', 'complex', '--apply')
            code, _, err = run(*args)
            self.assertEqual(code, 1)
            self.assertIn('恰好 1', err)
            self.assertEqual(path.read_text(encoding='utf-8'), original)
            self.assertEqual(run(*args, '--replace-roles')[0], 0)

    def test_explicit_inherit_replaces_existing_models(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'rules.md'
            path.write_text(m.render_block('中', rows('中', light='chosen')), encoding='utf-8')
            code, out, _ = run('write', str(path), '--budget', '中', '--inherit', '--json')
            self.assertEqual(code, 0)
            result = m.check_text(json.loads(out)['block'])
            self.assertEqual(set(result['rows'].values()), {'inherit-parent'})

    def test_confirmed_model_list_rejects_unknown_before_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'rules.md'
            args = ('write', str(path), '--budget', '中', '--fast', 'normal', '--strong', 'complex', '--light', 'unknown', '--models', 'normal,complex', '--apply')
            code, _, err = run(*args)
            self.assertEqual(code, 1)
            self.assertIn('未确认的模型', err)
            self.assertFalse(path.exists())
            code, _, _ = run(*args, '--set', '检索和简单任务=normal')
            self.assertEqual(code, 0)
            self.assertTrue(path.exists())


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
