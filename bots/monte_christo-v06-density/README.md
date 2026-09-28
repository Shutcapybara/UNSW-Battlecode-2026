# Monte Christo v06: shared density

Parent: `monte_christo-v01-core` (Bahamut pipeline, Sinbad v03 components).
Hypothesis: smoothed, spatially located ally/enemy reports improve allocation.

Unique visible dragon counts and toroidal position use a four-round EWMA.
Type-6 packets carry the source ID, position, counts and original time. Latest
reports are deduplicated by source, expire after 16 rounds, and feed a bounded
32-source spatial estimator. Two rotating rays are reserved for density; idle
rays are filled and one ray may relay an original report on odd rounds.
Forager targets are discounted by allied crowding and enemy density. Immediate
collision handling and the inherited tactical/production framework remain.

Development: 12–12 against Sinbad v03, Tew v12 and Hunter v20 on Arena,
Default Small, Devil and Colosseum, both sides. Parent v01 is 9–15 on identical
fixtures. Direct parent matches: 5–3.

The broader five-map development cohort regressed to 39–21 against six external
references, versus v01's 45–15, with 1–9 against v01 directly. There were nine
paired gains and 15 losses. This unconditional density policy remains an
experimental component, not the stable recommendation. Exact broader run:
`experiment_data/monte_christo-v06-density_20260925140237417189/`, using
`configs/monte_christo_messaging/validation.toml`.

Judge: four games against Hunter v20 on Arena/Stronghold, both sides;
26,006 metered turns, zero timeouts/errors, max 89.92M points, max memory 22.02 MB.

Exact runs: `experiment_data/monte_christo-v06-density_20260925132840215994/`
(native), `experiment_data/monte_christo-v06-density_20260925133156544079/`
(judge). Configuration: `configs/monte_christo_messaging/screen.toml` and
`sandbox.toml`. Parameters live in `params.py`.

See the full messaging report (`../../docs/monte_christo-messaging.md`) for packet
layout, prediction checks, source-matched results, regressions and limitations.
Checksums reject unrelated packets; they are not adversarial authentication.
