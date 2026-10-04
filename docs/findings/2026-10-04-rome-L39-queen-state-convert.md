# Rome L39/L49 — queen-state conversion proxy (rejected)

**Run:** 2026-10-04, `unswbc==1.2.3`, FRAME_VERSION 7, paired pool and generalization panels, seeds 1–3, both seats. Parent `rome-01-nodevil`; candidate `rome-03-queen-state-convert`. The source parent is the unchanged Rome base plus one switch; the historical exact base-copy golden check was 0 divergent / 21,479 turns under 1.2.2. A fresh 1.2.3 golden run did not complete, so parity here is source-derived rather than a new completed golden run.

## Mechanism and preregistered expectation

L39/L49 calls for queen-keyed conversion after the opposing side is depleted. The per-dragon policy API does not expose opponent unit count globally. This arm therefore tests the preregistered proxy: after r250, when our global team count is at most five, pin the crown to the original lowest-id queen, suppress takeover by another crown, and activate the existing feeder behavior. This is not a direct test of the opponent-count discriminator. Expected sign: queen length and queen-based round-limit conversion rise; economy lower bound stays above −0.03 and win is not materially harmed.

CPU sandbox probe: max 10.83M points/turn, zero errors (30M limit). Artifact remains well below the 4 MiB zipped limit.

## Result against the three-number form

- **Pool:** Δeconomy mean +0.0000 (cluster 90% CI [0.0000, 0.0000]); expected-score share −2.40 pp (−11.5 expected-score points), cluster 90% CI [−4.17, −0.83] pp.
- **Gen:** Δeconomy mean +0.0000 (cluster 90% CI [0.0000, 0.0000]); expected-score share −0.79 pp (−11 expected-score points), cluster 90% CI [−1.65, +0.07] pp.
- **Worst hygiene:** gen wall deaths +15.9% (0.047→0.054 per 1,000 dragon-turns); no other tier-2 rate rose by >10%.

The analyst queen target is ≥0.5 queen survival at the end of round-limit games on RL maps excluding pocket maps. On the five applicable pool maps (Default, Portals, QoS, Schooltime, Trauma), the parent had 2/167 (1.2%) and the candidate 2/168 (1.2%) alive at r490 among games reaching r490. The available gen RL maps (Default, Portals, QoS, Trauma; no Schooltime fixture in this panel) had 5/119 (4.2%) and 5/124 (4.0%). All-panel survival including early-elimination and pocket fixtures was 2/480 (0.42%)→2/480 (0.42%) pool, and 6/1,392 (0.43%)→5/1,392 (0.36%) gen.

Queen length and rank did not improve: all-panel mean r490 queen length with dead queens counted as zero was 0.063→0.071 pool and 0.096→0.095 gen; median was zero in both arms; the queen was longest in 2/480 pool and 5/1,392 gen candidate games, and in every game where it survived. Round-limit conversion (win rate among round-limit games) changed −5.60 pp pool (cluster 90% CI [−9.52, −2.16]) and −8.45 pp gen ([−13.13, −4.00]).

## Per-map and opening results

All per-map normalized economy deltas were 0.000. Since the trigger begins after r250, r50/r100/r150/r250 opening measures and their within-map percentiles against the parent were unchanged on every map. Per-map win-share deltas are saved in `game_stats/runs/rome-03-permap.csv`; the paired fixture-cluster summaries are in `game_stats/runs/rome-03-permap.clusters.csv`.

Largest adverse map was Portals: −21.88 pp pool and −27.08 pp gen. Pool QoS and Slithery each moved −2.08 pp; pool Trauma moved +2.08 pp. Gen Crossroads and Portal Quartet each moved −2.08/−4.17 pp. The broad cluster losses were bed-rich (−3.0 pp pool, −4.2 pp gen; cluster intervals exclude zero) and round-limit regime (−5.5 pp pool, −15.6 pp gen; intervals exclude zero). The per-map and cluster files retain the complete deltas.

## Gate decision

**REJECT.** The intended queen outcome did not move toward its target; pool win regressed with its cluster interval below zero, gen conversion regressed, and gen wall death rate exceeded the +10% hygiene ceiling. Economy and opening measures were unchanged. Do not stack this arm. The trigger proxy and global crown pin should not be treated as evidence for or against the exact opponent-count formulation.

Artifacts: `game_stats/runs/rome-03-queen-state-convert-z1+gen-s1-2-3.md`, the paired JSON scorecards, and the per-map CSVs. Feature-frame7 cache was used for the official cluster bootstrap. Current gate scripts report economy bounds at displayed precision (0.000); no positive pool economy lower bound is established.
