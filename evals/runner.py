#!/usr/bin/env python3
"""Frozen, evidence-first Tugite behavior evaluation (Python 3.11+, stdlib only)."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import re
import shutil
import signal
import shlex
import socket
import subprocess
import sys
import tarfile
import tempfile
import time
import tomllib
import uuid

ROOT = Path(__file__).resolve().parents[1]
SOURCE_REPOSITORY = "https://github.com/akitanabe/tugite.git"
VERSIONS = {
    "v7.3.7": "886e919a16ff6d318ed824ab53e8335362261c95",
    "v7.4.0": "7578104046e97bc93d8cddffb882983827db3b0f",
    "v7.5.0": "144cfb813efab5c4581d229a9ea221095cc4c55d",
}
CONTINUING = {"impl-lead", "test-report", "test-verify", "visualize-that"}
NEW = {"explain-this", "review-propose", "impl-plan", "impl-review"}
RESULTS = {"pass", "fail", "indeterminate"}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def write_json(path: Path, value: object) -> None:
    path.write_bytes(canonical(value))


def command(args: list[str], cwd: Path | None = None, timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, capture_output=True, timeout=timeout, check=False)


def git(*args: str, cwd: Path = ROOT) -> bytes:
    safe_args = list(args)
    if safe_args and safe_args[0] == "diff":
        safe_args[1:1] = ["--no-ext-diff", "--no-textconv", "--ignore-submodules=all"]
    result = command(["git", "-c", "core.fsmonitor=false", "-c", "core.hooksPath=/dev/null", *safe_args], cwd)
    if result.returncode:
        raise ValueError(result.stderr.decode(errors="replace"))
    return result.stdout


def safe_path(root: Path, relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ValueError(f"unsafe relative path: {relative}")
    target = root / path
    if not target.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"path escapes root: {relative}")
    return target


def file_inventory(root: Path) -> dict[str, str]:
    result = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"symlink in evidence: {path}")
        if path.is_file() and ".git" not in path.relative_to(root).parts:
            result[path.relative_to(root).as_posix()] = digest(path.read_bytes())
    return result


def fetch_source(repository: str, destination: Path) -> None:
    """Read fixed snapshots from the source repo, never this eval repo's object DB."""
    if repository != SOURCE_REPOSITORY:
        local_source = Path(repository).resolve()
        if not local_source.is_dir():
            raise ValueError("source must be the canonical Tugite URL or an existing local Git repository")
        repository = str(local_source)
    git("init", "--bare", "-q", str(destination))
    refs = [f"{sha}:refs/tugite-eval/{version}" for version, sha in VERSIONS.items()]
    git("fetch", "--no-tags", "--depth=1", "--update-shallow", repository, *refs, cwd=destination)
    for version, sha in VERSIONS.items():
        if git("rev-parse", f"refs/tugite-eval/{version}^{{commit}}", cwd=destination).decode().strip() != sha:
            raise ValueError("source version identity mismatch")


def unpack_distribution(sha: str, destination: Path, source_repository: Path) -> None:
    data = git("archive", sha, "plugins/codex", cwd=source_repository)
    destination.mkdir(parents=True)
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        for member in archive.getmembers():
            safe_path(destination, member.name)
            if not (member.isdir() or member.isfile()):
                raise ValueError("distribution must contain regular files/directories")
        archive.extractall(destination, filter="data")


def validate_case(case: dict, distributions: Path) -> dict:
    skill = case["skill"]
    expected_versions = list(VERSIONS) if skill in CONTINUING else ["v7.5.0"]
    if skill not in CONTINUING | NEW or case["versions"] != expected_versions:
        raise ValueError(f"invalid track/versions: {case['id']}")
    if case["category"] not in {"normal", "boundary", "failure", "ambiguous"}:
        raise ValueError("invalid category")
    if not re.fullmatch(r"[a-z0-9-]+", case["id"]):
        raise ValueError("invalid case id")
    if not case["observations"] or not case["common_metrics"]:
        raise ValueError("observations and common metrics are required")
    ids = set()
    for observation in case["observations"]:
        if observation["id"] in ids:
            raise ValueError("duplicate observation id")
        ids.add(observation["id"])
        if not set(observation["versions"]) <= set(expected_versions) or not observation["versions"]:
            raise ValueError("invalid observation applicability")
        for version in observation["versions"]:
            basis = observation["basis"][version]
            path = safe_path(distributions / version / "plugins/codex", basis["path"])
            content = path.read_text()
            if basis["quote"] not in content:
                raise ValueError(f"basis not found: {case['id']}/{version}/{observation['id']}")
            basis["sha256"] = digest(path.read_bytes())
    return case


