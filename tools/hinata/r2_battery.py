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
  A6 (ts_base inputs; rev 7: ENC+HBP) trained and scored on the three highest-rated teachers (lowest crank, then highest elo; teachers_v1)
  A7 (ts_base inputs; rev 7: ENC+HBP) + teacher-team one-hot as input; scored twice: own identity (dev) and identity fixed to the top-rated team
  (the deploy form; never map identity). A8 (mirror augmentation) and A9 (split/cull/sprint heads) are NOT here: A8 needs
  Data's left-right column map of encoder v1, A9 needs labels of other action types; both are flagged, not improvised.
Sizes: one fit at max(--sizes) rounds; smaller sizes are the same booster's first n trees (identical to an n-round fit:
boosting is sequential and the bagging RNG advances per iteration). Unweighted by default (D-057 §C); --weighted = teacher weight.
Rev 6 (4 Oct 21:5xZ, Tanaka 21:25Z blockers 1-4 + nonnegative check): teacher-specific support from A0 (A6 exact top-3
rows, A7 full support, A2 only training-unsupported cells missing), metadata equal to A0 on keys, fixed TS inventory.
Rev 8 (5 Oct 00:5xZ, D-066 §C): candidate identities, teacher-specific inventory, cohort minimum and the A6/A7 input base
(ts_base) are read from r2_inventory.json; code otherwise rev 7. A6 = ts_base inputs on the top-3 teachers; A7 = ts_base + teacher id.
Rev 7 (4 Oct 22:4xZ, Tanaka 22:25Z): explicit candidate identities (POOLED_NAMES incl. full-data A10b per D-063 §C; A10b-f25/f50
and A7/A7fix descriptive per D-064 §C; any other arm name refuses); A10b required in the pooled inventory; A2 team candidates
eligible only with >= 10 frozen-cohort series (--cohort-series from Data); teacher-specific inventory = A2, A6.
Selection (D-057 §C, fixed; A10 added by D-059 §B, A10b by D-063 §C): pooled arms A1/A3/A4/A5/A10 x sizes; highest F/R/L fold accuracy; among arms whose whole-series
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
# rev 7 (Tanaka 22:25Z): explicit candidate identities, not name prefixes. Pooled deploy candidates = D-057 §C arms x sizes,
# A10-e4 (D-059 §B) and the full-data early-stopped CNN A10b (D-063 §C). Learning-curve fits are descriptive only.
# rev 8 (D-066 §C): the inventory is configuration, read from r2_inventory.json (override with env R2_INVENTORY)
import os as _os  # noqa: E402
INV_PATH = Path(_os.environ.get('R2_INVENTORY', str(Path(__file__).resolve().parent / 'r2_inventory.json')))
INV = json.loads(INV_PATH.read_text())
POOLED_NAMES = tuple(INV['pooled']); DESCRIPTIVE = tuple(INV['descriptive']); TS_BASE = INV.get('ts_base')
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
    base = {'A1': hbf, 'A3': enc}
    if TS_BASE not in base:
        raise SystemExit(f'refused: inventory ts_base {TS_BASE} must be A1 or A3 (D-066 §C 3)')
    c = {'A1': hbf, 'A2': hbf, 'A3': enc, 'A4': enc + HBP, 'A5': enc + hbf + HBP, 'A6': base[TS_BASE], 'A7': base[TS_BASE]}[arm]
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
    write(a, run, d, P, fk, {'A0': P}, dict(arm='A0', model_bytes={'A0': 0}, fit='none (argmax of the parent prior hb_pF/R/L)',
                                            teams_by_rating=[str(t) for t in order]), paths, dropped, [])


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


def check(P, name):
    ok = np.isfinite(P).all(1) & (P >= 0).all(1) & (np.abs(P.sum(1) - 1) < 1e-3)   # rev 6: nonnegative (Tanaka 21:25Z)
    if not ok.all():
        raise SystemExit(f'refused: {name} has {int((~ok).sum())} rows with missing or non-normalised predictions')


def write(a, run, d, _, fk, arms, info, paths, dropped, X):
    sup = np.ones(len(d), bool)
    for P in arms.values():
        sup &= np.isfinite(P).all(1)
    if not sup.all():
        if info['arm'] != 'A2':
            raise SystemExit(f"refused: {info['arm']} left {int((~sup).sum())} rows unpredicted")
        info['unsupported_rows'] = int((~sup).sum())   # A2 only: team absent from a fold's train side; declared subset
        d = d[sup].reset_index(drop=True); fk = fk[sup]; arms = {k: v[sup] for k, v in arms.items()}
    for n, P in arms.items():
        check(P, n)
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


