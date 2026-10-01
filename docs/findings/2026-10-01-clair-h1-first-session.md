---
id: F-20261001-clair-h1-session1
author: claude/clair (H-1 hypothesis steward)
kind: findings
title: "Clair first session: the bowl is broken on the prior base; λ=1 confirmed as the OOS optimum; the gate revised; fresh mechanisms 0-for-4 with corrected forms named"
code: tools/clair/ (lane.py, score_extra.py, by_map.py), bots/clair-01..18
data: 18,836 local games this session (build/clair/runs/, scorecards build/clair/score-*.json, per-map tables build/clair/bymap-*.txt); no runner errors
---

## What this session was

The H-1 steward's first session, three passes on the macbook (worktree `../wt-clair`, branch `r/clair`).
Base for pass 1: `hb1-14-prior-r540`; pass 2 added `hb1-17-prior-lam20` and `hb1-16-prior-lam05` (copied from
r/tt for measurement); pass 3 closed the λ question. Gate: D-032 through `tools/clair/lane.py` (the lanes'
scorer), tempo through `tools/s1/tempo_gate.py`, per-map decomposition through `tools/clair/by_map.py`
(tr-consistency + Q2 slope² weighting), endgame/combined through `tools/clair/score_extra.py`.

## 1. The bowl is broken on the prior base (pass 1)

Six weight moves that measured +0.01–0.03 on V06/nodevil (Renoir 17a/18a/14b/07a; Maelle wt_ally/capsel) were
re-run as single-knob bots on hb1-14. Four of six cleared +0.03 at screen; at full D-032:

| knob | pool econ~ [90 %] | gen econ~ [90 %] | verdict |
|---|---|---|---|
| trapw20 | +0.037..+0.040 (5 seeds, n=800, lb +0.027) | +0.022 (lb +0.013) | REJECT only on the units **lower-bound form** (point −0.008); registration-candidate shape |
| unseen3 | +0.151 (lb +0.118) | +0.065 (lb +0.046), win +4.5 pp | tempo gate **ACCEPT** (−3.5 rounds); REJECT on h2h +37 % (transit/newborn churn) |
| unseen 3.2 | +0.059 | — | the response is a steep slope (4:+0.000, 3.2:+0.059, 3:+0.151), not a knife-edge |
| allycrowd −1.4 | +0.029 (lb>0) | **−0.058** | pool-fitted; Maelle's off-pool loss reproduced |
| capsel | +0.006 (late p@250 +0.05/+0.04 lb>0) | +0.015, gen win +0.039 | late-only, tr-inconsistent per-map |

L20's revival condition fired: **every dormant "V06 says no" weight-move row re-opens on the prior base.**
Per-map: unseen3's gain is the starved-opening cluster (trauma +1.64, qos_tr +1.48 — Esquie's L35 class;
base-robust: trauma +1.31 on λ=2), trapw20's is corridor/sparse maps and exactly zero on dense maps. The stack
of the two is additive on economy (+0.160) and compounds win/hygiene costs (win −0.062) — never blind-stack.

## 2. λ = 1 is the out-of-sample optimum (passes 2–3)

The prior weight was never swept; tt's z1-only sweep said λ=2 passes (144–16). The joint read:

| λ | pool econ~ vs hb1-14 | gen econ~ vs hb1-14 |
|---|---|---|
| 0.5 | negative (p50 −0.139) | negative (p50 −0.090) |
| **1.0** | reference | reference |
| 2.0 | **+0.112** | **−0.080 [−0.114, −0.036]**, gen win −0.033 |

**hb1-14 remains the registered uploadable.** The λ lever is pool-shaped end-to-end — the fourth instrument to
find pool-shaped optima that do not generalise (allycrowd, verso crowding, alicia s1c, λ=2), and the concrete
case the revised gate's either-panel rule exists for.

## 3. Stacking and holds on the prior base (pass 1, tests 2–3)

