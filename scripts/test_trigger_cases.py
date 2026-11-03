"""Keep trigger_cases.json in step with the skills and the eval parser."""
import unittest

import eval_triggers


class TriggerCasesTest(unittest.TestCase):
    def setUp(self):
        self.candidates = eval_triggers.load_candidates()
        self.cases = eval_triggers.load_cases()

    def test_expected_skills_are_auto_invocable(self):
        for case in self.cases:
            self.assertTrue(case["prompt"].strip())
            self.assertTrue(case["expect"], case["prompt"])
            for name in case["expect"]:
                if name == eval_triggers.NONE:
                    self.assertEqual(case["expect"], [name], f"{case['prompt']} mixes none with skills")
                    continue
                self.assertIn(name, self.candidates, f"{case['prompt']} expects {name}")

    def test_has_negative_cases(self):
        negatives = [case for case in self.cases if case["expect"] == [eval_triggers.NONE]]
        self.assertGreaterEqual(len(negatives), 3, "keep cases that should not trigger any skill")

    def test_prompts_are_unique(self):
        prompts = [case["prompt"] for case in self.cases]
        self.assertEqual(len(prompts), len(set(prompts)))

    def test_every_auto_skill_has_a_case(self):
        covered = {name for case in self.cases for name in case["expect"]}
        missing = sorted(name for name in self.candidates if name not in covered)
        self.assertEqual(missing, [], "add a trigger case for each new auto-invocable skill")

    def test_router_is_not_a_candidate(self):
        self.assertNotIn("s-router", self.candidates)

    def test_parse_choice_reads_bare_and_wrapped_answers(self):
        names = {"tdd", "systematic-debugging"}
        self.assertEqual(eval_triggers.parse_choice("tdd\n", names), "tdd")
        self.assertEqual(eval_triggers.parse_choice("`systematic-debugging`.", names), "systematic-debugging")
        self.assertEqual(eval_triggers.parse_choice("none", names), "none")
        self.assertEqual(
            eval_triggers.parse_choice("The answer is systematic-debugging.\nIt fits bugs.", names),
            "systematic-debugging",
        )
        self.assertEqual(eval_triggers.parse_choice("**tdd**\n\nReason: not systematic-debugging", names), "tdd")
        self.assertEqual(eval_triggers.parse_choice("None", names), "none")
        self.assertEqual(eval_triggers.parse_choice("", names), "")


if __name__ == "__main__":
    unittest.main()
