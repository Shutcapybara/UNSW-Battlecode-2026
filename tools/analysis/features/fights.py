"""C2-0 fight anatomy: contact/fight events on F1 frames (no new decoder).

Definitions (kept simple and identical for every cohort; distances are wrap-aware Manhattan
on the replay's own geometry, portals not followed - a portal can only hide a contact, never
invent one, and the bias is the same for everyone):

  contact     an enemy head within 4 cells of a friendly head
  cluster     connected component of heads joined by cross-team contact edges
  fight       a cluster event where >= 3 heads of one side and >= 1 of the other stand within
              6 cells of the cluster centre; 1v1, 2v1 and 2v2 contacts are separate classes
  event       clusters linked across rounds by shared participants, ended by 5 contact-less rounds
  initiator   the side whose head first stands adjacent (<= 1 cell) to an enemy head, credited by
              who closed more distance in the round that created the adjacency
  outcome     participant deaths up to last contact + 5 rounds: trade (both lose a head),
              kill for X (only Y loses one), disengage (neither)
  next-10     material change over the 10 rounds after first contact, and whether the nearest
              3 beds' next pearl went to a different side than their previous one

CLI:
  python -m tools.analysis.features.fights extract <replay paths...> --out DIR [--jobs N]
  python -m tools.analysis.features.fights report --events DIR/fights.parquet \
      --index public_replays/corpus/index.jsonl --ladder public_replays/corpus/ladder \
      --out-md docs/analysis/C2-fight-anatomy.md --out-json game_stats/fight_anatomy.json
"""
import argparse, collections, json, math, multiprocessing
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from .frame import load
from ..c1e_pace import load_ladders, rank_at

CONTACT_D = 4          # enemy head within 4 cells => contact
WINDOW_D = 6           # fight window radius around the cluster centre
GROUP_MIN = 3          # >= 3 heads of one side in the window => group fight
NO_CONTACT_CLOSE = 5   # event ends after 5 contact-less rounds
PRE_ROUNDS = 3         # coordination window before first contact
RESOLVE_PAD = 5        # participant deaths counted up to last contact + 5
NEXT10 = 10            # outcome window after first contact
BED_WAIT = 30          # rounds to wait for the nearest beds' next eater
COMPACT = {'Portals', 'Prisoners Dilemma', 'Devil', 'Trophy'}
REACH_STEPS = 5
REACH_MAX = 61         # 1 + 2*5*6 open ground
COHORTS = ('top10', 'r11_30', 'band', 'team7')
LABEL = {'top10': 'top 10', 'r11_30': 'ranks 11-30', 'band': 'band 55-85', 'team7': 'team 7'}


def wd(a, b, W, H):
    """wrap-aware Manhattan distance between two cells"""
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    return min(dx, W - dx) + min(dy, H - dy)


def circ_mean(cells, W, H):
    """circular mean position (wrap-safe)"""
    ax = math.atan2(sum(math.sin(2 * math.pi * c[0] / W) for c in cells),
                    sum(math.cos(2 * math.pi * c[0] / W) for c in cells))
    ay = math.atan2(sum(math.sin(2 * math.pi * c[1] / H) for c in cells),
                    sum(math.cos(2 * math.pi * c[1] / H) for c in cells))
    return (round(ax % (2 * math.pi) * W / (2 * math.pi)) % W,
            round(ay % (2 * math.pi) * H / (2 * math.pi)) % H)


def reach5(nbr, cell, cache):
    """cells reachable in <= 5 steps ignoring bodies (terrain corridor-ness)"""
    if cell in cache:
        return cache[cell]
    dist = {cell: 0}
    q = collections.deque([cell])
    while q:
        c = q.popleft()
        if dist[c] >= REACH_STEPS:
            continue
        for n in nbr[c]:
            if n is not None and n not in dist:
                dist[n] = dist[c] + 1
                q.append(n)
    cache[cell] = len(dist)
    return len(dist)


def _cluster_components(hd, W, H):
    """contact clusters at one round: [{members {id: head}, nA, nB, centre}]"""
    A = [i for i, (t, _) in hd.items() if t == 'A']
    B = [i for i, (t, _) in hd.items() if t == 'B']
    if not A or not B:
        return []
    pa = np.array([hd[i][1] for i in A], dtype=np.int64)
    pb = np.array([hd[i][1] for i in B], dtype=np.int64)
    dx = np.abs(pa[:, None, 0] - pb[None, :, 0])
    dy = np.abs(pa[:, None, 1] - pb[None, :, 1])
    D = np.minimum(dx, W - dx) + np.minimum(dy, H - dy)
    pairs = np.argwhere(D <= CONTACT_D)
    if not len(pairs):
        return []
    adj = collections.defaultdict(set)
    for ka, kb in pairs:
        i, j = A[ka], B[kb]
        adj[i].add(j)
        adj[j].add(i)
    seen, comps = set(), []
    for start in list(adj):
        if start in seen:
            continue
        grp, stack = set(), [start]
        while stack:
            u = stack.pop()
            if u in grp:
                continue
            grp.add(u)
            stack.extend(adj[u] - grp)
        seen |= grp
        comps.append(dict(members={i: hd[i][1] for i in grp},
                          nA=sum(1 for i in grp if hd[i][0] == 'A'),
                          nB=sum(1 for i in grp if hd[i][0] == 'B'),
                          centre=circ_mean([hd[i][1] for i in grp], W, H)))
    return comps


