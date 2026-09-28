"""Recurring A1 statistics over hub `games` rows (analysis handoff A1, 28 Sep 2026): loss anatomy (Q1), exact-pair
candidate-minus-control contrasts (Q2), the starting-layout rule (Q3), runtime (Q6) and sonar (Q7) tables.

Pure functions; `tools/hub/analysis.run` calls `run()` every cycle and `packet_lines()` for packet §4. Conventions:
terminal outcomes for eliminated sides (stage fields carry the final state forward), missing fields stay missing,
statistics pool only within one submission and are stratified by opponent submission where the packet shows them.
The heavy one-off versions of these analyses live under `tools/analysis/`; see `docs/analysis/ATLAS.md`.
"""
import math
import statistics
from collections import defaultdict

from .analysis import COMPACT, STAGES, med, stage, opp_stage, per_1k

DEATH_CAUSES = ('death_wall', 'death_self', 'death_body', 'death_h2h')
NEAR_CAP_POINTS, CAP_POINTS = 90_000_000, 100_000_000


def quantile(values, q):
    values = sorted(v for v in values if v is not None)
    if not values:
        return None
    pos = (len(values) - 1) * q
    lo, hi = int(math.floor(pos)), int(math.ceil(pos))
    return round(values[lo] + (values[hi] - values[lo]) * (pos - lo), 1)


def map_class(row):
    return 'compact' if row.get('map_name') in COMPACT else 'open'


def controlled(games, side='A'):
    """Verified controlled games of one API side (field and dev pools); the A-side is the only sample with n."""
    return [g for g in games if g.get('verified') and g.get('origin') == 'controlled' and (side is None or g.get('api_side') == side)]


def sign_test_p(better, worse):
    """Exact two-sided binomial test of better vs worse discordant pairs (ties dropped); None with no discordance."""
    n = better + worse
    if n == 0:
        return None
    k = min(better, worse)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return round(min(1.0, 2 * tail), 3)


# ----------------------------------------------------------------------------------------------------------------
# A1 Q1: loss anatomy
# ----------------------------------------------------------------------------------------------------------------

def first_behind(row, key='total'):
    """First stored stage at which our side trails the opponent on `key`; 'never' if it never does; None if unknown.
    The earliest stored stage is r100, so 100 means 'by r100', not 'at r100'."""
    for r in STAGES:
        a, b = stage(row, r, key), opp_stage(row, r, key)
        if a is None or b is None:
            return None
        if a < b:
            return r
    return 'never'


def lead_at(row, r=100, key='total'):
    a, b = stage(row, r, key), opp_stage(row, r, key)
    if a is None or b is None:
        return None
    return 'ahead' if a > b else ('behind' if a < b else 'level')


def death_rates(rows):
    """Median deaths per 1k dragon-turns by cause over rows (terminal state of every game, eliminated sides included)."""
    out = {c: med([per_1k(x, c) for x in rows]) for c in DEATH_CAUSES}
    out['newborn_deaths_10'] = med([stage(x, 499, 'newborn_deaths_10') for x in rows])
    return out


def survival(rows, side='own'):
    """Share of games in which the side still has units at each stored stage."""
    f = stage if side == 'own' else opp_stage
    out = {}
    for r in STAGES:
        vals = [f(x, r, 'units') for x in rows]
        vals = [v for v in vals if v is not None]
        out[str(r)] = round(sum(1 for v in vals if v > 0) / len(vals), 2) if vals else None
    return out


