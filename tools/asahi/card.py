#!/usr/bin/env python3
"""Asahi (Phase 3 Evaluator) result cards: candidate vs parent on paired fixtures, and dose curves.

Conventions (frozen 4 Oct 2026, before any Asahi run; changing them needs a new version of this file):
- Outcomes: FRAME_VERSION 7 engine verdicts from tools.analysis.features (win 1, draw 0.5, loss 0).
- Pairing: fixture = (seed, map, opponent, seat). Only fixtures present with rc 0 in BOTH arms are compared;
  every other expected fixture is listed as MISSING and never counted as a loss.
- Interval: cluster bootstrap over (map, opponent, seat) clusters, seeds kept together; 1,000 resamples, numpy
  default_rng(7); reported interval = 5th-95th percentile (two-sided 90 %, i.e. one-sided 95 % lower bound).
- Economy: pearls@50/100/150/250 each divided by the PARENT's per-map median of that checkpoint (floor 1), because
  the field references in docs/analysis/benchmarks predate the 2 Oct swap and do not cover the seven restored maps.
  econ = per-game mean of the four normalised checkpoints (paired mean difference); econ~ = mean over checkpoints
  of the difference of medians. units@100, total@100: same normalisation, difference of medians.
- Queen columns (queen = the side's lowest-id initial dragon, dead = 0, no succession): reached = round-limit (RL)
  games; conditional = queen alive at the end among RL games; joint = RL and queen alive, over all games;
  queen-decided W/L = RL games whose engine reason is 'queen'.
- Tier-2 deaths: mean per-1k rates; flagged when the parent rate > 0.05 and the candidate's is > 1.10x.
- Gate letter, D-042 win-led rule (Himeji): PASS iff pool win lb > 0, gen win lb > -0.02, econ lb > -0.03 on both
  panels, units@100 and total@100 lb >= -0.02 on both panels, no tier-2 flag, no new invalid deaths. FAIL iff a
  clause is violated with the whole interval on the wrong side (ub below its threshold) or pool win ub < 0 or a
  tier-2 flag. Otherwise HOLD. A seed-1 screen gets the letter with the prefix 'screen-'; only seeds 1-3 (D-042) or
  1-5 (D-045 learned125) carry a gate verdict.

    python tools/asahi/card.py card CAND --parent PARENT --seeds 1 --out docs/learning/results/NAME
    python tools/asahi/card.py curve --doses 0:PARENT,4:CAND4,8:CAND8 --seeds 1 --out docs/learning/results/NAME
"""
from __future__ import annotations

import argparse, json, sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tools/asahi'))
import panel as P  # noqa: E402

ECON = ['pearls@50', 'pearls@100', 'pearls@150', 'pearls@250']
MAT = ['units@100', 'total@100']
HYG = ['death_wall_per1k', 'death_self_per1k', 'death_ally_body_per1k', 'death_h2h_ally_per1k', 'death_invalid_per1k']
SIDE = ['death_h2h_enemy_per1k', 'death_enemy_body_per1k', 'deaths_per1k', 'births@100']
KEY = ['seed', 'mapkey', 'opp', 'seat']
CLUSTER = ['mapkey', 'opp', 'seat']


