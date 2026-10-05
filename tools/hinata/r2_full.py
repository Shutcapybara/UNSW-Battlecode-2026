"""Hinata R2 — D-064 §C full-row refit: the best development tree arm and A10b refitted on Kageyama's full teacher rows
(build/learn/kageyama/teachers_v1/, one parquet per game). Same arms, parameters, series5 folds, F/R/L metric and whole-series
bootstrap as r2_battery.py / r2_cnn_b.py; only the loading and batching change so ~2.75 M rows fit in memory. Configuration
fixed in P-hinata-03 §"Full-row refit (D-064 §C)" before any full-row fit. TRAINING-SPLIT ROWS ONLY.

  trees --arm A1|A3|A4|A5 --dir <shard dir> --run <run dir> [--sizes 400,800] [--budget s] [--threads N]
  cnn   --dir <shard dir> --run <run dir> [--max-epochs 40] [--patience 3] [--threads N] [--budget s]
  rows  --dir <shard dir> --out <json>        support + oracle share per teacher and per map (no fit)

Loading: per shard, columns projected to keys + metadata + the arm's features; refusals as r2_bc.load (split must be 'train',
no held-out map, allowlist map-identity check); oracle move rows (y_kind 0, y_first 0..3, blocks_src 'oracle') kept in native
dtype (encoder int16, HB-1 float32); rev 2 fills preallocated matrices in a second pass (peak = matrices + one shard; peak RSS
printed and recorded as peak_gib). Trees: the training fold is materialised as float32 and handed to LightGBM exactly as
r2_battery.fit does (same construction, so dev120 parity is exact); peak memory = int16 store + one float32 training copy. num_threads = --threads (default ASAHI_MAX_WORKERS or 1);
all other LightGBM parameters are r2_bc.PARAMS. CNN: r2_cnn_b's network, inner split, early stopping and seeds unchanged;
the window tensor is cast to float32 per mini-batch. Resumable per fold (model files). Outputs as r2_battery.write (rows.parquet,
p_<arm>.npy, registry.json) plus support.json; the bridge line 'dev120 games' scores the out-of-fold predictions on the games
of build/learn/kageyama/teachers_dev120.p{0,1} (descriptive; folds differ from the development table's).
"""
import argparse, hashlib, json, os, sys, time
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r2_bc as R  # noqa: E402
import r2_battery as BAT  # noqa: E402

META = ['game', 'side', 'dragon', 'round', 'turn', 'split', 'map', 'map_era', 'series_key', 'blocks_src', 'y_kind', 'y_first', 'x_is_queen']
DEV120 = ['build/learn/kageyama/teachers_dev120.p0.parquet', 'build/learn/kageyama/teachers_dev120.p1.parquet']


def shards(dirp):
    return sorted(p for p in Path(dirp).glob('*.parquet') if not p.name.startswith('_'))


def peak_gib():
    import resource
    r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return round(r / 2 ** 30 if sys.platform == 'darwin' else r / 2 ** 20, 2)   # bytes on macOS, KiB on Linux


def load(dirp, teachers, X):
    """rev 2 (D-066 §C memory ceiling): two passes. Pass 1 reads metadata only and fixes the kept rows; pass 2 fills
    preallocated matrices (int16 columns -> Mi, all others -> Mf float32) shard by shard. Peak = the matrices + one shard.
    Row order and values are identical to rev 1 (shard order, filter, teacher join that preserves order)."""
    import pyarrow.parquet as pq
    hm = set(json.loads(R.HELDOUT.read_text())['heldout_maps'])
    bad = [c for c in X if R.banned(c[len('hb_f_'):] if c.startswith('hb_f_') else c)]
    if bad:
        raise SystemExit(f'refused: map-identity columns: {bad}')
    sh_ = shards(dirp); sc = pq.read_schema(sh_[0]); I = [j for j, c in enumerate(X) if str(sc.field(c).type) == 'int16']
    sI = set(I); Fl = [j for j in range(len(X)) if j not in sI]; metas = []; keeps = []; share = []
    for p in sh_:
        d = pd.read_parquet(p, columns=META)
        assert (d.split == 'train').all(), f'{p}: non-train rows'
        assert not d['map'].isin(hm).any(), f'{p}: held-out map rows present'
        mv = (d.y_kind == 0) & d.y_first.between(0, 3)
        share.append(d[mv].groupby('map').blocks_src.agg(lambda s: (s == 'oracle').sum()).rename('oracle').to_frame().join(
            d[mv].groupby('map').size().rename('moves')))
        k = (mv & (d.blocks_src == 'oracle')).to_numpy(); keeps.append(k)
        metas.append(d[k].drop(columns=['split', 'blocks_src', 'y_kind']))
    d = pd.concat(metas, ignore_index=True); del metas
    t = pd.read_parquet(teachers)[['game', 'side', 'team', 'weight']]
    n0 = len(d); d = d.merge(t, on=['game', 'side'], how='left')
    if len(d) != n0 or d.team.isna().any():
        raise SystemExit(f'refused: rows without a unique teacher entry')
    N = len(d); Mi = np.empty((N, len(I)), np.int16); Mf = np.empty((N, len(Fl)), np.float32); r0 = 0
    ci = [X[j] for j in I]; cf = [X[j] for j in Fl]
    for p, k in zip(sh_, keeps):
        n = int(k.sum())
        if n:
            x = pd.read_parquet(p, columns=ci + cf)
            Mi[r0:r0 + n] = x[ci].to_numpy(np.int16)[k] if ci else 0
            Mf[r0:r0 + n] = x[cf].to_numpy(np.float32)[k] if cf else 0
            r0 += n
    assert r0 == N
    sh = pd.concat(share).groupby(level=0).sum()
    return d, Mi, Mf, I, Fl, {m: dict(moves=int(r.moves), oracle=int(r.oracle), share=round(float(r.oracle / r.moves), 4)) for m, r in sh.iterrows()}


