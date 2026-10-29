#!/usr/bin/env python3
"""Materialize precommitted #398 semantics for one pinned side; never launch a trial."""
from __future__ import annotations

import argparse
import copy
from pathlib import Path
import re
import tempfile

import cloud_receipt
import cloud_task
import runner as r

BASELINE = 'c44261f1f70da40c75123a91153a8aa6c6d4be1e'
CORPUS = r.ROOT / 'cases/explain-398/corpus.json'


def prepare(destination: Path, side: str, revision: str, source: str, trials: int) -> None:
    if not re.fullmatch(r'[0-9a-f]{40}', revision):
        raise ValueError('full fixed SHA required; placeholders/branches are not executable')
    if side == 'baseline' and revision != BASELINE:
        raise ValueError('baseline identity is preregistered')
    corpus = copy.deepcopy(r.read_json(CORPUS))
    selected_versions = {'baseline': BASELINE, 'candidate': revision} if side == 'both' else {side: revision}
    corpus['cases'] = [case for case in corpus['cases'] if set(selected_versions) & set(case['versions'])]
    for case in corpus['cases']:
        case['versions'] = [version for version in case['versions'] if version in selected_versions]
        case['observations'] = [o for o in case['observations'] if set(selected_versions) & set(o['versions'])]
        for observation in case['observations']:
            observation['versions'] = [version for version in observation['versions'] if version in selected_versions]
            observation['basis'] = {version: observation['basis'][version] for version in observation['versions']}
    destination.mkdir(parents=True, exist_ok=False)
    with tempfile.TemporaryDirectory(prefix='tugite-398-corpus-') as temporary:
        selected = Path(temporary) / 'corpus.json'
        r.write_json(selected, corpus)
        round_path = destination / 'round'
        r.freeze(round_path, selected, 'gpt-6.1-sol', 'medium', source, selected_versions)
    cells = []
    for case in corpus['cases']:
        # Regressions are candidate-only, one trial; focus supports preregistered 1..3.
        count = trials if case['id'].startswith('explain-398-') else 1
        for version in case['versions']:
            for trial in range(1, count + 1):
                attempt = r.prepare(round_path, case['id'], version, trial, None)
                target = destination / 'inputs' / attempt.name
                cloud_task.export(round_path, attempt, target)
                cells.append({'case_id': case['id'], 'version': version, 'trial': trial,
                              'input': str((target / 'input.json').relative_to(destination)),
                              'input_sha256': r.digest((target / 'input.json').read_bytes())})
    r.write_json(destination / 'index.json', {'cells': cells})
    r.write_json(destination / 'quality-protocol.json', {
        'protocol_id': 'output-quality-v1', 'round_id': r.read_json(round_path / 'spec.json')['round_id'],
        'requested': {'model': 'gpt-6.1-sol', 'effort': 'medium'},
        'input_index': 'index.json', 'input_index_sha256': r.digest((destination / 'index.json').read_bytes()),
        'semantics_sha256': r.digest(CORPUS.read_bytes()),
        'scope': 'Output quality; internal evidence/effective model unknown is a limitation, not a stop.',
    })
    cloud_receipt.snapshot(round_path, destination / 'snapshot')
    print(r.canonical({'destination': str(destination), 'side': side, 'repo_sha': revision,
                       'semantics_sha256': r.digest(CORPUS.read_bytes()), 'cells': cells}).decode(), end='')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('side', choices=['baseline', 'candidate', 'both'])
    parser.add_argument('revision')
    parser.add_argument('destination', type=Path)
    parser.add_argument('--source-repo', default=r.SOURCE_REPOSITORY)
    parser.add_argument('--focus-trials', type=int, choices=[1, 2, 3], default=1)
    args = parser.parse_args()
    try:
        prepare(args.destination.resolve(), args.side, args.revision, args.source_repo, args.focus_trials)
    except (ValueError, KeyError, OSError) as error:
        parser.exit(2, f'error: {error}\n')


if __name__ == '__main__':
    main()