def load_arm(bot: str, panel: str, seeds: list[int]) -> tuple[pd.DataFrame, dict]:
    root = P.run_root(bot, panel)
    meta = json.loads((root / 'run.json').read_text()) if (root / 'run.json').exists() else {}
    fx = P.fixtures(bot, panel, seeds)
    fpath = root / 'features' / 'features.parquet'
    if not fpath.exists():
        return pd.DataFrame(), dict(meta, expected=len(fx), missing=[f['game'] for f in fx])
    F = pd.read_parquet(fpath)
    D = pd.read_parquet(root / 'features' / 'dragons.parquet', columns=['game', 'id', 'side', 'died', 'initial'])
    idx = {}
    for line in open(root / 'index.jsonl'):
        r = json.loads(line)
        idx[r['game']] = r
    want = {f['game']: f for f in fx}
    F = F[F['game'].isin(want)].copy()
    F['seat'] = F['side']
    F = F[F.apply(lambda r: want[r['game']]['seat'] == r['side'], axis=1)].copy()
    F['rc'] = F['game'].map(lambda g: idx.get(g, {}).get('rc'))
    F = F[F['rc'] == 0]
    F['seed'] = F['game'].map(lambda g: want[g]['seed'])
    F['mapkey'] = F['game'].map(lambda g: want[g]['map'])
    F['opp'] = F['game'].map(lambda g: want[g]['opp'])
    F['win'] = F['result'].map({'win': 1.0, 'draw': 0.5, 'loss': 0.0})
    F['rl'] = (F['reason'] != 'elimination').astype(float)
    q = D[D['initial'].astype(bool)].sort_values('id').groupby(['game', 'side']).first().reset_index()
    q['q_alive'] = q['died'].isna().astype(float)
    F = F.merge(q[['game', 'side', 'q_alive']], on=['game', 'side'], how='left')
    F['q_joint'] = F['rl'] * F['q_alive']
    F['q_dec'] = ((F['rl'] == 1) & (F['reason'] == 'queen')).astype(float)
    F['cls'] = F['mapkey'].map(P.map_class)
    missing = sorted(set(want) - set(F['game']))
    return F, dict(meta, expected=len(fx), missing=missing)


def normalise(Fc: pd.DataFrame, Fp: pd.DataFrame):
    ref = {c: Fp.groupby('mapkey')[c].median() for c in ECON + MAT}
    for F in (Fc, Fp):
        for c in ECON + MAT:
            F[c + '|n'] = F[c] / F['mapkey'].map(ref[c]).clip(lower=1.0)
        F['econ'] = F[[c + '|n' for c in ECON]].mean(axis=1)


def stat(m: pd.DataFrame) -> dict:
    s = dict(win=(m.win_c - m.win_p).mean(), econ=(m.econ_c - m.econ_p).mean(),
             econ_med=np.mean([m[c + '|n_c'].median() - m[c + '|n_p'].median() for c in ECON]))
    for c in MAT:
        s[c] = m[c + '|n_c'].median() - m[c + '|n_p'].median()
    s['q_joint'] = (m.q_joint_c - m.q_joint_p).mean()
    rc, rp = m[m.rl_c == 1], m[m.rl_p == 1]
    s['q_cond'] = (rc.q_alive_c.mean() if len(rc) else np.nan) - (rp.q_alive_p.mean() if len(rp) else np.nan)
    s['conv'] = (rc.win_c.mean() if len(rc) else np.nan) - (rp.win_p.mean() if len(rp) else np.nan)
    for c in ('death_wall_per1k',):
        s[c] = (m[c + '_c'] - m[c + '_p']).mean()
    return s


def bootstrap(m: pd.DataFrame, nb=1000, seed=7) -> dict:
    groups = list(m.groupby(CLUSTER).indices.values())
    rng = np.random.default_rng(seed)
    pt = stat(m)
    B = pd.DataFrame([stat(m.iloc[np.concatenate([groups[i] for i in rng.integers(0, len(groups), len(groups))])])
                      for _ in range(nb)])
    return {k: [float(pt[k]), float(B[k].quantile(0.05)), float(B[k].quantile(0.95))] for k in pt}


def side_summary(F: pd.DataFrame) -> dict:
    s = dict(n=int(len(F)), W=int((F.result == 'win').sum()), L=int((F.result == 'loss').sum()),
             D=int((F.result == 'draw').sum()), win=float(F.win.mean()),
             reached=int(F.rl.sum()), q_cond=float(F[F.rl == 1].q_alive.mean()) if F.rl.sum() else None,
             q_joint=float(F.q_joint.mean()), q_dec_W=int(((F.q_dec == 1) & (F.result == 'win')).sum()),
             q_dec_L=int(((F.q_dec == 1) & (F.result == 'loss')).sum()),
             conv=float(F[F.rl == 1].win.mean()) if F.rl.sum() else None)
    for c in ECON + MAT + HYG + SIDE:
        if c in F:
            s[c] = float(F[c].mean())
    return s


