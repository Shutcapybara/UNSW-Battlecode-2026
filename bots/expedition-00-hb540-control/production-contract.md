# Expedition food-hold screen v1 — prospective production test

Declared 2026-10-01 before any food-hold games. Candidate expedition-11-foodhold,
parent expedition-01-nodevil. Runtime source manifest and campaign contracts are
immutable after execution starts. No registration or promotion.

Mechanism: before r150, defer an ordinary split when the already-selected move
is one known, simulation-safe step that eats an observed pearl and has the
existing required room, with a fully represented body. Preserve scores, route
selection, prior, emergency escape and partial-body opening rescue/production.
This isolates immediate food opportunity cost. It does not impose a target
split rate or tune an exploration score. The simulation does not predict an
unseen enemy's next action; "safe" means its existing known-state check.

S1's split-restraint association motivates the question; it does not establish
causality. Expedition 05's stronger-opponent results show that opening gains
and outcome gains can separate by opponent. Competing explanations: restraint
preserves productive parents; fewer early children surrender territory; repeated
meals merely postpone expansion; improved intake still fails to concentrate into
a winning longest dragon. No automatic dose/round-boundary sweep follows.

Panel production-v1: every one of the ten LIVE maps, both seats, HB17 and the
g01 r150 graft, fresh seeds 3 and 4, 80 pairs / 160 games. Seed 3 is discovery;
seed 4 is confirmation. These seeds were not used in Expedition's frontier-v1
screen. They are not globally held-out maps or independently sampled opponents.
Complete both without changing source or selecting maps. Reuse only exact
source/fixture-matched production-v1 rows. All earlier panels and verdicts stand.

Primary outcome: paired expected score (win 1, draw .5, loss 0), including
absolute strength and discordant fixtures. Advance to broader testing only if
confirmation gain is strictly positive, neither opponent's confirmation delta
is negative, and no map loses more than one expected-score point. Errors, source
or replay mismatches, incomplete coverage, and failed bookkeeping block judgment.
These are bounded screening rules, not statistical acceptance or promotion.

Prospective evaluation change: opening tempo is a diagnostic, not a veto for
this screen. Immediate growth is the mechanism; winning is the objective. Record
what the prior frontier rule (which also vetoed slower opening tempo) would have
decided on exactly these data, alongside the new result. Do not rewrite the
explore-frontier-v1 verdict. Record whole-map-cluster uncertainty for score and
tempo; only ten maps and related controls limit inference.

Also report full opening trajectories through r150, split counts, newborn and
ally-collision costs, r250 material share and pressure, final total/longest
margins, round-limit and elimination outcomes, separately by map/opponent/seat
and seed. Contrast all fixtures with cohorts defined by the parent's reaching
r250/r400; candidate-survivor conditioning is descriptive only. These diagnose
mechanisms, not extra post-hoc acceptance thresholds. A favorable screen still
needs unfamiliar topology, diverse authenticated opposition, and sandbox checks.

CPU only, one game worker, campaign.py exclusive lock, 20-minute admission budget
and cap 96 per batch; retain replay recovery. Before games, verify source/build,
guard boundaries, recorded-input activation, switch-off parity and archive size.
