"""Resumable unattended collect -> train -> play -> evaluate loop."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading
import time

from filelock import FileLock

from .collect import collect
from .cycle_state import find_pending_cycle, fingerprint_after_completion
from .data import ROOT, VERSION as DATA_VERSION, atomic_json, dataset, dataset_fingerprint
from .evaluate import package, paired_gate, run_game, source_hash
from .panel_gate import PANEL_GATE_VERSION, paired_panel_gate
from .train import fit


def now():
    return datetime.now(timezone.utc).isoformat()


def absolute(path):
    path = Path(path)
    return path if path.is_absolute() else ROOT / path


def evaluation_fingerprint(config):
    """Hash evaluation semantics, excluding worker parallelism.

    Changing the number of local workers must not invalidate a frozen policy or
    its exact paired fixtures; the fixture identities and gate thresholds are
    unchanged by that operational setting.
    """
    evaluation = dict(config.get('evaluation', {}))
    evaluation.pop('jobs', None)
    payload = dict(evaluation=evaluation, training=config.get('training', {}),
                   seed=config.get('seed', 1701), data_version=DATA_VERSION,
                   panel_gate_version=PANEL_GATE_VERSION)
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def bootstrap(config, root, status):
    """Local teacher games bootstrap the replay-free Windows checkout."""
    settings = config.get('bootstrap', {})
    if not settings.get('enabled', False):
        return
    teacher = absolute(settings['teacher'])
    for board in settings['maps']:
        for opponent in settings['opponents']:
            for side in 'AB':
                if (root / 'STOP').exists():
                    return
                identity = dict(teacher=source_hash(teacher), opponent=source_hash(absolute(opponent)),
                                map=hashlib.sha256(absolute(board).read_bytes()).hexdigest(), side=side,
                                seed=settings.get('seed', 1701))
                name = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()[:24]
                path = root / 'bootstrap' / f'{name}.replay'
                if path.exists() and path.with_suffix('.json').exists():
                    continue
                status('bootstrap', fixture=identity)
                run_game(teacher, absolute(opponent), absolute(board), side, identity['seed'], path)
                pair_group = hashlib.sha256(json.dumps({k: v for k, v in identity.items() if k != 'side'}, sort_keys=True).encode()).hexdigest()
                atomic_json(path.with_suffix('.json'), dict(source='local_teacher', fixture=identity, series_id=pair_group))


def run(config_path, once=False):
    config_path = Path(config_path).resolve()
    config = json.loads(config_path.read_text(encoding='utf-8'))
    root = absolute(config['output'])
    root.mkdir(parents=True, exist_ok=True)
    lock = FileLock(str(root / 'worker.lock'), timeout=0)
    with lock:
        state_path = root / 'state.json'
        state = json.loads(state_path.read_text()) if state_path.exists() else dict(cycle=0)

        def status(stage, **extra):
            payload = dict(pid=os.getpid(), stage=stage, updated_at=now(), cycle=state['cycle'])
            payload.update(extra)
            atomic_json(root / 'status.json', payload)
            print(json.dumps(payload), flush=True)

        collection_stop = threading.Event()
        collection_lock = threading.Lock()

        def collect_pass():
            with collection_lock:
                try:
                    report = collect(config.get('collection', {}), root / 'public',
                                     stop_file=root / 'STOP', stop_event=collection_stop)
                except Exception as exc:
                    report = dict(status='download_error', error=type(exc).__name__, downloaded=0)
                atomic_json(root / 'last_collection.json', report)
                print(json.dumps(dict(stage='background_collection', **report)), flush=True)
                return report

        def collection_loop():
            interval = max(60, config.get('poll_seconds', 900))
            while not collection_stop.is_set() and not (root / 'STOP').exists():
                if collection_stop.wait(interval):
                    break
                if not (root / 'STOP').exists():
                    collect_pass()

        collector = None
        if not (root / 'STOP').exists():
            status('collecting')
            collect_pass()
            if not (root / 'STOP').exists():
                collector = threading.Thread(target=collection_loop, name='top-game-collector', daemon=True)
                collector.start()

        atomic_json(root / 'run_config.json', config)
        while not (root / 'STOP').exists():
            started = time.monotonic()
            try:
                # Reserve disk space; never delete historical data automatically.
                if shutil.disk_usage(root).free < config.get('min_free_gb', 10) * 1024 ** 3:
                    status('waiting_for_disk_space')
                else:
                    collection_path = root / 'last_collection.json'
                    collection = (json.loads(collection_path.read_text(encoding='utf-8'))
                                  if collection_path.exists() else None)
                    bootstrap(config, root, status)
                    if (root / 'STOP').exists():
                        break
                    status('extracting', collection=collection)
                    roots = [root / 'public/replays', root / 'bootstrap', root / 'selfplay']
                    roots.extend(absolute(p) for p in config.get('replays', []))
                    with collection_lock:
                        rows_per_side = config.get('rows_per_side', 256)
                        games, audit = dataset(roots, root / 'cache', config.get('max_games', 200),
                                               rows_per_side=rows_per_side)
                    atomic_json(root / 'extraction_audit.json', audit)
                    # Map holdout is an additional independent generalisation
                    # check, not a source of training labels.
                    holdout = set(config.get('holdout_map_names', []))
                    for game in games:
                        if game['map'] in holdout:
                            game['split'] = 'test'
                    manifest = [dict(sha256=g['sha256'], split=g['split'], map=g['map'],
                                     provenance=g['provenance']) for g in games]
                    atomic_json(root / 'dataset_manifest.json', manifest)
                    fingerprint = dataset_fingerprint(games, rows_per_side)
                    counts = {s: sum(g['split'] == s for g in games) for s in ('train', 'validation', 'test')}
                    if counts['train'] < 2 or counts['validation'] < 1:
                        status('waiting_for_replays', games=counts, collection=collection, quarantined=len(audit))
                    else:
                        gate = config.get('evaluation', {})
                        gate_hash = evaluation_fingerprint(config)
                        cycle_dirs = sorted((p for p in (root / 'cycles').glob('*')
                                             if p.is_dir() and p.name.isdigit()), reverse=True)
                        pending = find_pending_cycle(cycle_dirs, fingerprint, gate_hash)
                        if pending is None and state.get('fingerprint') == fingerprint:
                            status('waiting_for_new_data', games=counts)
                        else:
                            if pending:
                                cycle, cycle_meta = pending
                                state['cycle'] = int(cycle.name)
                                settings = dict(cycle_meta['training_settings'])
                                incumbent = Path(cycle_meta['incumbent']).resolve()
                                status('resuming_cycle', phase=cycle_meta.get('phase'), cycle=state['cycle'])
                            else:
                                existing = [int(p.name) for p in cycle_dirs]
                                state['cycle'] = max([state['cycle']] + existing) + 1
                                cycle = root / 'cycles' / f'{state["cycle"]:06d}'
                                cycle.mkdir(parents=True, exist_ok=True)
                                settings = dict(config.get('training', {}))
                                settings['seed'] = config.get('seed', 1701) + state['cycle']
                                incumbent = absolute(state.get('incumbent', gate['incumbent']))
                                cycle_meta = dict(fingerprint=fingerprint, evaluation_hash=gate_hash,
                                                  training_settings=settings, incumbent=str(incumbent), phase='training')
                                atomic_json(cycle / 'cycle.json', cycle_meta)
                                atomic_json(state_path, state)

                            summary_path = cycle / 'training' / 'training_summary.json'
                            candidate = cycle / 'candidate'
                            if summary_path.exists():
                                summary = json.loads(summary_path.read_text(encoding='utf-8'))
                            else:
                                resume_path = cycle / 'training' / 'last.pt'
                                if resume_path.exists():
                                    settings['resume'] = str(resume_path)
                                status('training', games=counts, resuming=resume_path.exists())
                                summary = fit(games, cycle / 'training', **settings)
                            if not (candidate / 'policy.json').exists():
                                candidate = package(cycle / 'training/policy.json', candidate)
                            cycle_meta.update(phase='trained', candidate=str(candidate))
                            atomic_json(cycle / 'cycle.json', cycle_meta)
                            if (root / 'STOP').exists():
                                break

                            incumbent = Path(cycle_meta['incumbent']).resolve()
                            gate_path = cycle / 'evaluation' / 'gate.json'
                            if gate_path.exists():
                                report = json.loads(gate_path.read_text(encoding='utf-8'))
                            else:
                                status('evaluating', candidate=str(candidate), incumbent=str(incumbent))
                                if gate.get('panels'):
                                    panels = [dict(name=panel['name'],
                                                   maps=[absolute(p) for p in panel['maps']],
                                                   opponents=[absolute(p) for p in panel.get('opponents', gate['opponents'])],
                                                   seeds=panel.get('seeds', gate.get('seeds', [1, 2, 3])))
                                              for panel in gate['panels']]
                                    report = paired_panel_gate(candidate, incumbent, panels,
                                        cycle / 'evaluation', root / 'cache',
                                        population_weight=settings.get('population_weight', 0.25),
                                        bootstrap=gate.get('bootstrap', 4000), seed=config.get('seed', 1701),
                                        jobs=gate.get('jobs', 1), stop_file=root / 'STOP',
                                        min_clusters=gate.get('min_clusters', 4))
                                else:
                                    report = paired_gate(candidate, incumbent,
                                        [absolute(p) for p in gate['opponents']], [absolute(p) for p in gate['maps']],
                                        gate.get('seeds', [1702, 1703]), cycle / 'evaluation', root / 'cache',
                                        population_weight=settings.get('population_weight', 0.25),
                                        min_pairs=gate.get('min_pairs', 12), stop_file=root / 'STOP')
                            if report['promote'] and state.get('incumbent') != str(candidate):
                                # Local incumbent pointer only, no submission/activation.
                                state['incumbent'] = str(candidate)
                                atomic_json(root / 'incumbent.json', dict(bot=str(candidate), cycle=state['cycle'], gate=report))
                                atomic_json(state_path, state)
                            status('rollouts', promoted=report['promote'])
                            rollout = config.get('rollouts', {})
                            exploratory = package(cycle / 'training/policy.json', cycle / 'exploratory',
                                                  rollout.get('temperature', 0.5), settings['seed'])
                            for index, board in enumerate(rollout.get('maps', [])):
                                if (root / 'STOP').exists():
                                    break
                                opponent = absolute(rollout['opponents'][index % len(rollout['opponents'])])
                                side = 'AB'[state['cycle'] % 2]
                                path = root / 'selfplay' / f'cycle{state["cycle"]:06d}-{index}.replay'
                                if path.exists() and path.with_suffix('.json').exists():
                                    continue
                                run_game(exploratory, opponent, absolute(board), side, settings['seed'] + index, path)
                                atomic_json(path.with_suffix('.json'), dict(source='local_rollout',
                                    policy_hash=source_hash(exploratory), opponent_hash=source_hash(opponent),
                                    actor_side=side, series_id=f'rollout-{state["cycle"]}-{index}'))
                            tree_policy = cycle / 'training' / 'tree_top10_winners_policy.json'
                            rollout_maps = rollout.get('maps', [])
                            if tree_policy.exists() and rollout_maps and not (root / 'STOP').exists():
                                tree_opponent = package(tree_policy, cycle / 'tree-zoo-top10-winners',
                                                        seed=settings['seed'])
                                tree_side = 'AB'[(state['cycle'] + len(rollout_maps)) % 2]
                                tree_seed = settings['seed'] + len(rollout_maps)
                                tree_path = root / 'selfplay' / f'cycle{state["cycle"]:06d}-tree-top10-winners.replay'
                                tree_receipt = tree_path.with_suffix('.json')
                                receipt = dict(source='local_rollout', policy_hash=source_hash(exploratory),
                                    opponent_hash=source_hash(tree_opponent), actor_side=tree_side,
                                    opponent_family='top10_ranked_winner_tree',
                                    series_id=f'rollout-{state["cycle"]}-tree-top10-winners')
                                if not (tree_path.exists() and tree_receipt.exists()
                                        and json.loads(tree_receipt.read_text(encoding='utf-8')) == receipt):
                                    run_game(exploratory, tree_opponent, absolute(rollout_maps[0]),
                                             tree_side, tree_seed, tree_path)
                                    atomic_json(tree_receipt, receipt)
                            if (root / 'STOP').exists():
                                break
                            state['fingerprint'] = fingerprint_after_completion(cycle_meta, fingerprint)
                            atomic_json(state_path, state)
                            cycle_meta.update(phase='complete', promoted=report['promote'])
                            atomic_json(cycle / 'cycle.json', cycle_meta)
                            status('cycle_complete', promoted=report['promote'], validation=summary['validation'])
            except InterruptedError as exc:
                status('stopping', reason=str(exc))
                break
            except Exception as exc:
                # Detailed local trace in log; status stays machine-readable.
                import traceback
                traceback.print_exc()
                status('retry_wait', error=f'{type(exc).__name__}: {exc}')
                atomic_json(state_path, state)
                if once:
                    raise
            if once:
                break
            delay = max(5, config.get('poll_seconds', 900) - (time.monotonic() - started))
            until = time.monotonic() + delay
            while time.monotonic() < until and not (root / 'STOP').exists():
                time.sleep(min(5, max(0, until - time.monotonic())))
        collection_stop.set()
        if collector:
            collector.join()
        status('stopped' if (root / 'STOP').exists() else 'finished')

