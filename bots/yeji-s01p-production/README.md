# yeji-s01p-production

**Lineage:** Yeji (`claude/yeji/01SVqD5S`). **Parent:** `yeji-s01-swarm-dissolve` (host `ouroboros-v10-beacon`). **Status:** frozen benchmark.

The **P arm** of the S1 2×2, saved as its own bot: `yeji-s01-swarm-dissolve` with the dissolve/crown layer set back to the host (`dissolve_on=0, crown_elect_from=200, crown_stagger=1, crown_elect_longest=0, crown_min_len=4, crown_trap_mult=1, crown_crowd_mult=1, crown.risk=1.6`). What remains on top of the host: the `lambda_unit` production schedule (unit target 64, split value ×1 to r100, → 0 by r380), gatherer-only children, certificate with crown id, target hysteresis 1.0, `ACT:` logging.

Panel (unswbc 1.2.2, `--seed 1`, 10 live maps × both sides × 8 refs, 160 paired fixtures): **0.531** vs control `ouroboros-v10-beacon` 0.494 — **+0.037, 19 better / 13 worse, sign p = 0.38**. Per map: schooltime +0.25, default +0.19, portals +0.19, QoS +0.06, dilemma +0.06, trophy +0.06, devil 0, autarky −0.06, slithery −0.19, trauma −0.19. Longest r499 median 26 (control 24); units r100 14 (open maps 17 vs 14). Not significant: selection evidence only.
