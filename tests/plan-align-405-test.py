#!/usr/bin/env python3
"""Deterministic corpus/adapter checks; no model execution or semantic oracle."""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'evals'))
import runner

CORPUS = json.loads((ROOT / 'cases/plan-align-405/corpus.json').read_text())
DIALOGUE = json.loads((ROOT / 'cases/plan-align-405/dialogue.json').read_text())


class PlanAlignCorpusTest(unittest.TestCase):
    def test_case_inputs_and_parent_turns_are_complete(self):
        ids = [case['id'] for case in CORPUS['cases']]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), set(DIALOGUE['cases']))
        for case in CORPUS['cases']:
            with self.subTest(case=case['id']):
                self.assertTrue(case['prompt'].strip())
                self.assertTrue(DIALOGUE['cases'][case['id']])
                self.assertTrue(all(isinstance(turn, str) and turn.strip()
                                    for turn in DIALOGUE['cases'][case['id']]))
                self.assertLessEqual(set(case['common_metrics']), set(CORPUS['common_metrics']))
                files = CORPUS['fixtures'][case['fixture']] | case['overrides']
                self.assertTrue(files['requirements.md'].strip())
                for name, content in files.items():
                    runner.safe_path(Path('/fixture'), name)
                    self.assertNotIn(Path(name).parts[0], {'.git', '.agents', '.codex'})
                    self.assertTrue(content.strip())

    def test_plan_align_requires_explicit_version_and_rejects_invalid_basis(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / 'candidate/plugins/codex/skills/plan-align/SKILL.md'
            path.parent.mkdir(parents=True)
            path.write_text('Synthetic contract witness.')
            case = {'id': 'synthetic-plan', 'skill': 'plan-align', 'category': 'normal',
                    'versions': ['candidate'], 'common_metrics': ['grounding'],
                    'observations': [{'id': 'one', 'versions': ['candidate'],
                        'basis': {'candidate': {'path': 'skills/plan-align/SKILL.md',
                                                'quote': 'contract witness'}}}],
                    'required_quality_observations': ['one']}
            runner.validate_case(copy.deepcopy(case), root, {'candidate': '0' * 40})
            with self.assertRaisesRegex(ValueError, 'invalid track/versions'):
                runner.validate_case(copy.deepcopy(case), root)
            broken = copy.deepcopy(case)
            broken['observations'][0]['basis']['candidate']['quote'] = 'absent witness'
            with self.assertRaisesRegex(ValueError, 'basis not found'):
                runner.validate_case(broken, root, {'candidate': '0' * 40})
            broken = copy.deepcopy(case)
            broken['required_quality_observations'] = ['missing']
            with self.assertRaisesRegex(ValueError, 'required quality observations'):
                runner.validate_case(broken, root, {'candidate': '0' * 40})

    @unittest.skipUnless(os.environ.get('TUGITE_SOURCE_REPO'), 'set TUGITE_SOURCE_REPO for candidate checks')
    def test_candidate_basis_and_mutated_quote_rejection(self):
        source = Path(os.environ['TUGITE_SOURCE_REPO']).resolve()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'candidate').symlink_to(source, target_is_directory=True)
            for case in CORPUS['cases']:
                with self.subTest(case=case['id']):
                    valid = runner.validate_case(copy.deepcopy(case), root, {'candidate': '0' * 40})
                    self.assertTrue(valid['observations'][0]['basis']['candidate']['sha256'])
                    broken = copy.deepcopy(case)
                    broken['observations'][0]['basis']['candidate']['quote'] = 'missing plan-align witness'
                    with self.assertRaisesRegex(ValueError, 'basis not found'):
                        runner.validate_case(broken, root, {'candidate': '0' * 40})


if __name__ == '__main__':
    unittest.main()
