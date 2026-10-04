# Himeji unit 10 — live-data ownership resumed, fresh top-team endgames

4 October 2026 Adelaide / 3 October UTC. User resumed Himeji, assigned live-database connectivity, game collection,
top-team anatomy and investigation of possible concealed active-bot switching. The30-minute heartbeat is ACTIVE
with the new scope; the old Antioch-only collection restriction is superseded for this lane. No bot experiments,
uploads or activations. The existing shared collector remains the only downloader.

## First finding: queen preservation is now widespread in the sampled top cohort

A fresh FRAME_VERSION7 store decoded119 recent games without errors (238sides). All238 side outcomes agree
with the official corpus winner. An independent replay-header audit verifies119 hashes/results; all72 round-limit
winners obey queen→longest→total, with0 violations. The sample spans17 API map names /18 decoder labels
(Prisoners Dilemma10 is separate), starts03:43:50–22:16:32UTC on3October, and contains123current-top10 sides.

| Population in decoded sample | RL sides / series | Queen alive at RL end | Whole-series95% interval | Sole surviving queen wins | Losses with final total lead / all RL losses | Losses given final total lead |
|---|---:|---:|---|---:|---:|---:|
| Current top10, ranked | 53 /27 | 25/53 =47.2% | [32.3%,63.1%] | 19/19 | 3/11 | 3/35 |
| Current top10, unranked | 21 /5 | 9/21 =42.9% | [33.3%,57.2%] | 3/3 | 3/7 | 3/12 |

These are **terminal round-limit** measures, not r490 checkpoints or carried early-ended states. Bootstrap:
1,000whole-series resamples, seed104, both observed top-team sides retained when applicable. Uncertainty describes
the selected decoded coverage sample; it does not repair missing games or identify a population trend. Ranked and
unranked have different opponents/maps and must not be compared as a mode effect.

Ranked surviving queen lengths include Vibing++37/3/123/25 (4of7RL), SSS73/35 (2of3),
team82 lengths51/32/37/19/16 (5of7), and WeHaveQuizzes60 (1of5). This overturns any working assumption that
current top teams almost always reach the end with dead queens. It is **not** a controlled change from the older
0.7% estimate: cohort, map pool, time and selection all changed. Preservation/growth is observed; intentional
feeding, mobility and the exact mechanism still require event-level anatomy. Next priority is trace the long-queen
examples' split retention, food source and movement, with within-map comparison against dead-queen games.

At r50 on Around UNSW, seven sampled ranked top-team sides range57–110bed pearls,34–70births and64–106total
length. The110-bed-pearl/70-birth side (952, game991820) still loses at the round limit. These are individual
observations, not targets or evidence that more births cause losses. Per-team/map/mode rows are exported.

## Collection and database handoff

The live SQLite connection succeeds in read-only mode. The hub has1,280 own-game records; the public corpus is
separate and much larger. At reorientation the daemon PID35400 ran from app snapshot0298966ec with executor
in shadow. It downloaded40replays/pass with0errors in inspected passes; no competing client was started and no
credential was displayed/copied. Live ladder snapshot221421Z and database ladder agree. Later logs reached
114,008indexed games at22:28:49UTC; collection remains continuous. No collector/deployment settings changed.

Analysis freeze22:23:21.896645UTC:113,915unique corpus games, index SHA256
`039af5161d7e50db94a995ef6a7971940da185214f9d1911eeb08109a32b5d61`, latest start22:18:35.647Z.
Ladder `20261003T221421Z.json`, top10 IDs306/91/264/213/952/842/552/87/82/566.
Eight of those ten had last direct collector checks more than24hours old at freeze. Indirect opponent collection
still supplied some newer games. The queue is advancing:566 was directly refreshed at22:23:50; do not mistake
collection lag for a team going inactive. Next wake must verify remaining stale top-team checks and new-game yield.

The old shared S-1 metadata was last updated1October15:43UTC. Preserve it and all frozen benchmarks.
The fresh **versioned Himeji store**, readable by other local analysts, is:
`/Users/alik/Documents/Codex/2026-10-01/p2-a-analyst-one-claude-opus/work/himeji-live-store/`.
It has an exclusive writer lock, pinned decoder-source hashes, atomic metadata replacement, committed-part markers
and incremental game IDs. Metadata113,915games; decoded119of150eligible recent current-top10/us games in this
freeze. Selection balances team/map/mode, newest first, from2October22:00UTC. Thus31queued games remain;
new snapshots may expand the queue. The180-second budget drained in185seconds with two workers. No worker remains.
No shared norms or old store were rewritten. S-1's existing tables omit explicit queen checkpoint columns; the
separate official terminal-header artifact supplies this unit's endgame rows, and r490 remains pending.

The map pool is17API names again; historical ten-map filters would drop Around UNSW, Australia, Islands, Maze,
Stripes, Tower Defense and weakhold. New map/rules diagnostics must retain these strata. Era is the accepted
post123 boundary1October06:00Z; current72RLheaders support the queen ordering, but no fresh sprint-price audit
was run. PD10 remains separately labelled; no geometry alias is asserted.

