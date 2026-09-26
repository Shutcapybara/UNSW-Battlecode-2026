# Serre: the super-lineage — compose the proven mechanisms onto the strongest chassis

Lineage owner: Kimi. Founded 2026-09-26. Mission (owner brief, meta-level):
stand above the individual lineage studies, find the existing bots that
actually perform, work out *what makes them good*, and combine those
mechanisms into one lineage — iterating Serre toward the best bot in the
repository. The organising documents are the strategy/execution brief
(`docs/STRATEGY_AND_EXECUTION.txt`) and its statistical input
(`docs/STRATEGIC_STATS_SUMMARY.md`); every other lineage's study doc is
treated as a parts catalogue with measured evidence attached.

## 1. Method

Each lineage already ran a disciplined single-question study (combat on two
chasses, density features, portal memory, execution contracts). Their
**positive results are proven mechanisms with frozen evidence**; their
**negative results are equally valuable** — they mark mechanisms that must
not be re-tried. Serre's method is composition, not exploration:

1. Take the strongest measured bot as the foundation (§3).
2. Graft **one proven mechanism per arm**, behind a default-off switch, with
   the borrowed source recorded. Parameter retunes of the inherited evaluator
   are not grafts — sinbad already measured its local optimum.
3. Pair every arm per-fixture against the incumbent's baseline record on the
   dev screen (deterministic engine). Advance/gauntlet/promotion gates are
   frozen in `tools/serre/selection_rule.json` (written before any outcome
   was read), including per-map-class regression checks — the drake big_empty
   lesson: no aggregate promotion with a collapsed map class.
4. Read the fresh reserve once per release candidate. Judge-meter every
   promoted source.

## 2. Who is actually good (64,192-game shared ledger, 2026-09-26)

Two independent instruments, used together: the model-adjusted rating panel
(`experiment_data/bot-ratings/latest.md`, 236 frozen versions) and direct
fixture-collapsed native head-to-heads recomputed from `game_stats.parquet`.
Sparse ratings (few fixtures/opponents) are treated as hints, never verdicts —
feynman-x01's 78.9% rests on 14 fixtures against a weak slice; vn-x06-info-grad1's
84.0% on 36.

**Established top tier** (rating, fixtures, and direct H2H agree):

| Bot | Panel | Key direct head-to-heads (fixture-collapsed) |
|---|---|---|
| **sinbad-v07-divecap** | **84.0%** (114 fix, 55 opp) | 18–6 ouroboros-v13 · 20–2 leviathan-v09 · 17–5 tew-v12 · 13–11 monte_christo-x12 · 4–0 valjean-v01 · 2–0/2–0/2–2 von_neumann x06/x01/x04 |
| von_neumann-x04-support | 83.1% (87 fix) | 6–2 ouroboros-v13 · 6–2 tew-v12 · 2–2 sinbad-v07 |
| von_neumann-x01-frozen (= porthos-x04-policy byte-copy) | 78.3% | 9–3 ouroboros-v13 · 6–2 tew-v12 · 0–4 avery-v08 · 0–2 sinbad-v07 |
| valjean-v01-portal-memory | 77.7% | 4–0 vn-x03 · 3–1 vn-x01 · 0–4 sinbad-v07 |
| monte_christo-x12-remote-density | 75.7% (164 fix) | 8–2 ouroboros-v13 · 8–2 tew-v12 · 6–4 MC-v01 · 11–13 sinbad-v07 |
| porthos-x04-policy | 74.5% (378 fix) | 23–11 ouroboros-v13 · 22–16 tew-v12 |
| ouroboros-v13-ladder | 73.5% (1428 fix) | 18–30 MC-v01 · loses to the whole tier above |

The same data exposes **matchup structure the panel averages hide**:
leviathan-v09 wins 76.7% of its 1639 field games but goes **2–20 vs
sinbad-v07 and 3–19 vs sinbad-v06** — arrival-aware economy beats the field
and loses to the sinbad threat model specifically. avery-v08 crown-race is
mid-tier overall yet **4–0 vs the porthos/von_neumann chassis** on fresh maps:
the crown endgame is the French line's measured hole.

