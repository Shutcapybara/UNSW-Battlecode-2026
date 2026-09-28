---
id: A1-Q9-ranked-exposure
author: claude/analysis/session-01KHqE
kind: observation
title: Ranked exposure is not confined to even UTC hours — 8 of the 27 ranked series cached today were requested by other teams' members at arbitrary times; the Elo impact of executor uploads is unrecorded
task: A1 statistics analysis (handoff §3.9)
supersedes: nothing; corrects the handoff's count (20 ranked games of 9663 are recorded in `ranked_exposure`, not 15)
evidence: hub `ranked_exposure` (20 rows, 4 series), `seen_series` cache in LIVE/state/state.json (27 ranked series, 12:12Z), external_actions timeline; `tools/analysis/a1_report.py §Q9`
---

**Unit:** 5-game ranked series. No API call was made; the numbers are what the legacy cache captured.

## Timeline of ranked series (28 Sep, UTC)

| requested | requester | opponent (rank) | our submission | status when cached | our Elo change |
|---|---|---|---|---|---|
| 00:00 | autoscrim | 952 | 8540 (B) | completed 2-3 | +4 |
| 00:00 | autoscrim | 201 | 8540 (B) | completed 5-0 | +12 |
| 01:02 | member of 481 | 481 | 8540 (B) | completed 4-1 | +6 |
| 02:00 | autoscrim | 45, 34 | 8540 | partly pending when cached | — |
| 02:28 | **our member** (jX4g…) | 545 dev | 9508 (A) | completed 2-3 | 0 (dev opponent −3) |
| 04:00 | autoscrim | 875, 481 | 9508 | pending/running | — |
| 04:57, 05:12, 05:32, 05:51, 05:53 | members of 15, 203, 853, 135, 853 | 15, 203, 853, 135, 853 | 9508 (B) | completed/pending | — |
| 06:00 | autoscrim | 133, 950 | 9508 | pending | — |
| 06:46 | member of 853 | 853 | **9663** (executor upload, activated by a teammate at ~06:46) | 4 of 5 completed (b,a,a,a) | — |
| 08:00 | autoscrim | 74, 577 | **9663** | pending | — |
| 09:22 | member of 790 | 790 | **9663** | running (a, b so far) | — |
| 09:33, 09:51, 10:31, 11:12 | autoscrim/other | 133, 40, 790, 977 | (ids not in payload) | completed | −3, −4, +4, +7 |
| 10:00, 12:00 | autoscrim | 762, 19, 75, 406 | — | pending | — |

Observations:

1. **Eight of the 27 cached ranked series were requested by other teams' members** (481, 15, 203, 853 ×3, 135,
   790) at 01:02, 04:57, 05:12, 05:32, 05:51, 05:53, 06:46 and 09:22 — none near an even hour — and one by our own
   member (a ranked dev game at 02:28). An even-hour blackout window
   covers the autoscrims only; roughly half of ranked exposure arrives at arbitrary times and can only be avoided by
   never having an executor upload active outside a test window, which the current transaction design already
   ensures (restore the incumbent after build). The 9663 exposure happened because a **teammate activated** the
   executor's upload; that is an activation-policy problem (D-004), not a scheduling one.
2. **Autoscrims start 4–36 minutes after their nominal hour** (00:00 → 00:36 for 433243; 02:00 → 02:22/02:33;
   04:00 → 04:06), so a blackout measured from the even hour must extend at least 40 minutes after it to cover the
   actual start, or the exposure guard must key on `startedAt`, not `requestedAt`. The configured guard (8 min
   before / 12 after) covers the request, not the start; whether the submission is bound at request or start time is
   untested (research item 6).
3. **Elo impact of executor uploads: unknown.** The four 9663 series (463004, 467153, 468473, 474275) were cached
   while pending/running, so `eloChangeA/B` is null in every `ranked_exposure` row; the legacy cache never refetched
   them. Completed series in the cache show per-series changes of −12 … +12 (|Δ| median 4); our net over the eight
   completed series with a recorded change is **+26**. A single refetch of those four series ids on the Mac
   (`/api/v1/battles/<id>`) closes the gap; the cache also lacks `submissionAId/BId` for series after 09:33.
4. **K-factor regime:** cannot be inferred from eight series. The observed changes are not zero-sum (0 / −3 for the
   dev game; −3 / +4 for 431963), which points to per-team scaling, but the documented K = 96 with 5-game
   performance-vs-expectation makes ±12 per series the plausible ceiling. Whether a fresh upload inherits the team's
   game count (and hence K) cannot be read from the record; only a deliberate comparison of two identical series
   (one under a fresh upload) would show it, which no one should run.

## Decision

Keep the blackout but key it on autoscrim *start* (≥ 40 min after the even hour) and treat member-requested ranked
series as unavoidable: the only lever is not letting executor uploads stay active (teammates must be told, D-004).
Refetch the four 9663 series to book the Elo cost of testing to date.

## Falsifier

A refetch showing zero Elo change on the 9663 series (then exposure is cosmetic), or an autoscrim whose games start
inside the 8/12-minute window and bind the submission at request time (then the current guard suffices).
