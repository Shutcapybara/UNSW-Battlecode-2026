# monte_christo-x09-fast-observe

Parent: `monte_christo-v06-density`.

Parameters changed: `{'density_half_life': 1.0, 'density_age_half_life': 12.0}`. All other executable files are inherited unchanged, except x09 separates observation and age half-lives in `density.init()`.

Development: **10–14** against Sinbad v03, Tew v12 and Hunter v20 on four maps, both sides; v01 is 9–15 on the same fixtures. Direct v01: **4–4**. These are selection results, not an independent final test.

Configuration: `configs/monte_christo_messaging/screen.toml`. Exact run: `experiment_data/monte_christo-x09-fast-observe_20260925135829830836`. No caught policy errors or native timeouts in its 32-game audit; native runs do not establish judge-budget safety.

See the messaging report (`../../docs/monte_christo-messaging.md`) for hypothesis, packet format, predictive errors, map/side regressions, later validation and deployment status.
