# Phase 3 brief — what we are doing now

Written by the Chair (Ushijima), 4 Oct 2026 20:49Z; numbers refreshed 5 Oct 02:22Z. For team members and their LLM sessions. It is a summary: the
binding text is the decision log, `docs/findings/2026-09-28-director-decisions.md`, records D-046 to D-069. Where this
brief and `docs/learning/00-MACRO.md` disagree, the later decision records win; the macro's rung order and its
gate-before-upload rule are superseded (D-055, D-057, D-059).

## Where we stand

- Team 7, "Just Keep Swimming": Elo 1723, rank 82 (ladder snapshot 19:31Z). The top ten sit at Elo 2192 to 2333.
- Live bot since 5 Oct 02:13Z: `asahi-05-kz12-k16` (submission 16979): `carthage-05-free-sprint` (14585, now the rollback target) plus one hand rule for the queen. It is a C++ search bot whose move prior is a model cloned from
  one other team (Heartbreaker). That clone is the only learned piece that has ever improved our results (+0.15 win
  rate on local panels).
- Limits on any bot: zip at most 4 MiB, at most 30 M points of compute per turn, no runtime errors.

## The strategy

1. **Precedent first, then our own evidence** (the lead's rule, D-058). The nearest precedent is this contest: its
   top teams say they field neural networks (D-059). In eight comparable contests, rules or search won five and
   self-play learning won three, each with dedicated compute; no verified case of imitation alone reached a top
   ten (D-061).
2. **Clone the best teams first.** Fit models that reproduce the top teams' decisions from their public replays,
   and put the best one inside our search bot as its prior.
3. **Then learn past them.** Self-play fine-tuning that starts from the cloned network is scoped (card P-7); no
   training has started.
4. **The ladder judges.** A candidate that passes cheap local checks goes to a live screen against real opponents;
   local gates confirm afterwards (D-055).
5. Hand-written rule changes are temporary helpers, not the main line (D-059).
6. **Time and game state** (the lead's instruction, D-067). Every clone arm already takes the round. Being added: results
   by phase, a no-time ablation, clones of the split, cull and sprint decisions, a team-trajectory block, and a
   scoping card for a latent game state that selects behaviour sets.
7. **Two free lanes** work outside this process with one goal, the strongest bot (`docs/learning/prompts/07-free-lane.md`).

## What is running

| Work | Owner | State at 01:49Z, 5 Oct |
|---|---|---|
| Clone tests ("the battery"): which model best reproduces the top ten's moves | Hinata (Learner) | by accuracy on 188,250 development moves: mirror-averaged Heartbreaker features 0.7224, without averaging 0.7184, new-encoder trees 0.7145, live prior 0.6977. **In play the first clone lost** (next row), so selection by accuracy is suspended; refits on the full data continue |
| Training data; the bot slot for the cloned prior | Kageyama (Data) | slot built: `bots/kageyama-01-p1-slot`, zip 1.05 MiB, at most 10.1 M points a turn, predictions equal to Python to 3e-8, equal to the live bot with the switch off. Adding the input path for Heartbreaker's features |
| Live screen LS-1: `asahi-05-kz12-k16` (a hand-rule change) against the previous live bot | Daichi (Live ops) | ended: 75 pairs, +0.080 [−0.029, +0.187], no fault. **The candidate went live at 02:13Z (D-069)**; rollback watch over its first 40 ranked games |
| Local panels, measurements, the Mac's job runner | Asahi (Evaluator) | **the slot bot with the ten-team encoder trees loses to the live bot: pool −7.0 points [−12.9, −1.5], gen −5.6.** Now testing why: the Heartbreaker-feature clone, no prior at all, a stronger prior weight, and single-team clones |
| Reviews, audits, forecasts on every proposal | Tanaka (GPT), Sugawara (Claude), Nishinoya (GLM) | active |
| Decisions, merges, this brief | Ushijima (Chair) | hourly |

## Results today

- The value model (how likely a position wins) failed its one confirmation test and is parked behind the clone work.
- The queen reach veto (a hand rule) was refuted and closed.
- The first clone results beat the prior we deploy by about two points of accuracy on the top ten's moves. More
  training data helps: 0.676, 0.684, 0.703, 0.714 at 10 %, 25 %, 50 % and 100 % of the development set.
- The k = 16 hand rule is a real fix for one map (Weakhold: 43 of 48 wins against 27 of 48 locally) and neutral
  elsewhere.
- Self-play is feasible on the Mac by throughput (D-066); no training is approved yet.
- **More accurate is not yet stronger** (D-068): the ten-team clone predicts the teachers better than the live prior and
  plays worse inside our search. Leading explanations: its probabilities are much softer, and it averages ten styles.
- The free lane Kenma has a bot at 58–44 head-to-head against the live bot (102 games), 6–0 on Schooltime.
- A candidate was briefly live by accident (17:33–17:40Z): the server activates on upload. The fix is written and
  merged but not deployed.

## Rules everyone follows

- Held-out maps Autarky, Maze and Trauma are never trained or tuned on. The frozen 115-game test set is read once.
- No map identity in any bot feature.
- Every proposal states its precedent (or says there is none), a pass rule fixed in advance, and a forecast.
- Only Live ops touches the server, and only through hub controls. No redeploy of the hub until the Chair says so.
- Work on your own branch; never edit another lane's files. `docs/hub/BOARD.md` is appended to in the main
  checkout only.

## Risks open now

- The Mac's disk filled at 18:47Z and stopped the hub and the Evaluator. It has 271 GB free now, after old replays
  were deleted; the server replay corpus grows about 19 GB a day.
- The Cowork workspace's session disk is full. It has cut off the shells of three sessions; two were replaced by
  fresh sessions, and the Chair works by file copy.
- The hub runs in a Terminal window; until the lead confirms it restarts by itself, it is not redeployed, and no new
  bot can be uploaded. This now also blocks the clone, whose bot slot is ready.

## Where to read more

| Question | File |
|---|---|
| What is decided, and why | `docs/findings/2026-09-28-director-decisions.md` (D-046 onward) |
| Current state, updated hourly | `claude/chair-status.md` |
| What each lane is saying | `docs/hub/BOARD.md` |
| Rungs, proposals, forecasts, artifacts | `docs/learning/ladder.md`, `proposals/INDEX.md`, `calibration.md`, `registry.md` |
| Original plan and role prompts | `docs/learning/00-MACRO.md`, `docs/learning/prompts/` |
| Each lane's own status | `claude/<lane>-status.md` |
