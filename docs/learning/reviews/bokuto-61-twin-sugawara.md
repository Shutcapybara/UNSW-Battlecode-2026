# bokuto-61-mouth — where the pool miss against its twin sits (Sugawara, 5 Oct 2026 21:30Z)

Context: D-089 §D names 61 for trial 5 at ≈ 21:50Z if four conditions hold. Asahi 21:16Z: all four met. Bokuto 21:18Z:
pool vs atlas-off twin 41 −3.68 [−8.09, +0.74], 40/40 seeds ≤ −5 (a clear miss, not "on the line").

## Replication (frozen inputs: Asahi's pool index files, seed 1, read-only)

`wt-asahi/build/asahi/runs/{bokuto-61-mouth/028c97bf, bokuto-41-atlas0/2fdf07f2, bokuto-46-regions/2c202713}/pool/index.jsonl`.
272 paired games each, 0 missing. Wins 61 228, 41 238, 46 235 — matches the card (−10 games = −3.68 pp).

| | discordant 61 wins | 61 losses | two-sided sign p |
|---|---|---|---|
| 61 vs 41 (twin) | 17 | 27 | 0.17 |
| 61 vs 46 | 16 | 23 | 0.34 |
| 61 vs 41, Australia + Slithery removed | 17 | 15 | — |
| 61 vs 46, Australia + Slithery removed | 13 | 13 | — |

By map (61 − 41 over 16): Australia −6, Slithery −6, Islands −3, Autarky −2, QoS −2 … Default +3, Tower defense +5.
Against 46: Slithery −5, QoS −4, Australia −2. **The whole miss is two maps.** Every pool map is a live map, so the
atlas fires everywhere in this panel; the twin contrast is atlas line vs no atlas on the maps it was built for.

Mechanism of the 13 losses on those two maps (61 lost, 41 won 12 of them): 61 loses on "longest dragon" (our queen gone),
where 41 wins "longer queen, 6–33 to 0" in 7 of them (one 61 loss, ouroboros on Australia, is itself on "longer queen 5 to 0"). **The cost is the queen dying, not the economy** — 61's longest is
35–56 in these losses. Consistent with Asahi's qk2 queen wall deaths 10 (61) vs 3 (46).

## Verdict: amend (what the Chair should record when naming)

- The four D-089 conditions are met as written; I replicate condition (2)'s inputs.
- **D-089 §D waived the twin condition for "the 46 line" on the ground that the twin number was on the line.** 61's twin
  number is not on the line. Under D-089's own rule (no relabel), naming 61 is a second waiver of D-087 §C and should be
  recorded as such, with its own grounds (qk2 vs 18 +16.18 [+4.41, +29.41]; h2h vs 46 +7.84 [−1.96, +17.65]; the miss is
  two maps and the queen). Not silently inherited from 46's.
- Which bot: I do not object to 61. The localised miss (queen deaths on Australia/Slithery, both in the ranked draw) is a
  named failure class to watch at the look, not an aggregate atlas harm (17–15 elsewhere).
- I cannot separate the cause (57's queen-blind rule vs 58's reachable target vs the mouth hunk): no 57/58 pool runs exist.

## Other notes

- `chaewon-y04-probe` and `yuna-v05-core` give identical outcome + reason + rounds in 12/34 (61) and 16/34 (41) map-seat
  cells: a near-clone pair inside the pool's opponent clusters. The map × opp bootstrap counts them as independent;
  intervals are a little narrow. Minor; not decision-changing.
- Mechanism seat: inputs legal (sight/sonar-derived routes; atlas covered by D-080 §D / D-089 §D); no split touched.
- Precedent: Halite/Lux agents with map-specific route tables routinely won aggregate panels while failing on a
  few layouts; the fix was per-layout fallbacks, which is the rec-28 idea (withdrawn unit 31) and could return here.

## Forecasts (log; not Brier-scored since D-072 §B)

- 61 trial > +0.204 at look: 0.20; > +0.126: 0.40 (unchanged from 46).
- 61 ladder queen deaths on Australia/Slithery games ≥ 41's local rate: 0.65.

Code: inline python over the three index files (paired by map, opp, seat; seed 1).
