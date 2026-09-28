# monte_christo-x04-channel-only

Parent: `monte_christo-v06-density`.

Parameters changed: `{'density_policy': 0}`. All other executable files are inherited unchanged. This computes and sends density reports without using them to score movement, isolating changes to the legacy report schedule.

Development: **12–12** against Sinbad v03, Tew v12 and Hunter v20 on four maps, both sides; v01 is 9–15 on the same fixtures. Direct v01: **4–4**. These are selection results, not an independent final test.

Configuration: `configs/monte_christo_messaging/screen.toml`. Exact run: `experiment_data/monte_christo-x04-channel-only_20260925134129597279`. No caught policy errors or native timeouts in its 32-game audit; native runs do not establish judge-budget safety.

Broader development: **45–15** against six external references, matching v01's
45–15, with seven paired gains and seven losses. Direct parent: **4–6**.
Hunter improved from 8–2 to 10–0; Sinbad regressed from 6–4 to 4–6.
Exact run: `experiment_data/monte_christo-x04-channel-only_20260925141424445042`,
configuration `configs/monte_christo_messaging/validation.toml`. All 70 games
audited without caught policy errors or native timeouts.

The x10 silent-slot control has identical movement/split streams for both teams
in all 32 initial screen fixtures. Density payloads themselves did not cause
those outcome changes; withholding legacy traffic did. Judge cost evidence and
final selection are recorded in the report below.

Judge cost probe: Hunter v20, Stronghold A, 15,428 metered turns, no timeouts or
caught errors, maximum 58.373M points and 22,020,096 bytes. Compared with x10's
identical movement/split trajectory, this unused density pipeline adds 0.900M
points per turn on average (3.25% of x10's mean). This includes state handling
and receiving/parsing as well as sending. Run:
`experiment_data/monte_christo-x04-channel-only_20260925144701764829`;
configuration `configs/monte_christo_messaging/cost-probe.toml`.

See the messaging report (`../../docs/monte_christo-messaging.md`) for hypothesis, packet format, predictive errors, map/side regressions, later validation and deployment status.
