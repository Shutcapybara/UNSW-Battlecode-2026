# X-1 — The three-tier learned loop: representation → decisions → policy improvement, cycled (Opus 5.5, desktop, Claude Code)

Lineage: as given by the lead. Bots `bots/<lineage>-<nn>-<slug>/`, branch `r/<lineage>`, worktree `../wt-<lineage>`,
tools `tools/<lineage>/`. Host: the desktop (`~/Documents/Projects/2026/UNSW-Battlecode-2026`, `.venv`, 4090, ~2,900
games/h, `--jobs $(( $(nproc) - 2 ))`). C++ bot; all training offline.

Read first: `docs/hub/prompts/2026-09-29-R-index.md` (rules, D-032/D-033/D-036/D-037), `docs/hub/HYPOTHESES.md`
(L16, L27, L31–L34, L36, L37), **`docs/findings/2026-09-30-hb1-heartbreaker.md` and `claude/hb1-status.md`** (the
result this lane builds on), `bots/hb1-12-direction-prior/` and `bots/hb1-04-deployable/` (the search-plus-prior
architecture and the compiled-tree export), `tools/hb1/` and `tools/team_recon_claude/features_v5.py` (the
per-turn candidate/feature/choice dataset and the GBT training path), `docs/hub/prompts/2026-09-30-SF1-state-and-features.md`
and the SF-1 lineage's status file (the hand-built state module and feature interface — coordinate, do not
duplicate), `docs/hub/prompts/2026-09-30-RL1-curve-matching.md` (the reward design; RL-1 may be folded into this
lane if the lead says so), `docs/analysis/BENCHMARKS.md`, `docs/findings/2026-09-30-s1-Q3-opening-components.md`.

## What HB-1 established, and what this lane is

Heartbreaker is a rule wrapper around one learned decision (direction); its direction GBT, used as a prior
inside Ares's search (`λ·log p(first step)` added to the path score), took Ares from 122–38 to **139–21** with
economy +0.03–0.04 and every death rate down 30–40 %, replicated at two seeds. Strength is steep in direction
accuracy (0.73 → 7 % win, 0.83 → 35 %, 0.85 → 55 %). Memory features added ≤ 0.2 pp to imitating *their*
direction — their policy is memoryless. Trees matched or beat an MLP on every decision.

This lane replaces "imitate Heartbreaker" with "learn our own", in three tiers that are fitted in turn and
cycled:

- **Tier 1, representation:** a small CNN over the local view (9×9–15×15; channels: terrain, kelp, pearls, bed
  timing, ally/enemy parts, seen-age, the SF-1 grids) and a small GRU (64–128) carrying accumulated state,
  trained with auxiliary decision heads and then frozen; its embedding is exported as features.
- **Tier 2, decisions:** one XGBoost head per decision — direction, split gate, child allocation, portal entry,
  engage/refuse, sonar emission — on the hand features (SF-1 + the tier-4 map memory) plus the tier-1
  embedding; exported as compiled nodes (`hb1-04`'s path). The direction head is the prior inside Ares's search,
  as in hb1-12; the others gate or replace the corresponding rules behind switches.
- **Tier 3, policy improvement:** the operator that makes the next cycle's targets better than imitation. Use
  **expert iteration**: play games with the current search-plus-priors bot, relabel each logged decision with
  what the *search* (deeper, with lookahead and outcome credit over the next 20 rounds) would have chosen, and
  refit tier 2 on the relabelled set; the search is the policy improvement, the trees distil it. Add ES/SPSA
  over the few continuous knobs (λ per head, temperatures, the search caps) on the D-032 objective. Full
  policy-gradient RL is the fallback if expert iteration stalls, not the start.
- **Tier 4 (hidden, algorithmic):** the bot's own map memory — SF-1's decayed grids, bed timing, portal pairs,
  the mode/belief variable. Not learned; it is the substrate the learned tiers read. Share SF-1's module.

The cycle: (0) tier 2 on top-30 corpus targets with hand features only (= hb1-12 with our own model) → (1) tier 1
trained on the same targets, embedding added to tier 2, refit → (2) tier 3 relabels with search, refit tier 2 →
(3) tier 1 re-trained on the improved targets → repeat. One cycle = one version; the D-032 scorecard on both
panels after every cycle, plus fidelity (held-out agreement per head) and a fixed opponent set so cycles are
comparable. Stop a tier when its refit stops moving the gate.

## How tier 4 feeds route selection (the lead's question)

The map memory is consumed twice, and the two consumers are different objects:

1. **By the search, as targets and edge costs.** Ares's target search already runs over memory (remembered
   pearls, beds with ripening times, portal pairs, seen-age → unseen value). Tier 4 extends what it runs over: the
   decayed grids become **edge costs** on the memory graph — `enemy_ew` and `death_ew` as risk, `ally_ew` as
   congestion, seen-age as uncertainty, `food_ew` as attraction — and the belief/mode variable selects which cost
   vector is active. Route selection is then "search over the memory graph with learned costs"; tier 3's ES fits
   the cost weights on the D-032 objective. This is SF-1's Part 2 and it needs no neural component.
