"""Hinata R2 — D-057 §C / D-058 §C development battery. DEVELOPMENT ROWS ONLY; no card (each arm = a registry row).

  fit    --arm A1|A2|A3|A4|A5|A6|A7 --rows <parquet,...> --run build/hinata/r2/battery/<arm>-<tag>
         [--side <parquet,...>] [--rounds 800] [--sizes 400,800] [--weighted] [--budget 150] [--expect-folds <manifest.json>]
  a0     --rows ... --run ... [--side ...]           the parent's prior as it plays: argmax of hb_pF/hb_pR/hb_pL, no fit
  table  --runs <dir> --a0 <a0 run> [--out table.json]   D-057 §C table + the frozen selection rule (descriptive helper;
                                                      the rule is the Chair's text, this code implements it, it does not amend it)

Shared with r2_bc.py rev 4 (imported, not copied): load() (train-split/held-out refusals, teacher join, move turns,
blocks_src == 'oracle' filter, map-identity refusal on the allowlist), folds() (series5 hash 'hinata-r2/<series>'),
frl() (F/R/L-conditional accuracy, argmax over renormalised F/R/L) and series_boot() (1,000 x seed 7, 5th/95th).
--expect-folds refuses unless every fold's test-row hash equals the given manifest's (dev120: dev120-enc-s5/manifest.json).

Arms (D-057 §C, D-058 §C). Columns: ENC = allowlist r2_features_enc_v1.txt; HBF = HB-1's feature vector (columns with
prefix --hb-prefix, default 'hb_f_'); HBP = hb_pF, hb_pR, hb_pL (Kageyama hb1_scores, parent prior exactly as it plays).
  A1 HBF pooled | A2 HBF per teacher team (one fit per team per fold; pooling cost, D-058: deploy-candidate type)
  A3 ENC | A4 ENC+HBP (the card's union) | A5 ENC+HBF+HBP
  A6 ENC+HBP trained and scored on the three highest-rated teachers (lowest crank, then highest elo; teachers_v1)
  A7 ENC+HBP + teacher-team one-hot as input; scored twice: own identity (dev) and identity fixed to the top-rated team
  (the deploy form; never map identity). A8 (mirror augmentation) and A9 (split/cull/sprint heads) are NOT here: A8 needs
  Data's left-right column map of encoder v1, A9 needs labels of other action types; both are flagged, not improvised.
Sizes: one fit at max(--sizes) rounds; smaller sizes are the same booster's first n trees (identical to an n-round fit:
boosting is sequential and the bagging RNG advances per iteration). Unweighted by default (D-057 §C); --weighted = teacher weight.
Selection (D-057 §C, fixed): pooled arms A1/A3/A4/A5 x sizes; highest F/R/L fold accuracy; among arms whose whole-series
interval overlaps the leader's, the smallest model; must beat A0 on the same rows (paired whole-series bootstrap of the
accuracy difference, 5th pct > 0) and reach 0.75, else R2b. Sugawara 19:30Z: if the selected arm is in [0.750, 0.756], print
the runner-up and a leave-one-fold-out selection (descriptive). D-058 §C: best teacher-specific arm (A2/A6/A7) goes forward if
it beats A0 on its target teachers' rows (5th pct > 0). Never reads held-out maps, the frozen cohort, test or validation buckets.
"""
import argparse, hashlib, json, sys, time
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r2_bc as R  # noqa: E402

KEY = ['game', 'side', 'dragon', 'round', 'turn']
HBP = ['hb_pF', 'hb_pR', 'hb_pL']
POOLED = ('A1', 'A3', 'A4', 'A5')
PARAMS = dict(R.PARAMS)


def sha(p):
    return R.sha(p)


def rowkey(d):
    return (d.game.astype(str) + '/' + d.side.astype(str) + '/' + d.dragon.astype(str) + '/' + d['round'].astype(str) + '/' + d.turn.astype(str)).to_numpy()


def get(a):
    paths = a.rows.split(','); d, enc, dropped = R.load(paths, a.teachers, a.features, 'oracle')
    if a.side:
        s = pd.concat([pd.read_parquet(p) for p in a.side.split(',')], ignore_index=True)
        s = s[[c for c in s.columns if c in KEY or c in HBP or c.startswith(a.hb_prefix)]]
        assert not s.duplicated(KEY).any(), 'side file has duplicate row keys'
        n0 = len(d); d = d.drop(columns=[c for c in s.columns if c not in KEY and c in d.columns]).merge(s, on=KEY, how='left')
        assert len(d) == n0
    hbf = [c for c in d.columns if c.startswith(a.hb_prefix)]
    bad = [c for c in hbf if R.banned(c[len(a.hb_prefix):])]
    if bad:
        raise SystemExit(f'refused: map-identity HB-1 columns: {bad}')
    t = pd.read_parquet(a.teachers).groupby('team').agg(crank=('crank', 'min'), elo=('elo', 'max')).reset_index()
    order = t.sort_values(['crank', 'elo'], ascending=[True, False]).team.tolist()
    return d, enc, hbf, dropped, paths, order


