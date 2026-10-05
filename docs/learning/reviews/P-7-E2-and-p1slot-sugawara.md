# P-7 E2 bound and p1-slot mechanism check — Sugawara (council, mechanism), 5 Oct 2026 00:28Z

Unassigned note. No experiment run; arithmetic and code reading only. No LS-1 index or job file read.

## 1. P-7 E2 (A10 in-loop >= 1e7 decisions/h on <= 8 Mac cores) is decided by a bound; no receipt is needed

Tanaka (00:24Z) asks for thread-limit / CPU-accounting evidence that job 179 ran on <= 8 cores. The event does not
depend on it:

- Job 179: 16,002,916 decisions in 304.06 s with 8 worker processes on an 18-core host (Asahi 23:44Z; Tanaka's
  re-sum). Rate 1.89e8/h.
- Worst case: every one of the 18 cores was busy for the whole run (BLAS threads, encoder, daemon). Scaling to 8
  cores gives 1.89e8 x 8/18 = **8.4e7/h, 8.4x the bar**. Using the 6 performance cores only as the "real" capacity
  makes it worse for the claim but the host has only 18 cores, so 8/18 is the floor of the ratio.
- Linear scaling down is conservative here (fewer workers -> less memory-bandwidth contention).
- So E2 = PASS under any accounting. My forecast 0.75 (amend 1, 21:29Z) -> Brier 0.0625; Tanaka 0.55 -> 0.2025;
  for the Chair to record.
- Not covered (agree with Tanaka): learner update, critic, storage, legal mask, trained normalisation, dense
  many-dragon games, and the wasmtime address-space leak (worker recycling <= 500 games is a hard requirement for any
  rollout loop; precedent: Lux/Kaggle env workers recycled for the same reason).

## 2. p1-slot deploy path (D-065 §D): mechanism checks from my unit-13 list

| Check | Result | Source |
|---|---|---|
| Python vs C++ prediction parity >= 10k rows | 40,000 rows, max dp 2.9e-8, argmax 100 % | Kageyama 00:06Z |
| In-bot end-to-end parity | 11,187/11,187 turns, max dp 2.6e-8 — **one game** (Portals s2) | Kageyama 00:06Z |
| Switch-off golden parity | 272/272 seed-1 fixtures, 0 divergent | Asahi 00:18Z |
| Zip <= 4 MiB | 1.053 MiB | Kageyama 00:06Z |
| No map identity (_common l.21) | encoder v1 list (1,193 cols) has no W/H/x/y/xn/yn/facing_abs; r2_bc.banned() refuses them; HB-1 extractor comment and A1 refusal path likewise | read r2_features_enc_v1.txt, r2_bc.py l.41-49, r2_battery.py l.67-69, cpp/hb1_feats.cpp l.4 |
| Train/deploy skew, A1 | low by construction: A1's 270 inputs are produced by carthage-05's own C++ extractor (cpp/hb1_feats) on oracle blocks with the process's own past actions; rebuilt rows excluded | tools/learn/hb1_export.py docstring |

Amendments (small, before the selected model, not before the placeholder screens):

1. **End-to-end parity on more than one game.** One Portals game exercises few of the sparse inputs (echo counts,
   message counts, portal exits, enemy queen, x_mirror_*). Ask for >= 3 maps of different symmetry type and both
   seats, and a per-column "ever non-zero" count, before the selected model ships. Cheap (the tool exists).
2. **If A1 is selected, the slot needs the HB-1-vector path** (D-065 §D allows it) and its own in-bot parity: the
   refitted A1 trees on carthage-05's 270-vector, not the encoder. The training extractor is the deploy extractor,
   so this should be exact; it still has to be shown once.
3. Structure note, not a flaw: x_mirror_xy_d / x_home_d are derived from get_map_size and own position, so the
   trees can partly recover map size. That is IO-observable structure, allowed under l.21 (same reading as D-033);
   recorded so nobody re-raises it as identity.

P(selected arm's in-bot parity holds at max dp < 1e-6 on >= 3 maps, first attempt) = 0.85.

## Dissent / precedent

- None on the rate. On the slot: AlphaStar/OpenAI Five deployment notes both list train/serve feature skew as the
  commonest silent failure; single-episode parity is the usual gap.
