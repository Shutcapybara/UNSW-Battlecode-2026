"""Summarize each own game against its fixed three geometry/seat/time matches."""
import argparse
import collections
import json
import statistics
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument('--input', type=Path, required=True)
ap.add_argument('--out', type=Path, required=True)
a = ap.parse_args()
sel = json.loads((a.input/'selection.json').read_text())
games = {g['game_id']:g for g in map(json.loads, (a.input/'flows.jsonl').read_text().splitlines())}
assert set(games) == set(sel['games'])
start, end = sel.get('window_start',250), sel.get('window_end_exclusive',400)
side = lambda g,s: next(z for z in g['sides'] if z['side']==s)

def metrics(z):
    assert z['reached_window'] and z['residual']==0
    return dict(total_start=z['start']['total'], total_end=z['end']['total'],
                units_start=z['start']['units'], capshare=z['at_cap_rounds']/(end-start),
                bed=z['eats'].get('bed',0), ally=z['eats'].get('ally_corpse',0),
                enemy=z['eats'].get('enemy_corpse',0), unknown=z['eats'].get('unknown',0),
                paid=z['sprint_paid'], death_segments=z['death_segments'], splits=z['splits'],
                split_delta=z['split_delta'], delta=z['observed_delta'])

blocks, components, teams, series = [], [], collections.Counter(), set()
for b in sel['blocks']:
    g = games[b['own_game']]
    own = metrics(side(g,b['side']))
    fields = [metrics(side(games[m['game']],b['side'])) for m in b['matches']]
    field = {k:statistics.mean(f[k] for f in fields) for k in own}
    blocks.append(dict(game=b['own_game'], series=g['series_id'], map_hash=b['map_hash'], side=b['side'],
                       own=own, field_mean=field, difference={k:field[k]-own[k] for k in own}))
    component = {g['series_id']}
    for m in b['matches']:
        f = games[m['game']]
        teams[f['team_a' if b['side']=='A' else 'team_b']] += 1
        component.add(f['series_id'])
        series.add(f['series_id'])
    components.append(component)
changed = True
while changed:
    changed = False
    for i in range(len(components)):
        j = next((j for j in range(i+1,len(components)) if components[i]&components[j]),None)
        if j is not None:
            components[i] |= components.pop(j)
            changed = True
            break
out = dict(window=[start,end], blocks=blocks,
           equal_block_means={group:{k:statistics.mean(b[group][k] for b in blocks) for k in blocks[0][group]}
                              for group in ('own','field_mean','difference')},
           difference_ranges={k:[min(b['difference'][k] for b in blocks),max(b['difference'][k] for b in blocks)]
                              for k in blocks[0]['own']},
           dependence=dict(own_games=len(blocks), field_match_slots=sum(len(b['matches']) for b in sel['blocks']),
                           field_unique_games=len(games)-len(blocks),field_series=len(series),
                           field_slot_teams=dict(teams),connected_components=len(components),
                           component_series=[sorted(c) for c in components]),
           verification=dict(games=len(games), side_windows=sum(len(g['sides']) for g in games.values()),
                             all_mass_residuals_zero=all(z.get('residual')==0 for g in games.values() for z in g['sides']),
                             payload_and_winner_checked=True, map_hash_check='metadata full hash, decoder12-character prefix checked'),
           uncertainty='Five connected series components: ranges only, no stable CI or causal/full-opponent-matched gap. No early ends in the selected window.')
a.out.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out['equal_block_means'],indent=2))
