"""Offline v5 rows (HB-1): v4 actor-local rows + decision labels for all five decisions.

v5 = v4 (features_view.Proc on rebuilt round blocks, unchanged) plus, per turn:
  legality   split_elig (length>=4 and units<limit), n_exit_ord (free ordinary F/R/L), n_exit_portal,
             n_exit_any; per candidate the v4 cX_block code already encodes free/kelp/portal/body.
  labels     y_family / y_first / y_split (as v4), y_child = split size, y_parent = length - split size,
             y_sonar_n (rays cast this turn), y_sonar_mask (bit per relative direction F=1,R=2,B=4,L=8,
             relative to the facing the dragon had when it received its block), y_sonar_v (first payload),
             y_sonar_vset (sorted distinct payloads, '|'-joined), post_died / post_reason (the actor died
             during its own action).
and per game a trajectory file (units / longest / total per team every 10 rounds + final) for Q1(e).

    python3 features_v5.py OUTDIR SIDES_JSON replay...        (SIDES_JSON: {game_id: 'A'|'B'})
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import recon, roundblock, features_view as FV

REL_BIT = {'F': 1, 'R': 2, 'B': 4, 'L': 8}


def extract(path, side, gid):
    g = recon.Game(path)
    procs, rows = {}, []
    pend = {}
    cur = {}                  # the row of the dragon currently acting (sonar / death attach here)
    turns_seen = {}
    traj = []

    def teamstat(t):
        al = [d for d in g.dragons.values() if d.alive and d.team == t]
        return dict(units=len(al), longest=max([len(d.body) for d in al] or [0]), total=sum(len(d.body) for d in al))

    def cb(kind, **k):
        if kind == 'round':
            cur.clear()
            if k['round'] % 10 == 0:
                traj.append(dict(round=k['round'], A=teamstat('A'), B=teamstat('B')))
        elif kind == 'turn':
            cur.clear()
            d = k['dragon']
            if d.team != side:
                return
            n = turns_seen.get(d.id, 0)
            turns_seen[d.id] = n + 1
            lines = roundblock.build_block(g, d, proto3=(n > 0 or d.parent is not None))
            blk, _ = FV.parse_block(lines)
            pr = procs.get(d.id)
            if pr is None:
                pr = procs[d.id] = FV.Proc(d.id, side, g.board.W, g.board.H, g.board.unit_limit)
            row = pr.features(blk)
            row.update(game=gid, dragon=d.id, mem_initial=int(d.parent is None))
            row['split_elig'] = int(row['length'] >= 4 and row['units'] < row['unit_limit'])
            row['n_exit_ord'] = sum(int(row[f'c{r}_block'] == 0) for r in 'FRL')
            row['n_exit_portal'] = sum(int(row[f'c{r}_portal'] == 1) for r in 'FRL')
            row['n_exit_any'] = row['n_exit_ord'] + row['n_exit_portal']
            row.update(y_sonar_n=0, y_sonar_mask=0, y_sonar_v=-1, y_sonar_vset='', post_died=0, post_reason='')
            pend['row'], pend['proc'], pend['facing'] = row, pr, d.facing
        elif kind == 'action' and 'row' in pend and k['dragon'].team == side:
            row, pr = pend.pop('row'), pend.pop('proc')
            a = k['action']
            row['y_family'] = a[0]
            if a[0] == 'move':
                rels, c = [], pend['facing']
                for s in a[1]:
                    rels.append(FV.abs_to_rel(FV.DIRS[recon.DIRS.index(c)], FV.DIRS[recon.DIRS.index(s)]))
                    c = s
                row.update(y_first=rels[0], y_nsteps=len(rels), y_seq=''.join(rels), y_split=0, y_child=0, y_parent=0)
                pr.record_action('move', rels=rels)
            elif a[0] == 'split':
                row.update(y_first='split', y_nsteps=0, y_seq='S%d' % a[1], y_split=a[1], y_child=a[1],
                           y_parent=row['length'] - a[1])
                pr.record_action('split', split=a[1])
            else:
                row.update(y_first=a[0], y_nsteps=0, y_seq=a[0], y_split=0, y_child=0, y_parent=0)
            row['_facing'] = pend['facing']
            row['_vals'] = []
            rows.append(row)
            cur['row'], cur['id'] = row, k['dragon'].id
        elif kind == 'sonar' and cur.get('id') == k['sender']:
            row = cur['row']
            row['y_sonar_n'] += 1
            rel = FV.abs_to_rel(FV.DIRS[recon.DIRS.index(row['_facing'])], FV.DIRS[recon.DIRS.index(k['direction'])])
            row['y_sonar_mask'] |= REL_BIT[rel]
            row['_vals'].append(k['value64'])
        elif kind == 'death' and cur.get('id') == k['dragon'].id:
            cur['row']['post_died'] = 1
            cur['row']['post_reason'] = k['reason']
    res = g.run(cb)
    for r in rows:
        v = r.pop('_vals')
        r.pop('_facing')
        if v:
            r['y_sonar_v'] = int(v[0]) if v[0] < 2 ** 62 else -2
            r['y_sonar_vset'] = '|'.join(str(x) for x in sorted(set(v)))
    traj.append(dict(round='end', A=teamstat('A'), B=teamstat('B')))
    return rows, g, dict(game=gid, side=side, map=g.board.name, result=res, traj=traj, checks=dict(g.checks))


def _one(args):
    p, side, gid, out = args
    o = out / f'{gid}.parquet'
    if o.exists():
        return gid, -1
    import pandas as pd
    try:
        rows, g, desc = extract(p, side, gid)
        df = pd.DataFrame(rows)
        df['map'] = g.board.name
        df.to_parquet(out / f'{gid}.part')
        (out / f'{gid}.part').replace(o)
        (out / f'{gid}.traj.json').write_text(json.dumps(desc))
        return gid, len(df)
    except Exception as e:
        (out / f'{gid}.error').write_text(repr(e))
        return gid, -2


if __name__ == '__main__':
    import argparse
    from multiprocessing import Pool
    ap = argparse.ArgumentParser()
    ap.add_argument('outdir')
    ap.add_argument('sides')
    ap.add_argument('replays', nargs='+')
    ap.add_argument('--jobs', type=int, default=1)
    a = ap.parse_args()
    out = Path(a.outdir); out.mkdir(parents=True, exist_ok=True)
    sides = json.loads(Path(a.sides).read_text())
    work = [(p, sides[Path(p).stem], int(Path(p).stem), out) for p in a.replays if Path(p).stem in sides]
    with Pool(a.jobs) as pool:
        for gid, n in pool.imap_unordered(_one, work):
            print(gid, n, flush=True)
