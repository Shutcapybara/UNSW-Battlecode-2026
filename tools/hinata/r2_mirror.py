"""Hinata R2 arm A8 — left-right mirror of development rows (P-hinata-03 §"Arm A8", fixed before any A8 fit).

  check  --rows <parquet,...> [--side <hb shard,...>] --out <json>      involution + coverage on every row/column (no model)
  diag   --run <battery run dir> --rows ... [--side ...] --out <json>  existing fold models scored on mirrored test rows
                                                                        (labels swapped) vs unmirrored; descriptive
  fit    --arm A1|A3|A4|A5 --rows ... [--side ...] --run <dir> [--sizes 400,800] [--budget s]
         A8 = base arm trained on training rows + their mirror images (test rows never mirrored); same params/folds.

Map (Kageyama 21:26Z, 21:56Z): window x_f{F}r{R}_{ch} -> x_f{F}r{-R}_{ch} with kelp/portal/head_fac R<->L; scalars
x_exit_R<->x_exit_L, x_last_first_rel 1<->3, negate x_ownq_r, x_enemyq_r, x_home_r, x_mirror_xy_r, x_mirror_y_r except 999;
HB-1 hb_f_g_{f}_{r}_* -> hb_f_g_{f}_{-r}_*, hb_f_cR_*<->hb_f_cL_*, hb_f_pearl_right<->hb_f_pearl_left, hb_f_mem_last_rel 2<->3;
hb_pR<->hb_pL; label y_first 1<->3. Every other column is declared invariant and listed in `check`'s output.
"""
import argparse, json, re, sys, time
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r2_bc as R  # noqa: E402
import r2_battery as BAT  # noqa: E402

NEG_R = ['x_ownq_r', 'x_enemyq_r', 'x_home_r', 'x_mirror_xy_r', 'x_mirror_y_r']
SWAP_CH = {'kelp_R': 'kelp_L', 'portal_R': 'portal_L', 'head_fac_R': 'head_fac_L'}
CODE = {'x_last_first_rel': {1: 3, 3: 1}, 'hb_f_mem_last_rel': {2: 3, 3: 2}, 'y_first': {1: 3, 3: 1}}
WIN = re.compile(r'^x_f(m?\d)r(m?\d)_(.+)$'); HBG = re.compile(r'^hb_f_g_(-?\d+)_(-?\d+)_(.+)$')


def _neg(s):
    return s[1:] if s.startswith('m') else ('0' if s == '0' else 'm' + s)


def partner(c):
    """Column whose value moves into c under the mirror (the map is a permutation of columns plus value maps)."""
    m = WIN.match(c)
    if m:
        f, r, ch = m.groups(); ch = {**SWAP_CH, **{v: k for k, v in SWAP_CH.items()}}.get(ch, ch)
        return f'x_f{f}r{_neg(r)}_{ch}'
    m = HBG.match(c)
    if m:
        f, r, ch = m.groups(); return f'hb_f_g_{f}_{-int(r)}_{ch}'
    for a, b in (('x_exit_R', 'x_exit_L'), ('hb_f_pearl_right', 'hb_f_pearl_left'), ('hb_pR', 'hb_pL')):
        if c in (a, b):
            return b if c == a else a
    if c.startswith(('hb_f_cR_', 'hb_f_cL_')):
        return 'hb_f_cL_' + c[8:] if c.startswith('hb_f_cR_') else 'hb_f_cR_' + c[8:]
    return c


def mirror(d, cols):
    """Mirror image of rows d over columns cols (+ y_first). Column permutation, then value maps."""
    out = d.copy()
    for c in cols:
        p = partner(c)
        if p != c:
            if p not in d.columns:
                raise SystemExit(f'refused: mirror partner {p} of {c} absent')
            out[c] = d[p].to_numpy()
    for c in NEG_R:
        if c in cols:
            v = out[c].to_numpy(); out[c] = np.where(v == 999, v, -v).astype(v.dtype)
    for c, mp in CODE.items():
        if c in out.columns and (c in cols or c == 'y_first'):
            v = out[c].to_numpy(); w = v.copy()
            for a, b in mp.items():
                w[v == a] = b
            out[c] = w
    return out


def get(a):
    return BAT.get(argparse.Namespace(rows=a.rows, teachers=a.teachers, features=a.features, side=a.side, hb_prefix='hb_f_'))


def check(a):
    d, enc, hbf, dropped, paths, order = get(a); cols = enc + hbf + [c for c in BAT.HBP if c in d.columns]
    m2 = mirror(mirror(d, cols), cols); bad = [c for c in cols + ['y_first'] if not np.array_equal(m2[c].to_numpy(), d[c].to_numpy())]
    moved = [c for c in cols if partner(c) != c]; inv = [c for c in cols if partner(c) == c and c not in NEG_R and c not in CODE]
    m1 = mirror(d, cols); changed = {c: float((m1[c].to_numpy() != d[c].to_numpy()).mean()) for c in cols if c in NEG_R or c in CODE}
    out = dict(rows=int(len(d)), columns=len(cols), involution_failures=bad, permuted=len(moved), value_mapped=sorted(changed),
               value_mapped_changed_share=changed, invariant=inv, n_invariant=len(inv),
               y_first_counts=dict(orig=d.y_first.value_counts().sort_index().to_dict(), mirrored=m1.y_first.value_counts().sort_index().to_dict()))
    Path(a.out).write_text(json.dumps(out, indent=1, default=str)); print(json.dumps({k: v for k, v in out.items() if k != 'invariant'}, default=str)[:3000])


