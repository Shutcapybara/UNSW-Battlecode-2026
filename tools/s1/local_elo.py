"""Local Elo: one Bradley-Terry rating for every local bot with enough games, from every local result we hold.

  python3 tools/s1/local_elo.py      -> build/s1/out/local_elo/{games.parquet, ratings.csv}

Sources (deduplicated within each):
  experiment_data results (build/atlas/local_results.parquet, 24-28 Sep, 133k games, many maps)
  atlas overnight panel   (build/atlas/panel/index.jsonl, 30 Sep-1 Oct, 20k games, 10 ladder maps, seed 1)
  renoir / ra runs        (build/ra/runs/*/*/index*.jsonl)
  expedition panels       (build/expedition/replay-panels/*/*/rows.jsonl)
  crown-graft run         (build/s1/tmp/graft/graft_index.jsonl)
Model: P(A beats B) = 1 / (1 + 10^((R_B - R_A)/400)), draws count half, ridge prior (each bot plays 2 virtual draws
against the pool mean), mean of rated bots = 1500. SE from the diagonal of the Hessian (ignores covariance: slightly
optimistic for bots whose opponents are themselves poorly rated). Rated: >= 30 games and >= 5 distinct opponents.
Two fits: all maps, and the 10 ladder maps only. Bot date = first git add of bots/<name> or first game, whichever is
earlier.
"""
import glob, json, os, re, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
os.chdir(ROOT); sys.path.insert(0, str(ROOT))
if sys.platform.startswith('linux') and (ROOT / 'build' / 's1-pylib').exists():
    sys.path.append(str(ROOT / 'build' / 's1-pylib'))
import numpy as np
import pandas as pd

OUT = ROOT / 'build' / 's1' / 'out' / 'local_elo'
LADDER = {'schooltime', 'portals', 'slithery_fight', 'queen_of_spades', 'default', 'trophy', 'dilemma', 'autarky', 'devil', 'trauma'}
MIN_GAMES, MIN_OPPS = 30, 5


def norm_map(m):
    m = str(m).replace('maps/', '').replace('.map', '')
    return m.split('/')[-1].lower()


def load():
    rows = []
    r = pd.read_parquet(ROOT / 'build' / 'atlas' / 'local_results.parquet')
    s = r.outcome.map({'A': 1.0, 'B': 0.0, 'draw': 0.5})
    rows.append(pd.DataFrame(dict(a=r.bot_a, b=r.bot_b, s=s, map=r['map'].map(norm_map),
                                  t=pd.to_datetime(r.run_started_at, utc=True), src='experiment')))
    def jl(paths, src, conv):
        seen, out = set(), []
        for p in paths:
            for line in open(p):
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                x = conv(d, p)
                if x and x[-1] not in seen:
                    seen.add(x[-1]); out.append(x[:-1])
        return pd.DataFrame(out, columns=['a', 'b', 's', 'map']).assign(src=src, t=pd.NaT)
    W = {'A': 1.0, 'B': 0.0, 'D': 0.5, 'draw': 0.5}
    rows.append(jl([ROOT / 'build/atlas/panel/index.jsonl'], 'panel',
                   lambda d, p: (d['a'], d['b'], W.get(d['winner']), norm_map(d['map']), d['game']) if d.get('rc') == 0 else None))
    rows.append(jl(sorted(glob.glob('build/ra/runs/*/*/index*.jsonl')), 'ra',
                   lambda d, p: (d['botA'], d['botB'], W.get(d.get('winner')), norm_map(d['map']), (Path(p).parent.parent.name, d['panel'], d['game']))
                   if d.get('rc') == 0 and d.get('winner') in W else None))
    def ex(d, p):
        res = {'win': 1.0, 'loss': 0.0, 'draw': 0.5}.get(d.get('result'))
        if res is None:
            return None
        c = Path(d['cand']).name
        a, b, s = (c, d['opp'], res) if d['side'] == 'A' else (d['opp'], c, 1 - res)
        return (a, b, s, norm_map(d['map']), (c, d['opp'], d['map'], d['side'], d.get('seed')))
    rows.append(jl(sorted(glob.glob('build/expedition/replay-panels/*/*/rows.jsonl')), 'expedition', ex))
    rows.append(jl([ROOT / 'build/s1/tmp/graft/graft_index.jsonl'], 'graft',
                   lambda d, p: (d['a'], d['b'], W.get(d['winner']), norm_map(d['map']), d['game'])
                   if d.get('rc') == 0 and 'hb1-04-deployable' not in (d['a'], d['b']) else None))
    g = pd.concat(rows, ignore_index=True).dropna(subset=['s'])
    g = g[g.a != g.b]
    return g


def eligible(g):
    keep = set(pd.concat([g.a, g.b]).unique())
    while True:
        h = g[g.a.isin(keep) & g.b.isin(keep)]
        cnt = pd.concat([h.a, h.b]).value_counts()
        opp = pd.concat([h[['a', 'b']].rename(columns={'a': 'x', 'b': 'y'}), h[['b', 'a']].rename(columns={'b': 'x', 'a': 'y'})]).groupby('x').y.nunique()
        new = set(cnt[cnt >= MIN_GAMES].index) & set(opp[opp >= MIN_OPPS].index)
        if new == keep:
            return h, sorted(keep)
        keep = new


