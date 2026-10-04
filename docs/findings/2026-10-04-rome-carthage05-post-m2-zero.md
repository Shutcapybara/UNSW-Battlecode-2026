# Rome's post-M2 zero: carthage-05-free-sprint

**Date:** 2026-10-04  
**Map era:** post-m2  
**Runtime:** unswbc 1.2.3  
**Parent:** `carthage-05-free-sprint` (runtime-source fingerprint `7df05a3f`)  
**Status:** required baseline, not a hypothesis arm; no D-032 gate verdict.

## Coverage and method

The pool used the required `run_panel.LIVE_MAPS_M2`: 17 live-map templates, each against the eight ZOO opponents,
seeds 1–3, both seats (816 official games). All 816 completed with official outcomes and replay feature extraction.
The first pass had four missing fixtures that timed out after 1,800 seconds; those exact fixtures were rerun and all
completed. No replay, frame cache, or raw run log is committed.

The official gen panel used 29 map templates, eight ZOO opponents, seeds 1–3, both seats (1,392 games); all completed.
It contains 192 games on four stale twins of swapped maps: Autarky tr, Default tr, Prisoners Dilemma tr, and Trophy tr.
These are historical geometry and are excluded from current transfer interpretation. Schooltime and Slithery Fight
twins were not present in this gen fixture set. The other 1,200 games span 25 current or unflagged map hashes.

The 17-template M2 pool also does not cover two live variants reported in the map audit: Schooltime open4 and
Prisoners Dilemma 10-dragon. This baseline is therefore the required template-set zero, not full coverage of every
observed live-map variant.

## Absolute panel results

| Panel / map set | Games | Wins–losses–draws | Expected score | Raw median pearls @50 / @100 / @150 / @250 | Median units / total / births @100 |
|---|---:|---:|---:|---:|---:|
| Pool M2, 17 templates | 816 | 656–160–0 | 0.804 | 28 / 92.5 / 164 / 286.5 | 23 / 56 / 38 |
| Gen, all 29 templates | 1,392 | 1,038–353–1 | 0.746 | 35 / 114 / 177.5 / 236 | 28 / 65 / 47 |
| Gen, excluding 4 stale twins | 1,200 | 861–338–1 | 0.718 | see per-map CSV | see per-map CSV |

No post-M2 reference values are published for a target-relative comparison. These are absolute measurements of the new
parent and map set, not gains and not evidence that the parent meets the deployment gate.

## Queen columns

Counts below are for Carthage's original lowest-ID queen. `reached` is the number of games whose replay reaches r490;
`joint` means that the same queen is still alive at r490. Survival among reached games is conditional, while the
joint event uses every game as its denominator.

| Panel | Reached r490 | Joint reached and alive | Survival among reached | Joint survival / all games | Mean queen length at r490, dead as zero | Queen longest at r490, all games / when alive |
|---|---:|---:|---:|---:|---:|---:|
| Pool M2 | 444/816 | 2/816 | 2/444 (0.45%) | 2/816 (0.25%) | 0.043 | 0/816; 0/2 |
| Gen | 217/1,392 | 4/1,392 | 4/217 (1.84%) | 4/1,392 (0.29%) | 0.040 | 3/1,392; 3/4 |

Official results with a queen-decided reason: pool 21 games (2 wins, 19 losses), so 19/160 losses (11.9%) were queen-
decided; gen 8 games (4 wins, 4 losses), so 4/353 losses (1.13%) were queen-decided. All 29 winners' terminal queen
lengths agreed with the queen verdict. Map-cluster percentile-bootstrap 95% intervals for the share of losses decided
by a queen are pool [3.3%, 25.5%] and gen [0.0%, 3.3%]. These intervals resample map hashes, not individual games.

## Pool results by live template and exact hash

| Map | Map hash | W–L | Reached / joint alive r490 | Queen-decided losses |
|---|---|---:|---:|---:|
| Around UNSW | `ea443f10a63c` | 43–5 | 48 / 1 | 1 |
| Australia | `7fccdee8a73a` | 40–8 | 48 / 1 | 2 |
| Autarky | `c622b9afe8fe` | 43–5 | 10 / 0 | 1 |
| Default | `42d4766ffede` | 41–7 | 16 / 0 | 0 |
| Devil | `a09e8f2d3bdd` | 46–2 | 1 / 0 | 0 |
| Islands | `8a403c0aa6c7` | 43–5 | 40 / 0 | 0 |
| Maze | `f154114e3ed9` | 43–5 | 47 / 0 | 0 |
| Portals | `56341e6577da` | 35–13 | 46 / 0 | 3 |
| Prisoners Dilemma | `fd02547854cb` | 42–6 | 7 / 0 | 1 |
| Queen Of Spades | `126d71b46443` | 48–0 | 4 / 0 | 0 |
| Schooltime | `5b9481d0c654` | 36–12 | 45 / 0 | 8 |
| Slithery Fight | `001f3501dc5b` | 37–11 | 48 / 0 | 0 |
| Stripes | `31b22a24c467` | 14–34 | 2 / 0 | 0 |
| Tower Defense | `1f097251f445` | 36–12 | 9 / 0 | 0 |
| Trauma | `dcf39d713c06` | 41–7 | 47 / 0 | 3 |
| Trophy | `4f84e990688c` | 41–7 | 0 / 0 | 0 |
| weakhold | `4cf0e4e57c12` | 27–21 | 26 / 0 | 0 |

Full per-map/hash medians and queen columns for both panels are in
[`rome-carthage05-post-m2-permap.csv`](../../game_stats/runs/rome-carthage05-post-m2-permap.csv); machine-readable
panel totals are in [`rome-carthage05-post-m2`](../../game_stats/runs/rome-carthage05-post-m2).

## Next unit under D-044

The next hand-rule arm will declare at least three doses including parent dose 0, report the response curve and
economy, deaths-by-cause, units, length, and win split by elimination/round-limit regime and map era. Its finding will
end with the RL translation: observation, action, value/reward, and whether the behaviour is demonstrated by top-team
replays or requires exploration. The live Schooltime cage fix is C+D plus an E reserve-slot dose; Shenzhen's follow-up
found broad E3 can hurt elsewhere, so any Rome version must make E cage-conditional and report its dose response.
Separately, Kanazawa has posted H-KZ12 as a D-044 dial with k={0,4,8,16} on the queen's kelp-only pocket size and
live M2 queen survival as primary. The next unit will follow the board's current priority after checking that request
against the director's cage-fix-first order.
