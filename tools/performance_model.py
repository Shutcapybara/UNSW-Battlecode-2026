"""Regularized expected-score model with a skew-symmetric matchup interaction.

logit E[score(A)] = s[A]-s[B] + t[A,map]-t[B,map] + b[map]
                   + U[A]·V[B] - V[A]·U[B].
Draws contribute score 0.5; this is fractional logistic loss, not a draw model.
Missing matches contribute no loss. Positive ridge penalties regularize sparse
entrants. s is general strength, t map affinity, b initiative, UV matchup cycles.
"""
import numpy as np
from scipy.optimize import minimize
from scipy.special import expit


def unpack(x, n, m, q, maps=True):
    offset = n
    s = x[:n]
    t = x[offset:offset+n*m].reshape(n, m) if maps else np.zeros((n, m))
    offset += n*m if maps else 0
    b = x[offset:offset+m]
    offset += m
    u = x[offset:offset+n*q].reshape(n, q)
    v = x[offset+n*q:].reshape(n, q)
    return s, t, b, u, v


def logits(x, data, n, m, q, maps=True):
    a, c, board, _ = data
    s, t, b, u, v = unpack(x, n, m, q, maps)
    return s[a]-s[c] + t[a, board]-t[c, board] + b[board] + (u[a]*v[c]-v[a]*u[c]).sum(axis=1)


def objective(x, data, n, m, q, maps=True, ridge=5.):
    a, c, board, y = data
    s, t, b, u, v = unpack(x, n, m, q, maps)
    z = logits(x, data, n, m, q, maps)
    loss = np.sum(np.logaddexp(0, z)-y*z)
    error = expit(z)-y
    ds = np.bincount(a, error, minlength=n)-np.bincount(c, error, minlength=n)
    db = np.bincount(board, error, minlength=m)
    gradients = [ds + .2*s]
    loss += .1*np.sum(s*s) + .5*np.sum(b*b)
    if maps:
        dt = (np.bincount(a*m+board, error, minlength=n*m)-
              np.bincount(c*m+board, error, minlength=n*m)).reshape(n, m)
        gradients.append((dt+ridge*t).ravel())
        loss += .5*ridge*np.sum(t*t)
    gradients.append(db+b)
    du, dv = np.zeros_like(u), np.zeros_like(v)
    for k in range(q):
        du[:, k] = np.bincount(a, error*v[c,k], minlength=n)-np.bincount(c, error*v[a,k], minlength=n)
        dv[:, k] = np.bincount(c, error*u[a,k], minlength=n)-np.bincount(a, error*u[c,k], minlength=n)
    # Each coordinate pair contributes rank at most two to the skew matrix.
    loss += .5*ridge*(np.sum(u*u)+np.sum(v*v))
    gradients += [(du+ridge*u).ravel(), (dv+ridge*v).ravel()]
    return loss/len(y), np.concatenate(gradients)/len(y)


def fit(data, n, m, q=0, maps=True, ridge=5., seed=42, start=None):
    size = n + (n*m if maps else 0) + m + 2*n*q
    x = np.zeros(size)
    if start is not None:
        if start['q'] == q and start['maps'] == maps:
            x[:] = start['x']
        ss, tt, bb, _, _ = unpack(start['x'], n, m, start['q'], start['maps'])
        s, t, b, _, _ = unpack(x, n, m, q, maps)
        s[:] = ss
        if maps:
            t[:] = tt
        b[:] = bb
    if q and (start is None or start['q'] != q or start['maps'] != maps):
        x[-2*n*q:] = np.random.default_rng(seed).normal(0, .1, 2*n*q)
    result = minimize(objective, x, args=(data,n,m,q,maps,ridge), jac=True, method="L-BFGS-B",
                      options=dict(maxiter=450, ftol=1e-10, gtol=1e-6, maxcor=15))
    return dict(x=result.x, q=q, maps=maps, ridge=ridge, success=bool(result.success),
                iterations=int(result.nit), objective=float(result.fun), message=str(result.message))


def predictions(model, data, n, m):
    return expit(logits(model['x'], data, n, m, model['q'], model['maps']))


def metrics(y, p):
    p = np.clip(p, 1e-9, 1-1e-9)
    decisive = y != .5
    return dict(log_loss=float(np.mean(-y*np.log(p)-(1-y)*np.log1p(-p))),
                brier=float(np.mean((p-y)**2)),
                decisive_accuracy=float(np.mean((p[decisive] >= .5) == (y[decisive] > .5))))


def subset(data, mask):
    return tuple(v[mask] for v in data)
