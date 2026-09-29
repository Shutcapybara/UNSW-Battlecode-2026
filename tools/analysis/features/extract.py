"""Feature extraction over decoded frames (F1 feature lab).

extract(g) -> dict(side_rows=[2 dicts], series=[per-round rows], dragons=[per-dragon rows], deaths=[rows])
Every side-game row carries the game context (map, map class, map_hash, side, bot, opponent, winner, reason ...)
so any split is a filter. Feature metadata lives in registry.REGISTRY.
Units: side-game rows are one side of one game; series rows are one side of one round; dragon rows one dragon.
"""
import collections, math
import numpy as np
from statistics import pstdev

CHECKPOINTS = (25, 50, 100, 150, 250, 400, 499)
SAMPLE = 5                   # rounds between territory / EPG / enclosure samples
VIEW = 3                     # 7x7 view = Chebyshev radius 3
REACH_STEPS = 5              # enclosure: cells reachable within 5 steps, bodies blocked
REACH_MAX = 1 + 2 * REACH_STEPS * (REACH_STEPS + 1)   # 61 on open ground
ENCLOSED = 15                # reach5 <= 15 counts as enclosed (≈ a quarter of open ground)
TAUS = (1, 2, 4)
COMPACT = {'Portals', 'Prisoners Dilemma', 'Devil', 'Trophy'}


def other(t):
    return 'B' if t == 'A' else 'A'


def tdelta(a, b, n):
    """shortest signed displacement a->b on a ring of size n"""
    d = (b - a) % n
    return d - n if d > n / 2 else d


def gini(xs):
    xs = sorted(xs)
    n = len(xs)
    if n == 0 or sum(xs) == 0:
        return float('nan')
    cum = sum((i + 1) * x for i, x in enumerate(xs))
    return (2 * cum) / (n * sum(xs)) - (n + 1) / n


def bfs(nbr, sources, limit=None, blocked=None):
    dist = {}
    q = collections.deque()
    for s in sources:
        if s not in dist:
            dist[s] = 0
            q.append(s)
    while q:
        c = q.popleft()
        d = dist[c]
        if limit is not None and d >= limit:
            continue
        for n in nbr[c]:
            if n is not None and n not in dist and (blocked is None or n not in blocked):
                dist[n] = d + 1
                q.append(n)
    return dist


