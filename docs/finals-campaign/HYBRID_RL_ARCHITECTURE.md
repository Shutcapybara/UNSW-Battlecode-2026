# Hybrid hierarchical RL architecture

**Status: architecture proposal; encoder/PPO harness prototype implemented, strength unmeasured.**
This design responds to three constraints:
terminal outcomes give weak credit to individual choices; strategy needs to change across the
500-round horizon; and full self-play is expensive while the site has a large replay archive.
The current experiment record says the one-turn action/sonar PPO did not beat the fallback. Do not
read the new encoder or its smoke test as evidence that a replacement is ready.

## Runtime policy

Use one shared observation encoder and per-dragon persistent state, then factor the policy into an
option head and a conditional sonar head:

```text
legal local observation + inbox + per-dragon memory + phase context
                              │
                  shared encoder (small GRU optional)
                       ┌──────┴────────┐
                option scorer     value features
                       │
      persistent intent + target/parameters
                       │
       deterministic C++ executor + safety guard
                       │
              selected move/landing
                       │
       conditional packet-template scorer
                       │
                 command + radio
```

This is one policy with two conditionally ordered heads, not two unrelated actors. Sonar is chosen
after the option executor determines the actual move and post-move geometry. Start with shared
weights across workers and keep queen/crown safety, required handoffs, feeder behavior and sonar
receiver semantics deterministic. Use a small recurrent state only if replay tests show that the
existing explicit memory and inbox do not capture the needed history.

### Concrete encoder candidate

The proposal above did not pin down encoder layers. For a separate encoder experiment, retain the
audited encoder-v1 contract unchanged: split its 1,193 values into the egocentric grid
`G[7,7,23]` and scalar vector `s[66]`. Keep integer feature production and C++/Python parity at
the boundary; normalization belongs inside the model. This lets the representation change without
silently changing what replay rows mean.

```text
G[7,7,23] ── same 3x3 conv 23→32, ReLU ── same 3x3 conv 32→32, ReLU ── flatten ── linear 1568→96 ─┐
                                                                                         ├─ concat
s[66] ── named scaling/clipping ── linear 66→64, ReLU ── linear 64→64, ReLU ─────────────┤
phase bucket + queen context ── two 8-value embeddings ───────────────────────────────────┘
                                     ── linear to 128, ReLU ── shared state z[128]
```

The grid branch gives local wall, portal, body, head and food patterns a spatial inductive bias;
the final flatten-and-project preserves each cell's forward/side/distance position in the already
rotated egocentric frame. The scalar branch keeps counts, ages, distances, inbox/echo statistics,
and round context on their existing named scales. Phase and queen embeddings condition the shared
state; current worker-role flags remain in candidate features. Do not create three independent
full encoders. The actor may use only observable or received phase/role context. A full team
tiebreak summary belongs in a versioned message if workers need it; it must not leak from the
training critic.

Start feed-forward. Encoder v1 already carries round, rounds remaining, a five-bucket phase,
queen visibility/age, local state, inbox/echo data and explicit recent-action features. Persistent
options add intent across turns. Add a per-dragon GRU after a history ablation demonstrates a
specific missing dependency; do not make recurrence a prerequisite for the first test.

The action scorer consumes `z[128]`, a learned 16-value semantic option embedding and that
candidate's parameters (projected to 32 values), then scores the concatenation through a 128-unit
layer. The sonar scorer consumes its packet-template embedding and parameters, the shared state,
and a learned projection of the selected action's full 32-value feature vector. This lets the
packet policy condition on move and landing intent rather than only the action category. Joint PPO
uses one dragon-turn likelihood: the selected action log-probability plus the four sonar
log-probabilities conditioned on that action, all against the same terminal team return. The
submitted actor remains local. The executable prototype is [`spatial_model.py`](../../tools/finals/spatial_model.py),
with resumable joint PPO and a fixed-panel monitor in [`train_spatial.py`](../../tools/finals/train_spatial.py).
It currently uses the existing six action kinds and three packet menu kinds; it does not yet
implement persistent multi-round options, early/mid/late expert heads, potential shaping, offline
IQL, or the centralized full-team critic. Its value head shares the encoder and sees only the same
local observation as the actor. Those are later stages, not silently claimed as complete here.

Compare this two-stream encoder against the current flat 32-unit scorer on matched training and
held-out map panels before adopting it. These dimensions are a starting hypothesis, not measured
choices or a claim of stronger play.

