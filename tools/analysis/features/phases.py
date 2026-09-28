"""Phase detection per side-game (F1 feature lab).

Three views of 'opening exploration -> mid-game economic churn -> endgame crown race':
  rules     t1 = first round after the discovery peak where the 10-round mean of newly seen cells falls below 25% of
            its peak; t2 = first round after t1 by which 90% of the side's splits are done AND the 10-round mean of
            top1_share is above its game median (production stops, length concentrates). Missing = None.
  segments  exact least-squares segmentation (dynamic programming) of the standardised signal vector on 5-round
            bins into K+1 segments; K chosen by a BIC-style penalty (0..4), and the K=2 fit reported separately.
  labels    each K=2 segment gets the phase name whose signature it matches best (explore high -> opening,
            production/eat high -> economy, concentration high + production low -> crown).
Signals (per side, per round, all rates per living dragon so map size and population cancel):
  explore = new cells seen / (49 * units); produce = splits / units; eat = pearls / units;
  contact = share of dragons with an enemy in view; die = deaths / units; concentrate = top1_share
"""
import math
import numpy as np

SIGNALS = ('explore', 'produce', 'eat', 'contact', 'die', 'concentrate')
BIN = 5
MIN_SEG = 4  # bins (20 rounds)


def signals(df):
    """df: series rows of one side-game sorted by round -> dict of numpy arrays (length R)"""
    u = np.maximum(df['units'].to_numpy(float), 1)
    alive = df['units'].to_numpy(float) > 0
    get = lambda c: df[c].to_numpy(float) if c in df else np.zeros(len(df))
    out = dict(explore=get('new_seen') / (49 * u), produce=get('splits') / u, eat=get('eats') / u,
               contact=np.nan_to_num(get('contact_share')), die=get('deaths') / u,
               concentrate=np.nan_to_num(get('top1_share'), nan=1.0))
    for k in out:
        out[k] = np.where(alive, out[k], np.nan)
    return out


def smooth(x, w=10):
    x = np.nan_to_num(x)
    k = np.ones(w) / w
    return np.convolve(x, k, mode='full')[:len(x)]


def rule_phases(sig):
    ex = smooth(sig['explore'])
    n = len(ex)
    if n < 20 or ex.max() <= 0:
        return None, None
    peak = int(np.argmax(ex))
    below = np.where(ex[peak:] < 0.25 * ex[peak])[0]
    t1 = int(peak + below[0]) if len(below) else None
    prod = np.nan_to_num(sig['produce'])
    cs = np.cumsum(prod)
    t2 = None
    if t1 is not None and cs[-1] > 0:
        conc = smooth(sig['concentrate'])
        med = np.median(conc[t1:]) if n > t1 else np.inf
        done = np.where((cs >= 0.9 * cs[-1]) & (np.arange(n) > t1) & (conc >= med))[0]
        t2 = int(done[0]) if len(done) and done[0] < n - 10 else None
    return t1, t2


def binned(sig, scale):
    R = len(next(iter(sig.values())))
    nb = R // BIN
    if nb < 2 * MIN_SEG:
        return None
    X = np.stack([np.nan_to_num((np.nanmean(sig[k][:nb * BIN].reshape(nb, BIN), axis=1) - scale[k][0]) / scale[k][1])
                  for k in SIGNALS], axis=1)
    return X


def segment(X, K):
    """exact least-squares segmentation into K+1 pieces; returns (cost, breakpoints in bins)"""
    n = len(X)
    cs = np.vstack([np.zeros((1, X.shape[1])), np.cumsum(X, 0)])
    cs2 = np.concatenate([[0], np.cumsum((X ** 2).sum(1))])

    def cost(i, j):  # [i, j)
        m = j - i
        s = cs[j] - cs[i]
        return (cs2[j] - cs2[i]) - (s @ s) / m

    INF = float('inf')
    D = np.full((K + 1, n + 1), INF)
    B = np.zeros((K + 1, n + 1), int)
    for j in range(MIN_SEG, n + 1):
        D[0, j] = cost(0, j)
    for k in range(1, K + 1):
        for j in range((k + 1) * MIN_SEG, n + 1):
            best, arg = INF, 0
            for i in range(k * MIN_SEG, j - MIN_SEG + 1):
                c = D[k - 1, i] + cost(i, j)
                if c < best:
                    best, arg = c, i
            D[k, j], B[k, j] = best, arg
    if not np.isfinite(D[K, n]):
        return INF, []
    bps, j = [], n
    for k in range(K, 0, -1):
        j = B[k, j]
        bps.append(j)
    return D[K, n], sorted(bps)


def label_segments(X, bps):
    idx = [0] + list(bps) + [len(X)]
    names = []
    for a, b in zip(idx, idx[1:]):
        m = X[a:b].mean(0)
        d = dict(zip(SIGNALS, m))
        score = dict(opening=d['explore'], economy=d['produce'] + d['eat'] - d['explore'] * 0.5,
                     crown=d['concentrate'] - d['produce'])
        names.append(max(score, key=score.get))
    return names


def detect(df, scale, max_k=4, penalty=None):
    sig = signals(df)
    t1, t2 = rule_phases(sig)
    row = dict(rule_t1=t1, rule_t2=t2)
    X = binned(sig, scale)
    if X is None:
        return row
    n, d = X.shape
    pen = penalty if penalty is not None else 2 * d * math.log(n)
    best = None
    costs = {}
    for K in range(0, max_k + 1):
        c, bps = segment(X, K)
        costs[K] = c
        if not math.isfinite(c):
            continue
        score = c + pen * K
        if best is None or score < best[0]:
            best = (score, K, bps)
    row['cp_k'] = best[1] if best else None
    c2, bps2 = segment(X, 2)
    if bps2:
        row['cp_t1'], row['cp_t2'] = bps2[0] * BIN, bps2[1] * BIN
        labs = label_segments(X, bps2)
        row['cp_labels'] = '-'.join(labs)
        row['cp_gain_2'] = 1 - c2 / costs[0] if costs[0] > 0 else float('nan')
    c1, bps1 = segment(X, 1)
    if bps1:
        row['cp1_t'] = bps1[0] * BIN
    return row


