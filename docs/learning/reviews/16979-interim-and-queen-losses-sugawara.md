# 16979: interim D-052 §B residual and queen-rule losses (Sugawara, 5 Oct 03:35Z)

Unit 17. Not assigned; written under D-067 §G (replicate statistics-bearing claims) and the council's duty to flag a
likely rollback early. **This is not the D-052 §B look.** The rule has one look, at 40 ranked games; nothing here
changes it, and I recommend no action before it unless the lead chooses one (D-070 §A).

## 1. Daichi's contradiction is the queen rule: confirmed from the replays

`frame.decode` (tools/analysis/features) reads the replay header reason directly. All four games Daichi flagged
(1098984, 1098987, 1099081, 1099082) and both 14585 games (1092918, 1094553) end with reason **`queen`**: our original
queen (lowest initial id) is dead, theirs is alive (final lengths 3, 2, 11, 30, 3, 3). `tools/hub/executor.analyse_replay`
reports these as `roundLimit`, which is why the longest-dragon check looked contradictory. **D-070 §A's reading is
right.** Suggest the executor pass the header reason through, so no later scan repeats this.

## 2. Queen losses, 16979 against its parent (ranked, post-m2, team 7, by start time around 02:13Z activation)

| window | games | W–D–L | losses by `queen` | Schooltime | non-Schooltime queen losses / games |
|---|---|---|---|---|---|
| 16979, first 25 decoded | 25 | 8–1–16 | 10 / 16 | 3 games, 3 queen losses | 7 / 22 (32 %) |
| 14585, last 120 | 120 | 56–0–64 | 29 / 64 | 15 games, 15 lost (13 queen) | 16 / 105 (15 %) |

- **Schooltime is a sure loss for both binaries.** In the 91 most recent post-m2 team-7 Schooltime games I decoded
  (ranked and unranked, both seats), our queen dies by `self` at round 0 in **91/91**, and we win 1. This is the
  known cage (H-SZ1, my P-sugawara-01, parked). Schooltime drew 15 of the parent's last 120 ranked games (12.5 %),
  so the cage alone costs roughly 0.07 of residual per game in that window.
- Outside Schooltime, 16979 loses by the queen rule twice as often per game (7/22 against 16/105; binomial tail
  P(≥ 7 | 22, 0.152) ≈ 0.04, uncorrected, one look of mine). Mid-game queen deaths at r62–248. Small n; the queen is
  the mechanism of the shortfall either way, and k = 16 is not known to touch queen safety.

## 3. Interim residual (approximate, not the rule's frozen inputs)

D-052 §B construction: own rating fixed at 1725 (Daichi 02:55Z), opponent rating from the last ladder snapshot
before each game (`public_replays/corpus/ladder/*.json`, 10-min cadence; the rule uses game-time ratings), draw 0.5,
parent window = 14585's last 120 ranked games, series bootstrap, windows resampled independently, 1,000 × seed 7.

- 16979: **29 games, 6 series, mean residual −0.187**; 14585: 120 games, 24 series, −0.009.
- **Difference −0.178, 5/95 [−0.233, −0.122].** Both D-052 §B conditions (< −0.08; 95th < 0) hold now.
- To end above −0.08 at 40 games the next 11 must add about +1.9 of residual, i.e. roughly 10 wins in 11 against
  1550–1650 opponents.
- **Forecast revised: P(D-052 §B fires at the 40-game look) 0.75** (was 0.08 at 02:28Z, before any game). The old
  forecast will score badly; it assumed 16979 ≈ 14585 + noise, and the queen-loss rate above says the first 25
  games are worse than noise alone would explain, or the map draw is unlucky (Schooltime 3/25).

## 4. Mechanism notes

- The residual uses our rating fixed at 1725 while we fell to 1633: every later opponent is rated below us, so
  E ≈ 0.65–0.80 and a 50 % record reads as −0.2. That is the rule's design (Tanaka's anchor point), not a flaw.
- If the rule fires, the rollback restores 14585, which has the same Schooltime cage. Neither binary addresses
  the largest single loss source; Kenma's `pocket-queen` is the only bot in the programme that claims to.
- Replication inputs: `public_replays/corpus/index.jsonl` (game ids 1098984–1102450 and later), replays, ladder
  snapshots. Code run inline (VM disk full; nothing written to other lanes' dirs).

## Precedent

Halite/Lux post-mortems: a single deterministic opening failure on one map routinely outweighs policy tweaks;
the fix is a structural safety check (here H-SZ1: when every queen move is fatal, split rather than move), not a
map rule (_common.md l.21).
