"""HB-1 Q4 step 0: which direction scorer is worth porting to C++?

    .venv/bin/python tools/hb1/q4_scorer_offline.py

On the Q1 direction rows (same held-out games), compares exportable scorers over the three candidates F/R/L:
  logit      conditional logit: score_c = w . phi(candidate c) + b_c, shared w (symmetric across directions)
  mlp_cand   shared-weight MLP per candidate: score_c = f([phi(c), global state]) + b_c
  gbt_full   the Q1 3-class GBT on the whole row (reference ceiling)
  gbt_100    the same, capped at 100 trees (export size)
phi(c) = that candidate's c?_ features, with the block code one-hot. Global state = the non-candidate, non-grid
columns (scalars, local summaries, memory, messages). Accuracy is reported raw and inside the wrapper's move mask
(free / portal / enemy-head only). Writes game_stats/runs/hb1-q4-scorer-offline.json.
"""
import json, sys, time
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import q1_decisions as Q1

ROOT = Path(__file__).resolve().parents[2]
B = ROOT / 'build' / 'hb1'
OUT = ROOT / 'game_stats' / 'runs' / 'hb1-q4-scorer-offline.json'
MOVES = ('F', 'R', 'L')
BLOCKS = (-1, 0, 1, 2, 3, 4, 5, 6, 7)


def cand_tensor(d):
    keys = sorted({c[3:] for c in d.columns if c.startswith('cF_')} - {'block'})
    per = []
    for r in MOVES:
        blk = d[f'c{r}_block'].to_numpy()
        oh = np.stack([blk == b for b in BLOCKS], 1).astype(np.float32)
        per.append(np.concatenate([d[[f'c{r}_{k}' for k in keys]].to_numpy(np.float32), oh], 1))
    return np.stack(per, 1), keys + [f'block_{b}' for b in BLOCKS]            # (n, 3, k)


def allowed(d):
    """Wrapper W4 move mask: free, portal or enemy-head target."""
    return np.stack([((d[f'c{r}_block'] == 0) | ((d[f'c{r}_block'] == -1) & (d[f'c{r}_portal'] == 1)) |
                      (d[f'c{r}_block'] == 7)).to_numpy() for r in MOVES], 1)


def fit_scorer(C, G, y, tr, te, hidden, epochs=10):
    import torch, torch.nn as nn
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    mu_c, sd_c = C[tr].reshape(-1, C.shape[2]).mean(0), C[tr].reshape(-1, C.shape[2]).std(0) + 1e-6
    tc = torch.tensor((C - mu_c) / sd_c, dtype=torch.float32, device=dev)
    if G is not None:
        mu_g, sd_g = G[tr].mean(0), G[tr].std(0) + 1e-6
        tg = torch.tensor((G - mu_g) / sd_g, dtype=torch.float32, device=dev)
    yt = torch.tensor(y, device=dev)
    torch.manual_seed(Q1.SEED)
    k = C.shape[2] + (G.shape[1] if G is not None else 0)
    net = (nn.Linear(k, 1) if hidden == 0 else
           nn.Sequential(nn.Linear(k, hidden), nn.ReLU(), nn.Linear(hidden, hidden // 2), nn.ReLU(),
                         nn.Linear(hidden // 2, 1))).to(dev)
    bias = nn.Parameter(torch.zeros(3, device=dev))
    opt = torch.optim.AdamW(list(net.parameters()) + [bias], lr=2e-3, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, epochs)

    def scores(idx):
        x = tc[idx]
        if G is not None:
            x = torch.cat([x, tg[idx].unsqueeze(1).expand(-1, 3, -1)], 2)
        return net(x).squeeze(-1) + bias

    tri = torch.tensor(np.flatnonzero(tr), device=dev)
    for _ in range(epochs):
        for i in tri[torch.randperm(len(tri), device=dev)].split(4096):
            opt.zero_grad()
            nn.functional.cross_entropy(scores(i), yt[i]).backward()
            opt.step()
        sched.step()
    with torch.no_grad():
        s = torch.cat([scores(i) for i in torch.tensor(np.flatnonzero(te), device=dev).split(65536)])
    n_par = sum(p.numel() for p in net.parameters()) + 3
    return s.softmax(1).cpu().numpy(), n_par


def acc(p, y, mask):
    raw = (p.argmax(1) == y).mean()
    pw = np.where(mask, p, -1)
    wr = (pw.argmax(1) == y).mean()
    return dict(acc=float(raw), acc_wrapped=float(wr))


def main():
    d = pd.read_parquet(B / 'q1' / 'direction.parquet')
    games = sorted(pd.read_parquet(B / 'games.parquet').query("set == 'corpus'").game.astype(int))
    test_games = set(np.random.default_rng(Q1.SEED).choice(games, len(games) // 5, replace=False).tolist())
    te = d.game.astype(int).isin(test_games).to_numpy()
    tr = ~te
    X, y = Q1.xy('direction', d)
    C, ckeys = cand_tensor(d)
    gcols = [c for c in X.columns if Q1.family(c) in ('scalar', 'local', 'memory', 'msgs') and c not in
             ('free_dirs', 'n_exit_ord', 'n_exit_portal', 'n_exit_any')]
    G = X[gcols].to_numpy(np.float32)
    mask = allowed(d)[te]
    res = dict(n_train=int(tr.sum()), n_test=int(te.sum()), cand_features=ckeys, global_features=gcols,
               obs_outside_mask=float((~mask[np.arange(te.sum()), y[te]]).mean()))
    for name, G_, h in (('logit_cand', None, 0), ('logit_cand+global', G, 0), ('mlp_cand', None, 64),
                        ('mlp_cand+global', G, 64), ('mlp_cand+global_128', G, 128)):
        t0 = time.time()
        p, npar = fit_scorer(C, G_, y, tr, te, h)
        res[name] = acc(p, y[te], mask) | dict(params=int(npar), sec=round(time.time() - t0, 1))
        print(name, res[name], flush=True)
    for name, it in (('gbt_full', 300), ('gbt_100', 100)):
        t0 = time.time()
        m, p = Q1.fit_gbt(X[tr], y[tr], X[te], y[te], iters=it)
        res[name] = acc(p, y[te], mask) | dict(trees=int(m.m.get_booster().num_boosted_rounds()) * 3,
                                               sec=round(time.time() - t0, 1))
        print(name, res[name], flush=True)
    OUT.write_text(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
