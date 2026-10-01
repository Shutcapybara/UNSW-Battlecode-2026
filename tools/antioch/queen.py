"""Queen and endgame rows, one per side-game (unswbc 1.2.3 tiebreak: queen -> longest -> total).

  python3 tools/antioch/queen.py --index public_replays/corpus/index.jsonl --dir public_replays/corpus/replays \
      --since 2026-09-30 --out build/antioch/queen.parquet --jobs 20
  python3 tools/antioch/queen.py --glob 'build/zoo/**/*.replay' --out build/antioch/queen_local.parquet

The queen is the team's original lowest-id dragon (verified on post-change replays: the engine's queen field equals that
dragon's length, 0 once it has died; no succession). On a split the parent keeps the id and the head end, so the queen
survives splits but keeps only the head piece. The same dragon is tracked in pre-change games, so the counterfactual
"what would the new tiebreak have said" is available for both eras.

Columns per side: queen_alive_end, queen_len_end, queen_len@{100,250,400,490}, queen_rank@490 (1 = longest of own
dragons, ties share the best rank), queen_is_longest@490, queen_share@490 (queen ÷ own total), queen_death_round,
queen_death_cause, queen_killed_by_enemy, queen_eats, queen_eats_300 (eats from r300), queen_corpse_eats_300 (ally
corpse pearls eaten by the queen from r300: the feeding signal), queen_splits / queen_splits_300 and the length they shed,
queen_steps_300 (cells moved from r300), queen_disp_300 (torus Manhattan from its r300 head to its final head), plus the
game end (units, longest, total, end_reason, engine winner, which tiebreak level decided under the new rules, and the
counterfactual old-rule winner).
"""
import collections, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
CHECK = (100, 250, 400, 490)


def torus(a, b, W, H):
    dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
    return min(dx, W - dx) + min(dy, H - dy)


def rows_for(path, gid=None):
    from tools.analysis.features import frame as F
    from tools.antioch.era import header
    try:
        h = header(path)
        g = F.decode(path)
    except Exception as e:
        return [dict(game=gid or Path(path).stem, error=f'{type(e).__name__}: {e}')]
    R, ev = g['rounds'], g['events']
    last = len(R) - 1
    teams = sorted({t for t, _ in R[0].values()})
    queen = {t: min(i for i, (tt, _) in R[0].items() if tt == t) for t in teams}
    side_of = {t: s for s, t in zip('AB', teams)}       # team labels in the frame are 'A'/'B' in map order
    out = []
    for t in teams:
        s = side_of[t]
        q = queen[t]
        o = 'B' if s == 'A' else 'A'
        r_ = dict(game=gid or Path(path).stem, side=s, queen_id=q, last_round=g['last_round'])
        for c in CHECK:
            rr = min(c, last)
            own = {i: len(b) for i, (tt, b) in R[rr].items() if tt == t}
            ql = own.get(q, 0)
            r_[f'queen_len@{c}'] = ql
            if c == 490:
                r_['own_units@490'] = len(own)
                r_['own_total@490'] = sum(own.values())
                r_['own_longest@490'] = max(own.values(), default=0)
                r_['queen_rank@490'] = (1 + sum(v > ql for v in own.values())) if ql else None
                r_['queen_is_longest@490'] = int(ql > 0 and ql == r_['own_longest@490'])
                r_['queen_share@490'] = ql / r_['own_total@490'] if r_['own_total@490'] else None
                opp = {i: len(b) for i, (tt, b) in R[rr].items() if tt != t}
                oq = opp.get(queen[[x for x in teams if x != t][0]], 0)
                r_['opp_queen_len@490'] = oq
                r_['opp_total@490'] = sum(opp.values())
                r_['opp_longest@490'] = max(opp.values(), default=0)
        d = [x for x in ev['deaths'] if x['id'] == q]
        r_['queen_death_round'] = d[0]['round'] if d else None
        r_['queen_death_cause'] = d[0]['cause'] if d else None
        r_['queen_death_len'] = d[0]['length'] if d else None
        r_['queen_killed_by_enemy'] = int(bool(d) and d[0].get('killer_team') not in (None, t))
        e = [x for x in ev['eats'] if x['id'] == q]
        r_['queen_eats'] = len(e)
        r_['queen_eats_300'] = sum(x['round'] >= 300 for x in e)
        r_['queen_corpse_eats_300'] = sum(x['round'] >= 300 and x['origin'] == 'ally_corpse' for x in e)
        r_['queen_enemy_corpse_eats_300'] = sum(x['round'] >= 300 and x['origin'] == 'enemy_corpse' for x in e)
        sp = [x for x in ev['splits'] if x['parent'] == q]
        r_['queen_splits'] = len(sp)
        r_['queen_splits_300'] = sum(x['round'] >= 300 for x in sp)
        r_['queen_shed'] = sum(x['child_len'] for x in sp)
        r_['queen_shed_300'] = sum(x['child_len'] for x in sp if x['round'] >= 300)
        mv = [a for a in ev['actions'] if a['id'] == q and a.get('kind') == 'move' and a['round'] >= 300]
        r_['queen_steps_300'] = sum(a.get('steps', 0) for a in mv)
        r_['queen_sprints_300'] = sum(a.get('steps', 0) >= 2 for a in mv)
        h300 = R[min(300, last)].get(q)
        hend = R[last].get(q)
        r_['queen_disp_300'] = torus(h300[1][0], hend[1][0], g['W'], g['H']) if h300 and hend else None
        # game end (engine header) and tiebreak level under the new rules
        mine, theirs = (h['queen_a'], h['longest_a'], h['total_a']), (h['queen_b'], h['longest_b'], h['total_b'])
        if s == 'B':
            mine, theirs = theirs, mine
        r_.update(queen_len_end=mine[0], longest_end=mine[1], total_end=mine[2], units_end=h[f'units_{s.lower()}'],
                  opp_queen_len_end=theirs[0], opp_longest_end=theirs[1], opp_total_end=theirs[2],
                  units_opp_end=h[f'units_{o.lower()}'], queen_alive_end=int(q in R[last]),
                  end_reason=h['res_reason'], engine_won=1.0 if h['res_winner'] == s else 0.5 if h['res_winner'] == 'draw' else 0.0)
        if h['res_reason'] == 1:
            level = next((k for k, a, b in zip(('queen', 'longest', 'total'), mine, theirs) if a != b), 'tie')
            old = next(((1.0 if a > b else 0.0) for a, b in zip(mine[1:], theirs[1:]) if a != b), 0.5)
            new = next(((1.0 if a > b else 0.0) for a, b in zip(mine, theirs) if a != b), 0.5)
        else:
            level, old, new = 'elimination', None, None
        r_.update(decided_by=level, won_old_rule=old, won_new_rule=new,
                  material_lead_end=(1 if mine[2] > theirs[2] else -1 if mine[2] < theirs[2] else 0))
        out.append(r_)
    return out


