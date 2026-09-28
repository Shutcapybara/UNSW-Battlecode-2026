# yeji-s01-swarm-dissolve

**Lineage:** Yeji (`claude/yeji/01SVqD5S`). **Parent:** `ouroboros-v10-beacon` (single-file evaluator, Claude/Ouroboros). **Status:** frozen; **rejected locally** (see the 2×2). Kept as a benchmark and as the source of the production arm `yeji-s01p-production`.

Built to the S1 prompt (`claude/next-gen-prompt-S1-swarm-dissolve.md`): a swarm through the opening, then a crown fed by adjacent dissolution from a map-conditioned onset. Every tunable is in `params.py`; `main.py` has no defaults of its own. Mechanisms log `LOG ACT:<tag>` in the turn's single write.

## What changed from the host

| Layer | Change | Params (neutral value = host) |
|---|---|---|
| Strategy | `lambda_unit(t)`: split value × 1 until `produce_until` (100), linear to 0 at `produce_stop` (380) or the onset; unit target 64 on every map; every child a gatherer (no scouts, no hunters) | `unit_target` (0), `produce_until`/`produce_stop` (380/380), `role_mix_on` (1) |
| Strategy | Crown elected from r250 with an id stagger (`id*7919 mod 20`), only by a dragon no fresher ally report beats, min length 6; crown risk ×3, trap ×2, crowding ×3 | `crown_elect_from` (200), `crown_stagger` (1), `crown_elect_longest` (0), `crown_min_len` (4), `crown.risk` (1.6), `crown_trap_mult`/`crown_crowd_mult` (1) |
| Execution | `escort` (head for the crown within `feed_radius`) and `dissolve` (no action → death, only with our head on a real edge next to the crown's visible head, L ≤ 3) from `onset_portals`/`onset_slithery` 300, `onset_default` 400; production stops at the onset | `dissolve_on` (0 = host feeding: L ≤ 20 within 2 tiles from r400) |
| Execution | `salvage` logged (`ACT:salv`): host emergency split L−2, forced strikes, least-bad fallback | `salvage_on` |
| State | Map class from size + portal ids (Portals: 32×16 with a portal id ≥ 4; Slithery Fight: 63×27) | — |
| Messaging | Crown beacon carries the crown id; the birth certificate (backward ray) carries role, target, crown id and length | `cert_enabled` |
| Momentum | Target hysteresis: keep the current target unless another beats it by 1.0; switches reported per 100 rounds (`ACT:sw<n>_<turns>`) | `hysteresis_margin` (0) |

## Six-line measurement report

Panel: unswbc **1.2.2**, `--seed 1`, the ten live maps × both sides × 8 references (yuna-v02-core, gavroche-v32, sinbad-v07, hunter-v20, kraken-v04, vibing-mimic, witten-x03, fry-v14) = **160 paired fixtures** per arm, harness `tools/yeji/yrun.py`. Medians are over games that reach the round.

1. **Strategy.** `lambda_unit` = 1 → 0 over r100–r380 (or the onset); `lambda_crown` = crown risk ×3 from r250; `lambda_ctrl` = 0. Funnel (this bot, 160 games, whole panel): 676 dissolves → 995 corpse pearls → 826 eaten by an ally within 2 rounds (83 %) → 733 by a crown (74 %); crown alive at the end in 89/160 games; median longest r400 11 (opponents 7), r499 **17** (opponents 16; control 24). Compact maps: 159 dissolves, 176 crown-eaten pearls; open: 517 / 557. Conversion delivers well, but the mass is tiny (≈4.6 pearls per game) and the crown rules lose length.
2. **Execution.** 2×2 below. Production: `ACT:prod` 116/game; units r100 median 14 (control 14; open maps 17 vs 14). Salvage: 180 `ACT:salv` per game. Strike option: host's parity-less trade pricing (unchanged). Dissolve: see the funnel.
3. **Implementation.** Metered (`--sandbox -v`, vs sinbad-v07-divecap): Schooltime as A **max 54.0M, p99 36.2M, p50 23.1M, 25,158 turns**; Portals as B **max 40.5M, p99 32.1M, 9,254 turns**; zero `exceeded`, zero `MC_ERROR` (1.2.2). The 1.0.0 probes are in the findings file. **No degradation mode is implemented** (the host has none; the bot stays far under the cap, but a budget-aware mode is still owed).
4. **State.** Host memory (terrain, portal pairs, beds, pearls, enemies, allies, zone heat, doom corridors) plus: map class → onset; crown belief (cell, length, round, id) → escort/dissolve; target + switch count → hysteresis.
5. **Messaging.** Host packets (self, enemy, portal, bed, doom, crown beacon, handoff) with the crown id added to the beacon and certificate. Certificate delivery (`ACT:cert` / births): **0.37** — the backward ray reaches the child in about a third of births. Newborn deaths within 10 rounds: 40.5 per 100 births (control 40.9). No certificate ablation was run against this bot (the host already sends a handoff on the same ray, so the control is not a clean "off").
6. **Momentum.** Target switches 33 per 100 dragon-turns with margin 1.0 (no margin-0 ablation run); first-pearl round median 6 (control 6).

## The 2×2 (160 paired fixtures each, control = ouroboros-v10-beacon 0.494)

| Arm | Score | Δ vs control | pairs better / worse | sign p | units r100 | longest r499 |
|---|---|---|---|---|---|---|
| control (v10) | 0.494 | — | — | — | 14 | 24 |
| P: production only (`yeji-s01p-production`) | **0.531** | **+0.037** | 19 / 13 | 0.38 | 14 (open 17) | 26 |
| D: dissolve only | 0.419 | −0.075 | 10 / 22 | 0.05 | 14 | 15 |
| PD: this bot | 0.444 | −0.050 | 15 / 23 | 0.26 | 14 | 17 |

Per map (PD − control): schooltime +0.25, default +0.19, devil +0.06, trophy +0.06, autarky −0.06, dilemma −0.06, QoS −0.06, portals −0.25, slithery −0.31, trauma −0.31.

## Falsifiers

- **H-prod: fired.** Units r100 median 14 (< 15) over the panel; wall/self deaths 3.5 per 1k turns (> 2, ≤ 5). Production helps only on open maps (17 vs 14); on compact maps the pearl intake, not the split rule, is the bottleneck.
- **H-dissolve: fired.** Longest r400 11 = base (11); longest r499 17 < base 24. The dissolve arm is the worst arm (−0.075, p = 0.05).
- **H-cert: untested** (no clean ablation; delivery measured at 0.37).

Findings: `docs/findings/2026-09-29-yeji-s01-swarm-dissolve.md`.
