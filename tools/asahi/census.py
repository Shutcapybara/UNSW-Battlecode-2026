#!/usr/bin/env python3
"""Discordance census (D-056 §D.2, D-057 §D amendment 2): for each candidate against the parent on seed-matched
fixtures (seed, map, opponent, seat), per map: candidate better / worse / tied (outcome for our side: win 1, draw 0.5,
loss 0), the share of pairs whose outcome differs (switch discordance), and the share whose game differs at all
(winner or round count). Beside it, the parent's own seed noise: the same fixture at seed s against seed s' (all seed
pairs available), share of outcome-different pairs. Reads only run indexes (rc 0 rows).

    python tools/asahi/census.py --parent carthage-05-free-sprint --cands asahi-05-kz12-k16,asahi-07-hkz26-m0 \
        [--panel pool] --out docs/learning/results/asahi/census
"""
import argparse, itertools, json, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/asahi'))
import panel as P  # noqa: E402


def rows(bot, panel):
    root = P.run_root(bot, panel)
    out = {}
    for line in open(root / 'index.jsonl'):
        r = json.loads(line)
        if r.get('rc') != 0:
            continue
        seat = 'A' if r['botA'] == bot else 'B'
        opp = r['botB'] if seat == 'A' else r['botA']
        w = r.get('winner')
        score = 0.5 if w in ('draw', None) else 1.0 if w == seat else 0.0
        out[(r['seed'], r['map'], opp, seat)] = (score, r.get('winner'), r.get('rounds'))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--parent', required=True); ap.add_argument('--cands', required=True)
    ap.add_argument('--panel', default='pool'); ap.add_argument('--out', required=True)
    a = ap.parse_args()
    par = rows(a.parent, a.panel)
    res = {'panel': a.panel, 'parent': a.parent, 'cands': {}}
    L = [f'# Discordance census — {a.panel} panel, parent `{a.parent}`\n',
         'Seed-matched pairs (seed, map, opponent, seat). better / worse / tied = candidate outcome vs parent; '
         'disc = share of pairs with a different outcome; game≠ = share with a different winner or round count. '
         "Parent seed noise = the parent's own outcome differences between seeds s and s' on the same fixture.\n"]
    # parent seed noise
    by = defaultdict(dict)
    for (s, m, o, t), v in par.items():
        by[(m, o, t)][s] = v
    noise = defaultdict(lambda: [0, 0])
    for (m, o, t), d in by.items():
        for s1, s2 in itertools.combinations(sorted(d), 2):
            noise[m][0] += 1; noise[m][1] += d[s1][0] != d[s2][0]
    seeds_p = sorted({k[0] for k in par})
    for cand in a.cands.split(','):
        c = rows(cand, a.panel)
        keys = sorted(set(c) & set(par))
        tab = defaultdict(lambda: [0, 0, 0, 0, 0])   # better, worse, tied, outcome-diff, game-diff
        for k in keys:
            m = k[1]; cs, cw, cr = c[k]; ps, pw, pr = par[k]
            t = tab[m]
            t[0] += cs > ps; t[1] += cs < ps; t[2] += cs == ps; t[3] += cs != ps; t[4] += (cw, cr) != (pw, pr)
        seeds = sorted({k[0] for k in keys})
        res['cands'][cand] = dict(seeds=seeds, pairs=len(keys), by_map={m: v for m, v in tab.items()})
        L.append(f'## `{cand}` — seeds {seeds}, {len(keys)} pairs\n')
        L.append("| map | pairs | better | worse | tied | disc | game≠ | parent seed noise (pairs, disc) |\n|---|---|---|---|---|---|---|---|")
        tot = [0] * 5
        for m in sorted(tab):
            t = tab[m]; n = t[0] + t[1] + t[2]; tot = [x + y for x, y in zip(tot, t)]
            nz = noise.get(m, [0, 0])
            L.append(f"| {m} | {n} | {t[0]} | {t[1]} | {t[2]} | {t[3] / n:.3f} | {t[4] / n:.3f} | "
                     f"{nz[0]}, {nz[1] / nz[0]:.3f} |" if nz[0] else f"| {m} | {n} | {t[0]} | {t[1]} | {t[2]} | {t[3] / n:.3f} | {t[4] / n:.3f} | — |")
        n = tot[0] + tot[1] + tot[2]
        allnoise = [sum(v[0] for v in noise.values()), sum(v[1] for v in noise.values())]
        L.append(f"| **all** | {n} | {tot[0]} | {tot[1]} | {tot[2]} | {tot[3] / max(1, n):.3f} | {tot[4] / max(1, n):.3f} | "
                 f"{allnoise[0]}, {allnoise[1] / max(1, allnoise[0]):.3f} |\n")
    res['parent_seed_noise'] = {m: v for m, v in noise.items()}
    res['parent_seeds'] = seeds_p
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix('.json').write_text(json.dumps(res, indent=1))
    out.with_suffix('.md').write_text('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
