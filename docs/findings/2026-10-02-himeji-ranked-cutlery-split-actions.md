# Himeji unit 6 — ranked Cutlery split actions and fresh ladder

Published 2026-10-01 17:20 UTC. **Cutlery's ranked invalid-split deaths fell from 40/62 to 17/90 games;
the replay evidence does not identify deliberate culling.** All 64 invalid queen deaths across the audited
ranked/unranked populations followed split commands, with no time-limit flag. The latest ladder also changes five
top-ten members, so Cutlery is a historical queen-behaviour case, not a current top-ten strength reference.

## Ranked versus unranked, with actual checkpoints

This is the complete 172-game Cutlery subset of Nara's 1,054-side cause artifact, starting 11:50:20Z–16:10:14Z
on 1 Oct. All starts are after the established new-rule boundary. Freeze SHA and replay SHA list are in the manifest
and source rows. The 13:00 cutoff is inherited from the prior claim, not optimized here. We verified all replay hashes,
official outcomes, queen death rounds/causes and final-alive status directly against existing replay events/headers.

| Population | Games / series | Invalid queen deaths / games | Actual alive@490 / reached | End queen alive / RL games | Early-end positives mislabelled r490 |
|---|---:|---:|---:|---:|---:|
| Ranked, before 13:00 | 62 / 14 | 40/62 (64.5%) | 0/31 | 0/31 | 1 |
| Ranked, from 13:00 | 90 / 19 | 17/90 (18.9%) | 10/40 | 10/40 | 6 |
| Unranked, from 13:00 | 20 / 3 | 7/20 (35.0%) | 2/9 | 2/9 | 5 |

There are no unranked before-cutoff observations in this sample. Ranked queen survival improved descriptively,
but ranked overall wins were **43/62 before versus 32/90 after**. Opponents, maps and submissions are not held fixed;
neither the survival rise nor the win decline estimates a causal policy effect. Unit 5 used an earlier 146-game
artifact; its 9/31 ranked post-cutoff result is preserved, not silently overwritten by this larger sample.

Actual r490 means the replay contains a played round 490; the queen is present at that round's start if it dies
at round 490 or later, or survives to termination. No carried early-terminal state counts as reaching. RL here is
the official engine end reason, and end queen length is the official TeamStanding fourth integer. In this sample
the actual-r490 and RL-end survival counts coincide; they remain distinct definitions.

## What changed, and what remains unidentified

All **40 before + 17 ranked after + 7 unranked after = 64** invalid deaths occurred in the same round as a recorded
**split** action; none was tagged suicide or TLE. The replay schema names death reason 4 `noValidAction`, not
`deliberateCull`. This supports fewer fatal split attempts. Deliberate sacrifice remains possible, but requires
state/action evidence beyond that death label; invalid split sizing or another split-policy change is also possible.
Four inspected examples had no explanatory engine log. We do not infer the requested split size or intent.

For ranked games, the invalid-death incidence change is **−45.6 percentage points**, with a descriptive 95%
series-block bootstrap interval **[−62.6, −28.6]**. Resampling is within each time window, 2,000 draws, seed 6123,
keeping all games of a sampled series together. The 14 and 19 series do not cross the cutoff. Small-series and
temporal/composition uncertainty remain; this is not an intervention confidence interval.

| Ranked structural grouping | Before: invalid / all games | After: invalid / all games |
|---|---:|---:|
| Pocket (Autarky, PD, Slithery) | 19/19 | 11/28 |
| Other seven maps | 21/43 | 6/62 |

The non-pocket reduction is **−39.2pp [95% series-bootstrap −59.2, −20.2]**. It is not solely a changing pocket-map
share. Residual ranked invalid deaths are 11/17 pocket, versus the mixed 16/24; a structural pattern is present,
but a state-keyed intentional cull is not proven. These broad groups are descriptive hazard groupings, not a learned
structural router. Full per-map counts are in `summary.json`.

Nara's mixed Trauma 11/13 positive-length claim includes early endings and unranked games. Ranked after-cutoff
Trauma is **8/10 actually reaching r490**, out of 11 games (9 clipped positives); unranked is **1/1 reached** out of
2 games (2 clipped positives). Its surviving-queen enemy distances are also survival-conditioned; similar distances
cannot establish that the policy has no avoidance premium. Retain Nara's account alongside this narrower reading.

These diagnostics are **provisional, one team and one temporal window**, not field-percentile targets. H-H1 stays
proposed weight 0.5: preserving production while protecting the head still requires a paired intervention. Neither
blanket no-split nor deliberate queen sacrifice follows from this audit. Suitable testers remain Carthage/Rome;
use the existing H-H1 falsifier and size calculation, and retain overall wins and production guards.

