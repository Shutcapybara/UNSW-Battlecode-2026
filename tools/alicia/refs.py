#!/usr/bin/env python3
"""Freeze tools/alicia/base_refs.json: the base's own per-map medians on the held-in off-pool maps (maps without
field references) and rho_s = the base's pool-median ratio to the field median, so reward.py can place an off-pool
side-game on the pooled field scale (design memo §0.2). Training seeds only (>= 1000), never the evaluation seeds.

    python3 tools/alicia/refs.py --seeds 1000,1001 --pool-cache build/alicia/train/s1/games.jsonl [--jobs 14]
"""
from __future__ import annotations

import argparse, json, os, statistics, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.alicia import env as E  # noqa: E402
from tools.alicia.reward import BASE_REFS, CURVE, Curve  # noqa: E402
from tools.alicia.train import HELD_IN, POOL, ZOO  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seeds', default='1000,1001')
    ap.add_argument('--pool-cache', required=True, help='env cache holding parent (no-override) rows on the pool')
    ap.add_argument('--jobs', type=int, default=max(1, (os.cpu_count() or 4) - 2))
    a = ap.parse_args()
    curve = Curve()
    fx = [dict(params={}, map=m, seat=s, seed=int(sd), opp=o)
          for sd in a.seeds.split(',') for m in HELD_IN for o in ZOO for s in 'AB']
    E.prebuild(E.BOT)
    rows = [r for r in E.run(fx, str(ROOT / 'build/alicia/refs/games.jsonl'), a.jobs) if r]
    maps = {}
    for m in HELD_IN:
        rs = [r for r in rows if r['map'] == m]
        if rs and not curve.has_field(rs[0]['field_map']):
            maps[m] = {s: statistics.median(r[s] for r in rs) for s in CURVE}
            maps[m]['n'] = len(rs)
    ph = E.phash({})
    pool = [r for r in E.load_cache(a.pool_cache).values() if r['phash'] == ph and r['map'] in POOL]
    rho = {}
    for s in CURVE:
        rs = [r[s] / curve.median[s][r['field_map']] for r in pool if curve.median[s].get(r['field_map'])]
        rho[s] = statistics.median(rs)
    out = dict(note='base (alicia-02-tunable, no override) per-map medians on held-in maps; rho = base pool median '
                    'ratio to field median; training seeds only', seeds=a.seeds, n_pool=len(pool), rho=rho, maps=maps)
    BASE_REFS.write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