def arm_cols(arm, enc, hbf):
    return {'A1': hbf, 'A3': enc, 'A4': enc + BAT.HBP, 'A5': enc + hbf + BAT.HBP}[arm]


def hb_cols(dirp):
    import pyarrow.parquet as pq
    return [c for c in pq.read_schema(shards(dirp)[0]).names if c.startswith('hb_f_')]


def support(d, oracle_share):
    s = d.series_key.astype(str)
    return dict(rows=int(len(d)), frl=int(np.isin(d.y_first, R.FRL).sum()), games=int(d.game.nunique()), series=int(s.nunique()),
                teams=int(d.team.nunique()), maps=sorted(d['map'].unique().tolist()), map_era=sorted(d.map_era.astype(str).unique().tolist()),
                oracle_share_by_map=oracle_share,
                frl_by_team={str(k): int(v) for k, v in d[np.isin(d.y_first, R.FRL)].groupby('team').size().items()})


def bridge(d, P):
    g = set(pd.concat([pd.read_parquet(p, columns=['game']) for p in DEV120]).game.astype(str))
    m = d.game.astype(str).isin(g).to_numpy(); y = d.y_first.to_numpy(int)
    return dict(dev120_games=R.frl(y, P, m), not_dev120=R.frl(y, P, ~m))


def manifest(run, man):
    mp = run / 'manifest.json'
    if mp.exists() and json.loads(mp.read_text()) != json.loads(json.dumps(man, default=str)):
        raise SystemExit(f'refused: {run} has a different manifest; use a new --run')
    if not mp.exists() and (any(run.glob('model_*.txt')) or any(run.glob('model_*.pt'))):
        raise SystemExit(f'refused: {run} has models but no manifest')
    mp.write_text(json.dumps(man, indent=1, default=str))


def common(a, X):
    t0 = time.time(); run = Path(a.run); run.mkdir(parents=True, exist_ok=True)
    d, Mi, Mf, I, Fl, osh = load(a.dir, a.teachers, X); F = R.folds(d, 'series5'); rk = BAT.rowkey(d)
    fh = {k: hashlib.sha256('\n'.join(sorted(rk[te])).encode()).hexdigest() for k, te in F.items()}
    sup = support(d, osh); (run / 'support.json').write_text(json.dumps(sup, indent=1))
    print(f'loaded {len(d)} rows in {time.time() - t0:.0f}s, peak {peak_gib()} GiB', flush=True)
    return t0, run, d, F, fh, sup, Mi, Mf, I, Fl


def man_paths(dirp):   # registry rows_sha = the shard manifest's sha (it carries every shard's sha256)
    m = Path(dirp) / '_manifest.json'
    return [str(m)] if m.exists() else [str(p) for p in shards(dirp)]


def shard_shas(dirp):
    m = Path(dirp) / '_manifest.json'
    return R.sha(m) if m.exists() else None


