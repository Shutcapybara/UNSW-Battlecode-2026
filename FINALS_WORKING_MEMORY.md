# Finals campaign: working memory

Updated: 8 October 2026, Australia/Adelaide. Read this short handoff first when resuming. Keep it current; see [`docs/finals-campaign/`](docs/finals-campaign/README.md) for the plan and detailed evidence.

## Objective

The objective is **finish top 10 among eligible teams in the GF qualifier on unseen maps, then win the Grand Final on unseen maps**. Ladder rank is a proxy for strength and seeding, not a separate finish-line. See the [roadmap](docs/finals-campaign/ROADMAP.md).

## Current user-authorized iteration goal

**Latest user request:** submit Kuroo07 and keep it active. Completed:20627/v112 compiled and API-verified sole active; user-requested deployment, not strength promotion.

**Previous server retest:** leave Kuroo02 active and retest it against ComTamSuonNuong (team193) on every map lost in match1427506. Activated 20472/v111 and queued 14 unranked games, IDs1431103–1431116, series `086328b2-45f1-4238-818f-1de0c4240aa9`; retest completed2–12 (Australia/Maze wins), zero own runtime faults. Kuroo02 was active for that retest. Latest steering: diagnose1431111 round439 queen split and nearby large-snake feeding; Kuroo03 expanded test requested:88 native games across22 maps vs02 finished31–57, zero replay faults; rejected for strength;02 remained active at that stage. Native screen4–4 (3–1 vs02,1–3 vs12); server retest complete2–12, no sandbox runtime check. Akaashi12 remains unpromoted because it did not clear the existing strength/runtime gate. Its focused screens total496 games; it lost35–37 against original01–06 and its targeted weak-map follow-up lost16–24. Prior authorization: continue until the user clears the goal: after each Heartbreaker series, inspect
all losses using total/queen/longest length curves and linked death/split events;
fix the biggest evidenced weaknesses with general rules in fresh snapshots,
then upload/activate and queue the remaining loss maps again. User explicitly
authorizes this ongoing server loop. Do not equate deployment with statistically
confirmed promotion. Campaign: `docs/finals-campaign/HEARTBREAKER_ITERATION.md`.

Latest authorized follow-up: isolate the fixes from02. Local04 (visible obstruction donor election) and05 (late free queen escape beam) built/tested on22 maps,44 games each, seed81034/both seats:04=22–22 with no observable gameplay difference;05=21–23, free overrides on Stronghold/Islands only. Regressions and88 replay audits pass.05 sandbox Slithery pair1–1, zero faults, peak11.1M points. Neither promoted. Artifacts `build/finals/20261008-kuroo04-05-isolated/`. No upload/activation.

User-authorized distress work completed locally:06 raw23–21/44, but three pre400 invalid deaths and no feed; unpromoted. Fresh07 fixes diagonal visible-queen rejection. Final07 panel22–22/44 across22 maps, zero replay faults; Stronghold r422 request to donor5 feeds49 cells, queen eats16 donor pearls and finishes87 vs mirrored02 queen6 (first state divergence423). Protocol/donor/expiry/visibility regressions pass.07 Stronghold sandbox pair1–1, zero faults, peak10.34M;06 Slithery pair recovered/completed1–1, zero candidate faults. Subsequent user-requested upload/activation completed:20627/v112 API-verified sole active. Artifacts `build/finals/20261008-kuroo07-screen/`, `20261008-kuroo07-runtime/`; full evidence in docs/kuroo-family.md.

## Live checkpoint

