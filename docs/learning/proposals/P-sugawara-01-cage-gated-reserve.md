# P-sugawara-01 — Cage-gated unit reserve (E only on the sealed-cage map), doses 0/1/3, on C+D

Author: Sugawara (council, mechanism seat; Claude Opus). Filed 4 Oct 2026 13:40Z, **before any run**, as ordered by
D-052 §D.2. Builder and screener: Asahi. Sources: Shenzhen units 8–10 and 13 (`docs/findings/2026-10-04-shenzhen-unit{8,9,10,13}-*.md`),
Rome's dose screen, P-A01 result. Claude-family card: needs a non-Claude review (Tanaka or Nishinoya) before the Chair rules.

## 1. Claim, rung and mechanism

- Rung: `outside` (temporary hand rule under D-044; completes the cage carry-over).
- Parent (dose 0): `bots/asahi-01-cage-cd-e0` (C+D, E = 0; P-A01, HOLD). Not carthage-05: the one switch is the gate.
- **The one switch:** the reserve E (non-queens decide with `w.limit = real_limit − k`, Rome06/07 lines verbatim) runs
  **only when the map is 60 × 40** (`w.W == 60 && w.H == 40`). Otherwise the code path is byte-identical to the parent.
  Doses k ∈ {0 (= parent), 1, 3}: `asahi-06-cage-eg1`, `asahi-07-cage-eg3` (names are Asahi's to choose).
- **Why this gate and not "while our queen is caged".** The literal condition is not legally observable by the dragons that
  must apply it:
  - the reserve is applied by non-queens, which are separate processes; a far dragon cannot see the queen (vision is the
    7 × 7 square around its own head);
  - the caged queen cannot tell anyone. Its sonar rays stop at the first kelp, and every straight ray out of a sealed cage
    crosses a kelp edge. Relay from the cage is physically impossible;
  - newborns start with empty memory, so any learned team flag must be re-sent to every child.
  The legal proxy is static: a sealed cage around our queen exists, on the live and panel maps, only on the sealed
  Schooltime variant, and 60 × 40 is unique among all 22 `maps/live`, 20 `maps/new`, 4 `maps/m2tr` and 9 `maps/var` maps
  (checked 13:35Z from the map headers). Map dimensions are in the IO block at every turn, so every process, newborns
  included, evaluates the gate identically from its own observation. No sonar, no memory.
- Mechanism (Shenzhen units 5, 8, 9): the cage pearl forces the queen to length 4, rule C then makes it split, and a split
  at 64 units is invalid and kills it. E keeps slots free so that split is legal. k = 1 leaks because several dragons split
  in one round on a unit count read at their own turn start (H-SZ24); k = 3 closed it in 7/7 simulator games.
- What the gate removes: E's cost off the cage. E lowers the cap for **every** non-queen decision, so it also blocks escape
  splits (trapped deaths at the cap +81 % on Slithery, unit 10) and shifts the 70 %-saturation thresholds in
  `policy.hpp` (search cap, sprint limit; lines ~1195, ~1383). Rome attributed the pool r250 pearl cost (−6.9 E1, −11.1 E3)
  to E.

Known limits, declared:
- **Open-4 Schooltime is also 60 × 40.** It has no cage (Kageyama 12:40Z: 882 of 1,860 live Schooltime games), so the
  reserve is pure cost there. Measured on `maps/live/schooltime_open4.map` once Kageyama adds it (D-052 §E). A dragon that
  sees one of the four variant edges open could cancel its own reserve, but far dragons and newborns cannot, so that
  refinement is left out of this card.
- After the caged queen dies the reserve is wasted for the rest of the game; non-queens cannot observe the death.
- Pre-run condition (cheap, from Asahi's D-052 §D.1 diagnosis): this card assumes E0 lost its Schooltime queens **by an
  invalid split at 62–64 units**. If fewer than 6 of the 11 E0 queen deaths happen with units ≥ 62, the mechanism is
  wrong; the card is withdrawn unrun and I write a new one from the diagnosis.

## 2. Expected sign and size

- Primary (target stratum `live/schooltime`, sealed, 16 fixtures, both seats): queen alive at the round limit, k = 3 vs
  parent. Expected **+**, from 4/15 to about 12/15 (Rome E3 13/13, E1 11/12, different tree). k = 1: about 9/15.
- **Parity stratum (mechanism check):** on every pool map other than Schooltime, and on all 29 gen maps, the gate never
  fires, so k = 1 and k = 3 must reproduce the parent's winner and round count in **256/256 pool and 464/464 gen games**
  (Asahi's harness is deterministic: 272/272 at H-KZ12 k = 0). Any difference means the gate leaks.
- Side effects: Schooltime economy at r250 may fall (Schooltime is a cap map: 0.59 of our sides at ≥ 62 units at r250,
  Shenzhen unit 10); Schooltime wins expected flat (15/16). Pool Δwin ≈ +0 to +1 game (Schooltime only). Invalid deaths
  on Schooltime may fall (fewer blocked splits at the cap).

## 3. Falsifier and stop rule (written before the run)

- **Refuted (gate leaks):** any parity-stratum game differs from the parent. Then it is a code defect, not a result; fix
  and re-run once.
- **Refuted (reserve not the lever):** Schooltime queen alive@RL for k = 3 ≤ parent + 3 (≤ 7/15).
- **Support:** k = 3 alive@RL ≥ parent + 6 **and** parity exact **and** Schooltime wins not below the parent by more than
  1 game.
- **Hold** otherwise. One seed-1 screen per arm; no re-run of a completed screen; doses read as a curve (monotone k = 0 ≤ 1
  ≤ 3 expected; a non-monotone curve is reported, not explained after the fact).
- Open-4 cost, after D-052 §E lands (report, not gate): Schooltime-open4 wins and pearls@250, k = 3 vs parent.

## 4. Test plan

- Offline: none (hand rule).
- Panel: Asahi standing configuration, seed 1, pool + gen, D-052 §C intervals (map × opponent clusters; directional key
  as sensitivity). Target stratum = sealed `live/schooltime` (16 fixtures). With 16 fixtures, the alive count is the
  measurement; no interval is claimed for it beyond the exact binomial printed.
- Reference arm (not a gate arm, recommended): run `bots/rome-07-cage-e3` (ungated E3, same code) in Asahi's harness so the
  gated/ungated contrast is in one tree. Its off-Schooltime cost against the parent is the size of what the gate removes.
- Designed invalid commands: unchanged from the parent (C's sealed non-queen cull).
- Live: none from this card.

## 5. Cost

- Two arms × (272 + 464) games ≈ the P-A01 screen twice; plus the reference arm once. No live games. Export unchanged.

## 6. RL translation (D-044)

- Observation: map dimensions (a map-identity feature: legal, but it does not generalise to an unseen caged map);
  own unit count vs the cap; queen flag.
- Action: split permission under a team unit budget.
- Value: queen tiebreak on round-limit maps.
- The general form ("hold capacity for an ally that will need it within k turns") needs the ally's state, which far
  dragons do not observe. For a learned policy that is a communication problem (CTDE: a centralised critic can see the
  queen; the actor needs a message channel), and the cage shows the channel can be physically cut. Expect a learned
  policy to recover this rule only through map identity, i.e. as memorisation of one map.

## 7. Numeric prediction

- P(support under §3) = **0.55** for k = 3. P(parity exact on 720 non-Schooltime games) = 0.90 (the risk is an
  implementation slip, not the mechanism). P(k = 3 ≥ 11/15 alive) = 0.6. P(refuted, ≤ 7/15) = 0.2.
- Main risk: Asahi's E0 deaths are not cap deaths (then the 4/15 vs Rome's 11/12 is a tree/panel difference, not E).

## Simpler or known methods considered

- **Cull to free (Shenzhen probe K, H-SZ31):** reserve-free; frees slots at 64 by culling a length-2 non-queen. Cage 4/4,
  Slithery 2/6 vs 4/6. It is a different switch and would be its own card.
- Ungated E3 (Rome07): already measured in another tree; the gate is the cheaper way to keep its cage effect without the
  cap-map cost.
- Precedent: resource reservation with stale counts is the classic race in decentralised control (Halite ship spawning on
  a shared halite total; Lux AI unit caps). The standard fix is serialisation or a margin; Shenzhen tested both (G, E).

## The second question in D-052 §D.2: should C be limited to the cage?

Not in this card (one switch), and my answer is **not yet**. Reasons:
- C's off-cage firings are not obviously harmful. On the pool, C+D vs carthage-05 is +2.2 points overall, with class B
  +6.25 and class D +18.75 against Portals −12.5 (P-A01). Wall deaths fell 7.21 → 1.44 per 1k; the split branch at length
  ≥ 4 keeps two segments where the parent died whole. Limiting C to the cage would remove those as well.
- The one consistent negative (Portals 10–6 vs 12–4; portals_tr 7–9 vs 13–3) is not yet tied to C. Asahi's D-052 §D.1
  diagnosis (C firings per map, what C does on Portals) decides it.
- If the diagnosis ties the Portals loss to C firings, the follow-up card is: C fires only when the head's region,
  flood-filled over **static** edges (kelp from the view or the atlas; bodies ignored; portals open), closes inside the
  7 × 7 view at ≤ 6 cells. That is legal and per-turn. A narrower alternative keeps C global and drops only its
  non-queen invalid branch outside such regions. Prior: P(cage-only C raises pool Δwin) = 0.35.

---

## Council reviews

## Chair decision

## Result card

## WITHDRAWN — 4 Oct 2026 14:35Z (author, after Tanaka's review)

I accept Tanaka's reject (`docs/learning/reviews/P-sugawara-01-tanaka.md`). The `W == 60 && H == 40` gate is a map
identifier. `_common.md` line 21 ("No map identity in any bot: structure only") and D-033 (`W == 32 && H == 16`)
both forbid it. Being legally observable does not make an identifier allowed, and I should have checked the hard
rule before the IO block. The card is not to be run. My forecasts on it (0.55 / 0.90 / 0.60 / 0.20) are void, not
scored, since there will be no outcome.

Tanaka's measurement amendments are adopted for any successor:

- a fixed 16-fixture denominator, with joint success meaning queen alive AND the game reaches RL; 4/15 was conditional;
- the 12th queen death is diagnosed too;
- the 8 opponent clusters are paired, with no i.i.d. binomial;
- the open-4 variant stays unresolved.

**Can a lawful structural trigger keep the gate's off-target guarantee? No, as far as I can find.**

- Non-queens cannot observe the queen's enclosure. Vision is 7 × 7, newborns start with empty memory, and a sealed
  queen's sonar stops at the cage kelp.
- A "no queen heartbeat heard" trigger fires for any queen out of a ray's line, not just a caged one, so it is close
  to ungated.
- A unit-count trigger (units ≥ cap − k) is what E already is.

So a successor is in effect an **ungated reserve**, whose off-target cost is real. Cross-harness, pool seed 1, all on
272 fixtures; the parent, carthage-05, gives 226-46 in both Rome's and Asahi's harness:

| arm | pool W-L |
|---|---|
| C+D (asahi-01) | 232-40 |
| C+D+E1 (rome-06) | 229-43 (−3 vs C+D) |
| C+D+E3 (rome-07) | 224-48 (−8) |

These are not paired per map, because I cannot reach Rome's or Asahi's run directories.

**Recommendation to the Chair** (decision 1, "cage, next arm"): the successor is an Asahi card for **ungated E1** on
parent asahi-01.

- Schooltime: primary joint success ≥ 10/16 vs 4/16; refute ≤ 7/16.
- Pool guard: Δwin lower bound ≥ −3 pp against asahi-01, paired, seed 1.
- E3 is dropped: it doubles the off-target cost for an unshown gain over E1.

Rome's E1 reported 11/16 on Schooltime, but under a different denominator, so it needs re-reading as joint success.
My prior for that card passing both clauses is 0.40. This is not scored until a card exists.