def trees(a):
    import lightgbm as lgb
    enc = [l.strip() for l in Path(a.features).read_text().splitlines() if l.strip()]
    X = arm_cols(a.arm, enc, hb_cols(a.dir) if a.arm in ('A1', 'A5') else [])
    t0, run, d, F, fh, sup, Mi, Mf, I, Fl = common(a, X)
    sizes = sorted(int(s) for s in a.sizes.split(',')); rounds = max(sizes); P_ = dict(R.PARAMS, num_threads=a.threads)
    manifest(run, dict(arm=a.arm, mode='full-rows trees', dir=a.dir, shards_manifest_sha=shard_shas(a.dir), teachers_sha=R.sha(a.teachers),
                       code_sha=R.sha(__file__), r2_bc_sha=R.sha(R.__file__), r2_battery_sha=R.sha(BAT.__file__), features_sha=R.sha(a.features),
                       n_features=len(X), params=P_, rounds=rounds, sizes=sizes, weighted=False, n_rows=int(len(d)), folds=fh))
    y = d.y_first.to_numpy(int)

    def rowsx(r, dt=np.float32):
        o = np.empty((len(r), len(X)), dt); o[:, I] = Mi[r]; o[:, Fl] = Mf[r]; return o

    Ps = {s: np.full((len(d), 4), np.nan) for s in sizes}; nbytes = {s: 0 for s in sizes}; fk = np.empty(len(d), object)
    for k, te in F.items():
        fk[te] = k; mf = run / f'model_{k}.txt'
        if not mf.exists():
            if time.time() - t0 > a.budget:
                print('budget reached; rerun to resume'); return
            tr = np.flatnonzero(~te)
            # numpy float32 path exactly as r2_battery (a lightgbm.Sequence pre-filters rare features differently, which changes
            # feature_fraction's draws: parity check 22:58Z). Peak = int16 store + this float32 training copy.
            b = lgb.train(P_, lgb.Dataset(rowsx(tr), y[tr], weight=np.ones(len(tr))), num_boost_round=rounds)
            b.save_model(str(mf)); print(f'{mf.name} {time.time() - t0:.0f}s peak {peak_gib()} GiB', flush=True)
        b = lgb.Booster(model_file=str(mf)); ti = np.flatnonzero(te)
        for s in sizes:
            Ps[s][ti] = np.concatenate([b.predict(rowsx(ti[i:i + 100000]), num_iteration=s) for i in range(0, len(ti), 100000)])
            nbytes[s] += len(b.model_to_string(num_iteration=s).encode())
    arms = {f'{a.arm}-{s}': Ps[s] for s in sizes}
    info = dict(arm=a.arm, mode='full-rows', model_bytes={n: int(nbytes[int(n.split('-')[1])] / len(F)) for n in arms},
                support=sup, bridge={n: bridge(d, P) for n, P in arms.items()}, seconds=round(time.time() - t0), peak_gib=peak_gib())
    a.weighted = False; BAT.write(a, run, d, None, fk, arms, info, man_paths(a.dir), {}, X)


