# HB-1 — Heartbreaker (team 62): anatomy of a learned policy, and a structured mimic (Opus 5.5, desktop, Claude Code)

Host: the Ubuntu desktop, `~/Projects/UNSW-Battlecode-2026`, venv `.venv`, `--jobs $(( $(nproc) - 2 ))`, GPU available
(`torch` cu128 on the 4090 — optional for this task; tree models train on CPU). Branch `r/hb1`, worktree `../wt-hb1`,
bots under `bots/hb1-<nn>-<slug>/`, tools under `tools/hb1/`. Read first: `docs/hub/prompts/2026-09-29-R-index.md`
(rules), `docs/hub/HYPOTHESES.md` (the ledger; you end by proposing weights), the two prior Heartbreaker recon
packets — `experiment_data/team_recon_62_20260927T140359Z/REPORT.md` (+ `FEATURE_LEDGER.md`, `COMPARISON_LEDGER.md`)
and `experiment_data/team_recon_62_20260927_glm/NEXT_CYCLE.md` — and `tools/team_recon_claude/README.md` (the
imitation/feature tooling that produced them; extend it, do not fork it). Also `docs/findings/2026-09-28-analysis-claude-Q5-opponent-fingerprints.md`
and the `ouroboros-m01-vibing-mimic` README (what a plain clone achieved, and why that is not the goal here).

## What is already known (do not re-derive; verify on the new data)

Heartbreaker is rank ~37 at 1847, the field's elimination specialist (56 of our 64 losses to it are eliminations).
The 27 Sep recon learned its move-vs-split gate at 99.3 % accuracy but exact commands at only 66 % (local greedy
baseline 62 %), found: splits on 94.7 % of opportunities when no ordinary exit is free and far more selectively
otherwise; wall-crossing commands only when no exit and no eligible split exist (a validity wrapper, zero invalid
commands in 180 games); sonar payloads drawn from the same {3,4,5,6} ecosystem code as Vibing++ with no receiver
response; a map-distribution cliff (Portals 1/10, Slithery 2/11, Trauma 2/11); asymmetric cross-era transfer
(early→late 58 %, late→early 67.5 %: later policies are supersets); hourly upload bursts. The RL attribution
(gradient training + auto-upload since 25 Sep evening) is the best-supported hypothesis, not an identification.
Open from that packet: era metrics rest on 3 games each; era 2750 is the natural static snapshot; payload meaning
is a dead end (do not spend time there).

## Data

- The corpus on the Mac holds 558 team-62 games (27–29 Sep, ranked and unranked, **no submission ids** — D-023).
  Its target was raised to 6,000 on 29 Sep 21:30 UTC so the collector pulls their whole reachable history; expect
  the count to grow over the next day. The desktop has no API key by design; pull from the Mac:
  ```bash
  M=alik@<mac>; MREPO=/Users/alik/Documents/Projects/UNSW-Battlecode-2026
  ssh $M "cd $MREPO/public_replays/corpus && python3 -c \"
  import json
  for l in open('index.jsonl'):
      r=json.loads(l)
      if 62 in (r['team_a'],r['team_b']): print('replays/%d.replay'%r['game_id'])\"" > /tmp/hb62.txt
  rsync -a --files-from=/tmp/hb62.txt $M:$MREPO/public_replays/corpus/ public_replays/corpus/
  rsync -a $M:$MREPO/public_replays/corpus/index.jsonl $M:$MREPO/public_replays/corpus/ladder public_replays/corpus/
  rsync -a $M:$MREPO/experiment_data/team_recon_62_20260927T140359Z $M:$MREPO/experiment_data/team_recon_62_20260927_glm experiment_data/
  ```
  Re-run the first three lines daily to pick up new games. The 27 Sep packets' own replay sets (with submission ids
  and era labels) are in `experiment_data/team_recon_62_*`; they are the only era-labelled data and stay the
  anchor for any cross-era claim.
- Timestamps in `index.jsonl` (`finished_at`) plus the ladder snapshots give a rating time series; behavioural
  drift by time window is the substitute for submission ids after 28 Sep.

## The questions, in order

