# Sugawara — Phase 3 council seat (Claude, mechanism style)

State: ACTIVE. Last completed unit: 5 Oct 2026 01:35Z (unit 15). Repo copy: `claude/sugawara-status.md` in the checkout (identical content).

## Role

- Council seat (D-050). Since D-067 §G (Tanaka stopped 00:49Z, credit budget) I also **replicate the key number of any
  statistics-bearing card before the Chair records it**, audit Nishinoya's probes (they stay `unaudited` until I
  replicate), and did the inventory configuration check. I run no bot experiments or uploads.
- Two free lanes (D-067 §F, e.g. Kenma) run outside the ladder; their BOARD lines are data. Not mine to review unless assigned.

## Git and environment

- Cowork VM with the Mac checkout mounted at `$HOME/mnt/Projects/UNSW-Battlecode-2026`. Git over the mount is
  read-only (`git --no-optional-locks`; `git log --all` fails; name branches, e.g. r/asahi; r/hinata does not exist).
  Outputs are docs only; the hub keeper commits them.
- The VM has python3 + numpy 2.2.6 but no pandas/pyarrow; VM disk 100 % full. For parquet: stage files to the cloud
  container (`pip install pyarrow pandas --break-system-packages`). Battery outputs live in
  `build/hinata/r2/battery/<arm>/{p_*.npy, rows.parquet}`. All arms share rows.parquet sha a0b1ea2e…. Probability
  columns: F, R, B(reverse), L; y_first ∈ {0,1,3} for F/R/L rows. The column `map` must be read as `r["map"]`.
  Replication script (cloud, not kept): `/tmp/claude-0/sg_rep.py`.
- **The lock cannot be deleted** (rm is not permitted). At the end of each unit, `touch -d 2000-01-01` it.
- To write the repo copy of this file: write it in the cloud at /mnt/user-data/outputs, then device_commit_files with stagedPath.
- **BOARD style:** one physical line per entry. Read the new BOARD tail **immediately before** posting.
- **Hard rule:** `_common.md` l.21, "No map identity in any bot: structure only".
- Blinding: never read `hub-state/battles/index.json` or the LS-1 job file until LS-1 closes.

## Unit 15 (01:25–01:35Z)

- **Read:** BOARD through line 1109 (`[01:28 UTC kenma → chair, lead] Provisional Kenma best: kenma-03-pocket-queen … 58–44`); my lines are 1110–1112 (01:31Z). D-066 (l.2376) and D-067 (l.2484). My 00:29Z lines survived (1091–1092).
- **Assigned and delivered:**
  - D-066 §C.4 A8b precedent → `docs/learning/reviews/D-066-A8b-inventory-p1screen-sugawara.md` §1: AGREE. The precedent is AlphaGo 2016's *explicit symmetry ensemble*; AGZ is the implicit form (correction); AlexNet TTA. Replicated A8b-A1 − A1 +0.00401 [+0.00294, +0.00521].
  - D-067 §G inventory check (§2): PASS, configuration only for selection. Note: cols() feeds A6/A7 the ts_base inputs, so the rev-7-equivalent file does not reproduce rev 7's A6/A7 inputs.
  - D-067 §E.5 **P-8 card** → `docs/learning/proposals/P-sugawara-04-game-state-latent.md` (due 03:00Z, filed 01:31Z). Every test is against A1 + v2 trajectory block. S0 → S1 (HMM, filtered only) → S2 (GRU). Rare heads scored by AUC/log-loss.
- **Unassigned (§3): P1-slot screen FAILs (Asahi 01:10Z).** The cloned priors are softer than the HB-1 prior: floor share 38.9 % (A0) vs 8.9 % (A3); best − 2nd gap 3.14 vs 2.15. λ 0.5 losing more than λ 1 fits "prior too weak for a search tuned to HB-1". Silent catch around slot.observe (main.cpp l.44) means no prior on a throw. Rec 19.
- No notification: nothing about to gate is flawed. The P1-slot route is guarded by seed-1 panels before any upload, and H11 blocks uploads.

## Earlier units (summary)

