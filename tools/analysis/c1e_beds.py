#!/usr/bin/env python3
"""C1-E live bed-map reconstruction: where pearls actually spawn on the live server maps.

Live replay map texts carry no TILE spawn fields (all-zero TILE lines), so the F1 bed
features (density, bed territory, EPG) are NaN on corpus replays and the local map files
cannot be assumed to match. This script reconstructs, per map layout (map_hash), the set of
bed cells and their empirical spawn rates from PearlCountdown/TileChange spawn events over
the cached corpus frames, and compares each layout against the local map file's bed set.

  python tools/analysis/c1e_beds.py            # ranked games, frames from build/c1e/frames
Out: game_stats/live_beds.json + a printed per-map summary.
"""
import argparse, collections, json, multiprocessing, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

LOCAL_FILES = {'Autarky': 'autarky', 'Default': 'default', 'Devil': 'devil', 'Portals': 'portals',
               'Prisoners Dilemma': 'dilemma', 'Queen Of Spades': 'queen_of_spades', 'Schooltime': 'schooltime',
               'Slithery Fight': 'slithery_fight', 'Trauma': 'trauma', 'Trophy': 'trophy'}
CACHE = ROOT / 'build/c1e/frames'
DECODED = ROOT / 'build/c1e/decoded'


def one(args):
    gid, map_name, parity = args
    from tools.analysis.features.frame import load
    try:
        g = load(str(DECODED / f'{gid}.replay'), str(CACHE))
    except Exception as e:
        return dict(gid=gid, map=map_name, error=f'{type(e).__name__}: {e}')
    beds = collections.Counter()
    for s in g['events']['spawns']:
        if s['origin'] == 'bed':
            beds['%d,%d' % s['cell']] += 1
    return dict(gid=gid, map=map_name, map_hash=g['map_hash'], rounds=g['last_round'] + 1,
                parity=parity, beds=dict(beds))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--index', default='build/c1e/ranked_games.jsonl')
    ap.add_argument('--out', default='game_stats/live_beds.json')
    ap.add_argument('--jobs', type=int, default=10)
    a = ap.parse_args(argv)
    try:
        multiprocessing.set_start_method('fork')
    except RuntimeError:
        pass
    from concurrent.futures import ProcessPoolExecutor
    rows = [json.loads(l) for l in open(ROOT / a.index)]
    jobs = [(r['game_id'], r['map_name'], r['game_id'] % 2) for r in rows
            if (DECODED / f"{r['game_id']}.replay").exists()]
    layouts = collections.defaultdict(lambda: dict(n=0, rounds=0, cells=collections.Counter(),
                                                   parities=collections.Counter(), games=[]))
    errors = 0
    with ProcessPoolExecutor(a.jobs) as ex:
        for i, res in enumerate(ex.map(one, jobs, chunksize=8), 1):
            if 'error' in res:
                errors += 1
                continue
            L = layouts[(res['map'], res['map_hash'])]
            L['n'] += 1
            L['rounds'] += res['rounds']
            L['parities'][res['parity']] += 1
            L['cells'].update(res['beds'])
            L['games'].append(res['gid'])
    out = {}
    sys.path.insert(0, str(ROOT / 'tools/hub/vendor/ouroboros'))
    from mapview import load_map
    for (name, mh), L in sorted(layouts.items()):
        d = dict(map=name, map_hash=mh, n_games=L['n'], total_rounds=L['rounds'],
                 bed_count=len(L['cells']),
                 game_id_parity_counts={str(k): v for k, v in sorted(L['parities'].items())},
                 example_games=L['games'][:3],
                 beds={c: dict(spawns=k, per_1000_rounds=round(1000 * k / L['rounds'], 3))
                       for c, k in sorted(L['cells'].items(), key=lambda kv: -kv[1])})
        lp = ROOT / 'maps' / (LOCAL_FILES.get(name, name.lower().replace(' ', '_')) + '.map')
        if lp.exists():
            local = {c for c, v in load_map(lp.read_text())['tiles'].items() if v[1] > 0}
            live = {tuple(int(x) for x in c.split(',')) for c in L['cells']}
            d['local_file_beds'] = len(local)
            d['local_overlap'] = len(live & local)
            d['live_only'] = len(live - local)
            d['local_only_never_seen_live'] = len(local - live)
        out.setdefault(name, {})[mh[:16]] = d
        print(f"{name:20s} {mh[:16]} n={L['n']:4d} rounds={L['rounds']:7d} live_beds={len(L['cells']):4d}"
              f" local={d.get('local_file_beds')} overlap={d.get('local_overlap')} live_only={d.get('live_only')}"
              f" parities={dict(L['parities'])}")
    Path(ROOT / a.out).parent.mkdir(parents=True, exist_ok=True)
    json.dump(dict(_note=('live bed cells and empirical spawn rates per map layout (map_hash), '
                          'reconstructed from bed-origin spawn events; TILE lines in live replays carry no spawn fields'),
                   _index=str(a.index), _games=len(jobs), _errors=errors, maps=out),
              open(ROOT / a.out, 'w'), indent=1, sort_keys=True)
    print(f'wrote {a.out}: {len(jobs)} games, {errors} errors, {len(out)} maps')


if __name__ == '__main__':
    main()
