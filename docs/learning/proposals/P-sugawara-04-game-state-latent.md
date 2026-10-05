# P-8 — Scoping: a game-state latent that selects behaviour sets (state filter, recurrent core, or phase belief)

Sugawara (council, mechanism), 5 Oct 2026 01:45Z. Requested by D-067 §E.5, due 03:00Z. **Scoping card.** It fixes an
order of tests and their falsifiers. It approves no fit and no bot by itself.

## 1. Claim, rung and mechanism

- **Rung:** R3/R4 offline (the split, child size, cull and sprint heads, and the trajectory block). It also binds P-7
  (whether the network has a recurrent core).
- **Parent:** A1-400 (the selectable arm on the HB-1 vector), plus the encoder v2 trajectory block (D-067 §E.7) once it
  exists. **The one switch tested is the latent, against the trajectory block, not against A1.**
- **Mechanism.** A game-state latent is a summary of the observation history that the current turn lacks: "we are
  ahead / behind / contested / starved / late-and-safe". Options (a)–(c) differ only in how the summary is computed:
  - (a) **State filter (HMM):** K discrete states, with emissions over what one process legally sees each turn: round,
    unit count and its change, own length and its change, contact (an enemy head or body in the 7×7), the echo kind
    counts, and the message count. The posterior is computed by the **forward recursion only** and fed to the heads as
    K inputs.
  - (b) **Recurrent core:** a GRU (≤ 64 units) between the encoder and the heads of the network arm (A10b), trained by
    truncated backpropagation on each process's sequence.
  - (c) **Phase belief from measured state:** a small fixed function, e.g. a logistic phase score from round, the
    unit-count trajectory and own-length trajectory, used as an input *and* as the gate of a 2–3-expert blend of
    heads. Chess's tapered evaluation interpolates the midgame and endgame weights by a material-based phase.
    D-067's T1 (three hard phase models) is already the hard-gated form of (c).
- **The decisive mechanism point:** a forward-filter posterior is a deterministic function of the process's own
  observation history. A tree model given good summaries of that history (counts, deltas over 20 and 100 rounds,
  rounds since an event) can represent nearly any such function. **So (a) adds information only if the v2 summaries
  miss something.** The earned gain must therefore be measured against "A1 + v2 block", not against A1. Otherwise
  the card would credit the latent with what the summaries already carry. This is the standard frame-stacking versus
  recurrence comparison (below).

### Legality (per-process memory)

- Every input is in the dragon's own IO block or in its own earlier blocks. The round and the unit count are given;
  echoes and messages arrive at turn start.
- **A new process starts with an empty history.** After a split, the child is a fresh process. Its filter starts
  from the prior over states, or from a state passed by sonar, which costs a message. Training sequences must restart
  at each process birth exactly as the engine does. **Data must state which half of a split keeps the old process.**
  If training lets the child inherit the parent's history, that is train/deploy skew.
- **No smoothing.** Forward–backward or Viterbi over a whole game uses future turns, which is illegal at play and is
  leakage in evaluation. Only the filtered posterior p(z_t | o_1..t) may be computed, in training as at play.
- **No map identity** (`_common.md` l.21): the emissions take no W, H or map id. Map size enters only through
  get_map_size-derived structure, as encoder v1 already does.

## 1b. Precedent

| precedent | method | result | closeness / departure | confidence |
|---|---|---|---|---|
| Tapered evaluation (Fruit, Stockfish, PeSTO; chessprogramming.org "Tapered Eval") | two weight sets blended by a material phase | standard in strong engines | = option (c); the phase there is fully observed, ours is partly | high |
| OpenAI Five (Berner et al. 2019, arXiv 1912.06680) | single-layer 4,096-unit LSTM core, self-play PPO | beat world champions | partial observability as ours; budget ~10⁵× ours | high |
| AlphaStar (Vinyals et al., Nature 2019) | deep LSTM core; policy conditioned on a statistic z (build order, cumulative stats) sampled from human games | Grandmaster | **z is literally "a latent that selects a behaviour set"**, but it is chosen at game start, not inferred | high |
| FTW, Capture the Flag (Jaderberg et al., Science 2019) | two-timescale recurrent core with a latent variable | human-level | slow/fast latent = behaviour mode; RL-only | high |
| DRQN (Hausknecht & Stone 2015) | LSTM vs frame stacking in DQN | about equal on fully observed Atari; better when frames flicker | **the frame-stacking ≈ summaries control used here** | high |
| Heartbreaker authors (D-059) | LSTM layers in their direction model | no help | same game, same head | as reported |
| HB-1 (30 Sep) | memory features in the direction clone | ≤ 0.2 pts | same head | own data |
| Shenzhen H-SZ68 (01:19Z) | exact-7×7-state lookup | 0.802 on recurring states | ~1 move in 5 is not a function of the view; an upper bound on what history *plus noise* explains | own data, sim |
| HMM in games | Dereszynski et al. (AIIDE 2011) fit an HMM over StarCraft build states for *prediction* | — | **I know of no HMM controlling a game agent**, as the Chair said; recall medium, check before citing | medium |