def _closer(hd, ia, ib, r, W, H):
    """who closed more distance in the round leading into round r; None if not computable"""
    if r <= 0 or ia not in hd[r - 1] or ib not in hd[r - 1]:
        return None
    pa0, pb0 = hd[r - 1][ia][1], hd[r - 1][ib][1]
    pa1, pb1 = hd[r][ia][1], hd[r][ib][1]
    prev = wd(pa0, pb0, W, H)
    da = prev - wd(pa1, pb0, W, H)     # a's move, b held fixed
    db = prev - wd(pa0, pb1, W, H)     # b's move, a held fixed
    return 'A' if da > db else 'B' if db > da else 'even'


def detect(g):
    """one event row per contact cluster event in the game"""
    W, H, nbr = g['W'], g['H'], g['nbr']
    rounds = g['rounds']
    R = len(rounds) - 1                      # rounds[R] is the final state
    heads = [{i: (t, b[0]) for i, (t, b) in snap.items()} for snap in rounds]
    bodylen = [{i: len(b) for i, (t, b) in snap.items()} for snap in rounds]
    team = {}
    for hd in heads:
        for i, (t, _) in hd.items():
            team[i] = t
    died = {d['id']: d for d in g['events']['deaths']}
    eats_by_team = collections.Counter()             # (team, round) -> pearls
    bed_eats = collections.defaultdict(list)         # cell -> [(round, team)]
    bed_cells = {sp['cell'] for sp in g['events']['spawns'] if sp['origin'] == 'bed'}
    for e in g['events']['eats']:
        if 0 <= e['round'] <= R:
            eats_by_team[(e['team'], e['round'])] += 1
            if e['origin'] == 'bed':
                bed_eats[e['cell']].append((e['round'], e['team']))
    rays = collections.Counter()                     # (round, id) -> rays
    for p in g['events']['sonar']:
        rays[(p['round'], p['id'])] += 1
    reach_cache = {}

    # ---- link clusters into events (shared participants; 5 contact-less rounds close it) ----
    live, done = [], []
    for r in range(R):
        comps = _cluster_components(heads[r], W, H)
        for ev in live:
            ev['matched'] = False
        for comp in comps:
            ids = set(comp['members'])
            best, shared = None, 0
            for ev in live:
                s = len(ids & ev['parts'])
                if s > shared:
                    best, shared = ev, s
            if best is not None:
                best.update(matched=True, rE=r, gap=0, parts=best['parts'] | ids,
                            max_heads=max(best['max_heads'], len(ids)))
            else:
                live.append(dict(r0=r, rE=r, gap=0, parts=ids, max_heads=len(ids),
                                 centre0=comp['centre'], nA0=comp['nA'], nB0=comp['nB'], matched=True))
        for ev in live:
            if not ev['matched']:
                ev['gap'] += 1
        still = []
        for ev in live:
            (done if ev['gap'] > NO_CONTACT_CLOSE else still).append(ev)
        live = still
    done.extend(live)

    rows = []
    for ev in done:
        r0, rE = ev['r0'], ev['rE']
        partsA = {i for i in ev['parts'] if team.get(i) == 'A'}
        partsB = {i for i in ev['parts'] if team.get(i) == 'B'}
        centre = ev['centre0']
        sup = {'A': set(), 'B': set()}
        for i, (t, h) in heads[r0].items():
            if wd(h, centre, W, H) <= WINDOW_D:
                sup[t].add(i)
        sA, sB = len(sup['A']), len(sup['B'])
        # ---- first adjacency => initiator; first contact => closer ----
        # adjacency is checked on POST-move positions (snapshot r+1 for survivors, the death
        # cell for heads that died that round): heads that collide mid-round never sit <= 1
        # apart in a start-of-round snapshot.
        def _after(i, r):
            nxt = heads[r + 1] if r + 1 <= R else {}
            if i in nxt:
                return nxt[i][1]
            rec = died.get(i)
            return rec['head'] if rec and rec['round'] == r else None

        first_adj, initiator, closer = None, None, None
        for r in range(r0, min(rE, R - 1) + 1):
            aliv = [(i, heads[r][i][1]) for i in partsA if i in heads[r]]
            bliv = [(i, heads[r][i][1]) for i in partsB if i in heads[r]]
            if not aliv or not bliv:
                continue
            post = {i: _after(i, r) for i, _ in aliv + bliv}
            if any(p is None for p in post.values()):
                continue
            best = min((wd(post[a], post[b], W, H), a, b) for (a, _) in aliv for (b, _) in bliv)
            if r == r0:
                d0, (ia, _), (ib, _) = min((wd(pa[1], pb[1], W, H), pa, pb) for pa in aliv for pb in bliv)
                closer = _closer(heads, ia, ib, r0, W, H)
            if best[0] <= 1:
                first_adj = r
                _, ia, ib = best
                pre_a, pre_b = heads[r][ia][1], heads[r][ib][1]
                prev = wd(pre_a, pre_b, W, H)
                da = prev - wd(post[ia], pre_b, W, H)
                db = prev - wd(pre_a, post[ib], W, H)
                initiator = 'A' if da > db else 'B' if db > da else 'even'
                break
        # ---- participant deaths in the resolve window ----
        d = {'A': 0, 'B': 0}
        ll = {'A': 0, 'B': 0}
        cred = {'A': 0, 'B': 0}
        for i in ev['parts']:
            rec = died.get(i)
            if rec and r0 <= rec['round'] <= rE + RESOLVE_PAD:
                t = rec['team']
                d[t] += 1
                ll[t] += rec['length']
                if rec.get('killer_team') == ('A' if t == 'B' else 'B'):
                    cred['A' if t == 'B' else 'B'] += 1
        outcome = ('trade' if d['A'] and d['B'] else
                   'killA' if d['B'] and not d['A'] else
                   'killB' if d['A'] and not d['B'] else 'disengage')
        # ---- next-10 material (side-wide) and nearest-bed flips ----
        d10 = {t: sum(1 for i in heads[r0] if team[i] == t and i in died
                      and r0 <= died[i]['round'] < r0 + NEXT10) for t in 'AB'}
        ll10 = {t: sum(died[i]['length'] for i in heads[r0] if team[i] == t and i in died
                       and r0 <= died[i]['round'] < r0 + NEXT10) for t in 'AB'}
        p10 = {t: sum(eats_by_team[(t, r)] for r in range(r0, min(r0 + NEXT10, R + 1))) for t in 'AB'}
        flips, seen_beds = 0, 0
        if bed_cells:
            for cell in sorted(bed_cells, key=lambda c: wd(c, centre, W, H))[:3]:
                hist = bed_eats.get(cell, [])
                pre = [(r, t) for r, t in hist if r < r0]
                post = [(r, t) for r, t in hist if r0 <= r < r0 + BED_WAIT]
                if post:
                    seen_beds += 1
                    if not pre or pre[-1][1] != post[0][1]:
                        flips += 1
        bed_flip = flips / seen_beds if seen_beds else float('nan')
        # ---- coordination: pre-contact convergence, entry spread, rays ----
        conv, spread, nrays = {}, {}, {}
        for t in 'AB':
            grp = sup[t] | (partsA if t == 'A' else partsB)
            moved = set()
            for rr in range(max(0, r0 - PRE_ROUNDS), r0):
                for i in grp:
                    if rr >= 1 and i in heads[rr] and i in heads[rr - 1] and \
                            wd(heads[rr][i][1], centre, W, H) < wd(heads[rr - 1][i][1], centre, W, H):
                        moved.add(i)
            entries = [rr for rr in range(max(0, r0 - 5), r0 + 1)]
            firsts = []
            for i in grp:
                e0 = next((rr for rr in entries if i in heads[rr]
                           and wd(heads[rr][i][1], centre, W, H) <= WINDOW_D), None)
                if e0 is not None:
                    firsts.append(e0)
            conv[t] = len(moved)
            spread[t] = (max(firsts) - min(firsts)) if len(firsts) > 1 else (0 if firsts else float('nan'))
            nrays[t] = sum(n for (rr, i), n in rays.items()
                           if max(0, r0 - PRE_ROUNDS) <= rr < r0 and i in grp)
        # ---- geometry at first contact ----
        cells = [(x, y) for x in range(W) for y in range(H) if wd((x, y), centre, W, H) <= WINDOW_D]
        open_ratio = sum(reach5(nbr, c, reach_cache) for c in cells) / (REACH_MAX * len(cells))
        degree = sum(sum(1 for n2 in nbr[c] if n2 is not None) for c in cells) / (4 * len(cells))
        bed_dist = min((wd(c, centre, W, H) for c in bed_cells), default=float('nan'))
        portal3 = any(wd(c, centre, W, H) <= 3 for c in g['portal_cells'])
        # ---- event class ----
        if max(sA, sB) >= GROUP_MIN:
            cls = 'group'
        elif (ev['nA0'], ev['nB0']) == (1, 1):
            cls = '1v1'
        elif min(ev['nA0'], ev['nB0']) == 1 and max(ev['nA0'], ev['nB0']) == 2:
            cls = '2v1'
        elif (ev['nA0'], ev['nB0']) == (2, 2):
            cls = '2v2'
        else:
            cls = 'pair'
        units = {t: sum(1 for i in heads[r0] if heads[r0][i][0] == t) for t in 'AB'}
        total = {t: sum(bodylen[r0][i] for i in heads[r0] if heads[r0][i][0] == t) for t in 'AB'}
        rows.append(dict(
            game=int(g['id']), map=g['map'], map_class='compact' if g['map'] in COMPACT else 'open',
            r0=r0, rE=rE, dur=rE - r0 + 1, cls=cls, nA0=ev['nA0'], nB0=ev['nB0'], sA0=sA, sB0=sB,
            cx=centre[0], cy=centre[1], max_heads=ev['max_heads'], winner=g['winner'],
            first_adj=first_adj, initiator=initiator, first_closer=closer,
            unitsA=units['A'], unitsB=units['B'], totalA=total['A'], totalB=total['B'],
            engA=sum(bodylen[r0][i] for i in partsA if i in bodylen[r0]),
            engB=sum(bodylen[r0][i] for i in partsB if i in bodylen[r0]),
            dA=d['A'], dB=d['B'], llA=ll['A'], llB=ll['B'], credA=cred['A'], credB=cred['B'],
            outcome=outcome, d10A=d10['A'], d10B=d10['B'], ll10A=ll10['A'], ll10B=ll10['B'],
            p10A=p10['A'], p10B=p10['B'], bed_flip=bed_flip,
            convA=conv['A'], convB=conv['B'], denA=len(sup['A'] | partsA), denB=len(sup['B'] | partsB),
            spreadA=spread['A'], spreadB=spread['B'], raysA=nrays['A'], raysB=nrays['B'],
            open_ratio=open_ratio, degree_mean=degree, bed_dist=bed_dist, portal3=portal3))
    return rows


