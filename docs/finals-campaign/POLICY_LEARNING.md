# Policy learning design and original qualifier plan

> This preserves the staged action/sonar design drafted for the 6 October qualifier sprint. Its measured outcomes are recorded in [the experiment log](EXPERIMENT_LOG.md); the current campaign direction is in [the roadmap](ROADMAP.md). Proposed methods below are not evidence of a strength gain.

## Current recommendation: joint heads now; persistent options remain the strategic target

The earlier action-only and sonar-only trainers were useful ablations, but they were a poor default
for the intended policy: action choice changes movement and landing geometry, which changes the
value of the sonar packet. The new spatial prototype therefore uses one shared encoder, a
conditional action head and a sonar head conditioned on the selected action features; joint PPO
optimizes their summed log-probability against the same team return. Its first native run verifies
the pipeline only and says nothing about strength.

The strategic target remains a learned manager over persistent worker options. The measured
one-turn menu exposed MOVE/SPLIT commands under labels such as FORAGE, DISPERSE and BED, without a
persistent target, duration or learned termination rule. In the earlier staged data, the action
learner mostly reproduced the incumbent; the greedy sonar actor chose the incumbent packet on all
140,439 measured selectable rays; the action/sonar/combined development arms tied the fallback.
That evidence argues against promoting the staged formulation, not against testing the corrected
joint prototype or against RL generally. See the [experiment log](EXPERIMENT_LOG.md).