def diag(a):
    import lightgbm as lgb
    d, enc, hbf, dropped, paths, order = get(a); man = json.loads((Path(a.run) / 'manifest.json').read_text()); arm = man['arm']
    X = BAT.cols(arm, enc, hbf); m = mirror(d, X); F = R.folds(d, 'series5'); y = d.y_first.to_numpy(int); ym = m.y_first.to_numpy(int)
    s = max(man['sizes']) if not a.size else a.size; P = np.full((len(d), 4), np.nan); Pm = P.copy()
    for k, te in F.items():
        b = lgb.Booster(model_file=str(Path(a.run) / f'model_{k}.txt'))
        P[te] = b.predict(d.loc[te, X].to_numpy(np.float32), num_iteration=s); Pm[te] = b.predict(m.loc[te, X].to_numpy(np.float32), num_iteration=s)
    Pm_back = Pm[:, [0, 3, 2, 1]]   # mirrored prediction mapped back to the original frame (R<->L)
    ser = d.series_key.to_numpy()
    out = dict(arm=f'{arm}-{s}', run=a.run, unmirrored=R.frl(y, P), mirrored=R.frl(ym, Pm),
               mirrored_minus_unmirrored=BAT.paired(y, Pm_back, P, ser),
               argmax_agreement=float((R.FRL[P[:, R.FRL].argmax(1)] == R.FRL[Pm_back[:, R.FRL].argmax(1)])[np.isin(y, R.FRL)].mean()),
               mean_abs_dp=float(np.abs(P - Pm_back).mean()), population='dev120 oracle F/R/L moves, series5 folds, post-m2')
    Path(a.out).write_text(json.dumps(out, indent=1, default=str)); print(json.dumps(out, default=str))


def fit(a):
    import lightgbm as lgb
    t0 = time.time(); d, enc, hbf, dropped, paths, order = get(a); X = BAT.cols(a.arm, enc, hbf); BAT.need(d, X)
    run = Path(a.run); run.mkdir(parents=True, exist_ok=True); m = mirror(d, X)
    F = R.folds(d, 'series5'); rk = BAT.rowkey(d); import hashlib
    fh = {k: hashlib.sha256('\n'.join(sorted(rk[te])).encode()).hexdigest() for k, te in F.items()}
    if a.expect_folds and json.loads(Path(a.expect_folds).read_text())['folds'] != fh:
        raise SystemExit('refused: fold test-row hashes differ from --expect-folds')
    sizes = sorted(int(s) for s in a.sizes.split(',')); rounds = max(sizes); y = d.y_first.to_numpy(int); ym = m.y_first.to_numpy(int)
    man = dict(arm='A8', base=a.arm, rows_sha=[R.sha(p) for p in paths], side_sha=[R.sha(p) for p in a.side.split(',')] if a.side else [],
               code_sha=R.sha(__file__), r2_battery_sha=R.sha(BAT.__file__), r2_bc_sha=R.sha(R.__file__), features_sha=R.sha(a.features),
               n_features=len(X), params=BAT.PARAMS, rounds=rounds, sizes=sizes, folds=fh, augmentation='training rows + mirror images; test unmirrored')
    mp = run / 'manifest.json'
    if mp.exists() and json.loads(mp.read_text()) != json.loads(json.dumps(man, default=str)):
        raise SystemExit('refused: different manifest; use a new --run')
    mp.write_text(json.dumps(man, indent=1, default=str))
    Xo = d[X].to_numpy(np.float32); Xm = m[X].to_numpy(np.float32)
    Ps = {s: np.full((len(d), 4), np.nan) for s in sizes}; nb = {s: 0 for s in sizes}; fk = np.empty(len(d), object)
    for k, te in F.items():
        fk[te] = k; mf = run / f'model_{k}.txt'; tr = np.flatnonzero(~te)
        if not mf.exists():
            if time.time() - t0 > a.budget:
                print('budget reached; rerun to resume'); return
            Xt = np.concatenate([Xo[tr], Xm[tr]]); yt = np.concatenate([y[tr], ym[tr]])
            b = lgb.train(BAT.PARAMS, lgb.Dataset(Xt, yt, weight=np.ones(len(yt))), num_boost_round=rounds); del Xt
            b.save_model(str(mf)); print(f'{mf.name} {time.time() - t0:.0f}s', flush=True)
        b = lgb.Booster(model_file=str(mf)); ti = np.flatnonzero(te)
        for s in sizes:
            Ps[s][ti] = b.predict(Xo[ti], num_iteration=s); nb[s] += len(b.model_to_string(num_iteration=s).encode())
    arms = {f'A8-{a.arm}-{s}': Ps[s] for s in sizes}
    BAT.write(a, run, d, None, fk, arms, dict(arm='A8', base=a.arm, model_bytes={f'A8-{a.arm}-{s}': int(nb[s] / len(F)) for s in sizes},
                                               seconds=round(time.time() - t0)), paths, dropped, X)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['check', 'diag', 'fit'])
    ap.add_argument('--rows', required=True); ap.add_argument('--side'); ap.add_argument('--run'); ap.add_argument('--out')
    ap.add_argument('--arm', choices=['A1', 'A3', 'A4', 'A5']); ap.add_argument('--size', type=int)
    ap.add_argument('--teachers', default='build/learn/kageyama/teachers_v1.parquet'); ap.add_argument('--features', default=str(R.FEATS))
    ap.add_argument('--sizes', default='400,800'); ap.add_argument('--budget', type=float, default=1e9); ap.add_argument('--expect-folds')
    a = ap.parse_args(); a.weighted = False; {'check': check, 'diag': diag, 'fit': fit}[a.cmd](a)


if __name__ == '__main__':
    main()
