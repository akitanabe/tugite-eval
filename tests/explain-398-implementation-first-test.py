#!/usr/bin/env python3
"""Two-sample input continuity and prospective applicability; no output scoring."""
import hashlib
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / 'cases/explain-398-code-centered/corpus.json'
NEW = ROOT / 'cases/explain-398-implementation-first/corpus.json'
ROUND = ROOT / 'rounds/explain-398-implementation-first-006'


class ImplementationFirstCorpusTest(unittest.TestCase):
    def setUp(self):
        self.old = json.loads(OLD.read_text())
        self.new = json.loads(NEW.read_text())

    def test_only_two_candidate_cases_with_original_fixture_and_prompts(self):
        self.assertEqual([c['id'] for c in self.new['cases']],
                         ['explain-398-session-flow', 'explain-398-infrastructure'])
        self.assertEqual(self.new['fixtures'], {'webview': self.old['fixtures']['webview']})
        for case in self.new['cases']:
            previous = next(c for c in self.old['cases'] if c['id'] == case['id'])
            self.assertEqual(case['versions'], ['candidate'])
            for key in ('prompt', 'fixture', 'overrides', 'working_changes'):
                self.assertEqual(case[key], previous[key])

    def test_technical_observations_preserved_and_old_presentation_removed(self):
        for case in self.new['cases']:
            previous = next(c for c in self.old['cases'] if c['id'] == case['id'])
            expected = [(o['id'], o['expectation']) for o in previous['observations']
                        if 'candidate' in o['versions'] and o['id'] != 'code-centered-explanation']
            self.assertEqual([(o['id'], o['expectation']) for o in case['observations'][:-1]], expected)
            self.assertTrue(all(o['versions'] == ['candidate'] for o in case['observations']))
            self.assertEqual(case['observations'][-1]['id'], 'implementation-first-explanation')
            self.assertEqual(set(case['observations'][-1]['basis']), {'candidate'})
            self.assertNotIn('code-centered-readability', case['common_metrics'])
            self.assertIn('implementation-first-readability', case['common_metrics'])
            for key in ('traceability', 'usefulness', 'accuracy', 'conciseness-without-loss'):
                self.assertEqual(self.new['common_metrics'][key], self.old['common_metrics'][key])

    def test_registration_tracks_exact_scope_and_corpus_hash(self):
        registration = json.loads((ROUND / 'preregistration.json').read_text())
        self.assertEqual(registration['corpus_sha256'], hashlib.sha256(NEW.read_bytes()).hexdigest())
        self.assertEqual(registration['sample_count'], 2)
        self.assertEqual(registration['trials_per_case'], 1)
        self.assertEqual(registration['selected_cases'], [c['id'] for c in self.new['cases']])
        self.assertTrue(registration['prospective'])
        if registration['candidate_sha'] is not None:
            self.assertRegex(registration['candidate_sha'], r'^[0-9a-f]{40}$')

    def test_new_publication_contains_requirement_summaries_not_transcript(self):
        for case in self.new['cases']:
            for observation in case['observations']:
                self.assertNotIn('user_requirement_basis', observation)
                self.assertNotIn('user_requirement_override', observation)
        # Transcript framing and runtime logs are outside this new delivery's scope.
        for path in (ROOT / 'cases/explain-398-implementation-first').rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts:
                self.assertNotIn('<transcript_evidence>', path.read_text())


if __name__ == '__main__':
    unittest.main()
