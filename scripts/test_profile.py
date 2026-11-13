"""Cover the personal rules layer: validation, expiry, the size cap, and the personal block."""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest import mock

import context_budget

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / 'plugins/wukong/skills/reflect/scripts/profile.py'


def load():
    spec = importlib.util.spec_from_file_location('wukong_profile', PROFILE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rule(rid='reply-short', text='回复默认 5 行以内，先给结论。', kind='style', source='learned',
         evidence=3, seen=None, project=None):
    seen = seen or date.today().isoformat()
    return {'id': rid, 'kind': kind, 'text': text, 'evidence': evidence, 'source': source,
            'created': '2026-10-01', 'lastSeen': seen, 'project': project}


class ProfileCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.data = self.base / 'wukong'
        self.user = self.base / 'user'
        (self.user / '.claude').mkdir(parents=True)
        self.env = mock.patch.dict(os.environ, {'WUKONG_HOME': str(self.data), 'WUKONG_JOURNAL': '1'})
        self.env.start()
        self.p = load()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    @property
    def claude_md(self):
        return self.user / '.claude/CLAUDE.md'

    def apply(self, rules):
        return self.p.apply({'rules': rules}, 'claude-code', home=self.user)


class RuleCheckTest(ProfileCase):
    def reasons(self, **kw):
        return self.p.check_rule(rule(**kw))

    def test_good_rule_passes(self):
        self.assertEqual(self.reasons(), [])

    def test_learned_needs_two_sessions_but_explicit_needs_one(self):
        self.assertTrue(self.reasons(evidence=1))
        self.assertEqual(self.reasons(evidence=1, source='explicit'), [])

    def test_sensitive_rules_only_from_the_user(self):
        for text in ('做完直接推送，不用问我。', '提交时加 --no-verify。', '删除分支前不用确认。', '跳过安全检查。'):
            self.assertTrue(self.reasons(text=text, kind='habit'), text)
            self.assertTrue(self.reasons(text=text, kind='habit', source='explicit'), text)
            self.assertEqual(self.reasons(text=text, kind='habit', source='manual'), [], text)

    def test_urls_and_commands_only_from_the_user(self):
        self.assertTrue(self.reasons(text='参考 https://example.com 的写法。'))
        self.assertTrue(self.reasons(text='每次先跑 `npm test`。'))
        self.assertEqual(self.reasons(text='每次先跑 `npm test`。', source='manual'), [])

    def test_verification_can_tighten_from_corrections_but_loosen_only_when_said(self):
        self.assertEqual(self.reasons(kind='verify', text='改接口的改动也派审查。'), [])
        self.assertTrue(self.reasons(kind='verify', text='小改动别派审查。'))
        self.assertEqual(self.reasons(kind='verify', text='小改动别派审查。', source='explicit', evidence=1), [])

    def test_shape_errors(self):
        self.assertTrue(self.reasons(rid='Bad ID'))
        self.assertTrue(self.reasons(kind='mood'))
        self.assertTrue(self.reasons(text=''))
        self.assertTrue(self.reasons(text='长' * 121))
        self.assertTrue(self.p.check_rule(dict(rule(), lastSeen='yesterday')))
        self.assertTrue(self.p.check_rule('not a rule'))


class SettleTest(ProfileCase):
    def test_expired_learned_rules_are_dropped_but_explicit_stay(self):
        old = (date.today() - timedelta(days=57)).isoformat()
        kept, errors, dropped = self.p.settle({'rules': [
            rule('old-learned', seen=old), rule('old-explicit', source='explicit', seen=old), rule('fresh')]})
        self.assertEqual(errors, [])
        self.assertEqual([r['id'] for r in kept], ['old-explicit', 'fresh'])
        self.assertEqual([d['id'] for d in dropped], ['old-learned'])

    def test_over_the_cap_drops_the_weakest_learned_rules(self):
        rules = [rule('r%02d' % i, text='第%02d条：' % i + '规' * 100, evidence=2 + i % 5) for i in range(12)]
        rules.append(rule('mine', text='我手写的规则。', source='manual', evidence=1))
        kept, errors, dropped = self.p.settle({'rules': rules})
        self.assertEqual(errors, [])
        self.assertTrue(dropped)
        self.assertLessEqual(self.p.estimate(self.p.render(kept)), self.p.PERSONAL_LIMIT)
        self.assertIn('mine', [r['id'] for r in kept])
        weakest_kept = min(r['evidence'] for r in kept if r['source'] == 'learned')
        self.assertTrue(all(next(r for r in rules if r['id'] == d['id'])['evidence'] <= weakest_kept for d in dropped))

    def test_duplicates_and_bad_drafts_are_errors(self):
        self.assertTrue(self.p.settle({'rules': [rule(), rule()]})[1])
        self.assertTrue(self.p.settle({'nope': []})[1])

    def test_project_rules_stay_out_of_the_block(self):
        body = self.p.render([rule(), rule('api-only', text='这个项目接口都返回分页。', kind='habit', project='acme-api')])
        self.assertIn('回复默认', body)
        self.assertNotIn('分页', body)
        self.assertEqual(self.p.render([rule(project='acme-api')]), '')

    def test_limit_matches_the_budget_script(self):
        self.assertEqual(self.p.PERSONAL_LIMIT, context_budget.PERSONAL_LIMIT)


class CollectTest(ProfileCase):
    def test_collect_summarizes_events_since_a_date(self):
        journal = self.p.journal
        now = int(time.time())
        for at, event, extra in (
            (now - 40 * 86400, 'correction', {'text': '太旧了'}),
            (now - 100, 'correction', {'text': '不对，太长了'}),
            (now - 90, 'explicit', {'text': '以后先给结论'}),
            (now - 80, 'skill', {'name': 'wukong:tdd'}),
            (now - 70, 'skill', {'name': 'wukong:tdd'}),
            (now - 60, 'task', {'text': '加分页'}),
        ):
            journal.append(dict({'at': at, 'ts': 'x', 'event': event, 'session': 's%d' % (at % 7)}, **extra), self.data)
        result = self.p.collect(since=(date.today() - timedelta(days=30)).isoformat())
        self.assertEqual([c['text'] for c in result['corrections']], ['不对，太长了'])
        self.assertEqual([c['text'] for c in result['explicit']], ['以后先给结论'])
        self.assertEqual(result['skills'], {'wukong:tdd': 2})
        self.assertGreaterEqual(result['sessions'], 1)

    def test_collect_without_journal_is_empty(self):
        result = self.p.collect()
        self.assertEqual((result['corrections'], result['explicit'], result['skills']), ([], [], {}))


class WriteTest(ProfileCase):
    def test_apply_writes_block_and_private_profile(self):
        result = self.apply([rule()])
        self.assertTrue(result['applied'])
        text = self.claude_md.read_text(encoding='utf-8')
        self.assertIn('<!-- wukong:personal:start -->', text)
        self.assertIn('回复默认 5 行以内', text)
        if os.name == 'posix':
            self.assertEqual((self.data / 'profile.json').stat().st_mode & 0o777, 0o600)

    def test_invalid_draft_writes_nothing(self):
        result = self.apply([rule(evidence=1)])
        self.assertFalse(result['applied'])
        self.assertFalse(self.claude_md.exists())
        self.assertFalse((self.data / 'profile.json').exists())

    def test_library_and_personal_blocks_leave_each_other_alone(self):
        gi = self.p.global_instructions
        self.claude_md.write_text('我自己的规则\n', encoding='utf-8')
        gi.sync_global('claude-code', home=self.user, apply=True)
        self.apply([rule()])
        after_personal = self.claude_md.read_text(encoding='utf-8')
        self.assertTrue(after_personal.startswith('我自己的规则\n'))
        self.assertLess(after_personal.index('wukong:instructions:end'), after_personal.index('wukong:personal:start'))
        self.assertEqual(gi.sync_global('claude-code', home=self.user)['status'], 'configured')
        with mock.patch.object(gi, 'load_template', return_value='收到任务后，在读文件、跑命令、提问或作答之前：\n新版库规则'):
            gi.sync_global('claude-code', home=self.user, apply=True)
        upgraded = self.claude_md.read_text(encoding='utf-8')
        self.assertIn('新版库规则', upgraded)
        self.assertIn('回复默认 5 行以内', upgraded)

    def test_diff_backup_undo_and_forget(self):
        self.apply([rule()])
        second = self.apply([rule(), rule('mockup-first', text='做界面先出图再写代码。', kind='route')])
        self.assertEqual([r['id'] for r in second['diff']['added']], ['mockup-first'])
        self.assertTrue(second['write']['backup'])
        self.assertIn('先出图', self.claude_md.read_text(encoding='utf-8'))
        undone = self.p.undo('claude-code', home=self.user)
        self.assertTrue(undone['ok'])
        self.assertNotIn('先出图', self.claude_md.read_text(encoding='utf-8'))
        self.assertEqual([r['id'] for r in self.p.load_profile()['rules']], ['reply-short'])
        self.assertFalse(self.p.forget('missing', 'claude-code', home=self.user)['ok'])
        self.assertTrue(self.p.forget('reply-short', 'claude-code', home=self.user)['ok'])
        self.assertNotIn('wukong:personal', self.claude_md.read_text(encoding='utf-8'))

    def test_off_clears_the_block_but_keeps_the_profile(self):
        self.apply([rule()])
        self.p.off('claude-code', home=self.user)
        self.assertNotIn('wukong:personal', self.claude_md.read_text(encoding='utf-8'))
        self.assertEqual(len(self.p.load_profile()['rules']), 1)

    def test_history_keeps_the_latest_versions(self):
        with mock.patch.object(self.p, 'HISTORY_KEEP', 3):
            for i in range(6):
                self.apply([rule(text='第 %d 版规则。' % i)])
        self.assertEqual(len(list((self.data / 'history').glob('profile-*.json'))), 3)

    def test_cursor_gets_a_block_to_paste(self):
        result = self.p.apply({'rules': [rule()]}, 'cursor')
        self.assertEqual(result['write']['status'], 'user_rules_verification_required')
        self.assertIn('wukong:personal:start', result['write']['block'])


class BlockMergeTest(ProfileCase):
    def test_round_trips_and_bad_markers(self):
        gi = self.p.global_instructions
        for base in ('', '我的规则\n', gi.managed_block() + '\n', gi.managed_block() + '\n其后内容\n', 'a\r\nb\r\n'):
            added = gi.merge_personal(base, '- 一条')
            self.assertEqual(gi.merge_personal(gi.merge_personal(added, '- 两条'), ''), base, repr(base))
        with self.assertRaises(gi.ConfigurationError):
            gi.merge_personal('<!-- wukong:personal:start -->\nx\n', '- y')


class CliTest(ProfileCase):
    def test_cli_exit_codes(self):
        draft = self.base / 'draft.json'
        draft.write_text(json.dumps({'rules': [rule(evidence=1)]}), encoding='utf-8')
        env = dict(os.environ)
        bad = subprocess.run([sys.executable, '-I', str(PROFILE), 'apply', str(draft), '--host', 'claude-code',
                              '--home', str(self.user)], capture_output=True, timeout=60, env=env)
        self.assertEqual(bad.returncode, 1)
        self.assertFalse(json.loads(bad.stdout)['applied'])
        draft.write_text(json.dumps({'rules': [rule()]}), encoding='utf-8')
        good = subprocess.run([sys.executable, '-I', str(PROFILE), 'apply', str(draft), '--host', 'claude-code',
                               '--home', str(self.user)], capture_output=True, timeout=60, env=env)
        self.assertEqual(good.returncode, 0, good.stderr)
        shown = subprocess.run([sys.executable, '-I', str(PROFILE), 'show'], capture_output=True, timeout=60, env=env)
        self.assertEqual(json.loads(shown.stdout)['rules'][0]['id'], 'reply-short')


if __name__ == '__main__':
    unittest.main()
