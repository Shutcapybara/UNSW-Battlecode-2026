# Kyoto status — P2 tester (GLM 5.3)

Prompt: `docs/hub/prompts/2026-10-01-P2-tester.md`. Branch `r/kyoto`, worktree `../wt-kyoto`, bots
`bots/kyoto-*`, tools `tools/kyoto/`, findings `docs/findings/2026-10-01-kyoto-*.md`.

**Host deviation:** rostered for the desktop but running on the **Mac** (no desktop access from this
session): 18 cores, panels at `nice 10`, jobs 12, ~280–290 games/h, shared with the hub + antioch.
Engine `unswbc 1.2.3` (hub venv). Base per prompt: `hb1-14-prior-r540` with the `W==32 && H==16`
terms off (D-033) = `kyoto-01-nodevil`.

## Running table

| version | change vs parent | verdict | pointer |
|---|---|---|---|
| kyoto-00-base | byte-copy of hb1-14-prior-r540 | golden parity ✓ (devil A s1: 657 turns, 0 divergent) | — |
| kyoto-01-nodevil | shape_terms=false (renoir-23 form) | **the lane zero**; D-033 cost arm vs kyoto-00 at s1 running | unit-1 finding |
| kyoto-02-queenguard | H-Q1 combined queen guard | **SHELVED** — carthage claimed H-Q1 first (board 23:15 ACST); probes: queen death r41→r171/r214, killers enemy-h2h + ally-body | this file |
| kyoto-03-latecap | search_cap_late 48→160, sparse 64→512 (lune-r1-07 effective profile on the prior base) | running after the zero; expected p@150/250 up, p@50 flat | unit-1 finding |

## Unit 1 (1 Oct) — base under 1.2.3, queen measurements, first analyst item

- Setup: worktree + `tools/kyoto/lane.py` (rc copy, scoring/gate code identical — only paths/hosts
  differ) + `tools/kyoto/gen_reference.json` (rc's frozen renoir-00 medians) + `tools/kyoto/queen.py`
  (antioch's row logic, engine-verdict truth via `tools.antioch.era.header`).
- Golden parity before any change: `tools/cx/golden.py` devil-A-s1, 657 turns / 13 dragons, 0
  divergent. Nodevil patch verified surgical: default-A-s1 14,477 turns 0 divergent (inert
  off-shape), devil diverges from turn 6 (active).
- Queen id scheme verified on 1.2.3 replays: ids interleave by team parity from r0 (A even from 0,
  B odd from 1) → the queen is id 0 (A) / 1 (B), knowable in-bot (`ct.get_id()`).
- Engine checks in own replays: verdict strings carry the new tiebreak (queen first); sprint pricing
  check = `tools.antioch.era.signals` aggregate over the run (see finding).
- Items: (a) zero = kyoto-01 both panels seeds 1–3 + kyoto-00 s1 for the D-033 cost; (b) queen rows
  on the zero's replays; (c) first analyst item H-Q1 was claimed by carthage → took the cap-lift
  (H-1 ranked #4 flavour) instead; kyoto-02 shelved with a board note.
- Frame-patch caveat: lane win shares use frame.py's inferred winner (old-rule longest→total) until
  the director applies antioch's `frame-engine-verdict.patch`; queen/endgame numbers here use the
  engine verdict directly (exact).

## Resume

```sh
cd ../wt-kyoto
tail -f build/kyoto/logs/queue.log build/kyoto/logs/queue2.log   # queue.sh: kyoto-01 s1-3 then kyoto-00 s1; queue2: kyoto-03
PY=/Users/alik/Documents/Projects/UNSW-Battlecode-2026/.venv/bin/python
$PY tools/kyoto/lane.py score kyoto-03-latecap --parent kyoto-01-nodevil --seeds 1,2,3   # also try --phase late
$PY tools/kyoto/queen.py --run kyoto-01-nodevil        # queen rows + sprint-era spot check
```
