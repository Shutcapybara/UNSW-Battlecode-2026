"""Verso tier 3: relabel logged decisions with what a better operator would have chosen.

    .venv/bin/python tools/verso/relabel.py hindsight ARM [--panel train] [--horizon 20] [--jobs 8]
    .venv/bin/python tools/verso/relabel.py audit     ARM [--panel train]

hindsight (operator B): for every logged one-step move of our dragons, tools/verso/cpp/hindsight.cpp searches the
*recorded* next rounds of that game — true terrain, every other dragon moving as it did, pearls appearing as
they did — and returns, for each first step F/R/L, the best value reachable (discounted pearls minus the loss of
the dragon if every continuation dies) and whether any continuation survives the horizon. Reactive deaths are
not pinned on a cell: a recorded ram on this dragon kills it wherever it stands within the attacker's reach at
that moment, and an enemy head that entered a cell we would occupy is a head-to-head only with probability
--p-adj (an ally is assumed to see us and yield). Written next to the
game's arrays as <game>.hind-h<H>.npy: float32 [n, 9] in the row order of H (NaN rows where there was no move).
The label is clairvoyant about the future and assumes the others do not react; the head trained on it sees only
the live features, so it learns the expectation of the hindsight value given what the dragon could observe.

audit: consistency of the hindsight model with the record (a recorded move that survived must not be called
dead), and what share of our deaths had a surviving alternative k rounds earlier.

The Monte-Carlo operator (A) needs no relabelling step: tools/verso/dataset.py stores the realised returns.
"""
from __future__ import annotations

import argparse, glob, os, subprocess, sys, tempfile
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'team_recon_claude'))
import common as C

SRC = Path(__file__).resolve().parent / 'cpp' / 'hindsight.cpp'
EXE = C.B / 'bin' / 'hindsight'
DIRS = ['north', 'east', 'south', 'west']


def build_exe():
    if not EXE.exists() or EXE.stat().st_mtime < SRC.stat().st_mtime:
        EXE.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(['g++', '-O2', '-std=c++20', str(SRC), '-o', str(EXE)], check=True)


def tape(replay, path):
    """Write the hindsight tape of one game. S_r = state at the first turn of round r; the last snapshot is the
    final state."""
    import recon
    g = recon.Game(replay)
    b = g.board
    W, H = b.W, b.H
    NC = W * H
    cell = lambda t: t[1] * W + t[0]
    dest = np.full((NC, 4), -1, np.int32)
    for (x, y), row in b.nbr.items():
        for k, (t, via, has_edge) in enumerate(row):
            if t is not None:
                dest[y * W + x, k] = cell(t)
    occ, pearl, eater, heads, bodies = [], [], [], [], []
    eats, born, parent, atk = [], {}, {}, []
    cur = {'round': -1, 'snapped': -1, 'eater': None}

    def snap():
        o = np.zeros(NC, np.uint16); p = np.zeros(NC, np.uint8)
        hd, bd = {}, {}
        for d in g.dragons.values():
            if not d.alive:
                continue
            cs = [cell(t) for t in d.body]
            for c in cs:
                o[c] = d.id + 1
            hd[d.id] = cs[0]; bd[d.id] = cs
        for t in g.pearls:
            p[cell(t)] = 1
        occ.append(o); pearl.append(p); heads.append(hd); bodies.append(bd)
        eater.append(np.zeros(NC, np.uint16))

    def cb(kind, **k):
        if kind == 'turn' and cur['snapped'] < g.round:
            for r in range(cur['snapped'] + 1, g.round + 1):   # a round with no turn repeats the state
                snap()
            cur['snapped'] = g.round
        elif kind == 'split':
            born[k['child'].id] = g.round; parent[k['child'].id] = k['parent'].id
        elif kind == 'action':
            cur['steps'] = len(k['action'][1]) if k['action'][0] == 'move' else 0
        elif kind == 'death' and k['reason'] == 'hitHeadToHead' and k['actor'] is not None and k['actor'] != k['dragon'].id:
            # the victim's head cell, and how many steps the attacker's move had
            atk.append((g.round, cell(k['dragon'].body[0]), k['actor'], k['dragon'].id, max(1, cur.get('steps', 1))))
        elif kind == 'pearl_eat' and k['dragon'] is not None and eater:
            c = cell(k['tile'])
            eater[-1][c] = k['dragon'].id + 1
            eats.append((g.round, c, k['dragon'].id))
    g.run(cb)
    snap()
    NR, NID = len(occ), max(g.dragons) + 1
    head = np.full((NR, NID), -1, np.int32)
    off = np.zeros(NR * NID + 1, np.int32)
    cells = []
    for r in range(NR):
        for i in range(NID):
            bd = bodies[r].get(i)
            if bd:
                head[r, i] = bd[0]; cells += bd
            off[r * NID + i + 1] = len(cells)
    par = np.array([parent.get(i, -1) for i in range(NID)], np.int32)
    brn = np.array([born.get(i, -1) for i in range(NID)], np.int32)
    team = np.array([1 if (i in g.dragons and g.dragons[i].team == 'B') else 0 for i in range(NID)], np.int32)
    ea = np.array(sorted(eats, key=lambda e: (e[2], e[0])), np.int32).reshape(-1, 3)
    at = np.array(atk, np.int32).reshape(-1, 5)
    with open(path, 'wb') as f:
        f.write(np.array([0x34544856, W, H, NC, NR, NID, len(cells), len(ea), len(at)], np.int32).tobytes())
        for a in (dest, np.stack(occ), np.stack(pearl), np.stack(eater), head, par, brn, team, off,
                  np.array(cells, np.int32), ea, at):
            f.write(np.ascontiguousarray(a).tobytes())
    return NR


