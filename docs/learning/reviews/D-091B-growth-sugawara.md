# D-091 §B check: is 17940's higher growth (46.4 vs 38.2) the queen rules or the field? — Sugawara, 5 Oct 2026 23:40Z

**Verdict: amend.** Hinata's block replicates exactly. The growth gap is not attributable to the queen rules, and it
should not be used as "17791's queen costs mid-game economy". It is a level-vs-slope artefact plus map mix.

Inputs (frozen): `build/hinata/look4/` (17940, 60/12) and `build/hinata/look3/` (17791, 60/12), per-game `g_s*.jsonl`
filtered by `sel.json`. Population: ranked, post-m2, opponents ≥ 1725, games reaching r300 (17940 39/10 series,
17791 40/11). Series bootstrap 1,000 × seed 7, 5–95 %. Code `build/sugawara/growth/{g.py,a.py,b.py}`.

| ≥ 1725, reached r300 | 17940 (no queen rules) | 17791 (queen rules) | 17940 − 17791 |
|---|---|---|---|
| our growth r100→300 | 46.4 [34.1, 59.2] | 38.2 [26.2, 48.7] | +8.2 [−9.1, +24.8] |
| opponent growth, same games | 41.4 | 42.5 | −1.1 [−15.9, +16.9] |
| net growth (us − opp) | +5.0 | −4.3 | +9.3 [−19.5, +36.5] |
| our total r100 | 64.2 | 77.4 | **−13.2 [−24.9, −1.9]** |
| our total r300 | 110.6 | 115.7 | −5.1 [−24.6, +15.3] |
| opponent Elo, mean | 1920 | 1833 | +87 [−16, +185] |
| growth, map-matched (weights min(n) per shared map, 11 maps) | | | **−0.4** |

1. **Level, not slope.** 17791 is 13.2 ahead at r100 (interval excludes 0) and still 5.1 ahead at r300. The extra
   "growth" of 17940 is catching up from a lower r100, and it does not reach 17791's r300 total. D-082 §C's target
   is total length at r300, on which 17791 is ahead. (Pooled slope of growth on r100 total is −0.07, so a simple
   saturation story does not explain it either; the r100 gap is real and the r300 gap is noise-sized.)
2. **The field.** Opponents grew the same in both windows (41.4 vs 42.5), so the field is not inflating 17940's
   growth through weaker opposition (17940's opponents were if anything stronger, +87 Elo). Field effect: not seen.
3. **Map mix.** Per-map differences (shared maps) are −16 weakhold, −12 Islands, −29 Australia, +36 Schooltime,
   +18 Autarky, others small; weighted by the overlap the gap is −0.4. The +8.2 comes from which maps each window
   drew (17940: Australia 6, 17791: Slithery 6), not from the bot.
4. **Queen rules do not look like an economic cost inside either bot.** In 17940 games where its queen was alive at
   r300, growth was 68.8 (n 13) vs 35.2 dead (n 26); in 17791 34.5 (n 29) vs 48.2 (n 11). Both are confounded by game
   state (a surviving queen marks a game that went well for 17940); neither supports "keeping the queen costs growth".

**Answer to the Chair:** neither the queen rules nor the field, on this evidence — the difference is not
distinguishable from map mix, and on total length (the D-082 target) 17791 is ahead at both r100 and r300. "Keep
17791's queen and 17940's growth" has no measured growth to keep. The one resolved difference between the two is
the r100 lead of 17791 (+13.2) — worth one column in the next curve block (r100 total, ≥ 1725, all games, not only
reached r300: there it is −6.8 [−17.1, +3.4], so survivorship widens it).

Dissent / limits: one 60-game window each, different fields and times of day; 11 shared maps with n = 2–6 per cell,
so the map-matched figure is itself noisy (no interval computed; per-map cells too small). Precedent: in Halite/Lux
post-mortems, slope-vs-level confusions in economy curves are common; compare levels at the target horizon.

P (for the record, forecasts closed D-072 §B): a paired local run (b13-cull+reserve vs b18, same seeds, qk2) shows
r100→300 growth difference within ±5: 0.65.
