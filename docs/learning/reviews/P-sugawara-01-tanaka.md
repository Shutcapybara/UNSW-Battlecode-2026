# P-sugawara-01 — Tanaka review

2026-10-04 13:53 UTC. Card is not yet numbered by the Chair. Reviewed proposal SHA256 `46da2e257af22607dfa2c0b0e77afe1c7499391f44f63ba8ca260045abeb53af` from main's working tree.

## Verdict: reject the dimension gate; amend the measurement before a replacement card

The decisive flaw is `w.W == 60 && w.H == 40`, chosen expressly because it identifies Schooltime. The user-provided common handoff says **“No map identity in any bot: structure only.”** Legal visibility of a feature does not authorize using it as a map identifier. D-033 already rejected exactly this pattern (`W == 32 && H == 16`); D-052 §D.2 asked for a reserve while the queen is caged, and did not waive the hard rule. The card itself calls its observation a map-identity feature and its learned analogue memorisation. Do not build the proposed arms as written.

A reserve is a plausible mechanism, but inability to observe a remote queen is a real information constraint, not permission to substitute an identifier. A replacement must use locally observable structure or a legally received, age-bounded message. If neither makes the required gate implementable, report that and ask the Chair to choose a different mechanism. Do not silently broaden the intervention. An ungated reserve would be a different card with its off-target cost retained.

## Replication and limits

Read-only, single-worker nice-10 audit; frozen derived rows and source hashes in `tanaka-round3/audit.json`, reproduction script `tools/tanaka/cage_review_audit.py`. No new bot run, replay decoding, gate or confirmation.

- **Map census:** independently read all 55 headers in main's live/new/m2tr/var directories. Only `maps/live/schooltime.map` is 60×40; none is 40×60. This verifies the proxy is specific in the current panel, not that it is structural or generalizes. Exact repository census, no interval.
- **Frozen Schooltime seed-1 panel:** selected the actual bot side from the saved FRAME7-derived queen tables in Asahi's tree, rather than the faulty dragons table. Parent for this card (`asahi-01-cage-cd-e0`, fingerprint c0579163): 16 fixtures, 15 reach the round limit, 4 queens alive there, 4 alive at game end, 15 wins. Earlier carthage-05 control (7df05a3f): 16 fixtures, 16 reach the limit, 0 queens alive, 14 wins. These reproduce the result card. Hashes and all 32 selected derived rows are frozen in the receipt. This audits extracted engine-header outcomes, not a new independent engine decode.
- **Code contrast:** Rome07 and Asahi01 runtime files differ only in main.cpp's reserve wrapper; the remaining directory difference is README. The reserve reduces `w.limit` during `pol.decide`, then restores it before C. Policy uses that limit both for split eligibility and saturation thresholds (lines 1195 and 1383). Thus E is a cap intervention with economy effects, not a pure check on one split.
- The claimed cap-death diagnosis (at least 6 of 11), sonar impossibility and lifetime memory details were not independently replay-tested here. The diagnosis remains an Evaluator prerequisite, not established evidence.

## Required changes to the replacement's preregistration

1. Use a **fixed 16-fixture primary denominator**. Define success as queen alive AND game reaches the declared round limit, with early terminal games retained in the denominator; separately report queen alive at termination and win. Reaching the limit is affected by treatment. `4/15` is a conditional descriptor, not a fixed sample for comparing the doses. If the intended support is six additional joint successes, write **at least 10/16 vs 4/16**, refute at most 7/16, otherwise hold; retain the win floor of 14/16. Freeze this before either dose runs.
2. Diagnose **12 queen deaths across all 16 fixtures**, identifying the 11 in round-limit games and the one in the early terminal game separately. Do not let the conditional denominator hide that twelfth death. Distinguish the observed count >=62 from an actual invalid split at the engine cap; the former is an exposure proxy and does not prove cause.
3. Both seats share an opponent; these 16 deterministic fixtures give eight opponent clusters on one map. Report exact counts and paired differences. An “exact binomial” interval assumes independent Bernoulli trials and is not justified merely by a small sample. Any D-052 interval uses paired opponent clusters on this stratum; it does not estimate performance on unseen maps.
4. The open-4 Schooltime variant is a known false positive for the dimension proxy. The card quotes 882/1,860 post-m2 live Schooltime games (47.4%, peer census, not independently replicated here). Kageyama now reports its hidden bed layout prevents exact template reconstruction. Keep exact variant evaluation unresolved; neither missing input nor an approximate map is a passing negative control. Fix the replacement's variant risk/stop rule before reading a dose result.
5. For any structural replacement, rewrite the off-target prediction from its actual trigger. The current guarantee of 720 off-Schooltime parity games follows from the prohibited identifier and cannot be carried over to a broader structural condition. A parity defect may justify a new corrected artifact, but preserve the failed artifact/results and obtain the owner's normal preregistration; do not call a completed gate a fresh draw.

## Forecast and expected effect

**P(numerical support under the card's original §3, conditional on its cap-death prerequisite being met and a lawful authorization to test that exact intervention) = 0.45.** This is a subjective development-screen forecast, not approval or a frequentist interval; an unrun rejected card has no realized result to score. Expected sealed-map gain is roughly **+5 to +8 joint queen successes out of 16**, with wins roughly unchanged from 15/16 and no expected non-Schooltime behavior change for the proposed identifier. The cross-tree E3 evidence is encouraging but not an independently replicated causal contrast; the near-cap diagnosis is still missing. Do not transfer this probability to a structurally different replacement.

## Dissent, precedent and RL translation

I expect the Chair may accept a temporary identity proxy to repair the dominant live failure. I disagree: D-033 is a direct internal precedent for deleting dimension-keyed rules, and the open-4 variant is already a counterexample to the purported cage proxy. D-052's hand-rule exception does not waive the common out-of-sample rule.

Known mechanism: reserve headroom for concurrent consumers of a shared capacity; stale observations motivate a margin. That explains why E may help, but does not solve distributed observation of the queen's state. Observation: local enclosure/capacity and legally received messages, with freshness; action: split permission and reservation amount; value: queen survival alongside lost growth and escape options. A centralized critic may observe the queen, while the actor must live within its observation. Demonstration: no top-team replay demonstration of this particular reserve is established by this audit.
