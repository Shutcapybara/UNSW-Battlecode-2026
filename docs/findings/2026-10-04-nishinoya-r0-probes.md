# Nishinoya R0 probes — council seat bring-up (4 Oct 2026)

**Status: unaudited** (GLM probe seat; every number below is a full-store census, not a sample, so
no intervals are given — an auditor seat should replicate the counts before the Chair relies on them).
Lane `r/nishinoya`, worktree `../wt-nishinoya`. Read-only queries against `build/s1/corpus/` in the
main checkout at 10:30–10:44Z, 4 Oct 2026. No bot runs, no uploads.

Purpose: three cheap counter-checks behind the Chair's first decisions (D-045/D-046: frozen splits,
R0 decode finish, learned-arm gating), run before any card exists to review.

## A — post-m2 decode backlog (Data's R0 blocker)

Population: all 121,983 rows of `games.parquet`; in-scope = store's `in_scope`; post-m2 = `map_era`.
Decoded = has a part in `deaths/` (cross-checked against `series/` and `sides/` — all three give the
same game set; `transits/` covers a subset, 5,915 post-m2, older format).

- In-scope post-m2 games in store: **14,674** (was 13,439 at Chongqing C5-01, 05:55Z: +1,235 in ~4.5 h
  of collector growth).
- Decoded post-m2: **7,057** (Chongqing's 05:55Z "7,030" and 08:20Z "≈7,200" bracket this; the exact
  census is 7,057).
- **Decode queue: 7,617 and growing** — decode idle since 05:18Z (newest part 15:48 local = 05:18Z,
  no decode process at 10:44Z) while the store adds games faster than the idle decode drains them.
- Total store with parts: 51,395 games.

Consequence for Data's R0: the one-off native decode needs re-running; at Chongqing's rate estimate
(~1 h for 6,300 at `--jobs 6`) the queue is now ~20 % larger.

## B — held-out split feasibility (Chair freezes ≥3 maps spanning classes A–E)

Population: the 14,674 in-scope post-m2 games, per map, with ranked split, top-ten involvement
(`rank_a≤10 or rank_b≤10` on the store's snapshot ranks) and our own games (team id 7, string).

Classes per Chongqing C7-03 (QoS = "Queen Of Spades" in the store's map names):

| cls | map | in-scope | ranked | top10-ranked | ours |
|---|---|---|---|---|---|
| A | Queen Of Spades | 884 | 587 | 128 | 12 |
| A | Autarky | 874 | 559 | 140 | 18 |
| A | Default | 888 | 562 | 135 | 20 |
| A | Devil | 752 | 530 | 128 | 11 |
| A | Stripes | 666 | 487 | 109 | 10 |
| A | Tower Defense | 706 | 508 | 120 | 14 |
| A | Trophy | 866 | 565 | 135 | 18 |
| B | Around UNSW | 875 | 559 | 128 | 19 |
| B | Australia | 915 | 553 | 119 | 20 |
| B | Islands | 900 | 575 | 125 | 18 |
| B | Maze | 819 | 563 | 147 | 23 |
| B | Schooltime | 1,045 | 583 | 141 | 23 |
| C | Prisoners Dilemma | 728 | 511 | 129 | 15 |
| C | Trauma | 955 | 602 | 141 | 21 |
| C | weakhold | 712 | 556 | 142 | 17 |
| D | Slithery Fight | 1,050 | 615 | 160 | 18 |
| E | Portals | 1,039 | 595 | 138 | 19 |

- Every live map carries 666–1,050 in-scope games and 487–615 ranked, so any ≥3-map held-out choice
  leaves ≥ ~600 in-scope training games per remaining map; no map is too thin to hold out or to train on.
- Each held-out map removes only 10–23 of our own games (296 total in-scope post-m2, 110 ranked;
  latest our-game 06:35Z — collection is live).
- Note for the record: C7-03's "PD/PD10" appears as one map ("Prisoners Dilemma") in the post-m2
  store; class A has 7 maps, B 5, C 3, D 1, E 1 = 17, matching `LIVE_MAPS_M2`.

## C — learned-arm gate tooling: version contradiction (blocks every learned125 gate run)

- `tools/carthage/lane.py` implements `--gate learned125` (opt-in; default `d032` unchanged) and at
  line 475 **hard-codes `runtime_version == '1.2.5'`** when verifying run records; anything else
  reads as unverified → INCOMPLETE.
- The main `.venv` has **`unswbc==1.2.3`** installed (D-042's outstanding "hub venv → 1.2.3" is what
  shipped; nothing newer is installed here).
- But the Phase 3 Learner prompt pins **`unswbc==1.2.9`** (maps; engine stated identical to 1.2.3),
  and D-045/Antioch's gate doc scopes the rule to **`unswbc==1.2.5`**.
- So three versions are in play and the installed one matches neither newer pin. Under the current
  venv every `--gate learned125` run fails its run-record check; after any repin, either `lane.py`'s
  literal or D-045's text is stale. This needs one Chair ruling (which version is canonical for R0+
  panels, and the matching `lane.py` edit) before the Evaluator gates anything.
- Consistency checks that passed: `maps/live/` = 22 templates (D-043); `LIVE_MAPS_M2` = 17 maps;
  `tools/hb1/cpp/` parity path present (blob/compact parity, check_parity) — the R2 export route exists.

## RL translation

These are infrastructure findings, not arm mechanisms; the D-044 four-part translation applies only
loosely: (B) fixes the observation/teacher data volumes the encoder and BC heads will see per map
(after any held-out freeze), and (C) is a prerequisite for any R2+ deploy gate to be runnable at all.
No behaviour claim is made.

## Provenance

- `build/s1/corpus/games.parquet` @ 10:30Z; `deaths|series|sides|transits/part-*.parquet` census @ 10:44Z.
- Scripts: inline pyarrow queries (venv `.venv`, pyarrow 21); no writes to the store.
