---
id: A1-Q8-judge-divergence
author: claude/analysis/session-01KHqE
kind: observation
title: Every live game of 28 Sep shows the post-27-Sep judge signature (92 % replay-drive agreement, first mismatch by round 6) for two unrelated bots; messages are mostly right, not absent
task: A1 statistics analysis (handoff §3.8)
supersedes: extends claude/jks-self-audit-status.md §2 (public games) to the controlled live record; the "~92 % after 13:00 UTC" claim is reproduced
evidence: `tools/team_recon_claude/replay_drive.py` and `replay_drive_msgvar.py` (WV=all) run in the Cowork VM on `LIVE/state/decoded/*.replay` against `bots/bifrost-v01-portal-memory` (fingerprint-matched to 8540) and `bots/yuna-v02-core` (9663); per-game results in `build/a1_replay_drive_live.csv` (121 games)
---

**Unit:** command (one recorded action per dragon-turn), nested in game; 121 games, 965,412 commands.

| source (local bot) | live games | commands | agreement | exact games | first mismatch round (median / q90) | worst / best map | by opponent |
|---|---:|---:|---:|---:|---|---|---|
| 8540 bifrost-v01-portal-memory | 51 | 383,696 | **0.922** | 0 | 6 / 16 | Trophy 0.80 / Trauma 0.96 | 45 0.93, 62 0.91, 470 0.93, 545 0.93, 752 0.91 |
| 9663 yuna-v02-core | 70 | 581,886 | **0.924** | 1 (a 53-round game, 170 commands) | 7 / 17 | Trophy 0.83 / PD 0.98 | 45 0.91, 62 0.93, 470 0.92, 545 0.94, 752 0.93 |

The self-audit's public-replay result (bifrost 8540: 0 of 502,822 mismatches before 12:30 UTC 27 Sep; 91.6 % after
13:08) is reproduced on today's controlled record with the same map ordering (Trophy worst, Trauma best) and now for a
second, unrelated bot (yuna-v02: a gavroche-family host). The divergence is therefore a property of the judge's input
stream, not of one bot's code.

**Messages are the carrier, and they are mostly right.** Dropping every delivered sonar message from the rebuilt
input (`WV=all`) *lowers* agreement in 29 of 29 games (0.904 → 0.832 on the 29 shortest 8540 games). So the bot
does consume the recorded messages and most of them are what it received; the discrepancy is a subset of messages
(delivery, ordering or recording), consistent with the self-audit's single-block perturbation result (removing one
teammate sonar reproduced the recorded move).

## What this means for the evidence tiers

- **Native local games (unswbc 1.0.0 / 1.2.x on the Mac) are unaffected** — they never see the judge's message
  stream. Local outcome ledgers, seeded panels and probe metering (which is native) remain valid evidence.
- **Replay-drive on post-change games is ~92 % faithful per decision** for any bot; counterfactual probes on live
  positions ("what would X have done here") drift from round ~6 and compound. Use them for opening-phase questions
  (rounds 0–20) only, or on the 141 pre-change public games.
- **Offline features built from post-change replays mis-state the inbox** for ~8 % of turns; imitation-learning
  models trained on them inherit that noise.

## The one-game experiment that settles it (for director authorisation; no upload is made by this analysis)

1. Build `bots/tap-v01` from `bots/yuna-v02-core` with one change: at the top of the per-turn loop, echo the raw
   stdin block (every line, verbatim, base64 if needed) as `LOG STDIN <turn> <chunk>` lines before the action.
   `tools/team_recon_claude/validate_tap.py` already checks byte-exactness of the tap locally on 1.2.2.
2. Upload it as `LV-tap-v01-<fp8>-ai` with the standard upload transaction (restore the incumbent after build),
   request **one dev game vs 752 on Trophy** (the worst-agreement map, side A) inside a quota window with no
   other dispatch, and harvest the replay.
3. Compare, turn by turn, the logged stdin with the round block that `roundblock.py` rebuilds from the replay:
   the first differing line names the bug (a message missing, extra, reordered, or a countdown/echo field).
   Expected runtime: one dev game (≤ 3 minutes), 1 dev-quota unit, no ranked exposure (dev pool).
4. If the stdin matches the rebuilt block exactly, the divergence is inside the judge's *bot process*
   (e.g. an environment difference), and the next probe is a tap of `sys.version`/`os.environ` in the same build.

## Decision

Local metering and native panels stay valid; replay-drive and replay-derived inboxes on post-27-Sep games are
approximate and must be labelled so in every finding that uses them. Authorise the tap game (item 6 of the research
list) — it costs one dev game and removes an unknown that touches every replay-based tool.

## Falsifier

A post-change live game that replay-drives exactly for a full-length game (the record has none in 121), or a tap
game whose logged stdin equals the rebuilt block for every turn.
