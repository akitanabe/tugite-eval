#!/usr/bin/env python3
"""Cloud transport boundaries and evidence, without any LLM invocation."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / 'evals/cloud_task.py'
spec = importlib.util.spec_from_file_location('existing_tests', ROOT / 'tests/eval-runner-test.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
Base = module.EvaluationCliTest


class CloudTaskTest(unittest.TestCase):
    setUpClass = classmethod(Base.setUpClass.__func__)
    setUp = Base.setUp
    cli = Base.cli
    prepare = Base.prepare

    def cloud(self, *args: object, ok: bool = True) -> subprocess.CompletedProcess:
        if args and args[0] == 'collect' and '--before-sha256' not in args:
            args = (*args, '--before-sha256', self.before_sha256)
        result = subprocess.run([sys.executable, str(ADAPTER), *map(str, args)], capture_output=True, text=True)
        self.assertEqual(result.returncode == 0, ok, result.stderr)
        return result

    def package(self) -> tuple[Path, str]:
        attempt = self.prepare()
        package = self.directory / 'package'
        self.cloud('export', self.round, attempt, package)
        identity = hashlib.sha256((package / 'input.json').read_bytes()).hexdigest()
        return package, identity

    def stage_package(self) -> tuple[Path, Path, str]:
        package, identity = self.package()
        staged = self.directory / 'staged'
        receipt = self.cloud('stage', package / 'input.json', identity, staged, '--source-repo', self.source_repository)
        self.before_sha256 = json.loads(receipt.stdout)['before_sha256']
        self.assertEqual(self.before_sha256, hashlib.sha256((staged / 'before.json').read_bytes()).hexdigest())
        return package, staged, identity

    def test_input_has_fixture_and_fixed_distribution_but_no_judge_observations(self) -> None:
        package, staged, identity = self.stage_package()
        packet = json.loads((package / 'input.json').read_text())
        self.assertEqual(packet['files']['requirements.md'], json.loads((self.round / 'spec.json').read_text())['cases'][4]['files']['requirements.md'])
        self.assertEqual(packet['repo_sha'], '886e919a16ff6d318ed824ab53e8335362261c95')
        self.assertTrue(set(packet).isdisjoint({'observations', 'common_metrics', 'rubric'}))
        self.assertFalse((staged / 'control.json').exists())
        self.assertEqual(hashlib.sha256((staged / 'input.json').read_bytes()).hexdigest(), identity)
        prompt = (staged / 'prompt.txt').read_text()
        self.assertIn('distribution/plugins/codex/skills/test-report/SKILL.md first', prompt)
        self.assertTrue((staged / 'workspace/.agents/skills/test-report').is_symlink())
        self.assertFalse(subprocess.check_output(['git', 'remote'], cwd=staged / 'workspace'))

    def test_input_hash_mutation_is_rejected_before_staging(self) -> None:
        package, identity = self.package()
        with (package / 'input.json').open('a') as stream:
            stream.write(' ')
        self.cloud('stage', package / 'input.json', identity, self.directory / 'staged', ok=False)
        self.assertFalse((self.directory / 'staged').exists())

    def test_distribution_hash_mutation_rejected(self) -> None:
        package, _ = self.package()
        path = package / 'input.json'
        packet = json.loads(path.read_text())
        packet['distribution']['plugins/codex/skills/test-report/SKILL.md'] = '0' * 64
        path.write_text(json.dumps(packet))
        identity = hashlib.sha256(path.read_bytes()).hexdigest()
        self.cloud('stage', path, identity, self.directory / 'staged', '--source-repo', self.source_repository, ok=False)
        self.assertFalse((self.directory / 'staged').exists())

    def test_runtime_constrained_case_is_not_silently_emulated(self) -> None:
        cases = json.loads((self.round / 'spec.json').read_text())['cases']
        case = next(c for c in cases if c.get('capability_constraint'))
        attempt = self.prepare(case['id'], case['versions'][0])
        self.cloud('export', self.round, attempt, self.directory / 'package', ok=False)
        self.assertFalse((self.directory / 'package').exists())

    def test_collection_tracks_authored_artifacts_without_promoting_synthetic_to_llm(self) -> None:
        _, staged, identity = self.stage_package()
        (staged / 'workspace/notes.txt').write_text('authored test artifact')
        response = self.directory / 'response.txt'
        response.write_text('synthetic fixture response')
        result = self.directory / 'result'
        self.cloud('collect', staged, identity, response, result)
        packet = json.loads((result / 'collection.json').read_text())
        self.assertEqual(packet['evidence_kind'], 'unverified-cloud-output')
        self.assertIsNone(packet['effective_parent']['model'])
        self.assertIsNone(packet['resolved_parent']['model'])
        self.assertIsNone(packet['loaded_distribution'])
        self.assertTrue(packet['distribution_unchanged'])
        self.assertTrue((result / 'artifacts/notes.txt').exists())
        seal = json.loads((result / 'result-seal.json').read_text())
        for name, digest in seal.items():
            self.assertEqual(hashlib.sha256((result / name).read_bytes()).hexdigest(), digest)
        self.cloud('collect', staged, identity, response, result, ok=False)

    def test_collection_captures_git_config_drift_without_executing_modified_git_settings(self) -> None:
        _, staged, identity = self.stage_package()
        with (staged / 'workspace/.git/config').open('a') as stream:
            stream.write('\n# changed\n')
        response = self.directory / 'response.txt'
        response.write_text('test response')
        result = self.directory / 'result'
        self.cloud('collect', staged, identity, response, result)
        after = json.loads((result / 'after.json').read_text())
        self.assertFalse(after['git_configuration_unchanged'])
        self.assertNotIn('diff', after)

    def test_collection_observes_distribution_agent_and_discovery_drift(self) -> None:
        _, staged, identity = self.stage_package()
        skill = staged / 'distribution/plugins/codex/skills/test-report/SKILL.md'
        skill.write_text(skill.read_text() + '\nchanged\n')
        agent = next((staged / 'workspace/.codex/agents').glob('*.toml'))
        agent.write_text(agent.read_text() + '\n# changed\n')
        (staged / 'workspace/.agents/skills/test-report').unlink()
        response = self.directory / 'response.txt'
        response.write_text('test response')
        result = self.directory / 'result'
        self.cloud('collect', staged, identity, response, result)
        collection = json.loads((result / 'collection.json').read_text())
        for field in ('distribution_unchanged', 'agent_config_unchanged', 'discovery_unchanged'):
            self.assertFalse(collection[field])
        self.assertEqual((result / 'before.json').read_bytes(), (staged / 'before.json').read_bytes())

    def test_artifact_symlink_returns_incomplete_collection_without_seal(self) -> None:
        _, staged, identity = self.stage_package()
        (staged / 'workspace/symlink').symlink_to(staged / 'input.json')
        response = self.directory / 'response.txt'
        response.write_text('test response')
        result = self.directory / 'result'
        self.cloud('collect', staged, identity, response, result, ok=False)
        self.assertFalse((result / 'result-seal.json').exists())

    def test_unsafe_fixture_path_is_rejected_before_staging(self) -> None:
        package, _ = self.package()
        path = package / 'input.json'
        packet = json.loads(path.read_text())
        packet['files']['../escape'] = 'invalid'
        path.write_text(json.dumps(packet))
        identity = hashlib.sha256(path.read_bytes()).hexdigest()
        self.cloud('stage', path, identity, self.directory / 'staged', ok=False)
        self.assertFalse((self.directory / 'staged').exists())

    def test_parent_held_snapshot_hash_rejects_rewritten_baseline(self) -> None:
        _, staged, identity = self.stage_package()
        response = self.directory / 'response.txt'
        response.write_text('test response')
        baseline = staged / 'before.json'
        original = baseline.read_bytes()
        value = json.loads(original)
        config = staged / 'workspace/.git/config'
        config.write_text(config.read_text() + '\n# changed after stage\n')
        # Rewriting baseline to the changed config would previously conceal drift.
        rewritten_config_hash = hashlib.sha256(config.read_bytes()).hexdigest()
        mutations = {
            'head': '0' * 40, 'git_config': rewritten_config_hash, 'git_hooks': {},
            'agent_config': {}, 'discovery': {}, 'files': {}, 'diff': 'rewritten',
        }
        for field, replacement in mutations.items():
            with self.subTest(field=field):
                changed = {**value, field: replacement}
                baseline.write_text(json.dumps(changed))
                result = self.directory / ('result-' + field)
                failure = self.cloud('collect', staged, identity, response, result, ok=False)
                self.assertIn('parent-held before SHA-256', failure.stderr)
                self.assertFalse(result.exists())
        baseline.write_bytes(original)
        self.cloud('collect', staged, identity, response, self.directory / 'valid-result')

    def test_collect_without_parent_snapshot_anchor_is_rejected(self) -> None:
        _, staged, identity = self.stage_package()
        response = self.directory / 'response.txt'
        response.write_text('test response')
        result = self.directory / 'result'
        missing = subprocess.run([sys.executable, str(ADAPTER), 'collect', str(staged), identity,
                                  str(response), str(result)], capture_output=True, text=True)
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn('--before-sha256', missing.stderr)
        self.assertFalse(result.exists())


if __name__ == '__main__':
    unittest.main()
