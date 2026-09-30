"""Verso tier-2 export: XGBoost boosters -> one head blob (VERSO_POLICY) or a compiled header.

    .venv/bin/python tools/verso/export.py blob   OUT.bin  dir=build/verso/models/c0-hb/dir.ubj [q=...] [--bot B]
    .venv/bin/python tools/verso/export.py header OUT.hpp  dir=... [--bot B]
    .venv/bin/python tools/verso/export.py parity OUT.bin  dir=... --x rows.npy      # C++ margins vs XGBoost

Head kinds by name: dir -> 0 (softmax over F/R/L), q -> 1 (three regressors), anything else binary (kind 2).
A booster is a model file written by train_heads.py next to `<file>.features.json` (its column names). Feature
indices are re-keyed to the bot's schema (`VERSO_SCHEMA=1 <bot binary>`), whose hash is stored in the blob; the
bot refuses a blob exported for another schema. Node encoding: hb1-04's 8-byte preorder word (verso.hpp).
The `q` head is written as one booster per first step (q_F, q_R, q_L files), interleaved tree by tree.
"""
from __future__ import annotations

import argparse, json, struct, subprocess, sys, tempfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C

KIND = {'dir': 0, 'q': 1}


def load_booster(path):
    import xgboost as xgb
    b = xgb.Booster()
    b.load_model(str(path))
    feats = json.loads(Path(str(path) + '.features.json').read_text())
    return b, feats


def trees_of(booster):
    """-> list of (left, right, feat, cond, default_left) arrays per tree, and the per-tree output index."""
    with tempfile.NamedTemporaryFile(suffix='.json') as f:
        booster.save_model(f.name)
        m = json.loads(Path(f.name).read_text())
    gb = m['learner']['gradient_booster']['model']
    out = []
    for t in gb['trees']:
        out.append((np.array(t['left_children']), np.array(t['right_children']), np.array(t['split_indices']),
                    np.array(t['split_conditions'], dtype=np.float32), np.array(t['default_left'])))
    return out, list(gb['tree_info'])


def encode_tree(tree, fmap):
    left, right, feat, cond, dleft = tree
    out = []

    def f32(x):
        return struct.unpack('<I', struct.pack('<f', float(x)))[0]

    def emit(i):
        pos = len(out)
        out.append(0)
        if left[i] < 0:
            out[pos] = (0x7FFF << 32) | f32(cond[i])
            return
        emit(int(left[i]))
        off = len(out) - pos
        assert off < 65536
        emit(int(right[i]))
        f = fmap[int(feat[i])]
        assert 0 <= f < 0x7FFF
        out[pos] = (off << 48) | (int(bool(dleft[i])) << 47) | (f << 32) | f32(cond[i])
    import sys as _s
    _s.setrecursionlimit(100000)
    emit(0)
    return out


def tree_sum(tree, x):
    left, right, feat, cond, dleft = tree
    i = 0
    while left[i] >= 0:
        v = x[feat[i]]
        i = (left[i] if dleft[i] else right[i]) if np.isnan(v) else (left[i] if np.float32(v) < cond[i] else right[i])
    return float(cond[i])


def head_words(name, paths, names):
    """-> (kind, K, base[K], tree_start, words) for one head. `paths`: one booster, or three for kind 1."""
    import xgboost as xgb
    idx = {n: i for i, n in enumerate(names)}
    kind = KIND.get(name, 2)
    per_out = []  # per output: list of encoded trees; base
    bases = []
    if kind == 1:
        assert len(paths) == 3, 'q needs q_F, q_R, q_L'
    for p in paths:
        b, feats = load_booster(p)
        fmap = [idx[f] for f in feats]
        trees, info = trees_of(b)
        K = max(info) + 1
        # base margin per output, measured on a probe row (robust to xgboost's base_score conventions)
        probe = np.zeros((1, len(feats)), np.float32)
        marg = np.atleast_1d(b.predict(xgb.DMatrix(probe, feature_names=feats), output_margin=True)[0])
        sums = np.zeros(K)
        for t, k in zip(trees, info):
            sums[k] += tree_sum(t, probe[0])
        base = marg - sums
        enc = [[] for _ in range(K)]
        for t, k in zip(trees, info):
            enc[k].append(encode_tree(t, fmap))
        per_out += enc
        bases += list(base)
    K = len(per_out)
    n = max(len(e) for e in per_out)
    leaf0 = [(0x7FFF << 32)]  # a zero leaf pads outputs with fewer trees
    words, start = [], []
    for t in range(n):
        for k in range(K):
            start.append(len(words))
            words += per_out[k][t] if t < len(per_out[k]) else leaf0
    return kind, K, np.array(bases, np.float32), np.array(start, np.uint32), np.array(words, np.uint64)


