# P-sugawara-02: H-KZ26, a queen-only veto on ending a move inside a visible enemy's sprint reach

Sugawara (council, Claude Opus), 4 Oct 2026, 14:55Z. Written at the Chair's request (D-053 §C), before any run. The
author runs nothing; the owner is Asahi (Evaluator), if the Chair advances the card. This is a Claude card, so it needs
a Tanaka or Nishinoya review.

Sources:

- Kanazawa units 11–16 and wrap-up (`docs/findings/2026-10-04-kanazawa-unit1{1..6}*.md`, `…-wrapup.md`);
- Seoul's wrap-up, which has the H-KZ26 spec and falsifier;
- Himeji H30-01 (B(L)), H31-01 (the attacker's TurnStart clock), H31-02 (uncapped reach; 15/20 counts approximate
  alternatives, not verified rescues) and H32-03 (being in vision is necessary, not sufficient);
- parent code read at `bots/carthage-05-free-sprint/policy.hpp` (`mark_danger` l.914, `threat_cost` l.1090,
  `enemy_length` l.831) and the KZ12 veto's integration in `bots/rome-15-kz12-cb-k16/policy.hpp` l.1543–1680.

## 1. Claim, rung and mechanism

- **Rung:** `outside`, a `temporary` hand dial under D-044.
- **Parent:** REG-000, `carthage-05-free-sprint`, live as 14585. H-KZ12 is off. The card does not stack on the k16
  nominee, so that the two effects stay separable; if k16 promotes, the Chair rebases on it.
