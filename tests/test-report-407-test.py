#!/usr/bin/env python3
"""Fixture counterexamples and real packet validation; no model invocation."""
from pathlib import Path
import copy
import json
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'evals'))
import runner
CORPUS = json.loads((ROOT / 'cases/test-report-407/corpus.json').read_text())


def run_fixture(files, probe):
    with tempfile.TemporaryDirectory() as tmp:
        for name, content in files.items():
            path = runner.safe_path(Path(tmp), name)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        return subprocess.run([sys.executable, '-c', probe], cwd=tmp, capture_output=True, text=True)


class FixtureTest(unittest.TestCase):
    def test_valid_fixture_and_cancellation_counterexample(self):
        files = copy.deepcopy(CORPUS['fixtures']['coupon'])
        suite = "import unittest; r=unittest.TextTestRunner().run(unittest.defaultTestLoader.discover('tests')); raise SystemExit(not r.wasSuccessful())"
        self.assertEqual(run_fixture(files, suite).returncode, 0)
        files['coupon.py'] = files['coupon.py'].replace('        self.used -= 1', '        pass')
        self.assertEqual(run_fixture(files, suite).returncode, 0)
        probe = 'from coupon import Usage; u=Usage(1); u.use(); u.cancel(); assert u.use()'
        self.assertNotEqual(run_fixture(files, probe).returncode, 0)

    def test_read_order_valid_variant_is_rejected(self):
        files = copy.deepcopy(CORPUS['fixtures']['coupon'])
        files['coupon.py'] = files['coupon.py'].replace('    amount=price()\n    allowed=eligibility()', '    allowed=eligibility()\n    amount=price()')
        public = 'from coupon import checkout; assert checkout(lambda:100,lambda:True)==100; assert checkout(lambda:100,lambda:False) is None'
        self.assertEqual(run_fixture(files, public).returncode, 0)
        suite = "import unittest; r=unittest.TextTestRunner().run(unittest.defaultTestLoader.discover('tests')); raise SystemExit(not r.wasSuccessful())"
        self.assertNotEqual(run_fixture(files, suite).returncode, 0)

    def test_case_inputs_and_required_observations(self):
        ids = [c['id'] for c in CORPUS['cases']]
        self.assertEqual(len(ids), len(set(ids)))
        for case in CORPUS['cases']:
            self.assertEqual(case['versions'], ['baseline', 'candidate'])
            self.assertEqual(set(case['required_quality_observations']), {o['id'] for o in case['observations']})
            files = CORPUS['fixtures'][case['fixture']] | case['overrides']
            for name in files:
                runner.safe_path(Path('/fixture'), name)
            compile(files['tests/test_coupon.py'], 'test_coupon.py', 'exec')


if __name__ == '__main__':
    unittest.main()
