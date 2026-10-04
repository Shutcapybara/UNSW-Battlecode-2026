"""Hinata R2 — D-059 §B battery arm A10: a small CNN on the dragon's own egocentric 7x7 window + scalar features,
forward/right/left head, no recurrence. DEVELOPMENT ROWS ONLY; same rows, series5 folds, F/R/L metric as r2_battery.py.

  fit --rows <parquet,...> --run build/hinata/r2/battery/A10-<tag> [--epochs 4] [--expect-folds <manifest>] [--threads 1]

Input (encoder v1, read from the allowlist, layout inferred from column names; Kageyama to confirm, D-059 §B):
  planes  x_f{a}r{b}_{ch}: a = forward offset -3..3 (fm3..f3), b = lateral offset -3..3 (rm3..r3), 23 channels
          -> tensor [23, 7, 7] (rows a, cols b); facing-relative, so no map identity and no absolute position.
  scalars every other allowlisted column (66), standardised by the training fold's mean/sd.
Net (fixed 4 Oct, before any A10 outcome; no tuning): conv3x3 23->32, ReLU, conv3x3 32->32, ReLU (padding 1), flatten
  1568 ++ scalars -> FC 64, ReLU -> FC 4 (F, R, B, L). Adam lr 1e-3, batch 512, 4 epochs, cross-entropy, unweighted,
  torch seed 7, rows shuffled per epoch (numpy seed 7). Scored like every arm: F/R/L-conditional argmax.
Reports: accuracy (via r2_battery.write -> registry.json, table-compatible), parameter count = bytes at 8-bit weights,
  multiply-accumulates per inference (the Evaluator converts MACs to engine points with a deploy probe; not estimated here).
"""
import argparse, hashlib, json, re, sys, time
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r2_bc as R  # noqa: E402
import r2_battery as BAT  # noqa: E402

OFF = ['m3', 'm2', 'm1', '0', '1', '2', '3']


def layout(X):
    pat = re.compile(r'^x_f(m?\d)r(m?\d)_(.+)$'); chans = []
    for c in X:
        m = pat.match(c)
        if m and m.group(3) not in chans:
            chans.append(m.group(3))
    grid = [[[f'x_f{a}r{b}_{ch}' for b in OFF] for a in OFF] for ch in chans]
    flat = [c for ch in grid for row in ch for c in row]
    miss = [c for c in flat if c not in X]
    if miss:
        raise SystemExit(f'window layout incomplete: {miss[:5]}')
    scal = [c for c in X if c not in set(flat)]
    return chans, flat, scal


def main():
    import torch, torch.nn as nn
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['fit']); ap.add_argument('--rows', required=True)
    ap.add_argument('--run', required=True); ap.add_argument('--teachers', default='build/learn/kageyama/teachers_v1.parquet')
    ap.add_argument('--features', default=str(R.FEATS)); ap.add_argument('--epochs', type=int, default=4)
    ap.add_argument('--expect-folds'); ap.add_argument('--threads', type=int, default=1)
    a = ap.parse_args(); t0 = time.time(); torch.set_num_threads(a.threads); run = Path(a.run); run.mkdir(parents=True, exist_ok=True)
    paths = a.rows.split(','); d, X, dropped = R.load(paths, a.teachers, a.features, 'oracle')
    chans, flat, scal = layout(X); C = len(chans)
    F = R.folds(d, 'series5'); rk = BAT.rowkey(d)
    fh = {k: hashlib.sha256('\n'.join(sorted(rk[te])).encode()).hexdigest() for k, te in F.items()}
    if a.expect_folds and json.loads(Path(a.expect_folds).read_text())['folds'] != fh:
        raise SystemExit('refused: fold test-row hashes differ from --expect-folds')
    man = dict(arm='A10', rows_sha=[R.sha(p) for p in paths], code_sha=R.sha(__file__), r2_bc_sha=R.sha(R.__file__),
               r2_battery_sha=R.sha(BAT.__file__), teachers_sha=R.sha(a.teachers), features_sha=R.sha(a.features),
               channels=chans, n_scalars=len(scal), epochs=a.epochs, folds=fh)
    mp = run / 'manifest.json'
    if mp.exists() and json.loads(mp.read_text()) != json.loads(json.dumps(man)):
        raise SystemExit('refused: different manifest; use a new --run')
    if not mp.exists() and any(run.glob('model_*.pt')):
        raise SystemExit('refused: model files without a manifest; use a new --run')
    mp.write_text(json.dumps(man, indent=1))
    Xp = d[flat].to_numpy(np.float32).reshape(len(d), C, 7, 7); Xs = d[scal].to_numpy(np.float32); y = d.y_first.to_numpy(np.int64)
    P = np.full((len(d), 4), np.nan); fk = np.empty(len(d), object)

    class Net(nn.Module):
        def __init__(s):
            super().__init__()
            s.c = nn.Sequential(nn.Conv2d(C, 32, 3, padding=1), nn.ReLU(), nn.Conv2d(32, 32, 3, padding=1), nn.ReLU(), nn.Flatten())
            s.h = nn.Sequential(nn.Linear(32 * 49 + len(scal), 64), nn.ReLU(), nn.Linear(64, 4))

        def forward(s, p, z):
            return s.h(torch.cat([s.c(p), z], 1))

    nparam = None
    for k, te in F.items():
        fk[te] = k; mf = run / f'model_{k}.pt'; tr = ~te
        mu = Xs[tr].mean(0); sd = Xs[tr].std(0) + 1e-6; Z = (Xs - mu) / sd
        torch.manual_seed(7); net = Net(); nparam = sum(p.numel() for p in net.parameters())
        if mf.exists():
            net.load_state_dict(torch.load(mf))
        else:
            opt = torch.optim.Adam(net.parameters(), 1e-3); lossf = nn.CrossEntropyLoss(); rng = np.random.default_rng(7)
            idx = np.flatnonzero(tr)
            for ep in range(a.epochs):
                rng.shuffle(idx); tot = 0.0
                for i in range(0, len(idx), 512):
                    b = idx[i:i + 512]; opt.zero_grad()
                    loss = lossf(net(torch.from_numpy(Xp[b]), torch.from_numpy(Z[b])), torch.from_numpy(y[b])); loss.backward(); opt.step()
                    tot += float(loss) * len(b)
                print(f'{k} epoch {ep} loss {tot / len(idx):.4f} {time.time() - t0:.0f}s', flush=True)
            torch.save(net.state_dict(), mf)
        net.eval(); ti = np.flatnonzero(te); out = []
        with torch.no_grad():
            for i in range(0, len(ti), 4096):
                b = ti[i:i + 4096]; out.append(torch.softmax(net(torch.from_numpy(Xp[b]), torch.from_numpy(Z[b])), 1).numpy())
        P[ti] = np.concatenate(out)
    macs = C * 32 * 9 * 49 + 32 * 32 * 9 * 49 + (32 * 49 + len(scal)) * 64 + 64 * 4
    a.weighted = False
    BAT.write(a, run, d, None, fk, {f'A10-e{a.epochs}': P},
              dict(arm='A10', model_bytes={f'A10-e{a.epochs}': int(nparam)}, bytes_note='parameters at 8-bit weights (+ scalar mean/sd not counted)',
                   params=int(nparam), macs_per_inference=int(macs), channels=C, scalars=len(scal), seconds=round(time.time() - t0)),
              paths, dropped, X)


if __name__ == '__main__':
    main()
