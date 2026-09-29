# C2-0 — fight anatomy: is coordinated fighting worth building?

Generated 2026-09-29T12:26:03Z from the public corpus (ranked completed games; both sides pooled; no submission ids — pooled by team). 182788 contact events over 10331 games; side-game universe per cohort in the JSON `_meta.universe`. Definitions as in `tools/analysis/features/fights.py` (Manhattan contact <= 4, window 6, group >= 3, 5-round closure, adjacency-based initiator, deaths to last contact + 5).

## Pooled, group-class fights per cohort

| cohort | side-games | fights/game | initiator share ±ci | trades | kill-for | kill-against | disengage | own deaths/fight | own len lost/fight | trade ahead share | conv ratio | conv>=2 share | synced entries | rays/head pre | pearl Δ next10 | bed flip |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| top 10 | 1913 | 8.96 | 53.6% ±2.1% | 35.6% | 14.4% | 10.9% | 39.2% | 6.42 | 18.2 | 55.1% | 0.29 | 83.6% | 22.8% | 2.66 | 1.08 | 34.5% |
| ranks 11-30 | 3116 | 9.36 | 49.4% ±1.7% | 33.6% | 12.8% | 14.6% | 39.1% | 7.18 | 19.0 | 46.5% | 0.26 | 80.7% | 22.5% | 2.76 | 2.77 | 31.2% |
| band 55-85 | 6543 | 8.57 | 49.9% ±1.2% | 33.0% | 12.9% | 13.3% | 40.8% | 6.84 | 18.9 | 44.2% | 0.27 | 80.6% | 23.8% | 2.48 | -0.81 | 34.8% |
| team 7 | 114 | 7.55 | 48.3% ±10.5% | 30.9% | 13.8% | 12.3% | 43.0% | 11.6 | 32.9 | 42.5% | 0.18 | 81.9% | 26.2% | 2.66 | 4.01 | 29.2% |

## Contact classes per side-game

| cohort | group | 2v1 | 1v1 | 2v2 | pair | 1v1 initiator share |
|---|---|---|---|---|---|---|
| top 10 | 8.96 | 0.36 | 8.84 | 0.06 | 0.00 | 51.3% |
| ranks 11-30 | 9.36 | 0.34 | 8.37 | 0.06 | 0.00 | 48.3% |
| band 55-85 | 8.57 | 0.35 | 8.62 | 0.06 | 0.00 | 50.8% |
| team 7 | 7.55 | 0.30 | 8.86 | 0.04 | 0.00 | 47.1% |

## Win rate conditional on group-fight outcome (per side-game)

- **top 10**: net_even: 65.5% (n=759); net_kill+: 66.8% (n=621); net_kill-: 58.1% (n=454); no_group_fight: 70.9% (n=79)
- **ranks 11-30**: net_even: 53.4% (n=1155); net_kill+: 52.3% (n=864); net_kill-: 57.0% (n=949); no_group_fight: 54.7% (n=148)
- **band 55-85**: net_even: 47.3% (n=2433); net_kill+: 47.3% (n=1873); net_kill-: 47.6% (n=1981); no_group_fight: 44.9% (n=256)
- **team 7**: net_even: 68.6% (n=51); net_kill+: 54.8% (n=31); net_kill-: 66.7% (n=30); no_group_fight: 50.0% (n=2)

## Era split (group fights)

| era | cohort | n | share | initiator | trades | conv ratio |
|---|---|---|---|---|---|---|
| early | top 10 | 6335 | 37.0% | 52.2% | 46.5% | 0.16 |
| early | ranks 11-30 | 9705 | 33.3% | 49.0% | 42.6% | 0.13 |
| early | band 55-85 | 18471 | 32.9% | 49.4% | 41.5% | 0.13 |
| early | team 7 | 287 | 33.3% | 42.9% | 41.5% | 0.08 |
| mid | top 10 | 6135 | 35.8% | 53.4% | 30.4% | 0.52 |
| mid | ranks 11-30 | 10382 | 35.6% | 50.0% | 28.9% | 0.46 |
| mid | band 55-85 | 20515 | 36.6% | 50.1% | 29.4% | 0.46 |
| mid | team 7 | 312 | 36.2% | 48.0% | 26.3% | 0.48 |
| late | top 10 | 4665 | 27.2% | 57.5% | 27.6% | 0.67 |
| late | ranks 11-30 | 9078 | 31.1% | 49.5% | 29.4% | 0.61 |
| late | band 55-85 | 17113 | 30.5% | 50.5% | 28.0% | 0.64 |
| late | team 7 | 262 | 30.4% | 69.2% | 24.8% | 0.68 |

