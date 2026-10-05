"""P-hinata-06 standing column (D-080 §A): matched loss-rate gap of a trial sub vs 14585 re-weighted to the trial's opponents.
Index-only (winner field). Usage: python3 tools/hinata/p06_column.py TRIAL_SUB START_ISO [N_MIN=60] [--parity]"""
import json, sys, bisect, collections, random, statistics as st
from pathlib import Path
REF = '14585'; MAP_SWITCH = '2026-10-02T03:49:00'
args = [a for a in sys.argv[1:] if not a.startswith('--')]
T, START = args[0], args[1]; NMIN = int(args[2]) if len(args) > 2 else 60
games = []
for l in open('public_replays/corpus/index.jsonl'):
    if '"team_a": 7,' not in l and '"team_b": 7,' not in l: continue
    r = json.loads(l)
    if not (r.get('ranked') and r.get('status') == 'completed' and (r.get('started_at') or '') >= MAP_SWITCH): continue
    us = 'a' if r['team_a'] == 7 else 'b'; sub = str(r['bot_a'] if us == 'a' else r['bot_b'])
    if sub not in (T, REF): continue
    w = r.get('winner'); lost = int(w in ('a', 'b') and w != us)
    games.append(dict(gid=r['game_id'], series=r['series_id'], start=r['started_at'], sub=sub, map=r['map_name'],
                      opp=r['team_b'] if us == 'a' else r['team_a'], lost=lost, won=int(w == us)))
games = list({g['gid']: g for g in games}.values()); games.sort(key=lambda g: (g['start'], g['gid']))
tr_all = [g for g in games if g['sub'] == T and g['start'] >= START]
# cut at the first series boundary at or after NMIN games
tr, seen = [], []
for g in tr_all:
    if g['series'] not in seen:
        if len(tr) >= NMIN: break
        seen.append(g['series'])
    tr.append(g)
tr = [g for g in tr_all if g['series'] in seen]
complete = len(tr) >= NMIN
snaps = sorted(Path('public_replays/corpus/ladder').glob('*.json')); keys = [p.stem for p in snaps]; cache = {}
def elo(g):
    k = g['start'][:19].replace('-', '').replace(':', '') + 'Z'; i = bisect.bisect_right(keys, k) - 1
    if i < 0: return None
    if i not in cache: cache[i] = {t['id']: t['elo'] for t in json.load(open(snaps[i]))}
    return cache[i].get(g['opp'])
for g in tr: g['opp_elo'] = elo(g)
eo = collections.defaultdict(list)
for g in tr:
    if g['opp_elo'] is not None: eo[g['opp']].append(g['opp_elo'])
band_of = {o: ('hi' if st.median(v) >= 1725 else 'lo') for o, v in eo.items()}
for g in tr: band_of.setdefault(g['opp'], 'lo')
topp = {g['opp'] for g in tr}
rf = [g for g in games if g['sub'] == REF and g['opp'] in topp]
def gap(tr, rf):
    ref_by = collections.defaultdict(list)
    for r in rf: ref_by[r['opp']].append(r['lost'])
    out = {}
    for band in ('hi', 'lo', 'all'):
        t = [r for r in tr if r['opp'] in ref_by and (band == 'all' or band_of[r['opp']] == band)]
        out[band] = (None, 0) if not t else (sum(r['lost'] for r in t) / len(t) - sum(st.mean(ref_by[r['opp']]) for r in t) / len(t), len(t))
    return out
def boot(rs, rng):
    s = collections.defaultdict(list)
    for r in rs: s[r['series']].append(r)
    k = list(s); return [r for _ in k for r in s[rng.choice(k)]]
def ci(v):
    v = sorted(v); n = len(v)
    def q(p):
        x = p * (n - 1); i = int(x); return v[i] + (v[min(n - 1, i + 1)] - v[i]) * (x - i)
    return [round(q(.05), 3), round(q(.95), 3)]
pt = gap(tr, rf); rng = random.Random(7); bs = collections.defaultdict(list)
for _ in range(1000):
    for b, (v, n) in gap(boot(tr, rng), boot(rf, rng)).items():
        if v is not None: bs[b].append(v)
lr = lambda X: f"{sum(r['lost'] for r in X)}/{len(X)}"
res = dict(trial=T, start=START, window_complete=complete, trial_games=len(tr), trial_series=len(seen),
           window=[tr[0]['start'], tr[-1]['start']] if tr else None, trial_WL=f"{sum(g['won'] for g in tr)}-{sum(g['lost'] for g in tr)}",
           opps=len(topp), matched_opps=len({r['opp'] for r in rf}), ref_games=len(rf),
           band_counts={b: sum(1 for g in tr if band_of[g['opp']] == b) for b in ('hi', 'lo')},
           loss_trial={b: lr([g for g in tr if b == 'all' or band_of[g['opp']] == b]) for b in ('hi', 'lo', 'all')},
           gap={b: dict(gap=None if v is None else round(v, 3), n_trial=n, ci90=ci(bs[b]) if bs[b] else None) for b, (v, n) in pt.items()},
           per_opp={str(o): dict(band=band_of[o], elo=round(st.median(eo[o])) if eo[o] else None, trial=lr([g for g in tr if g['opp'] == o]),
                                 ref=lr([g for g in rf if g['opp'] == o])) for o in sorted(topp)},
           gids=[g['gid'] for g in tr])
print(json.dumps({k: v for k, v in res.items() if k != 'gids'}, indent=1))
out = Path('build/hinata/col'); out.mkdir(parents=True, exist_ok=True)
json.dump(res, open(out / f'col-{T}-{START[:16].replace(":", "")}.json', 'w'), indent=1)