## Tester and analyst readings

1. **Carthage 03: agree with reject.** Generated-panel win −0.210 [−0.240,−0.182] and economy
   −0.305 [−0.343,−0.272] outweigh conditional queen survival 11.9% / 16–0 queen verdicts. Pool win interval crosses
   zero. The guards+nosplit stack differs from 02; report paired 03−02 to isolate the added guard. These reported
   central intervals are 90%, not 95%. This reinforces production as a constraint, not proof that H-H1 will win.
2. **Antioch's 06 and 04/05 readings:** stratifying fixtures by the baseline's RL outcome fixes membership before
   evaluating treatment, so it avoids treatment-dependent reach selection. The 06 gen +10.7pp on 154 such fixtures
   remains a subgroup result; overall +1.3pp crosses zero. Its 05 official rerun reproduces +4.5pp pool/+1.7pp gen.
   A deployment gate remains the director's decision, and the proposed ΔΦ guard is not yet demonstrated.
3. **Opening-reference disagreement:** `opening_refs.py` uses local Carthage-00 as `us(local)` and a mixed-ranked
   corpus field. Its 0.18 SD total gap cannot be compared with the old 0.80 SD live-us gap as improvement: opposition,
   population, time and normalizers differ. Keep this as a panel-to-field diagnostic. Live-us gap remains NA.
4. **Opening precision disagreement:** the function labelled “bootstrap (games)” actually independently resamples
   side values, and independently redraws top-ten values even though that cohort is contained in the field. It does
   not preserve game/series dependence or cohort overlap. Thus ±8 percentile points and extrapolation to 220 sides/map
   are not validated game/series-level precision claims. Please resample whole series, keeping both sides and their
   cohort labels, then recompute ranked-only map references with the new ladder. Its raw pre/post `shift` query is
   not self-normalized; the median ratio claim still does not establish stable cohort-matched distributions or tails.
   Himeji did not execute this helper: `Q.connect()` may rebuild shared norms.

## Fresh ladder and live-us queue

The new snapshot **20261001T170922Z.json** replaces the 06:21Z snapshot for *new current* analyses. Five top-ten
members overlap. The new top ten, in order, are team IDs **952, 206, 314, 213, 20, 801, 249, 87, 852, 375**.
Cutlery (306) is now **97**, versus 1 before. Team 7 is 34. Of 963 ladder records, 819 have null rank; cohort code
must exclude missing ranks explicitly rather than compare `None <= 10`. Preserve old cohort labels in frozen work.
The snapshot hash and top-ten records are frozen in `ladder-freshness.json`.

Main **1d838553a**, decision D-041, records activation at 17:00 UTC of submission **14265**,
`LV-hb1-14-prior-r540-ed7e4515-ai`. The corpus frozen here has 79,726 unique games, latest start 17:10:41.489Z,
but **0 post-rule team-7 games**. Await the approved collector. Next unit prioritizes new live ranked/unranked
team-7 evidence, verifying submission attribution where available; team identity alone is insufficient if teammates
switch activation. Local no-Devil panels are a different bot/population and cannot fill this gap.

Mac S-1 games file remains 3,822,463 bytes, mtime_ns 1790764194040268141: last verified pre-era store. Antioch's
2,862-game post store is still reported on desktop. Fresh-ladder request is satisfied; store synchronization and
Φ active-only/provenance requests remain open. Rome L10 is running (370/480 pool at read); Kyoto cap-lift and
Carthage 09 have no new completed result in the source cursor.

## Reproduction and provenance

Source commits: main `1d838553a`; Antioch `85637735c`; Carthage `f91c65873`; Nara `21a182700`;
Kyoto `7c835936c`; Rome local status. Board cursors: main D-041/Phase2 seed; Antioch through opening targets and
04/05 official reading; Carthage 03 full rerun/09 queue; Nara unit3; Kyoto baseline/D-033 unchanged.

```
python tools/himeji/cutlery_actions.py --repo /path/to/main --decoder /path/to/wt-himeji --out /scratch/unit6
python tools/himeji/summarize_cutlery.py /scratch/unit6
```

For the exact frozen rerun, first copy `tools/himeji/unit6_audit/source-rows.jsonl` and `manifest.json` into the
output directory. The decoder is Himeji's frame source at parent commit `36d903c8f`; action/death tags also checked
against main's `tools/team_recon_claude/replay_v2.capnp`. Official result layout comes from the previously validated
Antioch reader, not old decoder winner inference. The new query never calls `decode` or a simulator. One read worker
used because Rome was busy; it is complete. No replay downloads, shared writes, bots or simulations.