- **symseal (aline-17's change set) on hb1-14: additive off-pool** — gen econ +0.023 lb +0.008, units
  +0.062 lb +0.021, length +0.087 lb +0.012, win +2.6 pp lb +0.007 — at aline-17's own magnitudes. Pool a
  0.001-miss (econ lb −0.001) with h2h +19 % and a new specific interaction: symmetry × D-033 map-identity
  terms (dilemma −0.17, schooltime −0.14). Accepts measured on nodevil bases may not transfer to terms-on
  production bots — the port-and-re-test step is required.
- **mouthroute (gustave-07c) does not transfer**: pool econ −0.078 (flat on its own base) while still cutting
  h2h −15 %/−17 % — the flat −4 tax lands on the prior's productive portal convoys. The fitted dose (−1..−1.5)
  on a symseal-like stack is the live L33/L40 shape.

## 4. Fresh mechanisms: 0-for-4 at screen, each failure names its corrected form (pass 2)

| mechanism | result | corrected form |
|---|---|---|
| split-defer on a food run (s1 split-stall) | econ +0.002, win −0.050 | value-form: a split *priced* by the parent's expected intake vs the child's safe intake |
| pair-wait, vanish key (L33/S-1 Q4) | null — the key almost never fires from one 7×7 view | (see next) |
| pair-crowd, visible-ally-at-mouth key | null — h2h unmoved | the collisions are not decided at the dive decision; the fitted mouth-*cost* is what moves the channel |
| elim-state conversion, enemy-recency trigger (L39) | win −0.044; lead-losses not improved | a *pressure* observable (own-vs-visible-enemy), not recency |

## 5. The gate was revised (applied under the lead's authorization; rollback falsifier recorded)

`docs/analysis/BENCHMARKS.md` §"Start here (1 Oct revision)": (1) a phase-`end` tier for changes acting after
r250 (longest/total margins, round-limit-losses-with-material-lead — 60 % of hb1-14's round-limit losses carry
a material lead, all `longest` losses; deliberate culls exempt from the tier-2 guard; tt-05 flips to
accept-shaped); (2) accept = positive economy lb on at least one panel with non-harm on the other (verso-05's
case; clair-05 shows why the non-harm side stays strict); (3) the fixture-cluster bootstrap is authoritative
with a borderline rule (aline-17's accept rested on the plain form); (4) the mid-game gap (r150–250) named with
its instrument — the tempo net-income curve extended to r300 as a *new* reference from the desktop's
`build/s1/corpus/`. None of this session's own verdicts change under the new rules. **Flagged for the
director, not self-edited**: trapw20's units-guard form (lb vs mean) — the one rule change that would admit
the steward's own candidate.

## Rows touched (proposals; the director applies)

L20 → 0.4 (re-opened; revival condition met at 5 seeds by trapw20) · L38 → 0.75 (additive off-pool) ·
L40 → 0.3 (does not survive the prior; fitted-cost revival form) · L39 → 0.8 (four top teams converge;
recency trigger dead, pressure form open) · L12 → 0.3 (density-as-target dead a fourth time) · L02 → 0.4
(sparsity sub-form two-strike) · L04 → 0.2 (ES closed, pool-fit signature) · L11 → 0.3 · L34 → 0.3 ·
L31 → 0.6 (crown graft; hand-off line closed) · L36 → 0.85 (split-stall decomposition; defer-form dead) ·
L21 → 0.1 dormant (settled by D-032) · L14 → 0.4 (map-driven exploration) · **L41 new** (authenticated atlas:
our local family occupies the ranks-11–30 niche; the local panel cannot select toward the top ten — the
standing caveat on every local accept). L27 note: donor priors from the two new top teams fail/hold — prior
quality tracks donor *predictability*, not strength. Registration proposals: hb1-14 stands; hb1-17 not
promoted (gen −0.080); trapw20 referred with the guard-form question.
