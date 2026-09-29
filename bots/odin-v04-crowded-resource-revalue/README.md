# Odin v04 — crowded-resource compact opening candidate

**Status:** experimental synthesis candidate; preserves Odin v03 and adopts
Fenrir v20's single crowded-resource valuation change.

## Delta from v01

The normal room-checked split path is conservative when a newly spawned long
dragon has only a partial body observation. This version keeps the bounded
round-0/1 tail rescue and round-30 child-2 production window, but only on maps
with at most 625 tiles. It restores Odin v01's arrival-only bed valuation so
the compact opening change can be judged independently. All density, swarm,
echo-lane, room-aware, gated-pressure, and 40-tile feeder behavior is unchanged.

This version additionally reduces the ally-density penalty in resource value
from 0.25 to 0.10. It is intentionally isolated from Fenrir's newborn
separation and late CPU caps so the resource hypothesis can be measured on
Odin's chassis.

## Base

Odin starts from the frozen Serre v01 source, based on Sinbad v07/e23.
That gives it arrival-aware bed values, sonar food and portal sharing,
probabilistic threat costs, guarded strikes, crown feeding, bounded search, and
the newborn body-chain fix. Serre's 182-game gauntlet was 134–48 against seven
reference bots; those results belong to Serre, not Odin.

## Adopted mechanisms

- **Porthos x03/x04 spatial evidence and policy.** Odin tracks bounded,
  decaying aggregate dragon counts and directional segment density over sonar.
  It discounts progress toward crowded resources, values child and parent room
  together before splitting, and makes the early push toward enemy density and
  relaxed strike margin available only to foragers before round 200 when the
  team has at least 70% of its unit capacity. Crown and feeder roles do not
  receive the push.
- **Heimdall v10 isolated echo lanes.** Every fourth turn, when no crown, prey,
  handoff, or portal packet needs a ray, Odin sends one isolated sonar ray.
  A following enemy echo creates a small, short-lived penalty on that ray's
  lane. Aggregate echoes are not treated as coordinates. Existing portal
  messages keep priority; that scan turn's ordinary resource and density reports
  are deferred.
- **Longer-range crown feeding.** Spike's replay diagnosis found round-limit
  losses where the team had more total length but small dragons stayed beyond
  the 16-tile feeder radius. Odin sets that radius to 40 to test whether those
  dragons can convert into a longer surviving crown. This can pull them away
  from food or defense earlier, so it needs its own paired reading.
- **Conservative combat.** The candidate keeps Sinbad's probabilistic threat
  model. Its Porthos-inspired pressure is state-gated because Gödel and Von
  Neumann found that unconditional aggression and simpler strike retunes did
  not generalize.

The source snapshots are [Serre v01](../serre-v01-foundation/README.md),
[Porthos x04](../porthos-x04-policy/README.md),
[Heimdall v10](../heimdall-v10-isolated-echo-lanes/README.md), and
[Spike x03](../spike-x03-v32-farfeed/README.md). Odin has its own
64-bit sonar tag and does not share these packets with other bot lines.

## Hypotheses and limits

The room-aware split value targets crowding and poor births; the density
signals and opening-only pressure target Serre's slow opening and its failure
to contest Devil's central fast beds. The short echo warning targets hidden
contact risk. These are transfer hypotheses. Porthos measured its policy on
its own chassis, and Heimdall measured echo lanes on its own chassis.

Odin still has the documented weak matchups on Devil, Arena, and flipped
maps. Spike's wider feeder radius targets the round-500 length race, but remains
a replay-derived hypothesis rather than a measured Odin gain.
Porthos's saturation policy may still trade too eagerly on a different
chassis. The added sonar fields, echo tracking, and child-room flood also need
a fresh judge-meter check.

No Odin strategy or CPU benchmark has been run. Keep it outside the active
frontier until a paired gauntlet, fresh-map check, and judge-sandbox screen are
recorded.
