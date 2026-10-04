#!/usr/bin/env python3
"""P-4 / H-KZ26 verdict card (D-054 §C; card §3 as amended by Tanaka). Our side only.

Per arm vs parent, pool and gen separately, seed 1, on paired fixtures (seed, map, opp, seat):
- strike hazard = sum(strike deaths of our original queen) / sum(alive queen-rounds)   [strikes.parquet, frozen labeller]
- all-cause queen hazard = sum(queen deaths) / sum(alive queen-rounds)
- ratio cand / parent; paired cluster bootstrap over map × opponent (D-052 §C), 1,000 resamples, seed 7, linear 5th-95th,
  numerator and denominator recomputed per draw; a draw with zero parent strikes (ratio undefined) is invalid and counted;
  < 900 valid draws -> INCOMPLETE.
- all-cause hazard difference (cand - parent), its 5th percentile (refute clause);
- food per turn = pearls eaten by all own dragons / alive own dragon-turns (features dragons table: eats, turns), ratio;
- fixed-fixture all-cause queen death incidence per game, P(queen alive at round limit) (header, queen.parquet).
Binding readout: pool and gen POOLED (clusters panel × map × opponent), each panel printed separately (frozen
4 Oct 18:00Z, before any parent game was labelled). Verdict on m = 0 (card §3): support iff strike ratio <= 0.70 and all-cause hazard ratio <= 1 and guards hold;
refute iff strike ratio >= 0.90, or all-cause diff 5th pct > 0, or food ratio <= 0.90; else hold. Stops: < 10 parent
strike events on pool + gen -> "no local exposure"; < 5 firings / 1k queen decisions (hkz26_summary.json) -> "no reach".

    python tools/asahi/hkz26_card.py --arm asahi-07-hkz26-m0 [--arm2 asahi-08-hkz26-m1] --out docs/learning/results/asahi/P-4-s1
"""
import argparse, json, sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/asahi'))
import panel as P  # noqa: E402
import card as C  # noqa: E402

PARENT = 'carthage-05-free-sprint'


def side_table(bot, panel, seeds=(1,)):
    root = P.run_root(bot, panel)
    S = pd.read_parquet(root / 'strikes.parquet')
    if 'error' in S and S['error'].notna().any():
        raise SystemExit(f'{bot} {panel}: labeller errors {S[S.error.notna()].game.tolist()[:5]}')
    fx = {f['game']: f for f in P.fixtures(bot, panel, list(seeds))}
    S = S[S.game.isin(fx)]
    S = S[S.apply(lambda r: fx[r.game]['seat'] == r.side, axis=1)].copy()
    for k in ('seed', 'opp', 'seat'):
        S[k] = S.game.map(lambda g: fx[g][k])
    S['mapkey'] = S.game.map(lambda g: fx[g]['map'])
    D = pd.read_parquet(root / 'features/dragons.parquet', columns=['game', 'side', 'eats', 'turns'])
    food = D.groupby(['game', 'side']).agg(eats=('eats', 'sum'), dturns=('turns', 'sum')).reset_index()
    S = S.merge(food, on=['game', 'side'], how='left')
    Q = pd.read_parquet(root / 'queen.parquet', columns=['game', 'side', 'queen_end', 'reason'])
    S = S.merge(Q, on=['game', 'side'], how='left')
    S['q_alive_rl'] = ((S.queen_end > 0) & (S.reason != 'elimination')).astype(int)
    return S, sorted(set(fx) - set(S.game)), S.labeller_sha256.iloc[0]


def stat(m):
    ps, cs = m.strike_p.sum(), m.strike_c.sum()
    pr, cr = m.alive_rounds_p.sum(), m.alive_rounds_c.sum()
    hp, hc = ps / pr, cs / cr
    ap, ac = m.dead_p.sum() / pr, m.dead_c.sum() / cr
    fp, fc = m.eats_p.sum() / m.dturns_p.sum(), m.eats_c.sum() / m.dturns_c.sum()
    return dict(strike_ratio=hc / hp if hp > 0 else np.nan, allcause_ratio=ac / ap if ap > 0 else np.nan,
                allcause_diff=ac - ap, food_ratio=fc / fp if fp > 0 else np.nan)


def paired(arm, panel):
    Sc, mc, shac = side_table(arm, panel)
    Sp, mp, shap = side_table(PARENT, panel)
    k = ['seed', 'mapkey', 'opp', 'seat']
    cols = ['strike', 'dead', 'alive_rounds', 'eats', 'dturns', 'q_alive_rl', 'category']
    m = Sc[k + cols].merge(Sp[k + cols], on=k, suffixes=('_c', '_p')).sort_values(k).reset_index(drop=True)
    m['panel'] = panel
    return m, mc, mp, shac, shap


