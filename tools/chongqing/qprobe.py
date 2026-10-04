"""chongqing: queen home-range / contact probe on contact maps (post-m2). Run from the repo root.

  python3 tools/chongqing/qprobe.py --maps "Australia,Islands,Around UNSW" --per 15 [--era post-m2]

For each (map, group in {us, top10}) sample of games: the queen's Chebyshev distance from its spawn at death (or at the end),
enemy heads within Chebyshev 3 of the queen's head at the death round, the queen's length at death, and the share of
rounds the queen spent within 6 of its spawn (Shenzhen H-SZ14/16 'home range'). Decode-only (frame.decode), ~0.5 s/game.
"""
import argparse, collections, statistics, sys, time
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))
PY = ROOT / 'build' / 's1-pylib'
if sys.platform.startswith('linux') and PY.exists():
    sys.path.append(str(PY))
import pandas as pd
from tools.analysis.features.frame import decode


def cheb(a, b, W, H):
    dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1])
    return max(min(dx, W - dx), min(dy, H - dy))   # torus-aware (sonar wraps; movement may too)


def probe(path, team):
    g = decode(path)
    W, H = g['W'], g['H']
    rounds = g['rounds']
    ids = [i for i, (tt, b) in rounds[0].items() if tt == team]
    q = min(ids)
    spawn = rounds[0][q][1][0]
    home6 = 0; alive_rounds = 0; death = None; dist_death = None; enemies3 = None; len_death = None
    for r, snap in enumerate(rounds):
        if q in snap:
            head = snap[q][1][0]
            alive_rounds += 1
            if cheb(head, spawn, W, H) <= 6:
                home6 += 1
            last_head, last_len = head, len(snap[q][1])
        else:
            death = r - 1
            break
    end_snap = rounds[death] if death is not None else rounds[-1]   # state just before the fatal round / final state
    dist_death = cheb(last_head, spawn, W, H)
    enemies3 = sum(1 for i, (tt, b) in end_snap.items() if tt != team and cheb(b[0], last_head, W, H) <= 3)
    return dict(R=g['last_round'], death=death, alive=death is None, dist_death=dist_death, enemies3=enemies3,
                len_death=last_len, home6_share=home6 / max(1, alive_rounds))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--maps', default='Australia,Islands,Around UNSW')
    ap.add_argument('--per', type=int, default=15)
    ap.add_argument('--era', default='post-m2')
    a = ap.parse_args()
    g = pd.read_parquet(ROOT / 'build/s1/corpus/games.parquet'); t = pd.read_parquet(ROOT / 'build/s1/corpus/teams.parquet')
    top = set(t[t.cohort == 'top10'].team)
    g = g[(g.map_era == a.era)].sort_values('started_at', ascending=False)
    rows = []
    t0 = time.time()
    for m in a.maps.split(','):
        gm = g[g['map'] == m]
        for grp, sel in (('us', (gm.team_a == '7') | (gm.team_b == '7')), ('top10', (gm.team_a.isin(top) | gm.team_b.isin(top)) & (gm.team_a != '7') & (gm.team_b != '7'))):
            for r in gm[sel].head(a.per).itertuples():
                if grp == 'us':
                    team = 'A' if r.team_a == '7' else 'B'
                else:
                    team = 'A' if r.team_a in top else 'B'
                p = ROOT / 'public_replays/corpus/replays' / f'{r.game}.replay'
                if not p.exists():
                    continue
                rows.append(dict(map=m, grp=grp, game=r.game, **probe(p, team)))
    df = pd.DataFrame(rows)
    pd.set_option('display.width', 220)
    agg = df.groupby(['map', 'grp']).agg(n=('game', 'size'), alive=('alive', 'mean'), death_med=('death', 'median'),
                                        dist_med=('dist_death', 'median'), dist_p75=('dist_death', lambda s: s.quantile(.75)),
                                        far_gt6=('dist_death', lambda s: (s > 6).mean()), enemies3_mean=('enemies3', 'mean'),
                                        enemies3_ge1=('enemies3', lambda s: (s >= 1).mean()), len_med=('len_death', 'median'),
                                        home6=('home6_share', 'mean')).round(2)
    print(agg.to_string())
    print(f'[{len(df)} games, {time.time() - t0:.0f}s]', file=sys.stderr)
    df.to_csv(ROOT / 'build/chongqing/qprobe.csv', index=False)


if __name__ == '__main__':
    main()
