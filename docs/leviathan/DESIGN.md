# Current direction: cycle 1 convergence

Leviathan now maintains a local convergence base in `bots/leviathan-v08-core`
and a pearl-component experiment in `bots/leviathan-v09-arrival`. V08 explicitly
borrows the complete Ouroboros v10 evaluator, with an equivalent parameter-table
extraction. V09 separates arrival-time bed targets from confirmed immediate
growth. Crown, feeding and teammate information consumers are inherited, not
new Leviathan inventions. The earlier v07 design below is retained as history.

See [CONVERGENCE.md](CONVERGENCE.md) for scope, component interfaces, neutral
parameters, and the inherited packet/doctrine gaps. See [RESULTS.md](RESULTS.md)
and each bot README for measured outcomes. The unifier owns ACTIVE promotion.

The independent [Riptide family](RIPTIDE.md) uses `leviathan-xNN-riptide-*`
for the user-requested hard divergence: fresh C++ route forecasting,
resource-funded reproduction, and distributed length banking. Its separate
[results](RIPTIDE_RESULTS.md) preserve experimental baselines and ablations.

[Charybdis](CHARYBDIS.md), `leviathan-x04-charybdis-replies`, is a separate
chess-inspired exploration: a local multi-actor game with adversarial replies,
birth-round scheduling, and explicitly valued head trades. Its
[results](CHARYBDIS_RESULTS.md) include a no-search control, decision traces,
and preserved compute-budget failures. It does not replace either family.

---

# Leviathan design and iteration framework

Leviathan is GPT's independent Python lineage. Hydra, Kraken, Ouroborous, and the
shared runner are read-only dependencies. New work goes in `bots/leviathan-*`,
`tools/leviathan`, `docs/leviathan`, and `build/leviathan`.

## Objective and architecture

The actual objective is lexicographic: avoid elimination, then maximize the
longest surviving dragon at round 500, then total team length. Population and
territory are instruments for achieving that objective, not the final score.

Each dragon runs its own process:

1. Parse the local observation and public sonar messages.
2. Update persistent terrain, paired portals, pearl observations, spawn countdowns,
   own body, visits, and recent teammate reports.
3. Build a bounded enemy reach estimate and a bounded pearl/frontier search.
4. Enumerate legal moves, sprints of up to three steps, head trades, and splits.
5. Score candidates, choose the best, simulate its body, and write once.

The bot is self-contained (`main.py`, `weights.py`, `bot.toml`). It imports no
other lineage. Reading Kraken informed protocol handling, toroidal portal
geometry, capped search, per-dragon memory, and the first-turn budget concern.
The implementation is fresh Python. The lab reuses the shared tournament module
without editing it, and copies every opponent before building it.

## Evaluation functions

Movement uses `sum(weight * feature)`:

| Feature | Meaning |
|---|---|
| Pearl | Confirmed pearls eaten minus segments spent sprinting |
| Target | Discounted opportunity value of the first direction's BFS region |
| Danger | Estimated enemy reach at the final head location |
| Mobility | Capped reachable space plus immediate exits |
| Trap | Too little free space or no exit |
| Visit | Repeated occupation, discouraging loops |
| Frontier | Exploration reward |
| Sprint | Additional cost for committing extra steps |

The material correction was the largest measured improvement: three pearls in
three steps yield **one** net segment, not three. Sprinting can still be selected
to escape danger, but the evaluator no longer rewards consuming pearl supply
without corresponding growth.

A head attack is a terminal exchange: visible enemy length minus own length,
less a fixed unit-loss cost and a scarcity cost proportional to `1 / units`.
Visible length is only a lower bound. The last friendly dragon never deliberately
selects a trade. This is a heuristic, not a proof that a trade is winning.

Split value decreases with the fraction of the target population already alive,
subtracts the risk of staying at the same head position, and falls after the
production phase. Early versions' map-area cap was removed after replay evidence
showed a four-unit target could not compete with expanding opponents.

