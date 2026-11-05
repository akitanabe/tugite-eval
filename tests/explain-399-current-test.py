#!/usr/bin/env python3
"""Current normal selection excludes retired experiments; no model execution."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'evals'))
import cloud_receipt as receipt

CURRENT = ROOT / 'cases/explain-399'
EXPECTED = ['explain-399-separated', 'explain-399-mixed', 'explain-399-infrastructure',
            'explain-399-unknown-connection', 'explain-this-normal', 'explain-this-boundary',
            'explain-this-failure', 'explain-this-ambiguous']

def read(path):
    return json.loads(path.read_text())


class CurrentSelectionTest(unittest.TestCase):
    def test_current_corpus_preserves_canonical_eight_exactly(self):
        plan = read(CURRENT / 'current.json')
        corpus_path = ROOT / plan['corpus']
        corpus = read(corpus_path)
        frozen = read(ROOT / 'rounds/explain-399-all-023/resolved-corpus.json')
        canonical = {key: value for key, value in frozen.items() if key != 'cases'}
        canonical['cases'] = [case for case in frozen['cases'] if case['id'] in EXPECTED]
        self.assertEqual(corpus, canonical)
        self.assertEqual(plan['selected_cases'], EXPECTED)
        self.assertEqual([case['id'] for case in corpus['cases']], EXPECTED)
        self.assertEqual(plan['sample_count'], 8)
        self.assertEqual(plan['trials_per_case'], 1)
        self.assertEqual(plan['corpus_sha256'], hashlib.sha256(corpus_path.read_bytes()).hexdigest())
        for case in corpus['cases']:
            self.assertEqual(case['required_quality_observations'], plan['required_quality_observations'])
            self.assertNotIn('15歳', case['prompt'])
            self.assertNotIn('audience', case['id'])

    def test_current_inputs_are_same_eight_sealed_packets(self):
        plan = read(CURRENT / 'current.json')
        index_path = ROOT / plan['input_index']
        self.assertEqual(plan['input_index_sha256'], hashlib.sha256(index_path.read_bytes()).hexdigest())
        cells = read(index_path)['cells']
        self.assertEqual([cell['case_id'] for cell in cells], EXPECTED)
        frozen_root = ROOT / 'rounds/explain-399-all-023'
        prior = {cell['case_id']: cell for cell in read(frozen_root / 'index.json')['cells']}
        for cell in cells:
            path = ROOT / cell['input']
            self.assertEqual(path, frozen_root / prior[cell['case_id']]['input'])
            self.assertEqual(cell['input_sha256'], prior[cell['case_id']]['input_sha256'])
            self.assertEqual(cell['input_sha256'], hashlib.sha256(path.read_bytes()).hexdigest())
            packet = read(path)
            self.assertEqual(packet['repo_sha'], plan['candidate_sha'])
            self.assertEqual(packet['requested'], plan['requested'])
            self.assertEqual(packet['response_reporting'], plan['reporting'])
            self.assertEqual((packet['version'], packet['trial']), ('candidate', 1))
            self.assertNotIn('15歳', packet['prompt'])

    def test_retired_frozen_history_still_verifies(self):
        for name in ['explain-399-audience-022', 'explain-399-all-023']:
            history = ROOT / 'rounds' / name
            receipt.verify_tree(history / 'snapshot', 'snapshot-seal.json')
            protocol = read(history / 'quality-protocol.json')
            self.assertEqual(protocol['input_index_sha256'], hashlib.sha256((history / 'index.json').read_bytes()).hexdigest())
            for cell in read(history / 'index.json')['cells']:
                self.assertEqual(cell['input_sha256'], hashlib.sha256((history / cell['input']).read_bytes()).hexdigest())
            retirement = read(history / 'RETIREMENT.json')
            self.assertEqual(retirement['current_normal_case_count'], 8)
            self.assertEqual(len(retirement['retired_cases']), 3)
            self.assertIn('current.json', retirement['current_plan'])
        # Initial frozen corpus also stays byte-identical to its original registration.
        registration = read(ROOT / 'rounds/explain-399-012/preregistration.json')
        self.assertEqual(registration['corpus_sha256'], hashlib.sha256((CURRENT / 'corpus.json').read_bytes()).hexdigest())


if __name__ == '__main__':
    unittest.main()
