#!/usr/bin/env python3
"""Prospective meaning/purpose criterion change; no candidate execution."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
NEW = ROOT / 'rounds/explain-398-role-meaning-011'
OLD = ROOT / 'rounds/explain-398-concise-flow-010'


class RoleMeaningCorpusTest(unittest.TestCase):
    def test_neutral_inputs_are_unchanged(self):
        old = json.loads((OLD / 'corpus.json').read_text())
        new = json.loads((NEW / 'corpus.json').read_text())
        self.assertEqual(old['fixtures'], new['fixtures'])
        self.assertEqual([c['id'] for c in old['cases']], [c['id'] for c in new['cases']])
        self.assertEqual(len(new['cases']), 2)
        for before, after in zip(old['cases'], new['cases']):
            for key in ['prompt', 'fixture', 'overrides', 'working_changes', 'versions', 'response_reporting']:
                self.assertEqual(before[key], after[key])
            self.assertEqual([o['id'] for o in after['observations']], ['essential-flow', 'role-meaning-in-flow'])
            self.assertTrue(all(o['versions'] == ['candidate'] for o in after['observations']))

    def test_new_criteria_are_recorded_without_overwriting_prior_criteria(self):
        old = json.loads((OLD / 'corpus.json').read_text())
        new = json.loads((NEW / 'corpus.json').read_text())
        self.assertNotEqual(old['common_metrics'], new['common_metrics'])
        for before, after in zip(old['cases'], new['cases']):
            self.assertNotEqual(before['observations'], after['observations'])
            self.assertEqual(after['observations'][1]['requirement_basis']['kind'], 'explicit-prospective-user-clarification')
        self.assertTrue((NEW / 'AUDIT.md').exists())

    def test_exactly_two_connected_packets_match_scope(self):
        registration = json.loads((NEW / 'preregistration.json').read_text())
        self.assertEqual(registration['corpus_sha256'], hashlib.sha256((NEW / 'corpus.json').read_bytes()).hexdigest())
        self.assertEqual((registration['sample_count'], registration['trials_per_case']), (2, 1))
        self.assertEqual(registration['candidate_sha'], '3fc608131926491866503c154e176b67e60a3890')
        cells = json.loads((NEW / 'index.json').read_text())['cells']
        self.assertEqual([c['case_id'] for c in cells], registration['selected_cases'])
        self.assertEqual(len(cells), 2)
        for cell in cells:
            path = NEW / cell['input']
            self.assertEqual(cell['input_sha256'], hashlib.sha256(path.read_bytes()).hexdigest())
            packet = json.loads(path.read_text())
            self.assertEqual(packet['repo_sha'], registration['candidate_sha'])
            self.assertEqual((packet['version'], packet['trial']), ('candidate', 1))
            self.assertEqual(packet['response_reporting'], 'task-response-only')
            self.assertFalse({'observations', 'common_metrics', 'rubric'} & packet.keys())


if __name__ == '__main__':
    unittest.main()
