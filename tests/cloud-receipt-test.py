#!/usr/bin/env python3
"""Parent receipt/import CLI behavior. All runtime evidence here is test data."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / 'evals/cloud_receipt.py'
spec = importlib.util.spec_from_file_location('transport_tests', ROOT / 'tests/cloud-task-test.py')
transport = importlib.util.module_from_spec(spec)
spec.loader.exec_module(transport)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CloudReceiptTest(unittest.TestCase):
    setUpClass = classmethod(transport.CloudTaskTest.setUpClass.__func__)
    cli = transport.CloudTaskTest.cli
    prepare = transport.CloudTaskTest.prepare
    cloud = transport.CloudTaskTest.cloud
    package = transport.CloudTaskTest.package
    stage_package = transport.CloudTaskTest.stage_package

    def setUp(self) -> None:
        transport.CloudTaskTest.setUp(self)
        # Separate local eval-code Git fixture, never core history or real inference.
        self.code = self.directory / 'eval-code'
        (self.code / 'evals').mkdir(parents=True)
        for name in ('runner.py', 'cloud_task.py', 'cloud_receipt.py'):
            shutil.copyfile(ROOT / 'evals' / name, self.code / 'evals' / name)
        def git(*args: str) -> str:
            return subprocess.check_output(['git', *args], cwd=self.code, stderr=subprocess.DEVNULL, text=True).strip()
        git('init', '-q')
        git('add', '.')
        git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'code fixture')
        self.revision = git('rev-parse', 'HEAD')

    def receipt(self, *args: object, ok: bool = True) -> subprocess.CompletedProcess:
        result = subprocess.run([sys.executable, str(RECEIPT), *map(str, args)], capture_output=True, text=True)
        self.assertEqual(result.returncode == 0, ok, result.stderr)
        return result

    def setup_receipt(self, available: bool | None = True, source: str = 'parent-runtime') -> tuple[Path, Path]:
        package, staged, self.identity = self.stage_package()
        self.input = package / 'input.json'
        self.attempt = next((self.round / 'attempts').iterdir())
        stage = self.directory / 'stage.json'
        stage.write_text(json.dumps(self.stage_receipt))
        evidence = self.directory / 'setup-evidence.txt'
        evidence.write_text('SYNTHETIC TEST DATA: parent observed stage output and fixture capabilities')
        capabilities = self.directory / 'capabilities.json'
        packet = json.loads(self.input.read_text())
        capabilities.write_text(json.dumps({key: {'available': available, 'evidence': 'test probe'} for key in packet['required_capabilities']}))
        self.pre = self.directory / 'pre'
        self.receipt('receive-stage', self.input, stage, evidence, capabilities, self.pre,
                     '--task-id', 'task-fixture', '--setup-turn-id', 'setup-fixture', '--parent-id', 'parent-fixture',
                     '--eval-code-sha', self.revision, '--eval-repository', self.code, '--observation-source', source)
        return package, staged

    def outputs(self, transcript: bool | None = True, source: str = 'parent-runtime',
                synthetic: bool = False, available: bool | None = True) -> None:
        _, staged = self.setup_receipt(available=available)
        response = self.directory / 'response.txt'
        response.write_text('SYNTHETIC TEST DATA: report response')
        self.result = self.directory / 'result'
        self.cloud('collect', staged, self.identity, response, self.result)
        self.runtime = self.directory / 'parent-runtime'
        self.runtime.mkdir()
        proof = self.runtime / 'events.txt'
        proof.write_text('SYNTHETIC TEST DATA: runtime completion/identity/artifact observation')
        packet = json.loads(self.input.read_text())
        self.post = self.directory / 'post.json'
        post = {
            'schema': 1, 'parent_id': 'parent-fixture', 'task_id': 'task-fixture', 'run_turn_id': 'run-fixture',
            'attempt_id': packet['attempt_id'], 'input_sha256': self.identity, 'eval_code_sha': self.revision,
            'pre_receipt_sha256': sha(self.pre / 'receipt.json'), 'result_seal_sha256': sha(self.result / 'result-seal.json'),
            'observation_source': source, 'runtime_files': {'events.txt': sha(proof)},
            'synthetic': synthetic, 'capability_blockers': [], 'limitations': ['test data only'], 'telemetry': {},
            'observations': {key: {'value': True, 'evidence': ['events.txt']} for key in
                             ('agent_turn_completed', 'input_identity_verified', 'artifact_provenance_verified', 'transcript_complete')},
        }
        post['observations']['transcript_complete']['value'] = transcript
        self.post.write_text(json.dumps(post))

    def import_output(self, ok: bool = True, round_path: Path | None = None, attempt: Path | None = None) -> subprocess.CompletedProcess:
        return self.receipt('import', round_path or self.round, attempt or self.attempt, self.input, self.result,
                            self.pre, self.post, self.runtime, '--eval-repository', self.code, ok=ok)

    def execution(self) -> dict:
        return json.loads((self.attempt / 'execution.json').read_text())

    def test_parent_receipt_and_independent_judgment_connect_to_report(self) -> None:
        self.outputs()
        self.import_output()
        execution = self.execution()
        self.assertEqual(execution['state'], 'completed')
        self.assertIsNone(execution['effective_parent']['model'])
        judgment = self.directory / 'judgment.json'
        self.cli('judge-template', str(self.round), str(self.attempt), str(judgment))
        value = json.loads(judgment.read_text())
        value['judge_id'] = 'independent-fixture'
        for section in ('observations', 'common_metrics'):
            for finding in value[section].values():
                finding.update(result='indeterminate', reason='Synthetic mechanism test, no semantic inference', evidence=['cloud/result/response.txt'])
        judgment.write_text(json.dumps(value))
        self.cli('adjudicate', str(self.round), str(self.attempt), str(judgment))
        self.cli('report', str(self.round))
        report = json.loads((self.round / 'report.json').read_text())
        row = next(row for row in report['rows'] if row['case_id'] == 'test-report-normal' and row['version'] == 'v7.3.7')
        self.assertEqual(row['attempts'][0]['cloud_task_id'], 'task-fixture')
        self.assertEqual(row['missing_initial_trials'], [2, 3])
        self.assertEqual(row['spec_conformance'], 'indeterminate')
        self.import_output(ok=False)

    def test_incomplete_transcript_never_counts_as_completed_trial(self) -> None:
        self.outputs(transcript=None)
        self.import_output()
        self.assertEqual(self.execution()['state'], 'evidence-incomplete')
        self.assertFalse(self.execution()['comparison_eligible'])
        self.cli('report', str(self.round))
        rows = json.loads((self.round / 'report.json').read_text())['rows']
        row = next(row for row in rows if row['case_id'] == 'test-report-normal' and row['version'] == 'v7.3.7')
        self.assertEqual(row['missing_initial_trials'], [1, 2, 3])

    def test_child_self_report_cannot_promote_to_completed(self) -> None:
        self.outputs(source='child-self-report')
        self.import_output()
        self.assertEqual(self.execution()['evidence_kind'], 'cloud-reference')
        self.assertNotEqual(self.execution()['state'], 'completed')

    def test_explicit_synthetic_marker_is_preserved(self) -> None:
        self.outputs(synthetic=True)
        self.import_output()
        self.assertEqual(self.execution()['evidence_kind'], 'synthetic')
        self.assertFalse(self.execution()['comparison_eligible'])

    def test_unavailable_or_unknown_required_capability_blocks_run(self) -> None:
        self.outputs(available=None)
        self.assertEqual(json.loads((self.pre / 'receipt.json').read_text())['state'], 'blocked')
        self.import_output()
        self.assertEqual(self.execution()['state'], 'blocked')

    def test_mismatched_identities_and_evidence_are_rejected_before_import(self) -> None:
        self.outputs()
        original = self.post.read_bytes()
        post = json.loads(original)
        mutations = {'task_id': 'wrong-task', 'attempt_id': 'wrong-attempt', 'eval_code_sha': '0' * 40,
                     'input_sha256': '0' * 64, 'pre_receipt_sha256': '0' * 64,
                     'result_seal_sha256': '0' * 64, 'run_turn_id': 'setup-fixture'}
        for field, changed in mutations.items():
            with self.subTest(field=field):
                self.post.write_text(json.dumps({**post, field: changed}))
                self.import_output(ok=False)
                self.assertFalse((self.attempt / 'execution.json').exists())
                self.assertFalse((self.attempt / 'cloud').exists())
        self.post.write_bytes(original)
        (self.runtime / 'events.txt').write_text('altered runtime evidence')
        self.import_output(ok=False)

    def test_changed_result_or_baseline_is_rejected(self) -> None:
        self.outputs()
        response = self.result / 'response.txt'
        original = response.read_bytes()
        response.write_text('changed after parent inspection')
        self.import_output(ok=False)
        response.write_bytes(original)
        baseline = self.result / 'before.json'
        value = json.loads(baseline.read_text())
        value['head'] = '0' * 40
        baseline.write_text(json.dumps(value))
        # Even if child recomputes its seal, parent-held result seal and baseline differ.
        seal = json.loads((self.result / 'result-seal.json').read_text())
        seal['before.json'] = sha(baseline)
        (self.result / 'result-seal.json').write_text(json.dumps(seal))
        post = json.loads(self.post.read_text())
        post['result_seal_sha256'] = sha(self.result / 'result-seal.json')
        self.post.write_text(json.dumps(post))
        failure = self.import_output(ok=False)
        self.assertIn('initial snapshot mismatch', failure.stderr)

    def test_snapshot_restore_works_without_producer_workspace(self) -> None:
        self.outputs()
        snapshot = self.directory / 'snapshot'
        self.receipt('snapshot', self.round, snapshot)
        restored = self.directory / 'restored'
        self.receipt('restore', snapshot, restored, '--source-repo', self.source_repository)
        restored_attempt = restored / 'attempts' / self.attempt.name
        self.assertFalse((restored_attempt / 'workspace').exists())
        self.import_output(round_path=restored, attempt=restored_attempt)
        self.cli('report', str(restored))
        self.assertTrue((restored / 'report.json').exists())

    def test_evaluator_task_cannot_adjudicate_itself(self) -> None:
        self.outputs()
        self.import_output()
        path = self.directory / 'judgment.json'
        self.cli('judge-template', str(self.round), str(self.attempt), str(path))
        value = json.loads(path.read_text())
        value['judge_id'] = 'task-fixture'
        path.write_text(json.dumps(value))
        failed = self.cli('adjudicate', str(self.round), str(self.attempt), str(path), ok=False)
        self.assertIn('cannot independently judge itself', failed.stderr)

    def test_telemetry_cannot_be_filled_without_runtime_evidence(self) -> None:
        self.outputs()
        value = json.loads(self.post.read_text())
        value['telemetry'] = {'effective_parent': {'value': {'model': 'invented', 'effort': 'medium'}, 'evidence': []}}
        self.post.write_text(json.dumps(value))
        self.import_output(ok=False)
        self.assertFalse((self.attempt / 'execution.json').exists())

    def reseal_result(self) -> None:
        seal_path = self.result / 'result-seal.json'
        seal = json.loads(seal_path.read_text())
        seal_path.write_text(json.dumps({key: sha(self.result / key) for key in seal}))
        post = json.loads(self.post.read_text())
        post['result_seal_sha256'] = sha(seal_path)
        self.post.write_text(json.dumps(post))

    def test_changed_prompt_cannot_replace_parent_pre_run_prompt(self) -> None:
        self.outputs()
        (self.result / 'prompt.txt').write_text('different evaluated task')
        self.reseal_result()
        failure = self.import_output(ok=False)
        self.assertIn('prompt differs from parent-held stage receipt', failure.stderr)
        self.assertFalse((self.attempt / 'execution.json').exists())

    def assert_report_excludes_drift(self, field: str, document: str = 'collection.json') -> None:
        self.outputs()
        path = self.result / document
        value = json.loads(path.read_text())
        value[field] = False
        path.write_text(json.dumps(value))
        self.reseal_result()
        self.import_output()
        self.assertEqual(self.execution()['state'], 'evidence-incomplete')
        self.assertFalse(self.execution()['comparison_eligible'])
        self.cli('report', str(self.round))
        row = next(row for row in json.loads((self.round / 'report.json').read_text())['rows']
                   if row['case_id'] == 'test-report-normal' and row['version'] == 'v7.3.7')
        self.assertEqual(row['missing_initial_trials'], [1, 2, 3])

    def test_distribution_drift_never_counts_as_completed(self) -> None:
        self.assert_report_excludes_drift('distribution_unchanged')

    def test_agent_configuration_drift_never_counts_as_completed(self) -> None:
        self.assert_report_excludes_drift('agent_config_unchanged')

    def test_discovery_drift_never_counts_as_completed(self) -> None:
        self.assert_report_excludes_drift('discovery_unchanged')

    def test_git_config_drift_never_counts_as_completed(self) -> None:
        self.assert_report_excludes_drift('git_configuration_unchanged', 'after.json')

    def test_legacy_pilot_without_pre_receipt_is_not_accepted(self) -> None:
        self.setup_receipt()
        failure = self.receipt('receive-stage', ROOT / 'pilots/cloud-pilot-001/input.json',
                               self.directory / 'stage.json', self.directory / 'setup-evidence.txt',
                               self.directory / 'capabilities.json', self.directory / 'legacy-pre',
                               '--task-id', 'task-fixture', '--setup-turn-id', 'setup-fixture', '--parent-id', 'parent-fixture',
                               '--eval-code-sha', self.revision, '--eval-repository', self.code,
                               '--observation-source', 'parent-runtime', ok=False)
        self.assertIn('pre-receipt-free pilot remains reference-only', failure.stderr)

    def test_unsealed_git_directory_is_rejected_before_import(self) -> None:
        self.outputs()
        (self.result / '.git').mkdir()
        (self.result / '.git/unsealed').write_text('extra hidden evidence')
        failure = self.import_output(ok=False)
        self.assertIn('.git is not allowed in an evidence tree', failure.stderr)
        self.assertFalse((self.attempt / 'execution.json').exists())
        self.assertFalse((self.attempt / 'cloud').exists())


class QualityReceiptTest(unittest.TestCase):
    setUpClass = classmethod(CloudReceiptTest.setUpClass.__func__)
    setUp = CloudReceiptTest.setUp
    cli = CloudReceiptTest.cli
    prepare = CloudReceiptTest.prepare
    cloud = CloudReceiptTest.cloud
    package = CloudReceiptTest.package
    stage_package = CloudReceiptTest.stage_package
    receipt = CloudReceiptTest.receipt
    execution = CloudReceiptTest.execution
    def quality_outputs(self, source: str = 'parent-task-completion', observed: bool | None = True,
                        blockers: list[str] | None = None, synthetic: bool = False) -> None:
        package, staged, self.identity = self.stage_package()
        self.input = package / 'input.json'
        self.attempt = next((self.round / 'attempts').iterdir())
        # No pre-run receipt or even a retained before.json is required for quality.
        (staged / 'before.json').unlink()
        response = self.directory / 'response.txt'
        response.write_text('SYNTHETIC TEST DATA: completed output')
        self.result = self.directory / 'result'
        self.cloud('collect', staged, self.identity, response, self.result, '--quality')
        self.completion = self.directory / 'parent-completion'
        self.completion.mkdir()
        proof = self.completion / 'completion.txt'
        proof.write_text('SYNTHETIC TEST DATA: parent task completion with collected output')
        packet = json.loads(self.input.read_text())
        index = self.directory / 'index.json'
        index.write_text(json.dumps({'cells': [{'case_id': packet['case_id'], 'version': packet['version'],
                                              'input_sha256': self.identity}]}))
        self.protocol = self.directory / 'quality-protocol.json'
        self.protocol.write_text(json.dumps({'protocol_id': 'output-quality-v1', 'round_id': packet['round_id'],
                                            'input_index': 'index.json', 'input_index_sha256': sha(index),
                                            'requested': packet['requested']}))
        self.post = self.directory / 'quality-post.json'
        self.post.write_text(json.dumps({
            'parent_id': 'parent-fixture', 'task_id': 'task-fixture', 'run_turn_id': None,
            'attempt_id': packet['attempt_id'], 'input_sha256': self.identity, 'eval_code_sha': self.revision,
            'protocol_sha256': sha(self.protocol), 'result_seal_sha256': sha(self.result / 'result-seal.json'),
            'observation_source': source, 'parent_observed_completion': observed, 'output_match_verified': True,
            'completion_evidence': ['completion.txt'], 'evidence_files': {'completion.txt': sha(proof)},
            'synthetic': synthetic, 'capability_blockers': blockers or [], 'limitations': ['test data only'],
        }))

    def import_quality(self, ok: bool = True) -> subprocess.CompletedProcess:
        return self.receipt('quality-import', self.round, self.attempt, self.input, self.result,
                            self.post, self.completion, self.protocol, '--eval-repository', self.code, ok=ok)

    def test_quality_completion_counts_without_pre_receipt_transcript_or_effective_model(self) -> None:
        self.quality_outputs()
        self.import_quality()
        value = self.execution()
        self.assertEqual(value['state'], 'completed')
        self.assertEqual(value['evidence_kind'], 'llm')
        self.assertEqual(value['internal_compliance'], 'indeterminate')
        self.assertIsNone(value['effective_parent']['model'])
        self.assertFalse((self.attempt / 'cloud/pre').exists())
        judgment = self.directory / 'quality-judgment.json'
        self.cli('judge-template', str(self.round), str(self.attempt), str(judgment))
        packet = json.loads(judgment.read_text())
        packet['judge_id'] = 'independent-output-fixture'
        for section in ('observations', 'common_metrics'):
            for finding in packet[section].values():
                finding.update(result='indeterminate' if section == 'observations' else 'pass',
                               reason='Output-only mechanism fixture; internal operations unknown',
                               evidence=['cloud/result/response.txt'])
        packet['output_quality'] = {'result': 'pass', 'reason': 'test fixture output', 'evidence': ['cloud/result/response.txt']}
        judgment.write_text(json.dumps(packet))
        self.cli('adjudicate', str(self.round), str(self.attempt), str(judgment))
        self.cli('report', str(self.round))
        row = next(row for row in json.loads((self.round / 'report.json').read_text())['rows']
                   if row['case_id'] == 'test-report-normal' and row['version'] == 'v7.3.7')
        self.assertEqual(row['missing_initial_trials'], [2, 3])
        self.assertEqual(row['spec_conformance'], 'indeterminate')
        self.assertEqual(row['attempts'][0]['judgment']['output_quality']['result'], 'pass')

    def test_quality_child_self_report_is_not_a_completed_actual_trial(self) -> None:
        self.quality_outputs(source='child-self-report')
        self.import_quality()
        self.assertEqual(self.execution()['state'], 'evidence-incomplete')
        self.assertEqual(self.execution()['evidence_kind'], 'cloud-reference')

    def test_quality_unknown_completion_is_not_counted(self) -> None:
        self.quality_outputs(observed=None)
        self.import_quality()
        self.assertNotEqual(self.execution()['state'], 'completed')

    def test_quality_permission_blocker_still_blocks(self) -> None:
        self.quality_outputs(blockers=['fixture write denied by runtime'])
        self.import_quality()
        self.assertEqual(self.execution()['state'], 'blocked')
        self.assertFalse(self.execution()['comparison_eligible'])

    def test_quality_synthetic_never_counts_as_actual_trial(self) -> None:
        self.quality_outputs(synthetic=True)
        self.import_quality()
        self.assertEqual(self.execution()['evidence_kind'], 'synthetic')
        self.assertNotEqual(self.execution()['state'], 'completed')

    def test_quality_mismatched_input_artifact_or_protocol_is_rejected(self) -> None:
        self.quality_outputs()
        original = json.loads(self.post.read_text())
        for field in ('input_sha256', 'protocol_sha256', 'result_seal_sha256'):
            with self.subTest(field=field):
                self.post.write_text(json.dumps({**original, field: '0' * 64}))
                self.import_quality(ok=False)
                self.assertFalse((self.attempt / 'execution.json').exists())


if __name__ == '__main__':
    unittest.main()
