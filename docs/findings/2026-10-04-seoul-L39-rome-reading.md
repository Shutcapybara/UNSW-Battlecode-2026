# Seoul reading — Rome's L39/L49 queen-state conversion result

**Date:** 4 October 2026
**Type:** cross-lane reading and next-test design; no Seoul bot run
**Source:** Rome's in-progress branch finding `docs/findings/2026-10-04-rome-L39-queen-state-convert.md` and status; main board D-042 identifies L39/L49 as the top tester item.

## Result that now narrows the question

Rome's `rome-03-queen-state-convert` tested the observable proxy available to its per-dragon policy: after r250, when **our own team count** is at most five, pin the crown/feeder role to the original queen. It ran the 1.2.3 pool and gen panels, seeds 1–3, both seats, with FRAME_VERSION 7 and the original `rome-01-nodevil` parent. The report rejects it.

- Pool expected-score share fell 2.40 percentage points (cluster 90% CI [−4.17, −0.83]); queen alive among reached applicable RL games stayed 2/167 → 2/168 (1.2%).
- Gen expected-score share fell 0.79 points (cluster 90% CI [−1.65, +0.07]); round-limit conversion fell 8.45 points (cluster 90% CI [−13.13, −4.00]); queen alive among reached applicable RL games changed 5/119 → 5/124 (4.2% → 4.0%).
- Gen wall deaths rose 15.9%, over the stated +10% tier-2 guard. Economy and opening checkpoints were unchanged because the rule begins after r250. Portals was the largest adverse map (−21.88 points pool, −27.08 gen).

## What this does and does not falsify

It falsifies this **own-team-count trigger plus global original-queen crown pin** as a useful L39/L49 mechanism on these fixtures. It does not test the original L39 discriminator: TT's finding was that the **opponent's** unit count around r300 predicts whether elimination remains likely. Rome explicitly reports that its proxy is not the opponent-count test. Treating this rejection as evidence against every state-keyed conversion trigger would overstate the result.

The implementation constraint is material: a per-dragon observation does not contain the opponent's global unit count. The cheap next information step is an observability audit, not another conversion panel: on saved games, reconstruct what each eligible dragon could infer at r250–350 from visible enemy bodies and teammate sonar, then measure count-estimation error, staleness and map/regime coverage against referee truth. A candidate should only follow if an identity-free, locally available proxy has useful precision and recall on the conversion decision; otherwise L39's proposed trigger is unavailable under the current information boundary.

## Scheduling

Seoul did not launch games. At this check the shared host was quiet by load average, but Rome's status still marks H-H1 (`rome-04-queen-head-tie`) in progress and its paired result artifacts were present. Do not overlap that lane. Recheck status and host activity before any new run.