def compare(cand: str, parent: str, panel: str, seeds: list[int]) -> dict:
    Fc, mc = load_arm(cand, panel, seeds)
    Fp, mp = load_arm(parent, panel, seeds)
    out = dict(panel=panel, cand=cand, parent=parent, seeds=seeds,
               meta=dict(cand={k: mc.get(k) for k in ('fingerprint', 'runtime', 'panel_hash', 'host', 'expected')},
                         parent={k: mp.get(k) for k in ('fingerprint', 'runtime', 'panel_hash', 'host', 'expected')}),
               missing=dict(cand=mc['missing'], parent=mp['missing']))
    if Fc.empty or Fp.empty:
        out['status'] = 'INCOMPLETE'
        return out
    normalise(Fc, Fp)
    cols = ['win', 'econ', 'rl', 'q_alive', 'q_joint', 'q_dec', 'result', 'cls'] + [c + '|n' for c in ECON + MAT] + HYG
    m = Fc[KEY + cols].merge(Fp[KEY + cols], on=KEY, suffixes=('_c', '_p'))
    out['paired'] = int(len(m))
    out['summary'] = dict(cand=side_summary(Fc[Fc.set_index(KEY).index.isin(m.set_index(KEY).index)]),
                          parent=side_summary(Fp[Fp.set_index(KEY).index.isin(m.set_index(KEY).index)]))
    out['boot'] = bootstrap(m)
    t2 = {}
    for h in HYG:
        p, c = m[h + '_p'].mean(), m[h + '_c'].mean()
        t2[h] = dict(parent=float(p), cand=float(c), rel=float(c / p - 1) if p > 0 else None,
                     flag=bool(p > 0.05 and c > 1.10 * p) or bool(h == 'death_invalid_per1k' and p == 0 and c > 0))
    out['tier2'] = t2
    rows = []
    for (mk, cls), g in m.groupby(['mapkey', 'cls_c']):
        rows.append(dict(map=mk, cls=cls, n=len(g), W=int((g.result_c == 'win').sum()), L=int((g.result_c == 'loss').sum()),
                         dwin=float((g.win_c - g.win_p).mean()), decon=float((g.econ_c - g.econ_p).mean()),
                         dq_joint=float((g.q_joint_c - g.q_joint_p).mean()),
                         q_alive_rl=f"{int((g.q_joint_c).sum())}/{int(g.rl_c.sum())} vs {int((g.q_joint_p).sum())}/{int(g.rl_p.sum())}",
                         dwall=float((g.death_wall_per1k_c - g.death_wall_per1k_p).mean())))
    out['per_map'] = rows
    out['per_class'] = [dict(cls=k, n=len(g), dwin=float((g.win_c - g.win_p).mean()), decon=float((g.econ_c - g.econ_p).mean()),
                             dq_joint=float((g.q_joint_c - g.q_joint_p).mean()),
                             dwall=float((g.death_wall_per1k_c - g.death_wall_per1k_p).mean()))
                        for k, g in m.groupby('cls_c')]
    out['status'] = 'COMPLETE' if not (mc['missing'] or mp['missing']) else 'PARTIAL'
    return out


def gate_letter(pool: dict, gen: dict, seeds: list[int]) -> tuple[str, list[str]]:
    why, fail = [], False
    if pool.get('status') == 'INCOMPLETE' or gen.get('status') == 'INCOMPLETE':
        return 'INCOMPLETE', ['a panel has no paired games']
    def chk(name, b, key, thr, strict):
        nonlocal fail
        pt, lo, hi = b[key]
        ok = lo > thr if strict else lo >= thr
        if not ok:
            why.append(f'{name} {key} {pt:+.4f} [{lo:+.4f}, {hi:+.4f}] vs {thr:+.2f}')
            if hi < thr:
                fail = True
        return ok
    pb, gb = pool['boot'], gen['boot']
    ok = chk('pool', pb, 'win', 0.0, True)
    if pb['win'][2] < 0:
        fail = True
    ok &= chk('gen', gb, 'win', -0.02, True)
    for nm, b in (('pool', pb), ('gen', gb)):
        ok &= chk(nm, b, 'econ', -0.03, True)
        ok &= chk(nm, b, 'units@100', -0.02, False)
        ok &= chk(nm, b, 'total@100', -0.02, False)
    for nm, c in (('pool', pool), ('gen', gen)):
        flags = [h for h, v in c['tier2'].items() if v['flag']]
        if flags:
            ok = False; fail = True; why.append(f'{nm} tier-2 up: {flags}')
    if pool.get('status') != 'COMPLETE' or gen.get('status') != 'COMPLETE':
        why.append('missing fixtures (listed; not counted)')
    letter = 'PASS' if ok else 'FAIL' if fail else 'HOLD'
    prefix = '' if len(seeds) >= 3 else 'screen-'
    return prefix + letter, why


