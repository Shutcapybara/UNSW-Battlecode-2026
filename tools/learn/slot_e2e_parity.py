"""End-to-end parity of a slot bot in play (Data lane, kageyama; D-065 §D, D-066 §E, Sugawara's two conditions).

The bot is built with a debug writer (one file per process, /tmp/p1dbg/<id>.txt, lines "round pF pR pB pL"). This
script rebuilds the same process's inputs from the game's replay in Python (encoder v1 through encode.py, or HB-1's
vector through cpp/hb1_feats), scores them with the source LightGBM model (mirror-averaged with --mirror, using
export_gbt's tables, which equal tools/hinata/r2_mirror.py), and compares turn by turn. It also counts, per input
column, the turns on which the column was non-zero, so sparse columns are seen to have been exercised.

    python slot_e2e_parity.py REPLAY TEAM MODEL.txt FEATURES.txt [--dbg /tmp/p1dbg] [--mirror] [--hb1-exe EXE] [--out J]
"""
import argparse, collections, json, os, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rebuild, block as B, encode as E, labels as LB, export_gbt as X


def enc_rows(data, team):
    turns = collections.defaultdict(list)
    rebuild.walk(data, lambda i, sp, txt, ctx: turns[i].append((sp, txt, ctx)))
    rows, keys = [], []
    for did, seq in turns.items():
        sp = seq[0][0]
        if sp['team'] != team:
            continue
        enc = E.Encoder(B.Spawn(sp['id'], sp['team'], sp['W'], sp['H'], sp['unit_limit']))
        for k, (sp_, txt, ctx) in enumerate(seq):
            b = B.parse_block(txt)
            rows.append(enc.observe(b)); keys.append((did, k, ctx['round']))
            y = LB.label(ctx, b, did, sp['team'])
            if y['y_kind'] == 0: enc.act('move', list(y['y_seq']))
            elif y['y_kind'] == 1: enc.act('split', child=y['y_child'], rnd=ctx['round'])
            elif y['y_kind'] == 2: enc.act('invalid')
            else: enc.act('none')
    return np.asarray(rows, dtype=np.float32), keys


def hb1_rows(data, team, exe, feats):
    import hb1_export as HX
    keys, seqs, src = HX.game_turns('local', data, None, {team}, 100)
    names, M = HX.run_exe(exe, seqs)
    ix = {n: i for i, n in enumerate(names)}
    cols = [ix[f[5:]] for f in feats]
    return M[:, 3:][:, cols].astype(np.float32), [(k[2], k[4], k[3]) for k in keys]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('replay'); ap.add_argument('team'); ap.add_argument('model'); ap.add_argument('features')
    ap.add_argument('--dbg', default='/tmp/p1dbg'); ap.add_argument('--mirror', action='store_true')
    ap.add_argument('--hb1-exe', default=''); ap.add_argument('--out', default='')
    a = ap.parse_args()
    import lightgbm as lgb
    feats = [l.strip() for l in open(a.features) if l.strip()]
    data = open(a.replay, 'rb').read()
    if feats[0].startswith('hb_f_'):
        Xr, keys = hb1_rows(data, a.team, a.hb1_exe, feats)
    else:
        Xr, keys = enc_rows(data, a.team)
    bst = lgb.Booster(model_file=a.model)
    P = bst.predict(Xr)
    if a.mirror:
        src, neg, code = X.mirror_tables(feats)
        Xm = Xr[:, src].copy()
        for i in neg:
            Xm[:, i] = np.where(Xm[:, i] == 999, Xm[:, i], -Xm[:, i])
        orig = Xm.copy()
        for i, f, t in code:
            Xm[:, i] = np.where(orig[:, i] == f, t, Xm[:, i])
        P = 0.5 * (P + bst.predict(Xm)[:, [0, 3, 2, 1]])
    C = {int(f[:-4]): [list(map(float, l.split())) for l in open(Path(a.dbg) / f)] for f in os.listdir(a.dbg)}
    n = miss = big = am = 0; mx = 0.0
    for (did, k, r), p in zip(keys, P):
        if did not in C or k >= len(C[did]):
            miss += 1; continue
        c = C[did][k]
        assert int(c[0]) == r, (did, k, r, c[0])
        d = float(np.abs(np.array(c[1:]) - p).max()); mx = max(mx, d); n += 1; big += d > 1e-6
        am += int(np.argmax(c[1:]) == np.argmax(p))
    nz = (np.nan_to_num(Xr, nan=0.0) != 0).sum(0)
    res = dict(replay=a.replay, team=a.team, model=a.model, mirror=a.mirror, turns=len(keys), compared=n, missing=miss,
               max_abs_dp=mx, over_1e6=big, argmax_agree=am, processes_in_dbg=len(C),
               columns=len(feats), columns_never_nonzero=int((nz == 0).sum()),
               nonzero_turns={f: int(v) for f, v in zip(feats, nz)})
    print(json.dumps({k: v for k, v in res.items() if k != 'nonzero_turns'}))
    if a.out:
        Path(a.out).write_text(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
