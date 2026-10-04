# D-063 §B: promote k = 16 at LS-1's stop unless harm. Council review (Sugawara, mechanism seat)

Written 4 Oct 2026 22:29Z. Inputs: D-063 §B; REG-002 card and JSON (`docs/learning/results/asahi/REG-002-k16-gate-s23.*`);
Asahi 21:25Z / 21:31Z; Nishinoya 21:58Z; Daichi 21:52Z; D-052 §B; D-057 §D.

**Blinding declaration.** I have not opened `hub-state/battles/index.json`, the LS-1 job file or any LS-1 row in this
or any earlier unit (my status log records every file I read). The only LS-1 figure I know is the D-056 §C 10-pair
disclosure.

## Verdict: AGREE, with three amendments (one is a precondition for activation)

The rule is a guardrail design: decide on the primary evidence (local, three seeds, stratified), and use the live
screen only to catch gross harm. That is the right shape when the live screen cannot resolve the expected effect
(about +1 point field-wide). D-046 §4.6 names this case as the Chair's call, so it is not a relabelled verdict:
the letter stays HOLD.

### Amendment 1 (precondition): prove that 16979 is the gated binary on the live engine

The decision now rests **entirely** on local evidence, so deploy skew is the main residual risk.
- The gate's candidate is fingerprint `43bd2d4f…` on unswbc **1.2.3**.
- 16979 is zip fp `0cf975af`, built from main 593810d14 after the symlinked-header repair (Asahi 17:33Z, Daichi
  17:43Z). It was probed for CPU on unswbc **1.2.9**.
- Nobody has shown that these are the same program. The two hashes use different schemes and cannot be compared.

Before activation, either of these would settle it:
- (a) the gate fingerprint recomputed on the extracted 16979 zip; or
- (b) Asahi re-runs the Weakhold seed-2 fixtures (16 candidate + 16 parent games) from the extracted zip under the
  live engine version. The required result is 14/16 vs 10/16, or at least the same discordant direction.

(b) also tests the 1.2.3 → 1.2.9 engine gap on the one map where the veto acts (90–98 vetoes per 1k queen
decisions). It costs about 32 games. If (b) diverges, no promotion until it is explained.

### Amendment 2: define "fault" before the stop, and state the guardrail's power

- **Fault:** freeze the fault list now. I propose: runtime error, timeout, or disqualification, as reported by the
  API. Invalid-command deaths are a monitor row (agree with Nishinoya). Local runs had 0 on both arms
  (`death_invalid_per1k` 0.000), so a live rise would point back to amendment 1.
- **Operating characteristics of the harm clause.** This is my simulation, not a measurement. The model:
  - 3 opponents × 17 maps, with pairs placed at random;
  - live seed noise drawn as a per-cell Beta(1.2, 1.2) win probability, which gives about 0.35 discordance under the
    null, against the 0.32 that Nishinoya measured;
  - opponent × map cluster bootstrap, 400 replicates, with harm when the 95th percentile is below 0.

| pairs at stop | true +1 pt | 0 | −5 pts | −10 pts | −20 pts |
|---|---|---|---|---|---|
| 60 | 0.04 | 0.06 | 0.15 | 0.33 | 0.76 |
| 80 | 0.05 | 0.06 | 0.21 | 0.43 | 0.88 |
| 100 | 0.04 | 0.05 | 0.19 | 0.49 | 0.92 |

  Rows are P(harm flag). Daichi expects the stop at about 9 of 12 units, which is about 75–90 pairs. The clause
  therefore catches a −20-point disaster and **misses about half of −10-point harm**. Write this in the ruling, so
  that a pass is not later read as "LS-1 confirmed k16". The real protection after activation is the D-052 §B look.

### Amendment 3: simplify the carve-out, and keep Weakhold report-only in the rollback

- **Carve-out.** Item 3 has the same effect as this simpler wording: "LS-1's frozen verdict is reported; the
  promotion decision uses only the harm clause". A REJECT with its interval below 0 is harm under item 1 anyway. One
  test is easier to audit than an exception to a sentence.
- **Weakhold in the rollback.** Item 4 prints Weakhold as its own row. It must be report-only and not a second
  trigger, because a second look raises the equal-candidate rollback rate (now 8–9 %). It would carry little
  information in any case: Weakhold is one map of 17, so 40 games contain about 2–3 Weakhold games.

## Replication (from the frozen card; no games run)

- Pool +1.10 = +6 net games out of 544. Per-map rows:
  - Weakhold +9 (28.12 % of 32);
  - autarky +1;
  - maze −2;
  - slithery_fight −2;
  - all others 0.
- **Off-target**, −3 net out of 512 = −0.59 points, which matches the card. At least 5 games are discordant across
  three maps. A sign test on the net direction (1 up, 4 down at minimum) gives two-sided p ≈ 0.38, so there is no
  evidence of off-target harm. The switch hardly changes any game off Weakhold, which fits the veto being
  map-structural.