2. **By the heads, as features.** HB-1's candidate features (forward run, blocked neighbours, reachable area,
   pearl distance, ally heads within 2) are computed from the *view*; they carried 14 pp of direction accuracy.
   Tier 4 supplies the same quantities computed over the *memory* — distance to the nearest remembered pearl and
   ripening bed along the memory graph, reachable area beyond the view, corridor degree and dead-end depth ahead,
   hazard along each candidate's first k steps, the ally/enemy inclination received over sonar — as features of
   each candidate first step. That is how the direction head sees routes it cannot see.

HB-1's "memory adds ≤ 0.2 pp" was measured on Heartbreaker's choices, which are a function of the view because
their policy is; it is not evidence about what our bot could use. The test in cycle 1 is the direction head with
and without the tier-4 route features at equal data, on our own relabelled targets, not theirs.

## Phases (the lead's proposal — yes, with one caution)

Learn an opening policy, a mid-game policy and a crown-race policy, and a switch between them. The evidence
supports the split: the search's phase bifurcation (L03: wide search hurts before r40 and helps after), the
opening gap (L36: the loss is r0–25 economy), Heartbreaker's late gate being pure escape (no productive late
splits — a different regime), and the tempo metric. The caution is data: three separate model sets triple what
each head needs. So build it in two steps: first **phase as a feature** (a phase belief from measured state —
units, total length, contact made, bed saturation, tempo lag, clock as a soft prior — never a round threshold) with
per-phase sample weighting, and check the per-phase held-out accuracy; split into **separate heads per phase**
only where the single model's per-phase accuracy is worse than a phase-specific model's on the same data. The
switch is L32 at game scale: a belief over {opening, mid, crown race} updated by observation, with the transition
learnable from where each phase's heads out-score the others (train it as a mixture-of-experts gate: relabel each
logged state with the head that the search preferred, fit the gate on state features). The crown race in
particular is its own problem (S-4, C1-E's finding that the winner's longest margin is 0–1 in decided games); its
heads may be simpler than the opening's. Report the phase boundaries the gate learns as a function of state and
whether they vary by map cluster (D-036) — that is a finding in itself.

## Sonar

Two separate problems; do not conflate them. (a) **Receiving**: packets and echo counts are observations — inputs
to tier 1 and features for tier 2 (Heartbreaker's steering uses echo counts: −0.86 pp without them). (b)
**Sending**: what to broadcast is a tier-2 head *only under a fixed protocol* — the payload encodes L32/L33's
inclination (mode, confidence, coarse position, team nonce) and the head decides when and which directions.
Emergent, end-to-end learned communication is out of scope: the channel is non-differentiable, credit assignment
across agents is unsolved at this scale, and the first-body/either-team semantics make it fragile. Local
coordination comes from tier 4 (the belief update on receipt, L33's coupling) with the coupling weights fitted by
tier 3's ES, not from learning the protocol.

## Is the design reasonable? (the lead asked; answer in the decision memo, §0 of the finding, before building)

Assess and state: (1) whether tier 1 earns its place — HB-1 says memory adds nothing for *their* memoryless policy,
which says nothing about ours; the test is tier 2 with vs without the embedding at equal training data, and
linear probes on the GRU state for enclosure/food density/mode (L34); (2) whether the cycle converges or
oscillates — track held-out agreement between successive tier-2 models and the gate; a cycle that changes the
policy without moving the gate is churn; (3) the data budget per cycle (games to relabel; at ~2,900/h and ~10k
actor-turns per game a 500-game cycle is a few hours end to end); (4) leakage: the same fixtures must not train
and evaluate; the D-032 panels are held out from every training set; the out-of-sample rule applies to features
(no map identity) and the generalisation panel decides.

## Deliverables

`tools/<lineage>/{dataset,train_repr,train_heads,relabel,export,cycle}.py` (resumable, logged), the C++ side
(feature dump, compiled heads, embedding forward pass, `POLICY_FILE` loader for local games, golden parity with
all heads off, CPU probe with them on — stay under 30 M points/turn), one bot per cycle with `CANDIDATE.toml`
(`language = "c++"`, `lineage_parent` = previous cycle), `claude/<lineage>-status.md` after every cycle (the cycle
table: per-head held-out agreement, gate on both panels, fidelity to the previous cycle, CPU), findings at cycle
0, cycle 2 and at the end (`docs/findings/2026-10-0x-<lineage>-*.md`, ending with the ledger rows touched — L16,
L27, L34 at least — and proposed weights). Commit and push `r/<lineage>` after every cycle. Do not commit training
data or replays; keep model blobs under `build/` and commit only the compiled heads the bot needs — and keep one
copy of any large header, referenced by the versions, not one per bot directory (HB-1's tree carries 1.1 M lines
of duplicated headers). Do not register; do not read lane `rb`.