def _one(args):
    npz, replay, out, horizon, gamma, unit, gd, padj, esc, rho, kappa = args
    try:
        H = np.load(npz)['H']
        q = (H[:, 11] == 0) & (H[:, 12] >= 0)
        Q = H[q][:, [2, 3, 5, 8, 7]].astype(np.int32)     # round, id, length, head cell, facing
        with tempfile.TemporaryDirectory(dir='/dev/shm') as td:
            tp, qp, op = Path(td) / 't.bin', Path(td) / 'q.bin', Path(td) / 'o.bin'
            tape(replay, tp)
            Q.tofile(qp)
            subprocess.run([str(EXE), str(tp), str(qp), str(len(Q)), str(op), str(horizon), str(gamma), str(unit),
                            str(gd), str(padj), str(esc), str(rho), str(kappa)], check=True)
            R = np.fromfile(op, np.float32).reshape(len(Q), 9)
        full = np.full((len(H), 9), np.nan, np.float32)
        full[q] = R
        np.save(out, full)
        return Path(npz).stem, int(q.sum())
    except Exception as e:
        return Path(npz).stem, f'ERR {type(e).__name__}: {e}'


def hind_path(npz, tag):
    """tag: the horizon (default label set, gamma 0.97) or the name of a variant (--tag)"""
    return Path(str(npz)[:-4] + f'.hind-h{tag}.npy')


def cmd_hindsight(a):
    build_exe()
    data = C.B / 'data' / a.arm / a.panel
    reps = C.B / 'runs' / a.arm / a.panel / 'replays'
    work = []
    for f in sorted(glob.glob(str(data / '*.npz'))):
        if f.endswith(('.tmp.npz', '.view.npz')):
            continue
        out = hind_path(f, a.tag or a.horizon)
        rep = reps / (Path(f).stem + '.replay')
        if rep.exists() and not out.exists():
            work.append((f, str(rep), out, a.horizon, a.gamma, a.unit_value,
                         a.gamma if a.gamma_death is None else a.gamma_death, a.p_adj, a.esc, a.rho, a.kappa))
    print(f'{len(work)} games to relabel', flush=True)
    n = 0
    with Pool(a.jobs) as pool:
        for name, rows in pool.imap_unordered(_one, work):
            if isinstance(rows, str):
                print(name, rows, flush=True)
            else:
                n += rows
    print(f'relabelled {n} move rows')