Most coefficients are in `weights.py`; some structural constants remain in
`main.py`. Weight-only experiments should change one coefficient or a clearly
stated group. Structural changes require a new version and regression tests.

## Roles: implemented and planned

Roles currently change with local state; they are not fixed birth assignments.

| Role | Current specialization | Next testable extension |
|---|---|---|
| Scout | Short dragons before round 90 value frontier targets more | Relay map discoveries and quantify information gained |
| Hunter | Default early/mid-game role; can trade and reproduce | Border control and fresh enemy sightings, priced by team strength |
| Gatherer | Long dragons or round 360 onward; higher trade cost, reduced splitting | Elect protected longest dragon; allocate pearl beds to it |

All roles currently use the same movement evaluator. Teammate sonar self-reports
are decoded and retained but **do not yet drive target allocation**. Sonar echoes
are parsed and ignored. There is no shared-memory shortcut, reliable map-wide
broadcast, full information map, minimax opponent model, or learned evaluator.
These are deliberate limitations of this first measured iteration, not completed
features. Public sonar messages are unauthenticated; the namespace/team bit only
filters accidental cross-lineage messages.

## Safety and search budget

Collision is checked before the tail vacates. Candidate simulation charges each
sprint step and rejects own-body/known-body collisions. Unknown portal partners
are blocked. Once paired, a portal can lead beyond current vision, so v06 counts
a pearl toward sprint affordability **only when observed this turn**. Stale
pearls remain useful as destinations, but cannot fund a guaranteed legal action.

The enemy reach model covers three steps and ignores detailed enemy length,
intent, and hidden bodies. Space evaluation holds other bodies stationary. These
approximations can miss ambushes, overestimate threats, and create traps. `MOVE N`
with indicator `trapped` is the fallback when no enumerated action survives; wall
and self deaths with that indicator are often consequences of an earlier trap,
not a mistaken edge parser.

Search is capped (180 target cells, 48 enqueued continuations, depth 3). The cap
on enqueues does not mean exactly 48 scored candidates. First-turn children search
only one movement step. V07 invalidates only affected graph entries when learning terrain, rather than
clearing every cached transition. The lab measures real judge CPU points; native timing
is not evidence of judge compatibility.

## Experimental contract

1. State a replay-grounded hypothesis and create a new version.
2. Run regression tests, then both side assignments on the quick suite.
3. Compare common opponent/map/side cases, with identical opponent source hashes
   and map hashes. Report regressions as well as wins.
4. Inspect population, split counts, final official lengths, death causes, and
   decision indicators around losses. Save all replays, including wins.
5. Verify sandbox health. A single illegal action or timeout deserves investigation.
6. Validate on holdout maps; once used for tuning they are no longer untouched
   holdouts. Preserve rejected versions and their explanations.

Repeated identical runs are deterministic checks, not independent samples.
Do not report significance or confidence intervals as if the side-swapped map
cases were independent random games. No seed control is exposed by this runner.
Never count failed matches as losses. The lab saves partial results and refuses
to overwrite an existing run directory; start a fresh directory after failures.

## Next hypotheses, ordered by evidence

1. **Length concentration:** big_empty losses finished 25–37 and 28–30 against
   Fry. Test an earlier growth transition for the largest locally known dragon,
   rather than stopping all reproduction simultaneously.
2. **Congestion and traps:** high late self/wall deaths, often with `trapped`
   indicators, suggest time-aware body release and teammate destination claims.
3. **Combat initiative:** Hydra wins most direct encounters. Compare survival,
   split timing, and attacks at equal resource levels before adding more search.
4. **Information value:** use the existing self reports for conservative pearl
   ownership, with freshness decay and no hard safety decisions based on sonar.
5. **Search budget:** add deeper tactical search only after profiling the expensive
   turns; six sampled judge games are not a proof over all reachable positions.

Official rules: https://game.battlecode.au/docs/structure
Movement: https://game.battlecode.au/docs/movement
Judge limits: https://game.battlecode.au/docs/timeouts
