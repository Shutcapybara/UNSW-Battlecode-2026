# cx-c status — early-game efficiency accounting (C1-C, GLM 5.3)

## 2026-09-29 (day 1): ledger delivered, no chassis yet

**State**: C1-A's chassis (`bots/cx-a01-chassis`) has not landed (no `cx-*` bot dirs or worktrees when this
session started), so today is the §1 accounting — per the task prompt, the deliverable that needs no chassis.
No `bots/cx-c01-eff` directory exists yet; no CANDIDATE.toml (nothing to register — no fix has been measured).
§2 fixes start the moment the chassis API is committed.

**Delivered**:
- `tools/analysis/c1c_ledger.py` — aggregates the F1 parquets (never re-decodes) over corpus ranked (C1-E
  cohorts), team-7 live (all 194 games of 28 Sep, our side, by submission), and the new local fixtures.
  Output: `docs/analysis/C1-efficiency-ledger.md` + `game_stats/efficiency_ledger.json`.
- `tools/analysis/c1c_frames.py` — portal transits + child first-pearl lag from the decode cache (our games).
- `build/c1c/features-team7` (194 games extracted; corpus replays are gzipped — staged gunzipped copies in
  `build/c1c/team7-src`, same workaround C1-E used) and `build/c1c/features-yuna` (120 fixtures:
  yuna-v03-core vs fenrir-v18 / kazuha-s01, 10 maps × both sides × seeds 1–3; driver
  `build/c1c/run_fixtures.py`; record 30–30 vs fenrir, 55–5 vs kazuha).
- Findings: `docs/findings/2026-09-30-cx-c01-eff.md` (ledger first, priority list, falsifier verdict, fix
  list with acceptance gates).

**Headline numbers**: length identity exact (len/pearl + sprint/pearl = 1). On Portals we out-eat the top ten
(16.4 vs 11.4 pearls/100dt at 6.0 vs 8.8 moves/pearl) and still lose 131.7 length/1k dt vs band 70.7 — the
deficit is leaks, not income/effort. Leak ranking (team7 − band, len/1k, r100): Portals trapped +62.6,
Portals newborn +47.7, Portals portal +24.1, Slithery trapped +23.2 / newborn +22.9, Portals crowd23 +21.9,
Schooltime trapped +21.2. Sprint tax 0.023/pearl vs band median 0 (only pooled outside-IQR mechanism).
Falsifier did NOT fire (4/54 pooled, 35/54 on Portals).

**Deferred**: idle turns, waiting-vs-travelling, contested/missed beds, field-cohort portal transits — need
frame-level data the parquets don't carry; the contested-bed statistic also needs C1-B's arrival rounds.
First-pearl lag was measured instead of assumed: median 5 rounds everywhere (not a differentiator).

**Next** (blocked on C1-A):
1. `bots/cx-c01-eff` on the chassis; fix order: trapped/mill escape → newborn siting → sprint discipline
   (portal exits are C1-D's, wall/kelp goes into C1-B's cost map).
2. Each fix = one `params.hpp` switch, measured alone on the 120-fixture grid (regenerate with
   `build/c1c/run_fixtures.py`), accepted only if it moves its statistic AND pearls r100.
3. `CANDIDATE.toml` for the accepted set; director registers for the dev screen vs 545.