## 3. What makes the best bots good (mechanism inventory with evidence)

**sinbad-v07-divecap — the foundation.** Every gain came from diagnosing a
structural leak in replays, not from tuning:
- arrival-aware bed values — a bed counts only if its pearl is due when we
  arrive (v06: compact maps 13–19 → 25–7);
- threat model, crown/feeding, food sharing by sonar, CPU budget (v02);
- hunting by dragons up to length 8, two-level trap penalty, strike search
  (v03–v05);
- portal-pair sharing and escape split (v03);
- dive-incentive cut 7→3 after traces showed exploratory portal dives fatal
  ~37% of the time, often killing an ally too (v07: portal maps 36–20 → 45–11);
- newborn body-chain fix (e23: a freshly split dragon misread its own body;
  a 14-long crown died on its first move).

**porthos-x04 / von_neumann — French line.** Policy P1: early-saturation
aggression (foragers at the population cap push into enemy density to gain
space) + confinement-gated REPRODUCE — measured **+13 on the 182-game
gauntlet** over its state/radio control. Von Neumann's combat study on the
same chassis adds the verdict that shapes Serre's combat expectations:
removing strikes costs 5 games (combat is load-bearing), but 28 admission
re-parameterisations and both new conditioning mechanisms all fail — **the
binding constraint is contact creation by economy movement, not trade
admission**. Matches the replay statistics: opponent-kill advantage adds
nothing at round 100 (−0.0002), initiating contact is on average negative.

**valjean-v01 — portal-exit risk memory.** Monte Christo charged every unseen
portal exit a full dragon's value, so dragons sat forever in closed portal
boxes; estimating exit risk from sightings near the exit in the last 12 rounds
(floor 0.15; 0.5 unseen; 1.0 if a body was near) took dilemma+autarky from
3–21 to 14–10. Its RELEASE also ports sinbad-v06's settings into the Monte
Christo architecture — proof that sinbad's mechanics transfer across
codebases.

**javert-v01 — length-density radio.** A 44-bit type-7 packet (ally/enemy
visible *length* sums, co-rounded sender/round/position merge guard, no relay
amplification) on a second reserved ray. The only radio change in the whole
programme that survived a fresh reserve (10–2; the entire gain was three
confined-map conversions). The policy features consuming it were
outcome-neutral — **the information itself was the win**.

**ouroboros-v13 — map-class awareness.** Ladder production/strike path on
compact maps (≤625 tiles), evaluator path on open maps; best-measured strong
bot (1428 fixtures) and Godel's chosen chassis for exactly this property.

**avery-v08 — crown-race endgame.** Crown banking/feeding schedules; beats
the French line 4–0 on fresh combat maps. The endgame (longest living
dragon, then total length) is a distinct game the economy bots can lose
after winning 400 rounds.

**Negative knowledge (do not graft):** devaluing pocket/dead-end pearls
(halves intake — pocket farming *is* the economy); crowding/enclosed-space
split penalties (null/negative twice); isotropic count-gradient frontiers
(failed the fresh reserve; gradients must be route-aware, persistence-gated,
multi-source); long-window dual EWMA as spatial contrast (big_empty collapse,
twice); racing the population cap (+0.00145 — no value beyond expansion);
kill-volume objectives; time-ramped danger multipliers (time is a gate, not
a multiplier).

## 4. Foundation and alternatives