## Spoofing/switching: current evidence is insufficient

The24-hour collection window ending22:23:21UTC contains155current-top10 side-games. **All155have missing
submission IDs and blank replay bot names.** Known code/bot identity therefore cannot be recovered from these fields.
There are0shared ranked/unranked strata under exact `(map_hash,seat,opponent,UTC day)` matching for every current
top team. Missing comparisons stay missing; no synthetic decoy classification is filled in.

| Team | Ranked wins/games (series) | Unranked wins/games (series) |
|---|---:|---:|
| 306 Vibing++ | 12/13 (4) | 0/0 |
| 91 SSS | 7/7 (2) | 3/4 (1) |
| 264 forgot to mention | 7/10 (4) | 16/20 (3) |
| 213 Sponge(Albert and Bob) | 18/23 (7) | 2/3 (2) |
| 952 Cache me outside | 7/14 (4) | 0/0 |
| 842 horse | 1/1 (1) | 11/15 (1) |
| 552 fandagong | 11/12 (3) | 0/0 |
| 87 WeHaveQuizzes | 10/11 (3) | 0/0 |
| 82 free trip to sydney pls | 9/11 (3) | 1/6 (3) |
| 566 tungtung67 | 3/5 (1) | 0/0 |

The largest visible mode difference (82) is a screening lead only: sixseries, different matchups, no identity
labels. Vibing++has no collected unranked sample here; this cannot establish either continuous deployment or
concealment. Also, ranked starts now occur outside the old even-hour autoscrim heuristic; use observed ranked
status and series times, not that legacy window as an active-bot label. Our own fresh corpus coverage is just two
unranked losses in one series,0ranked; database/corpus incompleteness is not proof no other games occurred.

**H-H2 (proposed ledger row; weight unassigned):** some teams alternate reproducible behavioral regimes around
ranked series. Mechanism to measure: opening action pattern plus splitting/sprint/queen-growth policy changes
repeat near ranked activity, then revert. A normal rollout should produce a persistent change instead. Falsify a
large switching claim if a held-out later window lacks recurrent switches, matched effects disappear, or the
95%upper bound excludes a prespecified30pp performance difference. Do not equate behavioral switching with intent
to deceive; that stronger claim needs identifiable switching/other corroboration and alternative explanations.

Suggested minimum:40independent matched series per proposed regime, one preregistered comparable fixture per
series, across at least two separate time windows. This is approximately the independent sample needed to detect
80%vs50% binary win rates at two-sided5%alpha/80%power (~39per group); clustering, selection and behavioral
multiple testing may require more. Estimate dependence before extending to all games. Suitable analysts: Himeji
collection/timing and Nara behavior; Antioch independent queen/action check. Testers should not spend live games
until observation coverage justifies a specific discriminating matchup. No battle requests issued here.

## Communication lane and readings

`tools/himeji/COMMUNICATION.md` establishes addressed board IDs, evidence pointers, reply tracking and routing.
Antioch/Nara are available by remote branch/status but have no visible direct chat in the current inventory.
Do not invent delivery. Direct analyst messages can supplement the board when an existing chat is identified;
no extra task, external message, or peer restart was created. Rome's existing chat “Run P2-T hypothesis tests”
is active, resuming L10; its pending full official score is not a new result. Prior partial old-decoder win+0.83pp
cannot be read as an accepted full gate. D-042's adopted Himeji win-led adaptation rule is acknowledged;
non-adaptation gates and the open units-guard question remain distinct.

## Reproduction and next cycle

Queries committed under `tools/himeji/`: `resume_store.py`, `snapshot_analysis.py`, `summarize_store.py`,
`recent_endgames.py`, `summarize_endgames.py`. Compact artifacts are in `tools/himeji/unit10_audit/`;
raw snapshot/index and parquet stay uncommitted. Main-source hashes are frozen in`decoder-source.json`.
Use main's analysis Python; no environment changes or simulator calls. Each script's `--help` gives arguments.
The store builder reads a frozen `index.jsonl`, `ladder.json`, and `manifest.json` snapshot and checkpoints by game.

Source cursors: main0298966ec, Antioch2c7113f66, Carthage5b69fa9d0, Kyoto fccea71c0,
Nara21a182700, Romead611b51c plus current resumed chat. Board read through directorD-042 and peer wrap-ups;
Himeji postsH10-01..06. Automatic approval review rejected a main fast-forward; Himeji remains on its separate
branch and reads current main dependencies without importing unrelated commits. This did not block collection,
analysis, communication setup or scheduling.

Next bounded unit: verify top-team refresh catch-up; freeze new data and finish/extend the31-game queue; analyze
long-queen food/split/movement traces and matched weak/strong regimes. Refresh per-map field references only when
coverage and time stability support them. Current anchors are provisional; no new field percentile or matched
live-us gap is claimed. Read new Rome results when published. The heartbeat will resume active work rather than
overlap a worker, and stay quiet on unchanged state.
