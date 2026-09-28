"""Periodic analysis of the live record (Part B §9.3–§9.4, day-one form): stage profiles, loss decomposition,
per-map paired deltas of the running experiment, and the conversion-funnel proxies that the stored per-game stage
statistics allow. Pure functions over hub `games` rows; recomputed every cycle and written into the tick and packet.
"""
import json
import statistics
from collections import defaultdict

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
    for row in conn.execute('SELECT game_id, own_submission, opponent_team, opponent_submission, map_id, map_name, map_hash, api_side, pool, origin, verified, score, longest_margin, rounds, reason, faults, cpu_max, stages, opponent_stages FROM games'):
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
    # handoff A1 additions (2026-09-28)
    try:
        result['layout_parity'] = layout_parity(games)
        result['runtime'] = runtime_table(games)
        result['sonar'] = sonar_table(games)
        field = [g for g in games if g.get('origin') == 'controlled' and g.get('pool') == 'field' and g.get('verified')]
        result['trailing'] = {sub: trailing_profile(rows) for sub, rows in _by_submission(field).items() if rows}
        result['elo'] = elo_trajectory(_series_payloads(conn))
    except Exception as exc:  # A1 statistics must never stop the cycle
        result['a1_error'] = repr(exc)[:200]
    return result


def _by_submission(games):
    out = defaultdict(list)
    for g in games:
        out[g.get('own_submission')].append(g)
    return out


def _series_payloads(conn):
    try:
        return [json.loads(r['payload']) for r in conn.execute('SELECT payload FROM series') if r['payload']]
    except Exception:
        return []


def packet_lines(analysis, incumbent=None):
    """Compact, ≤ 40 lines for packet §4."""
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
    L.extend(packet_lines_a1(analysis))
    return L[:48]


# --- handoff A1 additions (2026-09-28): layout parity, first-trailing stage, runtime, sonar, elo ----

def layout_parity(games):
    """Starting-layout rule detector (handoff §3.3). For each map, the share of games whose
    map_hash equals the hash implied by their own game_id parity (each map's two hashes labelled
    by first-seen). Returns per-map match rate and exceptions; a map matching ~100% is governed by
    id parity (deterministic fill control), ~50% is coin-flip random."""
    first, seen = {}, {}
    for g in games:
        h, m = g.get('map_hash'), g.get('map_id')
        if not h or m is None:
            continue
        key = (m, h)
        if key not in seen:
            seen[key] = len([1 for k in seen if k[0] == m])  # 0 for first hash, 1 for second, ...
        first.setdefault(m, {})[h] = seen[key]
    per_map = {}
    for m, hashes in first.items():
        if len(hashes) != 2:
            per_map[m] = dict(n_hashes=len(hashes), match_rate=None, note='not a 2-layout map; parity rule not applicable')
            continue
        for flip in (False, True):  # first-seen labelling is arbitrary: accept either polarity
            bit = {h: (b ^ 1) if flip else b for h, b in hashes.items()}
            ok = bad = 0
            for g in games:
                h, mm = g.get('map_hash'), g.get('map_id')
                if mm == m and h in bit and g.get('game_id') is not None:
                    if bit[h] == g['game_id'] % 2:
                        ok += 1
                    else:
                        bad += 1
            if ok >= bad:  # keep the polarity that agrees; ok>=bad means correlation >= 0.5
                break
        per_map[m] = dict(n_hashes=2, match_rate=round(ok / (ok + bad), 3) if ok + bad else None,
                          exceptions=bad, n=ok + bad)
    return per_map


def first_trailing(row, stages=(100, 200, 250, 300, 320, 360, 380, 400, 450, 499)):
    """First stage r where the eventual loser's total length < winner's total (None if never)."""
    won = (row.get('score') or 0) >= 0.5
    for r in stages:
        lo = opp_stage(row, r, 'total') if won else stage(row, r, 'total')
        hi = stage(row, r, 'total') if won else opp_stage(row, r, 'total')
        if lo is not None and hi is not None and lo < hi:
            return r
    return None


def trailing_profile(rows):
    """Share of games whose eventual loser already trails on total length by r250, per map class."""
    out = {}
    for cls, sel in (('compact', lambda x: x.get('map_name') in COMPACT), ('open', lambda x: x.get('map_name') not in COMPACT)):
        sub = [first_trailing(x) for x in rows if sel(x)]
        sub = [t for t in sub if t is not None]
        if sub:
            out[cls] = dict(n=len(sub), at_or_before_250=round(sum(1 for t in sub if t <= 250) / len(sub), 2))
    return out