This encoder swap is not required to add option types. First keep the current flat trunk when
extending the candidate schema, so old option scores can be preserved; evaluate the two-stream
encoder as a separate representation change. A new trunk needs distillation or other warm-start
evidence and must not be assumed to reproduce an old checkpoint exactly.

### State and phase specialization

Keep one shared trunk, with a phase-conditioned option scorer and small early/mid/late output
heads or a soft gate over those heads. Inputs should include round and rounds remaining, the
estimated terminal tiebreak position, queen alive/length, longest living dragon, total team
length, unit count/cap, known food and bed opportunities, local threat, and role. Do not hard-code
round cutoffs as the only phase signal: a weak position near round 450 can require a different
plan from a strong position at the same round.

At inference the actor must use only legal local observations, its own memory and received
messages. A training-only team critic may see the full state; it must not leak into the submitted
actor. If workers need a shared endgame target, communicate a compact phase/asset intent through a
versioned sonar template, or use a deterministic assignment rule. Do not assume each dragon can
read another process's private state.

The option pool should describe goals, not just the next compass move. A deterministic proposer
can instantiate candidates such as:

- `EXPLORE(direction/sector)` or `EXPLORE_PORTAL(portal)`;
- `HARVEST(resource/region)` and `BED_TIMING(bed)`;
- `INTERCEPT(enemy)` when the target is visible or recently reported;
- `FEED_ASSET(queen/crown)` with deterministic donor assignment and safety checks;
- `PRODUCE_SAFE` when the queen, unit cap and nearby space permit it.

