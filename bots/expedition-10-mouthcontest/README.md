# expedition-10-mouthcontest

Prospective L40 mechanism test, frozen 2026-10-01 before any games.
Parent for implementation: expedition-09-mouthroute. Evaluation control:
expedition-01-nodevil. No registration or promotion.

One change: charge the inherited weight-4 portal-mouth penalty only when an
observed allied head occupies the proposed final cell or can land there in one
known step. Reachability uses remembered topology, including paired portals;
all four directions are included conservatively. Unknown edges, unseen allies
and multi-step sprints do not qualify. The inherited route/crossing exemptions,
any-portal option, three-step route window, and HB540 model are unchanged.
This tests selective congestion avoidance, not a complete collision predictor.

Motivation: 09 delays food access in Queen of Spades B / Gavroche seed 1 and
loses four QoS games relative to 01, but improves three Portals outcomes. It
also loses two Portal Quartet games. These are discovery data. No map identity
or seed enters the behavior. No assertion is made that the new rule fixes the
recorded action until closed-loop replay evidence establishes it.

## Fixed focused screen: mouth-contest-v1

Both seats, every original panel opponent, seeds 1 and 2; ordered Queen of
Spades, Portals, Devil, then new/mc26_portal_quartet per seed. This is 56 pairs
per seed: 16 each on the three pool maps and 8 on Quartet. Reuse exact saved
01 fixtures; never rerun completed games. 09 is a secondary comparison only
where its same-fixture evidence already exists. Seed 1 is discovery, seed 2
is confirmation. Complete both seeds without tuning this source between them.
This is a scheduling addition, not replacement of the original full panels.

Record paired wins, full opening tempo curve through r150, food/splits/material
at r50/r100/r150, later material and termination, by map/opponent/seat/seed.
Trace the known Gavroche r33/r34 access and first-food timing explicitly.
Devil is the no-portal negative control; require exact arena-stat parity there.

Advance to broader testing only if: no errors/hash/bookkeeping failures;
Devil parity holds; the discovery first-food delay falls below 09's 15 rounds;
seed-2 total wins are at least 01's, with no map more than one win below 01;
and neither QoS nor Quartet has slower seed-2 mean opening tempo than 01.
Otherwise reject or mark the mechanism unresolved, preserving every result.
These are screening decisions, not statistical acceptance or promotion. Keep
paired outcome counts and sample uncertainty visible; one confirmation seed
does not establish generalization. The original D-032, median/mean sensitivity,
map/phase and sandbox guards remain unresolved until independently assessed.

Native CPU only, one game worker, campaign.py's exclusive lock and replay
recovery. Runtime hashes are frozen in source-manifest.json and run contracts.
Local CPU timing does not establish sandbox validity. Follow status for results.
