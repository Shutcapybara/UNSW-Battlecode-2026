# Qualifier and Grand Final campaign roadmap

Updated 6 October 2026. This is the strategy plan, not a result report. The user clarified the competitive objective: **finish in the top 10 among eligible teams in the GF qualifier on unseen maps, then win the Grand Final on unseen maps**. Ladder #1 is a proxy for team strength, not a separate finish-line.

## Current position

- Qualifier lock: 9 October, 4:30 pm Adelaide time. The active submission at lock is fixed for seeding.
- Submission **17791**, `bokuto-18-queenfeed`, is the sole active fallback as of the latest authenticated read on 6 October. Recheck before lock.
- No challenger is currently supported. Bokuto 63 failed the frozen independent confirmation gate; the action and sonar PPO arms showed no measured gain. Preserve those findings and do not repeat the same training/evaluation loop without a new hypothesis.
- Live leaderboard snapshot, 6 October 21:47 Adelaide: our team is rank 69 overall and 52nd among 171 eligible teams with a current ladder rank; 335 teams are marked eligible in the roster. The tenth currently ranked eligible team is at 2245 Elo, 420 above our 1825. A bounded sample covered 17 recent ranked series (85 game rows) from the ten highest-ranked eligible teams, but neither API metadata nor the 17 replay headers exposed submission IDs or bot labels. These are volatile ladder and opponent snapshots, not qualifier seeds, frozen controls, or predictions of best-of-seven results. Details and limits are in [baseline context](BASELINE_AND_EVENT_CONTEXT.md).
- Official format is confirmed: the Qualifier is best-of-7; every qualifier map is unseen; teams are seeded from ladder rating after autoscrims; the top 10 eligible teams from the Qualifier advance. The Grand Final is best-of-5 and its 10 finalists are seeded by ladder rating on 16 October. Thus ladder rank helps seed both stages, while qualifier bracket results determine advancement. See the [Qualifier page](https://game.battlecode.au/tournaments/qualifier), [competition terms](https://battlecode.au/terms), and [official map announcement](https://game.battlecode.au/updates).

## Campaign stages

1. **Protect the current event entry.** Keep the qualified fallback active. Before any change, require a fresh server read, a candidate that clears the prewritten strength and runtime gates, and a verified readback. If no challenger qualifies, use 17791 at lock.
2. **Build the eligible-field baseline.** Snapshot our current rating/seed, identify eligible submissions and likely opponents from current, source-attributed games, and record map mix, seat effects, sample counts and uncertainty. Ladder #1 is a useful strength and seeding signal, not a substitute for qualifier advancement or the Grand Final result. Treat old frontier tables and short rating windows as historical context, not current truth.
3. **Find a mechanism before choosing a tool.** Use replay and tournament diagnostics to rank failures by frequency and expected competitive impact: early queen losses, economy/production, map adaptation without atlas use, coordination/sonar, and late conversion. Turn each selected failure into one falsifiable hypothesis with a measurable behavior change.
4. **Run isolated candidate cycles.** Make one immutable snapshot per hypothesis. Check baseline parity where applicable, legality, protocol behavior, CPU/memory and artifact size. Screen against 18 plus a small set of strong, behaviorally distinct controls on both seats. Keep development and confirmation maps/fixtures separate.
5. **Confirm against the tournament objective.** For qualifier readiness, estimate performance against the eligible field on held-out maps and optimize both match-win odds and bracket advancement; after qualification, optimize and test for winning the Grand Final on another unseen-map set. Use preregistered, untouched map/opponent/seed sets, cluster by map (and report source-family sensitivity), and require zero unresolved faults. Track ladder rating as strength/seeding evidence, not as a substitute for either tournament result. Verify the exact uploaded artifact and active submission.
6. **Treat hybrid hierarchical RL as a post-Qualifier hypothesis.** Do not restart the same one-turn PPO actor: measured action/sonar versions showed no lift. If replay diagnosis supports it, test persistent worker options, phase-conditioned scoring, offline replay warm-start and online fine-tuning with deterministic C++ executors and safety overrides. The proposal is in [the hybrid architecture note](HYBRID_RL_ARCHITECTURE.md); it is not a measured improvement or submission change.

## Work queue

- **Now, before lock:** one final authenticated active-submission read; preserve 17791 unless a candidate clears every gate in time.
- **Next research block:** resolve exact opponent bot versions for the sampled eligible teams; then inspect those replays and our losses for repeatable failure mechanisms. Current roster/rating and match samples are recorded, but exact opponent versions, qualifier seeding and the bracket are not yet available.
- **First candidate cycle:** choose the highest-value falsifiable mechanism, write its expected signature and gate before coding, and make a small isolated snapshot. Do not start with an architecture rewrite or a broad reward sweep.

For each new cycle, add one row to the root handoff's current task board and a dated entry to [the experiment log](EXPERIMENT_LOG.md). Record hypotheses as proposed until measurements exist; log rejected candidates and why they failed.
