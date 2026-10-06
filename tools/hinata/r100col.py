"""r100 total column (Sugawara D-091B ask): our total length at r100, opponents >= 1725, all games that reached r100
(not only those reaching r300). Series bootstrap 1,000 x seed 7, 5-95 %.
Usage: python3 tools/hinata/r100col.py DIR POP [REFDIR REFPOP]"""
import json, glob, random, sys, collections
def load(d): return [json.loads(l) for f in sorted(glob.glob(d + '/g_s*.jsonl')) for l in open(f)]
def sel(d):
    try: return {g['gid'] for g in json.load(open(d + '/sel.json'))['games']}
    except Exception: return None
def rows(d, pop):
    G, S = load(d), sel(d); out = collections.defaultdict(list)
    for g in G:
        if 'err' in g or g.get('pop') != pop or (S is not None and g['gid'] not in S): continue
        s = g['us']; th = 'B' if s == 'A' else 'A'; e = g['elo_' + th.lower()]
        if e is None or e < 1725: continue
        c = g['c' + s]
        if '100' not in c: continue
        out[g['series']].append(c['100'][1])
    return out
def mean(S): xs = [x for v in S.values() for x in v]; return sum(xs) / len(xs), len(xs), len(S)
def boot(S, rng):
    k = list(S); xs = [x for kk in (rng.choice(k) for _ in k) for x in S[kk]]; return sum(xs) / len(xs)
def ci(S):
    rng = random.Random(7); b = sorted(boot(S, rng) for _ in range(1000)); return b[49], b[949]
def gap(S, R):
    rng = random.Random(7); b = sorted(boot(S, rng) - boot(R, rng) for _ in range(1000)); return b[49], b[949]
a = sys.argv[1:]; S = rows(a[0], a[1]); m, n, s = mean(S); lo, hi = ci(S)
print(f"{a[1]} >=1725 r100 total (games reaching r100): {m:.1f} [{lo:.1f},{hi:.1f}] n {n}/{s} series")
if len(a) >= 4:
    R = rows(a[2], a[3]); mr, nr, sr = mean(R); glo, ghi = gap(S, R)
    print(f"  ref {a[3]}: {mr:.1f} n {nr}/{sr}; diff {m-mr:+.1f} [{glo:+.1f},{ghi:+.1f}]")