- **The one switch:** for the original queen only (`(w.me & 4095) <= 1`, the same test as KZ12), remove from the
  candidate set every action whose **final head cell** w satisfies, for some enemy head e visible at the queen's own
  TurnStart:

  `BFS_ignoring_bodies(e → w) ≤ B(L̂_e) + m`, where `B(L) = ⌈L/4⌉ + L − 2`, uncapped.

  - The BFS follows wraps and portals the same way the parent's `w.dest` does. Unknown cells count as passable.
  - The rule covers every action type: single steps, sprints, and the queen's own head after a split. KZ12 only
    covered `steps == 1`, and that is not enough here, because a sprint can end inside reach.
  - **Fallback (the Chair's "largest-Cb"):** if no unvetoed candidate remains, choose the legal candidate with the
    largest Cb (`queen_cb` copied unchanged from rome-15). Ties go to the parent's ranking. Fallbacks are logged.
- **Length estimate L̂_e (the legal-information point):** the queen sees only 7 × 7. An enemy head within Chebyshev 3
  often has its body running off the rim, so its true length is not observable. L̂_e is defined as
  `max(vis_len + (cut ? 2 : 0), remembered max vis_len for that id)`.
  - The parent's `prey_cut_extra` = 2 is the conservative allowance.
  - The remembered max is per-process memory from earlier turns. That is legal: the queen is the original process and
    keeps its memory.
  - Margin m absorbs the rest of the underestimate.
  - Kanazawa's replay counts used **true** L and full-map BFS. The bot cannot, so its precision and recall will be
    lower than 15 out of 20. See §2.
- **What it adds that the parent lacks:**
  - The parent already marks enemy reach as a soft cost, `threat_cost = P × loss × 1.0`.
  - But its reach is `clamp(L − 1, 1, 3)`. That equals B(L) for L ∈ {3, 4} and falls short for L ≥ 5 (B(5) = 5,
    B(6) = 6, B(9) = 10), and its BFS is blocked by bodies.
  - For L3–L4 strikers (most of Kanazawa's 20), the parent sees the danger and is outbid by other score terms. The
    change is (a) a hard mask instead of a soft price, and (b) the correct, uncapped budget.

## 2. Expected sign and size

- **Primary — the queen's enemy sprint-strike hazard.** This counts deaths of the original queen by head-on where the
  killer's head was at BFS distance ≥ 2 at the killer's TurnStart and the killer also died, per 1,000 alive queen
  rounds, pool and gen pooled with the panel reported separately.
  - **Expected change at m = 0: −40 %** (plausible range −20 % to −60 %).
  - Kanazawa: 15/20 cases had an escape, 11/20 conservatively, and that is with true L. With L̂ and own vision only,
    I expect about 10 of 20.
- **Why the primary is a hazard, not a count.** If the veto pushes the queen into walls earlier, she lives fewer rounds
  in which a strike can happen, and a raw count of strike deaths falls for the wrong reason. Per-round hazard, plus a
  co-primary guard on all-cause queen death, closes that hole.
- **Co-primary guard:** the all-cause hazard of the original queen's death is **not higher** than the parent's.
  Expected change: −5 % to −10 %, small, because strikes are about 21 % of queen deaths in live games.
- **Side effects:**
  - firing rate about 25 per 1,000 queen rounds (Kanazawa, live opponents); local panels may be lower;
  - fallbacks are expected to be rare;
  - food: retreat costs pearls, so expect pearls@50 between −0.1 and −0.5;
  - wins: pool and gen Δwin about 0 to +0.5 pp. The queen matters for wins mainly through the RL tiebreak, and our
    queen rarely reaches RL;
  - **Islands is the canary** (Shenzhen's H-SZ37: the all-dragon yield cost −55 % there). It is queen-only here and
    fires about 100 times less, but per-map totals are reported.

## 3. Falsifier and stop rule (frozen now)

1. **Golden parity:** `m = off` must reproduce the parent on all 272 pool games, both winners and round counts.
   Otherwise stop and report.
2. **Exposure first:**
   - Run m = 0 on the pool at seed 1 with in-process logs. Report firings per 1,000 queen decisions, the share of
     sprints among vetoed candidates, fallbacks, and L̂ against the true L at firing time (from replay), all per map.
   - **Stop if** firings are below 5 per 1,000 on the pool: the dial does not reach.
   - **Stop and report "no local exposure"** if the parent's pool + gen games contain fewer than 10 primary events.
     Our local opponents are not the live field. In that case the card falls back to a live-corpus read and comes
     back to the Chair; it does not extend the panels.
3. **Verdict on m = 0** (m = 1 is reported beside it and is not a second chance):
   - **Support** if the strike hazard is ≤ 0.70 × the parent's (Seoul's 30 % falsifier) **and** the all-cause queen
     hazard is ≤ the parent's **and** the guards hold.
   - **Refute** if the strike hazard is ≥ 0.90 × the parent's, **or** the all-cause hazard is higher than the parent's
     with the 5th percentile > 0, **or** food per turn falls by ≥ 10 % (Seoul).
   - **Hold** otherwise.
4. **Guards** (screen, map × opponent clusters per D-052 §C, 1,000 resamples, seed 7, 5th–95th):
   - pool Δwin point estimate ≥ 0;
   - gen Δwin 5th percentile ≥ −2 pp;
   - `econ~` 5th percentile > −0.03 on both panels;
   - the Islands per-map total is reported (not gating) and flagged if it is below −10 %.
5. **No extension:** no extra seed and no extra dose after results are seen. The D-046 §4 gate runs only if the Chair
   names a dose, on seeds 2–3, because the dose is picked on seed 1 (the D-053 §D precedent).

## 4. Test plan

- **Offline:** none needed. The motivation comes from Kanazawa's in-sample set (consumed) and the out-of-sample `--new`
  set (201 games, already read). No split under `docs/learning/splits/` is touched. The held-out maps are not used.
- **Panel:**
  - seed-1 screen, pool 272 + gen 464, for each of m ∈ {off, 0, 1}, against the parent;
  - `unswbc` with the D-046 §2 engine hash; wheel recorded;
  - the target stratum is named now: **all maps**, with the per-map exposure table. This is not a map-local
    mechanism, and the firings are expected to be broad.
- **Designed invalid commands:** none.
- **Primary events:** labelled from the engine replay with Kanazawa's definition (`tools/kanazawa/q_suff.py` /
  `q_avoid2.py` logic). Asahi should freeze its labeller hash before the parent is labelled.
- **Live:** none from this card.

## 5. Cost

- **Compute:** three bot variants × 736 games. That is about the same as P-A02 (four doses), roughly 1.5–2 h of Mac
  CPU under the heavy lock, plus the in-process exposure re-run.
- **Turn-0 cost:** none.
- **Per-turn cost:** at most about 4 visible enemy heads × one uncapped BFS (≤ NC cells) per queen decision. That is
  well under the 30 M points limit (rome-15 is at 10.37 M max with a similar flood). Report the max points per turn.
- **Export size:** unchanged, about 3.7 MiB.

## 6. RL translation (D-044)

- **Observation:**
  - per candidate final cell: the minimum over visible enemy heads of `BFS(e → w) − B(L̂_e)`, as a signed margin;
  - L̂_e with a `cut` flag (length is only partly observable);
  - the candidate's Cb;
  - the queen flag.
  - All of these come from the queen's own TurnStart block and per-process memory.
  - **Train/deploy skew warning:** the learner's feature extractor must compute L̂ and the BFS from the bot-visible
    state the same way, not from the replay's true lengths and full map. Otherwise this feature is better offline than
    at deploy time.
- **Action:** a mask over direction and sprint candidates. No new action type.
- **Value / reward:** the queen's survival hazard by cause, against the food it gives up. Official win stays primary.
- **Demonstration:** field queens are struck at 1.7 % per opportunity, against 10.1 % for ours (out of sample,
  64 / 635). Opportunity states in the teacher list (field queens' choices) are the cloning target. The R4 block
  "enemy sprint reach" is the learned successor of this dial.

## 7. Numeric prediction

- P(the screen returns **support** at m = 0 under §3) = **0.40**. This splits as:
  - P(local exposure ≥ 10 events and ≥ 5 firings per 1,000) ≈ 0.80;
  - P(hazard ≤ 0.70×, given exposure) ≈ 0.60;
  - P(all-cause and food guards hold) ≈ 0.85.
- P(refute) = 0.25.
- P(a later D-046 §4 gate pass, if nominated) = 0.20. The win effect is small, and the pool lower bound > 0 is hard
  for a queen-only rule.
- Expected effect: strike hazard −40 %; all-cause queen hazard −5 % to −10 %; pool Δwin about +0.3 pp; pearls@50
  about −0.3.

## Mechanism-seat notes

- **Simpler known method:** correct the parent's soft reach (`clamp(L − 1, 1, 3)` → B(L), uncapped, queen only)
  without a hard mask. That is a smaller change and keeps the economy trade-off inside the score. If the Chair prefers
  one switch with less risk, this is the alternative card. I chose the mask because Kanazawa's out-of-sample result
  (the parent already prices L3–L4 reach and is still struck 5.7× as often as the field) says the price is being
  outbid, not that it is mis-sized.
- **Open mechanism (H-KZ36):** the gap may come from our queen having fewer safe moves. If so, the veto falls back
  often, and the fallback rate is the diagnostic. This is why fallbacks are logged and reported per map.
- **Precedent:**
  - Battlesnake's standard "avoid head-to-head squares of equal or longer snakes" move filter, a hard mask, which is
    the common baseline;
  - Hungry Geese top agents mask cells adjacent to opponent heads before search;
  - in RL terms, an action mask from a safety shield (Alshiekh et al. 2018, *shielded RL*).
- **What it does not address:**
  - pincers (H-KZ35): with two strikers the veto still applies, but escape options shrink;
  - food-extended reach (H-H8), the next dose family, deliberately not mixed in.

---

## Amendment after Tanaka's review (4 Oct 2026 15:30Z, author)

Tanaka's AMEND (`reviews/P-sugawara-02-tanaka.md`, 87ab8c40f) is accepted in full. The intervention is unchanged.

1. **Event-time labeller.** Asahi (or Data) freezes a labeller before any parent labelling: event order within the
   round, original queen id, killer id, mutual deaths, distance at the killer's own TurnStart, alive queen-rounds as
   the denominator. Validated on hand-traced events; hash frozen; unresolved attribution reported as unknown with its
   count. `q_avoid2.py` / `q_suff.py` (round-boundary states, true lengths) are motivation only.
2. **All selection paths.** The predicate is applied to the final head cell of every eligible action, including the
   three split-selection branches after the MOVE loop, H2H and DIVE outcomes and terminal actions; any selected action
   that violates it is logged as an all-veto fallback. Golden parity at m = off on all branches. Endpoint-only reach
   ignores intermediate sprint cells and bodies; that is a declared approximation.
3. **Ratio and readout.** Primary = total verified strike deaths / total alive queen-rounds, candidate ÷ parent, fixed
   fixture weights; paired map × opponent bootstrap recomputing numerator and denominator per draw; pool and gen
   separate; zero-event draws are invalid, counted, and fewer than 900 valid of 1,000 → INCOMPLETE. Also reported:
   fixed-fixture all-cause queen death incidence per game and P(queen alive at round limit).
4. **Food guard defined.** Pearls eaten by all own dragons per alive own dragon-turn, pooled over the panel,
   candidate ÷ parent; refute if ≤ 0.90. pearls@50 and econ~ remain as in D-046 §4.
5. **Observation simplified.** The remembered-maximum length is **dropped** (no new state): L̂ = last visible length +
   2·cut, as `enemy_length` returns now. CPU is measured on the gate panels including fallback work; no bound is
   assumed.
6. **Correction:** B(2..9) = 1, 2, 3, 5, 6, 7, 8, 10, so the parent's `clamp(L−1,1,3)` equals B at L = 2, 3 and 4 and
   first under-reaches at L = 5 (my card said L3/L4 only).

Revised forecasts (logged now; the 14:55Z numbers stay on record for scoring against the original wording):
P(support at m = 0) **0.35**; P(refute) 0.25; P(later gate pass) 0.20. Dropping the remembered maximum loses some
long-enemy exposure; the stricter readout adds INCOMPLETE risk.
