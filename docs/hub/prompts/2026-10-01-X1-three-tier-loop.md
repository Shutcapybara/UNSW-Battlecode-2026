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
