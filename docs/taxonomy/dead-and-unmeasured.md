# Dead, map-keyed and unmeasured register

Merged from the `## Dead / undocumented / never-measured` and `## Prompt vs delivery` sections of the nine extraction notes (`/home/claude/work/notes/*.md`; `d1` governance also contributes its ledger reconciliation). Each row gives a pointer: a corpus path, `origin/<branch>:path` for branch-only files, or `project:claude/<doc>` for project docs. "(inferred)" marks items the notes derived from code reading without a run.

## Contents
- [(a) Dead parameters, unread state, never-flipped switches, unreachable branches](#a-dead-parameters-unread-state-never-flipped-switches-unreachable-branches)
- [(b) Terms keyed on map dimensions or map identity](#b-terms-keyed-on-map-dimensions-or-map-identity)
- [(c) Built but never measured; mandated but not delivered](#c-built-but-never-measured-mandated-but-not-delivered)
- [Counts](#counts)

## (a) Dead parameters, unread state, never-flipped switches, unreachable branches

Effect column: what is known about the consequence. "Varied → exactly 0" means an experiment changed the item and every game came out identical to the parent.

### Ares C++ line (V06 and descendants)

| Item | Lineages | Pointer | Effect |
|---|---|---|---|
| `pearl_ttl` — no call site; policy reads `memory_ttl` | Ares V06 and every descendant (renoir, lune, sciel, esquie, monoco, ares-v07…v33) | bots/ares-v06-expanded-search-support/params.hpp; origin/r/monoco:claude/ra-status.md (ra-04) | ra-04 varied it → exactly 0 ("The changed constant has no call sites") |
| `search_depth1` — declared, unread; `frontier_search_depth` only gates the value-bound early exit | Ares V06+ | params.hpp; F/2026-09-30-r1-search-ladder.md | ares-v09 README claims "16 → 20" for this knob; that part of V09 cannot act |
| `bed_wait_max`, `bed_tie`, `ally_yield`, `dive_cost`, `dive_min_age`, `blind_landing_penalty`, `keep_facing_bonus`, `visit_ttl_count` | Ares V06+ | params.hpp:14-201 (c1 Part 2) | declared, no reader; never varied |
| `bed_wait = 0.0` constant → future-bed branches in `cell_value` (policy.hpp:741-742) and `escape_resource_value` (:161-162) unreachable | Ares V06+ (inherited from V05 bed_wait fix) | policy.hpp; c1 | branch becomes live when varied: renoir-01a/01c −0.065 / −0.058 econ~; esquie-02/03/03b gate it (S-28) |
| `head_block = 0` → flood head-block code (policy.hpp:922-931) unreachable | Ares V06+; `head_block 0` also in every Python host | policy.hpp; pa1; pa2 | Python: sinbad-v02 ablation with head_block on −8; Ares: never varied |
| `indicator = false` | Ares V06+ | params.hpp | never flipped |
| Sonar type 3 (inherit) decoded, never sent | Ares V06+ | radio code (c1 Part F) | dead receiver |
| `World::atlas_try()` / `atlas.hpp` defined, never called (V08 is the only caller); `Params::atlas_enabled` | Ares V05, V06 and descendants except V08 | world.hpp:276; F/2026-09-30-ra-lane.md (Base row) | renoir-00 with `atlas_enabled=false` → 0 divergent over 16,715 golden turns (atlas-off as shipped) |
| ares-v27 `map_has_known_portal` atlas branch unreachable (atlas never populated) | ares-v27 | bots/ares-v27-no-portal-farm-upgrade/ | README claims atlas use; branch cannot fire |
| Dead state: `atlas`/`atlas_bed`, `seen_count`, `last_exit_portal`/`round`, `last_move`, `DragonMem.cell/facing/first_round`, `echoes`, `fwd.first/parent/dives`, `rev` Grid, `nav::dist/path/rev_dist` (policy side) | Ares V06+ | c1 Part F | computed or declared, not read by policy |
| Orphan comment for removed `split_enemy_cheb` | Ares V03+ | params.hpp:19-20 | none |
| `shape_terms`, `monoco_sprint_discipline`, `monoco_threat_budget`, `sit_enabled` (sciel-01a), `pt_enabled` (sciel-02a) left in bots, default off | esquie, monoco, sciel | origin/r/esquie:bots/esquie-01-nodevil/params.hpp:16; origin/r/monoco, origin/r/sciel bot dirs | off state = parent behaviour |
| Monoco switches committed OFF: ra-05 (`memory_ttl`), ra-09 (`escape_spawn_area`), ra-10 (`pearl_value`) | monoco | origin/r/monoco:bots/ra-05*, ra-09*, ra-10* | bot directory behaves as the parent (d3) |
| r3-03 v1 escape still required `best_score < −500` | r3-03 v1 | F/2026-09-30-r3-ares-leaks.md | wired inert → 160 games bit-identical to V06 |
| Single-knob moves measured inert: renoir-10a open15 (79/80 identical, Δ 0.000), 05b splitval10 (Δ −0.003 [−0.010, 0.003]), 20b hunt40 (Δ 0.000) | Renoir on V06 | F/2026-09-30-ra-lane.md | varied → exactly 0 or indistinguishable from 0 |
| cx-f05 `f1_escape` declared, never read (probe unswitchable); cx-f05 F-2 gates off; cx-f03 sprint governor `f3_sprint=false` | cx-f chassis | origin/cx/f:bots/cx-f05*, cx-f03*; F/2026-09-30-cx-f01-leaks.md | switch cannot be exercised / built-and-off |
| cx-b02 `ally_claim_r` never read; `crowd_w=0`, `split_crowd_max=99`, `crowd_room_k=0` built-and-off | cx-b router | origin/cx/b:bots/cx-b02*; F/2026-09-30-cx-b01-router.md | router crowd rules never active |
| Feeder chooses a DEAD move next to the visible crown (sacrificial self-kill feeding) | Ares V06+ | policy.hpp:1287-1296 | undocumented live behaviour; no finding describes or measures it |
| Threat probability highest (0.9) when our dragon is longer | Ares V06+ | policy.hpp threat model (c1) | undocumented; never isolated |

### Python hosts (yuna / tyr / fenrir / bifrost / gavroche / S1–S2 lines)

| Item | Lineages | Pointer | Effect |
|---|---|---|---|
| `v_stale` 1.5 ("per 100 rounds since a tile was seen") — no consumer | every SIN/MC/INT and yuna-derived params.py: yuna, tyr, bifrost, skadi, heimdall, loki, chaewon-y, pace, eunchae, spike, the-goat, jet, sinbad, gavroche, gaia, fenrir, odin, vicious, fafnir, newton, ein-dog, ed, scholze, witten, fermi, valjean, javert, VN | bots/sinbad-v07-divecap/params.py:L24 (and each copy) | seen-age never enters target value except via gossip trust (F-03) |
| `open_mode` 0 ("opening expansion", no code) | yuna-v01…x43, chaewon-y*, eunchae, pace, spike-x11/x12 | bots/yuna-v05-core/params.py | no code path |
| `handoff_bonus` 8.0 defined (params.py L145), never read | tidus-t08/t09 | bots/tidus-t08-dangerhandoff/params.py | README's "Bonus +8" never applied |
| `cert_target_ttl` 15 unread | sakura-s01 | origin/sakura/s01:bots/sakura-s01*/params.py | none |
| `risk_features.py` never imported; MC fitted-hazard table path off | all yuna-derived hosts; shipped inside gavroche, vicious, fenrir, gaia | bots/yuna-v05-core/risk_features.py | dead module |
| `roles.outgoing` / `roles.decode` (radio owns messaging); `tactics.bfs_from` / `rev_dist` / `exits` | yuna-derived hosts | bots/yuna-v05-core/roles.py, tactics.py | never called |
| `training_trace`, `density_trace`, `escape_trace` (never set); `phase_trace` (only yuna-t03); `training_trace` key with no reader in valjean/javert | yuna-derived, valjean, javert, s02-portal | params.py of each | diagnostics never produced |
| `density_policy` 2 (gradient) flipped only in gavroche-v16…v19; v31–v66 overrides omit `density_policy`/`info_aggro_push`, so the gradient is off in v31–v66 and in gavroche-v54, vicious, fenrir, gaia | gavroche and descendants | bots/gavroche-v*/override.py (pa2 override record) | gavroche-v28 was a no-op (gate on a 0 param); Scholze credits v32's core to a term that is 0 |
| `attack` always 1; `child_tail` only x25–x27 | yuna | bots/yuna-x25-tail-all… | never varied elsewhere |
| tidus `crowd_mid_switch` (t07 override has literal `THRESH` → NameError at import) | tidus-t07 | bots/tidus-t07-switcher/override.py | t07 cannot start ("UNBUILT-OUT") |
| `sk_camp_w` 0.0 → `sk_camp_horizon`, `sk_camp_wait`, `sk_camp_floor` unread in effect | sakura-s02 (shipped) | origin/sakura/s02:bots/sakura-s02-arrival-econ/params.py | camp code kept, off after measurement (Schooltime total r250 135→52) |
| yeji-s06 `dissolve_on` 0 → `diss_any`, `diss_len_margin`, `diss_enemy_clear`, `onset_*`, `feed_max_len` 3, `feed_radius` 30, `feed_late_round` 0 dead | yeji-s06 | origin/yeji/s01:bots/yeji-s06*/main.py:1834-1852 | dead with dissolve off |
| yeji `w_field` 12 / FIELD bed field built from map prior; `map_prior` = 0 (inferred) | yeji-s06 | origin/yeji/s01:bots/yeji-s06*/main.py:615, 694 | dead (inferred) |
| yeji `target_rate_d0` 0, `unit_cells` 0, `w_parity` 0 (screened off); `role_mix_on` 0 → hunt./scout. role slices and `mix_*` tuples unread (inferred) | yeji-s01…s06 | origin/yeji/s01:bots/yeji-s0*/params | screened off / unread |
| `λ_ctrl` = 0 "hook only" | kazuha, yeji | S1 bots params | never active |
| javert `v_hunt` unread; `LEN_DENSITY` length field built, unconsumed in x02 | javert | bots/javert-x02-lendensity/ | x02 still gave the reserve gain (10–2): the effect runs through what allies hear and relay |
| fafnir `strike_support` read but inert; `bed_per_k` 0, `fast_edisc` 0, `dive_units` 999, `blind_mem` 0, `crowd_need` 0 dead by default (newton turns `fast_edisc` on) | fafnir-v01 and descendants | docs/leaklab-findings.md; fafnir params.py | f3: every fixture identical; f12 reserve 16 fixtures byte-identical ("the active mechanisms never fire on the frozen families") |
| sinbad `fast_per` 0 ("tested: noise"), `ladder_nc` 0 ("no gain") | sinbad | bots/sinbad-v07-divecap/params.py | measured null, left off |
| valjean `room_r`, `sat_disc`, `sat_hunt`, `w_crowd_split`, `w_confine_split`, `mass_rays`, `pressure`, `support`, `escape_eval`, `region`, `dead_end_disc`, `trap_cap`, `vac_eat` default off | valjean | bots/valjean-v01-portal-memory/params.py; docs/feynman.md §4 | rejected set in feynman §4; the rest never measured |
| VN `atk_space`; newton `crown_split` (null), `guard_age` (null) | von_neumann, newton | docs/von_neumann.md; docs/newton.md | never measured / null |
| vicious temporal switches (`temporal_egress`, `_split_guard`, `_open_bonus`, `_conversion`, `_crown_state`, `_body_state`) read via `P.get` with no params.py entry | vicious | bots/vicious-x*/ | defaults hidden in code |
| porthos P1 swarm-push term `aggro_push` | porthos | docs/von_neumann.md (cycle 2) | engages nowhere: vn grad1 0 flips; VN INFO-1 "can never change an argmax" |
| einstein `portal_access`, `portal_memory` default 0 | einstein-v02 | experiment_data/strategy_leaks_2026092623/REPORT.md | access-only arm identical to parent in every matched cell |
| Fermi x01 support correction | fermi | experiment_data/strategy_leaks_20260926T225505Z_fermi/REPORT.md | changed cost on 3/859 threatened turns; no action changed |
| Vibing split-size rule vs learned arms | team-recon graft | experiment_data/team_recon_306_20260927_claude/REPORT.md §5b | identical action streams in 12/12 |
| Yuna momentum variants x14/x15/x23/x39/x40 | yuna | bots/yuna-x14…x40 | plateau at w 0.6: varied, none moved results |
| gavroche v28 (`info_aggro_push` gate on 0); tyr V30 ("exact same outcomes"); tyr V26 ("no effect") | gavroche, tyr | docs/gavroche-resume-2026-09-26.md; docs/tyr-family.md | varied → exactly 0 |
| serre-v02 `compact_max` / `doctrine_*` / `fast_contest` default off | serre | bots/serre-v02-doctrine/; docs/serre.md §8 | arms v02a/b/c have no results |
| estuary `continuation.py` implemented, disabled (`estuary.safety=0`) | leviathan-x03 Estuary | docs/leviathan/ESTUARY_BOT_HANDOFF.md | disabled after measurement (off: Stronghold subset 8–4 → 11–1) |
| the-goat-v02 retained, "not runtime-ready" | the-goat | docs/the-goat-family.md | not runnable |
| Hard-coded knobs outside params: heimdall `SCAN_PERIOD` 4, `ECHO_TTL` 2, `HEAD_LANE_COST` 1.6, `BODY_LANE_COST` 0.35, decay 0.55, `bed_wait` 12 − 6×activity, threat cap 0.18; tyr separation `_topology` literals; sim BLIND cheb > 3; threat_map cheb 7; sprint gate cheb 4; prune ttl 400; trail cap 700/600; visits decay 16 | heimdall, tyr, yuna-derived | pa1 §Dead (hard-coded knobs) | never swept |

### Model lines (ouroboros, hydra, kraken, leviathan, musketeers)

| Item | Lineages | Pointer | Effect |
|---|---|---|---|
| Echoes parsed, never consumed; `w_blind_portal` 0.0 (evaluated, zero weight); ladder/orphan/`w_eat_prod` knobs default 0 in v12 | ouroboros-v12/v13 | bots/ouroboros-v13-ladder/main.py:L173-175 | `orphan_role=1` measured negative; `w_eat_prod` never reported |
| Doom memory `w_doomed` = 0 since late v05; tunnel / zone-heat / spread / blind-portal terms flagged "prove or delete" | ouroboros v05+ | docs/ouroboros-macro-spec.md §1.3 | no ablation table; zero-wall deaths come from exact candidate simulation |
| s02-portal `bed_atlas`, `atlas_far`, `pre_wait`, `sprint_pearl`, `v_contest`, `explore_on` present and off; `info_aggro_push` 0.0; trace switches 0 | ouroboros-s02-portal | bots/ouroboros-s02-portal/README.md | off because they lost (S2 economy arms) |
| `relay_ttl` never read; `want_split` risk argument unused; v04 = v03 + empty override | kraken-v04/v05 | bots/kraken-v05-safety/; docs/leviathan/LINEAGE_REVIEW.md | none |
| `sprint_max`, `bed_rearm_gap` (world.py:L300 hard-codes r+14), `late_bed_mult` never read; `crown_spacing` 0 / `crown_space_pen` 0.0; `yield_gap`/`yield_radius` "kept, inert"; `indicator` 1 costs bytes | hydra-v11 | bots/hydra-v11-macro/ | README's "re-armed on the mean gap" not implemented |
| Teammate self-reports decoded and stored, never consumed; echoes "parsed and ignored" | leviathan v01–v07 | docs/leviathan/DESIGN.md | L1 probe only |
| `pearl.prepos`, `pearl.confirmed_only` neutral 0 in config, enabled only by params.py | leviathan-v09 / x03 | bots/leviathan-v09-arrival/ | config default ≠ shipped value |
| `STRATEGY_VERSION` 0 (contextual scores disabled); rich features computed, P0 consumes 7 columns; VERSIONS string labels identical across x01…x04 (only int versions switch) | dartegnan, aramis | bots/dartegnan-v01-contract/ | computed, unused |
| features v2 (phase, early, sat, area_here, room_ratio, counts, lengths, child_room, swarm_gain) "computed but UNUSED by P0" | porthos-x03 | bots/porthos-x03-swarm/ | computed, unused |
| Sonar echo counts stored but read only by cx-f02, r3-02, heimdall, hydra-v06 | all other lines | CATALOGUE F-19 | information without a consumer (P-23) |
| Coefficients outside the parameter table | ouroboros | docs/leviathan/LINEAGE_REVIEW.md | not tunable by the harness |

### Instruments and governance code

| Item | Lineages | Pointer | Effect |
|---|---|---|---|
| `portal_steps` counter dead on main after the `-X ours` merge | tools (R-4) | F/2026-09-29-r4-01-tooling.md | portal-step metrics read 0 until R-4 fixed it |
| `split_has_room` len-2 reversed iterator `length_error` swallowed by the runner catch-all | cx-f01 | F/2026-09-30-cx-f01-leaks.md | a branch silently falls back |
| unswbc 1.2.2 sandbox wasm cache hashes only .c/.cpp | all C++ bots | d3 instrument notes | header-only edits reuse a stale build (arena.py purges) |
| Vendored `analyse()` undercounts portal steps 5–15 % | tools | d3 instrument notes | biased portal rates |
| 400-refusal fallback to single-orientation blocks | hub (D-022) | F/2026-09-28-director-decisions.md D-022 | "stays as dead code (no wave exceeds the map count)" |
| `tests/test_hub_analysis_a1.py` imports functions not on main | codex A1 | tests/ (per Claude memo) | fails at import |
| jet `firstturn_cpu.py` | jet | docs (jet) | "returned zeros, was not restored" |
| `configs/porthos/reserve.toml.disabled`; curation scripts "not present in this checkout" | porthos, benchmarks | configs/porthos/ | unrunnable (maps missing) |
| Exceptions firing every game in the live control: fenrir-v18 / Tyr V12 `separation.py` (`bed_wait=0` ZeroDivisionError; missing global `RESOURCE_PAUSE_USED`) | fenrir-v18, Tyr V12 | F/2026-09-29-ouroboros-s02-portal.md | live control ran its fallback path; fixed in Ares V05 and ouroboros-s02-portal |

## (b) Terms keyed on map dimensions or map identity

| Term | Condition | Lineages | Pointer | Measured effect if any |
|---|---|---|---|---|
| `devil_center_bonus` (x-midline pull until r42), `devil_lane_bonus` (y lanes by id until r100), `ally_body_buffer` | `W == 32 && H == 16` — live on Devil, Prisoners Dilemma **and Portals** | Ares V06 and all descendants except where `shape_terms=false` (esquie); origin Tyr V12 | bots/ares-v06-expanded-search-support/policy.hpp; D-033 | renoir-23 off: pooled −0.042 [−0.103, −0.006]; Devil econ~ −1.22, win 1.00→0.31; Dilemma +0.13, 0.62→0.75; devil_tr / trophy_tr base win 17 %; esquie nodevil Devil 1.00→0.50, Portals diverges 638 turns |
| `devil_center_progress`, `devil_lane_progress`, `ally_body_buffer` | `w.W != 32 or w.H != 16` returns early | tyr-v09…v34 | bots/tyr-v33-targeted-resource-defense/policy.py L39-76, L465 | tyr V12 vs V01 on Devil 12–0; central cells by r42 59 vs 8 |
| `has_long_center_beds` | 32×16 | tyr-v29 | docs/tyr-family.md | Dilemma 0–4 |
| `early_feed_map_sizes` ((63,27),(48,24)); `early_pearl_map_sizes` ((25,25)); `opening_dive_map_sizes` ((32,16)) | exact (W,H) | tyr-v23; v26–v28, v33; v33 | bots/tyr-v33-targeted-resource-defense/override.py | V33 vs V12 seeds 1–18: Trauma 32–4, Autarky 2–34, Dilemma 6–30 |
| Trophy sector term | `w.W * w.H == 625` (Trophy identity) | bifrost-v28 | bots/bifrost-v28-tuned-trophy-sector/ | won two direct Trophy games; no external change |
| `opening_sector_max_cells`, `info_aggro_max_cells`, `enemy_disc_compact_cells`, `bed_wait_compact_cells`, `ally_route_max_cells` | ≤ 625 cells | bifrost v08; v11/v19; v13/v18; v15; v22–v25 | docs/bifrost-family.md; params of each | V23 route ownership QoS 8–0 → 3–5 |
| `arena_lane_area` 121 | exact arena size → identity | gaia-v53 | bots/gaia-v53-arena-opposing-lanes/ | none recorded |
| `tiny_opening_area` 400, `threat_pearl_min_area` 400, `large_map_area` 2000; V47 medium band 400–1,999 | area thresholds | gaia v45, v47 | docs/gaia-family.md | V46 all-map threat gate regressed Big Empty; V48–V50 arena splits lost both Fenrir games |
| Slithery / Portals onset | `W == 63 && H == 27` (main.py:165); `pid >= 4 && W == 32 && H == 16` (main.py:578); `onset_portals` / `onset_slithery` 300 | yeji-s01 | origin/yeji/s01:bots/yeji-s01/main.py | yeji-s01 PD − v10: Portals −0.25, Slithery −0.31 |
| Dissolve onset | width == 63, or ≤ 625 cells with ≥ 6 portal pairs (kazuha); 63×27 or 512 cells with ≥ 6 pairs (sakura); 32×16 with start length 3 or ≥ 5 pairs, 63×27 → r300 (chaewon-s01); fixed public dimensions for Portals and Slithery (eunchae) | kazuha, sakura, chaewon, gpt-eunchae S1 | S1 findings (F/2026-09-28-*-s01-swarm-dissolve.md) | kazuha dissolve Portals −4, Slithery −4 |
| Map atlas modules `atlas_<W>x<H>.py` (25x25, 25x35, 32x16, 32x32, 48x24, 54x18, 60x40, 63x27), several maps per size resolved by kelp string | exact (W,H) + kelp | chaewon, eunchae, pace, sakura-s02; yeji `mapprior.py`; pace-v02 per-map curve via atlas name | origin/sakura/s02:…/world.py:82; bots/pace-v01-nolimit/world.py:L229 | s02-portal +0.108 (atlas + safety, component split unknown); chaewon-y02 ±0.000; yeji-s02 map field Devil +0.44 / Default −0.50 |
| Frame table `FRAMES` by (W,H,team); dispatcher | exact (W,H); `W*H <= 400` | jet-v01…v05 | bots/jet-v05-frame-mirror/; project:claude/jet-status.md | dispatcher "never fires on the live pool, because every live map is larger than 400 tiles"; frame mirror QoS 12 vs 7, Schooltime 12 vs 9 |
| Compact doctrine / portal-scout guard | NC ≤ 625 | ouroboros-v13 DOCTRINE ("open": {}), hydra-v11, hunter-v20…v23, leviathan-v09 `compact_only` | bots/ouroboros-v13-ladder/; bots/hunter-v23-supported-arrival-feed/main.cpp:348-349 | ouroboros-v13 compact 65–1–54 → 99–1–20; leviathan-v09 compact 79–69–2 → 93–57; hunter-v20 portal scouts disabled there ("probes depleted V20 there") |
| Compact / fast-bed thresholds | NC ≤ 625 (≥ 256 floor for some) | spike-x08 `compact_nc`; tidus `fast_edisc_nc` 625 / `nc_min` 256; skadi-v11 256–625; `pace_compact_tiles` 625; yeji `prior_max_cells` / `field_compact_cells` 625; `risk_features` compact; O13 / godel / einstein `compact_max_cells`; fafnir `compact_nc`; newton `fast_edisc_nc`; MC v05; odin v03/v06; serre-v02 doctrine; sakura-s02 `risk_features.py` | params.py of each (pa1, pa2) | avery-v07 compact production arena 3–8–1 → 7–4–1; others not isolated |
| Small / mid map tiers | NC ≤ 600; ≤ 2000 | avery `small_map_cells`; gavroche `opening_small_map_tiles` (v05/v08); O13 `team_target_small`, `scout_min_cells` 600, `team_target_mid` 2000; leviathan Python NC ≤ 600 / 625 / 2000 | params.py of each | none isolated |
| drake tiers | NC ≤ 200 / 300 / 650 / 1300; compact doctrine NC ≤ 650 | drake-v11 | bots/drake-v11-satutfix/main.py:L1086, L1491–1497, L1558, L1592, L1648, L1780, L1874 | none isolated |
| `large_map_area` | 1100 (v03, v11–v16), 1800 (v23/v25/v26), 3000 (v19/v20); v12 sets 10,000,000 to disable | doug | bots/doug-v*/ | no recorded outcomes except one 1–9 screen |
| `w_dir_nc`; momentum scope | NC ≤ 256 (= Colosseum / default_small size) | ein-dog | bots/ein-dog-x08-momentum-scoped/ | x04 momentum Devil +3, Colosseum −2 |
| `big_map_cells`, brawl spread, brawl detector | NC ≥ 3000; NC//50; NC ≤ 300; default_small signature | kraken | bots/kraken-v05-safety/ | none isolated |
| R2 component | disabled on boards > 64 | dartegnan | bots/dartegnan-v01-contract/ | none |
| Mimic input features | W, H, x, y, xn, yn as model inputs | ouroboros-m01 | bots/ouroboros-m01-vibing-mimic/features_view.py:L150-153 | m01: Devil 6–2, Trophy 7–1, Autarky 6–2 vs Big Empty 0–8, Portals 2–6, Slithery 2–6 |
| Learned donor gate | `width > 61.5` | 470 transfer graft on tew | experiment_data/team_recon_470_20260927T150303Z | never reaches threshold on widths 32/54/32: 0/12 activation |
| Feed clock `feed_from = 500 − feed_base − ⌊(W+H)·feed_k⌋`; gavroche-v20 `feed_base` 14 "start at round 410 on 64x64 maps" | W + H | SIN/MC `roles.py:L12` and every descendant; Ares (feed clock W+H, F-22) | bots/sinbad-v07-divecap/roles.py:L12 | "the inherited dimension-derived clock" (ed); not isolated |
| Radio message gates | FOOD and DENSITY only if W, H ≤ 64; PORTAL share only if 2·W·H ≤ 8192; vicious egress off NC > 4096 | all Python hosts; Ares radio field gates W,H ≤ 64 and 2·NC ≤ 8192 | radio.py of each; Ares radio code (F-02, F-22) | no pool map crosses the gates; not measured |
| Router horizon `clamp(√NC, 20, 60)` | tile count (observable, not identity) | cx-b router | origin/cx/b:bots/cx-b0*/ | not isolated |
| Compact 256–625 and ≤ 625 thresholds across the ouroboros/hydra/hunter/leviathan lines (summary) | NC thresholds | see rows above | d5 §Dead; pb §Dead | "No literal `W==`/`H==` found in these lineages' main sources" (pb) |

## (c) Built but never measured; mandated but not delivered

### Mechanisms built, never measured

| Item | Where | Why it matters | Id |
|---|---|---|---|
| ares-v12 (screen pending), v18, v29, v30, v31 ("Development screen: pending"); robert-v02 | bots/ares-v12…, v18, v29–v31, robert-v02-trap-pearl-gate README / CANDIDATE.toml | wave-2 enclosure/split variants in the production line with no result | S-02, S-05, S-01 |
| ares-v10…v20 not described in docs/ares-family.md (jumps from V09 to V21–V28; V19 used as base without a family entry) | docs/ares-family.md | the base of V21–V33 is documented only in READMEs | S-01, S-02, S-03 |
| Renoir 01b, 03a, 04a, 05a, 06b, 07d, 09a, 10b, 12b, 13a, 14a, 17b, 18b, 20a (7 listed "Queued, not run"; 7 built, unreported) | bots/renoir-*; F/2026-09-30-ra-lane.md | 14 of 47 ra directories have no result | S-26, S-27, S-09, S-30, S-38, S-21, S-02 |
| monoco ra-12 (94/160 rows, 37 Errno 35 failures) | origin/r/monoco:claude/ra-status.md | interrupted single-knob sweep | S-30 |
| esquie `min_age` 16–18 ("the untested middle"); structure-gated critical split (fast-bed + high newborn churn) | origin/r/esquie:F/2026-10-01-esquie-map-anatomy.md | the r50 Trauma gain lives in that window; the gated split is the proposed form of L24 | S-28, S-03 |
| sciel-05 target claims (proposed after the family closed) | origin/r/sciel:claude/sciel-status.md | named next form of the L12 economy (arrival-level deconfliction) | S-23, S-22 |
| r3-05 gen panel | F/2026-09-30-r3-ares-leaks.md | out-of-sample check missing | S-02 |
| ouroboros-s02 seed 2; Slithery A on 1.0.0 | F/2026-09-29-ouroboros-s02-portal.md | the +0.108 is one seed | S-17, S-20 |
| eunchae-s02 ablations, full panel, metered profile; gpt-eunchae s01–s06 (one unpaired game per version) | F/2026-09-29-eunchae-s02-pearl-band.md; F/2026-09-28-gpt-eunchae-s0*.md | "not evidence-bearing" | S-27, S-24 |
| clone-62 / clone-545 bots | eunchae-s02 finding | mandated by S2, "No bots/clone-62-v01 or bots/clone-545-v01 is claimed" (sakura built clone-62-v01) | S-56 |
| cx-b territory@100; Hungarian assignment; C1-C idle/waiting/contested-bed stats; C1-D §2–4 as its own bot; cx-c01-eff and cx-d01-portals bots | F/2026-09-30-cx-b01-router.md; C1-C/C1-D findings | blocked on chassis; C1-F implemented the rules instead | S-58, F-43, F-44 |
| Newborn-neck fix alone; truncated-trail salvage alone; hysteresis margin 0 ablation; certificate on/off in yeji (host sends handoff on the same ray); yeji-s06 online beds; Dilemma 10-dragon local map | S1 findings (d2) | components of the S1 generation never isolated | S-11, S-57, S-27 |
| chaewon-y06-lean (no numbers); chaewon-y04/y05 without CANDIDATE.toml; y05 HOLD on one fixture until the sakura-s02 port | origin/chaewon/s01 | the HOLD evidence is one fixture on the Python line | S-17 |
| spike-x05…x12 (README hypotheses only); tyr-v26/v29/v30 focused screens only; the-goat-v04 strategy (CPU-failed first); tyr pearl-funded threat CPU cost; heimdall echo constants | bots/spike-x*, tyr-v*, the-goat-v04, heimdall-v10 | mechanisms in code with no panel result | S-36, S-38, S-33, A-12 |
| vicious x06/x07 ("outcomes pending"), x10/x11 body-state, x12–x27; ed v01–v24; doug v01–v26 (except one 1–9 screen; v15 missing); ein-dog x01/x02/x03/x05/x06/x09/x10 | bots/vicious-*, ed-*, doug-*, ein-dog-*; campaign dirs absent from the corpus | results live only in absent `experiment_data/` dirs | S-43, S-44, S-57 |
| serre-v02 arms; serre G1–G7 graft roadmap; valjean default-off switches; VN `atk_space`; javert PORTAL_SCOUT (x04), SPACE_TRADE (x05); gavroche v20, v22 (bounded feeding); alik_test_bot; formatted-hunter-v22(-python) | docs/serre.md; bots/* | built, no recorded outcome | S-42, S-19, S-43 |
| fry-v04…v08, v10 (escorts, kamikaze); hunter-v16 boost-trap, v18/v19 look-ahead; ouroboros-v11 ("null result", no numbers); chimera-v01 gate verdict; athos x-series (docs/athos.md absent; x16 missing); m01/m01p `model.json` and `params.json` absent | bots/*; docs/leviathan/LINEAGE_REVIEW.md | look-ahead and learned components without numbers | S-60, S-53, A-22 |
| skadi-v07-productive-farm, skadi-v09-fafnir-soft-exit (not in docs/skadi.md); skadi v13 holdout; hydra-v11 not in the cycle-00 archive | docs/skadi.md; docs/cycles/ | undocumented directories | S-08, S-16 |
| Heimdall v10 judge check (one Big Empty game); avery sandbox CPU on Big Empty "still never done"; Faye F-004 decision on 64 archived fixtures (owner call pending) | docs/heimdall-family.md; docs/handoffs/avery-lineage-handoff.txt; docs/faye.md | CPU gate unverified for shipped candidates | S-33 |
| Undocumented Ares behaviours: sacrificial feeder DEAD move (policy.hpp:1287-1296); threat 0.9 when longer; clone-62 guarded mode masks certain-death first steps (wall+self 0.0/1k vs target 3.76) | c1; d2 | live behaviour never measured against outcome | A-14, A-11, S-56 |
| Mechanisms cut for CPU under the Python 100M budget: 3-step sprint candidates (gavroche-v21 all off lost 4/4); target search 1,500 → 160 → late 32–64 (gavroche v35–v66 Big Empty/Stronghold regressions; yuna-x37/x38 larger caps −7/−5); flood caps 24/40; reverse search removed (sinbad v02); valjean F2 topology normalisation (never run) | pa1 §CPU; pa2 §CPU; F/2026-09-30-r1-search-ladder.md | never re-measured on the C++ host, which has headroom (V06 max 8.6M) | S-31, S-33, S-62 |

### Analysis instruments with no consumer or no run

| Item | Where | Why it matters | Id |
|---|---|---|---|
| F1 validation V4 (own-bot logs) "Not yet used", V5 (toggle tests) "Not yet run" | docs/analysis/FEATURES.md; docs/analysis/F1-status.md | the 237 features are unvalidated against interventions | F-45 |
| HMM phase outputs (`hmm.json`, `phase_t1/t2`, per-phase rates); rule t2 "should not be used"; four-state HMM "next" | docs/analysis/FEATURES.md | no bot or gate consumer | F-45, A-15 |
| EPG (`epg_tau*`, `epg_conversion` log-odds 0.22/0.11), `density_ratio`, `bed_expected_share`, `bed_territory` | docs/analysis/FEATURES.md | analysis-only; NaN on corpus replays (no TILE fields) | F-45, P-23 |
| `game_stats/live_beds.json` (live bed maps with per-cell rates) | docs/analysis/C1-pace-targets.md | C1-E spec step 2 requires live beds; bot atlases use local-file counts (Schooltime 326 vs live 444; Slithery 339 vs 497; QoS 442 vs 472) | F-47, F-21 |
| `field_distributions.json` cited by BENCHMARKS | docs/analysis/benchmarks/ | file absent (only field_references.json, map_reference_medians.json) | F-41 |
| FEATURE_BACKLOG "next"/"idea": momentum/derivative reducers, revisits, allied head spread, portal transits/outcomes, `h2h_initiated_share`, sonar-rate-responds-to-state, contested pearls, role clustering, lead-dragon exposure, decisive round | docs/analysis/FEATURE_BACKLOG.md | never done | F-45 |
| `tools/rl_earlygame.py`, `rl_earlygame_gpu.py`, `rl_runtime.py`; tools/ouroboros, tools/leviathan, tools/loki scripts | docs/rl-earlygame.md (section duplicated); READMEs only | no training numbers, no bot consumer; scripts absent | S-55, F-27 |
| Strategy-discovery atlas | Witten report | source files missing ("cached bytecode but no readable source files"); expansion fails majority baseline; fresh probes 0/8 | F-51 |
| Replay-association hypotheses (reach ~30 units, `time_to_32`, enemy-corpse capture, frontier fraction, bed occupancy) | tools/replay_analysis studies (4, 26 Sep) | none turned into a bot term | F-50, P-23 |
| Body suppression of bed spawns | docs/public-replay-review-2026-09-25.md §3 | named "Candidate hypothesis", never measured | P-24 |
| Map-symmetry inference; tunnel / dead-end pricing; length-density radio (javert "10–2") | docs/leaklab-findings.md §5; sinbad handoff idea #1; serre G3; ouroboros-macro-spec P4; HANDOFF §4.3 ("nobody yet") | ranked, never built | A-17, F-24, S-24 |
| Strike-propensity gossip / per-opponent `p_strike` | macro-spec §6; kraken-macro-spec S7 "Untried"; godel cycle 2 | never built | A-11, S-42 |
| Sonar ablation per packet kind; judge-divergence tap game (authorised D-017a/D-018.4); refetch of the 9663 ranked series; autoscrim semantics | docs/analysis/RESEARCH_LIST.md; D-017/D-018 | never run live | F-19, P-22 |
| Frontier dominance test | docs/frontier-panel-20260929.md | all 16 bots undominated: no discriminating power at this panel size | F-50 |
| gavroche-v40 threat-off probe, v41 CPU profile | experiment_data/gavroche-v40-threat-off-probe_*/REPORT.md | diagnostic builds excluded from the benchmark roster | S-38 |

### Mandated by a decision or prompt, not delivered

| Item | Where | Why it matters | Id |
|---|---|---|---|
| D-032 re-scores (Renoir 17a/17d/18a/18c, Lune late cap) and the ledger's queued Monoco ra-03/ra-05 (L20) | F/2026-09-28-director-decisions.md D-032 | the one-seat screens overstated (C-11); the gate revision was never applied to its motivating rows | S-49, S-38, S-57, S-32 |
| R-4b (interval GATE line, corpse-share diagnostic) | docs/hub/prompts (R-4); d1 prompt vs delivery | L29 churn weight rests on it | F-49, P-07 |
| R-6 four-arm bed-guard ladder — prompt never issued ("prompt pending") | project:claude/r-prompt-index.md | L11 bed-guard (0.35) has no test; esquie-03b is the only relevant evidence | S-27, S-28 |
| R-5 eval tuner (folded into SF-1); SF-1 state & features; RL-1 curve matching; HB-1 Heartbreaker anatomy; R-2b blind lane (Basquiat); R-2c guided lane (Cézanne) | project:claude/r5-prompt-eval-tuner-opus.md, sf1-…, rl1-…, hb1-…, r2b-…, r2c-… | nothing in the corpus; L04 tuner depends on R-5 | A-04, F-45, A-23 |
| K-1 Parts 3–4 (Sophie; Parts 1–2 on r/sophie, not pushed); A2 corpus statistics (coverage atlas, decoy detection); S-1 opening component table and portals | project:claude/k1-…, analysis-handoff-A2-…, s1-prompt-stats-assistant.md | partial deliveries | F-50, F-51 |
| Ledger hypotheses never tested: L02 volatility-keyed extension; L04 tuner; L13 momentum on Ares; L15 crown consensus; L25 V09 profile as a named point; L31–L34 (state machines, mode belief, sonar coordination, learned state); H4 swarm flywheel | docs/hub/HYPOTHESES.md | weights set without a measurement | A-15, A-04, S-57, S-43, A-24, A-13 |
| L10 local fight rules (never built); L09 leader-coordinated fight protocol (dropped without a bot); L14 scout splits (stated test bed `maps/new` has 0/20 dead ends) | docs/hub/HYPOTHESES.md; esquie map signature | fight pricing is where gen fight-loss maps (pinwheel, seam, commons) would pay | S-40, S-41, A-26 |
| Wave-2 Ares V20–V33 not read into the ledger; no (T) rows despite the ledger procedure; V28 and V33 uploaded live (12440, 12584) while the hub was in shadow | docs/hub/HYPOTHESES.md; FRONTIER.md | L24 and L30 weights ignore 14 versions | S-03, S-04, S-05, S-14 |
| Midline-race replacement for the 32×16 shape terms | D-033; origin/r/esquie finding (L28) | Devil's win share drops 1.00→0.50 without the terms; the structural replacement is unbuilt | S-45 |
| C1-E feature-keyed pace targets (OOS rule 3) | docs/analysis/C1-pace-targets.md; d1 | targets are per map identity, not per observable feature | F-47, P-14 |
| v2.1 live pipeline confirmation ("No confirmation has ever opened; no promotion has ever happened") | docs/hub/PROTOCOL_V2.md; Audit 28 Sep 12:00 | local-to-live transfer never closed | S-52 |
| Certificate delivery geometry ("three lineages disagree", HANDOFF §4); A2 decoy method | docs/HANDOFF.md §4 | see C-60 | F-17, F-51 |
| S1: sakura skipped the 3-seed panel; chaewon ran 4 opponents on 80 fixtures; gpt-eunchae no panel, no 2×2; kazuha finding header "numbers below are placeholders" (stale) | F/2026-09-28-director-S1-evaluation.md; S1 findings | S1 arms are not on a common panel (C-61) | S-24 |
| S2: sakura-s02 seed 1 only (3 asked); ablation arms did not play clone-62; shipped bot fails the 1.0.0 hub gate (Slithery max 81.5M; p99 > 60M on three fixtures); eunchae-s02 param bumps only, "sprint funding not isolated" | origin/sakura/s02:F/2026-09-29-sakura-s02-arrival-econ.md; F/2026-09-29-eunchae-s02-pearl-band.md | S2 economy hypotheses tested on one seed | S-27, S-19, S-26 |
| P1 pace: falsifier precondition (≥ 80 % attainment) never met by any of the three authors; constraints "≤ 10 per 100 births, ≤ 5 per 1k" — "No arm satisfies them" (field 38.5 and 10.8) | F/2026-09-29-pace-v01.md (all three copies) | the causal pace hypothesis was not cleanly tested | S-35 |
| Tyr live-loss review asked for outcome metrics (portal/center arrival, pearl lead r30, segments per dead-end harvest, largest-dragon survival, wall deaths) | F/2026-09-29-tyr-v01-live-loss-review.md | later tyr screens report W–L by map only | P-10 |
| R-3 step 1 prescribed a V19 reach-band start; R-3 used C1-F switch re-targeting instead (V19 later tested by esquie-04) | F/2026-09-30-r3-ares-leaks.md | ordering, not loss of evidence | S-03 |
| cx-a01: launcher wrapper under `bots/_golden/` replaced by engine-callback recording | F/2026-09-29-cx-a01-chassis.md | changes how golden parity is recorded | S-50 |
| A1: codex v1 shallow pass; tap build and band download proposed by Claude and GLM, neither could run them (key/authorisation) | F/2026-09-28-analysis-*-memo.md | judge divergence still unmeasured | F-51, P-22 |
| Replay statistics handoff: four parallel studies, overlapping conclusions, none produced a bot change | docs/REPLAY_STATISTICS_HANDOFF.md | see C-51…C-53 | F-50 |
| Team-recon grafts (306 split size, 62 admission, 470 early feed, 7 production priority): all failed the same frozen +2/12 gate on one 36-fixture panel covering 10.31 % of map weight | experiment_data/team_recon_*/REPORT.md | the panel may be too narrow to detect a transfer | S-56 |
| STRATEGY_LEAK_DISCOVERY: Scholze promoted 3 versions (+2..+5 on 36-game arms) without the reserve or confirmation set; fafnir released despite the inactive reserve; no repair promoted | experiment_data/strategy_leaks_20260927T000855Z_scholze/REPORT.md; docs/STRATEGY_LEAK_DISCOVERY_PROMPT.md | promotion gates not applied | A-27, S-37, S-39 |
| Musketeer lineage reports (aramis/athos/porthos/dartegnan/javert) requested; not present as REPORT.md; porthos "fresh-map-family validation still owed" | docs/porthos-lineage.md | intention/executor results unverified off the panel | A-21 |
| Project brief roles and information propagation: kraken size-coded birth roles measured costly and dropped; ouroboros weight-slice roles with hand-offs (half never arrive); packet catalogues whose value was measured weak without consumers | docs/family-comparison.md; docs/ouroboros-design.md | the roles-at-creation premise has no positive measurement | S-61, A-26, P-23 |
| HANDOFF.md cycle plan (§8): only cycle-00 recorded; FRONTIER panel replaced the gauntlet process (inferred) | docs/HANDOFF.md; docs/cycles/ | unifier cycles not run | A-27 |
| ouroboros-macro-spec P0 feature-family ablation table, P2, P4–P7; GLM macro-spec P3–P5 (hydra-v11 reached P0–P2 only); kraken-macro-spec v06–v08 (production, aggression, economy) specced, not built | docs/ouroboros-macro-spec.md; docs/macro-spec.md; docs/kraken-macro-spec.md | planned build orders stopped after the first phase | S-59, S-36, S-42 |
| feynman F2–F9 EWMA density features (only F1A info-only delivered, 18–18); faye cohort cycles (no bot; F-002/F-004 not executed); serre composition (delivered by fafnir, not serre); ein-dog charter "doctrine must key on observable geometry, not map identity" (delivered momentum scoped by NC ≤ 256); newton compact-contact repair (devil-A only) | docs/feynman.md; docs/faye.md; docs/serre.md; bots/ein-dog-*; docs/newton.md | briefs partly delivered | F-12, S-46, S-36 |
| Gavroche stop rule ("if V66 did not work, stop … stage the best that avoids TLE") → V54 staged, not submitted; Skadi stop → v13 holdout not run | docs/gavroche-resume-2026-09-26.md; docs/skadi.md | stop rules followed; staged bot never submitted | S-33 |

## Counts

(a) 70 rows (19 Ares C++, 31 Python, 11 model lines, 9 instruments/governance); (b) 26 rows; (c) 64 rows (21 built-never-measured, 15 analysis instruments, 28 mandated-not-delivered).
