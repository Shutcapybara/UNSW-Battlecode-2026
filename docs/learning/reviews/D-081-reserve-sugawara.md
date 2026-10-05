# D-081 §B — does the free unit slot explain kenma-03 > bokuto-13 on the ladder? (Sugawara, 5 Oct 2026 11:40Z)

**Verdict: the hypothesis is not supported. Recommend `asahi-27-b13-reserve` is not made a trial candidate on this basis.**

Data: ranked replays of team 7, frame.decode, all decoded (240/240, 0 missing). Windows as Daichi's:
14585 = last 120 ranked before 02:13Z (4 Oct 18:48 – 5 Oct 02:09, 24 series); 17388 = 05:02–07:13Z (60 / 12);
17530 = 08:15:41–10:30:04Z (60 / 12). Opponent band = opponent rating in the last ladder snapshot before the game
(≥ 1725: 55 / 35 / 25 games). Post-m2 maps pooled; descriptive only — the windows share one opponent (351), so no
matched comparison is possible from these rows. Unit limit 64 (no own team exceeds 64 in any game).
Code `build/sugawara/reserve/{res.py,summ.py}`, rows `rows.jsonl`.

## 1. bokuto-13-cull already keeps the slot

`bots/bokuto-13-cull/bokuto.hpp` l.349 ("keep one unit slot for the queen": non-queen split blocked at
`units >= limit − 1`) and l.381 (escape-split search only if `queen || units < limit − 1`). The replays agree:

| | 14585 | 17388 kenma-03 | 17530 bokuto-13 |
|---|---|---|---|
| games whose own max units = 64 | 46/120 | 3/60 | 1/60 |
| games whose max = 63 | 0 | 16 | 15 |
| start-of-round snapshots at 64 units, r100–400 | 24.6 % | 0.0 % | 0.0 % |
| queen splits in rounds starting at 62–63 units | 21 | 11 | 10 |
| queen splits at r ≥ 100 (per game) | 85 (0.71) | 59 (0.98) | 44 (0.73) |

Both trial bots behave the same at the cap. A slot difference cannot explain the ladder gap between them;
asahi-27 differs from bokuto-13 only where Kenma's `w.limit − 1` reaches policy split paths that bokuto's guard
does not (policy.hpp l.1113/1145/1164) — in practice 1 game in 60 reached 64.

## 2. The queen cannot use a slot when she dies

A split needs length ≥ 4. Queen length at death ≥ 4: 17388 4/58, 17530 3/43, 14585 24/116; with the team at 64
units **and** length ≥ 4: 0, 0 and 3/116. So even for 14585 a free slot could have changed at most 3 queen deaths.

## 3. kenma-03's queen survives worse, not better

| | 14585 | 17388 | 17530 |
|---|---|---|---|
| queen alive r100 / 200 / 300 / 400 | 49/117, 12/102, 4/85, 3/77 | 32/59, 8/48, 5/42, 0/39 | 42/58, 32/51, 21/45, 14/39 |
| queen alive at the end | 4/120 | 2/60 | 17/60 |
| queen deaths by cause (r0 = Schooltime cage) | h2h 51, wall 34, self 25 (r0 15), body 6 | h2h 30, wall 21, body 4, self 3 | h2h 26, wall 14, body 2, self 1 |
| wall queen deaths per game | 0.28 | 0.35 | 0.23 |

17388 loses fewer games by the queen rule (7 vs 14) because **both queens are dead** in most of its round-limit
games, which are then decided by longest dragon. Result by end reason, ≥ 1725 band:

| ≥ 1725 | elimination W–L | longest W–L | queen W–L |
|---|---|---|---|
| 14585 (55) | 12–13 | 12–4 | 0–14 |
| 17388 (35) | 8–7 | **10–5** | 0–5 |
| 17530 (25) | 4–7 | **2–6** | 1–5 |

Below 1725: 17388 elim 4–5, longest 9–5, queen 0–2; 17530 elim 10–2, longest 9–1, queen 4–9.
Own units (median) at r100/200/300/400 vs ≥ 1725: 17388 20.5/34/49.5/46, 17530 15/22/26/29, 14585 19/41/53/44;
the opponents' medians were 22/35/36/31.5 and 14.5/25.5/17/20.5 — different opponents, so not attributable.

## Reading

The ≥ 1725 gap sits in the length race after both queens are gone (and elimination), not in queen survival.
17530 keeps its queen far more often and still loses the queen race to the stronger half; 17388 lets its queen die
and wins the longest race. Rival explanations not separable here: opponent mix (1 shared opponent; 17388 met 7
teams ≥ 1725, 17530 5), and noise (25–35 games per band). Mechanism candidates worth a look: bokuto-13's queen
protection (escort, cull of length-2 units at r60–340, caution) spending army length that matters only when the
queen dies anyway.

## Recommendations

1. Do not make asahi-27 a trial candidate on the slot hypothesis; if it is built anyway, read it on `qk2` only,
   expecting ≈ 0 vs bokuto-13. P(asahi-27 pool differs from bokuto-13 by > 2 pp either way): 0.20.
2. Add 'end reason × result' (elimination / longest / queen) by band to the trial table and the matched column;
   the decisive class differs between bots.
3. For bokuto-18: queen protection is worth having only if the queen reaches the limit alive; if she dies
   (17530: 43/60), the army must still win longest. Measure longest/total at the limit in games where our queen died.

Precedent: Lux/Halite post-mortems — rule-of-the-limit tiebreakers decide which resource matters late; the
evaluation must be split by terminal condition, not pooled.

Limits: the split-at-cap count uses start-of-round unit snapshots (deaths within a round are not ordered against
splits in the decoder), so I report snapshot cap occupancy rather than exact "units before split".