def freeze(destination: Path, corpus: Path, model: str, effort: str, source_repository: str = SOURCE_REPOSITORY) -> None:
    """Create once; every input, rubric and distribution is fixed before a trial."""
    destination.mkdir(parents=True, exist_ok=False)
    try:
        with tempfile.TemporaryDirectory(prefix="tugite-eval-source-") as temporary:
            source_git = Path(temporary) / "source.git"
            fetch_source(source_repository, source_git)
            for version, sha in VERSIONS.items():
                unpack_distribution(sha, destination / "distributions" / version, source_git)
        source = read_json(corpus)
        cases = []
        seen = set()
        for case in source["cases"]:
            if case["id"] in seen:
                raise ValueError("duplicate case id")
            seen.add(case["id"])
            fixture = source["fixtures"][case.pop("fixture")].copy()
            fixture.update(case.pop("overrides", {}))
            for relative in list(fixture) + list(case.get("working_changes", {})):
                safe_path(destination, relative)
                if relative.startswith((".git/", ".codex/", ".agents/")):
                    raise ValueError("fixture cannot supply runtime configuration")
            case["files"] = fixture
            case["common_metrics"] = {name: source["common_metrics"][name] for name in case["common_metrics"]}
            cases.append(validate_case(case, destination / "distributions"))
        if not cases:
            raise ValueError("empty corpus")
        write_json(destination / "spec.json", {
            "schema": 1, "round_id": str(uuid.uuid4()), "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "versions": VERSIONS, "source_repository": source_repository,
            "source_acquisition": "separate temporary bare Git repository; shallow fetch of exact SHAs",
            "requested": {"model": model, "effort": effort},
            "repetition": {"initial": 3, "maximum": 5, "additional": "disagreement or indeterminate; record reason before running trials 4/5", "stop": "5 trials, infrastructure denial, identity drift, or safety failure"},
            "cases": cases,
        })
        shutil.copy2(Path(__file__), destination / "runner.py")
        write_json(destination / "seal.json", file_inventory(destination))
        (destination / "attempts").mkdir()
    except Exception:
        shutil.rmtree(destination)
        raise


def verify_round(round_path: Path) -> dict:
    seal = read_json(round_path / "seal.json")
    actual = file_inventory(round_path / "distributions")
    expected = {k.removeprefix("distributions/"): v for k, v in seal.items() if k.startswith("distributions/")}
    if actual != expected:
        raise ValueError("frozen distribution identity drift")
    if digest(Path(__file__).read_bytes()) != seal["runner.py"]:
        raise ValueError("executing runner identity differs from frozen runner")
    for relative in ("spec.json", "runner.py"):
        if digest((round_path / relative).read_bytes()) != seal[relative]:
            raise ValueError(f"frozen {relative} identity drift")
    return read_json(round_path / "spec.json")


def choose_case(spec: dict, case_id: str, version: str) -> dict:
    case = next((item for item in spec["cases"] if item["id"] == case_id), None)
    if case is None:
        raise ValueError("unknown case")
    if version not in case["versions"]:
        raise ValueError("not-applicable: no baseline exists for this skill")
    return case


