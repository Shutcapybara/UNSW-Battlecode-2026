"""H-SZ34: head-on deaths after r150 in simulator replays: mutual share, victim-vs-killer length, corpse pearls taken by the killer side."""
import sys, glob, collections; sys.path.insert(0, '/home/claude/fr'); import frame
c = collections.Counter(); dl = collections.Counter()
for f in sorted(glob.glob(sys.argv[1])):
    g = frame.decode(f); R = g['last_round']
    for d in g['events']['deaths']:
        if d['round'] < 150: continue
        c['deaths'] += 1; c['d_' + d['cause']] += 1
        if d['cause'] != 'h2h' or d['killer'] is None: continue
        if d.get('mutual'): c['mutual'] += 1; continue
        k = d['killer']; r = min(d['round'], R); rk = g['rounds'][max(0, r - 1)]
        kl = len(rk[k][1]) if k in rk else None; vl = d['length']
        if kl is None: continue
        c['oneway'] += 1; dl['victim_shorter' if vl < kl else ('equal' if vl == kl else 'victim_longer')] += 1
        c['vlen'] += vl; c['klen'] += kl
print(dict(c)); print(dict(dl)); print('mean victim/killer len', round(c['vlen']/max(1,c['oneway']),2), round(c['klen']/max(1,c['oneway']),2))
# trade ledger: for each head-on pair (mover = mutual actor, partner = its victim) after r150, corpse pearls born from each
# and who eats them within 50 rounds (mover team / partner team / nobody).
led = collections.Counter()
for f in sorted(glob.glob(sys.argv[1])):
    g = frame.decode(f); R = g['last_round']
    dd = {d['id']: d for d in g['events']['deaths']}
    ebc = collections.defaultdict(list)
    for e in g['events']['eats']: ebc[tuple(e['cell'])].append((e['round'], e['team']))
    for v in ebc.values(): v.sort()
    born = collections.defaultdict(list)
    for s in g['events']['spawns']:
        if s['origin'] in ('A', 'B') and s.get('donor') is not None: born[s['donor']].append(s)
    for d in g['events']['deaths']:
        if d['cause'] != 'h2h' or not d.get('mutual') or d['round'] < 150 or d['round'] > R - 50: continue
        mt = d['team']; pt = d['killer_team']
        if mt == pt: led['ally_pair'] += 1; continue
        led['pairs'] += 1; led['mover_len'] += d['length']; led['partner_len'] += dd[d['killer']]['length'] if d['killer'] in dd else 0
        for who, did in (('m', d['id']), ('p', d['killer'])):
            for s in born.get(did, []):
                lst = ebc.get(tuple(s['cell']), []); j = next((x for x in lst if x[0] >= s['round']), None)
                tag = 'none' if j is None or j[0] > s['round'] + 50 else ('mover' if j[1] == mt else 'partner')
                led[f'{who}_born'] += 1; led[f'{who}_to_{tag}'] += 1
print(dict(led))
