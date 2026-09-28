# ouroboros-m01-vibing-mimic

A behavioural clone of the public team **Vibing++** (team 306, submission 8264). Every move is a learned imitation
of that team's recorded actions.

- **Model:** one boosted-tree model (`model.json`, 120 iterations × 31 leaves, pure-Python inference). Trained on 96
  public games (84 train + 12 validation) and fitted only on legal inputs: the dragon's own round block and its own
  process memory. `features_view.py` is the exact code used to build the training rows.
- **Behaviour:** no sonar. Single-step moves; splits as `SPLIT L-2`; `SPLIT 1` as its deliberate death command.
  Guarded mode masks certain-death first steps.
- **Parity:** export matches sklearn to 1e-16. Closed-loop decisions match an offline recomputation 413/413.
- **Local results** (unswbc 1.1.0, 13 public maps × both sides), 51–53 overall:

  | Opponent | Result |
  |---|---|
  | fry-v14 | 22–4 |
  | serre-v01 | 13–13 |
  | sinbad-v07 | 13–13 |
  | gavroche-v32 | 3–23 |

  ouroboros-v10 scored 36–68 on the same fixtures.
- **Limits:** under-produces and misses Vibing++'s r320 conversion. Not an estimate of the real team's strength.
- **Use:** as a swarm-specialist benchmark opponent.
- **Evidence:** `experiment_data/team_recon_306_20260927_claude/REPORT.md` §5a.
- **Pure variant:** `ouroboros-m01p-vibing-mimic-pure` is the same model without the death mask. It produced
  identical results.
