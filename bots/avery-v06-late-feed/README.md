# avery-v06-late-feed — current lineage tip

**Lineage:** avery · **Parent:** avery-v05-strict-crown.

## Hypothesis

The v05 run's round-500 losses were mostly **long** length races, not close
ones: against the ouroboros/tew cluster our longest dragon finished at 5–17
while fed enemy crowns hit 27–44 (stronghold 8v42, trauma 6v15, devil 14v37,
queen_of_spades 14v28). The strict crown banks but is never **fed**. Feeding
mechanics are proven by ouroboros-v09/v10 and drake-v02; v04's feeding
failure was early/broad (from round 200 with many crowns — the economy
froze). Late, strict feeding should convert surplus units into crown length
without touching the economy.

## Changes vs v05

- `feed_start=410` (30 rounds after voluntary splits stop): non-crown
  dragons with `LEN <= feed_max_len=10` home to the freshest known crown
  (self-report ≤ 3 rounds, or relayed beacon ≤ `feed_beacon_memory=6`) and
  **die in place** once within `feed_dist=2` (deliberate missing action;
  corpse deposits ceil(len/2) pearls beside the crown, which eats them).
  Homing range `feed_range=16`; feeders only move when the crown is known
  longer than them.
- From `feed_start`, non-crowns value pearls/spawns at 25% (leave them for
  the crown); the crown keeps full value.
- `protocol.py`: `write_reply` accepts `command None` (deliberate no-action
  death), ported from drake-v02 — the only adapter change in the lineage.

## Results

Run `experiment_data/avery-v06-late-feed_20260925075329034170` (132 games,
6 opponents — gauntlet-5 plus tew-v12-mid-support, native, both sides,
11 maps, config `avery-gauntlet.toml`). All six opponent directories verified
byte-identical to the v05 run's frozen sources.

| Opponent | v06 W–L–D | v05 W–L–D |
|---|---|---|
| ouroboros-v10-beacon | **16–6** | 15–7 |
| hunter-v14-cpp | **16–6** | 12–10 |
| hunter-v20-portal-scouts | 12–10 | **14–8** |
| fry-v14 | **18–4** | 16–6 |
| kraken-v04-eval | 17–4–1 | 18–3–1 |
| **gauntlet-5 total** | **79–30–1 (72.3%)** | 75–34–1 (68.6%) |
| tew-v12-mid-support | **10–12** | 9–13 |

All 17 flipped games are round-500 length races — 11 won (margins up to
+23), 6 lost (all narrow: 45v47, 29v31, 12v17, 7v11, 5v6, one 0-margin
tiebreak). **Zero elimination outcomes flipped either way**: the mechanic
only touches the endgame race. r500 losses dropped from 51% of round-limit
games (v05, full roster) to 30% (20/66). Feed-deaths appear in stats as
`invalid_action_deaths`/`suicides` (676) — all deliberate.

Big-map crowns now reach 45 (big_empty, was ~31). Remaining length-race
losses concentrate on **stronghold B** (17v48 vs ouroboros/tew, 10v44 vs
kraken), **devil B** (17v33) and **trauma** (0–2 margins): compact maps
where the enemy crown out-farms/out-feeds ours. Crown survival/growth on
compact maps is still the open problem.

## Open questions for v07+

1. Compact-map crown race: stronghold-B/devil-B losses by 30+ segments
   remain. Ideas: earlier crown on compact maps (enemy crowns start banking
   ~200), crown farm anchoring near dense beds, feeding from 380.
2. hunter-v20 regression (14–8 → 12–10, two narrow r500 losses): watch on
   the next run; not elimination-driven.
3. tew cluster is ouroboros-ladder variants (tew on-disk code IS
   ouroboros-v13-ladder with per-version `defaults.py`); treat them as one
   cluster, and re-verify hashes before trusting a "tew" number.
4. team_kills still ~42% of deaths (5891/13992); target-claim packets
   untried.
5. Sandbox CPU validation still never done for avery (all runs native;
   this run: 132/132 recorded, runtime_faults=0).
