# Gavroche V43 late CPU budget

Parent: V36. This version disables triple candidates from round 150. From round
380, it also caps target search at 32 nodes and long-body safety floods at 24
cells, regardless of live-unit count.

Four sandbox games against V31 completed 2–2 without faults. All p99 samples
passed 60M: 46.4–46.6M on Big Empty and 53.9–59.1M on Trauma. Three of four
maxima passed 80M; the remaining Trauma peak was 83.4M at round 245, before the
target and flood caps engaged. See
`experiment_data/gavroche-v43-sandbox-cpu_20260927200000000000`.
