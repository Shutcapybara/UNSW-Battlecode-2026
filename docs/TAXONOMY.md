# Taxonomy of the problem and opportunity space

**Owner:** T-1 (lineage `t1`, branch `r/t1`) · **Snapshot:** `main` at `9315914c9` plus the unmerged lane branches
(`origin/r/{esquie,monoco,ra,sciel,r3,r4}`, `origin/cx/*`, `origin/{pace,glm,sakura,yeji,chaewon,kazuha,gpt}/*`,
`origin/analysis/a1`) and the claude.ai project status files, read 30 Sep 2026 06:30 UTC · **Entries:** 40 F · 27 A ·
25 P · 62 S, each with a detail file in [`docs/taxonomy/`](taxonomy/).

This is a map of objects, not a log. The findings and the decisions file say *when* something happened; the ledger
(`docs/hub/HYPOTHESES.md`) says *what we believe*; this file says *what exists* — every feature the bots compute, every
decision design, every named failure class, every mechanism thrown at one — and cross-references them, so that "has this
been tried, on what, with what result, and why did it stop" is one lookup. Entries state what was measured, never whether
it is good.

**How to read an entry.** Ids are stable and never renumbered (`F-` feature, `A-` algorithm design, `P-` problem, `S-`
attempted solution; `F-40+` are analysis-side). Every row links to `taxonomy/<id>.md`, which carries the pointers
(file and section, or bot path and line), the full evidence table, discrepancies and a change log. Ledger rows are `Lnn`,
decisions `D-nnn`. Host marks in §4: ● measured on the Ares C++ line (the production line since D-029), ◐ on Ares and
elsewhere, ○ only on Python hosts, the cx chassis or older lines. Verdict codes in §5: A accept · H hold · LH local hold ·
R reject · N never measured · D dropped · U in use · O built, off · Op open · C closed.

**Reference for building:** [PIECES-AND-PUZZLES.md](PIECES-AND-PUZZLES.md) — the same material reduced to pieces,
puzzles and the information-horizon ladder. **Registers** (detail too large for this page): [map × mechanism](taxonomy/map-mechanism.md) (553 rows) ·
[contradictions](taxonomy/contradictions.md) (C-01…C-84) · [dead code, dimension-keyed terms, never-measured and
undelivered work](taxonomy/dead-and-unmeasured.md) · [full matrices](taxonomy/matrices.md).

**Three facts that shape everything below.** (1) The production bot is Ares V06 (a C++ port of Python Tyr V12) and its
lanes; it uses 8.6 M of a 100 M CPU budget, so every line that stopped on the Python CPU wall stopped for a reason that no
longer holds. (2) On this lineage every hygiene gain bought with caution has cost economy about one for one (D-035), and
every economy gain of +0.05 or more measured so far has been blocked by the ally head-on guard ([P-04](taxonomy/P-04.md)). (3) The
measurement layer itself carries known defects — seed noise larger than the old gate, two scorecards 20 % apart on the
same games, dead parameters measured as mechanisms ([P-19](taxonomy/P-19.md)–[P-21](taxonomy/P-21.md)).

## 1. State and features

### 1a. Bot-side state (what a dragon knows)

"In Ares" = present and live in Ares V06 and its lanes' bases. Consumers are algorithm designs (§2).

| Id | Feature | Lineages | Consumers | In Ares | Evidence it matters |
|---|---|---|---|---|---|
| [F-01](taxonomy/F-01.md) | Terrain edges, kelp and the dest table | all planning bots (Python hosts, ares/V06 lanes, anna/cx) | A-02, A-04, A-08, A-09, A-10, A-19, A-20 | yes | r3-04 kelp-edge cost econ -0.072, wall -27% |
| [F-02](taxonomy/F-02.md) | Portal pairs (pair table, radio type 5, 2·NC≤8192 gate) | SIN/MC hosts, ares/V06 lanes, ouroboros | A-02, A-04, A-10, A-12, A-13, A-17 | yes | sinbad e11 portal sharing 44-10 vs 43-11 |
| [F-03](taxonomy/F-03.md) | Seen-age and sector-unseen (incl. dead v_stale) | SIN/MC hosts, ares/V06 lanes | A-02, A-03, A-09, A-10, A-13, A-17 | yes | nothing on seen-age itself (unseen_value sweeps are A-03); v_stale dead |
| [F-04](taxonomy/F-04.md) | Pearl memory (memory_ttl; dead pearl_ttl; confirmed-only) | all hosts, ares/V06 lanes, ouroboros, leviathan | A-02, A-03, A-04, A-05, A-13 | yes | TTL moves small: renoir-08a -0.013, ra-05 +0.0024; ra-04 exactly 0 (dead) |
| [F-05](taxonomy/F-05.md) | Bed timing (bed/spawn_at, bed_wait=0, bed_stale, bper, respawn-gap memory) | all hosts, ares/V06 lanes, cx-b02 (gap memory) | A-02, A-03, A-04, A-09, A-12, A-13, A-14, A-19 | yes (future-bed branch off) | arrival rule leviathan-v09 22-8 vs 15-14; renoir-01a/c -0.06 |
| [F-06](taxonomy/F-06.md) | Other-dragon memory and vacancy (parts/vac, DragonMem, hidden_tail) | SIN/MC hosts, ares/V06 lanes | A-02, A-04, A-10, A-11, A-14 | yes | nothing isolated |
| [F-07](taxonomy/F-07.md) | Own body / trail reconstruction (incl. newborn neck) | all bots; neck fix chaewon/sakura | A-02, A-04, A-06, A-07, A-08 | yes | opening rescue for incomplete bodies gavroche-v02 13-3, scholze-v02 24-12 … |
| [F-08](taxonomy/F-08.md) | Visit counts (anti-dither) | SIN/MC hosts, ares/V06 lanes | A-04, A-09 | yes | renoir-18a pooled +0.015 [-0.006,0.033] null |
| [F-09](taxonomy/F-09.md) | Room flood (time-aware flood_room, flood_need, caps) | SIN/MC hosts, ares/V06 lanes, anna/cx, ouroboros | A-04, A-06, A-07, A-08, A-19, A-20 | yes | renoir-12a min_area 8 -0.183; ra-01 trap 60 -0.084 |
| [F-10](taxonomy/F-10.md) | Five-step body-blocked reach / enclosure | ares-v13..v33, esquie-04, cx-f01; F1/C1-C analysis | A-04, A-07, A-08, A-27 | V13+ teammates; esquie-04 (off) | ≤8 hazard 650-695/1k (6-7x); v19 11-9; esquie-04 econ -0.035 |
| [F-11](taxonomy/F-11.md) | Threat map and support counts | all hosts, ares/V06 lanes, ouroboros, kraken, hydra | A-02, A-04, A-05, A-06, A-10, A-11 | yes | fafnir f12 size-matched support gauntlet +6; renoir-17d threat 0 +0.019 n.s. |
| [F-12](taxonomy/F-12.md) | Ally/enemy density fields (local EWMA + radio reports) | MC/gavroche/yuna/tyr hosts, ares/V06 lanes, drake, javert, VN | A-03, A-04, A-12, A-13, A-16 | yes | javert x02 info layer 10-2; consumers null/negative (ra-07 -0.017) |
| [F-13](taxonomy/F-13.md) | EW food-density memory (sciel food_ew) | sciel-03a..04b | A-03, A-17 | no (sciel branch) | sciel-03a econ +0.067 (h2h_ally +34%) |
| [F-14](taxonomy/F-14.md) | Direction momentum (EWMA of first steps) | yuna, tyr, ares/V06 lanes, ein-dog | A-04, A-14 | yes | yuna +6, plateau at 0.6; never varied on Ares |
| [F-15](taxonomy/F-15.md) | Target hysteresis memory | SIN/MC hosts, ares/V06 lanes, ouroboros | A-02 | yes | ra-06 hysteresis 1.75 econ -0.0435 |
| [F-16](taxonomy/F-16.md) | Crown / feeder / prey state | all hosts, ares/V06 lanes, ouroboros, hydra, hunter, avery | A-03, A-04, A-06, A-12, A-13, A-14 | yes | ouroboros crown/feed/beacon series 219-42 -> 238-23; hunt_from inert on Ares |
| [F-17](taxonomy/F-17.md) | Newborn escape state and split handoff / birth certificate | fenrir/tyr/ares separation; S1 certificates; ouroboros K_HANDOFF | A-04, A-09, A-10, A-12, A-13, A-14, A-26 | yes | cert delivery 35-49%; kazuha newborn 24.7 vs 27.9%; ra-09 +0.011 hold |
| [F-18](taxonomy/F-18.md) | Portal transit and exit memory | host blind_mem; cx-f02; r3; sciel-02a; yeji; tyr-v08 | A-04, A-09, A-10, A-12 | no (r3/sciel switches off; last_exit unread) | pre-entry forms throttle volume: r3-02 steps -68% econ -0.120; valjean 3-21 -> 14-10 |
| [F-19](taxonomy/F-19.md) | Sonar echo counts | heimdall, hydra-v06, kraken-v05, cx-f02, chaewon-y04, r3-02, m01 … | A-02, A-03, A-04, A-10, A-11, A-12, A-23 | stored, unread | heimdall v10 panel 91-59; chaewon-y04 probe +0.062 n.s. |
| [F-20](taxonomy/F-20.md) | Sonar packet layout (team tag, types 1-9, 64-bit) | all radio-using lineages | A-12, A-13 | yes | sinbad food gossip +3; javert length packets 10-2; Riptide radio off 4-20 vs on 2-22 |
| [F-21](taxonomy/F-21.md) | Atlas / public-map prior | anna/cx, cx-b router, ares-v01/v02/v08, chaewon, pace, sakura-s02, yej … | A-02, A-03, A-10, A-17, A-19 | dead code | ares-v08 econ +0.188 (ally h2h +205%); off-pool inert |
| [F-22](taxonomy/F-22.md) | Map dimensions and size thresholds | every bot; identity terms in tyr/ares/V06 lanes, S1 lines, jet | A-04, A-10, A-12, A-13, A-14, A-16, A-17, A-18, A-19, A-23, A-25 | yes (32×16 terms live in V06..V33; off in lanes) | renoir-23 nodevil econ -0.042, Devil win 1.00 -> 0.31 |
| [F-23](taxonomy/F-23.md) | Game clock, phase and unit-count state | all bots | A-02, A-04, A-05, A-06, A-10, A-14, A-15, A-24, A-26 | yes | lune-r1-07 late cap econ +0.026; yuna t1 60 vs 120 (-3) |
| [F-24](taxonomy/F-24.md) | Dead-end peel / 2-core trees and doom memory | cx-b01/b02 router, ouroboros, kraken-v05 | A-04, A-06, A-12, A-13, A-19 | no | K_DOOM devil 4-10 vs 7-7 (+2 bench); kraken nodoom = other ablations |
| [F-25](taxonomy/F-25.md) | Arrival maps (own/enemy/ally BFS arrival times) | cx-b01/b02 router only | A-19 | no | router length r100 176/3/61 (atlas ~2/3); units n.s. |
| [F-26](taxonomy/F-26.md) | Mode / role state (roles at birth, modes) | host roles; ouroboros slices; kraken/hydra birth roles; estuary; gaia | A-04, A-06, A-14, A-17, A-21, A-24, A-26 | partial (crown/feeder/escape flags) | orphan_role=1 -11 net compact; kraken newborn deaths 28.0% vs 15.1% |
| [F-27](taxonomy/F-27.md) | Learned-feature vectors | ouroboros-m01, loki, clone-62, team-recon v4, MC hazard | A-11, A-23 | no | m01 accuracy 0.739 (ceiling ~0.74); zoo 51-53 |
| [F-28](taxonomy/F-28.md) | Pearl ownership / claims state | Ares/host discounts; fry-v13/v14; hunter; bifrost; riptide; router … | A-03, A-12, A-13, A-16, A-19 | discounts yes; claims no | renoir-06a owndisc 0 econ +0.021 win -0.113; avery-v03 74-35 vs 70-39 |