def _one(task):
    path, cache = task
    try:
        return detect(load(path, cache))
    except Exception as e:      # keep the run alive; failures counted in the summary
        return [dict(game=int(Path(path).stem), error=f'{type(e).__name__}: {e}')]


def extract(paths, out_dir, jobs, cache=None):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    tasks = [(str(p), cache) for p in paths]
    out_rows, n_fail = [], 0
    if jobs > 1 and len(tasks) > 1:
        with multiprocessing.get_context('fork').Pool(jobs) as pool:
            for n, rows in enumerate(pool.imap_unordered(_one, tasks, chunksize=2), 1):
                if rows and 'error' in rows[0]:
                    n_fail += 1
                else:
                    out_rows.extend(rows)
                if n % 500 == 0:
                    print(f'  {n}/{len(tasks)} games ({n_fail} failed)', flush=True)
    else:
        for n, t in enumerate(tasks, 1):
            rows = _one(t)
            if rows and 'error' in rows[0]:
                n_fail += 1
            else:
                out_rows.extend(rows)
            if n % 100 == 0:
                print(f'  {n}/{len(tasks)} games ({n_fail} failed)', flush=True)
    if n_fail:
        (Path(out_dir) / 'failed.txt').write_text(f'{n_fail} games failed\n')
    df = pd.DataFrame(out_rows)
    if not len(df):
        print('no events extracted')
        return
    df.to_parquet(Path(out_dir) / 'fights.parquet', index=False)
    print(f'wrote {out_dir}/fights.parquet: {len(df)} events over {df["game"].nunique()} games, {n_fail} games failed')


