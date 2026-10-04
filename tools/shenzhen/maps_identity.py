"""Shenzhen: are maps/live/ (unswbc 1.2.9 templates) identical to the maps the server plays post-m2?
Replay map text carries every TILE as "TILE i k 0 0" (bed flag and interval zeroed), so beds cannot be
checked from replays; they are masked. For every (map, map_hash) seen after 2 Oct 04:31Z (>= 20 games), take one replay's embedded map text and compare to the
template: exact text (modulo a trailing END line), and with the DRAGON team digits swapped (the other seat)."""
import duckdb, hashlib, sys
sys.path.insert(0, '.')
from tools.analysis.features import frame
FILES = {'Autarky': 'autarky', 'Default': 'default', 'Prisoners Dilemma': 'dilemma', 'Schooltime': 'schooltime',
         'Slithery Fight': 'slithery_fight', 'Trophy': 'trophy', 'Trauma': 'trauma', 'Portals': 'portals', 'Devil': 'devil',
         'Queen Of Spades': 'queen_of_spades', 'Australia': 'australia', 'Islands': 'islands', 'Around UNSW': 'unsw',
         'Maze': 'maze', 'Stripes': 'stripes', 'Tower Defense': 'tower_defense', 'weakhold': 'weakhold'}
cap = {}; orig = frame.terrain
def spy(mt): cap['t'] = mt; return orig(mt)
frame.terrain = spy
def mask(l):
    p = l.split()
    return ' '.join(p[:3] + ['_', '_']) if p and p[0] == 'TILE' and len(p) == 5 else l   # replays zero the bed fields
norm = lambda s: [mask(l.rstrip()) for l in s.strip().splitlines() if l.strip() and l.strip() != 'END']
def swap(lines):
    out = []
    for l in lines:
        p = l.split()
        if p and p[0] == 'DRAGON':
            p[1] = '1' if p[1] == '0' else '0'; l = ' '.join(p)
        out.append(l)
    return out
g = duckdb.sql("""select map, map_hash, count(*) n, min(game) game from 'build/s1/corpus/games.parquet'
   where started_at >= '2026-10-02 04:31:00+00' group by 1,2 having count(*) >= 20 order by 1,2""").df()
for r in g.itertuples():
    if r.map not in FILES:
        print(f'{r.map:18s} {r.map_hash} n={r.n:5d}  no template mapping'); continue
    frame.decode(f'public_replays/corpus/replays/{r.game}.replay')
    live = norm(cap['t']); tpl = norm(open(f'maps/live/{FILES[r.map]}.map').read())
    if live == tpl: v = 'IDENTICAL'
    elif live == swap(tpl): v = 'IDENTICAL (seat-swapped dragon teams)'
    elif sorted(live) == sorted(tpl) or sorted(live) == sorted(swap(tpl)): v = 'same lines, different order'
    else:
        a, b = set(live), set(tpl) | set(swap(tpl))
        v = f'DIFFERS: {len(set(live) - b)} lines only in server map, {len(set(tpl) - set(live))} only in template'
    print(f'{r.map:18s} {r.map_hash} n={r.n:5d}  {v}')
