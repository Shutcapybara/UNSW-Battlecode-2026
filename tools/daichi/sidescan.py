import gzip,sys,json
from pathlib import Path
sys.path.insert(0,'.')
from tools.hub.executor import analyse_replay, runtime_exceptions
idx={}
for l in open('public_replays/corpus/index.jsonl'):
    r=json.loads(l)
    if str(r['game_id']) in sys.argv[1:]: idx[str(r['game_id'])]=r
out=Path('build/daichi/tmp/rep')
for gid in sys.argv[1:]:
    r=idx[gid]; us='A' if r['team_a']==7 else 'B'; them='B' if us=='A' else 'A'
    d=out/f'{gid}.dec'
    if not d.exists(): d.write_bytes(gzip.decompress(Path(f'public_replays/corpus/replays/{gid}.replay').read_bytes()))
    a=analyse_replay(d); f=a['final']
    exc=len(runtime_exceptions(d,us)); tle=a['stats'][us].get('tle',0)
    won=a['winner']==us
    print(gid,r['map_name'][:12],a['reason'],a['rounds'],'WON' if won else 'lost',f'us L{f[us]["longest"]} T{f[us]["total"]} n{f[us]["units"]}',f'them L{f[them]["longest"]} T{f[them]["total"]} n{f[them]["units"]}',f'tle{tle} exc{exc}', 'ODD' if a['reason']=='roundLimit' and (f[us]['longest']>f[them]['longest'])!=won else '')