def cmd_audit(a):
    import dataset as D
    data = C.B / 'data' / a.arm / a.panel
    tot = dict(rows=0, rec_alive=0, rec_alive_called_dead=0, rec_dead=0, rec_dead_called_alive=0,
               rec_dead_alt_alive=0, agree=0, comparable=0, all_dead=0)
    by_ttd = {}
    hcol = D.YCOLS.index(f'died_{a.horizon}')
    for f in sorted(glob.glob(str(data / '*.npz'))):
        if f.endswith(('.tmp.npz', '.view.npz')) or not hind_path(f, a.tag or a.horizon).exists():
            continue
        z = np.load(f)
        H, Y = z['H'], z['Y']
        R = np.load(hind_path(f, a.tag or a.horizon))
        ok = ~np.isnan(R[:, 0]) & (H[:, 13] == 1)
        rel = (H[:, 12] - H[:, 7]) % 4
        k = np.where(rel == 0, 0, np.where(rel == 1, 1, np.where(rel == 3, 2, -1)))
        ok &= k >= 0
        H, Y, R, k = H[ok], Y[ok], R[ok], k[ok]
        val, alive = R[:, 0::3], R[:, 1::3]
        i = np.arange(len(k))
        died = Y[:, hcol] > 0
        tot['rows'] += len(k)
        tot['rec_alive'] += int((~died).sum()); tot['rec_alive_called_dead'] += int((~died & (alive[i, k] == 0)).sum())
        tot['rec_dead'] += int(died.sum()); tot['rec_dead_called_alive'] += int((died & (alive[i, k] == 1)).sum())
        alt = alive.copy(); alt[i, k] = 0
        tot['rec_dead_alt_alive'] += int((died & (alive[i, k] == 0) & (alt.max(1) == 1)).sum())
        tot['all_dead'] += int((alive.max(1) == 0).sum())
        best = val.argmax(1)
        uniq = (val == val.max(1, keepdims=True)).sum(1) == 1
        tot['comparable'] += int(uniq.sum()); tot['agree'] += int((uniq & (best == k)).sum())
        ttd = Y[:, D.YCOLS.index('ttd')]
        rs = Y[:, D.YCOLS.index('reason')]
        for t in range(0, 9):   # turns before the dragon's own death: is there a surviving first step?
            for rn, rc in (('all', 0), ('wall', 1), ('self', 2), ('body', 3), ('h2h', 4)):
                m = (ttd == t) & ((rs == rc) if rc else True)
                s = by_ttd.setdefault((t, rn), [0, 0, 0])
                s[0] += int(m.sum()); s[1] += int((m & (alive.max(1) == 1)).sum()); s[2] += int((m & (alive[i, k] == 1)).sum())
    import json
    print(json.dumps(tot, indent=1))
    print('rounds before own death | reason | n | some first step survives | the taken step survives')
    for (t, rn), v in sorted(by_ttd.items()):
        print(f'  {t:2d} {rn:5s} {v[0]:7d} {v[1] / max(1, v[0]):.3f} {v[2] / max(1, v[0]):.3f}')


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    for c in ('hindsight', 'audit'):
        p = sub.add_parser(c); p.add_argument('arm'); p.add_argument('--panel', default='train')
        p.add_argument('--horizon', type=int, default=20); p.add_argument('--jobs', type=int, default=8)
        p.add_argument('--gamma', type=float, default=0.97); p.add_argument('--unit-value', type=float, default=3.0)
        p.add_argument('--gamma-death', type=float, default=None, help='discount of the death term (default: gamma)')
        p.add_argument('--tag', default='', help='name of the label set (default: the horizon)')
        p.add_argument('--p-adj', type=float, default=0.5,
                       help='probability that an enemy head entering our cell is a head-to-head')
        p.add_argument('--esc', type=float, default=2.0,
                       help='loss when a dragon of length >= 4 runs out of moves (escape split); < 0: a full loss')
        p.add_argument('--rho', type=float, default=1.0,
                       help='share of a dead dragon the side does not eat back (tempo credit: ~0.55 measured)')
        p.add_argument('--kappa', type=float, default=1.0, help='share of a killed enemy the side eats')
    a = ap.parse_args()
    {'hindsight': cmd_hindsight, 'audit': cmd_audit}[a.cmd](a)


if __name__ == '__main__':
    main()