def fmt_iv(v, pct=True):
    k = 100 if pct else 1
    return f'{k * v[0]:+.2f} [{k * v[1]:+.2f}, {k * v[2]:+.2f}]'


def markdown(cards: dict, letter: str, why: list[str]) -> str:
    L = []
    any_c = next(iter(cards.values()))
    L.append(f"# {any_c['cand']} vs {any_c['parent']} — seeds {','.join(map(str, any_c['seeds']))}\n")
    L.append(f'**Gate letter: {letter}**' + (' — ' + '; '.join(why) if why else '') + '\n')
    L.append('Intervals: cluster bootstrap (map×opp×seat), 1,000 resamples, seed 7, 5th–95th percentile. '
             'Win, queen and conversion in percentage points; economy and material as normalised units ×100.\n')
    for panel, c in cards.items():
        L.append(f'## {panel}\n')
        if c.get('status') == 'INCOMPLETE':
            L.append('INCOMPLETE: no paired games.\n'); continue
        s, b = c['summary'], c['boot']
        L.append(f"Paired fixtures {c['paired']} (cand expected {c['meta']['cand']['expected']}, missing cand "
                 f"{len(c['missing']['cand'])}, parent {len(c['missing']['parent'])}). Status {c['status']}.\n")
        L.append('| | cand | parent |\n|---|---|---|')
        for k in ('W', 'L', 'D', 'win', 'reached', 'q_cond', 'q_joint', 'q_dec_W', 'q_dec_L', 'conv') + tuple(ECON + MAT):
            f = lambda v: '—' if v is None else f'{v:.4f}' if isinstance(v, float) else str(v)
            L.append(f"| {k} | {f(s['cand'].get(k))} | {f(s['parent'].get(k))} |")
        L.append('\n| Δ | point [90 %] |\n|---|---|')
        for k in ('win', 'econ', 'econ_med', 'units@100', 'total@100', 'q_joint', 'q_cond', 'conv'):
            L.append(f'| {k} | {fmt_iv(b[k])} |')
        L.append(f"| death_wall_per1k | {fmt_iv(b['death_wall_per1k'], False)} |")
        L.append('\nTier-2 deaths per 1k dragon-turns:\n\n| cause | parent | cand | rel | flag |\n|---|---|---|---|---|')
        for h, v in c['tier2'].items():
            rel = '—' if v['rel'] is None else f"{100 * v['rel']:+.1f}%"
            L.append(f"| {h} | {v['parent']:.3f} | {v['cand']:.3f} | {rel} | {'**yes**' if v['flag'] else ''} |")
        L.append('\nPer class:\n\n| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |\n|---|---|---|---|---|---|')
        for r in c['per_class']:
            L.append(f"| {r['cls']} | {r['n']} | {100 * r['dwin']:+.2f} | {100 * r['decon']:+.2f} | {100 * r['dq_joint']:+.2f} | {r['dwall']:+.3f} |")
        L.append('\nPer map:\n\n| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |\n|---|---|---|---|---|---|---|---|')
        for r in c['per_map']:
            L.append(f"| {r['map']} | {r['cls']} | {r['n']} | {r['W']}-{r['L']} | {100 * r['dwin']:+.2f} | {100 * r['decon']:+.2f} | {r['q_alive_rl']} | {r['dwall']:+.3f} |")
        if c['missing']['cand'] or c['missing']['parent']:
            L.append('\nMissing (not counted): cand ' + ', '.join(c['missing']['cand'][:30]) +
                     ('…' if len(c['missing']['cand']) > 30 else '') + '; parent ' + ', '.join(c['missing']['parent'][:30]))
        L.append(f"\nRuntime / fingerprint: cand `{c['meta']['cand']['runtime']}` `{(c['meta']['cand']['fingerprint'] or '')[:12]}` "
                 f"panel `{c['meta']['cand']['panel_hash']}`; parent `{c['meta']['parent']['runtime']}` "
                 f"`{(c['meta']['parent']['fingerprint'] or '')[:12]}` panel `{c['meta']['parent']['panel_hash']}`.\n")
    return '\n'.join(L) + '\n'


