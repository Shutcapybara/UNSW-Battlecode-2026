# Baseline and event context

> Planning snapshot from 6 October 2026. For the current status, always use [the root handoff](../../FINALS_WORKING_MEMORY.md); later decisions and evidence are in [the experiment log](EXPERIMENT_LOG.md).

## Verified schedule and sources

| Event | Adelaide time | Meaning |
|---|---|---|
| Qualifier submission lock | Fri 9 Oct, **4:30 pm** | Active bot is locked; uploads and manual match requests close |
| Qualifier seeding | After post-lock autoscrims | Exact separate cutoff time is not published on the page |
| Qualifier stream | Sat 10 Oct, **5:00 pm** | Best of seven, all maps unseen |
| Grand Final seeding | 16 Oct | Ladder-rating date; exact time not verified |
| Grand Final | 17 Oct | Separate submission-lock time not verified |

Sources checked 6 October: [qualifier event](https://game.battlecode.au/tournaments/qualifier),
[season schedule and FAQ](https://battlecode.au/#timeline).
The previous suggestion to keep an atlas bot for seeding and then swap it is invalid for the qualifier.
**Proposed internal deadline:** freeze code on 8 October evening and finish submission verification
and activation by 9 October noon Adelaide. These are working targets, not organiser deadlines.

## Current repository and strength evidence

The checkout inspected was at `6985391e` (6 October merge of `r/shenzhen`). It contains approximately
1,131 bot snapshots. `FRONTIER.md` is the canonical registry but its main rankings/active-upload
description are stale for current Queen rules. Update it when establishing the new baseline;
retain the old ratings explicitly as historical panels rather than mixing them with live Elo.

| Candidate | Recorded evidence | Use |
|---|---|---|
| `bokuto-18-queenfeed` / 17791 | 32W–28L in 60 ranked games; score minus expectation at common 1725 anchor +0.174, 90% series-bootstrap interval [+0.079, +0.282]; no stored maps | Best-supported tournament fallback |
| `bokuto-61-mouth` / 18078 | Active at Phase 3 stop; final live look unread; stores 17 ladder maps | Inspect its completed trial; challenger requires a new atlas-free snapshot and unseen-map evidence |
| `asahi-27-b13-reserve` / 17940 | 25W–35L in 60-game trial; did not replace 17791 | Component control |
| Local `growth_rl` PPO policies | 32 saved gates inspected, none passing | Research artifacts, not a promoted replacement |

Source: [Phase 3 summary](../../docs/findings/2026-10-06-phase3-summary.md),
[Bokuto 18 notes](../../bots/bokuto-18-queenfeed/README.md). A fresh authenticated API read and
activation/readback at 6 Oct 21:22 Adelaide confirmed fallback 17791 as the sole active submission.
The approximate 1859 performance estimate for 17791 comes from a short window, not a settled rating.

## Live eligible-field snapshot

Authenticated `GET /api/v1/leaderboard`, captured 6 October 2026 at 21:47 Adelaide
(`build/finals/20261006-eligible-field-baseline/summary.json`): 984 roster rows, 335 marked
eligible, and 171 eligible teams with a current numeric ladder rank. Our team, **Just Keep
Swimming** (ID 7), was eligible at overall rank 69, Elo 1825, and 52nd among those 171 currently
ranked eligible teams. The tenth currently ranked eligible team was at overall rank 11 with Elo
2245, a raw 420-point gap.

This is one volatile snapshot. It does not establish a qualifier seed, bracket position, probability
of reaching the top 10, or strength on unseen maps. The exact qualifier seeding follows post-lock
autoscrims, and advancement is decided by best-of-seven match results. Use current source-attributed
games and later published seeding to identify likely opponents; do not turn the Elo gap into a
projection.

## Recent likely-opponent sample

At 21:54 Adelaide, read the two most recent ranked series exposed for each of the ten highest-ranked
eligible teams. The sample contains 17 distinct series and 85 game rows. The battle API returned no
submission IDs in these series; one public replay per series was fetched into the ignored
`build/finals/20261006-eligible-field-baseline/replay-samples/` directory, but all 17 replay headers
had empty bot labels. The metadata and header reports are referenced in the [experiment log](EXPERIMENT_LOG.md).
This is useful for mapping recent opponents and map exposure, but it is not yet a source-attributed
opponent panel. Resolve exact bot versions before freezing them as controls or drawing strategic
conclusions.

Recorded diagnosis: Bokuto 18 queen alive at r300 ~0.72; 14/20 r300 leads converted. Economy is
behind: total length ~65 at r100 versus ~78 for top-ten winners, r100→r300 growth ~38 versus ~68.
These are observational comparisons, not matched causal tests. Against stronger teams, early
elimination/contact losses also matter. Use absolute/carried r100/r300 totals (eliminated team = 0)
alongside reached-round views to avoid survivorship bias. Do not infer that queen safety costs
growth: that earlier reading was withdrawn after correcting initial levels and map mix.

The recorded C++ turn budget is 100M points, typical incumbent cost ~13M. Additional search may
be useful, but turning up existing knobs did not reliably spend more compute. Measure the actual
export under the judge; native wall time is not its point cost.

Recent local RL evidence is newer than the handoff:

- `build/growth_rl/ppo/native-league-batch24-wallfocus/evaluation-update69-vs-u24-transfer/`:
  candidate score 0/32 Default/Devil, 1/48 Autarky/Maze/Trauma, 2/32 seen wall-map fixtures.
- `build/growth_rl/ppo/native-league-survival-focused/evaluation-update45-combined-seeds1701-1706/`:
  candidate score 18/192, across four controls.
- These compare against an old learned reference that often dies immediately. Growth deltas are
  **not gains over Bokuto 18**. The learner cannot be selected from those deltas.
- `tools/growth_rl/ppo.py` uses a small feed-forward network, local critic, terminal-result
  credit and later direct death penalties; no recurrent core or temporal GAE. It has 23 actions
  (four walks, sixteen two-step sequences, three split allocations), no sonar. Some current death
  penalties dwarf the +/-1 terminal reward. Do not continue reward sweeps as the main sprint.
- `tools/learn/ppo.py` is a separate encoder-v1 smoke prototype, not the new C++ option learner.

Preserve existing user work: `tools/growth_rl/__main__.py` and `tools/learn/README.md` are modified;
new PPO/winner-data tools and map files are untracked. Recheck `git status` at every handoff.
Do not overwrite, delete, stage, or commit unrelated changes as part of this sprint.
