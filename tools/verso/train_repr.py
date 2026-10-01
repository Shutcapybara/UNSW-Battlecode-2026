"""Verso tier 1: a small CNN over the egocentric map-memory window and a GRU over the dragon's turns, trained with
auxiliary decision/outcome heads, then frozen; its state is exported as extra features for tier 2.

    .venv/bin/python tools/verso/train_repr.py fit   --name r1 --data ARM[,ARM] [--epochs 6] [--hidden 96] [--emb 64]
    .venv/bin/python tools/verso/train_repr.py embed --name r1 --data ARM[,ARM]     # <game>.emb-<name>.npy per game
    .venv/bin/python tools/verso/train_repr.py probe --name r1 --data ARM[,ARM]     # linear probes on the state

Input per turn: the bot's own view tensor (verso.hpp ViewDump: 18 byte channels on an 11x11 window of its map
memory, facing up; read from <game>.view.npz) plus a few scalars from the feature vector. Sequences are one
dragon's consecutive turns. Auxiliary heads: the first step taken (F/R/L), the 20-round lineage return, death
within 20 rounds, bed pearls eaten within 20 rounds. Held-out = fold 0 of the by-game split used by
train_heads.py (same seed), so tier-2 comparisons with and without the embedding share their test games.
"""
from __future__ import annotations

import argparse, glob, json, sys, time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C
import dataset as D

SCALARS = ['length', 'units_frac', 'round', 'echo_kelp', 'echo_ally', 'echo_allyHead', 'echo_enemy',
           'echo_enemyHead', 'n_msgs', 'mem_len_delta', 'mem_since_eat', 'mem_since_split', 'mem_last_rel']
SCALE = [20, 1, 500, 8, 8, 8, 8, 8, 8, 1, 50, 50, 4]
ONEHOT = {0: 3, 2: 3, 5: 7, 7: 4, 8: 4, 9: 4, 10: 4}           # channel -> classes
DENSE = {1: 255, 3: 1, 4: 61, 6: 20, 11: 255, 12: 255, 13: 255, 14: 255, 15: 255, 16: 16, 17: 13}
N_PLANES = sum(ONEHOT.values()) + len(DENSE)


def load_games(arms, panel='train', limit=0):
    """-> list of dicts per game with H, S (scalars), V (uint8 tensor), Y, plus the global fold of each game."""
    _, names = C.schema()
    si = [names.index(s) for s in SCALARS]
    files = []
    for arm in arms.split(','):
        fs = sorted(f for f in glob.glob(str(C.B / 'data' / arm / panel / '*.npz'))
                    if not f.endswith(('.tmp.npz', '.view.npz')))
        files += fs[:limit] if limit else fs
    n = len(files)
    fold = np.empty(n, np.int8)
    fold[np.random.default_rng(C.SEED).permutation(n)] = np.arange(n) % 5
    out = []
    for gi, f in enumerate(files):
        vp = Path(f).with_suffix('.view.npz')
        if not vp.exists():
            continue
        z, v = np.load(f), np.load(vp)
        out.append(dict(name=Path(f).stem, path=f, H=z['H'], S=z['X'][:, si] / np.array(SCALE, np.float32),
                        V=v['V'], ok=v['ok'], Y=z['Y'], fold=int(fold[gi])))
    return out


def sequences(g):
    """row indices of each dragon's turns, in round order"""
    H = g['H']
    key = H[:, 3].astype(np.int64) * 2 + (H[:, 4] == 66)
    order = np.lexsort((H[:, 2], key))
    cuts = np.flatnonzero(np.diff(key[order])) + 1
    return np.split(order, cuts)


def planes(V, device):
    """uint8 [n, 18, 11, 11] -> float [n, N_PLANES, 11, 11]"""
    import torch
    import torch.nn.functional as F
    v = torch.as_tensor(V, device=device).long()
    parts = []
    for ch, k in ONEHOT.items():
        parts.append(F.one_hot(v[:, ch].clamp(max=k - 1), k).permute(0, 3, 1, 2).float())
    for ch, sc in DENSE.items():
        parts.append((v[:, ch].float() / sc).clamp(max=1.0).unsqueeze(1))
    return torch.cat(parts, 1)


