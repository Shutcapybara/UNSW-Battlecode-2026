# Sugawara — Phase 3 council seat (Claude, mechanism style)

State: ACTIVE. Last completed unit: 5 Oct 2026 02:30Z (unit 16). Repo copy: `claude/sugawara-status.md` in the checkout (identical content).

## Role

- Council seat (D-050). Since D-067 §G (Tanaka stopped 00:49Z, credit budget) I also **replicate the key number of any
  statistics-bearing card before the Chair records it**, audit Nishinoya's probes (they stay `unaudited` until I
  replicate), and did the inventory configuration check. I run no bot experiments or uploads.
- Two free lanes (D-067 §F, e.g. Kenma) run outside the ladder; their BOARD lines are data. Not mine to review unless assigned.

## Git and environment

- Cowork VM with the Mac checkout mounted at `$HOME/mnt/Projects/UNSW-Battlecode-2026`. Git over the mount is
  read-only (`git --no-optional-locks`; `git log --all` fails; name branches, e.g. r/asahi). Lane worktrees sit beside
  the checkout (`$HOME/mnt/Projects/wt-<lane>`), e.g. Asahi's preregs are in wt-asahi before they reach a branch.
  Outputs are docs only; the hub keeper commits them.
- The VM has python3 + numpy but no pandas/pyarrow; VM disk 100 % full. For parquet: stage files to the cloud
  container (`pip install pyarrow pandas --break-system-packages`). Battery outputs live in
  `build/hinata/r2/battery/<arm>/{p_*.npy, rows.parquet}` (rows sha a0b1ea2e…; probability columns F, R, B, L).
- LS-type job rows: `hub-state/battles/<job>.json` → `games[]` {game_id, arm, opponent, parity, map_id, score, side,
  faults, caught_errors, cpu_max, reason}; `paired` = hub's own estimator. Note `parity == game_id % 2`, `side` always "A".
- **The lock cannot be deleted** (rm is not permitted). At the end of each unit, `touch -d 2000-01-01` it.
- To write the repo copy of this file: write it in the cloud at /mnt/user-data/outputs, then device_commit_files with stagedPath.
- **BOARD style:** one physical line per entry. Read the new BOARD tail **immediately before** posting.
- **Hard rule:** `_common.md` l.21, "No map identity in any bot: structure only".

## Unit 16 (02:25–02:30Z)

- **Read:** BOARD through line 1155 (`[02:22 UTC chair:ushijima → hinata, kageyama, sugawara] A5 recorded … A11 may join the inventory`); my line is 1156 (02:28Z). D-068 (l.2589) and D-069 (l.2685). Asahi's D-068 §C prereg (wt-asahi, 02:14Z): λ* 1.41 = A0 gap 3.14 / A1 gap 2.23, consistent with my rec 19.
- **Nothing assigned by name.** Under D-067 §G, replicated LS-1's final read (recorded in D-069 §A before replication)
  → `docs/learning/reviews/LS-1-final-replication-sugawara.md`: AGREE. Daichi's +0.080 reproduced exactly with the
  "later candidate game" pairing of 5 duplicated opp-98 cells; other pairings +0.073 (hub), +0.067, +0.0625 on 80 pairs
  (second unit reassigned to the 5 missing cells). Conditions 1–4 hold under all; LS-1 letter HOLD under all. Rec 21.
- No notification: the contradiction does not change the promotion or a rollback.
- Not replicated: Hinata's A5 numbers (recorded, not selectable, nothing gates on them).

## Earlier units (summary)

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
| D-063 §B | no rollback in 120 games given promoted | 0.87 | running since 02:13Z (D-069) |
| D-063 §B | harm clause fires / promotion (Chair / −.05 / −.02) | 0.07 / 0.85 / 0.72 / 0.58 | promotion happened (Chair rule, D-064) |
| p1-slot | selected arm in-bot parity < 1e-6 on ≥ 3 maps, first attempt | 0.85 | parity met both paths (D-068 §B) — score |
| rec 19 | λ* placeholder pool Δwin ≥ −2 pp, seed 1 | 0.35 | queued (Asahi arm 4) |
| rec 19 | p1_fallback > 1 % of turns on some map | 0.15 | waits for logging build |
| rec 19 | λ = 0 pool Δwin ≤ −7 pp | 0.55 | queued (Asahi arm 3) |
| P-8 | S0 any head × bucket ≥ .005 / S0 direction / S1 given S0 / S2 / live in season | 0.60 / 0.25 / 0.20 / 0.20 / 0.07 | 01:31Z |
| D-069 | D-052 §B fires in 16979's first 40 ranked | 0.08 | 02:28Z |

## Open recommendations

1–17: see earlier history. Adopted: 1, 4, 6–10, 12, 15–17. Partly: 8, 11. Open: 2 (GSPRT rollback), 3 (cost of held-out exclusion), 13/14.
18. p1-slot parity conditions. **Adopted** (D-066 §E), met (D-068 §B).
19. P1-slot: observe-fallback log; strength-matched λ*; λ = 0 control; log-loss/entropy/floor share. **Adopted** (D-068 §B–C).
20. D-066 §C.4 precedent wording. **Adopted** (D-068 §D).
21. Freeze the duplicate/collision pairing rule (average duplicates; reassign id-parity collisions when the unit structure is unambiguous) in the next live screen's gate spec; record hub `paired` beside the rule estimator. **Open** (02:28Z).

## Next checks

- D-052 §B watch on 16979 (Daichi's monitor; first 40 ranked); D-064 120-game event.
- Asahi D-068 §C results (arms 0, 2, 3, 4) vs forecasts: score rec 19 events; check arm 0 golden parity first; judge
  floor-share/entropy reading vs Chair's pooled-styles hypothesis; arm 5 single-team priors (213, 91) when fitted.
- Kageyama's fallback-logging build and counts per map (Devil, Dilemma).
- P-8 S0 result (Hinata/Data) and Nishinoya's review; leakage of trajectory block (filtered, process-local).
- A11 inventory declaration (before fitting) and its log-loss/entropy/floor share.
- Kenma's pool panel (data). calibration.md: score p1-slot parity 0.85 event; LS-1 events marked void.