## Geometry (top 10 vs band, group fights; no map identity)

- **corridor_degree**: open>0.75: top10 init 54.8% conv 0.34 (n=11957) vs band init 49.5% conv 0.30 (n=38293); tight<=0.75: top10 init 50.2% conv 0.22 (n=5178) vs band init 50.7% conv 0.22 (n=17806)
- **open_ratio**: open>=0.75: top10 init 51.5% conv 0.33 (n=3600) vs band init 51.7% conv 0.30 (n=10559); tight<0.75: top10 init 54.4% conv 0.28 (n=13535) vs band init 49.2% conv 0.26 (n=45540)
- **bed_dist**: bed3-6: top10 init 54.0% conv 0.36 (n=3834) vs band init 50.1% conv 0.36 (n=12137); bed<=2: top10 init 53.6% conv 0.28 (n=12739) vs band init 49.8% conv 0.25 (n=42103); bed>6: top10 init 38.5% conv 0.39 (n=562) vs band init 54.8% conv 0.36 (n=1859)
- **portal3**: no_portal: top10 init 54.4% conv 0.30 (n=12319) vs band init 49.5% conv 0.27 (n=41014); portal<=3: top10 init 51.6% conv 0.28 (n=4816) vs band init 50.7% conv 0.28 (n=15085)

## Map class (descriptive only)

- compact / top 10: n=4335, 2.27/game, initiator 51.2%, trades 44.4%, conv 0.26
- compact / band 55-85: n=15312, 2.34/game, initiator 49.4%, trades 35.8%, conv 0.22
- compact / team 7: n=196, 1.72/game, initiator 36.8%, trades 31.1%, conv 0.12
- open / top 10: n=12800, 6.69/game, initiator 54.3%, trades 32.6%, conv 0.30
- open / band 55-85: n=40787, 6.23/game, initiator 50.0%, trades 31.9%, conv 0.29
- open / team 7: n=665, 5.83/game, initiator 51.5%, trades 30.8%, conv 0.20

## Initiator share by unit parity at contact (the confound-killer)

| cohort | ahead mix | even | behind | init ahead | init even | init behind |
|---|---|---|---|---|---|---|
| top 10 | 53.6% | 6.9% | 39.5% | 56.5% (n=1189) | 50.3% (n=195) | 50.2% (n=850) |
| ranks 11-30 | 47.7% | 6.2% | 46.1% | 53.2% (n=1589) | 47.6% (n=269) | 45.7% (n=1516) |
| band 55-85 | 44.8% | 7.0% | 48.1% | 54.8% (n=2828) | 50.9% (n=554) | 45.0% (n=3044) |
| team 7 | 43.0% | 8.1% | 48.9% | 40.0% (n=35) | 55.6% (n=9) | 53.5% (n=43) |

## The S-3 comparisons

### top 10 − band 55-85

| metric | top 10 | ±ci | band 55-85 | ±ci | delta |
|---|---|---|---|---|---|
| initiator_share | 53.6% | 2.1% | 49.9% | 1.2% | 3.7% |
| conv_ge2_share | 83.6% | 0.6% | 80.6% | 0.4% | 3.0% |
| trade_share | 35.6% | 0.7% | 33.0% | 0.4% | 2.6% |
| kill_for_share | 14.4% | 0.5% | 12.9% | 0.3% | 1.5% |
| disengage_share | 39.2% | 0.7% | 40.8% | 0.4% | -1.6% |
| group_events_per_game | 8.96 | — | 8.57 | — | 0.38 |
| trade_ahead_share | 0.55 | — | 0.44 | — | 0.11 |
| conv_ratio | 0.29 | — | 0.27 | — | 0.02 |

### team 7 − band 55-85

| metric | team 7 | ±ci | band 55-85 | ±ci | delta |
|---|---|---|---|---|---|
| initiator_share | 48.3% | 10.5% | 49.9% | 1.2% | -1.6% |
| conv_ge2_share | 81.9% | 2.8% | 80.6% | 0.4% | 1.3% |
| trade_share | 30.9% | 3.1% | 33.0% | 0.4% | -2.1% |
| kill_for_share | 13.8% | 2.3% | 12.9% | 0.3% | 0.9% |
| disengage_share | 43.0% | 3.3% | 40.8% | 0.4% | 2.1% |
| group_events_per_game | 7.55 | — | 8.57 | — | -1.02 |
| trade_ahead_share | 0.42 | — | 0.44 | — | -0.02 |
| conv_ratio | 0.18 | — | 0.27 | — | -0.09 |