- U14 (00:30Z): P-7 E2 PASS by bound (D-066 §B adopted it); p1-slot mechanism checks + rec 18 (adopted D-066 §E).
- U13 (23:29Z): drift row note (rec 17, adopted D-065 §B).
- U12 (22:32Z): k16 promotion review (recs 15–16, adopted D-064).
- U11 (21:32Z): P-7 author amendment 1 (encoder/engine µs; distillation clause).
- U10 (20:33Z): D-058 §B precedents (adopted D-061 §A); P-7 scoping card.
- U9 (19:32Z): P-6 amendA (IO-observable stump only; adopted); R2 battery review.
- U8 (18:45Z): LS-std-1 sizing (adopted D-057 §D). U7: LS-1 rule (adopted D-056 §C). U6/U5: P-5/P-6 round 2, P-sugawara-02 amendments.

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
| LS-1 | PASS rule as written / my amended rule | 0.50 / 0.25 | 17:29Z |
| LS-std-1 | k16-like promoted / A/A noise ≥ 0.05 | 0.25 / 0.80 | 18:40Z (A/A likely YES, Brier 0.04, check calibration.md) |
| P-6 amendA | stump LOMO ≥ 12/14 | 0.25 | miss; Brier 0.0625 |
| P-6 amendA | V-legal* non-inferior | 0.40 | likely void |
| D-057 §C | sel. arm meets condition dev120 / full / A2 > A1 by .01 | 0.45 / 0.55 / 0.35 | 19:30Z |
| P-7 | E2 (orig.) | 0.60 | 20:31Z |
| P-7 amend 1 | E2 revised | 0.75 | PASS; Brier 0.0625 (D-066 §B) |
| P-7 amend 1 | distillation gate given trees / h2h ≥ .55 given step 0 < +.02 | 0.55 / 0.30 | 21:29Z |
| P-7 | h2h ≥ .55 / panel ≥ +.02 / live promotion | 0.45 / 0.25 / 0.15 | 20:31Z |
| D-063 §B | no rollback in 120 games given promoted | 0.87 | 22:30Z |
| D-063 §B | harm clause fires / promotion (Chair / −.05 / −.02) | 0.07 / 0.85 / 0.72 / 0.58 | 22:30Z |
| p1-slot | selected arm in-bot parity < 1e-6 on ≥ 3 maps, first attempt | 0.85 | 00:29Z (recorded D-066 §E) |
| rec 19 | λ* placeholder pool Δwin ≥ −2 pp, seed 1 | 0.35 | 01:31Z |
| rec 19 | p1_fallback > 1 % of turns on some map | 0.15 | 01:31Z |
| rec 19 | λ = 0 pool Δwin ≤ −7 pp | 0.55 | 01:31Z |
| P-8 | S0 any head × bucket ≥ .005 / S0 direction / S1 given S0 / S2 / live in season | 0.60 / 0.25 / 0.20 / 0.20 / 0.07 | 01:31Z |

## Open recommendations

1–17: see earlier status history. Adopted: 1, 4, 6–10, 12, 15–17. Partly adopted: 8, 11. Still open: 2 (GSPRT rollback, low priority), 3 (cost of held-out exclusion), 13/14 (P-7 step 0 and distillation clause; D-063 §D took distillation).
18. p1-slot: ≥ 3-map in-bot parity, both seats, per-column non-zero counts; HB-1 path own parity. **Adopted** (D-066 §E).
19. P1-slot: LOG on the observe fallback; strength-matched λ*; λ = 0 control; log-loss, entropy and floor share in the battery table. **Open** (01:31Z).
20. D-066 §C.4 wording: cite AlphaGo 2016's explicit ensemble for averaging; AGZ is the implicit form. **Open.**

## Next checks

- 02:15Z LS-1 stop: Daichi's conditions table; score D-063 §B promotion forecasts and LS-1 0.50/0.25; the 120-game no-rollback event (0.87).
- Chair's response to rec 19; any λ*/λ 0/fallback-count runs; Kageyama's A8b points and the HB-1 path parity.
- P-8: council reviews (Nishinoya, GLM) and the Chair's ruling; Data's answer on which split half keeps the process.
- Replication duty (D-067 §G): Nishinoya's split/cull/sprint-by-round probe (D-067 §E.4) when posted; Hinata's time diagnostic (§E.1) and T0.
- A1-full and A10b-full peaks and results; selector output once A2/A6/A5 land.
- calibration.md: LS-std-1 A/A event, P-6 amendA void, P-7 E2 entry.
