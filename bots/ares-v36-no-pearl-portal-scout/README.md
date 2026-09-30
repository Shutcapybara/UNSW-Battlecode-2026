# Ares V36 — no-pearl portal scout

V36 branches from V35 after match 674727. With no fresh pearl target, an
unpaired portal has target value 8 instead of 3, ahead of ordinary unseen
ground at 5. A fresh pearl target and known beds keep their existing values.
Ordinary portal scouting starts at dragon age 3; V35's crown threat logic and
newborn split-time portal handoff are retained.

In the replay, Team A dragon 1 approaches the portal edge at `(6,17)` and turns
north on round 52. Its preceding pearl was eaten at round 33 and the next is
not until round 86. The intended change is to send it through the portal when
there is no current pearl target. See the [V36 finding](../../docs/findings/2026-09-30-ares-v36-no-pearl-portal-scout.md).

The contest API lists V36 as submission v91 (ID 12728), active as of 2026-09-30 07:02 UTC. Locally it remains experimental and outside `FRONTIER.md`; its V19 screen is weaker than V35.
