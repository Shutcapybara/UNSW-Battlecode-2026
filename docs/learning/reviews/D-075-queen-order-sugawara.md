# D-075 §D — queen build order after Bokuto's pool (Sugawara, queen owner, 5 Oct 2026 05:30Z)

Answer to the Chair's D-075 §D request (move Bokuto's caution/crown block beside or ahead of q2a, or say why not).

## Verdict: amend my 04:38Z order — Bokuto's queen block goes ahead of q2a, isolated, on carthage-05

New order (each one switch, seed-1 pool with queen columns, same host as Asahi's cards):

1. **`sugawara-q1-cage`** unchanged in content, but on **carthage-05** (live incumbent 14585 since 04:53Z), not k16.
2. **`sugawara-q2b-crown`** = carthage-05 + **only** the bokuto-04 queen block from `wt-bokuto/bots/bokuto-04-queen/policy.hpp`
   (diff against carthage-05 is ~30 lines, all marked `// bokuto-04`): `is_queen` + `QueenParams`
   (no queen SPLIT after r60, two call sites; threat ×3; danger penalty 6 on cells an enemy head reaches next turn;
   dive penalty 40; no queen attack; no queen prey role), the crown lines (queen claims the crown at r ≥ 250;
   a live queen keeps it; feeders feed a queen crown regardless of `feed_min_crown`). **Excluded:** `bokuto.hpp`
   (bokuto-02 survival guard + cage split + reserve slot), `bokuto_branch.hpp` and the two `branch_allowed` lines
   (bokuto-03), the `main.cpp` guard hook. Bokuto's tree is not edited; Asahi copies.
3. **q2a (grow, split floor 12) is parked.** q2b's "no queen split after r60" subsumes it; q2a returns only if q2b's
   economy cost is ≥ 3 pp and the split rule is the cause.
4. The **68-game queen-keeper panels** (vs `bokuto-04-queen`, vs `kenma-03-pocket-queen`; 17 maps × 2 seats, seed 1)
   run for carthage-05 and k16 first (D-075 §D order), then for q2b.

## Why (replication from frozen inputs)

Re-read of Asahi's seed-1 pool index files (`wt-asahi/build/asahi/runs/<bot>/<fp>/pool/index.jsonl`; bokuto-04 ff68a709,
carthage-05 7df05a3f, k16 43bd2d4f, kenma-03 e60733a9; 272 fixtures each, paired on map × opponent × seat; 0 missing).
Reasons in the files: `longer queen` = round-limit queen comparison (dead queen = 0).

Paired outcome table, bokuto-04 (rows) × carthage-05 (cols); q = decided by `longer queen`:

| | c05 W | c05 L | c05 Lq |
|---|---|---|---|
| bokuto W | 157 | 23 | 4 |
| bokuto Wq | **38** | 3 | 1 |
| bokuto L | 28 | 14 | 0 |
| bokuto Lq | 3 | 1 | 0 |

- **Of bokuto-04's 42 queen-decided wins, 38 are fixtures carthage-05 also won.** Only 4 are rescues. The pool's queen
  columns measure *how* bokuto wins, not what the queen block adds: the pool's opponents rarely keep a queen, so a
  kept queen converts wins c05 would have taken on `longest dragon`. Asahi's 04:53Z line ("pays for itself in wins
  against c05") is not supported by the pairing; the parity is **31 gains vs 31 losses — 62 of 272 fixtures (23 %)
  discordant**. Gains: Tower Defense 6, Islands/Schooltime/Trophy/Weakhold 5 each. Losses: Default 5, UNSW 5, QoS 4;
  21 of 31 losses by `longest dragon` (economy), opponents yuna-v05 7, hunter-v20/kazuha-s01/ouroboros-m01 4 each.
- bokuto-04 stacks three layers on carthage-05 (guard, branch gate, queen block). The 23 % churn is far larger than a
  queen-only switch would produce (c05 vs k16 differed on 33 of 816 fixtures, 4 %). **The pool cannot say which layer
  carries the economy cost (−6.3) or the Weakhold/Trauma gains.** Weakhold and Trauma are bokuto-03's branch-model maps;
  Schooltime is bokuto-02's cage split. So "the broad mechanism has the evidence" is true of the bot, not yet of the block.
- Kenma-03 for comparison: 13 queen wins, all 13 on fixtures c05 won; discordant 17/272 (6 %).
- Same reading vs k16: bokuto-04's 42 queen wins, 38 on k16 wins.

So the block is worth building **because** it is the only part of Bokuto's queen keeping we can test as one switch, and
its prize can only be read on the keeper panels and the ladder, not on the pool.

## Mechanism checks

- Legality: `is_queen = (w.me & 4095) <= 1` is the structural id rule (D-072 §C; ids 0/1 on all 16 live maps); the crown
  election uses existing crown messages; nothing beyond turn-start observation. OK. `_common.md` l.21: no map identity. OK.
- Parent: carthage-05 is bokuto-04's own base, so the block ports byte-exact; onto k16 it would need a merge with the veto
  (`!is_queen` guards touch the same attack branch). With k16 rolled back and its veto a suspect for queen exposure
  (D-075 §A, third explanation), build on c05; k16 + block only if the k16 panel is clean.
- Simpler known method: "the king does not leave the castle" — a separate guarded king unit is standard in Halite-era
  and Lux season-1 bots (protect the critical unit; trade economy for survival). Hungry Geese has no analogue.
- Train/deploy skew, leakage: none (hand-written rule, no learned part).

## Forecasts (owner's, not council; for my own record)

- q2b pool not below carthage-05 (paired 5th pct > −5 pp): **0.55**; Δwin point estimate −2 pp.
- q2b pool queen-decided wins ≥ 25: **0.60**; of them on c05 non-wins ≤ 5: 0.75.
- q2b beats carthage-05 on the bokuto-04 keeper panel by ≥ +5 pp: **0.40**.

## Dissent / risks

- The block's "threat ×3 and no attack" may be what costs QoS/UNSW; if so the fix is a phase gate (block only after r250),
  a second switch, not part of q2b.
- The pool will under-read the prize of every queen change. If the ladder trials (17388, bokuto-04) are the deciding
  measurement anyway, q2b's pool + panel are a screen for the next trial slot, not a promotion case.
