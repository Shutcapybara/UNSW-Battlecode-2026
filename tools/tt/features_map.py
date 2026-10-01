"""TT: per-dragon internal map features (v6 "map memory"), from the exact protocol blocks each dragon received.

    python3 tools/tt/features_map.py OUTDIR SIDES_JSON replay... [--jobs N]     (SIDES_JSON: {game_id: 'A'|'B'})

Each dragon keeps what it has seen: edge kinds (open / kelp / portal) per cell side, when each cell was last seen,
remembered pearls (with the round seen), beds (with their predicted next spawn). A child starts with an empty map
(fresh process, as on the judge). Per candidate move F / R / L, a bounded BFS (radius RAD) over the remembered map
from the candidate cell - through known open edges into known cells, stopping at unseen cells, kelp, portals and
currently visible bodies - gives:
  mm_reach      known cells reachable within RAD (dead ends beyond the 7x7 view)
  mm_frontier   BFS distance to the nearest never-seen cell (exploration), RAD+1 if none
  mm_pearl      BFS distance to the nearest remembered pearl seen in the last 30 rounds, RAD+1 if none
  mm_bed        BFS distance d to the nearest bed whose next spawn is <= round + d + 1, RAD+1 if none
  mm_stale      mean rounds since last seen over reached cells within distance 6
plus per turn: mm_known (cells ever seen), mm_seen_frac (of the map), mm_pearls_known, mm_beds_known.
Blocked or portal candidates get -1. Writes one parquet per game keyed (game, dragon, round).
"""
import json, sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'team_recon_claude'))
import recon, roundblock, features_view as FV

RAD = 12
DIRS = ('N', 'E', 'S', 'W')
OPP = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}


class MapMem:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.edge = {}          # (x, y, dir) -> '.', 'w', or portal id
        self.seen = {}          # (x, y) -> last round seen
        self.pearl = {}         # (x, y) -> round a pearl was last seen there
        self.bed = {}           # (x, y) -> predicted next spawn round

    def step(self, x, y, d):
        dx, dy = FV.DXY[d]
        return (x + dx) % self.W, (y + dy) % self.H

    def update(self, blk, R):
        tiles = blk['tiles']
        for k, (x, y, p, cd) in enumerate(tiles):
            self.seen[(x, y)] = R
            if p:
                self.pearl[(x, y)] = R
            else:
                self.pearl.pop((x, y), None)
            if cd >= 0:
                self.bed[(x, y)] = R + cd
        Hm, Vm = blk['H'], blk['V']
        for r in range(7):
            for c in range(7):
                x, y = tiles[r * 7 + c][:2]
                for d, e in (('N', Hm[r][c]), ('S', Hm[r + 1][c]), ('W', Vm[r][c]), ('E', Vm[r][c + 1])):
                    self.edge[(x, y, d)] = e
                    nx, ny = self.step(x, y, d)
                    self.edge[(nx, ny, OPP[d])] = e

    def bfs(self, start, R, blocked):
        dist = {start: 0}
        q = deque([start])
        frontier = RAD + 1
        reach, pearl, bed, stale, stale_n = 0, RAD + 1, RAD + 1, 0, 0
        while q:
            a = q.popleft()
            da = dist[a]
            if a not in self.seen:
                frontier = min(frontier, da)
                continue
            reach += 1
            if a in self.pearl and R - self.pearl[a] <= 30:
                pearl = min(pearl, da)
            if a in self.bed and self.bed[a] <= R + da + 1:
                bed = min(bed, da)
            if da <= 6:
                stale += R - self.seen[a]
                stale_n += 1
            if da >= RAD:
                continue
            for d in DIRS:
                e = self.edge.get((a[0], a[1], d))
                if e is not None and e != '.':
                    continue                      # kelp or portal
                b = self.step(a[0], a[1], d)
                if b in dist or b in blocked:
                    continue
                dist[b] = da + 1
                q.append(b)
        return dict(mm_reach=reach, mm_frontier=frontier, mm_pearl=pearl, mm_bed=bed,
                    mm_stale=stale / stale_n if stale_n else -1)

    def features(self, blk, R, facing):
        tiles = blk['tiles']
        head = tiles[24][:2]
        blocked = {(x, y) for _t, _i, x, y, _f, _h in blk['bodies']}
        row = dict(mm_known=len(self.seen), mm_seen_frac=len(self.seen) / (self.W * self.H),
                   mm_pearls_known=sum(1 for v in self.pearl.values() if R - v <= 30),
                   mm_beds_known=len(self.bed))
        for rel in ('F', 'R', 'L'):
            ad = FV.rel_to_abs(facing, rel)
            e = self.edge.get((head[0], head[1], ad), '.')
            cell = self.step(head[0], head[1], ad)
            if e != '.' or cell in blocked:
                f = dict(mm_reach=-1, mm_frontier=-1, mm_pearl=-1, mm_bed=-1, mm_stale=-1)
            else:
                f = self.bfs(cell, R, blocked)
            for k, v in f.items():
                row[f'c{rel}_{k}'] = v
        return row


def extract(path, side, gid):
    g = recon.Game(path)
    mems, seen_turns, rows = {}, {}, []

    def cb(kind, **k):
        if kind != 'turn':
            return
        d = k['dragon']
        if d.team != side:
            return
        n = seen_turns.get(d.id, 0)
        seen_turns[d.id] = n + 1
        blk, _ = FV.parse_block(roundblock.build_block(g, d, proto3=(n > 0 or d.parent is not None)))
        mm = mems.get(d.id)
        if mm is None:
            mm = mems[d.id] = MapMem(g.board.W, g.board.H)
        mm.update(blk, blk['round'])
        row = mm.features(blk, blk['round'], blk['dir'])
        row.update(game=gid, dragon=d.id, round=blk['round'])
        rows.append(row)
    g.run(cb)
    return rows


def _one(args):
    p, side, gid, out = args
    o = out / f'{gid}.parquet'
    if o.exists():
        return gid, -1
    import pandas as pd
    try:
        rows = extract(p, side, gid)
        pd.DataFrame(rows).to_parquet(out / f'{gid}.part')
        (out / f'{gid}.part').replace(o)
        return gid, len(rows)
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
