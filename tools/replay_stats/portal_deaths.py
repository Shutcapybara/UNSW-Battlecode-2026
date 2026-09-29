#!/usr/bin/env python3
"""C1-D §1 — portal transit exposure and death, measured from replay frames.

Per game and side, for chosen populations (team 7 live games; top teams 306/70/801; in-game
opponents as controls): exact portal steps (per-step simulation of every move command through
the replay's own edge map), deaths within 2 rounds of the dead dragon's own portal step (by
cause), deaths where two friendly heads used the same portal pair within 3 rounds, and the
round distribution of those deaths. Death classes reuse tools/analysis/features/extract.death_class.

  python tools/replay_stats/portal_deaths.py                  # all populations, cached frames
  python tools/replay_stats/portal_deaths.py --teams 7 306
Out: build/c1d/portal_deaths.json (+ printed tables).
"""
import argparse, collections, json, multiprocessing, statistics, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.analysis.features.frame import load           # noqa: E402
from tools.analysis.features.extract import death_class  # noqa: E402

sys.path.insert(0, str(ROOT / 'tools/hub/vendor/leviathan'))
from replay import Reader  # noqa: E402

CACHE = ROOT / 'build/c1e/frames'
DECODED = ROOT / 'build/c1e/decoded'
DIRS = ((0, -1), (1, 0), (0, 1), (-1, 0))   # N E S W, the engine's direction indices


