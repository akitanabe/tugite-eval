#!/usr/bin/env python3
"""Fixture/oracle and runner applicability checks; no model calls or commits."""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "evals"))
import runner

CORPUS = json.loads((ROOT / "cases/walkthrough-403/corpus.json").read_text())
DIALOGUE = json.loads((ROOT / "cases/walkthrough-403/dialogue.json").read_text())


def files_for(case: dict) -> dict:
    return CORPUS["fixtures"][case["fixture"]] | case["overrides"]


def run_fixture(files: dict, script: str) -> subprocess.CompletedProcess:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        for name, body in files.items():
            path = runner.safe_path(root, name)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body)
        return subprocess.run([sys.executable, "-c", script], cwd=root,
                              text=True, capture_output=True, check=False)


class Walkthrough403Test(unittest.TestCase):
    def test_fixture_requirements_in_both_code_shapes(self):
        probe = '''from entry import build
class Notifier:
    fail = False
    def send(self, result):
        self.last = dict(result)
        if self.fail:
            raise RuntimeError("notification failed")
n = Notifier()
b, reserve = build(n)
assert reserve({"id": "a", "seats": 2})["status"] == 201
assert b.free == 6 and b.holds == {"a": 2}
for request in [{"id": "a", "seats": 1}, {"id": "b", "seats": 7},
                {"id": "b", "seats": 0}, {"id": "b", "seats": -1},
                {"id": "b", "seats": True}]:
    try:
        reserve(request)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid reservation accepted")
    assert b.free == 6 and b.holds == {"a": 2}
assert b.cancel("a") is True and b.free == 8 and b.holds == {}
assert b.cancel("a") is False and b.free == 8
n.fail = True
try:
    reserve({"id": "a", "seats": 3})
except RuntimeError:
    pass
else:
    raise AssertionError("notification failure swallowed")
assert b.free == 5 and b.holds == {"a": 3}
'''
        for case in CORPUS["cases"]:
            if case["skill"] == "code-explain":
                with self.subTest(case=case["id"]):
                    result = run_fixture(files_for(case), probe)
                    self.assertEqual(result.returncode, 0, result.stderr)

    def test_supplied_tests_miss_cancel_state_mutation(self):
        files = copy.deepcopy(CORPUS["fixtures"]["booking"])
        test_command = "import unittest; r=unittest.TextTestRunner().run(unittest.defaultTestLoader.discover('tests')); raise SystemExit(not r.wasSuccessful())"
        result = run_fixture(files, test_command)
        self.assertEqual(result.returncode, 0, result.stderr)
        files["booking.py"] = files["booking.py"].replace(
            "        self.free += self.holds.pop(key)", "        self.holds.pop(key)")
        result = run_fixture(files, test_command)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = run_fixture(files, 'from booking import Bookings; b=Bookings(8); b.reserve("a",2); b.cancel("a"); assert b.free == 8')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("AssertionError", result.stderr)

    def test_supplied_tests_miss_duplicate_reservation_mutation(self):
        files = copy.deepcopy(CORPUS["fixtures"]["booking"])
        files["booking.py"] = files["booking.py"].replace(
            '        if key in self.holds:\n            raise ValueError("duplicate booking")\n', '')
        result = run_fixture(files, "import unittest; r=unittest.TextTestRunner().run(unittest.defaultTestLoader.discover('tests')); raise SystemExit(not r.wasSuccessful())")
        self.assertEqual(result.returncode, 0, result.stderr)
        result = run_fixture(files, '''from booking import Bookings
b=Bookings(8)
b.reserve("a",2)
try:
    b.reserve("a",1)
except ValueError:
    pass
else:
    raise AssertionError("duplicate accepted")
''')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate accepted", result.stderr)

    def test_dialogue_covers_cases_without_leaking_judgment(self):
        ids = [case["id"] for case in CORPUS["cases"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), set(DIALOGUE["cases"]))
        for case in CORPUS["cases"]:
            with self.subTest(case=case["id"]):
                self.assertTrue(case["prompt"])
                turns = DIALOGUE["cases"][case["id"]]
                if case["skill"] == "walkthrough-assist":
                    self.assertTrue(turns)
                    self.assertIn("終了", turns[-1])
                self.assertTrue(all(isinstance(turn, str) and turn.strip() for turn in turns))
                self.assertLessEqual(set(case["common_metrics"]), set(CORPUS["common_metrics"]))
                for name in files_for(case):
                    runner.safe_path(Path("/fixture"), name)
                    self.assertNotIn(Path(name).parts[0], {".git", ".agents", ".codex"})

    def test_new_skills_require_explicit_version_map(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for skill in ("code-explain", "walkthrough-assist"):
                path = root / "candidate/plugins/codex/skills" / skill / "SKILL.md"
                path.parent.mkdir(parents=True)
                path.write_text("A synthetic specification quote.")
                case = {"id": "synthetic-case", "skill": skill, "category": "normal",
                        "versions": ["candidate"], "common_metrics": ["grounding"],
                        "observations": [{"id": "one", "versions": ["candidate"],
                                          "basis": {"candidate": {"path": f"skills/{skill}/SKILL.md", "quote": "synthetic specification"}}}]}
                runner.validate_case(copy.deepcopy(case), root, {"candidate": "0" * 40})
                with self.assertRaisesRegex(ValueError, "invalid track/versions"):
                    runner.validate_case(copy.deepcopy(case), root)
                case["skill"] = "unregistered-skill"
                with self.assertRaisesRegex(ValueError, "invalid track/versions"):
                    runner.validate_case(case, root, {"candidate": "0" * 40})

    @unittest.skipUnless(os.environ.get("TUGITE_SOURCE_REPO"), "set TUGITE_SOURCE_REPO for current candidate basis checks")
    def test_current_distribution_basis_and_missing_quote_rejection(self):
        source = Path(os.environ["TUGITE_SOURCE_REPO"]).resolve()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "candidate").symlink_to(source, target_is_directory=True)
            for case in CORPUS["cases"]:
                with self.subTest(case=case["id"]):
                    valid = runner.validate_case(copy.deepcopy(case), root, {"candidate": "0" * 40})
                    self.assertTrue(valid["observations"][0]["basis"]["candidate"]["sha256"])
                    broken = copy.deepcopy(case)
                    broken["observations"][0]["basis"]["candidate"]["quote"] = "deliberately nonexistent quote for rejection test"
                    with self.assertRaisesRegex(ValueError, "basis not found"):
                        runner.validate_case(broken, root, {"candidate": "0" * 40})


if __name__ == "__main__":
    unittest.main()
