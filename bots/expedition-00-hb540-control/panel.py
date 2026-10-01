#!/usr/bin/env python3
"""Expedition panel contract. Defaults to a dry run; never starts games implicitly.

Use --run only on an authorized host. --score is read-only over completed rows.
The historical Aline D-032 mean-form gate is reported alongside its cluster
intervals; it is not silently substituted for the median-form lane gate.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.rb import gate
from tools.analysis.features.run_panel import runtime_fingerprint

SPEC = importlib.util.spec_from_file_location('expedition_panel_source', ROOT / 'tools/rb/run.py')
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)
OUT = ROOT / 'build/expedition/panels'
PARENT = 'expedition-01-nodevil'
BOTS = [d['bot'] for d in json.loads(Path(__file__).with_name('manifest.json').read_text())][1:]


def paths(bot):
    return OUT / f'{bot}-{runtime_fingerprint(str(ROOT / "bots" / bot))[:12]}'


def expected(panel, seeds):
    maps, opps = (runner.LIVE, runner.ZOO) if panel == 'z1' else (runner.GEN, gate.GEN_OPPS)
    return {(m, side, seed, opp) for m in maps for side in 'AB' for seed in seeds for opp in opps}


def load_complete(bot, panel, seeds):
    path = paths(bot) / f'{panel}.jsonl'
    rows = {}
    for line in path.read_text().splitlines():
        r = json.loads(line)
        if r['seed'] not in seeds:
            continue
        k = (r['map'], r['side'], r['seed'], r['opp'])
        if k in rows:
            raise ValueError(f'Duplicate fixture in {path}: {k}')
        if Path(r['cand']).name != bot or r.get('errors') or r['result'] not in ('win', 'loss', 'draw'):
            raise ValueError(f'Failed or misattributed fixture in {path}: {k}')
        rows[k] = r
    wanted = expected(panel, seeds)
    if set(rows) != wanted:
        raise ValueError(f'{path}: {len(wanted - rows.keys())} missing / {len(rows.keys() - wanted)} extra fixtures')
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('bot', choices=BOTS)
    modes = ap.add_mutually_exclusive_group()
    modes.add_argument('--run', action='store_true')
    modes.add_argument('--score', action='store_true')
    ap.add_argument('--seeds', default='1,2,3')
    ap.add_argument('--jobs', type=int, default=1)
    ap.add_argument('--budget', type=float, default=180)
    a = ap.parse_args()
    seeds = [int(s) for s in a.seeds.split(',')]
    if not seeds or len(seeds) != len(set(seeds)) or any(s < 1 for s in seeds):
        ap.error('Use unique positive seeds')
    if not 1 <= a.jobs <= 4 or a.budget <= 0:
        ap.error('Use 1–4 jobs and a positive bounded run budget')
    counts = {p: len(expected(p, seeds)) for p in ('z1', 'gen')}
    print(json.dumps({'bot': a.bot, 'parent': PARENT, 'seeds': seeds, 'fixtures_per_arm': counts,
                      'fingerprint': runtime_fingerprint(str(ROOT / 'bots' / a.bot)),
                      'path': str(paths(a.bot)), 'game_execution': a.run}, indent=2))
    if a.score:
        if a.bot == PARENT or seeds != [1, 2, 3]:
            ap.error('Gate scoring requires a candidate and exactly seeds 1,2,3')
        stats = {p: gate.panel_stats(load_complete(a.bot, p, seeds), load_complete(PARENT, p, seeds), p)
                 for p in ('z1', 'gen')}
        verdict, reasons = gate.gate(stats)
        report = dict(candidate=a.bot, parent=PARENT, historical_aline_mean_gate=verdict, reasons=reasons,
                      panels=stats, promotion='NOT AUTHORIZED BY THIS REPORT',
                      caveat='Historical mean-form diagnostic; median form, tempo, r25/r50, and sandbox CPU still required.')
        dest = paths(a.bot) / 'score.json'
        dest.write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report, indent=2))
    elif a.run:
        dest = paths(a.bot)
        dest.mkdir(parents=True, exist_ok=True)
        # Run one bounded panel per invocation. Resume uses the same source-keyed file.
        for panel in ('z1', 'gen'):
            path = dest / f'{panel}.jsonl'
            if path.exists():
                try:
                    load_complete(a.bot, panel, seeds)
                    continue
                except ValueError as e:
                    if 'missing' not in str(e):
                        raise
            cmd = [sys.executable, str(ROOT / 'tools/rb/run.py'), f'bots/{a.bot}', '--panel', panel,
                   '--seeds', a.seeds, '--out', str(path), '--jobs', str(a.jobs), '--budget', str(a.budget)]
            if panel == 'gen':
                cmd += ['--opps', ','.join(gate.GEN_OPPS)]
            subprocess.run(cmd, cwd=ROOT, check=True)
            break


if __name__ == '__main__':
    main()
