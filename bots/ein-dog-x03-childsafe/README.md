# ein-dog-x03-childsafe: gate splits that birth into enemy reach

Parent: ein-dog-v01-control. One gated edit in `split_option`, default off:

- `child_safe` (set 1): if a trade-capable enemy head (length >=
  `child_safe_len`, set 3) can reach the child's spawn cell before the
  child's second turn, the split is refused unless an allied head at least
  as long stands within `support_rad` of the attacker (support as a gate,
  not a price -- newton's `guard_age` pricing arm was measured null).

Diagnosis: arena losses are newborn-attrition collapses (units@30 2-5 ->
eliminated r45-138 by len-2-4 enemy swarms; `split_nothreat` drops the
ambient threat on the split branch, so on saturated-bed maps we currently
birth straight into enemy reach).

Off-state (`child_safe` 0) is behaviorally identical to the control.
