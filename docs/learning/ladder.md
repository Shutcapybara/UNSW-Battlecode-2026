# Ladder state (Chair)

Kept by the Chair (Ushijima). Rules: `00-MACRO.md` §1 and D-046. A rung passes only when this file records it.

## Current state (4 Oct 2026 10:50Z)

- **Rung: R0, open.**
- Incumbent and parent: `carthage-05-free-sprint` (submission 14585). Fallback: `hb1-14-prior-r540` (14265).
- Deadline: assumed 2026-10-11 10:30Z until the lead answers (D-046 §1). No new mechanism types after 8 Oct 10:30Z.

| Rung | Adds | Status | Owner | Record |
|---|---|---|---|---|
| R0 | infrastructure | **open** | Data, Learner, Evaluator, Live ops | D-046 |
| R1 | V0 value model | not started (card may be written during R0) | Learner | |
| R2 | P1 BC direction head | not started (card may be written during R0) | Learner | |
| R3 | split/size, cull, sprint heads | not started | Learner | |
| R4 | feature blocks | not started | Data, Learner | |
| R5 | V in the search | not started | Learner | |
| R6 | expert iteration | small scale only, by a later D-record | Learner | |
| R7 | CNN/GRU | deferred (no GPU) | | |
| R8 | PPO league | deferred (no GPU) | | |

## R0 exit checklist

| # | Item | Gate | Owner | Status |
|---|---|---|---|---|
| 1 | Post-m2 decode finished (queue 7,617 at 10:30Z and growing; Nishinoya probe 1, unaudited) | every in-scope post-m2 game and all own games decoded | Data (native Mac job; the lead starts it if the VM cannot) | open |
| 2 | Frozen splits | manifests with hashes in `docs/learning/splits/`, approved in D-047 | Data proposes, Chair approves | open; constraints frozen in D-046 §3 |
| 3 | Observation encoder | Python = C++ bit for bit on 1,000 turns | Data (Python), Learner (C++) | open |
| 4 | Action labeller | agreement with HB-1 labels on Heartbreaker data > 99 % | Data | open |
| 5 | Leakage audit | no held-out map, series or gate fixture in any training set | Data | open |
| 6 | Registry in use | every artifact has an entry in `registry.md` | Chair keeps the file; owners add entries | file created |
| 7 | Gen twins regenerated from `maps/live/` | the six swapped maps' twins rebuilt; stale twins excluded until then | Evaluator | open |
| 8 | `battles.json` control and live monitor | built, tested, redeployed; `docs/learning/live.md` refreshing | Live ops | open |
| 9 | `maps/live/` equals the server's maps | map text in post-m2 replays matches the templates | Data | open |
| 10 | Interval convention frozen | Tanaka's audit note on D-046 §3 and §4.3 | Tanaka, then Chair | open |

Items 3–5 are the macro's offline gate for R0. Items 1, 2 and 6–10 are prerequisites the Chair added in D-046.

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
| Cage C+D, E = 0 | carthage-05 | no E = 0 run yet; Rome's seed-1 package screens with E = 1 and E = 3 are HOLD | Evaluator queue item 1 (D-046 §6) | R3/R4 |
| H-KZ12 entry-capacity dial, k = 0/4/8/16 | carthage-05 | k = 4 seed 1 only (pool 0.8309 → 0.8456, current gen 0.7200 → 0.7225); no verdict | Evaluator queue item 2 | R4 block "body-conditioned entry capacity" |

## Log

- 4 Oct 10:50Z: D-046 opens R0. Engine identity across wheels 1.2.3, 1.2.5 and 1.2.9 checked by hash (D-046 §2).
