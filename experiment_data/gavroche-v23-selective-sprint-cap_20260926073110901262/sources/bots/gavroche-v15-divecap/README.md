# Gavroche v15: dive cap

Parent: Gavroche v13, the paced tail-rescue line. The only behavior change is
reducing the value of an unpaired portal from 7 to 3, following Sinbad v07's
measured dive-cap change. The aim is to keep portal exploration while reducing
fatal dives and friendly head-on collisions.

The supplied replay set contains four 11-map series: Team A won 6/11 and 4/11
games for bot ID 6813, and 7/11 and 2/11 for bot ID 6883. That opponent split
argues for a broad evaluation rather than tuning to just one winning opponent.
Big Empty, Prisoner's Dilemma, and Trophy recur as loss maps in those series;
other maps swing by opponent.

## Cross-family comparison

Native, both sides, 13 maps, 182 games, no runner or runtime errors:
100–82 overall (54.9%). It scored 78–52 (60.0%) across five selected model-family references: Sinbad
v07 12–14, x06 tf-05 19–7, reconstructed x06 grad1 16–10, x04 support
15–11, and Monte Christo x12 16–10. Against the
Gavroche v13 baseline it split the series 13–13. This remains a useful low-gradient
alternative: it did better than v16 and v17 against tf-05, while losing ground
against v13 and the reconstructed grad1 reference.

Full report: `experiment_data/gavroche-v15-divecap_20260926050810205628/summary.md`.
