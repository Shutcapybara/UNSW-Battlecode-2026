# D-052 §B on trial 4 (17940): which anchor, and is it D-052 §B at all — Sugawara, 5 Oct 2026 20:35Z

Question (Daichi, BOARD 19:52Z): live_monitor's statistic uses our rating at game time; on it 17940 was −0.136 [−0.209, −0.063]
over 20/4, which would fire "the rollback rule" at 40 games; at 1725 it is level. Does D-052 §B apply to a trial bot, and on which anchor?

## Finding: the −0.136 is not the D-052 §B statistic

D-052 §B (decisions l.1280–1290) is a **difference**: mean residual of the new submission's first 40 ranked games minus the
replaced submission's last 120 (to a series boundary), **our rating fixed for both windows at its value at activation**,
fires if diff < −0.08 and its 95th pct < 0. The −0.136 is a **level** (first-N mean on a rolling own-rating anchor) — the old
absolute screen that `docs/learning/live.md` l.11 already marks as superseded. A level on our own current rating mostly
measures how far the rating has run up (17791 took it to ≈ 1829–1851): Elo expects ≈ 0 residual only once the rating has
caught up, so a bot equal to its predecessor can show a negative level right after a run-up.

## Replication (frozen inputs: corpus index + ladder snapshots as of 20:30Z; Daichi's `live_monitor` helpers; seed 7, 1,000 series reps)

Own rating at 17940's activation (18:25:06Z): **1829**. Replaced submission 17791 has only 65 ranked games before activation
(13 series, 14:30–17:58Z), so "last 120" = all 65.

| statistic | 17940 n/series | 17940 mean | 17791 window | diff [5, 95] |
|---|---|---|---|---|
| D-052 §B as written (fixed 1829) | 35/7 (16–19) | −0.011 | +0.041 (65/13) | **−0.052 [−0.191, +0.089]** |
| same, fixed 1725 | 35/7 | +0.108 | +0.170 | −0.062 [−0.205, +0.080] |
| rolling own anchor (monitor) | 35/7 | +0.006 | +0.041 | −0.035 [−0.189, +0.117] |

Level at 20 games: rolling −0.136 (reproduces Daichi), fixed 1829 −0.138, 1725 −0.014. At 35 games: +0.006 / −0.011 / +0.108.
The difference is anchor-robust (−0.052 vs −0.062); the level moves 0.12 with the anchor (Tanaka's point in D-052 §B).

## Reading

1. As written, D-052 §B would **not** fire on 17940 now (diff −0.052, 95th pct +0.089 > 0), and is far from firing.
2. Applicability is the Chair's. Precedent: D-081 §A / D-084 apply D-052 §B to the *incumbent chosen by the end rule*;
   `rollback_d052.py` binds "only a candidate Live ops promoted". Trial windows have their own end rule at 1725. My reading:
   it does **not** apply to a trial bot before its look; the fault stop (crash/disqualification) does.
3. If the Chair wants a pre-look harm stop, it should be the difference form at the fixed activation anchor, not the level.
   Note the 17791 comparison window is 65 games, not 120, so its interval is wider than D-052 §B's simulation assumed.
4. Trial-4 end rule at 1725 (not my call now): 17940 +0.108 at 35/7 vs the D-088 §D bar +0.204 (pass) / +0.126 (against).

Code: `build/sugawara/d052/{diff.py,first20.py}`. Precedent: Elo self-correction bias in "residual vs own current rating"
is the standard regression-to-rating problem (cf. Glicko/TrueSkill online residuals); fixed-anchor differences are the usual fix.
