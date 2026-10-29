"""Check the supported distribution and host adaptation contract."""
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import check_marketplace
import marketplace_lib
import update_skill_policies


class HostSupportTest(unittest.TestCase):
    def test_only_supported_manifests_are_versioned(self):
        self.assertEqual(set(marketplace_lib.MANIFEST_REL_PATHS), {
            'plugin.json', '.claude-plugin/plugin.json', '.cursor-plugin/plugin.json',
        })

    def test_host_validation_rejects_an_obsolete_adapter(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'README.md').write_text('Supported: Codex, Claude Code, Cursor.\n', encoding='utf-8')
            with patch.object(check_marketplace, 'ROOT', root):
                problems = check_marketplace.Problems()
                check_marketplace.check_supported_hosts(problems)
                self.assertTrue(problems.ok(), problems.items)
                (root / '.codebuddy-plugin').mkdir()
                (root / '.codebuddy-plugin/marketplace.json').write_text('{}', encoding='utf-8')
                problems = check_marketplace.Problems()
                check_marketplace.check_supported_hosts(problems)
                self.assertFalse(problems.ok())

    def test_host_validation_rejects_unsupported_active_instructions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / 'plugins/s-atlas/skills/example'
            skill.mkdir(parents=True)
            (skill / 'SKILL.md').write_text('Use T3 Code delegate_task before proceeding.\n', encoding='utf-8')
            with patch.object(check_marketplace, 'ROOT', root):
                problems = check_marketplace.Problems()
                check_marketplace.check_supported_hosts(problems)
                self.assertFalse(problems.ok())

    def test_policy_update_does_not_rewrite_skill_instructions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / 'plugins/s-atlas/skills/example'
            (skill / 'agents').mkdir(parents=True)
            instructions = '---\nname: example\ndescription: example\n---\nUse the browser and preserve the model configuration.\n'
            (skill / 'SKILL.md').write_text(instructions, encoding='utf-8')
            with patch.object(update_skill_policies, 'ROOT', root), redirect_stdout(StringIO()):
                update_skill_policies.main()
                first = (skill / 'agents/openai.yaml').read_bytes()
                update_skill_policies.main()
            self.assertEqual((skill / 'SKILL.md').read_text(encoding='utf-8'), instructions)
            self.assertEqual((skill / 'agents/openai.yaml').read_bytes(), first)

    def test_host_validation_detects_missing_platform_guide(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plugin = root / 'plugins/s-atlas'
            plugin.mkdir(parents=True)
            (plugin / 'HOSTS.md').write_text('[Codex](skills/s-router/references/codex-tools.md)', encoding='utf-8')
            with patch.object(check_marketplace, 'ROOT', root):
                problems = check_marketplace.Problems()
                check_marketplace.check_supported_hosts(problems)
                self.assertFalse(problems.ok())
                guide = plugin / 'skills/s-router/references/codex-tools.md'
                guide.parent.mkdir(parents=True)
                guide.write_text('# Codex\n', encoding='utf-8')
                problems = check_marketplace.Problems()
                check_marketplace.check_supported_hosts(problems)
                self.assertTrue(problems.ok(), problems.items)

    def test_host_guides_resolve_in_project_link_layout(self):
        source = marketplace_lib.ROOT / 'plugins/s-atlas'
        with tempfile.TemporaryDirectory() as directory:
            installed = Path(directory) / '.agents'
            installed.mkdir()
            (installed / 'HOSTS.md').write_bytes((source / 'HOSTS.md').read_bytes())
            for filename in ('codex-tools.md', 'claude-code-tools.md', 'cursor-tools.md'):
                original = source / 'skills/s-router/references' / filename
                self.assertTrue(original.is_file(), str(original))
                destination = installed / 'skills/s-router/references' / filename
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(original.read_bytes())
                self.assertTrue(destination.is_file())
            # Project installation places HOSTS beside skills/, as plugin packaging does.
            text = (installed / 'HOSTS.md').read_text(encoding='utf-8')
            for filename in ('codex-tools.md', 'claude-code-tools.md', 'cursor-tools.md'):
                relative = 'skills/s-router/references/' + filename
                self.assertIn('(' + relative + ')', text)
                self.assertTrue((installed / relative).is_file())


if __name__ == '__main__':
    unittest.main()
