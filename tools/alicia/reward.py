"""Alicia (RL-1) reward: the benchmark curve term, the churn/hygiene guards and the terminal term.

Design and justification: docs/findings/2026-09-30-alicia-rl-design.md §0.2.

    C = 1/2 mean(pct p@50, p@100, p@150, p@250) + 1/4 pct units@100 + 1/4 pct total@100
    T = 1/2 win + 1/2 total_share@250
    P = sum_g max(0, rate_g / rate_g(parent) - 1.10)       (per policy, rates aggregated over its fixtures)
        g in {avoidable (wall+self+ally body+ally h2h), ally churn (ally body+ally h2h; L29), newborn deaths}:
        pooled groups, because per-rate counts over one generation's ~20 games are Poisson-noisy (~15 %);
        the D-032 gate still checks every rate separately.
    R = mean_fixtures[(1 - beta) C + beta T] - P

pct is the mid-rank percentile among field sides on the same map (docs/analysis/benchmarks/field_distributions.json).
A map without field references uses the base's own per-map medians (tools/alicia/base_refs.json) mapped onto the
pooled field scale: pct = F_pool(x / (median_base(map) / rho)), rho = the base's pool-median ratio to the field median.
"""
from __future__ import annotations

import bisect, json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BENCH = ROOT / 'docs/analysis/benchmarks'
BASE_REFS = Path(__file__).with_name('base_refs.json')

ECON = ['pearls@50', 'pearls@100', 'pearls@150', 'pearls@250']
MAT = ['units@100', 'total@100']
CURVE = ECON + MAT
REPORT = CURVE + ['births@100', 'top1_share@100', 'total_share@250']
# guard rates: per 1k dragon-turns (the first four), per 100 births (newborn)
GUARDS = ['death_wall_per1k', 'death_self_per1k', 'death_ally_body_per1k', 'death_h2h_ally_per1k',
          'newborn_deaths10_per100']
GUARD_FREE = 1.10
GROUPS = {'g_avoidable_per1k': GUARDS[:4], 'g_ally_churn_per1k': ['death_ally_body_per1k', 'death_h2h_ally_per1k'],
          'g_newborn_per100': ['newborn_deaths10_per100']}


def mid_pct(dist, x):
    lo, hi = bisect.bisect_left(dist, x), bisect.bisect_right(dist, x)
    return (lo + (hi - lo) / 2) / len(dist)


class Curve:
    def __init__(self):
        raw = json.load(open(BENCH / 'field_distributions.json'))
        refs = json.load(open(BENCH / 'field_references.json'))
        self.dist = {s: {m: sorted(v) for m, v in raw[s].items()} for s in CURVE}
        self.median = {s: {m: refs[s][m]['median'] for m in refs[s]} for s in CURVE}
        # pooled field scale: every field side's value / its map's field median, over the reference maps
        self.pooled = {}
        for s in CURVE:
            v = []
            for m, d in self.dist[s].items():
                med = self.median[s].get(m)
                if med:
                    v += [x / med for x in d]
            self.pooled[s] = sorted(v)
        self.base = json.load(open(BASE_REFS)) if BASE_REFS.exists() else {}

    def has_field(self, field_map):
        return field_map in self.dist['pearls@100']

    def pct(self, s, x, field_map, map_key):
        """(percentile, source) for statistic s of one side-game; source 'field' | 'base' | None."""
        if x is None or (isinstance(x, float) and math.isnan(x)):
            return None, None
        if field_map in self.dist[s]:
            return mid_pct(self.dist[s][field_map], x), 'field'
        b = self.base.get('maps', {}).get(map_key, {}).get(s)
        rho = self.base.get('rho', {}).get(s)
        if b and rho:
            return mid_pct(self.pooled[s], x / (b / rho)), 'base'
        return None, None

    def curve_terms(self, row):
        """row: an env metric row. Returns {'C': .., 'pct': {s: p}, 'src': ..} or None if the map has no reference."""
        pc, src = {}, set()
        for s in CURVE:
            p, where = self.pct(s, row.get(s), row.get('field_map'), row['map'])
            if p is None:
                return None
            pc[s] = p; src.add(where)
        C = 0.5 * sum(pc[s] for s in ECON) / 4 + 0.25 * pc['units@100'] + 0.25 * pc['total@100']
        return {'C': C, 'pct': pc, 'src': '+'.join(sorted(src))}


def terminal(row):
    w = row.get('won')
    sh = row.get('total_share@250')
    if w is None or sh is None or (isinstance(sh, float) and math.isnan(sh)):
        return None
    return 0.5 * w + 0.5 * sh


def agg_rates(rows):
    """dragon-turn / birth weighted guard rates over a policy's fixtures."""
    dt = sum(r.get('dragon_turns') or 0 for r in rows)
    br = sum(r.get('births') or 0 for r in rows)
    out = {}
    for g in GUARDS:
        if g.endswith('per100'):
            num = sum((r.get(g) or 0) * (r.get('births') or 0) / 100 for r in rows)
            out[g] = 100 * num / br if br else 0.0
        else:
            num = sum((r.get(g) or 0) * (r.get('dragon_turns') or 0) / 1000 for r in rows)
            out[g] = 1000 * num / dt if dt else 0.0
    for k, parts in GROUPS.items():
        out[k] = sum(out[g] for g in parts)
    return out


def penalty(rates, parent_rates):
    p, parts = 0.0, {}
    for g in GROUPS:
        b = parent_rates.get(g) or 0.0
        if b <= 0:
            continue
        x = max(0.0, rates[g] / b - GUARD_FREE)
        parts[g] = round(x, 4); p += x
    return p, parts


def policy_reward(rows, parent_rows, beta, curve):
    """rows/parent_rows: env rows of one policy / the parent on the same fixtures (paired by fixture key).
    Returns a summary dict with R and its parts."""
    cs, ts, pcs = [], [], {s: [] for s in CURVE}
    for r in rows:
        ct = curve.curve_terms(r)
        t = terminal(r)
        if ct is None or t is None:
            continue
        cs.append(ct['C']); ts.append(t)
        for s in CURVE:
            pcs[s].append(ct['pct'][s])
    if not cs:
        return None
    C, T = sum(cs) / len(cs), sum(ts) / len(ts)
    rates = agg_rates(rows)
    P, parts = penalty(rates, agg_rates(parent_rows)) if parent_rows else (0.0, {})
    out = {'R': (1 - beta) * C + beta * T - P, 'C': C, 'T': T, 'P': P, 'P_parts': parts, 'n': len(cs),
           'win': sum(r['won'] for r in rows) / len(rows), 'rates': {k: round(v, 3) for k, v in rates.items()}}
    for s in CURVE:
        out['pct_' + s] = sum(pcs[s]) / len(pcs[s])
    for s in REPORT:
        v = [r[s] for r in rows if r.get(s) is not None and not (isinstance(r[s], float) and math.isnan(r[s]))]
        out['mean_' + s] = sum(v) / len(v) if v else None
    return out