TS_PLANNED = list(INV['ts_planned'])   # rev 8: from the inventory file (rev 7: A2, A6; D-064 §C A7fix descriptive)
MIN_COHORT_SERIES = int(INV.get('min_cohort_series', 10))   # D-064 §C
META = ['team', 'series_key', 'map', 'x_is_queen']


def a2_allowed(A0):
    """rev 6 (Tanaka 21:25Z #3): the only rows A2 may leave unpredicted are A0 rows of (team t, fold k) where team t has no
    A0 row outside fold k (no training support). Derived from A0 alone, before reading any A2 output."""
    t = A0.team.astype(str).to_numpy(); f = A0.fold.astype(str).to_numpy(); bad = np.zeros(len(A0), bool); cells = []
    for tt in sorted(set(t)):
        for k in sorted(set(f)):
            if not ((t == tt) & (f != k)).any() and ((t == tt) & (f == k)).any():
                m = (t == tt) & (f == k); bad |= m; cells.append(dict(team=tt, fold=k, rows=int(m.sum())))
    return bad, cells


PLANNED = list(POOLED_NAMES) + TS_PLANNED   # rev 7: A10b (full data) is a required pooled arm
KNOWN = set(POOLED_NAMES) | set(DESCRIPTIVE) | set(TS_PLANNED)


