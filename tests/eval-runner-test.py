#!/usr/bin/env python3
"""Observable evaluation CLI behavior; fixtures never count as LLM trials."""
from __future__ import annotations

import json
import hashlib
import runpy
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "evals/runner.py"


class EvaluationCliTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # Fetch once for the suite, independently of the eval repository's Git DB.
        # Each round still verifies/fetches the fixed SHAs from this local source.
        cls.source_temporary = tempfile.TemporaryDirectory(prefix="tugite-test-source-")
        cls.addClassCleanup(cls.source_temporary.cleanup)
        cls.source_repository = Path(cls.source_temporary.name) / "source.git"
        spec = runpy.run_path(str(RUNNER))
        spec["fetch_source"](spec["SOURCE_REPOSITORY"], cls.source_repository)

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.round = self.directory / "round"
        self.cli("freeze", str(self.round))

    def cli(self, *args: str, ok: bool = True) -> subprocess.CompletedProcess:
        # Acquisition is an explicit separate repository; no core objects are
        # installed in this repository while exercising the original 16 cases.
        if args and args[0] == "freeze":
            args = (*args, "--source-repo", str(self.source_repository))
        result = subprocess.run([sys.executable, str(RUNNER), *args], cwd=ROOT, capture_output=True, text=True)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
        return result

    def prepare(self, case: str = "test-report-normal", version: str = "v7.3.7", trial: int = 1) -> Path:
        result = self.cli("prepare", str(self.round), case, version, "--trial", str(trial))
        return Path(result.stdout.strip())

    def blocked(self, attempt: Path) -> None:
        # Trusted executor test double records infrastructure failure, not behavior.
        executable = self.directory / "fake-codex"
        executable.write_text("#!/usr/bin/env python3\nimport sys\nif '--version' in sys.argv: print('test-double')\nelif 'sandbox' in sys.argv: sys.exit(7)\nelse: sys.exit(99)\n")
        executable.chmod(0o755)
        self.cli("run", str(self.round), str(attempt), "--codex", str(executable))

    def judgment(self, attempt: Path, result: str = "indeterminate") -> Path:
        path = self.directory / "judgment.json"
        self.cli("judge-template", str(self.round), str(attempt), str(path))
        value = json.loads(path.read_text())
        value["judge_id"] = "independent-test-fixture"
        for section in ("observations", "common_metrics"):
            for finding in value[section].values():
                finding.update(result=result, reason="Infrastructure failure prevents semantic observation", evidence=["execution.json"])
        path.write_text(json.dumps(value))
        return path

    def test_pinned_inputs_and_new_track(self) -> None:
        value = json.loads((self.round / "spec.json").read_text())
        self.assertEqual(len(value["cases"]), 32)
        self.assertEqual(sum(len(case["versions"]) for case in value["cases"]), 64)
        self.cli("prepare", str(self.round), "explain-this-normal", "v7.3.7", ok=False)
        attempt = self.prepare("explain-this-normal", "v7.5.0")
        metadata = json.loads((attempt / "attempt.json").read_text())
        self.assertEqual(metadata["track"], "v7.5.0-attainment")
        self.assertIsNone(metadata["effective_parent"]["model"])
        self.assertIsNone(metadata["loaded_distribution"])

    def test_source_snapshots_are_separate_from_eval_git_history(self) -> None:
        spec = json.loads((self.round / "spec.json").read_text())
        self.assertEqual(spec["source_repository"], str(self.source_repository))
        for sha in spec["versions"].values():
            result = subprocess.run(["git", "cat-file", "-e", sha], cwd=ROOT, capture_output=True)
            self.assertNotEqual(result.returncode, 0, "Core history must not be imported into the eval repository")
        expected = subprocess.run(["git", "show", spec["versions"]["v7.3.7"] + ":plugins/codex/skills/test-report/SKILL.md"], cwd=self.source_repository, capture_output=True, check=True).stdout
        self.assertEqual((self.round / "distributions/v7.3.7/plugins/codex/skills/test-report/SKILL.md").read_bytes(), expected)

    def test_frozen_expectation_and_distribution_tampering_fail_closed(self) -> None:
        spec = self.round / "spec.json"
        original = spec.read_bytes()
        spec.write_bytes(original + b" ")
        self.cli("prepare", str(self.round), "test-report-normal", "v7.3.7", ok=False)
        spec.write_bytes(original)
        source = self.round / "distributions/v7.3.7/plugins/codex/skills/test-report/SKILL.md"
        source.write_text(source.read_text() + "tampered")
        self.cli("report", str(self.round), ok=False)

    def test_snapshot_preserves_explicit_review_target_and_unrelated_dirty(self) -> None:
        attempt = self.prepare("impl-review-boundary", "v7.5.0")
        metadata = json.loads((attempt / "attempt.json").read_text())
        self.assertIn("app.py", metadata["before"]["diff"])
        self.assertIn("unrelated.txt", metadata["before"]["diff"])
        self.assertIn("Human", (attempt / "workspace/unrelated.txt").read_text())
        self.assertEqual(subprocess.run(["git", "remote"], cwd=attempt / "workspace", capture_output=True).stdout, b"")

    def test_trials_are_append_only_and_additional_reason_is_required(self) -> None:
        self.prepare()
        self.cli("prepare", str(self.round), "test-report-normal", "v7.3.7", ok=False)
        self.cli("prepare", str(self.round), "test-report-normal", "v7.3.7", "--trial", "4", ok=False)
        self.cli("prepare", str(self.round), "test-report-normal", "v7.3.7", "--trial", "4", "--reason", "Preregistered disagreement investigation")
        self.cli("freeze", str(self.round), ok=False)

    def test_failed_isolation_never_becomes_llm_or_skill_failure(self) -> None:
        attempt = self.prepare()
        self.blocked(attempt)
        execution = json.loads((attempt / "execution.json").read_text())
        self.assertEqual(execution["state"], "blocked")
        self.assertEqual(execution["evidence_kind"], "infrastructure-only")
        self.assertNotIn("command", execution)
        self.cli("adjudicate", str(self.round), str(attempt), str(self.judgment(attempt, "pass")), ok=False)
        self.cli("adjudicate", str(self.round), str(attempt), str(self.judgment(attempt)))
        self.cli("report", str(self.round))
        report = json.loads((self.round / "report.json").read_text())
        self.assertEqual(report["comparison"], "indeterminate")
        row = next(row for row in report["rows"] if row["case_id"] == "test-report-normal" and row["version"] == "v7.3.7")
        self.assertEqual(row["missing_initial_trials"], [1, 2, 3])
        self.assertEqual(row["spec_conformance"], "indeterminate")

    def test_report_rejects_modified_execution_evidence(self) -> None:
        attempt = self.prepare()
        self.blocked(attempt)
        (attempt / "execution.json").write_text('{}')
        self.cli("report", str(self.round), ok=False)

    def test_report_rejects_modified_judgment(self) -> None:
        attempt = self.prepare()
        self.blocked(attempt)
        self.cli("adjudicate", str(self.round), str(attempt), str(self.judgment(attempt)))
        (attempt / "judgment.json").write_text('{}')
        self.cli("report", str(self.round), ok=False)

    def test_execution_refuses_fixture_or_agent_drift(self) -> None:
        attempt = self.prepare()
        source = attempt / "workspace/app.py"
        original = source.read_bytes()
        source.write_text("def quote(weight, express=False): return 0")
        self.cli("run", str(self.round), str(attempt), ok=False)
        self.assertFalse((attempt / "execution.json").exists())
        source.write_bytes(original)
        config = attempt / "workspace/.codex/agents/implementer.toml"
        config.write_text(config.read_text() + "# modified")
        self.cli("run", str(self.round), str(attempt), ok=False)

    def test_comparison_is_independent_and_requires_repeated_llm_evidence(self) -> None:
        packet = {"round_id": json.loads((self.round / "spec.json").read_text())["round_id"],
                  "judge_id": "independent-test-fixture", "independent": True,
                  "decisions": [{"case_id": "test-report-normal", "baseline": "v7.3.7", "candidate": "v7.5.0",
                                 "result": "worsened", "reason": "Test comparison", "metric_ids": ["task-usefulness"], "evidence": []}]}
        path = self.directory / "comparison.json"
        path.write_text(json.dumps(packet))
        self.cli("compare", str(self.round), str(path), ok=False)
        packet["decisions"][0]["result"] = "indeterminate"
        path.write_text(json.dumps(packet))
        self.cli("compare", str(self.round), str(path))
        self.cli("report", str(self.round))
        self.assertIn("Test comparison", (self.round / "report.md").read_text())
        self.cli("compare", str(self.round), str(path), ok=False)

    def test_synthetic_turn_preserves_artifact_bytes_without_becoming_eval(self) -> None:
        attempt = self.prepare("visualize-that-normal", "v7.5.0")
        executable = self.directory / "synthetic-codex"
        executable.write_text("""#!/usr/bin/env python3
import json, pathlib, sys
if '--version' in sys.argv:
    print('synthetic-test-double')
elif 'sandbox' in sys.argv:
    print(json.dumps({key: True for key in ['fixture_write', 'outside_read_blocked', 'outside_write_blocked', 'distribution_write_blocked', 'agent_config_write_blocked', 'skill_discovery_write_blocked', 'network_blocked', 'push_blocked']}))
else:
    root = pathlib.Path(sys.argv[sys.argv.index('-C') + 1])
    (root / 'diagram.html').write_text('<html>synthetic fixture only</html>')
    source = (root / '.agents/skills/visualize-that/SKILL.md').resolve()
    print(json.dumps({'type': 'item.completed', 'item': {'type': 'collabAgentToolCall', 'tool': 'spawnAgent', 'receiverThreadIds': ['resolved-child', 'requested-only-child'], 'model': 'requested-test-model', 'reasoningEffort': 'medium'}}))
    print(json.dumps({'type': 'item.completed', 'item': {'type': 'subAgentActivity', 'kind': 'started', 'agentThreadId': 'resolved-child', 'model': 'runtime-resolved-model', 'reasoningEffort': 'high'}}))
    print(json.dumps({'type': 'item.completed', 'item': {'type': 'commandExecution', 'command': 'cat ' + str(source), 'cwd': str(root), 'exitCode': 0, 'aggregatedOutput': source.read_text()}}))
    print(json.dumps({'type': 'item.completed', 'item': {'type': 'commandExecution', 'command': 'cat ' + str(source), 'cwd': str(root), 'exitCode': 0, 'aggregatedOutput': source.read_text()[:20]}}))
    print(json.dumps({'type': 'item.completed', 'item': {'type': 'agent_message', 'text': 'synthetic fixture only; effective model is imagined-self-report'}}))
    print(json.dumps({'type': 'turn.completed', 'usage': {'input_tokens': 0, 'output_tokens': 0}}))
""")
        executable.chmod(0o755)
        self.cli("run", str(self.round), str(attempt), "--codex", str(executable), "--synthetic")
        execution = json.loads((attempt / "execution.json").read_text())
        self.assertEqual(execution["evidence_kind"], "synthetic")
        self.assertIsNone(execution["effective_parent"]["model"])
        children = {child["thread_id"]: child for child in execution["spawned_children"]}
        self.assertEqual(children["resolved-child"]["requested_model"], "requested-test-model")
        self.assertEqual(children["resolved-child"]["effective_model"], "runtime-resolved-model")
        self.assertIsNone(children["requested-only-child"]["effective_model"])
        self.assertEqual(execution["loaded_distribution"]["coverage"], "partial-content-observed")
        self.assertEqual(len(execution["loaded_distribution"]["full_reads"]), 1)
        self.assertEqual((attempt / "artifacts/diagram.html").read_text(), '<html>synthetic fixture only</html>')
        self.cli("adjudicate", str(self.round), str(attempt), str(self.judgment(attempt, "pass")), ok=False)
        (attempt / "artifacts/diagram.html").write_text("modified")
        self.cli("adjudicate", str(self.round), str(attempt), str(self.judgment(attempt)), ok=False)

    def test_prepared_only_comparison_remains_indeterminate(self) -> None:
        for version in ("v7.3.7", "v7.5.0"):
            self.prepare(version=version)
        packet = {"round_id": json.loads((self.round / "spec.json").read_text())["round_id"],
                  "judge_id": "independent-test-fixture", "independent": True,
                  "decisions": [{"case_id": "test-report-normal", "baseline": "v7.3.7", "candidate": "v7.5.0",
                                 "result": "indeterminate", "reason": "Prepared but not run", "metric_ids": ["task-usefulness"], "evidence": []}]}
        path = self.directory / "comparison.json"
        path.write_text(json.dumps(packet))
        self.cli("compare", str(self.round), str(path))
        self.cli("report", str(self.round))
        report = json.loads((self.round / "report.json").read_text())
        self.assertEqual(report["comparison"][0]["result"], "indeterminate")
        self.assertEqual(next(row for row in report["rows"] if row["case_id"] == "test-report-normal")["missing_initial_trials"], [1, 2, 3])

    def test_renderer_feature_normalization_is_not_assumed(self) -> None:
        attempt = self.prepare("visualize-that-failure", "v7.5.0")
        executable = self.directory / "fake-render-codex"
        features = ["browser_use", "browser_use_external", "browser_use_full_cdp_access", "in_app_browser", "browser_annotation_api", "image_generation", "view_image", "shell_tool", "unified_exec"]
        executable.write_text("#!/usr/bin/env python3\nimport sys\nfeatures=" + repr(features) + "\nif 'features' in sys.argv:\n    for feature in features: print(feature, 'stable', 'true' if feature=='unified_exec' else 'false')\nelif '--version' in sys.argv: print('test-double')\nelif 'sandbox' in sys.argv: sys.exit(7)\nelse: sys.exit(99)\n")
        executable.chmod(0o755)
        self.cli("run", str(self.round), str(attempt), "--codex", str(executable))
        execution = json.loads((attempt / "execution.json").read_text())
        self.assertEqual(execution["state"], "blocked")
        self.assertTrue(execution["checks"]["renderer_controls"]["observed_features"]["unified_exec"])
        self.assertNotIn("command", execution)

    def test_git_configuration_is_rejected_before_host_hooks_can_execute(self) -> None:
        attempt = self.prepare()
        marker = self.directory / "host-command-ran"
        hook = self.directory / "fsmonitor-hook"
        hook.write_text(f"#!/bin/sh\ntouch '{marker}'\necho token\n")
        hook.chmod(0o755)
        subprocess.run(["git", "config", "core.fsmonitor", str(hook)], cwd=attempt / "workspace", check=True)
        self.cli("run", str(self.round), str(attempt), ok=False)
        self.assertFalse(marker.exists())
        self.assertFalse((attempt / "execution.json").exists())

    def test_comparison_rejects_other_case_evidence(self) -> None:
        other = self.prepare("test-report-boundary")
        self.blocked(other)
        self.cli("adjudicate", str(self.round), str(other), str(self.judgment(other)))
        packet = {"round_id": json.loads((self.round / "spec.json").read_text())["round_id"],
                  "judge_id": "independent-test-fixture", "independent": True,
                  "decisions": [{"case_id": "test-report-normal", "baseline": "v7.3.7", "candidate": "v7.5.0",
                                 "result": "indeterminate", "reason": "Wrong evidence must be rejected", "metric_ids": ["task-usefulness"],
                                 "evidence": [str((other / "judgment.json").relative_to(self.round))]}]}
        path = self.directory / "comparison.json"
        path.write_text(json.dumps(packet))
        self.cli("compare", str(self.round), str(path), ok=False)

    def test_complete_comparison_packet_and_report(self) -> None:
        references = []
        for version in ("v7.3.7", "v7.5.0"):
            for trial in (1, 2, 3):
                attempt = self.prepare(version=version, trial=trial)
                # Stored telemetry fixture for the consumer protocol only. This is
                # fabricated unit-test input, never an actual evaluation run.
                execution = {"state": "completed", "evidence_kind": "llm", "test_fixture": True}
                (attempt / "execution.json").write_text(json.dumps(execution))
                (attempt / "evidence-seal.json").write_text(json.dumps({"execution.json": hashlib.sha256((attempt / "execution.json").read_bytes()).hexdigest()}))
                self.cli("adjudicate", str(self.round), str(attempt), str(self.judgment(attempt, "pass")))
                references.append(str((attempt / "judgment.json").relative_to(self.round)))
        packet = {"round_id": json.loads((self.round / "spec.json").read_text())["round_id"],
                  "judge_id": "independent-test-fixture", "independent": True,
                  "decisions": [{"case_id": "test-report-normal", "baseline": "v7.3.7", "candidate": "v7.5.0",
                                 "result": "equivalent", "reason": "Unit-test protocol fixture only", "metric_ids": ["task-usefulness"], "evidence": references}]}
        path = self.directory / "comparison.json"
        path.write_text(json.dumps(packet))
        self.cli("compare", str(self.round), str(path))
        self.cli("report", str(self.round))
        result = json.loads((self.round / "report.json").read_text())
        self.assertEqual(result["comparison"][0]["result"], "equivalent")
        row = next(item for item in result["rows"] if item["case_id"] == "test-report-normal" and item["version"] == "v7.5.0")
        self.assertEqual(row["spec_conformance"], "pass")
        self.assertEqual(row["missing_initial_trials"], [])

    def test_rubric_coverage_is_exact_and_external_references_are_rejected(self) -> None:
        attempt = self.prepare()
        self.blocked(attempt)
        path = self.judgment(attempt)
        value = json.loads(path.read_text())
        value["common_metrics"].pop("uncertainty-honesty")
        path.write_text(json.dumps(value))
        self.cli("adjudicate", str(self.round), str(attempt), str(path), ok=False)
        path = self.judgment(attempt)
        value = json.loads(path.read_text())
        value["observations"]["responsibility"]["evidence"] = ["../../outside"]
        path.write_text(json.dumps(value))
        self.cli("adjudicate", str(self.round), str(attempt), str(path), ok=False)


if __name__ == "__main__":
    unittest.main()
