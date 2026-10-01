"""TT: endgame gate - paired win difference for changes that act after the opening (feeding, conversion, crown).

    .venv/bin/python tools/tt/endgame_gate.py --cand DIR [DIR ...] --parent DIR [DIR ...] [--material]

Why a separate gate. The scorecard gate (BENCHMARKS step 4) is decided by the economy curve up to r250, counts chosen
deaths (culls) as hygiene failures and compares unpaired win shares; tempo covers r10-150. A change that only acts
from ~r300 leaves all of those unchanged or misread. This gate pairs games on the fixture (seed, map, opponent, seat;
bot names stripped from s<seed>__<map>__<A>__<B>), so the opening is shared, and reports:
  - win difference (candidate - parent) with a 95 % bootstrap CI over fixtures, overall, per regime and per map;
  - per arm: round-limit record and elimination losses (feeding exposes dragons), and with --material the round-limit
    losses with a material lead (conversion failures) and the median longest dragon at the end (replay decode).
Regimes (tools/tt/map_mechanism.py, ladder end mix): elimination maps vs round-limit maps; maps outside both are 'other'.
Verdict (same vocabulary as tempo; maps weighted by their paired games):
  ACCEPT        CI entirely above 0, and no regime's own CI entirely below 0
  REJECT        CI entirely below 0
  NO GAIN       CI excludes a gain of +2 pp (upper bound < +2 pp)
  INCONCLUSIVE  anything else (add seeds, preferably on the maps where the change acts)
"""
import argparse, glob, json, re, sys
from multiprocessing import Pool
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
ELIM = {'trophy', 'devil', 'queen_of_spades', 'dilemma', 'default', 'autarky'}
LIMIT = {'schooltime', 'trauma', 'slithery_fight', 'portals'}


def load(dirs):
    rows = []
    for d in dirs:
        idx = Path(d) / 'index.jsonl'
        x = pd.read_json(idx, lines=True)
        x['root'] = str(Path(d))
        rows.append(x)
    x = pd.concat(rows).drop_duplicates('game', keep='last')
    x = x[x.rc == 0] if 'rc' in x else x
    return x


def keyed(x, bot):
    x = x[(x.botA == bot) | (x.botB == bot)].copy()
    x['side'] = np.where(x.botA == bot, 'A', 'B')
    x['won'] = (x.winner == x.side).astype(int)
    x['limit'] = x.reason.astype(str).str.contains('round|limit|length', case=False) & ~x.reason.astype(str).str.contains('elimination')
    x['key'] = [f"s{s}__{m}__{a if a != bot else 'X'}__{b if b != bot else 'X'}" for s, m, a, b in zip(x.seed, x['map'], x.botA, x.botB)]
    return x.set_index('key')


def material(args):
    path, side = args
    sys.path.insert(0, str(ROOT / 'tools' / 'tt')); sys.path.insert(0, str(ROOT / 'tools' / 'team_recon_claude'))
    import concentration_bot as C
    try:
        _, e = C.one((path, side))
        return e['L'], e['T'], e['oT']
    except Exception:
        return None, None, None


