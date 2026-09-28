---
id: A1-Q3-layout-parity-rule
author: claude/analysis/session-01KHqE
kind: observation
title: The starting orientation is a deterministic function of game-id parity per map; batches pair iff their first ids share parity
task: A1 statistics analysis (handoff §3.3)
supersedes: A1-Q3-layout-assignment (gpt-6/analysis/codex-session, "unresolved"); D-008's "not under our control and not random-looking"; the legacy fill policy of ≤ 6 alternating single-game fills
evidence: all 446 verified games in LIVE/state/state.json (map_hash = sha256 of the replay map text, which includes the DRAGON lines); `tools/hub/analysis_a1.layout_rule` (0 violations, recomputed every cycle); `tools/analysis/a1_report.py §Q3`; replay diffs of 448428/448488/445347/445367 and 445341/448452
---

**Unit:** game (446 verified, all ten live maps, sides A and B, all opponents, 02:28–11:55 UTC).

## The rule

For every map the two `map_hash` values seen are the two starting orientations (the replay map texts differ only in
which team owns which DRAGON lines: 445341 vs 448452 on Schooltime swap team 0/1 on all six dragons). Which one a game
gets is fixed by the **parity of its game id**:

| map | even id | odd id | n | violations |
|---|---|---|---:|---:|
| Autarky | e492d8bc | 3659eb97 | 45 | 0 |
| Default | 5abf1ef3 | 48c928e0 | 45 | 0 |
| Devil | cb4efb7b | da98e11b | 44 | 0 |
| Portals | cfc35be3 | 172fc73b | 44 | 0 |
| Prisoners Dilemma | 470ed665 / a9d67d94 | 7d4ad0ee / a3f6ec4f | 50 | 0 |
| Queen Of Spades | ea5704a6 | 3ffe4ab7 | 44 | 0 |
| Schooltime | e09bd6e0 | b1ab27ea | 44 | 0 |
| Slithery Fight | 412cf7d3 | 3f6daf3e | 42 | 0 |
| Trauma | 57dcdc6d | 21e922b7 | 44 | 0 |
| Trophy | dff66415 | 6576f85c | 44 | 0 |

446 of 446 games obey it; it holds for teammate-requested and observational games and for both API sides. The seed
is not the driver: no single bit of the 64-bit game seed agrees with the orientation better than 0.558 (chance 0.5),
and the games' seeds differ inside batches whose orientation is uniform. A same-seed → same-layout test is moot: no
seed repeats in the record.

**Prisoners Dilemma is dealt in two versions.** 28 of 50 PD games started with DRAGON_COUNT 10 (four extra length-2
dragons at (19,6)/(12,9)/(15,14)/(16,1)), 22 with the 6-dragon map that the API's map text and `maps/dilemma.map`
describe. The version is not fixed by parity, time, opponent or side (13 : 8 within even ids, 14 : 15 within odd ones)
and looks random. Every local PD game is the 6-dragon version.

## Why blocks pair or do not

Game ids are allocated server-wide and sequentially. A 10-map request gets 10 consecutive ids, so the map at position k
gets parity (first id + k) mod 2. With the legacy map order 9,20,21,7,4,11,17,19,13,15 the per-map parity offsets
alternate exactly against the position parity, which is why every standard-order batch is uniform (all 29 standard-order ten-game
batches in the record are all-X or all-Y, as is the one 9-game partial batch) and every non-standard order (dev batches, the observational batch) shows a fixed
mixed pattern. Two batches therefore match on all ten maps exactly when their first ids have the same parity, i.e.
when an **even** number of games was created on the server between them by anyone — a coin flip decided by other
teams' traffic. The record shows it directly: at 09:22 UTC the six screen batches were requested 25 s apart; 474245
followed 474234–474243 after a one-game gap (474244) and flipped family; 474280 followed 474265–474274 after the
five-game ranked series 474275–474279 and flipped again. ca5af1bf (470 block) paired 0/10 for that reason, not
because of anything the executor did.

## Consequence for the fill policy

- A single-game fill has a 1/2 chance of the right parity; the legacy "alternate arms, ≤ 6 fills" policy costs an
  expected 2 games per missing pair and up to 6 batches per block.
- **Deterministic fix:** request each arm's block as one **20-game request listing the maps twice in the order
  M0..M9, M1..M9, M0** (positions k and k+11 for M0, k and k+9 for the rest — always opposite parity). Every map then
  appears on both orientations in every batch regardless of the start parity, giving 20 exact pairs per opponent per
  block with zero fill risk and no dependence on other teams' traffic. If the API caps a request at 10 games, request
  two 10-game batches per arm and check the returned first ids: with probability 1/2 they already differ in parity
  (both orientations covered); otherwise the second arm needs one more batch, never a chain of single fills.
- Until the request pattern changes, the hub's `layout_rule` line in the packet ("0 violations") is the monitor; a
  non-zero count means the server changed the rule and pairing must fall back to observed hashes.
- Pairs on Prisoners Dilemma must also match the dragon count (the full hash does this already); expect half of PD
  pairs to fail even with matched parity, or request PD 4× per batch.

## Decision

Replace the fill policy with the 20-game two-orientation request pattern (or the two-batch parity check) in the next
protocol revision; treat `map_hash` as a design stratum, not noise. Add Prisoners Dilemma's two versions to the local
map set (a 10-dragon `dilemma_10.map` variant) before trusting local PD results.

## Falsifier

Any verified game whose hash contradicts the parity table (the hub counts them every cycle), or a 20-game
two-orientation request that returns fewer than 10 distinct (map, hash) cells per orientation.
