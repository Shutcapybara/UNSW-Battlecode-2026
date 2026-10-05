# P-9 / P-hinata-05 (learned cull gate from bokuto-13's randomisation) — Sugawara mechanism review

Unit 22, 2026-10-05 08:3x UTC. Code read: `wt-asahi/bots/bokuto-13-cull/bokuto.hpp:273-281` (byte copy d192d721),
`policy.hpp:570` (`w.me & 4095` is the dragon id). Not assigned by name; S0 approved by D-078 §D, so read before it runs.

## Verdict: amend (S0 estimand and unit), before any S0 number is read

The hash is not a per-turn coin. `((me*7919 + rnd*131) & 7) == 0` with 7919 ≡ 7 and 131 ≡ 3 (mod 8) reduces to
**rnd ≡ 3·me (mod 8)**: each dragon gets a hit on exactly one round in every eight, at a phase fixed by its id
(checked: id 2 → rounds 62, 70, 78; id 4 → 60, 68, 76). Consequences:

1. **A dragon that stays eligible for 8 rounds is culled with certainty.** A "no hit this turn" row is mostly a
   dragon that is culled 1–7 rounds later. S0(a) as written (hit vs no hit per eligible dragon-turn, outcome over
   20/50 rounds) estimates the effect of culling *a few rounds earlier*, not cull vs no cull. The 20/50-round
   windows of the two arms overlap almost entirely; expect a near-zero ITT whatever the true value of a cull.
2. **Rows are not independent draws with propensity 1/8.** Consecutive eligible turns of one dragon are a
   deterministic sequence; the first hit ends the spell. Treating turns as i.i.d. bandit rows (IPW at p = 1/8,
   T-learner) double-counts spells and conditions on survival to the hit round.
3. **What is random:** at spell entry (first eligible round r0) the delay **D = (3·me − r0) mod 8 is uniform on 0..7
   and independent of state** (id assigned at spawn, r0 a property of the state; check the D histogram as a
   diagnostic). The spell may end (pearl in view, unit drop, demand false, why = f/c) before D elapses, so
   P(culled in spell) falls with D. That is a valid instrument.

### Exact change

- Unit = eligibility spell (superset as in §2), first round r0, state at r0.
- Instrument = D (uniform 0..7). First stage: P(cull observed in spell | D) — report it; if it is flat near 1, the
  data carry no cull-vs-no-cull contrast and the route stops at S0 (timing only).
- ITT = outcome(Δteam length / units at r0+20, r0+50; game result) regressed on D (or D = 0 vs D ≥ 4); Wald/IV =
  ITT / first-stage gap. Clusters = series (game) as in the card.
- Uplift (S0(c)) on spell-level rows with the D-contrast as treatment; the S1 gate then means "cull at the first
  eligible round when predicted positive, otherwise never" — which **is** on the data's support (D = 0 spells, 1/8),
  whereas "never" is supported only by spells that ended before their hit.
- Note interference: dragons with equal id mod 8 are hit on the same round; one cull drops `units` below
  `limit − 1` and removes later dragons' eligibility. Team-level outcomes absorb this; per-dragon outcomes do not.

## Other mechanism checks

- Observability: cull inputs (len, units, limit, rnd, pearl in view, head cell) are turn-start legal; `g_br->demand`
  and `dec.why` are internal (card says so) — superset dilution only lowers the first stage. Fine.
- Train/deploy skew: features `x_traj_*` must be computed by the bot from its own history at deploy — TRAJ_VERSION 1
  parity check required before S1 (the card does not list a parity step; add one, as for the p1 slot).
- Leakage: held-out maps dropped by file name — fine; S1 scored on seed 2 — fine. Fixture opponents shared — noted.
- Simpler method first: before any uplift model, the D-contrast mean by two or three hand strata (corridor near,
  enemy within 20) answers whether a gate can beat the hash at all.

## Replication

None numeric: no S0 output exists yet. The hash algebra was checked by running the expression for ids 2–9.

## P(pass) and effect

- P(first stage has a usable gap: P(cull | D = 0) − P(cull | D = 7) ≥ 0.25): 0.45.
- P(S0 finds a D-contrast effect excluding 0 at 90 % on training maps, n ≈ 200 games): 0.20.
- S1 (given S0 passes): keep the author's point +1 pp; P(5th pct > −3 and point > 0) 0.25.

## Dissent (against myself)

If most spells end within a few rounds (e.g. pearls come into view often), the per-turn framing is close to right
and the amendment only costs a re-index. The D histogram and spell-length distribution decide this in one pass.

## Precedent

Logged-propensity off-policy learning (contextual bandits, IPS/DR; Dudík et al.) needs *per-decision* randomisation;
a deterministic round-robin schedule is the classic "systematic assignment" pitfall in A/B testing — analyse it by the
random offset (here D), as with encouragement/IV designs. Halite/Lux bots tuned spawn-cull timing by
self-play sweeps over a delay parameter; the D-contrast is the observational version of that sweep.
