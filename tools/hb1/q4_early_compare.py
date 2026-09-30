"""HB-1 Q4 diagnosis: early-game actions of the mimic vs real Heartbreaker against Ares V04 (same replays as
q4_traj_compare). Per round bucket: turns, split rate on split-eligible turns, eats per 100 turns (length grew
since the dragon's previous turn), deaths per 100 turns by reason. Writes game_stats/runs/hb1-q4-early-compare.json.
"""
import collections, json, sys
from multiprocessing import Pool
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'team_recon_claude'))
import recon

BUCKETS = ((0, 25), (25, 50), (50, 100), (100, 200), (200, 500))


def bucket(r):
    for lo, hi in BUCKETS:
        if lo <= r < hi:
            return f'{lo}-{hi - 1}'


def one(args):
    path, side, src = args
    g = recon.Game(str(path))
    c = collections.Counter()
    last_len = {}

    def cb(kind, **k):
        if kind == 'turn':
            d = k['dragon']
            if d.team != side:
                return
            b = bucket(g.round)
            L = len(d.body)
            c[(b, 'turns')] += 1
            if d.id in last_len and L > last_len[d.id]:
                c[(b, 'eats')] += 1
            last_len[d.id] = L
            units = sum(1 for o in g.dragons.values() if o.alive and o.team == side)
            if L >= 4 and units < g.board.unit_limit:
                c[(b, 'elig')] += 1
        elif kind == 'action' and k['dragon'].team == side and k['action'][0] == 'split':
            c[(bucket(g.round), 'splits')] += 1
        elif kind == 'death' and k['dragon'].team == side:
            c[(bucket(g.round), 'death_' + k['reason'])] += 1
    g.run(cb)
    return src, c


def main():
    g = pd.read_parquet(ROOT / 'build/hb1/games.parquet')
    real = g[(g.opp == 7) & (g.set == 'corpus') & (g.t >= pd.Timestamp('2026-09-29 06:47', tz='UTC'))]
    work = [(r.path, r.side, 'real') for r in real.itertuples()]
    work += [(p, p.stem.split('__')[1], 'mimic') for p in sorted((ROOT / 'build/hb1/games/mimic-vs-ares-v04').glob('*.replay'))]
    tot = {'real': collections.Counter(), 'mimic': collections.Counter()}
    with Pool(8) as pool:
        for src, c in pool.imap_unordered(one, work):
            tot[src].update(c)
    rows = []
    for src, c in tot.items():
        for lo, hi in BUCKETS:
            b = f'{lo}-{hi - 1}'
            t = max(1, c[(b, 'turns')])
            row = dict(src=src, bucket=b, turns=c[(b, 'turns')], split_rate_elig=c[(b, 'splits')] / max(1, c[(b, 'elig')]),
                       eats_per100=100 * c[(b, 'eats')] / t)
            for k in [k for k in c if k[0] == b and k[1].startswith('death_')]:
                row[k[1] + '_per100'] = 100 * c[k] / t
            rows.append(row)
    d = pd.DataFrame(rows).fillna(0).set_index(['bucket', 'src']).sort_index()
    print(d.round(2).to_string())
    (ROOT / 'game_stats/runs/hb1-q4-early-compare.json').write_text(json.dumps(d.reset_index().to_dict('records'), indent=1))


if __name__ == '__main__':
    main()
