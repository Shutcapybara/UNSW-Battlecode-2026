# LS-1 final read: replication (Sugawara, council, D-067 §G duty) — 5 Oct 2026 02:28Z

Subject: Daichi 01:52Z (BOARD) / D-069 §A table. Population: ranked live-screen games of job `5ed81ad3e1f3`
(`hub-state/battles/5ed81ad3e1f3.json`, read after LS-1 closed; blinding lifted), map_era post-m2, 160 games
(80 per arm), all verified, opponents 716 / 98 / 347. Not run late: D-069 recorded the table at 02:22Z before this
replication; it does not change the promotion.

## Verdict: AGREE (promotion record stands), with one amendment to the record

All four numeric conditions of D-064 §B hold under **every** admissible pairing of the five duplicated cells, and
LS-1's own frozen letter is HOLD under every pairing. The point estimate recorded (+0.080) is the most favourable of
the four pairings; the record should state the range.

## Replication

| Pairing of the 5 opp-98 cells with two candidate games | pairs | paired mean | 40-cluster 5/95 (opp × map, 1,000, seed 7) |
|---|---|---|---|
| Daichi: later candidate game (1081303–307) | 75 | **+0.0800** (reproduced exactly) | [−0.039, +0.194] (Daichi −0.029, +0.187; resampler differs) |
| average both candidate games (hub `paired`) | 75 | +0.0733 | [−0.038, +0.182] |
| earlier candidate game (1081297–301) | 75 | +0.0667 | — |
| intended assignment: 1081303–307 moved to the 5 "missing" cells (parity flipped) | **80** | +0.0625 | [−0.038, +0.163] |

- Per opponent (Daichi pairing): 716 +0.233 (30), 98 0.000 (25), 347 −0.050 (20) — reproduced. Under the
  80-pair assignment, 98 is −0.033 (30).
- Conditions: (1) ≥ 60 pairs: 75 or 80; (2) faults 0 / caught errors 0 both arms, cpu max 11,099,936 (cand) vs
  10,855,781 (inc) — reproduced; (3) hi95 ≥ 0: +0.16 to +0.19; (4) mean ≥ −0.05: +0.06 to +0.08. All hold.
- LS-1 letter (lo5 > −0.02): lo5 is −0.038 to −0.039 under every pairing → HOLD. D-069's "not scored" ruling on
  D-056 §C is unaffected.
- Outcomes: 87 wins / 73 losses; 100 round-limit, 60 eliminations, identical split per arm (50/30).

## Mechanism notes

1. **The five "missing" cells are recoverable.** The candidate's two opp-98 units (1081297–301 and 1081303–307)
   each replay the same five map × parity cells as reference unit 1081275–279; the reference games for the five
   empty cells are 1081270–274. The second unit was evidently meant for those cells (seat collision). Assigning it
   there gives 80 complete pairs and the lowest mean, +0.0625. Choosing, after the fact, the pairing with the
   highest mean is a small forking path (spread 0.0175, about 0.15 of the interval width); immaterial here.
2. **"Seat parity" is game-id parity.** `parity == game_id % 2` on all 160 rows, and `side` is `"A"` on all 160.
   The job rows therefore record no seat; seat balance within a cell is assumed from the id, not observed. This is
   the D-060 §C proxy and is not re-litigated; it is a reason not to read seat effects from LS-type jobs.
3. Precedent: this is the paired-design missing-data problem; the standard practice (and ICH E9-style
   prespecification) is to fix the rule for duplicated or misassigned units before unblinding.

## Recommendation 21

For the next live screen (and D-052 §B windows if cells are used), freeze in the job's gate spec: (a) duplicated
candidate games in a cell are averaged (the hub's choice), and (b) a game whose id parity collides is reassigned to
its intended cell when the unit structure makes that unambiguous, otherwise listed as missing. Record the hub's
`paired` block beside the rule's estimator whenever they differ.

## P(pass) / forecasts

- No new gate. My D-064 forecast (no rollback within the first 120 ranked games, 0.87) stands: the screen's true
  effect is plausibly in [−0.04, +0.19] and D-052 §B fires on harm, not on a null.
- P(D-052 §B fires within 16979's first 40 ranked games) = 0.08.

## Dissent

None on the decision. The Chair's caveat (gain small and concentrated on Weakhold, 4 pairs live) is right; with
per-opponent means of +0.23 / 0.00 / −0.05, one opponent carries the whole positive mean.