def loss_anatomy(games, submission, min_games=20, side='A'):
    """Q1: where and when one submission loses, on its verified controlled games of one API side (field and dev).
    Returns None below `min_games`. Every number is a per-game statistic; opponents are stratified by submission id."""
    rows = [g for g in controlled(games, side) if g.get('own_submission') == submission]
    if len(rows) < min_games:
        return None
    losses = [x for x in rows if (x.get('score') or 0) == 0]
    wins = [x for x in rows if (x.get('score') or 0) == 1]
    elim = [x for x in losses if x.get('reason') == 'elimination']
    rl = [x for x in losses if x.get('reason') == 'roundLimit']
    out = dict(submission=submission, n=len(rows), share=round(sum(x.get('score') or 0 for x in rows) / len(rows), 3), side=side,
               wins=len(wins), losses=len(losses), losses_elimination=len(elim), losses_roundlimit=len(rl),
               elimination_round=dict(median=med([x.get('rounds') for x in elim]), q25=quantile([x.get('rounds') for x in elim], 0.25),
                                      q75=quantile([x.get('rounds') for x in elim], 0.75),
                                      compact=med([x.get('rounds') for x in elim if map_class(x) == 'compact']),
                                      open=med([x.get('rounds') for x in elim if map_class(x) == 'open'])),
               roundlimit_loss_longest_margin=dict(median=med([x.get('longest_margin') for x in rl]), q25=quantile([x.get('longest_margin') for x in rl], 0.25),
                                                   q75=quantile([x.get('longest_margin') for x in rl], 0.75)),
               win_reasons=dict(elimination=sum(1 for x in wins if x.get('reason') == 'elimination'), roundlimit=sum(1 for x in wins if x.get('reason') == 'roundLimit')))
    # by map class and by opponent submission
    by_class, by_opp = {}, {}
    for cls in ('compact', 'open'):
        sub = [x for x in rows if map_class(x) == cls]
        if sub:
            by_class[cls] = dict(n=len(sub), share=round(sum(s.get('score') or 0 for s in sub) / len(sub), 2),
                                 losses_elimination=sum(1 for s in sub if (s.get('score') or 0) == 0 and s.get('reason') == 'elimination'),
                                 losses_roundlimit=sum(1 for s in sub if (s.get('score') or 0) == 0 and s.get('reason') == 'roundLimit'),
                                 survival_own=survival(sub, 'own'), survival_opp=survival(sub, 'opp'))
    for key in sorted({(x.get('opponent_team'), x.get('opponent_submission')) for x in rows}, key=lambda k: (str(k[0]), str(k[1]))):
        sub = [x for x in rows if (x.get('opponent_team'), x.get('opponent_submission')) == key]
        by_opp[f'{key[0]}/{key[1]}'] = dict(n=len(sub), share=round(sum(s.get('score') or 0 for s in sub) / len(sub), 2),
                                            losses_elimination=sum(1 for s in sub if (s.get('score') or 0) == 0 and s.get('reason') == 'elimination'),
                                            losses_roundlimit=sum(1 for s in sub if (s.get('score') or 0) == 0 and s.get('reason') == 'roundLimit'),
                                            units_r100=med([stage(s, 100, 'units') for s in sub]), opp_units_r100=med([opp_stage(s, 100, 'units') for s in sub]),
                                            total_r250=med([stage(s, 250, 'total') for s in sub]), opp_total_r250=med([opp_stage(s, 250, 'total') for s in sub]),
                                            longest_r400=med([stage(s, 400, 'longest') for s in sub]), opp_longest_r400=med([opp_stage(s, 400, 'longest') for s in sub]),
                                            longest_r499=med([stage(s, 499, 'longest') for s in sub]), opp_longest_r499=med([opp_stage(s, 499, 'longest') for s in sub]))
    out['by_class'] = by_class
    out['by_opponent'] = by_opp
    # stage curves for wins vs losses by class
    curves = {}
    for cls in ('compact', 'open'):
        for res, sel in (('win', wins), ('loss', losses)):
            sub = [x for x in sel if map_class(x) == cls]
            if sub:
                curves[f'{cls}_{res}'] = dict(n=len(sub), units_r100=med([stage(x, 100, 'units') for x in sub]), opp_units_r100=med([opp_stage(x, 100, 'units') for x in sub]),
                                             total_r250=med([stage(x, 250, 'total') for x in sub]), opp_total_r250=med([opp_stage(x, 250, 'total') for x in sub]),
                                             longest_r400=med([stage(x, 400, 'longest') for x in sub]), opp_longest_r400=med([opp_stage(x, 400, 'longest') for x in sub]),
                                             longest_r499=med([stage(x, 499, 'longest') for x in sub]), opp_longest_r499=med([opp_stage(x, 499, 'longest') for x in sub]),
                                             deaths_per_1k=death_rates(sub))
    out['curves'] = curves
    # first stage behind on total, for losses and wins
    fb = defaultdict(int)
    for x in losses:
        fb[str(first_behind(x))] += 1
    out['loss_first_behind_total'] = dict(fb)
    fbw = defaultdict(int)
    for x in wins:
        fbw[str(first_behind(x))] += 1
    out['win_first_behind_total'] = dict(fbw)
    # conditional win share given the r100 lead on total, by class
    cond = {}
    for cls in ('compact', 'open'):
        for lead in ('ahead', 'behind'):
            sub = [x for x in rows if map_class(x) == cls and lead_at(x) == lead]
            if sub:
                cond[f'{cls}_{lead}_r100'] = dict(n=len(sub), share=round(sum(s.get('score') or 0 for s in sub) / len(sub), 2))
    out['share_by_r100_lead'] = cond
    return out


