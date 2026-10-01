# tools/maelle — SF-1 state-and-features lane (Maelle lineage)

Python: the repo venv (`.venv/bin/python`, unswbc 1.2.2, pandas, scipy, sklearn, torch). Outputs under
`build/maelle/` (never committed); summaries under `game_stats/runs/maelle/`.

| Tool | What |
|---|---|
| `lane.py` | panels, CPU probe and the D-032 gate; an *arm* = bot dir + `MAELLE_PARAMS` overrides |
| `tune.py` | `scan`: paired grid over one weight + quadratic surface + bootstrap interval of its optimum; `spsa`: joint re-tune |
| `fit.py` | `corpus-extract` + `clogit`: top-30 sides' target choices, conditional logit, implied bot weights; `selfplay`: outcome regressions on the bot's own dumps |
| `dump.py` | reader for `MAELLE_DUMP` decision dumps (`stats`) |

Typical loop for one feature (weights are runtime-overridable, so the scan needs no rebuilds):

```sh
PY=.venv/bin/python
# parent: all weights 0, both panels, seeds 1-3, with the decision dump (training data)
$PY tools/maelle/lane.py run maelle-02-features --panel both --seeds 1,2,3 --dump --extract
# prior
$PY tools/maelle/fit.py corpus-extract --jobs 4 && $PY tools/maelle/fit.py clogit --features food,ally,enemy
$PY tools/maelle/fit.py selfplay --dumps build/maelle/dumps/maelle-02-features/pool
# fit: paired scan on pool seed 1 (value 0 = the parent arm)
$PY tools/maelle/tune.py scan --bot maelle-03-foodfree --var wt_food_free --values=-0.5,0.75,1.5 \
    --parent maelle-02-features --panel pool --seeds 1
# gate: the version dir with the fitted weight compiled in, no overrides
$PY tools/maelle/lane.py run maelle-03-foodfree --panel both --seeds 1,2,3 --extract
$PY tools/maelle/lane.py score maelle-03-foodfree --parent maelle-02-features --seeds 1,2,3 \
    --json game_stats/runs/maelle/maelle-03-foodfree.json
# CPU (sandbox judge pricing; dense fixtures, both seats)
tools/maelle/cpu_probe.sh bots/maelle-03-foodfree foodfree
```

The scan's objective J (per side-game) is econ + 0.5·mean(units@100, length@100) − 0.08·ally head-on deaths/1k,
so a fit cannot buy economy with churn (L29); acceptance is always the D-032 gate, never J.
