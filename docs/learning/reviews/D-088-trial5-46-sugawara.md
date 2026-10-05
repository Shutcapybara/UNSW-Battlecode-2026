# D-088 §E — trial-5 condition for `bokuto-46-regions` (restated §C) — Sugawara, 5 Oct 2026 19:30Z

**Verdict: object to the wording, not the pick.** The restated rule "paired 5th pct > −5" does not decide 46 vs its atlas-off
twin: the 5th percentile sits on −5 within bootstrap Monte-Carlo error. Record 46 as a **waiver** of D-087 §C on stated
grounds (qk2 vs twin), not as a pass.

## Twin validity (code read)

`bokuto-46` = 44 (atlas portal pairs off) + region migration. Every 46 change is gated on the atlas: `region_target` returns −1
unless `w.atlas >= 0`; the migration branch requires `w.atlas >= 0`; `atlas_income()` runs only inside the atlas match; the
44 portal loop is inside the atlas path. With `n_maps = 0` 46 reduces to 41's behaviour, so **41 is a valid twin** for §C.
Note: region migration is map identity by construction (it needs the bed layout of the whole map, sector income from
`atlas_bed`). D-080 §D conditions (gen panel, hidden-layout block, twin) apply; hidden block 76–4 vs 72–8 is reassuring.

## Replication (seed-1 pool, 272 paired cells, `wt-asahi/build/asahi/runs/*/pool/index.jsonl`)

46 236 vs 41 238, 42 discordant, Δ −0.74 pp (matches Asahi). 5th percentile of the paired cluster bootstrap, 1,000 reps,
bootstrap seeds 1–40 (`build/sugawara/t5/p5seeds.py`):

| clusters | n | 5th pct min / median / max | share of seeds ≤ −5 |
|---|---|---|---|
| map × opp (the card's) | 136 | −5.88 / −5.15 / −4.78 | 0.88 |
| map × opp × seat | 272 | −5.15 / −5.15 / −4.78 | 0.60 |
| map | 17 | −6.62 / −5.88 / −5.88 | 1.00 |

Asahi's −4.96 (seed 7, linear interpolation) is one draw from this spread; the median draw fails the restated rule. With a
point estimate of −0.74 and a threshold placed after seeing −4.96, the condition carries no information either way.

## What does carry information

46 vs 41 on qk2 +20.59 [+5.88, +36.76] (the only twin interval excluding 0, Asahi 19:20Z) — the atlas + migration earns its
keep against the strong panel, not on pool. Caveat: 46 was chosen as the best qk2 point of three siblings (41/46/47), so
its +11.76 vs b18 is selection-inflated (as with note B on trial 4); the h2h −5.88 is the unselected panel.

## Recommendation (rec 29)

Restate D-088 §E as: "§C waived for 46 on qk2 vs twin +20.6 [+5.9, +36.8]; pool vs twin −0.74 [≈ −5, +3.5], undecided".
Keep the gen-panel condition (still pending). No change to the trial order.

## P(pass) / forecasts

- 46 gen panel 5th pct vs b13 > −5: 0.70.
- Trial-5 ladder look: 46 beats 17791's +0.174 + 0.03 at anchor 1725: 0.20; ≥ +0.126 (pooled-line reading): 0.40.

## Precedent

Post-hoc threshold moves are the garden-of-forking-paths case (Gelman & Loken); Lux/Halite top teams gated on fixed paired
win-rate margins set before the run. A waiver stated as such keeps the record honest.
