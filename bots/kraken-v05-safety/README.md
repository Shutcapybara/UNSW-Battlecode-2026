# kraken-v05-safety

- **Line:** Kraken (Kimi, exploration track)
- **Base:** kraken-v04-eval (identical to v03-judge-safe in behaviour)
- **Hypothesis (macro spec S5):** a probabilistic strike model with
  initiative and trade pricing, plus doom memory, exit counting and
  traffic terms, cuts kraken's measured leak (~100 body-crash and ~29
  wall deaths per game) at equal unit volume — and thereby converts
  more games.
- **Cycle 1, 2026-09-25.**

## Changes vs v04 (all weights in CFG, neutral-off via ablation)

1. **Threat cost field** replaces binary lethal/soft levels. An enemy
   head at BFS distance k prices `p_strike[k] x (w_danger_base +
   w_danger_seg x my_len)`, scaled by:
   - *initiative*: enemies acting after me this round (higher id) can
     react to my move (`ini_notmoved=1.0` vs `ini_moved=0.85`);
   - *trade value*: `clamp(my_len / their_len, 0.35, 1.6)` — a shorter
     enemy wants the mutual kill more.
   Cells at or above `hard_frac` of my value count as lethal for
   flood-fill, BFS compass and escape sprints. Splittable enemies keep a
   newborn-strike term (`p_newborn`) around the tail.
2. **Doom memory:** an ally seen inside our inner 5x5 last round that is
   gone now died there; the death cell (`w_doom=500`) and its approaches
   (`w_doom_adj=120`) stay marked for `doom_ttl=200` rounds.
3. **Exit counting:** destinations leaving 0/1 survivable continuations
   pay `w_exit0=-260 / w_exit1=-70` (2-step, grow-aware, pearl slack).
4. **Traffic terms:** `w_ally_adj=-12` per adjacent ally part,
   `w_crowd=-6` per blocked neighbour.
5. Brawl mode discounts the whole threat field by
   `brawl_threat_scale=0.2` (was a flat -150).

## Results (native, deterministic, both sides; build/kraken-v05-*)

**Screen** (4 maps: arena, default_small, trophy, queen_of_spades):

| Matchup | v05 | v04 control (same set) |
|---|---|---|
| vs fry-v14 | 2–6 | 2–6 |
| vs hunter-v14 | 2–6 | 2–6 |
| vs kraken-v04 | **6–2** | — |

Median loss round 180 (v04 control: 132) — v05 survives longer.

**Gauntlet** (11 maps x 2 sides, 110 games; build/kraken-v05-gauntlet):

| Opponent | v05 | v04 reference (ACTIVE.md cycle 0) | net flip |
|---|---|---|---|
| ouroboros-v10-beacon | 3–18–1 | 0–21–1 | **+6** |
| hunter-v14 | 7–15 | 8–14 (GLM fixture) | -2 |
| hunter-v20 | 8–13–1 | 12–9–1 | **-8** |
| fry-v14 | 10–12 | 10–12 (GLM fixture) | 0 |
| kraken-v04 (mirror, self-contained) | **14–8** | — | +6 |
| **Total vs field** | **38–58–2** | ~30–56–2 | +8 |

Side split: A 21–32–2, B 21–34–0.
Map class (mirror included): compact 9–39–2, open 33–27–0.
vs field only: **compact 1–37–2, open 27–21–0** — the compact wall is
production (S3), untouched by this variant. Wins vs fry/hunters are
almost all round-500 length races (23 of 25), the kraken identity.

## Ablations (vs hunter-v20, 11 maps x 2, the regressed matchup)

v04's 12–9–1 record against hunter-v20 was kraken's unique gauntlet
strength; v05 lost it. Single-component ablations (kbench variants):

| Variant | Ablated | vs hunter-v20 |
|---|---|---|
| kraken-x01-notrade | trade scaling | 10–11–1 |
| kraken-x02-noini | initiative pricing | 10–11–1 |
| kraken-x03-noexit | exit counting | 10–11–1 |
| kraken-x04-nodoom | doom memory | 10–11–1 |
| kraken-x05-pstrong | p_strike -> 1.1/0.55/0.2 (near-binary) | 10–11–1 |

No single component, nor near-binary contact pricing, explains the drop:
every perturbation lands on the same ~10 open-map wins (default,
queen_of_spades, schooltime, stronghold, trauma, both sides) with
big_empty as the swing map (only x04-nodoom took big_empty B). The cost
is distributed across the move from a hard wall (-700 flat) to
expected-value pricing as a whole — v04's hunter edge came from extreme
risk aversion carrying length to round 500, not from any one knob.

## Sandbox CPU (judge meter, vs hunter-v14)

| Map | p50 | p99 | max | v04 p99 (same set) |
|---|---|---|---|---|
| big_empty | 40–43M | 61.5–61.7M | 66.4–67.9M | 60.8–61.0M |
| trauma | 31M | 32.7M | 35.9M | — |

No CPU regression from S5 (Δp99 ≈ +0.6M). Both v04 and v05 sit
marginally over the 60M p99 gate on big_empty at ~64 units — a
pre-existing line issue, not introduced here.

## Verdict: **null result — not promoted**

- Fails the promotion rule: hunter-v20 drops 8 net (12–9–1 to 8–13–1),
  beyond the -3 tolerance, despite +6 vs ouroboros-v10 (first kraken
  wins ever against v10) and +6 in the mirror.
- **kraken-v04-eval remains the line tip and gauntlet bot** (it keeps
  the only winning record against hunter-v20).
- Knowledge returned to §4.3 (threat model row): probabilistic pricing
  beats the binary wall in the mirror (+6) and against ouroboros (+6),
  initiative/trade/exit/doom each contribute roughly +1 net against
  hunter-v20 when removed, and expected-value safety pricing by itself
  does not win compact maps (1–37–2 there) — the compact fix must come
  from production (S3, kraken-v06), not from threat pricing.
- big_empty vs hunter-v20 is the identified swing map for any v06
  candidate: doom memory behaviour there needs a replay look before
  keeping it on big maps.
