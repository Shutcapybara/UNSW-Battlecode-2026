"""Re-derive every number quoted in the A1 findings from the live record (handoff A1, 28 Sep 2026).

    python -m tools.analysis.a1_report --state LIVE/state/state.json [--out build/a1_report.md]

Sections: inventory, Q1 loss anatomy per source, Q2 exact-pair contrasts per experiment, Q3 layout rule and batch
parity, Q5 opponent fingerprints from the live record, Q6 runtime, Q7 sonar, Q9 ranked-series timeline. Pure pandas
over `tools.analysis.live_record.games_table`; the recurring subset of these statistics runs in the hub via
`tools/hub/analysis_a1.py` and both must agree (see tests/test_hub_analysis.py and the ATLAS cross-check).
"""
import argparse
import json
import math

import numpy as np
import pandas as pd

from .live_record import COMPACT, STAGES, games_table, load_state

SOURCES_MIN = 20
FAMILY_X = {'e492d8bc', '48c928e0', 'da98e11b', 'cfc35be3', 'ea5704a6', 'b1ab27ea', '3f6daf3e', '57dcdc6d', 'dff66415', '7d4ad0ee', 'a3f6ec4f'}


def sign_test_p(better, worse):
    n = better + worse
    if n == 0:
        return None
    k = min(better, worse)
    return round(min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n), 3)


def controlled_a(df):
    return df[(df.verified == True) & (df.origin == 'controlled') & (df.side == 'A')].copy()  # noqa: E712


def first_behind(r, key='total'):
    for s in STAGES:
        a, b = r[f's{s}_{key}'], r[f'o{s}_{key}']
        if pd.isna(a) or pd.isna(b):
            return None
        if a < b:
            return s
    return 'never'


def md_table(df, floatfmt=2):
    df = df.copy()
    cols = list(df.columns)
    lines = ['| ' + ' | '.join(str(c) for c in cols) + ' |', '|' + '---|' * len(cols)]
    for _, r in df.iterrows():
        vals = []
        for c in cols:
            v = r[c]
            if isinstance(v, float):
                vals.append('' if pd.isna(v) else (f'{v:.{floatfmt}f}' if abs(v - round(v)) > 1e-9 else f'{int(round(v))}'))
            else:
                vals.append(str(v))
        lines.append('| ' + ' | '.join(vals) + ' |')
    return '\n'.join(lines)


def inventory(df):
    ok = df[df.verified == True]  # noqa: E712
    return dict(results=len(df), verified=int(len(ok)), unverified=int(len(df) - len(ok)), controlled=int((ok.origin == 'controlled').sum()),
                observational=int((ok.origin == 'observational').sum()), side_a=int((ok.side == 'A').sum()), side_b=int((ok.side == 'B').sum()),
                field=int((ok.pool == 'field').sum()), dev=int((ok.pool == 'dev').sum()), sources=ok.submission.value_counts().to_dict(),
                opponent_submissions={f'{int(t)}/{int(s)}': int(n) for (t, s), n in ok.groupby(['opponent', 'opponent_submission']).size().items()},
                span=[str(df.requested_ts.min()), str(df.requested_ts.max())], maps=ok.map_name.value_counts().to_dict())