def build_blob(heads, bot):
    h, names = C.schema(bot)
    out = bytearray(b'VRSM' + struct.pack('<3I', 1, len(heads), h))
    info = {}
    for name, paths in heads.items():
        kind, K, base, start, words = head_words(name, paths, names)
        out += name.encode()[:15].ljust(16, b'\0')
        out += struct.pack('<4I', kind, K, len(start), len(words))
        out += base.tobytes(); out += b'\0' * (-len(out) % 8)
        out += start.tobytes(); out += b'\0' * (-len(out) % 8)
        out += words.tobytes()
        info[name] = dict(kind=kind, K=K, trees=int(len(start)), nodes=int(len(words)))
    return bytes(out), info


def parse_heads(specs):
    heads = {}
    for s in specs:
        name, p = s.split('=', 1)
        heads[name] = p.split(',')
    return heads


def margins_cpp(blob_path, head, X, bot):
    """Margins of `head` from the C++ evaluator (tools/verso/cpp/head_parity.cpp built against the bot's verso.hpp)."""
    exe = C.B / 'bin' / f'head_parity-{bot}'
    src = Path(__file__).resolve().parent / 'cpp' / 'head_parity.cpp'
    hdr = C.ROOT / 'bots' / bot / 'verso.hpp'
    if not exe.exists() or exe.stat().st_mtime < max(src.stat().st_mtime, hdr.stat().st_mtime):
        exe.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(['g++', '-O2', '-std=c++20', f'-I{C.ROOT / "bots" / bot}', '-DVERSO_NO_EMBED', str(src),
                        '-o', str(exe)], check=True)
    with tempfile.TemporaryDirectory() as td:
        xp, op = Path(td) / 'x.f32', Path(td) / 'out.f64'
        np.ascontiguousarray(X, np.float32).tofile(xp)
        subprocess.run([str(exe), str(blob_path), head, str(xp), str(X.shape[0]), str(op)], check=True)
        return np.fromfile(op, np.float64).reshape(X.shape[0], -1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['blob', 'header', 'parity'])
    ap.add_argument('out')
    ap.add_argument('heads', nargs='+')
    ap.add_argument('--bot', default='verso-00-base')
    ap.add_argument('--x', help='parity: .npy of schema-ordered rows')
    a = ap.parse_args()
    heads = parse_heads(a.heads)
    if a.cmd in ('blob', 'header'):
        blob, info = build_blob(heads, a.bot)
        out = Path(a.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        if a.cmd == 'blob':
            out.write_bytes(blob)
        else:
            w = np.frombuffer(blob + b'\0' * (-len(blob) % 8), '<u8')
            L = ['// generated by tools/verso/export.py - do not edit. Heads: ' + json.dumps(info), '#pragma once',
                 'inline constexpr unsigned long long verso_blob[] = {']
            for i in range(0, len(w), 8):
                L.append(','.join(f'0x{int(x):x}ull' for x in w[i:i + 8]) + ',')
            L += ['};', '']
            out.write_text('\n'.join(L))
        print(json.dumps(dict(out=str(out), bytes=len(blob), heads=info)))
        return
    # parity: every head's C++ margins against XGBoost on the given rows
    import xgboost as xgb
    _, names = C.schema(a.bot)
    idx = {n: i for i, n in enumerate(names)}
    X = np.load(a.x).astype(np.float32)
    for name, paths in heads.items():
        cpp = margins_cpp(a.out, name, X, a.bot)
        ref = []
        for p in paths:
            b, feats = load_booster(p)
            m = b.predict(xgb.DMatrix(X[:, [idx[f] for f in feats]], feature_names=feats), output_margin=True)
            ref.append(m.reshape(len(X), -1))
        ref = np.concatenate(ref, axis=1)
        d = np.abs(cpp - ref).max()
        am = (cpp.argmax(1) != ref.argmax(1)).sum() if ref.shape[1] > 1 else 0
        print(f'{name}: rows {len(X)}, max |margin diff| {d:.2e}, argmax differences {int(am)}')


if __name__ == '__main__':
    main()