def make_model(emb, hidden):
    import torch
    import torch.nn as nn

    class Repr(nn.Module):
        def __init__(self):
            super().__init__()
            self.conv = nn.Sequential(nn.Conv2d(N_PLANES, 32, 3, padding=1), nn.ReLU(),
                                      nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(),
                                      nn.Conv2d(64, 64, 3), nn.ReLU())             # 9 x 9
            self.centre = nn.Conv2d(64, 16, 1)                                     # centre 5 x 5 kept spatially
            self.fc = nn.Sequential(nn.Linear(16 * 25 + 128 + len(SCALARS), 128), nn.ReLU(), nn.Linear(128, emb), nn.Tanh())
            self.gru = nn.GRU(emb, hidden, batch_first=True)
            self.heads = nn.Linear(emb + hidden, 3 + 1 + 1 + 1)

        def embed(self, x, s):
            c = self.conv(x)
            mid = torch.relu(self.centre(c[:, :, 2:7, 2:7])).flatten(1)
            pooled = torch.cat([c.mean((2, 3)), c.amax((2, 3))], 1)
            return self.fc(torch.cat([mid, pooled, s], 1))

        def forward(self, x, s, B, T, h0=None):
            e = self.embed(x, s).view(B, T, -1)
            h, hn = self.gru(e, h0)
            z = torch.cat([e, h], 2)
            return self.heads(z), z, hn
    return Repr()


def targets(g, rows):
    H, Y = g['H'][rows], g['Y'][rows]
    rel = (H[:, 12] - H[:, 7]) % 4
    k = np.full(len(rows), -100, np.int64)
    ok = (H[:, 11] == 0) & (H[:, 13] == 1) & ((H[:, 14] & 1) == 0)
    k[ok & (rel == 0)] = 0; k[ok & (rel == 1)] = 1; k[ok & (rel == 3)] = 2
    i = D.YCOLS.index('dlen_20')
    ret = Y[:, i] + 3.0 * Y[:, i + 1]
    return k, ret.astype(np.float32), Y[:, i + 2].astype(np.float32), Y[:, i + 3].astype(np.float32)


def cmd_fit(a):
    import torch
    import torch.nn.functional as F
    dev = 'cuda'
    games = load_games(a.data, limit=a.limit)
    T = a.chunk
    chunks = {True: [], False: []}   # held-out? -> (game index, row indices [T])
    for gi, g in enumerate(games):
        for seq in sequences(g):
            for i in range(0, len(seq), T):
                c = seq[i:i + T]
                if len(c) >= 4:
                    chunks[g['fold'] == 0].append((gi, c))
    print(f'games {len(games)} (held-out {sum(g["fold"] == 0 for g in games)}), chunks {len(chunks[False])} / {len(chunks[True])}', flush=True)
    model = make_model(a.emb, a.hidden).to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=1e-4)
    rng = np.random.default_rng(C.SEED)

    def batch(items):
        B = len(items)
        V = np.zeros((B, T, D.VIEW_C, D.VIEW_N, D.VIEW_N), np.uint8)
        S = np.zeros((B, T, len(SCALARS)), np.float32)
        K = np.full((B, T), -100, np.int64)
        R = np.zeros((B, T), np.float32); Dd = np.zeros((B, T), np.float32); Bd = np.zeros((B, T), np.float32)
        M = np.zeros((B, T), np.float32)
        for b, (gi, c) in enumerate(items):
            g = games[gi]; n = len(c)
            V[b, :n] = g['V'][c]; S[b, :n] = g['S'][c]
            K[b, :n], R[b, :n], Dd[b, :n], Bd[b, :n] = targets(g, c)
            M[b, :n] = 1
        return V, S, K, R, Dd, Bd, M

    def run(items, train):
        V, S, K, R, Dd, Bd, M = batch(items)
        B = len(items)
        x = planes(V.reshape(B * T, *V.shape[2:]), dev)
        s = torch.as_tensor(S.reshape(B * T, -1), device=dev)
        out, _, _ = model(x, s, B, T)
        out = out.view(B * T, -1)
        m = torch.as_tensor(M.reshape(-1), device=dev)
        k = torch.as_tensor(K.reshape(-1), device=dev)
        r = torch.as_tensor(R.reshape(-1), device=dev); d = torch.as_tensor(Dd.reshape(-1), device=dev)
        bd = torch.as_tensor(Bd.reshape(-1), device=dev)
        l_pol = F.cross_entropy(out[:, :3], k, ignore_index=-100)
        l_ret = (F.smooth_l1_loss(out[:, 3], r / 4.0, reduction='none') * m).sum() / m.sum()
        l_die = (F.binary_cross_entropy_with_logits(out[:, 4], d, reduction='none') * m).sum() / m.sum()
        l_bed = (F.smooth_l1_loss(out[:, 5], bd / 2.0, reduction='none') * m).sum() / m.sum()
        loss = l_pol + l_ret + l_die + l_bed
        if train:
            opt.zero_grad(); loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
        acc = ((out[:, :3].argmax(1) == k) & (k >= 0)).sum().item() / max(1, (k >= 0).sum().item())
        return [l_pol.item(), l_ret.item(), l_die.item(), l_bed.item(), acc]

    hist = []
    t0 = time.time()
    for ep in range(a.epochs):
        model.train()
        idx = rng.permutation(len(chunks[False]))
        tr = []
        for i in range(0, len(idx) - a.batch + 1, a.batch):
            tr.append(run([chunks[False][j] for j in idx[i:i + a.batch]], True))
        model.eval()
        te = []
        with torch.no_grad():
            for i in range(0, len(chunks[True]), a.batch):
                te.append(run(chunks[True][i:i + a.batch], False))
        row = dict(epoch=ep, train=np.mean(tr, 0).round(4).tolist(), test=np.mean(te, 0).round(4).tolist(),
                   sec=round(time.time() - t0))
        hist.append(row)
        print(json.dumps(row), flush=True)
    out = C.MODELS / a.name
    out.mkdir(parents=True, exist_ok=True)
    torch.save(dict(state=model.state_dict(), emb=a.emb, hidden=a.hidden), out / 'repr.pt')
    (out / 'meta.json').write_text(json.dumps(dict(name=a.name, data=a.data, emb=a.emb, hidden=a.hidden,
                                                    chunk=T, history=hist, columns=['pol', 'ret', 'die', 'bed', 'acc']), indent=1))


