#!/usr/bin/env python3
"""Preregistered two-case scope and fixture continuity; no new candidate packets."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
NEW = ROOT / 'cases/explain-398-concise-flow/corpus.json'
OLD = ROOT / 'cases/explain-398-implementation-first/corpus.json'
ROUND = ROOT / 'rounds/explain-398-concise-flow-007'


class ConciseFlowCorpusTest(unittest.TestCase):
    def test_fixture_scope_and_initial_changes_are_preserved(self):
        old, new = json.loads(OLD.read_text()), json.loads(NEW.read_text())
        self.assertEqual(old['fixtures'], new['fixtures'])
        self.assertEqual([c['id'] for c in new['cases']], [c['id'] for c in old['cases']])
        self.assertEqual(len(new['cases']), 2)
        for before, after in zip(old['cases'], new['cases']):
            for key in ('fixture', 'working_changes', 'overrides'):
                self.assertEqual(before[key], after[key])
            self.assertNotEqual(before['prompt'], after['prompt'])
            self.assertEqual(after['versions'], ['candidate'])
            self.assertEqual(after['response_reporting'], 'task-response-only')

    def test_new_observations_replace_exhaustive_presentation_checklists(self):
        corpus = json.loads(NEW.read_text())
        for case in corpus['cases']:
            self.assertEqual([o['id'] for o in case['observations']],
                             ['essential-flow', 'short-implementation-first'])
            self.assertTrue(all(o['versions'] == ['candidate'] for o in case['observations']))
            self.assertEqual(set(case['common_metrics']), set(corpus['common_metrics']))
            self.assertTrue(all(set(o['basis']) == {'candidate'} for o in case['observations']))
        self.assertTrue((ROOT / 'cases/explain-398-concise-flow/REFERENCE.md').is_file())

    def test_registration_is_pending_two_samples_without_candidate_packets(self):
        registration = json.loads((ROUND / 'preregistration.json').read_text())
        self.assertEqual(registration['corpus_sha256'], hashlib.sha256(NEW.read_bytes()).hexdigest())
        self.assertIsNone(registration['candidate_sha'])
        self.assertEqual(registration['sample_count'], 2)
        self.assertEqual(registration['trials_per_case'], 1)
        self.assertFalse((ROUND / 'inputs').exists())
        self.assertFalse((ROUND / 'snapshot').exists())


if __name__ == '__main__':
    unittest.main()
