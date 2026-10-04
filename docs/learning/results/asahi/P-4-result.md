# P-4 (H-KZ26 queen reach veto) — screen result, seed 1 (Asahi, 4 Oct 2026 20:20Z)

Card: `docs/learning/proposals/P-sugawara-02-hkz26-queen-reach-veto.md` (D-054 §C, Tanaka's amendments). Arms on
REG-000 (carthage-05), one switch `Params::queen_reach_m`: `asahi-06-hkz26-off` (fp 934ccd27), `asahi-07-hkz26-m0`
(e05f0e6b), `asahi-08-hkz26-m1` (4e36494c), r/asahi. Panels: pool 272 + gen 464 per arm, seed 1, wheel 1.2.3
(engine 26e68680…), 0 missing, 0 runtime errors. Labeller `tools/asahi/strike_label.py` sha256 684754bd… (frozen and
validated before the parent was labelled). Readout `tools/asahi/hkz26_card.py` (sha256 7fa5fc27…, frozen 17:30Z).

## Verdict (frozen rule, m = 0): **REFUTE** — strike-hazard ratio 1.069 ≥ 0.90

| | m = 0 | m = 1 |
|---|---|---|
| strike deaths / alive queen-rounds, cand vs parent (pooled) | 30 / 105,908 vs 22 / 83,058 | 34 / 110,262 vs 22 / 83,058 |
| **strike-hazard ratio** (pooled; 5th–95th) | **1.069 [0.685, 1.788]** | 1.164 [0.744, 1.920] |
| all-cause queen hazard ratio | **0.703 [0.662, 0.746]** | 0.664 [0.618, 0.705] |
| food per alive own dragon-turn ratio | 0.997 [0.989, 1.005] | 0.994 [0.986, 1.002] |
| queen alive at round limit (fixtures) | 4 vs 3 | 12 vs 3 |
| queen-initiated head-on deaths | 53 vs 225 | 38 vs 225 |
| pool Δwin pp (map × opp) | −1.84 [−4.41, +0.74] | −3.31 [−6.99, +0.37] |
| gen Δwin pp | −0.65 [−2.80, +1.72] | +0.22 [−1.94, +2.59] |
| gen Δecon ×100 (mean form) | −2.00 [−3.82, −0.16] | −3.52 [−5.71, −1.35] |
| pool exposure (queen decisions with ≥ 1 vetoed candidate) | 69.5 / 1k | 100.7 / 1k |
| all-vetoed fallbacks (pool) | 733 | 1,676 |

Stops checked: golden parity at m = off 272/272; exposure 69.5 / 1k ≥ 5; parent strike events 22 ≥ 10; valid draws
1,000 pooled (948 on the pool panel alone). Pool-only and gen-only rows are in `P-4-hkz26-s1.md`; per-arm curve in
`P-4-hkz26-curve-s1.md`.

## Reading

- The veto does not lower the strike hazard (the card's mechanism). It does lower the queen's all-cause hazard by
  ~30 %, almost entirely by removing the queen's **own** head-on moves (queen-initiated deaths 225 → 53): the H2H
  candidate is judged at the struck head's cell, which is always inside reach. Strike deaths stay at ~1 per 3,500
  alive queen-rounds; the queen lives longer and meets the same strikers.
- Win does not follow: pool −1.8 pp (m0) and −3.3 pp (m1), gen economy down. The pool Δwin guard (point ≥ 0) fails.
- Firing is concentrated on open maps (Stripes, Dilemma, Default, Trophy, Australia); near zero on Portals, Maze,
  Trauma and Weakhold (an enemy head is rarely visible to our queen there).
- Local exposure is thin: 22 parent strike events over 736 games against the zoo, against Kanazawa's live 64 / 635
  opportunities. A live read is the better test of the strike mechanism (card §3.2's fallback).

## Checks

- Behaviour without firing equals the parent: every game in which the veto never fired is identical to the parent's
  (winner and rounds): 117 / 117 (m0), 111 / 111 (m1), pool. The capture's "changed without veto" counter (1,151) is
  a counting artifact: a re-selected split keeps the same action but a different unused `dirs` field.
- The first m0 build (withdrawn 18:13Z before any outcome was read) changed choices on non-firing turns; fixed.

## RL translation (D-044)

- Observation: the signed reach margin min_e BFS(e → w) − B(L̂_e) per candidate is cheap and legal, but on these
  panels it does not predict strikes; L̂ underestimates (cut chains) and strikers come from outside vision.
- Action: a mask on head-on candidates (queen-initiated H2H) is what moved the queen's survival — a candidate R3/R4
  action-mask feature, separate from reach.
- Value: queen all-cause hazard fell 30 % with no win gain locally — consistent with the queen mattering through the
  round-limit tiebreak, which our queen still rarely reaches (4–12 of 736).
- Demonstration: the field's 1.8 % strike rate per opportunity (Kanazawa) is not reproduced by masking reach on our
  vision alone; cloning field queens' choices in opportunity states remains the learned path.
