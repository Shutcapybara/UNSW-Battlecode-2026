# monte_christo-x03-local-density

Parent: `monte_christo-v06-density`.

Parameters changed: `{'density_remote': 0, 'density_rays': 0}`. All other executable files are inherited unchanged, except x09 separates observation and age half-lives in `density.init()`.

Development: **8–16** against Sinbad v03, Tew v12 and Hunter v20 on four maps, both sides; v01 is 9–15 on the same fixtures. Direct v01: **5–3**. These are selection results, not an independent final test.

Configuration: `configs/monte_christo_messaging/screen.toml`. Exact run: `experiment_data/monte_christo-x03-local-density_20260925133924187150`. No caught policy errors or native timeouts in its 32-game audit; native runs do not establish judge-budget safety.

See the [messaging report](../../docs/monte_christo-messaging.md) for hypothesis, packet format, predictive errors, map/side regressions, later validation and deployment status.
