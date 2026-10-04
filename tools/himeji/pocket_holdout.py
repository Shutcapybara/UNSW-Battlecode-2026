"""Audit the predeclared pocket trigger on all newly collected Schooltime games.
No downloads, simulator, bot intervention or shared-store writes.
"""
import argparse, collections, hashlib, json, sys
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', type=Path, required=True)
    ap.add_argument('--snapshot', type=Path, required=True)
    ap.add_argument('--previous', type=Path, required=True)
    a = ap.parse_args()
    sys.path.insert(0, str(a.repo))
    from tools.analysis.features import frame as F
    raw = (a.snapshot / 'index.jsonl').read_bytes()
    index = {r['game_id']: r for r in map(json.loads, raw.splitlines())}
    old = {r['game_id'] for r in map(json.loads, (a.previous / 'index.jsonl').read_bytes().splitlines())}
    cohort = sorted(gid for gid, r in index.items() if gid not in old and r['map_name'] == 'Schooltime')
    # These two named games audit Nara's new claim only, never enter the holdout.
    corrections = [996205, 995614]
    selection = {'cohort': cohort, 'corrections': corrections,
                 'rule': 'Every Schooltime game in snapshot but absent from previous snapshot; outcome independent; both sides.',
                 'index_sha256': hashlib.sha256(raw).hexdigest(),
                 'previous_index_sha256': hashlib.sha256((a.previous/'index.jsonl').read_bytes()).hexdigest(),
                 'decoder_sha256': hashlib.sha256(Path(F.__file__).read_bytes()).hexdigest(),
                 'trigger': 'Initial original queen length4 fills a 4-cell no-bed terrain component, all component cells degree2, zero empty adjacent cells.'}
    (a.snapshot/'pocket-selection.json').write_text(json.dumps(selection, indent=2)+'\n')
    out = a.snapshot/'pocket-rows.jsonl'
    done = {r['game'] for r in map(json.loads, out.read_text().splitlines())} if out.exists() else set()
    for gid in sorted(set(cohort+corrections)):
        if gid in done:
            continue
        meta = index[gid]
        path = a.repo/'public_replays/corpus/replays'/f'{gid}.replay'
        assert hashlib.sha256(path.read_bytes()).hexdigest() == meta['sha256']
        g = F.decode(path)
        assert g['winner'].lower() == meta['winner']
        header = F._reader(path).object(0, 0)
        sides = []
        for side, tid in [('A', meta['team_a']), ('B', meta['team_b'])]:
            q = min(i for i, (s, _) in g['rounds'][0].items() if s == side)
            body = g['rounds'][0][q][1]
            component = {body[0]}
            queue = list(component)
            while queue:
                for cell in g['nbr'][queue.pop()]:
                    if cell is not None and cell not in component:
                        component.add(cell)
                        queue.append(cell)
            occ = {cell for _, b in g['rounds'][0].values() for cell in b}
            empty = [cell for cell in g['nbr'][body[0]] if cell is not None and cell not in occ]
            cycle = len(component)==4 and all(len({n for n in g['nbr'][c] if n is not None})==2 for c in component)
            trigger = cycle and len(body)==4 and set(body)==component and not empty and not (component & set(g['beds']))
            sp = [e for e in g['events']['splits'] if e['parent']==q and e['round']==0]
            children = {e['child'] for e in sp}
            cp = {}
            for r in [0,1,2,25,100,490]:
                reach = g['last_round']>=r
                b = g['rounds'][r].get(q) if reach else None
                cp[str(r)] = {'reached': reach, 'length': len(b[1]) if b else 0 if reach else None, 'alive': bool(b) if reach else None}
            final_body = len(g['rounds'][-1][q][1]) if q in g['rounds'][-1] else 0
            assert final_body == g['final'][side]['queen']
            sides.append({'side':side, 'team':tid, 'submission':header.text(1 if side=='A' else 2), 'queen':q,
                'spawn_body':body, 'component_size':len(component), 'component_beds':len(component & set(g['beds'])),
                'cycle4':cycle, 'empty_steps':len(empty), 'trigger':trigger,
                'initial_actions':[e for e in g['events']['actions'] if e['id']==q and e['round']==0],
                'initial_splits':sp, 'early_child_deaths':[e for e in g['events']['deaths'] if e['id'] in children and e['round']<=2],
                'early_child_actions':[e for e in g['events']['actions'] if e['id'] in children and e['round']<=2],
                'early_queen_food':[e for e in g['events']['eats'] if e['id']==q and e['round']<=2],
                'queen_death':next((e for e in g['events']['deaths'] if e['id']==q),None),
                'checkpoints':cp, 'final':g['final'][side],
                'queen_head_cells':len({s[q][1][0] for s in g['rounds'] if q in s}),
                'total490':sum(len(b) for s,b in g['rounds'][490].values() if s==side) if g['last_round']>=490 else None})
        row={'game':gid, 'cohort':gid in cohort, 'map':g['map'], 'map_hash':g['map_hash'], 'ranked':meta['ranked'], 'series':meta['series_id'], 'started_at':meta['started_at'], 'fetched_at':meta['fetched_at'], 'sha256':meta['sha256'], 'winner':g['winner'], 'reason':g['reason'], 'last_round':g['last_round'], 'sides':sides}
        with out.open('a') as f:
            f.write(json.dumps(row)+'\n')
        print(gid, 'heldout' if gid in cohort else 'correction', [(s['team'],s['trigger'],s['final']['queen']) for s in sides], flush=True)
if __name__=='__main__':
    main()
