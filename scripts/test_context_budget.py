"""Keep the resident-context estimate honest and under its cap."""
import unittest

import context_budget


class ContextBudgetTest(unittest.TestCase):
    def test_estimate_counts_cjk_per_character_and_latin_per_four(self):
        self.assertEqual(context_budget.estimate(''), 0)
        self.assertEqual(context_budget.estimate('中文'), 2)
        self.assertEqual(context_budget.estimate('abcd'), 1)
        self.assertEqual(context_budget.estimate('abcde'), 2)
        self.assertEqual(context_budget.estimate('中文abcd，'), 4)

    def test_only_auto_skills_are_counted(self):
        labels = {label for label, _ in context_budget.measure()}
        self.assertIn('skill tdd', labels)
        self.assertNotIn('skill docx', labels)
        self.assertNotIn('skill wukong-mode', labels)
        for part in ('global rules (AGENTS.md)', 'SessionStart hook line', 'prompt-sharpen note (per message)'):
            self.assertIn(part, labels)

    def test_current_tree_is_under_the_cap(self):
        self.assertEqual(context_budget.problems(), [])

    def test_over_the_cap_names_the_largest_parts(self):
        found = context_budget.problems(limit=10)
        self.assertEqual(len(found), 1)
        self.assertIn('global rules (AGENTS.md)', found[0])


if __name__ == '__main__':
    unittest.main()