def cmd_card(a):
    seeds = [int(s) for s in a.seeds.split(',')]
    cards = {p: compare(a.cand, a.parent, p, seeds) for p in ('pool', 'gen')}
    letter, why = gate_letter(cards['pool'], cards['gen'], seeds)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix('.json').write_text(json.dumps(dict(letter=letter, why=why, cards=cards), indent=1, default=float))
    out.with_suffix('.md').write_text(markdown(cards, letter, why))
    print(letter, why)


def cmd_curve(a):
    seeds = [int(s) for s in a.seeds.split(',')]
    doses = [d.split(':', 1) for d in a.doses.split(',')]
    parent = doses[0][1]
    L = [f'# Dose curve, parent {parent} (dose {doses[0][0]}), seeds {a.seeds}\n',
         'Each row: dose arm vs dose-0 parent, paired; cluster bootstrap 90 % (see card.py header).\n']
    res = {}
    for panel in ('pool', 'gen'):
        L.append(f'## {panel}\n\n| dose | bot | paired | Δwin pp | Δecon ×100 | Δunits@100 | Δtotal@100 | Δq_joint pp | Δq_cond pp | Δconv pp | Δwall/1k |\n|---|---|---|---|---|---|---|---|---|---|---|')
        for dose, bot in doses[1:]:
            c = compare(bot, parent, panel, seeds)
            res[f'{panel}:{dose}'] = c
            if c.get('status') == 'INCOMPLETE':
                L.append(f'| {dose} | {bot} | INCOMPLETE |'); continue
            b = c['boot']
            L.append(f"| {dose} | {bot} | {c['paired']} | {fmt_iv(b['win'])} | {fmt_iv(b['econ'])} | {fmt_iv(b['units@100'])} | "
                     f"{fmt_iv(b['total@100'])} | {fmt_iv(b['q_joint'])} | {fmt_iv(b['q_cond'])} | {fmt_iv(b['conv'])} | {fmt_iv(b['death_wall_per1k'], False)} |")
        L.append('')
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix('.json').write_text(json.dumps(res, indent=1, default=float))
    out.with_suffix('.md').write_text('\n'.join(L) + '\n')
    print('\n'.join(L))


def cmd_parity(a):
    """Golden parity at panel level: every fixture's winner and round count identical (index rows, rc 0)."""
    seeds = [int(x) for x in a.seeds.split(',')]
    def rows(bot):
        root = P.run_root(bot, a.panel)
        return {r['game'].replace(bot, '@'): r for r in map(json.loads, open(root / 'index.jsonl')) if r.get('rc') == 0}
    c, p = rows(a.cand), rows(a.parent)
    exp = {f['game'].replace('X', '@') for f in P.fixtures('X', a.panel, seeds)}
    both = sorted(exp & set(c) & set(p))
    diff = [g for g in both if (c[g]['winner'], c[g]['rounds']) != (p[g]['winner'], p[g]['rounds'])]
    res = dict(cand=a.cand, parent=a.parent, panel=a.panel, expected=len(exp), compared=len(both), divergent=len(diff),
               divergent_games=diff[:50], verdict='PARITY' if both and not diff and len(both) == len(exp) else 'NO-PARITY' if diff else 'INCOMPLETE')
    print(json.dumps(res, indent=1))
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True); Path(a.out).write_text(json.dumps(res, indent=1))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('card'); c.add_argument('cand'); c.add_argument('--parent', required=True)
    c.add_argument('--seeds', default='1'); c.add_argument('--out', required=True)
    d = sub.add_parser('curve'); d.add_argument('--doses', required=True); d.add_argument('--seeds', default='1')
    d.add_argument('--out', required=True)
    q = sub.add_parser('parity'); q.add_argument('cand'); q.add_argument('--parent', required=True)
    q.add_argument('--panel', default='pool'); q.add_argument('--seeds', default='1'); q.add_argument('--out')
    a = ap.parse_args()
    {'card': cmd_card, 'curve': cmd_curve, 'parity': cmd_parity}[a.cmd](a)


if __name__ == '__main__':
    main()
