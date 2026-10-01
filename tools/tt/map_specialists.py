"""TT: per-map specialists. Which teams win more on a map than their opponents' strength predicts?

    .venv/bin/python tools/tt/map_specialists.py [--all-games] [--min-games 60] [--top 12]

Bradley-Terry fit on the corpus index (ranked games by default: unranked games can be dummy uploads): a strength per
team (teams under --min-games pooled) plus a side-B advantage per map; no map-by-team terms. A team's map residual is
its actual minus expected wins on that map over games against fitted opponents, as a rate, with the binomial SE of the
expectation. Reports the five analysed top teams plus our team (7) and the --top strongest others.
Writes game_stats/runs/tt-map-specialists[-all].json.
"""
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parents[2]
NAMES = {62: 'Heartbreaker', 70: 'cheji bt', 206: 'Stockfish', 264: 'forgot to mention', 952: 'Cache me outside', 7: 'us (7)'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--all-games', action='store_true')
    ap.add_argument('--min-games', type=int, default=60)
    ap.add_argument('--top', type=int, default=12)
    a = ap.parse_args()
    d = pd.read_json(ROOT / 'public_replays/corpus/index.jsonl', lines=True)
    d = d[d.winner.isin(['a', 'b']) & d.map_name.notna()]
    if not a.all_games:
        d = d[d.ranked]
    mc = d.map_name.value_counts()
    d = d[d.map_name.isin(mc[mc >= 500].index)]          # the ten ladder maps
    vc = pd.concat([d.team_a, d.team_b]).value_counts()
    keep = set(vc[vc >= a.min_games].index)
    ta = d.team_a.where(d.team_a.isin(keep), -1).to_numpy()
    tb = d.team_b.where(d.team_b.isin(keep), -1).to_numpy()
    teams = sorted(set(ta) | set(tb)); ti = {t: i for i, t in enumerate(teams)}
    maps = sorted(d.map_name.unique()); mi = {m: i for i, m in enumerate(maps)}
    n, T, M = len(d), len(teams), len(maps)
    rows = np.arange(n)
    X = sparse.csr_matrix(
        (np.r_[np.ones(n), -np.ones(n), np.ones(n)],
         (np.r_[rows, rows, rows], np.r_[[ti[t] for t in ta], [ti[t] for t in tb], T + d.map_name.map(mi).to_numpy()])),
        shape=(n, T + M))
    y = (d.winner == 'a').to_numpy().astype(int)
    lr = LogisticRegression(C=10.0, fit_intercept=False, max_iter=5000).fit(X, y)
    p_a = lr.predict_proba(X)[:, 1]
    s = dict(zip(teams, lr.coef_[0][:T]))
    side = dict(zip(maps, lr.coef_[0][T:]))
    d = d.assign(p_a=p_a)
    long = pd.concat([
        pd.DataFrame(dict(team=d.team_a, map=d.map_name, won=(d.winner == 'a').astype(int), p=d.p_a)),
        pd.DataFrame(dict(team=d.team_b, map=d.map_name, won=(d.winner == 'b').astype(int), p=1 - d.p_a))])
    strong = [t for t, _ in sorted(s.items(), key=lambda kv: -kv[1]) if t != -1 and t not in NAMES][:a.top]
    out = dict(games=int(n), ranked_only=not a.all_games, side_b_logit={m: -v for m, v in side.items()}, teams={})
    print(f"{n:,} games ({'ranked' if not a.all_games else 'all'}), {T} teams. Residual = (wins - expected)/games on "
          f"the map, in pp; * = |residual| > 2 SE.\n")
    hdr = 'team'.ljust(22) + 'str'.rjust(6) + ''.join(m[:8].rjust(10) for m in maps)
    print(hdr)
    for t in list(NAMES) + strong:
        if t not in s:
            continue
        g = long[long.team == t]
        cells, rec = [], {}
        for m in maps:
            x = g[g['map'] == m]
            if len(x) < 8:
                cells.append('-'.rjust(10)); continue
            r = (x.won.sum() - x.p.sum()) / len(x)
            se = np.sqrt((x.p * (1 - x.p)).sum()) / len(x)
            rec[m] = dict(n=int(len(x)), win=float(x.won.mean()), expected=float(x.p.mean()), resid=float(r), se=float(se))
            cells.append(f"{100 * r:+.0f}{'*' if abs(r) > 2 * se else ' '}({len(x)})".rjust(10))
        out['teams'][str(t)] = dict(name=NAMES.get(t, str(t)), strength=float(s[t]), maps=rec)
        print(NAMES.get(t, str(t))[:22].ljust(22) + f"{s[t]:6.2f}" + ''.join(cells))
    (ROOT / 'game_stats/runs' / f"tt-map-specialists{'-all' if a.all_games else ''}.json").write_text(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