def q1(df):
    ok = controlled_a(df)
    ok['res'] = ok.score.map({1: 'W', 0: 'L'})
    out = {}
    for s, g in ok.groupby('submission'):
        if len(g) < SOURCES_MIN:
            continue
        L, W = g[g.res == 'L'], g[g.res == 'W']
        e, rl = L[L.reason == 'elimination'], L[L.reason == 'roundLimit']
        rows = []
        for cls in ('compact', 'open'):
            for res in ('W', 'L'):
                h = g[(g.map_class == cls) & (g.res == res)]
                if len(h):
                    rows.append(dict(cls=cls, res=res, n=len(h), u100=h.s100_units.median(), ou100=h.o100_units.median(), t250=h.s250_total.median(), ot250=h.o250_total.median(),
                                     l400=h.s400_longest.median(), ol400=h.o400_longest.median(), l499=h.s499_longest.median(), ol499=h.o499_longest.median(),
                                     wall1k=(1000 * h.s499_death_wall / h.s499_turns).median(), self1k=(1000 * h.s499_death_self / h.s499_turns).median(),
                                     body1k=(1000 * h.s499_death_body / h.s499_turns).median(), h2h1k=(1000 * h.s499_death_h2h / h.s499_turns).median(),
                                     nb10=h.s499_newborn_deaths_10.median(), splits=h.s499_splits.median()))
        curves = pd.DataFrame(rows).round(1)
        opp = g.groupby(['opponent', 'opponent_submission']).agg(n=('score', 'size'), share=('score', 'mean'), u100=('s100_units', 'median'), ou100=('o100_units', 'median'),
                                                                t250=('s250_total', 'median'), ot250=('o250_total', 'median'), l400=('s400_longest', 'median'), ol400=('o400_longest', 'median'),
                                                                l499=('s499_longest', 'median'), ol499=('o499_longest', 'median')).round(2)
        opp['elim_losses'] = g.groupby(['opponent', 'opponent_submission']).apply(lambda h: int(((h.score == 0) & (h.reason == 'elimination')).sum()))
        opp['rl_losses'] = g.groupby(['opponent', 'opponent_submission']).apply(lambda h: int(((h.score == 0) & (h.reason == 'roundLimit')).sum()))
        surv = {cls: dict(own=[float(round((h[f's{r}_units'] > 0).mean(), 2)) for r in STAGES], opp=[float(round((h[f'o{r}_units'] > 0).mean(), 2)) for r in STAGES], n=len(h))
                for cls, h in g.groupby('map_class')}
        cond = g.assign(lead=np.sign(g.s100_total - g.o100_total)).groupby(['map_class', 'lead']).agg(n=('score', 'size'), share=('score', 'mean')).round(2)
        out[int(s)] = dict(n=len(g), share=round(g.score.mean(), 3), wins=len(W), losses=len(L), elim=len(e), rl=len(rl),
                           elim_round=dict(median=e.rounds.median(), q25=e.rounds.quantile(.25), q75=e.rounds.quantile(.75), compact=e[e.map_class == 'compact'].rounds.median(), open=e[e.map_class == 'open'].rounds.median()),
                           rl_loss_margin=dict(median=rl.longest_margin.median(), q25=rl.longest_margin.quantile(.25), q75=rl.longest_margin.quantile(.75)),
                           win_reasons=W.reason.value_counts().to_dict(), win_elim_round=W[W.reason == 'elimination'].rounds.median(),
                           by_class={cls: dict(n=len(h), share=float(round(h.score.mean(), 2)), elim=int(((h.score == 0) & (h.reason == 'elimination')).sum()), rl=int(((h.score == 0) & (h.reason == 'roundLimit')).sum())) for cls, h in g.groupby('map_class')},
                           curves=curves, by_opponent=opp.reset_index(), survival=surv,
                           loss_first_behind_total={str(k): int(v) for k, v in L.apply(first_behind, axis=1).value_counts().items()}, win_first_behind_total={str(k): int(v) for k, v in W.apply(first_behind, axis=1).value_counts().items()},
                           loss_first_behind_units={str(k): int(v) for k, v in L.apply(lambda r: first_behind(r, 'units'), axis=1).value_counts().items()},
                           share_by_r100_lead={f'{c}_{ {1.0: "ahead", -1.0: "behind", 0.0: "level"}[l] }': dict(n=int(v.n), share=float(v.share)) for (c, l), v in cond.iterrows()})
    pooled = ok.assign(lead=np.sign(ok.s100_total - ok.o100_total)).groupby(['map_class', 'lead']).agg(n=('score', 'size'), share=('score', 'mean')).round(2)
    return out, pooled


PAIR_KEYS = ['s100_units', 's250_total', 's400_longest', 's499_longest', 's499_deaths', 's499_death_h2h', 's499_newborn_deaths_10', 's499_splits', 's499_sonar', 'cpu_max', 'faults', 'longest_margin']


