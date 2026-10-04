# Himeji unit26 — own-game collection gap and analyst readings

4 October 2026, 06:22–06:40 UTC. Source receipt: `tools/himeji/unit26_audit/manifest.json`.
Main9bcc9c344 remains separate; own parent b775eebdc. No API calls, downloads, executor changes or main writes.

## Collection diagnosis

The sole collector is healthy, but it does not directly watch team7. `tools/hub/corpus.py:watch_list` unconditionally removes `cfg.team.id`, including an explicitly configured team. The hub snapshot caches recent battle listings in SQLite `series`; harvesting into `games` only follows accepted experiment requests. There is no general own-history-to-corpus bridge in this path. A current active-submission check is therefore not evidence of complete replay coverage.

Frozen corpus: 120,469 games at06:22:55Z, +478 since unit25 and **zero new own games**; 2,261 own games total, latest03:25:53Z. The database initially exposed1157 cached records at06:21:39Z, then1164 at06:32:23Z during the audit. The committed raw audit includes the later checkpoint, but **all counts below exclude cache observations after06:22:55Z**, avoiding comparison of newly played games with an older corpus. SQLite was opened immutable/read-only/query-only; WAL was excluded. Its `games` table still contains1280 rows, latest ingestion29September09:22:43Z. Submission14585 is active and14265 idle at06:32:23Z; missing replay identities are not inferred from that snapshot.

| Cache window / mode | Listed completed games with replay / series | Missing corpus index or payload / series | Recoverable from hub raw files |
|---|---:|---:|---:|
| 4Oct ranked |99 /20|**79 /16**|0|
| 4Oct unranked |4 /4|**4 /4**|0|
| After4Oct03:26 ranked |40 /8|40 /8|0|
| After4Oct03:26 unranked |3 /3|3 /3|0|
| Since2Oct04:31 ranked |830 /168|741 /152|0|
| Since2Oct04:31 unranked |1126 /155|963 /146|0|

These are deduplicated **cache-subset availability counts**, not a server census or performance estimate; there is no sampling CI for this deterministic comparison. A requested-time window is not replay-certified map era. Each sibling game contributes only its own listed status/hasReplay; the parent payload's winner, map and submission are never copied to siblings. There are zero conflicting mode/series assignments. API own submission IDs are missing for every selected row, so these are team7 counts, not verified14585 counts.

Concrete missing examples: ranked1020397–1020401 (team71 vs7, series d0619a10-3d9b-4024-8265-c35cf1d89644, requested06:12:29Z); unranked1019954 (team203 vs7, requested06:02:59Z). All were already listed completed/hasReplay before the freeze. Today's ranked missingness is35/50 against currently watched opponents versus44/49 against unwatched opponents; all4 unranked opponents are unwatched. Current membership is not historical polling opportunity, and these strata are not causal estimates, but they demonstrate a collection-selection problem beyond simple lack of games.

## Repair and acceptance

`prepare_own_collection_patch.py` produces `unit26_audit/corpus-own-team.patch` against main collector SHA2566bb33fd775768eafdaf38c287ce1853f45e8852d2e40acd5077502f3fec8c51c. It is **prepared, not deployed**. Opt-in `corpus.include_own_team=true` retains team7, even with no ladder entry. Refresh eligibility no longer requires reaching historical depth; stale own-team and top-team checks get priority. A fresh own-team check yields priority. Existing pass budget, refresh reserve, per-team limit, shared paced client and executor-yield checks are unchanged. Six pure selection checks and syntax validation pass; no network or daemon is started by the preparer.

Director/keeper integration request: review/apply this collector-only patch and enable the opt-in in the existing sole collector's collection configuration. Keep submission/executor settings unchanged. The patch supersedes the earlier undeployed refresh-only proposal. The known missing-ID manifest also needs bounded backfill through that same collector; a newest-page refresh alone does not repair historical gaps. Verify team7 in progress, successful own checks and actual arrivals for the cited IDs, then verify official replay winners, identities and map hashes before updating live references. Main-source ownership prevents Himeji deploying it in this unit; no permission rejection occurred.

H-H2 remains unresolved. The absence of recent unranked replays is demonstrably a coverage issue, not evidence of no recent unranked games, bot switching or concealment. After repair, compare matched map/hash, seat, opponent and time blocks with replay identity/behavior evidence. Freeze historical estimates as **conditional on the collected sample**; do not silently turn them into population rates. Missing matched live-us gaps remain NA.

## Readings and requests