def cols(arm, enc, hbf):
    c = {'A1': hbf, 'A2': hbf, 'A3': enc, 'A4': enc + HBP, 'A5': enc + hbf + HBP, 'A6': enc + HBP, 'A7': enc + HBP}[arm]
    if arm in ('A1', 'A2', 'A5') and not hbf:
        raise SystemExit(f'{arm} needs HB-1 feature columns (prefix hb_f_); none present')
    return c


def need(d, c):
    miss = [x for x in c if x not in d.columns]
    if miss:
        raise SystemExit(f'refused: columns absent: {miss[:8]}')
    nan = d[c].isna().any(axis=1).to_numpy()
    if nan.any():
        raise SystemExit(f'refused: {int(nan.sum())} rows lack HB-1/encoder values (side file incomplete)')


def a0(a):
    d, enc, hbf, dropped, paths, order = get(a); need(d, HBP); run = Path(a.run); run.mkdir(parents=True, exist_ok=True)
    P = np.zeros((len(d), 4)); P[:, 0], P[:, 1], P[:, 3] = d.hb_pF, d.hb_pR, d.hb_pL
    F = R.folds(d, 'series5'); fk = np.empty(len(d), object)
    for k, te in F.items():
        fk[te] = k
    write(a, run, d, P, fk, {'A0': P}, dict(arm='A0', model_bytes={'A0': 0}, fit='none (argmax of the parent prior hb_pF/R/L)'), paths, dropped, [])


def fit(a):
    import lightgbm as lgb
    t0 = time.time(); d, enc, hbf, dropped, paths, order = get(a); run = Path(a.run); run.mkdir(parents=True, exist_ok=True)
    X = cols(a.arm, enc, hbf); top3 = order[:3]; topteam = order[0]
    if a.arm == 'A6':
        d = d[d.team.isin(top3)].reset_index(drop=True)
    tcols = []
    if a.arm == 'A7':
        for t in sorted(d.team.unique()):
            d[f'tid_{t}'] = (d.team == t).astype(np.int8); tcols.append(f'tid_{t}')
        X = X + tcols
    need(d, X)
    F = R.folds(d, 'series5'); rk = rowkey(d)
    fh = {k: hashlib.sha256('\n'.join(sorted(rk[te])).encode()).hexdigest() for k, te in F.items()}
    if a.expect_folds and a.arm != 'A6':
        exp = json.loads(Path(a.expect_folds).read_text())['folds']
        if exp != fh:
            raise SystemExit('refused: fold test-row hashes differ from --expect-folds (not the same rows/folds)')
    y = d.y_first.to_numpy(int); w = d.weight.to_numpy(float) if a.weighted else np.ones(len(d))
    sizes = sorted(int(s) for s in a.sizes.split(',')); rounds = max(sizes)
    man = dict(arm=a.arm, rows_sha=[sha(p) for p in paths], side_sha=[sha(p) for p in a.side.split(',')] if a.side else [],
               teachers_sha=sha(a.teachers), code_sha=sha(__file__), r2_bc_sha=sha(R.__file__), features_sha=sha(a.features),
               n_features=len(X), hb_prefix=a.hb_prefix, params=PARAMS, rounds=rounds, sizes=sizes, weighted=a.weighted,
               teams_top3=[str(t) for t in top3], n_rows=int(len(d)), folds=fh)
    mp = run / 'manifest.json'
    if mp.exists():
        if json.loads(mp.read_text()) != json.loads(json.dumps(man, default=str)):
            raise SystemExit(f'refused: {run} has a different manifest; use a new --run')
    else:
        if any(run.glob('model_*.txt')):
            raise SystemExit(f'refused: {run} has models but no manifest')
        mp.write_text(json.dumps(man, indent=1, default=str))
    Ps = {s: np.full((len(d), 4), np.nan) for s in sizes}; Pfix = {s: np.full((len(d), 4), np.nan) for s in sizes}
    nbytes = {s: 0 for s in sizes}; fk = np.empty(len(d), object); groups = sorted(d.team.unique()) if a.arm == 'A2' else [None]
    for k, te in F.items():
        fk[te] = k
        for g in groups:
            tr = ~te if g is None else (~te & (d.team == g).to_numpy()); tt = te if g is None else (te & (d.team == g).to_numpy())
            mf = run / (f'model_{k}.txt' if g is None else f'model_{k}_t{g}.txt')
            if not tt.any() or not tr.any():
                continue
            if not mf.exists():
                if time.time() - t0 > a.budget:
                    print('budget reached; rerun to resume'); return
                b = lgb.train(PARAMS, lgb.Dataset(d.loc[tr, X].to_numpy(np.float32), y[tr], weight=w[tr]), num_boost_round=rounds)
                b.save_model(str(mf)); print(f'{mf.name} {time.time() - t0:.0f}s', flush=True)
            b = lgb.Booster(model_file=str(mf)); Xt = d.loc[tt, X].to_numpy(np.float32)
            for s in sizes:
                Ps[s][tt] = b.predict(Xt, num_iteration=s); nbytes[s] += len(b.model_to_string(num_iteration=s).encode())
            if a.arm == 'A7':
                Xf = d.loc[tt, X].copy()
                for c in tcols:
                    Xf[c] = np.int8(c == f'tid_{topteam}')
                for s in sizes:
                    Pfix[s][tt] = b.predict(Xf.to_numpy(np.float32), num_iteration=s)
    arms = {f'{a.arm}-{s}': Ps[s] for s in sizes}
    if a.arm == 'A7':
        arms.update({f'A7fix-{s}': Pfix[s] for s in sizes})
    mods = sorted(run.glob('model_*.txt'))
    info = dict(arm=a.arm, model_bytes={f'{n}-{s}': int(nbytes[s] / len(F)) for n in ({a.arm, 'A7fix'} if a.arm == 'A7' else {a.arm}) for s in sizes},
                n_models=len(mods), bytes_note='mean per fold of the booster text truncated at that size',
                note='A2 bytes = sum over teams per fold' if a.arm == 'A2' else '', seconds=round(time.time() - t0))
    write(a, run, d, None, fk, arms, info, paths, dropped, X)


