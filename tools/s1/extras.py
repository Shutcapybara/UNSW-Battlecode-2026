"""s1 extras: per-side-round, per-side-game, per-death and per-transit features the F1 extractor does not produce.

Focus: the opening (rounds 0-150 stored every round) and own goals / portals. Inputs: a decoded frame `g`
(tools.analysis.features.frame) and the F1 `extract()` output for the same game. Definitions: docs/findings/s1-STORE.md.
"""
import collections, math
import numpy as np

EARLY = 150          # rounds 0..EARLY are stored every round
STRIDE = 5           # after EARLY, every STRIDE rounds
LAST = 500           # series are padded (terminal state carried forward) to this round
VIEW = 3             # 7x7 view (Chebyshev radius 3)
REACH_STEPS = 5
OWN_GOALS = ('wall', 'self', 'ally_body', 'h2h_ally', 'invalid')
DXY = ((0, -1), (1, 0), (0, 1), (-1, 0))   # N E S W (replay step codes 0..3)


def stored_rounds(last=LAST):
    return [r for r in range(last + 1) if r <= EARLY or r % STRIDE == 0]


def _tor(a, n):
    a = np.abs(a)
    return np.minimum(a, n - a)


def _circ_rg(xs, ys, W, H):
    """RMS torus distance of heads to their circular mean (radius of gyration of the swarm)"""
    def centre(v, n):
        ang = 2 * np.pi * v / n
        s, c = np.sin(ang).sum(), np.cos(ang).sum()
        return (math.atan2(s, c) % (2 * math.pi)) * n / (2 * math.pi) if abs(s) + abs(c) > 1e-9 else v[0]
    cx, cy = centre(xs, W), centre(ys, H)
    dx, dy = _tor(xs - cx, W), _tor(ys - cy, H)
    return float(np.sqrt((dx * dx + dy * dy).mean()))


def _bfs_count(nbr, src, blocked, limit):
    seen = {src}
    frontier = [src]
    for _ in range(limit):
        nxt = []
        for c in frontier:
            for n in nbr[c]:
                if n is not None and n not in seen and n not in blocked:
                    seen.add(n)
                    nxt.append(n)
        frontier = nxt
    return len(seen)