The executor owns the target and continues until it is reached, consumed, stale or unreachable,
an emergency interrupts it, or a bounded timeout fires. Movement, sprint choice, collision checks
and path recovery remain in the tested low-level controller. In the endgame, the manager should
shift from broad growth toward the actual win condition: elimination wins immediately; at the
round limit the comparison is queen length, then longest living dragon, then total length, in
that order ([official scoring rules](https://game.battlecode.au/docs/structure)). Thus a
`FEED_ASSET` option should compare queen and crown needs against the current tiebreak margin, not
blindly feed one unit in every state.

The action actor should score a variable list of candidate records rather than use a fixed-size
softmax output layer:

```text
score(candidate) = scorer(shared_state, option_type_embedding, candidate_parameters)
```

Each record has a stable semantic ID, availability mask, parameters, features, executor version,
initiation condition and termination rule. The sonar head uses the same pattern over legal packet
templates, conditioned on the chosen option, actual move/landing, phase and inbox/echo state.
Protect mandatory packets and `NO_SEND`; add a packet type only with its receiver behavior and
protocol version.

## Dense reward and credit

Keep the terminal team result as the objective. The current collector adds dense learning signal
through the implemented phase-aware Heartbreaker potential over the terminal score ingredients
and progress toward them:

```text
r_t = terminal_result_t + gamma * Phi(s_{t+1}) - Phi(s_t)
```

Include round/phase inside the potential and set terminal potential to zero. The implemented
Heartbreaker terms use queen/longest/total-length advantage, queen survival, material advantage,
and distinct head-visited tiles. Phase weights fade exploration and survival signals while raising
the queen/longest/total tiebreak proxy. The five terms are combined by a normalized weighted sum,
so Phi stays in [-1, 1]; alpha is fixed at 0.2. Verify the scale and discounted telescoping before
training. Do not pay a raw per-turn bonus for eating, feeding, sending sonar or keeping a dragon
alive: those shortcuts can conflict with the match result. Potential differences are a standard
policy-preserving shaping form under the stated MDP assumptions
([Ng, Harada and Russell](https://ai.stanford.edu/~ang/papers/shaping-icml99.pdf)).

For individual action credit, train a centralized team value critic and an agent-specific
advantage at each option choice. First establish a MAPPO-style centralized-training/decentralized-
execution baseline. If shared team credit still obscures donor, scout and attacker contributions,
test a counterfactual baseline that scores the selected option against that same dragon's other
legal options while holding the rest of the sampled team behavior fixed; COMA is a primary
reference for this credit-assignment design ([paper](https://arxiv.org/abs/1705.08926)). Keep
births, own death, team termination, option interruption and overlapping options explicit. Do not
flatten all dragon decisions into one fictitious trajectory.

For an option lasting `k` rounds, aggregate the per-round shaped rewards over those `k` rounds
and bootstrap with `gamma^k`; do not treat every option as a one-round transition. This is needed
for consistent credit across short combat options and longer exploration/feed goals.

## Offline replay plus online self-play

Use the site archive for offline learning and self-play for correcting the policy on its own
state distribution. They need separate update rules:

1. **Build a replay dataset.** Decode both teams' actions, lawful observations, selected option
   candidates where reconstructable, game/version, map family, round, role, outcome and transition
   timing. Keep wins, losses and draws; stratify by phase, map family and behavior cohort. Exclude
   incompatible rule eras and audit observation/action reconstruction before training.
2. **Offline warm start.** Fit the value/phase representation and candidate policy with an
   in-sample conservative method such as IQL. IQL learns from a fixed dataset without querying
   values for unseen actions and extracts a policy with advantage-weighted behavior cloning; this
   is safer than unconstrained Q-learning on the mixed-quality, mixed-policy archive
   ([IQL paper](https://arxiv.org/abs/2110.06169)). Use only actions whose outcomes and candidate
   mapping can be reconstructed. Old replays cannot teach the outcome of a newly invented option
   that was never executed.
3. **Online correction.** Fine-tune with MAPPO/PPO-style updates on fresh full games against a
   versioned league: incumbent, prior snapshots, and distinct strong controls. Use a centralized
   critic, fresh on-policy actor batches, phase-balanced sampling, and replay data for value or
   auxiliary updates plus a bounded behavior-cloning anchor. Do not treat old replay actions as
   on-policy PPO samples. If behavior probabilities are absent, exact importance correction is
   unavailable; IQL is the offline stage, not a way to disguise stale data as fresh rollouts.
4. **Measure each source separately.** Report replay-only, self-play-only and combined ablations.
   Use map/opponent/time clusters and a held-out unseen-map set untouched by option design,
   offline fitting and self-play selection. Keep replay records tied to the rules version and
   policy behavior cohort when identifiable.

MAPPO is a reasonable cooperative on-policy baseline in published multi-agent testbeds, and IQL
   demonstrates offline initialization followed by online fine-tuning; neither paper predicts
   performance in this game ([MAPPO](https://arxiv.org/abs/2103.01955),
[IQL](https://arxiv.org/abs/2110.06169)).

## Adding actions without restarting

**Yes, if the model is candidate-scored and its schema is versioned.** A flat output vector whose
index means “north/portal/pearl/attack” must resize and remap when actions change. The current
`Scorer` already emits one score per supplied candidate, so the number of candidate rows can grow
without resizing its output layer. However, Bokuto 64/65 encode the six action kinds as the first
six entries of a fixed 32-value candidate vector; simply extending the enum would overlap the
existing feature columns. The candidate *count* is extensible today; the action *type schema* is
not. See [`options.hpp`](../../bots/bokuto-64-option-chassis/options.hpp) and
[`model.py`](../../tools/finals/model.py).

Separate type from parameters: use a learned embedding per semantic option ID plus the existing
shared candidate feature scorer. The old scorer can be warm-started without changing the old
options' scores: copy its first six candidate-weight columns into the six option embeddings and
its remaining columns into the parameter scorer. Initialize a new option from the closest parent
embedding (for example, `EXPLORE_PORTAL` from `EXPLORE`) and give it a low prior probability until
it has coverage. This preserves the old decision function for existing options while allowing
the new embedding and executor to train.

For a new action, add its semantic ID, feature schema, proposer, executor, initiation/termination
and legality tests; retain the incumbent candidate and freeze the proven trunk during the first
warm-up. Then train on new option-level episodes and unfreeze shared weights only if the new action
has adequate coverage. Save an action-schema version in every replay, checkpoint and export. If the
new action changes observations or receiver semantics, migrate and revalidate affected data rather
than silently interpreting old checkpoints.

Warm-starting avoids a full restart, but does not give a new action learned value for free. It needs
real outcomes, valid counterfactual/simulator data, or a deterministic executor whose value is
measured. New sonar templates likewise need receiver implementation and rollout evidence; adding
a sender token alone does not make a useful team action.

## Gates before implementation

1. Prove replay-to-observation/action parity and classify which archive games are usable.
2. Test deterministic persistent options and endgame feeding against the incumbent before RL.
3. Verify shaped rewards against the terminal score on hand-constructed games and full replays.
4. Train the offline warm start; report phase- and role-stratified validation, not training loss.
5. Fine-tune online and require improvement over both the incumbent and fixed-option ablations on
   untouched map/opponent clusters, zero unresolved faults, and the existing promotion interval.

Until these gates pass, keep this as research architecture. It does not change the qualifier
fallback or authorize a new submission.
