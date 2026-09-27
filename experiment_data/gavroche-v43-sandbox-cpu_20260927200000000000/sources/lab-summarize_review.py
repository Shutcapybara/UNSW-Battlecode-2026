"""Aggregate frozen review runs, preserving provenance and paired cases."""
import collections
import hashlib
import json
import re
from pathlib import Path
from lab import ROOT, source_hashes

BASE = ROOT / 'build/lineage-review-20260924'

def load_run(name):
    rows = json.loads((BASE/name/'results.json').read_text())
    for row in rows:
        row['artifact_directory'] = str(BASE/name)
        log = (BASE/name/row['log']).read_text()
        for side in 'AB':
            logged = len(re.findall(r'\(team ' + side + r'\) died:', log))
            assert logged == sum(row['analysis']['teams'][side]['deaths'].values()), row['replay']
    return rows

def aggregate(rows):
    stats = collections.defaultdict(collections.Counter)
    pairs = collections.defaultdict(collections.Counter)
    maps = collections.defaultdict(collections.Counter)
    for row in rows:
        assert not row.get('error') and not row.get('analysis_error'), row
        a = row['analysis']
        assert a['outcome'] == row['outcome'] and a['rounds'] == row['rounds']
        for side in 'AB':
            bot = row['team_' + side.lower()]
            st, detail = stats[bot], a['teams'][side]
            outcome = 'draws' if row['outcome']=='draw' else ('wins' if row['outcome']==side else 'losses')
            st['played'] += 1
            st[outcome] += 1
            st['elimination_losses'] += outcome=='losses' and a['reason']=='elimination'
            for k in ['splits','pearls','turns','timeouts','initiated_trades']:
                st[k] += detail[k]
            st.update(detail['deaths'])
            if detail.get('max_points_estimate') is not None:
                st['max_points_estimate'] = max(st['max_points_estimate'], detail['max_points_estimate'])
            pairs[bot][row['team_'+('b' if side=='A' else 'a')]] += outcome=='wins'
            maps[bot][row['map']] += outcome=='wins'
    return dict(matches=len(rows), stats=dict(stats), pair_wins=dict(pairs), map_wins=dict(maps))

def main():
    native, flagship, sandbox = map(load_run, ['native','flagship','sandbox'])
    primary=[r for r in native if not any(r['team_'+s]=='hydra-v10-farmclean' for s in ['a','b'])]+flagship
    manifests={x:json.loads((BASE/x/'manifest.json').read_text()) for x in ['native','flagship','sandbox']}
    shared=set(manifests['native']['bots']) & set(manifests['flagship']['bots'])
    for name in shared:
        assert manifests['native']['hashes'][name]==manifests['flagship']['hashes'][name]
    map_hashes={}
    for run, manifest in manifests.items():
        map_hashes[run]={}
        for name, hashes in manifest['hashes'].items():
            assert source_hashes(BASE/run/'sources/bots'/name)==hashes
        for name in manifest['maps']:
            data=(BASE/run/'sources/maps'/(name+'.map')).read_bytes()
            h=hashlib.sha256(data).hexdigest()
            map_hashes[run][name]=h
            if run!='native':assert map_hashes['native'][name]==h
    assert manifests['sandbox']['hashes']==manifests['flagship']['hashes']
    originals={name:source_hashes(ROOT/'bots'/name)==hashes for m in manifests.values() for name,hashes in m['hashes'].items()}
    event_rows=[]
    for run in ['native','flagship']:
        for row in json.loads((BASE/run/'event-metrics.json').read_text()):
            if run=='native' and 'hydra-v10-farmclean' in [row['team_a'],row['team_b']]:continue
            event_rows.append(row)
    events=collections.defaultdict(collections.Counter)
    for row in event_rows:
        for side in 'AB':
            st=events[row['team_'+side.lower()]]
            for k,v in row['teams'][side].items():
                st[k]=max(st[k],v) if k.startswith('peak_') else st[k]+v
    for bot, st in events.items():assert st['births']==aggregate(primary)['stats'][bot]['splits']
    by_case={(r['map'],r['team_a'],r['team_b']):r for r in primary}
    changed=[]
    for row in sandbox:
        peer=by_case[(row['map'],row['team_a'],row['team_b'])]
        if row['outcome']!=peer['outcome']:
            changed.append(dict(map=row['map'],team_a=row['team_a'],team_b=row['team_b'],native=peer['winner'],sandbox=row['winner']))
    summary=dict(primary_native=aggregate(primary), latest_native=aggregate(native), sandbox=aggregate(sandbox),
                 primary_events=dict(events), mode_outcome_changes=changed, original_sources_still_match=originals,
                 map_hashes=map_hashes, unique_new_matches=len(native)+len(flagship)+len(sandbox))
    (BASE/'primary-results.json').write_text(json.dumps(primary,indent=2)+'\n')
    (BASE/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ['primary_events','map_hashes']},indent=2))

if __name__=='__main__':main()
