#!/usr/bin/env python3
"""Input-only transport for fresh cloud tasks; no nested inference process."""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile

import runner as r


def export(round_path: Path, attempt: Path, destination: Path) -> None:
    spec, metadata = r.verify_attempt(round_path, attempt)
    r.verify_workspace(attempt, metadata)
    case = r.choose_case(spec, metadata['case_id'], metadata['version'])
    if case.get('capability_constraint'):
        raise ValueError('capability-constrained cases require a separately verified runtime adapter')
    destination.mkdir(parents=True, exist_ok=False)
    distribution = round_path / 'distributions' / metadata['version']
    packet = {
        'schema': 1, 'adapter': 'fresh-cloud-task-v1',
        'attempt_id': metadata['attempt_id'], 'round_id': metadata['round_id'],
        'case_id': metadata['case_id'], 'trial': metadata['trial'],
        'version': metadata['version'], 'repo_sha': metadata['repo_sha'],
        'skill': case['skill'], 'prompt': case['prompt'],
        'files': case['files'], 'working_changes': case.get('working_changes', {}),
        'requested': spec['requested'],
        'distribution': r.file_inventory(distribution),
        'agent_config': {str(p.relative_to(attempt / 'workspace')): p.read_text()
                         for p in (attempt / 'workspace/.codex').rglob('*') if p.is_file()},
    }
    r.write_json(destination / 'input.json', packet)
    r.write_json(destination / 'control.json', {
        'input_sha256': r.digest((destination / 'input.json').read_bytes()),
        'round_seal': r.read_json(round_path / 'seal.json'),
        'attempt': metadata, 'rubric': r.read_json(attempt / 'rubric.json'),
        'change_reason': 'Fresh cloud task transport; retains frozen corpus and version rubrics; nested CLI optional.',
    })


def verify_input(path: Path, expected: str) -> dict:
    if r.digest(path.read_bytes()) != expected:
        raise ValueError('input identity mismatch')
    packet = r.read_json(path)
    if packet['repo_sha'] != r.VERSIONS[packet['version']]:
        raise ValueError('fixed source identity mismatch')
    for relative in list(packet['files']) + list(packet['working_changes']):
        r.safe_path(Path('/fixture'), relative)
        if Path(relative).parts[0] in {'.git', '.agents', '.codex'}:
            raise ValueError('fixture cannot supply runtime configuration')
    for relative in packet['agent_config']:
        r.safe_path(Path('/fixture'), relative)
        if Path(relative).parts[0] != '.codex':
            raise ValueError('agent config must be under .codex')
    return packet


