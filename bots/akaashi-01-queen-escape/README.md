# Akaashi 01 — queen escape

New safety family forked directly from immutable `bokuto-18-queenfeed`, atlas disabled.
The family preserves Bokuto 18's economy and feeding policy while developing queen survival.
Experimental; Bokuto 18 remains the supported qualifier fallback.

Changes:

- Demand six future single-step moves for every queen from round zero, including small teams.
- Apply the existing future head-adjacency exclusion to queens from round zero; retain the
  inherited relaxation when no strict continuation exists.
- Accept a queen dodge replacement only when it passes that same survival horizon.
- Enable existing teammate yielding beside a visible queen at every team size.

The initiating failure is Trophy match 1404793, team B (queen ID 0): at round 66 the queen
moves north from (2,7) into a two-cell alcove. Ally 38 subsequently moves west from (4,7),
closing its exit. The queen moves east at round 67 and dies against kelp at round 68.
Akaashi chooses east at round 66 instead. The original guard could assume a continuation
through cells near an ally head while the team had only five dragons; it also permitted
short-horizon dodge overrides before the final survival check.

Verification and measured screen results are in [the family notes](../../docs/akaashi-family.md).
Run the synthetic baseline/candidate regression with `python3 tests/test_akaashi_queen_escape.py`.
Replay and engine artifacts are under `build/queen-safety-1404793/`; no replay payload is tracked.