1. **Rome4d69e3f06:** carthage05 runtime7df05a3f, LIVE_MAPS_M2 pool656–160–0/816 and gen1038–353–1/1392 are a completed local zero, not live performance. Four timed-out fixtures were rerun and resolved. Pool queen-decided losses19/160=11.9% [map-hash bootstrap95%3.3–25.5]; survival2/444 actual490 reaches (joint2/816). Distinguish denominators and local population from H20's frozen live sample. Correct Himeji's prior shorthand: **four** stale gen twins are actually present (192 games); Schooltime/Slithery twins are absent. Remaining1200 games861–338–1 are current or unflagged, not independently certified transfer. Two live variants remain outside the17-template pool. This is a source/report reading, not an independent rerun of2208 replays.
2. **Rome dose attribution:** plain carthage05 dose0 versus C+D+E1/E3 measures a combined package response. An E-specific curve needs fixed C+D with E0/1/3; otherwise label package effects. No extra panel requested. The current Kanazawa feature is directed-entry inclusive C(u→v), not the static per-cell feature in Rome's final paragraph. Direct coordination delivered to active Rome chat; no interruption or restart.
3. **Kanazawa57bfbb463:** accept the descriptive16/19 primary and12/19 consumed-holdout approximate alternatives. `q_forced.py` removes every dragon's tail at round snapshots and ignores same-round actions/growth. Own-tail entry can be fatal before the tail vacates; an alternate cell is not yet proven body-legal or safe. Thus H-KZ11 falsification/weight reduction should remain qualified pending exact TurnStart legality. Retain H-H6.5 and H-KZ12 alongside this disagreement. Pearl association17/19+18/19 is useful, but cannot establish the value of deliberately planting bait; stratify parent/mode/series, preserve future horizon/censoring, and avoid treating consumed94 as fresh confirmation.
4. **Naraa884062ea:** disagree with06:02 claim that a longer surviving enemy queen makes own culling rational through longest/total recycling. If terminal queens are3vs4, turning3 into0 still loses the queen comparison regardless of own longest/total. Culling could help only through subsequent changes (enemy queen death, elimination, future growth opportunities), which the reported aggregate cull rates do not establish. Command failure/wall labels do not by themselves prove deliberate sacrifice. Keep enemy-queen-state features, but do not use0.42/0.43 as demonstrations of that conditional policy without trajectories. Nara's open sign for H-SZ26 agrees with H25; H-H7 remains.4, no new arm needed.

## Reproduction and next action

From Himeji repo (raw index freeze remains local scratch; no raw replays committed):

```sh
python3 tools/himeji/own_collection_audit.py --hub /Users/alik/Documents/Projects/battlecode-hub --index /Users/alik/Documents/Codex/2026-10-01/p2-a-analyst-one-claude-opus/work/himeji-unit26/index.jsonl --corpus /Users/alik/Documents/Projects/UNSW-Battlecode-2026/public_replays/corpus --out /tmp/himeji-own-audit
python3 tools/himeji/summarize_own_collection.py --rows tools/himeji/unit26_audit/cached-own-games.jsonl --progress tools/himeji/unit26_audit/collection-progress.json --observed-before 2026-10-04T06:22:55 --out /tmp/himeji-coverage.json
python3 tools/himeji/prepare_own_collection_patch.py --repo /Users/alik/Documents/Projects/UNSW-Battlecode-2026 --out /tmp/himeji-repair
```

The first command is a new checkpoint query, not a promise of identical future counts. The second exactly reproduces frozen counts from committed derived rows. `coverage-at-freeze.json` is primary; `summary.json` and `watch-selection.json` deliberately retain the later06:32 checkpoint for provenance and must not be substituted. Next wake: integration receipt/collection proof first; otherwise independent H-H7 newborn-linked bed capture or peer exact-entry legality reading. Do not repeat unchanged audits. Own stores31games/62sides+1110 pending and historical754 remain untouched.

## RL translation

**Observation:** preserve collection route, mode, replay identity certainty, map hash and time in dataset metadata; never expose future-death or missingness outcomes as policy inputs. For queen decisions, observed enemy-queen state plus directed/body-conditioned geometry matters.
**Action:** escape, feeding and culling remain separate choices; this collection unit does not add a bot action or claim a learned policy.
**Value/reward:** use official queen→longest→total outcomes and explicit reach/censoring; a surviving longer enemy queen prevents fallback. Missing games have unknown rewards, not losses or zero value.
**Demonstration:** sparse opponent-discovered own replays cannot establish deployment prevalence or intent. Backfill and then validate behavior on independent series before treating culls or bait entries as demonstrations. H-H6/H-H7 retain their existing falsifiers, dose plans and sample-size requirements.
