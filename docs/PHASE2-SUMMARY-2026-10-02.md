# Phase 2, first wave — what nine instances found in 24 hours (director, 2 Oct 2026 ACST)

Scope: the six Phase 2 instances (analysts Antioch/Claude, Himeji/GPT, Nara/GLM; testers Carthage/Claude, Kyoto/GPT,
Rome/GLM), the three hypothesis stewards (Clair, Obscur, Expedition) and the TT wrap-up, all merged to `main` at
`41f23e04e` and later. Every number is quoted from the finding it came from; the ledger (`docs/hub/HYPOTHESES.md`,
now L01–L50) carries the weights and D-042 the rulings. Read with `docs/PHASE1-SUMMARY.md` for what came before.

## 1. The rules change is now measured, and the field has already moved

The live server switched between 05:58Z and 09:23Z on 1 Oct; no game started in that window, so Antioch's rule
(`post ⇔ started_at ≥ 06:00Z`, now the store's `games.era`) and Nara's (`≥ 09:00Z`) classify every game identically
(D-042 adopts Antioch's). Three independent sprint audits agree on the formula `paid = steps − min(steps, ⌈L/4⌉)` (Nara
44,825 moves, Rome 72,334 charges, Himeji 267/7 discriminating moves, zero violations) and on the tiebreak (Nara: of
3,978 post-change games 2,135 reach the round limit, 175 = 8.2 % are decided by the queen, 102 = 4.8 % against the
old longest-dragon order; Rome 38/38 queen tiebreaks consistent). The queen is the team's original lowest-id dragon,
keeps its id and head end on splits, and has no successor: dead = 0.

Our replay decoder was wrong for the new rule (it inferred winners by longest → total). Carthage fixed it by inferring
the queen from the body track (FRAME_VERSION 6, `FRAME_RULES=pre123` for old replays); Antioch fixed it by reading the
engine's own verdict and the header's new queen field (validated 300/300 against server winners). Main now carries both
as FRAME_VERSION 7 (D-042). Himeji re-read the testers' headline numbers with official outcomes: Rome's base pool
83.65 % → 82.60 %, Kyoto's cap-lift +3.45 pp → +2.19 pp [−1.26, +5.43]. **Every score produced with FRAME_VERSION 5 on
post-change replays is superseded**; nothing is to be scored with it again.

The field's opening did not move (Antioch: post/pre medians 1.00 at r25 and r50 on 2,862 games), but the endgame did:
own-goal deaths are up 12 % field-wide (Nara; top-ten wall deaths 4.8 → 8.8 per 1k), and the ladder map pool narrowed
to the ten ladder maps. One team (Cutlery, 306) changed its bot at about 13:00Z to keep its queen alive — ranked queen
alive@490 0/31 → 9/31, invalid deaths 40/62 → 17/90 (Himeji) — and promptly fell to rank 97; its queen is "the crown
from birth" (454/500 move-rounds, grows to 22 by r400; Nara). Nobody in the top ten keeps a queen: field RL queen
alive@490 2.2 %, top ten 0.7 %, median queen death r41 (Antioch); 71 % of side-rounds are queenless.

## 2. The queen, measured on us

On `hb1-14-prior-r540` our queen reaches r490 in about 1 % of games (Carthage 2/219 reached on the pool, Kyoto 1/217
on round-limit games, Rome 2/480 joint); it dies at median r65–94, by head-on (pool 146 of ~290 deaths) and wall. On the
three pocket maps (Slithery, Autarky, PD) every queen on both sides dies by r4–5 and splitting cannot escape (Antioch's
engine probe falsified H-Q3). Hazards: 5 / 34 / 76 deaths per 1k rounds at 0 / 1 / 2+ enemy heads within 3 (Antioch);
the ten rounds after a split hold 45.5 % of queen deaths in 9.0 % of rounds, exposure ratio 7.24 [5.03, 10.08]
replicated at 4.98 and 6.52 on seeds 2–3 (Himeji); on contact maps 65–84 % of queen deaths are enemy head-ons, on pocket
maps 0 % (Nara). Length is not armour: in 2,161 mutual head-ons the longer dragon died 857 times, the shorter 496.

What it is worth: the lone-queen rule is 36/36 (26 from behind on total), and a counterfactual where the top ten kept
their queen lifts their RL win rate 0.773 → 0.877 (Antioch). What it costs: every queen arm Carthage built loses
generalisation economy — 02 queen-nosplit −0.317, 08 queen-avoid-guard gets gen alive@490 to 33.3 % with a 46/0 queen
record but econ −0.031 and units/total below the guard; 07 queen-yield +0.029 pool economy with the target untouched.
Himeji's reading stands: queen-verdict tallies are changed subsets, not added wins. L49 is at 0.5 with the falsifier
"alive@490 ≥ 0.5 excluding pocket maps at econ lb > −0.03 on both panels".

## 3. What passed, what did not

- **Sprint adaptation (Carthage 04/05).** Correct sprint pricing plus free on-route 2/3-step moves: 05 vs 00 pool win
  +0.045 [+0.019, +0.074], gen +0.017 [+0.003, +0.031], economy flat, guards pass. The first bot adapted to 1.2.3;
  registered as `carthage-05-free-sprint` at 545 (D-042). The 05−04 increment alone is inconclusive (pool win lb
  −0.020, Himeji), so the gain may be mostly the price fix, which does not transfer to the gen twins (+1/96).
- **The bowl was V06's, not the lineage's.** Clair re-ran the weight scans on the prior base: trapw20 pool econ +0.037
  [+0.024, +0.054], gen +0.022 [+0.013, +0.032], win flat, tier-2 clean — rejected only by the units lower bound
  (−0.063; point −0.008 at five seeds); unseen3 pool +0.151, gen +0.065, gen win +0.045, tempo −3.5 rounds — rejected on
  h2h +37 %. Obscur independently on verso-05: unseen3 +0.148 with pool win −0.044. Economy moves now, wins do not
  (the prior already wins 88 % of the pool): L20 0.1 → 0.3, L29 (churn) 0.8 → 0.9. λ = 1 is the out-of-sample optimum
  (λ = 2: pool +0.112, gen −0.080 [−0.114, −0.036]) — hb1-17 is not a better base than hb1-14.
- **Symmetry is additive off-pool, with a head-on cost on the prior's traffic** (Clair on hb1-14: gen econ +0.023
  [+0.008, +0.039], win +0.026; pool h2h +19 %; Obscur on verso-05 s1–3: gen +0.021 [+0.009], pool units lb −0.073;
  Expedition seed 1 gen +5.39 pp [+1.08, +10.35], incomplete). L38 → 0.75; a stacking candidate once a head-on fix
  that does not tax the convoy exists (L42).
