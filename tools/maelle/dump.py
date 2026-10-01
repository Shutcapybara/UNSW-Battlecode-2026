#!/usr/bin/env python3
"""Read Maelle decision dumps (MAELLE_DUMP files written by maelle-02+ bots).

Record = int32 header[12] {magic 'MLD1', rnd, me, team, kind (0 target, 1 move), n, chosen, cols, len, units,
why, target} + n*cols float32. Target rows: log(score), steps, pearl_now, memory, bed, unseen, f(cell)[NT].
Move rows: score, steps, g(move)[NM].

    python tools/maelle/dump.py stats FILE...      # feature distributions (for the saturation scales)
"""
from __future__ import annotations

import sys
import numpy as np

MAGIC = 0x31444c4d
TNAMES = ["food", "food_unseen", "ally", "enemy", "threat", "death", "age", "food_sat", "food_clock",
          "ally_clock", "enemy_clock", "sparse", "food_free"]  # maelle-02 dumps carry the first 12
MNAMES = ["food", "ally", "enemy", "threat", "death", "age"]
TCOLS = ["logscore", "steps", "pearl_now", "memory", "bed", "unseen"] + TNAMES
MCOLS = ["score", "steps"] + MNAMES


def read(path):
    """-> list of (header dict, rows ndarray)"""
    b = open(path, "rb").read()
    out, i = [], 0
    while i + 48 <= len(b):
        h = np.frombuffer(b, np.int32, 12, i)
        if h[0] != MAGIC:
            raise ValueError(f"{path}: bad magic at {i}")
        n, cols = int(h[5]), int(h[7])
        rows = np.frombuffer(b, np.float32, n * cols, i + 48).reshape(n, cols)
        out.append((dict(rnd=int(h[1]), me=int(h[2]), team=chr(h[3]), kind=int(h[4]), n=n, chosen=int(h[6]),
                         len=int(h[8]), units=int(h[9]), why=chr(h[10]) if h[10] > 0 else '-', target=int(h[11])), rows))
        i += 48 + 4 * n * cols
    return out


def tables(paths):
    """-> (targets DataFrame, moves DataFrame); one row per candidate with decision keys and a chosen flag"""
    import pandas as pd
    T, M = [], []
    for gi, p in enumerate(paths):
        for dec, (h, rows) in enumerate(read(p)):
            cols = TCOLS if h["kind"] == 0 else MCOLS
            cols = (cols + [f"x{k}" for k in range(len(cols), rows.shape[1])])[:rows.shape[1]]
            df = pd.DataFrame(rows, columns=cols)
            df["chosen"] = (np.arange(h["n"]) == h["chosen"]).astype(np.int8)
            for k in ("rnd", "me", "team", "len", "units", "why"):
                df[k] = h[k]
            df["dec"] = f"{gi}:{h['me']}:{h['rnd']}"
            df["file"] = gi
            (T if h["kind"] == 0 else M).append(df)
    return (pd.concat(T, ignore_index=True) if T else None, pd.concat(M, ignore_index=True) if M else None)


def stats(paths):
    T, M = tables(paths)
    for name, df, feats in (("targets", T, TNAMES), ("moves", M, MNAMES)):
        if df is None:
            continue
        print(f"== {name}: {df['dec'].nunique()} decisions, {len(df)} rows")
        for f in feats:
            if f not in df:
                continue
            x = df[f].to_numpy()
            nz = x[x > 0]
            q = np.percentile(nz, [10, 50, 90]) if len(nz) else [0, 0, 0]
            print(f"  {f:12s} nonzero {len(nz) / len(x):6.1%}  p10/p50/p90 of nonzero {q[0]:.3f} {q[1]:.3f} {q[2]:.3f}"
                  f"  mean chosen {df.loc[df.chosen == 1, f].mean():.3f} vs all {x.mean():.3f}")


if __name__ == "__main__":
    if sys.argv[1] == "stats":
        stats(sys.argv[2:])
