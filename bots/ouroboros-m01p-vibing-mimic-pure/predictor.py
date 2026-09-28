"""Dependency-free inference for an exported HistGradientBoosting model."""
import json


class Predictor:
    def __init__(self, path):
        d = json.load(open(path))
        self.features, self.classes, self.base = d['features'], d['classes'], d['baseline']
        self.model_classes = d['model_classes']
        # flatten: for each iteration, list per class of (f,t,l,r,leaf,v,m)
        self.trees = [[(t['f'], t['t'], t['l'], t['r'], t['leaf'], t['v'], t['m']) for t in it] for it in d['trees']]
        self.k = len(self.base)

    def raw(self, x):
        s = list(self.base)
        for it in self.trees:
            for c, (f, t, l, r, leaf, v, m) in enumerate(it):
                i = 0
                while not leaf[i]:
                    xv = x[f[i]]
                    if xv != xv:
                        i = l[i] if m[i] else r[i]
                    elif xv <= t[i]:
                        i = l[i]
                    else:
                        i = r[i]
                s[c] += v[i]
        return s

    def proba(self, row):
        import math
        x = [row.get(f, float('nan')) for f in self.features]
        s = self.raw(x)
        if self.k == 1:
            p1 = 1 / (1 + math.exp(-s[0]))
            return {self.classes[self.model_classes[0]]: 1 - p1, self.classes[self.model_classes[1]]: p1}
        mx = max(s)
        e = [math.exp(v - mx) for v in s]
        z = sum(e)
        return {self.classes[self.model_classes[c]]: e[c] / z for c in range(self.k)}