# ---------------------------------------------------------------- report ----

def cohort_of(rank, team_id):
    if team_id == 7:
        return 'team7'
    if rank is None:
        return None
    if rank <= 10:
        return 'top10'
    if rank <= 30:
        return 'r11_30'
    if 55 <= rank <= 85:
        return 'band'
    return None


def _prop_ci(xs):
    """(mean, n, 1.96*se) of a 0/1 series with NaN dropped"""
    s = pd.Series(xs).dropna().astype(float)
    n = len(s)
    if not n:
        return float('nan'), 0, float('nan')
    m = s.mean()
    se = math.sqrt(max(m * (1 - m), 1e-12) / n)
    return float(m), int(n), float(1.96 * se)


def _mean_ci(xs):
    s = pd.Series(xs).dropna().astype(float)
    n = len(s)
    if not n:
        return float('nan'), 0, float('nan')
    return float(s.mean()), int(n), float(1.96 * s.std() / math.sqrt(n))


def _side_frames(ev):
    """duplicate each event per side, oriented own/opponent, cohort attached"""
    frames = []
    for s in 'AB':
        o = 'B' if s == 'A' else 'A'
        f = pd.DataFrame(dict(
            game=ev['game'], side=s, cls=ev['cls'], r0=ev['r0'], map_class=ev['map_class'],
            cohort=ev['cohort_' + s.lower()], won=(ev['winner'] == s).astype(float),
            initiator=ev['initiator'],
            own_init=(ev['initiator'] == s).astype(float).where(ev['initiator'].isin(['A', 'B'])),
            outcome=ev['outcome'],
            own_kill=(ev['outcome'] == 'kill' + s).astype(float),
            kill_against=(ev['outcome'] == 'kill' + o).astype(float),
            trade=(ev['outcome'] == 'trade').astype(float),
            own_d=(ev['dA'] if s == 'A' else ev['dB']).astype(float),
            opp_d=(ev['dB'] if s == 'A' else ev['dA']).astype(float),
            own_ll=(ev['llA'] if s == 'A' else ev['llB']).astype(float),
            opp_ll=(ev['llB'] if s == 'A' else ev['llA']).astype(float),
            units=(ev['unitsA'] if s == 'A' else ev['unitsB']).astype(float),
            opp_units=(ev['unitsB'] if s == 'A' else ev['unitsA']).astype(float),
            conv=(ev['convA'] if s == 'A' else ev['convB']).astype(float),
            den=(ev['denA'] if s == 'A' else ev['denB']).astype(float),
            spread=(ev['spreadA'] if s == 'A' else ev['spreadB']).astype(float),
            rays=(ev['raysA'] if s == 'A' else ev['raysB']).astype(float),
            p10=(ev['p10A'] if s == 'A' else ev['p10B']).astype(float),
            opp_p10=(ev['p10B'] if s == 'A' else ev['p10A']).astype(float),
            ll10=(ev['ll10A'] if s == 'A' else ev['ll10B']).astype(float),
            opp_ll10=(ev['ll10B'] if s == 'A' else ev['ll10A']).astype(float),
            bed_flip=ev['bed_flip'].astype(float), open_ratio=ev['open_ratio'].astype(float),
            degree=ev['degree_mean'].astype(float), bed_dist=ev['bed_dist'].astype(float),
            portal3=ev['portal3'].astype(float)))
        frames.append(f)
    return pd.concat(frames, ignore_index=True)