def prepare(round_path: Path, case_id: str, version: str, trial: int, reason: str | None) -> Path:
    spec = verify_round(round_path)
    case = choose_case(spec, case_id, version)
    if trial not in range(1, 6) or (trial > 3 and not reason):
        raise ValueError("trial must be 1..5; trials 4/5 need a preregistered reason")
    attempt = round_path / "attempts" / f"{case_id}--{version}--{trial}"
    attempt.mkdir(exist_ok=False)
    workspace = attempt / "workspace"
    workspace.mkdir()
    for relative, content in case["files"].items():
        target = safe_path(workspace, relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
    git("init", "-q", cwd=workspace)
    git("add", ".", cwd=workspace)
    git("-c", "user.name=Eval Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "固定した評価入力", cwd=workspace)
    # No remote: push is additionally blocked by tool network and outside-write restrictions.
    for relative, content in case.get("working_changes", {}).items():
        safe_path(workspace, relative).write_text(content)
    bundle = round_path / "distributions" / version / "plugins/codex"
    installer = command(["bash", str(bundle / "install/install-agents.sh"), "--repo", str(workspace)])
    if installer.returncode:
        raise ValueError(installer.stderr.decode() + installer.stdout.decode())
    (attempt / "installer.txt").write_bytes(installer.stdout + installer.stderr)
    # All dependencies/references/custom agents remain available. Discovery links are
    # runtime staging, never evidence of actual model loading.
    discovery = workspace / ".agents/skills"
    discovery.mkdir(parents=True)
    for skill in (bundle / "skills").iterdir():
        (discovery / skill.name).symlink_to(skill.resolve(), target_is_directory=True)
    available = {}
    for path in sorted((workspace / ".codex/agents").glob("*.toml")):
        definition = tomllib.loads(path.read_text())
        available[definition["name"]] = {"definition_sha256": digest(path.read_bytes()),
            "requested_model": definition.get("model"), "requested_effort": definition.get("model_reasoning_effort"),
            "effective_model": None, "effective_effort": None}
    # Baseline overlays are explicit experiment settings, separate from immutable distribution.
    for path in (workspace / ".codex/agents").glob("*.toml"):
        content = path.read_text()
        for key, value in (("model", spec["requested"]["model"]), ("model_reasoning_effort", spec["requested"]["effort"])):
            content = re.sub(rf"^{key} = .*?$", f"{key} = {json.dumps(value)}", content, flags=re.MULTILINE)
        path.write_text(content)
    staged = {path.name: digest(path.read_bytes()) for path in (workspace / ".codex/agents").glob("*.toml")}
    # Snapshot fixture before runtime directories (which contain symlinks).
    before = {"head": git("rev-parse", "HEAD", cwd=workspace).decode().strip(),
              "files": {key: digest((workspace / key).read_bytes()) for key in case["files"]},
              "status": git("status", "--porcelain=v1", cwd=workspace).decode(),
              "git_config": digest((workspace / ".git/config").read_bytes()),
              "git_hooks": file_inventory(workspace / ".git/hooks"),
              "diff": git("diff", "HEAD", cwd=workspace).decode()}
    prompt = (f"Use ${case['skill']} by reading {bundle.resolve()}/skills/{case['skill']}/SKILL.md. "
              "Resolve its references against that distribution. Available custom agents are installed in .codex/agents. "
              "This is a fresh invocation. Work only inside the supplied disposable repository. "
              "No remote/network/push authority. Do not install dependencies.\n\n" + case["prompt"])
    (attempt / "prompt.txt").write_text(prompt)
    applicable = [observation for observation in case["observations"] if version in observation["versions"]]
    write_json(attempt / "rubric.json", {"observations": applicable, "common_metrics": case["common_metrics"]})
    write_json(attempt / "attempt.json", {
        "schema": 1, "attempt_id": str(uuid.uuid4()), "round_id": spec["round_id"],
        "case_id": case_id, "version": version, "repo_sha": VERSIONS[version], "trial": trial,
        "additional_reason": reason, "track": "comparison" if case["skill"] in CONTINUING else "v7.5.0-attainment",
        "requested_parent": spec["requested"], "effective_parent": {"model": None, "effort": None},
        "available_agents": available, "child_overlay": spec["requested"], "staged_agent_hashes": staged, "staged_config": file_inventory(workspace / ".codex"),
        "discovery": {path.name: str(path.readlink()) for path in discovery.iterdir()},
        "spawned_children": None, "loaded_distribution": None, "cost": None,
        "before": before, "runtime": {"python": platform.python_version(), "os": platform.platform()},
        "state": "prepared", "evidence_kind": "not-run",
    })
    write_json(attempt / "input-seal.json", {name: digest((attempt / name).read_bytes()) for name in ("prompt.txt", "rubric.json", "attempt.json")})
    return attempt


def verify_attempt(round_path: Path, attempt: Path) -> tuple[dict, dict]:
    spec = verify_round(round_path)
    if attempt.parent.resolve() != (round_path / "attempts").resolve():
        raise ValueError("attempt must belong to round")
    metadata = read_json(attempt / "attempt.json")
    if metadata["round_id"] != spec["round_id"]:
        raise ValueError("round identity mismatch")
    for name, expected in read_json(attempt / "input-seal.json").items():
        if digest((attempt / name).read_bytes()) != expected:
            raise ValueError("attempt input identity drift")
    return spec, metadata


def verify_evidence(attempt: Path) -> None:
    for name, expected in read_json(attempt / "evidence-seal.json").items():
        if digest(safe_path(attempt, name).read_bytes()) != expected:
            raise ValueError("execution evidence identity drift")
    judgment = attempt / "judgment.json"
    if judgment.exists() and digest(judgment.read_bytes()) != (attempt / "judgment.sha256").read_text().strip():
        raise ValueError("judgment identity drift")


def verify_workspace(attempt: Path, metadata: dict) -> None:
    workspace = attempt / "workspace"
    if digest((workspace / ".git/config").read_bytes()) != metadata["before"]["git_config"] or file_inventory(workspace / ".git/hooks") != metadata["before"]["git_hooks"]:
        raise ValueError("prepared Git configuration/hooks drift")
    files = {str(path.relative_to(workspace)): digest(path.read_bytes()) for path in workspace.rglob("*")
             if path.is_file() and not path.is_symlink() and not set(path.relative_to(workspace).parts) & {".git", ".agents", ".codex"}}
    if files != metadata["before"]["files"] or git("rev-parse", "HEAD", cwd=workspace).decode().strip() != metadata["before"]["head"]:
        raise ValueError("prepared fixture identity drift")
    if git("diff", "HEAD", cwd=workspace).decode() != metadata["before"]["diff"]:
        raise ValueError("prepared diff identity drift")
    if git("status", "--porcelain=v1", cwd=workspace).decode() != metadata["before"]["status"] or digest((workspace / ".git/config").read_bytes()) != metadata["before"]["git_config"] or file_inventory(workspace / ".git/hooks") != metadata["before"]["git_hooks"]:
        raise ValueError("prepared repository configuration/status drift")
    expected_discovery_paths = {"skills"} | {"skills/" + name for name in metadata["discovery"]}
    if {str(path.relative_to(workspace / ".agents")) for path in (workspace / ".agents").rglob("*")} != expected_discovery_paths:
        raise ValueError("agent discovery layout drift")
    if file_inventory(workspace / ".codex") != metadata["staged_config"]:
        raise ValueError("custom agent configuration drift")
    discovery = workspace / ".agents/skills"
    if any(not path.is_symlink() for path in discovery.iterdir()) or {path.name: str(path.readlink()) for path in discovery.iterdir()} != metadata["discovery"]:
        raise ValueError("skill discovery identity drift")


def profile_arguments(workspace: Path, distribution: Path, temporary: Path) -> list[str]:
    # CLI config, not model instructions, owns tool effects. Keep credentials and
    # other checkouts outside readable roots; runtime authentication stays in the host process.
    paths = {"/": "none", "/usr": "read", "/bin": "read", "/lib": "read", "/lib64": "read",
             "/opt": "read", "/etc": "read", "/dev": "write",
             str(workspace): "write", str(distribution): "read", str(temporary): "write",
             str(workspace / ".git"): "write", str(workspace / ".codex"): "read",
             str(workspace / ".agents"): "read"}
    encoded = "{" + ", ".join(f"{json.dumps(key)}={json.dumps(value)}" for key, value in paths.items()) + "}"
    return ["-c", 'default_permissions="eval"', "-c", "permissions.eval.file_system=" + encoded,
            "-c", "permissions.eval.network.enabled=false", "-c", 'approval_policy="never"',
            "-c", 'web_search="disabled"', "-c", 'features.apps=false',
            "-c", 'shell_environment_policy.inherit="none"']


def canary(executable: str, arguments: list[str], attempt: Path) -> dict:
    workspace = attempt / "workspace"
    sentinel = attempt / "secret-canary"
    sentinel.write_text("nonsecret-read-isolation-canary")
    forbidden = attempt / "outside-write-canary"
    remote = attempt / "push-target.git"
    git("init", "--bare", "-q", str(remote))
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen()
    port = listener.getsockname()[1]
    # Check forbidden reads/writes, a real local push, and a reachable TCP endpoint.
    # Every failed control is fatal; failure to start the probe is not protection evidence.
    script = """
import json, pathlib, socket, subprocess, sys
workspace, sentinel, outside, distribution, remote, port = sys.argv[1:]
checks = {}
p = pathlib.Path(workspace) / 'allowed-canary'
try:
    p.write_text('ok'); checks['fixture_write'] = p.read_text() == 'ok'; p.unlink()
except OSError:
    checks['fixture_write'] = False
try:
    pathlib.Path(sentinel).read_bytes(); checks['outside_read_blocked'] = False
except OSError:
    checks['outside_read_blocked'] = True
for label, target in [('outside_write_blocked', outside),
                      ('distribution_write_blocked', distribution + '/.canary'),
                      ('agent_config_write_blocked', workspace + '/.codex/.canary'),
                      ('skill_discovery_write_blocked', workspace + '/.agents/.canary')]:
    try:
        pathlib.Path(target).write_text('unsafe'); checks[label] = False
    except OSError:
        checks[label] = True
try:
    with socket.create_connection(('127.0.0.1', int(port)), timeout=2):
        checks['network_blocked'] = False
except OSError:
    checks['network_blocked'] = True
result = subprocess.run(['git', '-c', 'protocol.file.allow=always', 'push', remote, 'HEAD:refs/heads/escape'], cwd=workspace, capture_output=True)
checks['push_blocked'] = result.returncode != 0
print(json.dumps(checks))
sys.exit(0 if all(checks.values()) else 1)
"""
    try:
        result = command([executable, "sandbox", "-P", "eval", *arguments, "-C", str(workspace),
            sys.executable, "-c", script, str(workspace), str(sentinel), str(forbidden),
            str(attempt.parent.parent / "distributions" / read_json(attempt / "attempt.json")["version"]),
            str(remote), str(port)])
        try:
            checks = json.loads(result.stdout)
        except (ValueError, TypeError):
            checks = {}
        unchanged = not forbidden.exists() and not (remote / "refs/heads/escape").exists()
        return {"passed": result.returncode == 0 and len(checks) == 8 and all(checks.values()) and unchanged,
                "returncode": result.returncode, "checks": checks,
                "stdout": result.stdout.decode(errors="replace"), "stderr": result.stderr.decode(errors="replace")}
    finally:
        listener.close()
        sentinel.unlink(missing_ok=True)
        for owned_canary in (forbidden, workspace / ".codex/.canary", workspace / ".agents/.canary",
                              attempt.parent.parent / "distributions" / read_json(attempt / "attempt.json")["version"] / ".canary"):
            owned_canary.unlink(missing_ok=True)


def scrub(text: str) -> str:
    text = re.sub(r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]+", r"\1[REDACTED]", text)
    text = re.sub(r"\b(?:sk-[A-Za-z0-9_-]{12,}|gh[pousr]_[A-Za-z0-9_]+)\b", "[REDACTED]", text)
    return text


RENDER_FEATURES = ("browser_use", "browser_use_external", "browser_use_full_cdp_access", "in_app_browser",
                   "browser_annotation_api", "image_generation", "view_image", "shell_tool", "unified_exec")


def renderer_controls(executable: str, arguments: list[str]) -> dict:
    result = command([executable, "features", "list", *arguments])
    observed = {}
    for line in result.stdout.decode(errors="replace").splitlines():
        columns = line.split()
        if columns and columns[0] in RENDER_FEATURES and columns[-1] in {"true", "false"}:
            observed[columns[0]] = columns[-1] == "true"
    return {"passed": result.returncode == 0 and set(observed) == set(RENDER_FEATURES) and not any(observed.values()),
            "observed_features": observed, "returncode": result.returncode,
            "stderr": scrub(result.stderr.decode(errors="replace")),
            "scope": "CLI feature configuration only; first successful execution must also verify tool surface and absence of alternate server-side tools"}


def decode_telemetry(events: list[dict], distribution: Path) -> dict:
    """Decode only runtime provenance, never model prose or requested defaults.

    v2 ThreadItem schema identifies collabAgentToolCall.model as *requested*,
    subAgentActivity.model as *resolved at creation*, and commandActions as
    best-effort. Full read output must match a frozen file before recording it.
    """
    parent = {"model": None, "effort": None}
    children = {}
    settings = []
    reads = []
    for line, event in enumerate(events, 1):
        if not isinstance(event, dict):
            continue
        provenance = {"file": "events.jsonl", "event_ordinal": line, "event_type": event.get("type", event.get("method"))}
        if event.get("type") == "response.completed" and isinstance(event.get("response"), dict):
            response = event["response"]
            if isinstance(response.get("model"), str):
                parent["model"] = response["model"]
                parent["provenance"] = provenance
            reasoning = response.get("reasoning")
            if isinstance(reasoning, dict) and isinstance(reasoning.get("effort"), str):
                parent["effort"] = reasoning["effort"]
        if event.get("method") == "thread/settingsUpdated":
            params = event.get("params", {})
            settings.append({"thread_id": params.get("threadId"), "settings": params.get("threadSettings"),
                             "provenance": provenance, "meaning": "runtime settings; not provider-returned model identity"})
        item = event.get("item")
        if event.get("method") == "item/completed":
            item = event.get("params", {}).get("item")
        if not isinstance(item, dict):
            continue
        kind = item.get("type")
        if kind in {"collabAgentToolCall", "collab_agent_tool_call"} and item.get("tool") in {"spawnAgent", "spawn_agent"}:
            for child_id in item.get("receiverThreadIds", item.get("receiver_thread_ids", [])):
                child = children.setdefault(child_id, {"thread_id": child_id, "effective_model": None, "effective_effort": None})
                child.update(requested_model=item.get("model"), requested_effort=item.get("reasoningEffort", item.get("reasoning_effort")),
                             request_provenance=provenance)
        if kind in {"subAgentActivity", "sub_agent_activity"} and item.get("kind") == "started":
            child_id = item.get("agentThreadId", item.get("agent_thread_id"))
            if child_id:
                child = children.setdefault(child_id, {"thread_id": child_id, "effective_model": None, "effective_effort": None})
                child.update(effective_model=item.get("model"), effective_effort=item.get("reasoningEffort", item.get("reasoning_effort")),
                             resolved_provenance=provenance, setting_scope="runtime resolved at child creation; backend physical model is not attested")
        if kind not in {"commandExecution", "command_execution"} or item.get("exitCode", item.get("exit_code")) != 0:
            continue
        # General shell parsing and best-effort read tags are insufficient. Only
        # an exact cat command + full matching output is a full-content witness.
        try:
            words = shlex.split(item.get("command", ""))
            if len(words) == 3 and Path(words[0]).name in {"bash", "sh"} and words[1] in {"-c", "-lc"}:
                words = shlex.split(words[2])
            if len(words) != 2 or words[0] != "cat":
                continue
            candidate = Path(words[1])
            if not candidate.is_absolute():
                candidate = Path(item.get("cwd", "/")) / candidate
            candidate = candidate.resolve()
            if not candidate.is_relative_to(distribution.resolve()) or not candidate.is_file():
                continue
            output = item.get("aggregatedOutput", item.get("aggregated_output"))
            if not isinstance(output, str) or output.encode() != candidate.read_bytes():
                continue
            reads.append({"path": str(candidate.relative_to(distribution.resolve())), "sha256": digest(output.encode()),
                          "provenance": provenance, "meaning": "full frozen content surfaced in tool output; semantic compliance not inferred"})
        except (ValueError, OSError):
            continue
    return {"effective_parent": parent, "spawned_children": list(children.values()) or None,
            "observed_runtime_settings": settings,
            "loaded_distribution": {"coverage": "partial-content-observed", "full_reads": reads} if reads else None}


def run(round_path: Path, attempt: Path, codex: str, timeout: int, synthetic: bool = False) -> None:
    _, metadata = verify_attempt(round_path, attempt)
    if (attempt / "execution.json").exists():
        raise ValueError("attempt execution already recorded; create a new trial")
    verify_workspace(attempt, metadata)
    executable = shutil.which(codex)
    checks = {}
    blockers = []
    if not executable:
        blockers.append("Codex CLI unavailable")
    else:
        result = command([executable, "--version"])
        checks["version"] = result.stdout.decode(errors="replace").strip()
    temporary = attempt / "tool-tmp"
    temporary.mkdir()
    distribution = round_path / "distributions" / metadata["version"]
    arguments = profile_arguments(attempt / "workspace", distribution, temporary)
    case = choose_case(verify_round(round_path), metadata["case_id"], metadata["version"])
    if case.get("capability_constraint") == "no-reviewer":
        arguments += ["-c", "features.multi_agent=false"]
    if case.get("capability_constraint") == "no-renderer":
        for feature in RENDER_FEATURES:
            arguments += ["-c", f"features.{feature}=false"]
        if executable:
            checks["renderer_controls"] = renderer_controls(executable, arguments)
            if not checks["renderer_controls"]["passed"]:
                blockers.append("Runtime did not confirm all renderer/shell/inspection features disabled")
    write_json(attempt / "permission-profile.json", arguments)
    if executable:
        try:
            checks["canary"] = canary(executable, arguments, attempt)
        except (OSError, subprocess.TimeoutExpired) as error:
            checks["canary"] = {"passed": False, "error": str(error)}
        if not checks["canary"]["passed"]:
            blockers.append("Runner isolation canary failed or could not start; no LLM session launched")
    execution = {"state": "blocked", "evidence_kind": "infrastructure-only",
        "attempt_id": metadata["attempt_id"], "checks": checks, "blockers": blockers, "synthetic": synthetic,
        "effective_parent": {"model": None, "effort": None}, "spawned_children": None,
        "loaded_distribution": None, "cost": None, "timeout_seconds": timeout}
    evidence_files = ["execution.json", "permission-profile.json"]
    if not blockers:
        # Same explicit named profile on sandbox and exec; no legacy sandbox flags
        # or approval escalation that could silently replace the tested profile.
        args = [executable, "exec", "--ignore-user-config", "--ephemeral", "--json", *arguments,
                "-m", metadata["requested_parent"]["model"], "-c",
                "model_reasoning_effort=" + json.dumps(metadata["requested_parent"]["effort"]),
                "-C", str(attempt / "workspace"), "-"]
        execution["command"] = args
        started = time.monotonic()
        with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
            process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=stdout, stderr=stderr,
                start_new_session=True, env={**os.environ, "TMPDIR": str(temporary)})
            try:
                process.communicate((attempt / "prompt.txt").read_bytes(), timeout=timeout)
                execution["state"] = "completed" if process.returncode == 0 else "failed"
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
                execution["state"] = "timeout"
            execution["returncode"] = process.returncode
            for name, stream in (("events.jsonl", stdout), ("stderr.txt", stderr)):
                stream.seek(0)
                data = stream.read(10_000_001)
                if len(data) > 10_000_000:
                    execution["state"] = "evidence-truncated"
                (attempt / name).write_text(scrub(data[:10_000_000].decode(errors="replace")))
                evidence_files.append(name)
        execution["duration_seconds"] = time.monotonic() - started
        # A started thread is not proof that inference succeeded. Only a completed
        # turn with an agent message establishes an LLM behavior observation.
        events = []
        for line in (attempt / "events.jsonl").read_text().splitlines():
            try:
                parsed = json.loads(line)
                if isinstance(parsed, dict):
                    events.append(parsed)
            except ValueError:
                continue
        if any(e.get("type") == "turn.completed" for e in events) and any(
                e.get("item", {}).get("type") == "agent_message" for e in events):
            execution["evidence_kind"] = "synthetic" if synthetic else "llm"
        execution.update(decode_telemetry(events, distribution))
        execution["usage"] = [e.get("usage") for e in events if e.get("type") == "turn.completed"]
        execution["telemetry_limit"] = "Effective parent/child settings, child inventory and actual distribution loads are unknown unless independently observed in runtime evidence; requested values never substitute."
        # Retain exact changes and all authored artifacts, including ignored files.
        # Runtime configuration symlinks are recorded separately and never followed.
        files = {}
        for path in sorted((attempt / "workspace").rglob("*")):
            relative = path.relative_to(attempt / "workspace")
            if not path.is_symlink() and path.is_file() and not set(relative.parts) & {".git", ".agents", ".codex", "__pycache__"}:
                files[str(relative)] = digest(path.read_bytes())
                target = safe_path(attempt / "artifacts", str(relative))
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(path.read_bytes())
                evidence_files.append("artifacts/" + str(relative))
        workspace = attempt / "workspace"
        git_configuration_safe = digest((workspace / ".git/config").read_bytes()) == metadata["before"]["git_config"] and file_inventory(workspace / ".git/hooks") == metadata["before"]["git_hooks"]
        after = {"files": files, "git_configuration_unchanged": git_configuration_safe}
        if git_configuration_safe:
            after.update(head=git("rev-parse", "HEAD", cwd=workspace).decode().strip(),
                         status=git("status", "--porcelain=v1", "--untracked-files=all", cwd=workspace).decode(),
                         diff=git("diff", metadata["before"]["head"], cwd=workspace).decode())
        else:
            execution["state"] = "repository-config-drift"
            execution["evidence_kind"] = "infrastructure-only"
        write_json(attempt / "after.json", after)
        evidence_files.append("after.json")
        try:
            verify_round(round_path)
            execution["frozen_distribution_unchanged"] = True
        except ValueError:
            execution["frozen_distribution_unchanged"] = False
            execution["state"] = "identity-drift"
            execution["evidence_kind"] = "infrastructure-only"
    write_json(attempt / "execution.json", execution)
    write_json(attempt / "evidence-seal.json", {name: digest((attempt / name).read_bytes()) for name in evidence_files})


def judge_template(round_path: Path, attempt: Path, destination: Path) -> None:
    _, metadata = verify_attempt(round_path, attempt)
    rubric = read_json(attempt / "rubric.json")
    write_json(destination, {"attempt_id": metadata["attempt_id"], "judge_id": "", "independent": True,
        "observations": {item["id"]: {"result": "indeterminate", "evidence": [], "reason": ""} for item in rubric["observations"]},
        "common_metrics": {item: {"result": "indeterminate", "evidence": [], "reason": ""} for item in rubric["common_metrics"]},
        "limitations": ["Effective model/effort must come from runtime telemetry, not requested settings."]})


def adjudicate(round_path: Path, attempt: Path, judgment_path: Path) -> None:
    _, metadata = verify_attempt(round_path, attempt)
    if (attempt / "judgment.json").exists():
        raise ValueError("judgment exists; preserve prior adjudication")
    rubric = read_json(attempt / "rubric.json")
    judgment = read_json(judgment_path)
    if judgment["attempt_id"] != metadata["attempt_id"] or not judgment["judge_id"] or judgment["independent"] is not True:
        raise ValueError("identified independent judge required")
    execution = read_json(attempt / "execution.json")
    verify_evidence(attempt)
    for section, expected in (("observations", {item["id"] for item in rubric["observations"]}), ("common_metrics", set(rubric["common_metrics"]))):
        if set(judgment[section]) != expected:
            raise ValueError("judgment must cover every applicable observation/metric exactly once")
        for finding in judgment[section].values():
            if finding["result"] not in RESULTS or not finding["reason"]:
                raise ValueError("valid result and reason required")
            if finding["result"] != "indeterminate" and execution["evidence_kind"] != "llm":
                raise ValueError("infrastructure/synthetic evidence cannot establish skill pass/fail")
            if finding["result"] != "indeterminate" and not finding["evidence"]:
                raise ValueError("pass/fail needs evidence references")
            for reference in finding["evidence"]:
                if reference not in read_json(attempt / "evidence-seal.json"):
                    raise ValueError("judgment may cite only sealed execution evidence")
    write_json(attempt / "judgment.json", judgment)
    (attempt / "judgment.sha256").write_text(digest((attempt / "judgment.json").read_bytes()) + "\n")


def report(round_path: Path) -> None:
    spec = verify_round(round_path)
    rows = []
    for case in spec["cases"]:
        for version in case["versions"]:
            attempts = []
            for path in sorted((round_path / "attempts").glob(f"{case['id']}--{version}--*")):
                _, metadata = verify_attempt(round_path, path)
                if (path / "execution.json").exists():
                    verify_evidence(path)
                execution = read_json(path / "execution.json") if (path / "execution.json").exists() else {}
                judgment = read_json(path / "judgment.json") if (path / "judgment.json").exists() else None
                attempts.append({"path": str(path.relative_to(round_path)), "trial": metadata["trial"],
                    "execution_state": execution.get("state", "not-run"), "evidence_kind": execution.get("evidence_kind", "not-run"),
                    "judgment": judgment, "effective_parent": execution.get("effective_parent"),
                    "loaded_distribution": execution.get("loaded_distribution")})
            completed = [item for item in attempts if item["judgment"] is not None and item["evidence_kind"] == "llm" and item["execution_state"] == "completed"]
            values = [finding["result"] for item in completed for finding in item["judgment"]["observations"].values()]
            conformance = "indeterminate"
            if {1, 2, 3} <= {item["trial"] for item in completed}:
                conformance = "fail" if "fail" in values else ("pass" if values and set(values) == {"pass"} else "indeterminate")
            # Counts are descriptive only; differences need independent comparison adjudication.
            rows.append({"case_id": case["id"], "version": version,
                "track": "comparison" if case["skill"] in CONTINUING else "v7.5.0-attainment",
                "attempts": attempts, "missing_initial_trials": sorted(set(range(1, 4)) - {a["trial"] for a in completed}),
                "spec_conformance": conformance, "quality_change": "indeterminate",
                "reason": "Independent semantic adjudication and complete repeated LLM evidence required; no automatic causal ranking."})
    comparisons = []
    if (round_path / "comparisons.json").exists():
        if digest((round_path / "comparisons.json").read_bytes()) != (round_path / "comparisons.sha256").read_text().strip():
            raise ValueError("comparison judgment identity drift")
        comparisons = read_json(round_path / "comparisons.json")["decisions"]
    payload = {"round_id": spec["round_id"], "versions": spec["versions"], "requested": spec["requested"], "rows": rows,
        "comparison": comparisons or "indeterminate", "causal_model_claim": None,
        "note": "Version-specific observations measure attainment. Common metrics alone support comparison; missing old skills are not regression cells."}
    write_json(round_path / "report.json", payload)
    lines = ["# Tugite behavior evaluation", "", f"Round: `{spec['round_id']}`", "",
        "版別適合と共通品質変動は独立判定する。モデル差の因果的優劣は結論しない。", "",
        "| Case | Version | Track | Trials | Missing initial | State |", "|---|---|---|---:|---|---|"]
    for row in rows:
        states = ", ".join(a["execution_state"] for a in row["attempts"]) or "not-run"
        lines.append(f"| {row['case_id']} | {row['version']} | {row['track']} | {len(row['attempts'])} | {row['missing_initial_trials']} | {states} |")
    lines += ["", "## Independent comparisons", ""]
    for decision in comparisons:
        lines.append(f"- {decision['case_id']} {decision['baseline']} → {decision['candidate']}: **{decision['result']}** — {decision['reason']}")
    if not comparisons:
        lines.append("判定不能: 独立した比較裁定は未提出。")
    lines += ["", "実効設定・ロード状況は未観測なら null。staged inventory はロードの証明ではない。", ""]
    (round_path / "report.md").write_text("\n".join(lines))


def compare(round_path: Path, judgment_path: Path) -> None:
    spec = verify_round(round_path)
    if (round_path / "comparisons.json").exists():
        raise ValueError("comparison exists; preserve prior decisions")
    packet = read_json(judgment_path)
    if packet["round_id"] != spec["round_id"] or not packet["judge_id"] or packet["independent"] is not True:
        raise ValueError("identified independent comparison judge required")
    seen = set()
    for decision in packet["decisions"]:
        case = choose_case(spec, decision["case_id"], decision["baseline"])
        choose_case(spec, decision["case_id"], decision["candidate"])
        key = (case["id"], decision["baseline"], decision["candidate"])
        if key in seen or case["skill"] not in CONTINUING or decision["baseline"] == decision["candidate"]:
            raise ValueError("invalid duplicate or attainment-track comparison")
        seen.add(key)
        if decision["result"] not in {"improved", "worsened", "equivalent", "indeterminate"} or not decision["reason"]:
            raise ValueError("comparison result and reason required")
        if not decision["metric_ids"] or not set(decision["metric_ids"]) <= set(case["common_metrics"]):
            raise ValueError("compare only preregistered common metrics")
        for version in (decision["baseline"], decision["candidate"]):
            for trial in range(1, 4):
                attempt = round_path / "attempts" / f"{case['id']}--{version}--{trial}"
                if not attempt.exists():
                    if decision["result"] != "indeterminate":
                        raise ValueError("three initial trials per version required for directional comparison")
                    continue
                verify_attempt(round_path, attempt)
                if not (attempt / "execution.json").exists():
                    if (attempt / "evidence-seal.json").exists() or (attempt / "judgment.json").exists():
                        raise ValueError("inconsistent prepared-only evidence state")
                    if decision["result"] != "indeterminate":
                        raise ValueError("unexecuted trials cannot establish directional comparison")
                    continue
                verify_evidence(attempt)
                execution = read_json(attempt / "execution.json")
                if decision["result"] != "indeterminate" and (execution["evidence_kind"] != "llm" or execution["state"] != "completed" or not (attempt / "judgment.json").exists()):
                    raise ValueError("completed, independently judged LLM trials required")
        if decision["result"] != "indeterminate" and not decision["evidence"]:
            raise ValueError("comparison evidence references required")
        for reference in decision["evidence"]:
            path = safe_path(round_path, reference)
            if path.name != "judgment.json" or not path.is_file() or path.parent.parent != round_path / "attempts":
                raise ValueError("comparison must cite independent trial judgments")
            _, referenced = verify_attempt(round_path, path.parent)
            if referenced["case_id"] != case["id"] or referenced["version"] not in {decision["baseline"], decision["candidate"]}:
                raise ValueError("comparison evidence case/version mismatch")
            verify_evidence(path.parent)
    write_json(round_path / "comparisons.json", packet)
    (round_path / "comparisons.sha256").write_text(digest((round_path / "comparisons.json").read_bytes()) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    frozen = sub.add_parser("freeze")
    frozen.add_argument("round", type=Path)
    frozen.add_argument("--corpus", type=Path, default=ROOT / "evals/corpus.json")
    frozen.add_argument("--model", default="gpt-6.1-sol")
    frozen.add_argument("--effort", default="medium")
    frozen.add_argument("--source-repo", default=SOURCE_REPOSITORY, help="Canonical Tugite URL or a local Git source repository; never the eval object database implicitly")
    comparison = sub.add_parser("compare")
    comparison.add_argument("round", type=Path)
    comparison.add_argument("judgment", type=Path)
    for name in ("prepare", "run", "judge-template", "adjudicate", "report"):
        item = sub.add_parser(name)
        item.add_argument("round", type=Path)
        if name == "prepare":
            item.add_argument("case")
            item.add_argument("version", choices=VERSIONS)
            item.add_argument("--trial", type=int, default=1)
            item.add_argument("--reason")
        elif name != "report":
            item.add_argument("attempt", type=Path)
            if name == "run":
                item.add_argument("--codex", default="codex")
                item.add_argument("--timeout", type=int, default=600)
                item.add_argument("--synthetic", action="store_true", help="Mark test-double output permanently ineligible as LLM evidence")
            else:
                item.add_argument("judgment", type=Path)
    args = parser.parse_args()
    try:
        if args.action == "freeze":
            freeze(args.round.resolve(), args.corpus, args.model, args.effort, args.source_repo)
        elif args.action == "prepare":
            print(prepare(args.round.resolve(), args.case, args.version, args.trial, args.reason))
        elif args.action == "run":
            run(args.round.resolve(), args.attempt.resolve(), args.codex, args.timeout, args.synthetic)
        elif args.action == "judge-template":
            judge_template(args.round.resolve(), args.attempt.resolve(), args.judgment)
        elif args.action == "compare":
            compare(args.round.resolve(), args.judgment)
        elif args.action == "adjudicate":
            adjudicate(args.round.resolve(), args.attempt.resolve(), args.judgment)
        else:
            report(args.round.resolve())
    except (ValueError, KeyError, OSError, subprocess.TimeoutExpired) as error:
        parser.exit(2, f"error: {error}\n")


if __name__ == "__main__":
    main()