def _job(a):
    return rows_for(*a)


def main():
    import argparse, glob, multiprocessing as mp
    import pandas as pd
    ap = argparse.ArgumentParser()
    ap.add_argument('--index'); ap.add_argument('--dir'); ap.add_argument('--glob')
    ap.add_argument('--since', default=''); ap.add_argument('--until', default='9999')
    ap.add_argument('--out', required=True); ap.add_argument('--jobs', type=int, default=8)
    a = ap.parse_args()
    meta = None
    if a.index:
        idx = [json.loads(l) for l in open(a.index)]
        idx = [r for r in idx if a.since <= (r.get('finished_at') or '') < a.until]
        tasks = [(Path(a.dir) / f"{r['game_id']}.replay", str(r['game_id'])) for r in idx]
        tasks = [x for x in tasks if x[0].exists()]
        meta = pd.DataFrame(idx)[['game_id', 'finished_at', 'team_a', 'team_b', 'map_name', 'winner', 'ranked']]
        meta['game'] = meta.game_id.astype(str)
    else:
        tasks = [(p, None) for p in sorted(glob.glob(a.glob, recursive=True))]
    with mp.get_context('fork').Pool(a.jobs) as pool:
        rows = [r for rs in pool.imap_unordered(_job, tasks, chunksize=8) for r in rs]
    df = pd.DataFrame(rows)
    if meta is not None:
        df = df.merge(meta, on='game', how='left')
        df['team'] = df.apply(lambda r: str(r.team_a if r.side == 'A' else r.team_b) if r.get('team_a') == r.get('team_a') else None, axis=1)
        df['opp'] = df.apply(lambda r: str(r.team_b if r.side == 'A' else r.team_a) if r.get('team_a') == r.get('team_a') else None, axis=1)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(a.out, index=False)
    print(f'{len(df)} side rows from {len(tasks)} replays -> {a.out}')


if __name__ == '__main__':
    main()
