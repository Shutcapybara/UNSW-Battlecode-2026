# Decisions and promotion rulings

Updated 6 October 2026. Detailed evidence and reproduction paths are in [the experiment log](EXPERIMENT_LOG.md).

- The campaign target is **finish top 10 among eligible teams in the GF qualifier on unseen maps, then win the Grand Final on unseen maps**. Ladder #1 is a strength/seeding proxy, not a separate finish-line. Official format: qualifier best-of-7, seeded by ladder after autoscrims; top 10 eligible teams advance. Grand Final best-of-5, seeded by ladder rating on 16 Oct. Sources: [Qualifier](https://game.battlecode.au/tournaments/qualifier), [terms](https://battlecode.au/terms), [map announcement](https://game.battlecode.au/updates).
- Keep `bokuto-18-queenfeed` as the supported qualifier fallback. Submission **17791** was activated after the frozen candidate gate failed and authenticated readback confirmed it as the sole active submission. Recheck before the 9 October 4:30 pm Adelaide lock.
- Do not promote `bokuto-63-resource-crowding`: 86–88 against 18, no replay faults, but its direct advantage was +0.00575 with a 90% map-cluster interval of [−0.05172, +0.06322]. The prewritten lower-bound gate failed.
- Do not promote action-only, sonar-only, combined PPO, or optional-packet suppression. The staged policies tied the incumbent on the four-map development screen; suppression later lost 83–91 in confirmation. See the experiment log for each protocol, split, and artifact.
- Preserve the frozen statistical rule: require a positive confirmation estimate, a 90% map-cluster lower bound above zero, and zero unresolved judge faults. For a campaign aimed at #1, also test against strong current opponents; beating the fallback alone is insufficient evidence of field leadership.
- Keep measured snapshots immutable. A new behavior belongs in a new versioned bot directory, and its claim remains provisional until the appropriate untouched confirmation and artifact checks pass.
