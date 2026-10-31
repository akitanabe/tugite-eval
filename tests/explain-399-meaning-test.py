#!/usr/bin/env python3
"""Pre-registration and consistency checks only; never grade natural-language output."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'evals'))
import runner as r
ROUND = ROOT / 'rounds/explain-399-meaning-020'


class MeaningCriterionTest(unittest.TestCase):
    def test_only_meaning_observation_and_gate_added_to_three_cases(self):
        before = r.read_json(ROOT / 'rounds/explain-399-remaining-019/corpus.json')
        after = r.read_json(ROUND / 'corpus.json')
        self.assertEqual(before['fixtures'], after['fixtures'])
        self.assertEqual(before['common_metrics'], after['common_metrics'])
        reg = r.read_json(ROUND / 'preregistration.json')
        self.assertEqual([c['id'] for c in after['cases']], reg['selected_cases'])
        self.assertEqual(len(after['cases']), 3)
        source = {c['id']: c for c in before['cases']}
        for case in after['cases']:
            normalized = copy.deepcopy(case)
            added = normalized['observations'].pop()
            self.assertEqual(added['id'], 'grounded-processing-meaning')
            self.assertIn('basis_pending', added)
            self.assertEqual(normalized['required_quality_observations'].pop(), 'grounded-processing-meaning')
            self.assertEqual(normalized, source[case['id']])
            self.assertEqual(case['required_quality_observations'],
                             ['displayed-execution-structure', 'grounded-processing-meaning'])
        self.assertEqual(reg['corpus_sha256'], hashlib.sha256((ROUND / 'corpus.json').read_bytes()).hexdigest())

    def test_factual_structural_pass_cannot_offset_semantic_fail(self):
        # Semantic labels are judge-only curated calibration. This test checks the gate,
        # not whether the text truly merits its label; independent readers assess that.
        examples = r.read_json(ROUND / 'calibration.json')['examples']
        rubric = {'required_quality_observations': ['displayed-execution-structure', 'grounded-processing-meaning']}
        literal = next(x for x in examples if x['id'] == 'literal-operations')
        self.assertEqual(literal['expected']['grounded-accuracy'], 'pass')
        self.assertEqual(literal['expected']['displayed-execution-structure'], 'pass')
        self.assertEqual(literal['expected']['grounded-processing-meaning'], 'fail')
        self.assertEqual(len(examples), 4)
        for example in examples:
            judgment = {'output_quality': {'result': 'pass'}, 'observations': {
                key: {'result': value} for key, value in example['expected'].items()}}
            if example['expected']['grounded-processing-meaning'] == 'pass':
                r.validate_output_quality_observations(judgment, rubric)
            else:
                with self.assertRaisesRegex(ValueError, 'mandatory quality observations'):
                    r.validate_output_quality_observations(judgment, rubric)
        for result in ['indeterminate', None]:
            observations = {'displayed-execution-structure': {'result': 'pass'}}
            if result:
                observations['grounded-processing-meaning'] = {'result': result}
            with self.assertRaises(ValueError):
                r.validate_output_quality_observations({'output_quality': {'result': 'pass'},
                                                        'observations': observations}, rubric)
        r.validate_output_quality_observations({'output_quality': {'result': 'fail'}, 'observations': {}}, rubric)

    def test_no_candidate_packet_or_fabricated_comparison(self):
        reg = r.read_json(ROUND / 'preregistration.json')
        if reg['candidate_sha'] is None:
            self.assertIsNone(reg['candidate_tree'])
            self.assertFalse((ROUND / 'inputs').exists())
            self.assertFalse((ROUND / 'snapshot').exists())
        else:
            cells = r.read_json(ROUND / 'index.json')['cells']
            self.assertEqual([c['case_id'] for c in cells], reg['selected_cases'])
            self.assertEqual(len(cells), 3)
            for cell in cells:
                packet_path = ROUND / cell['input']
                packet = r.read_json(packet_path)
                self.assertEqual(hashlib.sha256(packet_path.read_bytes()).hexdigest(), cell['input_sha256'])
                self.assertEqual(packet['repo_sha'], reg['candidate_sha'])
                self.assertEqual((packet['version'], packet['trial']), ('candidate', 1))
                self.assertFalse({'observations', 'rubric', 'common_metrics', 'required_quality_observations'} & packet.keys())
        comparison = r.read_json(ROUND / 'comparison-plan.json')
        self.assertEqual([c['case_id'] for c in comparison['cases']], reg['selected_cases'])
        for case in comparison['cases']:
            self.assertTrue(all(value is None for key, value in case.items() if key != 'case_id'))


if __name__ == '__main__':
    unittest.main()
