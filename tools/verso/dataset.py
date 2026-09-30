"""Verso data: join a game's feature dump (VERSO_DUMP, written by the bot) with outcomes read from its replay.

    .venv/bin/python tools/verso/dataset.py build ARM [--panel train] [--jobs 8] [--keep-raw]
    .venv/bin/python tools/verso/dataset.py info  ARM [--panel train]

Per game -> build/verso/data/<ARM>/<panel>/<game>.npz with
  H   int32 [n, 16]   the dump header (common.HDR): rnd, me, team, len, units, face, head, W, H, act, first, ...
  X   float32 [n, F]  the bot's own feature vector (schema order; never recomputed in Python)
  Y   float32 [n, len(YCOLS)]  outcomes of that dragon-turn, from the replay:
      for each horizon h in HORIZONS (rounds): dlen_h, dunits_h (material of the dragon's lineage at the start of
      round t+h minus the dragon at t: the dragon itself plus every descendant born from round t on), died_h (the
      dragon itself is dead by then), bed_h / corpse_h (pearls the dragon itself ate in the window, by provenance),
      heff_h (rounds actually observed; shorter at the end of the game)
      plus ttd (rounds until the dragon's own death, 999 if it survives), reason (death reason code), won (its team
      won the game: 1 / 0.5 / 0), final_margin (team total length share at the end)
The raw dump is deleted after a successful conversion unless --keep-raw.
"""
from __future__ import annotations

import argparse, glob, json, os, sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'team_recon_claude'))
import common as C

HORIZONS = (5, 10, 20, 40)
YCOLS = [f'{k}_{h}' for h in HORIZONS for k in ('dlen', 'dunits', 'died', 'bed', 'corpse', 'heff')] + \
        ['ttd', 'reason', 'won', 'final_margin']
VIEW_R, VIEW_C = 5, 18
VIEW_N = 2 * VIEW_R + 1
REASON = {'hitWall': 1, 'hitSelf': 2, 'hitOtherBody': 3, 'hitHeadToHead': 4, 'noValidAction': 5}


def outcomes(replay):
    """-> dict with per-round length snapshots, lineage, deaths and eats of every dragon in the game."""
    import recon
    g = recon.Game(replay)
    snap = []            # per round: {id: length} at the start of the round (alive dragons)
    born, parent, death = {}, {}, {}
    eats = {}            # id -> list of (round, is_corpse)
    team = {}

    def cb(kind, **k):
        if kind == 'round':
            snap.append({d.id: len(d.body) for d in g.dragons.values() if d.alive})
            for d in g.dragons.values():
                team.setdefault(d.id, d.team)
        elif kind == 'split':
            ch = k['child']
            born[ch.id] = g.round; parent[ch.id] = k['parent'].id; team[ch.id] = ch.team
        elif kind == 'death':
            d = k['dragon']
            death[d.id] = (g.round, k['reason'])
        elif kind == 'pearl_eat' and k['dragon'] is not None:
            eats.setdefault(k['dragon'].id, []).append((g.round, k['prov'] == 'corpse'))
    res = g.run(cb)
    snap.append({d.id: len(d.body) for d in g.dragons.values() if d.alive})  # final state
    kids = {}
    for c, p in parent.items():
        kids.setdefault(p, []).append(c)
    return dict(snap=snap, born=born, kids=kids, death=death, eats=eats, team=team, result=res)


def lineage(o, d, t):
    """the dragon plus every descendant born from round t on"""
    out, stack = [d], [c for c in o['kids'].get(d, []) if o['born'][c] >= t]
    while stack:
        c = stack.pop()
        out.append(c)
        stack += o['kids'].get(c, [])
    return out


def y_rows(o, H):
    snap, n_r = o['snap'], len(o['snap']) - 1   # snap[n_r] is the final state
    Y = np.zeros((len(H), len(YCOLS)), np.float32)
    res = o['result']
    tot = {t: res[t]['total'] for t in 'AB'}
    cache = {}
    for i in range(len(H)):
        t, d, tm = int(H[i, 2]), int(H[i, 3]), chr(int(H[i, 4]))
        l0 = snap[t].get(d, int(H[i, 5])) if t < len(snap) else int(H[i, 5])
        lin = None
        col = 0
        ev = o['eats'].get(d, ())
        for h in HORIZONS:
            te = min(t + h, n_r)
            if lin is None:
                key = (d, t)
                lin = cache.get(key)
                if lin is None:
                    lin = cache[key] = lineage(o, d, t)
            s = snap[te]
            alive = [x for x in lin if x in s]
            Y[i, col] = sum(s[x] for x in alive) - l0
            Y[i, col + 1] = len(alive) - 1
            Y[i, col + 2] = 0.0 if d in s else 1.0
            Y[i, col + 3] = sum(1 for (r, c) in ev if t <= r < te and not c)
            Y[i, col + 4] = sum(1 for (r, c) in ev if t <= r < te and c)
            Y[i, col + 5] = te - t
            col += 6
        dr = o['death'].get(d)
        Y[i, col] = dr[0] - t if dr else 999
        Y[i, col + 1] = REASON.get(dr[1], 9) if dr else 0
        Y[i, col + 2] = 0.5 if res['winner'] is None else float(res['winner'] == tm)
        Y[i, col + 3] = tot[tm] / max(1, tot['A'] + tot['B'])
    return Y