Features computed but consumed by nothing on the production line: echo counts ([F-19](taxonomy/F-19.md); read only by
cx-f02, r3-02 and Python/model lines), the atlas ([F-21](taxonomy/F-21.md); `atlas_try` never called after V02 except
V08), `DragonMem.cell/facing/first_round`, `last_exit_*`, `seen_count` and the sonar type-3 receiver (nothing sends it).
Built but living only off the production line: the dead-end peel and arrival maps ([F-24](taxonomy/F-24.md),
[F-25](taxonomy/F-25.md); cx router), respawn-gap memory (cx-b02 inside [F-05](taxonomy/F-05.md)), EW food density
([F-13](taxonomy/F-13.md); Sciel branch), portal transit memory ([F-18](taxonomy/F-18.md); switched off). Dead V06
parameters: `pearl_ttl`, `bed_wait_max`, `bed_tie`, `ally_yield`, `dive_cost`, `dive_min_age`, `blind_landing_penalty`,
`search_depth1`, `keep_facing_bonus`, `visit_ttl_count` (anna-chassis leftovers); constant switches `bed_wait = 0`,
`head_block = 0`. Python hosts carry the unread `v_stale` in every copy.

### 1b. Analysis-side features (what we measure bots with)

| Id | Instrument | Lineages / users | Consumers | Evidence | Status |
|---|---|---|---|---|---|
| [F-40](taxonomy/F-40.md) | Economy curve, map-normalised (econ~, p@k) | analysis; ra/renoir, monoco, sciel, R-4, lune, esquie | A-27 | map share 0.74 -> 0.13; seed shift +0.071 > gate bar | in use |
| [F-41](taxonomy/F-41.md) | Three-number form and field references | analysis (BENCHMARKS, F1) | A-27 | percentile map share 0.22 vs 0.45 | in use |
| [F-42](taxonomy/F-42.md) | Tier-2 hygiene rates and newborn10 | analysis; all lane scorecards | A-27 | ICC 0.91-0.98, rating rho ~0; guard decided sciel-03a, renoir-07a | in use |
| [F-43](taxonomy/F-43.md) | Efficiency ledger and leak classes (C1-C; r3_ledger) | analysis; cx-c01, r3, sciel | A-27 | team 7 - band Portals trapped +62.6 len/1k; V06 carries profile | in use |
| [F-44](taxonomy/F-44.md) | Portal-step walk (C1-D) | analysis; cx-d01, r3, cx arena | A-27 | 28.2 vs 12.5 deaths/100 steps (team 7 vs 306); basis of D-035 | in use |
| [F-45](taxonomy/F-45.md) | F1 feature lab (237 features) | analysis (tools/analysis/features) | A-19, A-27 | territory@100 +1.5-1.8 log-odds/sd; EPG/HMM no consumer | in use (V4/V5 not run) |
| [F-46](taxonomy/F-46.md) | Fight anatomy (C2) | analysis | A-27 | team 7 32.9 vs band 18.9 length lost per fight; rules never built | in use (diagnostic) |
| [F-47](taxonomy/F-47.md) | Pace targets and live bed maps (C1-E) | analysis; pace-v01..v03 (precursor curve) | A-06, A-27 | pace controller -0.008 (360 pairs); live beds unconsumed | in use (no bot consumer of C1-E files) |
| [F-48](taxonomy/F-48.md) | Map signature and brick list (esquie 21 features) | esquie, leaklab; S1 bot-side signatures | A-14, A-18, A-27 | gen suite lacks pool brick motifs; kazuha/sakura early onset -4 Portals/Slithery | in use |
| [F-49](taxonomy/F-49.md) | Scorecards, panels and parity harnesses | R-4, ra/monoco/sciel lanes, lune, cx golden, ouroboros/leviathan/jet t … | A-01, A-27 | R-4 reproduces V06 exactly; caught r3-03 v1 inert wiring | in use |
| [F-50](taxonomy/F-50.md) | Outcome models and ratings | analysis (ratings, frontier, pace, S1, replay studies) | A-27 | local vs live Spearman +0.10/-0.20; frontier all 16 undominated | in use (ratings barred from queue) |
| [F-51](taxonomy/F-51.md) | Corpus and team-recon pipelines | analysis (team_recon claude/codex/GLM, hub) | A-23, A-27 | 2,361,735/2,361,735 steps exact; replay-drive 1,195,129 exact | in use |

Analysis outputs with no bot or gate consumer: the F1 HMM phases, EPG, `density_ratio` ([F-45](taxonomy/F-45.md)); the
live bed maps `game_stats/live_beds.json` (bots' atlases use the local map files, which differ on Schooltime 326 vs 444
beds, Slithery 339 vs 497; [F-47](taxonomy/F-47.md)); the fitted-Q tooling ([S-55](taxonomy/S-55.md)). F1 validation steps
V4 (own-bot logs) and V5 (toggle tests) never ran.

## 2. Algorithm designs

Ares V06 decides each turn in this order (`policy.hpp:1129-1438`): hear radio → threat map → visits → search cap → target
BFS → hysteresis / far target / hunt → escape plan → candidate paths → score → split options → escape split → momentum;
the whole decision sits inside a catch-all fallback ([A-01](taxonomy/A-01.md)). "Never varied" lists parameters no lane
has moved (Ares lanes for the C++ designs).