def _cohort_block(sd, universe):
    """pooled per-cohort aggregate over group-class events; universe = n side-games per cohort"""
    out = {}
    g = sd[sd['cls'] == 'group']
    for c in COHORTS:
        gg = g[g['cohort'] == c]
        n_games = universe.get(c, 0)
        b = {'n_side_games': n_games, 'n_group_events': int(len(gg))}
        b['group_events_per_game'] = (len(gg) / n_games) if n_games else float('nan')
        b['initiator_share'], b['initiator_n'], b['initiator_ci95'] = _prop_ci(gg['own_init'])
        b['even_adj_share'] = float((gg['initiator'] == 'even').mean()) if len(gg) else float('nan')
        for k, src in (('trade_share', 'trade'), ('kill_for_share', 'own_kill'), ('kill_against_share', 'kill_against')):
            b[k], _, _ = _prop_ci(gg[src])
        b['disengage_share'] = 1 - b['trade_share'] - b['kill_for_share'] - b['kill_against_share'] if len(gg) else float('nan')
        b['deaths_own_per_fight'], _, _ = _mean_ci(gg['own_d'])
        b['deaths_opp_per_fight'], _, _ = _mean_ci(gg['opp_d'])
        b['lenlost_own_per_fight'], _, _ = _mean_ci(gg['own_ll'])
        b['lenlost_opp_per_fight'], _, _ = _mean_ci(gg['opp_ll'])
        tr = gg[gg['trade'] > 0]
        b['n_trades'] = int(len(tr))
        if len(tr):
            b['trade_ahead_share'] = float((tr['units'] > tr['opp_units']).mean())
            b['trade_units_margin'] = float((tr['units'] - tr['opp_units']).median())
        gw = gg[gg['den'] >= 2]
        b['conv_ratio'] = float(gg['conv'].sum() / gg['den'].sum()) if gg['den'].sum() else float('nan')
        b['conv_ge2_share'], b['conv_ge2_n'], _ = _prop_ci(gw['conv'] >= 2)
        b['synch_share'], _, _ = _prop_ci(gw['spread'] <= 1)      # entries into the window within 1 round
        b['rays_pre_per_head'] = float(gg['rays'].sum() / gg['den'].sum()) if gg['den'].sum() else float('nan')
        b['pearl_delta_next10'], _, _ = _mean_ci(gg['p10'] - gg['opp_p10'])
        b['lenlost_delta_next10'], _, _ = _mean_ci(gg['ll10'] - gg['opp_ll10'])
        b['bed_flip_share'], _, _ = _prop_ci(gg['bed_flip'])
        out[c] = b
    return out


