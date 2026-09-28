"""win ~ stage statistics: L2-regularised logistic regression over panel games.

  winmodel.py DIR [DIR...] [--diff]

One row per game from the candidate arm's side (all arms, all opponents, both
sides).  Features are standardised; C is chosen by leave-one-map-out AUC.
--diff uses (ours - theirs) for the stage statistics instead of ours alone.
Reports coefficients (on standardised features), LOMO AUC, and the two
statistics that carry the prediction (best two-feature LOMO AUC).
"""
import argparse, itertools, sys
from pathlib import Path
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
sys.path.insert(0, str(Path(__file__).resolve().parent))
from panel import load

STAGE = [("units_r25", 25, 0), ("units_r50", 50, 0), ("units_r100", 100, 0), ("total_r250", 250, 1), ("longest_r400", 400, 2)]
CAUSES = ["wall", "self", "body", "h2h", "invalid"]


def feats(t, turns_norm=True):
    f = {}
    for name, st, i in STAGE:
        f[name] = t["at"][str(st)][i]
    k = max(1, t["turns"]) / 1000.0
    for c in CAUSES:
        f["deaths_%s_per1k" % c] = t["deaths"].get(c, 0) / k
    f["splits"] = t["splits"]
    f["newborn_deaths10"] = t["newborn10"]
    f["portal_steps"] = t["portal_steps"]
    f["sonar_rays"] = t["sonar"]
    return f


def lomo_auc(X, y, maps, C):
    p = np.zeros(len(y))
    for m in sorted(set(maps)):
        te = maps == m
        tr = ~te
        if len(set(y[tr])) < 2:
            return float("nan")
        mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-9
        clf = LogisticRegression(C=C, max_iter=2000).fit((X[tr] - mu) / sd, y[tr])
        p[te] = clf.predict_proba((X[te] - mu) / sd)[:, 1]
    return roc_auc_score(y, p)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("dirs", nargs="+"); ap.add_argument("--diff", action="store_true")
    ap.add_argument("--stage-only", action="store_true")
    ap.add_argument("--early", action="store_true", help="only units r25/r50/r100 (no end-of-game leakage)")
    ap.add_argument("--zmap", action="store_true", help="z-score each feature within its map (label-free)")
    a = ap.parse_args()
    rows = load(a.dirs)
    F = []
    for r in rows:
        f = feats(r["me"])
        if a.diff:
            g = feats(r["op"])
            f = {k: f[k] - g[k] for k in f}
        F.append(f)
    names = list(F[0])
    if a.early:
        names = ["units_r25", "units_r50", "units_r100"]
    if a.stage_only:
        names = [n for n in names if n in dict((s[0], 1) for s in STAGE)]
    X = np.array([[f[n] for n in names] for f in F], float)
    y = np.array([1 if r["res"] == "W" else 0 for r in rows])
    maps = np.array([r["map"] for r in rows])
    if a.zmap:
        for m in set(maps):
            k = maps == m
            X[k] = (X[k] - X[k].mean(0)) / (X[k].std(0) + 1e-9)
    print("games %d, wins %d (%.3f), features %d, %s" % (len(y), y.sum(), y.mean(), len(names), ("diff" if a.diff else "own") + (" zmap" if a.zmap else "")))
    best = max(((lomo_auc(X, y, maps, C), C) for C in (0.01, 0.03, 0.1, 0.3, 1.0)), key=lambda t: t[0])
    print("LOMO AUC %.3f at C=%g" % best)
    mu, sd = X.mean(0), X.std(0) + 1e-9
    clf = LogisticRegression(C=best[1], max_iter=2000).fit((X - mu) / sd, y)
    for n, c in sorted(zip(names, clf.coef_[0]), key=lambda t: -abs(t[1])):
        print("  %-24s %+.3f" % (n, c))
    singles = sorted(((lomo_auc(X[:, [i]], y, maps, 1.0), names[i]) for i in range(len(names))), reverse=True)
    print("single-feature LOMO AUC:", ", ".join("%s %.3f" % (n, v) for v, n in singles[:8]))
    pairs = []
    for i, j in itertools.combinations(range(len(names)), 2):
        pairs.append((lomo_auc(X[:, [i, j]], y, maps, 1.0), names[i], names[j]))
    pairs.sort(reverse=True)
    print("best two-feature LOMO AUC:", "; ".join("%s + %s %.3f" % (p[1], p[2], p[0]) for p in pairs[:5]))
