"""Hinata R2 — D-063 §C arm A10b: A10's CNN (r2_cnn.py, unchanged architecture) trained with early stopping on an inner
split of each fold's training series; plus its learning curve (D-062 §C). DEVELOPMENT ROWS ONLY; same rows, series5 folds,
F/R/L metric as r2_battery.py. Fixed in P-hinata-03 §"D-063 §C arm A10b" before any A10b fit.

  fit --rows <parquet,...> --run build/hinata/r2/battery/A10b-<tag> [--frac 1.0] [--max-epochs 40] [--patience 3]
      [--expect-folds <A10-u manifest>] [--threads 1]

Inner split: training series with sha256('inner/<series>') % 1000 < 200 (>= 1 series forced). Stop: 4-class cross-entropy
on inner rows after each epoch; best-epoch weights kept; stop after `patience` epochs without improvement or max-epochs.
No refit on the inner series. --frac < 1 subsamples TRAINING series by sha256('frac/<series>') % 1000 < frac*1000 (r2_bc rev 4
rule); test folds unchanged. Resumable per fold (model_<fold>.pt + log_<fold>.json written when a fold completes).
"""
import argparse, hashlib, json, sys, time
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r2_bc as R  # noqa: E402
import r2_battery as BAT  # noqa: E402
from r2_cnn import layout  # noqa: E402


def h(tag, s):
    return int(hashlib.sha256(f'{tag}/{s}'.encode()).hexdigest(), 16) % 1000


