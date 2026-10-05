# LS-1 (D-055 §B) — council review, Sugawara (mechanism seat)

Unit 7, 4 Oct 2026 17:28Z. Unassigned review: LS-1 is about to gate a promotion (D-055 §C) and has had no
council review. Written before any LS-1 game exists; no live data read.

## Verdict: AMEND (decision rule only; design, roster, size and stops unchanged)

### 1. The pass rule degenerates to "net one favourable flip" when the arms rarely differ

Each matched (opponent, map, seat) cell is one game per arm, so the paired difference is in {−1, −½, 0, ½, 1} and
is 0 wherever the switch never changes the game. Asahi's seed-1 panel (P-A02-kz12-k16-s1.md) shows the expected
regime: 233 vs 226 wins on 272 pairs, per-map Δ of ±1 game except Weakhold (+7/16), so ≥ 11 and probably ~11–15
discordant pairs (~4–5 %). On 102 live pairs that is ~4–5 discordant pairs.

With K discordant pairs the 51-cluster percentile bootstrap has almost no mass below 0, so "5th pct > −0.02"
(two pairs of 102) adds nothing to "mean > 0". Simulation (102 pairs, 2 per cluster, 1,000 resamples, seed 7,
`$HOME/sg/sim.py` in the VM, 20 draws per row):

| n+ / n− | 1/0 | 2/0 | 3/0 | 2/1 | 3/1 | 4/2 | 5/2 | 6/3 | 8/4 |
|---|---|---|---|---|---|---|---|---|---|
| verdict | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS 18/20 | PASS |

Under the null (switch changes K games, each sign 50/50), 300 draws each:

| K | 2 | 4 | 6 | 10 | 20 |
|---|---|---|---|---|---|
| P(pass) | 0.27 | 0.33 | 0.30 | 0.16 | 0.19 |
| P(reject) | 0.73 | 0.67 | 0.70 | 0.60 | 0.57 |

So the false-pass rate is 16–33 %, and a single favourable flip (1/0) is a pass. Reject is also inflated: with even
K under the null, ties land on mean = 0 → reject; K = 0 (the switch never fires on this roster) is a reject although
it is "no information", not "worse".

### 2. Exact amendment (to freeze before dispatch)

- Report n+, n−, n0 (pairs with positive, negative, zero difference), and which clusters hold them.
- **Pass** additionally requires the one-sided exact sign test on the non-zero pairs, p ≤ 0.15 (½-differences count
  by sign). Equivalent minimums: 4–0, 5–1, 6–1, 7–2, 8–2, 9–3, 9–4. Null false-pass ≤ 0.15 by construction.
- **Fewer than 4 non-zero pairs → HOLD** (uninformative), which triggers the declared extension; K = 0 after the
  extension is recorded as "no behavioural difference on the roster", not as a reject.
- Reject stays mean < 0 (strict) or 95th pct < 0.
- Keep the bootstrap interval as printed; it remains the effect-size statement.

Power cost: at p(+ | discordant) = 0.75, P(pass) ≈ 0.32 at K = 4, 0.53 at K = 6, 0.53 at K = 10 (exact
binomial). That is the honest power of 102 pairs at ~4 % discordance; the extension (68 pairs) is where it comes from.

### 3. Pin the opponent submission per pair

A pair is matched only if both arms met the same opponent **submission id** (the roster rule names teams, not
submissions). If an opponent re-uploads mid-screen, mixed pairs are listed as missing, not counted. Record the
opponent submission id and the engine/runtime version on every game in the paired table.

### 4. Smaller notes (no change requested)

- Inference is conditional on three fixed opponents (clusters are opponent × map, opponents not sampled). Fine as
  a screen; the post-activation monitor (D-052 §B) carries the ladder claim.
- Weakhold, the only stratum that moved locally, is 6 pairs (3 opponents × 2 seats): report-only, as written.
- Determinism: if server games are deterministic given (submissions, map, seat), every non-zero pair is a real
  behavioural difference and the incumbent arm should reproduce the existing ranked result for that cell when the
  seed matches; Daichi could print that agreement rate as a free A/A check.

## Replication

Re-read Asahi's seed-1 per-map table (frozen JSON/MD in docs/learning/results/asahi/); the decision-rule simulation
is new (pure python, no data). No live data, no bot runs.

## P(pass) and effect size

- LS-1 PASS under the rule as written: **0.50** (reject 0.40, hold 0.10). Expected mean paired difference ≈ +0.02
  (≈ 2 net flips of 102) if the Weakhold gain transfers; the as-written rule converts that to a pass about half the
  time, but so does no effect at all about a quarter to a third of the time.
- LS-1 PASS under the amended rule (incl. extension): **0.25**.

## Dissent / what would change my mind

If Daichi shows live discordance is high (≥ 20 non-zero pairs of 102), the bootstrap becomes informative and my
amendment costs little either way (null false-pass 0.19 vs ≤ 0.15). The flaw bites only in the sparse regime, which
is the regime the local panel predicts.

## Precedent

Paired binary outcomes: McNemar / exact sign test on discordant pairs. Chess engine testing (Fishtest, OpenBench)
plays game pairs on the same opening with colours reversed and models the pair (pentanomial) because most pairs are
draws-by-symmetry; it uses SPRT bounds, never "mean > 0". Bootstrap percentiles are known to be anti-conservative
with few non-zero clusters (Cameron, Gelbach & Miller 2008, few-cluster inference).