**serre-v01-foundation = byte-copy of `build/sinbad/exp/e23`** (sinbad v07 +
newborn bugfix; sinbad's designated v08 start). Manifest
`tools/serre/frozen.json`: 10 files, zero mismatches.

| Candidate | Why not |
|---|---|
| porthos-x04 / von_neumann | Strong (gauntlet 126–56), but loses the direct H2H samples to sinbad-v07; its own study shows its combat surface is at a flat optimum |
| valjean-v01 | Strictly weaker measured base (0–4 vs sinbad-v07); its architecture is the better *experiment* chassis, not the better player |
| ouroboros-v13 | Best-measured, but loses every top-tier H2H; kept as gauntlet opponent |
| monte_christo-x12 | 11–13 vs sinbad-v07; density radio is a graft source, not a base |

Feynman's baseline table rejected sinbad as a *feature-study* chassis
(monolithic evaluator, no intention contract). Serre's goal is playing
strength by composition, so the monolith with the dominant record is the
right foundation — and sinbad's own arena/override workflow supports
default-off graft arms.

## 5. Harness

- Dev screen `configs/serre/screen.toml`: ouroboros-v13, leviathan-v09,
  porthos-x04, avery-v08 × devil, queen_of_spades, trauma, Colosseum × both
  sides = 32 games. Map choice targets the foundation's measured leaks.
- Gauntlet `configs/serre/gauntlet.toml`: 7 opponents × 13 maps × both
  sides = 182 games (roster in the config header).
- Fresh reserve `configs/serre/reserve.toml`: two families frozen before any
  outcome was read (`tools/serre/make_reserve.py`,
  `tools/serre/reserve_frozen.json`): **twinlakes** (30×22, open, two rich
  bed clusters — pure economy/distribution/endgame transition) and
  **crossfire** (26×26, central fast-bed band behind staggered kelp walls +
  one mirror-paired portal — the devil leak and portal-exit risk surface).
  4 opponents × 2 maps × both sides = 16 games.
- Judge `configs/serre/sandbox.toml`: hunter-v22 × arena/stronghold × both
  sides, sandbox mode.
- Selection/promotion gates: `tools/serre/selection_rule.json` (frozen
  2026-09-26 before any outcome was read).
- Runner: `PYTHONPYCACHEPREFIX=/tmp/serre-pycache .venv/bin/python
  tools/compare_bot.py bots/<candidate> --config <toml>` with
  `PATH="$HOME/.local/bin:$PATH"` (unswbc 1.0.0 — do not upgrade mid-study).
  Long runs detached with `nohup`, polled via `progress.json`; `--resume`
  per run directory recovers interruptions.

## 6. Baseline records (serre-v01-foundation)

Native, deterministic fixtures, both sides; zero errors/faults everywhere.

| Set | Run | Record |
|---|---|---|
| Screen (32) | `experiment_data/serre-v01-foundation_20260926043218987725` | **23–9**: ouroboros 6–2, leviathan 7–1, porthos 5–3, avery 5–3 · Colosseum 8–0, queen 7–1, trauma 6–2, **devil 2–6** |
| Reserve (16) | `experiment_data/serre-v01-foundation_20260926043901052781` | **13–3**: twinlakes 8–0, crossfire 5–3 · avery 4–0, ouroboros 3–1, leviathan 3–1, MC-x12 3–1 |
| Gauntlet (182) | `experiment_data/serre-v01-foundation_20260926044305646987` | running |
| Judge sandbox (4) | — | pending |

The devil leak reproduces on fresh fixtures (2–6), confirming it as the
foundation's largest measured hole. Crossfire's 5–3 shows the contested-centre
+ portal surface is beatable but not dominant.

**Devil leak quantified (G1 diagnosis, screen replays, `tools/sinbad/deaths.py`
+ `eatmap.py`):** the foundation harvests **103–211 bed pearls per devil game
vs the opponent's 575–779** (a 4–7× throughput deficit), and the gap opens
early — ~60–80 vs ~210 in the first 150 rounds — so the centre is never
contested, not lost late. Death profiles show the churn is congestion, not
combat: `self`/`wall`/`body` deaths of length-2–3 dragons dominate (200+
self-deaths in long games vs leviathan/porthos), almost all with **zero free
exits**. The foundation cedes the fast beds, then its crowd strangles itself
on its own half while the winner farms the centre. G1 must therefore move
collectors into contested space early *and* relieve self-congestion — pushing
more bodies at the centre without decongesting would feed the second problem.

## 7. Graft roadmap (ranked by expected value)

| # | Graft | Source lineage (evidence) | Target leak | Integration surface |
|---|---|---|---|---|
| G1 | **Contested-centre economy**: value/support machinery that commits collectors to contested fast beds instead of ceding them | sinbad handoff (devil 6–12; own half eatmap), porthos P1 early-saturation push (+13 gauntlet), ouroboros contest path | devil 2–6, crossfire 5–3 | decision: bed values contested-aware; approach toward supported contested beds. Diagnose with `tools/sinbad/eatmap.py` + deaths first |
| G2 | **Portal-exit risk memory**: estimate unseen-exit risk from recent sightings near the exit (floor 0.15 / 0.5 / 1.0) instead of a flat dive penalty | valjean-v01 (dilemma+autarky 3–21 → 14–10) | crossfire portals; FX/FY robustness | state: per-portal risk table; decision: replace flat `p_dive`/`v_dive` terms |
| G3 | **Map-symmetry inference**: detect the map's symmetry class early; mirror own-side observations (beds, terrain, portal pairs) onto their half | sinbad handoff idea #1 (no prior art) | FX/FY ~50% vs 75% originals; slow bed discovery | world/state: symmetry hypothesis + mirrored bed/portal priors |
| G4 | **Opening production**: faster productive splitting in the first 30 rounds (production ladder geometry, child-exit checks) | ouroboros-v13 ladder (compact), tew-v07/v12, avery compact production; stats: expansion +0.1044 | arena 10–8, out-produced 2× by round 20 | roles/production doctrine; keep per-stats warning: split for future collection, not cap racing |
| G5 | **Endgame transition + long-dragon protection**: enemy-density-aware retreat and crown preservation once expansion value falls; guard long dragons from short enemy heads on big maps | avery-v08 crown-race (4–0 vs French line), sinbad idea #3 (~9 long dragons/big_empty game), feynman F4 design, stats: longest-living-dragon tiebreak | round-500 length stalls; big-map crown deaths | decision: phase-gated (gate, not multiplier) preservation regime; RETREAT direction from enemy density |
| G6 | **Length-density radio**: javert's type-7 packet discipline (44-bit length sums, merge guard, no relay amplification) | javert-v01 (fresh reserve 10–2; only proven radio win) | confined-map coordination | comms/radio: info-only cell first (send/hear/cache, nothing consumes), consumption cell second |
| G7 | **Contact creation**: executor-level approach/intercept objectives that manufacture favourable contacts | von_neumann verdict (binding constraint), aramis ATTACK separation | secondary; combat volume itself is ~null | candidates/executors — only after G1–G5; judge by material retained, never kills |

Each graft: hypothesis card → default-off arm → 32-game screen (advance ≥
baseline+2, no map cell worse than −2) → 182-game gauntlet (≥ +3, devil+arena
watched) → 16-game fresh reserve (≥ baseline+1) → judge clean → release as
`bots/serre-vNN-<name>`. Mechanism metrics (pearls/round, new-unit survival,
attributed length lost, crown conversion, per-map W-L) accompany every arm.

## 8. Experiment log

| Arm | Change | Screen | Gauntlet | Reserve | Judge | Verdict |
|---|---|---|---|---|---|---|
| v01 foundation | = sinbad e23 | 23–9 | — | 13–3 | — | **baseline established** |

## 9. Shared-workspace notes

- Other lineages (GLM: von_neumann; Kimi sessions: godel, feynman) are
  active in this tree. Commit only `bots/serre-*`, `configs/serre/`,
  `tools/serre/`, `tests/test_serre_*.py`, `docs/serre.md`, and this lineage's
  `game_stats/runs/*.parquet` contributions. Never edit another lineage's
  measured version — copy with a new name.
- The ledger is append-only: publish run contributions, rebuild the central
  parquet per `game_stats/README.md`.
- Foreground shell cap ~300 s: screens/reserve fit; the gauntlet runs
  detached. Device throughput measured 2026-09-26: ~7–8 games/min at jobs 6.