def load_model(name):
    import torch
    ck = torch.load(C.MODELS / name / 'repr.pt', map_location='cuda')
    m = make_model(ck['emb'], ck['hidden']).to('cuda')
    m.load_state_dict(ck['state'])
    m.eval()
    return m, ck['emb'] + ck['hidden']


def embed_game(model, g, dim, step=4096):
    """full-sequence forward pass per dragon -> [n rows, dim] (embedding + recurrent state at each turn)"""
    import torch
    E = np.zeros((len(g['H']), dim), np.float32)
    with torch.no_grad():
        for seq in sequences(g):
            h = None
            for i in range(0, len(seq), step):
                c = seq[i:i + step]
                x = planes(g['V'][c], 'cuda')
                s = torch.as_tensor(g['S'][c], device='cuda')
                _, z, h = model(x, s, 1, len(c), h)
                E[c] = z[0].cpu().numpy()
    return E


def cmd_embed(a):
    model, dim = load_model(a.name)
    games = load_games(a.data, limit=a.limit)
    for g in games:
        np.save(Path(g['path']).with_suffix(f'.emb-{a.name}.npy'), embed_game(model, g, dim))
    print(f'embedded {len(games)} games, dim {dim}')


def cmd_probe(a):
    """Linear probes (ridge / logistic on the frozen state) for quantities the hand-built state carries:
    enclosure (room of the forward step, tF_reach8), food density (tF_food8, s_pearls_known), mode (a_why)."""
    from sklearn.linear_model import Ridge, LogisticRegression
    from sklearn.preprocessing import StandardScaler
    model, dim = load_model(a.name)
    games = load_games(a.data, limit=a.limit)
    _, names = C.schema()
    probes = ['tF_reach8', 'tF_food8', 's_pearls_known', 'tF_corr_len', 's_beds_known', 'tF_pearl_d', 's_since_enemy']
    E, P, W, te = [], [], [], []
    for g in games:
        e = embed_game(model, g, dim)
        z = np.load(g['path'])
        sub = np.random.default_rng(1).choice(len(e), min(len(e), 3000), replace=False)
        E.append(e[sub]); P.append(z['X'][sub][:, [names.index(p) for p in probes]])
        W.append(z['X'][sub][:, names.index('a_why')]); te.append(np.full(len(sub), g['fold'] == 0))
    E, P, W, te = np.concatenate(E), np.concatenate(P), np.concatenate(W), np.concatenate(te)
    sc = StandardScaler().fit(E[~te])
    Etr, Ete = sc.transform(E[~te]), sc.transform(E[te])
    res = {}
    for j, p in enumerate(probes):
        y = np.clip(P[:, j], -1, 99)
        m = Ridge(alpha=1.0).fit(Etr, y[~te])
        res[p] = dict(r2=float(m.score(Ete, y[te])))
    m = LogisticRegression(max_iter=300).fit(Etr, W[~te].astype(int))
    res['a_why'] = dict(acc=float(m.score(Ete, W[te].astype(int))),
                        majority=float(np.bincount(W[te].astype(int)).max() / te.sum()))
    (C.MODELS / a.name / 'probes.json').write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    for c in ('fit', 'embed', 'probe'):
        p = sub.add_parser(c)
        p.add_argument('--name', required=True); p.add_argument('--data', required=True)
        p.add_argument('--limit', type=int, default=0)
        if c == 'fit':
            p.add_argument('--epochs', type=int, default=6); p.add_argument('--hidden', type=int, default=96)
            p.add_argument('--emb', type=int, default=64); p.add_argument('--chunk', type=int, default=32)
            p.add_argument('--batch', type=int, default=128); p.add_argument('--lr', type=float, default=1e-3)
    a = ap.parse_args()
    {'fit': cmd_fit, 'embed': cmd_embed, 'probe': cmd_probe}[a.cmd](a)


if __name__ == '__main__':
    main()
