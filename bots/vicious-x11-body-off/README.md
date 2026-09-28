# vicious-x11-body-off — Off-switch control for body-state repair

Vicious, derived from the frozen Gavroche final (v54) through x05. Changes only activate with `temporal_body_state=1`.

Tracks unseen tail length separately, preserves occupied visible segments until the true tail vacates, values actual movement/growth costs, and shifts own-body release times in route/flood search. Does not invent unseen segment coordinates. Tests compare partial views against a complete-body simulation oracle.

Experimental; campaign and complete evidence: `experiment_data/temporal_policy_20260927T162922Z_vicious/cycle_03`. Not submitted.
