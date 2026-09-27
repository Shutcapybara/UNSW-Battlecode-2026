# Einstein v02: Ouroboros portal access and memory

Parent control: `bots/einstein-v01-frozen`, an executable clone of
`bots/ouroboros-v13-ladder`.

The compact production ladder excludes portal edges from its local route
graph. `portal_access` optionally yields to the evaluator when a safe, known
paired portal is directly reachable. The evaluator can then compare that move
with ordinary steps. A separate `portal_memory` switch prices known blind
exits from recent body observations. Unknown or unpaired exits keep the old
behavior.

Both switches default off. The factorial probe crosses access (off/on) with
memory (off/on), so portal integration and exit valuation can be separated.
No promotion is claimed before feature-off action parity, activation
diagnostics and matched probes are complete.

Parameters are in `defaults.py`: `portal_access`, `portal_memory`,
`portal_mem_weight`, `portal_mem_recent`, `portal_mem_floor`, and
`portal_mem_unseen`. The default memory penalty is risk × the candidate
dragon's material value, following Valjean's established expected-loss
semantics; it is not a separately tuned flat score.
