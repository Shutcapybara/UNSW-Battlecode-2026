"""Hub preflight worker: metered probes on the pinned toolkit plus the activation contract, for one candidate.

    python -m tools.hub.preflight --candidate NAME [--root HUB]

Runs `unswbc run --sandbox --verbose` on the configured fixtures (Schooltime as A, Portals as B by default) against
the frozen reference opponent, parses the per-turn points, reconciles metering (readings + faults == turns), applies
the local gate, evaluates the activation contract on the same logs, and records probes/contract_results. Sets the
candidate's status to runtime_ok, runtime_failed or inactive_mechanism. Load-gated by the daemon.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import zipfile
from pathlib import Path

from . import db
from .config import hub_root, load_config
from .contracts import evaluate as evaluate_contract, points_profile
from .stats import FAULT

MAP_FILES = {9: 'schooltime', 20: 'portals', 21: 'slithery_fight', 7: 'queen_of_spades', 4: 'default', 11: 'trophy', 17: 'dilemma', 19: 'autarky', 13: 'devil', 15: 'trauma'}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def unpack(archive, target):
    target.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        z.extractall(target)
    return target


def run_probe(cfg, root, cand, map_id, side, source_dir):
    repo = Path(cfg['paths']['repo'])
    toolkit = cfg['paths']['toolkit']
    opponent = repo / cfg['runtime']['probe_opponent']
    board = repo / 'maps' / f'{MAP_FILES[map_id]}.map'
    out = Path(root) / 'runtime' / cand['name']
    out.mkdir(parents=True, exist_ok=True)
    label = f'{map_id}-{side}'
    replay, log = out / f'{label}.replay', out / f'{label}.log'
    bots = [source_dir, opponent] if side == 'A' else [opponent, source_dir]
    cmd = [toolkit, 'run', '--sandbox', '--verbose', '-o', str(replay), str(board), *map(str, bots)]
    env = dict(os.environ, PYTHONPYCACHEPREFIX=str(Path(root) / 'pycache'), UV_CACHE_DIR=str(Path(root) / 'uv-cache'))
    load = os.getloadavg()[0] if hasattr(os, 'getloadavg') else None
    started = time.time()
    row = dict(candidate_name=cand['name'], fingerprint=cand['fingerprint'], map_id=map_id, side=side, toolkit_path=toolkit, load_avg_1m=load,
               opponent_fingerprint=sha256_tree(opponent), map_sha256=sha256(board), replay_path=str(replay), at=db.now_iso())
    try:
        version = subprocess.check_output([toolkit, '--version'], text=True, timeout=30).strip().splitlines()[0]
        row['toolkit_version'] = version
        with log.open('w') as handle:
            result = subprocess.run(cmd, stdout=handle, stderr=subprocess.STDOUT, env=env, cwd=out, timeout=900)
        text = log.read_text(errors='replace')
        row['log_sha256'] = sha256(log)
        if result.returncode:
            raise RuntimeError(f'runner exit {result.returncode}')
        prof = points_profile(text, side)
        faults = [m for m in FAULT.findall(text) if m[2].upper() == side]
        turns = sum(1 for l in text.splitlines() if re.match(rf'^round \d+: bot \d+ \(team {side}\) stdout:', l))
        caught = len(re.findall(r'MC_ERROR', text))
        metered_ok = prof['turns'] + len(faults) == turns and turns > 0
        gate = cfg['runtime']['local_gate']
        passed = metered_ok and not faults and not caught and (prof['max_points'] or 10**12) < gate['max_points'] and (prof['p99_points'] or 10**12) < gate['p99_points']
        row.update(turns=turns, metered=prof['turns'], faults=len(faults), caught_errors=caught, max_points=prof['max_points'], p99_points=prof['p99_points'], passed=int(passed), error=None if metered_ok else 'metering incomplete')
    except Exception as exc:
        row.update(passed=0, error=type(exc).__name__ + ': ' + str(exc)[:200])
    row['id'] = f"{cand['name']}/{label}/{cand['fingerprint'][:12]}"
    row['seconds'] = round(time.time() - started)
    return row, log


def sha256_tree(directory):
    files = {p.name: sha256(p) for p in sorted(Path(directory).iterdir()) if p.is_file() and p.suffix in ('.py', '.toml', '.cpp', '.c', '.h')}
    return hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidate', required=True)
    p.add_argument('--root', default=None)
    a = p.parse_args(argv)
    root = Path(a.root) if a.root else hub_root()
    cfg = load_config(root)
    conn = db.connect(root)
    cand = conn.execute('SELECT * FROM candidates WHERE name=?', (a.candidate,)).fetchone()
    if not cand:
        print('unknown candidate', file=sys.stderr)
        return 2
    cand = db.loads_row(cand, 'activation_contract', 'source_files')
    source = unpack(cand['archive_path'], Path(root) / 'runtime' / cand['name'] / 'source')
    fixtures = []
    for map_id, side in cfg['runtime']['probe_fixtures']:
        existing = conn.execute('SELECT * FROM probes WHERE candidate_name=? AND fingerprint=? AND map_id=? AND side=?', (cand['name'], cand['fingerprint'], map_id, side)).fetchone()
        if existing:
            fixtures.append((dict(existing), Path(existing['replay_path']).with_suffix('.log')))
            continue
        row, log = run_probe(cfg, root, cand, map_id, side, source)
        db.upsert(conn, 'probes', row, 'id')
        fixtures.append((row, log))
        if not row['passed']:
            break
    passed = all(r['passed'] for r, _ in fixtures) and len(fixtures) == len(cfg['runtime']['probe_fixtures'])
    if not passed:
        conn.execute("UPDATE candidates SET status='runtime_failed', retired_reason='runtime_invalid', updated_at=? WHERE name=?", (db.now_iso(), cand['name']))
        db.event(conn, root, 'hub/preflight', 'probe_failed', dict(candidate=cand['name'], fixtures=[{k: r.get(k) for k in ('map_id', 'side', 'max_points', 'p99_points', 'faults', 'error')} for r, _ in fixtures]))
        print('runtime_failed', json.dumps([{k: r.get(k) for k in ('map_id', 'side', 'max_points', 'p99_points', 'faults', 'error')} for r, _ in fixtures]))
        return 0
    contract = cand.get('activation_contract') or {'kind': 'legacy_none'}
    logs = [dict(label=f"{r['map_id']}-{r['side']}", side=r['side'], log_text=Path(log).read_text(errors='replace') if Path(log).exists() else '') for r, log in fixtures]
    verdict = evaluate_contract(contract, logs)
    db.upsert(conn, 'contract_results', dict(id=f"{cand['name']}/{cand['fingerprint'][:12]}", candidate_name=cand['name'], fingerprint=cand['fingerprint'], kind=verdict['kind'],
                                             detail=verdict['detail'], passed=None if verdict['passed'] is None else int(verdict['passed']), at=db.now_iso()), 'id')
    if verdict['passed'] is False:
        conn.execute("UPDATE candidates SET status='retired', retired_reason='inactive_mechanism', updated_at=? WHERE name=?", (db.now_iso(), cand['name']))
        db.event(conn, root, 'hub/preflight', 'inactive_mechanism', dict(candidate=cand['name'], detail=verdict['detail']))
        print('inactive_mechanism', json.dumps(verdict['detail']))
        return 0
    if verdict['passed'] is None:
        db.event(conn, root, 'hub/preflight', 'contract_unevaluated', dict(candidate=cand['name'], kind=verdict['kind']))
    conn.execute("UPDATE candidates SET status='runtime_ok', updated_at=? WHERE name=?", (db.now_iso(), cand['name']))
    db.event(conn, root, 'hub/preflight', 'runtime_ok', dict(candidate=cand['name'], fixtures=[{k: r.get(k) for k in ('map_id', 'side', 'max_points', 'p99_points', 'toolkit_version')} for r, _ in fixtures]))
    print('runtime_ok')
    return 0


if __name__ == '__main__':
    sys.exit(main())
