"""Replay a mimic game offline: recompute v4 features from rebuilt blocks and the bot's decision rule;
compare with the actions the bot actually took.  python3 clone_parity.py REPLAY SIDE MODEL [guarded|pure]"""
import sys, json, collections
sys.path.insert(0, '/home/claude/w/tools')
import features_v4, export_hgb
rep, side, model = sys.argv[1:4]
mode = sys.argv[4] if len(sys.argv) > 4 else 'guarded'
rows, g = features_v4.extract(rep, side, 0)
pr = export_hgb.Predictor(model)
c = collections.Counter(); ex = []
for r in rows:
    p = pr.proba(r)
    if r['length'] < 4 or r['units'] >= r['unit_limit']:
        p['split'] = 0.0
    if mode == 'guarded':
        for rel in 'FRL':
            if r['c%s_block' % rel] in {1, 2, 3, 4, 5, 6}:
                p[rel] = 0.0
        if max(p[x] for x in 'FRL') == 0 and p['split'] == 0:
            p['suicide'] = 1.0
    ch = max(p, key=p.get)
    got = r['y_first'] if r['y_family'] in ('move', 'split') else r['y_family']
    if got == 'split' and r['y_split'] == 1:
        got = 'suicide'
    ok = ch == got
    c['match' if ok else 'mismatch'] += 1
    if not ok and len(ex) < 5:
        ex.append((r['round'], r['dragon'], ch, got))
print(json.dumps(dict(c)), ex)