def stage(path: Path, expected: str, destination: Path, source: str) -> None:
    packet = verify_input(path, expected)
    if source != r.SOURCE_REPOSITORY:
        local_source = Path(source).resolve()
        if not local_source.is_dir():
            raise ValueError('source must be canonical Tugite URL or existing local Git repository')
        source = str(local_source)
    destination.mkdir(parents=True, exist_ok=False)
    try:
        with tempfile.TemporaryDirectory(prefix='tugite-cloud-source-') as temporary:
            source_git = Path(temporary) / 'source.git'
            r.git('init', '--bare', '-q', str(source_git))
            # Only the selected fixed version is retrieved; no main skill is loaded.
            r.git('fetch', '--no-tags', '--depth=1', source, packet['repo_sha'], cwd=source_git)
            if r.git('rev-parse', 'FETCH_HEAD^{commit}', cwd=source_git).decode().strip() != packet['repo_sha']:
                raise ValueError('fetched source identity mismatch')
            r.unpack_distribution(packet['repo_sha'], destination / 'distribution', source_git)
        if r.file_inventory(destination / 'distribution') != packet['distribution']:
            raise ValueError('distribution content mismatch')
        workspace = destination / 'workspace'
        workspace.mkdir()
        for relative, content in packet['files'].items():
            target = r.safe_path(workspace, relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
        r.git('init', '-q', cwd=workspace)
        r.git('add', '.', cwd=workspace)
        # Record the local commit identity; transported fixture bytes are authoritative.
        r.git('-c', 'user.name=Eval Fixture', '-c', 'user.email=fixture@example.invalid',
              '-c', 'commit.gpgsign=false', 'commit', '-qm', '固定した評価入力', cwd=workspace)
        for relative, content in packet['working_changes'].items():
            r.safe_path(workspace, relative).write_text(content)
        for relative, content in packet['agent_config'].items():
            target = r.safe_path(workspace, relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
        bundle = destination / 'distribution/plugins/codex'
        discovery = workspace / '.agents/skills'
        discovery.mkdir(parents=True)
        for skill in (bundle / 'skills').iterdir():
            (discovery / skill.name).symlink_to(skill.resolve(), target_is_directory=True)
        shutil.copyfile(path, destination / 'input.json')
        r.write_json(destination / 'before.json', {
            'input_sha256': expected, 'head': r.git('rev-parse', 'HEAD', cwd=workspace).decode().strip(),
            'files': packet['files'], 'status': r.git('status', '--porcelain=v1', cwd=workspace).decode(),
            'diff': r.git('diff', 'HEAD', cwd=workspace).decode(),
            'git_config': r.digest((workspace / '.git/config').read_bytes()),
            'git_hooks': r.file_inventory(workspace / '.git/hooks'),
            'agent_config': r.file_inventory(workspace / '.codex'),
            'discovery': {p.name: str(p.readlink()) for p in discovery.iterdir()},
        })
        (destination / 'prompt.txt').write_text(
            f"Read {bundle.resolve()}/skills/{packet['skill']}/SKILL.md first and use ${packet['skill']}. "
            'Resolve references and dependencies only within that fixed distribution. '
            'Work in ' + str(workspace.resolve()) + '. Custom agents are staged in .codex/agents. '
            'No network, push, dependency installation, or work outside this disposable fixture is authorized. '
            'Do not read the eval corpus, control files, rubrics, other versions or prior trial results. '
            'Return your task response and identify files actually read, commands used and limitations.\n\n' + packet['prompt'] + '\n')
    except Exception:
        shutil.rmtree(destination)
        raise


def collect(staged: Path, expected: str, response: Path, destination: Path) -> None:
    packet = verify_input(staged / 'input.json', expected)
    before = r.read_json(staged / 'before.json')
    if before['input_sha256'] != expected:
        raise ValueError('staged input mismatch')
    if destination.resolve().is_relative_to(staged.resolve()):
        raise ValueError('result destination must be outside stage')
    workspace = staged / 'workspace'
    response_bytes = response.read_bytes()
    destination.mkdir(parents=True, exist_ok=False)
    (destination / 'response.txt').write_bytes(response_bytes)
    shutil.copyfile(staged / 'before.json', destination / 'before.json')
    artifacts = {}
    for path in sorted(workspace.rglob('*')):
        relative = path.relative_to(workspace)
        if set(relative.parts) & {'.git', '.codex', '.agents', '__pycache__'}:
            continue
        if path.is_symlink():
            raise ValueError('artifact symlink requires manual evidence collection')
        if path.is_file():
            target = r.safe_path(destination / 'artifacts', str(relative))
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(path.read_bytes())
            artifacts[str(relative)] = r.digest(path.read_bytes())
    config_safe = r.digest((workspace / '.git/config').read_bytes()) == before['git_config'] and r.file_inventory(workspace / '.git/hooks') == before['git_hooks']
    after = {'files': artifacts, 'git_configuration_unchanged': config_safe}
    if config_safe:
        after.update(head=r.git('rev-parse', 'HEAD', cwd=workspace).decode().strip(),
                     status=r.git('status', '--porcelain=v1', '--untracked-files=all', cwd=workspace).decode(),
                     diff=r.git('diff', before['head'], cwd=workspace).decode())
    r.write_json(destination / 'after.json', after)
    r.write_json(destination / 'collection.json', {
        'attempt_id': packet['attempt_id'], 'input_sha256': expected,
        'state': 'collected', 'evidence_kind': 'unverified-cloud-output',
        'distribution_unchanged': r.file_inventory(staged / 'distribution') == packet['distribution'],
        'agent_config_unchanged': r.file_inventory(workspace / '.codex') == before['agent_config'],
        'discovery_unchanged': all(p.is_symlink() for p in (workspace / '.agents/skills').iterdir())
            and {p.name: str(p.readlink()) for p in (workspace / '.agents/skills').iterdir()} == before['discovery'],
        'requested_parent': packet['requested'],
        'resolved_parent': {'model': None, 'effort': None},
        'effective_parent': {'model': None, 'effort': None},
        'spawned_children': None, 'loaded_distribution': None, 'usage': None, 'cost': None,
        'limitation': 'Task output/self report is not trusted runtime telemetry. Parent must attach transcript and attest actual execution; isolation is not established by this adapter.',
    })
    r.write_json(destination / 'result-seal.json', r.file_inventory(destination))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    out = sub.add_parser('export')
    for name in ('round', 'attempt', 'destination'):
        out.add_argument(name, type=Path)
    staged = sub.add_parser('stage')
    staged.add_argument('input', type=Path)
    staged.add_argument('sha256')
    staged.add_argument('destination', type=Path)
    staged.add_argument('--source-repo', default=r.SOURCE_REPOSITORY)
    collected = sub.add_parser('collect')
    collected.add_argument('staged', type=Path)
    collected.add_argument('sha256')
    collected.add_argument('response', type=Path)
    collected.add_argument('destination', type=Path)
    args = parser.parse_args()
    try:
        if args.action == 'export':
            export(args.round.resolve(), args.attempt.resolve(), args.destination.resolve())
        elif args.action == 'stage':
            stage(args.input, args.sha256, args.destination.resolve(), args.source_repo)
        else:
            collect(args.staged.resolve(), args.sha256, args.response, args.destination.resolve())
    except (ValueError, KeyError, OSError, subprocess.TimeoutExpired) as error:
        parser.exit(2, f'error: {error}\n')


if __name__ == '__main__':
    main()