def run(g, out, beds):
    W, H, nbr = g['W'], g['H'], g['nbr']
    rounds = g['rounds']
    R = len(rounds) - 1
    ev = g['events']
    offs = [(dx, dy) for dx in range(-VIEW, VIEW + 1) for dy in range(-VIEW, VIEW + 1)]
    kelp_adj = {c: sum(1 for n in v if n is None) for c, v in nbr.items()}
    bed_view, bed_touch = collections.defaultdict(list), collections.defaultdict(list)
    for b in beds:
        for dx, dy in offs:
            bed_view[((b[0] + dx) % W, (b[1] + dy) % H)].append(b)
            if abs(dx) <= 1 and abs(dy) <= 1:
                bed_touch[((b[0] + dx) % W, (b[1] + dy) % H)].append(b)
    nbeds = max(len(beds), 1)
    teams, birth = {}, {}
    seen_beds = {t: set() for t in 'AB'}
    arrive = {t: {} for t in 'AB'}
    first_head_view = {t: None for t in 'AB'}
    store = set(r for r in stored_rounds(R) if r <= R)
    col = {t: collections.defaultdict(dict) for t in 'AB'}     # name -> {round: value}

    for r, snap in enumerate(rounds):
        hs = {t: [] for t in 'AB'}
        for i, (t, b) in snap.items():
            teams[i] = t
            if i not in birth:
                birth[i] = (r, b[0])
            hs[t].append((i, b[0], len(b)))
        arr = {t: (np.array([h[1][0] for h in hs[t]]), np.array([h[1][1] for h in hs[t]])) for t in 'AB'}
        for t in 'AB':
            o = 'B' if t == 'A' else 'A'
            for i, h, L in hs[t]:
                for b in bed_view.get(h, ()):
                    seen_beds[t].add(b)
                for b in bed_touch.get(h, ()):
                    arrive[t].setdefault(b, r)
            # enemy head inside some 7x7 view of ours
            n_view = 0
            if hs[t] and hs[o]:
                (xa, ya), (xb, yb) = arr[t], arr[o]
                cheb = np.maximum(_tor(xa[:, None] - xb[None, :], W), _tor(ya[:, None] - yb[None, :], H))
                n_view = int((cheb.min(1) <= VIEW).sum())
            if n_view and first_head_view[t] is None:
                first_head_view[t] = r
            if r not in store:
                continue
            c = col[t]
            n = len(hs[t])
            if hs[t] and hs[o]:
                man = _tor(xa[:, None] - xb[None, :], W) + _tor(ya[:, None] - yb[None, :], H)
                c['enemy_head_dist_mean'][r] = float(man.min(1).mean())     # mean over our heads of the nearest enemy head
                c['enemy_head_dist_min'][r] = float(man.min())
            c['enemy_head_view_share'][r] = n_view / n if n else np.nan
            c['beds_seen_share'][r] = len(seen_beds[t]) / nbeds
            c['beds_reached_share'][r] = len(arrive[t]) / nbeds
            if not n:
                continue
            xs, ys = arr[t]
            bx = np.array([birth[i][1][0] for i, h, L in hs[t]])
            by = np.array([birth[i][1][1] for i, h, L in hs[t]])
            age = np.array([r - birth[i][0] for i, h, L in hs[t]], dtype=float)
            disp = _tor(xs - bx, W) + _tor(ys - by, H)
            c['disp_mean'][r] = float(disp.mean())
            c['disp_max'][r] = float(disp.max())
            ok = age >= 1
            c['disp_per_turn'][r] = float((disp[ok] / age[ok]).mean()) if ok.any() else np.nan
            c['kelp_adj_mean'][r] = float(np.mean([kelp_adj[h] for i, h, L in hs[t]]))
            if n >= 2:
                D = _tor(xs[:, None] - xs[None, :], W) + _tor(ys[:, None] - ys[None, :], H)
                iu = np.triu_indices(n, 1)
                c['pair_dist_mean'][r] = float(D[iu].mean())
                D = D + np.eye(n) * 1e9
                nn = D.min(1)
                c['nn_dist_mean'][r] = float(nn.mean())
                c['clustered_share'][r] = float((nn <= 3).mean())
                c['swarm_rg'][r] = _circ_rg(xs, ys, W, H)
                # cells of the map per dragon inside the swarm's bounding radius: a density proxy
                c['swarm_density'][r] = n / (math.pi * max(c['swarm_rg'][r], 1.0) ** 2)
            else:
                c['nn_dist_mean'][r] = np.nan
                c['swarm_rg'][r] = 0.0
            if r % STRIDE == 0:
                blocked = {x for i, (tt, b) in snap.items() for x in b}
                reach = [_bfs_count(nbr, h, blocked - {h}, REACH_STEPS) for i, h, L in hs[t]]
                c['reach5_mean'][r] = float(np.mean(reach))
                c['reach_le8_share'][r] = float(np.mean([x <= 8 for x in reach]))
                c['reach_le15_share'][r] = float(np.mean([x <= 15 for x in reach]))

    # ---------------- per-round events (per round, cumulated by the caller) ----------------
    E = {t: collections.defaultdict(lambda: np.zeros(R + 1)) for t in 'AB'}
    death_by = {d['id']: d for d in ev['deaths']}
    transits = []
    last_head = {}
    for a in ev['actions']:
        r, i, t = a['round'], a['id'], a['team']
        if r < 0 or r > R:
            continue
        if a['kind'] is None or (a['kind'] == 'move' and not a.get('steps')):
            E[t]['idle'][r] += 1
        if a['kind'] != 'move' or not a.get('dirs'):
            continue
        E[t]['steps'][r] += len(a['dirs'])
        b = rounds[r].get(i)
        if b is None:
            continue
        cur = b[1][0]
        dirs = a['dirs']
        hist = last_head.setdefault(i, collections.deque(maxlen=2))
        # U-turn over two moves: first step now opposite to the heading two moves ago (moves on consecutive rounds)
        if len(hist) == 2 and hist[0][0] == r - 2 and hist[1][0] == r - 1 and (dirs[0] + 2) % 4 == hist[0][1]:
            E[t]['turnaround'][r] += 1
        hist.append((r, dirs[-1]))
        view = None
        for k, d in enumerate(dirs):
            nx = nbr[cur][d] if d < 4 else None
            if nx is None:
                break
            gx = ((cur[0] + DXY[d][0]) % W, (cur[1] + DXY[d][1]) % H)
            if nx != gx:
                if view is None:
                    view = set()
                    for j, (tt, bb) in rounds[r].items():
                        if tt == t:
                            h = bb[0]
                            for dx, dy in offs:
                                view.add(((h[0] + dx) % W, (h[1] + dy) % H))
                back = ((nx[0] - DXY[d][0]) % W, (nx[1] - DXY[d][1]) % H)
                e_in, e_out = tuple(sorted([cur, gx])), tuple(sorted([back, nx]))
                pair = tuple(sorted([e_in, e_out]))      # portal identity: the two crossed edges, direction-free
                transits.append(dict(round=r, id=i, side=t, step=k, n_steps=len(dirs), length=len(b[1]),
                                     entry=f'{cur[0]},{cur[1]}', exit=f'{nx[0]},{nx[1]}',
                                     pair='|'.join(f'{a[0]},{a[1]}~{b[0]},{b[1]}' for a, b in pair), blind=nx not in view,
                                     age=r - birth.get(i, (0, None))[0]))
                E[t]['transits'][r] += 1
            cur = nx
    by_pair = collections.defaultdict(list)
    for x in transits:
        by_pair[x['pair']].append(x)
    moved_pairs = collections.defaultdict(set)
    for x in transits:
        near = [y for y in by_pair[x['pair']] if y is not x and abs(y['round'] - x['round']) <= 2]
        # same-pair double: another of our dragons through the same portal within +-2 rounds; contested: an enemy did
        x['double'] = any(y['side'] == x['side'] and y['id'] != x['id'] for y in near)
        x['contested'] = any(y['side'] != x['side'] for y in near)
        d = death_by.get(x['id'])
        dr = d['round'] if d else None
        x['died_same_move'] = bool(d and dr == x['round'] and d.get('actor') == x['id'])
        x['died_within3'] = bool(d and 0 <= dr - x['round'] <= 3)
        x['died_within10'] = bool(d and 0 <= dr - x['round'] <= 10)
        x['death_cause'] = d['cause'] if d and 0 <= dr - x['round'] <= 10 else None
        x['death_round'] = dr
        E[x['side']]['transit_blind'][x['round']] += x['blind']
        E[x['side']]['transit_double'][x['round']] += x['double']
        E[x['side']]['transit_contested'][x['round']] += x['contested']
        E[x['side']]['transit_died3'][x['round']] += x['died_within3']
        E[x['side']]['transit_died_same'][x['round']] += x['died_same_move']
        moved_pairs[x['side']].add(x['pair'])
    for p in ev['sonar']:
        hit = p.get('hit')
        if isinstance(hit, int) and hit in teams and 0 <= p['round'] <= R:
            rt = teams[hit]
            if hit == p['id']:
                E[rt]['sonar_recv_self'][p['round']] += 1      # own ray back into own body (not a packet)
                continue
            E[rt]['sonar_recv'][p['round']] += 1
            E[rt]['sonar_recv_enemy' if p.get('team') != rt else 'sonar_recv_ally'][p['round']] += 1

    # ---------------- deaths ----------------
    tr_by = collections.defaultdict(list)
    for x in transits:
        tr_by[x['id']].append(x)
    deaths = []
    for d in out['deaths']:
        r = d['round']
        snap = rounds[min(r, R)]
        me = snap.get(d['id'])
        h = me[1][0] if me else None
        cnt = collections.Counter()
        if h is not None:
            for j, (tt, b) in snap.items():
                if j == d['id']:
                    continue
                hh = b[0]
                if min(abs(hh[0] - h[0]), W - abs(hh[0] - h[0])) + min(abs(hh[1] - h[1]), H - abs(hh[1] - h[1])) <= 3:
                    cnt['ally' if tt == d['side'] else 'enemy'] += 1
        trs = [x for x in tr_by.get(d['id'], ()) if 0 <= r - x['round'] <= 3]
        deaths.append(dict(game=d['game'], id=d['id'], round=r, side=d['side'],
                           own_goal=d['cls'] in OWN_GOALS, ally_heads3=cnt['ally'], enemy_heads3=cnt['enemy'],
                           crowd=cnt['ally'] + cnt['enemy'] >= 2,
                           transit_same_move=any(x['round'] == r for x in trs), transit_within3=bool(trs),
                           transit_blind=any(x['blind'] for x in trs), born=birth.get(d['id'], (0,))[0],
                           kelp_adj=kelp_adj.get(h, np.nan) if h else np.nan))
        t = d['side']
        if d['cls'] in OWN_GOALS:
            E[t]['own_goals'][r] += 1
        if trs:
            E[t]['deaths_post_transit'][r] += 1
        if cnt['ally'] + cnt['enemy'] >= 2:
            E[t]['deaths_crowd'][r] += 1
        if d.get('enclosed'):
            E[t]['deaths_enclosed'][r] += 1
        if d.get('newborn'):
            E[t]['deaths_newborn'][r] += 1
        if d.get('near_portal'):
            E[t]['deaths_near_portal'][r] += 1

    # ---------------- side-game extras ----------------
    S = {t: {} for t in 'AB'}
    tot = {t: np.array([sum(len(b) for i, (tt, b) in s.items() if tt == t) for s in rounds], dtype=float) for t in 'AB'}
    fights = [d['round'] for d in out['deaths'] if d['cls'] in ('enemy_body', 'h2h_enemy')]
    first_fight = min(fights) if fights else None
    for t in 'AB':
        o = 'B' if t == 'A' else 'A'
        s = S[t]
        s['first_enemy_head_view'] = first_head_view[t]
        s['first_fight'] = first_fight
        a, b = tot[t], tot[o]
        m = np.maximum(a, b)
        rel = np.where(m > 0, (a - b) / np.maximum(m, 1), 0)
        idx = np.nonzero(np.abs(rel) > 0.10)[0]
        s['gap10_round'] = int(idx[0]) if len(idx) else None
        s['gap10_ahead'] = (1 if rel[idx[0]] > 0 else 0) if len(idx) else None
        signs = []
        for c in (50, 100, 150):
            x = rel[min(c, R)]
            s[f'lead@{c}'] = 1 if x > 0 else -1 if x < 0 else 0
            signs.append(s[f'lead@{c}'])
        s['lead_flips_50_150'] = sum(1 for u, v in zip(signs, signs[1:]) if u * v < 0)
        first = arrive[t]
        s['bed_first_share'] = (sum(1 for bb in beds if bb in first and (bb not in arrive[o] or first[bb] < arrive[o][bb]))
                                + 0.5 * sum(1 for bb in beds if bb in first and bb in arrive[o] and first[bb] == arrive[o][bb])) / nbeds
        s['bed_arrival_median'] = float(np.median(list(first.values()))) if first else None
        for c in (50, 100, 150):
            s[f'beds_reached@{c}'] = sum(1 for v in first.values() if v <= c) / nbeds
        trs = [x for x in transits if x['side'] == t]
        s['transits'] = len(trs)
        for c in (50, 100, 150):
            s[f'transits@{c}'] = sum(1 for x in trs if x['round'] <= c)
        s['transit_pairs'] = len(moved_pairs[t])
        s['transit_surv3'] = 1 - np.mean([x['died_within3'] for x in trs]) if trs else None
        s['transit_died_same_share'] = np.mean([x['died_same_move'] for x in trs]) if trs else None
        s['transit_blind_share'] = np.mean([x['blind'] for x in trs]) if trs else None
        s['transit_double_share'] = np.mean([x['double'] for x in trs]) if trs else None
        s['transit_contested_share'] = np.mean([x['contested'] for x in trs]) if trs else None
        s['transit_double_died3_share'] = np.mean([x['died_within3'] for x in trs if x['double']]) if any(x['double'] for x in trs) else None
        s['transit_blind_died3_share'] = np.mean([x['died_within3'] for x in trs if x['blind']]) if any(x['blind'] for x in trs) else None
        early = [x for x in trs if x['round'] <= EARLY]
        s['transit_surv3_0_150'] = 1 - np.mean([x['died_within3'] for x in early]) if early else None
        sp = [x for x in ev['splits'] if x['team'] == t and x['round'] <= EARLY]
        kids = [x['child'] for x in sp]
        s['births_0_150'] = len(kids)
        s['newborn_surv10_0_150'] = (np.mean([not (k in death_by and death_by[k]['round'] - birth.get(k, (0,))[0] <= 10) for k in kids])
                                     if kids else None)
        first_eat = {}
        for e in ev['eats']:
            first_eat.setdefault(e['id'], e['round'])
        ttf = [first_eat[k] - birth.get(k, (0,))[0] for k in kids if k in first_eat]
        s['newborn_first_pearl_median_0_150'] = float(np.median(ttf)) if ttf else None
        s['newborn_ever_ate_share_0_150'] = len(ttf) / len(kids) if kids else None
        ch = [x['child_len'] for x in sp]
        s['child_len_mean_0_150'] = float(np.mean(ch)) if ch else None
        for lo, hi in ((1, 2), (3, 3), (4, 5), (6, 999)):
            s[f'child_len_{lo}_{hi if hi < 999 else "up"}_share_0_150'] = (sum(1 for x in ch if lo <= x <= hi) / len(ch)) if ch else None
    splits = [dict(round=x['round'], side=x['team'], parent=x['parent'], child=x['child'], before=x['before'],
                   parent_len=x['parent_len'], child_len=x['child_len'],
                   child_died10=bool(x['child'] in death_by and death_by[x['child']]['round'] - x['round'] <= 10))
              for x in ev['splits']]
    return dict(cols=col, events=E, sides=S, deaths=deaths, transits=transits, splits=splits, R=R)
