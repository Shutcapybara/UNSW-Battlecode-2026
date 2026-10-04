# Phase 3 brief — what we are doing now

Written by the Chair (Ushijima), 4 Oct 2026 20:49Z. For team members and their LLM sessions. It is a summary: the
binding text is the decision log, `docs/findings/2026-09-28-director-decisions.md`, records D-046 to D-061. Where this
brief and `docs/learning/00-MACRO.md` disagree, the later decision records win; the macro's rung order and its
gate-before-upload rule are superseded (D-055, D-057, D-059).

## Where we stand

- Team 7, "Just Keep Swimming": Elo 1723, rank 82 (ladder snapshot 19:31Z). The top ten sit at Elo 2192 to 2333.
- Live bot: `carthage-05-free-sprint` (submission 14585), a C++ search bot whose move prior is a model cloned from
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

## What is running

| Work | Owner | State at 20:49Z |
|---|---|---|
| Clone tests ("the battery", arms A0 to A10): the current prior as is; the Heartbreaker recipe on ten teams, pooled and per team; new features; combinations; top-rated teachers only; mirrored data; a small CNN on the dragon's view | Hinata (Learner) | first fit 0.714 accuracy (weighted); CNN arm and unweighted refit running; most arms wait on Data |
| Training rows from the top ten's replays; Heartbreaker features; the frozen 115-game test set | Kageyama (Data) | development set ready (189,630 moves); **stalled since 18:50Z** by a full workspace disk |
| Live screen LS-1: `asahi-05-kz12-k16` (a hand-rule change) against the live bot, 204 games | Daichi (Live ops) | 60 games played; ends 02:15Z; likely too noisy to decide |
| Local gate for the same candidate on seeds 2–3 | Asahi (Evaluator) | running |
| Reviews, audits, forecasts on every proposal | Tanaka (GPT), Sugawara (Claude), Nishinoya (GLM) | active |
| Decisions, merges, this brief | Ushijima (Chair) | hourly |

## Results today

- The value model (how likely a position wins) failed its one confirmation test and is parked behind the clone work.
- The queen reach veto (a hand rule) was refuted and closed.
- More training data helps the clone: accuracy 0.676, 0.684, 0.703, 0.714 at 10 %, 25 %, 50 % and 100 % of the
  development set.
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

- The Mac's disk is 97 % full (31 GB free of 927 GB). It filled at 18:47Z and stopped the hub and the Evaluator.
- The Cowork workspace's session disk is full; it blocks Kageyama.
- The hub runs in a Terminal window; if it exits and nothing restarts it, collection and live games stop.

## Where to read more

| Question | File |
|---|---|
| What is decided, and why | `docs/findings/2026-09-28-director-decisions.md` (D-046 onward) |
| Current state, updated hourly | `claude/chair-status.md` |
| What each lane is saying | `docs/hub/BOARD.md` |
| Rungs, proposals, forecasts, artifacts | `docs/learning/ladder.md`, `proposals/INDEX.md`, `calibration.md`, `registry.md` |
| Original plan and role prompts | `docs/learning/00-MACRO.md`, `docs/learning/prompts/` |
| Each lane's own status | `claude/<lane>-status.md` |
