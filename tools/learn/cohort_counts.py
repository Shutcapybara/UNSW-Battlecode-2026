"""Label-free counts of a frozen cohort per teacher team (D-058 §C.4): games, series, teacher sides, teacher processes
and teacher dragon-turns, all processes and at the dataset's 15 % process sample. Reads only who took a turn (side,
dragon id) from each replay; no action, label, outcome or feature value is read into the output.
    python cohort_counts.py COHORT.parquet TEACHERS.parquet REPLAY_DIR OUT.json [PCT]"""
import collections, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd
import rebuild
import dataset as DS

coh, teach, rdir, out = sys.argv[1:5]
pct = int(sys.argv[5]) if len(sys.argv) > 5 else 15
C = pd.read_parquet(coh)
T = pd.read_parquet(teach)
rank = T.sort_values('started_at').groupby('team').agg(name=('name', 'last'), elo=('elo', 'last'), crank=('crank', 'last'))
per = collections.defaultdict(lambda: dict(games=set(), series=set(), sides=0, procs=0, turns=0, procs_s=0, turns_s=0,
                                            maps=collections.Counter()))
for r in C.itertuples():
    data = (Path(rdir) / f'{r.game}.replay').read_bytes()
    n = collections.Counter()
    team_of = {}
    rebuild.walk(data, lambda i, sp, txt, ctx: (n.__setitem__(i, n[i] + 1), team_of.__setitem__(i, sp['team'])))
    for s in r.teacher_sides.split(','):
        t = str(r.team_a if s == 'A' else r.team_b)
        d = per[t]
        d['games'].add(r.game); d['series'].add(r.series_key); d['sides'] += 1; d['maps'][r.map] += 1
        for i, c in n.items():
            if team_of[i] != s:
                continue
            d['procs'] += 1; d['turns'] += c
            if DS.keep(r.game, i, pct):
                d['procs_s'] += 1; d['turns_s'] += c
res = {}
for t, d in per.items():
    res[t] = dict(name=str(rank.name.get(int(t), rank.name.get(t, ''))) if len(rank) else '',
                  games=len(d['games']), series=len(d['series']), sides=d['sides'], processes=d['procs'],
                  dragon_turns=d['turns'], processes_pct=d['procs_s'], dragon_turns_pct=d['turns_s'], maps=dict(d['maps']))
tot = dict(games=len(C), series=C.series_key.nunique(), sides=sum(v['sides'] for v in res.values()),
           processes=sum(v['processes'] for v in res.values()), dragon_turns=sum(v['dragon_turns'] for v in res.values()),
           processes_pct=sum(v['processes_pct'] for v in res.values()),
           dragon_turns_pct=sum(v['dragon_turns_pct'] for v in res.values()))
Path(out).write_text(json.dumps(dict(pct=pct, total=tot, teams=res,
                                     rating=rank.reset_index().astype(str).to_dict('records')), indent=1, default=str))
print(json.dumps(tot))
