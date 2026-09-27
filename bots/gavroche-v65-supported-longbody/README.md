# Gavroche V65 supported long-body guard

Parent: V60. Preserve V60's CPU guard and movement policy, then raise the
nearby-allied-head strike bonus from 0.5 to 0.75. This targets V60's weak
grad1 matchup while testing whether a modestly stronger local support signal
can improve combat without changing its search workload.

The bonus applies per visible allied head within torus radius 3, capped at two
heads. The sandbox screen missed the conservative max CPU gate; see below.


Result: the first two Big Empty CPU samples passed (p99 47.3–47.5M, max 62.3–64.4M), but Trauma side B reached 82.7M (p99 59.7M). The screen stopped at 3/4 samples; no native panel was run. See `experiment_data/gavroche-v65-sandbox-cpu_20260927090528000000`. No timeout was recorded in the three samples, but the conservative max <80M gate failed.