def loss_anatomies(games, min_games=20, side='A'):
    subs = sorted({g.get('own_submission') for g in controlled(games, side) if g.get('own_submission') is not None}, reverse=True)
    out = {}
    for s in subs:
        a = loss_anatomy(games, s, min_games=min_games, side=side)
        if a:
            out[str(s)] = a
    return out


# ----------------------------------------------------------------------------------------------------------------
# A1 Q2: candidate-minus-control contrasts on exact pairs
# ----------------------------------------------------------------------------------------------------------------

PAIR_KEYS = ('units_r100', 'total_r250', 'longest_r400', 'longest_r499', 'deaths', 'death_h2h', 'newborn_deaths_10', 'splits', 'sonar', 'cpu_max', 'faults', 'longest_margin')


def _pair_value(row, key):
    if key == 'units_r100':
        return stage(row, 100, 'units')
    if key == 'total_r250':
        return stage(row, 250, 'total')
    if key == 'longest_r400':
        return stage(row, 400, 'longest')
    if key == 'longest_r499':
        return stage(row, 499, 'longest')
    if key in ('deaths', 'death_h2h', 'newborn_deaths_10', 'splits', 'sonar'):
        return stage(row, 499, key)
    return row.get(key)


def exact_pairs(games, candidate, control, experiment_id=None):
    """Exact pairs of one candidate and one control game on (block, map, API side, opponent submission, starting layout).
    Only verified games inside screen/confirmation blocks are paired; when a cell holds several games the earliest of
    each arm is used and the pair is flagged `duplicate`. Unpaired games are reported, never pooled."""
    rows = [g for g in games if g.get('verified') and g.get('block_id') and g.get('own_submission') in (candidate, control)
            and (experiment_id is None or g.get('experiment_id') == experiment_id) and g.get('phase') in ('screen', 'confirmation', None)]
    cells = defaultdict(lambda: {candidate: [], control: []})
    for g in rows:
        cells[(g.get('block_id'), g.get('map_id'), g.get('api_side'), g.get('opponent_submission'), g.get('map_hash'))][g['own_submission']].append(g)
    pairs, unpaired = [], {candidate: 0, control: 0}
    for key, arms in sorted(cells.items(), key=lambda kv: str(kv[0])):
        c, k = sorted(arms[candidate], key=lambda x: x['game_id']), sorted(arms[control], key=lambda x: x['game_id'])
        if not c or not k:
            unpaired[candidate] += len(c)
            unpaired[control] += len(k)
            continue
        c0, k0 = c[0], k[0]
        p = dict(block=key[0], map_id=key[1], map_name=c0.get('map_name'), map_class=map_class(c0), side=key[2], opponent_submission=key[3],
                 opponent_team=c0.get('opponent_team'), layout=(key[4] or '')[:8], candidate_game=c0['game_id'], control_game=k0['game_id'],
                 candidate_score=c0.get('score'), control_score=k0.get('score'), delta=(c0.get('score') or 0) - (k0.get('score') or 0),
                 candidate_reason=c0.get('reason'), control_reason=k0.get('reason'), duplicate=len(c) > 1 or len(k) > 1)
        for kk in PAIR_KEYS:
            a, b = _pair_value(c0, kk), _pair_value(k0, kk)
            p['d_' + kk] = (a - b) if a is not None and b is not None else None
        pairs.append(p)
    return pairs, unpaired


