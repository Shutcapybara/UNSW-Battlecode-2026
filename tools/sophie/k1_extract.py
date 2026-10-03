"""K-1 per-game extractor: deaths with position and context, head-cell exposure, and the
'general trouble' counters, for one replay -> one small gzipped JSON (resumable, memory-light).

Built on the F1 decoder (tools/analysis/features/frame.py) so causes and credit are the F1 ones.

    python -m tools.sophie.k1_extract --set us|field|local --out build/sophie/x/<set> [--budget 170] [--jobs 3]

Contexts on each death (overlap allowed, as in the C1-C ledger):
  newborn   child dying within 10 rounds of birth
  trapped   <=15 cells reachable in 5 steps with bodies blocking (F1 'enclosed'), suicide excluded
  portal    head within 2 steps of a portal cell (F1 near_portal)
  transit   the dragon took a portal step in this round or the previous two (own step)
  crowd23   length <=3 dying into own-side bodies (self / ally_body / h2h_ally)
  fight     C2-0-style window at the death round: an enemy head within 4 of the dying head, and >=3 heads
            of one side and >=1 of the other within 6 (wrap Manhattan, portals not followed)
"""
import argparse, collections, gzip, json, os, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPO = Path(os.environ.get('K1_REPO', ROOT))
sys.path.insert(0, str(REPO))
from tools.analysis.features.frame import decode  # noqa: E402
from tools.analysis.features.extract import death_class, bfs  # noqa: E402

REACH_STEPS, ENCLOSED = 5, 15
RB = ((0, 50), (50, 100), (100, 250), (250, 10 ** 6))
LB = ((1, 3), (4, 7), (8, 15), (16, 10 ** 6))


def band(v, bands):
    for i, (lo, hi) in enumerate(bands):
        if lo <= v < hi or (bands is LB and lo <= v <= hi):
            return i
    return len(bands) - 1


def wd(a, b, W, H):
    dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
    return min(dx, W - dx) + min(dy, H - dy)


def geo(c, d, W, H):
    x, y = c
    return ((x + (0, 1, 0, -1)[d]) % W, (y + (-1, 0, 1, 0)[d]) % H)


def process(path, meta):
    g = decode(path)
    W, H, nbr = g['W'], g['H'], g['nbr']
    rounds = g['rounds']
    R = len(rounds) - 1
    ev = g['events']
    sides = 'AB'
    # ---------- exposure: head cells, dragon-turns by round band x length band ----------
    head_cells = {t: collections.Counter() for t in sides}
    dt_rb_lb = {t: [[0] * 4 for _ in range(4)] for t in sides}
    dt100 = {t: 0 for t in sides}
    total_series = {t: [] for t in sides}
    units_series = {t: [] for t in sides}
    stationary = {t: 0 for t in sides}
    oscill = {t: 0 for t in sides}
    hist = {}
    for r in range(R):
        snap = rounds[r]
        tot = {t: 0 for t in sides}
        un = {t: 0 for t in sides}
        rb = band(r, RB)
        for i, (t, b) in snap.items():
            h = b[0]
            head_cells[t][h] += 1
            L = len(b)
            dt_rb_lb[t][rb][band(L, LB)] += 1
            if r < 100:
                dt100[t] += 1
            tot[t] += L
            un[t] += 1
            p = hist.get(i)
            if p is not None:
                if p[-1] == h:
                    stationary[t] += 1
                elif h in p[:-1]:
                    oscill[t] += 1          # head back on a cell it held 2-4 rounds ago (a small loop)
                p.append(h)
                if len(p) > 4:
                    p.pop(0)
            else:
                hist[i] = [h]
        if r % 5 == 0:
            for t in sides:
                total_series[t].append(tot[t])
                units_series[t].append(un[t])
    # ---------- portal steps by own dragons ----------
    transit_rounds = collections.defaultdict(set)   # id -> rounds with a portal step
    transits = {t: 0 for t in sides}
    steps_total = {t: 0 for t in sides}
    moves = {t: 0 for t in sides}
    no_action = {t: 0 for t in sides}
    tle = {t: 0 for t in sides}
    split_rounds = {t: [] for t in sides}
    for a in ev['actions']:
        t = a['team']
        if a['tle']:
            tle[t] += 1
        if a['kind'] is None:
            no_action[t] += 1
        if a['kind'] != 'move':
            continue
        moves[t] += 1
        steps_total[t] += a['steps']
        snap = rounds[a['round']] if a['round'] <= R else {}
        if a['id'] not in snap:
            continue
        c = snap[a['id']][1][0]
        for d in a.get('dirs', ()):
            if d > 3:
                break
            n = nbr[c][d]
            if n is None:
                break
            if n != geo(c, d, W, H):
                transits[t] += 1
                transit_rounds[a['id']].add(a['round'])
            c = n
    for s in ev['splits']:
        split_rounds[s['team']].append(s['round'])
    # ---------- pearls ----------
    eats = {t: collections.Counter() for t in sides}
    eat_origin = {t: collections.Counter() for t in sides}
    for e in ev['eats']:
        eats[e['team']][e['round']] += 1
        eat_origin[e['team']][e['origin']] += 1
    pearls_at = {t: {} for t in sides}
    for t in sides:
        cum, rr = 0, sorted(eats[t])
        for c in (25, 50, 100, 150, 250, 500):
            pearls_at[t][c] = sum(v for r, v in eats[t].items() if r <= c)
    births_at = {t: {c: sum(1 for r in split_rounds[t] if r <= c) for c in (50, 100, 250, 500)} for t in sides}
    # ---------- deaths ----------
    suicided = {(a['round'], a['id']) for a in ev['actions'] if a['kind'] == 'suicide'}
    deaths = []
    transit_death = {t: 0 for t in sides}
    act_at = {(a['round'], a['id']): a for a in ev['actions']}
    for d in ev['deaths']:
        t = d['team']
        cls = death_class(d, suicided)
        snap = rounds[d['round']] if d['round'] <= R else {}
        occ = {c for i, (tt, b) in snap.items() for c in b}
        body = snap.get(d['id'], (t, (d['head'],)))[1]
        head = body[0]
        rch = len(bfs(nbr, [head], REACH_STEPS, occ - {head}))
        near_portal = any(c in g['portal_cells'] for c in bfs(nbr, [d['head']], 2))
        tr = bool(transit_rounds.get(d['id'], set()) & {d['round'], d['round'] - 1, d['round'] - 2})
        if tr:
            transit_death[t] += 1
        heads = [(tt, b[0]) for i, (tt, b) in snap.items() if i != d['id']]
        enemy4 = any(tt != t and wd(h, head, W, H) <= 4 for tt, h in heads)
        fight = False
        if enemy4:
            near6 = collections.Counter(tt for tt, h in heads if wd(h, head, W, H) <= 6)
            near6[t] += 1
            fight = (near6[t] >= 3 and near6['B' if t == 'A' else 'A'] >= 1) or (near6['B' if t == 'A' else 'A'] >= 3 and near6[t] >= 1)
        newborn = (not d['initial']) and d['age'] <= 10
        deaths.append(dict(r=d['round'], id=d['id'], s=t, cls=cls, L=d['length'], age=d['age'], x=head[0], y=head[1],
                           reach=rch, nb=newborn, tr=(rch <= ENCLOSED and cls != 'suicide'), po=near_portal, tx=tr,
                           cr=(d['length'] <= 3 and cls in ('self', 'ally_body', 'h2h_ally')), fi=fight,
                           kt=d.get('killer_team'),
                           to=bool(act_at.get((d['round'], d['id']), {}).get('tle')),
                           na=(d['round'], d['id']) in act_at and act_at[(d['round'], d['id'])]['kind'] is None,
                           ns=(act_at.get((d['round'], d['id'])) or {}).get('steps', 0)))
    sonar = {t: 0 for t in sides}
    for s in ev['sonar']:
        if s['team'] in sonar:
            sonar[s['team']] += 1
    out = dict(meta=dict(meta, map=g['map'], map_hash=g['map_hash'], W=W, H=H, winner=g['winner'], reason=g['reason'],
                         last_round=g['last_round'], final=g['final'], n_initial=g['n_initial']),
               deaths=deaths,
               side={t: dict(head_cells=[[c[0], c[1], n] for c, n in head_cells[t].items()], dt_rb_lb=dt_rb_lb[t],
                             dt100=dt100[t], total5=total_series[t], units5=units_series[t], stationary=stationary[t],
                             oscillation=oscill[t], transits=transits[t], transit_deaths=transit_death[t],
                             steps=steps_total[t], moves=moves[t], no_action=no_action[t], tle=tle[t],
                             splits=split_rounds[t], pearls_at=pearls_at[t], births_at=births_at[t],
                             eat_origin=dict(eat_origin[t]), sonar=sonar[t]) for t in sides})
    return out