def report(events_path, index_path, ladder_dir, out_md, out_json):
    ev = pd.read_parquet(events_path)
    ev['game'] = ev['game'].astype(int)
    games = {}
    for line in open(index_path):
        r = json.loads(line)
        if r.get('ranked') and r.get('status') == 'completed':
            games[int(r['game_id'])] = r
    ladders = load_ladders(Path(ladder_dir))
    meta_games = {}
    for gid, r in games.items():
        when = datetime.fromisoformat(r['started_at'].replace('Z', '+00:00'))
        ra = rank_at(ladders, r['team_a'], when)
        rb = rank_at(ladders, r['team_b'], when)
        meta_games[gid] = dict(team_a=r['team_a'], team_b=r['team_b'],
                               cohort_a=cohort_of(ra, r['team_a']), cohort_b=cohort_of(rb, r['team_b']),
                               winner=r['winner'], autoscrim=bool(r.get('autoscrim_window')),
                               map=r['map_name'])
    mcols = {k: {gid: v[k] for gid, v in meta_games.items()}
             for k in ('team_a', 'team_b', 'cohort_a', 'cohort_b', 'winner', 'autoscrim')}
    for k, d in mcols.items():
        ev[k] = ev['game'].map(d)
    sd = _side_frames(ev)

    # universe: every ranked side-game with a known cohort (denominator for per-game rates)
    uni_rows = []
    for gid, m in meta_games.items():
        for s, coh in (('A', m['cohort_a']), ('B', m['cohort_b'])):
            if coh:
                uni_rows.append(dict(game=gid, side=s, cohort=coh, cls='__none',
                                     won=1.0 if m['winner'].lower() == s.lower() else 0.0))
    uni = pd.DataFrame(uni_rows)
    universe = uni.groupby('cohort').size().to_dict()

    # conditional win: net group-fight outcome per side-game
    g = sd[sd['cls'] == 'group']
    net = g.groupby(['game', 'side', 'cohort'], as_index=False).agg(
        net_kill=('own_kill', 'sum'), net_beat=('kill_against', 'sum'), nf=('own_kill', 'size'))
    uni2 = uni.merge(net, on=['game', 'side', 'cohort'], how='left')
    uni2['bucket'] = np.where(uni2['nf'].isna(), 'no_group_fight',
                              np.where(uni2['net_kill'] > uni2['net_beat'], 'net_kill+',
                                       np.where(uni2['net_kill'] < uni2['net_beat'], 'net_kill-', 'net_even')))
    cw = uni2.groupby(['cohort', 'bucket']).agg(n=('won', 'size'), win=('won', 'mean')).reset_index()
    cond_win = {c: {r['bucket']: {'n': int(r['n']), 'win_rate': float(r['win'])}
                    for _, r in cw[cw['cohort'] == c].iterrows()} for c in COHORTS}

    # class mix per cohort (events per side-game by class)
    classes = {}
    for c in COHORTS:
        sc = sd[sd['cohort'] == c]
        classes[c] = {k: len(sc[sc['cls'] == k]) / universe.get(c, 1) for k in ('group', '2v1', '1v1', '2v2', 'pair')}
        tr1 = sc[(sc['cls'] == '1v1')]
        classes[c]['1v1_initiator_share'] = float(tr1['own_init'].dropna().mean()) if len(tr1) else float('nan')

    per_cohort = _cohort_block(sd, universe)

    # era split (group class): early <100, mid 100-249, late >=250
    era = {}
    for c in COHORTS:
        gg = g[g['cohort'] == c]
        for tag, sel in (('early', gg['r0'] < 100), ('mid', (gg['r0'] >= 100) & (gg['r0'] < 250)), ('late', gg['r0'] >= 250)):
            e = gg[sel]
            if len(e):
                era.setdefault(tag, {})[c] = {
                    'n': int(len(e)), 'share': float(len(e) / len(gg)),
                    'initiator_share': float(e['own_init'].dropna().mean()),
                    'trade_share': float(e['trade'].mean()),
                    'conv_ratio': float(e['conv'].sum() / e['den'].sum()) if e['den'].sum() else float('nan')}

    # map class (descriptive) and geometry buckets: initiator + convergence, top10 vs band
    def bucket_block(col, fn):
        out = {}
        gg = g[g['cohort'].isin(['top10', 'band'])].copy()
        gg['b'] = fn(gg)
        for bval, bb in gg.groupby('b'):
            row = {}
            for c in ('top10', 'band'):
                e = bb[bb['cohort'] == c]
                if len(e):
                    row[c] = {'n': int(len(e)),
                              'initiator_share': float(e['own_init'].dropna().mean()),
                              'conv_ratio': float(e['conv'].sum() / e['den'].sum()) if e['den'].sum() else float('nan'),
                              'trade_share': float(e['trade'].mean()),
                              'events_per_game': float(len(e) / universe.get(c, 1))}
            out[str(bval)] = row
        return out

    geometry = {
        'corridor_degree': bucket_block('degree', lambda x: np.where(x['degree'] <= 0.75, 'tight<=0.75', 'open>0.75')),
        'open_ratio': bucket_block('open_ratio', lambda x: np.where(x['open_ratio'] < 0.75, 'tight<0.75', 'open>=0.75')),
        'bed_dist': bucket_block('bed_dist', lambda x: np.where(x['bed_dist'] <= 2, 'bed<=2', np.where(x['bed_dist'] <= 6, 'bed3-6', 'bed>6'))),
        'portal3': bucket_block('portal3', lambda x: np.where(x['portal3'] > 0, 'portal<=3', 'no_portal')),
    }
    mapclass = {}
    for mc in ('compact', 'open'):
        row = {}
        for c in ('top10', 'band', 'team7'):
            e = g[(g['cohort'] == c) & (g['map_class'] == mc)]
            if len(e):
                row[c] = {'n': int(len(e)), 'events_per_game': float(len(e) / universe.get(c, 1)),
                          'initiator_share': float(e['own_init'].dropna().mean()),
                          'conv_ratio': float(e['conv'].sum() / e['den'].sum()) if e['den'].sum() else float('nan'),
                          'trade_share': float(e['trade'].mean())}
        mapclass[mc] = row

    # S-3 deltas with CIs on the deciding shares
    s3 = {}
    for a, b in (('top10', 'band'), ('team7', 'band')):
        ga, gb = g[g['cohort'] == a], g[g['cohort'] == b]
        row = {}
        for name, (va, na, ca), (vb, nb, cb) in (
                ('initiator_share', _prop_ci(ga['own_init']), _prop_ci(gb['own_init'])),
                ('conv_ge2_share', _prop_ci(ga[ga['den'] >= 2]['conv'] >= 2), _prop_ci(gb[gb['den'] >= 2]['conv'] >= 2)),
                ('trade_share', _prop_ci(ga['trade']), _prop_ci(gb['trade'])),
                ('kill_for_share', _prop_ci(ga['own_kill']), _prop_ci(gb['own_kill'])),
                ('disengage_share', _prop_ci((ga['outcome'] == 'disengage').astype(float)),
                 _prop_ci((gb['outcome'] == 'disengage').astype(float)))):
            row[name] = {'a': va, 'b': vb, 'delta': va - vb, 'ci95_a': ca, 'ci95_b': cb, 'n_a': na, 'n_b': nb}
        row['group_events_per_game'] = {'a': len(ga) / universe.get(a, 1), 'b': len(gb) / universe.get(b, 1)}
        tra, trb = ga[ga['trade'] > 0], gb[gb['trade'] > 0]
        row['trade_ahead_share'] = {'a': float((tra['units'] > tra['opp_units']).mean()) if len(tra) else float('nan'),
                                    'b': float((trb['units'] > trb['opp_units']).mean()) if len(trb) else float('nan')}
        row['conv_ratio'] = {'a': float(ga['conv'].sum() / ga['den'].sum()) if ga['den'].sum() else float('nan'),
                             'b': float(gb['conv'].sum() / gb['den'].sum()) if gb['den'].sum() else float('nan')}
        s3[f'{a}_minus_{b}'] = row

    out = {'_meta': {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'n_events': int(len(ev)), 'n_games_with_events': int(ev['game'].nunique()),
        'n_ranked_side_games': int(len(uni)), 'universe': {k: int(v) for k, v in universe.items()},
        'definitions': (__doc__ or '').strip().split('CLI:')[0],
        'cohort_rule': 'team 7 fixed; top10 = rank<=10, r11_30 = 11-30, band = 55-85 in the ladder snapshot nearest game start',
    },
        'per_cohort': per_cohort, 'classes_per_game': classes, 'conditional_win': cond_win,
        'era': era, 'map_class_descriptive': mapclass, 'geometry': geometry, 's3_comparisons': s3}

    def clean(o):
        if isinstance(o, dict):
            return {k: clean(v) for k, v in o.items()}
        if isinstance(o, float) and o != o:
            return None
        return o

    Path(out_json).parent.mkdir(parents=True, exist_ok=True)
    json.dump(clean(out), open(out_json, 'w'), indent=1, sort_keys=True, allow_nan=False)
    Path(out_md).write_text(render_md(out))
    print(f'wrote {out_md} and {out_json}')