def table(a):
    """Selection per D-057 §C (pooled) and D-058 §C (teacher-specific). Tanaka 20:19Z defects fixed: finite complete
    predictions; pooled arms must have exactly A0's row keys, folds and labels (one-to-one); teacher-specific arms are scored
    on a declared target subset against A0 on the same keys; planned-arm inventory printed; decisions carry run + manifest sha.
    Teacher-specific targets: A6 -> its three teams (all its rows); A7fix -> the top-rated team's rows; A2 -> per team t,
    the A2 model of team t on team t's rows. Ranking among teacher-specific candidates (different populations): paired
    lift over A0 on own target rows; goes forward iff its 5th pct > 0 (hinata operationalisation of 'best', for the Chair)."""
    a0r = Path(a.a0); A0 = pd.read_parquet(a0r / 'rows.parquet'); P0 = np.load(a0r / 'p_A0.npy'); check(P0, 'A0'); key0 = rowkey(A0)
    if len(set(key0)) != len(key0):
        raise SystemExit('A0 row keys not unique')
    pos0 = pd.Series(np.arange(len(A0)), index=key0); rows = []; ts = []
    order = json.loads((a0r / 'registry.json').read_text()).get('info', {}).get('teams_by_rating')
    if not order:
        raise SystemExit('refused: A0 registry lacks teams_by_rating (rerun a0 with rev 6)')
    top3_0 = [str(x) for x in order[:3]]; top1_0 = top3_0[0]; t0s = A0.team.astype(str).to_numpy()
    a2bad, a2cells = a2_allowed(A0); waived = [x for x in (a.waive_ts or '').split(',') if x]
    for run in sorted(Path(a.runs).iterdir()):
        if not (run / 'registry.json').exists() or run.resolve() == a0r.resolve():
            continue
        reg = json.loads((run / 'registry.json').read_text()); B = pd.read_parquet(run / 'rows.parquet'); kb = rowkey(B)
        if len(set(kb)) != len(kb):
            raise SystemExit(f'{run}: duplicate row keys')
        idx = pos0.reindex(kb).to_numpy()
        if np.isnan(idx.astype(float)).any():
            raise SystemExit(f'{run}: rows not in A0 run')
        idx = idx.astype(int)
        if not ((A0.y_first.to_numpy()[idx] == B.y_first.to_numpy()).all() and (A0.fold.to_numpy()[idx] == B.fold.to_numpy()).all()):
            raise SystemExit(f'{run}: labels or folds differ from A0 on shared keys')
        for c in META:   # rev 6 (#2): metadata must equal A0's on the keys; clusters and targets are then taken from A0
            if not (A0[c].astype(str).to_numpy()[idx] == B[c].astype(str).to_numpy()).all():
                raise SystemExit(f'{run}: {c} differs from A0 on shared keys')
        y = B.y_first.to_numpy(int); p0 = P0[idx]; ms = sha(run / 'manifest.json')[:12]; s = A0.series_key.to_numpy()[idx]
        top = [str(x) for x in (json.loads((run / 'manifest.json').read_text()).get('teams_top3') or [])]
        inB = np.zeros(len(A0), bool); inB[idx] = True; tB = t0s[idx]
        for name, v in reg['arms'].items():
            if name not in KNOWN:   # rev 7: unknown identities refuse instead of being classified by prefix
                raise SystemExit(f'{run}/{name}: not a declared candidate identity {sorted(KNOWN)}')
            P = np.load(run / f'p_{name}.npy'); check(P, name); arm = name.split('-')[0]; pooled = name in POOLED_NAMES
            if pooled and len(B) != len(A0):
                raise SystemExit(f'{run}/{name}: pooled arm covers {len(B)} of {len(A0)} A0 rows; pooled arms need the full support')
            if arm == 'A6':   # rev 6 (#1): exactly A0's rows of the three top-rated teams, as declared and as A0 ranks them
                if top != top3_0:
                    raise SystemExit(f'{run}/{name}: declared teams {top} != A0 top three {top3_0}')
                if not (inB == np.isin(t0s, top3_0)).all():
                    raise SystemExit(f'{run}/{name}: rows are not exactly A0 rows of teams {top3_0}')
            if arm in ('A7', 'A7fix') and len(B) != len(A0):   # rev 6 (#2): A7 trains/scores on all teams -> full support
                raise SystemExit(f'{run}/{name}: A7 covers {len(B)} of {len(A0)} A0 rows; full support required')
            if arm in ('A7', 'A7fix') and top[:1] != [top1_0]:
                raise SystemExit(f'{run}/{name}: declared top team {top[:1]} != A0 top-rated {top1_0}')
            if arm == 'A2' and not (inB == ~a2bad).all():   # rev 6 (#3): only the training-unsupported cells may be missing
                raise SystemExit(f'{run}/{name}: A2 rows != A0 minus the {int(a2bad.sum())} training-unsupported rows {a2cells}')
            mb = reg['info']['model_bytes']; r = dict(arm=name, run=run.name, manifest=ms, pooled=pooled, role='pooled' if pooled else ('descriptive' if name in DESCRIPTIVE else 'teacher-specific'), rows=int(len(B)),
                     acc=v['frl_all']['acc'], n=v['frl_all']['n'], p05=v['frl_boot']['p05'], p95=v['frl_boot']['p95'],
                     queen=v['frl_queen']['acc'], nonqueen=v['frl_nonqueen']['acc'], bytes=mb.get(name, 0) if isinstance(mb, dict) else 0,
                     vs_A0=paired(y, P, p0, s), per_fold={k: x['acc'] for k, x in v['frl_per_fold'].items()},
                     per_team={k: x['acc'] for k, x in v['frl_per_team'].items()}, per_map={k: x['acc'] for k, x in v['frl_per_map'].items()})
            if arm == 'A2':
                r['team_mean'] = round(float(np.mean([x for x in r['per_team'].values() if x is not None])), 4)
                r['excluded'] = dict(rows=int(a2bad.sum()), cells=a2cells)
                for t in sorted(set(tB)):
                    m = tB == t; ts.append(dict(cand=f'{name}[team {t}]', target=f'team {t}', target_rows=int(m.sum()), run=run.name, manifest=ms, vs_A0=paired(y, P, p0, s, m)))
            elif arm == 'A6':
                ts.append(dict(cand=name, target=f'teams {top3_0}', target_rows=int(len(B)), run=run.name, manifest=ms, vs_A0=r['vs_A0']))
            elif arm == 'A7fix':
                m = tB == top1_0
                r['descriptive_vs_A0_top_team'] = dict(cand=name, target=f'team {top1_0} (top-rated)', target_rows=int(m.sum()), vs_A0=paired(y, P, p0, s, m))   # rev 7: descriptive only (D-064 §C)
            rows.append(r)
    have = {r['arm'] for r in rows}; missing = [x for x in PLANNED if x not in have]
    pool = [r for r in rows if r['pooled']]; sel = None
    if pool:
        lead = max(pool, key=lambda r: r['acc']); cand = [r for r in pool if r['p95'] >= lead['p05']]
        pick = min(cand, key=lambda r: (r['bytes'], -r['acc']))
        sel = dict(selected=pick['arm'], run=pick['run'], manifest=pick['manifest'], acc=pick['acc'], leader=lead['arm'],
                   overlapping=[r['arm'] for r in cand], beats_A0=pick['vs_A0']['p05'] > 0, reaches_075=pick['acc'] >= 0.75,
                   pooled_missing=[x for x in missing if x in POOLED_NAMES])
        sel['passes'] = sel['beats_A0'] and sel['reaches_075'] and not sel['pooled_missing']
        if sel['pooled_missing']:
            sel['note'] = 'INCOMPLETE: planned pooled arms missing; no selection claim'
        if 0.750 <= pick['acc'] <= 0.756:
            ranked = sorted(pool, key=lambda r: -r['acc']); sel['runner_up'] = ranked[1]['arm'] if len(ranked) > 1 else None
            ks = sorted(pool[0]['per_fold']); sel['leave_one_fold_out'] = {
                k: (lambda q: (q['arm'], q['per_fold'][k]))(max(pool, key=lambda r: np.mean([r['per_fold'][j] for j in ks if j != k]))) for k in ks}
    tsel = None
    ts_missing = [x for x in TS_PLANNED if x not in have and x not in waived]   # rev 6 (#4)
    if ts:   # rev 7: A2 team candidates need >= MIN_COHORT_SERIES frozen-cohort series (counts from Data, read without labels)
        cs = json.loads(Path(a.cohort_series).read_text()) if a.cohort_series else None
        for c in ts:
            if c['cand'].startswith('A2'):
                t = c['target'].split(' ', 1)[1]; c['cohort_series'] = None if cs is None else cs.get(t, 0)
                c['eligible'] = cs is not None and cs.get(t, 0) >= MIN_COHORT_SERIES
            else:
                c['eligible'] = True
        if any(c['cand'].startswith('A2') for c in ts) and cs is None:
            ts_missing = ts_missing + ['cohort-series counts (--cohort-series, Data)']
        ts_el = [c for c in ts if c['eligible']] or ts
        b = max(ts_el, key=lambda c: c['vs_A0']['diff'])
        tsel = dict(best=b, candidates=len(ts), ts_missing=ts_missing, waived=waived,
                    goes_forward=bool(b['eligible'] and b['vs_A0']['p05'] > 0 and not ts_missing))
        if ts_missing:
            tsel['note'] = 'INCOMPLETE: planned teacher-specific arms missing (Chair waiver needed); no advancement'
    out = dict(inventory=dict(path=str(INV_PATH), sha=sha(INV_PATH)), rows=rows, selection=sel, teacher_specific=dict(candidates=ts, selection=tsel), missing_planned=missing,
               a0=json.loads((a0r / 'registry.json').read_text())['arms']['A0']['frl_all'])
    Path(a.out).write_text(json.dumps(out, indent=1, default=str))
    for r in sorted(rows, key=lambda r: -r['acc']):
        print(f"{r['arm']:10s} rows {r['rows']} acc {r['acc']} [{r['p05']}, {r['p95']}] queen {r['queen']} vsA0 {r['vs_A0']} bytes {r['bytes']}")
    print('inventory', INV_PATH, sha(INV_PATH)[:12]); print('missing planned:', missing); print('selection', json.dumps(sel)); print('teacher-specific', json.dumps(tsel, default=str))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['fit', 'a0', 'table'])
    ap.add_argument('--arm', choices=['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7']); ap.add_argument('--rows'); ap.add_argument('--side')
    ap.add_argument('--teachers', default='build/learn/kageyama/teachers_v1.parquet'); ap.add_argument('--features', default=str(R.FEATS))
    ap.add_argument('--hb-prefix', default='hb_f_'); ap.add_argument('--run'); ap.add_argument('--sizes', default='400,800')
    ap.add_argument('--weighted', action='store_true'); ap.add_argument('--budget', type=float, default=1e9)
    ap.add_argument('--expect-folds'); ap.add_argument('--runs'); ap.add_argument('--a0'); ap.add_argument('--out', default='table.json')
    ap.add_argument('--cohort-series', help='JSON {team: frozen-cohort series count} from Data (no labels); rev 7, D-064 §C')
    ap.add_argument('--waive-ts', help='comma list of teacher-specific planned arms the Chair has waived (recorded)')
    a = ap.parse_args(); {'fit': fit, 'a0': a0, 'table': table}[a.cmd](a)


if __name__ == '__main__':
    main()