def q2(df):
    ok = df[(df.verified == True) & (df.block_phase == 'screen')].copy()  # noqa: E712
    out = {}
    for exp, g in ok.groupby('experiment_id'):
        cand, ctrl = int(g.experiment_candidate.iloc[0]), int(g.experiment_control.iloc[0])
        pairs, unpaired = [], {cand: 0, ctrl: 0}
        for (blk, m, side, osub, lay), h in g.groupby(['block_id', 'map_id', 'side', 'opponent_submission', 'map_hash']):
            c, k = h[h.arm == 'candidate'].sort_values('game_id'), h[h.arm == 'control'].sort_values('game_id')
            if len(c) == 0 or len(k) == 0:
                unpaired[cand] += len(c)
                unpaired[ctrl] += len(k)
                continue
            c0, k0 = c.iloc[0], k.iloc[0]
            row = dict(block=blk[:8], opp=int(h.block_opponent.iloc[0]), map=h.map_name.iloc[0], cls=h.map_class.iloc[0], layout=lay[:8], cand_game=int(c0.game_id), ctrl_game=int(k0.game_id),
                       d_score=c0.score - k0.score, cand_reason=c0.reason, ctrl_reason=k0.reason, dup=(len(c) > 1 or len(k) > 1))
            for key in PAIR_KEYS:
                row['d_' + key] = (c0[key] - k0[key]) if pd.notna(c0[key]) and pd.notna(k0[key]) else np.nan
            pairs.append(row)
        P = pd.DataFrame(pairs)
        better, worse = int((P.d_score > 0).sum()), int((P.d_score < 0).sum())
        flips = P[P.d_score != 0]
        out[exp[:8]] = dict(candidate=cand, control=ctrl, pairs=len(P), unpaired=unpaired,
                            delta=round(P.d_score.mean(), 3), better=better, same=int((P.d_score == 0).sum()), worse=worse, p=sign_test_p(better, worse),
                            by_opp=P.groupby('opp').agg(n=('d_score', 'size'), delta=('d_score', 'mean'), better=('d_score', lambda x: int((x > 0).sum())), worse=('d_score', lambda x: int((x < 0).sum()))).round(3).reset_index(),
                            by_cls=P.groupby('cls').agg(n=('d_score', 'size'), delta=('d_score', 'mean'), better=('d_score', lambda x: int((x > 0).sum())), worse=('d_score', lambda x: int((x < 0).sum()))).round(3).reset_index(),
                            stage_deltas={k: dict(median=P['d_' + k].median(), mean=round(P['d_' + k].mean(), 1), n=int(P['d_' + k].notna().sum())) for k in PAIR_KEYS},
                            flips=flips[['opp', 'map', 'd_score', 'cand_reason', 'ctrl_reason', 'd_s100_units', 'd_s250_total', 'd_s499_longest', 'd_faults']].reset_index(drop=True),
                            flip_r250_agree=int(((flips.d_s250_total > 0) == (flips.d_score > 0)).sum()), duplicates=int(P.dup.sum()))
    return out


