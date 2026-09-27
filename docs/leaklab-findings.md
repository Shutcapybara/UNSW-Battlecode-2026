# Leak lab: what the parquet says the top bots are missing (2026-09-26)

Data: 76,552-game ledger (`game_stats.parquet`: bot_field_tournament 38.2k,
benchmark 22.6k, compare_bot 13.7k, leviathan_lab 2.0k), map topology metrics
(`tools/leaklab/map_meta.py`), direct local runs (`unswbc run`, engine
deterministic per fixture), and the lineage handoffs.

## 1. Map taxonomy (from engine map files, `tools/leaklab/map_meta.json`)

| Map | Size class | Spawn dist | Corridor% | Fast beds | Portal pairs |
|---|---|---|---|---|---|
| arena | tiny (121) | **4 (instant)** | 3 | all (gap 20) | 0 |
| default_small / Colosseum | small (256) | 20-21 | 3-8 | none / none | 0 / **4** |
| trophy | small (625) | 16 | 10 | none | 1 |
| devil | medium (512) | 31 | **24** | **18 center** | 0 |
| dilemma | medium (512) | 34 | 8 | 12 center | **4** |
| queen_of_spades | medium (875) | 36 | 23 | none | 2 |
| default | large (1024) | 50 | 5 | none | **12** |
| autarky | large, narrow (972) | **52** | 7 | 14 | **8** |
| stronghold / trauma | large (1152) | 60-64 | 12 / **29** | 0 / 12 | 4 / 6 |
| schooltime | huge (2400) | 13 (maze) | 18 | none | 12 |
| big_empty | huge (4096) | **88** | 0 | none | 0 |

## 2. The divide is systematic — three axes, not one

Head-to-heads (ledger, ≥20-game pairs) flip direction **by map class**, consistently
across opponents. The same lineage that dominates one class is a punching bag
in another; every leak below reproduced in fresh local runs (2026-09-26).

**A. Production doctrine — compact/fast-bed maps (arena, devil, dilemma).**
The swarm producers (ouroboros-v13, tew-v12, gavroche) beat the careful
evaluators (sinbad/serre, leviathan, hunter) exactly where pearl income is
fast and bodies stay in contact:
- devil, serre vs ouroboros-v13 (both sides, fresh runs): serre **eliminated**
  at rounds 326-451 while v13 trades 503 dragons away. Ledger H2H v13 4-0.
  Baseline screen fixture: **serre 197 pearls vs v13's 1,509; 72 splits vs 522.**
- Round 251 dragon counts on devil: serre 7 vs v13 **53**.
- arena, serre vs tew-v12: serre eliminated at round 52, losing every
  head-to-head after being out-grown 2× by round 20 (tew ends with 26 dragons).
- The mechanism is not subtlety: fast beds fund `SPLIT 2` every time a dragon
  reaches length 4, and unit-count superiority wins melee trades + holds beds.
  Serre's conservative split policy (split_val 4.0, split_stop 380, ceding
  beds an enemy head is closer to: `enemy_disc 0.6`) donates the center.

**B. Big-open / low-contact maps (big_empty, autarky, schooltime).**
The reverse: careful evaluators + dispersion win. serre/sinbad-v06 win
big_empty 85-93% vs the field; gavroche-v17 (density-gradient control) beats
serre on big_empty **both sides** on length at round 500 — information/control
gradients are the only measured big-map edge over the sinbad evaluator.
Low-contact maps (autarky, dilemma, spawn dist 34-52) punish flat portal-risk
pricing: monte_christo-v01 sat frozen in portal boxes (dilemma 12%!) until
valjean-v01 priced unseen exits by sighting memory (dilemma+autarky 3-21 → 14-10).

**C. Portal maps (Colosseum, default, dilemma, autarky).**
Winners carry paired-portal sharing + dive caps (sinbad v07: portal maps
36-20 → 45-11) or scout-with-return-plan (hunter-v22). ouroboros-v13's ladder
has no portal risk model — it goes 0-6 vs serre on Colosseum while winning
devil 4-0: **the compact-map winners and the portal-map winners are different
bots because the two mechanisms were never combined.**

