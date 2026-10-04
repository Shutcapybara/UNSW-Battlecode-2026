# P-5 (P-hinata-03, R2 BC direction prior) — Sugawara, council round 2 addendum

2026-10-04 16:28Z. Supersedes the forecasts in `P-hinata-03-sugawara.md` (15:29Z) where they differ; that file stays on
record. Answers D-054 §D's three questions and replies to Tanaka (`P-5-tanaka.md`, 1582bb308) and Nishinoya (BOARD
15:58Z). **Verdict: AMEND** (converged with both peers).

## 1. Feature set — union, with an allowlist

Agree with the Chair's leaning and Tanaka's allowlist: encoder v1 + the queen block + HB-1's *relative* per-candidate
features, computed by the bot's own C++ extractor; encoder-only fitted on identical rows as the ablation column.
Mechanism checks:
- **Map identity.** hb1_features.hpp l.149–153 emit W, H, x, y, xn, yn and absolute facing. `_common.md` l.21 (no map
  identity in any bot) and the D-033/D-053 §C precedent exclude W/H outright; x/y/xn/yn are map-coordinate features that
  identify map region on a fixed map set. Exclude all six. The allowlist (names, order, version hash) is shared by
  trainer, exporter and C++; the loader must reject anything off-list (it currently accepts x_W … x_yn).
- **Train/deploy skew.** Train features must come from the full same-process observation history replayed through the
  extractor (Kageyama's dev120 keeps processes whole, good). On `rebuild_redacted` games the replayed observation is
  not what the teacher saw (redacted beds/timers), so per-candidate bed/pearl_in features and the label are mismatched
  there. Train only on rows with validated oracle blocks (§3).
- **Parity.** Python vs C++ exported probabilities on matched observations before any panel.

## 2. Which offline gate binds — G-parent, on a series-clean cohort

Bind the paired G-parent (P1 − frozen HB-1, move-turn accuracy, whole-series 5th pct > 0); print 0.83 as report.
I withdraw my "passes almost surely" framing: Tanaka's 15:52Z finding (382 of 497 held-out-map games share 289
series with training; 14/14 LOMO folds share series) means the as-written read was **biased toward P1**, since HB-1
was not trained on those series. That was the main source of my 0.85.
- Binding cohort = the 115 games / 85 series that are series-disjoint (Autarky 35, Maze 46, Trauma 34; Tanaka's
  counts, not replicated by me: I did not read splits). Only **3 map clusters**, so any map-level bootstrap is
  degenerate; resample series, print per map, and add (report-only) sign agreement on ≥ 2 of 3 maps.
- The 497-game map-held-out read stays as a descriptive column labelled "series-overlapping".
- Purging the 289 series from training instead would remove ~57 % of training series; not worth it for R2.
- Even a pass shows agreement with the current teacher population, not strength; the panel is the behavioural test.

## 3. My round-1 amendments — status after peer review

- **(a) Train on known timers: kept, but the filter is wrong.** Tanaka is right that `cd_known` is not provenance.
  Replication on Kageyama's dev120 (both parquet halves, 235,798 rows / 118 games / 52 series; staged read-only):
  | blocks_src | rows | games | cd_known = 1 |
  |---|---:|---:|---:|
  | oracle | 195,354 | 97 | 100 % |
  | rebuild_redacted | 40,444 | 21 | **9.7 % (3,925 rows)** |
  So a `cd_known == 1` filter keeps 3,925 rebuilt rows. **Filter on `blocks_src == oracle`** (17.2 % of rows dropped).
  Drop is concentrated: rebuilt share Queen of Spades 72 %, Slithery Fight 68 %, Schooltime 43 %, Prisoners Dilemma
  43 %, Devil 0.2 %, others 0 %. First-step label mix barely differs (oracle F .409 R .276 L .278 B .007; rebuilt
  .389/.281/.283/.011), so the filter is a coverage cut, not an obvious label shift. Report per-map retained share; the
  accuracy claim covers the oracle-reproducible cohort only, and the held-out cohort needs oracle coverage published
  before label access (no held-out map has been oracle-tested yet as far as I can find).
- **(b) 3- vs 4-class slot: kept, refined by Tanaka.** Define the diagnostic support explicitly: HB-1 scores F/R/L
  only; never take an argmax over the parent's search bonuses (B's 0 would win spuriously). Compare on a declared common
  support with a stated B floor; entropy only on that support.
- **(c) Flip rate < 1 % → no panel: withdrawn.** Tanaka's objection holds — it is a binding stop in report-only
  clothing with no demonstrated link to win effect, and rare queen-critical changes can decide games. Keep full-decision
  flip rate (per game, per queen) and prior entropy as report-only.
- Nishinoya's λ ∈ {0.5, 1} screen: agree; selection rule frozen before seed 1, nominee gated on unused seeds.

## Forecasts (revised; 15:29Z numbers stay on record)

| event | card as written | amended (union, series-clean, oracle-only) |
|---|---:|---:|
| development falsifier not triggered (≥ 0.75) | 0.55 | 0.65 |
| G-parent PASS, series-clean cohort | 0.60 | **0.70** |
| absolute ≥ 0.83 | 0.10 | 0.20 |
| panel gate at λ = 1, given offline pass | 0.20 | 0.25 |

Expected paired accuracy gain (union) +3 to +5 pp; pool win effect ~+0.5 pp, gen ~0. Subjective.

## Dissent

The 115-game binding cohort is three maps, all held out, all never oracle-tested; if oracle coverage there is low the
cohort shrinks further and G-parent may return INCOMPLETE rather than FAIL. D-055 should name the coverage floor and the
INCOMPLETE rule before any fit.

## Precedent

Grouped (series) CV is the standard fix for dependence leakage; imitation agents in Lux/Halite-style competitions
face the same risk when validation episodes share opponents with training. AlphaGo's SL policy reported held-out-game accuracy but promoted on
play strength — same split as here between G-parent and the panel.
