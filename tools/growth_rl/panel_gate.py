"""Resumable paired pool/generalisation gate for growth-policy checkpoints."""
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from .data import atomic_json, extract
from .evaluate import run_game, source_hash

CHECKPOINTS = (10, 25, 50, 75, 100)
DEATH_KINDS = ('wall', 'self', 'body', 'h2h')
PANEL_GATE_VERSION = 1


def _series(game, side, checkpoint):
    rounds = game['series']
    return rounds.get(str(checkpoint), rounds.get(checkpoint))[side]


def _checkpoint_metrics(game, side, population_weight):
    initial = _series(game, side, 0)
    rounds = {}
    for checkpoint in CHECKPOINTS:
        stats = _series(game, side, checkpoint)
        dragon_turns = max(1, stats.get('dragon_turns', 0))
        rounds[str(checkpoint)] = dict(
            units=stats['units'], total=stats['total'], longest=stats['longest'],
            pearls=stats['pearls'],
            corpse_pearl_share=stats.get('pearls_corpse', 0) / max(1, stats['pearls']),
            growth_objective=(math.log1p(stats['total']) - math.log1p(initial['total']) + population_weight *
                              (math.log1p(stats['units']) - math.log1p(initial['units']))),
            death_rates={kind: 1000 * stats.get(f'deaths_{kind}', 0) / dragon_turns
                         for kind in DEATH_KINDS},
            dragon_turns=stats.get('dragon_turns', 0),
            ended_before_checkpoint=game['result']['rounds'] < checkpoint)
    return rounds


def _run_fixture(fixture, candidate, incumbent, hashes, out, cache, population_weight):
    board = Path(fixture['map']).resolve()
    opponent = Path(fixture['opponent']).resolve()
    identity = fixture['identity']
    key = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()[:24]
    results = {}
    for name, bot, bot_hash in (('candidate', candidate, hashes['candidate']),
                                ('incumbent', incumbent, hashes['incumbent'])):
        replay = out / 'replays' / f'{key}-{name}.replay'
        receipt = replay.with_suffix('.json')
        expected = dict(**identity, actor_hash=bot_hash, source='evaluation')
        cached = receipt.exists() and json.loads(receipt.read_text(encoding='utf-8')) == expected
        if not replay.exists() or not cached:
            run_game(bot, opponent, board, identity['side'], identity['seed'], replay,
                     known_hashes=hashes)
            atomic_json(receipt, expected)
        game = extract(replay, cache)
        winner = game['result']['winner']
        results[name] = dict(score=0.5 if winner is None else float(winner == identity['side']),
                             checkpoints=_checkpoint_metrics(game, identity['side'], population_weight))
    return dict(identity=identity, map=str(board), opponent=str(opponent),
                candidate=results['candidate'], incumbent=results['incumbent'],
                candidate_hash=hashes['candidate'], incumbent_hash=hashes['incumbent'],
                gate_version=PANEL_GATE_VERSION)


def _pct(candidate, incumbent, floor=1.0):
    return (float(candidate) - float(incumbent)) / max(floor, float(incumbent))


def _record_vector(record, checkpoint='100'):
    cand, base = record['candidate'], record['incumbent']
    cs, bs = cand['checkpoints'][checkpoint], base['checkpoints'][checkpoint]
    vector = dict(
        growth_objective=cs['growth_objective'] - bs['growth_objective'],
        score=cand['score'] - base['score'],
        units_pct=_pct(cs['units'], bs['units']),
        total_pct=_pct(cs['total'], bs['total']),
        longest_pct=_pct(cs['longest'], bs['longest']),
        pearls_pct=_pct(cs['pearls'], bs['pearls']),
        corpse_pearl_share_delta=cs['corpse_pearl_share'] - bs['corpse_pearl_share'])
    for kind in DEATH_KINDS:
        vector[f'deaths_{kind}_relative'] = _pct(cs['death_rates'][kind], bs['death_rates'][kind], floor=0.25)
    return vector


def _cluster_interval(rows, names, bootstrap, seed):
    if not rows:
        return {name: dict(mean=None, lower=None, upper=None) for name in names}
    matrix = np.asarray([[row[name] for name in names] for row in rows], dtype=np.float64)
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, len(matrix), size=(bootstrap, len(matrix)))
    samples = matrix[indices].mean(axis=1)
    means = matrix.mean(axis=0)
    lower, upper = np.quantile(samples, [0.05, 0.95], axis=0)
    return {name: dict(mean=float(means[i]), lower=float(lower[i]), upper=float(upper[i]))
            for i, name in enumerate(names)}