def paired_contrast(games, candidate, control, experiment_id=None):
    """Q2: paired score delta and stage-profile deltas on exact pairs, with the discordant-pair sign test."""
    pairs, unpaired = exact_pairs(games, candidate, control, experiment_id)
    if not pairs:
        return None
    better = sum(1 for p in pairs if p['delta'] > 0)
    worse = sum(1 for p in pairs if p['delta'] < 0)
    same = len(pairs) - better - worse
    out = dict(candidate=candidate, control=control, experiment=experiment_id, pairs=len(pairs), unpaired=unpaired,
               candidate_share=round(sum(p['candidate_score'] or 0 for p in pairs) / len(pairs), 3),
               control_share=round(sum(p['control_score'] or 0 for p in pairs) / len(pairs), 3),
               delta=round(sum(p['delta'] for p in pairs) / len(pairs), 3), better=better, same=same, worse=worse, sign_test_p=sign_test_p(better, worse),
               duplicates=sum(1 for p in pairs if p['duplicate']))
    for group, keyf in (('by_opponent', lambda p: str(p['opponent_team'])), ('by_class', lambda p: p['map_class'])):
        d = defaultdict(list)
        for p in pairs:
            d[keyf(p)].append(p)
        out[group] = {k: dict(n=len(v), delta=round(sum(p['delta'] for p in v) / len(v), 3), better=sum(1 for p in v if p['delta'] > 0), worse=sum(1 for p in v if p['delta'] < 0))
                      for k, v in sorted(d.items())}
    out['stage_deltas'] = {k: dict(median=med([p['d_' + k] for p in pairs]), mean=(round(statistics.mean([p['d_' + k] for p in pairs if p['d_' + k] is not None]), 1)
                                                                                 if any(p['d_' + k] is not None for p in pairs) else None),
                                   n=sum(1 for p in pairs if p['d_' + k] is not None)) for k in PAIR_KEYS}
    flips = [p for p in pairs if p['delta'] != 0]
    agree = sum(1 for p in flips if p.get('d_total_r250') is not None and (p['d_total_r250'] > 0) == (p['delta'] > 0))
    out['flips'] = dict(n=len(flips), total_r250_sign_agrees=agree,
                        rows=[dict(opponent=p['opponent_team'], map=p['map_name'], delta=p['delta'], candidate_reason=p['candidate_reason'], control_reason=p['control_reason'],
                                   d_units_r100=p['d_units_r100'], d_total_r250=p['d_total_r250'], d_longest_r499=p['d_longest_r499'], d_faults=p['d_faults']) for p in flips])
    return out


# ----------------------------------------------------------------------------------------------------------------
# A1 Q3: starting-layout assignment
# ----------------------------------------------------------------------------------------------------------------

def layout_rule(games):
    """Q3: is the starting layout (map_hash) a function of game-id parity per map? For each map, learn the hash seen for
    each parity and count violations; report the rule status and the pairing consequence for 10-map batches.
    Maps with more than two hashes (Prisoners Dilemma has 6- and 10-dragon versions) are checked at family level:
    a family is the set of hashes seen with one parity; the rule holds when the two parity families are disjoint."""
    by_map = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    for g in games:
        if g.get('verified') and g.get('map_hash') and g.get('game_id') is not None and g.get('map_name'):
            by_map[g['map_name']][g['game_id'] % 2][g['map_hash'][:8]] += 1
    maps, violations, n_games = {}, 0, 0
    for m, par in sorted(by_map.items()):
        even = dict(par.get(0, {}))
        odd = dict(par.get(1, {}))
        overlap = set(even) & set(odd)
        v = sum(min(even[h], odd[h]) for h in overlap)
        violations += v
        n_games += sum(even.values()) + sum(odd.values())
        maps[m] = dict(even=even, odd=odd, hashes=len(set(even) | set(odd)), violations=v, n=sum(even.values()) + sum(odd.values()))
    return dict(n=n_games, maps=maps, violations=violations,
                rule='layout = f(map, game_id parity)' if n_games and violations == 0 else ('not parity-determined' if n_games else 'no data'),
                note='ids are allocated server-wide and sequentially; a 10-map batch gets consecutive ids, so two batches share layouts on every map '
                     'exactly when their first ids have the same parity (an even number of games were created between them by anyone). '
                     'A 20-game request listing the maps as M0..M9,M1..M9,M0 places every map at two positions of opposite parity and yields both layouts '
                     'per map regardless of the start parity.')


