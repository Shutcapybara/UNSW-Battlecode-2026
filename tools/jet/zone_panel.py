"""Rich-zone metrics for every game of panel dirs: arm opp map seat score | my/their zone eat<r100, all eat<r100, heads in zone.
usage: zone_panel.py OUT[,OUT2...] [MAP]"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent)); import richzone
mp = sys.argv[2] if len(sys.argv) > 2 else None
for o in sys.argv[1].split(','):
    E = Path(o)
    for l in sorted(open(E / 'results.jsonl')):
        r = json.loads(l)
        if 'score' not in r or (mp and r['map'] != mp): continue
        a = richzone.analyse(str(E / 'replays' / (r['key'].replace('|', '__') + '.replay')))
        me, th = (a['teams']['A'], a['teams']['B']) if r['seat'] == 'A' else (a['teams']['B'], a['teams']['A'])
        print(f"{r['arm'][-14:]:14s} {r['opp'][:10]} {r['map'][:8]:8s} {r['seat']} {r['score']} r{r['rounds']:3d} Z100 {me['eat100']:3d}/{th['eat100']:3d} all100 {me['eat_all100']:3d}/{th['eat_all100']:3d} in " + ' '.join(f"{me['inside'].get(k)}/{th['inside'].get(k)}" for k in richzone.SN))
