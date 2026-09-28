"""Stage-2 evaluation of frame tables against v32 on identical fixtures.
A table maps (map, seat) -> frame; frame 'id' games are the v32 control games themselves (the wrapper in the id frame is
exactly v32), other frames use jet-f32-<frame> or jet-f32-P rows for the same fixture.
usage: frame_eval.py RESULTS[,RESULTS...]"""
import collections, json, sys
rows = {}
for f in sys.argv[1].split(','):
    for l in open(f):
        r = json.loads(l)
        if 'score' in r: rows[r['key']] = r
CTRL = 'gavroche-v32-supported-divecap'
XY = dict(default='r', portals='r', dilemma='r', devil='r', queen_of_spades='r', autarky='r', trauma='r', slithery_fight='r', trophy='fx', schooltime='fx')
TABLES = {
    'P': {(m, 'B'): f for m, f in XY.items()},
    'S': {('portals', 'B'): 'r', ('dilemma', 'B'): 'r', ('devil', 'B'): 'r', ('autarky', 'B'): 'r', ('queen_of_spades', 'B'): 'r',
          ('trauma', 'B'): 'fx', ('schooltime', 'A'): 'r', ('slithery_fight', 'A'): 'fx'},
}
opps = sorted({r['opp'] for r in rows.values() if r['arm'] == CTRL})
maps = sorted({r['map'] for r in rows.values() if r['arm'] == CTRL})
for name, tab in TABLES.items():
    tot_c = tot_t = n = 0; miss = []; per = collections.defaultdict(lambda: [0, 0, 0]); flips = [0, 0]
    for m in maps:
        for o in opps:
            for s in 'AB':
                c = rows.get(f'{CTRL}|{o}|{m}|{s}')
                if c is None: miss.append(('ctrl', m, o, s)); continue
                fr = tab.get((m, s), 'id')
                if fr == 'id': t = c
                else:
                    t = rows.get(f'jet-f32-{fr}|{o}|{m}|{s}')
                    if t is None and TABLES['P'].get((m, s)) == fr: t = rows.get(f'jet-f32-P|{o}|{m}|{s}')
                if t is None: miss.append((fr, m, o, s)); continue
                tot_c += c['score']; tot_t += t['score']; n += 1
                per[m][0] += c['score']; per[m][1] += t['score']; per[m][2] += 1
                if t['score'] > c['score']: flips[0] += 1
                elif t['score'] < c['score']: flips[1] += 1
    print(f"== table {name}: {tot_t} vs control {tot_c} of {n} fixtures (up {flips[0]} / down {flips[1]}); missing {len(miss)}")
    print('   ' + ', '.join(f"{m} {v[1]:.0f}/{v[0]:.0f} of {v[2]}" for m, v in sorted(per.items())))
    if miss: print('   missing e.g.', miss[:6])
