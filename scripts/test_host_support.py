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
    def test_retired_hosts_and_manifests_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ('OpenCode', 'Pi', 'Cursor', 'WorkBuddy', 'CodeBuddy'):
                (root / 'README.md').write_text('Supported: ' + name + '\n', encoding='utf-8')
                with self.subTest(name=name), patch.object(check_marketplace, 'ROOT', root):
                    problems = check_marketplace.Problems()
                    check_marketplace.check_supported_hosts(problems)
                    self.assertFalse(problems.ok(), name)
            (root / 'README.md').write_text('Supported: Codex, Claude Code, Antigravity.\n', encoding='utf-8')
            for relative in (
                '.cursor-plugin/marketplace.json',
                'plugins/wukong/.cursor-plugin/plugin.json',
                '.codebuddy-plugin/marketplace.json',
                'plugins/wukong/.codebuddy-plugin/plugin.json',
            ):
                manifest = root / relative
                manifest.parent.mkdir(parents=True, exist_ok=True)
                manifest.write_text('{}', encoding='utf-8')
                with self.subTest(manifest=relative), patch.object(check_marketplace, 'ROOT', root):
                    problems = check_marketplace.Problems()
                    check_marketplace.check_supported_hosts(problems)
                    self.assertFalse(problems.ok(), relative)
                manifest.unlink()

    def test_antigravity_host_name_and_guide_are_allowed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plugin = root / 'plugins/wukong'
            guide = plugin / 'skills/wukong-router/references/antigravity-tools.md'
            guide.parent.mkdir(parents=True)
            guide.write_text('# Antigravity\n', encoding='utf-8')
            (root / 'README.md').write_text('Antigravity: agy plugin install ./plugins/wukong\n', encoding='utf-8')
            (plugin / 'HOSTS.md').write_text('[Antigravity](skills/wukong-router/references/antigravity-tools.md)\n', encoding='utf-8')
            with patch.object(check_marketplace, 'ROOT', root):
                problems = check_marketplace.Problems()
                check_marketplace.check_supported_hosts(problems)
                self.assertTrue(problems.ok(), problems.items)

    def test_hermes_agent_name_is_allowed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plugin = root / 'plugins/wukong'
            skill = plugin / 'skills/wukong-init'
            skill.mkdir(parents=True)
            (root / 'README.md').write_text('模型配置识别 Hermes agent。\n', encoding='utf-8')
            (plugin / 'HOSTS.md').write_text(
                '[Hermes](skills/wukong-router/references/hermes-tools.md)\n',
                encoding='utf-8',
            )
            guide = plugin / 'skills/wukong-router/references/hermes-tools.md'
            guide.parent.mkdir(parents=True)
            guide.write_text('# Hermes agent\n', encoding='utf-8')
            (skill / 'SKILL.md').write_text('确认宿主时包含 Hermes agent。\n', encoding='utf-8')
            with patch.object(check_marketplace, 'ROOT', root):
                problems = check_marketplace.Problems()
                check_marketplace.check_supported_hosts(problems)
                self.assertTrue(problems.ok(), problems.items)

    def test_only_supported_manifests_are_versioned(self):
        self.assertEqual(set(marketplace_lib.MANIFEST_REL_PATHS), {
            'plugin.json', '.claude-plugin/plugin.json',
        })

    def test_host_validation_rejects_an_obsolete_adapter(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'README.md').write_text('Supported: Codex, Claude Code, Antigravity.\n', encoding='utf-8')
            with patch.object(check_marketplace, 'ROOT', root):
                problems = check_marketplace.Problems()
                check_marketplace.check_supported_hosts(problems)
                self.assertTrue(problems.ok(), problems.items)
                (root / '.cursor-plugin').mkdir()
                (root / '.cursor-plugin/marketplace.json').write_text('{}', encoding='utf-8')
                problems = check_marketplace.Problems()
                check_marketplace.check_supported_hosts(problems)
                self.assertFalse(problems.ok())

    def test_host_validation_allows_t3_orchestration_instructions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / 'plugins/wukong/skills/example'
            skill.mkdir(parents=True)
            (skill / 'SKILL.md').write_text('Use T3 Code delegate_task before proceeding.\n', encoding='utf-8')
            with patch.object(check_marketplace, 'ROOT', root):
                problems = check_marketplace.Problems()
                check_marketplace.check_supported_hosts(problems)
                self.assertTrue(problems.ok(), problems.items)

    def test_policy_update_does_not_rewrite_skill_instructions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / 'plugins/wukong/skills/example'
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
            plugin = root / 'plugins/wukong'
            plugin.mkdir(parents=True)
            (plugin / 'HOSTS.md').write_text('[Codex](skills/wukong-router/references/codex-tools.md)', encoding='utf-8')
            with patch.object(check_marketplace, 'ROOT', root):
                problems = check_marketplace.Problems()
                check_marketplace.check_supported_hosts(problems)
                self.assertFalse(problems.ok())
                guide = plugin / 'skills/wukong-router/references/codex-tools.md'
                guide.parent.mkdir(parents=True)
                guide.write_text('# Codex\n', encoding='utf-8')
                problems = check_marketplace.Problems()
                check_marketplace.check_supported_hosts(problems)
                self.assertTrue(problems.ok(), problems.items)

    def test_host_guides_resolve_in_project_link_layout(self):
        source = marketplace_lib.ROOT / 'plugins/wukong'
        with tempfile.TemporaryDirectory() as directory:
            installed = Path(directory) / '.agents'
            installed.mkdir()
            (installed / 'HOSTS.md').write_bytes((source / 'HOSTS.md').read_bytes())
            guides = ('codex-tools.md', 'claude-code-tools.md', 'antigravity-tools.md', 'dsh-tools.md', 'hermes-tools.md')
            for filename in guides:
                original = source / 'skills/wukong-router/references' / filename
                self.assertTrue(original.is_file(), str(original))
                destination = installed / 'skills/wukong-router/references' / filename
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(original.read_bytes())
                self.assertTrue(destination.is_file())
            # Project installation places HOSTS beside skills/, as plugin packaging does.
            text = (installed / 'HOSTS.md').read_text(encoding='utf-8')
            for filename in guides:
                relative = 'skills/wukong-router/references/' + filename
                self.assertIn('(' + relative + ')', text)
                self.assertTrue((installed / relative).is_file())

    @unittest.skipUnless(os.name == 'nt' and (shutil.which('pwsh') or shutil.which('powershell')), 'Windows PowerShell junctions are required')
    def test_codex_install_migrates_legacy_junctions_and_protects_foreign_entries(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'scripts').mkdir()
            shutil.copyfile(marketplace_lib.ROOT/'scripts/install_local_skills.ps1', root/'scripts/install_local_skills.ps1')
            plugin = root/'plugins/wukong'
            (plugin/'skills/one').mkdir(parents=True)
            (plugin/'skills/one/SKILL.md').write_text('# one', encoding='utf-8')
            (plugin/'HOSTS.md').write_text('# host reference', encoding='utf-8')

            dest_skills = root/'.agents/skills'
            dest_skills.mkdir(parents=True)
            foreign_target = root/'other-repo/skills/foreign'
            foreign_target.mkdir(parents=True)
            shell = shutil.which('powershell') or shutil.which('pwsh')

            def junction(link, target):
                command = f"$ErrorActionPreference = 'Stop'; New-Item -ItemType Junction -Path '{link}' -Target '{target}' | Out-Null"
                made = subprocess.run([shell, '-NoProfile', '-Command', command], capture_output=True, text=True, env=powershell_environment(shell))
                self.assertEqual(made.returncode, 0, made.stdout + made.stderr)
                self.assertTrue(os.path.lexists(str(link)), link)

            def dangling_legacy_junction(name):
                # 旧目录早已删除，只剩悬空 Junction：先建目标再建链接，最后删掉目标。
                target = root/'plugins/s-atlas/skills'/name
                target.mkdir(parents=True)
                junction(dest_skills/name, target)
                target.rmdir()

            def dangling_junction(name, target):
                # 目标先建后删，只留下悬空 Junction。
                target.mkdir(parents=True)
                junction(dest_skills/name, target)
                target.rmdir()

            dangling_legacy_junction('one')
            dangling_legacy_junction('retired-skill')
            junction(dest_skills/'foreign', foreign_target)
            dangling_junction('removed-skill', plugin/'skills/removed-skill')
            dangling_junction('foreign-gone', root/'other-repo/skills/gone')

            result = subprocess.run(
                [shell, '-NoProfile', '-File', str(root/'scripts/install_local_skills.ps1')],
                capture_output=True, text=True, env=powershell_environment(shell),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual((dest_skills/'one/SKILL.md').read_text(encoding='utf-8'), '# one')
            self.assertEqual(Path(os.path.realpath(dest_skills/'one')), Path(os.path.realpath(plugin/'skills/one')))
            self.assertFalse(os.path.lexists(str(dest_skills/'retired-skill')))
            self.assertTrue((dest_skills/'foreign').exists())
            self.assertTrue(foreign_target.is_dir())
            self.assertFalse(os.path.lexists(str(dest_skills/'removed-skill')))
            self.assertTrue(os.path.lexists(str(dest_skills/'foreign-gone')))

            # 场景一：插件技能名上已有一个真实目录。必须拒绝，原内容不动，
            # 并且校验先于清理，所以同一轮里的旧 Junction 也不能被删。
            (plugin/'skills/two').mkdir(parents=True)
            (plugin/'skills/two/SKILL.md').write_text('# two', encoding='utf-8')
            (dest_skills/'two').mkdir()
            (dest_skills/'two/keep.txt').write_text('keep', encoding='utf-8')
            dangling_legacy_junction('stale')
            dangling_junction('removed-later', plugin/'skills/removed-later')
            rejected = subprocess.run(
                [shell, '-NoProfile', '-File', str(root/'scripts/install_local_skills.ps1')],
                capture_output=True, text=True, env=powershell_environment(shell),
            )
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn('two', rejected.stdout + rejected.stderr)
            self.assertEqual((dest_skills/'two/keep.txt').read_text(encoding='utf-8'), 'keep')
            self.assertTrue(os.path.lexists(str(dest_skills/'stale')))
            self.assertTrue(os.path.lexists(str(dest_skills/'removed-later')))

            # 场景二：插件技能名上是指向别处的 Junction，同样拒绝且不改动它。
            shutil.rmtree(dest_skills/'two')
            shutil.rmtree(plugin/'skills/two')
            (plugin/'skills/foreign').mkdir(parents=True)
            (plugin/'skills/foreign/SKILL.md').write_text('# foreign', encoding='utf-8')
            rejected = subprocess.run(
                [shell, '-NoProfile', '-File', str(root/'scripts/install_local_skills.ps1')],
                capture_output=True, text=True, env=powershell_environment(shell),
            )
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn('foreign', rejected.stdout + rejected.stderr)
            self.assertTrue((dest_skills/'foreign').exists())
            self.assertTrue(os.path.lexists(str(dest_skills/'stale')))


if __name__ == '__main__':
    unittest.main()