- **Qualifier lock:** 9 October, 4:30 pm Adelaide. The active submission at lock is fixed for seeding.
- **Active submission:**20627(v112), `LV-kuroo-07-distress-visibility-25dd4d8a-ai`, compiled and verified sole active on8 October at explicit user request. Server sourceHash `7e9f3afe2cad37d6d3b2076cc33d5dc6d8be2f5c727c8bdb0e4938bab635d07d`. Measured22–22; deployment is not strength promotion. Previous20472/Kuroo02 inactive; supported fallback17791.
- **Best supported fallback:** immutable local `bots/bokuto-18-queenfeed`, atlas disabled. Re-read active state before the qualifier lock.
- **No qualified replacement:** candidate 63 finished 86–88 vs 18, with zero replay faults, but its +0.00575 advantage had a 90% map-cluster interval [−0.05172, +0.06322]. It failed the frozen gate. Do not promote it.
- **PPO status:** the terminal-only joint pilot showed no monitor gain. The shared action/sonar trainer now uses bounded Heartbreaker potential-difference shaping (gamma 0.997, alpha 0.2); formula tests and a full-game collection smoke pass with zero overrides/faults. This verifies plumbing only; no shaped PPO run or strength gain is measured. Build binaries/data are absent in this checkout; rebuild and recollect, then start a fresh output directory because the reward objective changed. See the [experiment log](docs/finals-campaign/EXPERIMENT_LOG.md), [policy design](docs/finals-campaign/POLICY_LEARNING.md), and runnable command in [`tools/finals/README.md`](tools/finals/README.md).

## Active task board

| Priority | Task | State | Next evidence |
|---|---|---|---|
| Q1 | Protect event entry | 20627/Kuroo07 active at user request;17791 supported fallback | 14 outcomes collected/reviewed2–12; re-read active state before 9 Oct 4:30 pm Adelaide lock; testing is not strength promotion |
| C1 | Verify tournament contract | DONE: OFFICIAL RULES CHECKED | Qualifier is best-of-7 on unseen maps; seeds use ladder rating; top 10 eligible teams advance. GF is best-of-5 and seeded by ladder rating |
| C2 | Establish qualifier field baseline | In progress: ladder snapshot + 17-series sample | Resolve current bot versions for sampled top eligible teams; update when qualifier seeding/bracket is published |
| C3 | Shaped joint spatial policy | Training completed through update 1330 in `build/finals/spatial-joint-shaped-infinite-fixed/`; implementation tests pass, but the fixed monitor is strongly negative: 401–0–1,727 over 2,128 games (18.8% vs cached baseline 50%); no promotion or standalone export | Treat the checkpoint as rejected for strength; diagnose policy collapse/export path before any new training, then rerun a fresh held-out comparison only if the monitor recovers |
| C4 | Akaashi queen safety family | `akaashi-01-queen-escape` fixes Trophy 1404793 round-66 trap in oracle-verified branch; synthetic regression passes; small native screen 4–2 vs 18, no promotion | Broader paired development and frozen confirmation; see `docs/akaashi-family.md` |
| C5 | Akaashi visible queen strikes | `akaashi-02-queen-strike` takes pearl-funded sprint kill in Trophy 1407768 at protocol r46; oracle branch confirms queen death, tests pass; Trophy screen 1–1 vs 01 and 1–1 vs 18 | Broader paired development and confirmation; 06 is deployed |
| C6 | Akaashi threatened queen splits | `akaashi-03-threatened-queen-split` turns north instead of splitting at Trophy 1407768 r109; queen survives and A wins in oracle-verified scripted branch; safe/cage split and threat-union regressions pass | Screen 2–2 vs 02; focused metered/replay audits zero faults; broader paired confirmation next; 06 is deployed |
| C7 | Current iteration/test finished | 06 active20296(v108). Heartbreaker1415322–1415326 complete1–4: Default won; four losses. All curves/death/split diagnostics collected; zero own runtime faults | Akaashi07 test is complete; new local escort candidate08 is documented at C9 |
| C8 | Centre control and expansion | Akaashi07 20333/v109 test complete **2–5**, zero TLE/invalid faults: won Devil/Trophy, lost Australia/Autarky/Maze/Prisoners Dilemma/Stripes. Curves and linked deaths/splits collected | No further server iteration started; local08 addresses the latest user replay observation. Results `build/finals/heartbreaker-iteration/akaashi07-series/review/` |
| C9 | Queen escort versus equal pursuer | Local Akaashi08 changes A21 from W to N at protocol r47; scripted engine branch trades A21/B10 at r48, queen survives. Original replay oracle exact. Seven regression suites pass | Counterfactual only (nonresponsive recorded opponent); no strength claim. Keep local; await user before upload/next test. See family notes |
| C10 | Akaashi 01–06 family round robin | 480 balanced native games across 16 maps; 02 leads 88–72, followed by 04 (86–74) and 03 (85–75); no runner errors | Development ranking only. 07/08 were added after this roster freeze and are not covered. Full protocol and per-map results in the experiment log and `build/finals/20261008-akaashi-round-robin-500cap/` |
| C11 | Composite Akaashi family incl. untested07/08 | Akaashi12 screen vs01–11: **71–61**, 7–5 vs02, 35–37 vs original01–06. Replay extraction: all V0 checks passed, no TLE/invalid-death events. Uploaded/compiled as 20432/v110 at user's request; incumbent 20333 restored and API-verified sole active. | Not a win against every snapshot: losses vs01/04/05/11, tie vs03. Weak-map follow-up16–24. No sandbox check, active promotion, or server match. Replay comparison and submission receipt in Akaashi docs/log and `build/finals/20261008-akaashi12-submit/`. |
| C12 | Kuroo soft capacity reserve | New family forks Akaashi02/12; match1427506 A405 wall death caused by hard final-slot reserve. Exact oracle54,133 turns/zero mismatches; Kuroo02 outputs SPLIT5. Synthetic + inherited queen fixtures pass | Expanded128-game parent panel:32–32 vs02,34–30 vs12; hierarchical90% intervals include50%, no decisive strength gain. Replay audit128/128, registered F1 checks1152/1152 pass. Death rate higher vs both parents. Kuroo02 remains experimental; see docs/kuroo-family.md. |
| C13 | Kuroo queen obstruction/feed | 1431111 A1 guard splits31→7 at r438; A573 body blocks long-queen route. Local03 regression suites pass, expanded88-game/22-map test31–57 vs02; zero replay faults. End-game queen survival15/88 vs24/88; rejected for strength | No upload/promotion. Diagnosis:66 vs56 queens die before290; paid queen segments154 vs22. Proposed: isolate verified local obstruction feed from global guard changes; artifacts build/finals/20261008-kuroo03-expanded/. See docs/kuroo-family.md |

