# Sugawara — Phase 3 council seat (Claude, mechanism style)

State: ACTIVE. Last completed unit: 5 Oct 2026 03:37Z (unit 17). Repo copy: `claude/sugawara-status.md` in the checkout (identical content).

## Role

- Council seat (D-050). Since D-067 §G (Tanaka stopped 00:49Z, credit budget) I also **replicate the key number of any
  statistics-bearing card before the Chair records it**, audit Nishinoya's probes (they stay `unaudited` until I
  replicate), and did the inventory configuration check. I run no bot experiments or uploads.
- Two free lanes (D-067 §F, e.g. Kenma) run outside the ladder; their BOARD lines are data. Not mine to review unless assigned.

## Git and environment

- Cowork VM with the Mac checkout mounted at `$HOME/mnt/Projects/UNSW-Battlecode-2026`. Git over the mount is
  read-only (`git --no-optional-locks`; `git log --all` fails; name branches, e.g. r/asahi). Lane worktrees sit beside
  the checkout (`$HOME/mnt/Projects/wt-<lane>`). Outputs are docs only; the hub keeper commits them.
- **VM /sessions disk is 100 % full**: writes to `$HOME` (heredoc to a file, scripts) fail with ENOSPC. Writes **into
  the mount work** (python `open(...,"w")` on the checkout). Run scripts inline with `python3 -c '...'`.
- The VM has python3 + numpy; `tools/analysis/features/frame.decode` decodes replays (gives header `reason`, incl.
  `queen`; `events.deaths` with round/cause). `tools/hub/executor.analyse_replay` maps `queen` to `roundLimit`.
  Ranked index: `public_replays/corpus/index.jsonl` (team 7 = us; sub_a/sub_b are None for recent games → attribute by
  time; 16979 activated ≈ 02:13Z). Ladder snapshots `public_replays/corpus/ladder/*.json` (10-min cadence).
- Decode speed ≈ 1 s/game; 120 games fit in one 170 s call.
- **The lock cannot be deleted** (rm is not permitted). At the end of each unit, `touch -d 2000-01-01` it.
  A stray `build/sugawara/.sg_test` (1 byte) is mine; harmless.
- To write the repo copy of this file: python write on the mount (works) or stage+commit.
- **BOARD style:** one physical line per entry. Read the new BOARD tail **immediately before** posting.
- **Hard rule:** `_common.md` l.21, "No map identity in any bot: structure only".

## Unit 17 (03:25–03:37Z)

- **Read:** BOARD through line 1173 (`[03:21 UTC chair:ushijima → kageyama, asahi, sugawara, daichi, shenzhen] Fallback
  hypothesis: closed …`); my line is 1174 (03:34Z). D-070 (l.2739: §A 16979 first ten, queen rule; §B adopts my LS-1
  range + rec 21; §C T0 recorded; §D Kenma).
- **Nothing assigned by name.** Confirmed D-070 §A from replays (all flagged games reason `queen`), and computed an
  interim D-052 §B residual (approx. inputs): 29 games, diff −0.178 [−0.233, −0.122] → **P(fires at 40) revised 0.75**.
  Queen-loss tables: 16979 10/16 losses by queen (non-Schooltime 7/22 games vs parent 16/105); Schooltime cage 91/91
  r0 self-deaths, 15/120 of parent window. → `docs/learning/reviews/16979-interim-and-queen-losses-sugawara.md`.
- Notified the user (rollback likely at the 40-game look; forecast change from 0.08 to 0.75).
- Kageyama fallback count (0/76) closes my rec 19 event "p1_fallback > 1 %" locally (Asahi sandbox binding).
- Hinata T0: P(cost ≥ .005) 0.25 → no. Shenzhen 03:08Z correction (lookup 0.923 with terrain): data, not reviewed.

## Earlier units (summary)

- U16 (02:28Z): LS-1 final replication (adopted D-070 §B), rec 21 (adopted D-070 §B).
- U15 (01:35Z): A8b precedent (adopted D-068 §D), inventory rev 8 PASS, P-8 card filed (S0 approved D-068 §D), P1-slot softness reading (adopted as leading hypothesis D-068 §B).
- U14 (00:30Z): P-7 E2 PASS by bound (D-066 §B); p1-slot mechanism checks + rec 18 (adopted D-066 §E).
- U13 (23:29Z): drift row note (rec 17, D-065 §B). U12 (22:32Z): k16 promotion review (recs 15–16, D-064).
- U11–U5: P-7 amendment 1; D-058 §B precedents; P-6 amendA; R2 battery; LS-std-1 sizing; LS-1 rule; P-5/P-6 r2.

## Scored predictions (for Brier in calibration.md)

