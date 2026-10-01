# Benchmark features for local optimisation

29 September 2026 · claude/analysis/F1 (with the user). Exported from the Claude Doc of the same name; data and code in `docs/analysis/benchmarks/` and `tools/analysis/features/benchmarks.py`.
Revised 30 September 2026 (s1): the two sections below are new, and marked notes correct the older sections in place.

## Start here (30 Sep revision)

The original analysis below (29 Sep, 4,563 field games) still holds for what it measured. Six things changed after the
40,593-game top-50 corpus store (`tools/s1/`, findings `docs/findings/2026-09-30-s1-*.md`) and the lane results of 29–30 Sep.

**What to run on a candidate**

| Question | Command | Decides |
|---|---|---|
| Is the opening faster? | `python3 tools/s1/tempo_gate.py <candidate run dir> <parent run dir>` | ACCEPT / NO GAIN / REJECT / INCONCLUSIVE for early-game changes (see **Tempo** below) |
| Full tables: economy, hygiene, W-L-D | `python -m tools.analysis.features.scorecard bots/<candidate> --parent bots/<parent>` | the D-032 lane gate (paired, seeds 1–3, interval) |
| Endgame tier for late mechanisms | `python tools/clair/score_extra.py <bot> --parent <parent>` | longest/total margin at end + round-limit-losses-with-lead (see the 1 Oct revision below) |
| Where does it stand against the field per map? | `python3 tools/s1/q.py` / `tools/s1/q3.py` on the s1 store | diagnosis, not acceptance |

## Start here (1 Oct revision — H-1 steward; applied under the lead's authorization to revise the gate when the evidence warrants)

Three changes to the lane gate (D-032), each fixing a measured blindness. None of them flips any 1 Oct lane
verdict except where named. Evidence and analysis: `claude/clair-status.md` standing duty 4.

