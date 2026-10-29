#!/usr/bin/env python3
"""Preparation/transport and fixture boundaries; no model execution or scoring."""
import copy
import importlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'evals'))
import cloud_receipt
import cloud_task
import prepare_398
import runner as r


class TransportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.directory = Path(cls.temporary.name)
        cls.source = cls.directory / 'source.git'
        r.fetch_source(r.SOURCE_REPOSITORY, cls.source, {'baseline': prepare_398.BASELINE})
        # The same SHA on both sides is ONLY an adapter test, never a candidate result.
        cls.package = cls.directory / 'package'
        prepare_398.prepare(cls.package, 'both', prepare_398.BASELINE, str(cls.source), 1)

    def test_paired_round_supports_native_comparison_and_separate_rubrics(self):
        round_path = self.package / 'round'
        spec = r.verify_round(round_path)
        self.assertEqual(spec['versions'], {'baseline': prepare_398.BASELINE, 'candidate': prepare_398.BASELINE})
        self.assertEqual(len(r.read_json(self.package / 'index.json')['cells']), 10)
        for version, count in [('baseline', 1), ('candidate', 2)]:
            path = round_path / 'attempts' / f'explain-398-session-flow--{version}--1'
            self.assertEqual(len(r.read_json(path / 'rubric.json')['observations']), count)
            r.choose_case(spec, 'explain-398-session-flow', version)
        judgment = self.directory / 'compare.json'
        r.write_json(judgment, {'round_id': spec['round_id'], 'judge_id': 'synthetic-transport-test', 'independent': True,
                              'decisions': [{'case_id': 'explain-398-session-flow', 'baseline': 'baseline',
                                             'candidate': 'candidate', 'result': 'indeterminate', 'reason': 'No trial run',
                                             'metric_ids': ['accuracy'], 'evidence': []}]})
        r.compare(round_path, judgment)

    def test_custom_sha_round_restore_stage_and_quality_collection(self):
        restored = self.directory / 'restored'
        cloud_receipt.restore(self.package / 'snapshot', restored, str(self.source))
        cell = r.read_json(self.package / 'index.json')['cells'][0]
        input_path = self.package / cell['input']
        packet = cloud_task.verify_input(input_path, cell['input_sha256'])
        self.assertFalse(set(packet) & {'rubric', 'observations', 'common_metrics'})
        stage = self.directory / 'stage'
        cloud_task.stage(input_path, cell['input_sha256'], stage, str(self.source))
        self.assertEqual((stage / 'distribution/plugins/codex/skills/explain-this/SKILL.md').read_bytes(),
                         r.git('show', prepare_398.BASELINE + ':plugins/codex/skills/explain-this/SKILL.md', cwd=self.source))
        response = self.directory / 'response.txt'
        response.write_text('Synthetic transport probe. Not an evaluated explanation.\n')
        result = self.directory / 'result'
        cloud_task.collect(stage, cell['input_sha256'], response, result, None, quality=True)
        self.assertIsNone(r.read_json(result / 'collection.json')['effective_parent']['model'])
        cloud_receipt.verify_tree(result, 'result-seal.json')

    def test_fixture_sources_match_frozen_corpus_and_regressions_are_unchanged(self):
        corpus = r.read_json(prepare_398.CORPUS)
        for path in (ROOT / 'cases/explain-398/fixture').iterdir():
            if not path.is_file():
                continue
            self.assertEqual(path.read_text(), corpus['fixtures']['webview'][path.name])
        old = r.read_json(ROOT / 'evals/corpus.json')
        self.assertEqual(old['fixtures']['shipping'], corpus['fixtures']['shipping'])
        for case in old['cases']:
            if case['skill'] != 'explain-this':
                continue
            new = next(c for c in corpus['cases'] if c['id'] == case['id'])
            for key in ('prompt', 'overrides', 'working_changes', 'common_metrics'):
                self.assertEqual(case[key], new[key])
            self.assertEqual(case['observations'][0]['expectation'], new['observations'][0]['expectation'])

    def test_explicit_sample_selection_prepares_only_requested_cases(self):
        corpus = ROOT / 'cases/explain-398-code-centered/corpus.json'
        selected = ['explain-398-session-flow', 'explain-398-infrastructure']
        destination = self.directory / 'sample-selection'
        # Pinned old source here tests transport only, never a real new candidate.
        prepare_398.prepare(destination, 'candidate', prepare_398.BASELINE, str(self.source), 1,
                            corpus, prepare_398.BASELINE, selected)
        cells = r.read_json(destination / 'index.json')['cells']
        self.assertEqual([c['case_id'] for c in cells], selected)
        self.assertEqual({c['trial'] for c in cells}, {1})
        self.assertEqual({c['version'] for c in cells}, {'candidate'})
        self.assertEqual(len(list((destination / 'snapshot/attempts').iterdir())), 2)
        invalid = self.directory / 'invalid-selection'
        with self.assertRaises(ValueError):
            prepare_398.prepare(invalid, 'candidate', prepare_398.BASELINE, str(self.source), 1,
                                corpus, prepare_398.BASELINE, ['missing-case'])
        self.assertFalse(invalid.exists())

    def test_mismatched_map_and_placeholder_cannot_stage(self):
        cell = r.read_json(self.package / 'index.json')['cells'][0]
        packet = r.read_json(self.package / cell['input'])
        packet['fixed_versions']['baseline'] = '0' * 40
        altered = self.directory / 'altered.json'
        r.write_json(altered, packet)
        with self.assertRaises(ValueError):
            cloud_task.verify_input(altered, r.digest(altered.read_bytes()))
        with self.assertRaises(ValueError):
            prepare_398.prepare(self.directory / 'placeholder', 'candidate', '<CANDIDATE_SHA>', str(self.source), 1)
        self.assertFalse((self.directory / 'placeholder').exists())


class FixtureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / 'cases/explain-398/fixture'))
        cls.app = importlib.import_module('app')

    def setup_path(self):
        store, cookies, operation, dispatcher = self.app.build()
        parent = operation.prepare('binding', 10)
        code = operation.issue(parent, 'alice', 10)
        store.carts['alice'] = ['apple']
        request = {'parent': parent, 'code': code, 'now': 11, 'cookies': {'binding': 'binding'}}
        return store, cookies, dispatcher, code, request

    def test_success_then_middleware_and_replay(self):
        store, cookies, dispatcher, code, request = self.setup_path()
        store.sessions['old'] = {'user': 'old', 'expires': 11}
        self.assertEqual(dispatcher.dispatch('exchange', request), {'status': 204})
        session = cookies.issued[0][1]
        self.assertNotIn('old', store.sessions)
        cart_request = {'now': 12, 'cookies': {'session': session}, 'user': 'mallory'}
        self.assertEqual(dispatcher.dispatch('cart', cart_request), {'status': 200, 'cart': ['apple']})
        self.assertEqual(cart_request['user'], 'mallory')
        self.assertEqual(dispatcher.dispatch('exchange', request)['status'], 403)
        self.assertEqual(len(cookies.issued), 1)
        self.assertEqual(dispatcher.dispatch('cart', {'now': 71, 'cookies': {'session': session}})['status'], 403)

    def test_rejections_commit_failure_and_cookie_failure(self):
        for mutation in ['binding', 'expired', 'refresh', 'parent', 'code', 'used']:
            store, cookies, dispatcher, code, request = self.setup_path()
            if mutation == 'binding': request['cookies']['binding'] = 'wrong'
            if mutation == 'expired': request['now'] = 40
            if mutation == 'refresh': store.parents[request['parent']]['refresh_active'] = False
            if mutation == 'parent': request['parent'] = 'missing'
            if mutation == 'code': request['code'] = 'missing'
            if mutation == 'used': store.codes[code]['used'] = True
            before = copy.deepcopy((store.parents, store.codes, store.sessions))
            self.assertEqual(dispatcher.dispatch('exchange', request)['status'], 403)
            self.assertEqual((store.parents, store.codes, store.sessions), before)
            self.assertEqual(cookies.issued, [])
        store, cookies, dispatcher, code, request = self.setup_path()
        store.sessions['old'] = {'user': 'old', 'expires': 11}
        before = copy.deepcopy((store.parents, store.codes, store.sessions))
        store.fail_commit = True
        with self.assertRaisesRegex(RuntimeError, 'commit failed'):
            dispatcher.dispatch('exchange', request)
        self.assertEqual((store.parents, store.codes, store.sessions), before)
        self.assertEqual(store.serial, 3)
        self.assertEqual(cookies.issued, [])
        store, cookies, dispatcher, code, request = self.setup_path()
        cookies.fail = True
        with self.assertRaisesRegex(RuntimeError, 'cookie failed'):
            dispatcher.dispatch('exchange', request)
        self.assertTrue(store.codes[code]['used'])
        self.assertEqual(len(store.sessions), 1)
        self.assertEqual(cookies.issued, [])


if __name__ == '__main__':
    unittest.main()
