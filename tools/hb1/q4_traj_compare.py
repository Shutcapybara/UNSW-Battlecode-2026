"""HB-1 Q4 diagnosis: where does the mimic lose strength? Trajectories vs the same opponent on the same maps.

    .venv/bin/python tools/hb1/q4_traj_compare.py [--mimic-dir build/hb1/games/mimic-vs-ares-v04]

Real: Heartbreaker's corpus games vs team 7 after 29 Sep 06:47 UTC (our Ares V04 live). Mimic: the h2h replays.
For each side (subject = Heartbreaker or mimic, opp = Ares V04): dragons, longest, total length at fixed rounds,
medians over games still running, per map and pooled. Writes game_stats/runs/hb1-q4-traj-compare.json.
"""
import argparse, json, sys
from multiprocessing import Pool
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'team_recon_claude'))
import recon

ROUNDS = (25, 50, 100, 150, 200, 300, 400, 499)


def traj(args):
    path, side, src, mp = args
    g = recon.Game(str(path))
    snaps = {}
    other = 'B' if side == 'A' else 'A'

    def stat(t):
        al = [d for d in g.dragons.values() if d.alive and d.team == t]
        return len(al), max([len(d.body) for d in al] or [0]), sum(len(d.body) for d in al)

    def cb(kind, **k):
        if kind == 'round' and k['round'] in ROUNDS:
            snaps[k['round']] = (stat(side), stat(other))
    res = g.run(cb)
    rows = []
    for r, (s, o) in snaps.items():
        rows.append(dict(src=src, map=mp, round=r, units=s[0], longest=s[1], total=s[2], o_units=o[0],
                         o_longest=o[1], o_total=o[2], won=res.get('winner') == side))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mimic-dir', default=str(ROOT / 'build/hb1/games/mimic-vs-ares-v04'))
    a = ap.parse_args()
    g = pd.read_parquet(ROOT / 'build/hb1/games.parquet')
    real = g[(g.opp == 7) & (g.set == 'corpus') & (g.t >= pd.Timestamp('2026-09-29 06:47', tz='UTC'))]
    work = [(r.path, r.side, 'real', r.map) for r in real.itertuples()]
    names = {}
    for f in (ROOT / 'maps').glob('*.map'):
        for line in f.read_text().splitlines()[:5]:
            if line.startswith('MAP_NAME'):
                names[f.stem] = line.split(' ', 1)[1].strip()
    for p in sorted(Path(a.mimic_dir).glob('*.replay')):
        mp, seat, _ = p.stem.split('__')
        work.append((p, seat, 'mimic', names.get(mp, mp)))
    rows = []
    with Pool(8) as pool:
        for r in pool.imap_unordered(traj, work):
            rows += r
    d = pd.DataFrame(rows)
    cols = ['units', 'longest', 'total', 'o_units', 'o_longest', 'o_total']
    pooled = d.groupby(['src', 'round'])[cols].median().round(1)
    alive = d.groupby(['src', 'round']).size().rename('games_running')
    print(pd.concat([pooled, alive], axis=1).to_string())
    per_map = d[d['round'].isin([50, 100, 200])].groupby(['map', 'round', 'src'])[['units', 'total', 'o_units', 'o_total']].median()
    print(per_map.unstack('src').round(1).to_string())
    out = dict(pooled=pd.concat([pooled, alive], axis=1).reset_index().to_dict('records'),
               per_map=per_map.reset_index().to_dict('records'), n_real=len(real), n_mimic=len(work) - len(real))
    (ROOT / 'game_stats/runs/hb1-q4-traj-compare.json').write_text(json.dumps(out, indent=1, default=float))


if __name__ == '__main__':
    main()