def q3(df):
    ok = df[df.verified == True].copy()  # noqa: E712
    ok['layout'] = ok.map_hash.str[:8]
    ok['parity'] = ok.game_id % 2
    per_map = {}
    violations = 0
    for m, g in ok.groupby('map_name'):
        ct = pd.crosstab(g.parity, g.layout)
        even, odd = set(ct.columns[ct.loc[0] > 0]) if 0 in ct.index else set(), set(ct.columns[ct.loc[1] > 0]) if 1 in ct.index else set()
        v = int(sum(min(ct.loc[0, h], ct.loc[1, h]) for h in (even & odd))) if (even & odd) else 0
        violations += v
        per_map[m] = dict(n=len(g), even=sorted(even), odd=sorted(odd), violations=v, hashes=len(set(ct.columns)))
    ok['family'] = ok.layout.map(lambda h: 'X' if h in FAMILY_X else 'Y')
    # batches: requests with count 10 and the standard map order
    req = ok[ok.request_count == 10].groupby('request_index').agg(first_id=('game_id', 'min'), n=('game_id', 'size'), families=('family', lambda x: ''.join(x)), maps=('map_id', lambda x: ','.join(str(m) for m in x)), at=('request_at', 'first'), opponent=('opponent', 'first'), submission=('submission', 'first'))
    req['uniform'] = req.families.map(lambda f: len(set(f)) == 1)
    req['standard_order'] = req.maps == '9,20,21,7,4,11,17,19,13,15'
    # seed test: does any single seed bit predict the family?
    ok['seed_int'] = ok.seed.apply(lambda s: int(s, 16) if isinstance(s, str) else np.nan)
    fam = (ok.family == 'X').astype(int).values
    best = 0.0
    for b in range(64):
        bit = ((ok.seed_int.astype(np.uint64).values >> np.uint64(b)) & np.uint64(1)).astype(int)
        agree = (bit == fam).mean()
        best = max(best, agree, 1 - agree)
    # pairing consequence for screen blocks: same-parity first ids
    return dict(n=len(ok), violations=violations, per_map=per_map, batches=req.reset_index(), best_seed_bit_agreement=round(float(best), 3),
                pd_versions=ok[ok.map_name == 'Prisoners Dilemma'].layout.value_counts().to_dict())


def q5(df, ladder):
    ok = df[(df.verified == True) & (df.side == 'A')].copy()  # noqa: E712
    L = {x['id']: x for x in ladder}
    rows = []
    for (t, s), g in ok.groupby(['opponent', 'opponent_submission']):
        rows.append(dict(team=int(t), name=L.get(int(t), {}).get('name'), rank=L.get(int(t), {}).get('rank'), elo=L.get(int(t), {}).get('elo'), submission=int(s), n=len(g), our_share=round(g.score.mean(), 2),
                         u100=g.o100_units.median(), u250=g.o250_units.median(), t250=g.o250_total.median(), l320=g.o320_longest.median(), l400=g.o400_longest.median(), l499=g.o499_longest.median(),
                         peak_units=g.o499_peak_units.median(), splits=g.o499_splits.median(), rays_pt=round((g.o499_sonar / g.o499_turns).median(), 2), h2h1k=round((1000 * g.o499_death_h2h / g.o499_turns).median(), 1),
                         wall1k=round((1000 * g.o499_death_wall / g.o499_turns).median(), 1), self1k=round((1000 * g.o499_death_self / g.o499_turns).median(), 1), nb10=g.o499_newborn_deaths_10.median(),
                         portal_steps=g.o499_portal_steps.median(), sprints=g.o499_sprints.median(), initiated_h2h=g.o499_initiated_h2h.median(),
                         eliminated_us=int(((g.score == 0) & (g.reason == 'elimination')).sum())))
    ours = []
    for s, g in ok[ok.origin == 'controlled'].groupby('submission'):
        ours.append(dict(submission=int(s), n=len(g), u100=g.s100_units.median(), u250=g.s250_units.median(), t250=g.s250_total.median(), l320=g.s320_longest.median(), l400=g.s400_longest.median(), l499=g.s499_longest.median(),
                         peak_units=g.s499_peak_units.median(), splits=g.s499_splits.median(), rays_pt=round((g.s499_sonar / g.s499_turns).median(), 2), h2h1k=round((1000 * g.s499_death_h2h / g.s499_turns).median(), 1),
                         wall1k=round((1000 * g.s499_death_wall / g.s499_turns).median(), 1), self1k=round((1000 * g.s499_death_self / g.s499_turns).median(), 1), nb10=g.s499_newborn_deaths_10.median(), portal_steps=g.s499_portal_steps.median(),
                         sprints=g.s499_sprints.median(), initiated_h2h=g.s499_initiated_h2h.median()))
    band = [(x['rank'], x['id'], x['name'], x['elo']) for x in ladder if 60 <= x['rank'] <= 76]
    return pd.DataFrame(rows).sort_values('n', ascending=False), pd.DataFrame(ours), band


