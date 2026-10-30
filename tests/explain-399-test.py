#!/usr/bin/env python3
"""Issue399 fixture validity and pending-case scope; never invokes a model."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / 'cases/explain-399/corpus.json'
ROUND = ROOT / 'rounds/explain-399-012'


class Issue399Test(unittest.TestCase):
    def test_reuse_scope_and_new_authority(self):
        new = json.loads(CORPUS.read_text())
        old = json.loads((ROOT / 'rounds/explain-398-role-meaning-011/corpus.json').read_text())
        self.assertEqual(new['fixtures']['session-separated'], old['fixtures']['webview'])
        self.assertEqual([c['id'] for c in new['cases']], ['explain-399-separated', 'explain-399-mixed'])
        self.assertEqual(len({c['prompt'] for c in new['cases']}), 1)
        for case in new['cases']:
            self.assertEqual(case['versions'], ['candidate'])
            self.assertEqual(case['response_reporting'], 'task-response-only')
            for observation in case['observations']:
                self.assertEqual(observation['requirement_basis']['url'], 'https://github.com/akitanabe/tugite/issues/399')
                self.assertIn('basis_pending', observation)
                self.assertNotIn('basis', observation)
        registration = json.loads((ROUND / 'preregistration.json').read_text())
        self.assertIsNone(registration['candidate_sha'])
        self.assertEqual(registration['corpus_sha256'], hashlib.sha256(CORPUS.read_bytes()).hexdigest())
        self.assertFalse((ROUND / 'inputs').exists())
        self.assertFalse((ROUND / 'snapshot').exists())

    def test_fixture_success_rejection_and_commit_boundary(self):
        corpus = json.loads(CORPUS.read_text())
        probe = '''from app import build
store, cookies, op, dispatcher = build()
parent = op.prepare("binding", 10)
code = op.issue(parent, "alice", 10)
store.carts["alice"] = ["apple"]
request = {"parent": parent, "code": code, "now": 11, "cookies": {"binding": "binding"}}
bad = dict(request, cookies={"binding": "wrong"})
assert dispatcher.dispatch("exchange", bad)["status"] == 403
assert not store.codes[code]["used"] and not store.sessions and not cookies.issued
store.fail_commit = True
try:
    dispatcher.dispatch("exchange", request)
except RuntimeError:
    pass
else:
    raise AssertionError("commit failure missing")
assert not store.codes[code]["used"] and not store.sessions and not cookies.issued
store.fail_commit = False
assert dispatcher.dispatch("exchange", request)["status"] == 204
assert store.codes[code]["used"] and len(store.sessions) == 1 and len(cookies.issued) == 1
session = cookies.issued[0][1]
assert dispatcher.dispatch("cart", {"cookies": {"session": session}, "now": 12})["cart"] == ["apple"]
assert dispatcher.dispatch("exchange", request)["status"] == 403
assert len(store.sessions) == 1 and len(cookies.issued) == 1
# Cookie failure happens after state commit in both variants.
store, cookies, op, dispatcher = build()
parent = op.prepare("binding", 10)
code = op.issue(parent, "alice", 10)
cookies.fail = True
try:
    dispatcher.dispatch("exchange", {"parent": parent, "code": code, "now": 11, "cookies": {"binding": "binding"}})
except RuntimeError:
    pass
else:
    raise AssertionError("cookie failure missing")
assert store.codes[code]["used"] and len(store.sessions) == 1 and not cookies.issued
'''
        for name, files in corpus['fixtures'].items():
            with self.subTest(fixture=name), tempfile.TemporaryDirectory() as temporary:
                directory = Path(temporary)
                for relative, content in files.items():
                    path = directory / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(content)
                result = subprocess.run([sys.executable, '-c', probe], cwd=directory, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_mixed_variant_keeps_inline_responsibility(self):
        import ast
        corpus = json.loads(CORPUS.read_text())
        separated = corpus['fixtures']['session-separated']
        mixed = corpus['fixtures']['session-mixed']
        self.assertEqual(separated['app.py'], mixed['app.py'])
        self.assertEqual(separated['store.py'], mixed['store.py'])
        op = ast.parse(mixed['operation.py'])
        self.assertFalse(any(isinstance(n, ast.FunctionDef) and n.name == 'exchange' for n in ast.walk(op)))
        controller = next(n for n in ast.parse(mixed['web.py']).body if isinstance(n, ast.ClassDef) and n.name == 'Controller')
        exchange = next(n for n in controller.body if isinstance(n, ast.FunctionDef) and n.name == 'exchange')
        self.assertTrue(any(isinstance(n, ast.If) for n in ast.walk(exchange)))
        self.assertTrue(any(isinstance(n, ast.With) for n in ast.walk(exchange)))
        self.assertNotIn('self.operation.exchange(', mixed['web.py'])


if __name__ == '__main__':
    unittest.main()
