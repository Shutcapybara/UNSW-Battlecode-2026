"""Paired closed-loop local evaluation; never substitutes local for live Elo."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import importlib.metadata

import numpy as np

from .data import ROOT, atomic_json, extract


def bot_interpreter():
    """Use the lightweight base interpreter for bot workers when available.

    The game CLI probes ``UNSWBC_PYTHON`` with a short startup timeout. The
    campaign's venv contains PyTorch and can exceed that timeout under load,
    while exported bot packages use only the Python standard library.
    """
    candidates = [getattr(sys, '_base_executable', None)]
    base_name = 'python.exe' if os.name == 'nt' else 'bin/python'
    candidates.append(str(Path(sys.base_prefix) / base_name))
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(Path(candidate).resolve())
    return sys.executable


def package(policy, out, temperature=0.0, seed=0):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for source, name in ((Path(__file__).with_name('bot_main.py'), 'main.py'),
                         (Path(__file__).with_name('policy.py'), 'policy.py'),
                         (ROOT / 'tools/team_recon_claude/features_view.py', 'features_view.py'),
                         (Path(policy), 'policy.json')):
        shutil.copy2(source, out / name)
    atomic_json(out / 'settings.json', dict(temperature=temperature, seed=seed))
    (out / 'bot.toml').write_text('[project]\nlanguage = "py"\ninclude = ["*.py", "*.json"]\n', encoding='utf-8')
    return out


def source_hash(folder):
    h = hashlib.sha256()
    for path in sorted(Path(folder).rglob('*')):
        if any(p.startswith('.') or p == '__pycache__' for p in path.relative_to(folder).parts):
            continue
        if path.is_file() and path.suffix in ('.py', '.cpp', '.h', '.hpp', '.json', '.toml'):
            h.update(str(path.relative_to(folder)).encode())
            h.update(path.read_bytes())
    return h.hexdigest()


def run_game(bot, opponent, board, side, seed, output, timeout=600, known_hashes=None):
    bot, opponent, board = (Path(p).resolve() for p in (bot, opponent, board))
    output = Path(output).resolve()
    known_hashes = known_hashes or {}
    hash_of = lambda path: known_hashes.get(str(path)) or source_hash(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    a, b = (bot, opponent) if side == 'A' else (opponent, bot)
    command = [sys.executable, '-m', 'unswbc.cli', 'run', str(board), str(a), str(b),
               '-o', str(output), '--seed', str(seed), '--no-logs', '--no-draw']
    log = output.with_suffix('.log')
    env = dict(os.environ, UNSWBC_PYTHON=bot_interpreter(), UNSWBC_NO_UPDATE='1', UNSWBC_NO_VSCODE='1')
    from tools.stats_store import StatsStore
    store = StatsStore(queue_only=True)
    manifest = dict(bot_a=str(a), bot_b=str(b), source_a=hash_of(a), source_b=hash_of(b),
                    map=str(board), map_hash=hashlib.sha256(board.read_bytes()).hexdigest(), seed=seed,
                    mode='native', toolkit=importlib.metadata.version('unswbc'), replay=str(output), log=str(log))
    run_id = store.start_run(producer='growth_rl', manifest=manifest)
    atomic_json(output.with_suffix('.run.json'), dict(run_id=run_id))
    try:
        with log.open('w', encoding='utf-8') as stream:
            child = subprocess.Popen(command, cwd=output.parent, env=env, stdout=stream, stderr=subprocess.STDOUT,
                                     creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            try:
                returncode = child.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                if os.name == 'nt':
                    subprocess.run(['taskkill', '/PID', str(child.pid), '/T', '/F'], capture_output=True,
                                   creationflags=subprocess.CREATE_NO_WINDOW)
                else:
                    child.kill()
                child.wait()
                raise
        if returncode != 0 or not output.exists():
            raise RuntimeError(f'game failed (exit {returncode}); see {log}')
        match = re.search(r'^(?:team ([AB]) wins|draw) after (\d+) rounds', log.read_text(encoding='utf-8'), re.MULTILINE)
        if not match:
            raise RuntimeError(f'no completed game result in {log}')
        outcome = match[1] or 'draw'
        store.append_match(run_id, 'game', dict(**manifest, outcome=outcome, rounds=int(match[2]),
            winner=str(a if outcome == 'A' else b) if outcome != 'draw' else None, runtime_faults=None))
    except Exception as exc:
        store.append(run_id, 'match_error', 'game', dict(**manifest, outcome='error', error=type(exc).__name__))
        raise
    finally:
        store.close()
    return output


def paired_gate(candidate, incumbent, opponents, maps, seeds, out, cache,
                population_weight=0.25, min_pairs=12, bootstrap=2000, seed=1701,
                win_tolerance=0.05, stop_file=None):
    out = Path(out)
    records = []
    for board in maps:
        for opponent in opponents:
            for fixture_seed in seeds:
                for side in 'AB':
                    if stop_file and Path(stop_file).exists():
                        raise InterruptedError('STOP requested between evaluation games')
                    identity = dict(map_hash=hashlib.sha256(Path(board).read_bytes()).hexdigest(),
                                    opponent_hash=source_hash(opponent), side=side, seed=fixture_seed)
                    key = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()[:20]
                    pair = dict(identity=identity, map=str(board), opponent=str(opponent))
                    for name, bot in (('candidate', candidate), ('incumbent', incumbent)):
                        replay = out / 'replays' / f'{key}-{name}.replay'
                        receipt = replay.with_suffix('.json')
                        expected = dict(**identity, actor_hash=source_hash(bot), source='evaluation')
                        cached = receipt.exists() and json.loads(receipt.read_text()) == expected
                        if not replay.exists() or not cached:
                            run_game(bot, opponent, board, side, fixture_seed, replay)
                            atomic_json(receipt, expected)
                        game = extract(replay, cache)
                        series = game['series']
                        at100 = (series.get('100') or series[100])[side]
                        initial = (series.get('0') or series[0])[side]
                        objective = (np.log1p(at100['total']) - np.log1p(initial['total']) + population_weight * (
                            np.log1p(at100['units']) - np.log1p(initial['units'])))
                        winner = game['result']['winner']
                        pair[name] = dict(**at100, objective=float(objective),
                                          score=0.5 if winner is None else float(winner == side))
                    records.append(pair)
                    atomic_json(out / 'pairs.json', records)
                    print(f'paired evaluation {len(records)}: {Path(board).stem} {side}', flush=True)
    report = gate_report(records, min_pairs, bootstrap, seed, win_tolerance)
    report.update(candidate_hash=source_hash(candidate), incumbent_hash=source_hash(incumbent),
                  evidence='local native games; no judge-budget or live-Elo claim')
    atomic_json(out / 'gate.json', report)
    return report


def gate_report(records, min_pairs=12, bootstrap=2000, seed=1701, win_tolerance=0.05):
    """Bootstrap map/opponent clusters, keeping seats and seeds together."""
    groups = {}
    for pair in records:
        key = (pair['identity']['map_hash'], pair['identity']['opponent_hash'])
        groups.setdefault(key, []).append([
            pair['candidate'][m] - pair['incumbent'][m] for m in ('objective', 'score', 'units', 'total')])
    if not groups:
        return dict(promote=False, reason='no completed pairs', pairs=0)
    clusters = np.asarray([np.mean(rows, axis=0) for rows in groups.values()])
    rng = np.random.default_rng(seed)
    samples = np.asarray([clusters[rng.integers(0, len(clusters), len(clusters))].mean(0) for _ in range(bootstrap)])
    lower, upper = np.quantile(samples, [0.025, 0.975], axis=0)
    mean = clusters.mean(0)
    enough = len(records) >= min_pairs and len(groups) >= 4
    # Better retained growth with no supported win-rate or population collapse.
    promote = bool(enough and lower[0] > 0 and lower[1] >= -win_tolerance and mean[2] >= 0 and mean[3] > 0)
    return dict(promote=promote, pairs=len(records), clusters=len(groups),
                reason='passed' if promote else 'insufficient evidence or regression',
                deltas={m: dict(mean=float(mean[i]), low=float(lower[i]), high=float(upper[i]))
                        for i, m in enumerate(('growth_objective', 'score', 'units_r100', 'total_r100'))})