def q6(df):
    ok = controlled_a(df)
    ok['cpu_M'] = ok.cpu_max / 1e6
    t = ok.groupby('submission').agg(n=('cpu_M', 'size'), p50=('cpu_M', 'median'), p90=('cpu_M', lambda x: x.quantile(.9)), max=('cpu_M', 'max'), near_cap=('cpu_max', lambda x: int((x > 90e6).sum())),
                                     at_cap=('cpu_max', lambda x: int((x >= 100e6).sum())), faults=('faults', 'sum'), fault_games=('faults', lambda x: int((x > 0).sum())), turns=('turns', 'sum')).round(1)
    by_map = ok.groupby(['submission', 'map_name']).cpu_M.max().round(1).unstack(0)
    faults_map = ok[ok.submission == 9508].groupby('map_name').faults.agg(['sum', 'mean', 'max']).round(1)
    g = ok[ok.submission == 9508]
    fw = g.groupby(pd.cut(g.faults, [-1, 0, 5, 20, 60, 400])).agg(n=('score', 'size'), share=('score', 'mean'), elim_loss=('reason', lambda x: round(((x == 'elimination') & (g.loc[x.index, 'score'] == 0)).mean(), 2))).round(2)
    fw.index = fw.index.astype(str)
    return t, by_map, faults_map, fw


def q7(df):
    ok = controlled_a(df)
    ok['rays'] = ok.s499_sonar / ok.s499_turns
    ok['rays100'] = ok.s100_sonar / ok.s100_turns
    t = ok.groupby('submission').agg(n=('rays', 'size'), rays_per_turn=('rays', 'median'), q10=('rays', lambda x: x.quantile(.1)), q90=('rays', lambda x: x.quantile(.9)), rays_r100=('rays100', 'median')).round(2)
    by = ok.groupby(['submission', 'map_class', ok.score.map({1: 'W', 0: 'L'})]).rays100.median().round(2).unstack()
    return t, by