def main():
    import torch, torch.nn as nn
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['fit']); ap.add_argument('--rows', required=True)
    ap.add_argument('--run', required=True); ap.add_argument('--teachers', default='build/learn/kageyama/teachers_v1.parquet')
    ap.add_argument('--features', default=str(R.FEATS)); ap.add_argument('--frac', type=float, default=1.0)
    ap.add_argument('--max-epochs', type=int, default=40); ap.add_argument('--patience', type=int, default=3)
    ap.add_argument('--expect-folds'); ap.add_argument('--threads', type=int, default=1)
    a = ap.parse_args(); t0 = time.time(); torch.set_num_threads(a.threads); run = Path(a.run); run.mkdir(parents=True, exist_ok=True)
    paths = a.rows.split(','); d, X, dropped = R.load(paths, a.teachers, a.features, 'oracle')
    chans, flat, scal = layout(X); C = len(chans)
    F = R.folds(d, 'series5'); rk = BAT.rowkey(d)
    fh = {k: hashlib.sha256('\n'.join(sorted(rk[te])).encode()).hexdigest() for k, te in F.items()}
    if a.expect_folds and json.loads(Path(a.expect_folds).read_text())['folds'] != fh:
        raise SystemExit('refused: fold test-row hashes differ from --expect-folds')
    tag = f'A10b-f{int(round(a.frac * 100))}' if a.frac < 1 else 'A10b'
    man = dict(arm='A10b', tag=tag, rows_sha=[R.sha(p) for p in paths], code_sha=R.sha(__file__), r2_bc_sha=R.sha(R.__file__),
               r2_battery_sha=R.sha(BAT.__file__), teachers_sha=R.sha(a.teachers), features_sha=R.sha(a.features),
               channels=chans, n_scalars=len(scal), frac=a.frac, max_epochs=a.max_epochs, patience=a.patience,
               inner='sha256(inner/<series>)%1000<200', folds=fh)
    mp = run / 'manifest.json'
    if mp.exists() and json.loads(mp.read_text()) != json.loads(json.dumps(man)):
        raise SystemExit('refused: different manifest; use a new --run')
    if not mp.exists() and any(run.glob('model_*.pt')):
        raise SystemExit('refused: model files without a manifest; use a new --run')
    mp.write_text(json.dumps(man, indent=1))
    Xp = d[flat].to_numpy(np.float32).reshape(len(d), C, 7, 7); Xs = d[scal].to_numpy(np.float32); y = d.y_first.to_numpy(np.int64)
    ser = d.series_key.astype(str).to_numpy()
    useS = {s for s in set(ser) if a.frac >= 1 or h('frac', s) < a.frac * 1000}
    P = np.full((len(d), 4), np.nan); fk = np.empty(len(d), object)

    class Net(nn.Module):
        def __init__(s):
            super().__init__()
            s.c = nn.Sequential(nn.Conv2d(C, 32, 3, padding=1), nn.ReLU(), nn.Conv2d(32, 32, 3, padding=1), nn.ReLU(), nn.Flatten())
            s.h = nn.Sequential(nn.Linear(32 * 49 + len(scal), 64), nn.ReLU(), nn.Linear(64, 4))

        def forward(s, p, z):
            return s.h(torch.cat([s.c(p), z], 1))

    def predict(net, rows, Z):
        net.eval(); out = []
        with torch.no_grad():
            for i in range(0, len(rows), 4096):
                b = rows[i:i + 4096]; out.append(torch.softmax(net(torch.from_numpy(Xp[b]), torch.from_numpy(Z[b])), 1).numpy())
        net.train(); return np.concatenate(out)

    nparam = None; logs = {}
    for k, te in F.items():
        fk[te] = k; mf = run / f'model_{k}.pt'; lf = run / f'log_{k}.json'
        trS = sorted({s for s in set(ser[~te]) if s in useS})
        inS = [s for s in trS if h('inner', s) < 200] or [min(trS, key=lambda s: h('inner', s))]
        fitS = [s for s in trS if s not in inS]
        fit = np.isin(ser, fitS) & ~te; inn = np.isin(ser, inS) & ~te
        mu = Xs[fit].mean(0); sd = Xs[fit].std(0) + 1e-6; Z = (Xs - mu) / sd
        torch.manual_seed(7); net = Net(); nparam = sum(p.numel() for p in net.parameters())
        if mf.exists() and lf.exists():
            net.load_state_dict(torch.load(mf)); logs[k] = json.loads(lf.read_text())
        else:
            opt = torch.optim.Adam(net.parameters(), 1e-3); lossf = nn.CrossEntropyLoss(); rng = np.random.default_rng(7)
            idx = np.flatnonzero(fit); ii = np.flatnonzero(inn); yi = y[ii]
            best, bestep, bad, state, hist = np.inf, -1, 0, None, []
            for ep in range(a.max_epochs):
                rng.shuffle(idx); tot = 0.0
                for i in range(0, len(idx), 512):
                    b = idx[i:i + 512]; opt.zero_grad()
                    loss = lossf(net(torch.from_numpy(Xp[b]), torch.from_numpy(Z[b])), torch.from_numpy(y[b])); loss.backward(); opt.step()
                    tot += float(loss) * len(b)
                pv = predict(net, ii, Z); vl = float(-np.log(np.clip(pv[np.arange(len(ii)), yi], 1e-9, 1)).mean())
                hist.append(dict(epoch=ep, train_loss=round(tot / len(idx), 5), inner_loss=round(vl, 5)))
                print(f'{k} ep {ep} train {tot / len(idx):.4f} inner {vl:.4f} {time.time() - t0:.0f}s', flush=True)
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
    macs = C * 32 * 9 * 49 + 32 * 32 * 9 * 49 + (32 * 49 + len(scal)) * 64 + 64 * 4
    a.weighted = False
    BAT.write(a, run, d, None, fk, {tag: P},
              dict(arm='A10b', tag=tag, model_bytes={tag: int(nparam)}, bytes_note='parameters at 8-bit weights (+ scalar mean/sd not counted)',
                   params=int(nparam), macs_per_inference=int(macs), channels=C, scalars=len(scal), frac=a.frac,
                   folds={k: {kk: v for kk, v in L.items() if kk != 'history'} for k, L in logs.items()},
                   seconds=round(time.time() - t0)),
              paths, dropped, X)


if __name__ == '__main__':
    main()