def fit(h, bots, prior=2.0, iters=300):
    idx = {b: i for i, b in enumerate(bots)}
    ia, ib, s = h.a.map(idx).values, h.b.map(idx).values, h.s.values.astype(float)
    n = len(bots)
    th = np.zeros(n)
    k = np.log(10) / 400
    from scipy.optimize import minimize
    def f(x):
        d = x[ia] - x[ib]
        p = 1 / (1 + np.exp(-k * d))
        ll = s * np.log(p + 1e-12) + (1 - s) * np.log(1 - p + 1e-12)
        g = np.zeros(n)
        r = k * (s - p)
        np.add.at(g, ia, r); np.add.at(g, ib, -r)
        # prior: 'prior' virtual draws against the pool mean (rating 0)
        pp = 1 / (1 + np.exp(-k * x))
        llp = prior * (0.5 * np.log(pp) + 0.5 * np.log(1 - pp))
        gp = prior * k * (0.5 - pp)
        return -(ll.sum() + llp.sum()), -(g + gp)
    res = minimize(f, th, jac=True, method='L-BFGS-B', options=dict(maxiter=iters))
    x = res.x
    d = x[ia] - x[ib]; p = 1 / (1 + np.exp(-k * d)); w = k * k * p * (1 - p)
    H = np.zeros(n); np.add.at(H, ia, w); np.add.at(H, ib, w)
    pp = 1 / (1 + np.exp(-k * x)); H += prior * k * k * pp * (1 - pp)
    se = 1 / np.sqrt(H)
    x = x - x.mean() + 1500
    cnt = pd.concat([h.a, h.b]).value_counts()
    opp = pd.concat([h[['a', 'b']].rename(columns={'a': 'x', 'b': 'y'}), h[['b', 'a']].rename(columns={'b': 'x', 'a': 'y'})]).groupby('x').y.nunique()
    sc = pd.concat([h.groupby('a').s.sum(), (1 - h.s).groupby(h.b).sum()], axis=1).sum(axis=1)
    return pd.DataFrame(dict(elo=x, se=se, games=cnt.reindex(bots).values, opps=opp.reindex(bots).values,
                             score=(sc.reindex(bots) / cnt.reindex(bots)).values), index=bots)


def dates(g):
    p = subprocess.run(['git', 'log', 'HEAD', '--diff-filter=A', '--name-only', '--format=@@%aI', '--', 'bots'],
                       capture_output=True, text=True).stdout
    first, d = {}, None
    for line in p.splitlines():
        if line.startswith('@@'):
            d = line[2:]
        elif line.startswith('bots/') and d:
            b = line.split('/')[1]
            t = pd.Timestamp(d).tz_convert('UTC')
            if b not in first or t < first[b]:
                first[b] = t
    seen = pd.concat([g[['a', 't']].rename(columns={'a': 'bot'}), g[['b', 't']].rename(columns={'b': 'bot'})]).dropna().groupby('bot').t.min()
    return pd.Series(first), seen


def author(b):
    for f in ('CANDIDATE.toml', 'bot.toml'):
        p = ROOT / 'bots' / b / f
        if p.exists():
            m = re.search(r'author\s*=\s*"([^"]+)"', p.read_text(errors='ignore'))
            if m:
                return m.group(1)
    return ''


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    g = load()
    g.drop(columns=['t']).assign(t=g.t.astype(str)).to_parquet(OUT / 'games.parquet')
    print('games by source:', g.src.value_counts().to_dict(), 'bots', pd.concat([g.a, g.b]).nunique())
    h, bots = eligible(g)
    A = fit(h, bots)
    hl, botsl = eligible(g[g['map'].isin(LADDER)])
    Lr = fit(hl, botsl).add_suffix('_ladder')
    R = A.join(Lr, how='outer')
    gd, seen = dates(g)
    R['git_date'] = gd.reindex(R.index)
    R['first_game'] = seen.reindex(R.index)
    mt = {}
    for b in R.index:
        fs = [f for f in (ROOT / 'bots' / b).glob('*') if f.is_file()] if (ROOT / 'bots' / b).is_dir() else []
        if fs:
            mt[b] = pd.Timestamp(min(f.stat().st_mtime for f in fs), unit='s', tz='UTC')
    R['file_date'] = pd.Series(mt).reindex(R.index)
    R['date'] = R[['git_date', 'first_game']].min(axis=1).fillna(R['file_date'])
    R['lane'] = [b.split('-')[0] for b in R.index]
    R['author'] = [author(b) for b in R.index]
    srcs = pd.concat([g[['a', 'src']].rename(columns={'a': 'bot'}), g[['b', 'src']].rename(columns={'b': 'bot'})]).groupby('bot').src.agg(lambda s: ','.join(sorted(set(s))))
    R['sources'] = srcs.reindex(R.index)
    R.index.name = 'bot'
    R.sort_values('elo', ascending=False).to_csv(OUT / 'ratings.csv')
    print(f'rated: all maps {A.shape[0]} bots on {len(h)} games; ladder maps {Lr.shape[0]} bots on {len(hl)} games')
    print('elo all vs ladder spearman: %.3f' % R[['elo', 'elo_ladder']].dropna().corr(method='spearman').iloc[0, 1])
    print(R.sort_values('elo', ascending=False)[['elo', 'se', 'games', 'elo_ladder', 'se_ladder', 'games_ladder', 'date']].head(25).round(0).to_string())


if __name__ == '__main__':
    main()
