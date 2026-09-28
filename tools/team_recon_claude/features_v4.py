"""Offline v4 rows: rebuild each target round block, run features_view.Proc on it.

    python3 features_v4.py OUTDIR SIDES_JSON replay...
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import recon, roundblock, features_view as FV


def extract(path, side, gid):
    g = recon.Game(path)
    procs, rows = {}, []
    pend = {}
    turns_seen = {}

    def cb(kind, **k):
        if kind == 'turn':
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
            pend['row'], pend['proc'], pend['facing'] = row, pr, d.facing
        elif kind == 'action' and 'row' in pend and k['dragon'].team == side:
            row, pr = pend.pop('row'), pend.pop('proc')
            a = k['action']
            row['y_family'] = a[0]
            if a[0] == 'move':
                rels, cur = [], pend['facing']
                for s in a[1]:
                    rels.append(FV.abs_to_rel(FV.DIRS[recon.DIRS.index(cur)], FV.DIRS[recon.DIRS.index(s)]))
                    cur = s
                row.update(y_first=rels[0], y_nsteps=len(rels), y_seq=''.join(rels), y_split=0)
                pr.record_action('move', rels=rels)
            elif a[0] == 'split':
                row.update(y_first='split', y_nsteps=0, y_seq='S%d' % a[1], y_split=a[1])
                pr.record_action('split', split=a[1])
            else:
                row.update(y_first=a[0], y_nsteps=0, y_seq=a[0], y_split=0)
            rows.append(row)
    g.run(cb)
    return rows, g


if __name__ == '__main__':
    import pandas as pd
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    sides = json.loads(Path(sys.argv[2]).read_text())
    for p in sys.argv[3:]:
        gid = Path(p).stem
        o = out / f'{gid}.parquet'
        if gid not in sides or o.exists():
            continue
        try:
            rows, g = extract(p, sides[gid], int(gid) if gid.isdigit() else gid)
            df = pd.DataFrame(rows)
            df['map'] = g.board.name
            df.to_parquet(out / f'{gid}.part'); (out / f'{gid}.part').replace(o)
            print(gid, len(df), flush=True)
        except Exception as e:
            import traceback; traceback.print_exc()
            (out / f'{gid}.error').write_text(repr(e))