def tasks(which):
    corpus = REPO / 'public_replays/corpus'
    if which in ('us', 'field'):
        want = None
        if which == 'field':
            import pandas as pd
            want = set(pd.read_parquet(REPO / 'build/a2-field/features.parquet', columns=['game'])['game'].astype(int))
        for l in open(corpus / 'index.jsonl'):
            r = json.loads(l)
            us = 7 in (r['team_a'], r['team_b'])
            if (which == 'us' and not us) or (which == 'field' and (us or r['game_id'] not in want)):
                continue
            p = corpus / 'replays' / f"{r['game_id']}.replay"
            if p.exists():
                yield str(r['game_id']), str(p), dict(game=r['game_id'], team_A=r['team_a'], team_B=r['team_b'],
                                                      ranked=r['ranked'], sub_A=r.get('bot_a'), sub_B=r.get('bot_b'),
                                                      started=r['started_at'], map_name=r['map_name'])
    elif which.startswith('local:'):
        d = REPO / which[6:]
        for p in sorted(d.rglob('*.replay')):
            parts = p.stem.split('__')
            yield p.stem, str(p), dict(game=p.stem, botA=parts[2] if len(parts) > 3 else None,
                                        botB=parts[3] if len(parts) > 3 else None, seed=parts[0], panel=p.parent.parent.name)


def _one(job):
    key, path, meta, out = job
    try:
        res = process(path, meta)
        tmp = out + '.tmp'
        with gzip.open(tmp, 'wt') as f:
            json.dump(res, f, separators=(',', ':'))
        os.replace(tmp, out)
        return key, None
    except Exception as e:  # recorded, not fatal
        return key, f'{type(e).__name__}: {e}'


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--set', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--budget', type=float, default=165)
    ap.add_argument('--jobs', type=int, default=3)
    a = ap.parse_args(argv)
    t0 = time.time()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    todo = [(k, p, m, str(out / f'{k}.json.gz')) for k, p, m in tasks(a.set) if not (out / f'{k}.json.gz').exists()]
    errs = out / 'errors.txt'
    done = 0
    import multiprocessing as mp
    with mp.get_context('fork').Pool(a.jobs, maxtasksperchild=50) as pool:
        it = pool.imap_unordered(_one, todo)
        for key, err in it:
            done += 1
            if err:
                with open(errs, 'a') as f:
                    f.write(f'{key}\t{err}\n')
            if time.time() - t0 > a.budget:
                pool.terminate()
                break
    print(f'done {done} of {len(todo)} remaining; {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