1. **A phase-`end` tier for changes that act after r250** (the `--phase late` pattern extended; the economy
   checkpoints stop at r250 and *cannot* move for a later mechanism — tt-01/02 measured exactly +0.0000).
   Judged on: final `longest` and `total` length margins (`longest_margin_end`, in the feature extract since
   R-4), the round-limit-loss-with-material-lead rate (loss, non-elimination, `total_margin_end > 0`), and
   overall win, with p@50..p@250 and units/length@100 as guards. Rationale: 60 % of hb1-14's round-limit
   losses carry a material lead (clair's own panels, 21/35; tt measured 50 %), and every one is a `longest`
   loss; all four top teams convert deliberately (tt's four-team table) while the current gate cannot credit
   it. **Deliberate self-kills logged as culls are exempt from the tier-2 10 % guard in this tier** (30 Sep
   point 3 already classifies chosen deaths as non-hygiene; the `ACT:` marker pattern is the trace).
   Re-scored history: `tt-05-feed300-up` fail → **accept-shaped endgame hold** (141–19 level, longest 32 vs
   27, lead losses 8 % vs 50 %); tt-01 hold pending seeds 2–3; tt-02/03/04 stay fail (win / no concentration /
   no delivery); hb1-12/14, verso c2-feed140, esquie-03b unchanged.
2. **Accept = positive economy lower bound on at least one panel, non-harm on the other** (each panel's econ
   lb > −0.02, win lb > −0.02 on both), instead of "positive on the pool, non-harm on gen". The pool is ten
   known maps (identity-contaminated by rule, L28); the gen panel is the out-of-sample object, and the old
   form rejected the largest off-pool gain measured (verso-05: pool econ −0.017, gen econ +0.017, pool win
   lb +0.003 — kept by the lead over the letter). clair-05 (pool +0.029 lb>0, gen −0.058) shows the gen panel
   catching pool-fitted levers, so the non-harm side stays strict. Re-scored: verso-02 and verso-05
   REJECT → accept-shaped; aline-17, verso-01, maelle-04, gustave-07c/08a, esquie-03b, and every clair-01..08
   verdict unchanged.
3. **The fixture-cluster bootstrap is authoritative for ACCEPT** (fixtures within a seed×map cell share the
   layout; the plain form overstates independence — aline-17's accept rests on plain lb +0.005 vs cluster
   −0.000). Borderline rule so a corroborated accept is not chilled: accept when cluster lb > 0, or cluster
   lb > −0.005 **and** pool win lb > +0.02. Under it aline-17 stays ACCEPT. Report both forms until the end
   of the October cycle.

4. **What remains uncovered: the mid-game (r150–250).** The phase picture after this revision — opening:
tempo (net income, rounds 10–150) ✓; end: the phase-`end` tier ✓; mid-game: only the p@150/p@250 pearl
checkpoints, which count own-corpse recycling as economy (L29: 38 % of the base's pearls) and say nothing
about pressure or retention between the phases. The right instrument already exists in the tempo gate's
accounting (bed + enemy-corpse pearls, own corpses excluded, loss = unrecovered length): extend the reference
curves beyond r150 — `tempo_reference.json` carries rounds 0–150 only and is frozen. First step (desktop,
minutes against `build/s1/corpus/`, which is not committed): rebuild the reference to r300 as
`tempo_reference_r300.json` (do not overwrite the frozen file — every existing tempo number must stay
comparable), then judge mid-game changes on net-income lag at r150–250 with the phase-`end` tier as the
downstream guard. Until that reference exists, mid-game changes are judged on D-032 with the corpse-share
diagnostic (still unexecuted from D-035) reported beside it.

**Rollback (falsifier):** any bot promoted under these rules whose live screen or ladder share falls materially
below its panel prediction (D-019's probation rule is the template) — then the changed clause reverts and the
flip-set is re-scored against it. The gate serves winning, not the reverse; if local and live disagree, live
wins and this file changes again.

The two gates answer different questions: tempo is about the first 150 rounds, D-032 about the whole game. An opening
change should pass tempo and not fail D-032's guards. A late-game change is judged by D-032, with tempo as a guard: it
must not come out REJECT.

**What changed, and why**

1. **Tempo is the headline for the opening.** It is one number in rounds behind the top ten's curve, with a decision
   threshold. It predicts the result better than the pearls curve (within-map AUC 0.815 vs 0.77–0.80) and ranks teams by
   rating as well (ρ 0.65). It measures *net income* (bed and enemy-corpse pearls, minus unrecovered length), so feeding
   the swarm to itself does not raise it.
2. **The gross pearls curve is a diagnostic, not a target.**
   - It counts our own corpses eaten back as economy (L29: 38 % of the base's pearls).
   - Renoir 07c (lower exploration value) passed the old economy bar on the pool (+0.11) through churn.
   - On the same fixtures the tempo gate says **NO GAIN**: −1.2 rounds, CI [−2.4, 0.0] on the pool and +0.1 on the
     generalisation maps. Ally head-on deaths rose 42 %.
3. **Chosen deaths are not hygiene failures.**
   - The top ten die a lot by choice: 4.6 suicides and 2.1 invalid-action deaths per 1k dragon-turns in rounds 0–150,
     mostly enclosed length-2 dragons, as recycling.
   - The "0 per 1k" top-ten medians in the tables below are per-side-game medians on 28 Sep data. Pooled rates on the
     40k store are 5.3 wall and 3.8 own-body per 1k for the top ten (ours 11.9 and 6.8).
   - The invalid-action row still means "bug" for **our** bots: all 835 of our live invalid deaths are newborns at age 0.
4. **Ally head-on deaths are a portal-exit event, not a general hygiene rate.**
   - 93–99 % happen within 2 steps of a portal, about half within 3 rounds of a transit.
   - Watch them together with per-transit death within 3 rounds (top ten 0.20, us 0.28) and seen-landing deaths
     (0.21 vs 0.33).
   - Taking portals early is *not* the problem: it is +EV on all ten ladder maps (S1-Q5).
5. **Report per map, pair by seat.**
   - Map-specific skill is real (50/51 top teams have significant map effects, ~150 Elo spread).
   - Side B is favoured on 8 of 10 maps at equal Elo.
   - Pooled numbers can hide a map regression. Both gates print per-map rows and pair fixtures by seed, map, opponent and
     seat (D-036).
6. **The field references are frozen snapshots.**
   - `field_references.json` / `field_distributions.json` / `map_reference_medians.json` are the 28 Sep references;
     keep them for continuity with past scorecards.
   - `tempo_reference.json` is the 30 Sep top-ten curve set. It excludes SSS (91) and Cutlery (306), whose unranked
     games are not the bot their rating belongs to (SSS wins 36 % of unranked games at an Elo-expected 64 %).
   - Neither is ever rebuilt between a candidate and its parent.

## Tempo: the early-game benchmark

**In one sentence.** *How many rounds behind the top ten are we, averaged over rounds 10–150?*

- If we have eaten at round 60 what the top ten had eaten by round 48, we are 12 rounds behind at round 60.
- A constant lag means we are late but keeping pace. A growing lag (drift) means we are falling further behind.

**What is counted.**

- **Income:** bed pearls plus enemy-corpse pearls eaten. This is new mass. Eating our own corpses back is not income, so
  churn cannot raise the score.
- **Loss:** length lost to our deaths, minus the corpse pearls we ate back.
  - A death that feeds our own dragon costs nothing.
  - A death that feeds the enemy, or rots, costs its full length.
  - Loss beyond the top ten's at the same round is charged as income not earned; less loss is credited.
- **The curve we are measured against:** the median of eight top-ten teams on the same map
  (`benchmarks/tempo_reference.json`).
- **Maps without that curve** (maps/new, `_tr` variants) use the parent's own curve. There, tempo reads as rounds
  ahead of or behind the parent.

**One command.**

```
python3 tools/s1/tempo_gate.py build/zoo/<panel>-<candidate>-<fp8> build/zoo/<panel>-<parent>-<fp8>
python3 tools/s1/tempo_gate.py build/ra/runs/<cand-run>/pool build/ra/runs/<parent-run>/pool      # renoir-style runs
```

- Either argument can be a run folder with `replays/` inside, or the replays folder itself.
- It pairs games on the file name `s<seed>__<map>__<A>__<B>.replay`.
- It needs nothing else (no corpus store, no DuckDB), and caches decoded replays in `build/s1/tempo_cache/`.
- Decoding runs at ~1 replay/s per core the first time. Re-runs take seconds.

**Reading the output** (renoir-07c vs renoir-00-base, pool, 125 paired fixtures):

```
map                      ref        n    cand  parent   delta   95% CI
Default                  top10     12    -1.6     4.7    -6.3   [-11.1, -1.9]
Trophy                   top10     12    14.7    12.5    +2.2   [-1.7, +6.2]
...
tempo delta (candidate - parent, rounds, maps weighted equally; negative = faster): -1.17  95% CI [-2.42, +0.04]
guards ...  ally head-on /1k  2.013 -> 2.849 (worse by >10%)
VERDICT: NO GAIN (a 3-round improvement is excluded; keep the parent)
```

| Verdict | Rule | What to do |
|---|---|---|
| **ACCEPT** | delta ≤ −3 rounds, the 95 % CI is entirely below 0, and no map is significantly slower by more than 5 rounds | keep the change |
| **NO GAIN** | the CI rules out a 3-round gain (lower bound > −3) | keep the parent; the change is too small to matter for the opening |
| **REJECT** | the CI is entirely above 0 | the candidate is slower |
| **INCONCLUSIVE** | anything else | add seeds (the line says how many fixtures would settle it); do not tune on the same games |

**Why 3 rounds.**

- In the field, 3 rounds of tempo is worth ≈ 5 win points at 50 % (≈ 50 Elo); 10 rounds ≈ 16 points.
- Our live gap to the top ten is ~23–26 rounds. 3 rounds is an eighth of it.
- It is resolvable on current panels. The within-map spread of tempo on the local pool is ~10 rounds (field 20), so a
  3-round change needs ~85–170 side-games per arm depending on how well seeds pair. That is one pool run.

**Where everyone stands** (live corpus, rounds behind the eight-team reference; median per map, maps weighted equally):

| cohort | rounds behind |
|---|---|
| top 10 | 3.1 (includes SSS and Cutlery) |
| ranks 11–30 | 12.0 |
| ranks 31–50 | 14.1 |
| us (all team-7 games) | 26.1 |
| us since 29 Sep 06:00 | 22.9 |

Per map, us / top 10:

| map | us | top 10 |
|---|---|---|
| PD 10 | 60 | 5 |
| PD | 43 | 3 |
| Devil | 35 | 7 |
| Trophy | 34 | 3 |
| Autarky | 32 | 1 |
| Trauma | 29 | 4 |
| QoS | 26 | 4 |
| Portals | 14 | 3 |
| Default | 12 | 2 |
| Slithery | 8 | 1 |
| Schooltime | −5 | 1 |

Almost all of our gap is income, not loss: churn costs us the pearls dead newborns never eat, not the length itself.

**Pitfalls.**

- **Tempo depends on the opponents.** Compare a candidate only with its parent on the same panel. Absolute local
  numbers are not field numbers: the base scores ~5 rounds behind on the local pool, and ~23 live.
- **Ignore drift on its own.** Every cohort's drift is positive against a median reference; compare it between arms.
- **Eliminated sides** keep their last state, so their lag grows one round per round. That is intended.

Validation, definitions and the corpus numbers: `docs/findings/2026-09-30-s1-T-tempo-metric.md`.


## Summary

Optimise locally against three things. First, a **map-normalised economy curve**: pearls eaten at r50, r100, r150 and r250, divided by the field's median for that map. Second, **dragons and length at r100 on the same scale**. Third, a **hygiene group of self-inflicted death rates**. Use opponent-relative shares only as outcome proxies against a fixed panel.

- **Stripping context works, but the two kinds of stripping do different jobs.**
  - Dividing by the field's per-map median removes most of the map effect: in the field, the map's share of variance falls from 0.74 to 0.13. It adds little opponent noise (0.10) and puts the zoo and the field on one scale.
  - Taking the share against the opponent (ours / (ours + theirs)) removes the map entirely. It predicts results best (field log-odds per sd 1.10–1.58 vs 0.76–0.89 for the map-normalised version) and carries best across maps.
  - The cost of the relative version: 26–30% of its variance is *who you played*, so it is only comparable within a fixed opponent panel.
- **The economy gap is about 20% and consistent.** The zoo's median economy sits at 0.91–1.03 of the field median at every checkpoint. Field winners sit at 1.17–1.25 and the top ten teams at 1.13–1.17. Our best bots (chaewon-y04 1.28, yuna-v05 1.20 at r100) already match winners early.
- **Self-inflicted deaths behave like hygiene, not strategy.**
  - They are the most stable metrics we have (seed ICC 0.91–0.98, opponent share ≤ 0.09). They are the most bot-owned (the same team ranks the same on other maps: 0.6–0.86 correlation in the field).
  - The top ten teams have a median of 0 wall and self deaths, against 4.0 and 3.0 per 1k dragon-turns in the zoo. *(30 Sep: that is a per-side-game median. Pooled over 40k games the top ten run 5.3 wall and 3.8 own-body per 1k in rounds 0–150, plus 6.7 chosen deaths (suicide and invalid). See "Start here", point 3.)*
  - But they do not predict a team's rating (ρ ≈ 0). Within a game they even come slightly with winning (+0.20 log-odds live), because busy, winning swarms also bump into themselves more.
  - So they are safe to push down, as long as the economy curve does not drop.

Measuring against the field, on its average, its top ten and its full distribution, holds up. The field percentile on the same map is the best-behaved yardstick: it strips the most map and needs the fewest games, for example 13 side-games instead of 20 for kelp deaths. Report each benchmark as absolute, gap to the top ten, and field percentile, and optimise on the percentile.

## What makes a metric safe to optimise

A benchmark earns its place on six measured properties. Each was computed for 46 candidate metrics on the z1 zoo panel (560 seed-1 games, 80 fixtures × 3 seeds) and on 4,563 field games from 143 teams.

| Property | Why it matters | Measured as |
| --- | --- | --- |
| Low seed noise | A change must show up without thousands of games | Seed ICC: share of variance that survives re-seeding the same fixture |
| Bot-owned | An optimiser can only move what the bot controls | Share of within-map variance explained by which bot played |
| Low opponent contamination | Otherwise gains depend on who is in the panel | Share explained by the opponent, after the bot |
| Carries across maps | Final maps are out of sample | Leave-one-map-out rank correlation of bot (zoo) or team (field) means |
| Wins games | Otherwise it is style, not strength | Log-odds of winning per within-map sd, with the zoo rating or the Elo expected score held fixed |
| Same sign live | Local gains must mean something live | The field coefficient has the same sign and similar size as the zoo's |

A metric that is stable and bot-owned but not win-relevant is **hygiene**: reduce it, but never trade economy for it. A metric that wins games but is opponent-contaminated is an **outcome proxy**: compare it only against the same opponent panel.

## Does stripping context help?

Yes, keep the idea, but use each version for its own job. Map normalisation is the default yardstick. Opponent-relative shares predict results best, but they are only fair against a fixed panel.

| Metric (pearls eaten by r100) | Map share of variance (zoo / field) | Opponent share (zoo / field) | Seed ICC | Cross-map consistency (zoo / field) | Log-odds per sd (zoo / field) |
| --- | --- | --- | --- | --- | --- |
| Raw count `pearls@100` | 0.89 / 0.74 | 0.01 / 0.02 | 0.97 | 0.34 / 0.28 | 1.04 / 0.76 |
| Map-normalised `pearls@100\|map` | 0.45 / 0.13 | 0.10 / 0.09 | 0.77 | 0.35 / 0.34 | 1.04 / 0.76 |
| Capacity-normalised `bed_yield@100` | 0.60 / 0.61 | 0.07 / 0.05 | 0.79 | 0.35 / 0.29 | 1.05 / 0.79 |
| Opponent-relative `pearls@100\|rel` | 0 / 0 | 0.28 / 0.23 | 0.68 | 0.49 / 0.37 | 1.26 / 1.10 |
| Relative rate `pearls_per100dt_0_100\|rel` | 0 / 0 | 0.28 / 0.24 | 0.69 | 0.35 / 0.31 | 0.81 / 0.58 |

- **The raw count's high seed ICC is flattery.** Its stability comes from the map (89% of its variance), and the map is exactly what will be new in the final.
- **Dividing by bed capacity does not remove the map.** Maps differ in how reachable their beds are, not just in how many they have. So `bed_yield` stays 60% map. The empirical per-map median works better.
- **The relative share adds signal and adds the opponent.** It raises the win coefficient by a quarter to a half and carries best across maps (0.49). But 23–30% of its variance is the opponent, and its seed ICC falls to 0.68.
- **Relative-and-map combined is redundant.** A share against the opponent in the same game is already map-free: the map share is exactly 0.

The map-normalised numbers use the field's own per-map medians (`benchmarks/map_reference_medians.json`). That fixes the yardstick outside our zoo, so zoo runs, field games and future bots are all measured on the same scale. On an out-of-sample map, the reference is simply the first few hundred games of that map.

## Relative to the field: average, top and rank

Measuring against the field works, and the best form is a side's **percentile among field sides on the same map**. It keeps everything map normalisation gives, strips more of the map, and cuts the noise further, most of all for deaths.

| Version | Map share (zoo) | Bot share | Opponent share | Cross-map (zoo) | Side-games for half a bot-sd |
| --- | --- | --- | --- | --- | --- |
| Pearls at r100 ÷ field median | 0.45 | 0.25 | 0.10 | 0.35 | ~52 |
| Pearls at r100 ÷ top-10 median | 0.30 | 0.33 | 0.12 | 0.27 | ~47 |
| Pearls at r100 ÷ field 90th percentile | 0.29 | 0.34 | 0.12 | 0.29 | ~47 |
| Pearls at r100 field percentile | 0.22 | 0.39 | 0.12 | 0.30 | ~44 |
| Kelp deaths per 1k, absolute | 0.34 | 0.47 | 0.03 | 0.60 | ~20 |
| Kelp deaths, excess over field median | 0.09 | 0.65 | 0.04 | 0.60 | ~20 |
| Kelp deaths field percentile | 0.08 | 0.74 | 0.03 | 0.76 | ~13 |
| All self-inflicted deaths, absolute | 0.47 | 0.30 | 0.05 | 0.31 | ~39 |
| All self-inflicted deaths field percentile | 0.15 | 0.51 | 0.09 | 0.39 | ~30 |

- **Average, top and rank are one scale with different zero points.** Within a map they order sides identically, so their win signal is the same (pearls at r100: 1.04 log-odds zoo, 0.76 field). What differs is how much map is left over and how noisy the number is.
- **The percentile strips the most map and is the cheapest to measure.** Kelp-death percentile resolves a change in about 13 side-games instead of 20. It carries across maps at 0.76 instead of 0.60.
- **Ratio to the top does not work for deaths.** The top-10 median is 0 for four of the five death rates on most maps, so a ratio divides by zero. For deaths, use the excess over the top in deaths per 1k, or the percentile.
- **The percentile has a ceiling for zero-inflated rates.** 30–50% of field sides have zero kelp deaths on each map, so a perfect bot scores about 0.75–0.85, not 1. Read it as the share of the field you beat, with ties counted half.

Where our zoo stands on each yardstick. Each cell reads zoo median / field winners / top-10 teams.

| Economy metric | ÷ field median (1 = average) | ÷ top-10 median (1 = top) | Field percentile |
| --- | --- | --- | --- |
| Pearls at r50 | 0.91 / 1.17 / 1.16 | 0.79 / 1.00 / 1.00 | 0.44 / 0.61 / 0.60 |
| Pearls at r100 | 0.96 / 1.22 / 1.17 | 0.79 / 1.04 / 1.00 | 0.47 / 0.63 / 0.59 |
| Pearls at r150 | 0.94 / 1.25 / 1.15 | 0.78 / 1.08 / 1.00 | 0.46 / 0.64 / 0.58 |
| Pearls at r250 | 1.03 / 1.25 / 1.13 | 0.89 / 1.11 / 1.00 | 0.52 / 0.65 / 0.58 |
| Dragons at r100 | 0.89 / 1.28 / 1.14 | 0.76 / 1.02 / 1.00 | 0.41 / 0.66 / 0.64 |
| Length at r100 | 0.87 / 1.26 / 1.15 | 0.75 / 1.04 / 1.00 | 0.39 / 0.67 / 0.64 |
| Births by r100 | 0.91 / 1.23 / 1.16 | 0.77 / 1.05 / 1.00 | 0.45 / 0.63 / 0.59 |

| Death rate (per 1k dragon-turns) | Absolute | Excess over field median | Excess over top-10 median | Field percentile (higher = fewer) |
| --- | --- | --- | --- | --- |
| All self-inflicted | 12.97 / 12.66 / 9.83 | +2.67 / +1.03 / −1.24 | +3.71 / +2.36 / 0.00 | 0.36 / 0.44 / 0.58 |
| Kelp | 4.01 / 2.12 / 0.00 | +1.18 / +0.22 / −0.48 | +3.40 / +1.66 / 0.00 | 0.40 / 0.48 / 0.75 |
| Own body | 3.00 / 2.15 / 0.00 | +1.63 / +0.33 / −0.71 | +2.94 / +2.12 / 0.00 | 0.35 / 0.46 / 0.78 |
| Ally body | 1.51 / 1.14 / 0.56 | +0.51 / +0.16 / −0.28 | +0.92 / +0.48 / 0.00 | 0.37 / 0.45 / 0.65 |
| Ally head-on | 0.79 / 0.45 / 0.50 | +0.38 / 0.00 / +0.03 | +0.19 / 0.00 / 0.00 | 0.35 / 0.52 / 0.49 |

On economy, the zoo median beats 39–52% of field sides, field winners beat 61–67%, and the top ten beat 58–64%. On self-inflicted deaths, the zoo median beats only 35–40%, against 44–52% for winners and 49–78% for the top ten.

Recommendation: report every benchmark as three numbers: the absolute value, the gap to the top ten (ratio for economy, excess per 1k for deaths), and the field percentile. Optimise on the percentile. The per-map references are fixed files: `field_references.json` holds the median, p10, p25, p75, p90 and top-10 median per map, and `field_distributions.json` holds the full sorted field values that percentiles are read from.

## The benchmark set

The set has three tiers. Tier 1 is what to push up. Tier 2 is what to push down without losing tier 1. Tier 3 is what to watch against a fixed panel. Values are medians per side-game. `|map` means divided by the field's median on the same map, so 1.0 is a typical field side.

![The zoo economy runs about 20% below field winners at every checkpoint](benchmarks/economy-curve.png)

*z1 zoo panel (seed 1, 1,120 side-games) and 4,563 corpus games from 28 Sep 2026; medians per side-game.*

The best zoo bots already eat like field winners. yuna-v05 is at 1.20 and chaewon-y04 at 1.28 at r100. They fail to *keep* it: their length at r100 is only 0.91–1.00 of the field median, against 1.26 for winners. So the curve to raise is the one in the chart, and the gap to close first is retention.

| Tier | Metric | Direction | Zoo | Field | Field winners | Top 10 | Target |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 Opening | **Tempo**: rounds behind the top-ten net-income curve, r10–150 (`tools/s1/tempo_gate.py`) | down | panel-relative | — | — | 3.1 (us live 26) | each step: ≤ −3 rounds vs parent (gate) |
| 1 Economy | Economy curve `pearls@{50,100,150,250}\|map` *(diagnostic since 30 Sep: counts recycled corpses, L29)* | up | chart | 1.00 | chart | chart | ≥ 1.20 at every checkpoint |
| 1 Economy | Dragons at r100 `units@100\|map` | up | 0.89 | 1.00 | 1.28 | 1.14 | ≥ 1.15 |
| 1 Economy | Length at r100 `total@100\|map` | up | 0.87 | 1.00 | 1.26 | 1.15 | ≥ 1.15 |
| 1 Economy | Births by r100 `births@100\|map` | up | 0.91 | 1.00 | 1.23 | 1.16 | ≥ 1.15 |
| 1 Economy | Early concentration `top1_share@100` | down | 0.11 | 0.10 | 0.08 | 0.08 | ≤ 0.09 |
| 2 Hygiene | Kelp deaths `death_wall_per1k` | down | 4.01 | 2.22 | 2.12 | 0.00 | < 1 |
| 2 Hygiene | Own-body deaths `death_self_per1k` | down | 3.00 | 1.81 | 2.15 | 0.00 | < 1 |
| 2 Hygiene | Ally-body deaths `death_ally_body_per1k` | down | 1.51 | 0.98 | 1.14 | 0.56 | < 0.8 |
| 2 Hygiene | Ally head-on deaths `death_h2h_ally_per1k` | down | 0.79 | 0.31 | 0.45 | 0.50 | < 0.5 *(a portal-exit event; read it with per-transit death within 3 rounds: top ten 0.20, us 0.28)* |
| 2 Hygiene | No-valid-action deaths `death_invalid_per1k` | down | 0.00 | 0.00 | 0.00 | 0.00 | 0 for our bots (ouroboros-m01 has 10.9: a bug; our 835 live ones are all age-0 newborns). The top ten use invalid actions and suicides on purpose (2.1 + 4.6 per 1k): not a target for them |
| 3 Proxy | Bed capture `bed_capture_share` | up | 0.46 | 0.46 | 0.61 | 0.54 | beat the same panel |
| 3 Proxy | Pearl share at r150 `pearls@150\|rel` | up | 0.50 | 0.50 | 0.62 | 0.55 | beat the same panel |
| 3 Proxy | Territory at r100 `territory@100` | up | 0.50 | 0.50 | 0.58 | 0.52 | beat the same panel |
| 3 Proxy | Length share at r250 `total_share@250` | up | 0.50 | 0.50 | 0.76 | 0.60 | beat the same panel |

Death rates are per 1,000 dragon-turns. Tier 3 medians are 0.50 by construction, so only the winners' column carries information.

Six of eight zoo bots share the kelp and self-collision habit; kazuha-s01 and ouroboros-m01 already have zero kelp deaths. All self-inflicted deaths together (`avoidable_deaths_per1k`) run at a median of 13.0 per 1,000 dragon-turns in the zoo, against 11.9 in the field and 9.8 for the top ten teams.

## Guardrails: how each metric can blow up

Optimise tier 1 and tier 2 jointly, and accept a change only if the win rate against the panel does not drop. Each metric below has a cheap way to game it that loses games.

- **Fewer self-inflicted deaths by playing small.** kazuha-s01 and hunter-v20 have the fewest self-inflicted deaths in the zoo (7.9 and 9.7 per 1k) and win 19% and 12%. Hygiene counts only when the economy curve holds or rises in the same run.
- **Economy curve by feeding the swarm to itself** (30 Sep). Pearls eaten from our own corpses count as economy. Renoir 07c passed the +0.05 bar on the pool through churn, while the tempo gate, which ignores recycled corpses, says NO GAIN and ally head-on rose 42 %. Decide opening changes on tempo.
- **Economy curve by splitting into dust.** Births and pearls rise when a bot splits constantly into 2-segment children. Guard with `newborn_deaths10_per100` (zoo 33 per 100 births; the field is the same, winners 31). Also guard with length at r100, which must rise with pearls. The retention gap in the chart is this failure already happening.
- **Low concentration by never building a crown.** `top1_share@100` should be low early. `total_share@250` (log-odds 2.2 zoo, 2.4 field) and the final longest dragon still decide games, so check the r250 share whenever early concentration moves.
- **Relative shares by picking soft opponents.** A tier 3 metric is only comparable against the same panel on the same maps and seeds. Never compare tier 3 numbers across panels.
- **Map-normalised numbers on maps without a reference.** For a new map the reference median does not exist. Use the tier 1 raw numbers against our own previous bot on the same map until about 200 field games give a median.

Three tempting metrics should stay diagnostics, not targets:

- `kill_length_ratio` — the sign runs against intuition (log-odds −1.2 zoo, −1.1 field) and is unexplained.
- Kill counts — most kills are mutual head-on collisions, so both sides score them.
- `enemy_caused_deaths_per1k` — it strongly predicts losing (−1.5). But it is 16% opponent and shows no cross-map consistency in the zoo (−0.03), so it is not a bot trait.

## How to use it

*(30 Sep: for lanes, step 4 is superseded by D-032: paired fixtures, seeds 1–3, an interval gate, implemented in `scorecard.py`. For changes aimed at the opening, run the tempo gate as well; see "Start here" at the top. 1 Oct: D-032 itself is revised by the H-1 steward — the phase-`end` tier, the either-panel accept rule and the cluster-bootstrap authority; see "Start here (1 Oct revision)" above. `scorecard.py`'s printed GATE line still implements the 30 Sep letter and is superseded for lane decisions by the lane scorers (`tools/*/lane.py`) plus `tools/clair/score_extra.py` for the endgame tier.)*

One candidate against the z1 panel is 140 side-games: 7 opponents × 10 live maps × 2 seats, at seed 1. That is enough to see a change of half the typical gap between two zoo bots on every tier 1 and tier 2 metric.

| Metric | Side-games to resolve half a between-bot sd |
| --- | --- |
| Kelp deaths | ~20 |
| All self-inflicted deaths | ~40 |
| Pearls at r50 / r100 / r150 / r250, map-normalised | ~45 / 50 / 45 / 60 |
| Dragons / length at r100, map-normalised | ~70 / 80 |
| Bed capture, pearl share (relative) | ~55 |

These are 80% power and 5% two-sided, from the residual spread after map, bot and opponent. A change a third that size needs about 2.8× as many games, so add seed 2 when a decision is close.

1. Run the candidate against the fixed panel: `python -m tools.analysis.features.run_panel` with the candidate added to `ZOO`, seed 1, `--no-logs`.
2. Extract features: `python -m tools.analysis.features extract build/zoo/<panel>/replays --out … --cache …`.
3. Score it: `python -m tools.analysis.features.benchmarks`. This adds the `|map`, `|rel`, `|top`, `|xs`, `|xstop` and `|pct` columns from the fixed field references in `field_references.json` and `field_distributions.json`, so every run is on the same yardstick.
4. Accept a change when:
   - tier 1 rises by at least 0.05 of field median on the mean of the four economy checkpoints, with dragons and length at r100 not falling;
   - no tier 2 rate rises by more than 10%;
   - the win rate against the panel does not fall.

   Otherwise rerun at seed 2 before deciding.

The single-bot scorecard now exists (R-4): `python -m tools.analysis.features.scorecard bots/<candidate> --parent bots/<parent>`. It prints the tier tables, W-L-D and the D-032 gate line. The tempo gate is `python3 tools/s1/tempo_gate.py <candidate run> <parent run>`.

## Evidence

Every candidate screened, grouped by family.

- **Bot share / opponent share:** shares of within-map variance in the zoo (seed 1).
- **Cross-map:** leave-one-map-out rank correlation of bot means (zoo) or team means (field: 85 teams with at least 40 side-games).
- **Log-odds:** per within-map sd, holding the zoo rating (zoo) or the Elo expected score (field) fixed.
- **Team ρ:** Spearman correlation of a team's mean with its latest rating.

| Metric | Kind | Seed ICC | Bot share | Opp share | Cross-map zoo | Log-odds zoo | Log-odds field | Team ρ rating | Cross-map field |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `top1_share@100` | raw | 0.76 | 0.26 | 0.08 | 0.43 | -1.17 | -0.90 | -0.42 | 0.32 |
| `bed_yield@100` | capacity | 0.79 | 0.14 | 0.07 | 0.35 | 1.05 | 0.79 | 0.51 | 0.29 |
| `bed_yield@250` | capacity | 0.84 | 0.19 | 0.10 | 0.27 | 1.45 | 1.00 | 0.43 | 0.31 |
| `pearls@50\|map` | map | 0.67 | 0.34 | 0.06 | 0.42 | 0.78 | 0.58 | 0.46 | 0.31 |
| `pearls@100\|map` | map | 0.77 | 0.25 | 0.10 | 0.35 | 1.04 | 0.76 | 0.46 | 0.34 |
| `pearls@150\|map` | map | 0.81 | 0.28 | 0.13 | 0.44 | 1.22 | 0.85 | 0.45 | 0.35 |
| `pearls@250\|map` | map | 0.76 | 0.30 | 0.16 | 0.42 | 1.36 | 0.89 | 0.39 | 0.33 |
| `pearls_per100dt_0_100\|map` | map | 0.76 | 0.38 | 0.05 | 0.34 | 0.52 | 0.31 | 0.28 | 0.34 |
| `pearls@100` | raw | 0.97 | 0.07 | 0.01 | 0.34 | 1.04 | 0.76 | 0.46 | 0.28 |
| `pearls_per100dt_0_100` | rate | 0.89 | 0.29 | 0.04 | 0.31 | 0.52 | 0.31 | 0.28 | 0.34 |
| `pearls_per100dt_100_250` | rate | 0.91 | 0.32 | 0.04 | 0.27 | 0.33 | -0.04 | 0.09 | 0.45 |
| `epg_conversion` | rate | 0.88 | 0.11 | 0.03 | 0.12 | 0.22 | 0.11 | 0.10 | 0.31 |
| `bed_capture_share` | relative | 0.76 | 0.39 | 0.26 | 0.49 | 2.13 | 1.83 | 0.38 | 0.42 |
| `bed_pearls@100\|rel` | relative | 0.69 | 0.38 | 0.28 | 0.48 | 1.28 | 1.15 | 0.32 | 0.37 |
| `pearls@50\|rel` | relative | 0.63 | 0.35 | 0.26 | 0.42 | 0.82 | 0.80 | 0.25 | 0.30 |
| `pearls@100\|rel` | relative | 0.68 | 0.39 | 0.28 | 0.49 | 1.26 | 1.10 | 0.32 | 0.37 |
| `pearls@150\|rel` | relative | 0.75 | 0.40 | 0.29 | 0.46 | 1.56 | 1.30 | 0.35 | 0.40 |
| `pearls@250\|rel` | relative | 0.76 | 0.41 | 0.30 | 0.50 | 1.88 | 1.58 | 0.37 | 0.43 |
| `pearls_per100dt_0_100\|rel` | relative | 0.69 | 0.39 | 0.28 | 0.35 | 0.81 | 0.58 | 0.18 | 0.31 |
| `total@100` | raw | 0.89 | 0.09 | 0.06 | 0.16 | 1.31 | 1.08 | 0.57 | 0.32 |
| `total@100\|map` | map | 0.69 | 0.26 | 0.19 | 0.23 | 1.31 | 1.08 | 0.57 | 0.37 |
| `units@100\|map` | map | 0.72 | 0.29 | 0.19 | 0.27 | 1.35 | 1.04 | 0.55 | 0.39 |
| `total_share@100` | relative | 0.65 | 0.35 | 0.25 | 0.43 | 1.52 | 1.55 | 0.43 | 0.39 |
| `units_share@100` | relative | 0.67 | 0.35 | 0.26 | 0.45 | 1.58 | 1.46 | 0.39 | 0.41 |
| `total_share@250` | relative | 0.67 | 0.36 | 0.26 | 0.59 | 2.19 | 2.37 | 0.47 | 0.45 |
| `births@100\|map` | map | 0.77 | 0.26 | 0.10 | 0.48 | 1.10 | 0.75 | 0.49 | 0.34 |
| `births@100\|rel` | relative | 0.69 | 0.39 | 0.29 | 0.45 | 1.29 | 1.12 | 0.33 | 0.35 |
| `newborn_deaths10_per100` | rate | 0.92 | 0.30 | 0.07 | 0.15 | -0.24 | -0.36 | 0.06 | 0.35 |
| `territory@100` | relative | 0.65 | 0.33 | 0.24 | 0.51 | 1.78 | 1.63 | 0.44 | 0.37 |
| `seen_share@100` | capacity | 0.87 | 0.17 | 0.04 | 0.61 | 0.93 | 0.47 | 0.33 | 0.55 |
| `death_wall_per1k` | rate | 0.94 | 0.47 | 0.03 | 0.60 | 0.06 | -0.02 | 0.04 | 0.80 |
| `death_self_per1k` | rate | 0.96 | 0.33 | 0.06 | 0.50 | 0.59 | 0.21 | -0.12 | 0.78 |
| `death_ally_body_per1k` | rate | 0.91 | 0.40 | 0.09 | 0.61 | 0.63 | 0.21 | -0.03 | 0.72 |
| `death_h2h_ally_per1k` | rate | 0.98 | 0.41 | 0.02 | 0.19 | 0.24 | 0.06 | -0.15 | 0.60 |
| `death_invalid_per1k` | rate | 0.98 | 0.85 | 0.00 | 1.00 | 0.06 | 0.03 | -0.22 | 0.86 |
| `avoidable_deaths_per1k` | rate | 0.96 | 0.30 | 0.05 | 0.31 | 0.52 | 0.20 | 0.00 | 0.52 |
| `avoidable_deaths_per1k\|map` | map | 0.75 | 0.43 | 0.10 | 0.36 | 0.52 | 0.20 | 0.00 | 0.52 |
| `avoidable_deaths_per1k\|rel` | relative | 0.73 | 0.42 | 0.31 | 0.42 | 0.79 | 0.42 | 0.03 | 0.50 |
| `avoidable_death_share` | rate | 0.77 | 0.21 | 0.15 | 0.37 | 1.35 | 0.68 | -0.11 | 0.52 |
| `deaths_per1k` | rate | 0.96 | 0.30 | 0.07 | 0.12 | -0.26 | -0.51 | 0.08 | 0.48 |
| `deaths_per1k\|rel` | relative | 0.79 | 0.40 | 0.29 | 0.09 | -0.31 | -0.65 | -0.10 | 0.40 |
| `enemy_caused_deaths_per1k` | rate | 0.86 | 0.13 | 0.16 | -0.03 | -1.51 | -1.48 | 0.01 | 0.43 |
| `death_rate_enclosed_per1k` | rate | 0.75 | 0.20 | 0.05 | 0.23 | -0.11 | -0.48 | -0.19 | 0.50 |
| `enclosed_share_mean` | rate | 0.92 | 0.16 | 0.03 | 0.25 | 0.25 | 0.20 | 0.14 | 0.31 |
| `kill_length_ratio` | relative | 0.80 | 0.14 | 0.15 | 0.19 | -1.20 | -1.06 | -0.01 | 0.31 |
| `sprint_cost_per_pearl` | rate | 0.85 | 0.50 | 0.05 | 0.88 | -0.64 | -0.19 | 0.18 | 0.85 |

Sources: the z1 panel (1,120 seed-1 side-games plus 320 side-games at seeds 2–3) and 4,563 public corpus games from 28 Sep 2026 (10:15–20:43 UTC). Regenerate with `tools/analysis/features/benchmarks.py`; the full screen is `benchmark_screen.csv`.
