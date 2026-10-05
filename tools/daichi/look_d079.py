"""Trial look breakdowns: per window score-E@1725 by opponent band and Schooltime split, per-map W/n. Writes ids file."""
import sys, numpy as np
from datetime import datetime, timedelta, timezone
from pathlib import Path
sys.path.insert(0, 'build/daichi/tree/tools/daichi')
import live_monitor as lm
from trial_d075 import iso
since = datetime.now(timezone.utc) - timedelta(days=14)
L = lm.load_ladders(Path('public_replays/corpus/ladder'), since - timedelta(hours=2)); K = [t for t, _ in L]
allg = sorted([g for g in lm.own_games(Path('public_replays/corpus/index.jsonl'), since) if g['ranked']], key=lambda g: g['at'])
def win(sid, frm, n):
    gs = [g for g in allg if g['bot'] == sid and (not frm or g['at'] >= iso(frm))]
    ids, k = [], 0
    for g in gs:
        if not ids or ids[-1] != g['series']:
            if k >= n: break
            ids.append(g['series'])
        k += 1
    out = []
    for g in gs:
        if g['series'] in ids:
            ro = lm.rating_at(L, K, g['at'], g['opp'])
            if ro is not None: g = dict(g, ro=ro, r=g['score'] - 1/(1+10**((ro-1725)/400))); out.append(g)
    return out
def bs(gs):
    if not gs: return 'n 0'
    by = {}
    for g in gs: by.setdefault(g['series'], []).append(g['r'])
    S = list(by.values()); rng = np.random.default_rng(7); v = []
    for _ in range(1000):
        p = [S[i] for i in rng.integers(0, len(S), len(S))]; v.append(sum(map(sum, p)) / sum(map(len, p)))
    w = sum(g['score'] for g in gs)
    return f"n {len(gs)}/{len(S)} ser, W {w:g}, {np.mean([g['r'] for g in gs]):+.3f} [{np.percentile(v,5):+.3f}, {np.percentile(v,95):+.3f}]"
for sid, frm in (('17388', None), ('17530', '2026-10-05T08:15:41Z')):
    gs = win(sid, frm, 60)
    Path(f'build/daichi/tmp/ids{sid}_60.txt').write_text(' '.join(str(g['game_id']) for g in gs))
    print(f'== {sid}: all {bs(gs)}')
    print('  opp >=1725:', bs([g for g in gs if g['ro'] >= 1725]), '| <1725:', bs([g for g in gs if g['ro'] < 1725]))
    st = [g for g in gs if 'chool' in (g['map'] or '')]
    print('  Schooltime:', bs(st), '| rest:', bs([g for g in gs if g not in st]))
    print('  opps:', sorted({(g['opp'], round(g['ro'])) for g in gs}))
    m = {}
    for g in gs: m.setdefault(g['map'], []).append(g['score'])
    print('  maps:', ', '.join(f"{k} {sum(v):g}/{len(v)}" for k, v in sorted(m.items(), key=lambda kv: sum(kv[1])/len(kv[1]))))
