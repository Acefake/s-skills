"""Check the supported distribution and host adaptation contract."""
import tempfile
import unittest
import shutil
import subprocess
import os
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import check_marketplace
import marketplace_lib
import update_skill_policies


def powershell_environment(shell):
    environment = os.environ.copy()
    if Path(shell).name.lower() == 'powershell.exe':
        # A Python process launched by PowerShell 7 can inherit its incompatible modules.
        native_modules = Path(shell).parent / 'Modules'
        environment['PSModulePath'] = str(native_modules) + os.pathsep + environment.get('PSModulePath', '')
    return environment


class HostSupportTest(unittest.TestCase):
    def test_workbuddy_and_its_compatibility_directories_are_allowed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'README.md').write_text('WorkBuddy: .codebuddy/skills/ and ~/.codebuddy/CODEBUDDY.md\n', encoding='utf-8')
            with patch.object(check_marketplace, 'ROOT', root):
                problems = check_marketplace.Problems()
                check_marketplace.check_supported_hosts(problems)
                self.assertTrue(problems.ok(), problems.items)

    def test_adding_workbuddy_does_not_enable_other_retired_products(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ('T3 Code', 'OpenCode', 'CodeBuddy', 'Antigravity', 'Pi'):
                (root/'README.md').write_text('Supported: '+name, encoding='utf-8')
                with self.subTest(name=name), patch.object(check_marketplace, 'ROOT', root):
                    problems = check_marketplace.Problems()
                    check_marketplace.check_supported_hosts(problems)
                    self.assertFalse(problems.ok())

    @unittest.skipUnless(os.name == 'nt' and (shutil.which('pwsh') or shutil.which('powershell')), 'Windows PowerShell junctions are required')
    def test_workbuddy_project_install_and_repeat_preserve_skill_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'scripts').mkdir()
            shutil.copyfile(marketplace_lib.ROOT/'scripts/install_local_skills.ps1', root/'scripts/install_local_skills.ps1')
            plugin = root/'plugins/s-atlas'
            for name in ('one', 'two'):
                skill = plugin/'skills'/name
                skill.mkdir(parents=True)
                (skill/'SKILL.md').write_text('# '+name, encoding='utf-8')
            (plugin/'HOSTS.md').write_text('# host reference', encoding='utf-8')
            shell = shutil.which('powershell') or shutil.which('pwsh')
            command = [shell, '-NoProfile', '-File', str(root/'scripts/install_local_skills.ps1'), '-HostName', 'workbuddy']
            for _ in range(2):
                result = subprocess.run(command, capture_output=True, text=True, env=powershell_environment(shell))
                self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
                self.assertEqual((root/'.codebuddy/skills/one/SKILL.md').read_text(encoding='utf-8'), '# one')
                self.assertEqual((plugin/'skills/one/SKILL.md').read_text(encoding='utf-8'), '# one')
            (plugin/'HOSTS.md').write_text('# updated host reference', encoding='utf-8')
            updated = subprocess.run(command, capture_output=True, text=True, env=powershell_environment(shell))
            self.assertEqual(updated.returncode, 0, updated.stdout+updated.stderr)
            self.assertEqual((root/'.codebuddy/HOSTS.md').read_text(encoding='utf-8'), '# updated host reference')
            (root/'.codebuddy/HOSTS.md').write_text('user edit', encoding='utf-8')
            (plugin/'HOSTS.md').write_text('# third update', encoding='utf-8')
            rejected = subprocess.run(command, capture_output=True, text=True, env=powershell_environment(shell))
            self.assertNotEqual(rejected.returncode, 0)
            self.assertEqual((root/'.codebuddy/HOSTS.md').read_text(encoding='utf-8'), 'user edit')
            self.assertTrue((root/'.codebuddy/HOSTS.md').is_file())
            self.assertFalse((root/'.agents').exists())
            self.assertFalse((root/'.codebuddy/CODEBUDDY.md').exists())

    @unittest.skipUnless(os.name == 'nt' and (shutil.which('pwsh') or shutil.which('powershell')), 'Windows PowerShell junctions are required')
    def test_workbuddy_install_refuses_unowned_common_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'scripts').mkdir()
            shutil.copyfile(marketplace_lib.ROOT/'scripts/install_local_skills.ps1', root/'scripts/install_local_skills.ps1')
            plugin = root/'plugins/s-atlas'
            (plugin/'skills/one').mkdir(parents=True)
            (plugin/'skills/one/SKILL.md').write_text('# one', encoding='utf-8')
            (plugin/'HOSTS.md').write_text('# new host', encoding='utf-8')
            (root/'.codebuddy').mkdir()
            existing = root/'.codebuddy/HOSTS.md'
            existing.write_text('user content', encoding='utf-8')
            shell = shutil.which('powershell') or shutil.which('pwsh')
            result = subprocess.run([shell, '-NoProfile', '-File', str(root/'scripts/install_local_skills.ps1'), '-HostName', 'workbuddy'], capture_output=True, text=True, env=powershell_environment(shell))
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(existing.read_text(encoding='utf-8'), 'user content')
            self.assertFalse((root/'.codebuddy/skills/one').exists())

    def test_hermes_agent_name_is_allowed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plugin = root / 'plugins/s-atlas'
            skill = plugin / 'skills/setup-s-models'
            skill.mkdir(parents=True)
            (root / 'README.md').write_text('模型配置识别 Hermes agent。\n', encoding='utf-8')
            (plugin / 'HOSTS.md').write_text(
                '[Hermes](skills/s-router/references/hermes-tools.md)\n',
                encoding='utf-8',
            )
            guide = plugin / 'skills/s-router/references/hermes-tools.md'
            guide.parent.mkdir(parents=True)
            guide.write_text('# Hermes agent\n', encoding='utf-8')
            (skill / 'SKILL.md').write_text('确认宿主时包含 Hermes agent。\n', encoding='utf-8')
            with patch.object(check_marketplace, 'ROOT', root):
                problems = check_marketplace.Problems()
                check_marketplace.check_supported_hosts(problems)
                self.assertTrue(problems.ok(), problems.items)

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
            for filename in ('codex-tools.md', 'claude-code-tools.md', 'cursor-tools.md', 'workbuddy-tools.md', 'dsh-tools.md', 'hermes-tools.md'):
                original = source / 'skills/s-router/references' / filename
                self.assertTrue(original.is_file(), str(original))
                destination = installed / 'skills/s-router/references' / filename
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(original.read_bytes())
                self.assertTrue(destination.is_file())
            # Project installation places HOSTS beside skills/, as plugin packaging does.
            text = (installed / 'HOSTS.md').read_text(encoding='utf-8')
            for filename in ('codex-tools.md', 'claude-code-tools.md', 'cursor-tools.md', 'workbuddy-tools.md', 'dsh-tools.md', 'hermes-tools.md'):
                relative = 'skills/s-router/references/' + filename
                self.assertIn('(' + relative + ')', text)
                self.assertTrue((installed / relative).is_file())


if __name__ == '__main__':
    unittest.main()