def render_md(out):
    L = ['# C2-0 — fight anatomy: is coordinated fighting worth building?', '',
         f"Generated {out['_meta']['generated_at'][:19]}Z from the public corpus (ranked completed games; both sides pooled; "
         f"no submission ids — pooled by team). {out['_meta']['n_events']} contact events over "
         f"{out['_meta']['n_games_with_events']} games; side-game universe per cohort in the JSON `_meta.universe`. "
         'Definitions as in `tools/analysis/features/fights.py` (Manhattan contact <= 4, window 6, group >= 3, '
         '5-round closure, adjacency-based initiator, deaths to last contact + 5).', '']
    pc = out['per_cohort']

    def f(x, pct=False):
        if x is None or x != x:
            return '—'
        return f'{100 * x:.1f}%' if pct else (f'{x:.2f}' if abs(x) < 10 else f'{x:.1f}')

    L += ['## Pooled, group-class fights per cohort', '',
          '| cohort | side-games | fights/game | initiator share ±ci | trades | kill-for | kill-against | disengage | own deaths/fight | own len lost/fight | trade ahead share | conv ratio | conv>=2 share | synced entries | rays/head pre | pearl Δ next10 | bed flip |',
          '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for c in COHORTS:
        b = pc[c]
        L.append('| %s | %d | %s | %s ±%s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            LABEL[c], b['n_side_games'], f(b['group_events_per_game']),
            f(b['initiator_share'], True), f(b['initiator_ci95'], True),
            f(b['trade_share'], True), f(b['kill_for_share'], True), f(b['kill_against_share'], True), f(b['disengage_share'], True),
            f(b['deaths_own_per_fight']), f(b['lenlost_own_per_fight']),
            f(b.get('trade_ahead_share'), True), f(b['conv_ratio']), f(b['conv_ge2_share'], True),
            f(b['synch_share'], True), f(b['rays_pre_per_head']), f(b['pearl_delta_next10']), f(b['bed_flip_share'], True)))
    L += ['', '## Contact classes per side-game', '',
          '| cohort | group | 2v1 | 1v1 | 2v2 | pair | 1v1 initiator share |', '|---|---|---|---|---|---|---|']
    for c in COHORTS:
        cl = out['classes_per_game'][c]
        L.append('| %s | %s | %s | %s | %s | %s | %s |' % (
            LABEL[c], f(cl['group']), f(cl['2v1']), f(cl['1v1']), f(cl['2v2']), f(cl['pair']),
            f(cl['1v1_initiator_share'], True)))
    L += ['', '## Win rate conditional on group-fight outcome (per side-game)', '']
    for c in COHORTS:
        cw = out['conditional_win'][c]
        L.append('- **%s**: %s' % (LABEL[c], '; '.join(
            f"{k}: {f(v['win_rate'], True)} (n={v['n']})" for k, v in sorted(cw.items()))))
    L += ['', '## Era split (group fights)', '',
          '| era | cohort | n | share | initiator | trades | conv ratio |', '|---|---|---|---|---|---|---|']
    for tag in ('early', 'mid', 'late'):
        for c in COHORTS:
            e = out['era'].get(tag, {}).get(c)
            if e:
                L.append('| %s | %s | %d | %s | %s | %s | %s |' % (
                    tag, LABEL[c], e['n'], f(e['share'], True), f(e['initiator_share'], True),
                    f(e['trade_share'], True), f(e['conv_ratio'])))
    L += ['', '## Geometry (top 10 vs band, group fights; no map identity)', '']
    for geo, buckets in out['geometry'].items():
        L.append(f'- **{geo}**: ' + '; '.join(
            f"{b}: top10 init {f(v['top10'].get('initiator_share'), True)} conv {f(v['top10'].get('conv_ratio'))} (n={v['top10'].get('n')}) "
            f"vs band init {f(v['band'].get('initiator_share'), True)} conv {f(v['band'].get('conv_ratio'))} (n={v['band'].get('n')})"
            for b, v in buckets.items() if 'top10' in v and 'band' in v))
    L += ['', '## Map class (descriptive only)', '']
    for mc, row in out['map_class_descriptive'].items():
        for c, v in row.items():
            L.append(f'- {mc} / {LABEL[c]}: n={v["n"]}, {f(v["events_per_game"])}/game, initiator {f(v["initiator_share"], True)}, '
                     f'trades {f(v["trade_share"], True)}, conv {f(v["conv_ratio"])}')
    L += ['', '## The S-3 comparisons', '']
    for name, row in out['s3_comparisons'].items():
        a, b = name.split('_minus_')
        L.append(f'### {LABEL.get(a, a)} − {LABEL.get(b, b)}')
        L.append('')
        L.append('| metric | %s | ±ci | %s | ±ci | delta |' % (LABEL.get(a, a), LABEL.get(b, b)))
        L.append('|---|---|---|---|---|---|')
        for k, v in row.items():
            if isinstance(v, dict) and 'delta' in v:
                L.append('| %s | %s | %s | %s | %s | %s |' % (
                    k, f(v['a'], True) if 'share' in k else f(v['a']),
                    f(v.get('ci95_a'), True) if 'share' in k else f(v.get('ci95_a', float('nan'))),
                    f(v['b'], True) if 'share' in k else f(v['b']),
                    f(v.get('ci95_b'), True) if 'share' in k else f(v.get('ci95_b', float('nan'))),
                    f(v['delta'], True) if 'share' in k else f(v['delta'])))
            elif isinstance(v, dict):
                L.append('| %s | %s | — | %s | — | %s |' % (k, f(v['a']), f(v['b']), f(v['a'] - v['b']) if v['a'] == v['a'] and v['b'] == v['b'] else '—'))
        L.append('')
    L += ['## Reading', '']
    L += ['(written at the end of the run — see the JSON for every number behind these lines.)']
    L += ['']
    return '\n'.join(L) + '\n'


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    ex = sub.add_parser('extract')
    ex.add_argument('paths', nargs='+')
    ex.add_argument('--out', required=True)
    ex.add_argument('--jobs', type=int, default=max(1, multiprocessing.cpu_count() - 2))
    ex.add_argument('--cache', default=None)
    rp = sub.add_parser('report')
    rp.add_argument('--events', required=True)
    rp.add_argument('--index', default='public_replays/corpus/index.jsonl')
    rp.add_argument('--ladder', default='public_replays/corpus/ladder')
    rp.add_argument('--out-md', default='docs/analysis/C2-fight-anatomy.md')
    rp.add_argument('--out-json', default='game_stats/fight_anatomy.json')
    a = ap.parse_args()
    if a.cmd == 'extract':
        extract([Path(p) for p in a.paths], a.out, a.jobs, a.cache)
    else:
        report(a.events, a.index, a.ladder, a.out_md, a.out_json)