def _one(args):
    dump, replay, out, keep = args
    try:
        H, X = C.read_dump(dump)
        if not len(H):
            return out.name, 0
        o = outcomes(replay)
        Y = y_rows(o, H)
        tmp = out.with_suffix('.tmp.npz')
        np.savez_compressed(tmp, H=H, X=X, Y=Y)
        os.replace(tmp, out)
        vp = Path(str(dump) + '.view')
        if vp.exists():  # tier-1 tensors, re-ordered to the rows of H by (round, dragon, team)
            rec = 16 + VIEW_C * VIEW_N * VIEW_N
            raw = np.fromfile(vp, np.uint8)
            raw = raw[: len(raw) // rec * rec].reshape(-1, rec)
            vh = raw[:, :16].copy().view('<i4')
            key = {(int(r), int(m), int(t)): i for i, (_, r, m, t) in enumerate(vh)}
            order = np.array([key.get((int(h[2]), int(h[3]), int(h[4])), -1) for h in H])
            V = raw[:, 16:].reshape(-1, VIEW_C, VIEW_N, VIEW_N)[np.maximum(order, 0)]
            V[order < 0] = 0
            tmp = out.with_suffix('.view.tmp.npz')
            np.savez_compressed(tmp, V=V, ok=order >= 0)
            os.replace(tmp, out.with_suffix('.view.npz'))
            if not keep:
                os.unlink(vp)
        if not keep:
            os.unlink(dump)
        return out.name, len(H)
    except Exception as e:  # reported, not fatal: one bad game does not stop a cycle
        return out.name, f'ERR {type(e).__name__}: {e}'


def cmd_build(a):
    runs = C.B / 'runs' / a.arm / a.panel / 'replays'
    dumps = C.B / 'dumps' / a.arm / a.panel
    out = C.B / 'data' / a.arm / a.panel
    out.mkdir(parents=True, exist_ok=True)
    work = []
    for d in sorted(glob.glob(str(dumps / '*.bin'))):
        g = Path(d).stem
        rep = runs / (g + '.replay')
        o = out / (g + '.npz')
        if d.endswith('.view.bin'):
            continue
        if rep.exists() and not o.exists():
            work.append((d, str(rep), o, a.keep_raw))
    print(f'{len(work)} games to convert', flush=True)
    n = 0
    with Pool(a.jobs) as pool:
        for name, rows in pool.imap_unordered(_one, work):
            if isinstance(rows, str):
                print(name, rows, flush=True)
            else:
                n += rows
    print(f'done: {n} rows; {len([f for f in glob.glob(str(out / "*.npz")) if not f.endswith(".view.npz")])} games in {out}')


def load(arm, panel='train', games=None, cols=None, limit=None):
    """-> (H, X, Y, game index per row, game names). cols: schema column indices to keep (None = all)."""
    fs = sorted(glob.glob(str(C.B / 'data' / arm / panel / '*.npz')))
    fs = [f for f in fs if not f.endswith(('.tmp.npz', '.view.npz'))]
    if games is not None:
        fs = [f for f in fs if Path(f).stem in games]
    if limit:
        fs = fs[:limit]
    Hs, Xs, Ys, Gs = [], [], [], []
    for i, f in enumerate(fs):
        z = np.load(f)
        Hs.append(z['H']); Ys.append(z['Y'])
        Xs.append(z['X'] if cols is None else z['X'][:, cols])
        Gs.append(np.full(len(Hs[-1]), i, np.int32))
    return (np.concatenate(Hs), np.concatenate(Xs), np.concatenate(Ys), np.concatenate(Gs),
            [Path(f).stem for f in fs])


def _rey(args):
    npz, replay = args
    z = np.load(npz)
    Y = y_rows(outcomes(replay), z['H'])
    tmp = Path(str(npz)[:-4] + '.tmp.npz')
    np.savez_compressed(tmp, H=z['H'], X=z['X'], Y=Y)
    os.replace(tmp, npz)
    return 1


def cmd_reyield(a):
    """recompute the outcome table of existing arrays from their replays (after a change to y_rows)"""
    out = C.B / 'data' / a.arm / a.panel
    runs = C.B / 'runs' / a.arm / a.panel / 'replays'
    work = [(f, str(runs / (Path(f).stem + '.replay'))) for f in sorted(glob.glob(str(out / '*.npz')))
            if not f.endswith(('.tmp.npz', '.view.npz'))]
    with Pool(a.jobs) as pool:
        n = sum(pool.imap_unordered(_rey, work))
    print(f'recomputed outcomes of {n} games')


def cmd_info(a):
    H, X, Y, G, names = load(a.arm, a.panel)
    y = {c: Y[:, i] for i, c in enumerate(YCOLS)}
    mv = H[:, 11] == 0
    print(json.dumps(dict(games=len(names), rows=int(len(H)), moves=int(mv.sum()), splits=int((~mv).sum()),
                          explored=int((H[:, 14] & 1).sum()), learned_changed=int(((H[:, 14] & 2) > 0).sum()),
                          dlen_20=float(y['dlen_20'].mean()), died_20=float(y['died_20'].mean()),
                          bed_20=float(y['bed_20'].mean()), corpse_20=float(y['corpse_20'].mean())), indent=1))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    b = sub.add_parser('build'); b.add_argument('arm'); b.add_argument('--panel', default='train')
    b.add_argument('--jobs', type=int, default=8); b.add_argument('--keep-raw', action='store_true')
    i = sub.add_parser('info'); i.add_argument('arm'); i.add_argument('--panel', default='train')
    r = sub.add_parser('reyield'); r.add_argument('arm'); r.add_argument('--panel', default='train')
    r.add_argument('--jobs', type=int, default=8)
    a = ap.parse_args()
    {'build': cmd_build, 'info': cmd_info, 'reyield': cmd_reyield}[a.cmd](a)


if __name__ == '__main__':
    main()
