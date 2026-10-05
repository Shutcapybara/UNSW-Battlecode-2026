# Incumbent drift row (Daichi 22:52Z): how often does a 40-game window cross −0.08 by chance?

Council:sugawara, 4 Oct 2026 23:27Z. Unassigned note (council step 3). Not a gate; the drift row is a monitor row.

## Question

Daichi's 22:52Z monitor put submission 14585's rolling last-40 residual at **−0.129 [−0.227, −0.035]** (40 games /
8 series), across the −0.08 drift line. Does that indicate a real change (field trend, rating lag) that would bias the
D-052 §B look after a k16 promotion, or is it within the incumbent's own window-to-window noise?

## Replication (frozen input, no game run)

Input: `docs/learning/live-inputs/20261004T2252Z-39623008.json.gz` (at 22:52:16Z, index sha256 5c95be21…). Rows:
bot = 14585, ranked, with an expectation: **1,035 games / 209 series**, 2 Oct 04:23Z to 4 Oct 22:19Z. Residual =
score − exp, with exp as stored (game-time ratings; not D-052 §B's fixed anchor). map_era post-m2 throughout this span.

- Since activation: mean −0.018 (Daichi: −0.022 with his interval; the small gap is the centring or the exp source,
  not checked).
- Consecutive 120-game blocks: −0.040, +0.018, +0.016, −0.029, −0.071, −0.105, +0.061, +0.006, then −0.069 (75 games).
  SD of the eight full blocks ≈ 0.054, against ≈ 0.046 for independent games; the excess is the series clustering.
  No monotone trend.
- Last 120: **−0.030**; the 120 before: −0.034. The baseline window D-052 §B would use is at the incumbent's own mean.
- **Rolling 40-game windows over the incumbent's history (996 windows): 26.1 % are below −0.08; 9.9 % are at or below
  −0.129**; the minimum is −0.29.
- Series-exchangeable null (shuffle the 209 series, take the final ≥ 40-game window, 4,000 draws, seed 7):
  P(window ≤ −0.129) = **0.071**.

## Reading

1. The 22:52Z crossing is a ~7th-percentile excursion of the incumbent's own play, not evidence of a field trend.
2. **The −0.08 line on a 40-game window has a false-alarm rate of about one in four** on a submission whose mean is
   −0.02. As a monitor row it will fire most days. Recommendation (rec 17): report the drift row as the series-shuffle
   percentile of the latest 40-game window against the submission's own history, or use a 120-game window. One
   change; no gate depends on it.
3. For the D-052 §B look after a k16 promotion: the baseline (incumbent's last 120) is −0.03, near its mean, so the
   drift does not lower the bar the candidate is measured against, and there is no sign that a persistent field trend
   would push an equal candidate below it. My P(no rollback within 120 | promoted) stays **0.87**.

## Caveats

- exp uses game-time own ratings; D-052 §B fixes our rating at activation. Over 2.7 days 14585's rating moved little
  (Elo 1720 now, 1722 24 h ago, anchor 1694 at first game), so the anchor would shift all blocks by roughly the same
  amount and does not create the trend; not recomputed (opponent ratings are not in the frozen file).
- I read only the frozen live-inputs file; nothing from `hub-state/battles/` or the LS-1 job (blinding kept).

## Precedent

Control-chart practice (Shewhart / Western Electric): a limit is set from the process's own in-control variance, at a
stated false-alarm rate; a fixed −0.08 line on n = 40 is about a 1σ limit here.
