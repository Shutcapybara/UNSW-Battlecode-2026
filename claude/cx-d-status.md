# C1-D status — portal discipline (GLM 5.3, 29 Sep 2026)

**§1 (measurement) delivered; §2–4 blocked on the C1-A chassis** (no `bots/cx-*` yet as of this writing).
Findings: `docs/findings/2026-09-30-cx-d01-portals.md` (tables first). Tool: `tools/replay_stats/portal_deaths.py`
→ `build/c1d/portal_deaths.json`.

## §1 in five numbers

- Team 7 dies at **28.2 deaths per 100 portal steps** (ranked; 11/game median) vs team 306's **12.5** — transit
  volume is field-normal (49 vs 47–56 steps/game), safety is not.
- **Portals map**: we transit **399 steps/game (5.5× team 306's 72)** and log **154 near-portal deaths/game,
  36/100 steps, 332 same-pair double-use deaths in 5 games**.
- **Wall+self near-portal deaths: 623 in 35 games (team 306: 2)** — exit memory + exit-cell simulation targets.
- **Same-pair friendly double-use: 548 deaths in 35 games (15.7/game) vs 306's 4.3** — the parity rule's target;
  consistent with the 1,005 friendly head-on initiations finding.
- Near-portal deaths climb all game (peak r200–249) — not an opening-only problem.

Method notes: exact per-step portal detection (simulates every move command through the replay's own edge map;
4.74 M walks, 0 mismatches vs observed heads; the vendored `analyse()` undercounts 5–15 % by its guards — recorded
in the findings). Populations: team 7 ranked (35) + unranked dev (159, vs 62/45/752/241/75) + 306/70/801 ranked
(34/70/19) + in-game opponents. `LIVE/state` is not mounted on this machine; corpus games stand in (version
mixing post-D-023 caveated). Devil has no portals — zero steps for everyone (consistency check).

## Next (on chassis landing)

1. `bots/cx-d01-portals` on the C1-A chassis API: the four rules in `params.hpp`-switchable form (exit memory
   N-rounds; probe-ray-before-transit using sonar echo kinds; parity no-double-transit, ablated vs sonar-payload
   pair reservation; exit-cell simulation in id move order). Keep gatherers' willingness to transit.
2. Fixtures per the C1 index (ten maps × both sides × seeds 1–3 vs the fixed panel); primary outcome via this
   script: portal-step deaths per game and per transit on Portals, Default, Schooltime, Slithery; secondary units
   r100 and pearls by r100.
3. Falsifiers: all-rules-on cuts portal-step deaths < 25 % → fail; pearls by r100 drop > 10 % on portal-heavy
   maps → fail. `CANDIDATE.toml` for the passing set; findings updated; director registers.
