# Ladder state (Chair)

Kept by the Chair (Ushijima). Rules: `00-MACRO.md` §1 and D-046. A rung passes only when this file records it.

## Current state (4 Oct 2026 10:50Z)

- **R0 passed 4 Oct 14:28Z (D-053 §A). Rungs open: R1 (confirmation pending) and R2 (card pending).**
- Incumbent and parent: `carthage-05-free-sprint` (submission 14585). Fallback: `hb1-14-prior-r540` (14265).
- Deadline: handled by the lead; the Chair imposes no freeze (D-050 §2).
- GPU work may run on the Mac's shared memory, natively, under the heavy-job lock (D-050 §3).

| Rung | Adds | Status | Owner | Record |
|---|---|---|---|---|
| R0 | infrastructure | **passed** 4 Oct 14:28Z | Kageyama, Hinata, Asahi, Daichi | D-046, D-051 §5, D-052, D-053 §A |
| R1 | V0 value model | P-2: one confirmation on the manifest-v2 population (1,327 usable of 1,328); waits for the scorer revision with pinned ids and Tanaka's pass line. V0b is a privileged critic. P-6 (V-legal) in council round 2 | Hinata | D-052 §A, D-054 §A |
| R2 | P1 BC direction head | card P-5 in council round 2 (due 17:00Z); feature set under review (encoder v1 plus hb1's per-candidate features is the Chair's leaning); full teacher rows wait for the native executor | Hinata | D-054 §D |
| R3 | split/size, cull, sprint heads | not started | Learner | |
| R4 | feature blocks | not started | Data, Learner | |
| R5 | V in the search | needs a value model on the legal encoder (V-legal card after the decode, D-052 §A.7) | Hinata | |
| R6 | expert iteration | small scale only, by a later D-record | Learner | |
| R7 | CNN/GRU | allowed on the Mac's GPU (D-050 §3); only if the accuracy-per-KB curve shows the trees saturating | Hinata | |
| R8 | PPO league | allowed on the Mac's GPU (D-050 §3); only if R6 plateaus for two iterations | Hinata | |

## R0 exit checklist

| # | Item | Gate | Owner | Status |
|---|---|---|---|---|
| 1 | Post-m2 decode finished | every in-scope post-m2 game and all own games decoded | Kageyama (native Mac job) | **done**: 19,754 of 19,754 (13:55Z) |
| 2 | Frozen splits | manifests with hashes in `docs/learning/splits/` | Chair (maps), Kageyama (series, fixtures, row counts) | **done**: `kageyama-games-v2.json` (126,694 games, 28,602 series, sha ba21ac40…, 0 series across buckets, `consumed_by` column) and `kageyama-fixtures-v2.json` (sha a0385e85…); consumption tags re-checked by Tanaka on all rows |
| 3 | Observation encoder | Python = C++ bit for bit on 1,000 turns | Kageyama | **passed** (D-051 §5): 40,002 turns, 0 mismatches; re-run by Nishinoya on its own fixtures, 1,549 turns, 0 mismatches |
| 4 | Action labeller | agreement with HB-1 labels on Heartbreaker data > 99 % | Kageyama | **passed** (D-051 §5): 100 % of 75,306 Heartbreaker turns; re-run by Nishinoya, 100 % of 31,061 turns |
| 5 | Leakage audit | no held-out map, series or gate fixture in any training set | Kageyama | **passed**: 9 of 9 on manifest v2 (Kageyama), re-run by Nishinoya, 9 of 9; `smoke.parquet` rebuilt train-only |
| 6 | Registry in use | every artifact has an entry in `registry.md` | Chair keeps the file; owners add entries | file created |
| 7 | Gen twins regenerated from `maps/live/` | the swapped maps' twins rebuilt; stale twins excluded until then | Asahi | **done** (D-051 §5): four twins rebuilt in `maps/m2tr/`, on `main` |
| 8 | `battles.json` control and live monitor | built, tested, redeployed; `docs/learning/live.md` refreshing | Daichi | **done** (D-051 §5): redeployed with dispatch off; A/A job enabled by D-051; monitor hourly |
| 9 | `maps/live/` equals the server's maps | map text in post-m2 replays matches the templates | Kageyama | **closed with a limit** (D-053 §A): 36 of 38 texts match; the Schooltime open-4 and Dilemma 10-dragon variants have redacted bed layouts and cannot be rebuilt exactly; panels cover the template variant only |
| 10 | Interval convention frozen | Tanaka's audit note on D-046 §3 and §4.3 | Tanaka, then Chair | **done** (D-052 §C): map × opponent clusters, seats and seeds together; directional key as sensitivity |

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
| Cage C+D, E = 0 | carthage-05 | **parked** (D-053 §C): screen HOLD; the gated-reserve card P-3 rejected (map identity); live Schooltime is lost about equally with the cage open (−0.515, 27 games) and closed (−0.436, 24 games) | none | R3/R4 |
| H-KZ12 entry-capacity dial, k = 0/4/8/16 | carthage-05 | k = 16 nominated for the full gate on seeds 2–3 (D-053 §D); not started, Asahi idle since 13:50Z. Seed-1 gain is all Weakhold (15–1 against 8–8) | Asahi | R4 block "body-conditioned entry capacity" |

