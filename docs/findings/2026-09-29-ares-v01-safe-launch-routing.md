# Ares V01 safe launch routing — benchmark report

## Result

Ares V01 is an experimental C++ candidate based on anna-a02-chassis. It did
not pass the acceptance gates in [BENCHMARKS.md](../analysis/BENCHMARKS.md):
the mean of the four map-normalised pearl checkpoints improved by **0.0303**
field medians against the required **0.05**, and ally-body deaths increased
**44.3%** against the 10% Tier 2 limit. Its units and total length at r100 rose,
and its fixed-panel score matched Anna's. No V02 or follow-up tuning run was
made after this V01 screen.

## Run definition

- Runner: unswbc 1.2.1, native games, simulation seed 1.
- Fixed roster: fenrir-v18-arrival-ready-beds, yuna-v05-core,
  chaewon-y04-probe, sinbad-v07-divecap,
  gavroche-v32-supported-divecap, ouroboros-m01-vibing-mimic,
  kazuha-s01-swarm-dissolve, and hunter-v20-portal-scouts.
- Coverage: 8 opponents × 10 LIVE_MAPS × both seats = 160 Ares games and 160
  Anna control games on identical fixtures; 20 additional Ares–Anna games.
- Artifacts: 340 final replays; 340 extracted games and 680 side feature rows;
  no extraction errors. All 340 index rows record rc=0 and toolkit unswbc 1.2.1.
  Eight recovered rows lack an index winner label; their outcomes come from the
  extracted replay features. Local outputs are under ignored build/zoo/ares-v01/.
- Feature scoring: derive from tools/analysis/features/benchmarks.py with the
  checked-in map_reference_medians.json, field_references.json, and
  field_distributions.json. The raw field corpus was absent, so these fixed
  references were applied as published rather than regenerated.
- Source fingerprint over runtime C++/header files and bot.toml:
  6af8a6f47bd05da28b9d5b7ce2ca28a8d0acbcb10850c9138110a4ac27d24a62.

The bot uses simulation seed 1 for these games; this is a single-seed screen. No atlas-off generalisation panel was run, so these results cover the known live maps only.
The local report follows the benchmark's median-per-side-game convention. Each
value below is the median across 160 panel side-games; map-normalised values
use the fixed field median for the same map.

## Tier 1: economy and retention

| Metric | Ares V01 | Anna A02 | Difference |
| --- | ---: | ---: | ---: |
| Mean of four pearl checkpoints | 0.4705 | 0.4402 | +0.0303 |
| Pearls at r50, field-normalised | 0.5000 | 0.4674 | +0.0326 |
| Pearls at r100, field-normalised | 0.5078 | 0.4772 | +0.0306 |
| Pearls at r150, field-normalised | 0.4751 | 0.4280 | +0.0471 |
| Pearls at r250, field-normalised | 0.3991 | 0.3883 | +0.0107 |
| Dragons at r100, field-normalised | 0.7500 | 0.7295 | +0.0205 |
| Total length at r100, field-normalised | 0.7746 | 0.7040 | +0.0706 |
| Births by r100, field-normalised | 0.5316 | 0.5266 | +0.0050 |

The economy gain misses the +0.05 requirement. Dragons and total length at r100
do not regress.

## Tier 2: hygiene and guardrails

| Metric (per 1,000 dragon-turns) | Ares V01 | Anna A02 | Difference |
| --- | ---: | ---: | ---: |
| Wall deaths | 3.9976 | 3.6447 | +9.7% |
| Own-body deaths | 0.0000 | 0.0000 | unchanged |
| Ally-body deaths | 1.3008 | 0.9016 | +44.3% |
| Ally head-on deaths | 1.1640 | 1.4344 | −18.9% |
| No-valid-action deaths | 0.0000 | 0.0000 | unchanged |

Newborn deaths within ten rounds improved from 29.41 to 22.22 per 100 births.
The ally-body increase exceeds the allowed 10%; wall deaths rose by 9.7%, just
under the limit.

## Panel score and other signals

Both bots recorded 21 wins, 138 losses, and 1 draw (21.5/160 expected-score
points). In the 160 matched fixtures, Ares had 7 wins where Anna lost; Anna
also had 7 wins where Ares lost; both won 14, both lost 131, and one fixture
drew. The direct Ares–Anna games were 14–6 for Ares: 9–1 when Ares was Team A
and 5–5 when Ares was Team B. This direct sample is too small and seat-skewed to
supersede the fixed-panel score.

Tier 3 proxies were mixed: the median pearl share at r150 rose from 0.2665 to
0.2866 and territory at r100 from 0.4034 to 0.4317, while bed capture fell
from 0.2097 to 0.2016 and length share at r250 from 0.1629 to 0.1259.

The official benchmark workflow calls for a seed-2 rerun when a result fails
the threshold. This report closes the requested V01 iteration; it should be
read as preliminary single-seed evidence, with no admission or promotion
inferred from it.

## Direct matchup: Tyr V12

A separate native screen played Ares V01 against tyr-v12-devil-scout-tiebreak
on the same ten live maps, one game from each seat per map. With unswbc 1.2.2
and simulation seed 1, Tyr won **20–0**, taking both seats on every map:
Autarky, Default, Devil, Portals, Prisoners Dilemma, Queen Of Spades,
Schooltime, Slithery Fight, Trauma, and Trophy. Each game returned rc=0; there
were no draws. Tyr won 10 games as Team A and 10 as Team B. The 20 replay files
and index are in the ignored build/ares-v01-vs-tyr-v12-20260929/ directory.

This is a one-game-per-seat/map direct matchup, separate from the fixed zoo
panel and its unswbc 1.2.1 Anna control. It gives a clear result for this pair;
it does not replace the fixed-panel gate or establish an all-map ranking.
