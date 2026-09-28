# Gavroche v17: half-strength informed expansion

Parent: Gavroche v16. This keeps the Sinbad v07 dive cap (`v_dive = 3`) and
Von Neumann x06 informed expansion, but halves `info_aggro_push` from 2.0 to
1.0. All other source and parameter settings are unchanged.

The four supplied 11-map series against Tom and Nick show why both opponents
matter: Team A won 6/11, 4/11, 7/11, and 2/11 across the four series. Big Empty,
Prisoner's Dilemma, and Trophy recur as replay losses, but the winner varies by
opponent. The candidate was therefore compared across both sides of all 13
maps against both lineages and five selected model-family bots.

## Cross-family comparison

Native, 208/208 games, no runner or runtime errors: 125–83 overall (60.1%).
Against the same five model-family references as v15 and v16, it scored 84–46
(64.6%): Sinbad v07 16–10, x06 tf-05 18–8, reconstructed x06 grad1 13–13,
x04 support 19–7, and Monte Christo x12 18–8. The grad1 reconstruction comes
from the local x06 source and has sparse rating evidence, so its 13–13 is a
stress result rather than a firm estimate.

On the shared seven-opponent panel from the v16 run, after excluding the new
v16 head-to-head, v17 scored 112–70 versus v16's 111–71. That overall result is
close; the clearer improvement is against the five model-family references.
It also went 17–9 against Gavroche v13, 11–15 against v15, and 13–13 against
v16.

Across all eight references v17 scored 12–4 on Big Empty, 14–2 on Prisoner's
Dilemma, and 9–7 on Trophy. The replay losses are reduced on this panel, though
Sinbad still won both Big Empty fixtures.

Full report: `experiment_data/gavroche-v17-half-gradient_20260926055313164827/summary.md`.
