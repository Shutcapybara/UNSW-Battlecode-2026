"""Per-game growth r100->r300 on games that reached r300 (P-hinata-07 pre-registration, 2026-10-05).
Usage: python3 tools/hinata/growth_pg.py  -> prints 17791 / 17530 (opp >= 1725) and top-ten winners."""
import json, glob, random, collections
def load(d): return [json.loads(l) for f in sorted(glob.glob(d + '/g_s*.jsonl')) for l in open(f)]
def rows(G, pop):
    out = collections.defaultdict(list)
    for g in G:
        if 'err' in g or g.get('pop') != pop or g['last_round'] < 300: continue
        if pop == 'top10':
            s = g['winner']
            if s not in ('A', 'B'): continue
        else:
            s = g['us']; th = 'B' if s == 'A' else 'A'; e = g['elo_' + th.lower()]
            if e is None or e < 1725: continue
        c = g['c' + s]
        if '100' not in c or '300' not in c: continue
        out[g['series']].append(c['300'][1] - c['100'][1])
    return out
def mean(S): xs = [x for v in S.values() for x in v]; return sum(xs) / len(xs), len(xs), len(S)
def boot(S, rng):
    k = list(S); xs = [x for kk in (rng.choice(k) for _ in k) for x in S[kk]]; return sum(xs) / len(xs)
def ci(S):
    rng = random.Random(7); b = sorted(boot(S, rng) for _ in range(1000)); return b[49], b[949]
def gap(S, R):
    rng = random.Random(7); b = sorted(boot(S, rng) - boot(R, rng) for _ in range(1000)); return b[49], b[949]
L3 = load('build/hinata/look3'); C2 = load('build/hinata/curves2')
T = rows(C2, 'top10'); m, n, s = mean(T); lo, hi = ci(T)
print(f"top10 winners: growth {m:.1f} [{lo:.1f},{hi:.1f}] n {n}/{s} series")
for name, S in (('17791', rows(L3, '17791')), ('17530', rows(C2, '17530'))):
    m2, n2, s2 = mean(S); lo, hi = ci(S); glo, ghi = gap(S, T)
    print(f"{name} >=1725: growth {m2:.1f} [{lo:.1f},{hi:.1f}] n {n2}/{s2} series; gap vs top10 winners {m2-m:+.1f} [{glo:+.1f},{ghi:+.1f}]")
