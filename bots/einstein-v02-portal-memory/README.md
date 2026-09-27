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
Feature-off action parity matched on 18 native fixtures, including Dilemma.
The six-game activation probe recorded 20 ladder handoffs on Colosseum and
blind-exit pricing on Colosseum, Queen and Trauma.

The matched 42-cell factorial screen found no net portal-target gain from the
combined arm: Trauma improved by one score point and Dilemma lost one; all
three protected-map totals were unchanged. The direct Einstein v02/v01 screen
was 7-7 over 14 fixtures. The pre-registered target gate failed, so transformed
holdouts were not opened and v02 is not promoted. Keep both switches off unless
using it for further research. See
`experiment_data/strategy_leaks_2026092623/REPORT.md` for results and limits.

Parameters are in `defaults.py`: `portal_access`, `portal_memory`,
`portal_mem_weight`, `portal_mem_recent`, `portal_mem_floor`, and
`portal_mem_unseen`. The default memory penalty is risk × the candidate
dragon's material value, following Valjean's established expected-loss
semantics; it is not a separately tuned flat score.
