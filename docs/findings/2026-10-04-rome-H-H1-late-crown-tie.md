# Rome 04 — late crown tie handoff (H-H1 test card mismatch)

Date: 2026-10-04. Parent: `rome-01-nodevil`; runtime: `unswbc 1.2.3`; FRAME_VERSION 7; paired seeds 1–3, both seats. Candidate snapshot: `bots/rome-04-queen-head-tie/`.

## Preregistration and mechanism audit

The preregistered change was strict-majority to majority-or-tie crown inheritance at a 2+2 split. The recorded expected queen-survival checkpoint was r150. Himeji’s source audit established that `role_crown` cannot be set before r250, so the treatment cannot affect r150. It also established that type-7 inheritance is received by a recently born child (`parent != me`); the engine’s original queen remains the parent. This arm therefore tests a late crown-to-child equal-split handoff across crown roles, not retention of original-queen head material. The parent already assigns the maximum legal `length−2` piece on the relevant escape split, so this does not test a larger queen head allocation.

Himeji’s independent FRAME7 read reports r150 queen survival among fixtures reaching that checkpoint as 95/423 in each pool arm and 244/994 in each gen arm. All 12 opening columns (pearls, units, total length and births at r50/r100/r150) match fixture by fixture. Those are pre-treatment parity checks. Our replay cache does not retain the controller’s internal `role_crown` or message state, so the number of actual post-r250 active-crown equal-split handoffs and their receivers cannot be recovered from these panel replays. The observed original-queen 2+2 events (8 pool, 12 gen) are not a valid substitute for active-crown exposure. This run cannot establish or falsify H-H1’s original queen-retention mechanism; the post-r250 interpretation is exploratory, not preregistered.

## Paired panel results

Official `tools/obscur/rescore.py` and `tools/obscur/gates.py`, 4,000 bootstrap draws; clusters are map × opponent × seat with seeds held together.

| Panel | Parent W–L–D | Rome04 W–L–D | Win-share Δ (95% cluster interval) | Literal mean economy Δ | Median-checkpoint economy Δ |
|---|---:|---:|---:|---:|---:|
| Pool (480 pairs) | 396–83–1 | 390–90–0 | −1.35 pp [−3.125, +0.417] | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| Gen (1,392 pairs) | 1,036–356–0 | 1,036–356–0 | 0.00 pp [−0.503, +0.503] | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |

The combined-panel win point estimate is −0.7 pp [−1.4 pp, +0.0 pp]; combined conversion is −1.5 pp (90% lower bound −3.4 pp). Pool tiers: own-body death rate +1.9%, ally-body +0.6%, wall 0.0%, ally head-on −1.1%; no tier-2 rate rose over 10%. Gen tier-2 rates were flat. Units@100, length@100 and opening births are flat in both panels. D-037 opening percentiles at r50/r100/r150/r250 are unchanged by construction.

Per-map economy is exactly flat on all 39 maps. Pool win changes: Portals −11.46 pp (−5.5 expected-score points over 48 pairs), Slithery Fight −2.08 pp; other pool maps flat. Gen changes: `var+portals_tr` −4.17 pp, `new+md26_commons_spread_s0` +2.08 pp, `var+trauma_tr` +2.08 pp; other gen maps flat. The `var+portals_tr` cluster interval is wide because it is one map. Full per-map and structure-cluster tables: `game_stats/runs/rome-04-permap.csv` and `.clusters.csv`.

## Gate and disposition

**D-032: REJECT; do not stack.** The current economy-led gate fails because pool economy’s lower bound is exactly zero (the requirement is strictly positive) and pool win’s 90% lower bound is −2.81 pp, below −2 pp. The proposed cluster/mean audit also fails: combined economy lower bound is zero, and pool/gen economy upper bounds are zero. Late-route gate fails with no positive late-economy or conversion evidence. No tier-2 tripwire fired. This is a gate rejection of this arm, not a valid falsification of the original H-H1 causal mechanism: the preregistered queen endpoint precedes treatment, active-crown exposure is unavailable, and the implementation changes successor crown assignment rather than original queen head retention.

No post-change field reference replaces the parent-relative comparisons above. The independent analyst audit is `docs/findings/2026-10-04-himeji-rome04-timing-and-pocket-precursors.md`.
