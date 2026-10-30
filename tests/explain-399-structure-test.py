#!/usr/bin/env python3
"""Structural calibration and acceptance consistency; never a semantic text parser."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'evals'))
import runner as r

ROUND = ROOT / 'rounds/explain-399-structure-013'


class StructuralCriterionTest(unittest.TestCase):
    def test_neutral_inputs_and_factual_criteria_preserved(self):
        before = r.read_json(ROOT / 'cases/explain-399/corpus.json')
        after = r.read_json(ROUND / 'corpus.json')
        self.assertEqual(before['fixtures'], after['fixtures'])
        self.assertEqual(len(after['cases']), 2)
        for a, b in zip(before['cases'], after['cases']):
            for key in ['id', 'prompt', 'fixture', 'overrides', 'working_changes', 'response_reporting']:
                self.assertEqual(a[key], b[key])
            self.assertEqual(a['observations'], b['observations'][:-1])
            self.assertEqual(b['observations'][-1]['id'], 'displayed-execution-structure')
            self.assertEqual(b['required_quality_observations'], ['displayed-execution-structure'])
            self.assertEqual(a['common_metrics'], b['common_metrics'][:-1])
        reg = r.read_json(ROUND / 'preregistration.json')
        self.assertEqual(reg['corpus_sha256'], hashlib.sha256((ROUND / 'corpus.json').read_bytes()).hexdigest())
        self.assertEqual(reg['candidate_sha'], '3e9a42e29be0f0f81efad0ea1ef86d6c18615cba')
        cells = r.read_json(ROUND / 'index.json')['cells']
        self.assertEqual([c['case_id'] for c in cells], reg['selected_cases'])
        self.assertEqual(len(cells), 2)
        for cell in cells:
            packet_path = ROUND / cell['input']
            packet = r.read_json(packet_path)
            self.assertEqual(r.digest(packet_path.read_bytes()), cell['input_sha256'])
            self.assertEqual(packet['repo_sha'], reg['candidate_sha'])
            self.assertEqual((packet['version'], packet['trial']), ('candidate', 1))
            self.assertFalse({'observations', 'rubric', 'common_metrics', 'required_quality_observations'} & packet.keys())

    def test_factually_correct_fragments_cannot_be_quality_pass(self):
        # Expected semantic labels are curated judge calibration, not inferred from markup.
        # The code tests only the acceptance rule; it never grades natural language.
        data = r.read_json(ROUND / 'calibration.json')['examples']
        self.assertEqual(len(data), 4)
        rubric = {'required_quality_observations': ['displayed-execution-structure']}
        for variant in ['separated', 'mixed']:
            fragments = next(x for x in data if x['id'] == variant + '-fragments')
            structured = next(x for x in data if x['id'] == variant + '-structured')
            self.assertEqual(fragments['factual_claims'], structured['factual_claims'])
            self.assertEqual(fragments['expected']['execution-faithfulness'], 'pass')
            self.assertEqual(structured['expected']['execution-faithfulness'], 'pass')
            for sample in [fragments, structured]:
                judgment = {'output_quality': {'result': 'pass'}, 'observations': {
                    key: {'result': result} for key, result in sample['expected'].items()}}
                if sample['expected']['displayed-execution-structure'] == 'fail':
                    with self.assertRaisesRegex(ValueError, 'mandatory quality observations'):
                        r.validate_output_quality_observations(judgment, rubric)
                else:
                    r.validate_output_quality_observations(judgment, rubric)
        for result in ['indeterminate', 'missing']:
            obs = {} if result == 'missing' else {'displayed-execution-structure': {'result': result}}
            with self.assertRaises(ValueError):
                r.validate_output_quality_observations({'output_quality': {'result': 'pass'}, 'observations': obs}, rubric)
        # Historical rounds have no required field and retain their old behavior.
        r.validate_output_quality_observations({'output_quality': {'result': 'pass'}, 'observations': {}}, {})

    def test_adjudication_invokes_quality_gate_before_writing(self):
        rubric = {'observations': [{'id': 'displayed-execution-structure'}], 'common_metrics': {},
                  'required_quality_observations': ['displayed-execution-structure']}
        judgment = {'attempt_id': 'test', 'judge_id': 'independent-test', 'independent': True,
                    'output_quality': {'result': 'pass'}, 'observations': {
                        'displayed-execution-structure': {'result': 'fail', 'reason': 'synthetic calibration only', 'evidence': ['response.txt']}},
                    'common_metrics': {}}
        def read(path):
            return {'rubric.json': rubric, 'candidate-judgment.json': judgment,
                    'execution.json': {'evidence_kind': 'llm', 'test_fixture': True},
                    'evidence-seal.json': {'response.txt': 'test-only'}}[path.name]
        # No real round, candidate packet, execution or evidence is created.
        with patch.object(r, 'verify_attempt', return_value=({}, {'attempt_id': 'test'})), \
             patch.object(r, 'verify_evidence'), patch.object(r, 'read_json', side_effect=read), \
             patch.object(r, 'write_json') as write:
            with self.assertRaisesRegex(ValueError, 'mandatory quality observations'):
                r.adjudicate(Path('/synthetic-round'), Path('/synthetic-attempt'), Path('/candidate-judgment.json'))
            write.assert_not_called()


if __name__ == '__main__':
    unittest.main()