def pooled_scale(series):
    """mean/std of each signal over all alive side-rounds of a corpus (so segmentation is comparable across games)"""
    acc = {k: [] for k in SIGNALS}
    for _, df in series.groupby(['game', 'side']):
        s = signals(df.sort_values('round'))
        for k in SIGNALS:
            acc[k].append(s[k][~np.isnan(s[k])])
    out = {}
    for k, v in acc.items():
        v = np.concatenate(v)
        out[k] = (float(v.mean()), float(v.std() or 1.0))
    return out


# ---------------- left-to-right 3-state HMM, fitted pooled over a corpus ----------------
STATES = ('opening', 'economy', 'crown')
# contact is left out of the HMM: it is mostly fixed by map layout (compact maps are in contact from the start), and with it
# the third state became 'fighting' rather than 'crown race'. Without it the third state is high concentration + low production.
HMM_SIGNALS = ('explore', 'produce', 'eat', 'die', 'concentrate')


def hmm_view(X):
    return X[:, [SIGNALS.index(k) for k in HMM_SIGNALS]]


def _logemit(X, mu, var):
    # X (n,d); mu,var (S,d) -> (n,S)
    return -0.5 * (((X[:, None, :] - mu[None]) ** 2) / var[None] + np.log(2 * np.pi * var[None])).sum(-1)


def _fb(le, logA, logpi):
    n, S = le.shape
    la = np.full((n, S), -np.inf)
    lb = np.zeros((n, S))
    la[0] = logpi + le[0]
    for t in range(1, n):
        la[t] = np.logaddexp.reduce(la[t - 1][:, None] + logA, axis=0) + le[t]
    for t in range(n - 2, -1, -1):
        lb[t] = np.logaddexp.reduce(logA + (le[t + 1] + lb[t + 1])[None], axis=1)
    ll = np.logaddexp.reduce(la[-1])
    g = np.exp(la + lb - ll)
    xi = np.zeros((S, S))
    for t in range(n - 1):
        m = la[t][:, None] + logA + (le[t + 1] + lb[t + 1])[None] - ll
        xi += np.exp(m)
    return ll, g, xi


def _viterbi(le, logA, logpi):
    n, S = le.shape
    d = logpi + le[0]
    bp = np.zeros((n, S), int)
    for t in range(1, n):
        m = d[:, None] + logA
        bp[t] = m.argmax(0)
        d = m.max(0) + le[t]
    path = [int(d.argmax())]
    for t in range(n - 1, 0, -1):
        path.append(int(bp[t][path[-1]]))
    return path[::-1]


def fit_hmm(seqs, inits, iters=25):
    """seqs: list of (n,d) arrays; inits: list of state paths used to initialise emissions"""
    d = seqs[0].shape[1]
    S = 3
    Xall = np.concatenate(seqs)
    pall = np.concatenate(inits)
    mu = np.stack([Xall[pall == s].mean(0) if (pall == s).any() else Xall.mean(0) for s in range(S)])
    var = np.stack([Xall[pall == s].var(0) + 1e-2 if (pall == s).sum() > 1 else Xall.var(0) + 1e-2 for s in range(S)])
    A = np.array([[0.9, 0.09, 0.01], [0, 0.95, 0.05], [0, 0, 1.0]])
    pi = np.array([0.9, 0.08, 0.02])
    hist = []
    for it in range(iters):
        logA = np.log(np.where(A > 0, A, 1e-300))
        logpi = np.log(pi + 1e-300)
        G, XI, P0, tot = [], np.zeros((S, S)), np.zeros(S), 0.0
        for X in seqs:
            ll, g, xi = _fb(_logemit(X, mu, var), logA, logpi)
            tot += ll
            G.append(g)
            XI += xi
            P0 += g[0]
        hist.append(tot)
        Gall = np.concatenate(G)
        w = Gall.sum(0)
        mu = (Gall.T @ Xall) / w[:, None]
        var = np.stack([(Gall[:, s:s + 1] * (Xall - mu[s]) ** 2).sum(0) / w[s] for s in range(S)]) + 1e-2
        A = XI / XI.sum(1, keepdims=True)
        A = np.triu(A)            # left-to-right only
        A = A / A.sum(1, keepdims=True)
        pi = P0 / P0.sum()
        if it > 2 and abs(hist[-1] - hist[-2]) < 1e-4 * abs(hist[-1]):
            break
    return dict(mu=mu, var=var, A=A, pi=pi, loglik=hist)


def decode_hmm(model, X):
    logA = np.log(np.where(model['A'] > 0, model['A'], 1e-300))
    path = _viterbi(_logemit(X, model['mu'], model['var']), logA, np.log(model['pi'] + 1e-300))
    t1 = next((i for i, s in enumerate(path) if s >= 1), None)
    t2 = next((i for i, s in enumerate(path) if s >= 2), None)
    return path, (t1 * BIN if t1 is not None else None), (t2 * BIN if t2 is not None else None)


def rule_path(n_bins, t1, t2):
    p = np.zeros(n_bins, int)
    if t1 is not None:
        p[t1 // BIN:] = 1
    if t2 is not None:
        p[t2 // BIN:] = 2
    return p