# ----------------------------------------------------------------------------------------------------------------
# A1 Q6 / Q7: runtime and sonar
# ----------------------------------------------------------------------------------------------------------------

def first_stage_at_cap(row, cap=CAP_POINTS):
    for r in STAGES:
        v = stage(row, r, 'cpu_max')
        if v is not None and v >= cap:
            return r
    return None


def runtime_table(games, side='A'):
    """Q6: per-submission distribution of the game maximum points per turn, near-cap and at-cap games, faults, and
    the map maxima; from the live record's cpu_max (verified controlled games of one side)."""
    by_sub = defaultdict(list)
    for g in controlled(games, side):
        if g.get('cpu_max') is not None:
            by_sub[g['own_submission']].append(g)
    out = {}
    for sub, rows in sorted(by_sub.items(), key=lambda kv: -kv[0]):
        cpu = [x['cpu_max'] for x in rows]
        by_map = defaultdict(list)
        for x in rows:
            by_map[x.get('map_name')].append(x)
        at_cap = defaultdict(int)
        for x in rows:
            if x['cpu_max'] >= CAP_POINTS:
                at_cap[str(first_stage_at_cap(x))] += 1
        out[str(sub)] = dict(n=len(rows), p50_M=round(statistics.median(cpu) / 1e6, 1), p90_M=round(quantile(cpu, 0.9) / 1e6, 1), max_M=round(max(cpu) / 1e6, 1),
                             near_cap_games=sum(1 for c in cpu if c > NEAR_CAP_POINTS), at_cap_games=sum(1 for c in cpu if c >= CAP_POINTS),
                             faults=sum(x.get('faults') or 0 for x in rows), games_with_faults=sum(1 for x in rows if (x.get('faults') or 0) > 0),
                             metering_complete=all((x.get('cpu_recorded') == x.get('turns')) for x in rows if x.get('turns') is not None),
                             map_max_M={m: round(max(x['cpu_max'] for x in v) / 1e6, 1) for m, v in sorted(by_map.items())},
                             map_faults={m: sum(x.get('faults') or 0 for x in v) for m, v in sorted(by_map.items()) if sum(x.get('faults') or 0 for x in v)},
                             first_stage_at_cap=dict(at_cap))
    return out


def sonar_table(games, side='A'):
    """Q7: rays per dragon-turn by submission (median, q10, q90 over games, r100 window and whole game) and by outcome and class."""
    by_sub = defaultdict(list)
    for g in controlled(games, side):
        if stage(g, 100, 'turns') and stage(g, 499, 'turns') and stage(g, 100, 'sonar') is not None and stage(g, 499, 'sonar') is not None:
            by_sub[g['own_submission']].append(g)
    out = {}
    for sub, rows in sorted(by_sub.items(), key=lambda kv: -kv[0]):
        r100 = [stage(x, 100, 'sonar') / stage(x, 100, 'turns') for x in rows]
        full = [stage(x, 499, 'sonar') / stage(x, 499, 'turns') for x in rows]
        if not full:
            continue
        cell = {}
        for cls in ('compact', 'open'):
            for res, sc in (('win', 1), ('loss', 0)):
                v = [stage(x, 100, 'sonar') / stage(x, 100, 'turns') for x in rows if map_class(x) == cls and (x.get('score') or 0) == sc]
                if v:
                    cell[f'{cls}_{res}'] = dict(n=len(v), rays_per_turn_r100=round(statistics.median(v), 2))
        out[str(sub)] = dict(n=len(rows), rays_per_turn=round(statistics.median(full), 2), q10=round(quantile(full, 0.1), 2), q90=round(quantile(full, 0.9), 2),
                             rays_per_turn_r100=round(statistics.median(r100), 2), identifiable=(quantile(full, 0.9) - quantile(full, 0.1)) > 0.5, by_outcome=cell,
                             opponent_rays_per_turn=med([round(opp_stage(x, 499, 'sonar') / opp_stage(x, 499, 'turns'), 2) for x in rows if opp_stage(x, 499, 'turns') and opp_stage(x, 499, 'sonar') is not None]))
    return out