## 3. Leak inventory per named line (what each is missing)

| Line | Strong on | Missing (evidence) |
|---|---|---|
| sinbad/serre (e23) | big maps, portals, threat model | compact production + contested fast beds (devil 2-6 screen, arena 5-9 gauntlet; pearls 197 vs 1509); melee support (arena H2H losses to tew) |
| gavroche (v17/v32) | arena/dilemma/autarky (production + density), big_empty via gradient | default_small (12% — v17), portal risk memory late; long-dragon safety in melees |
| monte_christo/valjean | portal-exit memory (valjean), dilemma/autarky | compact production (arena 39-46%); arrival-aware economy on base MC; round-500 length stalls (36/55 losses) |
| ouroboros-v13 | devil 97%, arena 91%, dilemma 87% (compact ladder) | portal risk (Colosseum 32%, queen 39%, trauma 42%; 0-6 vs serre there); open-map evaluator is old v10 — loses big maps to serre |
| tew-v11/v12 | arena 86-92%, devil 84-87% | queen_of_spades 41-47% (portal+corridor), trauma 57%, mid-map economy vs evaluators |
| leviathan-v09 | field 73%, schooltime 91% | the sinbad threat model owns it head-to-head (2-20); no compact doctrine |
| hunter-v22 | arena/Colosseum, big maps | no feeding endgame (loses length races), melees vs swarm producers |
| vn/godel line | Colosseum/trauma/queen ~100% | devil catastrophic (8-33%): the whole line lacks a fast-bed answer |

**Is it systematic?** Yes, in the strict sense: each line's wins and losses
cluster by map class with the same sign across different opponents, because
each line tuned its one doctrine on a pool that over-represented its own
strong maps. Nobody ships both (a) a compact-map production/contest doctrine
AND (b) a portal-risk/dive-cap information layer AND (c) an arrival-aware
evaluator with crown/feeding. The chassis that carries (b)+(c) best is
serre-v01 (sinbad e23) — 134-48 gauntlet, wins every top-tier H2H except
compact maps.

## 4. The composite (fafnir): mechanisms grafted, each default-off

| Mechanism | Source (evidence) | Closes |
|---|---|---|
| period-aware bed value `bed_per_k` | serre G1 diagnosis: 4-7× pearl deficit on devil | A |
| fast-bed contest pricing `fast_edisc` | same: enemy-closer discount cedes center | A |
| compact production `compact_nc/unit_target/prod_boost` | ouroboros-v13 (devil 97%, arena 91%); tew | A |
| strike support bonus `strike_support` | tew-v11/v12 (arena 86-92%), gavroche-v32 | A |
| portal-exit risk memory `blind_mem` | valjean-v01 (dilemma+autarky 3-21 → 14-10) | B, C |
| allied threat discount `threat_ally` | tew support semantics; Lanchester counter-trade | A |

Gates: the serre frozen selection rule (screen +2, no map cell worse than -2;
gauntlet +3; reserve +1; judge clean). Baseline = serre-v01 screen 23-9
(devil 2-6), gauntlet 134-48 (arena 5-9, devil 2-12), reserve 13-3.

## 4a. Arm ledger (32-game screens, paired per fixture vs baseline 23-9)