The promising RL question is narrower: **can a learned strategic manager choose among a few
meaningful, temporally extended worker goals while the proven C++ policy handles movement and
safety?** A real option has an initiation condition, an executor, persistent state and a clear
termination or interruption condition. This follows the temporal-abstraction framing of
[Option-Critic](https://arxiv.org/abs/1609.05140), but begin with hand-designed deterministic
executors and learn only the manager; do not ask PPO to discover both skills and when to use them.
The user's further constraints—sparse individual credit, early/mid/late specialization and replay
reuse—are addressed in the detailed [hybrid architecture proposal](HYBRID_RL_ARCHITECTURE.md),
including phase-aware shaping, centralized credit, offline IQL followed by online PPO, and an
expandable candidate-scoring interface.

### Proposed runtime

- Keep the current deterministic chassis for path choice, legal action masks, collision/queen
  protection, feeder/crown behavior, reserve limits and sonar. Safety can interrupt an option on
  any turn. Keep the queen policy fixed in the first trial.
- At option boundaries, a **shared, role-conditioned worker actor** chooses among a small masked
  menu such as `FORAGE_TO_KNOWN_RESOURCE`, `EXPLORE_FRONTIER` and `BED_TIMING`. An executor owns
  the target and continues until it is reached/consumed, becomes stale or unreachable, a threat
  requires interruption, or a bounded option timeout fires. Add production or coordinated
  defense only when replay diagnosis supports them. Preserve the chosen option, target and age in
  that dragon's own state; do not depend on cross-dragon private memory.
- The actor sees only the legal observation, that dragon's memory/inbox, role and candidate-option
  features. Use shared weights for workers. A small recurrent state is optional only if a measured
  memory gap remains after exposing existing target/age/role features. No learned radio actor in
  the first trial.
- Train with **centralized training and decentralized execution**: a team critic may read the
  full simulator state during training, while the exported actor remains local and legal. MAPPO
  results make PPO a reasonable baseline for cooperative agents, but those benchmark results do
  not predict performance in this game ([MAPPO paper](https://arxiv.org/abs/2103.01955)).
- Store semi-Markov option transitions with elapsed duration `k`; bootstrap and discount across an
  option using `gamma^k`, and retain the shared team reward. Handle births, agent deaths, option
  interruption and overlapping worker options explicitly. Normalize actor/critic loss by episode
  and team-round so large swarms and long options do not get accidental extra weight. Privileged
  critic features must never enter the policy export.

### Gate before training

First compare each deterministic option and a fixed option manager against the incumbent on
matched states, both seats and development maps. Confirm that options are genuinely persistent,
change the intended behavior, and improve their own diagnostic (for example, resource arrival or
safe expansion) without increasing deaths, faults or invalid actions. If this baseline cannot
show a mechanism-level benefit, stop before PPO.

Only then train the manager from complete episodes, with the incumbent and a diverse league of
frozen strong policies, fresh map families and randomized starts. Keep a map/opponent holdout out
of both option design and training. Compare the learned manager against the fixed manager and
deterministic ablations on that holdout; use the existing map-cluster confirmation gate, zero
unresolved judge faults, and a separate Grand Final unseen-map test. The short on-policy runs and
four-map screens already in the log are plumbing/development evidence, not enough to support this
new architecture. **This is a post-Qualifier proposal, not a change to the current submission.**

## Original short-sprint plan (superseded by measured results)

| Date | Deliverable | Exit condition |
|---|---|---|
| **6 Oct, first block** | Pin Bokuto 18 sources, engine/map hashes and environment; baseline on unseen maps; inspect 61 trial; replay economy failures | Reproducible results and specific failing states, not a new rating estimate alone |
| **6 Oct, second block** | New snapshots for corridor escape/production ordering and resource-target congestion; isolate changes before combining | Narrow screens completed; retain only supported changes, or keep original 18 |
| **6 Oct, third block** | Expose pure candidate-action and packet-template interfaces; instrument choices; parity in baseline mode; profile full rollout loop | Baseline mode reproduces incumbent commands, history and radio; data/export path works |
| **7 Oct** | Train action model with frozen incumbent sonar; evaluate; then train sonar model against a frozen retained action policy | Each stage evaluated separately against its matching fixed-policy control |
| **8 Oct** | Compare action-only, sonar-only and combined policies on fresh maps; confirm strongest; judge/export check and live trial if qualified | Evidence beats the fallback and supports the shipped combination; freeze that evening |
| **9 Oct** | Final artifact/source check, active-submission confirmation, upload/activation early | Verified active fallback or winner before 4:30 pm Adelaide |

The user believes the former 6/7 October diagnosis/fix work can fit into today. Treat that as a
target and timebox it; do not describe it as already done or skip its evidence. If candidate
generation/rollout integration is unfinished on 7 October, reduce the menu and retain fixed sonar
rather than creating another training stack. By 8 October noon, an uncompetitive learner leaves
the qualifier path; preserve it for work after qualification. One model can ship if only it helps.

## Policy structure: small learned choices over a working chassis

Deploy **two conditional policy heads over one shared actor encoder**, shared across all dragons
with private per-dragon state: the action head selects what to do, then the sonar head selects what
to transmit conditioned on the chosen option. A training-only critic is allowed; it is not a third
submitted decision model. The current encoder prototype uses a 128-value shared state and
candidate scorers, while the strategic option manager can follow once persistent option
transitions exist. A small GRU is a later addition only if sequence collection/export is ready and
measured improvement justifies it. No large teacher, distillation fleet, engine rewrite, or
distributed optimizer is required for this sprint.

### Action model

Initial bounded menu, with parameters chosen by deterministic legal-view proposal code:

| Option | Proposal | Scope |
|---|---|---|
| `BASELINE` | Exact incumbent decision | Always present; initial queen decision remains this |
| `FORAGE` | Route to one of a few observed/remembered pearls | All eligible workers |
| `BED` | Approach a known bed with an observed or inferred arrival timer | Only when valid evidence exists |
| `DISPERSE` | Explore an under-visited/reachable area or leave a crowded resource site | Worker economy |
| `ESCAPE` | Exit a corridor via a survivable route or tested escape split | Preserve emergency rescue |
| `PRODUCE` | Tested production split with headroom and parent/child space | Workers; preserve reserve logic |
| `INTERCEPT` | Reach a visible or fresh reported prey target | Optional expansion after economy options work |
| `FEED` | Follow existing queen/crown donor behaviour | Optional; preserve deliberate death semantics |

This is a proposed API, **not an existing callable menu**. Start with BASELINE plus FORAGE,
DISPERSE and ESCAPE; add BED/PRODUCE where existing code can expose them safely. Defer optional
INTERCEPT/FEED overrides until evidence supports them. Keep queen behaviour fixed initially.
Do not assume incumbent escape ordering is defective in every state: reproduce it before patching.

Each candidate contains option ID, concrete MOVE/SPLIT command, target, availability mask and
features: route progress, expected pearl timing, split size, space, known threat, paid sprint
cost, own length/role, target age, crowding and cap headroom. Bound alternatives per option.
Deduplicate identical commands and define stable ordering. One selection per turn initially;
do not add multi-round commitment before credit for variable-duration options is implemented.

Proposal generation must not mutate persistent policy state several times. In particular, do
not call current `Policy::decide()` repeatedly on live state to enumerate options. Separate sensing,
memory/role updates, pure proposals, selected-action commit and radio preparation. An initial
copy-and-propose bridge must still prove only selected state/history is committed.

Keep existing structural legality and emergency/queen behaviour. Mask candidates the deployment
guard would override before sampling. If an unexpected override happens, log the actual command
and exclude that choice from the ordinary on-policy actor loss. Do not train on a sampled command
that the wrapper silently replaced. Worker feeding/trading deaths are not globally forbidden.

### Sonar model

Learn a **packet-template scheduler**, not arbitrary 64-bit messages. Begin by selecting/suppressing
or rerouting incumbent-compatible packets. Existing families in `policy.hpp` include type 1
queen/crown beacon, 2 food/bed gossip, 4 prey, 5 portal pair, 6 density, and 3/7 inheritance/handoff.
Verify their current semantics before reuse. Protect required split handoff and queen/crown
packets initially. Include NO_SEND and BASELINE, and do not change receiver semantics in stage one.

Score a bounded list per ray or use four small masked output heads. Inputs include legal observation,
recent inbox/echo history, packet age/priority, candidate recipient geometry, selected action/landing,
and previous sends. Payload construction and decoding remain deterministic. New target-claim
packets are a separate later intervention requiring receiver logic, expiry and an ablation; merely
transmitting a new type has no coordination benefit if nobody reads it.

Official mechanics: at most four unsigned 64-bit packets, one per cardinal ray; casts occur after
movement if the sender lives. Rays wrap, traverse portals and stop at kelp or the first body.
Sending into the sender's body redirects through the tail. Receipt is at the recipient's next
turn, so higher/lower IDs affect round delay. Echoes arrive on the sender's next turn, are aggregate
counts, and include self contacts. Sender/team metadata is absent and enemies can receive packets.
Use post-action geometry; a dying feeder sends nothing.
[Official sonar rules](https://game.battlecode.au/docs/sonar).

### Staged training and ablations

1. Instrument the deterministic incumbent and warm-start the action selector on its own chosen
   candidates. These labels come from our instrumented policy, not invented option labels for
   opponents' replay moves. Public replays are useful for diagnostics and supported auxiliary labels.
2. Train action choices with sonar fixed; use frozen incumbent/keeper opponents plus past snapshots.
3. Freeze the retained action model; warm-start and train sonar choices with the same team objective.
4. Evaluate four arms: deterministic chassis, action-only, sonar-only, both. Limited alternating
   fine-tuning is optional after those measurements; simultaneous learning is not the first run.

Baseline cloning/parity establishes integration, not strength. Sonar value needs receiver-dependent
rollouts. Counts of delivered packets, ally-head echoes or repeated messages are diagnostics, not
reward bonuses or promotion criteria. Compare the learned scheduler to both fixed incumbent sonar
and a controlled optional-packet suppression arm. Train/evaluate against policies that use sonar.

## Observation, reward and credit contract

Actors use protocol observations, actual per-dragon memory, own actions and received packets only.
Privileged engine state can label rewards/train a critic but never enters submitted actor inputs.
Do not use opponent/team identity, map names, stored atlases, future events or replay outcomes as
actor features. Relative locations from lawful memory are allowed. A 17x17 remembered crop does
not provide fresh 17x17 vision. Use the existing audited 7x7 encoder first.

Use team terminal result (+1/-1/0) plus **potential differences**:
`r_t = result_t + alpha * (gamma * Phi(s_next, round_next) - Phi(s_t, round_t))`.
The current collector implements `heartbreaker-potential-v1` with gamma 0.997 and fixed alpha
0.2. It decodes completed official replays for training-only state labels; replay state is never
passed to the actor. The five documented Heartbreaker terms are combined by a normalized weighted
sum, which explicitly bounds Phi to [-1, 1]. A terminal potential of zero is used after the final
transition for both elimination and round limit, so discounted shaping telescopes to
`-alpha * Phi(start_state)`. This keeps the terminal match result as the objective while giving
intermediate choices a bounded, phase-aware signal. Do not add Phi itself each turn or resurrect
large per-dragon death penalties. Aggregate queen survival/material into team advantage; useful
deliberate sacrifices must remain possible.

Maintain a team-round reward timeline and per-dragon decision trajectories. Never run GAE across
the flattened stream of different dragons as though it were one dragon. Handle births, own death,
team termination and rollout truncation explicitly; own death resets private recurrent state but
does not mean the team's episode ended. Retain delayed team credit for the last decisions of a
donor. Use actual elapsed rounds in discount/bootstrap calculations. Normalize losses so swarm
size and numbers of sonar sends do not become accidental reward multipliers.

The original user-supplied Heartbreaker potential, now implemented with the normalized weighted
sum and scale above, is:

```text
Q = live queen length (0 if dead); M = longest living dragon; Z = total living length
q = queen-alive indicator; C = count of distinct head-visited tiles per team
D(a,b) = clip(2*(a-b)/(a+b), -2, 2), or 0 if a+b=0
g(a,b) = 1/max(a,b) if both positive; 1 if both zero; 0 if exactly one zero
WIN   = tanh(D(Q_us,Q_them) + 0.4*g(Q_us,Q_them) *
        tanh(D(M_us,M_them) + 0.4*g(M_us,M_them)*tanh(D(Z_us,Z_them))))
LEN   = tanh(D(Z_us,Z_them))
QUEEN = q_us - q_them
KILL  = exp(-Z_them/15) - exp(-Z_us/15)
EXP   = tanh(0.005*(C_us-C_them))
s = round/500; K = max(C_us,C_them)/map_area
weights: WIN=1.5*s*s; LEN=1; QUEEN=clip((500-round)/125,0,1)
         KILL=0.8*(1-s*s*s); EXP=(1-K)*clip((75-round)/50,0,1)
Phi = weighted sum of these five terms
```

The weighted sum is divided by the sum of its phase-specific weights before use, rather than
clipped after summation. This preserves symmetry and the [-1, 1] bound while avoiding flat
gradients caused by post-hoc clipping. The exact implementation is pinned by `SHAPING_NAME`,
`SHAPING_ALPHA`, gamma and tests in `tools/finals/collect.py` and `tests/test_finals_shaping.py`.
The central critic is optional for the initial working loop; correct credit and deployment parity
are mandatory.

## Evaluation and implementation entry points

- C++ integration: `bots/bokuto-18-queenfeed/main.cpp` currently does helper update, `World::sense`,
  branch update, reserve adjustment, `Policy::decide`, `Guard::apply`, selected-action radio prep,
  movement/history commit and radio send. Inspect `policy.hpp`, `world.hpp`, `bokuto.hpp`, `params.hpp`.
- Encoder twins: `tools/learn/encode.py`, `cpp/learn_encode.hpp`, `cpp/learn_helper.hpp`; replay
  reconstruction: `rebuild.py`, `oracle.py`, `block.py`. Server replay bed timers are redacted and
  seats can swap; use oracle/template reconstruction when needed, never assume team A queen = 0.
- Existing selectors/trainers: `tools/growth_rl/ppo.py`, `policy.py`, `panel_gate.py`,
  `tools/learn/ppo.py`. Reuse verified collection/export patterns; these do not implement this menu.
- `tools/asahi/panel.py` has pool/gen/qk/qk2/h2h machinery, but h2h is pinned to **Kenma 03**;
  **gen-h2h versus Bokuto 18 is not implemented**. Do not pass a made-up panel name and assume
  it has the intended opponents. Validate/extend fixture generation or use an explicit comparison config.
- `tools/benchmarking/tournament.py` supports bounded dry runs, both seats and sandbox probes, but
  has **no seed argument** in its inspected CLI. Shared-seed promotion fixtures need a harness/config
  that records seeds explicitly; do not use an unseeded screen as the final paired comparison.
- `tools/compare_bot.py --config ... --dry-run` can validate an explicit comparison roster. Inspect
  the config schema before constructing it. Existing default `comparison.toml` is an old control pool.

Suggested first schedule inspection (no games run):

```sh
python3 tools/benchmarking/tournament.py \
  --bots bokuto-18-queenfeed kenma-03-pocket-queen \
  --maps new/mc26_crossroads new/mc26_portal_quartet \
  --jobs 1 --dry-run
```

For final selection, pin a development map set and separate **fresh generated confirmation maps**.
The repository's 29 gen maps and transposed twins are useful development fixtures but have already
been inspected/tuned in historical experiments; they are not pristine holdouts. Start with a small
screen; expand surviving candidates to at least 29 maps x 2 seats x 3 seeds = **174 direct games**
versus the retained baseline, plus keeper/strong-control comparisons. Save source/map/engine hashes,
exact seats and seeds, errors and results. Never count runner failures as strategic losses.

Selection: actual win score versus fallback first, queen survival and carried material/death causes
second. Use paired map clusters retaining seats/seeds; report 90% intervals and adaptive-selection
limits. Require a positive confirmation point estimate with lower interval above zero before
claiming a supported improvement, and no unresolved judge faults. A screen is not promotion.
For sibling variants use matched opponent fixtures too; a head-to-head alone may hide cyclic strength.
Live trials are useful corroboration, measured with one common rating anchor and series clusters.
Do not use the legacy growth-only gate as the qualifier decision.

Test contracts: default-selector parity, candidate legality/side-effect isolation, emergency override
logging, packet round-trip/post-action casts, reward boundaries and trajectory credit, recurrent
export (if used), and the final judge CPU/memory/ZIP limits. Run narrow relevant checks before broad
tests; ordinary docs changes do not need strategy tournaments. Bound all game batches and default to
one worker until reproducibility/resource use is known. Profile collection + encoding + inference +
optimization end to end before changing hardware. Use the friend's PC for independent seeded fixtures.

## External information and scope limits

Heartbreaker PPO/LSTMs/17x17 architecture and supplied reward are **user-provided intelligence**.
Cutlery/Vibing++ rented-H100 RL is an unverified hypothesis. Judge behaviour is measurable regardless
of architecture. Loong publishes useful engine/tooling code, but its quoted fast-training results
are pre-Queen and its released complete-match CUDA reference omits the device-only trainer interface.
Do not spend this sprint porting a simulator based on an assumed turnkey trainer.
[Loong learning](https://over-yonder.tech/games/loong/learning-to-play/),
[engine reference](https://over-yonder.tech/games/loong/an-engine-on-the-gpu/),
[rules caveat](https://over-yonder.tech/games/loong/slay-the-queen/).

Copy measured bots into new versioned directories. Keep generated models/replays/results under
`build/` or `/tmp`; follow `docs/artifact-policy.md`. Track small manifests/results summaries,
not large payloads or credentials. No server upload/activation or rental happened in this handoff.