def q9(state):
    rows = []
    for sid, p in (state.get('seen_series') or {}).items():
        m = p.get('match') or {}
        if m.get('ranked'):
            rows.append(dict(match=m.get('id'), map=p.get('mapName'), team_a=m.get('teamAId'), team_b=m.get('teamBId'), sub_a=m.get('submissionAId'), sub_b=m.get('submissionBId'),
                             requested_by=(m.get('requestedBy') or '')[:6] or None, requested_at=m.get('requestedAt'), started_at=m.get('startedAt'), status=m.get('status'), elo_a=m.get('eloChangeA'), elo_b=m.get('eloChangeB'),
                             our_side='A' if m.get('teamAId') == 7 else 'B', winners=''.join((g.get('winner') or '-') for g in p.get('games', []))))
    R = pd.DataFrame(rows).sort_values('requested_at')
    R['even_hour_autoscrim'] = R.requested_at.str.endswith('00:00.000Z') & R.requested_by.isna()
    R['our_elo'] = np.where(R.our_side == 'A', R.elo_a, R.elo_b)
    return R


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--state', required=True)
    ap.add_argument('--ladder')
    ap.add_argument('--out')
    args = ap.parse_args()
    state = load_state(args.state)
    df = games_table(state)
    ladder = json.load(open(args.ladder)) if args.ladder else []
    L = []
    inv = inventory(df)
    L += ['# A1 report (re-derived)', '', f"State updated {state.get('updated')}; incumbent {state.get('incumbent')}.", '', '## Inventory', '', '```', json.dumps(inv, indent=1, default=str), '```', '']
    anat, pooled = q1(df)
    L += ['## Q1 loss anatomy (verified controlled A-side games, field + dev; opponents stratified by submission)', '']
    L += ['Pooled win share by r100 total-length lead:', '', md_table(pooled.reset_index()), '']
    for s, a in anat.items():
        L += [f"### source {s}: n={a['n']} share={a['share']} W/L {a['wins']}/{a['losses']}; losses elim/RL {a['elim']}/{a['rl']}; elimination round median {a['elim_round']['median']} (q25 {a['elim_round']['q25']}, q75 {a['elim_round']['q75']}; compact {a['elim_round']['compact']}, open {a['elim_round']['open']}); RL-loss longest margin median {a['rl_loss_margin']['median']} (q25 {a['rl_loss_margin']['q25']}, q75 {a['rl_loss_margin']['q75']}); wins by reason {a['win_reasons']}, win-elimination round median {a['win_elim_round']}",
              '', f"by class: {a['by_class']}", '', f"losses first behind on total: {a['loss_first_behind_total']}; on units: {a['loss_first_behind_units']}; wins first behind on total: {a['win_first_behind_total']}", '',
              f"share by r100 total lead: {a['share_by_r100_lead']}", '', f"survival (share with units>0 at r{list(STAGES)}): {a['survival']}", '', md_table(a['curves'], 1), '', md_table(a['by_opponent']), '']
    L += ['## Q2 exact-pair contrasts (screen blocks; pairs on block, map, side, opponent submission, layout)', '']
    for eid, c in q2(df).items():
        L += [f"### {eid}: candidate {c['candidate']} − control {c['control']}: pairs {c['pairs']} (unpaired {c['unpaired']}, duplicates {c['duplicates']}), delta {c['delta']:+.3f}, better/same/worse {c['better']}/{c['same']}/{c['worse']}, sign-test p {c['p']}; flips {len(c['flips'])} of which r250-total sign agrees {c['flip_r250_agree']}", '',
              md_table(c['by_opp'], 3), '', md_table(c['by_cls'], 3), '', 'stage deltas (median / mean / n): ' + '; '.join(f"{k} {v['median']} / {v['mean']} / {v['n']}" for k, v in c['stage_deltas'].items()), '', md_table(c['flips'], 1), '']
    lay = q3(df)
    L += ['## Q3 starting-layout rule', '', f"games {lay['n']}, violations of layout = f(map, game_id parity): {lay['violations']}; best single seed-bit agreement with the family {lay['best_seed_bit_agreement']} (chance ≈ 0.5); Prisoners Dilemma hashes {lay['pd_versions']}", '',
          '```', json.dumps(lay['per_map'], indent=1), '```', '', 'Ten-game batches (request index, first id, families in request order, uniform, standard map order):', '', md_table(lay['batches'][['request_index', 'first_id', 'n', 'families', 'uniform', 'standard_order', 'submission', 'opponent', 'at']]), '']
    if ladder:
        opp, ours, band = q5(df, ladder)
        L += ['## Q5 opponent fingerprints from the live record (opponent stages, A-side verified games)', '', md_table(opp, 2), '', 'our sources on the same measures:', '', md_table(ours, 2), '', f'ladder band ranks 60–76: {band}', '']
    t, by_map, fm, fw = q6(df)
    L += ['## Q6 runtime (M points; verified controlled A-side)', '', md_table(t.reset_index(), 1), '', 'map maxima:', '', md_table(by_map.reset_index(), 1), '', '9508 faults by map:', '', md_table(fm.reset_index(), 1), '', '9508 win share by fault band (survivorship, not causal):', '', md_table(fw.reset_index(), 2), '']
    t7, by7 = q7(df)
    L += ['## Q7 sonar rays per dragon-turn', '', md_table(t7.reset_index(), 2), '', md_table(by7.reset_index(), 2), '']
    R = q9(state)
    L += ['## Q9 ranked series seen in the record', '', md_table(R[['match', 'map', 'team_a', 'team_b', 'sub_a', 'sub_b', 'requested_by', 'requested_at', 'started_at', 'status', 'elo_a', 'elo_b', 'our_side', 'winners', 'even_hour_autoscrim']], 1), '',
          f"our Elo sum over completed series with a recorded change: {R.our_elo.sum(skipna=True)} over {int(R.our_elo.notna().sum())} series; member-requested ranked series: {int(R.requested_by.notna().sum())} of {len(R)}", '']
    text = '\n'.join(L)
    if args.out:
        from pathlib import Path
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text)
    print(text if not args.out else f'wrote {args.out} ({len(L)} lines)')


if __name__ == '__main__':
    main()
