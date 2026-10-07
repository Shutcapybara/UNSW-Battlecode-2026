# Finals campaign: working memory

Updated: 7 October 2026, Australia/Adelaide. Read this short handoff first when resuming. Keep it current; see [`docs/finals-campaign/`](docs/finals-campaign/README.md) for the plan and detailed evidence.

## Objective

The objective is **finish top 10 among eligible teams in the GF qualifier on unseen maps, then win the Grand Final on unseen maps**. Ladder rank is a proxy for strength and seeding, not a separate finish-line. See the [roadmap](docs/finals-campaign/ROADMAP.md).

## Live checkpoint

- **Qualifier lock:** 9 October, 4:30 pm Adelaide. The active submission at lock is fixed for seeding.
- **Active submission:** 17791, `LV-bokuto-18-queenfeed-ba537e4e-ai`, sole active in the latest authenticated read on 6 October at 21:23 Adelaide; server source hash `fa16c1050cad8f74058f2023b15dbea64eb0ec08b9f2aef3ff19aaf45ede677b`.
- **Best supported fallback:** immutable local `bots/bokuto-18-queenfeed`, atlas disabled. Re-read active state before the qualifier lock.
- **No qualified replacement:** candidate 63 finished 86–88 vs 18, with zero replay faults, but its +0.00575 advantage had a 90% map-cluster interval [−0.05172, +0.06322]. It failed the frozen gate. Do not promote it.
- **PPO status:** the terminal-only joint pilot showed no monitor gain. The shared action/sonar trainer now uses bounded Heartbreaker potential-difference shaping (gamma 0.997, alpha 0.2); formula tests and a full-game collection smoke pass with zero overrides/faults. This verifies plumbing only; no shaped PPO run or strength gain is measured. Build binaries/data are absent in this checkout; rebuild and recollect, then start a fresh output directory because the reward objective changed. See the [experiment log](docs/finals-campaign/EXPERIMENT_LOG.md), [policy design](docs/finals-campaign/POLICY_LEARNING.md), and runnable command in [`tools/finals/README.md`](tools/finals/README.md).

## Active task board

| Priority | Task | State | Next evidence |
|---|---|---|---|
| Q1 | Protect event entry | 17791 active | Fresh API read before 9 Oct 4:30 pm Adelaide lock |
| C1 | Verify tournament contract | DONE: OFFICIAL RULES CHECKED | Qualifier is best-of-7 on unseen maps; seeds use ladder rating; top 10 eligible teams advance. GF is best-of-5 and seeded by ladder rating |
| C2 | Establish qualifier field baseline | In progress: ladder snapshot + 17-series sample | Resolve current bot versions for sampled top eligible teams; update when qualifier seeding/bracket is published |
| C3 | Shaped joint spatial policy | Shared encoder + conditional action/sonar heads + bounded potential differences implemented; reward math and full-game collection smoke verified, no shaped PPO strength evidence yet | Rebuild binaries/data if absent; run the fresh shaped trainer with `--until-stopped`; inspect terminal outcomes, shaped return, per-head choice rates and periodic fixed-monitor paired score |

Do not change the qualifier artifact without a fresh read, a candidate clearing the evidence/runtime gates, and a verified readback. Continue research toward the campaign target; the detailed cycle is in the [roadmap](docs/finals-campaign/ROADMAP.md).

## Working rules

Keep measured results separate from proposed work. Freeze bot snapshots; make behavior changes in new versioned directories. Separate development fixtures from untouched confirmation, cluster scores by map, and preserve zero-fault/runtime checks. Keep large artifacts under `build/` or `/tmp`, avoid paid compute unless newly authorized, and preserve unrelated user changes. The root task board stays concise; the [experiment log](docs/finals-campaign/EXPERIMENT_LOG.md) holds detailed protocols and results.
