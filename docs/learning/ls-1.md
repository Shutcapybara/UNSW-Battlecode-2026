# LS-1 — asahi-05-kz12-k16 vs 14585 (D-055 §B), Live ops record

## Build and eligibility item 4 (Daichi, 2026-10-04 17:10–17:33Z)

- Source: main `593810d14`, `bots/asahi-05-kz12-k16/` read with `git show` file by file (the mount refuses symlinks).
  `hb1_direction_compact.hpp` is a symlink in git (`../carthage-05-free-sprint/hb1_direction_compact.hpp`); it was
  resolved to main's blob of that file: 12,944,565 bytes, sha256 `1c3f8974dd7a8da1…` (= the working-tree copy).
  Every other file byte-checked against main. Manifest `CANDIDATE.toml` written by Daichi (D-055 §B), committed on
  r/daichi under `bots/asahi-05-kz12-k16/CANDIDATE.toml`; materialised directory `build/daichi/stage/asahi-05-kz12-k16`.
- Registered 17:20:18Z: fingerprint `0cf975af55bc…`, code fingerprint `54f8130e…`; hub archive 3.74 MiB, 16 files,
  holds the real header (size and sha256 checked inside the zip).
- CPU probe (cloud container, unswbc 1.2.9 `run --sandbox --verbose --seed 1`, vs sinbad-v07-divecap, maps/live):

| map, our seat | our turns | max points | round-0 max | faults | result |
|---|---:|---:|---:|---:|---|
| big_empty A | 25,953 | 10.6 M | — | 0 | lost 50–74 (r500) |
| schooltime A | 22,141 | 10.17 M | 7.03 M | 0 | won 67–28 |
| portals B | 9,971 | 10.05 M | 6.57 M | 0 | won 32–11 |
| slithery_fight A | 26,028 | 10.31 M | 6.99 M | 0 | won 76–26 |
| trauma B | 7,691 | 10.00 M | 7.13 M | 0 | won 23–21 |
| weakhold A | 9,341 | 9.72 M | 6.81 M | 0 | won 34–3 |
| weakhold B | 5,382 | 9.56 M | 6.83 M | 0 | won by elimination r321 |

  Max 10.6 M points per turn over 106,507 turns, round 0 at most 7.13 M; limit 30 M. Zip 3.74 MiB ≤ 4 MiB. **Pass.**
  (Hub preflight 17:27:46Z, toolkit label unswbc 1.0.0: max 10.09 M on two fixtures.)

## Upload (17:32:57Z) and the server's auto-activation

- `submit.json` with `activate: false` → submission **16979**, `LV-asahi-05-kz12-k16-0cf975af-ai`.
- **The server made 16979 active on upload** (mirror 17:37:31Z: 16979 active, 14585 idle) although no activate call
  was made; `submit_check` does not restore the previous active after a manual upload. 16979 was live from about
  17:32:57Z to **17:40:00Z**, when `restore.json` (previous 14585, candidate 16979) restored 14585 and reset control.
  Ranked games of 16979 in that window: 0 in the hub mirror at 17:43Z (to be re-checked in the public corpus).
- First LS-1 job `eccd265afc81` recorded `expect_active 16979` because of this; cancelled 17:40:07Z.

## Job

- `5ed81ad3e1f3`, accepted 17:41:15Z, 12 units / 204 games, arms [14585, 16979], expect_active 14585, deadline 8 h.
- Roster (rule of D-055 §B; 800 ranked games of 14585 from 2 Oct 17:26Z to 4 Oct 17:09Z; ladder 17:17Z, our 1725):
  716 (35 games, 1658), 98 (25, 1664, last 15:06Z), 347 (25, 1781, last 3 Oct 17:10Z; 98 before 347 by recency).
  Excluded by rating: 78 (35 games, 1580). Active = ranked games in the public corpus within the last 2 h (all five).
  Declared extension: 919 (20, 1696), 351 (20, 1665).
- Dispatch enabled 17:42:26Z (D-055 §B).
