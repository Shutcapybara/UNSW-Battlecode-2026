"""Periodic analysis of the live record (Part B §9.3–§9.4, day-one form): stage profiles, loss decomposition,
per-map paired deltas of the running experiment, and the conversion-funnel proxies that the stored per-game stage
statistics allow. Pure functions over hub `games` rows; recomputed every cycle and written into the tick and packet.

The A1 statistics (loss anatomy, exact-pair contrasts, layout rule, runtime, sonar) live in `analysis_a1.py` and are
merged into the same result by `run()`; see `docs/analysis/ATLAS.md`.
"""
import json
import statistics
from collections import defaultdict

STAGES = (100, 200, 250, 300, 320, 360, 380, 400, 450, 499)

COMPACT = {'Portals', 'Prisoners Dilemma', 'Devil', 'Trophy'}          # <= 625 tiles on the live pool
STAGE_KEYS = ('units', 'total', 'longest', 'deaths', 'death_wall', 'death_h2h', 'newborn_deaths_10', 'splits', 'sonar', 'turns', 'portal_steps', 'pearls', 'length_lost')


def med(values):
    values = [v for v in values if v is not None]
    return round(statistics.median(values), 1) if values else None


def stage(row, r, key):
    try:
        return row['stages'][str(r)][key]
    except (KeyError, TypeError):
        return None


def opp_stage(row, r, key):
    try:
        return row['opponent_stages'][str(r)][key]
    except (KeyError, TypeError):
        return None


def per_1k(row, key, r=499):
    d = stage(row, r, key)
    t = stage(row, r, 'turns')
    return round(1000 * d / t, 1) if d is not None and t else None


def profile(rows):
    """Stage profile of one submission (medians over verified controlled games) plus loss decomposition."""
    n = len(rows)
    if not n:
        return None
    losses = [x for x in rows if (x.get('score') or 0) == 0]
    elim = [x for x in losses if x.get('reason') == 'elimination']
    rl = [x for x in losses if x.get('reason') == 'roundLimit']
    wins = [x for x in rows if (x.get('score') or 0) == 1]
    out = dict(
        n=n, share=round(sum(x.get('score') or 0 for x in rows) / n, 2),
        units_r100=med([stage(x, 100, 'units') for x in rows]), total_r250=med([stage(x, 250, 'total') for x in rows]),
        longest_r400=med([stage(x, 400, 'longest') for x in rows]), longest_r499=med([stage(x, 499, 'longest') for x in rows]),
        opp_units_r100=med([opp_stage(x, 100, 'units') for x in rows]), opp_longest_r400=med([opp_stage(x, 400, 'longest') for x in rows]),
        splits_r100=med([stage(x, 100, 'splits') for x in rows]), portal_steps=med([stage(x, 499, 'portal_steps') for x in rows]),
        wall_deaths_per_1k=med([per_1k(x, 'death_wall') for x in rows]), h2h_deaths_per_1k=med([per_1k(x, 'death_h2h') for x in rows]),
        newborn_deaths_10=med([stage(x, 499, 'newborn_deaths_10') for x in rows]), length_lost=med([stage(x, 499, 'length_lost') for x in rows]),
        sonar_per_turn=med([round(stage(x, 499, 'sonar') / stage(x, 499, 'turns'), 2) for x in rows if stage(x, 499, 'turns')]),
        cpu_max=max((x.get('cpu_max') or 0) for x in rows), faults=sum((x.get('faults') or 0) for x in rows),
        losses=len(losses), losses_elimination=len(elim), losses_roundlimit=len(rl),
        elimination_round_median=med([x.get('rounds') for x in elim]),
        roundlimit_longest_margin_median=med([x.get('longest_margin') for x in rl]),
        win_longest_margin_median=med([x.get('longest_margin') for x in wins]),
    )
    by_class = {}
    for cls, sel in (('compact', lambda x: x.get('map_name') in COMPACT), ('open', lambda x: x.get('map_name') not in COMPACT)):
        sub = [x for x in rows if sel(x)]
        if sub:
            by_class[cls] = dict(n=len(sub), share=round(sum(s.get('score') or 0 for s in sub) / len(sub), 2),
                                 eliminations=sum(1 for s in sub if (s.get('score') or 0) == 0 and s.get('reason') == 'elimination'),
                                 units_r100=med([stage(s, 100, 'units') for s in sub]), longest_r400=med([stage(s, 400, 'longest') for s in sub]))
    out['by_class'] = by_class
    return out


def submission_profiles(games, min_games=10):
    by_sub = defaultdict(list)
    for g in games:
        if g.get('verified') and g.get('origin') == 'controlled' and g.get('pool') == 'field':
            by_sub[g['own_submission']].append(g)
    return {str(sub): profile(rows) for sub, rows in by_sub.items() if len(rows) >= min_games}