def write(a, run, d, _, fk, arms, info, paths, dropped, X):
    base = d[['game', 'side', 'dragon', 'round', 'turn', 'map', 'team', 'series_key', 'x_is_queen', 'y_first']].assign(fold=fk)
    base.to_parquet(run / 'rows.parquet'); y = d.y_first.to_numpy(int); q = d.x_is_queen.to_numpy() == 1; out = {}
    for name, P in arms.items():
        np.save(run / f'p_{name}.npy', P.astype(np.float32))
        out[name] = dict(frl_all=R.frl(y, P), frl_queen=R.frl(y, P, q), frl_nonqueen=R.frl(y, P, ~q),
                         frl_boot=R.series_boot(y, P, d.series_key.to_numpy()),
                         frl_per_team={str(t): R.frl(y, P, (d.team == t).to_numpy()) for t in sorted(d.team.unique())},
                         frl_per_map={m: R.frl(y, P, (d['map'] == m).to_numpy()) for m in sorted(d['map'].unique())},
                         frl_per_fold={k: R.frl(y, P, fk == k) for k in sorted(set(fk))})
    reg = dict(artifact=f'hinata-r2-battery-{info["arm"]}', status='development (D-057 §C battery, no card)', info=info,
               rows_sha=[sha(p) for p in paths], code_sha=sha(__file__), r2_bc_sha=sha(R.__file__), n_features=len(X),
               blocks='oracle', dropped_by_blocks=dropped, weighted=bool(getattr(a, 'weighted', False)), params=PARAMS, arms=out)
    (run / 'registry.json').write_text(json.dumps(reg, indent=1, default=str))
    print(json.dumps({n: dict(acc=v['frl_all']['acc'], n=v['frl_all']['n'], p05=v['frl_boot']['p05'], p95=v['frl_boot']['p95'],
                              queen=v['frl_queen']['acc']) for n, v in out.items()}, indent=1))


def paired(y, P, P0, s, m=None, n=1000, seed=7):
    m = np.isin(y, R.FRL) if m is None else (m & np.isin(y, R.FRL))
    h = (R.FRL[P[:, R.FRL].argmax(1)] == y) & m; h0 = (R.FRL[P0[:, R.FRL].argmax(1)] == y) & m
    g = pd.DataFrame(dict(s=s, d=h.astype(float) - h0.astype(float), n=m.astype(float)))[m].groupby('s')[['d', 'n']].sum()
    rng = np.random.default_rng(seed); D, N = g.d.to_numpy(), g.n.to_numpy(); o = []
    for _ in range(n):
        i = rng.integers(0, len(g), len(g)); o.append(D[i].sum() / N[i].sum())
    return dict(diff=round(float(D.sum() / N.sum()), 4), p05=round(float(np.percentile(o, 5)), 4), p95=round(float(np.percentile(o, 95)), 4), series=int(len(g)))


