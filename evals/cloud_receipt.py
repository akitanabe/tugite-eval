#!/usr/bin/env python3
"""Parent-owned receipts and conservative import into the existing round/report."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

import cloud_task as cloud
import runner as r


TRUSTED_SOURCES = {'parent-runtime', 'parent-artifact-inspection'}
INPUT_FILES = ('attempt.json', 'prompt.txt', 'rubric.json', 'input-seal.json')


def sha(path: Path) -> str:
    return r.digest(path.read_bytes())


def verify_tree(directory: Path, seal_name: str) -> dict:
    inventory = r.file_inventory(directory)
    inventory.pop(seal_name, None)
    seal = r.read_json(directory / seal_name)
    if not seal or inventory != seal:
        raise ValueError(f'{seal_name}: missing, extra or altered evidence')
    return seal


def code_hash(repository: Path, revision: str, filename: str) -> str:
    if len(revision) != 40 or any(c not in '0123456789abcdef' for c in revision):
        raise ValueError('full eval code SHA required')
    return r.digest(r.git('show', f'{revision}:evals/{filename}', cwd=repository))


def snapshot(round_path: Path, destination: Path) -> None:
    r.verify_round(round_path)
    destination.mkdir(parents=True, exist_ok=False)
    for name in ('spec.json', 'seal.json', 'runner.py'):
        shutil.copyfile(round_path / name, destination / name)
    for attempt in sorted((round_path / 'attempts').iterdir()):
        r.verify_attempt(round_path, attempt)
        target = destination / 'attempts' / attempt.name
        target.mkdir(parents=True)
        for name in INPUT_FILES:
            shutil.copyfile(attempt / name, target / name)
    r.write_json(destination / 'snapshot-seal.json', r.file_inventory(destination))


def restore(source: Path, destination: Path, repository: str) -> None:
    verify_tree(source, 'snapshot-seal.json')
    if sha(source / 'runner.py') != r.digest(Path(r.__file__).read_bytes()):
        raise ValueError('use the eval code revision that froze this round')
    destination.mkdir(parents=True, exist_ok=False)
    try:
        for name in ('spec.json', 'seal.json', 'runner.py'):
            shutil.copyfile(source / name, destination / name)
        shutil.copytree(source / 'attempts', destination / 'attempts')
        with tempfile.TemporaryDirectory(prefix='tugite-cloud-restore-') as temporary:
            source_git = Path(temporary) / 'source.git'
            r.fetch_source(repository, source_git)
            for version, revision in r.read_json(destination / 'spec.json')['versions'].items():
                r.unpack_distribution(revision, destination / 'distributions' / version, source_git)
        r.verify_round(destination)
        for attempt in (destination / 'attempts').iterdir():
            r.verify_attempt(destination, attempt)
    except Exception:
        shutil.rmtree(destination)
        raise


def receive_stage(input_path: Path, stage_path: Path, evidence_path: Path, capabilities_path: Path,
                  destination: Path, task_id: str, turn_id: str, parent_id: str,
                  revision: str, repository: Path, observation_source: str) -> None:
    packet = cloud.verify_input(input_path, sha(input_path))
    if packet['adapter'] != 'fresh-cloud-task-v2':
        raise ValueError('v2 input required; pre-receipt-free pilot remains reference-only')
    stage = r.read_json(stage_path)
    expected = {'input_sha256': sha(input_path), 'attempt_id': packet['attempt_id'],
                'round_id': packet['round_id'], 'state': 'staged-awaiting-parent-baseline-receipt',
                'adapter_sha256': code_hash(repository, revision, 'cloud_task.py'),
                'runner_sha256': code_hash(repository, revision, 'runner.py')}
    if any(stage.get(key) != value for key, value in expected.items()):
        raise ValueError('stage identity/code mismatch')
    if not all((task_id, turn_id, parent_id, evidence_path.stat().st_size)):
        raise ValueError('parent, task/turn identity and observed setup evidence required')
    if any(len(stage.get(key, '')) != 64 for key in ('before_sha256', 'prompt_sha256')):
        raise ValueError('stage before hash required')
    capabilities = r.read_json(capabilities_path)
    missing = [name for name in packet['required_capabilities']
               if capabilities.get(name, {}).get('available') is not True
               or not capabilities[name].get('evidence')]
    ready = observation_source in TRUSTED_SOURCES and not missing
    destination.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(stage_path, destination / 'stage.json')
    shutil.copyfile(evidence_path, destination / 'setup-evidence.txt')
    shutil.copyfile(capabilities_path, destination / 'capabilities.json')
    r.write_json(destination / 'receipt.json', {
        'schema': 1, 'kind': 'parent-pre-run', 'parent_id': parent_id,
        'task_id': task_id, 'setup_turn_id': turn_id, 'attempt_id': packet['attempt_id'],
        'input_sha256': sha(input_path), 'eval_code_sha': revision,
        'before_sha256': stage['before_sha256'], 'observation_source': observation_source,
        'required_capabilities': packet['required_capabilities'], 'missing_capabilities': missing,
        'state': 'ready' if ready else 'blocked',
        'created_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'files': r.file_inventory(destination),
        'limit': 'Parent attestation, not an authenticated runtime signature. Save before authorizing run; child output alone does not establish provenance.',
    })


def verify_pre(directory: Path) -> dict:
    pre = r.read_json(directory / 'receipt.json')
    actual = r.file_inventory(directory)
    actual.pop('receipt.json', None)
    if pre['kind'] != 'parent-pre-run' or actual != pre['files']:
        raise ValueError('parent pre-run receipt evidence drift')
    stage = r.read_json(directory / 'stage.json')
    if any(stage.get(key) != pre[key] for key in ('before_sha256', 'input_sha256', 'attempt_id')):
        raise ValueError('parent pre-run identity mismatch')
    return pre


def validate_packet(round_path: Path, attempt: Path, input_path: Path) -> tuple[dict, dict]:
    spec, metadata = r.verify_attempt(round_path, attempt)
    packet = cloud.verify_input(input_path, sha(input_path))
    case = r.choose_case(spec, metadata['case_id'], metadata['version'])
    expected = {key: metadata[key] for key in ('attempt_id', 'round_id', 'case_id', 'version', 'repo_sha', 'trial')}
    expected.update(adapter='fresh-cloud-task-v2', skill=case['skill'], prompt=case['prompt'], files=case['files'],
                    working_changes=case.get('working_changes', {}), requested=spec['requested'],
                    required_capabilities=cloud.required_capabilities(case['skill']),
                    distribution=r.file_inventory(round_path / 'distributions' / metadata['version']))
    config = {key.removeprefix('.codex/'): r.digest(value.encode()) for key, value in packet['agent_config'].items()}
    if any(packet.get(key) != value for key, value in expected.items()) or config != metadata['staged_config']:
        raise ValueError('cloud input differs from frozen attempt')
    return packet, metadata


def import_result(round_path: Path, attempt: Path, input_path: Path, result: Path,
                  pre_directory: Path, post_path: Path, runtime: Path, repository: Path) -> None:
    packet, metadata = validate_packet(round_path, attempt, input_path)
    if (attempt / 'execution.json').exists() or (attempt / 'cloud').exists():
        raise ValueError('preserve previous execution/import; use a new trial')
    # Parent-held evidence must be supplied independently of the child's result tree.
    for path in (pre_directory, post_path, runtime):
        if path.resolve().is_relative_to(result.resolve()):
            raise ValueError('parent evidence cannot come from child result directory')
    pre = verify_pre(pre_directory)
    pre_hash = sha(pre_directory / 'receipt.json')
    post_bytes = post_path.read_bytes()
    post = json.loads(post_bytes)
    expected = {'task_id': pre['task_id'], 'attempt_id': packet['attempt_id'],
                'input_sha256': sha(input_path), 'eval_code_sha': pre['eval_code_sha']}
    if any(pre.get(key) != value or post.get(key) != value for key, value in expected.items()):
        raise ValueError('task/attempt/input/code identity mismatch')
    if post['parent_id'] != pre['parent_id'] or post['pre_receipt_sha256'] != pre_hash:
        raise ValueError('parent or pre-run receipt mismatch')
    if not post['run_turn_id'] or post['run_turn_id'] == pre['setup_turn_id']:
        raise ValueError('distinct setup and run turn IDs required')
    stage = r.read_json(pre_directory / 'stage.json')
    if stage['adapter_sha256'] != code_hash(repository, pre['eval_code_sha'], 'cloud_task.py') or stage['runner_sha256'] != code_hash(repository, pre['eval_code_sha'], 'runner.py'):
        raise ValueError('parent receipt eval code hash mismatch')
    if stage['runner_sha256'] != sha(round_path / 'runner.py'):
        raise ValueError('code and frozen round runner mismatch')
    verify_tree(result, 'result-seal.json')
    if post['result_seal_sha256'] != sha(result / 'result-seal.json'):
        raise ValueError('parent result seal mismatch')
    if r.file_inventory(runtime) != post['runtime_files']:
        raise ValueError('parent runtime evidence hash mismatch')
    collection = r.read_json(result / 'collection.json')
    if collection['attempt_id'] != packet['attempt_id'] or collection['input_sha256'] != sha(input_path):
        raise ValueError('collected result identity mismatch')
    if collection.get('before_sha256') != pre['before_sha256'] or sha(result / 'before.json') != pre['before_sha256']:
        raise ValueError('parent-held initial snapshot mismatch')
    if sha(result / 'prompt.txt') != stage['prompt_sha256']:
        raise ValueError('evaluated prompt differs from parent-held stage receipt')
    before = r.read_json(result / 'before.json')
    if before['input_sha256'] != sha(input_path) or before['files'] != packet['files']:
        raise ValueError('initial fixture differs from fixed input')
    after = r.read_json(result / 'after.json')
    artifact_inventory = r.file_inventory(result / 'artifacts')
    if artifact_inventory != after['files']:
        raise ValueError('artifact inventory differs from sealed after snapshot')
    observations = post['observations']
    required = ('agent_turn_completed', 'input_identity_verified', 'artifact_provenance_verified', 'transcript_complete')
    for key in required:
        finding = observations[key]
        if finding['value'] is not None and type(finding['value']) is not bool:
            raise ValueError('observation must be true/false/null')
        if not set(finding['evidence']) <= set(post['runtime_files']) or (finding['value'] is not None and not finding['evidence']):
            raise ValueError('runtime observation requires parent-held evidence references')
    source_trusted = post['observation_source'] == 'parent-runtime'
    baseline_ready = pre['state'] == 'ready' and pre['observation_source'] in TRUSTED_SOURCES and not pre['missing_capabilities']
    actual_llm = source_trusted and baseline_ready and all(observations[key]['value'] is True for key in required[:3])
    unchanged = all(collection.get(key) is True for key in ('distribution_unchanged', 'agent_config_unchanged', 'discovery_unchanged')) and after['git_configuration_unchanged'] is True
    synthetic = post['synthetic']
    if type(synthetic) is not bool:
        raise ValueError('explicit synthetic boolean required')
    blockers = post['capability_blockers']
    completed = actual_llm and unchanged and not synthetic and not blockers and observations['transcript_complete']['value'] is True
    evidence_kind = 'synthetic' if synthetic else ('llm' if actual_llm else 'cloud-reference')
    state = 'completed' if completed else ('blocked' if blockers or not baseline_ready else 'evidence-incomplete')
    telemetry = {}
    for key in ('resolved_parent', 'effective_parent', 'spawned_children', 'loaded_distribution', 'usage', 'cost'):
        item = post.get('telemetry', {}).get(key, {'value': None, 'evidence': []})
        if item['value'] is not None and (not source_trusted or not item['evidence'] or not set(item['evidence']) <= set(post['runtime_files'])):
            raise ValueError('telemetry requires parent runtime observation and evidence')
        telemetry[key] = item['value']
    telemetry['effective_parent'] = telemetry['effective_parent'] or {'model': None, 'effort': None}
    telemetry['resolved_parent'] = telemetry['resolved_parent'] or {'model': None, 'effort': None}
    # All validation above is read-only. A partially copied import never gets execution/seal.
    target = attempt / 'cloud'
    shutil.copytree(result, target / 'result')
    shutil.copytree(pre_directory, target / 'pre')
    shutil.copytree(runtime, target / 'runtime')
    (target / 'post.json').write_bytes(post_bytes)
    shutil.copyfile(input_path, target / 'input.json')
    verify_tree(target / 'result', 'result-seal.json')
    verify_pre(target / 'pre')
    if sha(target / 'result/result-seal.json') != post['result_seal_sha256'] or sha(target / 'pre/receipt.json') != pre_hash or r.file_inventory(target / 'runtime') != post['runtime_files']:
        raise ValueError('evidence changed during parent import; preserve incomplete copy for inspection')
    execution = {'adapter': 'fresh-cloud-task-v2', 'state': state, 'evidence_kind': evidence_kind,
                 'attempt_id': metadata['attempt_id'], 'synthetic': synthetic,
                 'cloud_task_id': pre['task_id'], 'setup_turn_id': pre['setup_turn_id'], 'run_turn_id': post['run_turn_id'],
                 'eval_code_sha': pre['eval_code_sha'], 'input_sha256': sha(input_path),
                 'parent_pre_receipt_sha256': pre_hash,
                 'result_seal_sha256': sha(result / 'result-seal.json'),
                 'observations': observations, 'capability_blockers': blockers,
                 'comparison_eligible': completed, 'requested_parent': packet['requested'], **telemetry,
                 'limitations': post['limitations'],
                 'trust_boundary': 'Parent attestations with hashed evidence; source classification and completeness are not authenticated by this importer. Independent adjudication required.'}
    r.write_json(attempt / 'execution.json', execution)
    seal = {'execution.json': sha(attempt / 'execution.json')}
    seal.update({'cloud/' + name: value for name, value in r.file_inventory(target).items()})
    r.write_json(attempt / 'evidence-seal.json', seal)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    saved = sub.add_parser('snapshot')
    saved.add_argument('round', type=Path)
    saved.add_argument('destination', type=Path)
    restored = sub.add_parser('restore')
    restored.add_argument('snapshot', type=Path)
    restored.add_argument('round', type=Path)
    restored.add_argument('--source-repo', default=r.SOURCE_REPOSITORY)
    received = sub.add_parser('receive-stage')
    for name in ('input', 'stage', 'evidence', 'capabilities', 'destination'):
        received.add_argument(name, type=Path)
    for name in ('task-id', 'setup-turn-id', 'parent-id', 'eval-code-sha', 'observation-source'):
        received.add_argument('--' + name, required=True)
    received.add_argument('--eval-repository', type=Path, default=r.ROOT)
    imported = sub.add_parser('import')
    for name in ('round', 'attempt', 'input', 'result', 'pre', 'post', 'runtime'):
        imported.add_argument(name, type=Path)
    imported.add_argument('--eval-repository', type=Path, default=r.ROOT)
    args = parser.parse_args()
    try:
        if args.action == 'snapshot':
            snapshot(args.round.resolve(), args.destination.resolve())
        elif args.action == 'restore':
            restore(args.snapshot.resolve(), args.round.resolve(), args.source_repo)
        elif args.action == 'receive-stage':
            receive_stage(args.input, args.stage, args.evidence, args.capabilities, args.destination,
                          args.task_id, args.setup_turn_id, args.parent_id, args.eval_code_sha,
                          args.eval_repository, args.observation_source)
        else:
            import_result(args.round.resolve(), args.attempt.resolve(), args.input, args.result,
                          args.pre, args.post, args.runtime, args.eval_repository)
    except (ValueError, KeyError, OSError, subprocess.TimeoutExpired) as error:
        parser.exit(2, f'error: {error}\n')


if __name__ == '__main__':
    main()
