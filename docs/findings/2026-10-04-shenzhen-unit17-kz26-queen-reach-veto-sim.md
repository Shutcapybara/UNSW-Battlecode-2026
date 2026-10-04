---
id: shenzhen-unit17-kz26-queen-reach-veto-sim
author: Shenzhen (P2-A analyst, Opus 5.5)
kind: simulator screen of another lane's hypothesis (H-KZ26 had no tester after Seoul and Kanazawa closed); analysis copies only
title: Unit 17 — the H-KZ26 queen reach veto in the simulator: at m = 0 it halves enemy strikes on our queen (13 → 6 of 18), delays its death by ~80 rounds and costs no total; the queen still does not survive, because strikes are replaced by self, wall and invalid-command deaths
evidence: unswbc 1.2.9 local runs, carthage-05 + C+D (`c05d`) vs probe Q at m = 0 (`c05q0`) and m = 1 (`c05q1`); Around UNSW, Islands, Australia (maps/live), seeds 1–3, both seats (18 games per dose); tools/shenzhen/szqdeath.py, szleak.py
---

# 1. Probe

Probe Q applies to the queen (id 0/1) only. If its planned end cell is within B(L) + m of any visible enemy head
(B(L) = ⌈L/4⌉ + L − 2, Himeji H30-01, with L the enemy's visible length), it takes the safe single step that has the most
slack (distance − reach), provided that step has more slack than the plan. Distance is torus Manhattan with walls ignored,
so the reach is uncapped and conservative. There is no Cb fallback: if no step improves the slack, the plan stands. The
probe fires about 5 times per game.

# 2. Result (18 games per dose; queen = our side's id 0/1)

| dose | bot | queen killed by enemy head-on | other queen deaths | mean death round | queen alive at end | wins | pool total |
|---|---|---|---|---|---|---|---|
| m = 0 | c05d | **13** | 5 (self 3, invalid 1, body 1) | 145 | 0 | 6 | 2,626 |
| | **c05q0** | **6** | 12 (invalid 4, wall 3, self 2, ally body 2, ally h2h 1) | **223** | 0 | **12** | **2,709 (+3 %)** |
| m = 1 | c05d | 12 | 5 | 154 | 1 | 8 | 2,826 |
| | c05q1 | 9 | 8 (wall 5, self 2, invalid 1) | 186 | 1 | 10 | 2,537 (−10 %) |

Pool total per map at m = 0: Around UNSW −11 %, **Islands +32 %**, Australia +4 %. At m = 1: −2 % / −11 % / −20 %. The
enemy's share of our corpse pearls is unchanged (0.32–0.34).

Baseline across the three earlier sets (48 c05d sides): **81 % (39/48) of our queen deaths are enemy head-ons**, at mean length
3.2 and mean round 138. That is the sim's version of Kanazawa's live strike rate.

# 3. Reading

* The veto does its job at m = 0: enemy strikes on our queen fall 13 → 6. The queen lives ~80 rounds longer, and total does not
  pay for it (+3 %, Islands +32 %). By the H-SZ37 rule (pool total per map, Islands canary) m = 0 passes the screen.
  m = 1 vetoes more but strikes fall less (12 → 9) and total drops 10 %. The non-monotone dose is noise at 18 games, and
  m = 0 is the dose to carry. Wins 12/18 vs 6/18 is suggestive only (binomial, n = 18).
* **It does not produce a surviving queen.** On the open maps the queen dies anyway. The strikes it avoids turn into
  invalid-command deaths (4), walls (3), its own body (2) and ally contact (3). The queen-survival lever is therefore a
  stack: KZ26 (strikes) + KZ12 (pocket/seal veto, wall deaths) + a queen production rule (invalid deaths, below). One of
  them alone moves the death cause, not the tiebreak.

# 4. Hypotheses

* **H-KZ26 (Kanazawa) — sim screen passed at m = 0.** Strikes −54 %, death round +78, total +3 %, Islands +32 %. Ready for
  a tester's dose screen on `LIVE_MAPS_M2` with the Cb ≥ 4 fallback. Expect the queen column to move only once it is stacked.
* **H-SZ40 (0.5, new) — the queen does not split near the cap.** In the sim, 4 of the 12 non-strike queen deaths under
  the veto are `invalid`: a split at the unit cap kills the splitter (stale same-round counts, H-SZ24). Rule: the queen
  (id 0/1) never issues a production split when units ≥ limit − 4. Falsifier: queen `invalid` deaths not → 0 in 18
  stacked games (KZ26 m0 + H-SZ40), or total < −5 %. Size: 18 sim games. Suits any tester; zero information cost.
* **H-SZ41 (0.4, new) — "stack before you read the tiebreak".** No single queen rule moves queen-alive-at-end on open
  maps, because the hazards substitute for each other. Prediction: KZ26 + KZ12 + H-SZ40 together reach queen alive@end
  ≥ 4/18 in the sim on the three open maps, while each alone stays ≤ 1/18. Falsifier: the stack ≤ 1/18. Size: 18 sim
  games per arm (4 arms). Suits a tester, or this lane next unit.

# 5. Caveats

Self-play against one parent. 18 games per dose. Enemy length is the bot's own visible-length memory, so it is
underestimated for partly seen bodies. The probe ignores walls in the reach (conservative) and has no Cb fallback.

**RL translation.** Observation: enemy head positions and their visible lengths; the reach B(L) as a feature. Action: the queen's
single-step choice. Value: queen survival time, with total as a guard. Demonstration: field queens are struck 1.7 % per
opportunity vs ours 10.1 % (Kanazawa unit 16).