def panel_gate_report(records, expected_pairs, *, required=('pool', 'generalization'),
                      bootstrap=4000, seed=1701, min_clusters=4):
    """D-032-style 90% cluster bootstrap, keeping seeds/seats inside map-opponent clusters."""
    names = ('growth_objective', 'score', 'units_pct', 'total_pct', 'longest_pct', 'pearls_pct',
             'corpse_pearl_share_delta', *(f'deaths_{kind}_relative' for kind in DEATH_KINDS))
    grouped = {}
    for record in records:
        panel = record['identity']['panel']
        cluster = (record['identity']['map_hash'], record['identity']['opponent_hash'])
        grouped.setdefault(panel, {}).setdefault(cluster, []).append(record)

    panels = {}
    for offset, (name, expected) in enumerate(expected_pairs.items()):
        clusters = grouped.get(name, {})
        # Average seeds and both seats before resampling each map/opponent cluster.
        cluster_rows = []
        for rows in clusters.values():
            vectors = [_record_vector(record) for record in rows]
            cluster_rows.append({metric: float(np.mean([v[metric] for v in vectors])) for metric in names})
        checkpoint_reports = {}
        for checkpoint in CHECKPOINTS:
            cp_names = ('growth_objective', 'units_pct', 'total_pct', 'longest_pct', 'pearls_pct',
                        'corpse_pearl_share_delta')
            cp_clusters = []
            for rows in clusters.values():
                vectors = []
                for record in rows:
                    cand = record['candidate']['checkpoints'][str(checkpoint)]
                    base = record['incumbent']['checkpoints'][str(checkpoint)]
                    vectors.append(dict(
                        growth_objective=cand['growth_objective'] - base['growth_objective'],
                        units_pct=_pct(cand['units'], base['units']),
                        total_pct=_pct(cand['total'], base['total']),
                        longest_pct=_pct(cand['longest'], base['longest']),
                        pearls_pct=_pct(cand['pearls'], base['pearls']),
                        corpse_pearl_share_delta=cand['corpse_pearl_share'] - base['corpse_pearl_share']))
                cp_clusters.append({metric: float(np.mean([v[metric] for v in vectors])) for metric in cp_names})
            checkpoint_reports[str(checkpoint)] = _cluster_interval(
                cp_clusters, cp_names, bootstrap, seed + offset * 31 + checkpoint)
        panel_pairs = sum(len(rows) for rows in clusters.values())
        panels[name] = dict(
            pairs=panel_pairs, expected_pairs=expected,
            clusters=len(clusters), complete=(panel_pairs == expected and len(clusters) >= min_clusters),
            metrics=_cluster_interval(cluster_rows, names, bootstrap, seed + offset),
            per_checkpoint=checkpoint_reports)

    criteria = {}
    for name in required:
        panel = panels.get(name)
        criteria[f'{name}_complete'] = bool(panel and panel['complete'])
    pool = panels.get('pool', {}).get('metrics', {})
    generalization = panels.get('generalization', {}).get('metrics', {})
    criteria['pool_growth_positive'] = bool(pool.get('growth_objective', {}).get('lower') is not None and
                                            pool['growth_objective']['lower'] > 0)
    criteria['generalization_growth_noninferior'] = bool(
        generalization.get('growth_objective', {}).get('lower') is not None and
        generalization['growth_objective']['lower'] > -0.02)
    for panel_name, metrics in (('pool', pool), ('generalization', generalization)):
        for metric in ('units_pct', 'total_pct', 'score'):
            criteria[f'{panel_name}_{metric}_guard'] = bool(
                metrics.get(metric, {}).get('lower') is not None and metrics[metric]['lower'] >= -0.02)
        for kind in DEATH_KINDS:
            metric = metrics.get(f'deaths_{kind}_relative', {})
            criteria[f'{panel_name}_deaths_{kind}_guard'] = bool(
                metric.get('upper') is not None and metric['upper'] <= 0.10)
    promote = all(criteria.values())
    return dict(promote=promote, reason='passed' if promote else 'incomplete panel or D-032 guard failed',
                confidence=0.90, bootstrap_clusters='map x opponent; seeds and seats kept together',
                panels=panels, criteria=criteria)


def _identity_key(identity):
    return json.dumps(identity, sort_keys=True, separators=(',', ':'))