def experiment_contrast(games, candidate, control):
    """Stage deltas (candidate − control) over the two arms' verified field games, and per-map score deltas."""
    arms = {candidate: [], control: []}
    for g in games:
        if g.get('verified') and g.get('origin') == 'controlled' and g.get('pool') == 'field' and g.get('own_submission') in arms:
            arms[g['own_submission']].append(g)
    if not arms[candidate] or not arms[control]:
        return None
    pc, pk = profile(arms[candidate]), profile(arms[control])
    keys = ('share', 'units_r100', 'total_r250', 'longest_r400', 'longest_r499', 'wall_deaths_per_1k', 'h2h_deaths_per_1k', 'newborn_deaths_10', 'portal_steps', 'sonar_per_turn')
    delta = {k: (round(pc[k] - pk[k], 2) if pc.get(k) is not None and pk.get(k) is not None else None) for k in keys}
    per_map = defaultdict(lambda: {candidate: [], control: []})
    for sub, rows in arms.items():
        for g in rows:
            per_map[g.get('map_name')][sub].append(g.get('score') or 0)
    map_delta = {m: round(sum(v[candidate]) / len(v[candidate]) - sum(v[control]) / len(v[control]), 2)
                 for m, v in per_map.items() if v[candidate] and v[control]}
    ranked = sorted(map_delta.items(), key=lambda kv: kv[1])
    return dict(candidate=dict(n=pc['n'], share=pc['share']), control=dict(n=pk['n'], share=pk['share']), delta=delta, map_delta=map_delta,
                worst_maps=ranked[:2], best_maps=ranked[-2:], candidate_losses=dict(elimination=pc['losses_elimination'], roundlimit=pc['losses_roundlimit']),
                control_losses=dict(elimination=pk['losses_elimination'], roundlimit=pk['losses_roundlimit']))


def opponent_table(games):
    """Win share of each of our submissions against each opponent, field controlled games only."""
    cells = defaultdict(list)
    for g in games:
        if g.get('verified') and g.get('origin') == 'controlled' and g.get('pool') == 'field':
            cells[(g['own_submission'], g['opponent_team'])].append(g.get('score') or 0)
    return [dict(submission=s, opponent=o, n=len(v), share=round(sum(v) / len(v), 2)) for (s, o), v in sorted(cells.items(), key=lambda kv: (-kv[0][0], kv[0][1]))]


def load_games(conn):
    out = []
    for row in conn.execute('SELECT game_id, own_submission, opponent_team, opponent_submission, map_id, map_name, map_hash, api_side, pool, origin, verified, score, '
                            'longest_margin, rounds, reason, faults, cpu_max, cpu_recorded, turns, block_id, experiment_id, phase, stages, opponent_stages FROM games'):
        g = dict(row)
        for k in ('stages', 'opponent_stages'):
            try:
                g[k] = json.loads(g[k]) if isinstance(g[k], str) else g[k]
            except ValueError:
                g[k] = None
        out.append(g)
    return out


def run(conn, experiments):
    games = load_games(conn)
    result = dict(profiles=submission_profiles(games), opponents=opponent_table(games), contrasts={})
    for e in experiments:
        if e.get('status') == 'running' and e.get('candidate') and e.get('control'):
            c = experiment_contrast(games, e['candidate'], e['control'])
            if c:
                result['contrasts'][e['id']] = c
    try:
        from . import analysis_a1
        result.update(analysis_a1.run(games, experiments))
    except Exception as exc:  # the A1 block must never stop the cycle
        result['a1_error'] = repr(exc)[:200]
    return result


def packet_lines(analysis, incumbent=None):
    """Compact, ≤ 60 lines for packet §4 (≤ 40 here plus ≤ 20 from analysis_a1)."""
    L = ['- Stage profiles (medians over verified field games; deaths per 1k turns):', '',
         '| submission | n | share | units r100 (opp) | total r250 | longest r400 (opp) | longest r499 | wall/1k | h2h/1k | newborn≤10 | portal steps | losses elim/RL | elim round | RL longest margin |',
         '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for sub, p in sorted(analysis['profiles'].items(), key=lambda kv: -int(kv[0]))[:8]:
        L.append(f"| {sub}{' *' if str(incumbent) == sub else ''} | {p['n']} | {p['share']} | {p['units_r100']} ({p['opp_units_r100']}) | {p['total_r250']} | {p['longest_r400']} ({p['opp_longest_r400']}) | {p['longest_r499']} | {p['wall_deaths_per_1k']} | {p['h2h_deaths_per_1k']} | {p['newborn_deaths_10']} | {p['portal_steps']} | {p['losses_elimination']}/{p['losses_roundlimit']} | {p['elimination_round_median']} | {p['roundlimit_longest_margin_median']} |")
    for sub, p in sorted(analysis['profiles'].items(), key=lambda kv: -int(kv[0]))[:3]:
        bc = p.get('by_class') or {}
        if bc:
            L.append(f"- {sub} by map class: " + '; '.join(f"{cls} n={v['n']} share {v['share']} eliminations {v['eliminations']} units r100 {v['units_r100']} longest r400 {v['longest_r400']}" for cls, v in bc.items()))
    for eid, c in analysis['contrasts'].items():
        d = c['delta']
        L.append(f"- Running experiment {eid[:8]} contrast (candidate − control, field games so far; candidate n={c['candidate']['n']} share {c['candidate']['share']}, control n={c['control']['n']} share {c['control']['share']}): "
                 + ', '.join(f"{k} {v:+}" for k, v in d.items() if v is not None))
        L.append(f"  losses candidate elim/RL {c['candidate_losses']['elimination']}/{c['candidate_losses']['roundlimit']} vs control {c['control_losses']['elimination']}/{c['control_losses']['roundlimit']}; worst maps {c['worst_maps']}; best maps {c['best_maps']}")
    L = L[:40]
    try:
        from . import analysis_a1
        L.extend(analysis_a1.packet_lines(analysis))
    except Exception as exc:  # pragma: no cover - packet must always render
        L.append(f'- A1 statistics unavailable: {exc!r}'[:160])
    return L[:60]