| Arm | Mechanisms | Screen | Verdict |
|---|---|---|---|
| f2-prod | compact production boost only | 24-8 (+1), no regression | devil games byte-identical: the boost never won the argmax — serre's split *gates* (ambient threat re-charge, 4-cell newborn pocket, w_trap parent penalty) are the binding constraint |
| f2 gauntlet | — | **136-46 (+2)** of 182 | below the +3 gate; arena −1, devil +1, trophy +1 |
| f1/f1b-contest | period-aware bed value | 20-12 / 13-16 (**-3/-7**) | dead: slow-bed floor fix was not enough; early `bper` underestimates periods and the boost poisons the value field (queen/trauma collapse). Do not retry in this form |
| f3-support | strike support bonus | 23-9 (+0), every fixture identical | inert: serre strikes are value-gated before the bonus; tew's mechanism is a *gate*, not a bonus |
| f4-blindmem | portal-exit risk memory | 23-9 (+0); queen +1, Colosseum −1 | neutral here; its valjean-proven maps (dilemma/autarky) are not in the screen — gauntlet decides |
| f7-splitfire | f2 + split-no-threat | 24-8 (+1), devil +1, no regression | the ambient-threat re-charge on the split branch was blocking compact splits |
| f8-solid | f7 + threat_ally 0.25 (global, self-centred) | 24-8 (+1) | — |
| **f9-flood** | f8 + compact_child gate relaxation | **25-7 (+2), zero map regression** | **first arm through the screen gate**; devil 3-5 (+1), trauma 7-1 (+1) |
| f9 gauntlet | — | 103-36+ at 139/182, schooltime +3 but **stronghold −4** | global self-centred support underprices threats to long dragons on open big maps → fails the per-map check |
| f10-gated | threat_ally gated to compact maps | 24-8 (+1) | safe but loses f9's trauma flip |
| f11-counter | support counted around the ATTACKER (counter-threat), global | **26-6 (+3)**, devil 5-3 (+3) | screen gate cleared; gauntlet **134-48 (+0)**: big_empty −3 — endgame feeders cluster at the crown and "support" it against attackers they cannot deter |
| **f12-sizematch** | f11 + support counts only allies ≥ attacker length | **25-7 (+2)**, devil 4-4 | **RELEASED as bots/fafnir-v01-phalanx** |

**f12-sizematch final records (the release):**

| Set | Record | Detail |
|---|---|---|
| Screen 32 | **25-7** [23-9] | +2, no map cell regressed; devil 4-4 [2-6] |
| Gauntlet 182 | **140-42** [134-48] | **+6**; devil 5-9 [2-12], arena 6-8 [5-9], schooltime 13-1 [11-3], big_empty/stronghold 14-0 held, worst cell default_small 11-3 [12-2] |
| Reserve 16 | 13-3 [13-3] | all 16 fixtures byte-identical to baseline (the active mechanisms never fire on the frozen families); the strict "+1" promotion gate is not met — recorded |
| Judge sandbox | clean | 0 TLE / 0 faults / 0 errors (2-2 vs hunter-v22) |

 devil vs ouroboros-v13 head-to-head inside the gauntlet: 1-3 (was 0-4 for
 every sinbad-family version). The compact-map doctrine closed most of the
 devil gap and bought arena/schooltime without paying anywhere.

**Key diagnostic (why naive production grafts did nothing):** on devil the
foundation's split branch re-charges the ambient enemy-head threat at the
parent's position, and demands a 4-cell newborn pocket — under swarm contact
both gates fail almost every turn, so serre made 72 splits per devil game vs
v13's 522 and the +2 score boost changed literally nothing (fixtures
byte-identical). The production doctrine only engages once the split branch
stops double-charging risk the parent faces on every branch anyway
(`split_nothreat`) and accepts a 3-cell newborn pocket on compact maps
(`compact_child`).

## 5. What is still missing after fafnir (ranked, unmeasured)

1. **Map-symmetry inference** (serre G3): mirror own-half knowledge; the FX/FY
   robustness hole (~50% vs 75%) and slow enemy-half bed discovery.
2. **Endgame transition for the length race** (serre G5, avery-v08's crown
   banking): round-500 stalls cost valjean 36/55 losses; avery beats the
   French line 4-0 with scheduling alone.
3. **Tunnel/dead-end pricing** (ouroboros `w_tunnel`, valjean `dead_end_disc`)
   for trauma/queen_of_spades-style mazes — serre's flat `min_area 5` is the
   weakest safety term on 29%-corridor maps.
4. **Length-density radio** (javert: only radio graft that ever survived a
   fresh reserve, 10-2, all confined-map conversions).
