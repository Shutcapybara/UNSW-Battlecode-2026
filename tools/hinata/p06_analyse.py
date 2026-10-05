"""P-hinata-06 stage 2: matched loss-rate gap (trial sub vs re-weighted 14585) by opponent band + per-quantity tables."""
import csv, random, statistics as st, collections, json
from pathlib import Path
OUT = Path('build/hinata/p06')
rows = [r for q in sorted(OUT.glob('rows*.csv')) for r in csv.DictReader(open(q)) if r['reason'] not in ('MISSING', 'DECODE_ERR', '')]
for r in rows:
    r['won'] = int(r['won']); r['lost'] = 1 - r['won'] if r['reason'] != 'tie' else 0
    r['opp_elo'] = float(r['opp_elo']) if r['opp_elo'] else None
REF = '14585'; TRIALS = ['16979', '17388', '17530']
by = collections.defaultdict(list)
for r in rows: by[r['sub']].append(r)
print('n games', {k: len(v) for k, v in by.items()}, ' decoded rows', len(rows))
def gap(T, tr, rf, band_of):
    """loss rate T minus 14585 re-weighted to T's opponent counts, per band; only opponents present in both."""
    ref_by = collections.defaultdict(list)
    for r in rf: ref_by[r['opp']].append(r['lost'])
    out = {}
    for band in ('hi', 'lo', 'all'):
        t = [r for r in tr if r['opp'] in ref_by and (band == 'all' or band_of[r['opp']] == band)]
        if not t: out[band] = (None, 0); continue
        lt = sum(r['lost'] for r in t) / len(t)
        lr = sum(st.mean(ref_by[r['opp']]) for r in t) / len(t)
        out[band] = (lt - lr, len(t))
    return out
def series_boot(rs, rng):
    s = collections.defaultdict(list)
    for r in rs: s[r['series']].append(r)
    keys = list(s); return [r for _ in keys for r in s[rng.choice(keys)]]
res = {}
for T in TRIALS:
    tr, rf = by[T], by[REF]
    elo = collections.defaultdict(list)
    for r in tr:
        if r['opp_elo'] is not None: elo[r['opp']].append(r['opp_elo'])
    band_of = {o: ('hi' if st.median(v) >= 1725 else 'lo') for o, v in elo.items()}
    for r in tr: band_of.setdefault(r['opp'], 'lo')
    pt = gap(T, tr, rf, band_of)
    rng = random.Random(7); bs = collections.defaultdict(list)
    for _ in range(1000):
        g = gap(T, series_boot(tr, rng), series_boot(rf, rng), band_of)
        for b, (v, n) in g.items():
            if v is not None: bs[b].append(v)
    def ci(v):
        v = sorted(v); n = len(v)
        q = lambda p: v[int(p * (n - 1))] + (v[min(n - 1, int(p * (n - 1)) + 1)] - v[int(p * (n - 1))]) * (p * (n - 1) - int(p * (n - 1)))
        return (round(q(.05), 3), round(q(.95), 3))
    matched_opps = sorted({r['opp'] for r in tr} & {r['opp'] for r in rf})
    nref = sum(1 for r in rf if r['opp'] in set(matched_opps))
    res[T] = {b: dict(gap=None if v is None else round(v, 3), n_trial=n, ci90=ci(bs[b]) if bs[b] else None) for b, (v, n) in pt.items()}
    res[T]['matched_opps'] = len(matched_opps); res[T]['ref_games_on_matched'] = nref
    res[T]['trial_games'] = len(tr); res[T]['trial_series'] = len({r['series'] for r in tr})
    print(T, json.dumps(res[T]))
Q = ['q_us', 'q_them', 'L_us', 'L_them', 'u100_us', 'u100_them', 'len100_us', 'len100_them', 'lng100_us', 'lng100_them', 'last_round']
print('\nper sub: loss rate | share of losses by reason | queen alive at end (wins, losses) | means in losses')
tab = {}
for S in [REF] + TRIALS:
    rs = by[S] if S != REF else [r for r in by[REF] if r['opp'] in {x['opp'] for T in TRIALS for x in by[T]}]
    L = [r for r in rs if r['lost']]; W = [r for r in rs if r['won']]
    rc = collections.Counter(r['reason'] for r in L)
    qa = lambda X: round(sum(int(r['q_us']) > 0 for r in X) / max(1, len(X)), 2)
    hi = [r for r in rs if r['opp_elo'] and r['opp_elo'] >= 1725]; lo = [r for r in rs if r['opp_elo'] and r['opp_elo'] < 1725]
    lr = lambda X: f"{sum(r['lost'] for r in X)}/{len(X)}"
    tab[S] = dict(n=len(rs), loss=lr(rs), loss_hi=lr(hi), loss_lo=lr(lo), reasons_in_losses=dict(rc), queen_alive_win=qa(W), queen_alive_loss=qa(L),
                  loss_means={q: round(st.mean(float(r[q]) for r in L), 1) for q in Q} if L else {},
                  win_means={q: round(st.mean(float(r[q]) for r in W), 1) for q in Q} if W else {})
    print(S, json.dumps(tab[S]))
mp = collections.defaultdict(lambda: collections.Counter())
for S in [REF] + TRIALS:
    for r in (by[S] if S != REF else [r for r in by[REF] if r['opp'] in {x['opp'] for T in TRIALS for x in by[T]}]):
        mp[r['map']][S + ('L' if r['lost'] else 'n')] += 1
print('\nmaps (L = losses, n = not lost):')
for m, c in sorted(mp.items()):
    print(f"{m[:18]:18s}", ' '.join(f"{S}:{c[S+'L']}/{c[S+'L']+c[S+'n']}" for S in [REF] + TRIALS))
json.dump(dict(gap=res, tables=tab), open(OUT / 'result.json', 'w'), indent=1)