**Q1 — Structure before parameters.** Decompose the policy into the decisions a bot must make each turn and
measure each one separately on the new data: (a) the split gate (split / don't), (b) split allocation (child
length), (c) the move direction, (d) sonar emission (when, which directions, what), (e) the late-game
concentration behaviour the 27 Sep packet flagged as a weakness. For each: a per-turn dataset of legal candidates
with local-view features (`tools/team_recon_claude/features_v4.py` is the actor-local row; extend it, keep the
name versioned), the accuracy of a shallow tree, a deep GBT, and a small MLP at predicting their choice, and the
**information each feature family carries** (drop-family ablations). The gap between the shallow tree and the
MLP on each decision is the measure of how much of that decision is a rule and how much is learned. Report the
five gaps as the first table. Add (L31): fit a regime model (HMM or change-point detection) to per-dragon action and
feature sequences for Heartbreaker, three other top-30 teams and us; report whether behaviour segments into a few
discrete regimes with sharp transitions (a state machine) or drifts continuously (a scored evaluator), and which.

**Q2 — What is the wrapper, what is the policy.** The 27 Sep finding says validity is enforced outside the
learned part (no invalid commands, wall moves only under total blockade). Test the wrapper hypothesis directly:
enumerate the situations where the learned part's apparent choice would be invalid and show what they do instead;
list the wrapper's rules as code (`hb1/wrapper.py`), and show that the same MLP wrapped with those rules
reproduces command-level accuracy above the 66 % ceiling. The wrapper is what we can copy verbatim; the policy is
what we can only approximate.

**Q3 — Is it RL, and does it matter.** Use the time series: split the new corpus into 6-hour windows; for each,
the per-decision accuracies of a model trained on the previous window (transfer forward) and on the next window
(transfer backward). Continued superset drift (backward > forward) with rating rising says a training loop is
running; a flat series says it stopped. Add: the upload cadence inferred from behavioural change-points, and whether
change-points coincide with rating steps. State plainly which of these would look different for a hand-tuned bot
with frequent uploads; the 27 Sep packet's honest answer was "none of the replay evidence can distinguish", so if
that is still the answer, say so and stop spending on it.

**Q4 — The structured mimic.** Not a clone. Build `hb1-01-structured`: the wrapper from Q2 as rules; the split gate
and allocation from Q1 as an exported tree (the `export_hgb.py` path); the move direction as a **scored evaluator**
over the same features with weights fitted to their choices (logistic on candidate rows, or the MLP distilled into
a linear/GBT scorer); sonar as their observed emission rule. Implement in C++ on the Ares chassis
(`bots/ares-v06-expanded-search-support` copied; the scorer replaces the target/threat cost in `policy.hpp` behind a
switch, the wrapper replaces the move filter) so it is measured at real CPU. Fidelity first (decision agreement per
component on held-out games, closed-loop divergence vs their replays with `tools/team_recon_claude/closed_loop.py`),
then the BENCHMARKS scorecard on the z1 panel and the generalisation panel, atlas off, plus **head-to-head vs their
own replay opponents' bots where we have them** (our zoo includes several of the teams they beat us with).

**Q5 — What transfers.** The point of understanding them is to take pieces. For each component of Q4 that the
fidelity test says is faithful, port it alone into a copy of Ares V06 as a switch (`hb1-1x-<component>`) and run the
gate: does *their* split gate, *their* wrapper, *their* direction scorer, on *our* bot, pass? That is the finding
the ledger wants: rows L27 (learned decision functions), L05/L24 (leaks — their zero-invalid, blockade-only wall
behaviour is a leak fix by construction), L20/L04 (weights). End the finding with the rows touched and proposed
weights.

## Rules

Out-of-sample rule (no map-identity features anywhere in the mimic; their map cliff is a finding, not a
feature). One mechanism per version. Fidelity numbers are on held-out games never used for fitting. Copy, don't
edit, other trees. Never commit replays. Findings in `docs/findings/2026-09-30-hb1-heartbreaker.md`, status in
`claude/hb1-status.md` after every stage, raw rows in `game_stats/runs/hb1-*.json`, models under `build/hb1/`
(gitignored) with the exported predictors under `bots/hb1-*/`. Budget: Q1–Q3 are corpus work (hours, no games);
Q4 fidelity ~200 closed-loop games; Q4–Q5 panels ~8 × 340 games — under two hours each at this host's rate.