Reading: the strong precedents for a learned latent are recurrent cores trained by RL at large scale. The cheap, well
supported controls are summaries/frame stacks and phase blending. Behaviour cloning on 10 teachers gives a
recurrent core little to learn that summaries do not, which matches Heartbreaker's and HB-1's null results on the
direction head.

## 2. Expected sign and size

- **Direction head:** a latent over A1 + v2 gains < 0.003 (pooled). Possibly ≥ 0.005 only in the r ≥ 250 bucket.
- **Split / child size / cull / sprint heads (R3, D-067 §E.6):** this is where a mode variable should matter: a top
  team culls 18 times per 1,000 dragon-turns, our total length at r499 is 85 against 97–141, and our queen survives in
  1 % of games against 24–56 %. Expect the v2 block to carry most of it. The latent's own increment is uncertain.
- Side effects: none offline. At play, (a) and (c) cost < 1 k flops a turn. (b) GRU-64 costs ~65 k MACs a turn.
  Points to be measured; the A10-shape forward was 22–40 µs.

## 3. Falsifiers and stop rule

Metrics: accuracy for the direction head; **AUC and log-loss for the rare-event heads** (cull ~2 %, split, sprint),
where accuracy is uninformative (always "no" scores ~0.98 on cull). Paired series bootstrap, 1,000 × seed 7, 5/95, on
the R2 development split; per bucket = the encoder's phase bucket (< 25, < 100, < 250, < 400, ≥ 400).

- **S0 (information test, after D-067 §E.6 tables exist):** "A1 + v2" vs A1, per head. If no head gains ≥ 0.005
  (accuracy, or AUC on rare heads) in any bucket with ≥ 5,000 rows, **stop: history adds nothing measurable, and
  P-8 closes.** P-7's network stays feed-forward, with v2 as inputs.
- **S1 (the latent, only if S0 shows history value):** option (a) with K ∈ {3, 4, 6}, chosen by BIC on training
  folds only, posterior features into the same head. **Pass:** gain ≥ 0.005 over "A1 + v2" on at least one head ×
  bucket, with a paired 5th percentile > 0 after Holm correction over the 4 heads (buckets descriptive). **Falsified**
  otherwise.
- **S2 (recurrent core, network arm only, only if S1 passes or the Chair's network arm is selected for P-7):**
  GRU-64 vs the same network with v2 inputs, same rows and epochs. Same pass rule.
- Option (c) is run alongside S1 as T1's soft-gated form, at no extra cost if T1 runs.
- Stop rule: each stage is run once; no K, bucket or head is added after its results are seen.

## 4. Test plan

- Data: teachers_v1 sequences on the R2 development split (`docs/learning/splits/`); held-out maps and the frozen
  cohort are untouched. The HMM is fitted per training fold and filtered on that fold's held-out rows.
- Sequences are per process, with births restarting the filter (see Legality). A parity check that the in-bot C++
  forward recursion matches the Python one to 1e-6 is needed before any play use.
- Play: none in this card. A head that passes goes to R3's own card.

## 5. Cost

- S0: the v2 block (Kageyama, already ordered) plus one refit per head, about as much as A1 per head (~20 min each,
  ~3 GB).
- S1: HMM fit on ~3.4 M rows, diagonal Gaussian / Poisson emissions, K ≤ 6, ≤ 50 EM iterations: minutes. Check
  that `hmmlearn` is on the Mac or write the 60-line numpy forward-backward; the training E-step may smooth, but
  features for the heads must be *filtered*.
- S2: GRU on A10b's rows, truncated BPTT at 32 steps: about 2–3× A10b's epoch time. Only one heavy job at a time.
- At play: (a) and (c) are negligible (state K floats). (b) needs per-process hidden state (64 floats) and ~65 k MACs.

## 6. RL translation

- Observation: the IO block plus the process's own history, summarised (v2), filtered (a), or recurrent (b).
- Action: unchanged (direction, split, child size, cull, sprint).
- Value: P-6's value model takes the same latent. That is where a phase variable is most expected to pay
  (Shenzhen H-SZ59: the outcome signal is absent at r100 and present at r300).
- Demonstration: teachers_v1. The latent describes *game* state as seen by the process, not the teacher's intent.
  An HMM fitted to behaviour (actions as emissions) would encode teacher style; that is A7's job, not this card's.
  **Emissions exclude the actions.**

## 7. Numeric predictions

| event | P |
|---|---|
| S0: "A1 + v2" gains ≥ 0.005 on some head × bucket (≥ 5,000 rows) | **0.60** |
| S0: same on the direction head (any bucket) | 0.25 |
| S1 passes (latent over A1 + v2, Holm), given S0 passed | **0.20** |
| S2 passes (GRU over v2-input network), if run | 0.20 |
| A latent from this card is in a live bot within the season | 0.07 |

Expected effect if S1 passes: +0.005–0.01 AUC on the cull and split heads in buckets ≥ 250; ~0 on direction.

Dissent (my own): the strongest version of the lead's idea is AlphaStar's z, a **chosen** behaviour mode rather
than an inferred one: e.g. "feeder" vs "keeper" (D-067 §E.6 styles) picked per game or per phase by a bandit over
live results. That needs R3's heads to exist first and is out of this card's scope. I note it so that a null S1 is
not read as "modes don't matter".