| Queen reach veto (H-KZ26), m ∈ {off, 0, 1} | carthage-05 | card P-4 approved for a seed-1 screen (D-054 §C), after the k = 16 gate | Asahi | R4 block "enemy sprint reach" |

## Log

- 4 Oct 10:50Z: D-046 opens R0. Engine identity across wheels 1.2.3, 1.2.5 and 1.2.9 checked by hash (D-046 §2).
- 4 Oct 10:52Z: D-047. Held-out maps frozen (Maze, Trauma, Trophy). P-1 numbered; council round 1 opened on its gate
  reading; the fit waits for the decode or 5 Oct 00:00Z.
- 4 Oct 15:36Z: D-054. P-2's population fixed at 1,327 usable games (scope from manifest v2). P-4 (queen reach veto)
  approved for a screen. Council round 2 on P-5 (R2) and P-6 (V-legal), due 17:00Z. Asahi idle; the lead asked to
  wake it.
- 4 Oct 14:28Z: D-053. **R0 passed.** H-KZ12 k = 16 nominated for the first full gate (seeds 2–3). P-3 rejected (map
  identity); cage work parked. H-KZ26 card requested. D-052 §E withdrawn (variants cannot be rebuilt).
- 4 Oct 13:18Z: D-052. P-2 confirmation terms frozen (spec sha 15d79683…). Rollback rule replaced by a difference
  form. Interval convention frozen. Cage E = 0 screen held. Two map variants to be added to the pool. R0 items 2, 5
  and 10 recorded; items 1 and 9 open.
- 4 Oct 12:22Z: D-051. A/A live job enabled. R0 items 3, 4, 7 and 8 recorded; items 1, 2, 5, 9 and 10 open.
  P-2 confirmation held until D-052 (Tanaka: reserved series in the training rows; Φ not frozen).
- 4 Oct 11:18Z: D-050. Seats named by the lead. No Chair-imposed freeze. GPU work allowed on the Mac. Quota-runner
  condition replaced by a ledger check. R0 items reported by Kageyama and Asahi; none recorded until merged and
  re-run; split manifest v2 requested on Autarky, Maze, Trauma.
- 4 Oct 10:59Z: D-049. Held-out maps corrected to Autarky, Maze, Trauma (Trophy was used in the 10:52Z development
  fits). P-1 closed as failed in development. P-2 is the R1 candidate; its confirmation waits for D-050.
- 4 Oct 10:55Z: D-048. Executor stays in shadow; battles control may deploy with dispatch off; A/A dry run first;
  rollback reference put to the council; Rome may run the cage E = 0 screen until an Evaluator lane exists.