def paired_panel_gate(candidate, incumbent, panels, out, cache, *, population_weight=0.25,
                      bootstrap=4000, seed=1701, jobs=1, stop_file=None, min_clusters=4):
    """Run/reuse exact paired fixtures, then apply separate pool and unseen-map gates."""
    if jobs < 1:
        raise ValueError('jobs must be at least one')
    candidate, incumbent = Path(candidate).resolve(), Path(incumbent).resolve()
    out, cache = Path(out), Path(cache)
    out.mkdir(parents=True, exist_ok=True)
    hashes = {'candidate': source_hash(candidate), 'incumbent': source_hash(incumbent)}
    specs, fixtures, expected_pairs = [], [], {}
    opponent_hashes = {}
    for panel in panels:
        name = panel['name']
        maps = [Path(p).resolve() for p in panel['maps']]
        opponents = [Path(p).resolve() for p in panel['opponents']]
        seeds = [int(s) for s in panel['seeds']]
        expected_pairs[name] = len(maps) * len(opponents) * len(seeds) * 2
        specs.append(dict(name=name, maps=[str(p) for p in maps], opponents=[str(p) for p in opponents], seeds=seeds))
        for board in maps:
            if not board.is_file():
                raise FileNotFoundError(board)
            board_hash = hashlib.sha256(board.read_bytes()).hexdigest()
            for opponent in opponents:
                if not opponent.is_dir():
                    raise FileNotFoundError(opponent)
                if str(opponent) not in opponent_hashes:
                    opponent_hashes[str(opponent)] = source_hash(opponent)
                opponent_hash = opponent_hashes[str(opponent)]
                for fixture_seed in seeds:
                    for side in 'AB':
                        identity = dict(panel=name, map_hash=board_hash, opponent_hash=opponent_hash,
                                        side=side, seed=fixture_seed)
                        fixtures.append(dict(identity=identity, map=str(board), opponent=str(opponent)))
    hashes.update(opponent_hashes)

    by_key = {}
    for file in (out / 'pairs.jsonl', out / 'pairs.json'):
        if not file.exists():
            continue
        try:
            content = file.read_text(encoding='utf-8')
            previous = [json.loads(line) for line in content.splitlines() if line.strip()] if file.suffix == '.jsonl' else json.loads(content)
            for record in previous:
                if (record.get('candidate_hash') == hashes['candidate'] and
                        record.get('incumbent_hash') == hashes['incumbent'] and
                        record.get('gate_version') == PANEL_GATE_VERSION):
                    by_key[_identity_key(record['identity'])] = record
        except (json.JSONDecodeError, TypeError):
            continue
    missing = [f for f in fixtures if _identity_key(f['identity']) not in by_key]
    journal = (out / 'pairs.jsonl').open('a', encoding='utf-8')

    def persist(fixture, record):
        by_key[_identity_key(fixture['identity'])] = record
        journal.write(json.dumps(record, separators=(',', ':'), allow_nan=False) + '\n')
        journal.flush()

    try:
        # Compile each unique opponent once before concurrent matches use its build directory.
        warmed = set()
        remaining = []
        stopped = False
        for fixture in missing:
            opponent = fixture['opponent']
            if opponent in warmed:
                remaining.append(fixture)
                continue
            if stop_file and Path(stop_file).exists():
                stopped = True
                remaining.append(fixture)
                continue
            persist(fixture, _run_fixture(fixture, candidate, incumbent, hashes, out, cache, population_weight))
            warmed.add(opponent)
            print(f"paired panel fixture {len(by_key)}: {fixture['identity']['panel']} {Path(fixture['map']).stem} {fixture['identity']['side']}", flush=True)
        iterator = iter(remaining)
        with ThreadPoolExecutor(max_workers=jobs) as executor:
            running = {}
            exhausted = False
            while running or not exhausted:
                while not exhausted and not stopped and len(running) < jobs:
                    if stop_file and Path(stop_file).exists():
                        stopped = True
                        break
                    fixture = next(iterator, None)
                    if fixture is None:
                        exhausted = True
                        break
                    running[executor.submit(_run_fixture, fixture, candidate, incumbent,
                                            hashes, out, cache, population_weight)] = fixture
                if not running:
                    break
                done, _ = wait(running, return_when=FIRST_COMPLETED)
                for future in done:
                    fixture = running.pop(future)
                    record = future.result()
                    persist(fixture, record)
                    print(f"paired panel fixture {len(by_key)}: {fixture['identity']['panel']} {Path(fixture['map']).stem} {fixture['identity']['side']}", flush=True)
        ordered = [by_key[_identity_key(f['identity'])] for f in fixtures if _identity_key(f['identity']) in by_key]
        atomic_json(out / 'pairs.json', ordered)
        if stopped or (stop_file and Path(stop_file).exists()):
            raise InterruptedError('STOP requested between paired fixtures')
        report = panel_gate_report(ordered, expected_pairs, bootstrap=bootstrap, seed=seed,
                                   min_clusters=min_clusters)
        report.update(candidate_hash=hashes['candidate'], incumbent_hash=hashes['incumbent'],
                      evidence='local native games; no judge-budget or live-Elo claim',
                      panel_specs=specs)
        atomic_json(out / 'gate.json', report)
        return report
    finally:
        journal.close()
