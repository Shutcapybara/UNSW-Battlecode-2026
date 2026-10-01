# verso-02-hb540-prior

Verso cycle 2. Parent `verso-01-hb-dir-prior`; platform `verso-p4-platform` (phase knobs and the late-phase ramp,
a second head slot; inert at the defaults — golden 0 divergent against maelle-01-nodevil with `lam_dir=0`).

One change: the Heartbreaker direction prior is the first 540 rounds of the full 2,251-round GBT (255 leaves;
824,580 nodes = 6.6 MB embedded, header 15.5 MB of text, upload zip 3.68 MiB) instead of verso-01's 300-round
63-leaf model. Found by taking hb1-14 / tt-05 / tt-06 (the HB-1 and mimic lanes' uploadable bots) apart on the
Verso base: their off-pool edge over verso-01 (+6 to +8 pp win, +0.098 economy) comes from the prior's size;
V06's late search cap (48) alone costs the pool; their late feeding (tt-05 / tt-06) is neutral on these panels
(no zoo opponent converts); the Devil map-size terms are not used (D-033).

Reproduces the arm `c3-big540` (file-loaded head) exactly (trauma B, 12,306 turns, 0 divergent).

vs verso-01, seeds 1–3: pool unchanged (win 0.848 both; econ~ −0.001 [−0.028, +0.026]); generalisation win
0.618 → 0.716 (+0.097 [+0.064, +0.130]), econ~ +0.107 [+0.081, +0.135], units@100 +0.18, length@100 +0.13; tempo
−6.3 rounds off-pool. D-032 by the letter: REJECT on the pool lower bounds (point estimates 0); the lead decides.