# ----------------------------------------------------------------------------------------------------------------
# entry points used by tools/hub/analysis.py
# ----------------------------------------------------------------------------------------------------------------

def run(games, experiments):
    """All A1 statistics for one cycle; keys are merged into the tick's `analysis` block."""
    result = dict(pairs={})
    for e in experiments:
        if e.get('candidate') and e.get('control'):
            p = paired_contrast(games, e['candidate'], e['control'], e.get('id'))
            if p:
                result['pairs'][e['id']] = p
    result['anatomy'] = loss_anatomies(games)
    result['layout'] = layout_rule(games)
    result['runtime'] = runtime_table(games)
    result['sonar'] = sonar_table(games)
    return result


def packet_lines(analysis):
    """≤ 20 compact lines appended to packet §4."""
    L = []
    for eid, p in list((analysis.get('pairs') or {}).items())[:6]:
        L.append(f"- Exact pairs {eid[:8]} ({p['candidate']} − {p['control']}): {p['pairs']} pairs, delta {p['delta']:+.3f}, better/same/worse {p['better']}/{p['same']}/{p['worse']}, sign-test p {p['sign_test_p']}; "
                 f"by class " + '; '.join(f"{k} {v['delta']:+.2f} (n={v['n']})" for k, v in p['by_class'].items()) + f"; flips {p['flips']['n']} of which r250-total sign agrees {p['flips']['total_r250_sign_agrees']}; unpaired {p['unpaired']}")
    for sub, a in sorted((analysis.get('anatomy') or {}).items(), key=lambda kv: -kv[1]['n'])[:4]:
        bc, cond = a['by_class'], a['share_by_r100_lead']
        L.append(f"- Loss anatomy {sub} (A-side controlled, n={a['n']}, share {a['share']}): losses elim/RL {a['losses_elimination']}/{a['losses_roundlimit']}, elim round median {a['elimination_round']['median']} "
                 f"(compact {a['elimination_round']['compact']}, open {a['elimination_round']['open']}), RL-loss longest margin {a['roundlimit_loss_longest_margin']['median']}; "
                 f"compact share {bc.get('compact', {}).get('share')} (elim {bc.get('compact', {}).get('losses_elimination')}), open share {bc.get('open', {}).get('share')}; "
                 f"losses already behind on total by r100: {a['loss_first_behind_total'].get('100', 0)}/{a['losses']}; share ahead/behind at r100 compact "
                 f"{cond.get('compact_ahead_r100', {}).get('share')}/{cond.get('compact_behind_r100', {}).get('share')}, open {cond.get('open_ahead_r100', {}).get('share')}/{cond.get('open_behind_r100', {}).get('share')}")
    lay = analysis.get('layout') or {}
    if lay.get('n'):
        L.append(f"- Layout rule: {lay['rule']} over {lay['n']} games, {lay['violations']} violations" + ('' if lay['violations'] == 0 else ' — RULE BROKEN, check the server'))
    rt = analysis.get('runtime') or {}
    if rt:
        L.append('- Runtime (A-side controlled; M points): ' + '; '.join(f"{s} n={v['n']} p50 {v['p50_M']} p90 {v['p90_M']} max {v['max_M']} near-cap {v['near_cap_games']} at-cap {v['at_cap_games']} faults {v['faults']}" for s, v in sorted(rt.items(), key=lambda kv: -kv[1]['n'])[:6]))
    so = analysis.get('sonar') or {}
    if so:
        L.append('- Sonar rays per dragon-turn: ' + '; '.join(f"{s} {v['rays_per_turn']} (q10–q90 {v['q10']}–{v['q90']}, opp {v['opponent_rays_per_turn']})" for s, v in sorted(so.items(), key=lambda kv: -kv[1]['n'])[:6]))
    return L[:20]
