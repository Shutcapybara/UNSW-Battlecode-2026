"""sidescan v2 (D-070 §A / D-071 §C.3): per game, our side, header reason and each side's queen length at the last round.
usage: sidescan2.py [--sub N | game ids...]   (team 7 = us; ranked post-m2 only when --sub)"""
import gzip, sys, json
from pathlib import Path
sys.path.insert(0, '.')
from tools.hub.executor import analyse_replay, runtime_exceptions
from tools.analysis.features import frame
MAP_SWITCH = '2026-10-02T03:49:00'
rows = [json.loads(l) for l in open('public_replays/corpus/index.jsonl')]
if sys.argv[1] == '--sub':
    sub = int(sys.argv[2])
    sel = [r for r in rows if r.get('ranked') and r.get('status') == 'completed' and (r.get('started_at') or '') >= MAP_SWITCH
           and ((r['team_a'] == 7 and str(r.get('bot_a')) == str(sub)) or (r['team_b'] == 7 and str(r.get('bot_b')) == str(sub)))]
else:
    ids = set(sys.argv[1:]); sel = [r for r in rows if str(r['game_id']) in ids]
sel.sort(key=lambda r: r.get('started_at') or '')
out = Path('build/daichi/tmp/rep'); out.mkdir(exist_ok=True)
tot = dict(n=0, w=0, qloss=0, faults=0)
for r in sel:
    gid = str(r['game_id']); p = Path(f'public_replays/corpus/replays/{gid}.replay')
    if not p.exists(): print(gid, 'MISSING replay'); continue
    us = 'A' if r['team_a'] == 7 else 'B'; them = 'B' if us == 'A' else 'A'; opp = r['team_b'] if us == 'A' else r['team_a']
    d = out / f'{gid}.dec'
    if not d.exists(): d.write_bytes(gzip.decompress(p.read_bytes()))
    a = analyse_replay(d); fr = frame.decode(d); f = fr['final']
    exc = len(runtime_exceptions(d, us)); tle = a['stats'][us].get('tle', 0)
    won = fr['winner'] == us
    tot['n'] += 1; tot['w'] += won; tot['faults'] += (tle + exc) > 0; tot['qloss'] += (not won and fr['reason'] == 'queen')
    print(gid, r['started_at'][5:16], f'opp{opp}', r['map_name'][:14], fr['reason'], fr['last_round'], 'WON' if won else ('draw' if fr['winner']=='draw' else 'lost'),
          f"usQ{f[us]['queen']} L{f[us]['longest']}", f"themQ{f[them]['queen']} L{f[them]['longest']}", f'tle{tle} exc{exc}')
print('TOTAL', json.dumps(tot))
