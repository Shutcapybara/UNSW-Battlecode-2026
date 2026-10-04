# Rome H-KZ12 dose screen: k=4 partial result

**Date:** 2026-10-04  
**Map set:** post-M2 `LIVE_MAPS_M2` pool; gen panel with four stale pre-swap twins flagged  
**Parent:** `carthage-05-free-sprint`  
**Runtime:** `unswbc 1.2.3`  
**Status:** partial seed-1 screen; no D-042 verdict and no dose selection.

## What ran

The corrected H29 H-KZ12 arm uses candidate-specific, body-conditioned reachable capacity `Cb`, strict `Cb < k`, cycle exemption, unknown-frontier passability, and a max-`Cb` fallback if all legal ordinary moves are vetoed. Sprints, splits, and engine legality are unchanged. Dose 0 is exact parent parity. The preregistered dial is `{0,4,8,16}`; only doses 0 and 4 have been run so far, on seed 1 and both seats.

The M2 pool has 272 fixtures per arm and the gen panel 464. All official k=4 games completed and feature extraction covered every game. The gen set has 400 current/unflagged fixtures plus 64 stale pre-swap twins. Those stale fixtures have exactly zero parent-relative deltas and are not transfer evidence. Pool transcript capture is complete (272/272 reruns matched official winner and round count). Gen transcript capture was stopped at 197/464; this partial diagnostic sample is not used for exposure or cause-specific claims.

The recorded panel indexes identify the runtime as `unswbc 1.2.3`; this is explicitly a post-M2 map-set result under that runtime, not a 1.2.9 measurement. No post-M2 analyst references are available here, so report absolute and parent-relative values only.

## Screen results: k=4 versus k=0

| Panel / set | Games | k=0 absolute | k=4 absolute | Paired change |
|---|---:|---:|---:|---:|
| Post-M2 pool | 272 | 226–46, expected score 0.8309 | 230–42, 0.8456 | +0.0147 expected score |
| Gen, all maps | 464 | 349–115, 0.7522 | 350–114, 0.7543 | +0.0022 expected score |
| Gen, current/unflagged only | 400 | 288–112, 0.7200 | 289–111, 0.7225 | +0.0025 expected score |
| Gen, stale twins | 64 | 61–3 | 61–3 | 0 |

Pool checkpoint changes (paired medians) were pearls@50 −0.088, @100 −0.423, @150 +0.441, and @250 +1.963; units@100 −0.0147 and total length@100 +0.0147. Tier-2 wall deaths changed by −0.3866 per 1,000 dragon-turns; invalid deaths remained 0. This is a one-seed screen, not evidence that the gate passes.

Pool map-level expected-score changes: Weakhold +0.125, Slithery Fight +0.0625, Stripes +0.0625, and 0 on the other 14 templates. On Weakhold, pearls@100 changed −5.8125 and @250 +23.5625, with wall deaths −6.5854/1,000 turns. Maze had pearls@100 −0.6875, @250 −8.625, and wall deaths +0.121/1,000. Gen current-map changes were small and mixed; examples include Portals-tr expected score +0.0625 with pearls@100 +1 and @250 −4.625, and Trauma-tr pearls@100 +1.125 and @250 +4.125. These gen twins are stale geometry and remain historical.

Queen entry/veto exposure, same-round deaths, t+1…t+6 cause-specific outcomes with censoring, and fallback rates are not complete: the gen transcript rerun was stopped before full coverage. Doses 8 and 16 were not run. Therefore this report makes no efficacy, transfer, or D-042 gate claim; do not stack k=4.

## D-044 RL translation

- **Observation:** candidate-specific projected body and length; reachable non-kelp `Cb` (cap 16), cycle availability, known/unknown frontier, queen and enemy state, map hash/era, and the queen's cause-specific six-round outcome with censoring.
- **Action:** choose an ordinary one-cell queen direction after masking `Cb < k` pocket entries; retain parent ranking among eligible moves, with max-`Cb`/parent-ranking fallback if all legal moves are masked. Sprint, split, and rescue behavior stay as in the parent.
- **Value/reward:** reward survival against cause-specific queen death and queen-decided losses while tracking official win, food at r50/100/150/250, units/length, and side effects by map and elimination/round-limit regime. The current seed-1 score deltas do not isolate this reward or establish an improvement.
- **Demonstration:** post-M2 top-team replays demonstrate queen survival/growth as a general outcome, not this specific short-pocket avoidance policy. The policy therefore needs exploration/self-play or direct replay labels before it can be called demonstrated.

## Next step

Complete full transcript diagnostics for gen if the mechanism remains prioritized, then report exposure and cause-specific labels. Run k=8 and k=16 under the frozen contract to complete the dose curve before selecting any dose for held-out seeds and a D-042 gate.
