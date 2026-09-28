"""Feature registry (F1 feature lab): name -> definition, unit, family, source events, validation plan, version.

Checkpoint features are declared once as templates ('units@{c}') and expanded over CHECKPOINTS.
`validation` names the most direct check available (ladder in docs/analysis/FEATURES.md):
  V0 bookkeeping identity  V1 probe bot  V2 seed/side stability  V3 proximal target in the replay
  V4 own-bot logs  V5 toggle test  V6 outcome / Elo / field gap (needs data)
"""
from .extract import CHECKPOINTS

VERSION = 1
_T = []


def reg(name, family, unit, definition, source, validation='V2,V6', target=None):
    _T.append(dict(name=name, family=family, unit=unit, definition=definition, source=source,
                   validation=validation, target=target, version=VERSION))


# material
reg('units@{c}', 'material', 'dragons', 'living dragons of this side at the start of round c (terminal state carried forward)', 'snapshots', 'V0,V2,V6')
reg('total@{c}', 'material', 'segments', 'summed length of this side at round c', 'snapshots', 'V0,V2,V6')
reg('longest@{c}', 'material', 'segments', 'longest dragon of this side at round c', 'snapshots', 'V0,V2,V6')
reg('units_share@{c}', 'material', 'share', 'ours / (ours + theirs) living dragons at c', 'snapshots')
reg('total_share@{c}', 'material', 'share', 'ours / (ours + theirs) total length at c', 'snapshots')
reg('longest_share@{c}', 'material', 'share', 'ours / (ours + theirs) longest length at c', 'snapshots')
reg('top1_share@{c}', 'concentration', 'share', 'longest / total at c (crown concentration)', 'snapshots')
reg('len_gini@{c}', 'concentration', 'gini', 'Gini of dragon lengths at c (0 for one dragon)', 'snapshots')
reg('small_share@{c}', 'concentration', 'share', 'share of dragons with length <= 3 (c in 100, 250)', 'snapshots')
reg('big_share@{c}', 'concentration', 'share', 'share of dragons with length >= 10 (c in 100, 250)', 'snapshots')
reg('births@{c}', 'production', 'dragons', 'cumulative splits (children born) by round c', 'DragonSplit')
reg('deaths@{c}', 'survival', 'dragons', 'cumulative deaths by round c', 'DragonDeath')
reg('kills@{c}', 'fighting', 'dragons', 'cumulative enemy deaths credited to us by round c (they hit our body / h2h with us)', 'DragonDeath + mover')
reg('pearls@{c}', 'economy', 'pearls', 'cumulative pearls eaten by round c (any origin)', 'TileChange')
reg('bed_pearls@{c}', 'economy', 'pearls', 'cumulative bed pearls eaten by round c', 'TileChange + origin')
reg('seen_share@{c}', 'space', 'share of cells', 'share of map cells that were inside some 7x7 view of ours by round c', 'snapshots', 'V1,V2,V6')
reg('visited_share@{c}', 'space', 'share of cells', 'share of map cells our heads stood on by round c', 'snapshots', 'V1,V2,V6')
reg('territory@{c}', 'space', 'share of cells', 'cells strictly nearer (terrain BFS, portals, kelp) to our heads than theirs, ties half (c in 50,100,250)', 'snapshots + terrain', 'V0,V3', 'share of pearls eaten next')
reg('bed_territory@{c}', 'space', 'share of capacity', 'territory weighted by nominal bed rate 2/(min+max)', 'snapshots + TILE', 'V3', 'bed pearl share next')
reg('bed_expected_share@{c}', 'economy', 'share of capacity', 'sum over beds of rate x logistic(distance advantage), / capacity', 'snapshots + TILE', 'V3', 'bed pearl share next')
reg('enclosed_share@{c}', 'risk', 'share of dragons', 'share of our dragons with <= 15 cells reachable in 5 steps (bodies block)', 'snapshots + terrain', 'V3', 'death within 3 rounds')
reg('reach_mean@{c}', 'risk', 'cells', 'mean cells reachable in 5 steps from our heads (max 61 on open ground)', 'snapshots + terrain', 'V3', 'death within 3 rounds')
reg('density_ratio@{c}', 'economy', 'ratio', 'mean over our heads of bed rate in the 7x7 view / map-average view rate', 'snapshots + TILE', 'V1,V3', 'eats per dragon-turn')
# scalars
S = [
    ('first_lead_total', 'material', 'round', 'first round our total exceeds theirs'),
    ('lead_changes_total', 'material', 'count', 'sign changes of total-length difference'),
    ('lead_changes_longest', 'material', 'count', 'sign changes of longest-length difference'),
    ('first_len10', 'endgame', 'round', 'first round our longest >= 10'), ('first_len20', 'endgame', 'round', 'first round our longest >= 20 (crown)'),
    ('first_len30', 'endgame', 'round', 'first round our longest >= 30'),
    ('first_split', 'production', 'round', 'first split'), ('last_split', 'production', 'round', 'last split (production stop)'),
    ('first_pearl', 'economy', 'round', 'first pearl eaten'), ('first_contact', 'fighting', 'round', 'first round an enemy body is in any of our 7x7 views'),
    ('first_death', 'survival', 'round', 'first own death'), ('seen50', 'space', 'round', 'round we had seen 50% of cells'),
    ('seen90', 'space', 'round', 'round we had seen 90% of cells'), ('peak_units', 'production', 'dragons', 'max living dragons'),
    ('peak_units_round', 'production', 'round', 'round of peak living dragons'), ('leader_changes', 'endgame', 'count', 'times our longest dragon changed identity'),
    ('splits_0_50', 'production', 'splits', 'splits in rounds 0-49'), ('splits_50_100', 'production', 'splits', 'splits in rounds 50-99'),
    ('splits_100_250', 'production', 'splits', 'splits in rounds 100-249'), ('splits_250_500', 'production', 'splits', 'splits in rounds 250-499 (NaN if game ended)'),
    ('births', 'production', 'dragons', 'children born'), ('newborn_deaths10_per100', 'production', 'per 100 births', 'children dying within 10 rounds of birth'),
    ('child_len_median', 'production', 'segments', 'median child length at split'), ('child_len_le3_share', 'production', 'share', 'share of children of length <= 3'),
    ('dragon_turns', 'context', 'dragon-turns', 'sum over rounds of living dragons'),
    ('pearls_per100dt_0_100', 'economy', 'per 100 dragon-turns', 'pearls eaten per 100 dragon-turns, rounds 0-99'),
    ('pearls_per100dt_100_250', 'economy', 'per 100 dragon-turns', 'same, rounds 100-249'), ('pearls_per100dt_250_500', 'economy', 'per 100 dragon-turns', 'same, rounds 250-499'),
    ('pearls', 'economy', 'pearls', 'pearls eaten, whole game'),
    ('pearls_bed_share', 'economy', 'share', 'share of our pearls from beds'), ('pearls_ally_corpse_share', 'economy', 'share', 'share from our own corpses'),
    ('pearls_enemy_corpse_share', 'economy', 'share', 'share from enemy corpses'),
    ('bed_capture_share', 'economy', 'share of spawns', 'our bed eats / all bed spawns in the game'),
    ('bed_capacity_yield', 'economy', 'share of capacity', 'our bed eats / (nominal capacity x rounds)'),
    ('corpse_recovered_share', 'economy', 'share of drops', 'pearls from our corpses eaten by us / ceil(L/2) dropped'),
    ('corpse_lost_share', 'economy', 'share of drops', 'pearls from our corpses eaten by them / dropped'),
    ('sprint_cost_per_pearl', 'movement', 'segments per pearl', 'segments paid for sprints / pearls eaten'),
    ('density_ratio_mean', 'economy', 'ratio', 'mean over rounds of density_ratio'),
    ('epg_tau1', 'economy', 'pearls', 'expected pearl gain: sum_r sum_beds rate x exp(-d/1), d = our nearest head, sampled every 5 rounds x5'),
    ('epg_tau2', 'economy', 'pearls', 'EPG with tau 2'), ('epg_tau4', 'economy', 'pearls', 'EPG with tau 4'),
    ('epg_conversion', 'economy', 'ratio', 'bed pearls eaten / epg_tau2 (positioning vs conversion)'),
    ('territory_mean', 'space', 'share of cells', 'mean territory over samples'), ('bed_expected_share_mean', 'economy', 'share', 'mean contested bed share'),
    ('enclosed_share_mean', 'risk', 'share', 'mean enclosed share over samples'),
    ('deaths_per1k', 'survival', 'per 1k dragon-turns', 'own deaths'),
    ('death_wall_per1k', 'survival', 'per 1k dragon-turns', 'moved into kelp/wall'), ('death_self_per1k', 'survival', 'per 1k dragon-turns', 'hit own body'),
    ('death_ally_body_per1k', 'survival', 'per 1k dragon-turns', 'hit an ally body'), ('death_enemy_body_per1k', 'survival', 'per 1k dragon-turns', 'hit an enemy body'),
    ('death_h2h_enemy_per1k', 'survival', 'per 1k dragon-turns', 'head-to-head with enemy'), ('death_h2h_ally_per1k', 'survival', 'per 1k dragon-turns', 'head-to-head with ally'),
    ('death_suicide_per1k', 'survival', 'per 1k dragon-turns', 'deliberate suicide action'), ('death_invalid_per1k', 'survival', 'per 1k dragon-turns', 'no valid action'),
    ('kills_per1k', 'fighting', 'per 1k own dragon-turns', 'enemy deaths credited to us'),
    ('kill_length', 'fighting', 'segments', 'enemy length destroyed by our credit'), ('length_lost', 'survival', 'segments', 'own length lost to deaths'),
    ('kill_length_ratio', 'fighting', 'share', 'kill_length / (kill_length + length_lost)'),
    ('enclosed_death_share', 'risk', 'share of deaths', 'share of non-suicide deaths with reach5 <= 15 at round start'),
    ('death_rate_enclosed_per1k', 'risk', 'per 1k enclosed dragon-turns', 'deaths while enclosed / enclosed exposure'),
    ('death_rate_open_per1k', 'risk', 'per 1k open dragon-turns', 'deaths while open / open exposure'),
    ('portal_death_share', 'risk', 'share of deaths', 'deaths within 2 steps of a portal cell'),
    ('alive_end', 'survival', 'dragons', 'living dragons at the end'), ('lifetime_median', 'survival', 'rounds', 'median dragon lifetime (censored at end)'),
    ('sprint_share', 'movement', 'share of moves', 'moves with 2+ steps'), ('contact_share_mean', 'fighting', 'share', 'mean share of our dragons with an enemy in view'),
    ('rays_per_dt', 'sonar', 'rays per dragon-turn', 'sonar rays sent'), ('rays_per_dt_0_100', 'sonar', 'rays per dragon-turn', 'rounds 0-99'),
    ('rays_per_dt_100_250', 'sonar', 'rays per dragon-turn', 'rounds 100-249'), ('rays_per_dt_250_500', 'sonar', 'rays per dragon-turn', 'rounds 250-499'),
    ('rays_toward_com_share', 'sonar', 'share of rays', 'ray direction points toward the circular mean of other allied heads'),
    ('rays_away_com_share', 'sonar', 'share of rays', 'points away from allied centre'), ('rays_side_com_share', 'sonar', 'share of rays', 'perpendicular to allied centre'),
    ('rays_toward_enemy_share', 'sonar', 'share of rays', 'points toward the nearest enemy head (analyst knowledge)'),
    ('rays_away_enemy_share', 'sonar', 'share of rays', 'points away from nearest enemy head'),
    ('ray_hit_kelp_share', 'sonar', 'share of rays', 'ray stopped on kelp'), ('ray_hit_ally_share', 'sonar', 'share of rays', 'stopped on ally body'),
    ('ray_hit_ally_head_share', 'sonar', 'share of rays', 'stopped on ally head'), ('ray_hit_enemy_share', 'sonar', 'share of rays', 'stopped on enemy body'),
    ('ray_hit_enemy_head_share', 'sonar', 'share of rays', 'stopped on enemy head'), ('ray_hit_empty_share', 'sonar', 'share of rays', 'reached nothing'),
    ('ray_leak_share', 'sonar', 'share of rays', 'rays received by an enemy dragon'),
    ('ray_refracted_share', 'sonar', 'share of rays', 'rays aimed into the own neck that left through the tail'),
    ('rays_N_share', 'sonar', 'share of head rays', 'north, among rays that left the head'), ('rays_E_share', 'sonar', 'share of rays', 'east'), ('rays_S_share', 'sonar', 'share of rays', 'south'), ('rays_W_share', 'sonar', 'share of rays', 'west'),
    ('crown20', 'endgame', 'round', 'alias of first_len20'), ('longest_margin_end', 'endgame', 'segments', 'our longest - theirs at the end'),
    ('total_margin_end', 'endgame', 'segments', 'our total - theirs at the end'), ('close_end', 'endgame', 'flag', 'round-limit game with |longest margin| <= 3'),
    ('max_drawdown_total', 'material', 'segments', 'largest fall of total length from its running peak'), ('tle', 'compute', 'turns', 'turns over the time limit'),
    ('phase_t1', 'phase', 'round', 'opening -> economy transition, pooled left-to-right HMM (phases.py)'),
    ('phase_t2', 'phase', 'round', 'economy -> crown transition, HMM (NaN = never reached)'),
]
for ph_ in ('opening', 'economy', 'crown'):
    S += [(f'{ph_}_rounds', 'phase', 'rounds', f'duration of the {ph_} phase (HMM)'),
          (f'{ph_}_pearls_per100dt', 'phase', 'per 100 dragon-turns', f'pearls eaten inside the {ph_} phase'),
          (f'{ph_}_deaths_per1k', 'phase', 'per 1k dragon-turns', f'own deaths inside the {ph_} phase'),
          (f'{ph_}_splits_per100dt', 'phase', 'per 100 dragon-turns', f'splits inside the {ph_} phase'),
          (f'{ph_}_rays_per_dt', 'phase', 'rays per dragon-turn', f'sonar rays inside the {ph_} phase')]