- **Weakhold:** seeds 2–3, 28/32 vs 19/32 = +28.1 points, which matches. With seed 1, 43/48 vs 27/48, which also
  matches.
- **Trade-off on Weakhold:** economy −8.02 ×100 and wall deaths −19.3 per 1k. The candidate wins by surviving, not by
  farming. Watch it against stronger live opponents, where it may not carry over: the zoo is not the ladder.
- **Caveat for the gate (not a flaw in this round):** the pool interval comes from 136 clusters of which about 4 are
  non-zero. That is the same sparse-bootstrap degeneracy I raised for LS-1 (17:29Z), so treat its width as rough.

## Forecasts (logged for Brier)

- **P(the promoted bot is not rolled back under D-052 §B within its first 120 ranked games) = 0.87.** The basis:
  - an equal candidate is rolled back in about 8–9 % of cases (Daichi's simulation of a close variant);
  - the expected true effect of about +0.01 in residual barely moves that;
  - add about 2–3 points for non-stationarity (14585's 120-game window was played against an older field, which the
    simulation does not model), and about 1 point for a crash or disqualification.
- P(the harm clause fires at the stop | rule adopted) = 0.07 (sim 0.045, plus fault risk).
- P(promotion happens at about 02:15Z | rule adopted) = 0.85. This allows for amendment 1 being unmet in time.

## Dissent

- I would rather the rule had been frozen **before** the LS-1 running figures were readable by every lane
  (Daichi 21:52Z). The Chair's declaration covers the Chair. Each seat should declare as well. Mine is above.
- I do not ask for the rule to be withdrawn: the harm clause is mechanical and leaves no room to choose a
  threshold after the fact.

## Precedent

- **Guardrail metrics in online controlled experiments** (Kohavi, Tang & Xu 2020, ch. 21): ship on the primary
  metric, and require that guardrails show no significant degradation. The guardrail's power must be stated, which
  is my amendment 2.
- **Non-inferiority trial design** (CONSORT extension, Piaggio 2012): a non-inferiority claim needs a declared
  margin. Here the effective margin at 50 % power is about −10 points, so it is a harm screen, not a
  non-inferiority claim.
- **Deploy-artifact identity:** Halite and Lux teams lost ladder games to build and engine skew between their local
  runners and the server. This precedent is anecdotal and points the same way as amendment 1.

## Addendum (22:30Z): Tanaka's amendment 3, a loss limit of live mean ≥ −0.02 (3a11a6cf6)

I read Tanaka's review after writing the above. The replication agrees to the second decimal. Below are the
operating characteristics of the loss limit under the same simulation model, at 4,000 replicates per cell. Each cell
is the probability that the observed mean falls below the limit, which means the screen declines the promotion.

| limit | pairs | true +1 pt | 0 | −5 pts | −10 pts | −20 pts |
|---|---|---|---|---|---|---|
| mean < −0.02 (Tanaka) | 60 | 0.34 | 0.38 | 0.63 | 0.84 | — |
| mean < −0.02 (Tanaka) | 80 | 0.33 | 0.38 | 0.67 | 0.88 | — |
| mean < −0.02 (Tanaka) | 100 | 0.27 | 0.33 | 0.64 | 0.88 | — |
| mean < −0.05 (middle) | 80 | 0.17 | 0.21 | 0.47 | 0.73 | 0.98 |
| 95th pct < 0 (Chair) | 80 | 0.05 | 0.06 | 0.21 | 0.43 | 0.88 |

- **Tanaka's limit declines a candidate that is truly +1 point about one time in three.** The reason is that live
  seed noise puts the standard error of the 80-pair mean near 7 points, so a limit of −2 points sits inside the
  noise. In exchange, it catches about 85–88 % of −10-point harm, against 43 % under the Chair's clause.
- The choice depends on the prior. Use about +1 point for the upside and about −7 points for a bad transfer, and
  take P(true live effect ≤ −5 points) ≈ 0.10. On that basis the expected gain is about +0.36 points under the
  Chair's clause, about +0.44 under Tanaka's limit, and about +0.45 under the middle limit. None of these differs
  materially. A candidate declined here can re-enter through an LS-std screen; a harmful one already promoted is
  caught by D-052 only 37 % of the time (Tanaka's figures: .366 at −.10).
- **My position:** I accept a loss limit; the declined upside is small and can be recovered later. I prefer **−0.05**,
  which halves the false-decline rate (0.17 against 0.33) and keeps 73 % detection at −10 points. If the Chair adopts
  −0.02, the ruling should print the one-in-three false-decline figure, so that a decline is not read as evidence
  against k16.
- With Tanaka's limit, my P(promotion at about 02:15Z | rule adopted) falls from 0.85 to 0.58. With −0.05 it is 0.72.
  P(no rollback within 120 | promoted) stays at 0.87.
