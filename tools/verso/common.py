"""Verso shared helpers: the bot's feature schema, dump reader, mirror map, game split."""
from __future__ import annotations

import os, re, subprocess, sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
B = ROOT / 'build' / 'verso'
MODELS = B / 'models'
RELS = ['F', 'R', 'L']
SEED = 62
DUMP_MAGIC = 0x31445256
HDR = ['magic', 'nf', 'rnd', 'me', 'team', 'len', 'units', 'face', 'head', 'W', 'H', 'act', 'first', 'steps',
       'flags', 'greedy']


def bot_binary(bot='verso-00-base'):
    """Native build of a bot directory (unswbc's own build, so it is the binary the games run)."""
    from unswbc.project import Project
    from unswbc.run import _inspect
    built = Project.from_dir(str(ROOT / 'bots' / bot)).compile()
    return _inspect(built)[0][0]


def schema(bot='verso-00-base'):
    """-> (hash, names) as the bot itself reports them (single source of truth for every trainer/exporter)."""
    out = subprocess.run([bot_binary(bot)], env=dict(os.environ, VERSO_SCHEMA='1'), capture_output=True, text=True,
                         check=True).stdout.split('\n')
    return int(out[0]), [n for n in out[1:] if n]


def block(names):
    """feature family of each schema column: v5 (HB-1 actor-local row), ares (search outputs), t4 (map-memory
    route features and state scalars), h (outputs of earlier heads)."""
    out = []
    for n in names:
        if re.match(r'a[FRL]_', n) or n.startswith('a_'):
            out.append('ares')
        elif re.match(r't[FRL]_', n) or n.startswith('s_'):
            out.append('t4')
        elif n.startswith('h_'):
            out.append('h')
        else:
            out.append('v5')
    return np.array(out)


def mirror_perm(names):
    """Left-right mirror of the egocentric frame as a column permutation: X[:, perm] is the mirrored state.
    Value-level swaps (mem_last_rel codes R=2/L=3) are applied by mirror()."""
    idx = {n: i for i, n in enumerate(names)}
    perm = np.arange(len(names))
    for i, n in enumerate(names):
        m = re.match(r'g_(-?\d)_(-?\d)_(\w+)$', n)
        if m:
            perm[i] = idx[f'g_{m.group(1)}_{-int(m.group(2))}_{m.group(3)}']
            continue
        m = re.match(r'([cat])([RL])_(\w+)$', n)
        if m:
            perm[i] = idx[f"{m.group(1)}{'L' if m.group(2) == 'R' else 'R'}_{m.group(3)}"]
            continue
        m = re.match(r'(h_\w+)_([RL])$', n)
        if m:
            perm[i] = idx[f"{m.group(1)}_{'L' if m.group(2) == 'R' else 'R'}"]
            continue
        if n in ('pearl_left', 'pearl_right'):
            perm[i] = idx['pearl_right' if n == 'pearl_left' else 'pearl_left']
    return perm


def mirror(X, y, names):
    """-> mirrored copy of (X, y): classes F/R/L = 0/1/2, R and L swap."""
    Xm = X[:, mirror_perm(names)].copy()
    if 'mem_last_rel' in names:
        j = names.index('mem_last_rel')
        c = Xm[:, j].copy()
        Xm[c == 2, j] = 3
        Xm[c == 3, j] = 2
    ym = y.copy()
    ym[y == 1] = 2
    ym[y == 2] = 1
    return Xm, ym


def read_dump(path, nf=None):
    """-> (header int32 [n, 16], X float32 [n, nf]) of a VERSO_DUMP file."""
    raw = np.fromfile(path, dtype=np.uint8)
    if len(raw) < 64:
        return np.zeros((0, 16), np.int32), np.zeros((0, nf or 0), np.float32)
    if nf is None:
        nf = int(raw[:64].view('<i4')[1])
    rec = 64 + 4 * nf
    n = len(raw) // rec  # a killed process can leave a partial last record
    raw = raw[:n * rec].reshape(n, rec)
    H = raw[:, :64].copy().view('<i4')
    assert (H[:, 0] == DUMP_MAGIC).all() and (H[:, 1] == nf).all(), path
    return H, raw[:, 64:].copy().view('<f4')


def holdout(games, frac=5, seed=SEED):
    """HB-1's by-game split: every `frac`-th share of the sorted game ids, fixed seed."""
    games = sorted(games)
    return set(np.random.default_rng(seed).choice(games, len(games) // frac, replace=False).tolist())


if __name__ == '__main__':
    h, n = schema(sys.argv[1] if len(sys.argv) > 1 else 'verso-00-base')
    b = block(n)
    print(h, len(n), {k: int((b == k).sum()) for k in ('v5', 'ares', 't4', 'h')})
