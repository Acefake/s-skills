"""Exercise discovery defects using isolated skill fixtures."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from contextlib import redirect_stdout
from io import StringIO

from check_marketplace import (
    Problems,
    check_skill_resources,
    description_order_problem,
    description_trigger_problem,
    frontmatter_description,
    skill_reference_problems,
)
import update_skill_policies


class SkillResourcesTest(unittest.TestCase):
    def test_policy_update_preserves_metadata_and_is_repeatable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / 'plugins/s-atlas/skills/sample'
            (skill / 'agents').mkdir(parents=True)
            (skill / 'SKILL.md').write_text('---\nname: sample\ndescription: sample\n---\nBody\n', encoding='utf-8')
            metadata = skill / 'agents/openai.yaml'
            metadata.write_text('interface:\n  display_name: "Sample"\npolicy:\n  allow_implicit_invocation: false\ndependencies:\n  tools: []\n', encoding='utf-8')
            with patch.object(update_skill_policies, 'ROOT', root), redirect_stdout(StringIO()):
                update_skill_policies.main()
                first = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
                update_skill_policies.main()
                second = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            self.assertEqual(first, second)
            self.assertIn('display_name: "Sample"', metadata.read_text(encoding='utf-8'))
            self.assertIn('dependencies:\n  tools: []', metadata.read_text(encoding='utf-8'))
            self.assertIn('allow_implicit_invocation: true', metadata.read_text(encoding='utf-8'))

    def test_policy_and_link_defects_are_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            skill = Path(directory)
            (skill / 'agents').mkdir()
            policy = skill / 'agents/openai.yaml'
            text = '---\nname: sample\ndescription: example\ndisable-model-invocation: true\n---\n[guide](guide.md)'
            policy.write_text('policy:\n  allow_implicit_invocation: true\n', encoding='utf-8')
            problems = Problems()
            check_skill_resources(skill, text, problems)
            self.assertEqual(len(problems.items), 2)
            policy.write_text('policy:\n  allow_implicit_invocation: false\n', encoding='utf-8')
            (skill / 'guide.md').write_text('Available guide', encoding='utf-8')
            problems = Problems()
            check_skill_resources(skill, text, problems)
            self.assertTrue(problems.ok(), problems.items)

    def test_description_is_chinese_then_use_when(self):
        good = (
            '---\nname: sample\n'
            'description: "去掉 AI 腔。Use when prose sounds like AI."\n'
            '---\n'
        )
        self.assertIsNone(description_order_problem(frontmatter_description(good)))
        english_first = (
            '---\nname: sample\n'
            'description: "Use when prose sounds like AI. 中文触发：去掉 AI 腔。"\n'
            '---\n'
        )
        self.assertIsNotNone(description_order_problem(frontmatter_description(english_first)))
        self.assertIsNotNone(description_order_problem("中文：去掉 AI 腔。Use when prose sounds like AI."))
        self.assertIsNotNone(description_order_problem("去掉 AI 腔。"))
        self.assertIsNotNone(description_order_problem("中文触发：去掉 AI 腔。Use when prose sounds like AI."))

    def test_description_quotes_a_user_phrase_in_the_first_100_characters(self):
        self.assertIsNone(
            description_trigger_problem("「写个 Word」。创建文档。Use when producing a .docx.")
        )
        self.assertIsNotNone(
            description_trigger_problem("创建 Word。「写个 Word」。Use when producing a .docx.")
        )
        late = "「" + ("铺垫" * 60) + "」。Use when producing a .docx."
        self.assertGreater(late.index("」"), 100)
        self.assertIsNotNone(description_trigger_problem(late))


class SkillReferenceTest(unittest.TestCase):
    def test_old_prefix_and_archived_names_are_reported(self):
        active = {'tdd', 'swarm'}
        archived = {'test-driven-development', 'swarm'}
        text = '用 superpowers:tdd，再看 `test-driven-development` 和 `swarm`。'
        problems = skill_reference_problems(text, active, archived)
        self.assertEqual(len(problems), 2, problems)
        self.assertEqual(skill_reference_problems('用 `tdd` 和 `swarm`。', active, archived), [])

    def test_principle_without_prefix_is_reported(self):
        active = {'principle-fix-root-causes'}
        problems = skill_reference_problems('按 **fix-root-causes** 原则。', active, set())
        self.assertEqual(len(problems), 1, problems)
        self.assertEqual(skill_reference_problems('按 **principle-fix-root-causes** 原则。', active, set()), [])

    def test_bold_and_command_names_are_reported(self):
        active = {'tdd'}
        archived = {'test-driven-development', 'writing-skills'}
        text = '见 **test-driven-development**，或运行 /s-atlas:writing-skills。'
        problems = skill_reference_problems(text, active, archived)
        self.assertEqual(len(problems), 2, problems)


if __name__ == '__main__':
    unittest.main()