| card | event | P | logged |
|---|---|---|---|
| P-2 | confirmation PASS under spec 15d79683 | 0.50 | FAIL; Brier 0.25 (D-057 §B) |
| D-053 §D | k16 D-046 §4 gate PASS seeds 2–3 | 0.35 | 14:45Z |
| P-sugawara-02 | support / refute / later gate (orig.) | 0.40 / 0.25 / 0.20 | 14:55Z |
| P-sugawara-02 | support, amended | 0.35 | REFUTED; Brier 0.1225 (D-060 §B) |
| P-hinata-03 | dev ≥ 0.75 / G-macro / G-parent / panel gate / flip < 1 % | 0.55 / 0.10 / 0.85 / 0.20 / 0.15 | 15:30Z |
| P-hinata-04 | falsifier not triggered / V-legal AUC ≥ Φ | 0.85 / 0.20 | 15:30Z |
| P-5 r2 | dev ≥ .75 / G-parent clean / G-parent as written / ≥ .83 / panel gate | 0.65 / 0.70 / 0.60 / 0.20 / 0.25 | 16:28Z |
| P-6 r2 | falsifier not triggered | 0.80 | 16:28Z |
| LS-1 | PASS rule as written / my amended rule | 0.50 / 0.25 | NOT SCORED (D-069 §A: expired incomplete) |
| LS-std-1 | k16-like promoted / A/A noise ≥ 0.05 | 0.25 / 0.80 | 18:40Z (check calibration.md) |
| P-6 amendA | stump LOMO ≥ 12/14 | 0.25 | miss; Brier 0.0625 |
| P-6 amendA | V-legal* non-inferior | 0.40 | likely void |
| D-057 §C | sel. arm meets condition dev120 / full / A2 > A1 by .01 | 0.45 / 0.55 / 0.35 | 19:30Z |
| P-7 | E2 (orig.) | 0.60 | 20:31Z |
| P-7 amend 1 | E2 revised | 0.75 | PASS; Brier 0.0625 (D-066 §B) |
| P-7 amend 1 | distillation gate given trees / h2h ≥ .55 given step 0 < +.02 | 0.55 / 0.30 | 21:29Z |
| P-7 | h2h ≥ .55 / panel ≥ +.02 / live promotion | 0.45 / 0.25 / 0.15 | 20:31Z |
| D-063 §B | no rollback in 120 games given promoted | 0.87 | running since 02:13Z — now likely to miss |
| D-063 §B | harm clause fires / promotion (Chair / −.05 / −.02) | 0.07 / 0.85 / 0.72 / 0.58 | promotion happened (Chair rule, D-064) |
| p1-slot | selected arm in-bot parity < 1e-6 on ≥ 3 maps, first attempt | 0.85 | parity met both paths (D-068 §B) — score |
| rec 19 | λ* placeholder pool Δwin ≥ −2 pp, seed 1 | 0.35 | queued (Asahi arm 4) |
| rec 19 | p1_fallback > 1 % of turns on some map | 0.15 | 0/76 local (Kageyama 03:10Z); Asahi sandbox binding |
| rec 19 | λ = 0 pool Δwin ≤ −7 pp | 0.55 | queued (Asahi arm 3) |
| P-8 | S0 any head × bucket ≥ .005 / S0 direction / S1 given S0 / S2 / live in season | 0.60 / 0.25 / 0.20 / 0.20 / 0.07 | 01:31Z |
| D-069 | D-052 §B fires in 16979's first 40 ranked | 0.08 | 02:28Z (pre-games) — score at 40 |
| D-069 (rev.) | same, revised at 29 games (not for Brier; conditional on interim data) | 0.75 | 03:34Z |

## Open recommendations

1–17: see earlier history. Adopted: 1, 4, 6–10, 12, 15–17. Partly: 8, 11. Open: 2 (GSPRT rollback), 3 (cost of held-out exclusion), 13/14.
18–20 adopted (D-066 §E, D-068 §B–D). 21 (freeze pairing rule) **adopted** D-070 §B.
22. Pass the replay header reason (`queen`) through `tools/hub/executor.analyse_replay` instead of `roundLimit`. **Open** (03:34Z).
23. The Schooltime cage (91/91 r0 queen self-deaths; ≈ 12.5 % of ranked draws in the parent window) is the largest single
    residual source and survives a rollback; un-park a structural fix (H-SZ1 style) or fast-track Kenma's pocket-queen
    evaluation. **Open** (03:34Z; implicit in BOARD line, not phrased as a card).

## Next checks

- D-052 §B look at 40 ranked games of 16979 (Daichi); score my 0.08 forecast; compare Daichi's frozen-input residual
  with my approximate −0.178 (own anchor, snapshot timing, draw handling).
- Daichi's queen-state scan + 14585 vs 303/420.
- Asahi D-068 §C results (arms 0, 2, 3, 4) vs forecasts; Shenzhen H-SZ74 (arm 4 recovers ≥ half of arm 2's loss).
- Single-team priors (213, 91) and Shenzhen H-SZ71/72.
- P-8 S0 result (Hinata/Data) and Nishinoya's review.
- Kenma h2h vs asahi-05-kz12-k16 (data). calibration.md: score p1-slot parity 0.85 event; LS-1 events void.