for n, fam, unit, d in S:
    reg(n, fam, unit, d, 'events', 'V2,V6')

REGISTRY = {}
for t in _T:
    if '{c}' in t['name']:
        for c in CHECKPOINTS:
            REGISTRY[t['name'].format(c=c)] = dict(t, name=t['name'].format(c=c), template=t['name'])
    else:
        REGISTRY[t['name']] = t
FAMILIES = sorted({t['family'] for t in _T})

# features whose value a probe bot fixes (probe_check.py), and features tied to a V0 identity (checks.py)
V1_CHECKED = {'rays_per_dt', 'rays_N_share', 'rays_E_share', 'rays_S_share', 'rays_W_share', 'ray_refracted_share', 'births',
              'child_len_median', 'child_len_le3_share', 'sprint_share', 'splits_0_50', 'splits_50_100', 'splits_100_250'}
V0_CHECKED = {'pearls', 'length_lost', 'sprint_cost_per_pearl', 'territory_mean', 'corpse_recovered_share', 'corpse_lost_share'}
for _n, _t in REGISTRY.items():
    extra = [v for v, s in (('V1', V1_CHECKED), ('V0', V0_CHECKED)) if _n in s and v not in _t['validation']]
    if extra:
        _t['validation'] = ','.join(extra + [_t['validation']])
