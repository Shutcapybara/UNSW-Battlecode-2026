"""Judge runtime audit of our own team from public replays: per-turn instruction points and TLEs."""
import sys, json, glob, numpy as np, pandas as pd
sys.path.insert(0, 'tools'); import recon
m = pd.read_csv('out/corpus/manifest.csv', dtype={'game_id': str}); m = m[m.status == 'ok']
rows = []
for _, r in m.iterrows():
    g = recon.Game(f'corpus7/{r.game_id}.replay'); pts = []; tle = [0]
    def cb(kind, **k):
        if kind == 'action' and k['dragon'].team == r.side:
            if k['points'] is not None: pts.append(k['points'])
            if k['tle']: tle[0] += 1
    g.run(cb)
    p = np.array(pts) if pts else np.array([0])
    rows.append(dict(game=r.game_id, sub=int(r.target_submission), map=r.map_name, result=r.result, turns=len(pts), tle=tle[0],
                     p50=int(np.median(p)), p99=int(np.percentile(p, 99)), pmax=int(p.max()), share_over_80M=float((p > 80e6).mean()),
                     share_over_95M=float((p > 95e6).mean())))
D = pd.DataFrame(rows); D.to_csv('out/agg/runtime_audit.csv', index=False)
S = D.groupby('sub').agg(games=('game', 'size'), tle_games=('tle', lambda s: int((s > 0).sum())), tle_total=('tle', 'sum'),
                         p50=('p50', 'median'), p99=('p99', 'median'), pmax=('pmax', 'max'), over80=('share_over_80M', 'mean'))
print(S.to_string())
print(D[D.tle > 0].groupby(['sub', 'result']).size())
