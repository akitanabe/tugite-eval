#!/usr/bin/env python3
"""Prospective corpus continuity and preparation guards; never judge explanations."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'evals'))
import prepare_398

OLD = ROOT / 'cases/explain-398/corpus.json'
NEW = ROOT / 'cases/explain-398-code-centered/corpus.json'


class ProspectiveCorpusTest(unittest.TestCase):
    def test_fixture_prompt_and_previous_expectations_preserved(self):
        old, new = json.loads(OLD.read_text()), json.loads(NEW.read_text())
        self.assertEqual(old['fixtures'], new['fixtures'])
        self.assertEqual(len(new['cases']), 7)
        for before, after in zip(old['cases'], new['cases']):
            for key in ('id', 'prompt', 'overrides', 'working_changes', 'versions', 'fixture'):
                self.assertEqual(before[key], after[key])
            previous = copy.deepcopy([o for o in after['observations'][:-1]
                                      if o['id'] != '398-code-structure-and-effects'])
            self.assertEqual([(o['id'], o['expectation']) for o in before['observations']],
                             [(o['id'], o['expectation']) for o in previous])
            for expected, actual in zip(before['observations'], previous):
                self.assertEqual(expected['expectation'], actual['expectation'])
                self.assertEqual(expected['id'], actual['id'])
            added = after['observations'][-1]
            self.assertEqual(added['versions'], ['candidate'])
            self.assertEqual(added['id'], 'code-centered-explanation')
            self.assertTrue(added['user_requirement_basis']['purpose_quote'])
            self.assertTrue(added['user_requirement_basis']['structure_quote'])
            if before['id'] == 'explain-398-session-flow':
                old_structure = next(o for o in after['observations'] if o['id'] == '398-process-and-effects')
                new_structure = next(o for o in after['observations'] if o['id'] == '398-code-structure-and-effects')
                self.assertEqual(old_structure['versions'], ['baseline'])
                self.assertEqual(new_structure['versions'], ['candidate'])
                self.assertEqual(len(after['observations']), len(before['observations']) + 2)
            else:
                self.assertEqual(len(after['observations']), len(before['observations']) + 1)
            self.assertEqual(after['common_metrics'][:len(before['common_metrics'])], before['common_metrics'])

    def test_registration_matches_corpus_and_has_no_executable_candidate(self):
        import hashlib
        registration = json.loads((ROOT / 'rounds/explain-398-code-centered-005/preregistration.json').read_text())
        self.assertEqual(registration['corpus_sha256'], hashlib.sha256(NEW.read_bytes()).hexdigest())
        self.assertIsNone(registration['candidate_sha'])
        self.assertTrue(registration['prospective'])

    def test_unresolved_or_mismatched_sha_is_rejected_before_writing(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / 'pending'
            for side, revision, baseline in [('both', '<NEW_CANDIDATE_SHA>', prepare_398.BASELINE),
                                             ('both', prepare_398.BASELINE, '<BASELINE>'),
                                             ('baseline', prepare_398.BASELINE, '2e7ae9237103cc9a6c6d9afbb748c11ad2ea51e7')]:
                with self.assertRaises(ValueError):
                    prepare_398.prepare(target, side, revision, temporary, 1, NEW, baseline)
                self.assertFalse(target.exists())


if __name__ == '__main__':
    unittest.main()
