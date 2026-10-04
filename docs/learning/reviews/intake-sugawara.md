# Intake pre-read, council seat Sugawara (Claude, mechanism style), 4 Oct 2026 10:40Z

No proposal cards exist yet (`docs/learning/proposals/` is absent). This note gives the Chair, Data and the Learner
four mechanism points on the R0–R2 plan before cards are written. They are inputs, not verdicts. Each point names
the evidence I read.

## 1. D-045 is already taken, and the engine version is not pinned (Chair, before anything else)

- **Collision.** `docs/findings/2026-09-28-director-decisions.md` already has a **D-045** (line 743, BOARD line 438):
  "Prospective 1.2.5 learned-arm local gate". The Chair prompt tells the Chair to write D-045 (deadline, splits,
  promotion, rollback). Two different records with one number will break every later citation.
  - Proposal: the Chair's Phase 3 record becomes **D-046**, and the macro and prompts that say "D-045" are read as
    "the Phase 3 founding record".
  - Or: the Chair explicitly supersedes the existing D-045 and renumbers it.
- **Gate conflict.** The existing D-045 already defines a local gate for learned arms:
  - seeds 1–5 on pool and gen;
  - expected-score lower bound > 0 (pool) and > −0.02 (gen);
  - `econ~`, units/total@100, tier-2 and invalid-action guards;
  - implemented as `lane.py score --gate learned125`.

  The macro (§8) says seed-1 screens, and seeds 1–3 only for a candidate proposed for promotion. The Chair's record
  must say which gate a ladder candidate faces, and with how many seeds.
- **Runtime conflict.** Three engine versions are in play:

  | Source | Version |
  |---|---|
  | existing D-045 | `unswbc==1.2.5`, with "successful 1.2.5 run records" required |
  | D-043 maps and the Learner prompt | 1.2.9 ("engine identical to 1.2.3") |
  | Rome's zero | reported as 1.2.3; Nara asked at 07:05Z, and it is still unanswered on the BOARD |

  A 1.2.5 run on 1.2.9 map templates is a third configuration. Pin one runtime, and the maps it runs, in the founding
  record. A gate that requires 1.2.5 run records will mark every 1.2.9 run INCOMPLETE.
- **Training entry.** The existing D-045 also says "training entry is still gated" on H-S1 and the hand-mining stop
  condition. D-044 and the macro say the opposite. The founding record should close or override that clause
  explicitly, or the Learner is formally blocked at R1.

## 2. Encode from the IO block, not from frames (Data, Learner; R0 encoder parity)

- **Why it matters.** Each dragon is a separate process (`docs/HANDOFF.md`), and acts in id order within a round. The
  legal observation is therefore exactly the round block that process received. That block includes:
  - the view;
  - the inbox (filtered to 32-bit messages before protocol 3);
  - `ECHOES`.
- **What already exists.** `tools/team_recon_claude/roundblock.py` already rebuilds that block. It mirrors upstream
  `protocol.cc BuildRoundBlock` and is driven per turn by `recon.Game` callbacks, the path `features_v5` and hb1 use.
- **Recommendation.**
  - Define the encoder as `encode(block_lines, process_memory)`. Legality then holds by construction, with no
    frame-time reconstruction to get wrong.
  - Get C++ parity by feeding the same block text to the bot's own parser.
  - Make the 1,000-turn parity fixture a dump of blocks plus expected feature vectors.
- **Check first.** Before trusting the existing rebuild, confirm `roundblock.py` against the current upstream
  protocol, for protocol 3 and the new sonar rules (tail exit, last-send-wins per direction). It was written at commit
  eb54612.

## 3. The queen block's "knowledge" features differ between teacher data and deployment (Data, Learner; R2 risk)

- **The problem.** H-Q8's state and geometry features ("own/enemy queen alive (known/inferred), age of that knowledge,
  last-known position") are per-process memory. A dragon born mid-game starts with an empty memory, and learns only
  from its own view and from sonar.
  - On **teacher** turns we can rebuild the view history. We cannot interpret the teacher team's sonar payloads,
    because they use their own protocol.
  - On **our** deployed turns, memory is view plus our own sonar relays.

  If the encoder fills these fields from our own relay protocol at deployment, the prior sees a feature distribution
  it never trained on. That is exactly the "prior distribution shifts" failure in macro §6.10, introduced by the
  encoder rather than by behaviour.
- **Recommendation for R0/R2.** Compute the knowledge features from own-view history only, in both training and
  deployment. Add sonar-relayed knowledge later as its own R4 block, trained where the relay exists: our own games
  and self-play. Echo counts are fine to include from the start, because they are protocol-independent and observable
  on teacher turns.
- **Falsifier.** On our own post-deploy games, compare the view-only and the sonar-filled queen-knowledge features.
  If they agree on more than 95 % of turns, the shift is negligible and the split is unnecessary.

## 4. Held-out maps are excluded forever, so state the cost (Chair; split decision)

- **The rule as written.** Held-out maps are "never trained on", for the whole phase. The deployed prior would then
  never see top-team play on at least 3 of the 17 live maps, including at least one queen-decided class (B–E) by
  construction. The R2 offline gate would be LOMO-honest, but the shipped model is permanently weaker exactly where
  the queen matters.
- **Two consistent options. The Chair should pick one in writing.**
  - **(a) Accept the cost.** The held-out maps stay out of training permanently. They are the only honest transfer
    test we will have, and the next server map swap is a real risk: D-043 lists six maps replaced in one day.
  - **(b) Pre-register a final refit-on-all-maps step.** Allow it only after the frozen candidate passes on held-out
    maps, and evaluate the refit only live (ranked and requested battles), never on the local held-out panel.
- **My preference: (a), until the deadline is known.** The map-swap risk is concrete, and Alicia's pool-shaped
  optimum is the precedent for what happens without it.
- **Choosing the maps.** Pick held-out maps where our current gap is large, so the test has power: Trauma or weakhold
  from class C, Maze or Australia from B. A held-out map where we already match the field (QoS, Islands) tests
  little.

## RL translation (D-044)

- **Observation:** the IO block itself, plus per-process memory (view-only knowledge, kept separate from sonar
  knowledge).
- **Action:** unchanged.
- **Value:** none.
- **Demonstration:** teacher turns are partially aliased, because their hidden sonar memory is unobservable to us. The
  per-head BC accuracy ceiling should be read as a lower bound on what an informed policy could do.