def extract(g, meta=None):
    meta = meta or {}
    from .beds import resolve
    beds, beds_source = resolve(g)          # server replays blank bed timings; recovered from REPO/maps by terrain match
    W, H, nbr = g['W'], g['H'], g['nbr']
    cells = W * H
    R = len(g['rounds']) - 1            # rounds[R] is the final state
    ev = g['events']
    lam = {c: 2.0 / (lo + hi) for c, (lo, hi) in beds.items()}   # nominal bed rate, pearls/round
    capacity = sum(lam.values())
    static_reach = {}
    # pearl density: nominal bed rate summed over the 7x7 view, relative to the map-average view
    map_view_rate = capacity * (2 * VIEW + 1) ** 2 / cells
    view_rate = {}
    for x in range(W):
        for y in range(H):
            view_rate[(x, y)] = sum(lam.get(((x + dx) % W, (y + dy) % H), 0.0)
                                    for dx in range(-VIEW, VIEW + 1) for dy in range(-VIEW, VIEW + 1))

    def reach(c, blocked):
        return len(bfs(nbr, [c], REACH_STEPS, blocked))

    # ---------------- per-round snapshot series ----------------
    S = {t: collections.defaultdict(lambda: [0.0] * (R + 1)) for t in 'AB'}
    seen = {t: set() for t in 'AB'}
    visited = {t: set() for t in 'AB'}
    head_path = collections.defaultdict(list)       # id -> [(round, head)]
    dragon_turn_bed = collections.Counter()
    dragon_turn_contact = collections.Counter()
    dragon_turns = collections.Counter()
    leader = {t: None for t in 'AB'}
    samples = []
    reach_hist = collections.Counter()   # (side, reach5) -> sampled dragon-turns (exposure for the hazard curve)
    offs = [(dx, dy) for dx in range(-VIEW, VIEW + 1) for dy in range(-VIEW, VIEW + 1)]
    for r, snap in enumerate(g['rounds']):
        occ_team = {}
        for i, (t, b) in snap.items():
            for c in b:
                occ_team[c] = t
        for t in 'AB':
            mine = [(i, b) for i, (tt, b) in snap.items() if tt == t]
            lens = sorted((len(b) for i, b in mine), reverse=True)
            s = S[t]
            s['units'][r] = len(lens)
            s['total'][r] = sum(lens)
            s['longest'][r] = lens[0] if lens else 0
            s['mean_len'][r] = sum(lens) / len(lens) if lens else 0
            s['top1_share'][r] = lens[0] / sum(lens) if lens else float('nan')
            s['top3_share'][r] = sum(lens[:3]) / sum(lens) if lens else float('nan')
            s['len_cv'][r] = pstdev(lens) / (sum(lens) / len(lens)) if len(lens) > 1 else 0.0
            s['len_gini'][r] = gini(lens) if len(lens) > 1 else 0.0
            s['small_share'][r] = sum(1 for x in lens if x <= 3) / len(lens) if lens else float('nan')
            s['big_share'][r] = sum(1 for x in lens if x >= 10) / len(lens) if lens else float('nan')
            lid = max(mine, key=lambda ib: (len(ib[1]), -ib[0]))[0] if mine else None
            s['leader_change'][r] = 1.0 if (r > 0 and lid is not None and leader[t] is not None and lid != leader[t]) else 0.0
            leader[t] = lid if lid is not None else leader[t]
            new = 0
            contact = 0
            onbed = 0
            for i, b in mine:
                h = b[0]
                head_path[i].append((r, h))
                if r < R:
                    dragon_turns[i] += 1
                visited[t].add(h)
                dens = view_rate[h] / map_view_rate if map_view_rate else float('nan')
                onbed += dens
                if r < R:
                    dragon_turn_bed[i] += dens
                sees_enemy = False
                for dx, dy in offs:
                    c = ((h[0] + dx) % W, (h[1] + dy) % H)
                    if c not in seen[t]:
                        seen[t].add(c)
                        new += 1
                    if not sees_enemy and occ_team.get(c) == other(t):
                        sees_enemy = True
                if sees_enemy:
                    contact += 1
                    if r < R:
                        dragon_turn_contact[i] += 1
            s['new_seen'][r] = new
            s['seen_share'][r] = len(seen[t]) / cells
            s['visited_share'][r] = len(visited[t]) / cells
            s['contact_share'][r] = contact / len(mine) if mine else float('nan')
            s['density_ratio'][r] = onbed / len(mine) if mine else float('nan')
            s['pearls_on_board'][r] = len(g['pearls'][r])
        # ---- sampled: territory, EPG access, enclosure ----
        if r % SAMPLE == 0 or r == R:
            heads = {t: [b[0] for i, (tt, b) in snap.items() if tt == t] for t in 'AB'}
            dist = {t: bfs(nbr, heads[t]) if heads[t] else {} for t in 'AB'}
            blocked = set(occ_team)
            row = dict(round=r)
            for t in 'AB':
                da, db = dist[t], dist[other(t)]
                inf = 10 ** 6
                terr = cont = reachable = 0.0
                for c in nbr:
                    x, y = da.get(c, inf), db.get(c, inf)
                    if x == inf and y == inf:
                        continue
                    reachable += 1
                    if x < y:
                        terr += 1
                    elif x == y:
                        terr += 0.5
                    if abs(x - y) <= 1 and x < inf and y < inf:
                        cont += 1
                bterr = bexp = 0.0
                acc = {tau: 0.0 for tau in TAUS}
                for c, l in lam.items():
                    x, y = da.get(c, inf), db.get(c, inf)
                    if x < y:
                        bterr += l
                    elif x == y and x < inf:
                        bterr += l / 2
                    if x < inf:
                        for tau in TAUS:
                            acc[tau] += l * math.exp(-x / tau)
                    # contested expected share: logistic in distance advantage
                    if x < inf or y < inf:
                        adv = (y if y < inf else 99) - (x if x < inf else 99)
                        bexp += l / (1 + math.exp(-adv))
                mine = [(i, b) for i, (tt, b) in snap.items() if tt == t]
                reaches = []
                for i, b in mine:
                    x = reach(b[0], blocked - {b[0]})
                    reaches.append(x)
                    if r < R:
                        reach_hist[(t, x)] += 1
                row[t] = dict(territory=terr / reachable if reachable else float('nan'), contested=cont / reachable if reachable else float('nan'),
                              bed_territory=bterr / capacity if capacity else float('nan'),
                              bed_expected_share=bexp / capacity if capacity else float('nan'),
                              **{f'access_tau{tau}': acc[tau] for tau in TAUS},
                              reach_mean=sum(reaches) / len(reaches) if reaches else float('nan'),
                              enclosed_share=sum(1 for x in reaches if x <= ENCLOSED) / len(reaches) if reaches else float('nan'))
            samples.append(row)

    # ---------------- per-round event series ----------------
    E = {t: collections.defaultdict(lambda: [0.0] * (R + 1)) for t in 'AB'}
    for e in ev['eats']:
        E[e['team']]['eats'][e['round']] += 1
        E[e['team']]['eats_' + e['origin']][e['round']] += 1
    for e in ev['spawns']:
        if e['origin'] == 'bed' and 0 <= e['round'] <= R:
            for t in 'AB':
                E[t]['bed_spawns'][e['round']] += 1
    for e in ev['splits']:
        E[e['team']]['splits'][e['round']] += 1
    died_moving = {(d['round'], d['id']) for d in ev['deaths'] if d['actor'] == d['id']}
    for a in ev['actions']:
        t = a['team']
        if a['round'] < 0:
            continue
        if a['kind'] == 'move':
            E[t]['moves'][a['round']] += 1
            if a['steps'] > 1:
                E[t]['sprints'][a['round']] += 1
                E[t]['sprint_cost'][a['round']] += a.get('paid', 0)   # paid step by step; a death mid-sprint stops payment
        elif a['kind'] == 'suicide':
            E[t]['suicides'][a['round']] += 1
        elif a['kind'] is None:
            E[t]['no_action'][a['round']] += 1
        if a['tle']:
            E[t]['tle'][a['round']] += 1
    suicided = {(a['round'], a['id']) for a in ev['actions'] if a['kind'] == 'suicide'}
    deaths = []
    for d in ev['deaths']:
        t = d['team']
        cls = death_class(d, suicided)
        E[t]['deaths'][d['round']] += 1
        E[t]['death_' + cls][d['round']] += 1
        E[t]['length_lost'][d['round']] += d['length']
        if d.get('killer_team') == other(t):
            E[other(t)]['kills'][d['round']] += 1
            E[other(t)]['kill_length'][d['round']] += d['length']
        snap = g['rounds'][d['round']] if d['round'] <= R else {}
        occ = {c for i, (tt, b) in snap.items() for c in b}
        body = snap.get(d['id'], (t, (d['head'],)))[1]
        rch = reach(body[0], occ - {body[0]})
        if body[0] not in static_reach:
            static_reach[body[0]] = reach(body[0], None)
        near_portal = any(c in g['portal_cells'] for c in bfs(nbr, [d['head']], 2))
        deaths.append(dict(round=d['round'], id=d['id'], side=t, cause=d['cause'], cls=cls, length=d['length'], age=d['age'],
                           newborn=(not d['initial']) and d['age'] <= 10, reach5=rch, static_reach5=static_reach[body[0]],
                           enclosed=rch <= ENCLOSED, near_portal=near_portal, killer_team=d.get('killer_team')))
    # sonar: direction, relative direction to own team centre and to nearest enemy head, hit kinds
    team_cache, foe_cache = {}, {}
    for p in ev['sonar']:
        t = p['team']
        if t is None or p['round'] < 0 or p['round'] > R:
            continue
        r = p['round']
        E[t]['rays'][r] += 1
        if p.get('refracted'):
            E[t]['rays_refracted'][r] += 1
        else:
            E[t]['rays_' + 'NESW'[p['dir'] % 4]][r] += 1   # compass share over rays that left the head
        E[t]['ray_' + p['hit_kind']][r] += 1
        ox, oy = p['origin']
        vx, vy = ((0, -1), (1, 0), (0, 1), (-1, 0))[p['dir'] % 4]
        key = (r, t)
        if key not in team_cache:   # per round and team: angle sums of allied heads, foe heads
            snap = g['rounds'][r]
            hs = {i: b[0] for i, (tt, b) in snap.items() if tt == t}
            ang = {i: (math.sin(2 * math.pi * h[0] / W), math.cos(2 * math.pi * h[0] / W),
                       math.sin(2 * math.pi * h[1] / H), math.cos(2 * math.pi * h[1] / H)) for i, h in hs.items()}
            tot = [sum(a[k] for a in ang.values()) for k in range(4)]
            fl = [b[0] for i, (tt, b) in snap.items() if tt != t]
            team_cache[key] = (ang, tot, (np.array([h[0] for h in fl]), np.array([h[1] for h in fl])) if fl else None)
        ang, tot, foes = team_cache[key]
        n_al = len(ang) - (1 if p['id'] in ang else 0)
        if n_al > 0:
            own = ang.get(p['id'], (0, 0, 0, 0))
            sx, cx_, sy, cy_ = (tot[k] - own[k] for k in range(4))
            cx = (math.atan2(sx, cx_) % (2 * math.pi)) * W / (2 * math.pi) if abs(sx) + abs(cx_) > 1e-9 else ox
            cy = (math.atan2(sy, cy_) % (2 * math.pi)) * H / (2 * math.pi) if abs(sy) + abs(cy_) > 1e-9 else oy
            dot = vx * tdelta(ox, cx, W) + vy * tdelta(oy, cy, H)
            E[t]['rays_toward_com' if dot > 0.5 else 'rays_away_com' if dot < -0.5 else 'rays_side_com'][r] += 1
        if foes is not None:
            okey = (r, ox, oy, t)
            f = foe_cache.get(okey)
            if f is None:
                fx, fy = foes
                dx, dy = (fx - ox) % W, (fy - oy) % H
                dx = np.where(dx > W / 2, dx - W, dx)
                dy = np.where(dy > H / 2, dy - H, dy)
                k = int(np.argmin(np.abs(dx) + np.abs(dy)))
                f = (int(fx[k]), int(fy[k]))
                foe_cache[okey] = f
            dot = vx * tdelta(ox, f[0], W) + vy * tdelta(oy, f[1], H)
            E[t]['rays_toward_enemy' if dot > 0 else 'rays_away_enemy' if dot < 0 else 'rays_side_enemy'][r] += 1
    # dragon-turn denominators per round
    for t in 'AB':
        for r in range(R + 1):
            E[t]['dragon_turns'][r] = S[t]['units'][r] if r < R else 0

    # ---------------- per-dragon table ----------------
    born = {i: 0 for i in g['rounds'][0]}
    for s in ev['splits']:
        born[s['child']] = s['round']
    died = {d['id']: d for d in ev['deaths']}
    eats_by = collections.Counter(e['id'] for e in ev['eats'])
    rays_by = collections.Counter(p['id'] for p in ev['sonar'])
    sprints_by = collections.Counter(a['id'] for a in ev['actions'] if a['kind'] == 'move' and a['steps'] > 1)
    teams = {}
    for snap in g['rounds']:
        for i, (t, b) in snap.items():
            teams[i] = t
    maxlen = collections.Counter()
    for snap in g['rounds']:
        for i, (t, b) in snap.items():
            maxlen[i] = max(maxlen[i], len(b))
    dragons = []
    for i, path in head_path.items():
        xs, ys = [0.0], [0.0]
        for (r0, a), (r1, b) in zip(path, path[1:]):
            xs.append(xs[-1] + tdelta(a[0], b[0], W))
            ys.append(ys[-1] + tdelta(a[1], b[1], H))
        mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        rg = math.sqrt(sum((x - mx) ** 2 + (y - my) ** 2 for x, y in zip(xs, ys)) / len(xs))
        n = max(dragon_turns[i], 1)
        d = died.get(i)
        dragons.append(dict(id=i, side=teams[i], born=born.get(i, 0), died=d['round'] if d else None,
                            cause=death_class(d, suicided) if d else None, lifetime=(d['round'] if d else R) - born.get(i, 0),
                            max_len=maxlen[i], turns=dragon_turns[i], gyration=rg, density_ratio=dragon_turn_bed[i] / n,
                            contact_share=dragon_turn_contact[i] / n, rays_per_turn=rays_by[i] / n, eats=eats_by[i],
                            eats_per_100=100 * eats_by[i] / n, sprint_share=sprints_by[i] / n, initial=born.get(i, 0) == 0))

    # ---------------- assemble ----------------
    base = dict(game=g['id'], map=g['map'], map_class='compact' if g['map'] in COMPACT else 'open', map_hash=g['map_hash'],
                cells=cells, dragons_start=g.get('n_initial'), beds=len(beds), beds_source=beds_source, bed_capacity=capacity, rounds=R, reason=g['reason'], **meta)
    series = []
    for t in 'AB':
        for r in range(R + 1):
            row = dict(game=g['id'], side=t, round=r)
            for k, v in S[t].items():
                row[k] = v[r]
            for k, v in E[t].items():
                row[k] = v[r]
            series.append(row)
    side_rows = [side_features(g, t, S, E, samples, deaths, dragons, base, R, capacity) for t in 'AB']
    for row in dragons:
        row.update(game=g['id'], map=g['map'])
    for row in deaths:
        row.update(game=g['id'], map=g['map'])
    samp_rows = []
    for s in samples:
        for t in 'AB':
            r = s['round']
            nxt = sum(E[t]['eats_bed'][r:r + 10]) if 'eats_bed' in E[t] else 0
            samp_rows.append(dict(game=g['id'], map=g['map'], side=t, round=r, bed_eats_next10=nxt,
                                  units=S[t]['units'][min(r, R)], **s[t]))
    exposure = [dict(game=g['id'], map=g['map'], side=t, reach5=x, sampled_turns=n) for (t, x), n in reach_hist.items()]
    return dict(side_rows=side_rows, series=series, dragons=dragons, deaths=deaths, samples=samp_rows, exposure=exposure)


