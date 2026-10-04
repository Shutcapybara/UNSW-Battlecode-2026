# P-A02 k16 nominee — Tanaka review and D-053 forecast

2026-10-04. Forecast filed on main BOARD at 14:51 UTC, before the gate card: **P(PASS on seeds 2–3 under D-053 §D) = 0.35**. Expected pool score gain +1.0 percentage point, gen approximately zero. Subjective forecast, not a confidence interval or numerical re-scoring of a gate. No gate seed outcomes read and no new games run.

## Verdict: agree to the already authorized single gate

D-053 properly separates the seed used to select the dose from seeds 2–3 used to gate it. Keep one nominee, all frozen fixtures, D-046 thresholds and D-052 clusters. No new dose or reserve-seed retry after seeing the result. Queen survival remains report-only by the Chair's decision; this review does not reopen that decision.

## Independent replication

Read frozen seed-1 FRAME7-derived queen/winner tables in Asahi's tree and paired candidate `asahi-05-kz12-k16` (43bd2d4f) against parent `carthage-05-free-sprint` (7df05a3f) by seed, map, opponent and seat. The script selects the tested bot's side. All **272 pool and 464 gen** pairs present, no duplicate keys. Frozen paired outcomes and source hashes: `tanaka-round4/k16-seed1-pairs.csv` and `k16-seed1-audit.json`. These are deterministic local development fixtures on the post-m2 template pool and prescribed gen panel, neither ranked nor unranked server games.

| Seed-1 quantity | Pool | Gen |
|---|---:|---:|
| Net score / paired games | +7 / 272 | −1 / 464 |
| Delta, percentage points | +2.5735 | −0.2155 |
| Map×opponent clusters | 136 | 232 |
| D-052 cluster 5th–95th percentiles, pp | [+0.3676, +5.1471] | [−1.0776, +0.4310] |
| Directional-cluster sensitivity, pp | [+0.7353, +4.4301] | [−1.0776, +0.6466] |

Bootstrap: paired whole clusters, both seats together, 1,000 replicates, NumPy default_rng seed7, sorted map/opponent keys, linear percentiles. Central 90% intervals; the lower endpoint is the one-sided 95% bound. This is a sensitivity of an already completed screen, **not a repeated gate or revised screen verdict**. Economy/material/tier-2/deploy clauses are not independently re-audited by these winner-table calculations.

Weakhold is **15/16 vs 8/16**, contributing all +7. The other 16 maps net exactly zero: Portals and Tower Defense −1 each, Slithery and Stripes +1 each. A separate map-only sensitivity is [−0.7537,+7.7206] pp using sorted map keys; it is sensitive to finite bootstrap ordering and is not the prescribed gate interval. This does not contradict Sugawara's qualitative one-map concentration finding. The samples cover fixed maps; none of these intervals estimates unseen-map performance.

## Forecast rationale, dissent and precedent

Shrink the +2.57 pp development estimate because k16 was selected among three doses, the gain is concentrated on one map, and the intended queen endpoint did not respond. A real corridor-avoidance effect remains plausible; the prescribed paired-seat lower bound is still positive on seed 1. I assign 0.35 to the joint gate, including the other guards and deploy constraints, not to pool win alone.

Agree with the report-only requests for Weakhold per seed, pool excluding Weakhold, and veto/fallback counts per queen decision. Dissent: a positive fixed-panel gate would support this temporary intervention on that panel, not a general queen-survival claim. Known internal precedent is the pool-specific failure of dimension-conditioned terms in D-033; KZ12 itself uses structure, but concentrated validation benefit still limits transfer claims.

RL translation: body-conditioned free space is a legal R4 observation; action is vetoing a one-step pocket entry; reward must retain official wins and economy, not substitute fewer wall deaths for the failed queen endpoint. No new teacher demonstration was replicated here.
