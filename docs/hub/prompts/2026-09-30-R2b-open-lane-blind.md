# R-2b — Open exploration lane, blind (Opus 5.5, desktop, Claude Code) — lane `rb`, lineage **Basquiat**

Host: the Ubuntu desktop, `~/Documents/Projects/2026/UNSW-Battlecode-2026` (the only checkout; never `~/Projects`), venv `.venv`, `--jobs $(( $(nproc) - 2 ))`.
Branch `r/rb`, worktree `../wt-rb`, bots `bots/basquiat-<nn>-<slug>/`, tools `tools/rb/` (copy `tools/ra/lane.py`,
`variant.py`, `score.py` from `tools/ra/` and `tools/lune/score.py`; the scoring code is not the experiment).

## The one rule that makes this lane different

**Do not read the programme's conclusions.** Not `docs/hub/HYPOTHESES.md`, not `docs/findings/`, not `claude/*-status.md`,
not `docs/TEAM-SUMMARY-*.md`, not the other lanes' reports or their bot READMEs. The point of this lane is an
independent draw of ideas; if you read what the other lanes concluded you will reproduce their search. You may
read: the game documentation (`docs/game/` or https://game.battlecode.au/docs/), `docs/analysis/BENCHMARKS.md`
(the yardstick — required), the base bot's source, replays you generate, the corpus replays under
`public_replays/` if present, and the harness tools. If you find yourself opening a findings file, close it and
note it in your status file.

## Base and gate

- Base: `bots/lune-r1-07-latecap8x-only` copied verbatim to `basquiat-00-base` (Ares lineage, C++; a `params.hpp`
  bot; golden-harness parity with `tools/cx/golden.py replay --all` before anything else). Then, as your first
  version, set `devil_center_bonus`, `devil_lane_bonus` and `ally_body_buffer` to inactive (they are keyed on
  `W==32 && H==16`; treat that as forbidden map identity) — that is `basquiat-01-nodevil`, and it is the parent for
  everything after. No decision may depend on map dimensions, names or hashes; measured structure is fine.
- Gate (revised, D-032): each candidate vs its parent on **paired fixtures, seeds 1–3, live pool (z1) and the
  generalisation panel (`maps/new/*`, `maps/var/*_tr`)**, both seats — ~480 + ~700 games, about 25 minutes here.
  **Accept** when the bootstrap 90 % lower bound of Δ(economy mean) on the pool is > 0, the generalisation-panel
  Δ(economy) lower bound is > −0.02, units@100 and length@100 lower bounds are not < −0.02, no tier-2 death rate up
  > 10 %, and the panel win rate is not down (lower bound > −0.02). Report per-checkpoint deltas (p@50/100/150/250)
  as well as the mean, because a change that acts only late is judged on the checkpoints it can move, with the
  earlier ones as guards. A hold (hygiene better, economy flat) is logged and re-tested stacked later.
- One mechanism per version, one switch, expected sign stated before the run, the parent reproducible from the
  same source. CPU probe (`arena.py --sandbox`, four dense fixtures) for anything that adds computation; the
  budget is not a constraint you will hit, but report the max.

## What to do

Play the bot. Watch replays (`unswbc` produces them; the visualiser renders them). Form your own view of where
it wastes pearls, dragons and length, and why it loses the games it loses on the ten pool maps and on the
unseen suite. Then change one thing at a time and measure. Sources of ideas you may use freely: the game rules,
the bot's own code, chess-engine practice (evaluation terms, search shaping, phase handling), your own
replay reading. Keep a running table in `claude/rb-status.md` (version, mechanism, pool Δ with interval,
generalisation Δ, CPU max, verdict, one line of why) updated after every version, and a report
`docs/findings/2026-10-0x-rb-lane.md` at every fifth version: what was tried, what stuck, what the accepted stack
adds up to against `basquiat-01-nodevil`, and which *kinds* of mechanism paid. Every accepted version gets a
`CANDIDATE.toml` (`language = "c++"`, lineage `basquiat`, `lineage_parent` = previous accepted). Commit and push
`r/rb` after every version (`gh auth setup-git` is done on this host). Do not register anything yourself.

You will be told when the lane is stopped; until then, keep going.