def cnn(a):
    import torch, torch.nn as nn
    from r2_cnn import layout
    enc = [l.strip() for l in Path(a.features).read_text().splitlines() if l.strip()]
    chans, flat, scal = layout(enc); C = len(chans); torch.set_num_threads(a.threads)
    t0, run, d, F, fh, sup, Mi, Mf, I, Fl = common(a, enc)
    if Fl:
        raise SystemExit('refused: encoder columns are expected to be int16')
    manifest(run, dict(arm='A10b', mode='full-rows cnn', dir=a.dir, shards_manifest_sha=shard_shas(a.dir), teachers_sha=R.sha(a.teachers),
                       code_sha=R.sha(__file__), r2_bc_sha=R.sha(R.__file__), r2_battery_sha=R.sha(BAT.__file__), features_sha=R.sha(a.features),
                       channels=chans, n_scalars=len(scal), max_epochs=a.max_epochs, patience=a.patience,
                       inner='sha256(inner/<series>)%1000<200', n_rows=int(len(d)), folds=fh))
    pos = {c: j for j, c in enumerate(enc)}; fi = np.array([pos[c] for c in flat]); si = np.array([pos[c] for c in scal])
    Xs = Mi[:, si].astype(np.float32); y = d.y_first.to_numpy(np.int64)   # rev 2: windows gathered per batch from Mi
    ser = d.series_key.astype(str).to_numpy(); P = np.full((len(d), 4), np.nan); fk = np.empty(len(d), object)

    def h(tag, s):
        return int(hashlib.sha256(f'{tag}/{s}'.encode()).hexdigest(), 16) % 1000

    class Net(nn.Module):   # r2_cnn_b.py (A10b) architecture, unchanged
        def __init__(s):
            super().__init__()
            s.c = nn.Sequential(nn.Conv2d(C, 32, 3, padding=1), nn.ReLU(), nn.Conv2d(32, 32, 3, padding=1), nn.ReLU(), nn.Flatten())
            s.h = nn.Sequential(nn.Linear(32 * 49 + len(scal), 64), nn.ReLU(), nn.Linear(64, 4))

        def forward(s, p, z):
            return s.h(torch.cat([s.c(p), z], 1))

    def xb(b):
        return torch.from_numpy(Mi[b][:, fi].astype(np.float32).reshape(len(b), C, 7, 7))

    def predict(net, rows, Z):
        net.eval(); out = []
        with torch.no_grad():
            for i in range(0, len(rows), 4096):
                b = rows[i:i + 4096]; out.append(torch.softmax(net(xb(b), torch.from_numpy(Z[b])), 1).numpy())
        net.train(); return np.concatenate(out)

    nparam = None; logs = {}
    for k, te in F.items():
        fk[te] = k; mf = run / f'model_{k}.pt'; lf = run / f'log_{k}.json'
        trS = sorted(set(ser[~te]))
        inS = [s for s in trS if h('inner', s) < 200] or [min(trS, key=lambda s: h('inner', s))]
        fitS = [s for s in trS if s not in inS]
        fit = np.isin(ser, fitS) & ~te; inn = np.isin(ser, inS) & ~te
        mu = Xs[fit].mean(0); sd = Xs[fit].std(0) + 1e-6; Z = ((Xs - mu) / sd).astype(np.float32)
        torch.manual_seed(7); net = Net(); nparam = sum(p.numel() for p in net.parameters())
        if mf.exists() and lf.exists():
            net.load_state_dict(torch.load(mf)); logs[k] = json.loads(lf.read_text())
        else:
            if time.time() - t0 > a.budget:
                print('budget reached; rerun to resume'); return
            opt = torch.optim.Adam(net.parameters(), 1e-3); lossf = nn.CrossEntropyLoss(); rng = np.random.default_rng(7)
            idx = np.flatnonzero(fit); ii = np.flatnonzero(inn); yi = y[ii]
            best, bestep, bad, state, hist = np.inf, -1, 0, None, []
            for ep in range(a.max_epochs):
                rng.shuffle(idx); tot = 0.0
                for i in range(0, len(idx), 512):
                    b = idx[i:i + 512]; opt.zero_grad()
                    loss = lossf(net(xb(b), torch.from_numpy(Z[b])), torch.from_numpy(y[b])); loss.backward(); opt.step()
                    tot += float(loss) * len(b)
                pv = predict(net, ii, Z); vl = float(-np.log(np.clip(pv[np.arange(len(ii)), yi], 1e-9, 1)).mean())
                hist.append(dict(epoch=ep, train_loss=round(tot / len(idx), 5), inner_loss=round(vl, 5)))
                print(f'{k} ep {ep} train {tot / len(idx):.4f} inner {vl:.4f} {time.time() - t0:.0f}s peak {peak_gib()} GiB', flush=True)
                if vl < best - 1e-6:
                    best, bestep, bad = vl, ep, 0; state = {n: t.clone() for n, t in net.state_dict().items()}
                else:
                    bad += 1
                    if bad >= a.patience:
                        break
            net.load_state_dict(state); torch.save(state, mf)
            logs[k] = dict(best_epoch=bestep, epochs_run=len(hist), best_inner_loss=round(best, 5), fit_series=len(fitS),
                           inner_series=len(inS), fit_rows=int(fit.sum()), inner_rows=int(inn.sum()), history=hist)
            lf.write_text(json.dumps(logs[k], indent=1))
        ti = np.flatnonzero(te); P[ti] = predict(net, ti, Z)
    a.weighted = False
    BAT.write(a, run, d, None, fk, {'A10b-full': P},
              dict(arm='A10b-full', mode='full-rows', model_bytes={'A10b-full': int(nparam)}, params=int(nparam), support=sup,
                   bridge={'A10b-full': bridge(d, P)}, peak_gib=peak_gib(), folds={k: {kk: v for kk, v in L.items() if kk != 'history'} for k, L in logs.items()},
                   seconds=round(time.time() - t0)), man_paths(a.dir), {}, enc)


def rows(a):
    enc = [l.strip() for l in Path(a.features).read_text().splitlines() if l.strip()]
    d, _, _, _, _, osh = load(a.dir, a.teachers, enc[:1]); Path(a.out).write_text(json.dumps(support(d, osh), indent=1)); print(json.dumps(support(d, osh))[:2000])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['trees', 'cnn', 'rows'])
    ap.add_argument('--arm', choices=['A1', 'A3', 'A4', 'A5']); ap.add_argument('--dir', default='build/learn/kageyama/teachers_v1')
    ap.add_argument('--run'); ap.add_argument('--out'); ap.add_argument('--teachers', default='build/learn/kageyama/teachers_v1.parquet')
    ap.add_argument('--features', default=str(R.FEATS)); ap.add_argument('--sizes', default='400,800')
    ap.add_argument('--max-epochs', type=int, default=40); ap.add_argument('--patience', type=int, default=3)
    ap.add_argument('--threads', type=int, default=int(os.environ.get('ASAHI_MAX_WORKERS', '1'))); ap.add_argument('--budget', type=float, default=1e9)
    a = ap.parse_args(); {'trees': trees, 'cnn': cnn, 'rows': rows}[a.cmd](a)


if __name__ == '__main__':
    main()
