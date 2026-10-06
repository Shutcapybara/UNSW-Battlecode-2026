"""H-SZ34 head-on trade ledger (simulator replays). v2 (unit 16): lengths from the death records for both partners;
corpse pearls counted by event identity — spawns by donor id, eats by the eat event's own donor id (frame label), age <= 50.
Usage: szh2h.py 'glob' [botA_name_pos] -> per-bot partner/mover counts + pooled ledger."""
import sys, glob, collections; sys.path.insert(0, '/home/claude/fr'); import frame
led = collections.Counter(); per = collections.defaultdict(collections.Counter); causes = collections.Counter()
for f in sorted(glob.glob(sys.argv[1])):
    parts = f.split('/')[-1][:-7].split('_'); bots = {'A': parts[2], 'B': parts[3]}
    g = frame.decode(f); R = g['last_round']
    dd = {d['id']: d for d in g['events']['deaths']}
    born = collections.Counter(); eaten = collections.defaultdict(collections.Counter)
    for s in g['events']['spawns']:
        if s['origin'] in ('A', 'B') and s.get('donor') is not None: born[s['donor']] += 1
    for e in g['events']['eats']:
        if e.get('donor') is not None and e['origin'] != 'bed' and (e.get('age') or 0) <= 50: eaten[e['donor']][e['team']] += 1
    for t in 'AB': per[bots[t]]['games'] += 1; per[bots[t]]['total'] += g['final'][t]['total']; per[bots[t]]['win'] += g['winner'] == t
    for d in g['events']['deaths']:
        if d['round'] >= 150: causes[d['cause']] += 1
        if d['cause'] != 'h2h' or not d.get('mutual') or d['round'] < 150 or d['round'] > R - 50: continue
        mt, pt = d['team'], d['killer_team']
        if mt == pt or d['killer'] not in dd: led['ally_pair'] += 1; continue
        p = dd[d['killer']]; led['pairs'] += 1; led['m_len'] += d['length']; led['p_len'] += p['length']
        per[bots[mt]]['mover'] += 1; per[bots[pt]]['partner'] += 1
        led['p_longer'] += p['length'] > d['length']; led['equal'] += p['length'] == d['length']
        for who, rec in (('m', d), ('p', p)):
            led[f'{who}_born'] += born[rec['id']]
            led[f'{who}_to_mover'] += eaten[rec['id']][mt]; led[f'{who}_to_partner'] += eaten[rec['id']][pt]
print('causes', dict(causes)); print('ledger', dict(led))
n = max(1, led['pairs'])
for k in ('m_len', 'p_len', 'm_born', 'p_born', 'm_to_mover', 'm_to_partner', 'p_to_mover', 'p_to_partner'): print(k, round(led[k] / n, 2))
print('mover net', round((-led['m_len'] + led['m_to_mover'] + led['p_to_mover']) / n, 2), 'partner net', round((-led['p_len'] + led['m_to_partner'] + led['p_to_partner']) / n, 2))
for b, c in per.items(): print(b, dict(c), 'partner/game', round(c['partner'] / c['games'], 1), 'mover/game', round(c['mover'] / c['games'], 1))