| C14 | Isolated Kuroo fixes |04 local feed22–22/no observable effect;05 free escape21–23, longer queen on Stronghold but extra loss on Islands.88 replay audits zero faults;05 sandbox two games zero faults/peak11.1M | No upload/combination. Proposed targeted queen distress radio for original out-of-view donor; verify turn order and fresh-request election before testing |

| C15 | Targeted queen distress |07 implemented/tested:22–22 across22 maps, zero replay faults; one same-round native feed, Stronghold queen87 vs02 queen6. Focused sandbox zero faults/peak10.34M | 20627/v112 compiled and sole active at user request; not strength promotion. Independent seeds/opponents and better receipt routing remain proposed |


Do not change the qualifier artifact without a fresh read, a candidate clearing the evidence/runtime gates, and a verified readback. Continue research toward the campaign target; the detailed cycle is in the [roadmap](docs/finals-campaign/ROADMAP.md).

## Working rules

Keep measured results separate from proposed work. Freeze bot snapshots; make behavior changes in new versioned directories. Separate development fixtures from untouched confirmation, cluster scores by map, and preserve zero-fault/runtime checks. Keep large artifacts under `build/` or `/tmp`, avoid paid compute unless newly authorized, and preserve unrelated user changes. The root task board stays concise; the [experiment log](docs/finals-campaign/EXPERIMENT_LOG.md) holds detailed protocols and results.