def edge_kinds(maptext, W, H):
    """(x, y, dir) -> pid for portal edges only (same key formulation as the vendored dest():
    dir 0 from (x,y) crosses edge (0,x,y); dir 2 from (x,y) crosses (0,x,(y+1)%H);
    dir 1 from (x,y) crosses (1,(x+1)%W,y); dir 3 from (x,y) crosses (1,x,y))."""
    edges = collections.defaultdict(list)
    for line in maptext.splitlines():
        p = line.split()
        if p and p[0] == 'EDGE':
            idx, k, pid = map(int, p[1:])
            if k != 2:
                continue
            col, row = idx % (W + 1), idx // (W + 1)
            if col >= W or row >= 2 * H:
                continue
            edges[pid].append((row % 2, col, row // 2))
    cell_dir_pid = {}
    for pid, keys in edges.items():
        for ori, x, y in keys:
            for cx, cy, d in ((x, y, 0), (x, (y - 1) % H, 2)) if ori == 0 else (((x - 1) % W, y, 1), (x, y, 3)):
                cell_dir_pid[(cx % W, cy % H, d)] = pid
    return cell_dir_pid


def maptext_of(path):
    return Reader(str(path)).object(0, 0).text(0)


def portal_metrics(path):
    """Exact per-step portal walk. Returns per-side metrics + verification counters."""
    g = load(str(path), str(CACHE))
    W, H = g['W'], g['H']
    pid_of = edge_kinds(maptext_of(path), W, H)
    nbr = g['nbr']
    steps = {t: [] for t in 'AB'}            # (round, dragon, pid, entry, exit)
    death_head = {(d['round'], d['id']): d['head'] for d in g['events']['deaths']}
    verified = mismatched = 0
    for a in g['events']['actions']:
        if a['kind'] != 'move' or not a.get('dirs'):
            continue
        r, i = a['round'], a['id']
        snap = g['rounds'][r] if r < len(g['rounds']) else {}
        if i not in snap:
            continue                           # dead or gone at round start
        t, pos = snap[i][0], snap[i][1][0]
        for d in a['dirs']:
            pid = pid_of.get((pos[0], pos[1], d))
            nxt = nbr[pos][d]
            if pid is not None and nxt is not None and nxt != pos:
                steps[t].append((r, i, pid, pos, nxt))
            if nxt is None:
                break                          # commanded into kelp; nothing after executes
            pos = nxt
            if death_head.get((r, i)) == pos:
                break                          # died on this step; later dirs never executed
        nxt_snap = g['rounds'][r + 1] if r + 1 < len(g['rounds']) else {}
        if i in nxt_snap:
            if nxt_snap[i][1][0] == pos:
                verified += 1
            else:
                mismatched += 1
    # deaths: within 2 rounds of own portal step; cause; friendly same-pair use within 3 rounds
    suicided = {(a['round'], a['id']) for a in g['events']['actions'] if a['kind'] == 'suicide'}
    dead = []
    for d in g['events']['deaths']:
        t = d['team']
        own = [s for s in steps[t] if s[1] == d['id'] and d['round'] - 2 <= s[0] <= d['round']]
        double = any(s2[1] != d['id'] and s2[2] == s[2] and abs(s2[0] - s[0]) <= 3
                     for s in own for s2 in steps[t])
        dead.append(dict(round=d['round'], id=d['id'], team=t, cause=death_class(d, suicided),
                         near_portal_step=bool(own), same_pair_double=double))
    return dict(file=str(path), map=g['map'], winner=g['winner'], steps=steps, deaths=dead,
                verified=verified, mismatched=mismatched)


def _one(args):
    gid, = args
    try:
        return dict(gid=gid, **portal_metrics(DECODED / f'{gid}.replay'))
    except Exception as e:
        return dict(gid=gid, error=f'{type(e).__name__}: {e}')


def aggregate(games, side_of):
    """games: [{row, result}] → per-map and pooled rows for the target side (+opponent control)."""
    out = {}
    for label in ('target', 'opponent'):
        rows = []
        for gm in games:
            side = side_of(gm['row']) if label == 'target' else ('B' if side_of(gm['row']) == 'A' else 'A')
            st = gm['result']['steps'][side]
            deaths = [d for d in gm['result']['deaths'] if d['team'] == side]
            near = [d for d in deaths if d['near_portal_step']]
            rows.append(dict(map=gm['row']['map_name'], steps=len(st),
                             deaths=len(deaths), near=len(near),
                             near_wall=sum(1 for d in near if d['cause'] == 'wall'),
                             near_self=sum(1 for d in near if d['cause'] == 'self'),
                             near_ally=sum(1 for d in near if d['cause'] == 'ally_body'),
                             near_enemy_body=sum(1 for d in near if d['cause'] == 'enemy_body'),
                             near_h2h=sum(1 for d in near if d['cause'] in ('h2h_enemy', 'h2h_ally')),
                             near_invalid=sum(1 for d in near if d['cause'] == 'invalid'),
                             near_suicide=sum(1 for d in near if d['cause'] == 'suicide'),
                             double=sum(1 for d in near if d['same_pair_double']),
                             rounds=[d['round'] for d in near]))
        agg = {}
        for name, sel in [('ALL', rows)] + [(m, [r for r in rows if r['map'] == m]) for m in sorted({r['map'] for r in rows})]:
            if not sel:
                continue
            n_games = len(sel)
            tot_steps = sum(r['steps'] for r in sel)
            tot_near = sum(r['near'] for r in sel)
            agg[name] = dict(
                games=n_games,
                steps_per_game_med=statistics.median(r['steps'] for r in sel),
                steps_total=tot_steps,
                near_deaths_per_game_med=statistics.median(r['near'] for r in sel),
                near_deaths_total=tot_near,
                near_per_100_steps=round(100 * tot_near / tot_steps, 2) if tot_steps else None,
                deaths_total=sum(r['deaths'] for r in sel),
                near_by_cause={k: sum(r[k] for r in sel) for k in
                               ('near_wall', 'near_self', 'near_ally', 'near_enemy_body', 'near_h2h', 'near_invalid', 'near_suicide')},
                same_pair_double_deaths=sum(r['double'] for r in sel),
                near_round_bins={f'{b}-{b+49}': sum(1 for r in sel for x in r['rounds'] if b <= x < b + 50)
                                 for b in range(0, 500, 50)})
        out[label] = agg
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--teams', type=int, nargs='+', default=[7, 306, 70, 801])
    ap.add_argument('--out', default='build/c1d/portal_deaths.json')
    ap.add_argument('--jobs', type=int, default=10)
    a = ap.parse_args(argv)
    try:
        multiprocessing.set_start_method('fork')
    except RuntimeError:
        pass
    from concurrent.futures import ProcessPoolExecutor
    rows = [json.loads(l) for l in open(ROOT / 'public_replays/corpus/index.jsonl')]
    by_id = {r['game_id']: r for r in rows}
    teams = {7: [json.loads(l) for l in open(ROOT / 'build/c1d/team7_games.jsonl')]}  # ranked + unranked(dev)
    for tid in a.teams:
        if tid == 7:
            continue
        teams[tid] = [r for r in rows if tid in (r['team_a'], r['team_b']) and r['status'] == 'completed' and r['ranked']]
    gids, seen = [], set()
    for tid in a.teams:
        for r in teams[tid]:
            if r['game_id'] not in seen and (DECODED / f"{r['game_id']}.replay").exists():
                seen.add(r['game_id'])
                gids.append(r['game_id'])
    results = {}
    with ProcessPoolExecutor(a.jobs) as ex:
        for res in ex.map(_one, [(gid,) for gid in gids], chunksize=8):
            results[res['gid']] = res
    errs = [r for r in results.values() if 'error' in r]
    out = {'_meta': dict(games=len(gids), errors=len(errs),
                         verify=dict(verified=sum(r.get('verified', 0) for r in results.values() if 'error' not in r),
                                     mismatched=sum(r.get('mismatched', 0) for r in results.values() if 'error' not in r)),
                         error_samples=[e['error'] for e in errs[:3]]), 'teams': {}}
    for tid in a.teams:
        games = [dict(row=r, result=results[r['game_id']]) for r in teams[tid]
                 if r['game_id'] in results and 'error' not in results[r['game_id']]]
        side_of = (lambda r: 'A' if r['team_a'] == tid else 'B')
        agg = aggregate(games, side_of)
        if tid == 7:
            for label, sel in (('ranked', True), ('unranked_dev', False)):
                sub = [g for g in games if g['row']['ranked'] == sel]
                if sub:
                    agg[f'target_{label}'] = aggregate(sub, side_of)['target']
        out['teams'][tid] = agg
    Path(ROOT / a.out).parent.mkdir(parents=True, exist_ok=True)
    json.dump(out, open(ROOT / a.out, 'w'), indent=1, sort_keys=True)
    print(json.dumps(out['_meta']))
    for tid, agg in out['teams'].items():
        t = agg.get('target_ranked') or agg['target']
        print(f"team {tid}: {t['ALL']['games']} games, {t['ALL']['steps_per_game_med']} steps/game med, "
              f"{t['ALL']['near_deaths_per_game_med']} near-deaths/game med, "
              f"{t['ALL']['near_per_100_steps']}/100 steps, double {t['ALL']['same_pair_double_deaths']}")


if __name__ == '__main__':
    main()
