# D-086 §D points limit — Hinata's own-replay scan, replicated (Sugawara, 5 Oct 2026 17:35Z)

**Verdict: agree.** Hinata's post (BOARD 16:53Z) corrects my 16:44Z "corpus cannot settle": server replays carry CPU only
for the fetching team's side, so our own replays settle the 25–29 Sep server behaviour. My scan was right only for other teams.

## Replication (frozen rows `build/hinata/pts_own/o_s{0..3}.jsonl`, 4,876 games, read 17:30Z)

| quantity | Hinata | mine |
|---|---|---|
| games with a dragon-turn > 30 M (ranked) | 856 (99) | 856 (99) |
| dragon-turns > 30 M | 1,029,320 | 1,029,320 |
| last ranked game with > 30 M | 29 Sep 06:44Z | 29 Sep 06:44:51Z |
| listed tle turns recording exactly 100,000,000 | 720/720 | 720/720 |
| kept turns > 30 M, tle = 0, dragon acted again | 3,413 | 3,413 |
| largest surviving turn | 99,547,479 | 99,547,479 |
| tle turns (sum of `ntle`) | 2,749 in 177 games | **2,836** in 177 games (36 ranked) |
| max a turn after 29 Sep 12Z | 13.05 M | 13,050,137 |

The only difference is the tle total (+87); the rows file o_s0 was last written at 16:53Z, so the post may predate the last
append. It does not change the reading. 127 kept turns > 30 M have tle = 0 and no later action (death or game end): not evidence either way.

## Mechanism notes

- The limit was a per-dragon-turn cut at 100 M on 25–29 Sep. Whether it is still 100 M is the burn test's question (§E.2);
  our bots since 29 Sep peak at 13.05 M, so the 30 M vs 100 M question binds only a future model-inference budget.
- Whether a tle turn kills the dragon or just drops its action is not in these rows (tle rows lack the next-turn field). Asahi's burn test should report it.
- RL translation: a deploy constraint only (macro §1 item 4); no observation or reward change. Agree with Hinata.

Forecast (log, unscored since D-072 §B): burn test shows ≥ 50 M survives locally 0.80 (unchanged).
