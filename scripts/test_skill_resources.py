"""Exercise discovery defects using isolated skill fixtures."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from contextlib import redirect_stdout
from io import StringIO

from check_marketplace import Problems, check_skill_resources
import update_skill_policies


class SkillResourcesTest(unittest.TestCase):
    def test_policy_update_preserves_metadata_and_is_repeatable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / 'plugins/s/skills/sample'
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


if __name__ == '__main__':
    unittest.main()
