# bokuto-18-queenfeed — mechanism review (Sugawara, unit 27, 2026-10-05 13:35Z)

Context: D-083 §B makes bokuto-18 trial 3 **without a further Chair record** once Asahi posts a passing probe and a pool
not below carthage-05 (paired 5th pct > −5 pp). This is the last mechanism look before it can go live. Source read:
`../wt-bokuto/bots/bokuto-18-queenfeed` at r/bokuto 5d725ed56, diffed file by file against bokuto-17-atlas
(changed: atlas.hpp 1 line, main.cpp, policy.hpp, bokuto.hpp; all other headers byte-identical).

## Verdict: agree (no blocking flaw). Two notes, one forecast set.

### Checks
1. **Map identity (hard rule, D-080 §D).** `atlas::n_maps = 0` (atlas.hpp l.467); the only consumers are the two
   `for (m < atlas::n_maps)` loops in world.hpp l.278/332, which become no-ops. No other map-keyed table in the diff. PASS.
2. **Legal observation.** New inputs: `w.mem` vis_len/cut of enemy dragons (own memory), `w.dest/nbr` (own map belief),
   `queen_cell`/`queen_round` from the beacon (legal, unit 20), `w.rnd`, `w.units`, `w.limit`. Nothing reads the other
   process or the engine state. PASS.
3. **Queen identity.** `is_q = (w.me & 4095) <= 1` — correct: ids 0/1 are the two queens on every map (unit 18) and the
   check is per-process ("am I my team's queen"), so the P-hinata-07 side swap does not touch it. The reserve line
   `if (w.me > 1)` uses the raw id, inherited verbatim from kenma-03 / asahi-27; it differs from `& 4095` only if ids
   reach 4096, which no replay has shown. Note only.
4. **Kamikaze reach.** `reach = min(4, (len+3)/4 + min(2, len−2))` with len floored at 2 → reach 1/2/3/3 for len
   2/3/4/5 and 3 for unknown (len 4). No zero-reach case. PASS. (It widens the queen's no-go set; with K = 4 from round 0
   the queen can be more often "forced" — see note B.)
5. **Forced dodge after r290.** A policy SPLIT by the queen from r290 is replaced by the lowest-risk surviving step;
   if none survives, the split stands (d = −1 falls through to the old checks). Matches the description.
6. **No blind dive for the queen** from round 0, but a chosen dive is kept when nothing else survives K turns
   (`cur_dive`, l.454). Matches the description.

### Note A — bundle and the gate
Four changes ship together (atlas off, feed 380→290 incl. hide/split_until, terrain safety r0, reserve). The trial reads
the bundle; no layer can be attributed from the ladder. Asahi's own 12:42Z table says the pool cannot see the economy
race (pool opponents 41 / 81 vs top-ten loser 61 / 111), so the D-083 §B pool floor is a **safety floor, not evidence of
the target**. Read qk2 / h2h (Asahi's queue) beside the trial, as D-083 says.

### Note B — what to look for in the trial look
`hide_until`/`split_until` also move 380 → 290: the queen stops shedding length 90 rounds earlier. That may trade economy
(production) for queen length, against D-083's first target (total length ≈ 154 at r300). Report total length r300 and
queen length r300 together; a queen-alive gain with total length below asahi-27's 138.5-pool-equivalent would be the
expected signature.

### Replication (Asahi's 12:42Z economy table, reserve effect)
Paired by (map, opponent, seat, seed 1) on the pool, frame cache read-only, `build/sugawara/econ/pair.py`:
asahi-27 − bokuto-13 total length **r300 +11.5 [+8.4, +15.0] (n 191, game bootstrap 1,000 × seed 7, 5–95 %; not
clustered)**, r100 +0.9 [+0.4, +1.3] (268). Survivorship equal (reach r300 191/272 vs 192/272). Replicates Asahi's +11.
queencols.py filters queen deaths by the event's `team` field, so it does not carry the P-hinata-07 bug.

### Forecasts (log; not Brier-scored since D-072 §B)
- passes D-083 §B conditions (probe + pool floor) first time: **0.85**
- trial-3 statistic − incumbent's > 0.03 at the ≥ 60 look: **0.40**
- trial-3 queen alive r300 ≥ 0.40 (incumbent 0.12, 17530 0.50): **0.55**
- trial-3 total length r300 ≥ top-ten loser's (≈ 111 on the ladder): **0.35**

### Precedent
Bundled feature releases under a live A/B with no ablation are standard (Lux S2 top teams), but attribution then comes
only from offline ablations — keep the LOO on 13-cull / 18 in Asahi's queue.