| Id | Design | Lineages | Varied (by whom) | Never varied | Status |
|---|---|---|---|---|---|
| [A-01](taxonomy/A-01.md) | Turn loop and validity wrapper | Ares V01–V33+desc; Python MC/SIN hosts; gaia; m01/Vibing SPLIT 1 | V04 re-thrown exceptions→V05 fix; gaia v61/v62 fallback order; s02 host fixes | fallback rule (first OK dir, no radio); indicator; stage order | in use |
| [A-02](taxonomy/A-02.md) | Bounded target search | Ares/Tyr/SIN/MC; ouroboros; kraken; leviathan | search_cap 72→160 (V06), 256/96/80+frontier 6 (V09/robert), lune ×2/×4/×8, late 384/sparse 512 (lune-07), 100000 (lune-0 … | search_cap_late_from 40; sparse_from 150; sparse_units 20; saturation 0.7; sector 8; vmax rule | in use |
| [A-03](taxonomy/A-03.md) | Target valuation (cell_value) | Ares/Tyr/SIN/MC; ouroboros; kraken; router | pearl_value (ra-10); unseen_value (07a–d, 25); own_target_discount (06a/b); bed_wait (01a–c, esquie); bed_value (ra-08) … | memory_value; enemy_target_discount; dive_value (post-V04); bed_stale … | in use |
| [A-04](taxonomy/A-04.md) | Move scorer (candidate paths × terms) | SIN/MC/Tyr/Ares; ouroboros; leviathan; kraken; hydra-v11 | sprint_cost (ra-03); crowd_weight (09a/b); visit_weight (18a–c); trap_weight (14a/b, ra-01); trap_farm_factor (03a/b) … | goal_weight; momentum_weight/decay; material_unit_value; lv_end; trap_value_reference; w_bed_block … | in use |
| [A-05](taxonomy/A-05.md) | Sprint candidates and sprint discipline | Ares/Tyr/SIN/MC; the-goat; cx-f03; ouroboros; Riptide | sprint3_limit 10→12 (V06), lune ×2..×8 and 06; sprint_cost 1.5 (ra-03); w_sprint 1.5/2.0 (the-goat) … | sprint3_late_from 150; near-threat Chebyshev 4; len≥3 gate; no food sprints in Ares | in use |
| [A-06](taxonomy/A-06.md) | Routine and opening splits (production) | Ares/Tyr/SIN/MC; ouroboros; kraken/hydra; fry/hunter; porthos; router | split_value (05a/b); child_area (02a/b, ra-02); opening_production_until (10a/b); sciel-01a siting; tyr-v30 … | split_min_len 4; split_child 2; split_until_round 380 … | in use |
| [A-07](taxonomy/A-07.md) | Emergency / escape split (all moves dead) | Ares/Tyr/SIN/MC; ouroboros; fry; anna-a02; cx-f01; chimera; m01 | child size len−2→2 (V28), largest viable (V32); tyr-v16 checked split; cx-f01 child-step gate; room gate (reverted) | −900 trigger; −500 score; free-exit requirement; crown-handoff rule | in use |
| [A-08](taxonomy/A-08.md) | Critical-enclosure and cramped splits | ares-v13–v33; r3-03/05; esquie-04 … | band ≤15/≤8; weight 0.35/1.2; hard/soft/split response; child size; defer rules (V29–V31); r3 flood fraction trigger | reach horizon 5; critical 8 (split versions); r3 0.75 / −10; static occupancy | local hold |
| [A-09](taxonomy/A-09.md) | Newborn separation | fenrir→tyr/Ares/the-goat/heimdall; yuna nb_mode; ed; vicious; odin … | escape_spawn_area 15 (ra-09, off); Python node caps (the-goat, s02, yeji-s05); fenrir v3–v7; yuna nb_tight/push/radius … | 27 of 28 escape_* params; retries 2; acceptance tolerance; topology caps | in use |
| [A-10](taxonomy/A-10.md) | Portal handling | Ares (+v07/v08/v33), r3, sciel, cx-f02 … | dive_value 7→3 & blind_unseen 0.5→0.15 (V04); HOLD (v07); atlas (v08); type 9 (v33); r3-01/02; sciel-02a … | dive_value/base/p_dive (post-V04); blind_fresh/body/seen/unseen; escape_portal_bonus … | in use |
| [A-11](taxonomy/A-11.md) | Threat and support model | SIN/MC/Tyr/Ares; skadi/fafnir/fermi/gavroche/spike; ouroboros; kraken … | threat_weight (17a–d, ra-11); attack_margin (21a); support added V06 … | threat_long/equal/short; sprint_factor; ally_support; support_radius; enemy_loss_weight; threat_base … | in use |
| [A-12](taxonomy/A-12.md) | Sonar emission schedule | SIN/MC/Tyr/Ares; ouroboros; kraken; hunter; hydra; javert; drake … | HOLD type 8 (v07); type 9 (v33); cx-f02 probe; MC/drake density rays; gavroche density_rays; heimdall scan … | Ares ray priority; gossip_horizon 30; portal share period 2; density rays 2/relay; handoff retries 2 | in use |
| [A-13](taxonomy/A-13.md) | Sonar receipt and trust | SIN/MC/Tyr/Ares; ouroboros; VN; javert; heimdall/odin; kraken … | MC/drake half-lives; VN checksum; javert merge guard; heimdall echo bed horizon; sciel-03c radio ally count … | gossip_trust 8; crown replace rules; density ttl/sources; handoff tolerance; heimdall echo constants | in use |
| [A-14](taxonomy/A-14.md) | Crown, feeding and hunting endgame | SIN/MC/Tyr/Ares; ouroboros; avery; drake; hydra-v11; hunter; fry … | hunt_from (20a/b) … | all crown_* and feed_*; prey_ttl/min; hunt_max_len; hunt_value; w_flank; crown round 250 (literal) | in use |
| [A-15](taxonomy/A-15.md) | Phase guards (round/unit thresholds) | Ares; SIN/MC; ed/vicious/drake/yuna/tidus temporal layers; newton … | search_cap_late (lune); grow_from 340 (ra-12, incomplete); hunt_from; opening_production_until … | search_cap_late_from 40; sparse_from 150; sparse_units 20; sprint3_late_from 150 … | in use |
| [A-16](taxonomy/A-16.md) | Crowding and separation terms | Ares/Tyr/SIN/MC; yuna; avery; ouroboros; router; sciel; tidus … | crowd_weight (09a/b); own_target_discount (06a/b); density_ally_weight (ra-07); sciel-03b/c/04a/b … | crowd radius/shape (tdist 2, 3−d); ally tie-break; density radius/half_life/ttl/sources … | in use |
| [A-17](taxonomy/A-17.md) | Exploration | Ares/Tyr/SIN/MC; yuna; avery; hunter; bifrost; gaia; tyr lanes … | unseen_value (07a–d, 25); infogain (16); scarcity (22); Python v_unseen, eps, frontier sweeps, lanes, waypoint cache | sector size 8; sector fallback rule; escape unseen 0.35; scout splits (never built) | in use |
| [A-18](taxonomy/A-18.md) | Map-class doctrine | ouroboros-v13/einstein/chimera; serre; fafnir/newton; odin; MC; avery … | odin/newton/MC/avery/ein-dog scope gates; newton n4 ladder_nc; jet dispatcher | threshold values (625, 600, 256, …) never swept; no structure-gated switch built | open |
| [A-19](taxonomy/A-19.md) | Router: arrival-time routing and bed assignment | cx-b01/b02 (+noatlas) on anna-a02 | later_event_w 1.0→0.3; split_open_rounds 3; crowding rules (then off); landing exits 3→2; atlas on/off | horizon clamp 20/60; disc 0.95; enemy_conservatism 0.7; cluster 0.6; spacing 3; hysteresis 1.3 … | closed |
| [A-20](taxonomy/A-20.md) | Tiered cheap policy (anna chassis) | anna-a01/a02; cx-f00..f05; cx-b movement; ares-v01/v02; the-goat-v01 | split_when_trapped (a02); ares-v01 production/lanes/portal re-entry; cx-f01..f05 fixes; atlas on/off | tier order; −16 distance; −6 proximity; +8 preference; room_need formula; credits 4/2 … | closed |
| [A-21](taxonomy/A-21.md) | Intention / executor contracts (musketeers P0/P1/P2) | valjean/feynman; porthos; athos; aramis; dartegnan; javert … | P0 vs P1 (porthos-x04); DP1/DP2 (dartegnan); frontier (aramis); F0/F1×E0/E1; recon objective; VN knob arms … | six-intention menu; FEED_ALLY 100; executors after E0/E1; attack discount 0.93 | closed |
| [A-22](taxonomy/A-22.md) | Look-ahead and adversarial search | leviathan-x01/x02 Riptide, x04 Charybdis, x03 continuation … | horizon 1 vs 6; x02 capacity filter; reply_plies 0 vs 3; budget 1800→450; estuary safety 0/1 | beam width 8; discount 0.86; reply width 6; duel range 5; hunter 6-ply/size leads … | closed |
| [A-23](taxonomy/A-23.md) | Learned and imitation components | ouroboros-m01/m01p; clone-62; loki-v01/v02; heimdall-v08 … | m01 guarded/pure; loki v01→v02, scale; MC table→logistic→guard→≤625 | any learned module in C++; single-decision learned graft in Ares; fitted-Q panel; GRU … | open |
| [A-24](taxonomy/A-24.md) | Modes, state machines and mode beliefs | implicit: fry/hunter ladders, Ares role/escape flags, ouroboros slices … | Python momentum (yuna, ein-dog, doug); Estuary adaptive roles; sciel-02a steering | momentum_weight/decay on Ares; every L31/L32/L33 design | never measured |
| [A-25](taxonomy/A-25.md) | Frame mirror (seat transform) | jet-v05 (v32 host); make_frame.py … | frame per map (fx/r/id on Devil); per-cell selection; host | terrain-derived symmetry detection; seeded 1.2.x / live exposure | built, off |
| [A-26](taxonomy/A-26.md) | Roles at creation (scouts / hunters / gatherers) | kraken; hydra-v01–v03; ouroboros/einstein/chimera/leviathan-v08/v09 … | kraken team_target_mid 40, hunter_trade 1; ouroboros orphan_role, small-map mix; godel hunt share; Estuary adaptive … | kraken size↔role map and phase rounds; ouroboros role weight slices; any role layer on Ares | open |
| [A-27](taxonomy/A-27.md) | Evaluation protocol (gates, panels, OOS rule, live pipeline) | Ares lanes, R-4 scorecard, cx arena, Python lanes, hub executor | +0.05 → D-029.2 → D-032 interval → D-036 local hold; seat-A early stop; gen panel composition … | seed-1 default; +0.05 bar value; slope² map weighting; phase-aware gate; R-4b interval line … | in use |

Hard-coded constants not exposed as parameters in V06 include the crown round 250, game end 500, danger radius 7, enemy
reach clamp 1–3, near-threat radius 4, saturation 0.7·limit, the −900/−1000/−500 score sentinels and the feed clock
`500 − 40 − 0.6·(W+H)`. Undocumented behaviour found in code: feeders deliberately choose a fatal move beside a visible
crown (`policy.hpp:1287-1296`), and the threat cost is highest (p 0.9) when *we* are the longer dragon
([A-11](taxonomy/A-11.md), [A-14](taxonomy/A-14.md)).

## 3. Problems

Three-number form = ours · top-ten · band 55–85 or field percentile, as the sources give them ("not given" is kept rather
than filled). "Ours" names the bot or cohort measured: team-7 live (28 Sep ranked games), Ares V06 (R-3 z1 panel), V04
(parity finding) or the zoo. Length-lost rates are per 1k dragon-turns, rounds 0–99 ([F-43](taxonomy/F-43.md)).

| Id | Problem | Defining measurement | Ours | Top-10 | Band / pct | Concentrates in | Ledger |
|---|---|---|---|---|---|---|---|
| [P-01](taxonomy/P-01.md) | Trapped / enclosure deaths (≤8-reach hazard; the dead-end mill) | len lost/1k dt r0–99 by dragons enclosed at death (≤15 cells in 5 steps) [F-43] | team-7 live 33.8; Ares V06 36.1 | 18.5 | band 32.8; pct not given | Portals, Slithery, Schooltime (live); Slithery, Portals, Devil (V06) … | L24, L05, L30 |
| [P-02](taxonomy/P-02.md) | Newborn deaths | len lost/1k dt r0–99 by children dead ≤10 rounds [F-43] … | team-7 live 23.7 (35.4/100 births); Ares V06 19.3 | 24.0 (30.4/100 births) | band 18.4 (28.6/100); pct not given | Portals, Slithery, Schooltime (live) … | L05, L30 (no own row) |
| [P-03](taxonomy/P-03.md) | Portal-exit deaths (per-transit hazard, same-pair doubles) | deaths ≤2 rounds after own portal step per 100 steps [F-44] … | team-7 live 28.2/100 steps, 5.9 len/1k … | team 306 12.5/100; top-10 3.5 len/1k | band 3.1 len/1k; pct not given | Portals (399–513 steps/game, 36–42/100), Trophy, QoS, Slithery … | L06, L23, L05 |
| [P-04](taxonomy/P-04.md) | Crowding: ally head-on, ally-body, crowd23, target convergence | death_h2h_ally_per1k, death_ally_body_per1k [F-42]; crowd23 len/1k [F-43] | zoo h2h 0.79, body 1.51; Ares V04 h2h 0.949, body 2.419 … | h2h 0.50, body 0.56; crowd23 2.7 | pct zoo h2h 0.35, body 0.37; V04 0.248/0.286 … | Portals (h2h pct 0.056, crowd23 49.7), Devil, Slithery … | L12, L29, L33, L23 |
| [P-05](taxonomy/P-05.md) | Wall / kelp deaths | death_wall_per1k [F-42] | zoo 4.01; Ares V04 7.132; V06 7.763 (8.2 ledger) … | 0.00 | pct zoo 0.40; V04 0.340; band 0.7 | Slithery (live 25.8 vs band 8.9), Trauma, near portals; dead-end tips | — (L24, L05) |
| [P-06](taxonomy/P-06.md) | Own-body / self deaths | death_self_per1k [F-42] | zoo 3.00; Ares V04 3.884; V06 3.662 | 0.00 | pct zoo 0.35; V04 0.319 | Portals, Slithery (swarm density), QoS/Devil (esquie) … | — (guard D-032; L30) |
| [P-07](taxonomy/P-07.md) | Churn: pearls@k rewards corpse eating | share of intake from ally corpses … | V06 38% corpses, 443 deaths/game | not given | field corpse share 0.34–0.47; pct not given | Slithery, Autarky (farming 0.62 econ~), Dilemma, Portals … | L29 |
| [P-08](taxonomy/P-08.md) | Opening-vs-late trade-off (phase bifurcation) | per-checkpoint econ deltas p@50…p@250 [F-40]; winner−loser by r50/r100 [F-47] | V06 p@50 −0.017 / p@100 +0.048 … | V06 p@100 0.94–1.03 of top-10 | pct 0.55–0.60 (V06 pool) | compact maps decided by r100 … | L03, L02, L01, L21 |
| [P-09](taxonomy/P-09.md) | Starved openings (Trauma/Dilemma; nothing ripe, nothing targeted) | p@50/map and econ pct per map on brick list [F-48]; supply8/supply50 signature | Trauma 1 pearl by r50 (p@50 0.111), econ pct 0.375 … | not given | field median 9 pearls r50 (Trauma) … | Trauma, Prisoners Dilemma, QoS; gen pinwheel, crossroads_tr … | L11; proposed L31 (id clash) |
| [P-10](taxonomy/P-10.md) | Economy and retention gap to the field | pearls@k ÷ field median, econ~ [F-40]; three-number form [F-41] … | zoo p@100 0.96, length@100 0.87; Ares V04 p@100 1.016 … | zoo p@100 0.79 of top-10; length 0.75 | pct zoo p@100 0.47, length 0.39; V04 0.511 … | PD, Autarky, Trophy (map effects); compact maps before r100 | L05, L17, L21, L12, L20, L04 |
| [P-11](taxonomy/P-11.md) | Production is pearl-bound | split checks failing on length; units r100 vs pace target [F-47] | fafnir Devil 951/990 checks fail length; pace-v01 −0.008 | top-10 19 units r100 | band 15 units r100; pct not given | compact maps (Devil, arena, Trophy); r0–100 | L17, L30 |
| [P-12](taxonomy/P-12.md) | Fight cost and weak convergence | own deaths / length lost per fight, convergence ratio [F-46] | team 7 11.6 deaths, 32.9 len/fight; convergence 0.18 | convergence 0.29 | band 6.8 / 18.9, conv 0.27; pct not given | compact maps (conv 0.12, initiator 36.8%); gen fight-loss bricks | L10, L09, L33 |
| [P-13](taxonomy/P-13.md) | Crown / conversion at r500 | round-limit losses with material lead; longest gap at r500 … | bifrost 44 r500 losses, longest 14.5 vs 23 … | top1_share 0.08 | field 0.10; pct not given | big_empty, Trauma/Portals (maze conversion), Schooltime, stronghold … | L15, L18 |
| [P-14](taxonomy/P-14.md) | Map-identity dependence | pool vs gen win/econ; keyed-term ablation [F-49]; map fixed effects [F-50] | V06 pool 0.762 vs gen 0.524; terms off Devil 1.00→0.31 | not given | not given | Devil, Dilemma, Portals (32×16), Trophy; atlas maps | L28, L08, L26 |
| [P-15](taxonomy/P-15.md) | Pool fit and the generalisation gap (incl. dev-545 proxy, gen-panel coverage) | paired pool Δ vs gen Δ [F-49]; zoo coverage of field [F-45] … | renoir-07c pool +0.061 vs gen −0.016 … | not given | 19% of field side-games outside zoo range … | gen lacks corridor/kelp and portal-heavy clusters; transposed maps | L19, L14, L28 |
| [P-16](taxonomy/P-16.md) | Seat asymmetry and layout parity | win share by seat on symmetric maps; BT A-seat term … | seat A 32/48 (jet); A-seat +19.1 Elo | not given | not given | Autarky, Trauma, Trophy (A worse at equal Elo); Devil-B; arena | — |
| [P-17](taxonomy/P-17.md) | Timeouts (CPU; historical in C++) | sandbox points/turn p99/max; TLE/invalid deaths [F-42, F-49] | 9508 69/143 games at cap, 1,096 TLE turns; Ares V06 p99 7.4M | death_invalid 0 | field 0; pct not given | Portals, Slithery, Trauma, big_empty; boot turn, newborn turns | L22 |
| [P-18](taxonomy/P-18.md) | Oscillation / target switching / dithering | target switches per game/100 dt; revisit counts [F-08] | sakura-s01 2,210/1,333 switches/game; yeji 33/100 dt | not given | not given | Schooltime, Portals (switch counts); Devil (circling) | L13, L31 |
| [P-19](taxonomy/P-19.md) | Silent fallbacks, override drift and dead-parameter experiments (experiment hygiene) | parity replay, MC_ERROR counts, call-site reading [F-49] | ra-04 Δ exactly 0; separation exceptions 300/game Slithery … | not applicable | not applicable | Portals/Slithery (exception rates); all override-based lines | — (L20 note) |
| [P-20](taxonomy/P-20.md) | Seed noise and gate shape | same-bot seed shift; bootstrap width; power table [F-49, F-40] | renoir-00 econ~ 1.111 vs 1.182 (+0.071); ±0.03 on 160 games | not applicable | not applicable | late-only and map-concentrated gains (median vs mean) | L21, L20 |
| [P-21](taxonomy/P-21.md) | Scorecard / pipeline disagreement | same games re-scored under two pipelines [F-49] | V06 econ 1.111 vs Lune 1.240 … | not applicable | not applicable | all pool maps (level shift ~20%) | L01 |
| [P-22](taxonomy/P-22.md) | Local-to-live transfer and judge divergence | live − local win share; local-vs-public Spearman … | −7…−35 pp six of six; Spearman −0.64 … | not applicable | not applicable | PD (0.88 local vs 0.12 live), QoS, Dilemma, Autarky … | L19 |
| [P-23](taxonomy/P-23.md) | Information without a consumer | injection/ablation flips; readers per state field [F-19, F-20] | leviathan 20 injected reports → 0 action change; vn 0 flips | not applicable | not applicable | all maps; packet catalogues and analysis outputs | — (L12, L33 related) |
| [P-24](taxonomy/P-24.md) | Body suppression of bed spawns | scheduled renewals blocked by bodies per game (PRR) | M156377 Stronghold 2,088/6,902 blocked | not given | not given | Stronghold (one game); bed-dense maps untested | — |
| [P-25](taxonomy/P-25.md) | Corridor paralysis of long starting dragons | opening units r100 / elimination round for long-spawn seat (scholze screen) | Autarky B control 8 units r100, eliminated r405 → v02 20 uni … | not given | not given | Autarky (seat B), Prisoners Dilemma sealed corridors; r0–20 | — |

Problems named here that had no name before: [P-09](taxonomy/P-09.md) starved openings (Esquie's reading; its proposed
ledger id "L31" collides with the existing L31), [P-19](taxonomy/P-19.md) experiment hygiene (silent fallbacks; Python
`override.py` files that dropped their parent's overrides in Tyr V18–V23/V25–V34 and Gavroche V20–V29/V31–V66; dead parameters varied as
mechanisms), [P-21](taxonomy/P-21.md) scorecard disagreement, [P-23](taxonomy/P-23.md) information without a consumer,
[P-24](taxonomy/P-24.md) bodies suppressing bed spawns, [P-25](taxonomy/P-25.md) corridor paralysis. Two readings of the
core deficit coexist and are unreconciled: "the deficit is deaths, not income" (TEAM-SUMMARY §1.3) against "losing maps
are lost to opening economy and production, not deaths" (K-1: ρ +0.90 economy vs −0.66 avoidable deaths) —
[C-05](taxonomy/contradictions.md).

## 4. Attempted solutions

Grouped by the first problem each targets. "Why stopped" quotes or condenses the source; "(inferred)" in the detail file
marks a reason not stated by the source.

| Id | Mechanism | Host | Decisive number | Verdict | Why it stopped | Targets |
|---|---|---|---|---|---|---|
| **P-01** | **Trapped / enclosure deaths** | | | | | |
| [S-01](taxonomy/S-01.md) | Hard open-room filters and reach priority | ● Ares C++ teammates V10/V13/V14, robert-v02, renoir-12a | V14 5–15 vs V09; renoir-12a Δecon −0.183 | reject | hard escape selection too disruptive; pearls halved (V14 README, BASELINES) | P-01, P-10 |
| [S-02](taxonomy/S-02.md) | Soft room/reach/trap scores | ◐ Ares V11–V18, renoir-13/14, ra-01, r3-04/05; cx-f04 | V15 enclosed 71 vs 83/1k but pearls 74 vs 134; r3-04 econ −0.072 | reject | soft scores moved no hazard or cost retention; caution costs economy one for one | P-01, P-05 |
| [S-03](taxonomy/S-03.md) | Critical-enclosure escape split | ● Ares V19/V20 (teammates), esquie-04 (M-1) | V19 11–9, ≤8 hazard 680→615; esquie-04 econ −0.035, own-body +24% | reject | Slithery-shaped mechanism; costs every slow/corridor map (esquie-04 panel) | P-01 |
| [S-04](taxonomy/S-04.md) | Split-size salvage variants | ● Ares V21–V27 (teammates) | all 9–11 … 0–4 vs V19 | reject | upgrade generalised too broadly or gated too narrowly (V28 finding) | P-01 |
| [S-05](taxonomy/S-05.md) | Minimum-sacrifice and dead-end child search, feed-before-split | ● Ares V28–V32 (teammates; live v87/v88) | V28 12–8, V32 11–9 vs V19 (20 games, seed 1) | local hold | not stopped; continued to V33; never panelled (one seed) | P-01 |
| [S-06](taxonomy/S-06.md) | Escape-early cramped split (r3-03) | ● Ares V06 (R-3 lane) | win +5.00 pp seeds 1+2, econ +0.026, own-body +11% | hold | production lever not escape fix; pay down newborn churn first | P-01, P-11 |
| [S-07](taxonomy/S-07.md) | Chassis enclosure probe and corpse gate (cx-f01) | ○ cx chassis (anna-a02) | len_r100 37/167/36 p 1.0 (240 pairs) | reject | chassis already had the room tiers; leak lives in Tyr lineage | P-01 |
| [S-08](taxonomy/S-08.md) | Trapped-split grafts and exit guards | ○ Python: ouroboros-t01 on gavroche-v32, scholze-v04, skadi v0 … | t01 52–26 vs 51–27 (+1 vs +6 bar); skadi-v03 −4 net | reject | hosts already split on 87–90% of trapped turns; guard over-hedges | P-01 |
| [S-09](taxonomy/S-09.md) | Pocket-farm discount changes | ◐ Ares renoir-03b/24, V12 … | renoir-03b Δecon −0.058; farming worth 0.62 econ~ on Autarky | reject | pocket farming is the economy; change which pockets, not how many | P-01, P-07 |
| **P-02** | **Newborn deaths** | | | | | |
| [S-10](taxonomy/S-10.md) | Newborn separation / escape tuning | ◐ Python fenrir/tyr/yuna/odin/vicious; Ares V05 fix, ra-09 | ra-09 Δecon +0.011, self −5% (hold OFF); yuna x04 +6/80 | hold | hygiene-only; needs accepted economy base; lever positional not valuation | P-02 |
| [S-11](taxonomy/S-11.md) | Birth certificate and neck fix | ○ Python S1 v10 host; ouroboros-s02 infer_body; sinbad e23 | newborn/100 births 32.1 vs 31.5 (sakura); s02 41.4 vs 41.3 | reject | delivery works but moves nothing; child's problem is crowding not information | P-02 |
| [S-12](taxonomy/S-12.md) | Newborn siting | ● Ares V06 (sciel-01a); C1-C proposal unbuilt | nb10 34.6→34.6; econ −0.003 | reject | inert: len-4 parent just ate, tail near food by construction | P-02 |
| [S-13](taxonomy/S-13.md) | Child-area gate | ● Ares V06 renoir-02a/b, monoco ra-02 | ra-02 Δecon −0.0139 (s1+2) | reject | cautious single knob costs economy; one-knob bar out of reach | P-02 |
| [S-14](taxonomy/S-14.md) | Portal route handoff at split (ares-v33) | ● Ares V33 (teammates; live v89) | round robin 33–27; Default 0–6, QoS 6–0 | local hold | not stopped; one-seed screen, below promotion gate | P-02, P-03 |
| **P-03** | **Portal-exit deaths** | | | | | |
| [S-15](taxonomy/S-15.md) | Pre-entry pair memory and exit-known gates | ◐ cx-f02 (chassis); Ares r3-01/r3-02 | r3-02 portal −56% via steps −68%, econ −0.120 | reject | pure volume throttle; per-transit survival unchanged or worse | P-03 |
| [S-16](taxonomy/S-16.md) | Blind-exit occupancy memory | ○ Python valjean/bifrost/fenrir, witten, scholze, einstein, sk … | valjean Dilemma+Autarky 3–21→14–10; later grafts +0–2 | hold | grafts missed frozen gates; Python line superseded; never re-measured on Ares | P-03 |
| [S-17](taxonomy/S-17.md) | One-ray portal probe and HOLD packet | ◐ Ares V07 hold-only … | V07 114–46 (−5 pp), head-on −13.2%, econ +0.005 | reject | safety gain did not preserve panel result; host pricing already covers it | P-03, P-04 |
| [S-18](taxonomy/S-18.md) | Post-transit navigation (sciel-02a) | ● Ares V06 (sciel lane) | portal len/1k −21%, econ −0.004, units −0.057 | reject | hygiene at economy cost where transits are productive; no sweep | P-03 |
| [S-19](taxonomy/S-19.md) | Dive caps and phase-scheduled portal policy | ○ Python sinbad v_dive, yuna phase policy, tyr guards, scouts | sinbad portal set 45–11 vs 36–20; yuna-v05 +13.7 pp public | accept | adopted into Python hosts; scouts rejected; Python superseded by Ares | P-03, P-10 |
| **P-04** | **Crowding** | | | | | |
| [S-21](taxonomy/S-21.md) | Crowd and density weights | ◐ Ares renoir-09b/19a, ra-07; cx router v3; Python yuna x08 | ra-07 Δecon −0.017, h2h −2.1% vs 10% predicted | reject | scalar crowd terms cost pace, miss arrival-time collisions | P-04 |
| [S-22](taxonomy/S-22.md) | Valuation-time deconfliction (sciel-03b…04b) | ● Ares V06 + EW food (sciel lane) | 03c econ +0.105 pool, +16.3% gen; h2h_ally +38% | reject | collisions are arrival-time; valuation guards cannot see convergers | P-04 |
| [S-23](taxonomy/S-23.md) | Target claims and ownership | ◐ Python fry/hunter/bifrost/ouroboros; cx router … | hunter-v06 22–18 vs 20–20; renoir-06a win −0.113 | hold | claim protocol for Ares (sciel-05) never built | P-04 |
| **P-05** | **Wall / kelp deaths** | | | | | |
| [S-59](taxonomy/S-59.md) | Doom memory vs exact simulation | ○ ouroboros, kraken-v05, hydra-v11 (Python) | doom: Devil 4–10 with vs 7–7 without; w_doomed later 0 | dropped | Zero wall deaths came from exact simulation, not doom memory | P-05 |
| **P-08** | **Opening-vs-late trade-off** | | | | | |
| [S-31](taxonomy/S-31.md) | Search depth ladder | ● Ares V06/V09, robert-v01, lune L1–L3/×8 arms | V06 122–38, gen dragons +0.130; L1–L3 exp −0.04…−0.11 | accept | more search hurts opening; lever is what and when (late cap) | P-08, P-10 |
| [S-32](taxonomy/S-32.md) | Late-only search cap (lune-r1-07/08) | ● Lune R-1 on Ares V06 (C++) | econ +0.026, dragons@100 +0.053, length +0.046 (s1+2); gen econ +2.5 % | hold | Handed to R-5 (not delivered); registered 510 but executor in shadow | P-08, P-10 |
| **P-09** | **Starved openings** | | | | | |
| [S-28](taxonomy/S-28.md) | Supply-gated starve-wait | ● Ares esquie-01-nodevil (esquie lane) | 03b Δecon +0.0018 [−0.0024,+0.0062] seeds 1–3 | local hold | open: min_age 16–18 untested middle | P-09 |
| **P-10** | **Economy and retention gap to the field** | | | | | |
| [S-20](taxonomy/S-20.md) | Atlas as routes / as economy | ◐ Ares V08; cx chassis/router; Python s02, chaewon, yeji | V08 econ +0.188, ally head-on +205% | dropped | out-of-sample rule: tournament maps are unseen | P-10, P-14 |
| [S-25](taxonomy/S-25.md) | EW food-density memory (sciel-03a) | ● Ares V06 (sciel lane) | econ +0.067, pearls@100 +0.146; h2h_ally +34% | reject | ally head-on guard: convergence crowding as pre-declared | P-10 |
| [S-26](taxonomy/S-26.md) | Exploration value tuning | ◐ Ares renoir-07a–d/16/22/25; Python yeji, avery v09–v12 | 07a +0.110 pool, 07c gen −0.016; ally h2h +51% | reject | pool fit via churn: learned the ten maps | P-10 |
| [S-27](taxonomy/S-27.md) | Bed valuation and bed waiting | ◐ Ares renoir-01/11, ra-08 … | renoir-01a −0.065; 01c Devil −0.72; sinbad arrival beds 25–7 vs 13–19 | reject | flat waits lose on dense maps; keying untested (R-6 never issued) | P-10 |
| [S-29](taxonomy/S-29.md) | Pearl-memory TTL | ● Ares V06 renoir-08a, monoco ra-04/05 | ra-05 Δecon +0.0024 hygiene hold; ra-04 dead param | hold | hygiene-only; switch off pending accepted economy base | P-10 |
| [S-30](taxonomy/S-30.md) | Other single-knob moves on V06 | ● Ares V06 (renoir, monoco) | Renoir 33/0, Monoco 11/0; best +0.02 | reject | one-knob bar out of reach; seed shifts +0.07; local optimum | P-10 |
| [S-58](taxonomy/S-58.md) | Router (cx-b01/b02) | ○ cx-b on anna-a02 chassis (C++ testbed) | length r100 176/3/61 live pool; units n.s. (p 0.69) | reject | Routing is not the lever; survival is (atlas carried 2/3) | P-10 |
| [S-61](taxonomy/S-61.md) | Roles at creation | ○ kraken, hydra, ouroboros, leviathan, estuary (Python) | ouroboros orphan→gatherer −11 net compact (hunters load-bearing) | hold | Size-coded roles costly; hand-offs half lost; never built on Ares | P-10 |
| [S-62](taxonomy/S-62.md) | Sprint discipline | ◐ the-goat (Py), cx-f03 (chassis), ra-03 (Ares) | ra-03 econ +0.021, dragons/length +0.023 (s1+2) | hold | the-goat CPU wall; ra-03 below +0.05, D-032 re-score pending | P-10 |
| **P-11** | **Production is pearl-bound** | | | | | |
| [S-35](taxonomy/S-35.md) | Pace controller (P1: pace-v01–v03) | ○ chaewon-y04/yuna-v05 host (Python), 3 authors | −0.008 over 360 pairs (main); −0.017 (GLM); −0.483 (Codex) | reject | Production is pearl-bound, not decision-bound; push inert | P-11 |
| [S-36](taxonomy/S-36.md) | Production schedules and admission grafts | ◐ fafnir, avery, newton, hydra-v11, kraken, tew/bifrost grafts … | fafnir-v01 gauntlet 140–42 (+6); avery-v07 94–37–1 | reject | Split admission not binding; length-bound; grafts failed frozen gates | P-11, P-10 |
| [S-56](taxonomy/S-56.md) | Learned grafts from team recon | ○ tew-v12, bifrost 8540, gavroche-v32 hosts (Python) | team-7 learned graft Autarky 2–2→4–0 but quartet 2–2→0–4 | reject | All failed frozen +2/12 gate; weak intervention surface | P-11, P-13 |
| **P-12** | **Fight cost and weak convergence** | | | | | |
| [S-38](taxonomy/S-38.md) | Threat weight and strike threshold | ● renoir-17a–d/21a, monoco ra-11 on Ares V06 … | renoir-17d threat off +0.019 econ, win −0.037 | reject | Single-knob bar out of reach; D-032 re-score never run | P-12, P-10 |
| [S-39](taxonomy/S-39.md) | Size-matched support | ◐ fafnir f12, skadi, gavroche-v32, fermi (Py); Ares V06 (C++) | gavroche-v32 support +6.4 pp live pool; fafnir f12 gauntlet +6 | in use | Small gain did not survive fresh seeds; never ablated on Ares | P-12 |
| [S-40](taxonomy/S-40.md) | Local fight rules (refuse far from beds; converge-or-refuse) | ○ none built (intended Ares) | corpus: top ten initiate 38.5 % vs band 54.8 % at bed >6 | never measured | Not stated; routed to R-2 lanes, no lane tried it | P-12 |
| [S-41](taxonomy/S-41.md) | Leader-coordinated fight protocol (S-3) | ○ none built | convergence 0.29 vs 0.27; initiator edge = composition | dropped | No coordination signature in top ten (D-030) | P-12 |
| [S-42](taxonomy/S-42.md) | Aggression refits (godel, von_neumann, porthos P1, lanchester, w_parity) | ○ porthos/VN/godel/ouroboros/hydra/yeji (Python) | porthos-x04 gauntlet 126–56 (+13); godel x14 112–70 = base | reject | Binding constraint is contact creation, not trade admission | P-12 |
| [S-60](taxonomy/S-60.md) | Look-ahead / reply search | ○ hunter-v16–v19 (C++), leviathan Riptide/Charybdis (C++), Est … | Charybdis reply search 4–20 vs no-search 5–19; myopic = horizon | reject | No gain over myopic/no-search on weak chassis; not on Ares | P-12, P-01 |
| **P-13** | **Crown / conversion at r500** | | | | | |
| [S-24](taxonomy/S-24.md) | S1 swarm dissolve and density gossip | ○ Python ouroboros-v10 host (kazuha, sakura, chaewon, yeji, eu … | both arms 30–33% win (p 0.004–0.26) | reject | H-dissolve falsified everywhere; production pearl-limited | P-13, P-11, P-04 |
| [S-43](taxonomy/S-43.md) | Crown election and feeding clocks | ◐ ouroboros, avery, bifrost, spike, yuna, vicious, hunter-v23  … | ouroboros-v10 238–23; avery-v08 100–31–1 | in use | Clock tuning paused; maze conversion open; Ares crown never varied | P-13 |
| [S-44](taxonomy/S-44.md) | Earlier conversion and donors | ○ ouroboros-b01/b02, yuna, tyr, tew graft, newton (Py) … | b01 −0.013, b02 −0.064; donors 0 to −2.5 | reject | Earlier stop costs material; donations don't raise final longest | P-13 |
| **P-14** | **Map-identity dependence** | | | | | |
| [S-45](taxonomy/S-45.md) | Shape-terms ablation and midline-race replacement | ● renoir-23, esquie-01 on Ares (C++) | terms off: Devil win 1.00→0.31; gen win 0.524 vs pool 0.762 | open | Replacement unbuilt: cannot pass pool gate; handed to teammates | P-14 |
| [S-46](taxonomy/S-46.md) | Structure-gated switches / local hold (D-036) | ◐ esquie-03b on Ares; spike-x09, size-gated doctrines (Py) | esquie-03b Δecon +0.0018 [−0.0024,+0.0062], win +1.0 pp (s1–3) | local hold | Still open (min_age 16–18 untested); branch unmerged | P-14, P-15 |
| **P-15** | **Pool fit and the generalisation gap** | | | | | |
| [S-53](taxonomy/S-53.md) | Behavioural clone (ouroboros-m01) | ○ ouroboros-m01 (Python HGB) | 51–53 vs zoo; action accuracy 0.739 | reject | Capped by the teacher; under-produces, misses r320 conversion | P-15 |
| **P-16** | **Seat asymmetry and layout parity** | | | | | |
| [S-47](taxonomy/S-47.md) | Frame mirror (jet-v05) | ○ jet v32 host (Python), make_frame on other Py hosts | 99 vs 86 of 120 (up 16, down 3) | hold | Not stated; seat-B check/falsifier never run; Python host superseded | P-16 |
| [S-48](taxonomy/S-48.md) | Paired two-orientation requests and seat pairing (D-015, D-022) | ● hub executor (host-independent); local panels | 60-pair screen halves detectable Δ (from ≳0.25) | built, off | Executor in shadow since D-031 (teammates own submissions) | P-16, P-20 |
| **P-17** | **Timeouts** | | | | | |
| [S-33](taxonomy/S-33.md) | Python CPU cap series (gavroche v33–v66, tyr/yuna caps, the-goat-v04) | ○ gavroche, sinbad, MC, yuna, yeji, the-goat (Python) | gavroche-v54 69–39, p99 43–44 M, max 52.8–63.7 M | closed | User stop after V66; C++ removed the CPU wall (Ares 8.6 M) | P-17 |
| [S-34](taxonomy/S-34.md) | C++ port and exception fixes (ares-v02–v05, hunter-v14, s02 boot turn) | ◐ Ares V02–V05 (C++), hunter-v14 (C++), fenrir-v18 host (Py) | V04 golden 168,123 turns 0 divergences; V06 max 8.6 M | accept | Not stopped: became the production line (D-029) | P-17, P-19 |
| [S-54](taxonomy/S-54.md) | Teacher-ranker (loki-v01/v02) | ○ loki on bifrost-v01; heimdall-v08 (Python) | v01 native 47–13; live 0–30 with 336 CPU failures | reject | Runtime failure (CPU); gain did not transfer to Heimdall host | P-17 |
| **P-18** | **Oscillation / target switching / dithering** | | | | | |
| [S-57](taxonomy/S-57.md) | Target hysteresis and momentum tuning | ◐ ra-06/renoir-18 on Ares; yuna, ein-dog, S1 (Py) | ein-dog-v02 screen 30–2 (+5), gauntlet +1; live −0.067 | reject | ra-06 cost material; momentum bistable, never varied on Ares | P-18 |
| **P-19** | **Silent fallbacks, override drift and dead-parameter experiments** | | | | | |
| [S-50](taxonomy/S-50.md) | Golden-decision harness and parity checks | ● tools/cx/golden.py, R-4 (C++ lanes) … | V04 vs Tyr V12: 168,123 turns, 0 divergences | in use | Not stopped; Python override drift and judge divergence uncovered | P-19, P-21 |
| **P-20** | **Seed noise and gate shape** | | | | | |
| [S-49](taxonomy/S-49.md) | Gate revisions (+0.05 → D-029.2 → D-032 → D-036) | ● all Ares lanes | seed shift +0.071 > 0.05 bar; bootstrap ±0.03 at 160 games | in use | Not stopped; interval GATE line and D-032 re-scores never delivered | P-20, P-21 |
| **P-22** | **Local-to-live transfer and judge divergence** | | | | | |
| [S-51](taxonomy/S-51.md) | Field-relative benchmarks replacing zoo ratings | ● BENCHMARKS/F1 scorecard (all lanes) | local win share vs live slope 0.19; local overstates live 6/6 | in use | Zoo retired 28 Sep; panel opponents still zoo bots | P-22, P-20 |
| [S-52](taxonomy/S-52.md) | Live pipeline and dev screen (protocol v2/v2.1, dev-545) | ◐ hub executor; queued Ares V05/V06, lune-r1-07, s02 | no confirmation ever opened; bots win 10–30 % vs 545 | built, off | Executor to shadow (D-031); teammates upload by hand | P-22, P-15 |
| **P-25** | **Corridor paralysis of long starting dragons** | | | | | |
| [S-37](taxonomy/S-37.md) | Opening rescue split | ◐ gavroche v01–v14, scholze-v02, odin (Py) … | scholze-v02 24–12 vs 19–17 (Autarky 2–4→5–1) | accept | Lineages moved on; Ares window knob inert (fires on incomplete bodies) | P-25 |
| **A-23** | **Learned and imitation components** | | | | | |
| [S-55](taxonomy/S-55.md) | Offline fitted-Q early game (tools/rl_earlygame) | ○ tools only (Python), no bot | none recorded | never measured | Not stated; never panelled, no consumer before Ares move |  |

## 5. Cross-reference matrices

### 5a. Problems × solutions

| Problem | Solutions tried (verdict) |
|---|---|
| [P-01](taxonomy/P-01.md) | [S-01](taxonomy/S-01.md) R · [S-02](taxonomy/S-02.md) R · [S-03](taxonomy/S-03.md) R · [S-04](taxonomy/S-04.md) R · [S-05](taxonomy/S-05.md) LH · [S-06](taxonomy/S-06.md) H · [S-07](taxonomy/S-07.md) R · [S-08](taxonomy/S-08.md) R · [S-09](taxonomy/S-09.md) R · [S-60](taxonomy/S-60.md) R |
| [P-02](taxonomy/P-02.md) | [S-10](taxonomy/S-10.md) H · [S-11](taxonomy/S-11.md) R · [S-12](taxonomy/S-12.md) R · [S-13](taxonomy/S-13.md) R · [S-14](taxonomy/S-14.md) LH |
| [P-03](taxonomy/P-03.md) | [S-14](taxonomy/S-14.md) LH · [S-15](taxonomy/S-15.md) R · [S-16](taxonomy/S-16.md) H · [S-17](taxonomy/S-17.md) R · [S-18](taxonomy/S-18.md) R · [S-19](taxonomy/S-19.md) A |
| [P-04](taxonomy/P-04.md) | [S-17](taxonomy/S-17.md) R · [S-21](taxonomy/S-21.md) R · [S-22](taxonomy/S-22.md) R · [S-23](taxonomy/S-23.md) H · [S-24](taxonomy/S-24.md) R |
| [P-05](taxonomy/P-05.md) | [S-02](taxonomy/S-02.md) R · [S-59](taxonomy/S-59.md) D |
| [P-06](taxonomy/P-06.md) | [S-06](taxonomy/S-06.md) H · [S-11](taxonomy/S-11.md) R · [S-24](taxonomy/S-24.md) R |
| [P-07](taxonomy/P-07.md) | [S-09](taxonomy/S-09.md) R · [S-49](taxonomy/S-49.md) U |
| [P-08](taxonomy/P-08.md) | [S-31](taxonomy/S-31.md) A · [S-32](taxonomy/S-32.md) H |
| [P-09](taxonomy/P-09.md) | [S-26](taxonomy/S-26.md) R · [S-27](taxonomy/S-27.md) R · [S-28](taxonomy/S-28.md) LH |
| [P-10](taxonomy/P-10.md) | [S-01](taxonomy/S-01.md) R · [S-19](taxonomy/S-19.md) A · [S-20](taxonomy/S-20.md) D · [S-25](taxonomy/S-25.md) R · [S-26](taxonomy/S-26.md) R · [S-27](taxonomy/S-27.md) R · [S-29](taxonomy/S-29.md) H · [S-30](taxonomy/S-30.md) R · [S-31](taxonomy/S-31.md) A · [S-32](taxonomy/S-32.md) H · [S-36](taxonomy/S-36.md) R · [S-38](taxonomy/S-38.md) R · [S-58](taxonomy/S-58.md) R · [S-61](taxonomy/S-61.md) H · [S-62](taxonomy/S-62.md) H |
| [P-11](taxonomy/P-11.md) | [S-06](taxonomy/S-06.md) H · [S-24](taxonomy/S-24.md) R · [S-35](taxonomy/S-35.md) R · [S-36](taxonomy/S-36.md) R · [S-56](taxonomy/S-56.md) R |
| [P-12](taxonomy/P-12.md) | [S-38](taxonomy/S-38.md) R · [S-39](taxonomy/S-39.md) U · [S-40](taxonomy/S-40.md) N · [S-41](taxonomy/S-41.md) D · [S-42](taxonomy/S-42.md) R · [S-60](taxonomy/S-60.md) R |
| [P-13](taxonomy/P-13.md) | [S-24](taxonomy/S-24.md) R · [S-43](taxonomy/S-43.md) U · [S-44](taxonomy/S-44.md) R · [S-56](taxonomy/S-56.md) R |
| [P-14](taxonomy/P-14.md) | [S-20](taxonomy/S-20.md) D · [S-45](taxonomy/S-45.md) Op · [S-46](taxonomy/S-46.md) LH |
| [P-15](taxonomy/P-15.md) | [S-46](taxonomy/S-46.md) LH · [S-49](taxonomy/S-49.md) U · [S-52](taxonomy/S-52.md) O · [S-53](taxonomy/S-53.md) R |
| [P-16](taxonomy/P-16.md) | [S-47](taxonomy/S-47.md) H · [S-48](taxonomy/S-48.md) O |
| [P-17](taxonomy/P-17.md) | [S-33](taxonomy/S-33.md) C · [S-34](taxonomy/S-34.md) A · [S-54](taxonomy/S-54.md) R |
| [P-18](taxonomy/P-18.md) | [S-57](taxonomy/S-57.md) R |
| [P-19](taxonomy/P-19.md) | [S-34](taxonomy/S-34.md) A · [S-50](taxonomy/S-50.md) U |
| [P-20](taxonomy/P-20.md) | [S-48](taxonomy/S-48.md) O · [S-49](taxonomy/S-49.md) U · [S-51](taxonomy/S-51.md) U |
| [P-21](taxonomy/P-21.md) | [S-49](taxonomy/S-49.md) U · [S-50](taxonomy/S-50.md) U |
| [P-22](taxonomy/P-22.md) | [S-51](taxonomy/S-51.md) U · [S-52](taxonomy/S-52.md) O |
| [P-23](taxonomy/P-23.md) | **none** |
| [P-24](taxonomy/P-24.md) | [S-27](taxonomy/S-27.md) R |
| [P-25](taxonomy/P-25.md) | [S-37](taxonomy/S-37.md) A |

Cells with no direct attempt: **[P-06](taxonomy/P-06.md) own-body** (it is the guard that blocked r3-03 at +11 % and
esquie-04 at +24 %, but no mechanism targets it), **[P-23](taxonomy/P-23.md)** and **[P-24](taxonomy/P-24.md)**.
[P-12](taxonomy/P-12.md) fight cost has only single-knob threat weights on Ares; its two corpus-derived rules
([S-40](taxonomy/S-40.md)) were never built. [P-16](taxonomy/P-16.md) seat asymmetry and [P-18](taxonomy/P-18.md)
oscillation have no attempt on Ares beyond one hysteresis knob. [P-24](taxonomy/P-24.md) is listed against
[S-27](taxonomy/S-27.md) only as an adjacent mechanism.

### 5b. Solutions × lineages (summary; full table in [matrices.md](taxonomy/matrices.md))

Of 62 solution families, 39 have at least one variant measured on the Ares line (31 in the V06-derived lanes, 16 in the
teammates' V01–V33), 29 on Python hosts, 15 on model or older lines, 9 on the cx chassis; 3 are infrastructure and 3 were
never built into a bot ([S-40](taxonomy/S-40.md), [S-41](taxonomy/S-41.md), [S-55](taxonomy/S-55.md)). **Seventeen were never measured on the production host:** [S-07](taxonomy/S-07.md) chassis enclosure probe,
[S-08](taxonomy/S-08.md) trapped-split grafts, [S-11](taxonomy/S-11.md) birth certificate, [S-16](taxonomy/S-16.md)
blind-exit memory (present in Ares via the Tyr port as `blind_*`, never varied), [S-19](taxonomy/S-19.md) dive caps and
phase-scheduled portals (Ares carries `dive_value 3` from Tyr's override, never varied), [S-24](taxonomy/S-24.md) S1
dissolve, [S-33](taxonomy/S-33.md) CPU caps, [S-35](taxonomy/S-35.md) pace controller, [S-42](taxonomy/S-42.md)
aggression refits, [S-47](taxonomy/S-47.md) frame mirror, [S-53](taxonomy/S-53.md), [S-54](taxonomy/S-54.md), [S-56](taxonomy/S-56.md) learned
components, [S-58](taxonomy/S-58.md) router, [S-59](taxonomy/S-59.md) doom memory, [S-60](taxonomy/S-60.md) look-ahead,
[S-61](taxonomy/S-61.md) roles at creation. The teammates' line (V07–V33) and the R lanes overlap on the enclosure
problem only; their screens are 20 games against one opponent, the lanes' are 160–480-game paired panels.

### 5c. Features × consumers (summary; full table in [matrices.md](taxonomy/matrices.md))

Every feature has at least one consumer somewhere, but on the production line: 5 are computed and unread (echoes, atlas,
DragonMem position fields, `last_exit_*`, `seen_count`), 4 exist only in off-line bots (dead-end peel, arrival maps,
respawn-gap memory, EW food density), and 1 is switched off (portal transit memory). The analysis side feeds only the gate
([A-27](taxonomy/A-27.md)); no analysis feature has reached a bot as a term or a switch except the leak ledger's reach
definition (≤15 cells in 5 steps), which the teammates adopted in V13–V33 ([F-10](taxonomy/F-10.md)).

### 5d. Map × mechanism (summary; 553 rows in [map-mechanism.md](taxonomy/map-mechanism.md))

Base standing is Esquie's brick list for the lanes' base (V06 + late cap ×8, 32×16 terms off; z1 seeds 1+2).

| Pool map | Win | econ_pct | Largest leak (len/1k) · worst tier-2 (pct) | Largest positive (Ares line) | Largest negative (Ares line) |
|---|---:|---:|---|---|---|
| Autarky | 0.750 | 0.657 | trapped 38.2 · wall 0.239 | ares-v32 2–0 vs V19 ([S-05](taxonomy/S-05.md); 20-game screen); ares-v33 4–2 in RR ([S-14](taxonomy/S-14.md)) | renoir-24 farm2 −0.15 econ~ ([S-09](taxonomy/S-09.md)) |
| Default | 0.750 | 0.518 | portal 11.8 · ally-body 0.116 | sciel-03c +0.220 econ~ ([S-22](taxonomy/S-22.md)); sciel-03a +0.184 ([S-25](taxonomy/S-25.md)) | ares-v33 0–6 in RR ([S-14](taxonomy/S-14.md)); esquie-02 econ_pct −0.012 ([S-28](taxonomy/S-28.md)) |
| Devil | 0.500 | 0.680 | trapped 68.8 · self 0.190 | none above noise on the pool; esquie-02 win 0.500→0.531 ([S-28](taxonomy/S-28.md)). Off-pool: renoir-07c devil_tr +1.03 ([S-26](taxonomy/S-26.md)) | renoir-23 shape terms off: econ~ −1.22, win 1.00→0.31 ([S-45](taxonomy/S-45.md)); renoir-01c −0.72 ([S-27](taxonomy/S-27.md)) |
| Portals | 0.844 | 0.506 | trapped 81.9, portal 74.6 · h2h 0.056 | r3-02 exit-known: trapped 75.7→32.0, at pooled econ −0.120 ([S-15](taxonomy/S-15.md)); ares-v28 2–0 ([S-05](taxonomy/S-05.md)) | sciel-02a −0.045 econ~ ([S-18](taxonomy/S-18.md)); ares-v19 trapped 65.0→75.8 and esquie-04 81.9→87.5 ([S-03](taxonomy/S-03.md)) |
| Prisoners Dilemma | 0.812 | 0.413 | trapped 45.6 · h2h 0.143 | renoir-23 shape terms off: econ~ +0.13, win 0.62→0.75 ([S-45](taxonomy/S-45.md)); lune-r1-07 wins 22→29 ([S-32](taxonomy/S-32.md)) | esquie-04 trapped 45.6→54.6 (+20 %) ([S-03](taxonomy/S-03.md)) |
| Queen of Spades | 0.688 | 0.609 | trapped 35.4 · self 0.263 | renoir-07b unseen 8: +0.51 econ~ ([S-26](taxonomy/S-26.md)); ares-v33 6–0 ([S-14](taxonomy/S-14.md)) | esquie-04 trapped 35.4→40.5 (+14 %) ([S-03](taxonomy/S-03.md)) |
| Schooltime | 0.688 | 0.790 | trapped 34.5 · ally-body 0.146 | renoir-25 crowdexplore +0.83 econ~ ([S-26](taxonomy/S-26.md)); sciel-03a +0.600 ([S-25](taxonomy/S-25.md)) | renoir-01c −0.41 econ~ ([S-27](taxonomy/S-27.md)); renoir-22 −0.38 ([S-26](taxonomy/S-26.md)); esquie-02 win −9 pp ([S-28](taxonomy/S-28.md)) |
| Slithery Fight | 0.594 | 0.640 | trapped 101.3, newborn 73.6 · h2h 0.226 | esquie-04 trapped −19 %, newborn −28 % ([S-03](taxonomy/S-03.md)); ares-v33 5–1 ([S-14](taxonomy/S-14.md)) | r3-03 escape-early trapped 101.5→112.1 ([S-06](taxonomy/S-06.md)); lune-r1-07 p@250 −4 % ([S-32](taxonomy/S-32.md)) |
| Trauma | 0.750 | 0.375 | trapped 14.0 · wall 0.353 | esquie-03b win +6 pp, seeds 1–3 ([S-28](taxonomy/S-28.md)); renoir-01c +0.14 econ~ ([S-27](taxonomy/S-27.md)) | esquie-04 newborn 4.3→12.0, ×3 ([S-03](taxonomy/S-03.md)); ares-v28 0–2 ([S-05](taxonomy/S-05.md)) |
| Trophy | 0.719 | 0.594 | portal 13.2 · wall 0.177 | sciel-03c +0.248 econ~ ([S-22](taxonomy/S-22.md)); esquie-03b p@250 +0.14 ([S-28](taxonomy/S-28.md)); lune-r1-07 dragons@100 19.2→23.0 ([S-32](taxonomy/S-32.md)) | esquie-02 (gate-bug form) econ_pct 0.594→0.470, win 0.719→0.562 ([S-28](taxonomy/S-28.md)) |

## 6. The opportunity space

Derived from §5 and the stop reasons in §4, not asserted. Size = the problem's measured gap or the largest effect the line
has shown; cost = what the decisive test needs (L ≈ one D-032 run on the desktop, ~25 min per 1,200 games; M = a new
switch on Ares plus a run; H = new infrastructure). Lanes are the existing ones (R-index, 30 Sep).

| # | Opportunity | Derived from | Size | Cost | Lane |
|---|---|---|---|---|---|
| 1 | Arrival-level deconfliction on Ares: target claims over sonar (Sciel's proposed sciel-05 packet) or a port of the router's greedy bed assignment and de-convergence | [P-04](taxonomy/P-04.md) × [S-23](taxonomy/S-23.md) empty on Ares; the ally head-on guard rejected every economy gain ≥ +0.05 (mean) measured on Ares: sciel-03a…04b +0.039…+0.105 econ (gen +6…+16 %), renoir-07a +0.110, V08 +0.188 | H | M | rc (guided; its first item, Sciel-03b, is spent) |
| 2 | Run the re-scores nobody ran: those D-032 mandated (renoir-17a/17d/18a/18c, lune-r1-07; 18a has only a seed-2 repeat, pooled +0.015) and the Monoco ones the ledger queued under it (ra-03 +0.021, 2 seeds; ra-05); pool the threat-weight family (four settings — renoir-17a/17c/17d, ra-11 — all Δecon +0.002…+0.019) | [S-30](taxonomy/S-30.md), [S-38](taxonomy/S-38.md), [S-62](taxonomy/S-62.md), [S-32](taxonomy/S-32.md) stopped on the +0.05 bar that D-032 replaced | M | L | R-4b / director |
| 3 | Panel-measure the live teammate bots V28, V32, V33 under D-032 on both panels, with and without the 32×16 terms (V33 is live and still carries them; they also fire on Portals and Dilemma) | [S-05](taxonomy/S-05.md), [S-14](taxonomy/S-14.md) screened on 20 games vs one opponent; [S-45](taxonomy/S-45.md); L24 wave 2 unread | M–H | L | M-1 (Esquie) or R-3 |
| 4 | Execute the D-029.4 transfer (dead-end peel and tree values, arrival maps) plus cx-b02's respawn-gap memory as Ares switches | [F-24](taxonomy/F-24.md), [F-25](taxonomy/F-25.md), [F-05](taxonomy/F-05.md) live only on the chassis; targets the mill ([P-01](taxonomy/P-01.md), Slithery 101 len/1k) and starved openings ([P-09](taxonomy/P-09.md)) | H | M | R-3 successor / rc |
| 5 | Finish the structure-gated forms: esquie `min_age` 16–18; V19 split gated on the fast-bed + churn signature; bed waiting keyed on structure (flat waits won QoS +0.16 and Trauma +0.14, lost Devil −0.72) — issue R-6 | [S-28](taxonomy/S-28.md) local hold, [S-03](taxonomy/S-03.md), [S-27](taxonomy/S-27.md); R-6 never issued | M | L | M-1; R-6 |
| 6 | Put parameter liveness into the gate: refuse to score a variant whose flag-on build shows zero divergence from its parent in the golden replay, and make every lane runner purge the header-only wasm cache (cx `arena.py` already does) | [P-19](taxonomy/P-19.md): ra-04 measured a dead parameter (Δ 0), ra-05/09/10 committed switched off, r3-03 v1 inert for 160 games, V09 counts a dead `search_depth1` | protects every lane | L | R-4b |
| 7 | Seat-B analysis on Ares, then the frame mirror as a C++ wrapper | [P-16](taxonomy/P-16.md) × Ares empty; lune-r1-07's gain sits in seat B (dragons +0.106, length +0.101; seat A retention flat); jet: seat A 32/48 on symmetric maps; [S-47](taxonomy/S-47.md) Python only | M | L–M | S-1 (corpus), then rb/rc |
| 8 | Decisive tests for four open contradictions: C-05 (deaths vs economy, one joint per-map regression), C-06 (r3-03 seed 3 against a units-matched control), C-10 (base against itself over 5 seeds for the null spread), C-01 (V05 vs V06 under both scorecards) | [contradictions.md](taxonomy/contradictions.md) §A | frames all of P-01…P-11 | L | S-1 / K-1; R-3; R-4b |
| 9 | Synthetic generalisation maps with dead ends and portal mouths (the gen panel has 0/20 dead ends and 3/20 portal mouths, so L14, L24 and every portal mechanism cannot be tested off-pool) | [P-15](taxonomy/P-15.md), [F-48](taxonomy/F-48.md); K-1 Parts 3–4 not started | M | M | K-1 |
| 10 | Build the two local fight rules (refuse contact > 6 cells from a bed; converge-or-refuse) | [S-40](taxonomy/S-40.md) never built; [P-12](taxonomy/P-12.md): 11.6 own deaths and 32.9 length per fight vs band 6.8 / 18.9 | M (fights do not decide non-top-ten games, C2) | L–M | rb / rc |
| 11 | One learned decision in C++ (split now? enter this portal?) trained on the corpus and exported as a header | every learned attempt ([S-53](taxonomy/S-53.md)–[S-56](taxonomy/S-56.md)) was whole-policy Python and stopped on CPU, host transfer or the teacher ceiling — none of which binds a single C++ decision | unknown | H | RL-1 / SF-1 |
| 12 | Vary momentum and add modes on Ares | [A-24](taxonomy/A-24.md) never built; `momentum_*` never varied on Ares (L13); Sciel-02a's two-state steering moved its row | M | M | SF-1 |
| 13 | Key the search budget on observed local sparsity instead of round 40 | [S-32](taxonomy/S-32.md) hold at a round threshold; R-1's own recommendation; L02 volatility keying never measured | M | L–M | SF-1 / R-5 |
| 14 | Crown and feeding on Ares: first the corpus test (does r500 margin predict the win?), then vary `crown_*`/`feed_*`, none of which any lane has moved | [A-14](taxonomy/A-14.md) never varied; [P-13](taxonomy/P-13.md); L15 test not delivered | L–M | L | S-1 |
| 15 | Measure body suppression of bed spawns on our own games | [P-24](taxonomy/P-24.md) no attempt; one public game: 2,088 of 6,902 renewals blocked | unknown | L | S-1 |

Lines that stopped for reasons that no longer hold, and are not in the list above because a stronger form is listed:
the router ([S-58](taxonomy/S-58.md), measured on a chassis at 0.44–0.47 of field economy; L07's revival trigger has not
fired), blind-exit memory and dive caps ([S-16](taxonomy/S-16.md), [S-19](taxonomy/S-19.md); present in Ares, never
varied — cheap sweeps inside #2), Python CPU cuts ([S-33](taxonomy/S-33.md); the threat radius 7, reach clamp 1–3, density
source cap and separation BFS caps are still Python-era limits in Ares and were never widened; R-1 widened only search,
flood and sprint caps). Lines that stopped for reasons that still hold: pre-entry portal gates ([S-15](taxonomy/S-15.md),
volume throttles on both hosts), the atlas ([S-20](taxonomy/S-20.md), out-of-sample rule), swarm dissolve
([S-24](taxonomy/S-24.md)), pace forcing ([S-35](taxonomy/S-35.md)).

## Keeping this current

On each update request: `git log --since=<last T-1 commit>` over `docs/findings/`, `docs/hub/HYPOTHESES.md`, the
decisions file, `claude/*-status.md` and every `origin/r/*` branch; add or amend the entries touched (new ids are appended,
never renumbered; a changed verdict is a new line in the entry's change log, the old one stays); regenerate
`taxonomy/matrices.md` from the `_*.tsv` summaries; re-derive §6; report the diff in `claude/t1-status.md`. Ledger changes
are proposed there, never made here.
