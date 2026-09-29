# C2-0 — fight anatomy from the corpus: is coordinated fighting worth building?  (model: **GLM 5.3**; issued 29 Sep 01:20 UTC)

Read first: `docs/hub/prompts/2026-09-29-C1-index.md` (shared rules), `claude/ten-day-plan-2026-09-29.md`
§"Deferred experiments" (S-3 is the item this task serves), `docs/findings/2026-09-30-cx-c01-eff.md` (h2h is the
one death cause the top ten do not zero: 5.5–7.4 per 1k for every cohort), `docs/analysis/F1-status.md` and
`docs/analysis/FEATURES.md` (the extractor; per-death and per-dragon tables exist). Analysis only: no bot, no
protocol design. Low priority behind C1-F; a day at most.

## 0. The question

At least one team reportedly nominates a leader to direct local attacks. Before anyone designs a protocol, find
out from ~9,000 corpus replays (`public_replays/corpus/`, index + `replays/`, cohorts from the ladder snapshots
as in C1-E) whether the top ten *fight differently* from the band — who initiates, whether groups commit together,
and what a fight costs each side — or whether their h2h numbers come from the same behaviour at a better economy.

## 1. Definitions (state them in the report; keep them simple)

- **Contact**: an enemy head within 4 cells (path distance through known terrain if cheap; Manhattan otherwise) of
  a friendly head.
- **Fight**: a contact where ≥ 3 friendly heads and ≥ 1 enemy head are within a 6-cell window, lasting until no
  contact for 5 rounds. Also record 1-v-1 and 2-v-1 contacts as separate classes.
- **Initiator**: the side whose head first moves to a cell adjacent to (or onto) an enemy head; **trade**: both
  die; **kill**: one dies; **disengage**: neither within 5 rounds.
- **Outcome over the next 10 rounds**: length lost per side, dragons lost per side, pearls eaten in the window by
  each side, whether the local bed cluster changed hands (nearest 3 beds' next eater).
- **Coordination signals** (observable, no payload decoding): number of friendly heads that move toward the fight
  centre in the 3 rounds before first contact; whether the group's moves are synchronised (same round) or
  staggered by id order; sonar rays fired by the group in those rounds (count only).

## 2. What to produce

Per cohort (top 10, ranks 11–30, band 55–85, team 7), pooled and by map class: fights per game; initiator share;
outcome mix (trade / kill for / kill against / disengage); length and dragons lost per fight per side; parity of
trades (the S1 rule: trades priced by production — who was ahead in units when they traded); the coordination
signals above; and the **win rate of games conditional on fight outcome** (does winning fights win games, or does
winning games produce won fights). Then the two comparisons that decide S-3: (a) top ten minus band on initiator
share and on "group moves toward contact before contact" — if the top ten initiate more and converge more, there
is a coordination behaviour to copy; if they simply fight less and trade only when ahead, S-3 is a pricing rule,
not a protocol; (b) team 7 minus band on the same, to say which of the two we lack.

## 3. Rules

Ranked games only; both sides pooled; no submission ids (D-023) — pool by team. Re-use the F1 extractor's frames
and per-death tables; add a `fights.py` under `tools/analysis/features/` rather than a new decoder. Small n per
map is fine; say it. No map-identity conclusions (out-of-sample rule): describe fights by local geometry
(corridor width, distance to nearest bed, portal within 3 cells), not by map name.

## 4. Report

`docs/analysis/C2-fight-anatomy.md` (tables + ten lines of reading + the S-3 recommendation in one sentence:
protocol, pricing rule, or nothing), `game_stats/fight_anatomy.json`, `claude/c2-0-status.md`. Falsifier for the
protocol idea: top ten and band initiate and converge at the same rates (then the difference is economy and
pricing, and S-3 is dropped).