## Reading

**S-3 verdict: a pricing rule, not a protocol.** The top ten fight at the band's rate with the band's visible coordination; what they price differently is *when* to trade and what they do in the ten rounds after.

1. Everyone fights the same amount: 7.6–9.4 group fights per side-game in every cohort (top 10: 8.96, band: 8.58, team 7: 7.55) plus ~8.6 one-on-ones. h2h volume is a field-wide constant, as the C1-C death ledger says.
2. The top ten's pooled initiator share is +3.7pp over the band (53.6% vs 49.9%, CIs separated) — but the parity decomposition removes the behavioural read: at matched unit parity they initiate at 50.3% (even) and 50.2% (behind) vs the band's 50.9% / 45.0%. They are simply **ahead at contact more often** (53.6% of their fights vs the band's 44.8%) — the same behaviour at a better economy.
3. Convergence is identical: pre-contact heads-toward-centre ratio 0.29 vs 0.27; ≥2 convergers in 83.6% vs 80.6% of fights; synced group entries ~23% for both; pre-fight sonar 2.7 vs 2.5 rays per head. There is no observable group-coordination signature in the top ten.
4. What separates them is pricing and conversion: they trade while ahead in units 55.1% of the time vs the band's 44.2%; their kill balance is +3.5pp net (14.4% kill-for vs 10.9% kill-against; the band is −0.4pp); and the next-10 material swing after a fight is +1.08 pearls for them vs −0.81 for the band.
5. Their engagement is selective by geometry: the initiator edge appears at fights within 6 cells of a bed (53.6–54.0% vs band 49.8–50.1%) and disappears far from beds (bed>6: they initiate 38.5% vs the band's 54.8% — they refuse fights that buy nothing) and in tight corridors (50.2 vs 50.7).
6. Fight outcomes do not decide band or ranks-11–30 games (win rate flat at 47–57% across net-kill buckets) but do move the top ten (+8.7pp from fights-won to fights-lost, 66.8% → 58.1%); their best bucket is games with **no group fights at all** (70.9%, n=79). Fighting is something they survive, not something they win by.
7. Era: 37% of top-10 fights happen before r100 (46.5% of them trades — the opening bloodbath is field-wide); the initiator edge grows late (57.5% vs the band's 50.5%), again the pattern of engaging with a lead.
8. Team 7 minus band: initiation is NOT our gap (48.3% vs 49.9%; 1v1 47.1% vs 50.8%). Our gaps are reinforcement and cost: convergence 0.18 vs 0.27 (0.12 vs 0.22 on compact maps), and fights twice as bloody — 11.6 own deaths and 32.9 length lost per fight vs the band's 6.8 / 18.9. On compact maps we initiate only 36.8% of group fights (n=196 events): we take contacts, we do not make them.
9. The 2v1 class is rare everywhere (~0.3 per side-game): gangs do not roam looking for singles; groups meet head-on. The 1v1 initiator share is ~50% for every cohort — no skill signal in symmetric duels.
10. A fight flips the eater of about a third of the nearest beds in every cohort (~31–35%) — fights contest beds, but nobody converts location differentially; the *pricing* is the skill, not the venue.

## Caveats

Distances are wrap-aware Manhattan; portals are not followed (a portal can only hide a contact, never invent one; identical bias for all cohorts). Adjacency uses post-move positions (snapshot r+1 for survivors, the death cell for heads that died that round) — start-of-round snapshots alone miss every mid-round collision.
Deaths are priced to event participants within last-contact+5 rounds; overlapping events can each claim a shared death (pooled participant deaths ≈ 60% of all deaths on a 30-game cross-check).
Team 7 has 114 ranked side-games (861 group events); its cells carry ±3–10pp CIs and the parity split is directional only (n=9–43 per cell).
Bed cells are observed from bed-origin spawn events (live-true, but a bed that never spawned in a game is unseen; the local map files disagree with live beds on four maps per C1-E).
Cohorts pool team versions (no submission ids since 28 Sep, D-023); rank comes from the ladder snapshot nearest each game start. ~50% of games sit in autoscrim windows; C1-E found in/out medians nearly identical — pooled here too. 9 of 10,340 games produced zero contact events and stay in the denominators.
Event linking is greedy on shared participants; simultaneous clusters that share heads merge into one event.
No map-identity conclusions (out-of-sample rule): buckets are local geometry; the map-class table is descriptive only.