def table(a):
    a0r = Path(a.a0); A0 = pd.read_parquet(a0r / 'rows.parquet'); P0 = np.load(a0r / 'p_A0.npy'); key0 = rowkey(A0)
    rows = []; best_ts = None
    for run in sorted(Path(a.runs).iterdir()):
        if not (run / 'registry.json').exists() or run.resolve() == a0r.resolve():
            continue
        reg = json.loads((run / 'registry.json').read_text()); B = pd.read_parquet(run / 'rows.parquet')
        idx = pd.Series(np.arange(len(A0)), index=key0).reindex(rowkey(B)).to_numpy()
        if np.isnan(idx.astype(float)).any():
            raise SystemExit(f'{run}: rows not in A0 run')
        y = B.y_first.to_numpy(int); p0 = P0[idx.astype(int)]
        for name, v in reg['arms'].items():
            P = np.load(run / f'p_{name}.npy'); arm = name.split('-')[0]
            r = dict(arm=name, pooled=arm in POOLED, acc=v['frl_all']['acc'], n=v['frl_all']['n'], p05=v['frl_boot']['p05'], p95=v['frl_boot']['p95'],
                     queen=v['frl_queen']['acc'], nonqueen=v['frl_nonqueen']['acc'], bytes=reg['info']['model_bytes'][name] if isinstance(reg['info']['model_bytes'], dict) else 0,
                     vs_A0=paired(y, P, p0, B.series_key.to_numpy()), per_fold={k: x['acc'] for k, x in v['frl_per_fold'].items()},
                     per_team={k: x['acc'] for k, x in v['frl_per_team'].items()}, per_map={k: x['acc'] for k, x in v['frl_per_map'].items()})
            if arm == 'A2':
                r['team_mean'] = round(float(np.mean([x for x in r['per_team'].values() if x is not None])), 4)
            rows.append(r)
    pool = [r for r in rows if r['pooled']]; sel = None
    if pool:
        lead = max(pool, key=lambda r: r['acc']); cand = [r for r in pool if r['p95'] >= lead['p05']]
        sel = min(cand, key=lambda r: (r['bytes'], -r['acc']))
        sel = dict(selected=sel['arm'], acc=sel['acc'], leader=lead['arm'], overlapping=[r['arm'] for r in cand],
                   beats_A0=sel['vs_A0']['p05'] > 0, reaches_075=sel['acc'] >= 0.75)
        sel['passes'] = sel['beats_A0'] and sel['reaches_075']
        if 0.750 <= sel['acc'] <= 0.756:
            ranked = sorted(pool, key=lambda r: -r['acc']); sel['runner_up'] = ranked[1]['arm'] if len(ranked) > 1 else None
            ks = sorted(pool[0]['per_fold']); lofo = {}
            for k in ks:
                pick = max(pool, key=lambda r: np.mean([r['per_fold'][j] for j in ks if j != k])); lofo[k] = (pick['arm'], pick['per_fold'][k])
            sel['leave_one_fold_out'] = lofo
    out = dict(rows=rows, selection=sel, a0=json.loads((a0r / 'registry.json').read_text())['arms']['A0']['frl_all'])
    Path(a.out).write_text(json.dumps(out, indent=1, default=str))
    for r in sorted(rows, key=lambda r: -r['acc']):
        print(f"{r['arm']:10s} acc {r['acc']} [{r['p05']}, {r['p95']}] queen {r['queen']} vsA0 {r['vs_A0']} bytes {r['bytes']}")
    print('selection', json.dumps(sel))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['fit', 'a0', 'table'])
    ap.add_argument('--arm', choices=['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7']); ap.add_argument('--rows'); ap.add_argument('--side')
    ap.add_argument('--teachers', default='build/learn/kageyama/teachers_v1.parquet'); ap.add_argument('--features', default=str(R.FEATS))
    ap.add_argument('--hb-prefix', default='hb_f_'); ap.add_argument('--run'); ap.add_argument('--sizes', default='400,800')
    ap.add_argument('--weighted', action='store_true'); ap.add_argument('--budget', type=float, default=1e9)
    ap.add_argument('--expect-folds'); ap.add_argument('--runs'); ap.add_argument('--a0'); ap.add_argument('--out', default='table.json')
    a = ap.parse_args(); {'fit': fit, 'a0': a0, 'table': table}[a.cmd](a)


if __name__ == '__main__':
    main()
