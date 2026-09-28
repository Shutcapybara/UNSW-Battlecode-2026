#!/usr/bin/env python3
"""Score Yuna plans from the global results file.
python3 tools/yuna/yscore.py plan.json results.jsonl [--base CAND] [--by map|opp] [--ck 50,100]"""
import argparse, json, collections
def load(plan, res):
    fx = json.load(open(plan))['fixtures']
    rows = {}
    for line in open(res):
        try: r = json.loads(line)
        except Exception: continue
        if r.get('outcome') in ('W', 'L', 'D'): rows[r['id']] = r
    return fx, rows
def pts(o): return {'W': 1.0, 'D': 0.5, 'L': 0.0}[o]
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('plan'); ap.add_argument('res')
    ap.add_argument('--base'); ap.add_argument('--by', default='map'); ap.add_argument('--ck', default='50,100,300')
    a = ap.parse_args(); fx, rows = load(a.plan, a.res)
    cands = list(dict.fromkeys(f['cand'] for f in fx))
    tab = collections.defaultdict(lambda: collections.defaultdict(list))
    ck = collections.defaultdict(lambda: collections.defaultdict(list))
    how = collections.defaultdict(collections.Counter)
    key = {}
    CK = {}
    for f in fx:
        r = rows.get(f['id'])
        if not r: continue
        o = pts(r['outcome']); tab[f['cand']][f[a.by]].append(o); tab[f['cand']]['ALL'].append(o)
        key[(f['cand'], f['opp'], f['map'], f['side'])] = o
        cps = (r.get('stats') or {}).get('checkpoints') or {}
        me_ = f['side']
        for c_ in ('100', '200'):
            p_ = cps.get(c_)
            if p_ and me_ in p_: CK[(f['cand'], f['opp'], f['map'], f['side'], c_)] = (p_[me_].get('pearls') or 0, p_[me_].get('total') or 0, p_[me_].get('units') or 0)
        fin = (r.get('stats') or {}).get('final') or {}
        if me_ in fin: CK[(f['cand'], f['opp'], f['map'], f['side'], 'fin')] = (fin[me_].get('longest', 0), fin[me_].get('total', 0), fin[me_].get('units', 0))
        how[f['cand']][r['outcome'] + ':' + (r.get('how') or '?')[:5]] += 1
        st = r.get('stats') or {}
        me = f['side']; them = 'B' if me == 'A' else 'A'
        for c in a.ck.split(','):
            p = (st.get('checkpoints') or {}).get(c)
            if p and me in p and them in p:
                for k in ('units', 'total', 'longest', 'pearls'):
                    ck[f['cand']][c + k].append((p[me].get(k) or 0) - 0)
                    ck[f['cand']][c + k + '_opp'].append((p[them].get(k) or 0))
    groups = sorted({g for c in tab for g in tab[c]} - {'ALL'}) + ['ALL']
    w = max(len(c) for c in cands)
    print(' ' * w, *[g[:9].rjust(9) for g in groups])
    for c in cands:
        cells = []
        for g in groups:
            v = tab[c].get(g, [])
            cells.append(f'{sum(v):.0f}/{len(v)}'.rjust(9) if v else '-'.rjust(9))
        print(c.ljust(w), *cells)
    print()
    for c in cands:
        print(c.ljust(w), dict(how[c]))
        print(' ' * w, ' '.join(f'{k}={sum(v)/len(v):.1f}' for k, v in sorted(ck[c].items()) if not k.endswith('_opp') and v))
        print(' ' * w, ' opp:', ' '.join(f'{k[:-4]}={sum(v)/len(v):.1f}' for k, v in sorted(ck[c].items()) if k.endswith('_opp') and v))
    if a.base:
        for c in cands:
            if c == a.base: continue
            d = []; flips = collections.Counter()
            for (cc, o, m, s), v in key.items():
                if cc != c: continue
                b = key.get((a.base, o, m, s))
                if b is None: continue
                d.append(v - b)
                if v != b: flips[(m, 'up' if v > b else 'down')] += 1
            for c_ in ('100', '200', 'fin'):
                ds = [tuple(x - y for x, y in zip(v, CK[(a.base,) + k[1:]])) for k, v in CK.items() if k[0] == c and k[4] == c_ and (a.base,) + k[1:] in CK]
                if ds: print(f'   paired {c_} ({len(ds)}): ' + ' '.join(f'{n}{sum(x[i] for x in ds)/len(ds):+.1f}' for i, n in enumerate(('pearls/longest ', 'total ', 'units '))))
            if d:
                print(f'{c} vs {a.base}: paired n={len(d)} delta={sum(d):+.1f} ({100*sum(d)/len(d):+.1f} pp)  up={sum(1 for x in d if x>0)} down={sum(1 for x in d if x<0)}')
                print('   flips by map:', dict(sorted(flips.items())))
if __name__ == '__main__': main()