def runtime_table(games, near_cap=90_000_000, cap=100_000_000):
    """cpu_max distribution per (own_submission, pool) plus near-cap counts (handoff §3.6)."""
    cells = defaultdict(list)
    for g in games:
        if g.get('verified') and g.get('origin') == 'controlled':
            cells[(g['own_submission'], g.get('pool'))].append(g.get('cpu_max'))
    out = []
    for (sub, pool), vals in sorted(cells.items(), key=lambda kv: (kv[0][1] or '', kv[0][0])):
        vals = [v for v in vals if v is not None]
        if not vals:
            continue
        vals.sort()
        out.append(dict(submission=sub, pool=pool, n=len(vals),
                        med=vals[len(vals) // 2], p95=vals[min(len(vals) - 1, int(round(0.95 * (len(vals) - 1))))],
                        mx=vals[-1], over_near_cap=sum(1 for v in vals if v > near_cap), at_cap=sum(1 for v in vals if v >= cap)))
    return out


def sonar_table(games):
    """Sonar rate per submission with a within-stratum median split (share above vs below own median)."""
    cells = defaultdict(list)
    for g in games:
        if g.get('verified') and g.get('origin') == 'controlled':
            so, t = stage(g, 499, 'sonar'), stage(g, 499, 'turns')
            cells[(g['own_submission'], g.get('pool'))].append((so / t if so is not None and t else None, g.get('score') or 0))
    out = []
    for (sub, pool), vals in sorted(cells.items(), key=lambda kv: (kv[0][1] or '', kv[0][0])):
        rates = [r for r, _ in vals if r is not None]
        if not rates:
            continue
        m = statistics.median(rates)
        hi = [s for r, s in vals if r is not None and r > m]
        lo = [s for r, s in vals if r is not None and r <= m]
        out.append(dict(submission=sub, pool=pool, n=len(rates), rate_med=round(m, 2),
                        share_hi=round(sum(hi) / len(hi), 2) if hi else None,
                        share_lo=round(sum(lo) / len(lo), 2) if lo else None))
    return out


def elo_trajectory(series_payloads, team_id=7):
    """Our team Elo over the day from cached series snapshots (handoff §3.9).

    series_payloads: iterable of parsed legacy series payloads (dicts with match/teamAElo/teamBElo).
    Returns ordered snapshots [(series_id, our_elo, ranked)] and the day delta."""
    snaps = []
    for p in series_payloads:
        m = (p or {}).get('match') or {}
        a, b = m.get('teamAId'), m.get('teamBId')
        if team_id not in (a, b):
            continue
        ours = p.get('teamAElo') if a == team_id else p.get('teamBElo')
        gid = m.get('id')
        if ours is not None and gid is not None:
            snaps.append((int(gid), ours, bool(m.get('ranked'))))
    snaps.sort()
    delta = snaps[-1][1] - snaps[0][1] if len(snaps) >= 2 else None
    return dict(snapshots=snaps, first=snaps[0][1] if snaps else None, last=snaps[-1][1] if snaps else None, delta=delta)


def elo_lines(series_payloads, team_id=7):
    t = elo_trajectory(series_payloads, team_id)
    if not t['snapshots']:
        return []
    moves = [(a, b, b2 - a2) for (a, a2, _), (b, b2, _) in zip(t['snapshots'], t['snapshots'][1:]) if b2 != a2]
    return [f"- Team elo {t['first']} -> {t['last']} (delta {t['delta']:+d}) over {len(t['snapshots'])} series snapshots; "
            f"{len(moves)} elo moves: " + '; '.join(f"at series {b} {d:+d}" for _, b, d in moves[-6:])]


def packet_lines_a1(analysis):
    """Extra packet lines for the A1 statistics (layout parity, runtime, sonar)."""
    L = []
    lp = analysis.get('layout_parity') or {}
    broken = {m: v for m, v in lp.items() if v.get('match_rate') is not None and v['match_rate'] < 0.999}
    ok = {m: v for m, v in lp.items() if v.get('match_rate') is not None and v['match_rate'] >= 0.999}
    if ok:
        L.append(f"- Layout rule: {len(ok)}/{len(lp)} maps follow game-id parity exactly ({sum(v['n'] for v in ok.values())} games)"
                 + (f"; deviants: " + ', '.join(f"map {m} rate {v['match_rate']} ({v.get('note') or str(v.get('exceptions')) + ' exceptions'})" for m, v in broken.items()) if broken else ""))
    rt = analysis.get('runtime') or []
    hot = [r for r in rt if r['over_near_cap'] or r['at_cap']]
    if hot:
        L.append("- Runtime: " + '; '.join(f"{r['submission']} ({r['pool']}) med {r['med']/1e6:.0f}M max {r['mx']/1e6:.0f}M at-cap {r['at_cap']}/{r['n']}" for r in hot))
    sn = analysis.get('sonar') or []
    if sn:
        L.append("- Sonar/turn med by source: " + ', '.join(f"{r['submission']} {r['rate_med']} (hi-split share {r['share_hi']} vs lo {r['share_lo']})" for r in sn if r['pool'] == 'field'))
    return L
