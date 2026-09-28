# ouroboros-t01-gavroche32-trapsplit

This is an unmodified copy of gavroche-v32-supported-divecap (`inner_main.py` and its modules) behind a stdout filter,
`trapsplit_guard.py`.

**What the filter does.** When the host's MOVE would take a certain-death first step, no enemy-head trade is
available, length ≥ 4 and the team is below the unit cap, the MOVE becomes `SPLIT length-2`. This is Vibing++'s
trapped-salvage rule.

**Frozen test.** 78 paired fixtures (serre / sinbad / fry × 13 public maps × 2 sides):

| | Control | Graft |
|---|---|---|
| W–L | 51–27 | 52–26 |

- Activation: 47% of fixtures.
- Schooltime: −2.
- Verdict: **not supported**.

It is kept as a documented null result and as a reusable stdout-filter graft harness. Evidence:
`experiment_data/team_recon_306_20260927_claude/REPORT.md` §5b.
