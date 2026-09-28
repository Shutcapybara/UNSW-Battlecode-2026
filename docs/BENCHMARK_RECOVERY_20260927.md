# Benchmark recovery — 27 September 2026

Recovered the deleted benchmark runner, adaptive scheduler, ratings pipeline,
weight handling, analysis scripts, tests and 73-bot configuration. Restored Python
sources with surviving caches were checked against their compiled code, rather
than approximated from memory. All 19 benchmark tests and 3 similarity tests passed.

The contribution ledger contained 93,545 games at recovery. The latest
campaign's frozen initial ledger supplied 10,581
missing game IDs, bringing the union to 104,126. Earlier ledger
snapshots and every surviving benchmark SQLite journal were also checked. There
were no conflicting records. Recovered rows were republished to their original
per-run Parquets, so future central-ledger rebuilds retain them.

The existing campaign, `benchmark_20260927092112147957`, was resumed with its
73 frozen bots, 33 weighted maps, historical rating context and four runtime
holds unchanged. Both workers were cleanly restarted to reopen their log and
lock files. No bots or unrelated working files were reset, and no Git commit
was made.

Recovery audit and restored-file hashes:
`experiment_data/battlecode-recovery-20260927T135514Z/`.

A recovery archive outside the repository is available at:
`/private/tmp/battlecode-recovery-20260927T135514Z/restored-code-and-ledger.tar.gz`.
It contains restored code/config/tests, contribution Parquets, source identities,
the rebuilt central ledger and campaign identity metadata. The same directory
also retains the pre-recovery ledger/cache copies and a SQLite backup.

The restored source files remain uncommitted. The external archive provides a
second copy in case another repository cleanup removes untracked files.

Post-recovery verification: the collector completed 13 new games, and the ratings
worker published successfully at 2026-09-27 14:00:34 UTC using the rebuilt ledger.
