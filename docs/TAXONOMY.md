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

**Registers** (detail too large for this page): [map × mechanism](taxonomy/map-mechanism.md) (553 rows) ·
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

## 3–6

In progress (T-1 initial build).
