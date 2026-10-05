#!/usr/bin/env python3
"""Two pool totals (D-075 §F): templates only (the 272-fixture pool, as every card so far) and live-share weighted
(pool + the five hidden-bed variants of panel 'var').

Weights: each of the 17 live maps 1/17 of ranked games (assumption: the server draws maps uniformly; stated on every
output); within Devil, Queen of Spades, Slithery Fight, Schooltime and Dilemma the variant takes Kageyama's measured
share of all ranked post-m2 games (panel.VAR_SHARE) and the template the rest of that map's 1/17.
Paired by (seed, map, opp, seat); win = 1, draw = 0.5. Interval: stratified bootstrap, opponents resampled with
replacement within each map (or variant) stratum, 1,000 resamples, seed 7, linear 5th-95th. Missing fixtures listed,
never counted.

    python tools/asahi/vartotal.py CAND --parent PARENT [--seeds 1] [--out docs/learning/results/asahi/X-vartotal]
"""
import argparse, json, random, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/asahi'))
import panel as P  # noqa: E402


def outcomes(bot, pnl, seeds):
    root = P.run_root(bot, pnl)
    out = {}
    if not (root / 'index.jsonl').exists():
        return out
    for line in open(root / 'index.jsonl'):
        r = json.loads(line)
        if r.get('rc') != 0 or r['seed'] not in seeds:
            continue
        w = r.get('winner')
        out[(r['seed'], r['map'], r['opp'], r['seat'])] = 1.0 if w == r['seat'] else (0.0 if w in ('A', 'B') else 0.5)
    return out


def q(xs, p):
    xs = sorted(xs); x = p * (len(xs) - 1); i = int(x)
    return xs[i] + (xs[min(i + 1, len(xs) - 1)] - xs[i]) * (x - i)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('cand'); ap.add_argument('--parent', required=True)
    ap.add_argument('--seeds', default='1'); ap.add_argument('--out')
    a = ap.parse_args(); seeds = [int(s) for s in a.seeds.split(',')]
    exp, c, p = {}, {}, {}
    for pnl in ('pool', 'var'):
        for f in P.fixtures('X', pnl, seeds):
            exp[(f['seed'], f['map'], f['opp'], f['seat'])] = pnl
        c.update(outcomes(a.cand, pnl, seeds)); p.update(outcomes(a.parent, pnl, seeds))
    both = [k for k in exp if k in c and k in p]
    missing = sorted(set(exp) - set(both))
    base = 1.0 / len(P.POOL_MAPS)
    wmap = {m: base for m in P.POOL_MAPS}
    for v, sh in P.VAR_SHARE.items():
        wmap[v] = sh; wmap[P.VAR_BASE[v]] = base - sh
    strata = {}
    for k in both:
        strata.setdefault(k[1], {}).setdefault(k[2], []).append((c[k], p[k]))

    def total(maps, weights, draw=None):
        num = den = 0.0
        res = {}
        for m in maps:
            if m not in strata:
                continue
            opps = list(strata[m]); pick = opps if draw is None else [draw.choice(opps) for _ in opps]
            xs = [x for o in pick for x in strata[m][o]]
            dc = sum(x[0] for x in xs) / len(xs); dp = sum(x[1] for x in xs) / len(xs)
            w = weights[m]; num += w * (dc - dp); den += w
            res[m] = (dc, dp)
        return (100 * num / den if den else float("nan")), res

    rows = {}
    for name, maps, weights in (('templates only', P.POOL_MAPS, {m: 1.0 for m in P.POOL_MAPS}),
                                ('live-share weighted', P.POOL_MAPS + P.VAR_MAPS, wmap)):
        pt, per = total(maps, weights)
        rng = random.Random(7); bs = [total(maps, weights, rng)[0] for _ in range(1000)]
        wc = sum(weights[m] * per[m][0] for m in per) / sum(weights[m] for m in per)
        wp = sum(weights[m] * per[m][1] for m in per) / sum(weights[m] for m in per)
        rows[name] = dict(delta=pt, lo=q(bs, .05), hi=q(bs, .95), cand=wc, parent=wp)
    var_rows = {v: dict(n=sum(len(x) for x in strata.get(v, {}).values()), cand=total([v], {v: 1})[1].get(v, (None,))[0],
                        parent=total([v], {v: 1})[1].get(v, (None, None))[1]) for v in P.VAR_MAPS}
    L = [f'# {a.cand} vs {a.parent}: two pool totals (D-075 §F), seeds {seeds}', '',
         f'Paired fixtures {len(both)} of {len(exp)} (pool 272 + var 80 per seed); missing {len(missing)}.',
         'Weights: 17 live maps at 1/17 each (uniform map draw ASSUMED); variants at Kageyama\'s live shares of ranked '
         'post-m2 games, templates of those five maps the rest of 1/17. Stratified bootstrap (opponents within map), '
         '1,000 × seed 7, linear 5–95 %. Win rates per map averaged before weighting (templates-only total therefore '
         'equals the card\'s pool Δwin).', '',
         '| total | cand win | parent win | Δwin pp [90 %] |', '|---|---|---|---|']
    for k, r in rows.items():
        L.append(f"| {k} | {r['cand']:.4f} | {r['parent']:.4f} | {r['delta']:+.2f} [{r['lo']:+.2f}, {r['hi']:+.2f}] |")
    L += ['', '| variant | share | n | cand win | parent win |', '|---|---|---|---|---|']
    for v, r in var_rows.items():
        cw = '—' if r['cand'] is None else f"{r['cand']:.3f}"; pw = '—' if r['parent'] is None else f"{r['parent']:.3f}"
        L.append(f"| {v} | {P.VAR_SHARE[v]*100:.2f} % | {r['n']} | {cw} | {pw} |")
    if missing:
        L += ['', 'Missing (not counted): ' + ', '.join('/'.join(map(str, k)) for k in missing[:40])]
    txt = '\n'.join(L) + '\n'; print(txt)
    if a.out:
        Path(a.out).with_suffix('.md').write_text(txt)
        Path(a.out).with_suffix('.json').write_text(json.dumps(dict(rows=rows, variants=var_rows, missing=len(missing)), indent=1))


if __name__ == '__main__':
    main()
