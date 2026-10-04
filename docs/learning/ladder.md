# Ladder state (Chair)

Kept by the Chair (Ushijima). Rules: `00-MACRO.md` §1 and D-046. A rung passes only when this file records it.

## Current state (4 Oct 2026 10:50Z)

- **Rung: R0, open.**
- Incumbent and parent: `carthage-05-free-sprint` (submission 14585). Fallback: `hb1-14-prior-r540` (14265).
- Deadline: handled by the lead; the Chair imposes no freeze (D-050 §2).
- GPU work may run on the Mac's shared memory, natively, under the heavy-job lock (D-050 §3).

| Rung | Adds | Status | Owner | Record |
|---|---|---|---|---|
| R0 | infrastructure | **open**; most items reported done on lane branches, none recorded yet | Kageyama, Hinata, Asahi, Daichi | D-046, D-050 |
| R1 | V0 value model | P-1 (GBT) failed in development; P-2 (logistic) passed its own gate in development; confirmation on held-out maps waits for D-050 and the decode | Hinata | D-047, D-049 |
| R2 | P1 BC direction head | not started; offline work may run in parallel with R1 (D-047 §3) | Hinata | |
| R3 | split/size, cull, sprint heads | not started | Learner | |
| R4 | feature blocks | not started | Data, Learner | |
| R5 | V in the search | not started | Learner | |
| R6 | expert iteration | small scale only, by a later D-record | Learner | |
| R7 | CNN/GRU | allowed on the Mac's GPU (D-050 §3); only if the accuracy-per-KB curve shows the trees saturating | Hinata | |
| R8 | PPO league | allowed on the Mac's GPU (D-050 §3); only if R6 plateaus for two iterations | Hinata | |

## R0 exit checklist

| # | Item | Gate | Owner | Status |
|---|---|---|---|---|
| 1 | Post-m2 decode finished (queue 7,617 at 10:30Z and growing; Nishinoya probe 1, unaudited) | every in-scope post-m2 game and all own games decoded | Kageyama (native Mac job) | running since about 11:13Z, started by the lead |
| 2 | Frozen splits | manifests with hashes in `docs/learning/splits/` | Chair (maps), Kageyama (series, fixtures, row counts) | held-out maps frozen: Autarky, Maze, Trauma (D-049). Kageyama's v1 manifests used the earlier set; v2 requested (D-050 §5) |
| 3 | Observation encoder | Python = C++ bit for bit on 1,000 turns | Kageyama | reported: 40,002 turns, 0 mismatches (`r/kageyama`); recorded after merge and Nishinoya's re-run |
| 4 | Action labeller | agreement with HB-1 labels on Heartbreaker data > 99 % | Kageyama | reported: 100 % of 75,306 turns; recorded after merge and Nishinoya's re-run |
| 5 | Leakage audit | no held-out map, series or gate fixture in any training set | Kageyama | reported: 9 checks; re-run on the v2 manifest |
| 6 | Registry in use | every artifact has an entry in `registry.md` | Chair keeps the file; owners add entries | file created |
| 7 | Gen twins regenerated from `maps/live/` | the swapped maps' twins rebuilt; stale twins excluded until then | Asahi | reported: four twins rebuilt in `maps/m2tr/` (`r/asahi`); recorded after merge |
| 8 | `battles.json` control and live monitor | built, tested, redeployed; `docs/learning/live.md` refreshing | Daichi | control built on `r/daichi` (14 tests), not deployed, dispatch off (D-048); monitor first read posted 10:50Z |
| 9 | `maps/live/` equals the server's maps | map text in post-m2 replays matches the templates | Kageyama | 4 server games reproduced turn for turn (engine and map agree, up to a spawn-seat swap); corpus-wide check open |
| 10 | Interval convention frozen | Tanaka's audit note on D-046 §3 and §4.3 | Tanaka, then Chair | open |

Items 3–5 are the macro's offline gate for R0. Items 1, 2 and 6–10 are prerequisites the Chair added in D-046.
What each blocks: items 1–5 and 9 block the offline gates of R1 and R2; items 7 and 10 block panel gates; item 8
blocks live screens.

## R0 design constraints (adopted from the council intake, Sugawara 10:40Z)

1. **Encode from the IO round block.** The encoder is `encode(block_lines, process_memory)`: its input is the round
   block each dragon process legally received (view, inbox, echoes), rebuilt by
   `tools/team_recon_claude/roundblock.py` through the `recon` callbacks (the hb1 path). C++ parity comes from feeding
   the same block text to the bot's parser. Before use, re-check the block builder against protocol 3 and the
   current sonar rules (tail exit; the last send per direction wins).
2. **Queen-knowledge features from own-view history only** at R0–R2, in training and in deployment. Teachers' sonar
   payloads are unreadable to us, so filling these features from our own relays at deployment would be a
   distribution shift made by the encoder. Echo counts are included from the start. Sonar-relayed knowledge is its
   own R4 block, trained on our own games and self-play.
   - Falsifier: on our own post-deploy games, if view-only and sonar-filled queen-knowledge features agree on more
     than 95 % of turns, the separation is unnecessary.
3. Future-dependent analysis fields are labels only, never inputs (Himeji H23-05, H24-03).

## Outside the ladder (temporary hand rules, D-044 §3)

| Arm | Parent | State | Next | Learned replacement target |
|---|---|---|---|---|
| Cage C+D, E = 0 | carthage-05 | Asahi's P-A01, seed-1 screen queued behind the parent panel. Rome's package screens with E = 1 and E = 3 are HOLD. Live residual on Schooltime −0.45 [−0.52, −0.37] | Asahi | R3/R4 |
| H-KZ12 entry-capacity dial, k = 0/4/8/16 | carthage-05 | Rome: k = 4 seed 1 only (pool 0.8309 → 0.8456, current gen 0.7200 → 0.7225), no verdict. Asahi's P-A02: k = 16 exposure capture first | Asahi | R4 block "body-conditioned entry capacity" |

## Log

- 4 Oct 10:50Z: D-046 opens R0. Engine identity across wheels 1.2.3, 1.2.5 and 1.2.9 checked by hash (D-046 §2).
- 4 Oct 10:52Z: D-047. Held-out maps frozen (Maze, Trauma, Trophy). P-1 numbered; council round 1 opened on its gate
  reading; the fit waits for the decode or 5 Oct 00:00Z.
- 4 Oct 11:18Z: D-050. Seats named by the lead. No Chair-imposed freeze. GPU work allowed on the Mac. Quota-runner
  condition replaced by a ledger check. R0 items reported by Kageyama and Asahi; none recorded until merged and
  re-run; split manifest v2 requested on Autarky, Maze, Trauma.
- 4 Oct 10:59Z: D-049. Held-out maps corrected to Autarky, Maze, Trauma (Trophy was used in the 10:52Z development
  fits). P-1 closed as failed in development. P-2 is the R1 candidate; its confirmation waits for D-050.
- 4 Oct 10:55Z: D-048. Executor stays in shadow; battles control may deploy with dispatch off; A/A dry run first;
  rollback reference put to the council; Rome may run the cage E = 0 screen until an Evaluator lane exists.
