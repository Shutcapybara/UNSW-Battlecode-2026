# Comparison: skadi-v03-exit-only

complete: 12/12 games recorded; 5W 0D 7L. 0 game errors, 0 analysis errors, 0 reported bot runtime faults.

All W/D/L and scores are from the candidate's perspective. Score = (wins + 0.5 × draws) / played. Errors are not draws and are excluded from scores.

Mode: native (not judge CPU validation). Seed policy: fixture_hash_v1.

Curves are start-of-round snapshots plus the final state. Event counters are cumulative. Kills attribute each collision death to the other dragon's team; mutual head collisions count one death per victim, including friendly collisions. Unresolved attribution is exported separately. Self-collisions and wall deaths do not establish intent. Replay 'suicide' actions can represent an absent/invalid action, so they do not establish deliberate feeding either. Space control is the percentage of all tiles strictly closer in terrain-only movement steps to this team's nearest living head. Kelp, portals and wrapping are included; body blocking, facing, length, speed, pearl value and tactical safety are ignored. Ties and tiles unreachable by either team remain unclaimed. Control is sampled at the configured interval and at the final state.

| Opponent | W | D | L | Errors | Pending |
|---|---:|---:|---:|---:|---:|
| gavroche-final | 5 | 0 | 7 | 0 | 0 |
