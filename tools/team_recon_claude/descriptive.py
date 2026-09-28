"""Full-state descriptive view (analyst namespace — NOT for policy inputs).

    python3 descriptive.py OUTDIR replay [replay ...]

One JSON per replay: trajectories (every 10 rounds), stage deltas, and
event tables (splits, deaths, eats, sonar summary), plus reconstruction checks.
"""
import collections
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import recon  # noqa: E402

WINDOWS = ((0, 50), (50, 100), (100, 250), (250, 400), (400, 500))
SAMPLE = 10


def window_of(r):
    for lo, hi in WINDOWS:
        if lo <= r < hi:
            return f'{lo}-{hi}'
    return '400-500'


def analyse(path):
    g = recon.Game(path)
    b = g.board
    T = lambda: {k: collections.Counter() for k in ('eat', 'split', 'death', 'deathlen', 'turns', 'sprint', 'extra_steps',
                                                    'portal', 'sonar', 'sonar_hit', 'msgs_in', 'tle', 'split_child_len')}
    per = {t: T() for t in 'AB'}
    traj = []
    splits, deaths, crown = [], [], []
    sonar_vals = {t: collections.Counter() for t in 'AB'}
    sonar_dirrel = {t: collections.Counter() for t in 'AB'}
    act_hist = {t: collections.Counter() for t in 'AB'}
    first = {'A': {}, 'B': {}}
    state = {'round': -1}
    maxpts = {'A': 0, 'B': 0}
    last_crown = {'A': None, 'B': None}

    def snapshot(r):
        row = {'round': r}
        for t in 'AB':
            alive = [d for d in g.dragons.values() if d.alive and d.team == t]
            lens = sorted((len(d.body) for d in alive), reverse=True)
            row[t] = dict(units=len(alive), total=sum(lens), longest=lens[0] if lens else 0,
                          top3=sum(lens[:3]), share_longest=(lens[0] / sum(lens)) if lens else 0,
                          small=sum(1 for x in lens if x <= 3))
        row['pearls_on_board'] = len(g.pearls)
        traj.append(row)

    def cb(kind, **k):
        if kind == 'round':
            r = k['round']
            state['round'] = r
            if r % SAMPLE == 0:
                snapshot(r)
            for t in 'AB':
                alive = [d for d in g.dragons.values() if d.alive and d.team == t]
                if alive:
                    top = max(alive, key=lambda d: (len(d.body), -d.id))
                    if last_crown[t] is not None and top.id != last_crown[t]:
                        crown.append(dict(round=r, team=t, old=last_crown[t], new=top.id, new_len=len(top.body)))
                    last_crown[t] = top.id
        elif kind == 'action':
            d, a = k['dragon'], k['action']
            t = d.team
            w = window_of(state['round'])
            per[t]['turns'][w] += 1
            if a[0] == 'move':
                n = len(a[1])
                act_hist[t][f'move{min(n, 5)}'] += 1
                if n > 1:
                    per[t]['sprint'][w] += 1
                    per[t]['extra_steps'][w] += n - 1
            else:
                act_hist[t][a[0]] += 1
            if a[0] == 'tle':
                per[t]['tle'][w] += 1
            if k['points']:
                maxpts[t] = max(maxpts[t], k['points'])
            if a[0] == 'split':
                first[t].setdefault('split', state['round'])
        elif kind == 'step':
            if k['via_portal']:
                per[k['dragon'].team]['portal'][window_of(state['round'])] += 1
        elif kind == 'pearl_eat':
            d = k['dragon']
            if d is not None:
                per[d.team]['eat'][(window_of(state['round']), k['prov'] or 'unknown')] += 1
        elif kind == 'split':
            p, c = k['parent'], k['child']
            w = window_of(state['round'])
            per[p.team]['split'][w] += 1
            per[p.team]['split_child_len'][len(c.body)] += 1
            splits.append(dict(round=state['round'], team=p.team, parent=p.id, child=c.id, parent_len_after=len(p.body),
                               child_len=len(c.body), units_after=g.unit_count(p.team)))
        elif kind == 'death':
            d = k['dragon']
            w = window_of(state['round'])
            per[d.team]['death'][(w, k['reason'])] += 1
            per[d.team]['deathlen'][w] += k['length']
            actor = g.dragons.get(k['actor'])
            deaths.append(dict(round=state['round'], team=d.team, id=d.id, reason=k['reason'], length=k['length'],
                               age=state['round'] - d.born, self_turn=(k['actor'] == d.id),
                               actor_team=actor.team if actor else None))
        elif kind == 'sonar':
            s = g.dragons.get(k['sender'])
            if s is None:
                return
            t = s.team
            per[t]['sonar'][window_of(state['round'])] += 1
            per[t]['sonar_hit'][k['hitkind']] += 1
            sonar_vals[t][k['value64']] += 1
            rel = ('F' if k['direction'] == s.facing else 'B' if k['direction'] == recon.OPP[s.facing] else 'S')
            sonar_dirrel[t][rel] += 1
            if k['hit'] is not None and k['hit'] in g.dragons:
                per[g.dragons[k['hit']].team]['msgs_in'][window_of(state['round'])] += 1

    res = g.run(cb)
    snapshot(res['rounds'])

    def ser(c):
        return {('|'.join(map(str, k)) if isinstance(k, tuple) else str(k)): v for k, v in c.items()}

    out = dict(path=str(path), map=b.name, W=b.W, H=b.H, unit_limit=b.unit_limit, beds=len(b.gaps),
               portal_edges=b.portal_edges, version=g.version, result=res, checks=dict(g.checks),
               teams={t: {k: ser(v) for k, v in per[t].items()} for t in 'AB'},
               actions={t: dict(act_hist[t]) for t in 'AB'}, max_points=maxpts, first=first,
               sonar_distinct={t: len(sonar_vals[t]) for t in 'AB'},
               sonar_top={t: [[str(v), n] for v, n in sonar_vals[t].most_common(8)] for t in 'AB'},
               sonar_dirrel={t: dict(sonar_dirrel[t]) for t in 'AB'},
               traj=traj, splits=splits, deaths=deaths, crown=crown)
    return out


if __name__ == '__main__':
    outdir = Path(sys.argv[1])
    outdir.mkdir(parents=True, exist_ok=True)
    for p in sys.argv[2:]:
        o = outdir / (Path(p).stem + '.json')
        if o.exists():
            continue
        try:
            res = analyse(p)
        except Exception as e:  # keep going; ledger the failure
            res = dict(path=p, error=f'{type(e).__name__}: {e}')
        tmp = o.with_suffix('.part')
        tmp.write_text(json.dumps(res))
        tmp.replace(o)
        print(o.name, res.get('checks', res.get('error')), flush=True)