def circ_mean(vals, n):
    a = [2 * math.pi * v / n for v in vals]
    s, c = sum(map(math.sin, a)), sum(map(math.cos, a))
    if abs(s) < 1e-9 and abs(c) < 1e-9:
        return vals[0]
    return (math.atan2(s, c) % (2 * math.pi)) * n / (2 * math.pi)


def death_class(d, suicided):
    if d is None:
        return None
    t = d['team']
    if (d['round'], d['id']) in suicided:
        return 'suicide'
    c = d['cause']
    if c == 'h2h':
        return 'h2h_enemy' if d.get('killer_team') == other(t) else 'h2h_ally' if d.get('killer_team') == t else 'h2h_unknown'
    if c == 'body':
        if d.get('killer') == d['id']:
            return 'self'
        return 'enemy_body' if d.get('killer_team') == other(t) else 'ally_body' if d.get('killer_team') == t else 'body_unknown'
    return c


def at(series, r, R):
    """value at round r; terminal state carried forward after the game ended"""
    return series[min(r, R)]


def window(series, lo, hi, R):
    hi = min(hi, R)
    return sum(series[lo:hi]) if hi > lo else float('nan')


def side_features(g, t, S, E, samples, deaths, dragons, base, R, capacity):
    o = other(t)
    s, e, so, eo = S[t], E[t], S[o], E[o]
    f = dict(base, side=t, bot=_bot(g['bot' + t]), opponent=_bot(g['bot' + o]), won=1 if g['winner'] == t else 0 if g['winner'] == o else 0.5,
             result='win' if g['winner'] == t else 'loss' if g['winner'] == o else 'draw')
    cum = lambda k, E_=e: _cum(E_[k]) if k in E_ else [0.0] * (R + 1)
    # material curve at checkpoints
    for c in CHECKPOINTS:
        for k in ('units', 'total', 'longest'):
            f[f'{k}@{c}'] = at(s[k], c, R)
            a, b = at(s[k], c, R), at(so[k], c, R)
            f[f'{k}_share@{c}'] = a / (a + b) if a + b else 0.5
        f[f'top1_share@{c}'] = at(s['top1_share'], c, R)
        f[f'len_gini@{c}'] = at(s['len_gini'], c, R)
        f[f'seen_share@{c}'] = at(s['seen_share'], c, R)
        f[f'visited_share@{c}'] = at(s['visited_share'], c, R)
        f[f'pearls@{c}'] = at(cum('eats'), c, R)
        f[f'bed_pearls@{c}'] = at(cum('eats_bed'), c, R)
        f[f'births@{c}'] = at(cum('splits'), c, R)
        f[f'deaths@{c}'] = at(cum('deaths'), c, R)
        f[f'kills@{c}'] = at(cum('kills'), c, R)
    for c in (100, 250):
        f[f'small_share@{c}'] = at(s['small_share'], c, R)
        f[f'big_share@{c}'] = at(s['big_share'], c, R)
    # thresholds and firsts
    f['first_lead_total'] = next((r for r in range(R + 1) if s['total'][r] > so['total'][r]), None)
    f['lead_changes_total'] = sum(1 for r in range(1, R + 1) if (s['total'][r] - so['total'][r]) * (s['total'][r - 1] - so['total'][r - 1]) < 0)
    f['lead_changes_longest'] = sum(1 for r in range(1, R + 1) if (s['longest'][r] - so['longest'][r]) * (s['longest'][r - 1] - so['longest'][r - 1]) < 0)
    for th in (10, 20, 30):
        f[f'first_len{th}'] = next((r for r in range(R + 1) if s['longest'][r] >= th), None)
    f['first_split'] = next((r for r in range(R + 1) if e['splits'][r]), None)
    f['last_split'] = next((r for r in range(R, -1, -1) if e['splits'][r]), None)
    f['first_pearl'] = next((r for r in range(R + 1) if e['eats'][r]), None)
    f['first_contact'] = next((r for r in range(R + 1) if s['contact_share'][r] > 0), None)
    f['first_death'] = next((r for r in range(R + 1) if e['deaths'][r]), None)
    f['seen50'] = next((r for r in range(R + 1) if s['seen_share'][r] >= 0.5), None)
    f['seen90'] = next((r for r in range(R + 1) if s['seen_share'][r] >= 0.9), None)
    f['peak_units'] = max(s['units'])
    f['peak_units_round'] = s['units'].index(f['peak_units'])
    f['leader_changes'] = sum(s['leader_change'])
    # production
    for lo, hi in ((0, 50), (50, 100), (100, 250), (250, 500)):
        f[f'splits_{lo}_{hi}'] = window(e['splits'], lo, hi, R)
    kids = [x for x in dragons if x['side'] == t and not x['initial']]
    f['births'] = len(kids)
    f['newborn_deaths10_per100'] = 100 * sum(1 for d in deaths if d['side'] == t and d['newborn']) / len(kids) if kids else float('nan')
    ch = [sp['child_len'] for sp in g['events']['splits'] if sp['team'] == t]
    f['child_len_median'] = sorted(ch)[len(ch) // 2] if ch else float('nan')
    f['child_len_le3_share'] = sum(1 for x in ch if x <= 3) / len(ch) if ch else float('nan')
    # economy
    dt = sum(e['dragon_turns'])
    f['dragon_turns'] = dt
    for lo, hi in ((0, 100), (100, 250), (250, 500)):
        w = window(e['dragon_turns'], lo, hi, R)
        f[f'pearls_per100dt_{lo}_{hi}'] = 100 * window(e['eats'], lo, hi, R) / w if w and w == w else float('nan')
    tot_eats = sum(e['eats'])
    f['pearls'] = tot_eats
    for k in ('bed', 'ally_corpse', 'enemy_corpse'):
        f[f'pearls_{k}_share'] = sum(e.get('eats_' + k, [0])) / tot_eats if tot_eats else float('nan')
    spawns = sum(e.get('bed_spawns', [0]))
    f['bed_capture_share'] = sum(e.get('eats_bed', [0])) / spawns if spawns else float('nan')
    f['bed_capacity_yield'] = sum(e.get('eats_bed', [0])) / (capacity * max(R, 1)) if capacity else float('nan')
    ours_dropped = sum(math.ceil(d['length'] / 2) for d in deaths if d['side'] == t)
    rec = [x for x in g['events']['eats'] if x['origin'] in ('ally_corpse', 'enemy_corpse')]
    mine_back = sum(1 for x in rec if x['team'] == t and x['origin'] == 'ally_corpse')
    theirs_took = sum(1 for x in rec if x['team'] == o and x['origin'] == 'enemy_corpse')
    f['corpse_recovered_share'] = mine_back / ours_dropped if ours_dropped else float('nan')
    f['corpse_lost_share'] = theirs_took / ours_dropped if ours_dropped else float('nan')
    f['sprint_cost_per_pearl'] = sum(e.get('sprint_cost', [0])) / tot_eats if tot_eats else float('nan')
    f['density_ratio_mean'] = _nanmean(s['density_ratio'][:R])
    for c in (25, 100, 250):
        f[f'density_ratio@{c}'] = at(s['density_ratio'], c, R)
    # EPG from samples: access integral (tau 2), realised bed pearls, conversion
    sm = [x[t] for x in samples]
    for tau in TAUS:
        f[f'epg_tau{tau}'] = sum(x[f'access_tau{tau}'] for x in sm) * 5
    f['epg_conversion'] = sum(e.get('eats_bed', [0])) / f['epg_tau2'] if f['epg_tau2'] else float('nan')
    for c in (50, 100, 250):
        x = _sample_at(samples, c, t)
        if x:
            f[f'territory@{c}'] = x['territory']
            f[f'bed_territory@{c}'] = x['bed_territory']
            f[f'bed_expected_share@{c}'] = x['bed_expected_share']
            f[f'enclosed_share@{c}'] = x['enclosed_share']
            f[f'reach_mean@{c}'] = x['reach_mean']
    f['territory_mean'] = _nanmean([x['territory'] for x in sm])
    f['bed_expected_share_mean'] = _nanmean([x['bed_expected_share'] for x in sm])
    f['enclosed_share_mean'] = _nanmean([x['enclosed_share'] for x in sm])
    # survival
    mine = [d for d in deaths if d['side'] == t]
    k = 1000 / dt if dt else float('nan')
    f['deaths_per1k'] = len(mine) * k
    for cls in ('wall', 'self', 'ally_body', 'enemy_body', 'h2h_enemy', 'h2h_ally', 'suicide', 'invalid'):
        f[f'death_{cls}_per1k'] = sum(1 for d in mine if d['cls'] == cls) * k
    f['kills_per1k'] = sum(e.get('kills', [0])) * k
    f['kill_length'] = sum(e.get('kill_length', [0]))
    f['length_lost'] = sum(e.get('length_lost', [0]))
    f['kill_length_ratio'] = f['kill_length'] / (f['kill_length'] + f['length_lost']) if f['kill_length'] + f['length_lost'] else float('nan')
    enc_dt = f['enclosed_share_mean'] if f['enclosed_share_mean'] == f['enclosed_share_mean'] else None
    ne = sum(1 for d in mine if d['enclosed'] and d['cls'] != 'suicide')
    no = sum(1 for d in mine if not d['enclosed'] and d['cls'] != 'suicide')
    f['enclosed_death_share'] = ne / (ne + no) if ne + no else float('nan')
    if enc_dt is not None and dt:
        f['death_rate_enclosed_per1k'] = 1000 * ne / (dt * enc_dt) if enc_dt > 0 else float('nan')
        f['death_rate_open_per1k'] = 1000 * no / (dt * (1 - enc_dt)) if enc_dt < 1 else float('nan')
    f['portal_death_share'] = sum(1 for d in mine if d['near_portal']) / len(mine) if mine else float('nan')
    f['alive_end'] = s['units'][R]
    lives = [x['lifetime'] for x in dragons if x['side'] == t]
    f['lifetime_median'] = sorted(lives)[len(lives) // 2] if lives else float('nan')
    # movement
    moves = sum(e.get('moves', [0]))
    f['sprint_share'] = sum(e.get('sprints', [0])) / moves if moves else float('nan')
    f['contact_share_mean'] = _nanmean(s['contact_share'][:R])
    # sonar
    rays = sum(e.get('rays', [0]))
    f['rays_per_dt'] = rays / dt if dt else float('nan')
    for lo, hi in ((0, 100), (100, 250), (250, 500)):
        w = window(e['dragon_turns'], lo, hi, R)
        f[f'rays_per_dt_{lo}_{hi}'] = window(e['rays'], lo, hi, R) / w if 'rays' in e and w and w == w else 0.0
    for k in ('toward_com', 'away_com', 'side_com', 'toward_enemy', 'away_enemy'):
        f[f'rays_{k}_share'] = sum(e.get('rays_' + k, [0])) / rays if rays else float('nan')
    for k in ('kelp', 'ally', 'ally_head', 'enemy', 'enemy_head', 'empty'):
        f[f'ray_hit_{k}_share'] = sum(e.get('ray_' + k, [0])) / rays if rays else float('nan')
    f['ray_leak_share'] = (f['ray_hit_enemy_share'] + f['ray_hit_enemy_head_share']) if rays else float('nan')
    f['ray_refracted_share'] = sum(e.get('rays_refracted', [0])) / rays if rays else float('nan')
    direct = rays - sum(e.get('rays_refracted', [0]))
    for d in 'NESW':
        f[f'rays_{d}_share'] = sum(e.get('rays_' + d, [0])) / direct if direct else float('nan')
    # endgame
    f['crown20'] = f['first_len20']
    f['longest_margin_end'] = s['longest'][R] - so['longest'][R]
    f['total_margin_end'] = s['total'][R] - so['total'][R]
    f['close_end'] = 1 if (g['reason'] != 'elimination' and abs(f['longest_margin_end']) <= 3) else 0
    f['max_drawdown_total'] = _drawdown(s['total'])
    f['tle'] = sum(e.get('tle', [0]))
    return f


def _cum(xs):
    out, acc = [], 0.0
    for x in xs:
        acc += x
        out.append(acc)
    return out


def _nanmean(xs):
    xs = [x for x in xs if x == x]
    return sum(xs) / len(xs) if xs else float('nan')


def _sample_at(samples, r, t):
    best = None
    for x in samples:
        if x['round'] <= r:
            best = x
    return best[t] if best else None


def _drawdown(xs):
    peak, dd = 0, 0
    for x in xs:
        peak = max(peak, x)
        dd = max(dd, peak - x)
    return dd


def _bot(name):
    return name.rstrip('/').split('/')[-1]
