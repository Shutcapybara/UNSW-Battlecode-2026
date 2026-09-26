# tew-v14-strict-crown

Parent: `tew-v12-mid-support`. Keeps Tew's modular state, communication, evaluator, safety and production ladder. Borrows Avery v05's late, singular-crown idea.

Hypothesis: Tew loses a portion of long games when its longest survivor is too short. Delay promotion until round 300 and length 8, keep the longest crown more consistently, stop splitting at round 300 and disable late feeding. This isolates endgame banking from v13's compact-map restraint.

This is a focused experiment; see the comparison run linked from the final report. Native games do not certify judge-budget safety.

## Results

Native focused comparison `experiment_data/tew-v14-strict-crown_20260925073221345250`: **11–7**, no game errors or runtime faults. It scored 2–4 vs v12, 4–2 vs Avery v05 and 5–1 vs Drake v03 across Arena, Stronghold and default. The v14 crown schedule did not improve on v13's 12–6 in this small comparison. Three maps, six games per opponent.
