# Phase 3 brief — what we are doing now

Written by the Chair (Ushijima), 4 Oct 2026 20:49Z; numbers refreshed 23:43Z. For team members and their LLM sessions. It is a summary: the
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

| Work | Owner | State at 23:43Z |
|---|---|---|
| Clone tests ("the battery"): which model best reproduces the top ten's moves | Hinata (Learner) | on 188,250 development moves: the live prior 0.6977; Heartbreaker's features refitted on ten teams 0.7184; new-encoder trees 0.7145; small CNN 0.6785. Combination arms fitting; refits on the full data (2.75 M moves) next |
| Training data; the bot slot for the cloned prior | Kageyama (Data) | full rows built and audited; building `bots/kageyama-01-p1-slot` (the model inside the search bot, within 4 MiB) |
| Live screen LS-1: `asahi-05-kz12-k16` (a hand-rule change) against the live bot | Daichi (Live ops) | 120 of 204 games; stops 02:15Z on 5 Oct; the candidate goes live then if the conditions of D-064 §B hold |
| Local panels, measurements, the Mac's job runner | Asahi (Evaluator) | k = 16 local gate: hold overall, +28 points on Weakhold; throughput for self-play measured |
| Reviews, audits, forecasts on every proposal | Tanaka (GPT), Sugawara (Claude), Nishinoya (GLM) | active |
| Decisions, merges, this brief | Ushijima (Chair) | hourly |

## Results today

- The value model (how likely a position wins) failed its one confirmation test and is parked behind the clone work.
- The queen reach veto (a hand rule) was refuted and closed.
- The first clone results beat the prior we deploy by about two points of accuracy on the top ten's moves. More
  training data helps: 0.676, 0.684, 0.703, 0.714 at 10 %, 25 %, 50 % and 100 % of the development set.
- The k = 16 hand rule is a real fix for one map (Weakhold: 43 of 48 wins against 27 of 48 locally) and neutral
  elsewhere.
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
  bot can be uploaded.

## Where to read more

| Question | File |
|---|---|
| What is decided, and why | `docs/findings/2026-09-28-director-decisions.md` (D-046 onward) |
| Current state, updated hourly | `claude/chair-status.md` |
| What each lane is saying | `docs/hub/BOARD.md` |
| Rungs, proposals, forecasts, artifacts | `docs/learning/ladder.md`, `proposals/INDEX.md`, `calibration.md`, `registry.md` |
| Original plan and role prompts | `docs/learning/00-MACRO.md`, `docs/learning/prompts/` |
| Each lane's own status | `claude/<lane>-status.md` |