def compare(arm, panel):
    if panel == 'pooled':   # pool + gen together, clusters panel × map × opponent (binding, frozen 4 Oct 18:00Z)
        parts = [paired(arm, p) for p in ('pool', 'gen')]
        m = pd.concat([x[0] for x in parts], ignore_index=True)
        mc = parts[0][1] + parts[1][1]; mp = parts[0][2] + parts[1][2]; shac, shap = parts[0][3], parts[0][4]
    else:
        m, mc, mp, shac, shap = paired(arm, panel)
    groups = list(m.groupby(['panel', 'mapkey', 'opp'], sort=True).indices.values())
    rng = np.random.default_rng(7)
    B = pd.DataFrame([stat(m.iloc[np.concatenate([groups[i] for i in rng.integers(0, len(groups), len(groups))])])
                      for _ in range(1000)])
    pt = stat(m)
    iv = {c: [float(pt[c]), float(B[c].quantile(0.05)), float(B[c].quantile(0.95)), int(B[c].notna().sum())] for c in pt}
    counts = dict(paired=len(m), clusters=len(groups), parent_strikes=int(m.strike_p.sum()), cand_strikes=int(m.strike_c.sum()),
                  parent_alive_rounds=int(m.alive_rounds_p.sum()), cand_alive_rounds=int(m.alive_rounds_c.sum()),
                  parent_deaths=int(m.dead_p.sum()), cand_deaths=int(m.dead_c.sum()),
                  incidence_c=float(m.dead_c.mean()), incidence_p=float(m.dead_p.mean()),
                  q_alive_rl_c=int(m.q_alive_rl_c.sum()), q_alive_rl_p=int(m.q_alive_rl_p.sum()),
                  categories_c=m.category_c.value_counts().to_dict(), categories_p=m.category_p.value_counts().to_dict(),
                  missing_c=mc, missing_p=mp, labeller=[shac, shap])
    return dict(arm=arm, panel=panel, iv=iv, counts=counts)


def verdict(pooled, firing_per1k):
    ps = pooled['counts']['parent_strikes']
    if firing_per1k is not None and firing_per1k < 5:
        return 'STOP: no reach (< 5 firings / 1k)'
    if ps < 10:
        return f'STOP: no local exposure ({ps} parent strike events < 10)'
    iv = pooled['iv']
    if iv['strike_ratio'][3] < 900:
        return f"INCOMPLETE: valid draws {iv['strike_ratio'][3]} < 900"
    if iv['strike_ratio'][0] >= 0.90 or iv['allcause_diff'][1] > 0 or iv['food_ratio'][0] <= 0.90:
        return 'REFUTE'
    if iv['strike_ratio'][0] <= 0.70 and iv['allcause_ratio'][0] <= 1.0:
        return 'SUPPORT (win/econ guards: see the D-052 card)'
    return 'HOLD'


def fmt(v, pct=False):
    return f'{v[0]:.3f} [{v[1]:.3f}, {v[2]:.3f}] ({v[3]} valid)'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--arm', required=True); ap.add_argument('--arm2'); ap.add_argument('--out', required=True)
    a = ap.parse_args()
    L, res = ['# P-4 / H-KZ26 screen — strike and queen hazards, seed 1\n',
              'Paired fixtures; cluster bootstrap map × opponent, 1,000 × seed 7, linear 5th–95th; numerator and denominator '
              'recomputed per draw; undefined-ratio draws invalid. Our side only; original queen. Labeller sha256 printed.\n'], {}
    for arm in [x for x in (a.arm, a.arm2) if x]:
        cards = {p: compare(arm, p) for p in ('pooled', 'pool', 'gen')}
        sp = P.run_root(arm, 'pool') / 'hkz26_summary.json'
        fire = json.load(open(sp))['by_map']['ALL']['queen'] if sp.exists() else None
        f1k = 1000 * fire[1] / max(1, fire[0]) if fire else None
        v = verdict(cards['pooled'], f1k)
        res[arm] = dict(cards=cards, firing_per1k=f1k, verdict=v)
        L.append(f'## {arm}: **{v}**\n')
        if fire:
            L.append(f'Pool exposure: {fire[0]} queen decisions, {fire[1]} with ≥ 1 vetoed candidate ({f1k:.1f} / 1k), '
                     f'{fire[2]} all-vetoed fallbacks, {fire[3]} changed selections, {fire[5]} vetoed sprint candidates of {fire[4]}.\n')
        for p, c in cards.items():
            k, iv = c['counts'], c['iv']
            L.append(f"### {p}\n\n- paired {k['paired']} in {k['clusters']} clusters; missing cand {len(k['missing_c'])}, parent {len(k['missing_p'])}")
            L.append(f"- strikes: cand {k['cand_strikes']} / {k['cand_alive_rounds']} alive queen-rounds; parent {k['parent_strikes']} / {k['parent_alive_rounds']}")
            L.append(f"- strike-hazard ratio {fmt(iv['strike_ratio'])}")
            L.append(f"- all-cause queen deaths: cand {k['cand_deaths']}, parent {k['parent_deaths']}; hazard ratio {fmt(iv['allcause_ratio'])}; "
                     f"difference per round {fmt(iv['allcause_diff'])}")
            L.append(f"- food per alive own dragon-turn ratio {fmt(iv['food_ratio'])}")
            L.append(f"- fixed-fixture all-cause queen death incidence: cand {k['incidence_c']:.3f}, parent {k['incidence_p']:.3f}; "
                     f"queen alive at round limit: cand {k['q_alive_rl_c']}, parent {k['q_alive_rl_p']}")
            L.append(f"- death categories cand {k['categories_c']}; parent {k['categories_p']}")
            L.append(f"- labeller sha256 {k['labeller'][0][:16]} / {k['labeller'][1][:16]}\n")
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix('.json').write_text(json.dumps(res, indent=1, default=float))
    out.with_suffix('.md').write_text('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
