# Renoir — R-2 open lane `ra` (Claude Opus 5.5) — status

Updated 30 Sep ~04:00 UTC. Lineage **Renoir** (`bots/renoir-NN-slug/`), branch `r/ra`, tooling `tools/ra/`
(see `tools/ra/README.md`). Report: `docs/findings/2026-09-30-ra-lane.md`.

**State:** 28 candidates screened (incl. one ablation), **0 accepted, 0 holds**; nothing registered. Best directions are the risk-taking
moves (threat cost down, revisit penalty down, trap weight down) at +0.012 to +0.023 econ~ on 160 games, 3-5x
short of the +0.05 bar. Queue continues in the cloud container.

## Results (parent = renoir-00-base for all; d = candidate − parent on common fixtures)

| version | mechanism (one switch) | n | d econ~ | boot 90 % | d win | d units/len@100 | verdict |
|---|---|---|---|---|---|---|---|
| 01a bedwait4 | S-6 guard propensity: value beds ripening <=4 rounds after arrival | 160 | −0.065 | | −0.094 | −0.13/−0.07 | REJECT |
| 01c bedwait16 | same, 16 rounds | 159 | −0.058 | | −0.094 | −0.15/−0.08 | REJECT (QoS +0.16, Trauma +0.14; Devil −0.72, Schooltime −0.41) |
| 02a childarea8 | split only if the child has 8 reachable cells (was 4) | 160 | −0.011 | | +0.013 | −0.05/−0.01 | REJECT |
| 02b childarea12 | same, 12 | 82 | −0.007 | | −0.012 | −0.06/−0.03 | REJECT |
| 03b farm10 | pocket farming off (trap_farm_factor 0.15 -> 1) | 160 | −0.058 | [−0.118, −0.035] | −0.050 | −0.08/−0.05 | REJECT; kelp deaths −15 % |
| 04b gamma096 | target discount 0.93 -> 0.96 | 160 | −0.002 | [−0.056, 0.023] | −0.037 | −0.08/0 | REJECT |
| 05b splitval10 | split value 8 -> 10 | 160 | −0.003 | [−0.010, 0.003] | −0.025 | 0/0 | REJECT (inert) |
| 06a owndisc00 | a target an ally is nearer to is worth 0 (was x0.15) | 80 | +0.021 | | −0.113 | −0.14/−0.05 | REJECT |
| 07b unseen8 | exploration value 5 -> 8 | 80 | −0.050 | [−0.147, 0.036] | −0.088 | −0.05/−0.01 | REJECT (QoS +0.51) |
| 08a memttl20 | remembered pearls trusted 20 rounds (was 40) | 80 | −0.013 | | −0.038 | −0.14/−0.02 | REJECT |
| 10a open15 | opening production window 30 -> 15 | 80 | 0.000 | [0, 0] | 0 | 0/0 | REJECT (inert, 79/80 identical) |
| 11 idlebed | NEW: wait on a ripening bed only when the best target is exploration | 80 | −0.063 | | −0.075 | −0.18/−0.08 | REJECT |
| 12a minarea8 | min room 5 -> 8 cells for any move | 80 | −0.183 | | −0.100 | −0.15/−0.05 | REJECT; kelp deaths −20 % |
| 14b trapw20 | trap penalty 30 -> 20 | 80 | +0.017 | [−0.024, 0.055] | −0.088 | 0/+0.01 | REJECT |
| 15 cluster | NEW: target value x (1 + 0.3 x food mass within 2) | 80 | −0.032 | | −0.138 | −0.17/−0.08 | REJECT |
| 16 infogain | NEW: unseen target worth 5 x clamp(unseen cells revealed / 14, 0.3, 2) | 80 | **−0.223** | [−0.333, −0.119] | −0.200 | −0.20/−0.15 | REJECT |
| 17a threat05 | enemy threat cost x0.5 | 160 | +0.012 | [−0.023, 0.029] | −0.012 | −0.04/−0.03 | REJECT; total_share@250 +0.03 |
| 17c threat025 | threat cost x0.25 | 80 | +0.016 | [−0.033, 0.045] | +0.025 | −0.05/−0.03 | REJECT |
| 17d threat0 | threat cost off | 160 | +0.019 | [−0.017, 0.041] | −0.037 | −0.08/−0.04 | REJECT (seat-A screen said +0.044) |
| 18a visit005 | revisit penalty 0.15 -> 0.05 | 160 | +0.019 | [−0.001, 0.042] | +0.013 | −0.07/−0.01 | REJECT (seat-A screen said +0.033) |
| 18c visit0 | revisit penalty off | 160 | +0.012 | [−0.010, 0.035] | +0.019 | −0.06/−0.02 | REJECT |
| 13b slack1 | trap need len+1 | 80 | +0.008 | [−0.016, 0.040] | 0 | −0.01/−0.02 | REJECT |
| 22 scarcity | NEW: starving dragons explore x1.6 | 160 | −0.024 | [−0.061, 0.019] | −0.069 | −0.08/0 | REJECT |
| 23 nodevil | ABLATION: 32x16 terms off | 160 | −0.042 | [−0.103, −0.006] | −0.075 | −0.15/−0.04 | diagnostic: Devil win 1.00->0.31, Dilemma 0.62->0.75 |
| 19a edens0 | no enemy-density devaluation of targets | 80 | −0.003 | [−0.088, 0.051] | −0.050 | −0.13/−0.03 | REJECT |
| 20b hunt40 | hunters (len<=5 vs prey>=8) from round 40 (was 200) | 80 | 0.000 | [−0.010, 0.017] | −0.013 | −0.02/0 | REJECT (inert) |
| 21a attack0 | head-on strike threshold 0.5 -> 0 | 80 | −0.039 | [−0.083, −0.002] | −0.050 | −0.08/−0.08 | REJECT |

Queued in the cloud, not yet scored: 09b crowd x2, 13b slack 1, 07a unseen 3, 14a trap 45, 13a slack 6,
04a gamma 0.90, 03a farm 0.5, 18b visit 0.30, 17b threat x1.5.


