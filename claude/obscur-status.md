# H-1 `obscur` status — Obscur lineage (hypothesis steward; Claude Opus 5.5, desktop)

Prompt: `docs/hub/prompts/2026-10-01-H1-hypothesis-steward.md`. Branch `r/obscur`, worktree `../wt-obscur`. Bots
`bots/obscur-*` (copies), tools `tools/obscur/` (`lane.py` = Verso's runner with outputs under `build/obscur/`,
SF-1 weights via `M:` params, 2 h per-game timeout; `rescore.py` / `gates.py` = the gate audit). Nothing registered,
no other lane's tree edited. Everything below is a **proposal** for the director; ledger edits are not made here.

**Pass 1 — 1 Oct 2026, 15:00 ACST.** Read: HYPOTHESES (L01–L40 and log), D-029–D-039, BENCHMARKS, every lane's status
and findings on `origin/main` plus the commits not yet merged (`r/tt` +7, `r/alicia` +1). Re-scored ten past gate
decisions from the finished runs on this desktop (`build/{verso,rc,maelle}` and `wt-alicia/build/rc`) under the
current and the proposed gate. Started the three first-pass tests (now four arms, see below; the host is shared:
nice 10 on the lead's instruction, ~75–100 games/h).

## 0. Three things the director should see first

1. **`gustave-07c-mouthroute` is not a HOLD; it is a REJECT under the lanes' own letter** and under any economy
   statistic but the median: pool units@100 lb −0.055, length@100 lb −0.054 (guards −0.02), pool per-game-mean
   economy −0.044 [−0.063, −0.023] (Schooltime −0.32). It is registered at 505 (D-039.2) on the HOLD reading.
   The ally head-on cut (pool −18 %, gen −23 %) is real; the economy cost is real too. Proposal: drop it from the
   queue until it stacks with something that pays for it (it is in my test 3 on the prior base).
2. **The only clean D-032 accept in the programme, verso-01, sits on the boundary of the gen clause.** gen econ~ lb
   −0.017 in Verso's bootstrap, −0.020/−0.021 in mine (same rows, different resample seed); with the fixture-cluster
   bootstrap it is −0.034. Every other indicator of verso-01 is overwhelmingly positive (win +0.15/+0.05, units and
   length +0.19/+0.31). A gate whose flagship accept depends on the bootstrap's RNG seed is measuring its own noise
   at that clause. → Gate audit, item G2/G3.
3. **verso-05's gain over cycle 2 is endgame conversion, which the economy statistic cannot see**: win rate among
   games that reach the round limit +0.070 [+0.011, +0.131] pool, +0.112 [+0.036, +0.189] gen; P(loss | round limit,
   material lead) −0.11 [−0.19, −0.03] gen. The lead kept verso-05 "despite the D-032 letter"; the data says why.
   → Gate audit, item G4.

Also: lune-r1-07's "late cap ×8" is not ×8. `policy.hpp:1148` is `cap = std::min(cap, search_cap_late)` with
`search_cap = 160`, so `search_cap_late = 384` gives an effective late cap of **160** (base 48); the other change,
`search_cap_sparse 64 → 512`, is a `max` and does bind. R-1's "saturates by 384 / whole-map identical" is the clamp,
not the value-bound prune. Every base since D-033 (verso-*, maelle-*, aline-*, gustave-*) inherits this. L01/L02/L25
text must change; the 160→384 slope has never been measured (ranked item 4).

## 1. First-pass tests (running)

Base: **`verso-05-hb800-prior`**, not `hb1-14`, for four reasons: it is D-033-compliant (hb1-14 still carries the
three `W==32 && H==16` terms and V06's caps); aline-17, gustave-07c and maelle-04 were all built on the same root
(`lune-r1-07` nodevil), so their change sets apply as patches without re-porting; Maelle's and Renoir's knobs are
runtime parameters on it (`M:wt_ally`, `M:capsel`, `p.<knob>`), so the bowl scan needs no rebuilds; and Verso's
1,224 verso-05 games (seeds 1–3, both panels) are the parent arm — I replayed one fixture here and the replay is
byte-identical (`cmp`), so they were imported, not re-played. hb1-14 and verso-05 carry the same learned prior
(540 vs 800 rounds); the bowl question is about the prior, not the size.

| Arm | What (one change vs verso-05) | Question | Seed 1 (pool / gen) | Seeds 1–3 D-032 |
|---|---|---|---|---|
| `o-ally14` | `M:wt_ally=-1.4` (Maelle F2, maelle-04) | bowl: Maelle's live lever | running | — |
| `o-capsel384` | `M:capsel=1, capsel_hi=384` (Maelle F5, L02 selector) | bowl | queued | — |
| `o-threat05` | `p.threat_weight=0.5` (Renoir 17a) | bowl | queued | — |
| `o-visit005` | `p.visit_weight=0.05` (Renoir 18a) | bowl | queued | — |
| `o-trap20` | `p.trap_weight=20` (Renoir 14b) | bowl | queued | — |
| `o-unseen3` | `p.unseen_value=3` (Renoir 07a) | bowl; also the exploration contradiction (C3) | queued | — |
| `obscur-01-sym` | aline-13's symmetry change set alone | additivity, bare mechanism (aline-13 alone was a REJECT on gen hygiene) | running | — |
| `obscur-03-symseal` | obscur-01 + aline-07 seal (= aline-17 on verso-05) | additivity of what was accepted | running | — |
| `obscur-02-mouth` | gustave-07c's mouth rule | does the mouth rule survive the prior | queued | — |

Protocol: seed 1 on every arm first; an arm goes to seeds 2–3 unless its seed-1 pool economy *and* win upper bounds
are both below 0 (it cannot pass). Reported with the current gate and the proposed one (§4). Result table and weight
proposals follow in pass 1b.

## 2. Rows re-scored (proposals; grid 0.9/0.7/0.5/0.3/0.1, one step per result)

Off-grid weights in the ledger (0.15, 0.35, 0.4) are mapped to the grid when a row moves. "Text" = the row's
evidence is wrong or stale and must be corrected whether or not the weight moves.

| Row | Now | Proposed | Pointer | Why |
|---|---|---|---|---|
| L01 | 0.7 | 0.7 + text | `bots/lune-r1-07-latecap8x-only/policy.hpp:1145-1151` | late cap clamped to 160 (above); "×8 alone keeps the gain" is "late clamp 48→160 + sparse floor 64→512" |
| L02 | 0.7 | **0.5** | Maelle F5 (`claude/maelle-status.md:206-213`: lo 48 −0.020..−0.031; floor-kept lo 160 −0.015/−0.029); Gustave 04a −0.043 [−0.072, −0.005] (`docs/findings/2026-09-30-rc-lane.md`) | two right-host rejections of the row's own "recommended selector"; one step because the volatility-keyed extension half is untested. Strike "recommended selector" from the text |
| L03 | 0.7 | **0.5** | hb1-13 (fade is worse; "the dip is composition", `claude/hb1-status.md:313-333`); Verso opening belief `c0x-both-sf` s1–3 econ~ −0.062 [−0.103, −0.027]; Maelle 2b no optimum; TT ramps tt-06/07 worse | four phase-conditional remedies on the right host, none positive; the bifurcation is real, the remedy is not |
| L04 | 0.3 | 0.3 | Alicia `origin/r/alicia` stage 1 (s1c "not flat on the gate objective", ΔC +0.0155 se 0.0066) vs alicia-03 REJECT | hold until alicia-04's gate and my bowl scan read; contradiction C2 |
| L05 | 0.8 | 0.8 | — | not moved: the prior cuts leaks by steering (pro), Aline's farm cliff and Renoir say leaks are the economy's exhaust (con) |
| L06 | 0.3 | **0.2→ re-scoped** | S-1 Q4 (`docs/findings/2026-09-30-s1-Q4-portals-own-goals.md`): blind landings 0.207 vs field 0.189 | exit *knowledge* is not the gap; the own-traffic half moves to new row L42 |
| L09 | 0.15 | 0.15 | TT: Cache me outside's sonar is state-dependent (`claude/tt-status.md` ~469), handoff: niche N7 near-silent | evidence both ways; decisive test is a payload decode of Cache me outside (ranked list) |
| L10 | 0.4 | 0.5 | S-1 atlas: contact share −0.82 local / −0.46 live with strength; Q3 contact −0.46..−0.71 SD | corpus-only, but on-sign and cheap to test; untested on any bot (Gustave's directive 1 never ran) |
| L11 | 0.35 | **0.3** | Gustave 06b −0.016 [−0.038, −0.001]; 06a inert | a right-host rejection of the structure-keyed guard; L35 is its information-keyed survivor |
| L12 | 0.5 | **0.3** | Gustave 02b (Sciel-03a = flat ×0.70 value cut, 95.5 % of evaluations at exactly 0.70), 03a/03b density alone +0.008 / −0.005; Maelle F1 −0.030 [−0.057, 0.000] | the row's flagship evidence (Sciel-03a) was not density; two right-host nulls/rejections of density as a target term. Ally *crowding* (maelle-04) is a density term that does move material: give it its own row (L43) |
| L13 | 0.4 | **0.3** + text | Alicia ES varied `momentum_weight` jointly, no slope (`claude/alicia-status.md:25-33`); Monoco ra-06 hysteresis −0.044; Gustave 09a portal intent −0.005 | "not yet varied on Ares" is stale; commitment-shaped continuous changes are flat or negative |
| L14 | 0.3 | 0.3 + re-scope | Aline 04/12/19/23 (more exploration pressure: units, length or win lower bounds fail), Renoir 07b/16; Gustave 08a gen +0.027 | the *pressure* form has two independent right-host rejection sets → dormant as a sub-claim; scout splits (the row's actual claim) untested. My `o-unseen3` arm tests the other direction on the prior base |
| L15 | 0.3 | 0.3 + text | — | C1-E's "margin 0–1" is from elimination games (wrong population). Do **not** raise on "longest-margin sign predicts the round-limit result in 99 %": round-limit games are *decided* on length, so that is the rule, not evidence. TT: top teams feed without electing a crown — the location-consensus need is unshown |
| L21 | 0.3 | **0.1** (by rule) | D-032 | superseded; the gate-shape question moves to the gate audit and new row L44 |
| L24 | 0.35 | **0.3** | hb1-10 two-seed fail (own body +10.5 %, wall +10 %); Esquie-04 econ −0.035, own body +24 % | grid; two more right-host rejections of the V19 split |
| L27 | 0.8 | 0.8 + text | `claude/hb1-status.md:290-327` | hb1-12 was a **HOLD on z1 at two seeds** (R-4 mean, no gen panel, no bootstrap), not "an accept on every guard" (D-038); own-body −8.1 % / −18.1 %, not "30–40 %"; seed 2 is weak replication (139–21 for both bots at both seeds). "The prior's size is the lever" holds **off-pool only** (pool 300→540: win +0.000 [−0.032, +0.033]) and in the endgame (G4) |
| L28 | 0.9 | 0.9 + text | Esquie anatomy; Maelle golden (nodevil diverges on Portals) | Portals is also 32×16; "Dilemma is the other 32×16 map" is incomplete |
| L29 | 0.8 | **0.9** | second independent mechanism: Gustave 08a (pool econ~ +0.032, units −0.046, wall +11 %), Maelle self-play (food pays pearls and deaths one for one) beside Renoir 07a/07c; Verso corpse share 0.452→0.419 / 0.438→0.381 | established for the *local metric*. Live, ally-corpse share is 0.26–0.33 for everyone (S-1 handoff), so it is a yardstick hazard, not a behaviour gap |
| L34 | 0.35 | **0.3** | Verso tier 1 dropped by its pre-registered rule (CNN+GRU ≤ ±0.2 pp; probes recover the hand state) | own test (3) answered: the net is a compressor of the hand state |
| L35 | 0.5 | 0.5 + text | `docs/findings/2026-10-01-esquie-map-anatomy.md:227-241` | median-form econ at s1–3 −0.004; transfer (trauma_tr) is gen seed 1 only (≈ 4 games); the Trauma r50 gain *reverted* at min_age 24 — "fixes it locally" is true for p@250, not for the opening D-037 targets |
| L37 | 0.8 | split: L37a 0.9 / L37b **0.5** | S-1 Q2b/Q2c (`docs/findings/2026-09-30-s1-Q2-map-predictability.md:141-172`) | (a) everyone is a map specialist — replicated split-half → 0.9; (b) "Portals is the least predictable map → weight by slope²" — Q2c's clean sample gives slopes 0.42–0.64 (ratio² ≈ 0.43, not 1/9) and Q2b finds Portals the *most* specialist map: two results against → 0.5, and D-037's slope² weighting suspended (G6) |
| L38 | 0.7 | 0.7 | test 2 running | text: aline-13 (symmetry alone) was a REJECT (gen wall +10.3 %, gen win lb −0.032); the accept is the stack with the seal, and its cluster-bootstrap pool lb is −0.000 |
| L39 | 0.7 | 0.7 + text | `claude/tt-status.md:130-140, 326-333, 345-350` | "hb1-12 loses 57 % of its round-limit games with a lead" → 57 % of its round-limit **losses** had a lead (round-limit win rate 0.78); "opponent units at r300 is the observable" → TT: *not* observable, stand-in "no enemy met for a long time" (D-039.3 repeats the error); tt-05 was level (141–19), failing only own-body — the own-body guard rejects feeder suicides by construction (G5) |
| L40 | 0.5 | 0.5 + text | §0.1 | the mechanism claim stands (ally h2h −18/−23 %); the fix is a REJECT by the letter, not a HOLD |

Untouched this pass: L07, L08, L16–L20, L22, L23, L25 (but see L01 text: V09's late cap 80 *would* bind), L26,
L30–L33, L36. Stale text in L30: Sciel-01a already tested C1-C fix #2 (siting) on V06 — inert.

**New rows proposed**

| Id | Hypothesis | Weight | Evidence | Test |
|---|---|---|---|---|
| L41 | Early portal use (r0–50) is an opening component we under-use: top teams transit 5 by r50 vs our 2; a rush is +EV within-team on all ten maps | 0.5 | S-1 Q3, Q5 | one switch per D-037 cluster (portal-gated openings), tempo gate + D-032 guards |
| L42 | Own-traffic transit control: no newborn transits, one transit per pair per 2 rounds (same-pair doubles 0.37 vs 0.28; newborn transits 0.41 vs 0.25) | 0.5 | S-1 Q4 | sender-side rule on the prior base, measured on per-transit died-3 at equal transit volume (not a throttle: volume must hold) |
| L43 | Ally-crowding cost on targets (wt_ally −1.4) is a material/hygiene lever that needs a late-economy restorer | 0.5 | maelle-04: units/length@100 +0.043/+0.044 pool (medians; gen *means* −0.205 — sign depends on the statistic), every death rate down, gen p@250 −0.061, gen win −0.069 | `o-ally14` (running) on the prior base |
| L44 | The lane gate's economy clause measures what we want only if it (a) is paired-mean, (b) cluster-bootstrapped, (c) credits off-pool gains, (d) sees endgame conversion | 0.7 | §4 | the director's decision on G1–G6 |

## 3. Contradictions and their decisive tests

| # | Claims | Resolution so far | Decisive test (lane) |
|---|---|---|---|
| C1 | "Memory adds nothing" (TT/HB: history/trail +0.2–1.0 pp direction accuracy; Verso tier 1 ≤ 0.2 pp) vs "state is where the gains are" (D-035; Sciel-03a, Gustave) | Different things. The mimic evidence is *imitation accuracy* from the donor's own history; Verso tier 4 (our map memory → our hindsight advantage) is +0.6 pp R² offline; TT's remembered-map features (r/tt only) add +0.75–2.59 pp. The in-play "state" exhibit, Sciel-03a, was a flat value cut (Gustave 02b). The only state mechanisms that paid in play are symmetry (inferred map memory) and ally crowding (material). Memory of the *map* is live; memory of the dragon's *history* is not | Same-size Heartbreaker (or cheji bt) prior trained on v5 vs v5 + map-memory features (Verso's tier-4 block, computed by `world.hpp` in C++), D-032 both panels. **Verso** |
| C2 | L04 "flat bowl" (Maelle, Alicia ES at σ 0.2) vs Alicia s1c "not flat on the gate objective" (slopes |t| 2.9–4.2, curvature −0.003) | The bowl was measured with a curve reward whose material half is flat; the gate objective has slope but alicia-03's +0.02 training gain was a winner's curse on 1,052 games (−0.097 at the gate) | alicia-04 (gate-shaped reward) D-032 — running in **Alicia**; my bowl scan on the prior base is the cross-check |
| C3 | Lower exploration value pays (Renoir 07a +0.11 pool, Alicia slope against `unseen_value`, Gustave 08a gen +0.027) vs it is churn (Renoir 07c tempo NO GAIN, ally h2h up) vs cheji bt steers *toward* unexplored cells (+2.59 pp) | Hosts differ (V06+devil vs nodevil vs prior). Under the prior the direction choice is already shaped by a donor that explores | `o-unseen3` on verso-05 with tempo gate + corpse share. **Obscur (running)** |
| C4 | TT "top teams run a phase switch → L03 up" vs every phase remedy on our side failing (hb1-13, Verso belief, Maelle 2b, tt-06/07) | The top teams' switch is *conversion* (feed into one dragon, r250–300), which our gate cannot value (G4) and whose suicides our own-body guard rejects (G5). Our phase remedies were opening/fade knobs | State-keyed conversion trigger ("no enemy seen for N rounds" after r300) on verso-05, scored with the conversion term, opponent pool including the converters tt-05/08/10. **Verso** (has `l.*` late knobs) or **TT** |
| C5 | R-1 "late cap saturates at 384" vs the `min()` clamp at 160 | Code settles it: the effective cap is 160 | 160 vs 384 effective (clamp → override) on verso-05, D-032 late-phase. **Obscur** next, or Verso |
| C6 | Ally head-on mechanism: Sciel (arrival convergence at targets) vs Gustave/Aline (blind portal landings on mouths; 766/766 blind crossings) | Settled by Gustave's h2h anatomy on 02b: portal landings. Sciel-05 (target claims) aims at the wrong geometry | none needed; close |
| C7 | Trauma's starved opening: Aline (food behind portals → dive +0.333 on Trauma), Esquie (bed field in view, nothing ripe → wait), Renoir 22 (explore more, +0.11) | three remedies, three diagnoses, all local | first-pearl source attribution (bed vs portal-side ground) on Trauma replays of aline-23, esquie-03, renoir-22, then combine the starved gate with the winning action. **Esquie/M-1** or a desktop lane |
| C8 | D-037 weights maps by Elo slope² (Portals ≈ noise) vs S-1 Q2b/Q2c (Portals the most specialist map; slope ratio² 0.43) | Q2c is the author's own correction | inverse-variance weights from the paired local deltas across seeds 1–3 (G6). **Obscur** (gate code) |
| C9 | gustave-07c "HOLD, economy flat" vs pool mean −0.044 and material guards failing | statistic choice (median vs mean) | none: re-read (§0.1). Its re-test on the prior base is my arm `obscur-02-mouth` |

## 4. Gate audit (D-032 / D-036 / D-037)

**What the code does** (`tools/verso/lane.py`, `tools/rc/lane.py`, `tools/maelle/lane.py` — identical gate):
econ~ = mean over p@50/100/150/250 of [median(candidate) − median(parent)] on paired rows; bootstrap resamples
rows (seed × map × opponent × seat) i.i.d., 90 %; pool econ~ lb > 0; gen econ~ lb > −0.02; pool units, length lb ≥
−0.02 and win lb > −0.02 (no gen material or win guard); tier-2 = means of per-1k rates, point estimate, ignored
when the parent rate ≤ 0.05. `tools/rb/gate.py` (Aline) differs: per-game **mean** economy, gen guards applied,
cluster bootstrap reported but not gated. `tools/analysis/features/scorecard.py` — which BENCHMARKS (:16, :300,
:324) and the H-1 prompt call "the D-032 gate" — **does not implement D-032**: its `GATE:` line is BENCHMARKS step 4
(point Δecon ≥ +0.05, z1 only, `scorecard.py:219-240, 333-338`). Tempo is in no lane gate.

**Problems found, each with the proposed fix (G1–G6):**

- **G1 — statistic.** D-032 says "Δ(economy mean)"; the lanes gate a difference of medians. The two disagree in sign
  on gustave-07c pool (+0.001 vs −0.044), maelle-04 pool (−0.012 vs +0.025), and for material maelle-04 gen units
  (+0.052 median vs −0.205 mean). The median hides large per-map losses (07c Schooltime −0.32). **Fix:** gate on the
  paired per-game mean (D-032's text), report econ~ beside it.
- **G2 — bootstrap.** Seeds only move pearl respawns; 3/160 pool and 8/232 gen fixtures are identical across seeds, and
  W–L barely changes with the seed (hb1-12: 139–21 at both). Row resampling treats the three seeds of a fixture as
  independent → intervals too narrow by up to √3 on win. **Fix:** resample fixture clusters (map × opponent × seat,
  seeds together), as `tools/rb/gate.py:80-91` already does. Effect on lower bounds: −0.002 to −0.014.
- **G3 — panels.** Pool lb > 0 with gen lb > −0.02 means an off-pool-only gain can never pass and a pool-only gain
  (Renoir 07c, r3-03, aline-13's pool) can. That inverts the OOS rule and D-033's "close the pool–gen gap" — the
  tournament maps are unseen, so gen is the panel nearer the target. **Fix:** judge economy, win, units and length on
  the two panels **weighted equally** (combined lb: econ > 0; win, units, length ≥ −0.02), and fail any panel whose
  economy or win is significantly negative on its own (cluster ub ≤ 0). Apply the gen guards too.
- **G4 — endgame.** Economy stops at p@250; round-limit games (45–57 % of local games) are decided on length at r500.
  **Fix:** add a tier-1 endgame term, *conversion* = win rate among games that reach the round limit (paired, cluster
  bootstrap; columns `reason`, `result` already in `features.parquet`), as a guard (combined point ≥ −0.03) and as
  the score for the existing late-phase route (`--phase late`: accept on p@150/250 *or* conversion combined lb > 0,
  r100 clauses as guards). Report P(loss | round limit, material lead) and longest@499 as diagnostics — not gates:
  both are conditional on composition (a bot that eliminates more early leaves harder games at the limit;
  verso-01's longest@499 fell 6 while it won 15 pp more). Caveat stated in the code (`tools/obscur/gates.py`).
- **G5 — own-body guard vs chosen deaths.** The top ten's 4.6 suicides + 2.1 invalid per 1k are recycling; tt-05
  (level with hb1-12) and every feeder port failed only on own-body (+37–74 %). **Fix:** exclude deaths whose body was
  eaten by an own dragon within 3 rounds from the own-body/invalid rates when the change is a declared late-phase
  feeder mechanism; keep the raw rate as a diagnostic.
- **G6 — map weighting.** D-037's slope² weights rest on S-1 Q2 v1, which Q2c corrects (C8). Nothing implements them
  anyway. **Fix:** weight maps within a panel by the inverse variance of their paired deltas (from the parent's own
  seeds 1–3), capped at 3× the mean weight, *or* keep equal weights — not slope².
- **Not a fix, a fact:** `field_distributions.json` has no r25 reference, so D-037's r25 percentile cannot be computed
  from the frozen references; it needs the S-1 store, which is not on the desktop (no `build/s1`, no duckdb in
  `.venv`). Lanes on the desktop can run `tools/s1/tempo_gate.py` (no store needed).

**Re-scored history** (`tools/obscur/gates.py build/obscur/pairs.json`, 1,000 cluster resamples; full output in
`game_stats/runs/obscur/gate-audit-pass1.json`). NOW = the lanes' gate as coded; PROP = G1–G4 together.

| Pair | Recorded | NOW (re-run) | PROP | Combined econ (mean) [lb] | Combined win [lb] | Conversion [lb] | Flip |
|---|---|---|---|---|---|---|---|
| verso-01 vs verso-00 | ACCEPT | **REJECT** (gen econ~ lb −0.021) | ACCEPT | +0.066 [+0.017] | +0.100 [+0.067] | +0.022 [−0.032] | NOW is RNG-borderline; PROP keeps it |
| cycle 2 (540) vs cycle 0 | REJECT (letter) | REJECT (pool econ~ lb −0.025, pool win lb −0.030) | **ACCEPT** | +0.066 [+0.037] | +0.049 [+0.022] | −0.024 [−0.073] | **flips to accept**: off-pool econ +0.107, win +0.097 |
| verso-05 vs cycle 2 | lane parent by lead's call | REJECT (pool econ~ lb −0.038, units −0.103) | REJECT (combined units@100 lb −0.045) | +0.032 [+0.011] | +0.028 [+0.007] | **+0.091 [+0.040]** | same; the gain it does have is conversion |
| verso-05 vs cycle 0 | (not run as a gate) | REJECT (pool econ~ lb −0.047, units@100 lb −0.048) | **ACCEPT** (also late route) | +0.098 [+0.066] | +0.077 [+0.047] | +0.068 [+0.014] | **the lead's decision is what PROP would have decided** |
| gustave-07c vs 01 | HOLD | REJECT (pool econ~ lb −0.017; units/length lb −0.060/−0.053) | REJECT (pool mean ub −0.024) | −0.016 [−0.030] | +0.024 [+0.003] | +0.037 [−0.004] | **HOLD → REJECT** (registered at 505) |
| gustave-08a vs 01 | REJECT | REJECT | REJECT (win, units, length, tier-2) | +0.043 [+0.018] | −0.010 [−0.038] | +0.003 | — |
| maelle-04 vs 02 | REJECT | REJECT | REJECT | −0.006 [−0.035] | −0.024 [−0.054] | +0.002 | — |
| maelle-03 vs 02 | REJECT | REJECT | REJECT | −0.021 [−0.043] | −0.028 [−0.055] | +0.033 | — |
| verso-06 vs 05 | REJECT | REJECT | REJECT | −0.035 [−0.061] | +0.022 [+0.001] | +0.023 | — |
| alicia-03 vs 01 | REJECT | REJECT | REJECT | −0.046 [−0.071] | +0.007 [−0.021] | +0.050 | — |

Not re-scorable from desktop data: aline-17 (rb's runs keep JSONL summaries without `reason`/`longest`; its own gate
reports mean form [+0.005] plain, [−0.000] cluster — under PROP its pool clause is a boundary result, its gen +0.012
helps the combined form), esquie-03b (GLM host), hb1-12/13 (z1 only, no gen panel). Reading: **PROP flips three
verdicts, all in the direction the director or the lead already went by judgment** (keep the big prior; keep
verso-05; nothing is lost from verso-01), and one against a registration (07c). No REJECT becomes an ACCEPT
through the endgame term alone.

## 5. Ranked ten (weight × size of problem × cheapness of the decisive test)

| # | Row(s) | Experiment that moves it most | Lane | Cost |
|---|---|---|---|---|
| 1 | L44 (gate) | adopt G1–G4 (code exists in `tools/obscur/gates.py`; port into the shared gate) and re-issue verso-05 / cycle 2 / 07c verdicts | director → Obscur | hours, no games |
| 2 | L39, C4 | state-keyed conversion trigger ("no enemy seen ≥ N rounds", r ≥ 300) on verso-05, scored on conversion; opponents incl. tt-05/08/10 | Verso (late `l.*` knobs exist) | 1 arm |
| 3 | L38, L40, L43, bowl | the running first pass (9 arms) | Obscur | running |
| 4 | L01/L25, C5 | effective late cap 160 vs 384 (clamp → override) on verso-05; V09's 80 as a third point | Obscur | 2 arms, one-line change |
| 5 | L27, C1 | prior on v5 vs v5 + map-memory features, same size | Verso | 1 training + 1 arm |
| 6 | L42 / L33 | own-traffic transit gate (newborn ban + same-pair 2-round) on the prior base, volume held | rc (Gustave) if revived, else Obscur | 1 arm |
| 7 | L36 / L41 | early portal use as a structure-gated opening switch, tempo gate per map | M-1 / per-map lane | 1–2 arms |
| 8 | L35 | port esquie-03b onto verso-05 as a switch; settle C7 by first-pearl attribution on Trauma | Esquie or Obscur | replay analysis + 1 arm |
| 9 | L10 | refuse contact when nearest known bed > 6 (C2-0's rule), on verso-05; measure length lost per fight | any desktop lane | 1 arm |
| 10 | L09 | decode Cache me outside's sonar payloads against its state (TT says state-dependent) | TT | analysis only |

Held, not ranked: L04 (alicia-04 reading), L30 (needs the churn paid down first), L31–L32 (need the hard-mode
version built; nothing cheap moves them).

## 6. Housekeeping notes for the director

- Track A V28–V37 have no `(T)` rows (the teammate procedure at HYPOTHESES:70-80 requires them): V28/V32 (split
  size) → L24; V33 (newborn portal-edge handoff) → L30/L42; V36/V37 (no-pearl portal value 8/6, 13–7 and 17–3 vs
  V35) → L14, against Aline-23; V35 (crown threat, 38–42) → L39. All 20-game screens: directional.
- Monoco "holds" ra-09 (units −0.032, win −2.5 pp) and ra-10 (win −2.0 pp) are not hygiene-only holds under D-032.
  L20's promised D-032 re-score of ra-03/ra-05 was never run.
- Gustave's proposed "L30 (new)" collides with the existing L30; it belongs in L31's evidence.
- BENCHMARKS (:30-32, :286) and `s1-T-tempo-metric.md` attribute "+0.11" and "ally h2h +42 %" to Renoir 07c; 07c was
  +0.061 [+0.026, +0.090] (h2h +22 %); +0.110 / +51 % is 07a.
- `docs/TAXONOMY.md` (T-1) and an S-1 status file do not exist on any ref; the H-1 prompt lists both.

## Resume

```sh
cd ../wt-obscur
tail -f build/obscur/logs/queue.log                      # queue.sh (8 arms) + queue2.sh (obscur-03), nice 10
.venv/bin/python tools/obscur/lane.py score <arm> --parent verso-05-hb800-prior --seeds 1   # any arm, any time
.venv/bin/python tools/obscur/gates.py build/obscur/pairs.json   # add a pair to re-score it NOW vs PROP
```
