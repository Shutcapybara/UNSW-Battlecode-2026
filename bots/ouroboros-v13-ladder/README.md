# ouroboros-v13-ladder — compact maps play the production ladder

- **Line:** Ouroboros (Claude). **Base:** `ouroboros-v12-core` (= v10, modular).
- **Borrowed:** the decision ladder of `hunter-v20-portal-scouts` (user line),
  ported to Python in `ladder.py`; hunter-v15's pearl-hotspot sharing idea (K_HOT packet).
- **Hypothesis (P3):** v10 loses compact maps because its evaluator gathers
  ~30% fewer pearls per dragon-turn than hunter (0.12 vs 0.17, rounds 0–40),
  and that compounds. Playing hunter's ladder on compact maps, with our
  safety vetoes and our crown/feeding endgame, closes the gap without
  touching open maps.
- **Change:** one doctrine line, compact maps only (≤ 625 tiles):
  `{"ladder": 1, "ladder_safety": 2, "ladder_risk_max": 1.0, "hot_slots": 1}`.
  Open maps are v10 exactly (action-stream equivalent, 16/16).
- **Verdict: promote as the Ouroboros candidate for cycle 1.**

## What the ladder does (non-crown, non-feeding dragons, compact maps)

1. **attack:** with ≥ 3 units, sprint into a visible enemy head *longer* than us within len−1 free steps (trade up)
2. **split** whenever length ≥ 4 (child 2)
3. **food:** nearest visible pearl we own (route distance to friendly heads, ties by id)
4. **explore:** friend spacing ×60, view frontier ×80, pearl hotspots (own + heard) ×35, unscouted 4×4 sectors ×25

Our vetoes (fall back to the v10 evaluator for that turn): certain death by
exact simulation; a pocket smaller than len + 4 (flood); `head_risk` > 1.0.
Ladder dragons spend one ray per turn on a K_HOT hotspot (hunter's rotation over the 8 strongest).
Crowns (from round 200) and feeders (from 400) use the evaluator as in v10.

## Results (native, both sides; opponents = cycle-0 gauntlet minus v10)

| Set | v10-beacon | **v13-ladder** |
|---|---|---|
| Compact G+V (`gvc`: 5 maps + _T/_FX, 120 games) | 65–1–54 | **99–1–20** |
| Compact hold-out (`hoc`: _TFX/_FY, never tuned on, 80 games) | 43–1–36 | **61–1–18** |
| Open G+V (`gvo`, 120 games) | 115–0–5 | 115–0–5 (identical actions) |
| **G+V total (240)** | 180–1–59 | **214–1–25** |

Per opponent, G+V (compact + open):

| Opponent | v10 | v13 |
|---|---|---|
| hunter-v20-portal-scouts | 33–27 | **47–13** |
| hunter-v14-cpp-hybrid-route-spacing | 43–17 | **53–7** |
| fry-v14-stateful-size-aware-3 | 47–13 | **58–2** |
| kraken-v04-eval | 57–1–2 | 56–1–3 |

Compact by opponent (gvc): hunter-v20 3–27 → **17–13**, hunter-v14 15–15 → **25–5**,
fry-v14 18–12 → **29–1**, kraken-v04 29–1–0 → 28–1–1.
Side split, compact: v10 A 31–29 / B 34–1–25; v13 A 46–14 / B 53–1–6.

Cross-line, G+V (compact `gvc` + open `gvo`, both sides; v10 in brackets where run):

| Opponent | compact | open | total |
|---|---|---|---|
| leviathan-v09-arrival | 23–7 (v10 18–12) | **13–17** (= v10) | 36–24 |
| kraken-v05-safety | 28–1–1 (v10 27–1–2) | 26–4 | 54–1–5 |
| hydra-v11-macro | 30–0 (v10 30–0) | 30–0 | 60–0 |

Open maps are now the weak side against leviathan-v09 (v10's evaluator and crown
plus Leviathan's pearl model): 15 of 17 losses are round-500 length races with our
longest behind (e.g. 15 vs 32, 36 vs 43).

Economy against hunter-v20 (`econ.py`, rounds 20–40, per dragon-turn): pearls
eaten 0.13 → 0.19 (hunter 0.18); units at round 40 in losses 6.4 → parity.
The compact war is now a mirror match decided by trades, not by the pearl race.

## Screens that led here (compact `gvc`, vs hunter-v20, hunter-v14, fry-v14 [+kraken])

| Variant | Result | Note |
|---|---|---|
| v10 baseline (3 opp) | 36–54 | |
| evaluator knobs: spawn window 4 / goal ×2.5 / crowd off / spread ×4 / risk ↓ / split gates off / pearl bonus 2, 4 | 27–40 of 90 | all within noise or worse (σ ≈ 4.6) |
| orphans → gatherers (`orphan_role=1`) | 25–65 | the accidental hunters are load-bearing |
| **ladder** (4 opp, 120) | **90–3–27** | the structural change |
| ladder, no attack | 83–3–34 | attack worth ~7 |
| + pocket veto (`ladder_safety=2`) | 93–3–24 | |
| + risk veto 1.0 / 2.0 / 0.5 | 99 / 97 / 97 | hold-out: 60–2–18 vs 62–2–16 without it (noise) |
| + hotspots (`hot_slots=1` / 2) | 96 / ≈90 | |
| all four (= v13) | 100–3–17 | final, CPU-optimised build: 99–1–20 |

## CPU (sandbox, judge interpreter)

| Map | v10 p50 / p99 / max | v13 p50 / p99 / max |
|---|---|---|
| arena vs hunter-v20 | 20.2 / 34.6 / 35.7M | 22.4 / 38.5 / 42.3M |
| trophy vs hunter-v14 | 25.1 / 35.8 / 46.1M | 29.2 / 48.9 / 67.5M |
| devil vs hunter-v20 | – | 23.2 / 37.7 / 54.3M |
| big_empty vs hunter-v14 (open path) | 29 / 48 / 69M (cycle 0) | 28.8 / 46.1 / 60.6M |

Gate (p99 < 60M, max < 80M) passes. The first ladder build ran p99 84M /
max 99.9M on trophy; three exact or near-exact rewrites fixed it (adjacency
table for the view, one multi-source BFS for friend routes instead of two per
friend, a 7×7 distance transform for the hotspot / sector fields instead of a
whole-map BFS). Open maps run v10's code path.

## Judge packaging note (applies to every multi-file Python bot)

The judge compiles every `*.py` to a legacy `*.pyc` beside it and **deletes the
sources**. `main.py` therefore loads each module from `name.py` when present
(local runs) and otherwise unmarshals `name.pyc` (skipping the 16-byte header).
The first v12/v13 build crashed on turn 0 in `unswbc run --sandbox` for this reason.