- **The mouth tax is dead on three hosts** (Clair −0.078, Obscur −0.126, Expedition −0.056): L40 → 0.3.
- **Late search cap** (Kyoto-03: 48 → 160 late, 64 → 512 sparse): pool econ +0.015 [−0.002], p@250 +0.045 [+0.007],
  win +2.19 pp [−1.26, +5.43] official; gen flat; boundary reject, one fixture lost to an 1,800 s timeout.
- **L10 far-contact refusal** (Rome-02): +0.83 pp pool, economy identical, gen 1,253/1,392 unscored — no verdict.
- **Conversion** (TT): the four top teams cull small dragons beside a long ally from ~r200 (longest at r490 35–46 vs
  Heartbreaker 13). tt-05 (feed_base 140) equals hb1-14 on z1 with longest 32 vs 27 and limit-losses-with-lead 8 % vs
  50 % but own-body +60 %; hb1-24-portal-small +2.0 pp [+0.14, +3.84] under TT's own endgame gate on an hb1-17 base
  Clair has since shown regresses off-pool. All pre-change; L39 re-keyed to the queen at 0.8.

## 4. Targets and the gate

Antioch's post-change endgame columns (field / top ten): RL queen alive 0.022 / 0.007, RL losses with a total lead
0.347 / 0.511, longest at end 28 / 42.5, total 70 / 98; opening components top-10 − us at r50: transits 0.56 SD (largest),
bed pearls 0.31, splits 0.28. Himeji's per-map r50 percentile anchors are published but **provisional** (median bootstrap
width 0.44; release when ≥ 200 blocks/map and ≥ 50 top-ten sides); its ranked-only store (2,072 ranked games, 878
top-ten sides from 9 teams) is the reference set to use. Φ (Antioch's win-potential model: LOMO AUC 0.86 elimination /
0.63 round-limit at r50) is a diagnostic, not yet a guard.

Three gate proposals coexist. D-042 rules: Himeji's win-led rule for predeclared 1.2.3 adaptations (pool win lb > 0,
gen win lb > −0.02, econ lb > −0.03 both panels, units/total lb ≥ −0.02, no Φ guard, no queen exemption); Clair's
BENCHMARKS revision (end tier, either-panel accept with non-harm, cluster bootstrap) stands as written, but every flip
it implies (verso-02/05, tt-05) is an accept-shaped hold until recomputed on the desktop; the units guard form is open
(it alone blocks trapw20) and goes to the analysts; Obscur's `gates.py`/`phasegate.py` are the reference implementation
for the cluster bootstrap and should replace the scorecard's `GATE:` line.

## 5. Corrections worth remembering

Nara's unit-1 "total@100 +12.2 %" was a `len(body[1])` bug (retracted); lune-r1-07's late cap is clamped to 160, not
384; hb1-12 was a two-seed z1 hold, not a D-032 accept; L39's "57 %" was round-limit *losses* with a lead and opponent
units at r300 are not observable; Pulse Farms' r150 gap is survivorship (0/8 jointly live); replay headers do carry the
queen (Himeji 800/800) — Carthage's "replays lack queen fields" was wrong; Carthage's intervals are 90 % central;
Expedition's slope² map weighting is not implemented anywhere and both stewards reject it.
