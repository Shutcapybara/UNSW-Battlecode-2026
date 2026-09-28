# jet-v03-newton-richladder — Jet income-density dispatcher on host newton-x10-candidate

Built with tools/jet/make_dispatch.py from the frozen campaign copy of newton-x10-candidate
(experiment_data/benchmark_20260928064036195154/sources/bots). Host files verbatim in host/
(including its own override.py); ladder/ = jet-v02's ladder (ouroboros-v13 + certain-death-only vetoes).
Rule: ladder iff W*H <= 400 and the first view shows >= 20 fertile tiles, >= 8 empty, >= 75% of the
empty ones respawning within 20 rounds; on the 33-map suite only arena fires, where play is
identical to jet-v02 (arena vs 24 references: 41/48). Elsewhere identical to the host
(parity: Colosseum and default_small fixtures vs serre-v01 matched outcome and rounds).
Evidence: experiment_data/cohort_research_20260927T011500Z_jet/cycle_18_campaign_evidence_host_transfer.