def ci(diff, rng, B=4000):
    if len(diff) == 0:
        return float('nan'), float('nan'), float('nan')
    m = diff.mean()
    bs = rng.choice(diff, (B, len(diff)), replace=True).mean(1)
    return m, np.quantile(bs, 0.025), np.quantile(bs, 0.975)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cand', nargs='+', required=True); ap.add_argument('--parent', nargs='+', required=True)
    ap.add_argument('--cand-bot'); ap.add_argument('--parent-bot')
    ap.add_argument('--material', action='store_true')
    ap.add_argument('--out')
    a = ap.parse_args()
    C, P = load(a.cand), load(a.parent)
    guess = lambda x, d: re.sub(r'^(z1|gen)-(.*)-[0-9a-f]{8}$', r'\2', Path(d[0]).name)
    cb = a.cand_bot or guess(C, a.cand)
    pb = a.parent_bot or guess(P, a.parent)
    C, P = keyed(C, cb), keyed(P, pb)
    j = C[['map', 'won', 'limit', 'rounds', 'side', 'root', 'replay']].join(
        P[['won', 'limit', 'rounds', 'root', 'replay']], rsuffix='_p', how='inner')
    j['regime'] = j['map'].map(lambda m: 'elim' if m in ELIM else 'limit' if m in LIMIT else 'other')
    j['d'] = j.won - j.won_p
    rng = np.random.default_rng(0)
    print(f'{cb} vs {pb}: {len(j)} paired fixtures ({len(C)} / {len(P)} games)\n')
    if a.material:
        work = [(str(Path(r) / p), s) for r, p, s in zip(j.root, j.replay, j.side)] + \
               [(str(Path(r) / p), s) for r, p, s in zip(j.root_p, j.replay_p, j.side)]
        with Pool(12) as pool:
            m = pool.map(material, work, chunksize=4)
        n = len(j)
        j['L'], j['T'], j['oT'] = zip(*m[:n]); j['L_p'], j['T_p'], j['oT_p'] = zip(*m[n:])
    out = dict(cand=cb, parent=pb, paired=int(len(j)), rows={})

    def row(label, g):
        m, lo, hi = ci(g.d.to_numpy(), rng)
        r = dict(n=int(len(g)), cand_win=float(g.won.mean()), parent_win=float(g.won_p.mean()), delta=float(m),
                 lo=float(lo), hi=float(hi), changed=int((g.rounds != g.rounds_p).sum() + (g.won != g.won_p).sum() > 0 and
                                                       ((g.rounds != g.rounds_p) | (g.won != g.won_p)).sum()),
                 limW=f"{int((g.won & g.limit).sum())}-{int((~g.won.astype(bool) & g.limit).sum())}",
                 limW_p=f"{int((g.won_p & g.limit_p).sum())}-{int((~g.won_p.astype(bool) & g.limit_p).sum())}",
                 elimL=int((~g.won.astype(bool) & ~g.limit).sum()), elimL_p=int((~g.won_p.astype(bool) & ~g.limit_p).sum()))
        if a.material:
            lead = lambda w, l, T, oT: int(((w == 0) & l & (pd.to_numeric(T) > pd.to_numeric(oT))).sum())
            r.update(conv_fail=lead(g.won, g.limit, g['T'], g.oT), conv_fail_p=lead(g.won_p, g.limit_p, g.T_p, g.oT_p),
                     L_end=float(pd.to_numeric(g.L[g.limit]).median()) if g.limit.any() else None,
                     L_end_p=float(pd.to_numeric(g.L_p[g.limit_p]).median()) if g.limit_p.any() else None)
        out['rows'][label] = r
        extra = (f"  conv.fail {r['conv_fail']:>2} / {r['conv_fail_p']:<2}  longest@end {r['L_end']} / {r['L_end_p']}"
                 if a.material else '')
        print(f"{label:<16}{r['n']:>5}  {100 * r['cand_win']:5.1f} {100 * r['parent_win']:5.1f}  {100 * m:+6.2f} "
              f"[{100 * lo:+6.2f}, {100 * hi:+6.2f}]  changed {r['changed']:>4}  limit W-L {r['limW']:>7} / {r['limW_p']:<7} "
              f"elim losses {r['elimL']:>3} / {r['elimL_p']:<3}{extra}")
        return lo, hi

    print(f"{'':<16}{'n':>5}  {'cand':>5} {'par':>5}  {'delta pp':>7} {'95% CI':>17}")
    lo, hi = row('ALL', j)
    reg = {k: row(f'regime {k}', g) for k, g in j.groupby('regime')}
    for k, g in j.groupby('map'):
        row(f'  {k}', g)
    bad = [k for k, (l, h) in reg.items() if h < 0]
    if lo > 0 and not bad:
        v = 'ACCEPT'
    elif hi < 0:
        v = 'REJECT'
    elif hi < 0.02:
        v = 'NO GAIN'
    else:
        v = 'INCONCLUSIVE'
    out['verdict'] = v
    print(f"\nVERDICT: {v}" + (f" (regime significantly worse: {', '.join(bad)})" if bad else ''))
    if a.out:
        Path(a.out).write_text(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
